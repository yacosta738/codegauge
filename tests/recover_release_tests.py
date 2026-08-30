#!/usr/bin/env python3
"""Test-first contracts for the historical release recovery planner."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from recover_release import (  # noqa: E402
    RecoveryError,
    RecoveryPreflight,
    RecoveryRequest,
    ResourceSnapshot,
    ReconciliationError,
    audit_record,
    derive_idempotency_key,
    plan_recovery,
    execute_recovery,
    FileLock,
)

REPOSITORY = "yacosta738/codegauge"
VERSION = "0.3.0"
TAG = "v0.3.0"
SHA = "a" * 40
TREE = "fcc91b4850480945ae484c3ebdba18f8a4e38270"
MANIFEST = "43a6692a93b9648960906342f86ad69dd09bf8e151e990b5816bdb33f3220efc"
KEY = derive_idempotency_key(REPOSITORY, TAG, SHA)
LIVE_CONFIRMATION = "RECOVER_RELEASE_LIVE"
ARTIFACT_PLAN = ("canonical-tag", "github-release")


def request(**overrides: object) -> RecoveryRequest:
    values: dict[str, object] = {
        "repository": REPOSITORY,
        "default_branch": "main",
        "version": VERSION,
        "tag": TAG,
        "merged_sha": SHA,
        "pull_request": 75,
        "historical_tree": TREE,
        "historical_manifest": MANIFEST,
        "mode": "dry-run",
        "authorization": "RECOVER_RELEASE_DRY_RUN",
        "idempotency_key": KEY,
        "artifact_plan": list(ARTIFACT_PLAN),
    }
    values.update(overrides)
    return RecoveryRequest(**values)  # type: ignore[arg-type]


def test_exact_request_produces_deterministic_no_write_plan() -> None:
    result = plan_recovery(request(), ResourceSnapshot())

    assert result.status == "planned"
    assert result.outcome == "planned"
    assert result.no_writes is True
    assert result.tag == TAG
    assert result.merged_sha == SHA
    assert result.pull_request == 75
    assert result.intended_operations == ("create-canonical-tag", "create-github-release")
    assert result.idempotency_key == KEY
    assert len(result.provenance_digest) == 64


def test_matching_resources_converge_to_no_op() -> None:
    result = plan_recovery(
        request(),
        ResourceSnapshot(
            tag_exists=True,
            tag_sha=SHA,
            tag_type="commit",
            release_exists=True,
            release_tag=TAG,
            release_sha=SHA,
            release_version=VERSION,
        ),
    )

    assert result.outcome == "no-op"
    assert result.intended_operations == ()


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"repository": "codegauge"}, "repository"),
        ({"tag": "v0.3.1"}, "canonical tag"),
        ({"merged_sha": "not-a-sha"}, "merged_sha"),
        ({"idempotency_key": "0" * 64}, "idempotency_key"),
    ],
)
def test_invalid_exact_identity_fails_closed(overrides: dict[str, object], message: str) -> None:
    with pytest.raises(RecoveryError, match=message):
        values = request(**overrides)
        # Request is intentionally validated by the same public boundary used by the CLI.
        from recover_release import _request_from_value

        _request_from_value(values.__dict__)


def test_planner_revalidates_direct_requests_before_snapshot_use() -> None:
    with pytest.raises(RecoveryError, match="historical_tree"):
        plan_recovery(request(historical_tree="not-a-tree"), ResourceSnapshot())


def test_request_rejects_unexpected_fields() -> None:
    from recover_release import _request_from_value

    payload = request().__dict__
    payload["unexpected"] = "value"

    with pytest.raises(RecoveryError, match="unexpected fields"):
        _request_from_value(payload)


def test_planner_rejects_a_non_snapshot_boundary_value() -> None:
    with pytest.raises(RecoveryError, match="ResourceSnapshot"):
        plan_recovery(request(), {})  # type: ignore[arg-type]


def test_conflicting_resources_are_never_replaced() -> None:
    with pytest.raises(RecoveryError, match="conflicting"):
        plan_recovery(
            request(),
            ResourceSnapshot(tag_exists=True, tag_sha="b" * 40, tag_type="commit"),
        )


def test_live_mode_requires_explicit_authorization() -> None:
    with pytest.raises(RecoveryError, match="authorization"):
        from recover_release import _request_from_value

        values = request(mode="live", authorization="RECOVER_RELEASE_DRY_RUN")
        _request_from_value(values.__dict__)


def test_audit_contains_machine_and_human_no_write_fields() -> None:
    result = plan_recovery(request(), ResourceSnapshot())
    audit = audit_record(result)

    assert audit["audit"] == {"outcome": "planned", "no_writes": True, "error": None}
    assert audit["reasons"] == ["NO_WRITES: planner performs validation only"]


def test_cli_rejects_malformed_snapshot_without_writes(tmp_path: Path) -> None:
    request_path = tmp_path / "request.json"
    snapshot_path = tmp_path / "snapshot.json"
    request_path.write_text(json.dumps(request().__dict__), encoding="utf-8")
    snapshot_path.write_text("[]", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "recover_release.py"), "--request", str(request_path), "--snapshot", str(snapshot_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["audit"]["no_writes"] is True


def test_snapshot_rejects_unexpected_fields() -> None:
    from recover_release import _snapshot_from_value

    payload = ResourceSnapshot().__dict__
    payload["unexpected"] = "value"

    with pytest.raises(RecoveryError, match="unexpected fields"):
        _snapshot_from_value(payload)


def test_cli_writes_machine_and_human_refusal_audit(tmp_path: Path) -> None:
    request_path = tmp_path / "request.json"
    snapshot_path = tmp_path / "snapshot.json"
    machine_path = tmp_path / "audit" / "record.json"
    human_path = tmp_path / "audit" / "record.txt"
    request_path.write_text(json.dumps(request().__dict__), encoding="utf-8")
    snapshot_path.write_text("[]", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "recover_release.py"),
            "--request",
            str(request_path),
            "--snapshot",
            str(snapshot_path),
            "--audit-output",
            str(machine_path),
            "--human-output",
            str(human_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    machine = json.loads(machine_path.read_text(encoding="utf-8"))
    human = human_path.read_text(encoding="utf-8")
    assert machine["audit"]["outcome"] == "refusal"
    assert machine["audit"]["no_writes"] is True
    assert "NO_WRITES: True" in human
    assert "refusal:" in human


class FakeAdapter:
    def __init__(self, snapshot: ResourceSnapshot) -> None:
        self.current = snapshot
        self.calls: list[str] = []

    def snapshot(self, _: RecoveryRequest) -> ResourceSnapshot:
        return self.current

    def preflight(self, _: RecoveryRequest) -> RecoveryPreflight:
        return RecoveryPreflight(
            repository=REPOSITORY,
            default_branch="main",
            pull_request=75,
            merged_sha=SHA,
            historical_tree=TREE,
            historical_manifest=MANIFEST,
            historical_entry_count=13,
            current_entry_count=14,
            graph_mismatch=True,
            artifact_plan=ARTIFACT_PLAN,
            current_manifest_digest="b" * 64,
            snapshot=self.current,
        )

    def create_tag(self, _: RecoveryRequest) -> None:
        self.calls.append("tag")
        self.current = ResourceSnapshot(
            tag_exists=True, tag_sha=SHA, tag_type="commit",
            release_exists=self.current.release_exists, release_tag=self.current.release_tag,
            release_sha=self.current.release_sha, release_version=self.current.release_version,
        )

    def create_release(self, _: RecoveryRequest) -> None:
        self.calls.append("release")
        self.current = ResourceSnapshot(
            tag_exists=True, tag_sha=SHA, tag_type="commit",
            release_exists=True, release_tag=TAG, release_sha=SHA, release_version=VERSION,
        )


def test_live_execution_is_tag_then_release_and_rerun_is_no_op(tmp_path: Path) -> None:
    live = request(mode="live", authorization="RECOVER_RELEASE_LIVE")
    adapter = FakeAdapter(ResourceSnapshot())

    first = execute_recovery(
        live,
        adapter,
        lock_path=tmp_path / "recovery.lock",
        confirmation=LIVE_CONFIRMATION,
    )
    second = execute_recovery(
        live,
        adapter,
        lock_path=tmp_path / "recovery.lock",
        confirmation=LIVE_CONFIRMATION,
    )

    assert first.outcome == "reconciled"
    assert second.outcome == "no-op"
    assert adapter.calls == ["tag", "release"]


def test_live_execution_reports_ambiguous_release_failure_without_rollback(tmp_path: Path) -> None:
    class ReleaseFailureAdapter(FakeAdapter):
        def create_release(self, _: RecoveryRequest) -> None:
            self.calls.append("release")
            raise RecoveryError("release unavailable")

    live = request(mode="live", authorization="RECOVER_RELEASE_LIVE")
    adapter = ReleaseFailureAdapter(ResourceSnapshot())

    with pytest.raises(ReconciliationError, match="ambiguous") as failure:
        execute_recovery(
            live,
            adapter,
            lock_path=tmp_path / "recovery.lock",
            confirmation=LIVE_CONFIRMATION,
        )

    assert failure.value.mutation == "mutation-unknown"
    assert "re-read" in audit_record(
        failure.value.plan, mutation=failure.value.mutation
    )["audit"]["recovery_guidance"]
    assert adapter.calls == ["tag", "release"]
    assert adapter.current.tag_exists is True
    assert adapter.current.release_exists is False


def test_ambiguous_release_rerun_reconciles_only_the_missing_release(tmp_path: Path) -> None:
    class RetryReleaseAdapter(FakeAdapter):
        def __init__(self) -> None:
            super().__init__(ResourceSnapshot())
            self.release_attempts = 0

        def create_release(self, request: RecoveryRequest) -> None:
            self.release_attempts += 1
            if self.release_attempts == 1:
                self.calls.append("release")
                raise RecoveryError("temporary release outage")
            super().create_release(request)

    live = request(mode="live", authorization=LIVE_CONFIRMATION)
    adapter = RetryReleaseAdapter()

    with pytest.raises(ReconciliationError, match="ambiguous") as failure:
        execute_recovery(
            live,
            adapter,
            lock_path=tmp_path / "recovery.lock",
            confirmation=LIVE_CONFIRMATION,
        )

    assert failure.value.mutation == "mutation-unknown"

    result = execute_recovery(
        live,
        adapter,
        lock_path=tmp_path / "recovery.lock",
        confirmation=LIVE_CONFIRMATION,
    )

    assert result.outcome == "reconciled"
    assert adapter.calls == ["tag", "release", "release"]
    assert adapter.current.tag_exists is True
    assert adapter.current.release_exists is True


def test_recovery_does_not_create_release_until_tag_converges(tmp_path: Path) -> None:
    class NonConvergingTagAdapter(FakeAdapter):
        def create_tag(self, _: RecoveryRequest) -> None:
            self.calls.append("tag")

    live = request(mode="live", authorization=LIVE_CONFIRMATION)
    adapter = NonConvergingTagAdapter(ResourceSnapshot())

    with pytest.raises(RecoveryError, match="tag reconciliation"):
        execute_recovery(
            live,
            adapter,
            lock_path=tmp_path / "recovery.lock",
            confirmation=LIVE_CONFIRMATION,
        )

    assert adapter.calls == ["tag"]


def test_dry_run_never_calls_mutation_methods(tmp_path: Path) -> None:
    class NoWriteAdapter(FakeAdapter):
        def create_tag(self, _: RecoveryRequest) -> None:
            raise AssertionError("dry-run attempted tag creation")

        def create_release(self, _: RecoveryRequest) -> None:
            raise AssertionError("dry-run attempted release creation")

    dry_run = request()
    adapter = NoWriteAdapter(ResourceSnapshot())

    result = execute_recovery(
        dry_run,
        adapter,
        lock_path=tmp_path / "recovery.lock",
    )

    assert result.outcome == "planned"
    assert result.no_writes is True
    assert adapter.calls == []


def test_cli_records_partial_failure_as_mutation_audit(tmp_path: Path) -> None:
    """The audit boundary can represent a mutation followed by a refusal."""

    plan = plan_recovery(request(mode="live", authorization="RECOVER_RELEASE_LIVE"), ResourceSnapshot())
    record = audit_record(plan, mutation="partial-failure")
    record["audit"]["error"] = "release unavailable"

    assert record["audit"] == {
        "outcome": "partial-failure",
        "no_writes": False,
        "error": "release unavailable",
    }


def test_successful_live_reconciliation_audit_marks_writes(tmp_path: Path) -> None:
    live = request(mode="live", authorization=LIVE_CONFIRMATION)
    adapter = FakeAdapter(ResourceSnapshot())

    plan = execute_recovery(
        live,
        adapter,
        lock_path=tmp_path / "recovery.lock",
        confirmation=LIVE_CONFIRMATION,
    )
    record = audit_record(plan)

    assert record["audit"] == {
        "outcome": "reconciled",
        "no_writes": False,
        "error": None,
    }


def test_lock_refuses_concurrent_recovery(tmp_path: Path) -> None:
    lock_path = tmp_path / "recovery.lock"
    with FileLock(lock_path):
        with pytest.raises(RecoveryError, match="busy"):
            with FileLock(lock_path, timeout=0.01, poll=0.001):
                pass


def test_live_execution_requires_explicit_confirmation(tmp_path: Path) -> None:
    live = request(mode="live", authorization=LIVE_CONFIRMATION)
    adapter = FakeAdapter(ResourceSnapshot())

    with pytest.raises(RecoveryError, match="confirmation"):
        execute_recovery(live, adapter, lock_path=tmp_path / "recovery.lock")

    assert adapter.calls == []


def test_live_execution_revalidates_request_before_remote_preflight(tmp_path: Path) -> None:
    class TrackingAdapter(FakeAdapter):
        def preflight(self, _: RecoveryRequest) -> RecoveryPreflight:
            self.calls.append("preflight")
            return super().preflight(_)

    live = request(
        mode="live",
        authorization=LIVE_CONFIRMATION,
        idempotency_key="0" * 64,
    )
    adapter = TrackingAdapter(ResourceSnapshot())

    with pytest.raises(RecoveryError, match="idempotency_key"):
        execute_recovery(
            live,
            adapter,
            lock_path=tmp_path / "recovery.lock",
            confirmation=LIVE_CONFIRMATION,
        )

    assert adapter.calls == []


def test_live_execution_requires_independent_preflight_before_any_write(tmp_path: Path) -> None:
    class NoPreflightAdapter:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def snapshot(self, _: RecoveryRequest) -> ResourceSnapshot:
            self.calls.append("snapshot")
            return ResourceSnapshot()

        def create_tag(self, _: RecoveryRequest) -> None:
            self.calls.append("tag")

        def create_release(self, _: RecoveryRequest) -> None:
            self.calls.append("release")

    live = request(mode="live", authorization=LIVE_CONFIRMATION)
    adapter = NoPreflightAdapter()

    with pytest.raises(RecoveryError, match="preflight"):
        execute_recovery(
            live,
            adapter,  # type: ignore[arg-type]
            lock_path=tmp_path / "recovery.lock",
            confirmation=LIVE_CONFIRMATION,
        )

    assert adapter.calls == []


def test_live_execution_classifies_ambiguous_tag_write_as_mutation(tmp_path: Path) -> None:
    class AmbiguousTagAdapter(FakeAdapter):
        def create_tag(self, _: RecoveryRequest) -> None:
            self.calls.append("tag")
            raise OSError("connection closed after request was sent")

    live = request(mode="live", authorization=LIVE_CONFIRMATION)
    adapter = AmbiguousTagAdapter(ResourceSnapshot())

    with pytest.raises(ReconciliationError, match="ambiguous") as failure:
        execute_recovery(
            live,
            adapter,
            lock_path=tmp_path / "recovery.lock",
            confirmation=LIVE_CONFIRMATION,
        )

    assert failure.value.mutation == "mutation-unknown"
    assert failure.value.plan.no_writes is False
    record = audit_record(failure.value.plan, mutation=failure.value.mutation)
    assert record["audit"]["no_writes"] is False
    assert record["audit"]["outcome"] == "mutation-unknown"
    assert adapter.calls == ["tag"]


def test_live_execution_classifies_ambiguous_release_transport_failure_as_unknown(
    tmp_path: Path,
) -> None:
    class AmbiguousReleaseAdapter(FakeAdapter):
        def create_release(self, _: RecoveryRequest) -> None:
            self.calls.append("release")
            raise OSError("connection closed after release request was sent")

    live = request(mode="live", authorization=LIVE_CONFIRMATION)
    adapter = AmbiguousReleaseAdapter(ResourceSnapshot())

    with pytest.raises(ReconciliationError, match="ambiguous") as failure:
        execute_recovery(
            live,
            adapter,
            lock_path=tmp_path / "recovery.lock",
            confirmation=LIVE_CONFIRMATION,
        )

    assert failure.value.mutation == "mutation-unknown"
    assert failure.value.plan.no_writes is False
    record = audit_record(failure.value.plan, mutation=failure.value.mutation)
    assert record["audit"]["outcome"] == "mutation-unknown"
    assert record["audit"]["no_writes"] is False
    assert "re-read" in record["audit"]["recovery_guidance"]
    assert adapter.calls == ["tag", "release"]


def test_live_cli_requires_protected_execution_flag(tmp_path: Path) -> None:
    live = request(mode="live", authorization="RECOVER_RELEASE_LIVE")
    request_path = tmp_path / "request.json"
    snapshot_path = tmp_path / "snapshot.json"
    request_path.write_text(json.dumps(live.__dict__), encoding="utf-8")
    snapshot_path.write_text(json.dumps(ResourceSnapshot().__dict__), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "recover_release.py"), "--request", str(request_path), "--snapshot", str(snapshot_path)],
        check=False, capture_output=True, text=True,
    )

    assert result.returncode == 2
    assert "protected" in json.loads(result.stdout)["audit"]["error"]


def test_live_cli_requires_confirmation_marker(tmp_path: Path) -> None:
    live = request(mode="live", authorization=LIVE_CONFIRMATION)
    request_path = tmp_path / "request.json"
    snapshot_path = tmp_path / "snapshot.json"
    request_path.write_text(json.dumps(live.__dict__), encoding="utf-8")
    snapshot_path.write_text(json.dumps(ResourceSnapshot().__dict__), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "recover_release.py"),
            "--request",
            str(request_path),
            "--snapshot",
            str(snapshot_path),
            "--execute-live",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "confirmation" in json.loads(result.stdout)["audit"]["error"]


def test_dry_run_cli_supports_an_explicit_no_write_plan(tmp_path: Path) -> None:
    dry_run = request()
    request_path = tmp_path / "request.json"
    snapshot_path = tmp_path / "snapshot.json"
    request_path.write_text(json.dumps(dry_run.__dict__), encoding="utf-8")
    snapshot_path.write_text(json.dumps(ResourceSnapshot().__dict__), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "recover_release.py"),
            "--request",
            str(request_path),
            "--snapshot",
            str(snapshot_path),
            "--plan-only",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    record = json.loads(result.stdout)
    assert record["mode"] == "dry-run"
    assert record["audit"]["outcome"] == "planned"
    assert record["audit"]["no_writes"] is True


def test_live_cli_requires_a_github_token(tmp_path: Path) -> None:
    live = request(mode="live", authorization=LIVE_CONFIRMATION)
    request_path = tmp_path / "request.json"
    snapshot_path = tmp_path / "snapshot.json"
    request_path.write_text(json.dumps(live.__dict__), encoding="utf-8")
    snapshot_path.write_text(json.dumps(ResourceSnapshot().__dict__), encoding="utf-8")
    environment = {
        key: value
        for key, value in __import__("os").environ.items()
        if key not in {"GH_TOKEN", "GITHUB_TOKEN"}
    }

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "recover_release.py"),
            "--request",
            str(request_path),
            "--snapshot",
            str(snapshot_path),
            "--execute-live",
            "--confirm-live",
            LIVE_CONFIRMATION,
            "--expected-repository",
            REPOSITORY,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 2
    assert "GH_TOKEN" in json.loads(result.stdout)["audit"]["error"]


def test_live_cli_refuses_a_server_without_independent_preflight(tmp_path: Path) -> None:
    request_path = tmp_path / "request.json"
    snapshot_path = tmp_path / "snapshot.json"
    request_path.write_text(
        json.dumps(request(mode="live", authorization=LIVE_CONFIRMATION).__dict__),
        encoding="utf-8",
    )
    snapshot_path.write_text(json.dumps(ResourceSnapshot().__dict__), encoding="utf-8")
    expected_tag_path = f"/repos/{REPOSITORY}/git/ref/tags/{TAG}"
    expected_release_path = f"/repos/{REPOSITORY}/releases/tags/{TAG}"
    calls: list[tuple[str, str, object]] = []
    tag_payload = {
        "ref": f"refs/tags/{TAG}",
        "object": {"sha": SHA, "type": "commit"},
    }
    release_payload = {
        "id": 75,
        "tag_name": TAG,
        "target_commitish": SHA,
        "release_version": VERSION,
        "body": "Historical release recovery",
        "draft": False,
        "prerelease": False,
    }

    class Handler(BaseHTTPRequestHandler):
        def _respond(self, status: int, payload: object) -> None:
            encoded = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self) -> None:  # noqa: N802
            calls.append(("GET", self.path, None))
            if self.path == expected_tag_path:
                tag_calls = sum(1 for method, path, _ in calls if method == "GET" and path == expected_tag_path)
                self._respond(404 if tag_calls == 1 else 200, {"message": "Not Found"} if tag_calls == 1 else tag_payload)
                return
            if self.path == expected_release_path:
                release_calls = sum(1 for method, path, _ in calls if method == "GET" and path == expected_release_path)
                self._respond(404 if release_calls < 3 else 200, {"message": "Not Found"} if release_calls < 3 else release_payload)
                return
            self._respond(404, {"message": "Not Found"})

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            calls.append(("POST", self.path, body))
            if self.path == f"/repos/{REPOSITORY}/git/refs":
                self._respond(201, tag_payload)
                return
            if self.path == f"/repos/{REPOSITORY}/releases":
                self._respond(201, release_payload)
                return
            self._respond(404, {"message": "Not Found"})

        def log_message(self, _: str, *__: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    server.block_on_close = False
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        environment = {**os.environ, "GH_TOKEN": "loopback-token"}
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "recover_release.py"),
                "--request",
                str(request_path),
                "--snapshot",
                str(snapshot_path),
                "--execute-live",
                "--confirm-live",
                LIVE_CONFIRMATION,
                    "--github-api-url",
                    f"http://127.0.0.1:{server.server_port}",
                    "--lock-path",
                    str(tmp_path / "recovery.lock"),
                    "--expected-repository",
                    REPOSITORY,
                    "--expected-default-branch",
                    "main",
                    "--expected-tag",
                    TAG,
                    "--expected-merged-sha",
                    SHA,
                    "--expected-idempotency-key",
                    KEY,
                ],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert result.returncode == 2, result.stderr
    record = json.loads(result.stdout)
    assert record["audit"]["outcome"] == "refusal"
    assert record["audit"]["no_writes"] is True
    assert [method for method, _, _ in calls] == ["GET"]
    assert calls[0][1] == f"/repos/{REPOSITORY}"


def test_live_execution_returns_first_mutation_audit_when_tag_already_present(tmp_path: Path) -> None:
    """A second live run with the tag already at the merged SHA must be a no-op and
    must not call the write methods. The plan must still carry an idempotency-aware
    outcome and the audit must include the no-writes semantics."""

    class SnapshotAdapter:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def snapshot(self, _: RecoveryRequest) -> ResourceSnapshot:
            self.calls.append("snapshot")
            return ResourceSnapshot(
                tag_exists=True,
                tag_sha=SHA,
                tag_type="commit",
                release_exists=True,
                release_tag=TAG,
                release_sha=SHA,
                release_version=VERSION,
            )

        def preflight(self, _: RecoveryRequest) -> RecoveryPreflight:
            return RecoveryPreflight(
                repository=REPOSITORY,
                default_branch="main",
                pull_request=75,
                merged_sha=SHA,
                historical_tree=TREE,
                historical_manifest=MANIFEST,
                historical_entry_count=13,
                current_entry_count=14,
                graph_mismatch=True,
                artifact_plan=ARTIFACT_PLAN,
                current_manifest_digest="b" * 64,
                snapshot=self.snapshot(_),
            )

        def create_tag(self, _: RecoveryRequest) -> None:
            self.calls.append("tag")

        def create_release(self, _: RecoveryRequest) -> None:
            self.calls.append("release")

    live = request(mode="live", authorization="RECOVER_RELEASE_LIVE")
    adapter = SnapshotAdapter()

    plan = execute_recovery(
        live,
        adapter,
        lock_path=tmp_path / "recovery.lock",
        confirmation=LIVE_CONFIRMATION,
    )

    assert adapter.calls == ["snapshot"]
    assert plan.outcome == "no-op"
    assert plan.intended_operations == ()
    assert plan.no_writes is True


def test_dry_run_audit_records_are_machine_and_human_consistent(tmp_path: Path) -> None:
    """The dry-run audit must reproduce the deterministic machine/human pair end to end."""

    audit_machine = tmp_path / "audit" / "record.json"
    audit_human = tmp_path / "audit" / "record.txt"
    request_path = tmp_path / "request.json"
    snapshot_path = tmp_path / "snapshot.json"
    request_path.write_text(json.dumps(request().__dict__), encoding="utf-8")
    snapshot_path.write_text(json.dumps(ResourceSnapshot().__dict__), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "recover_release.py"),
            "--request", str(request_path),
            "--snapshot", str(snapshot_path),
            "--audit-output", str(audit_machine),
            "--human-output", str(audit_human),
        ],
        check=True, capture_output=True, text=True,
    )

    machine = json.loads(audit_machine.read_text(encoding="utf-8"))
    human = audit_human.read_text(encoding="utf-8")

    assert machine["status"] == "planned"
    assert machine["audit"]["outcome"] == "planned"
    assert machine["audit"]["no_writes"] is True
    assert machine["audit"]["error"] is None
    assert machine["intended_operations"] == ["create-canonical-tag", "create-github-release"]
    assert machine["idempotency_key"] == KEY
    assert machine["provenance_digest"] == _provenance_digest(request())
    assert "NO_WRITES: True" in human
    assert f"tag: {TAG}" in human
    assert f"target SHA: {SHA}" in human
    assert result.returncode == 0


def _provenance_digest(req: RecoveryRequest) -> str:
    from recover_release import _provenance_digest as derive

    return derive(req)
