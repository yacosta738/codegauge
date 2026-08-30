#!/usr/bin/env python3
"""Focused contracts for rollback handling and live recovery hardening."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_rollback_runbook_documents_disable_preserve_stop_inventory_and_deprecation() -> None:
    runbook = (ROOT / "docs" / "release-recovery-runbook.md").read_text(encoding="utf-8")
    required_sections = (
        "Disable live recovery",
        "Never delete or force-move",
        "Stop later publication stages",
        "Inventory immutable outputs",
        "Target deprecation and rollback",
    )
    for section in required_sections:
        assert section in runbook
    assert "new identity" in runbook


def test_recovery_workflow_has_disabled_by_default_live_gate_and_protected_environment() -> None:
    recovery = (WORKFLOWS / "release-recovery.yml").read_text(encoding="utf-8")

    assert "RELEASE_RECOVERY_LIVE_ENABLED" in recovery
    assert "test \"$LIVE_ENABLED\" = \"true\"" in recovery
    assert "environment:" in recovery
    assert "name: release-recovery-live" in recovery
    assert "inputs.request" not in recovery.split("concurrency:", 1)[1].split("jobs:", 1)[0]
    concurrency = recovery.split("concurrency:", 1)[1].split("jobs:", 1)[0]
    assert "inputs.release_tag" in concurrency
    assert "inputs.merged_sha" in concurrency
    assert "cancel-in-progress: false" in concurrency


def test_publication_failure_inventory_is_audit_only_and_keeps_dependency_stop_chain() -> None:
    publish = (WORKFLOWS / "release-publish.yml").read_text(encoding="utf-8")

    assert "publication-failure-inventory:" in publish
    assert "if: ${{ always()" in publish
    assert "No rollback, deletion, or force-move" in publish
    assert "docs/release-recovery-runbook.md" in publish
    inventory = publish.split("  publication-failure-inventory:", 1)[1]
    assert "actions/upload-artifact@" in inventory
    assert re.search(r"needs: \[[^\]]*publish-npm[^\]]*publish-oci[^\]]*\]", inventory)


def test_publication_failure_inventory_declares_schema_and_every_immutable_target() -> None:
    publish = (WORKFLOWS / "release-publish.yml").read_text(encoding="utf-8")
    inventory = publish.split("  publication-failure-inventory:", 1)[1]

    for field in (
        "canonical_version",
        "canonical_reference",
        "source_sha",
        "published_digest_or_package_version",
        "job_result",
        "evidence_location",
    ):
        assert field in inventory
    assert "publication-failure-inventory/v1" in inventory
    assert "UNKNOWN" in inventory
    assert "never republishes" in inventory

    expected_targets = (
        "codegauge-model",
        "codegauge-core",
        "codegauge-application",
        "codegauge-provider-jacoco",
        "codegauge-provider-typescript",
        "codegauge-cli",
        "@yacosta738/codegauge",
        "@yacosta738/codegauge-linux-x64-gnu",
        "@yacosta738/codegauge-linux-arm64-gnu",
        "@yacosta738/codegauge-darwin-x64",
        "@yacosta738/codegauge-darwin-arm64",
        "@yacosta738/codegauge-win32-x64-msvc",
        "@yacosta738/codegauge-win32-arm64-msvc",
        "codegauge-0.3.0-x86_64-unknown-linux-gnu.tar.gz",
        "codegauge-0.3.0-aarch64-unknown-linux-gnu.tar.gz",
        "codegauge-0.3.0-x86_64-unknown-linux-musl.tar.gz",
        "codegauge-0.3.0-aarch64-unknown-linux-musl.tar.gz",
        "codegauge-0.3.0-x86_64-apple-darwin.tar.gz",
        "codegauge-0.3.0-aarch64-apple-darwin.tar.gz",
        "codegauge-0.3.0-x86_64-pc-windows-msvc.zip",
        "codegauge-0.3.0-aarch64-pc-windows-msvc.zip",
        "ghcr.io/yacosta738/codegauge:0.3.0-amd64",
        "ghcr.io/yacosta738/codegauge:0.3.0-arm64",
        "ghcr.io/yacosta738/codegauge:0.3.0",
        "attestation: ghcr.io/yacosta738/codegauge@UNKNOWN",
    )
    for target in expected_targets:
        assert target in inventory


def test_read_only_carrier_uses_default_read_token_not_recovery_secret() -> None:
    carrier = (WORKFLOWS / "release-tag-carrier.yml").read_text(encoding="utf-8")
    assert "GH_TOKEN: ${{ github.token }}" in carrier
    assert "GH_TOKEN: ${{ secrets.RELEASE_PLEASE_TOKEN }}" not in carrier


def test_recovery_workflow_actions_are_pinned_and_dry_run_has_no_write_secret() -> None:
    recovery = (WORKFLOWS / "release-recovery.yml").read_text(encoding="utf-8")
    action_refs = re.findall(r"uses:\s+[^\s]+@([^\s#]+)", recovery)
    assert action_refs
    assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs)
    dry_run_section = recovery.split("- name: Validate request and produce no-write plan", 1)[1]
    dry_run_section = dry_run_section.split("- name: Upload planning audit", 1)[0]
    assert "RELEASE_PLEASE_TOKEN" not in dry_run_section
