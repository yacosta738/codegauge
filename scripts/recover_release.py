#!/usr/bin/env python3
"""Plan and execute authenticated, idempotent recovery of a historical release.

The planner is deliberately independent of GitHub. It validates the exact
operator request and a read-only snapshot before any adapter can perform the
two permitted live mutations: the canonical tag and its GitHub Release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, is_dataclass, replace
from pathlib import Path
from typing import Any, Mapping, Protocol


# Keep exception and dataclass identity stable when the CLI imports the adapter
# while this file is running as ``__main__``.
if __name__ == "__main__":
    sys.modules.setdefault("recover_release", sys.modules[__name__])

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
VERSION_RE = re.compile(
    r"^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-(?:[0-9A-Za-z-]+)(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
TAG_RE = re.compile(r"^v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
                    r"(?:-(?:[0-9A-Za-z-]+)(?:\.[0-9A-Za-z-]+)*)?"
                    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$")
EXPECTED_DEFAULT_BRANCH = "main"
EXPECTED_PULL_REQUEST = 75
HISTORICAL_MANIFEST_PATH = ".release-please-manifest.json"
RECOVERY_ARTIFACT_PLAN = ("canonical-tag", "github-release")
MUTATION_UNKNOWN_GUIDANCE = (
    "re-read the remote canonical tag and GitHub Release before retrying; "
    "never delete, force-move, replace, or blindly retry canonical resources."
)


class RecoveryError(ValueError):
    """Raised for a deterministic refusal before a remote write."""


@dataclass(frozen=True)
class RecoveryRequest:
    repository: str
    default_branch: str
    version: str
    tag: str
    merged_sha: str
    pull_request: int
    historical_tree: str
    historical_manifest: str
    artifact_plan: tuple[str, ...]
    mode: str
    authorization: str
    idempotency_key: str


@dataclass(frozen=True)
class ResourceSnapshot:
    tag_exists: bool = False
    tag_sha: str | None = None
    tag_type: str | None = None
    release_exists: bool = False
    release_tag: str | None = None
    release_sha: str | None = None
    release_version: str | None = None
    release_draft: bool | None = None
    release_body_digest: str | None = None
    release_id: int | None = None


@dataclass(frozen=True)
class RecoveryPreflight:
    """Evidence independently resolved by the live adapter before mutation."""

    repository: str
    default_branch: str
    pull_request: int
    merged_sha: str
    historical_tree: str
    historical_manifest: str
    historical_entry_count: int
    current_entry_count: int
    graph_mismatch: bool
    artifact_plan: tuple[str, ...]
    current_manifest_digest: str
    snapshot: ResourceSnapshot


@dataclass(frozen=True)
class RecoveryPlan:
    status: str
    outcome: str
    repository: str
    default_branch: str
    version: str
    tag: str
    merged_sha: str
    pull_request: int
    historical_tree: str
    historical_manifest: str
    artifact_plan: tuple[str, ...]
    mode: str
    authorization_required: bool
    idempotency_key: str
    provenance_digest: str
    existing: ResourceSnapshot
    intended_operations: tuple[str, ...]
    reasons: tuple[str, ...]
    no_writes: bool = True
    release_id: int | None = None
    preflight: RecoveryPreflight | None = None


class RecoveryAdapter(Protocol):
    """Remote boundary used by the executor and replaceable in tests."""

    def preflight(self, request: RecoveryRequest) -> RecoveryPreflight: ...

    def snapshot(self, request: RecoveryRequest) -> ResourceSnapshot: ...

    def create_tag(self, request: RecoveryRequest) -> None: ...

    def create_release(self, request: RecoveryRequest) -> None: ...


class ReconciliationError(RecoveryError):
    """Raised when a live operation needs operator reconciliation."""

    def __init__(self, message: str, *, plan: RecoveryPlan, mutation: str) -> None:
        super().__init__(message)
        self.plan = plan
        self.mutation = mutation


class FileLock:
    """Exclusive lock with timeout; lock ownership is repository-scoped by path."""

    def __init__(self, path: Path, timeout: float = 30.0, poll: float = 0.05) -> None:
        self.path = path
        self.timeout = timeout
        self.poll = poll
        self._held = False

    def __enter__(self) -> "FileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise RecoveryError(f"recovery lock is busy: {self.path}")
                time.sleep(self.poll)
            else:
                with os.fdopen(fd, "w", encoding="utf-8") as stream:
                    stream.write(f"pid={os.getpid()}\n")
                self._held = True
                return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self._held:
            try:
                self.path.unlink()
            except FileNotFoundError:
                pass
            self._held = False


def _required_sha(value: str, field: str) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise RecoveryError(f"{field} must be a 40-character lowercase Git SHA")
    return value


def _required_digest(value: str, field: str) -> str:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
        raise RecoveryError(f"{field} must be a lowercase SHA-256 digest")
    return value


def derive_idempotency_key(
    repository: str,
    tag: str,
    merged_sha: str,
    operation: str = "reconcile",
) -> str:
    if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
        raise RecoveryError("repository must be an exact owner/name")
    if not isinstance(tag, str) or not TAG_RE.fullmatch(tag):
        raise RecoveryError("tag must be a canonical vX.Y.Z tag")
    merged_sha = _required_sha(merged_sha, "merged_sha")
    if not isinstance(operation, str) or not operation:
        raise RecoveryError("operation must be non-empty")
    material = "\0".join((repository, tag, merged_sha, operation)).encode()
    return hashlib.sha256(material).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _load_json(path: Path, label: str) -> Any:
    try:
        with path.open(encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as error:
        raise RecoveryError(f"unable to read {label}: {error}") from error


def _snapshot_from_value(value: Mapping[str, Any]) -> ResourceSnapshot:
    if not isinstance(value, Mapping):
        raise RecoveryError("resource snapshot must be an object")
    fields = ResourceSnapshot.__dataclass_fields__
    unexpected = set(value) - set(fields)
    if unexpected:
        raise RecoveryError(
            "resource snapshot contains unexpected fields: "
            + ", ".join(sorted(unexpected))
        )
    for field in ("tag_exists", "release_exists"):
        if not isinstance(value.get(field, False), bool):
            raise RecoveryError(f"{field} must be boolean")
    for field in ("tag_sha", "release_sha"):
        field_value = value.get(field)
        if field_value is not None:
            _required_sha(field_value, field)
    if value.get("release_draft") is not None and not isinstance(value["release_draft"], bool):
        raise RecoveryError("release_draft must be boolean or null")
    for field in ("release_tag", "release_version", "release_body_digest", "tag_type"):
        field_value = value.get(field)
        if field_value is not None and not isinstance(field_value, str):
            raise RecoveryError(f"{field} must be a string or null")
    release_id = value.get("release_id")
    if release_id is not None and (
        not isinstance(release_id, int) or isinstance(release_id, bool) or release_id <= 0
    ):
        raise RecoveryError("release_id must be a positive integer or null")
    if value.get("release_body_digest") is not None:
        _required_digest(value["release_body_digest"], "release_body_digest")
    if value.get("tag_exists", False) and value.get("tag_sha") is None:
        raise RecoveryError("tag_exists requires tag_sha")
    if value.get("release_exists", False) and (
        value.get("release_tag") is None or value.get("release_sha") is None
    ):
        raise RecoveryError("release_exists requires release_tag and release_sha")
    return ResourceSnapshot(
        **{field: value.get(field, field_info.default) for field, field_info in fields.items()}
    )


def _request_from_value(value: Mapping[str, Any]) -> RecoveryRequest:
    required = (
        "repository", "default_branch", "version", "tag", "merged_sha",
        "pull_request", "historical_tree", "historical_manifest", "artifact_plan",
        "mode", "authorization", "idempotency_key",
    )
    unexpected = set(value) - set(required)
    if unexpected:
        raise RecoveryError(
            "request contains unexpected fields: " + ", ".join(sorted(unexpected))
        )
    missing = [field for field in required if field not in value]
    if missing:
        raise RecoveryError(f"request is missing: {', '.join(missing)}")
    repository = value["repository"]
    default_branch = value["default_branch"]
    version = value["version"]
    tag = value["tag"]
    if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
        raise RecoveryError("repository must be an exact owner/name")
    if default_branch != EXPECTED_DEFAULT_BRANCH:
        raise RecoveryError("default_branch must be the protected main branch")
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        raise RecoveryError("version must be valid semver")
    if not isinstance(tag, str) or tag != f"v{version}" or not TAG_RE.fullmatch(tag):
        raise RecoveryError("tag must be the canonical tag for version")
    merged_sha = _required_sha(value["merged_sha"], "merged_sha")
    pull_request = value["pull_request"]
    if not isinstance(pull_request, int) or isinstance(pull_request, bool) or pull_request <= 0:
        raise RecoveryError("pull_request must be a positive integer")
    if pull_request != EXPECTED_PULL_REQUEST:
        raise RecoveryError(
            f"pull_request must identify the historical merged PR #{EXPECTED_PULL_REQUEST}"
        )
    for field in ("historical_tree", "mode", "authorization", "idempotency_key"):
        if not isinstance(value[field], str) or not value[field]:
            raise RecoveryError(f"{field} must be a non-empty string")
    _required_sha(value["historical_tree"], "historical_tree")
    _required_digest(value["historical_manifest"], "historical_manifest")
    artifact_plan = value["artifact_plan"]
    if not isinstance(artifact_plan, (list, tuple)) or any(
        not isinstance(operation, str) for operation in artifact_plan
    ):
        raise RecoveryError("artifact_plan must be an ordered list of operation names")
    if tuple(artifact_plan) != RECOVERY_ARTIFACT_PLAN:
        raise RecoveryError(
            "artifact_plan must contain only canonical tag then GitHub Release reconciliation"
        )
    mode = value["mode"]
    if mode not in {"dry-run", "live"}:
        raise RecoveryError("mode must be dry-run or live")
    expected_key = derive_idempotency_key(repository, tag, merged_sha)
    if value["idempotency_key"] != expected_key:
        raise RecoveryError("idempotency_key does not match repository, tag, and merged_sha")
    expected_authorization = (
        "RECOVER_RELEASE_LIVE" if mode == "live" else "RECOVER_RELEASE_DRY_RUN"
    )
    if value["authorization"] != expected_authorization:
        raise RecoveryError(
            f"{mode} recovery requires {expected_authorization} authorization"
        )
    return RecoveryRequest(
        repository=repository,
        default_branch=default_branch,
        version=version,
        tag=tag,
        merged_sha=merged_sha,
        pull_request=pull_request,
        historical_tree=value["historical_tree"],
        historical_manifest=value["historical_manifest"],
        artifact_plan=tuple(artifact_plan),
        mode=mode,
        authorization=value["authorization"],
        idempotency_key=value["idempotency_key"],
    )


def load_request(path: Path) -> RecoveryRequest:
    value = _load_json(path, "recovery request")
    if not isinstance(value, Mapping):
        raise RecoveryError("recovery request must be an object")
    return _request_from_value(value)


def _validate_snapshot(request: RecoveryRequest, snapshot: ResourceSnapshot) -> None:
    if not is_dataclass(snapshot) or not all(
        hasattr(snapshot, field)
        for field in ResourceSnapshot.__dataclass_fields__
    ):
        raise RecoveryError("snapshot must be a ResourceSnapshot")
    try:
        snapshot_value = asdict(snapshot)
    except TypeError as error:
        raise RecoveryError("snapshot must be a ResourceSnapshot") from error
    _snapshot_from_value(snapshot_value)
    if snapshot.tag_exists and (snapshot.tag_type != "commit" or snapshot.tag_sha != request.merged_sha):
        raise RecoveryError("canonical tag exists with a conflicting type or SHA")
    if snapshot.release_exists and (
        snapshot.release_tag != request.tag
        or snapshot.release_sha != request.merged_sha
        or snapshot.release_version not in {None, request.version}
    ):
        raise RecoveryError("canonical release exists with a conflicting identity")


def _validate_request(request: RecoveryRequest) -> None:
    if not isinstance(request, RecoveryRequest):
        raise RecoveryError("request must be a RecoveryRequest")
    _request_from_value(asdict(request))


def _validate_preflight(
    request: RecoveryRequest,
    preflight: RecoveryPreflight,
) -> None:
    """Ensure the plan is built from independently authenticated evidence."""

    if not isinstance(preflight, RecoveryPreflight):
        raise RecoveryError("live recovery requires a RecoveryPreflight result")
    if preflight.repository != request.repository:
        raise RecoveryError("preflight repository identity does not match the request")
    if preflight.default_branch != request.default_branch:
        raise RecoveryError("preflight default branch does not match the request")
    if preflight.pull_request != request.pull_request:
        raise RecoveryError("preflight pull request does not match the request")
    if preflight.merged_sha != request.merged_sha:
        raise RecoveryError("preflight merged SHA does not match the request")
    if preflight.historical_tree != request.historical_tree:
        raise RecoveryError("preflight historical tree does not match the request")
    if preflight.historical_manifest != request.historical_manifest:
        raise RecoveryError("preflight historical manifest does not match the request")
    if tuple(preflight.artifact_plan) != tuple(request.artifact_plan):
        raise RecoveryError("preflight artifact plan does not match the request")
    if tuple(preflight.artifact_plan) != RECOVERY_ARTIFACT_PLAN:
        raise RecoveryError("preflight artifact plan contains an unapproved operation")
    if preflight.historical_entry_count != 13 or preflight.current_entry_count != 14:
        raise RecoveryError("preflight release graph has an unexpected entry count")
    if preflight.graph_mismatch is not True:
        raise RecoveryError("preflight must preserve the historical/current graph distinction")
    _required_digest(preflight.current_manifest_digest, "current_manifest_digest")
    _validate_snapshot(request, preflight.snapshot)


def _provenance_digest(request: RecoveryRequest) -> str:
    material = _canonical_json(asdict(request)).encode()
    return hashlib.sha256(material).hexdigest()


def plan_recovery(
    request: RecoveryRequest,
    snapshot: ResourceSnapshot,
    *,
    preflight: RecoveryPreflight | None = None,
) -> RecoveryPlan:
    """Validate an exact request and return a no-write reconciliation plan."""

    _validate_request(request)
    if preflight is not None:
        _validate_preflight(request, preflight)
        if snapshot != preflight.snapshot:
            raise RecoveryError("preflight snapshot does not match the planning snapshot")
    _validate_snapshot(request, snapshot)
    operations: list[str] = []
    if not snapshot.tag_exists:
        operations.append("create-canonical-tag")
    if not snapshot.release_exists:
        operations.append("create-github-release")
    return RecoveryPlan(
        status="planned",
        outcome="no-op" if not operations else "planned",
        repository=request.repository,
        default_branch=request.default_branch,
        version=request.version,
        tag=request.tag,
        merged_sha=request.merged_sha,
        pull_request=request.pull_request,
        historical_tree=request.historical_tree,
        historical_manifest=request.historical_manifest,
        artifact_plan=tuple(request.artifact_plan),
        mode=request.mode,
        authorization_required=request.mode == "live",
        idempotency_key=request.idempotency_key,
        provenance_digest=_provenance_digest(request),
        existing=snapshot,
        intended_operations=tuple(operations),
        reasons=("NO_WRITES: planner performs validation only",),
        release_id=snapshot.release_id,
        preflight=preflight,
    )


def _live_plan(request: RecoveryRequest, adapter: RecoveryAdapter) -> RecoveryPlan:
    """Build a live plan only from the adapter's independent read boundary."""

    preflight = getattr(adapter, "preflight", None)
    if not callable(preflight):
        raise RecoveryError(
            "live recovery requires an independent adapter preflight before writes"
        )
    evidence = preflight(request)
    if not isinstance(evidence, RecoveryPreflight):
        raise RecoveryError("live recovery adapter returned no trusted preflight")
    return plan_recovery(request, evidence.snapshot, preflight=evidence)


