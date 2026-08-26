#!/usr/bin/env python3
"""Verify release identity, package versions, archive manifests, and binary evidence.

The script is deliberately local and side-effect free apart from writing the requested
binary-evidence file.  GitHub publication jobs call it after checking out the exact
release-please SHA; local tests can exercise the pure validators without credentials.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
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
VERSION_TOKEN_RE = re.compile(
    rf"(?<![0-9A-Za-z-])({SEMVER_CORE})(?![0-9A-Za-z-])"
)
RELEASE_PLEASE_ANNOTATION_RE = re.compile(r"x-release-please-[A-Za-z-]+")
RUNTIME_CRATES = (
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-provider-typescript",
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
PRIVATE_CONFORMANCE_MANIFEST_PATH = "crates/codegauge-conformance/Cargo.toml"
PRIVATE_CONFORMANCE_PACKAGE_VERSION = "0.1.0"
PRIVATE_CONFORMANCE_DEPENDENCIES = (
    "codegauge-application",
    "codegauge-core",
    "codegauge-model",
    "codegauge-provider-jacoco",
    "codegauge-provider-typescript",
)
PRIVATE_CONFORMANCE_EXTRA_FILES = tuple(
    {
        "type": "toml",
        "path": f"/{PRIVATE_CONFORMANCE_MANIFEST_PATH}",
        "jsonpath": f'$.dependencies["{dependency}"].version',
    }
    for dependency in PRIVATE_CONFORMANCE_DEPENDENCIES
)
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
            '@.name.value == "codegauge-provider-typescript" || '
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
        "path": "/crates/codegauge-provider-typescript/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-application"].version',
    },
    {
        "type": "toml",
        "path": "/crates/codegauge-provider-typescript/Cargo.toml",
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
    {
        "type": "toml",
        "path": "/crates/codegauge-cli/Cargo.toml",
        "jsonpath": '$.dependencies["codegauge-provider-typescript"].version',
    },
    *PRIVATE_CONFORMANCE_EXTRA_FILES,
    {"type": "generic", "path": "/README.md"},
    {
        "type": "json",
        "path": "/tests/golden/valid-methods.json",
        "jsonpath": "$.tool.version",
    },
    {
        "type": "json",
        "path": "/tests/golden/typescript-valid.json",
        "jsonpath": "$.tool.version",
    },
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
        "crates/codegauge-provider-typescript",
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
            "tests/golden/typescript-valid.json",
            "crates/codegauge-model/tests/contracts.rs",
            "crates/codegauge-cli/tests/cli.rs",
        }
    )
    | frozenset({f"crates/{crate}/Cargo.toml" for crate in RUNTIME_CRATES})
    | NPM_PACKAGE_DIFF_PATHS
    | RUNTIME_CHANGELOG_PATHS
    | frozenset({PRIVATE_CONFORMANCE_MANIFEST_PATH})
)
RELEASE_METADATA_PATH = ".release-please-manifest.json"
ANNOTATED_ROOT_VERSION_LINES = {
    "README.md": 4,
    "crates/codegauge-model/tests/contracts.rs": 2,
}
TYPED_JSON_ROOT_PATHS = {
    "tests/golden/valid-methods.json": ("tool", "version"),
    "tests/golden/typescript-valid.json": ("tool", "version"),
}
RUNTIME_CARGO_DEPENDENCIES = {
    "crates/codegauge-core/Cargo.toml": ("codegauge-model",),
    "crates/codegauge-application/Cargo.toml": (
        "codegauge-core",
        "codegauge-model",
    ),
    "crates/codegauge-provider-jacoco/Cargo.toml": (
        "codegauge-application",
        "codegauge-model",
    ),
    "crates/codegauge-provider-typescript/Cargo.toml": (
        "codegauge-application",
        "codegauge-model",
    ),
    "crates/codegauge-cli/Cargo.toml": (
        "codegauge-application",
        "codegauge-model",
        "codegauge-provider-jacoco",
        "codegauge-provider-typescript",
    ),
}
RUNTIME_CARGO_MANIFEST_DEPENDENCIES = {
    "crates/codegauge-model/Cargo.toml": (),
    **RUNTIME_CARGO_DEPENDENCIES,
}
HUNK_HEADER_RE = re.compile(
    r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?: .*)?$"
)
NPM_BASE_PACKAGE_PATH = "npm/codegauge/package.json"
NPM_BASE_ALLOWED_FORMATTING_ADDED = (
    '  "files": [',
    '    "dist/index.js"',
    "  ],",
)
NPM_BASE_ALLOWED_FORMATTING_DELETED = ('  "files": ["dist/index.js"],',)
NPM_PLATFORM_PACKAGE_PATHS = {
    f"npm/packages/{package.removeprefix('@yacosta738/')}/package.json": package
    for package in NPM_PACKAGES
}
CONTENT_VALIDATED_STAGE_A_DIFFS = (
    ALLOWED_STAGE_A_DIFFS - {PRIVATE_CONFORMANCE_MANIFEST_PATH}
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


def resolve_carrier_event_sha(
    *,
    event_name: str,
    ref: str,
    github_sha: str,
    replay_sha: str | None,
    dry_run: bool,
) -> dict[str, Any]:
    """Select the trusted event identity without changing the source checkout.

    A replay deliberately separates the source revision (the current selected
    ``main`` checkout) from the historical merge revision used for read-only
    GitHub correlation and validation.  It is intentionally impossible to
    select that historical identity for a push or a live dispatch.
    """

    if event_name not in {"push", "workflow_dispatch"}:
        raise ProvenanceError(
            "carrier accepts only push or workflow_dispatch events"
        )
    if ref != "refs/heads/main":
        raise ProvenanceError("carrier accepts only refs/heads/main")
    if not isinstance(dry_run, bool):
        raise ProvenanceError("carrier dry_run mode must be boolean")

    source_sha = require_sha(github_sha, "source event SHA")
    if replay_sha is None:
        replay_sha = ""
    if not isinstance(replay_sha, str):
        raise ProvenanceError("replay_sha must be a string")
    if not replay_sha:
        return {
            "event_sha": source_sha,
            "replay": False,
            "source_sha": source_sha,
        }
    if event_name != "workflow_dispatch" or not dry_run:
        raise ProvenanceError("replay_sha requires workflow_dispatch with dry_run=true")
    return {
        "event_sha": require_sha(replay_sha, "replay SHA"),
        "replay": True,
        "source_sha": source_sha,
    }


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
        "crates/codegauge-provider-typescript",
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


def validate_private_boundaries(
    root: Path = ROOT,
    *,
    runtime_version: str | None = None,
) -> None:
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
    if (
        package.get("name") != "codegauge-conformance"
        or package.get("version") != PRIVATE_CONFORMANCE_PACKAGE_VERSION
        or package.get("publish") is not False
    ):
        raise ProvenanceError("codegauge-conformance must remain a private non-publishable package")
    if runtime_version is not None:
        dependencies = document.get("dependencies", {})
        if not isinstance(dependencies, dict):
            raise ProvenanceError("private conformance dependencies must be a TOML table")
        for dependency in PRIVATE_CONFORMANCE_DEPENDENCIES:
            dependency_config = dependencies.get(dependency)
            if (
                not isinstance(dependency_config, dict)
                or dependency_config.get("version") != runtime_version
                or dependency_config.get("path") != f"../{dependency}"
            ):
                raise ProvenanceError(
                    f"private conformance dependency pin drift for {dependency}"
                )
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
    validate_private_boundaries(root, runtime_version=version)


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


def _patch_change_lines(
    entry: dict[str, Any],
    *,
    path: str,
) -> tuple[list[str], list[str], list[str]]:
    """Return changed lines from one complete GitHub PR-file patch.

    The GitHub PR files API returns the patch body without the file headers that
    appear in a local unified diff.  The filename in the validated API entry is
    the only file identity available for that hunk-only form.  Keep accepting
    both that API form and a complete single-file unified diff, but never infer
    completeness from the additions/deletions metadata alone.
    """

    if entry.get("status") not in {"modified", "added"}:
        raise ProvenanceError(f"{path} must be an added or modified file")
    numeric_metadata = ("additions", "deletions", "changes")
    if any(
        isinstance(entry.get(field), bool) or not isinstance(entry.get(field), int)
        for field in numeric_metadata
    ):
        raise ProvenanceError(f"{path} diff is missing complete change metadata")
    if entry["changes"] != entry["additions"] + entry["deletions"]:
        raise ProvenanceError(f"{path} diff change count is inconsistent")

    patch = entry.get("patch")
    if not isinstance(patch, str) or not patch.strip():
        raise ProvenanceError(f"{path} diff requires a complete patch")
    lines = patch.splitlines()

    expected_diff_header = f"diff --git a/{path} b/{path}"
    diff_headers = [
        line
        for line in lines
        if line.startswith("diff --git ")
    ]
    if diff_headers:
        if lines[0] != expected_diff_header or diff_headers != [expected_diff_header]:
            raise ProvenanceError(f"{path} diff has missing or unexpected file context")
        hunk_start = next(
            (index for index, line in enumerate(lines) if line.startswith("@@")),
            None,
        )
        if hunk_start is None:
            raise ProvenanceError(f"{path} diff is missing a complete hunk")
        preamble = lines[1:hunk_start]
        expected_old_header = (
            "--- /dev/null"
            if entry["status"] == "added"
            else f"--- a/{path}"
        )
        expected_new_header = f"+++ b/{path}"
        if preamble.count(expected_old_header) != 1 or preamble.count(expected_new_header) != 1:
            if entry["status"] == "added":
                raise ProvenanceError(f"{path} added-file patch has invalid headers")
            raise ProvenanceError(f"{path} modified-file patch has invalid headers")

        metadata_patterns = (
            re.compile(r"^index [0-9a-f]+\.\.[0-9a-f]+(?: \d+)?$"),
            re.compile(r"^(?:new|deleted|old) file mode \d+$"),
            re.compile(r"^(?:old|new) mode \d+$"),
            re.compile(r"^(?:similarity|dissimilarity) index \d+%$"),
            re.compile(r"^(?:rename from|rename to) .+$"),
        )
        for line in preamble:
            if line in {expected_old_header, expected_new_header}:
                continue
            if not any(pattern.fullmatch(line) for pattern in metadata_patterns):
                raise ProvenanceError(f"{path} diff has malformed or unexpected headers")
    else:
        if not lines[0].startswith("@@"):
            raise ProvenanceError(f"{path} diff is neither a complete unified diff nor a hunk-only patch")
        if any(line.startswith("diff --git ") for line in lines):
            raise ProvenanceError(f"{path} diff contains an unexpected file section")
        hunk_start = 0

    added, deleted, hunk_counts = _parse_patch_hunks(
        lines[hunk_start:],
        path=path,
    )
    if entry["status"] == "added" and (
        deleted or any(old_count != 0 for old_count, _ in hunk_counts)
    ):
        raise ProvenanceError(f"{path} added-file patch contains deleted or old-file context")
    if len(added) != entry["additions"] or len(deleted) != entry["deletions"]:
        raise ProvenanceError(f"{path} diff patch is truncated or has inconsistent counts")
    return added, deleted, lines


def _parse_patch_hunks(
    lines: list[str],
    *,
    path: str,
) -> tuple[list[str], list[str], list[tuple[int, int]]]:
    """Parse every hunk and verify its declared old/new line counts."""

    if not lines or not lines[0].startswith("@@"):
        raise ProvenanceError(f"{path} diff is missing a complete hunk")

    added: list[str] = []
    deleted: list[str] = []
    hunk_counts: list[tuple[int, int]] = []
    index = 0
    while index < len(lines):
        header = lines[index]
        match = HUNK_HEADER_RE.fullmatch(header)
        if match is None:
            raise ProvenanceError(f"{path} diff contains a malformed hunk header")
        old_count = int(match.group(2) or "1")
        new_count = int(match.group(4) or "1")
        index += 1
        actual_old = 0
        actual_new = 0
        hunk_has_content = False
        while index < len(lines) and not lines[index].startswith("@@"):
            line = lines[index]
            if line == r"\ No newline at end of file":
                if not hunk_has_content:
                    raise ProvenanceError(f"{path} diff has an orphaned newline marker")
            elif line.startswith(" "):
                actual_old += 1
                actual_new += 1
                hunk_has_content = True
            elif line.startswith("+"):
                actual_new += 1
                added.append(line[1:])
                hunk_has_content = True
            elif line.startswith("-"):
                actual_old += 1
                deleted.append(line[1:])
                hunk_has_content = True
            else:
                raise ProvenanceError(f"{path} diff contains an unexpected hunk line")
            index += 1
        if not hunk_has_content:
            raise ProvenanceError(f"{path} diff contains an empty hunk")
        if actual_old != old_count or actual_new != new_count:
            raise ProvenanceError(f"{path} diff hunk is truncated or has inconsistent counts")
        hunk_counts.append((old_count, new_count))

    if not hunk_counts:
        raise ProvenanceError(f"{path} diff is missing a complete hunk")
    return added, deleted, hunk_counts


def _annotation_tokens(line: str) -> list[str]:
    return RELEASE_PLEASE_ANNOTATION_RE.findall(line)


def _version_tokens(line: str) -> list[str]:
    return VERSION_TOKEN_RE.findall(line)


def _validate_version_line_replacement(
    old_line: str,
    new_line: str,
    *,
    runtime_version: str,
    require_annotation: bool = False,
) -> None:
    old_versions = _version_tokens(old_line)
    new_versions = _version_tokens(new_line)
    if (
        len(old_versions) != 1
        or len(new_versions) != 1
        or not VERSION_RE.fullmatch(old_versions[0])
        or old_versions[0] == runtime_version
        or new_versions[0] != runtime_version
        or old_line.replace(old_versions[0], runtime_version, 1) != new_line
    ):
        raise ProvenanceError("version carrier patch contains an unexpected replacement")
    if require_annotation:
        if _annotation_tokens(old_line) != ["x-release-please-version"]:
            raise ProvenanceError("annotated carrier patch has an unexpected old marker")
        if _annotation_tokens(new_line) != ["x-release-please-version"]:
            raise ProvenanceError("annotated carrier patch has an unexpected new marker")
    elif _annotation_tokens(old_line) or _annotation_tokens(new_line):
        raise ProvenanceError("typed carrier patch contains an unapproved Release Please marker")


def _validate_annotated_root_patch(
    entry: dict[str, Any],
    *,
    path: str,
    runtime_version: str,
) -> None:
    added, deleted, _ = _patch_change_lines(entry, path=path)
    expected_lines = ANNOTATED_ROOT_VERSION_LINES[path]
    if len(added) != expected_lines or len(deleted) != expected_lines:
        raise ProvenanceError(
            f"{path} must contain exactly {expected_lines} annotated version replacements"
        )
    for old_line, new_line in zip(deleted, added):
        _validate_version_line_replacement(
            old_line,
            new_line,
            runtime_version=runtime_version,
            require_annotation=True,
        )


def _validate_typed_json_patch(
    entry: dict[str, Any],
    *,
    path: str,
    runtime_version: str,
) -> None:
    added, deleted, _ = _patch_change_lines(entry, path=path)
    if len(added) != 1 or len(deleted) != 1:
        raise ProvenanceError(f"{path} must contain one complete JSON replacement")
    if _annotation_tokens(added[0]) or _annotation_tokens(deleted[0]):
        raise ProvenanceError(f"{path} contains an unapproved Release Please marker")
    try:
        before = json.loads(deleted[0])
        after = json.loads(added[0])
    except json.JSONDecodeError as error:
        raise ProvenanceError(f"{path} patch is not complete JSON: {error}") from error
    expected = deepcopy(before)
    try:
        current: Any = expected
        for key in TYPED_JSON_ROOT_PATHS[path][:-1]:
            current = current[key]
        current[TYPED_JSON_ROOT_PATHS[path][-1]] = runtime_version
    except (KeyError, TypeError) as error:
        raise ProvenanceError(f"{path} is missing its configured typed JSONPath") from error
    if after != expected:
        raise ProvenanceError(f"{path} changed content outside its typed JSONPath")
    try:
        old_value: Any = before
        new_value: Any = after
        for key in TYPED_JSON_ROOT_PATHS[path]:
            old_value = old_value[key]
            new_value = new_value[key]
    except (KeyError, TypeError) as error:
        raise ProvenanceError(f"{path} is missing its configured typed JSONPath") from error
    if (
        not isinstance(old_value, str)
        or not VERSION_RE.fullmatch(old_value)
        or old_value == runtime_version
        or new_value != runtime_version
    ):
        raise ProvenanceError(f"{path} has an invalid typed version replacement")


def _validate_release_manifest_patch(
    entry: dict[str, Any],
    *,
    runtime_version: str,
) -> None:
    added, deleted, _ = _patch_change_lines(entry, path=RELEASE_METADATA_PATH)
    if _annotation_tokens("\n".join(added)) or _annotation_tokens("\n".join(deleted)):
        raise ProvenanceError("release metadata contains an unapproved Release Please marker")
    if len(added) == 1 and len(deleted) == 1:
        try:
            before = json.loads(deleted[0])
            after = json.loads(added[0])
        except json.JSONDecodeError as error:
            raise ProvenanceError(f"release metadata patch is not complete JSON: {error}") from error
        if set(before) != EXPECTED_RELEASE_MANIFEST_PATHS or set(after) != set(before):
            raise ProvenanceError("release metadata changed its approved path set")
        old_values = before.values()
        new_values = after.values()
    else:
        if len(added) != len(deleted) or len(added) != len(EXPECTED_RELEASE_MANIFEST_PATHS):
            raise ProvenanceError("release metadata patch is truncated or has unexpected lines")
        old_values = []
        new_values = []
        changed_paths: set[str] = set()
        for old_line, new_line in zip(deleted, added):
            old_match = re.fullmatch(r'\s*"([^"]+)": "([^"]+)",?\s*', old_line)
            new_match = re.fullmatch(
                rf'\s*"([^"]+)": "{re.escape(runtime_version)}",?\s*',
                new_line,
            )
            if not old_match or not new_match or old_match.group(1) != new_match.group(1):
                raise ProvenanceError("release metadata contains an unexpected line replacement")
            changed_paths.add(old_match.group(1))
            old_values.append(old_match.group(2))
            new_values.append(runtime_version)
        if changed_paths != EXPECTED_RELEASE_MANIFEST_PATHS:
            raise ProvenanceError("release metadata changed its approved path set")
    if any(
        not isinstance(value, str)
        or not VERSION_RE.fullmatch(value)
        or value == runtime_version
        for value in old_values
    ) or any(value != runtime_version for value in new_values):
        raise ProvenanceError("release metadata contains an unexpected version replacement")


def _validate_toml_version_patch(
    entry: dict[str, Any],
    *,
    path: str,
    runtime_version: str,
) -> None:
    added, deleted, patch_lines = _patch_change_lines(entry, path=path)
    if path == "Cargo.toml":
        expected_pairs = 1
        if not any(line.strip() == "[workspace.package]" for line in patch_lines):
            raise ProvenanceError("root Cargo.toml patch is outside workspace.package.version")
        if any(
            old.strip() != f'version = "{_version_tokens(old)[0]}"'
            or new.strip() != f'version = "{runtime_version}"'
            for old, new in zip(deleted, added)
            if len(_version_tokens(old)) == 1
        ):
            raise ProvenanceError("root Cargo.toml contains an unexpected replacement")
    elif path == "Cargo.lock":
        expected_pairs = len(RUNTIME_CRATES)
        if "codegauge-conformance" in "\n".join(patch_lines):
            raise ProvenanceError("Cargo.lock patch must not change the private package")
        missing = [
            crate
            for crate in RUNTIME_CRATES
            if not any(line.strip() == f'name = "{crate}"' for line in patch_lines)
        ]
        if missing:
            raise ProvenanceError(
                "Cargo.lock patch is missing runtime package context: " + ", ".join(missing)
            )
    elif path in RUNTIME_CARGO_MANIFEST_DEPENDENCIES:
        expected_pairs = 1 + len(RUNTIME_CARGO_MANIFEST_DEPENDENCIES[path])
        if not any(line.strip() == "[package]" for line in patch_lines):
            raise ProvenanceError(f"{path} patch is missing package context")
    else:
        raise ProvenanceError(f"no TOML content contract exists for {path}")

    if len(added) != expected_pairs or len(deleted) != expected_pairs:
        raise ProvenanceError(f"{path} contains an unexpected number of TOML replacements")
    package_versions = 0
    dependency_versions: set[str] = set()
    for old_line, new_line in zip(deleted, added):
        _validate_version_line_replacement(
            old_line,
            new_line,
            runtime_version=runtime_version,
        )
        old_stripped = old_line.strip()
        new_stripped = new_line.strip()
        if old_stripped.startswith("version = ") and new_stripped == f'version = "{runtime_version}"':
            package_versions += 1
            continue
        dependency_match = re.fullmatch(
            r'([A-Za-z0-9_-]+) = \{ version = "([^"]+)", path = "\.\./([A-Za-z0-9_-]+)" \}',
            old_stripped,
        )
        new_dependency_match = re.fullmatch(
            rf'([A-Za-z0-9_-]+) = \{{ version = "{re.escape(runtime_version)}", path = "\.\./([A-Za-z0-9_-]+)" \}}',
            new_stripped,
        )
        if not dependency_match or not new_dependency_match:
            raise ProvenanceError(f"{path} contains an unapproved TOML mutation")
        if (
            dependency_match.group(1) != new_dependency_match.group(1)
            or dependency_match.group(3) != new_dependency_match.group(2)
            or dependency_match.group(1) != dependency_match.group(3)
        ):
            raise ProvenanceError(f"{path} changed a dependency path")
        dependency_versions.add(dependency_match.group(3))

    if path == "Cargo.toml" and package_versions != 1:
        raise ProvenanceError("root Cargo.toml must update only workspace.package.version")
    if path == "Cargo.lock" and package_versions != expected_pairs:
        raise ProvenanceError("Cargo.lock must update exactly the six runtime versions")
    if path in RUNTIME_CARGO_MANIFEST_DEPENDENCIES:
        if package_versions != 1 or dependency_versions != set(
            RUNTIME_CARGO_MANIFEST_DEPENDENCIES[path]
        ):
            raise ProvenanceError(f"{path} changed an unexpected runtime dependency set")


def _validate_npm_package_patch(
    entry: dict[str, Any],
    *,
    path: str,
    runtime_version: str,
) -> None:
    added, deleted, _ = _patch_change_lines(entry, path=path)
    optional_keys = (
        set(NPM_PACKAGES)
        if path == NPM_BASE_PACKAGE_PATH
        else set()
    )
    expected_keys = {"version"} | optional_keys
    version_added: list[str] = []
    version_deleted: list[str] = []
    formatting_added: list[str] = []
    formatting_deleted: list[str] = []
    package_line = re.compile(r'\s*"([^"]+)": "([^"]+)",?\s*')
    for line in added:
        if (match := package_line.fullmatch(line)) and match.group(1) in expected_keys:
            version_added.append(line)
        else:
            formatting_added.append(line)
    for line in deleted:
        if (match := package_line.fullmatch(line)) and match.group(1) in expected_keys:
            version_deleted.append(line)
        else:
            formatting_deleted.append(line)

    formatting_is_empty = not formatting_added and not formatting_deleted
    formatting_is_allowed_base_rewrite = (
        path == NPM_BASE_PACKAGE_PATH
        and formatting_added == list(NPM_BASE_ALLOWED_FORMATTING_ADDED)
        and formatting_deleted == list(NPM_BASE_ALLOWED_FORMATTING_DELETED)
    )
    if not formatting_is_empty and not formatting_is_allowed_base_rewrite:
        raise ProvenanceError(f"{path} contains an unapproved package formatting mutation")
    expected_pairs = 1 + len(optional_keys)
    if len(version_added) != expected_pairs or len(version_deleted) != expected_pairs:
        raise ProvenanceError(f"{path} contains an unexpected number of package version edits")
    seen_keys: set[str] = set()
    for old_line, new_line in zip(version_deleted, version_added):
        old_match = re.fullmatch(r'\s*"([^"]+)": "([^"]+)",?\s*', old_line)
        new_match = re.fullmatch(
            rf'\s*"([^"]+)": "{re.escape(runtime_version)}",?\s*',
            new_line,
        )
        if not old_match or not new_match or old_match.group(1) != new_match.group(1):
            raise ProvenanceError(f"{path} contains an unapproved package mutation")
        key = old_match.group(1)
        if key != "version" and key not in optional_keys:
            raise ProvenanceError(f"{path} changed an unapproved package key")
        old_version = old_match.group(2)
        if not VERSION_RE.fullmatch(old_version) or old_version == runtime_version:
            raise ProvenanceError(f"{path} contains an invalid old package version")
        if key in seen_keys:
            raise ProvenanceError(f"{path} contains a duplicate package version edit")
        seen_keys.add(key)
    if seen_keys != {"version"} | optional_keys:
        raise ProvenanceError(f"{path} did not synchronize its approved package versions")


def _validate_generated_changelog_patch(
    entry: dict[str, Any],
    *,
    path: str,
    runtime_version: str,
) -> None:
    added, deleted, patch_lines = _patch_change_lines(entry, path=path)
    if entry.get("status") not in {"added", "modified"} or deleted or not added:
        raise ProvenanceError(f"{path} must be a complete generated changelog addition")
    if entry.get("status") == "added":
        if added[0] != "# Changelog":
            raise ProvenanceError(f"{path} is not a Release Please changelog")
    elif " # Changelog" not in patch_lines:
        raise ProvenanceError(f"{path} is not a Release Please changelog")
    version_header = re.compile(
        rf"^##+ (?:\[)?v?{re.escape(runtime_version)}(?:\]|(?:\s|$))"
    )
    if not any(version_header.match(line) for line in added):
        raise ProvenanceError(f"{path} changelog is missing the synchronized version header")
    if any(_annotation_tokens(line) for line in added):
        raise ProvenanceError(f"{path} contains an unapproved Release Please marker")


def _validate_noop_generic_patch(entry: dict[str, Any], *, path: str) -> None:
    _patch_change_lines(entry, path=path)
    raise ProvenanceError(
        f"{path} has no configured Release Please version marker and cannot be changed"
    )


def _validate_approved_content_patch(
    entry: dict[str, Any],
    *,
    path: str,
    runtime_version: str,
) -> None:
    if path in ANNOTATED_ROOT_VERSION_LINES:
        _validate_annotated_root_patch(
            entry,
            path=path,
            runtime_version=runtime_version,
        )
    elif path in TYPED_JSON_ROOT_PATHS:
        _validate_typed_json_patch(
            entry,
            path=path,
            runtime_version=runtime_version,
        )
    elif path == RELEASE_METADATA_PATH:
        _validate_release_manifest_patch(entry, runtime_version=runtime_version)
    elif path == "crates/codegauge-cli/tests/cli.rs":
        _validate_noop_generic_patch(entry, path=path)
    elif path == PRIVATE_CONFORMANCE_MANIFEST_PATH:
        _validate_private_conformance_patch(entry, runtime_version=runtime_version)
    elif (
        path == "Cargo.toml"
        or path == "Cargo.lock"
        or path in RUNTIME_CARGO_MANIFEST_DEPENDENCIES
    ):
        _validate_toml_version_patch(
            entry,
            path=path,
            runtime_version=runtime_version,
        )
    elif path == NPM_BASE_PACKAGE_PATH or path in NPM_PLATFORM_PACKAGE_PATHS:
        _validate_npm_package_patch(
            entry,
            path=path,
            runtime_version=runtime_version,
        )
    elif path in RUNTIME_CHANGELOG_PATHS:
        _validate_generated_changelog_patch(
            entry,
            path=path,
            runtime_version=runtime_version,
        )
    else:
        raise ProvenanceError(f"no content contract exists for approved path {path}")


def _validate_private_conformance_patch(
    entry: dict[str, Any],
    *,
    runtime_version: str | None,
) -> None:
    """Allow only five complete dependency-version replacements in the private manifest."""

    if runtime_version is None or not VERSION_RE.fullmatch(runtime_version):
        raise ProvenanceError(
            "private conformance diff validation requires a valid synchronized runtime version"
        )
    if entry.get("status") != "modified":
        raise ProvenanceError("private conformance manifest must be an existing modified file")

    added_patch_lines, deleted_patch_lines, patch_lines = _patch_change_lines(
        entry,
        path=PRIVATE_CONFORMANCE_MANIFEST_PATH,
    )
    if (
        entry["additions"] != len(PRIVATE_CONFORMANCE_DEPENDENCIES)
        or entry["deletions"] != len(PRIVATE_CONFORMANCE_DEPENDENCIES)
        or entry["changes"] != entry["additions"] + entry["deletions"]
    ):
        raise ProvenanceError(
            "private conformance diff must contain exactly five additions and five deletions"
        )

    required_context = {
        ' description = "Private cross-crate CodeGauge conformance suite"',
        " [dependencies]",
        " [dev-dependencies]",
        " schemars.workspace = true",
    }
    if not required_context <= set(patch_lines):
        raise ProvenanceError("private conformance diff patch is truncated")

    if len(deleted_patch_lines) != len(PRIVATE_CONFORMANCE_DEPENDENCIES) or len(
        added_patch_lines
    ) != len(PRIVATE_CONFORMANCE_DEPENDENCIES):
        raise ProvenanceError(
            "private conformance diff patch is truncated or contains unrelated changes"
        )

    deleted_dependencies: set[str] = set()
    added_dependencies: set[str] = set()
    for dependency in PRIVATE_CONFORMANCE_DEPENDENCIES:
        old_pattern = re.compile(
            rf"^-{re.escape(dependency)} = \{{ version = \"([^\"]+)\", path = \"\.\./{re.escape(dependency)}\" \}}$"
        )
        new_pattern = re.compile(
            rf"^\+{re.escape(dependency)} = \{{ version = \"{re.escape(runtime_version)}\", path = \"\.\./{re.escape(dependency)}\" \}}$"
        )
        old_matches = [
            f"-{line}" for line in deleted_patch_lines if old_pattern.fullmatch(f"-{line}")
        ]
        new_matches = [
            f"+{line}" for line in added_patch_lines if new_pattern.fullmatch(f"+{line}")
        ]
        if len(old_matches) != 1 or len(new_matches) != 1:
            raise ProvenanceError(
                f"private conformance diff contains an unapproved mutation for {dependency}"
            )
        old_version = old_pattern.fullmatch(old_matches[0]).group(1)
        if not VERSION_RE.fullmatch(old_version) or old_version == runtime_version:
            raise ProvenanceError(
                f"private conformance dependency {dependency} has an invalid old version"
            )
        deleted_dependencies.add(dependency)
        added_dependencies.add(dependency)

    expected_dependencies = set(PRIVATE_CONFORMANCE_DEPENDENCIES)
    if deleted_dependencies != expected_dependencies or added_dependencies != expected_dependencies:
        raise ProvenanceError("private conformance diff changed an unexpected dependency key")


def validate_stage_a_diff(
    changed_files: list[Any],
    *,
    version: str | None = None,
) -> None:
    """Allow only the synchronized version-PR file boundary."""

    paths: list[str] = []
    seen_paths: set[str] = set()
    for entry in changed_files:
        path = entry.get("filename") if isinstance(entry, dict) else entry
        if not isinstance(path, str) or not path:
            raise ProvenanceError("release PR diff contains invalid file metadata")
        normalized = path[2:] if path.startswith("./") else path
        if normalized in seen_paths:
            raise ProvenanceError(f"release PR diff contains duplicate path: {normalized}")
        seen_paths.add(normalized)
        paths.append(normalized)
        if normalized not in ALLOWED_STAGE_A_DIFFS:
            raise ProvenanceError(f"release PR diff contains an unapproved path: {normalized}")
        if normalized == PRIVATE_CONFORMANCE_MANIFEST_PATH:
            if not isinstance(entry, dict):
                raise ProvenanceError(
                    "private conformance manifest requires filename and complete patch metadata"
                )
            _validate_private_conformance_patch(entry, runtime_version=version)
        elif normalized in CONTENT_VALIDATED_STAGE_A_DIFFS:
            if version is None:
                continue
            if not isinstance(entry, dict):
                raise ProvenanceError(
                    f"{normalized} requires filename and complete patch metadata"
                )
            if not VERSION_RE.fullmatch(version):
                raise ProvenanceError(
                    f"{normalized} content validation requires a valid synchronized version"
                )
            _validate_approved_content_patch(
                entry,
                path=normalized,
                runtime_version=version,
            )
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
    candidates = select_matching_release_please_prs(pull_requests, event_sha)
    if len(candidates) != 1:
        raise ProvenanceError(
            "expected exactly one merged Release Please PR for the event SHA, "
            f"found {len(candidates)}"
        )
    if require_clean:
        validate_clean_checkout(root)
    version = validate_carrier_tree(root)
    pull_request = candidates[0]
    body = pull_request.get("body") or ""
    if body.count("---") < 2 or version not in body:
        raise ProvenanceError("merged Release Please PR body is not a synchronized version PR")
    validate_stage_a_diff(changed_files, version=version)
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
        if evidence.get("version") != f"codegauge {version}\n" or evidence.get("profiles") != "jvm-jacoco-v1\ntypescript-oxc-istanbul-v1\n":
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
        if version_output != f"codegauge {version}\n" or profiles_output != "jvm-jacoco-v1\ntypescript-oxc-istanbul-v1\n":
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
    carrier_event_sha = subcommands.add_parser("carrier-event-sha")
    carrier_event_sha.add_argument("--event-name", required=True)
    carrier_event_sha.add_argument("--ref", required=True)
    carrier_event_sha.add_argument("--github-sha", required=True)
    carrier_event_sha.add_argument("--replay-sha", default="")
    carrier_event_sha.add_argument("--dry-run", choices=("true", "false"), required=True)
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
        elif args.command == "carrier-event-sha":
            print(
                json.dumps(
                    resolve_carrier_event_sha(
                        event_name=args.event_name,
                        ref=args.ref,
                        github_sha=args.github_sha,
                        replay_sha=args.replay_sha,
                        dry_run=args.dry_run == "true",
                    ),
                    sort_keys=True,
                )
            )
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
