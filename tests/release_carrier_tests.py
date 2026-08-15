#!/usr/bin/env python3
"""Deterministic R-F6 carrier regressions.

These tests exercise the pure carrier boundary with a copied release tree.  No
GitHub API, credential, tag, release, package, or registry write is permitted.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from shutil import copytree, ignore_patterns


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.verify_release_provenance import (  # noqa: E402
    CarrierRecord,
    ProvenanceError,
    VERSION_RE,
    classify_carrier_prs,
    plan_carrier_tag,
    select_matching_release_please_prs,
    validate_carrier_event,
    validate_carrier_release_slot,
    validate_carrier_tree,
    validate_stage_a_diff,
)


SHA = "a" * 40
OTHER_SHA = "b" * 40
VERSION = "0.2.0"
PRIVATE_CONFORMANCE_PATH = "crates/codegauge-conformance/Cargo.toml"
PRIVATE_CONFORMANCE_DEPENDENCIES = (
    "codegauge-application",
    "codegauge-core",
    "codegauge-model",
    "codegauge-provider-jacoco",
)


def private_conformance_patch(
    *,
    version: str = VERSION,
    extra_changes: str = "",
) -> str:
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
    for dependency in PRIVATE_CONFORMANCE_DEPENDENCIES:
        lines.extend(
            [
                f'-{dependency} = {{ version = "0.1.0", path = "../{dependency}" }}',
                f'+{dependency} = {{ version = "{version}", path = "../{dependency}" }}',
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


def private_conformance_entry(
    *,
    patch: str | None = None,
    additions: int = 4,
    deletions: int = 4,
    changes: int = 8,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "filename": PRIVATE_CONFORMANCE_PATH,
        "status": "modified",
        "additions": additions,
        "deletions": deletions,
        "changes": changes,
    }
    if patch is not None:
        entry["patch"] = patch
    return entry


PRIVATE_CONFORMANCE_DIFF = private_conformance_entry(
    patch=private_conformance_patch()
)


def carrier_content_entry(
    path: str,
    patch: str,
    *,
    status: str = "modified",
    additions: int = 1,
    deletions: int = 1,
) -> dict[str, object]:
    return {
        "filename": path,
        "status": status,
        "additions": additions,
        "deletions": deletions,
        "changes": additions + deletions,
        "patch": patch,
    }


def line_patch(path: str, old: str, new: str) -> str:
    return "\n".join(
        [
            f"diff --git a/{path} b/{path}",
            f"--- a/{path}",
            f"+++ b/{path}",
            "@@ -1 +1 @@",
            f"-{old}",
            f"+{new}",
            "",
        ]
    )


GOLDEN_JSON_PATH = "tests/golden/valid-methods.json"
README_PATH = "README.md"
CONTRACTS_PATH = "crates/codegauge-model/tests/contracts.rs"
GENERATED_CHANGELOG_PATH = "crates/codegauge-model/CHANGELOG.md"


def patch_with_pairs(
    path: str,
    pairs: list[tuple[str, str]],
    *,
    context: tuple[str, ...] = (),
    status: str = "modified",
) -> str:
    if status == "added":
        header = [
            f"diff --git a/{path} b/{path}",
            "new file mode 100644",
            "--- /dev/null",
            f"+++ b/{path}",
            f"@@ -0,0 +1,{len(pairs)} @@",
        ]
        return "\n".join(header + [f"+{new}" for _, new in pairs] + [""])
    header = [
        f"diff --git a/{path} b/{path}",
        f"--- a/{path}",
        f"+++ b/{path}",
        f"@@ -1,{len(pairs)} +1,{len(pairs)} @@",
    ]
    return "\n".join(
        header
        + list(context)
        + [line for old, new in pairs for line in (f"-{old}", f"+{new}")]
        + [""],
    )


def valid_root_cargo_entry() -> dict[str, object]:
    old = 'version = "0.1.0"'
    new = 'version = "0.2.0"'
    return carrier_content_entry(
        "Cargo.toml",
        patch_with_pairs("Cargo.toml", [(old, new)], context=(" [workspace.package]",)),
    )


def valid_lock_entry() -> dict[str, object]:
    crates = (
        "codegauge-model",
        "codegauge-core",
        "codegauge-application",
        "codegauge-provider-jacoco",
        "codegauge-cli",
    )
    pairs = [(f'version = "0.1.0"', 'version = "0.2.0"') for _ in crates]
    context = tuple(f' name = "{crate}"' for crate in crates)
    return carrier_content_entry(
        "Cargo.lock",
        patch_with_pairs("Cargo.lock", pairs, context=context),
        additions=len(pairs),
        deletions=len(pairs),
    )


def valid_release_manifest_entry() -> dict[str, object]:
    manifest = json.loads(
        (ROOT / ".release-please-manifest.json").read_text(encoding="utf-8")
    )
    pairs = [
        (f'  "{path}": "{old_version}",', f'  "{path}": "{VERSION}",')
        for path, old_version in manifest.items()
    ]
    return carrier_content_entry(
        ".release-please-manifest.json",
        patch_with_pairs(
            ".release-please-manifest.json",
            pairs,
            context=(" {", " }"),
        ),
        additions=len(pairs),
        deletions=len(pairs),
    )


def valid_golden_entry() -> dict[str, object]:
    path = ROOT / GOLDEN_JSON_PATH
    before = path.read_text(encoding="utf-8").rstrip("\n")
    after = before.replace('"version":"0.1.0"', '"version":"0.2.0"', 1)
    return carrier_content_entry(
        GOLDEN_JSON_PATH,
        patch_with_pairs(GOLDEN_JSON_PATH, [(before, after)]),
    )


def valid_annotated_entry(path: str) -> dict[str, object]:
    before_lines = [
        line
        for line in (ROOT / path).read_text(encoding="utf-8").splitlines()
        if "x-release-please-version" in line
    ]
    pairs = [(line, line.replace("0.1.0", VERSION, 1)) for line in before_lines]
    return carrier_content_entry(
        path,
        patch_with_pairs(path, pairs),
        additions=len(pairs),
        deletions=len(pairs),
    )


def valid_changelog_entry(path: str = GENERATED_CHANGELOG_PATH) -> dict[str, object]:
    lines = ("# Changelog", "## 0.2.0", "", "* chore: synchronized runtime graph")
    return carrier_content_entry(
        path,
        patch_with_pairs(path, [("", line) for line in lines], status="added"),
        status="added",
        additions=len(lines),
        deletions=0,
    )


def valid_npm_entry(path: str = "npm/codegauge/package.json") -> dict[str, object]:
    package = json.loads((ROOT / path).read_text(encoding="utf-8"))
    pairs = [(f'  "version": "{package["version"]}",', '  "version": "0.2.0",')]
    if path == "npm/codegauge/package.json":
        pairs.extend(
            (f'    "{dependency}": "{old}",', f'    "{dependency}": "0.2.0",')
            for dependency, old in package["optionalDependencies"].items()
        )
    return carrier_content_entry(
        path,
        patch_with_pairs(path, pairs),
        additions=len(pairs),
        deletions=len(pairs),
    )


CORE_STAGE_A_DIFF = [
    valid_root_cargo_entry(),
    valid_lock_entry(),
    valid_release_manifest_entry(),
    valid_npm_entry(),
]


DIFF = [
    *CORE_STAGE_A_DIFF,
    PRIVATE_CONFORMANCE_DIFF,
]

APPROVED_NPM_PACKAGE_DIFFS = (
    "npm/codegauge/package.json",
    "npm/packages/codegauge-linux-x64-gnu/package.json",
    "npm/packages/codegauge-linux-arm64-gnu/package.json",
    "npm/packages/codegauge-darwin-x64/package.json",
    "npm/packages/codegauge-darwin-arm64/package.json",
    "npm/packages/codegauge-win32-x64-msvc/package.json",
    "npm/packages/codegauge-win32-arm64-msvc/package.json",
)

ROOT_CARRIER_PATHS = (
    "Cargo.toml",
    "Cargo.lock",
    "crates/codegauge-core/Cargo.toml",
    "crates/codegauge-application/Cargo.toml",
    "crates/codegauge-provider-jacoco/Cargo.toml",
    "crates/codegauge-cli/Cargo.toml",
    "README.md",
    "tests/golden/valid-methods.json",
    "crates/codegauge-model/tests/contracts.rs",
    "crates/codegauge-cli/tests/cli.rs",
    PRIVATE_CONFORMANCE_PATH,
)


def release_pr(merge_sha: str = SHA, number: int = 42) -> dict[str, object]:
    return {
        "number": number,
        "title": "chore: release codegauge runtime graph libraries",
        "body": (
            ":robot: I have created a release *beep* *boop*\n"
            "---\n\n"
            "<details><summary>codegauge-cli: 0.2.0</summary>\n\n"
            "release notes\n</details>\n\n"
            "---\n"
            "This PR was generated with [Release Please](https://github.com/googleapis/release-please)."
        ),
        "labels": [{"name": "autorelease: pending"}],
        "base": {"ref": "main", "repo": {"full_name": "yacosta738/codegauge"}},
        "merged_at": "2026-08-14T12:00:00Z",
        "merge_commit_sha": merge_sha,
    }


def ordinary_main_pr(merge_sha: str = SHA, number: int = 59) -> dict[str, object]:
    pull_request = release_pr(merge_sha=merge_sha, number=number)
    pull_request.update(
        {
            "title": "feat: add a carrier rehearsal fixture",
            "body": "ordinary feature pull request",
            "labels": [],
        }
    )
    return pull_request


def copy_release_tree() -> Path:
    directory = Path(tempfile.mkdtemp(prefix="codegauge-carrier-test-"))
    fixture = directory / "repo"
    copytree(
        ROOT,
        fixture,
        ignore=ignore_patterns(".git", "target", "node_modules", "dist", "__pycache__", "release-out"),
    )
    versioned_files = [
        fixture / "Cargo.toml",
        fixture / "Cargo.lock",
        fixture / ".release-please-manifest.json",
        *(
            path
            for path in fixture.glob("crates/*/Cargo.toml")
            if path.parent.name != "codegauge-conformance"
        ),
        fixture / "npm" / "codegauge" / "package.json",
        *fixture.glob("npm/packages/*/package.json"),
    ]
    for path in versioned_files:
        contents = path.read_text(encoding="utf-8")
        if path.name == "Cargo.lock":
            for crate in (
                "codegauge-model",
                "codegauge-core",
                "codegauge-application",
                "codegauge-provider-jacoco",
                "codegauge-cli",
            ):
                contents = re.sub(
                    rf'(name = "{re.escape(crate)}"\nversion = ")0\.1\.0("$)',
                    rf"\g<1>{VERSION}\g<2>",
                    contents,
                    flags=re.MULTILINE,
                )
        else:
            contents = contents.replace("0.1.0", VERSION)
        path.write_text(contents, encoding="utf-8")
    for relative_path in (README_PATH, CONTRACTS_PATH):
        path = fixture / relative_path
        lines = [
            line.replace("0.1.0", VERSION, 1)
            if "x-release-please-version" in line
            else line
            for line in path.read_text(encoding="utf-8").splitlines()
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    private_manifest = fixture / PRIVATE_CONFORMANCE_PATH
    private_text = private_manifest.read_text(encoding="utf-8")
    for dependency in PRIVATE_CONFORMANCE_DEPENDENCIES:
        private_text = private_text.replace(
            f'{dependency} = {{ version = "0.1.0"',
            f'{dependency} = {{ version = "{VERSION}"',
        )
    private_manifest.write_text(private_text, encoding="utf-8")
    golden_path = fixture / GOLDEN_JSON_PATH
    golden_text = golden_path.read_text(encoding="utf-8")
    golden_path.write_text(
        golden_text.replace('"version":"0.1.0"', f'"version":"{VERSION}"', 1),
        encoding="utf-8",
    )
    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    assert golden["tool"]["version"] == VERSION
    metadata = subprocess.run(
        [
            "cargo",
            "metadata",
            "--manifest-path",
            str(fixture / "Cargo.toml"),
            "--locked",
            "--no-deps",
            "--format-version",
            "1",
        ],
        cwd=fixture,
        check=False,
        capture_output=True,
        text=True,
    )
    assert metadata.returncode == 0, metadata.stderr
    metadata_packages = {
        package["name"]: package
        for package in json.loads(metadata.stdout)["packages"]
    }
    assert metadata_packages["codegauge-conformance"]["version"] == "0.1.0"
    workspace_tests = subprocess.run(
        ["cargo", "test", "--workspace", "--locked"],
        cwd=fixture,
        check=False,
        capture_output=True,
        text=True,
    )
    assert workspace_tests.returncode == 0, workspace_tests.stdout + workspace_tests.stderr
    return fixture


def assert_fails(callable_obj, message: str) -> None:
    try:
        callable_obj()
    except ProvenanceError:
        return
    raise AssertionError(message)


def main() -> int:
    fixture = copy_release_tree()
    try:
        record = validate_carrier_event(
            event_name="push",
            ref="refs/heads/main",
            event_sha=SHA,
            pull_requests=[release_pr()],
            changed_files=DIFF,
            root=fixture,
        )
        assert isinstance(record, CarrierRecord)
        assert record == CarrierRecord(
            version=VERSION,
            tag=f"v{VERSION}",
            merge_sha=SHA,
            version_pr_number=42,
        )
        manual_record = validate_carrier_event(
            event_name="workflow_dispatch",
            ref="refs/heads/main",
            event_sha=SHA,
            pull_requests=[release_pr()],
            changed_files=DIFF,
            root=fixture,
        )
        assert manual_record == record
        mixed_record = validate_carrier_event(
            event_name="push",
            ref="refs/heads/main",
            event_sha=SHA,
            pull_requests=[ordinary_main_pr(), release_pr()],
            changed_files=DIFF,
            root=fixture,
        )
        assert mixed_record == record

        # A normal feature-PR merge can trigger the carrier workflow before the
        # Release Please PR is merged.  That event is a successful no-op and
        # must never enter tree/version/tag validation.
        assert classify_carrier_prs([], SHA) == {
            "status": "skipped",
            "reason": "no-matching-release-please-pr",
            "matching_release_pr_count": 0,
        }
        assert select_matching_release_please_prs([ordinary_main_pr()], SHA) == []
        assert classify_carrier_prs([ordinary_main_pr()], SHA) == {
            "status": "skipped",
            "reason": "no-matching-release-please-pr",
            "matching_release_pr_count": 0,
        }
        assert classify_carrier_prs([ordinary_main_pr(), release_pr()], SHA) == {
            "status": "matched",
            "matching_release_pr_count": 1,
            "version_pr_number": 42,
        }
        assert_fails(
            lambda: classify_carrier_prs(
                [release_pr(), release_pr(number=43)], SHA
            ),
            "carrier accepted more than one matching Release Please PR",
        )
        malformed_pr = ordinary_main_pr()
        del malformed_pr["base"]
        assert_fails(
            lambda: classify_carrier_prs([malformed_pr], SHA),
            "carrier treated malformed PR data as a no-op",
        )
        carrier_inputs = fixture / "carrier-inputs"
        carrier_inputs.mkdir()
        (carrier_inputs / "pull-requests.json").write_text(
            json.dumps([release_pr()]), encoding="utf-8"
        )
        (carrier_inputs / "files.json").write_text(json.dumps(DIFF), encoding="utf-8")
        cli_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_release_provenance.py"),
                "carrier",
                "--event-name",
                "push",
                "--ref",
                "refs/heads/main",
                "--event-sha",
                SHA,
                "--pull-requests",
                str(carrier_inputs / "pull-requests.json"),
                "--pull-request-files",
                str(carrier_inputs / "files.json"),
                "--root",
                str(fixture),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert json.loads(cli_result.stdout) == {
            "version": VERSION,
            "tag": f"v{VERSION}",
            "merge_sha": SHA,
            "version_pr_number": 42,
        }
        manual_cli_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_release_provenance.py"),
                "carrier",
                "--event-name",
                "workflow_dispatch",
                "--ref",
                "refs/heads/main",
                "--event-sha",
                SHA,
                "--pull-requests",
                str(carrier_inputs / "pull-requests.json"),
                "--pull-request-files",
                str(carrier_inputs / "files.json"),
                "--root",
                str(fixture),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert json.loads(manual_cli_result.stdout) == json.loads(cli_result.stdout)

        selection_input = carrier_inputs / "ordinary-pull-requests.json"
        selection_input.write_text(
            json.dumps([ordinary_main_pr()]), encoding="utf-8"
        )
        skip_cli_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_release_provenance.py"),
                "carrier-pr-selection",
                "--event-sha",
                SHA,
                "--pull-requests",
                str(selection_input),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        assert json.loads(skip_cli_result.stdout) == {
            "matching_release_pr_count": 0,
            "reason": "no-matching-release-please-pr",
            "status": "skipped",
        }
        (carrier_inputs / "multiple-release-pull-requests.json").write_text(
            json.dumps([release_pr(), release_pr(number=43)]), encoding="utf-8"
        )
        multiple_cli_result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "verify_release_provenance.py"),
                "carrier-pr-selection",
                "--event-sha",
                SHA,
                "--pull-requests",
                str(carrier_inputs / "multiple-release-pull-requests.json"),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        assert multiple_cli_result.returncode != 0

        for package_path in APPROVED_NPM_PACKAGE_DIFFS:
            validate_stage_a_diff(
                [
                    "Cargo.toml",
                    "Cargo.lock",
                    ".release-please-manifest.json",
                    package_path,
                ]
            )
        for unapproved_path in (
            "npm/packages/codegauge-evil/package.json",
            "npm/packages/codegauge-linux-x86-gnu/package.json",
            "npm/packages/codegauge-linux-x64-gnu/package.json.bak",
        ):
            assert_fails(
                lambda path=unapproved_path: validate_stage_a_diff(
                    ["Cargo.toml", "Cargo.lock", ".release-please-manifest.json", path]
                ),
                f"carrier accepted unapproved npm path {unapproved_path}",
            )

        for approved_content_entry in (
            valid_golden_entry(),
            valid_annotated_entry(README_PATH),
            valid_annotated_entry(CONTRACTS_PATH),
            valid_changelog_entry(),
        ):
            validate_stage_a_diff(
                [*CORE_STAGE_A_DIFF, approved_content_entry],
                version=VERSION,
            )

        assert_fails(
            lambda: validate_stage_a_diff(
                [*CORE_STAGE_A_DIFF, README_PATH],
                version=VERSION,
            ),
            "carrier accepted an annotated root file by filename only",
        )
        assert_fails(
            lambda: validate_stage_a_diff(
                [
                    *CORE_STAGE_A_DIFF,
                    {
                        "filename": README_PATH,
                        "status": "modified",
                        "additions": 4,
                        "deletions": 4,
                        "changes": 8,
                    },
                ],
                version=VERSION,
            ),
            "carrier accepted a root file with missing patch metadata",
        )

        for mutation_name, mutation in (
            (
                "golden JSON wrong version",
                carrier_content_entry(
                    GOLDEN_JSON_PATH,
                    line_patch(
                        GOLDEN_JSON_PATH,
                        '{"tool":{"version":"0.1.0"}}',
                        '{"tool":{"version":"9.9.9"}}',
                    ),
                ),
            ),
            (
                "README wrong version",
                carrier_content_entry(
                    README_PATH,
                    line_patch(
                        README_PATH,
                        "CodeGauge `0.1.0` <!-- x-release-please-version -->",
                        "CodeGauge `9.9.9` <!-- x-release-please-version -->",
                    ),
                ),
            ),
            (
                "contracts wrong version",
                carrier_content_entry(
                    CONTRACTS_PATH,
                    line_patch(
                        CONTRACTS_PATH,
                        'version: "0.1.0".into(), // x-release-please-version',
                        'version: "9.9.9".into(), // x-release-please-version',
                    ),
                ),
            ),
            (
                "arbitrary generated-file content",
                carrier_content_entry(
                    GENERATED_CHANGELOG_PATH,
                    line_patch(
                        GENERATED_CHANGELOG_PATH,
                        "# Changelog",
                        "arbitrary generated content",
                    ),
                ),
            ),
            (
                "malformed annotated replacement",
                carrier_content_entry(
                    README_PATH,
                    line_patch(
                        README_PATH,
                        "CodeGauge `0.1.0` <!-- x-release-please-version -->",
                        "CodeGauge `0.2.0` <!-- x-release-please-version --> extra",
                    ),
                ),
            ),
            (
                "unexpected annotated replacement",
                carrier_content_entry(
                    README_PATH,
                    line_patch(
                        README_PATH,
                        "unrelated semver 0.1.0",
                        "unrelated semver 0.2.0 <!-- x-release-please-version -->",
                    ),
                ),
            ),
        ):
            assert_fails(
                lambda mutation=mutation: validate_stage_a_diff(
                    [*CORE_STAGE_A_DIFF, mutation],
                    version=VERSION,
                ),
                f"carrier accepted {mutation_name}",
            )

        validate_stage_a_diff(
            [*CORE_STAGE_A_DIFF, PRIVATE_CONFORMANCE_DIFF],
            version=VERSION,
        )
        for mutation_name, mutation in (
            (
                "private package version",
                private_conformance_entry(
                    patch=private_conformance_patch(
                        extra_changes='@@ -1,3 +1,3 @@\n-version = "0.1.0"\n+version = "0.2.0"'
                    ),
                    additions=5,
                    deletions=5,
                    changes=10,
                ),
            ),
            (
                "private publish flag",
                private_conformance_entry(
                    patch=private_conformance_patch(
                        extra_changes="@@ -7,1 +7,1 @@\n-publish = false\n+publish = true"
                    ),
                    additions=5,
                    deletions=5,
                    changes=10,
                ),
            ),
            (
                "private package name",
                private_conformance_entry(
                    patch=private_conformance_patch(
                        extra_changes='@@ -2,1 +2,1 @@\n-name = "codegauge-conformance"\n+name = "codegauge-public"'
                    ),
                    additions=5,
                    deletions=5,
                    changes=10,
                ),
            ),
            (
                "private dependency path",
                private_conformance_entry(
                    patch=private_conformance_patch().replace(
                        'path = "../codegauge-application"',
                        'path = "../unapproved"',
                    )
                ),
            ),
            (
                "private dependency key",
                private_conformance_entry(
                    patch=private_conformance_patch().replace(
                        "codegauge-model =",
                        "codegauge-unapproved =",
                    )
                ),
            ),
            (
                "private dependency feature",
                private_conformance_entry(
                    patch=private_conformance_patch().replace(
                        'path = "../codegauge-application"',
                        'path = "../codegauge-application", features = ["unapproved"]',
                    )
                ),
            ),
            (
                "private formatting/comment",
                private_conformance_entry(
                    patch=private_conformance_patch(
                        extra_changes="@@ -11,1 +11,2 @@\n [dependencies]\n+# unapproved formatting mutation"
                    ),
                    additions=5,
                    deletions=4,
                    changes=9,
                ),
            ),
            (
                "private truncated patch",
                private_conformance_entry(
                    patch=private_conformance_patch().replace(
                        '-codegauge-provider-jacoco = { version = "0.1.0", path = "../codegauge-provider-jacoco" }\n'
                        '+codegauge-provider-jacoco = { version = "0.2.0", path = "../codegauge-provider-jacoco" }\n',
                        "",
                    ),
                    additions=3,
                    deletions=3,
                    changes=6,
                ),
            ),
        ):
            assert_fails(
                lambda mutation=mutation: validate_stage_a_diff(
                    [*CORE_STAGE_A_DIFF[:3], mutation],
                    version=VERSION,
                ),
                f"carrier accepted {mutation_name} mutation",
            )

        assert_fails(
            lambda: validate_stage_a_diff(
                [
                    *CORE_STAGE_A_DIFF[:3],
                    {"filename": PRIVATE_CONFORMANCE_PATH, "status": "modified"},
                ],
                version=VERSION,
            ),
            "carrier accepted a private manifest without complete patch metadata",
        )
        for private_path in (
            "crates/codegauge-conformance/CHANGELOG.md",
            "crates/codegauge-conformance/README.md",
        ):
            assert_fails(
                lambda path=private_path: validate_stage_a_diff(
                    ["Cargo.toml", "Cargo.lock", ".release-please-manifest.json", path],
                    version=VERSION,
                ),
                f"carrier accepted unapproved private path {private_path}",
            )

        for changelog_path in DIFF:
            if isinstance(changelog_path, str) and changelog_path.endswith("/CHANGELOG.md"):
                validate_stage_a_diff(
                    [
                        "Cargo.toml",
                        "Cargo.lock",
                        ".release-please-manifest.json",
                        "npm/codegauge/package.json",
                        changelog_path,
                    ]
                )
        for unapproved_changelog in (
            "CHANGELOG.md",
            "npm/packages/codegauge-linux-x64-gnu/docs/CHANGELOG.md",
            "crates/codegauge-evil/CHANGELOG.md",
        ):
            assert_fails(
                lambda path=unapproved_changelog: validate_stage_a_diff(
                    ["Cargo.toml", "Cargo.lock", ".release-please-manifest.json", path]
                ),
                f"carrier accepted unapproved changelog path {unapproved_changelog}",
            )

        assert_fails(
            lambda: validate_carrier_event(
                event_name="push",
                ref="refs/heads/release",
                event_sha=SHA,
                pull_requests=[release_pr()],
                changed_files=DIFF,
                root=fixture,
            ),
            "carrier accepted a non-main push",
        )
        assert_fails(
            lambda: validate_carrier_event(
                event_name="push",
                ref="refs/heads/main",
                event_sha=OTHER_SHA,
                pull_requests=[release_pr()],
                changed_files=DIFF,
                root=fixture,
            ),
            "carrier accepted an unexpected merge commit",
        )
        assert_fails(
            lambda: validate_carrier_event(
                event_name="push",
                ref="refs/heads/main",
                event_sha=SHA,
                pull_requests=[release_pr(), release_pr(number=43)],
                changed_files=DIFF,
                root=fixture,
            ),
            "carrier accepted more than one merged Release Please PR",
        )

        graph_drift = fixture / "npm" / "packages" / "codegauge-darwin-x64" / "package.json"
        graph_drift.write_text(
            graph_drift.read_text(encoding="utf-8").replace(VERSION, "0.3.0"),
            encoding="utf-8",
        )
        assert_fails(
            lambda: validate_carrier_tree(fixture),
            "carrier accepted npm graph version drift",
        )
        graph_drift.write_text(
            graph_drift.read_text(encoding="utf-8").replace("0.3.0", VERSION),
            encoding="utf-8",
        )

        lockfile = fixture / "Cargo.lock"
        lockfile_contents = lockfile.read_text(encoding="utf-8")
        lockfile.unlink()
        assert_fails(
            lambda: validate_carrier_tree(fixture),
            "carrier accepted a missing Cargo.lock",
        )
        lockfile.write_text(lockfile_contents, encoding="utf-8")

        manifest = fixture / ".release-please-manifest.json"
        manifest.unlink()
        assert_fails(
            lambda: validate_carrier_tree(fixture),
            "carrier accepted missing release metadata",
        )
        manifest.write_text(
            json.dumps(
                {
                    ".": VERSION,
                    "crates/codegauge-model": VERSION,
                    "crates/codegauge-core": VERSION,
                    "crates/codegauge-application": VERSION,
                    "crates/codegauge-provider-jacoco": VERSION,
                    "crates/codegauge-cli": VERSION,
                    "npm/codegauge": VERSION,
                    "npm/packages/codegauge-linux-x64-gnu": VERSION,
                    "npm/packages/codegauge-linux-arm64-gnu": VERSION,
                    "npm/packages/codegauge-darwin-x64": VERSION,
                    "npm/packages/codegauge-darwin-arm64": VERSION,
                    "npm/packages/codegauge-win32-x64-msvc": VERSION,
                    "npm/packages/codegauge-win32-arm64-msvc": VERSION,
                }
            ),
            encoding="utf-8",
        )

        for carrier_path in ROOT_CARRIER_PATHS:
            path = fixture / carrier_path
            contents = path.read_bytes()
            path.unlink()
            assert_fails(
                lambda: validate_carrier_tree(fixture),
                f"carrier accepted a missing root-owned file: {carrier_path}",
            )
            path.write_bytes(contents)

        assert_fails(
            lambda: validate_carrier_event(
                event_name="push",
                ref="refs/heads/main",
                event_sha=SHA,
                pull_requests=[release_pr(merge_sha=OTHER_SHA)],
                changed_files=DIFF,
                root=fixture,
            ),
            "carrier accepted a PR whose merge commit differs from the event",
        )

        assert_fails(
            lambda: plan_carrier_tag("0.1.0", SHA),
            "carrier accepted the bootstrap version",
        )
        assert plan_carrier_tag(VERSION, SHA).action == "create"
        assert plan_carrier_tag(
            VERSION, SHA, existing_type="commit", existing_sha=SHA
        ).action == "noop"
        assert_fails(
            lambda: plan_carrier_tag(
                VERSION, SHA, existing_type="commit", existing_sha=OTHER_SHA
            ),
            "carrier accepted a conflicting tag",
        )
        assert_fails(
            lambda: plan_carrier_tag(
                VERSION, SHA, existing_type="tag", existing_sha=SHA
            ),
            "carrier accepted an annotated tag in the immutable slot",
        )
        assert_fails(
            lambda: validate_carrier_release_slot(existing_release=True),
            "carrier accepted an existing GitHub Release before tag creation",
        )

        for valid_version in (
            "0.0.0",
            "1.2.3",
            "1.2.3-alpha",
            "1.2.3-alpha.1",
            "1.2.3-0.3.7",
            "1.2.3+build.11.e0f985a",
            "1.2.3-alpha+build.11",
        ):
            assert VERSION_RE.fullmatch(valid_version), valid_version
        for invalid_version in (
            "01.2.3",
            "1.01.0",
            "1.2.03",
            "1.2.3-",
            "1.2.3-01",
            "1.2.3-alpha..1",
            "1.2.3+",
            "1.2.3+build..1",
            "1.2.3.4",
        ):
            assert not VERSION_RE.fullmatch(invalid_version), invalid_version
            assert_fails(
                lambda version=invalid_version: plan_carrier_tag(version, SHA),
                f"carrier accepted malformed semver {invalid_version}",
            )

        print("RELEASE CARRIER TESTS: PASS")
        return 0
    finally:
        import shutil

        shutil.rmtree(fixture.parent)


if __name__ == "__main__":
    raise SystemExit(main())
