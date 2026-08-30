#!/usr/bin/env python3
"""Focused local regression checks for the R-D/R-F release provenance boundary."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile

import pytest
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CALLER = ROOT / ".github" / "workflows" / "release.yml"
BUILD = ROOT / ".github" / "workflows" / "release-build.yml"
PUBLISH = ROOT / ".github" / "workflows" / "release-publish.yml"

from scripts.verify_release_provenance import (  # noqa: E402
    ProvenanceError,
    read_workspace_version,
    validate_archive_manifest,
    validate_linked_components,
    validate_package_versions,
    validate_release_identity,
    validate_historical_provenance,
    validate_release_assets,
    publication_order,
    release_dispatch_count,
    write_binary_evidence,
)

RELEASE_PLEASE_VERSION = "17.6.0"
ROOT_EXTRA_PATHS = {
    "Cargo.toml",
    "Cargo.lock",
    "crates/codegauge-core/Cargo.toml",
    "crates/codegauge-application/Cargo.toml",
    "crates/codegauge-provider-jacoco/Cargo.toml",
    "crates/codegauge-provider-typescript/Cargo.toml",
    "crates/codegauge-cli/Cargo.toml",
    "README.md",
    "tests/golden/valid-methods.json",
    "tests/golden/typescript-valid.json",
    "crates/codegauge-model/tests/contracts.rs",
    "crates/codegauge-cli/tests/cli.rs",
    "crates/codegauge-conformance/Cargo.toml",
}
NEW_RELEASE_VERSION = "0.3.0"
RUNTIME_GRAPH_PATHS = {
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


@dataclass(frozen=True)
class EffectiveCandidate:
    """Small candidate model for the Release Please 17.6.0 plugin boundary."""

    path: str
    component: str
    strategy_component: str
    release_type: str
    extra_files: tuple[object, ...]
    skip_github_release: bool


def test_release_please_effective_candidates_create_github_releases() -> None:
    """Only the unprefixed root candidate owns the canonical GitHub release."""

    config = json.loads(
        (ROOT / "release-please-config.json").read_text(encoding="utf-8")
    )

    assert config.get("skip-github-release", False) is False
    assert config["packages"]["."]["include-component-in-tag"] is False
    assert config["packages"]["."].get("skip-github-release", False) is False
    assert all(
        candidate.get("skip-github-release") is True
        for path, candidate in config["packages"].items()
        if path != "."
    )


def _effective_candidates(config: dict[str, Any]) -> list[EffectiveCandidate]:
    """Apply the manifest's default config the same way Release Please does."""

    defaults = {
        "release-type": config.get("release-type"),
        "skip-github-release": config.get("skip-github-release", False),
        "include-component-in-tag": config.get("include-component-in-tag", True),
    }
    candidates = []
    for path, package in config["packages"].items():
        effective = {**defaults, **package}
        configured_component = effective.get("component")
        package_name = effective.get("package-name")
        strategy_component = (
            ""
            if effective.get("include-component-in-tag") is False
            else str(configured_component or package_name or "")
        )
        candidates.append(
            EffectiveCandidate(
                path=path,
                component=str(configured_component or ""),
                strategy_component=strategy_component,
                release_type=str(effective.get("release-type")),
                extra_files=tuple(package.get("extra-files", [])),
                skip_github_release=bool(effective.get("skip-github-release", False)),
            )
        )
    return candidates


def _explicit_runtime_candidates_17_6_0(
    candidates: list[EffectiveCandidate],
) -> list[EffectiveCandidate]:
    """Model the explicit Stage-A candidate boundary.

    The exact v17.6.0 cargo-workspace source has no member exclusion option, so
    Stage A does not invoke it. The configured six Rust paths are the only
    Cargo candidates retained; non-Cargo carriers remain in the manifest.
    """

    runtime_cargo_paths = {
        "crates/codegauge-model",
        "crates/codegauge-core",
        "crates/codegauge-application",
        "crates/codegauge-provider-jacoco",
        "crates/codegauge-provider-typescript",
        "crates/codegauge-cli",
    }
    return [
        candidate
        for candidate in candidates
        if candidate.release_type != "rust" or candidate.path in runtime_cargo_paths
    ]


def _root_extra_update_paths(candidate: EffectiveCandidate) -> set[str]:
    """Model BaseStrategy.extraFileUpdates and its root path handling."""

    paths: set[str] = set()
    for extra_file in candidate.extra_files:
        path = extra_file["path"] if isinstance(extra_file, dict) else extra_file
        if not isinstance(path, str):
            raise AssertionError("extra-file path must be a string")
        if path.startswith("/") or candidate.path == ".":
            paths.add(path.lstrip("/"))
        else:
            paths.add(f"{candidate.path.rstrip('/')}/{path.lstrip('/')}")
    return paths


