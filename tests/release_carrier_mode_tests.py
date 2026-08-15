#!/usr/bin/env python3
"""Executable regressions for the carrier mode and replay record boundary."""

from __future__ import annotations

import os
import subprocess
import tempfile
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release-tag-carrier.yml"
REPLAY_SHA = "fcc91b4850480945ae484c3ebdba18f8a4e38270"


def mode_script() -> str:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    step_start = workflow.index("      - name: Resolve carrier mode")
    run_start = workflow.index("        run: |\n", step_start) + len("        run: |\n")
    run_end = workflow.index("\n      - name: Collect the one merged Release Please PR", run_start)
    return textwrap.dedent(workflow[run_start:run_end]).lstrip()


def run_mode(
    *,
    event_name: str,
    dispatch_dry_run: str,
    repository_dry_run: str,
    replay_sha: str = "",
) -> tuple[subprocess.CompletedProcess[str], dict[str, str], str]:
    source_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="codegauge-carrier-mode-") as directory:
        output_path = Path(directory) / "github-output"
        summary_path = Path(directory) / "step-summary"
        environment = {
            "PATH": os.environ["PATH"],
            "HOME": os.environ.get("HOME", "/tmp"),
            "GITHUB_EVENT_NAME": event_name,
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_SHA": source_sha,
            "GITHUB_OUTPUT": str(output_path),
            "GITHUB_STEP_SUMMARY": str(summary_path),
            "DISPATCH_DRY_RUN": dispatch_dry_run,
            "REPOSITORY_DRY_RUN": repository_dry_run,
            "REPLAY_SHA": replay_sha,
        }
        result = subprocess.run(
            ["bash", "-c", mode_script()],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
        )
        outputs: dict[str, str] = {}
        if output_path.exists():
            for line in output_path.read_text(encoding="utf-8").splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    outputs[key] = value
        summary = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
        return result, outputs, summary


def assert_mode(
    *,
    event_name: str,
    dispatch_dry_run: str,
    repository_dry_run: str,
    expected_dry_run: str,
    expected_mode: str,
) -> None:
    result, outputs, summary = run_mode(
        event_name=event_name,
        dispatch_dry_run=dispatch_dry_run,
        repository_dry_run=repository_dry_run,
    )
    assert result.returncode == 0, result.stderr
    source_sha = outputs["source_checkout_sha"]
    assert outputs == {
        "dry_run": expected_dry_run,
        "mode": expected_mode,
        "event_sha": source_sha,
        "replay": "false",
        "source_checkout_sha": source_sha,
    }
    assert "- replay: false" in summary
    assert f"- source checkout SHA: {source_sha}" in summary
    assert "- replay event SHA: none" in summary


def test_normal_push_defaults_to_live_without_replay() -> None:
    assert_mode(
        event_name="push",
        dispatch_dry_run="",
        repository_dry_run="",
        expected_dry_run="false",
        expected_mode="live",
    )


def test_normal_manual_dry_run_proceeds_without_replay() -> None:
    assert_mode(
        event_name="workflow_dispatch",
        dispatch_dry_run="true",
        repository_dry_run="true",
        expected_dry_run="true",
        expected_mode="dry-run",
    )


def test_normal_manual_live_proceeds_without_replay() -> None:
    assert_mode(
        event_name="workflow_dispatch",
        dispatch_dry_run="false",
        repository_dry_run="true",
        expected_dry_run="false",
        expected_mode="live",
    )


def test_replay_is_manual_dry_run_only() -> None:
    result, outputs, summary = run_mode(
        event_name="workflow_dispatch",
        dispatch_dry_run="true",
        repository_dry_run="",
        replay_sha=REPLAY_SHA,
    )
    assert result.returncode == 0, result.stderr
    assert outputs["replay"] == "true"
    assert outputs["event_sha"] == REPLAY_SHA
    assert outputs["source_checkout_sha"] != REPLAY_SHA
    assert f"- replay event SHA: {REPLAY_SHA}" in summary

    for event_name, dispatch_dry_run, replay_sha in (
        ("push", "", REPLAY_SHA),
        ("workflow_dispatch", "false", REPLAY_SHA),
        ("workflow_dispatch", "true", "not-a-sha"),
    ):
        result, _, _ = run_mode(
            event_name=event_name,
            dispatch_dry_run=dispatch_dry_run,
            repository_dry_run="",
            replay_sha=replay_sha,
        )
        assert result.returncode != 0


def test_replay_schema_is_total_and_boolean_checked() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "jq -er '.replay'" not in workflow
    assert "(.replay // false)" in workflow
    assert '($replay | type) == "boolean"' in workflow
    assert 'replay: ($replay_mode == "true")' in workflow
    assert (
        'replay_event_sha: (if $replay_mode == "true" then $event_sha else null end)'
        in workflow
    )


def main() -> int:
    test_normal_push_defaults_to_live_without_replay()
    test_normal_manual_dry_run_proceeds_without_replay()
    test_normal_manual_live_proceeds_without_replay()
    test_replay_is_manual_dry_run_only()
    test_replay_schema_is_total_and_boolean_checked()
    print("RELEASE CARRIER MODE TESTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