def _mutation_plan(plan: RecoveryPlan, mutation: str) -> RecoveryPlan:
    """Carry a write-attempt outcome without falsely retaining NO_WRITES."""

    return replace(
        plan,
        no_writes=False,
        reasons=plan.reasons + (f"MUTATION_ATTEMPTED: {mutation}",),
    )


def execute_recovery(
    request: RecoveryRequest,
    adapter: RecoveryAdapter,
    *,
    lock_path: Path,
    confirmation: str | None = None,
) -> RecoveryPlan:
    """Re-read state under a repository lock and reconcile tag then release."""

    _validate_request(request)
    if request.mode != "live":
        return plan_recovery(request, adapter.snapshot(request))
    if request.authorization != "RECOVER_RELEASE_LIVE" or confirmation != request.authorization:
        raise RecoveryError("live recovery requires explicit confirmation")
    with FileLock(lock_path):
        initial = _live_plan(request, adapter)
        if initial.outcome == "no-op":
            return initial
        mutations: list[str] = []
        if "create-canonical-tag" in initial.intended_operations:
            try:
                adapter.create_tag(request)
            except Exception as error:
                raise ReconciliationError(
                    "ambiguous canonical tag mutation; recovery state must be audited and re-read",
                    plan=_mutation_plan(initial, "mutation-unknown"),
                    mutation="mutation-unknown",
                ) from error
            mutations.append("create-canonical-tag")
        try:
            current = _live_plan(request, adapter)
        except Exception as error:
            if not mutations:
                raise
            raise ReconciliationError(
                "live recovery partially failed after canonical tag reconciliation",
                plan=_mutation_plan(initial, "partial-failure"),
                mutation="partial-failure",
            ) from error
        if "create-canonical-tag" in current.intended_operations:
            raise ReconciliationError(
                "canonical tag reconciliation did not converge; GitHub Release creation was skipped",
                plan=_mutation_plan(current, "partial-failure"),
                mutation="partial-failure",
            )
        if "create-github-release" in current.intended_operations:
            try:
                adapter.create_release(request)
            except Exception as error:
                raise ReconciliationError(
                    "ambiguous GitHub Release mutation; re-read remote tag and release "
                    f"state before retrying: {error}",
                    plan=_mutation_plan(current, "mutation-unknown"),
                    mutation="mutation-unknown",
                ) from error
            mutations.append("create-github-release")
        try:
            final = _live_plan(request, adapter)
        except Exception as error:
            raise ReconciliationError(
                "live recovery final preflight could not determine mutation state",
                plan=_mutation_plan(
                    current,
                    "mutation-unknown"
                    if "create-github-release" in mutations
                    else "partial-failure",
                ),
                mutation=("mutation-unknown" if "create-github-release" in mutations else "partial-failure"),
            ) from error
        if final.intended_operations:
            raise ReconciliationError(
                "live recovery did not converge to the canonical tag and GitHub Release",
                plan=_mutation_plan(
                    final,
                    "mutation-unknown"
                    if "create-github-release" in mutations
                    else "partial-failure",
                ),
                mutation=("mutation-unknown" if "create-github-release" in mutations else "partial-failure"),
            )
        if not mutations:
            return final
        return replace(
            final,
            outcome="reconciled",
            no_writes=False,
            reasons=final.reasons + (f"MUTATIONS: {', '.join(mutations)}",),
        )