def _version_key(version: str) -> tuple[int, int, int]:
    """Compare the release versions used by the v17.6.0 fixture."""

    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


def _linked_versions_preconfigure_17_6_0(
    config: dict[str, Any], candidates: list[EffectiveCandidate]
) -> dict[str, str]:
    """Model the exact LinkedVersions.preconfigure strategy-component gate.

    Release Please 17.6.0 calls ``strategy.getComponent()`` before it checks
    the configured component set.  BaseStrategy returns ``''`` when
    ``include-component-in-tag`` is false.  The fixture supplies the
    per-strategy versions that preconfigure would read from
    ``buildReleasePullRequest`` and then applies its highest-version forcing
    behavior to every strategy in the group.
    """

    linked_components = {
        component
        for plugin in config.get("plugins", [])
        if isinstance(plugin, dict) and plugin.get("type") == "linked-versions"
        for component in plugin.get("components", [])
    }
    group = [
        candidate
        for candidate in candidates
        if candidate.strategy_component
        and candidate.strategy_component in linked_components
    ]
    if not group:
        return {}

    proposed_versions = {
        candidate.path: (NEW_RELEASE_VERSION if candidate.path == "crates/codegauge-cli" else "0.1.1")
        for candidate in group
    }
    primary_version = max(proposed_versions.values(), key=_version_key)
    return {candidate.path: primary_version for candidate in group}


def _node_workspace_optional_update_17_6_0(
    config: dict[str, Any],
    candidates: list[EffectiveCandidate],
    linked_versions: dict[str, str],
) -> tuple[str, dict[str, str]]:
    """Model NodeWorkspace.combineDeps and PackageJson.updateContent.

    Release Please 17.6.0 includes optionalDependencies in the workspace graph
    and rewrites matching dependency versions through its package-json updater.
    This uses the repository's real package manifests and the versions map
    produced by the linked plugin, rather than asserting that the checked-in
    pins already happen to match.
    """

    node_plugins = [
        plugin
        for plugin in config.get("plugins", [])
        if isinstance(plugin, dict) and plugin.get("type") == "node-workspace"
    ]
    assert node_plugins == [{"type": "node-workspace", "merge": False}]

    node_candidates = [candidate for candidate in candidates if candidate.release_type == "node"]
    packages: dict[str, dict[str, Any]] = {}
    candidates_by_package: dict[str, EffectiveCandidate] = {}
    for candidate in node_candidates:
        package = json.loads(
            (ROOT / candidate.path / "package.json").read_text(encoding="utf-8")
        )
        packages[package["name"]] = package
        candidates_by_package[package["name"]] = candidate

    base = packages["@yacosta738/codegauge"]
    optional_dependencies = base["optionalDependencies"]
    workspace_names = set(packages)
    assert set(optional_dependencies) <= workspace_names

    # Every platform candidate is part of the versions map produced by the
    # linked/workspace flow.  PackageJson.updateContent then visits
    # optionalDependencies just as it visits dependencies/devDependencies.
    updated_versions = {
        package["name"]: linked_versions[candidate.path]
        for package in packages.values()
        if package["name"] in candidates_by_package
        for candidate in (candidates_by_package[package["name"]],)
        if candidate.path in linked_versions
    }
    rewritten = dict(optional_dependencies)
    for dependency, old_version in optional_dependencies.items():
        if dependency not in updated_versions:
            continue
        prefix = next(
            (
                supported
                for supported in ("^", "~", ">=", "<=", ">", "<")
                if old_version.startswith(supported)
            ),
            "",
        )
        rewritten[dependency] = f"{prefix}{updated_versions[dependency]}"

    return "npm/codegauge/package.json", rewritten


