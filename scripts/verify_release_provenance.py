#!/usr/bin/env python3
"""Verify release identity, package versions, archive manifests, and binary evidence.

The script is deliberately local and side-effect free apart from writing the requested
binary-evidence file.  GitHub publication jobs call it after checking out the exact
release-please SHA; local tests can exercise the pure validators without credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - CI uses modern Python
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "yacosta738/codegauge"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SEMVER_NUMERIC_IDENTIFIER = r"(?:0|[1-9][0-9]*)"
SEMVER_PRERELEASE_IDENTIFIER = (
    rf"(?:{SEMVER_NUMERIC_IDENTIFIER}|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
)
SEMVER_BUILD_IDENTIFIER = r"[0-9A-Za-z-]+"
SEMVER_CORE = (
    rf"{SEMVER_NUMERIC_IDENTIFIER}\."
    rf"{SEMVER_NUMERIC_IDENTIFIER}\."
    rf"{SEMVER_NUMERIC_IDENTIFIER}"
    rf"(?:-(?:{SEMVER_PRERELEASE_IDENTIFIER})"
    rf"(?:\.(?:{SEMVER_PRERELEASE_IDENTIFIER}))*)?"
    rf"(?:\+(?:{SEMVER_BUILD_IDENTIFIER})"
    rf"(?:\.(?:{SEMVER_BUILD_IDENTIFIER}))*)?"
)
SEMVER_RE = re.compile(rf"^v{SEMVER_CORE}$")
VERSION_RE = re.compile(rf"^{SEMVER_CORE}$")
RUNTIME_CRATES = (
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-cli",
)
NPM_PACKAGES = (
    "@yacosta738/codegauge-linux-x64-gnu",
    "@yacosta738/codegauge-linux-arm64-gnu",
    "@yacosta738/codegauge-darwin-x64",
    "@yacosta738/codegauge-darwin-arm64",
    "@yacosta738/codegauge-win32-x64-msvc",
    "@yacosta738/codegauge-win32-arm64-msvc",
)
TARGET_EXTENSIONS = {
    "x86_64-unknown-linux-gnu": "tar.gz",
    "aarch64-unknown-linux-gnu": "tar.gz",
    "x86_64-unknown-linux-musl": "tar.gz",
    "aarch64-unknown-linux-musl": "tar.gz",
    "x86_64-apple-darwin": "tar.gz",
    "aarch64-apple-darwin": "tar.gz",
    "x86_64-pc-windows-msvc": "zip",
    "aarch64-pc-windows-msvc": "zip",
}
RELEASE_PR_LABEL = "autorelease: pending"
ROOT_EXTRA_FILES = (
    {
        "type": "toml",
        "path": "/Cargo.toml",
        "jsonpath": "$.workspace.package.version",
    },
    {
        "type": "toml",
        "path": "/Cargo.lock",
        "jsonpath": (
            '$.package[?(@.name.value == "codegauge-model" || '
            '@.name.value == "codegauge-core" || '
            '@.name.value == "codegauge-application" || '
            '@.name.value == "codegauge-provider-jacoco" || '
            '@.name.value == "codegauge-cli")].version'
        ),
    },
    {
        "type": "toml",
        "path": "/crates/codegauge-core/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-model"].version',
    },
    {
        "type": "toml",
        "path": "/crates/codegauge-application/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-core"].version',
    },
    {
        "type": "toml",
        "path": "/crates/codegauge-application/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-model"].version',
    },
    {
        "type": "toml",
        "path": "/crates/codegauge-provider-jacoco/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-application"].version',
    },
    {
        "type": "toml",
        "path": "/crates/codegauge-provider-jacoco/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-model"].version',
    },
    {
        "type": "toml",
        "path": "/crates/codegauge-cli/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-application"].version',
    },
    {
        "type": "toml",
        "path": "/crates/codegauge-cli/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-model"].version',
    },
    {
        "type": "toml",
        "path": "/crates/codegauge-cli/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-provider-jacoco"].version',
    },
    {"type": "generic", "path": "/README.md"},
    {"type": "generic", "path": "/tests/golden/valid-methods.json"},
    {"type": "generic", "path": "/crates/codegauge-model/tests/contracts.rs"},
    {"type": "generic", "path": "/crates/codegauge-cli/tests/cli.rs"},
)
ROOT_CARRIER_PATHS = frozenset(
    extra_file["path"].removeprefix("/")
    for extra_file in ROOT_EXTRA_FILES
    if isinstance(extra_file, dict) and extra_file["path"].startswith("/")
)
RUNTIME_GRAPH_PATHS = frozenset(
    {
        ".",
        "crates/codegauge-model",
        "crates/codegauge-core",
        "crates/codegauge-application",
        "crates/codegauge-provider-jacoco",
        "crates/codegauge-cli",
        "npm/codegauge",
        "npm/packages/codegauge-linux-x64-gnu",
        "npm/packages/codegauge-linux-arm64-gnu",
        "npm/packages/codegauge-darwin-x64",
        "npm/packages/codegauge-darwin-arm64",
        "npm/packages/codegauge-win32-x64-msvc",
        "npm/packages/codegauge-win32-arm64-msvc",
    }
)
EXPECTED_RELEASE_MANIFEST_PATHS = RUNTIME_GRAPH_PATHS
NPM_PACKAGE_DIFF_PATHS = frozenset(
    {
        "npm/codegauge/package.json",
        *{
            f"npm/packages/{package.removeprefix('@yacosta738/')}/package.json"
            for package in NPM_PACKAGES
        },
    }
)
RUNTIME_CHANGELOG_PATHS = frozenset(
    {
        *{
            f"crates/{crate}/CHANGELOG.md" for crate in RUNTIME_CRATES
        },
        "npm/codegauge/CHANGELOG.md",
        *{
            path.removesuffix("package.json") + "CHANGELOG.md"
            for path in NPM_PACKAGE_DIFF_PATHS
            if path.startswith("npm/packages/")
        },
    }
)
ALLOWED_STAGE_A_DIFFS = (
    frozenset(
        {
            "Cargo.toml",
            "Cargo.lock",
            ".release-please-manifest.json",
            "README.md",
            "tests/golden/valid-methods.json",
            "crates/codegauge-model/tests/contracts.rs",
            "crates/codegauge-cli/tests/cli.rs",
        }
    )
    | frozenset({f"crates/{crate}/Cargo.toml" for crate in RUNTIME_CRATES})
    | NPM_PACKAGE_DIFF_PATHS
    | RUNTIME_CHANGELOG_PATHS
)


class ProvenanceError(ValueError):
    """Raised when a release input or artifact is not release-safe."""


@dataclass(frozen=True)
class CarrierRecord:
    """Auditable result of validating one merged Stage-A version PR."""

    version: str
    tag: str
    merge_sha: str
    version_pr_number: int


@dataclass(frozen=True)
class CarrierTagPlan:
    """Compare-and-create decision for the one canonical release tag."""

    action: str
    version: str
    tag: str
    sha: str


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProvenanceError(f"unable to read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ProvenanceError(f"JSON {path} must contain an object")
    return value


def require_sha(value: str, field: str) -> str:
    if not SHA_RE.fullmatch(value):
        raise ProvenanceError(f"{field} must be a 40-character lowercase Git SHA")
    return value


def version_from_tag(tag: str) -> str:
    match = SEMVER_RE.fullmatch(tag)
    if not match:
        raise ProvenanceError(f"release tag must be an exact v-prefixed semver: {tag}")
    return tag[1:]


def validate_release_version(version: str) -> str:
    """Validate a carrier version and reject the bootstrap metadata version."""

    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        raise ProvenanceError(f"release version is not a valid semver: {version}")
    if version == "0.1.0":
        raise ProvenanceError("bootstrap version 0.1.0 cannot become a release tag")
    return version


def validate_release_identity(
    *,
    release_tag: str,
    release_sha: str,
    main_sha: str,
    tag_revision: str,
    main_revision: str,
) -> str:
    """Validate the exact release-please tag and its merged-main revision.

    Both the release-please output SHA and the expected merged-main SHA are checked
    against the resolved tag.  A tag that merely happens to match the semver shape
    cannot pass this boundary.
    """

    version = version_from_tag(release_tag)
    require_sha(release_sha, "release_sha")
    require_sha(main_sha, "main_sha")
    require_sha(tag_revision, "tag revision")
    require_sha(main_revision, "main revision")
    if tag_revision != release_sha:
        raise ProvenanceError("release-please tag does not resolve to release_sha")
    if tag_revision != main_sha or main_revision != main_sha:
        raise ProvenanceError("release tag does not point to the expected merged-main commit")
    return version


def read_workspace_version(root: Path = ROOT) -> str:
    if tomllib is None:
        raise ProvenanceError("Python tomllib is required for release provenance checks")
    try:
        document = tomllib.loads((root / "Cargo.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ProvenanceError(f"unable to read workspace Cargo.toml: {error}") from error
    version = document.get("workspace", {}).get("package", {}).get("version")
    if not isinstance(version, str):
        raise ProvenanceError("workspace Cargo.toml has no package version")
    return version


def validate_package_versions(version: str, root: Path = ROOT) -> None:
    """Assert the Cargo and all twelve npm package manifests share one version."""

    if read_workspace_version(root) != version:
        raise ProvenanceError("Cargo workspace version does not match the release tag")

    lock_path = root / "Cargo.lock"
    if not lock_path.is_file():
        raise ProvenanceError("Cargo.lock is required for release provenance")
    lock_text = lock_path.read_text(encoding="utf-8")
    for crate in RUNTIME_CRATES:
        match = re.search(rf'name = "{re.escape(crate)}"\s+version = "([^"]+)"', lock_text)
        if not match or match.group(1) != version:
            raise ProvenanceError(f"Cargo.lock version drift for {crate}")

    for crate in RUNTIME_CRATES:
        path = root / "crates" / crate / "Cargo.toml"
        if not path.is_file() or tomllib is None:
            raise ProvenanceError(f"missing Cargo manifest for {crate}")
        package = tomllib.loads(path.read_text(encoding="utf-8")).get("package", {})
        if package.get("version") != version:
            raise ProvenanceError(f"{crate} Cargo manifest version does not match the workspace version")

    base_path = root / "npm" / "codegauge" / "package.json"
    base = load_json(base_path)
    if base.get("name") != "@yacosta738/codegauge" or base.get("version") != version:
        raise ProvenanceError("npm base package version/name does not match the release tag")
    optional = base.get("optionalDependencies")
    if not isinstance(optional, dict) or set(optional) != set(NPM_PACKAGES):
        raise ProvenanceError("npm base package does not declare exactly six approved platform packages")
    if any(value != version for value in optional.values()):
        raise ProvenanceError("npm optional dependency pins do not match the release tag")

    for package_name in NPM_PACKAGES:
        package_path = root / "npm" / "packages" / package_name.removeprefix("@yacosta738/") / "package.json"
        package = load_json(package_path)
        if package.get("name") != package_name or package.get("version") != version:
            raise ProvenanceError(f"npm platform package version drift: {package_name}")


def validate_linked_components(root: Path = ROOT) -> None:
    config = load_json(root / "release-please-config.json")
    linked = [
        component
        for plugin in config.get("plugins", [])
        if isinstance(plugin, dict) and plugin.get("type") == "linked-versions"
        for component in plugin.get("components", [])
    ]
    expected = {"codegauge-root"} | {crate for crate in RUNTIME_CRATES} | {"codegauge"} | {
        package.removeprefix("@yacosta738/") for package in NPM_PACKAGES
    }
    missing = sorted(expected - set(linked))
    if missing:
        raise ProvenanceError(f"release-please linked-versions is missing: {', '.join(missing)}")
    extra = sorted(set(linked) - expected)
    if extra:
        raise ProvenanceError(f"release-please linked-versions contains unapproved components: {', '.join(extra)}")


def validate_stage_a_configuration(root: Path = ROOT) -> None:
    """Validate the release-free, component-tagged Release Please manifest."""

    config = load_json(root / "release-please-config.json")
    if config.get("include-component-in-tag") is not True:
        raise ProvenanceError("Stage A must enable component-tagged strategy components")
    if config.get("skip-github-release") is not True:
        raise ProvenanceError("Stage A must skip all Release Please releases")
    if config.get("separate-pull-requests") is not False:
        raise ProvenanceError("Stage A must create one synchronized release PR")
    if "extra-files" in config:
        raise ProvenanceError("root extra-files must be owned by the effective root candidate")

    packages = config.get("packages")
    if not isinstance(packages, dict):
        raise ProvenanceError("release-please packages must be an object")
    expected_paths = {
        ".",
        "crates/codegauge-model",
        "crates/codegauge-core",
        "crates/codegauge-application",
        "crates/codegauge-provider-jacoco",
        "crates/codegauge-cli",
        "npm/codegauge",
        "npm/packages/codegauge-linux-x64-gnu",
        "npm/packages/codegauge-linux-arm64-gnu",
        "npm/packages/codegauge-darwin-x64",
        "npm/packages/codegauge-darwin-arm64",
        "npm/packages/codegauge-win32-x64-msvc",
        "npm/packages/codegauge-win32-arm64-msvc",
    }
    if set(packages) != expected_paths:
        raise ProvenanceError("Stage A package candidates do not match the approved runtime graph")
    if "crates/codegauge-conformance" in packages:
        raise ProvenanceError("private conformance must not be a Release Please candidate")

    root_package = packages.get(".")
    if not isinstance(root_package, dict):
        raise ProvenanceError("Stage A requires an explicit root metadata carrier")
    if root_package.get("component") != "codegauge-root":
        raise ProvenanceError("root metadata carrier component drift")
    if root_package.get("release-type") != "java":
        raise ProvenanceError("virtual Cargo root must use the non-Cargo metadata strategy")
    if root_package.get("initial-version") != "0.1.0":
        raise ProvenanceError("root metadata carrier initial version drift")
    if (
        root_package.get("skip-github-release") is not True
        or root_package.get("skip-changelog") is not True
        or root_package.get("skip-snapshot") is not True
        or "package-name" in root_package
    ):
        raise ProvenanceError("root metadata carrier must not publish as a package")
    if tuple(root_package.get("extra-files", [])) != ROOT_EXTRA_FILES:
        raise ProvenanceError("root metadata carrier extra-files drift")

    for path, package in packages.items():
        if not isinstance(package, dict):
            raise ProvenanceError(f"invalid Release Please package config: {path}")
        if package.get("skip-github-release", True) is not True:
            raise ProvenanceError(f"Stage A package can create a release: {path}")
    npm_package = packages.get("npm/codegauge", {})
    if npm_package.get("extra-files") != [
        {"type": "json", "path": "package.json", "jsonpath": "$.version"}
    ]:
        raise ProvenanceError("npm wrapper extra-file must be package-relative")

    node_plugins = [
        plugin
        for plugin in config.get("plugins", [])
        if isinstance(plugin, dict) and plugin.get("type") == "node-workspace"
    ]
    if node_plugins != [{"type": "node-workspace", "merge": False}]:
        raise ProvenanceError("Stage A requires one non-merging node-workspace plugin")
    validate_linked_components(root)


def validate_release_manifest(version: str, root: Path = ROOT) -> None:
    """Validate the Release Please manifest as immutable release metadata."""

    manifest = load_json(root / ".release-please-manifest.json")
    if set(manifest) != EXPECTED_RELEASE_MANIFEST_PATHS:
        raise ProvenanceError("release-please manifest paths do not match the approved runtime graph")
    for path, value in manifest.items():
        if value != version:
            raise ProvenanceError(f"release-please manifest version drift for {path}")


def validate_private_boundaries(root: Path = ROOT) -> None:
    """Keep the virtual root and conformance package outside publication."""

    if tomllib is None:
        raise ProvenanceError("Python tomllib is required for private boundary checks")
    try:
        document = tomllib.loads(
            (root / "crates" / "codegauge-conformance" / "Cargo.toml").read_text(
                encoding="utf-8"
            )
        )
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ProvenanceError(f"unable to read private conformance manifest: {error}") from error
    package = document.get("package", {})
    if package.get("name") != "codegauge-conformance" or package.get("publish") is not False:
        raise ProvenanceError("codegauge-conformance must remain a private non-publishable package")
    config = load_json(root / "release-please-config.json")
    linked = {
        component
        for plugin in config.get("plugins", [])
        if isinstance(plugin, dict) and plugin.get("type") == "linked-versions"
        for component in plugin.get("components", [])
    }
    if "codegauge-conformance" in linked or "crates/codegauge-conformance" in config.get("packages", {}):
        raise ProvenanceError("private conformance must not be release-linked")


def validate_root_carrier_files(root: Path = ROOT) -> None:
    """Require every baseline file owned by the Java root metadata carrier."""

    missing = sorted(
        path for path in ROOT_CARRIER_PATHS if not (root / path).is_file()
    )
    if missing:
        raise ProvenanceError(
            "root metadata carrier is missing required files: " + ", ".join(missing)
        )


def validate_carrier_metadata(version: str, root: Path = ROOT) -> None:
    """Validate Stage-A config, manifest, and private package boundaries."""

    validate_stage_a_configuration(root)
    validate_release_manifest(version, root)
    validate_private_boundaries(root)


def validate_clean_checkout(root: Path = ROOT) -> None:
    """Reject a carrier checkout that is not exactly the event tree."""

    try:
        result = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ProvenanceError(f"unable to inspect carrier checkout: {error}") from error
    if result.stdout.strip():
        raise ProvenanceError("carrier checkout is dirty")


def _pull_request_labels(pull_request: dict[str, Any]) -> set[str]:
    labels = pull_request.get("labels", [])
    if not isinstance(labels, list):
        return set()
    return {
        label.get("name") if isinstance(label, dict) else label
        for label in labels
        if isinstance(label, dict) and isinstance(label.get("name"), str)
        or isinstance(label, str)
    }


def _is_release_please_pr(pull_request: Any) -> bool:
    if not isinstance(pull_request, dict):
        return False
    base = pull_request.get("base", {})
    base_ref = base.get("ref") if isinstance(base, dict) else pull_request.get("base_ref")
    base_repository = base.get("repo", {}).get("full_name") if isinstance(base, dict) else None
    merged = bool(pull_request.get("merged_at") or pull_request.get("merged"))
    title = pull_request.get("title", "")
    body = pull_request.get("body") or ""
    return (
        base_ref == "main"
        and (base_repository is None or base_repository == REPOSITORY)
        and merged
        and RELEASE_PR_LABEL in _pull_request_labels(pull_request)
        and isinstance(title, str)
        and "release" in title.lower()
        and isinstance(body, str)
        and "Release Please" in body
    )


def _validate_pull_request_record(pull_request: Any, index: int) -> dict[str, Any]:
    """Validate the GitHub pull-request shape before classifying a carrier event."""

    if not isinstance(pull_request, dict):
        raise ProvenanceError(f"pull request entry {index} must be an object")
    required = {
        "number",
        "title",
        "body",
        "labels",
        "base",
        "merged_at",
        "merge_commit_sha",
    }
    missing = sorted(required - set(pull_request))
    if missing:
        raise ProvenanceError(
            f"pull request entry {index} is missing fields: {', '.join(missing)}"
        )

    number = pull_request["number"]
    if isinstance(number, bool) or not isinstance(number, int) or number <= 0:
        raise ProvenanceError(f"pull request entry {index} has an invalid number")
    if not isinstance(pull_request["title"], str):
        raise ProvenanceError(f"pull request entry {index} has an invalid title")
    if pull_request["body"] is not None and not isinstance(pull_request["body"], str):
        raise ProvenanceError(f"pull request entry {index} has an invalid body")

    base = pull_request["base"]
    if not isinstance(base, dict) or not isinstance(base.get("ref"), str):
        raise ProvenanceError(f"pull request entry {index} has an invalid base")
    base_repository = base.get("repo")
    if base_repository is not None and (
        not isinstance(base_repository, dict)
        or not isinstance(base_repository.get("full_name"), str)
    ):
        raise ProvenanceError(f"pull request entry {index} has an invalid base repository")

    labels = pull_request["labels"]
    if not isinstance(labels, list) or any(
        not isinstance(label, dict) or not isinstance(label.get("name"), str)
        for label in labels
    ):
        raise ProvenanceError(f"pull request entry {index} has invalid labels")

    merged_at = pull_request["merged_at"]
    if merged_at is not None and not isinstance(merged_at, str):
        raise ProvenanceError(f"pull request entry {index} has an invalid merged_at value")
    merge_commit_sha = pull_request["merge_commit_sha"]
    if merge_commit_sha is not None:
        if not isinstance(merge_commit_sha, str):
            raise ProvenanceError(
                f"pull request entry {index} has an invalid merge_commit_sha"
            )
        require_sha(merge_commit_sha, f"pull request entry {index} merge_commit_sha")
    return pull_request


def select_matching_release_please_prs(
    pull_requests: Any, event_sha: str
) -> list[dict[str, Any]]:
    """Return Release Please PRs merged exactly at the trusted event SHA."""

    event_sha = require_sha(event_sha, "event SHA")
    if not isinstance(pull_requests, list):
        raise ProvenanceError("pull requests JSON must contain an array")
    validated = [
        _validate_pull_request_record(pull_request, index)
        for index, pull_request in enumerate(pull_requests)
    ]
    return [
        pull_request
        for pull_request in validated
        if _is_release_please_pr(pull_request)
        and pull_request["merge_commit_sha"] == event_sha
    ]


def classify_carrier_prs(pull_requests: Any, event_sha: str) -> dict[str, Any]:
    """Classify a trusted main event before any carrier validation or mutation."""

    matching = select_matching_release_please_prs(pull_requests, event_sha)
    if len(matching) > 1:
        raise ProvenanceError(
            "expected at most one merged Release Please PR for the event SHA, "
            f"found {len(matching)}"
        )
    if not matching:
        return {
            "status": "skipped",
            "reason": "no-matching-release-please-pr",
            "matching_release_pr_count": 0,
        }
    return {
        "status": "matched",
        "matching_release_pr_count": 1,
        "version_pr_number": matching[0]["number"],
    }


def validate_stage_a_diff(changed_files: list[Any]) -> None:
    """Allow only the synchronized version-PR file boundary."""

    paths: list[str] = []
    for entry in changed_files:
        path = entry.get("filename") if isinstance(entry, dict) else entry
        if not isinstance(path, str) or not path:
            raise ProvenanceError("release PR diff contains invalid file metadata")
        normalized = path[2:] if path.startswith("./") else path
        paths.append(normalized)
        if normalized not in ALLOWED_STAGE_A_DIFFS:
            raise ProvenanceError(f"release PR diff contains an unapproved path: {normalized}")
    if not paths:
        raise ProvenanceError("release PR diff is empty")
    if not {"Cargo.toml", "Cargo.lock", ".release-please-manifest.json"}.intersection(paths):
        raise ProvenanceError("release PR diff is missing root Cargo/release metadata")
    if not any(path.startswith("npm/") for path in paths):
        raise ProvenanceError("release PR diff is missing npm runtime metadata")


def validate_carrier_event(
    *,
    event_name: str,
    ref: str,
    event_sha: str,
    pull_requests: list[Any],
    changed_files: list[Any],
    root: Path = ROOT,
    require_clean: bool = False,
) -> CarrierRecord:
    """Validate one trusted main event and its merged Stage-A version PR."""

    if event_name not in {"push", "workflow_dispatch"} or ref != "refs/heads/main":
        raise ProvenanceError(
            "carrier accepts only push or workflow_dispatch events on refs/heads/main"
        )
    event_sha = require_sha(event_sha, "event SHA")
    if require_clean:
        validate_clean_checkout(root)
    version = validate_carrier_tree(root)
    candidates = select_matching_release_please_prs(pull_requests, event_sha)
    if len(candidates) != 1:
        raise ProvenanceError(
            "expected exactly one merged Release Please PR for the event SHA, "
            f"found {len(candidates)}"
        )
    pull_request = candidates[0]
    body = pull_request.get("body") or ""
    if body.count("---") < 2 or version not in body:
        raise ProvenanceError("merged Release Please PR body is not a synchronized version PR")
    validate_stage_a_diff(changed_files)
    number = pull_request.get("number")
    if not isinstance(number, int) or number <= 0:
        raise ProvenanceError("merged Release Please PR number is invalid")
    return CarrierRecord(
        version=version,
        tag=f"v{version}",
        merge_sha=event_sha,
        version_pr_number=number,
    )


def validate_carrier_release_slot(*, existing_release: bool) -> None:
    """Fail closed if an untagged version already has a GitHub Release."""

    if existing_release:
        raise ProvenanceError("canonical GitHub Release already exists before tag creation")


def plan_carrier_tag(
    version: str,
    expected_sha: str,
    *,
    existing_type: str | None = None,
    existing_sha: str | None = None,
    existing_release: bool = False,
) -> CarrierTagPlan:
    """Return create/no-op or reject a conflicting canonical tag state."""

    version = validate_release_version(version)
    expected_sha = require_sha(expected_sha, "expected tag SHA")
    tag = f"v{version}"
    if existing_type is None and existing_sha is None:
        validate_carrier_release_slot(existing_release=existing_release)
        return CarrierTagPlan("create", version, tag, expected_sha)
    if existing_type != "commit" or existing_sha is None:
        raise ProvenanceError("canonical tag must be an existing lightweight commit ref")
    existing_sha = require_sha(existing_sha, "existing tag SHA")
    if existing_sha == expected_sha:
        return CarrierTagPlan("noop", version, tag, expected_sha)
    raise ProvenanceError("canonical tag already points to a different commit")


def validate_carrier_tree(root: Path = ROOT) -> str:
    """Derive and validate the release version from the merged main tree."""

    validate_root_carrier_files(root)
    version = validate_release_version(read_workspace_version(root))
    validate_package_versions(version, root)
    validate_carrier_metadata(version, root)
    return version


def validate_archive_manifest(path: Path, version: str, source_revision: str) -> dict[str, Any]:
    manifest = load_json(path)
    target = manifest.get("target")
    archive = manifest.get("archive")
    digest = manifest.get("sha256")
    if manifest.get("version") != version:
        raise ProvenanceError(f"{path.name} version drift")
    if manifest.get("source_revision") != source_revision:
        raise ProvenanceError(f"{path.name} immutable source revision drift")
    if manifest.get("rust_toolchain") != "1.97.1":
        raise ProvenanceError(f"{path.name} Rust toolchain drift")
    if target not in TARGET_EXTENSIONS:
        raise ProvenanceError(f"{path.name} contains an unapproved target")
    expected_archive = f"codegauge-{version}-{target}.{TARGET_EXTENSIONS[target]}"
    if archive != expected_archive:
        raise ProvenanceError(f"{path.name} archive name drift")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ProvenanceError(f"{path.name} must contain a lowercase SHA-256 digest")
    evidence = manifest.get("binary_evidence")
    if not isinstance(evidence, dict) or evidence.get("target") != target:
        raise ProvenanceError(f"{path.name} is missing target-aware binary evidence")
    if evidence.get("mode") == "native":
        if evidence.get("execution") != "native":
            raise ProvenanceError(f"{path.name} native evidence is not executable evidence")
        if evidence.get("version") != f"codegauge {version}\n" or evidence.get("profiles") != "java-jacoco-v1\n":
            raise ProvenanceError(f"{path.name} native version/profiles evidence drift")
    elif evidence.get("mode") == "cross-target":
        if evidence.get("execution") != "not-run":
            raise ProvenanceError(f"{path.name} cross-target evidence must state execution was not run")
    else:
        raise ProvenanceError(f"{path.name} has an unknown binary evidence mode")
    return manifest


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive_set(release_out: Path, version: str, source_revision: str) -> None:
    manifests = sorted(release_out.glob("release-manifest-*.json"))
    if len(manifests) != len(TARGET_EXTENSIONS):
        raise ProvenanceError(f"expected {len(TARGET_EXTENSIONS)} archive manifests, found {len(manifests)}")
    seen_targets: set[str] = set()
    for manifest_path in manifests:
        manifest = validate_archive_manifest(manifest_path, version, source_revision)
        target = str(manifest["target"])
        if target in seen_targets:
            raise ProvenanceError(f"duplicate archive target evidence: {target}")
        seen_targets.add(target)
        archive_path = release_out / str(manifest["archive"])
        sidecar_path = release_out / f"{archive_path.name}.sha256"
        if not archive_path.is_file() or not sidecar_path.is_file():
            raise ProvenanceError(f"missing archive or checksum sidecar for {target}")
        recorded_digest, recorded_name = sidecar_path.read_text(encoding="utf-8").split()
        if recorded_name != archive_path.name or recorded_digest != manifest["sha256"]:
            raise ProvenanceError(f"{target} checksum sidecar does not match its manifest")
        if sha256(archive_path) != recorded_digest:
            raise ProvenanceError(f"{target} archive checksum mismatch")
    if seen_targets != set(TARGET_EXTENSIONS):
        raise ProvenanceError("archive matrix is incomplete")


def write_binary_evidence(
    *,
    binary: Path,
    version: str,
    target: str,
    mode: str,
    output: Path,
) -> None:
    if target not in TARGET_EXTENSIONS:
        raise ProvenanceError(f"unapproved binary target: {target}")
    if not binary.is_file():
        raise ProvenanceError(f"release binary does not exist: {binary}")
    if mode == "native":
        try:
            version_output = subprocess.run([str(binary), "version"], check=True, capture_output=True, text=True).stdout
            profiles_output = subprocess.run([str(binary), "profiles"], check=True, capture_output=True, text=True).stdout
        except (OSError, subprocess.CalledProcessError) as error:
            raise ProvenanceError(f"native release binary smoke test failed: {error}") from error
        evidence: dict[str, Any] = {
            "mode": "native",
            "target": target,
            "execution": "native",
            "version": version_output,
            "profiles": profiles_output,
        }
        if version_output != f"codegauge {version}\n" or profiles_output != "java-jacoco-v1\n":
            raise ProvenanceError("native release binary version/profiles do not match release metadata")
    elif mode == "cross-target":
        evidence = {
            "mode": "cross-target",
            "target": target,
            "execution": "not-run",
            "reason": "target-aware evidence recorded without pretending the binary is native",
        }
    else:
        raise ProvenanceError("binary evidence mode must be native or cross-target")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def git_revision(ref: str) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", f"{ref}^{{commit}}"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ProvenanceError(f"unable to resolve Git revision for {ref}: {error}") from error


def git_is_ancestor(ancestor: str, descendant: str) -> None:
    """Require a release commit to remain on the current main ancestry."""

    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise ProvenanceError(f"unable to check main ancestry: {error}") from error
    if result.returncode != 0:
        raise ProvenanceError("release commit is not an ancestor of the current main ref")


def validate_inputs(args: argparse.Namespace) -> None:
    version = validate_release_version(version_from_tag(args.release_tag))
    tag_revision = git_revision(args.release_tag)
    origin_main_revision = git_revision("refs/remotes/origin/main")
    validate_release_identity(
        release_tag=args.release_tag,
        release_sha=args.release_sha,
        main_sha=args.main_sha,
        tag_revision=tag_revision,
        main_revision=args.main_sha,
    )
    git_is_ancestor(args.main_sha, origin_main_revision)
    if args.release_url and f"/releases/tag/{args.release_tag}" not in args.release_url:
        raise ProvenanceError("release URL does not identify the requested release tag")
    validate_package_versions(version)
    validate_linked_components()
    if args.release_url and not args.dry_run:
        try:
            subprocess.run(
                ["gh", "release", "view", args.release_tag, "--repo", args.repository, "--json", "tagName,url"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            raise ProvenanceError(f"release-please-created GitHub Release is not available: {error}") from error


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    subcommands = command.add_subparsers(dest="command", required=True)

    inputs = subcommands.add_parser("inputs")
    inputs.add_argument("--release-tag", required=True)
    inputs.add_argument("--release-sha", required=True)
    inputs.add_argument("--main-sha", required=True)
    inputs.add_argument("--release-url", default="")
    inputs.add_argument("--repository", default=REPOSITORY)
    inputs.add_argument("--dry-run", action="store_true")

    binary = subcommands.add_parser("binary")
    binary.add_argument("--binary", type=Path, required=True)
    binary.add_argument("--version", required=True)
    binary.add_argument("--target", required=True)
    binary.add_argument("--mode", choices=("native", "cross-target"), required=True)
    binary.add_argument("--evidence-output", type=Path, required=True)

    archives = subcommands.add_parser("archives")
    archives.add_argument("--release-version", required=True)
    archives.add_argument("--source-revision", required=True)
    archives.add_argument("--release-out", type=Path, required=True)
    carrier_selection = subcommands.add_parser("carrier-pr-selection")
    carrier_selection.add_argument("--event-sha", required=True)
    carrier_selection.add_argument("--pull-requests", type=Path, required=True)
    carrier = subcommands.add_parser("carrier")
    carrier.add_argument("--event-name", required=True)
    carrier.add_argument("--ref", required=True)
    carrier.add_argument("--event-sha", required=True)
    carrier.add_argument("--pull-requests", type=Path, required=True)
    carrier.add_argument("--pull-request-files", type=Path, required=True)
    carrier.add_argument("--root", type=Path, default=ROOT)
    carrier.add_argument("--require-clean", action="store_true")

    tag_plan = subcommands.add_parser("carrier-tag-plan")
    tag_plan.add_argument("--version", required=True)
    tag_plan.add_argument("--expected-sha", required=True)
    tag_plan.add_argument("--existing-type")
    tag_plan.add_argument("--existing-sha")
    tag_plan.add_argument("--existing-release", action="store_true")
    return command


def _load_json_value(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProvenanceError(f"unable to read JSON fixture {path}: {error}") from error


def _changed_files(value: Any) -> list[Any]:
    if not isinstance(value, list):
        raise ProvenanceError("pull request files JSON must contain an array")
    return value


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "inputs":
            validate_inputs(args)
            print("RELEASE INPUT PROVENANCE: PASS")
        elif args.command == "binary":
            write_binary_evidence(
                binary=args.binary,
                version=args.version,
                target=args.target,
                mode=args.mode,
                output=args.evidence_output,
            )
            print(f"BINARY PROVENANCE: PASS ({args.mode}, {args.target})")
        elif args.command == "archives":
            validate_sha = require_sha(args.source_revision, "source_revision")
            validate_archive_set(args.release_out, args.release_version, validate_sha)
            print("RELEASE ARCHIVE PROVENANCE: PASS")
        elif args.command == "carrier-pr-selection":
            selection = classify_carrier_prs(
                _load_json_value(args.pull_requests), args.event_sha
            )
            print(json.dumps(selection, sort_keys=True))
        elif args.command == "carrier":
            pull_requests = _load_json_value(args.pull_requests)
            changed_files = _changed_files(_load_json_value(args.pull_request_files))
            if not isinstance(pull_requests, list):
                raise ProvenanceError("pull requests JSON must contain an array")
            record = validate_carrier_event(
                event_name=args.event_name,
                ref=args.ref,
                event_sha=args.event_sha,
                pull_requests=pull_requests,
                changed_files=changed_files,
                root=args.root,
                require_clean=args.require_clean,
            )
            print(json.dumps(asdict(record), sort_keys=True))
        else:
            plan = plan_carrier_tag(
                args.version,
                args.expected_sha,
                existing_type=args.existing_type,
                existing_sha=args.existing_sha,
                existing_release=args.existing_release,
            )
            print(json.dumps(asdict(plan), sort_keys=True))
        return 0
    except ProvenanceError as error:
        print(f"RELEASE PROVENANCE: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