def audit_record(plan: RecoveryPlan, *, error: str | None = None, mutation: str | None = None) -> dict[str, Any]:
    record = asdict(plan)
    record["existing"] = asdict(plan.existing)
    record["intended_operations"] = list(plan.intended_operations)
    record["reasons"] = list(plan.reasons)
    record["audit"] = {
        "outcome": "refusal" if error else (mutation or plan.outcome),
        "no_writes": plan.no_writes if not mutation else False,
        "error": error,
    }
    if mutation == "mutation-unknown":
        record["audit"]["recovery_guidance"] = MUTATION_UNKNOWN_GUIDANCE
    return record


def refusal_record(error: Exception | str, *, request: RecoveryRequest | None = None) -> dict[str, Any]:
    """Build a redacted refusal record when validation cannot produce a plan."""

    message = str(error)
    record: dict[str, Any] = {
        "status": "refused",
        "audit": {"outcome": "refusal", "no_writes": True, "error": message},
    }
    if request is not None:
        record.update(
            {
                "repository": request.repository,
                "default_branch": request.default_branch,
                "version": request.version,
                "tag": request.tag,
                "merged_sha": request.merged_sha,
                "pull_request": request.pull_request,
                "historical_tree": request.historical_tree,
                "historical_manifest": request.historical_manifest,
                "artifact_plan": list(request.artifact_plan),
                "mode": request.mode,
                "idempotency_key": request.idempotency_key,
            }
        )
    return record