def _single_release_operations(
    config: dict[str, Any],
    candidates: list[EffectiveCandidate],
    version: str,
    linked_versions: dict[str, str],
) -> list[tuple[str, str]]:
    """Model the effective Stage-A release operation and its canonical tag."""

    assert config.get("include-component-in-tag") is True
    potential_operations = []
    for candidate in candidates:
        # The root strategy deliberately has an empty strategy component so the
        # merged/root release uses the unprefixed tag. LinkedVersions still
        # groups it by its configured component, while non-root candidates
        # remain version carriers with GitHub releases disabled.
        if candidate.path not in linked_versions and candidate.path != ".":
            continue
        tag = (
            f"{candidate.strategy_component}-v{version}"
            if candidate.strategy_component
            else f"v{version}"
        )
        potential_operations.append((candidate.path, tag))

    assert ("crates/codegauge-cli", f"codegauge-cli-v{version}") in potential_operations
    assert (".", f"v{version}") in potential_operations
    assert all(
        not candidate.skip_github_release
        for candidate in candidates
        if candidate.path == "."
    )
    return [operation for operation in potential_operations if operation[0] == "."]


def _linked_root_candidate_17_6_0(
    config: dict[str, Any],
    candidates: list[EffectiveCandidate],
    root_update_paths: set[str],
    optional_update_path: str,
) -> tuple[str, set[str]]:
    """Model LinkedVersions -> Merge returning one effective root candidate."""

    linked_components = {
        component
        for plugin in config["plugins"]
        if isinstance(plugin, dict) and plugin.get("type") == "linked-versions"
        for component in plugin["components"]
    }
    linked_candidates = [
        candidate for candidate in candidates if candidate.component in linked_components
    ]
    assert {candidate.path for candidate in linked_candidates} == RUNTIME_GRAPH_PATHS

    # Merge.run returns a candidate at ROOT_PROJECT_PATH and concatenates the
    # surviving candidate updates before deduplicating their paths.
    return ".", set(root_update_paths) | {optional_update_path}


def assert_release_please_17_6_0_root_pipeline(config: dict[str, Any]) -> None:
    """Exercise the effective root/plugin path, not only configuration shape."""

    assert RELEASE_PLEASE_VERSION == "17.6.0"
    candidates = _effective_candidates(config)
    root = next(candidate for candidate in candidates if candidate.path == ".")

    after_cargo = _explicit_runtime_candidates_17_6_0(candidates)
    assert root in after_cargo, (
        "the explicit Stage-A runtime list must retain the effective root candidate"
    )

    root_updates = _root_extra_update_paths(root)
    assert root_updates == ROOT_EXTRA_PATHS, (
        "the surviving root candidate must own every repository-level extra-file update"
    )
    root_extra_files = {
        extra_file["path"]: extra_file
        for extra_file in root.extra_files
        if isinstance(extra_file, dict)
    }
    assert root_extra_files["/tests/golden/valid-methods.json"] == {
        "type": "json",
        "path": "/tests/golden/valid-methods.json",
        "jsonpath": "$.tool.version",
    }, "the conformance golden must use the typed JSON updater"
    assert root_extra_files["/tests/golden/typescript-valid.json"] == {
        "type": "json",
        "path": "/tests/golden/typescript-valid.json",
        "jsonpath": "$.tool.version",
    }, "the TypeScript golden must use the typed JSON updater"
    assert root_extra_files["/README.md"] == {
        "type": "generic",
        "path": "/README.md",
    }
    assert root_extra_files["/crates/codegauge-model/tests/contracts.rs"] == {
        "type": "generic",
        "path": "/crates/codegauge-model/tests/contracts.rs",
    }
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    contracts = (
        ROOT / "crates" / "codegauge-model" / "tests" / "contracts.rs"
    ).read_text(encoding="utf-8")
    assert readme.count("x-release-please-version") == 4, (
        "README must mark only its four release-version lines"
    )
    assert contracts.count("x-release-please-version") == 2, (
        "contract fixtures must mark both release-version lines"
    )
    assert "x-release-please-version" not in (
        ROOT / "crates" / "codegauge-cli" / "tests" / "cli.rs"
    ).read_text(encoding="utf-8")
    assert not any(
        isinstance(plugin, dict) and plugin.get("type") == "cargo-workspace"
        for plugin in config.get("plugins", [])
    ), "Stage A must use the explicit runtime Cargo package list, not cargo-workspace discovery"

    linked_versions = _linked_versions_preconfigure_17_6_0(config, after_cargo)
    assert set(linked_versions) == RUNTIME_GRAPH_PATHS - {"."}, (
        "Release Please 17.6.0 LinkedVersions.preconfigure must retain every "
        "non-root runtime component while the root strategy emits an unprefixed tag"
    )
    assert set(linked_versions.values()) == {NEW_RELEASE_VERSION}, (
        "linked-versions must force every runtime candidate to the primary release version"
    )

    optional_update_path, rewritten_optional_dependencies = (
        _node_workspace_optional_update_17_6_0(config, after_cargo, linked_versions)
    )
    assert optional_update_path == "npm/codegauge/package.json"
    assert rewritten_optional_dependencies == {
        dependency: NEW_RELEASE_VERSION
        for dependency in rewritten_optional_dependencies
    }
    assert set(rewritten_optional_dependencies.values()) == {NEW_RELEASE_VERSION}

    effective_root_path, effective_root_updates = _linked_root_candidate_17_6_0(
        config, after_cargo, root_updates, optional_update_path
    )
    assert effective_root_path == "."
    assert root_updates <= effective_root_updates
    assert optional_update_path in effective_root_updates
    assert root.strategy_component == "", (
        "the root strategy must omit its component only for the canonical tag"
    )
    assert not root.skip_github_release, "the canonical root candidate owns the GitHub release"
    assert "package-name" not in config["packages"]["."]

    operations = _single_release_operations(
        config, candidates, NEW_RELEASE_VERSION, linked_versions
    )
    assert operations == [(".", f"v{NEW_RELEASE_VERSION}")], (
        "Stage A must create exactly one unprefixed canonical Release Please tag and release"
    )


