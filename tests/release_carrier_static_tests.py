#!/usr/bin/env python3
"""Static R-F6 workflow and security checks used by the local distribution runner."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
SHA_REF = re.compile(r"uses:\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([0-9a-f]{40})(?:\s|$)")
EXTERNAL_USE = re.compile(r"uses:\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([^\s#]+)")


def run_checks() -> list[str]:
    errors: list[str] = []
    release_please = (WORKFLOW_DIR / "release-please.yml").read_text(encoding="utf-8")
    release_config = (ROOT / "release-please-config.json").read_text(encoding="utf-8")
    carrier = (WORKFLOW_DIR / "release-tag-carrier.yml").read_text(encoding="utf-8")
    tag_workflow = (WORKFLOW_DIR / "release-on-tag.yml").read_text(encoding="utf-8")
    release = (WORKFLOW_DIR / "release.yml").read_text(encoding="utf-8")
    build = (WORKFLOW_DIR / "release-build.yml").read_text(encoding="utf-8")
    publish = (WORKFLOW_DIR / "release-publish.yml").read_text(encoding="utf-8")
    recovery = (WORKFLOW_DIR / "release-recovery.yml").read_text(encoding="utf-8")

    for path in WORKFLOW_DIR.glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        for match in EXTERNAL_USE.finditer(text):
            if not SHA_REF.fullmatch(match.group(0).rstrip()):
                errors.append(f"{path.name} has an unpinned action: {match.group(0)}")

    if "branches: [main]" not in release_please or "skip-github-release: true" in release_please:
        errors.append("Release Please must run on main and own the canonical GitHub Release")
    if "contents: write" not in release_please:
        errors.append("Release Please must have contents: write for canonical tag/release ownership")
    if "name: Historical Release Recovery" not in recovery:
        errors.append("historical recovery workflow must be explicit and separately invoked")
    if "workflow_dispatch:" not in recovery or "--execute-live" not in recovery:
        errors.append("historical recovery must expose explicit dry-run and live paths")
    if "RECOVER_RELEASE_LIVE" not in recovery:
        errors.append("historical recovery must require the live authorization confirmation")
    if "--plan-only" not in recovery or '--confirm-live "$CONFIRM_LIVE"' not in recovery:
        errors.append("historical recovery must plan live requests before explicit execution")
    live_step = recovery[recovery.index("- name: Reconcile canonical tag then GitHub Release") :]
    if "grep -F 'NO_WRITES: True' recovery-live-audit.txt" in live_step:
        errors.append("live recovery must audit reconciled/no-op outcomes instead of NO_WRITES")
    if "contents: ${{ inputs.execute_live" in recovery:
        errors.append("recovery permissions must be statically declared per job")
    if "name: Validate live authorization" not in recovery:
        errors.append("recovery must fail closed when live confirmation is missing")
    if "contents: write" in recovery.split("jobs:", 1)[0]:
        errors.append("historical recovery must not grant write permissions at workflow scope")
    if '"include-component-in-tag": true' not in release_config:
        errors.append("Stage A must enable component-tagged linked version lookup")
    if "secrets.RELEASE_PLEASE_TOKEN ||" in release_please or "github.token" in release_please:
        errors.append("Stage A must not fall back to GITHUB_TOKEN")
    if "uses: ./.github/workflows/release.yml" in release_please:
        errors.append("Stage A must not call the publication workflow")
    if any(
        marker in release_please
        for marker in ("gh release", "npm publish", "cargo publish", "release_created")
    ):
        errors.append("Stage A contains a publication or release-output side effect")

    # Release Please is the sole canonical tag/release owner.
    carrier_mutation_markers = (
        '--method POST',
        'refs/tags/',
        'git tag',
        'git push',
        'gh release create',
        'gh release edit',
        'gh release delete',
        'gh release upload',
        'autorelease: tagged',
        '--method PUT',
        '--method DELETE',
        'GITHUB_TOKEN',
    )
    for marker in carrier_mutation_markers:
        if marker in carrier:
            errors.append(f"carrier must remain read-only and never mutate releases: {marker}")

    for marker in (
        'gh release create',
        'gh release edit',
        'gh release delete',
        'github.token',
    ):
        if marker in publish:
            errors.append(f"release-publish must not use release mutation or fallback credentials: {marker}")
    for marker in ('gh release view', 'gh release upload', '${GITHUB_REPOSITORY}', 'secrets.RELEASE_PLEASE_TOKEN'):
        if marker not in publish:
            errors.append(f"release-publish must verify/upload with explicit scope and token: {marker}")

    if "push:" not in carrier or "branches: [main]" not in carrier:
        errors.append("carrier must be restricted to trusted main pushes")
    if "workflow_dispatch:" not in carrier or "dry_run:" not in carrier or "type: boolean" not in carrier:
        errors.append("carrier must expose an explicit manual dry-run input")
    if "replay_sha:" not in carrier or "type: string" not in carrier:
        errors.append("carrier must expose an optional replay_sha string input")
    if "REPLAY_SHA: ${{ inputs.replay_sha }}" not in carrier:
        errors.append("carrier must pass the optional replay_sha input to the resolver")
    if "carrier-event-sha" not in carrier:
        errors.append("carrier must resolve an explicit effective event SHA")
    if "EVENT_SHA: ${{ steps.mode.outputs.event_sha }}" not in carrier:
        errors.append("carrier must propagate the normalized EVENT_SHA output")
    if "SOURCE_CHECKOUT_SHA: ${{ steps.mode.outputs.source_checkout_sha }}" not in carrier:
        errors.append("carrier must record the current source checkout SHA")
    checkout_start = carrier.index("- uses: actions/checkout")
    checkout_end = carrier.index("- name: Resolve carrier mode", checkout_start)
    checkout_block = carrier[checkout_start:checkout_end]
    if "ref: ${{ github.sha }}" not in checkout_block:
        errors.append("carrier checkout must remain bound to the current selected event revision")
    if "replay_sha" in checkout_block:
        errors.append("carrier checkout must not use replay_sha as its source revision")
    if "vars.RELEASE_CARRIER_DRY_RUN" not in carrier:
        errors.append("carrier must read the temporary RELEASE_CARRIER_DRY_RUN repository variable")
    if "DISPATCH_DRY_RUN" not in carrier or "REPOSITORY_DRY_RUN" not in carrier:
        errors.append("carrier must normalize dispatch and repository-variable dry-run inputs")
    if "id: collect" not in carrier:
        errors.append("carrier must expose collection status to gate later validation/mutation steps")
    if "carrier-pr-selection" not in carrier:
        errors.append("carrier must classify matching Release Please PRs before fetching the diff")
    if 'status=skipped' not in carrier or "no-matching-release-please-pr" not in carrier:
        errors.append("carrier must record a successful no-matching-release skip")
    if 'test "$release_pr_count" -eq 1' in carrier:
        errors.append("carrier must not fail ordinary main pushes with a single-count assertion")
    if "steps.collect.outputs.status == 'matched'" not in carrier:
        errors.append("read-only carrier validation must require one matching Release Please PR")
    collection_marker = "carrier-pr-selection"
    files_marker = 'pulls/${release_pr_number}/files'
    if collection_marker in carrier and files_marker in carrier:
        if carrier.index(collection_marker) > carrier.index(files_marker):
            errors.append("carrier must classify the event before fetching Release Please diff files")
    if "map({filename: .filename, status: .status, additions: .additions, deletions: .deletions, changes: .changes, patch: .patch})" not in carrier:
        errors.append("carrier must retain complete PR file patch metadata for private diff validation")
    if "canonical_tag_ref" not in carrier or "not-started" not in carrier:
        errors.append("no-match records must explicitly prove tag/publication paths did not start")
    if "carrier_validation:" not in carrier or "not-run" not in carrier:
        errors.append("no-match records must prove carrier validation was not run")
    if "skipped)" in carrier:
        skip_branch = carrier[carrier.index("skipped)") : carrier.index(";;", carrier.index("skipped)"))]
        if "exit 0" not in skip_branch or files_marker in skip_branch:
            errors.append("no-match selection must exit successfully before fetching PR files")
    if 'if [[ "$GITHUB_EVENT_NAME" == "workflow_dispatch" ]]' not in carrier:
        errors.append("carrier must branch explicitly for trusted workflow_dispatch events")
    if 'test "$GITHUB_EVENT_NAME" = "push" || test "$GITHUB_EVENT_NAME" = "workflow_dispatch"' not in carrier:
        errors.append("carrier event collection must accept only push or workflow_dispatch")
    if 'case "${DISPATCH_DRY_RUN:-}"' not in carrier or 'case "${REPOSITORY_DRY_RUN:-}"' not in carrier:
        errors.append("carrier dry-run normalization must fail closed on unknown values")
    if '""|false)' not in carrier or 'dry_run=false' not in carrier:
        errors.append("carrier must default to live mode when the repository variable is absent or false")
    if "printf 'dry_run=%s\\n' \"$dry_run\"" not in carrier:
        errors.append("carrier must expose the normalized dry-run mode to later steps")
    if "printf 'event_sha=%s\\n' \"$event_sha\"" not in carrier:
        errors.append("carrier must expose the normalized event SHA to later steps")
    if "printf 'replay=%s\\n' \"$replay_mode\"" not in carrier:
        errors.append("carrier must expose the replay mode to later steps")
    if "source_checkout_sha" not in carrier or "replay_event_sha" not in carrier:
        errors.append("carrier records must identify source and replay event revisions")
    if "release-carrier-main" not in carrier or "cancel-in-progress: false" not in carrier:
        errors.append("carrier concurrency must be non-canceling and stable")
    if "permissions:\n  contents: read" not in carrier:
        errors.append("carrier must default to read-only GITHUB_TOKEN permissions")
    if "${GITHUB_REPOSITORY}" not in carrier:
        errors.append("carrier must use explicit repository scope for read-only API calls")
    if "gh api" not in carrier:
        errors.append("carrier must retain read-only GitHub API correlation")
    if "refs/heads/main" not in carrier or "GITHUB_SHA" not in carrier or "git rev-parse HEAD" not in carrier:
        errors.append("carrier must bind validation to the main event SHA")
    for required_event_use in (
        'commits/${EVENT_SHA}/pulls',
        '--event-sha "$EVENT_SHA"',
    ):
        if required_event_use not in carrier:
            errors.append(f"carrier must use normalized EVENT_SHA for {required_event_use}")
    if 'commits/${GITHUB_SHA}/pulls' in carrier or '--event-sha "$GITHUB_SHA"' in carrier:
        errors.append("carrier must not fall back to GITHUB_SHA after event normalization")
    if "GITHUB_STEP_SUMMARY" not in carrier or "mutations" not in carrier:
        errors.append("carrier dry-run must emit an auditable validation record")
    if 'validation: {' not in carrier or 'stage_a_diff: "passed"' not in carrier:
        errors.append("carrier plan must record the validated tree/diff/provenance boundaries")
    if "printf 'tag=%s\\n' \"$(jq -er '.tag' carrier-record.json)\" >> \"$GITHUB_OUTPUT\"" not in carrier:
        errors.append("carrier must write a valid named tag output")

    if '--replay-sha "${REPLAY_SHA:-}"' not in carrier or '--dry-run "$dry_run"' not in carrier:
        errors.append("carrier must fail closed when replay_sha is outside manual dry-run")
    if "release-on-tag.yml" in carrier or "gh workflow run" in carrier:
        errors.append("dry-run carrier must never dispatch the tag workflow directly")
    if any(
        marker in carrier
        for marker in (
            "actions/upload-artifact",
            "gh release upload",
            "cargo publish",
            "npm publish",
            "docker push",
        )
    ):
        errors.append("carrier must not upload or publish release artifacts")

    if 'tags: ["v*.*.*"]' not in tag_workflow:
        errors.append("tag caller must listen only for canonical vX.Y.Z tags")
    if "github.ref_name" not in tag_workflow or "github.sha" not in tag_workflow:
        errors.append("tag caller must pass the triggering tag and commit SHA")
    if "recovery" not in tag_workflow or "workflow_dispatch:" not in tag_workflow:
        errors.append("manual dispatch must be explicit recovery-only plumbing")
    if "uses: ./.github/workflows/release.yml" not in tag_workflow:
        errors.append("tag caller must invoke the existing reusable release workflow")

    if "release_url" not in release or "workflow_call:" not in release:
        errors.append("reusable release workflow inputs are incomplete")
    if "git merge-base --is-ancestor" not in build:
        errors.append("release preflight must validate main ancestry instead of moving main equality")
    if "gh release create" in publish or "gh release view" not in publish:
        errors.append("post-gate publisher must verify the existing canonical release")
    if "gh release create" in build or "gh release create" in carrier:
        errors.append("release creation must remain outside Stage A and the tag carrier")

    return errors


if __name__ == "__main__":
    failures = run_checks()
    if failures:
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print("RELEASE CARRIER STATIC TESTS: PASS")