def write_audit(record: Mapping[str, Any], path: Path | None, human_path: Path | None) -> None:
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_canonical_json(record) + "\n", encoding="utf-8")
    if human_path is not None:
        human_path.parent.mkdir(parents=True, exist_ok=True)
        audit = record["audit"]
        lines = [
            "CodeGauge release recovery",
            f"status: {record.get('status', 'refused')}",
            f"outcome: {audit.get('outcome')}",
            f"repository: {record.get('repository', 'unknown')}",
            f"tag: {record.get('tag', 'unknown')}",
            f"target SHA: {record.get('merged_sha', 'unknown')}",
            f"NO_WRITES: {audit.get('no_writes')}",
        ]
        if audit.get("error"):
            lines.append(f"refusal: {audit['error']}")
        if audit.get("recovery_guidance"):
            lines.append(f"recovery guidance: {audit['recovery_guidance']}")
        human_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    command.add_argument("--request", type=Path, required=True)
    command.add_argument("--snapshot", type=Path)
    command.add_argument("--audit-output", type=Path)
    command.add_argument("--human-output", type=Path)
    command.add_argument("--execute-live", action="store_true")
    command.add_argument("--confirm-live")
    command.add_argument("--plan-only", action="store_true")
    command.add_argument("--github-api-url", default="https://api.github.com")
    command.add_argument("--lock-path", type=Path)
    command.add_argument("--expected-repository")
    command.add_argument("--expected-default-branch")
    command.add_argument("--expected-tag")
    command.add_argument("--expected-merged-sha")
    command.add_argument("--expected-idempotency-key")
    return command