def test_publishable_typescript_provider_is_in_release_graph() -> None:
    config = json.loads(
        (ROOT / "release-please-config.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (ROOT / ".release-please-manifest.json").read_text(encoding="utf-8")
    )
    packages = config["packages"]
    linked_components = {
        component
        for plugin in config["plugins"]
        if plugin.get("type") == "linked-versions"
        for component in plugin["components"]
    }
    root_extra_files = packages["."]["extra-files"]
    root_extra_text = json.dumps(root_extra_files)

    assert "crates/codegauge-provider-typescript" in packages
    assert manifest["crates/codegauge-provider-typescript"] == "0.3.0"
    assert "codegauge-provider-typescript" in linked_components
    assert "/crates/codegauge-provider-typescript/Cargo.toml" in root_extra_text
    assert "codegauge-provider-typescript" in root_extra_text

    build_workflow = (ROOT / ".github/workflows/release-build.yml").read_text(
        encoding="utf-8"
    )
    publish_workflow = (ROOT / ".github/workflows/release-publish.yml").read_text(
        encoding="utf-8"
    )
    package_order = [
        build_workflow.index(f"cargo package --locked -p {crate}")
        for crate in (
            "codegauge-model",
            "codegauge-core",
            "codegauge-application",
            "codegauge-provider-jacoco",
            "codegauge-provider-typescript",
            "codegauge-cli",
        )
    ]
    publish_order = [
        publish_workflow.index(f"cargo publish -p {crate}")
        for crate in (
            "codegauge-model",
            "codegauge-core",
            "codegauge-application",
            "codegauge-provider-jacoco",
            "codegauge-provider-typescript",
            "codegauge-cli",
        )
    ]
    assert package_order == sorted(package_order)
    assert publish_order == sorted(publish_order)



def test_historical_release_provenance_allows_13_entry_snapshot_against_current_14_entry_graph() -> None:
    historical = {
        "commit": "cf46ba64bd2e723c28406ca6b7fc3c97d183f1d0",
        "tree": "f9fca04cb359e843bd13ab7ff4db0ff1a9ba4a1c",
        "manifest": {path: NEW_RELEASE_VERSION for path in RUNTIME_GRAPH_PATHS if path != "crates/codegauge-provider-typescript"},
    }
    result = validate_historical_provenance(
        historical,
        version=NEW_RELEASE_VERSION,
        merged_sha="cf46ba64bd2e723c28406ca6b7fc3c97d183f1d0",
        root=ROOT,
        expected_tree=historical["tree"],
    )

    assert result["historical_entry_count"] == 13
    assert result["current_entry_count"] == 14
    assert result["graph_mismatch"] is True
    assert result["commit"] == historical["commit"]
    assert result["tree"] == historical["tree"]
    assert result["merged_sha"] == "cf46ba64bd2e723c28406ca6b7fc3c97d183f1d0"


def test_historical_provenance_rejects_a_different_tree_or_graph_without_subset() -> None:
    historical = {
        "commit": "cf46ba64bd2e723c28406ca6b7fc3c97d183f1d0",
        "tree": "f9fca04cb359e843bd13ab7ff4db0ff1a9ba4a1c",
        "manifest": {path: NEW_RELEASE_VERSION for path in RUNTIME_GRAPH_PATHS if path != "crates/codegauge-provider-typescript"},
    }
    with pytest.raises(ProvenanceError, match="historical provenance is anchored"):
        validate_historical_provenance(
            {**historical, "tree": "0" * 40},
            version=NEW_RELEASE_VERSION,
            merged_sha=historical["commit"],
            root=ROOT,
            expected_tree=historical["tree"],
        )

    with pytest.raises(ProvenanceError, match="not present in the current graph"):
        validate_historical_provenance(
            {
                "commit": historical["commit"],
                "tree": historical["tree"],
                "manifest": {
                    **{path: value for path, value in historical["manifest"].items() if path != "."},
                    "crates/removed-runtime": NEW_RELEASE_VERSION,
                },
            },
            version=NEW_RELEASE_VERSION,
            merged_sha=historical["commit"],
            root=ROOT,
        )

    with pytest.raises(ProvenanceError, match="invalid path"):
        validate_historical_provenance(
            {
                "commit": historical["commit"],
                "tree": historical["tree"],
                "manifest": {
                    **{path: value for path, value in historical["manifest"].items() if path != "."},
                    "../outside": NEW_RELEASE_VERSION,
                },
            },
            version=NEW_RELEASE_VERSION,
            merged_sha=historical["commit"],
            root=ROOT,
        )


def test_release_assets_validate_manifests_checksums_and_required_inputs(tmp_path: Path) -> None:

    archive = tmp_path / "codegauge-0.3.0-x86_64-unknown-linux-gnu.tar.gz"

    archive.write_bytes(b"historical archive")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    sidecar = tmp_path / f"{archive.name}.sha256"
    sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    manifest = tmp_path / "release-manifest-x86_64-unknown-linux-gnu.json"
    manifest.write_text(
        json.dumps({
            "version": NEW_RELEASE_VERSION,
            "source_revision": "a" * 40,
            "target": "x86_64-unknown-linux-gnu",
            "archive": archive.name,
            "sha256": digest,
            "rust_toolchain": "1.97.1",
            "binary_evidence": {
                "target": "x86_64-unknown-linux-gnu",
                "mode": "cross-target",
                "execution": "not-run",
            },
        }),
        encoding="utf-8",
    )

    result = validate_release_assets(
        tmp_path,
        version=NEW_RELEASE_VERSION,
        source_revision="a" * 40,
    )

    assert result == {"manifest_count": 1, "archive_count": 1, "checksum_count": 1}


def test_release_assets_can_require_an_exact_target_matrix(tmp_path: Path) -> None:
    archive = tmp_path / "codegauge-0.3.0-x86_64-unknown-linux-gnu.tar.gz"
    archive.write_bytes(b"historical archive")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (tmp_path / f"{archive.name}.sha256").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    (tmp_path / "release-manifest-x86_64-unknown-linux-gnu.json").write_text(
        json.dumps({
            "version": NEW_RELEASE_VERSION,
            "source_revision": "a" * 40,
            "target": "x86_64-unknown-linux-gnu",
            "archive": archive.name,
            "sha256": digest,
            "rust_toolchain": "1.97.1",
            "binary_evidence": {
                "target": "x86_64-unknown-linux-gnu",
                "mode": "cross-target",
                "execution": "not-run",
            },
        }),
        encoding="utf-8",
    )
    with pytest.raises(ProvenanceError, match="target matrix"):
        validate_release_assets(
            tmp_path,
            version=NEW_RELEASE_VERSION,
            source_revision="a" * 40,
            expected_targets={"x86_64-unknown-linux-gnu", "aarch64-unknown-linux-gnu"},
        )


def test_release_assets_reject_a_tampered_checksum_sidecar(tmp_path: Path) -> None:
    archive = tmp_path / "codegauge-0.3.0-x86_64-unknown-linux-gnu.tar.gz"
    archive.write_bytes(b"historical archive")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (tmp_path / f"{archive.name}.sha256").write_text(
        f"{'0' * 64}  {archive.name}\n", encoding="utf-8"
    )
    (tmp_path / "release-manifest-x86_64-unknown-linux-gnu.json").write_text(
        json.dumps({
            "version": NEW_RELEASE_VERSION,
            "source_revision": "a" * 40,
            "target": "x86_64-unknown-linux-gnu",
            "archive": archive.name,
            "sha256": digest,
            "rust_toolchain": "1.97.1",
            "binary_evidence": {
                "target": "x86_64-unknown-linux-gnu",
                "mode": "cross-target",
                "execution": "not-run",
            },
        }),
        encoding="utf-8",
    )

    with pytest.raises(ProvenanceError, match="checksum"):
        validate_release_assets(
            tmp_path,
            version=NEW_RELEASE_VERSION,
            source_revision="a" * 40,
        )

def test_publication_contract_is_serial_and_at_most_once_per_release_identity() -> None:
    publish = PUBLISH.read_text(encoding="utf-8")
    tag_workflow = (ROOT / ".github/workflows/release-on-tag.yml").read_text(encoding="utf-8")
    assert publication_order(publish) == ("cargo", "npm", "oci")
    assert release_dispatch_count(tag_workflow) == 1
    assert "needs: publish-npm" in publish
    assert "needs: publish-release" in publish
    assert "cancel-in-progress: false" in tag_workflow


def test_publication_contract_rejects_parallel_or_fallback_writers() -> None:
    publish = PUBLISH.read_text(encoding="utf-8")
    tag_workflow = (ROOT / ".github/workflows/release-on-tag.yml").read_text(encoding="utf-8")
    with pytest.raises(ProvenanceError, match="required target|Cargo before npm before OCI"):
        publication_order(publish.replace("docker push", "npm publish", 1))
    with pytest.raises(ProvenanceError, match="exactly once"):
        release_dispatch_count(tag_workflow + "\nuses: ./.github/workflows/release.yml\n")


def test_publisher_verifies_the_exact_canonical_tag_without_stripping_v() -> None:
    publish = PUBLISH.read_text(encoding="utf-8")

    assert 'git/ref/tags/${RELEASE_REF}' in publish
    assert 'git/ref/tags/${RELEASE_REF#v}' not in publish


def main() -> int:
    caller = CALLER.read_text(encoding="utf-8")
    build = BUILD.read_text(encoding="utf-8")
    publish = PUBLISH.read_text(encoding="utf-8")
    release_please = (ROOT / ".github" / "workflows" / "release-please.yml").read_text(encoding="utf-8")
    tag_caller = (ROOT / ".github" / "workflows" / "release-on-tag.yml").read_text(encoding="utf-8")
    config_text = (ROOT / "release-please-config.json").read_text(encoding="utf-8")
    config = json.loads(config_text)
    assert_release_please_17_6_0_root_pipeline(config)

    assert config.get("include-component-in-tag") is True, "Stage A must enable linked components"
    assert "extra-files" not in config, "root extra-files must not be inherited by every package"
    assert "skip-github-release" not in config, "canonical Release Please ownership must not be globally suppressed"

    release_manifest = json.loads(
        (ROOT / ".release-please-manifest.json").read_text(encoding="utf-8")
    )
    assert set(release_manifest) == RUNTIME_GRAPH_PATHS
    assert set(release_manifest.values()) == {NEW_RELEASE_VERSION}

    packages = config.get("packages")
    assert isinstance(packages, dict) and "." in packages, "release-please needs an explicit root candidate"
    root_package = packages["."]
    assert root_package["component"] == "codegauge-root"
    assert root_package["release-type"] == "java"
    assert root_package["initial-version"] == "0.1.0"
    assert root_package["include-component-in-tag"] is False
    assert "skip-github-release" not in root_package
    assert root_package["skip-changelog"] is True
    assert root_package["skip-snapshot"] is True
    assert "package-name" not in root_package
    assert root_package["extra-files"] == [
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
        {
            "type": "toml",
            "path": "/crates/codegauge-conformance/Cargo.toml",
            "jsonpath": '$.dependencies["codegauge-application"].version',
        },
        {
            "type": "toml",
            "path": "/crates/codegauge-conformance/Cargo.toml",
            "jsonpath": '$.dependencies["codegauge-core"].version',
        },
        {
            "type": "toml",
            "path": "/crates/codegauge-conformance/Cargo.toml",
            "jsonpath": '$.dependencies["codegauge-model"].version',
        },
        {
            "type": "toml",
            "path": "/crates/codegauge-conformance/Cargo.toml",
            "jsonpath": '$.dependencies["codegauge-provider-jacoco"].version',
        },
        {
            "type": "toml",
            "path": "/crates/codegauge-conformance/Cargo.toml",
            "jsonpath": '$.dependencies["codegauge-provider-typescript"].version',
        },
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
    ], "root release files must be root-anchored and owned by the root candidate"

    assert packages["crates/codegauge-cli"]["skip-github-release"] is True

    npm_package = packages["npm/codegauge"]
    npm_extra_files = npm_package.get("extra-files", [])
    assert npm_extra_files == [
        {"type": "json", "path": "package.json", "jsonpath": "$.version"}
    ], "npm extra-files must be package-relative without duplicate package.json updates"
    assert all(
        not entry["path"].startswith(("/", "npm/")) for entry in npm_extra_files
    ), "npm extra-files must not be root-anchored or repository-prefixed"

    node_workspace_plugins = [
        plugin
        for plugin in config.get("plugins", [])
        if isinstance(plugin, dict) and plugin.get("type") == "node-workspace"
    ]
    assert node_workspace_plugins == [
        {"type": "node-workspace", "merge": False}
    ], "optional dependency synchronization must use the minimal non-merging node workspace plugin"
    assert all(
        plugin.get("type") != "node-workspace" or plugin.get("merge") is False
        for plugin in config["plugins"]
    )

    linked_components = {
        component
        for plugin in config["plugins"]
        if isinstance(plugin, dict) and plugin.get("type") == "linked-versions"
        for component in plugin.get("components", [])
    }
    assert "codegauge-root" in linked_components, "root candidate must join the single linked release"
    assert "codegauge-conformance" not in packages, "private conformance must not be publishable"
    assert "codegauge-conformance" not in linked_components, "private conformance must not be release-linked"

    platform_versions = {
        package_name: json.loads(
            (
                ROOT
                / "npm"
                / "packages"
                / package_name.removeprefix("@yacosta738/")
                / "package.json"
            ).read_text(encoding="utf-8")
        )["version"]
        for package_name in (
            "@yacosta738/codegauge-linux-x64-gnu",
            "@yacosta738/codegauge-linux-arm64-gnu",
            "@yacosta738/codegauge-darwin-x64",
            "@yacosta738/codegauge-darwin-arm64",
            "@yacosta738/codegauge-win32-x64-msvc",
            "@yacosta738/codegauge-win32-arm64-msvc",
        )
    }
    base_package = json.loads(
        (ROOT / "npm" / "codegauge" / "package.json").read_text(encoding="utf-8")
    )
    assert base_package["optionalDependencies"] == platform_versions, (
        "npm optionalDependencies must be exactly synchronized with linked platform versions"
    )

    cli_tests = (ROOT / "crates" / "codegauge-cli" / "tests" / "cli.rs").read_text(encoding="utf-8")
    assert 'codegauge 0.1.0\\n' not in cli_tests, "CLI release assertions must follow CARGO_PKG_VERSION"
    assert 'env!("CARGO_PKG_VERSION")' in cli_tests, "CLI version assertion must use the package version"

    assert "workflow_call:" in caller, "release caller must be callable by release-please"
    assert "workflow_dispatch:" in caller, "release caller must preserve manual rehearsal input"
    assert not re.search(r"^\s+push:\s*$", caller, re.MULTILINE), "arbitrary tag pushes must not start publication"
    for input_name in ("release_tag", "release_sha", "main_sha", "release_url", "dry_run"):
        assert f"{input_name}:" in caller, f"caller input is missing: {input_name}"
        assert f"{input_name}: ${{{{ inputs.{input_name} }}}}" in caller
    assert "uses: ./.github/workflows/release-build.yml" in caller
    assert "uses: ./.github/workflows/release-publish.yml" in caller
    assert "needs: release-build" in caller
    assert "secrets: inherit" in caller
    assert "permissions:\n      contents: write" in caller
    assert "inputs.release_tag ||" not in caller, "release jobs must not fall back to a default ref"
    assert "github.ref_name" not in caller, "release jobs must not consume the triggering ref"
    assert "workflow_call:" in build and "workflow_call:" in publish
    assert "release-preflight:" in build
    assert "scripts/verify_release_provenance.py" in build
    assert "verify_release_provenance.py binary" in build
    assert '--mode "${{ matrix.evidence_mode }}"' in build
    assert "gh release upload" in publish and "--clobber" in publish
    assert "gh release create" not in publish, (
        "the post-gate publisher must not create the canonical GitHub Release"
    )
    assert "gh release view" in publish, (
        "the post-gate publisher must verify the existing canonical release"
    )
    assert "release-preflight:" not in publish, "build preflight must gate the publish caller"
    assert "uses: ./.github/workflows/release.yml" not in release_please
    assert "steps.release.outputs" not in release_please
    assert "skip-github-release: true" not in release_please, (
        "Release Please ownership belongs in release-please-config.json"
    )
    assert config.get("skip-github-release", False) is False, (
        "release-please-config.json must preserve canonical Release Please ownership"
    )
    assert 'tags: ["v*.*.*"]' in tag_caller
    assert "github.ref_name" in tag_caller and "github.sha" in tag_caller

    version = read_workspace_version(ROOT)
    validate_package_versions(version)
    validate_historical_provenance(
        {
            "tree": "84f44690af8c1105666f8e62d8dcffa9b44c8f2b",
            "manifest": {
                path: NEW_RELEASE_VERSION
                for path in RUNTIME_GRAPH_PATHS
                if path != "crates/codegauge-provider-typescript"
            },
        },
        version=NEW_RELEASE_VERSION,
        merged_sha="cf46ba64bd2e723c28406ca6b7fc3c97d183f1d0",
        root=ROOT,
        expected_tree="84f44690af8c1105666f8e62d8dcffa9b44c8f2b",
    )
    for component in (
        "codegauge-linux-x64-gnu",
        "codegauge-linux-arm64-gnu",
        "codegauge-darwin-x64",
        "codegauge-darwin-arm64",
        "codegauge-win32-x64-msvc",
        "codegauge-win32-arm64-msvc",
    ):
        assert config_text.count(f'"{component}"') >= 2, f"linked release-please component is missing: {component}"

    validate_linked_components(ROOT)
    try:
        validate_package_versions("9.9.9", ROOT)
    except ProvenanceError:
        pass
    else:
        raise AssertionError("Cargo/npm version drift was accepted")
    assert (
        validate_release_identity(
            release_tag="v0.1.0",
            release_sha="a" * 40,
            main_sha="a" * 40,
            tag_revision="a" * 40,
            main_revision="a" * 40,
        )
        == "0.1.0"
    )
    for invalid in (
        {
            "release_tag": "0.1.0",
            "release_sha": "a" * 40,
            "main_sha": "a" * 40,
            "tag_revision": "a" * 40,
            "main_revision": "a" * 40,
        },
        {
            "release_tag": "v0.1.0",
            "release_sha": "a" * 40,
            "main_sha": "b" * 40,
            "tag_revision": "a" * 40,
            "main_revision": "b" * 40,
        },
    ):
        try:
            validate_release_identity(**invalid)
        except ProvenanceError:
            pass
        else:
            raise AssertionError("unsafe release provenance was accepted")

    directory = Path(tempfile.mkdtemp(prefix="codegauge-release-provenance-test-"))
    try:
        binary = directory / "codegauge"
        binary.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  version) printf 'codegauge 0.1.0\\n' ;;\n"
            "  profiles) printf 'jvm-jacoco-v1\\ntypescript-oxc-istanbul-v1\\n' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        binary.chmod(0o755)
        native_evidence = directory / "native.json"
        write_binary_evidence(
            binary=binary,
            version="0.1.0",
            target="x86_64-unknown-linux-gnu",
            mode="native",
            output=native_evidence,
        )
        cross_evidence = directory / "cross.json"
        write_binary_evidence(
            binary=binary,
            version="0.1.0",
            target="aarch64-pc-windows-msvc",
            mode="cross-target",
            output=cross_evidence,
        )
        assert json.loads(cross_evidence.read_text(encoding="utf-8"))["execution"] == "not-run"
        try:
            write_binary_evidence(
                binary=binary,
                version="0.2.0",
                target="x86_64-unknown-linux-gnu",
                mode="native",
                output=directory / "wrong-version.json",
            )
        except ProvenanceError:
            pass
        else:
            raise AssertionError("binary version drift was accepted")

        manifest_path = directory / "release-manifest-x86_64-unknown-linux-gnu.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "0.1.0",
                    "source_revision": "a" * 40,
                    "target": "x86_64-unknown-linux-gnu",
                    "archive": "codegauge-0.1.0-x86_64-unknown-linux-gnu.tar.gz",
                    "rust_toolchain": "1.97.1",
                    "sha256": "0" * 64,
                    "binary_evidence": json.loads(native_evidence.read_text(encoding="utf-8")),
                }
            ),
            encoding="utf-8",
        )
        validate_archive_manifest(manifest_path, "0.1.0", "a" * 40)
        tampered = json.loads(manifest_path.read_text(encoding="utf-8"))
        tampered["source_revision"] = "b" * 40
        manifest_path.write_text(json.dumps(tampered), encoding="utf-8")
        try:
            validate_archive_manifest(manifest_path, "0.1.0", "a" * 40)
        except ProvenanceError:
            pass
        else:
            raise AssertionError("archive source revision drift was accepted")
    finally:
        rmtree(directory)

    print("RELEASE PROVENANCE TESTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
