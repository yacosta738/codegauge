#!/usr/bin/env python3
"""Negative OCI verifier and publication failure-stop checks."""

from __future__ import annotations

from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BUILD_WORKFLOW = ROOT / ".github" / "workflows" / "release-build.yml"
PUBLISH_WORKFLOW = ROOT / ".github" / "workflows" / "release-publish.yml"
OCI_BUILD_SCRIPT = ROOT / "scripts" / "build_oci_release.sh"

if __package__:
    from .oci_distribution_evidence_tests import (
        _run_verifier,
        _write_synthetic_docker_archive,
        _write_synthetic_oci,
    )
else:
    from oci_distribution_evidence_tests import (
        _run_verifier,
        _write_synthetic_docker_archive,
        _write_synthetic_oci,
    )


def test_workflow_stops_before_publication_when_an_architecture_fails() -> None:
    build_workflow = BUILD_WORKFLOW.read_text(encoding="utf-8")
    publish_workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")
    build_step = OCI_BUILD_SCRIPT.read_text(encoding="utf-8")
    build_loop_end = build_step.index("\ndone\n")

    assert "set -euo pipefail" in build_step[:build_loop_end]
    assert "continue-on-error" not in build_step[:build_loop_end]
    assert "|| true" not in build_step[:build_loop_end]
    assert "exit 0" not in build_step[:build_loop_end]
    assert build_step[:build_loop_end].count("for architecture in amd64 arm64") == 1
    assert "docker/login-action" not in build_step
    assert "docker/login-action" not in build_workflow
    assert "needs: publish-npm" in publish_workflow
    assert "needs: [release-preflight, release-verify]" in build_workflow


def test_verifier_rejects_docker_id_drift() -> None:
    with tempfile.TemporaryDirectory(prefix="codegauge-oci-docker-id-negative-") as directory:
        root = Path(directory)
        archive, _, inspect, index_digest = _write_synthetic_oci(root)
        docker_archive, docker_config_digest, docker_platform_digest = _write_synthetic_docker_archive(
            root,
            labels=inspect["Config"]["Labels"],
        )
        oci_config_digest = inspect["Id"]
        assert isinstance(oci_config_digest, str)
        assert oci_config_digest not in {docker_config_digest, docker_platform_digest}
        inspect["Id"] = oci_config_digest

        result = _run_verifier(
            root,
            archive,
            index_digest,
            inspect,
            docker_archive=docker_archive,
        )

        assert result.returncode != 0
        output = result.stderr + result.stdout
        assert docker_platform_digest in output
        assert "Docker archive identity" in output


def test_verifier_rejects_runtime_or_metadata_mismatch() -> None:
    with tempfile.TemporaryDirectory(prefix="codegauge-oci-evidence-negative-") as directory:
        root = Path(directory)
        archive, _, inspect, index_digest = _write_synthetic_oci(root)
        result = _run_verifier(
            root,
            archive,
            index_digest,
            inspect,
            version_output="codegauge 9.9.9\n",
        )
        assert result.returncode != 0
        assert "version" in (result.stderr + result.stdout).lower()


def test_verifier_requires_emulation_evidence_for_qemu() -> None:
    with tempfile.TemporaryDirectory(prefix="codegauge-oci-qemu-negative-") as directory:
        root = Path(directory)
        archive, _, inspect, index_digest = _write_synthetic_oci(root, architecture="arm64")
        result = _run_verifier(
            root,
            archive,
            index_digest,
            inspect,
            architecture="arm64",
            runtime_mode="qemu",
        )
        assert result.returncode != 0
        assert "emulation" in (result.stderr + result.stdout).lower()


def test_verifier_rejects_root_runtime() -> None:
    with tempfile.TemporaryDirectory(prefix="codegauge-oci-root-negative-") as directory:
        root = Path(directory)
        archive, _, inspect, index_digest = _write_synthetic_oci(root, user="0")
        result = _run_verifier(root, archive, index_digest, inspect, non_root="0\n")
        assert result.returncode != 0
        assert "root" in (result.stderr + result.stdout).lower()


def test_verifier_rejects_metadata_digest_drift() -> None:
    with tempfile.TemporaryDirectory(prefix="codegauge-oci-digest-negative-") as directory:
        root = Path(directory)
        archive, _, inspect, _ = _write_synthetic_oci(root)
        result = _run_verifier(root, archive, "sha256:" + "b" * 64, inspect)
        assert result.returncode != 0
        assert "digest" in (result.stderr + result.stdout).lower()


def test_verifier_rejects_label_drift() -> None:
    with tempfile.TemporaryDirectory(prefix="codegauge-oci-label-negative-") as directory:
        root = Path(directory)
        archive, _, inspect, index_digest = _write_synthetic_oci(root)
        config = inspect["Config"]
        assert isinstance(config, dict)
        labels = config["Labels"]
        assert isinstance(labels, dict)
        labels["org.opencontainers.image.revision"] = "b" * 40
        result = _run_verifier(root, archive, index_digest, inspect)
        assert result.returncode != 0
        assert "label" in (result.stderr + result.stdout).lower()


def run_tests() -> None:
    test_workflow_stops_before_publication_when_an_architecture_fails()
    test_verifier_rejects_docker_id_drift()
    test_verifier_rejects_runtime_or_metadata_mismatch()
    test_verifier_requires_emulation_evidence_for_qemu()
    test_verifier_rejects_root_runtime()
    test_verifier_rejects_metadata_digest_drift()
    test_verifier_rejects_label_drift()


if __name__ == "__main__":
    run_tests()
    print("OCI DISTRIBUTION FAILURE TESTS: PASS")
