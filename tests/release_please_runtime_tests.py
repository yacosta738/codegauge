#!/usr/bin/env python3
"""Run the exact Release Please 17.6.0 chain against a read-only fake SCM."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "release_please_runtime_harness.mjs"
PRIVATE_CONFORMANCE_PATH = "crates/codegauge-conformance/Cargo.toml"
BASELINE_VERSION = "0.2.0"
TARGET_VERSION = "0.3.0"
STAGE_A_MANIFEST_PATHS = (
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
)
STAGE_A_RUNTIME_CRATES = (
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-provider-typescript",
    "codegauge-cli",
)
STAGE_A_OPTIONAL_DEPENDENCIES = (
    "@yacosta738/codegauge-linux-x64-gnu",
    "@yacosta738/codegauge-linux-arm64-gnu",
    "@yacosta738/codegauge-darwin-x64",
    "@yacosta738/codegauge-darwin-arm64",
    "@yacosta738/codegauge-win32-x64-msvc",
    "@yacosta738/codegauge-win32-arm64-msvc",
)
PRIVATE_DEPENDENCIES = (
    "codegauge-application",
    "codegauge-core",
    "codegauge-model",
    "codegauge-provider-jacoco",
    "codegauge-provider-typescript",
)

sys.path.insert(0, str(ROOT))

from scripts.verify_release_provenance import ProvenanceError, validate_stage_a_diff  # noqa: E402


def private_patch(extra_changes: str = "") -> str:
    lines = [
        "diff --git a/crates/codegauge-conformance/Cargo.toml b/crates/codegauge-conformance/Cargo.toml",
        "index 1111111..2222222 100644",
        "--- a/crates/codegauge-conformance/Cargo.toml",
        "+++ b/crates/codegauge-conformance/Cargo.toml",
        "@@ -10,12 +10,12 @@ description = \"Private cross-crate CodeGauge conformance suite\"",
        ' description = "Private cross-crate CodeGauge conformance suite"',
        " ",
        " [dependencies]",
    ]
    for dependency in PRIVATE_DEPENDENCIES:
        lines.extend(
            [
                f'-{dependency} = {{ version = "{BASELINE_VERSION}", path = "../{dependency}" }}',
                f'+{dependency} = {{ version = "{TARGET_VERSION}", path = "../{dependency}" }}',
            ]
        )
    lines.extend(
        [
            " ",
            " [dev-dependencies]",
            " schemars.workspace = true",
            " serde_json.workspace = true",
        ]
    )
    if extra_changes:
        lines.extend(extra_changes.splitlines())
    return "\n".join(lines) + "\n"


def private_entry(patch: str | None = None, *, additions: int = 5, deletions: int = 5):
    entry = {
        "filename": PRIVATE_CONFORMANCE_PATH,
        "status": "modified",
        "additions": additions,
        "deletions": deletions,
        "changes": additions + deletions,
    }
    if patch is not None:
        entry["patch"] = patch
    return entry


def content_entry(path: str, pairs: list[tuple[str, str]], *, context: tuple[str, ...] = ()):
    lines = [
        f"diff --git a/{path} b/{path}",
        f"--- a/{path}",
        f"+++ b/{path}",
        f"@@ -1,{len(context) + len(pairs)} +1,{len(context) + len(pairs)} @@",
        *context,
    ]
    lines.extend(line for old, new in pairs for line in (f"-{old}", f"+{new}"))
    return {
        "filename": path,
        "status": "modified",
        "additions": len(pairs),
        "deletions": len(pairs),
        "changes": len(pairs) * 2,
        "patch": "\n".join(lines) + "\n",
    }


def _entry_for(entries: list[dict[str, object]], filename: str) -> dict[str, object]:
    matches = [entry for entry in entries if entry.get("filename") == filename]
    assert len(matches) == 1, f"expected one fixture entry for {filename}, found {len(matches)}"
    return matches[0]


def _patch_text(entry: dict[str, object]) -> str:
    patch = entry.get("patch")
    assert isinstance(patch, str), "fixture entry must contain a textual patch"
    return patch


def _replace_patch_line(
    entry: dict[str, object],
    old_line: str,
    new_line: str,
) -> dict[str, object]:
    patch = _patch_text(entry)
    assert old_line in patch, f"fixture patch does not contain expected line: {old_line}"
    mutated = dict(entry)
    mutated["patch"] = patch.replace(old_line, new_line, 1)
    return mutated


def test_stage_a_prefix_builds_historical_fixture() -> None:
    entries = stage_a_prefix()
    manifest = _entry_for(entries, ".release-please-manifest.json")
    manifest_patch = _patch_text(manifest)
    assert manifest["additions"] == len(STAGE_A_MANIFEST_PATHS)
    assert manifest["deletions"] == len(STAGE_A_MANIFEST_PATHS)
    for path in STAGE_A_MANIFEST_PATHS:
        assert f'-  "{path}": "{BASELINE_VERSION}",' in manifest_patch
        assert f'+  "{path}": "{TARGET_VERSION}",' in manifest_patch

    npm = _entry_for(entries, "npm/codegauge/package.json")
    npm_patch = _patch_text(npm)
    assert f'-  "version": "{BASELINE_VERSION}",' in npm_patch
    assert f'+  "version": "{TARGET_VERSION}",' in npm_patch
    for dependency in STAGE_A_OPTIONAL_DEPENDENCIES:
        assert f'-    "{dependency}": "{BASELINE_VERSION}",' in npm_patch
        assert f'+    "{dependency}": "{TARGET_VERSION}",' in npm_patch

    validate_stage_a_diff(
        [*entries, private_entry(private_patch())],
        version=TARGET_VERSION,
    )


def test_stage_a_fixture_rejects_noop_and_wrong_version() -> None:
    entries = stage_a_prefix()
    manifest = _entry_for(entries, ".release-please-manifest.json")
    private = private_entry(private_patch())
    mutations = (
        (
            "no-op",
            _replace_patch_line(
                manifest,
                f'-  ".": "{BASELINE_VERSION}",',
                f'-  ".": "{TARGET_VERSION}",',
            ),
        ),
        (
            "wrong-version",
            _replace_patch_line(
                manifest,
                f'+  ".": "{TARGET_VERSION}",',
                '+  ".": "0.4.0",',
            ),
        ),
    )
    for mutation_name, mutated_manifest in mutations:
        mutated_entries = [
            mutated_manifest if entry is manifest else entry for entry in entries
        ]
        try:
            validate_stage_a_diff(
                [*mutated_entries, private],
                version=TARGET_VERSION,
            )
        except ProvenanceError:
            continue
        raise AssertionError(f"Stage-A fixture accepted {mutation_name} manifest replacement")


def stage_a_prefix() -> list[dict[str, object]]:
    if BASELINE_VERSION == TARGET_VERSION:
        raise AssertionError("historical fixture baseline and target versions must differ")

    manifest = json.loads(
        (ROOT / ".release-please-manifest.json").read_text(encoding="utf-8")
    )
    if set(manifest) != set(STAGE_A_MANIFEST_PATHS):
        raise AssertionError("current Release Please manifest has an unexpected path set")
    if any(value != TARGET_VERSION for value in manifest.values()):
        raise AssertionError("current Release Please manifest is not at the expected target version")
    manifest_pairs = [
        (
            f'  "{path}": "{BASELINE_VERSION}",',
            f'  "{path}": "{TARGET_VERSION}",',
        )
        for path in STAGE_A_MANIFEST_PATHS
    ]
    base_package = json.loads(
        (ROOT / "npm" / "codegauge" / "package.json").read_text(encoding="utf-8")
    )
    optional_dependencies = base_package.get("optionalDependencies")
    if not isinstance(optional_dependencies, dict):
        raise AssertionError("npm wrapper optionalDependencies must be an object")
    if set(optional_dependencies) != set(STAGE_A_OPTIONAL_DEPENDENCIES):
        raise AssertionError("npm wrapper has an unexpected optional dependency set")
    if base_package.get("version") != TARGET_VERSION:
        raise AssertionError("npm wrapper is not at the expected target version")
    if any(value != TARGET_VERSION for value in optional_dependencies.values()):
        raise AssertionError("npm wrapper optional dependencies are not at the expected target")
    npm_pairs = [
        (
            f'  "version": "{BASELINE_VERSION}",',
            f'  "version": "{TARGET_VERSION}",',
        )
    ] + [
        (
            f'    "{dependency}": "{BASELINE_VERSION}",',
            f'    "{dependency}": "{TARGET_VERSION}",',
        )
        for dependency in STAGE_A_OPTIONAL_DEPENDENCIES
    ]
    return [
        content_entry(
            "Cargo.toml",
            [(f'version = "{BASELINE_VERSION}"', f'version = "{TARGET_VERSION}"')],
            context=(" [workspace.package]",),
        ),
        content_entry(
            "Cargo.lock",
            [
                (f'version = "{BASELINE_VERSION}"', f'version = "{TARGET_VERSION}"')
            ]
            * len(STAGE_A_RUNTIME_CRATES),
            context=tuple(f' name = "{crate}"' for crate in STAGE_A_RUNTIME_CRATES),
        ),
        content_entry(".release-please-manifest.json", manifest_pairs),
        content_entry("npm/codegauge/package.json", npm_pairs),
    ]


def find_exact_package() -> Path | None:
    configured = os.environ.get("RELEASE_PLEASE_17_6_0_ROOT")
    candidates = [Path(configured)] if configured else []
    candidates.extend(
        path.parent
        for path in Path.home().joinpath(".npm", "_npx").glob(
            "*/node_modules/release-please/package.json"
        )
    )
    candidates.append(ROOT / "node_modules" / "release-please")
    for candidate in candidates:
        if candidate is None:
            continue
        package_json = candidate / "package.json"
        try:
            if json.loads(package_json.read_text(encoding="utf-8")).get("version") == "17.6.0":
                return candidate
        except (OSError, json.JSONDecodeError):
            continue
    return None


def main() -> int:
    test_stage_a_prefix_builds_historical_fixture()
    test_stage_a_fixture_rejects_noop_and_wrong_version()

    package_root = find_exact_package()
    if package_root is None:
        print(
            "RELEASE PLEASE V17.6.0 RUNTIME TESTS: UNTESTED "
            "(exact package is not installed; no JSON-shape substitute was claimed)"
        )
        return 0

    environment = {
        **os.environ,
        "CODEGAUGE_ROOT": str(ROOT),
        "RELEASE_PLEASE_17_6_0_ROOT": str(package_root),
    }
    result = subprocess.run(
        ["node", str(HARNESS)],
        check=False,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        return result.returncode

    try:
        validate_stage_a_diff(
            [
                *stage_a_prefix(),
                private_entry(private_patch()),
            ],
            version=TARGET_VERSION,
        )
    except ProvenanceError:
        print("PRIVATE DEPENDENCY PIN UPDATE: REJECTED")
        return 1
    else:
        print("PRIVATE DEPENDENCY PIN UPDATE: ACCEPTED")

    mutations = (
        (
            "package-version",
            private_entry(
                private_patch(
                    f'@@ -1 +1 @@\n-version = "{BASELINE_VERSION}"\n'
                    f'+version = "{TARGET_VERSION}"'
                ),
                additions=6,
                deletions=6,
            ),
        ),
        (
            "publish-flag",
            private_entry(
                private_patch("@@ -7 +7 @@\n-publish = false\n+publish = true"),
                additions=6,
                deletions=6,
            ),
        ),
        (
            "unrelated-private-path",
            {"filename": "crates/codegauge-conformance/CHANGELOG.md", "patch": "@@"},
        ),
    )
    for mutation_name, mutation in mutations:
        try:
            validate_stage_a_diff(
                [
                    *stage_a_prefix(),
                    mutation,
                ],
                version=TARGET_VERSION,
            )
        except ProvenanceError:
            print(f"PRIVATE MUTATION {mutation_name}: REJECTED")
        else:
            print(f"PRIVATE MUTATION {mutation_name}: ACCEPTED")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
