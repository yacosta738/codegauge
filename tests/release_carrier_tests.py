#!/usr/bin/env python3
"""Deterministic R-F6 carrier regressions.

These tests exercise the pure carrier boundary with a copied release tree.  No
GitHub API, credential, tag, release, package, or registry write is permitted.
"""

from __future__ import annotations

import json
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
    plan_carrier_tag,
    validate_carrier_event,
    validate_carrier_release_slot,
    validate_carrier_tree,
    validate_stage_a_diff,
)


SHA = "a" * 40
OTHER_SHA = "b" * 40
VERSION = "0.2.0"

DIFF = [
    "Cargo.toml",
    "Cargo.lock",
    ".release-please-manifest.json",
    "README.md",
    "tests/golden/valid-methods.json",
    "crates/codegauge-model/tests/contracts.rs",
    "crates/codegauge-cli/tests/cli.rs",
    "crates/codegauge-model/Cargo.toml",
    "crates/codegauge-core/Cargo.toml",
    "crates/codegauge-application/Cargo.toml",
    "crates/codegauge-provider-jacoco/Cargo.toml",
    "crates/codegauge-cli/Cargo.toml",
    "npm/codegauge/package.json",
    "npm/packages/codegauge-linux-x64-gnu/package.json",
    "npm/packages/codegauge-linux-arm64-gnu/package.json",
    "npm/packages/codegauge-darwin-x64/package.json",
    "npm/packages/codegauge-darwin-arm64/package.json",
    "npm/packages/codegauge-win32-x64-msvc/package.json",
    "npm/packages/codegauge-win32-arm64-msvc/package.json",
    "crates/codegauge-model/CHANGELOG.md",
    "crates/codegauge-core/CHANGELOG.md",
    "crates/codegauge-application/CHANGELOG.md",
    "crates/codegauge-provider-jacoco/CHANGELOG.md",
    "crates/codegauge-cli/CHANGELOG.md",
    "npm/codegauge/CHANGELOG.md",
    "npm/packages/codegauge-linux-x64-gnu/CHANGELOG.md",
    "npm/packages/codegauge-linux-arm64-gnu/CHANGELOG.md",
    "npm/packages/codegauge-darwin-x64/CHANGELOG.md",
    "npm/packages/codegauge-darwin-arm64/CHANGELOG.md",
    "npm/packages/codegauge-win32-x64-msvc/CHANGELOG.md",
    "npm/packages/codegauge-win32-arm64-msvc/CHANGELOG.md",
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
        *fixture.glob("crates/*/Cargo.toml"),
        fixture / "npm" / "codegauge" / "package.json",
        *fixture.glob("npm/packages/*/package.json"),
    ]
    for path in versioned_files:
        path.write_text(
            path.read_text(encoding="utf-8").replace("0.1.0", VERSION),
            encoding="utf-8",
        )
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
            "crates/codegauge-conformance/Cargo.toml",
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

        for changelog_path in DIFF:
            if changelog_path.endswith("/CHANGELOG.md"):
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