def _validate_expected_identity(request: RecoveryRequest, args: argparse.Namespace) -> None:
    expected = {
        "repository": args.expected_repository,
        "default_branch": args.expected_default_branch,
        "tag": args.expected_tag,
        "merged_sha": args.expected_merged_sha,
        "idempotency_key": args.expected_idempotency_key,
    }
    for field, value in expected.items():
        if value is not None and getattr(request, field) != value:
            raise RecoveryError(f"request {field} does not match the trusted workflow identity")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        request = load_request(args.request)
        _validate_expected_identity(request, args)
        if request.mode != "live" and args.execute_live:
            raise RecoveryError("--execute-live requires a live request")
        if request.mode == "live":
            if not args.execute_live and not args.plan_only:
                raise RecoveryError("live request requires the protected --execute-live path")
            if args.execute_live and args.plan_only:
                raise RecoveryError("live request cannot execute and plan-only at the same time")
            if args.execute_live and args.confirm_live != "RECOVER_RELEASE_LIVE":
                raise RecoveryError("live request requires explicit confirmation")
            if not args.expected_repository:
                raise RecoveryError(
                    "live recovery requires a trusted expected repository boundary"
                )
            if not os.environ.get("GH_TOKEN"):
                raise RecoveryError("live recovery requires GH_TOKEN")
            from recover_release_github import GitHubRecoveryAdapter, UrllibTransport

            adapter = GitHubRecoveryAdapter(
                UrllibTransport(os.environ["GH_TOKEN"], base_url=args.github_api_url),
                args.expected_repository,
            )
            if args.plan_only:
                plan = _live_plan(request, adapter)
            else:
                plan = execute_recovery(
                    request,
                    adapter,
                    lock_path=args.lock_path or Path(".release-recovery.lock"),
                    confirmation=args.confirm_live,
                )
        else:
            if args.snapshot is None:
                raise RecoveryError("dry-run recovery requires a resource snapshot")
            snapshot_value = _load_json(args.snapshot, "resource snapshot")
            snapshot = _snapshot_from_value(snapshot_value)
            plan = plan_recovery(request, snapshot)
        record = audit_record(plan)
        write_audit(record, args.audit_output, args.human_output)
        print(json.dumps(record, sort_keys=True))
        return 0
    except ReconciliationError as error:
        record = audit_record(error.plan, mutation=error.mutation)
        record["audit"]["error"] = str(error)
        write_audit(record, args.audit_output, args.human_output)
        print(json.dumps(record, sort_keys=True))
        return 3
    except RecoveryError as error:
        record = refusal_record(error)
        write_audit(record, args.audit_output, args.human_output)
        print(json.dumps(record, sort_keys=True))
        return 2


if __name__ == "__main__":
    sys.exit(main())
