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
PRIVATE_DEPENDENCIES = (
    "codegauge-application",
    "codegauge-core",
    "codegauge-model",
    "codegauge-provider-jacoco",
)

sys.path.insert(0, str(ROOT))

from scripts.verify_release_provenance import ProvenanceError, validate_stage_a_diff  # noqa: E402


def private_patch(extra_changes: str = "") -> str:
    lines = [
        "diff --git a/crates/codegauge-conformance/Cargo.toml b/crates/codegauge-conformance/Cargo.toml",
        "index 1111111..2222222 100644",
        "--- a/crates/codegauge-conformance/Cargo.toml",
        "+++ b/crates/codegauge-conformance/Cargo.toml",
        "@@ -10,11 +10,11 @@ description = \"Private cross-crate CodeGauge conformance suite\"",
        ' description = "Private cross-crate CodeGauge conformance suite"',
        " ",
        " [dependencies]",
    ]
    for dependency in PRIVATE_DEPENDENCIES:
        lines.extend(
            [
                f'-{dependency} = {{ version = "0.1.0", path = "../{dependency}" }}',
                f'+{dependency} = {{ version = "0.2.0", path = "../{dependency}" }}',
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


def private_entry(patch: str | None = None, *, additions: int = 4, deletions: int = 4):
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


def stage_a_prefix() -> list[dict[str, object]]:
    crates = (
        "codegauge-model",
        "codegauge-core",
        "codegauge-application",
        "codegauge-provider-jacoco",
        "codegauge-cli",
    )
    manifest = json.loads(
        (ROOT / ".release-please-manifest.json").read_text(encoding="utf-8")
    )
    manifest_pairs = [
        (f'  "{path}": "{old}",', f'  "{path}": "0.2.0",')
        for path, old in manifest.items()
    ]
    base_package = json.loads(
        (ROOT / "npm" / "codegauge" / "package.json").read_text(encoding="utf-8")
    )
    npm_pairs = [
        (f'  "version": "{base_package["version"]}",', '  "version": "0.2.0",')
    ] + [
        (f'    "{dependency}": "{old}",', f'    "{dependency}": "0.2.0",')
        for dependency, old in base_package["optionalDependencies"].items()
    ]
    return [
        content_entry(
            "Cargo.toml",
            [('version = "0.1.0"', 'version = "0.2.0"')],
            context=(" [workspace.package]",),
        ),
        content_entry(
            "Cargo.lock",
            [('version = "0.1.0"', 'version = "0.2.0"')] * len(crates),
            context=tuple(f' name = "{crate}"' for crate in crates),
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
            version="0.2.0",
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
                private_patch('@@ -1 +1 @@\n-version = "0.1.0"\n+version = "0.2.0"'),
                additions=5,
                deletions=5,
            ),
        ),
        (
            "publish-flag",
            private_entry(
                private_patch("@@ -7 +7 @@\n-publish = false\n+publish = true"),
                additions=5,
                deletions=5,
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
                version="0.2.0",
            )
        except ProvenanceError:
            print(f"PRIVATE MUTATION {mutation_name}: REJECTED")
        else:
            print(f"PRIVATE MUTATION {mutation_name}: ACCEPTED")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
