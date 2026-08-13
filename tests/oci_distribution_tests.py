#!/usr/bin/env python3
"""Focused local checks for the OCI publication boundary.

The workflow checks are intentionally static so they run without a Docker daemon.
The evidence test exercises the verifier against a synthetic OCI layout and never
contacts a registry.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_WORKFLOW = ROOT / ".github" / "workflows" / "release-build.yml"
PUBLISH_WORKFLOW = ROOT / ".github" / "workflows" / "release-publish.yml"
OCI_BUILD_SCRIPT = ROOT / "scripts" / "build_oci_release.sh"
VERIFY_SCRIPT = ROOT / "scripts" / "verify_oci_evidence.py"
VERSION = "0.1.0"
REVISION = "a" * 40


def job_block(workflow: str, job_name: str) -> str:
    import re

    match = re.search(
        rf"^  {job_name}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing {job_name} job"
    return match.group("body")


def test_workflow_builds_locally_before_publication() -> None:
    build_workflow = BUILD_WORKFLOW.read_text(encoding="utf-8")
    publish_workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")
    script = OCI_BUILD_SCRIPT.read_text(encoding="utf-8")
    build_job = job_block(build_workflow, "oci-preflight")
    publish_job = job_block(publish_workflow, "publish-oci")

    build_start = script.index("docker buildx build")
    inspect_start = next(
        script.index(fragment)
        for fragment in ("docker image inspect", "docker buildx imagetools inspect")
        if fragment in script
    )
    build_block = script[build_start:inspect_start]
    assert "--output=type=oci,dest=" in build_block
    assert "--push" not in build_block
    assert "--tag \"$STAGING_IMAGE\"" in build_block

    smoke_start = script.index(" version", inspect_start)
    evidence_start = script.index("scripts/verify_oci_evidence.py", smoke_start)
    login_start = publish_job.index("docker/login-action")
    push_start = publish_job.index("docker push", login_start)
    manifest_start = publish_job.index("docker buildx imagetools create", push_start)

    assert "docker load --input" in script
    assert build_start < inspect_start < smoke_start < evidence_start
    assert login_start < push_start < manifest_start
    assert "bash scripts/build_oci_release.sh" in build_job
    assert "needs: [release-preflight, release-verify]" in build_job
    assert "if: inputs.dry_run == false" in build_job
    assert "needs: publish-npm" in publish_job
    assert "name: Download verified OCI build artifacts" in publish_job
    assert "docker load --input" in publish_job

    assert "docker image inspect --platform" in script
    assert "--oci-archive" in script[evidence_start:]
    assert '--docker-archive "$DOCKER_ARCHIVE"' in script[evidence_start:]
    assert "--inspect-json" in script[evidence_start:]
    assert "--version-output" in script[evidence_start:]
    assert "--profiles-output" in script[evidence_start:]
    assert "--contract-output" in script[evidence_start:]
    assert "--non-root-output" in script[evidence_start:]
    assert "--output" in script[evidence_start:]
    assert "org.opencontainers.image.platform" in script
    assert "org.opencontainers.image.version" in script
    assert "org.opencontainers.image.revision" in script
    assert "org.opencontainers.image.source" in script


def test_workflow_asserts_runtime_contract_and_emulation_evidence() -> None:
    workflow = OCI_BUILD_SCRIPT.read_text(encoding="utf-8")
    job = job_block(BUILD_WORKFLOW.read_text(encoding="utf-8"), "oci-preflight")

    assert "docker/setup-qemu-action@" in job
    assert 'runtime_mode="qemu"' in workflow
    assert 'runtime_mode="native"' in workflow
    assert "--runtime-mode \"$runtime_mode\"" in workflow
    assert 'docker run --rm --platform "linux/${architecture}"' in workflow
    assert "--entrypoint /bin/sh" in workflow
    assert 'id -u' in workflow
    assert " version" in workflow
    assert " profiles" in workflow
    assert "analyze --profile java-jacoco-v1" in workflow
    assert "--input /tmp/contract.xml" in workflow
    assert "--format json" in workflow
    assert "contract-result" not in workflow


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


def test_workflow_persists_evidence_and_publishes_only_verified_digests() -> None:
    build_workflow = BUILD_WORKFLOW.read_text(encoding="utf-8")
    workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")
    job = job_block(workflow, "publish-oci")

    assert "mkdir -p oci-evidence" in OCI_BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "oci-evidence/${architecture}.json" in OCI_BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "name: OCI architecture evidence" in build_workflow
    assert "name: Download verified OCI build artifacts" in job
    evidence_step = job[job.index("name: OCI architecture evidence") :]
    assert "if: always()" in evidence_step
    assert "actions/upload-artifact@" in evidence_step
    assert "path: oci-evidence/" in evidence_step

    publish_start = job.index("name: Publish final verified OCI digests")
    publish_end = job.index("name: OCI architecture evidence", publish_start)
    publish = job[publish_start:publish_end]
    assert 'docker tag "$STAGING_IMAGE" "$FINAL_TAG"' in publish
    assert "published_digest" in publish
    assert "docker buildx imagetools inspect --raw" in publish
    assert "published_config_digest" in publish
    assert "oci_config_digest" in publish
    assert '"$IMAGE@${amd64_digest}"' in publish
    assert '"$IMAGE@${arm64_digest}"' in publish
    assert 'docker buildx imagetools inspect --raw "$IMAGE:${RELEASE_VERSION}"' in publish
    assert "published_config_digest" in publish
    assert "jq -e" in publish
    assert '"$IMAGE:latest"' in publish
    assert 'printf \'manifest_digest=%s\\n\' "$FINAL_DIGEST" >> "$GITHUB_OUTPUT"' in publish
    assert "subject-digest: ${{ steps.publish-manifest.outputs.manifest_digest }}" in job
    assert "actions/attest@" in job
    assert "push-to-registry: true" in job

    # The upload step may run after a failed architecture, but publication must
    # remain success-gated rather than using an unconditional always() condition.
    assert "if: always()" not in publish
    assert "set -euo pipefail" in publish


def _blob(value: bytes) -> tuple[str, bytes]:
    digest = hashlib.sha256(value).hexdigest()
    return f"sha256:{digest}", value


def _write_synthetic_oci(
    root: Path,
    *,
    architecture: str = "amd64",
    version: str = VERSION,
    revision: str = REVISION,
    user: str = "codegauge",
) -> tuple[Path, str, dict[str, object], str]:
    platform = f"linux/{architecture}"
    labels = {
        "org.opencontainers.image.version": version,
        "org.opencontainers.image.revision": revision,
        "org.opencontainers.image.source": "https://github.com/yacosta738/codegauge",
        "org.opencontainers.image.platform": platform,
    }
    config = {
        "architecture": architecture,
        "os": "linux",
        "config": {"User": user, "Labels": labels},
        "rootfs": {"type": "layers", "diff_ids": []},
    }
    config_digest, config_bytes = _blob(json.dumps(config, separators=(",", ":")).encode())
    manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "digest": config_digest,
            "size": len(config_bytes),
        },
        "layers": [],
    }
    manifest_digest, manifest_bytes = _blob(json.dumps(manifest, separators=(",", ":")).encode())
    index = {
        "schemaVersion": 2,
        "manifests": [
            {
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "digest": manifest_digest,
                "size": len(manifest_bytes),
                "platform": {"os": "linux", "architecture": architecture},
            }
        ],
    }
    archive = root / f"{architecture}.tar"
    with tarfile.open(archive, "w") as output:
        files = {
            "oci-layout": b'{"imageLayoutVersion":"1.0.0"}\n',
            "index.json": json.dumps(index, separators=(",", ":")).encode(),
            f"blobs/sha256/{manifest_digest.removeprefix('sha256:')}": manifest_bytes,
            f"blobs/sha256/{config_digest.removeprefix('sha256:')}": config_bytes,
        }
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            output.addfile(info, io.BytesIO(content))
    inspect = {
        "Id": config_digest,
        "Os": "linux",
        "Architecture": architecture,
        "Config": {"User": user, "Labels": labels},
    }
    index_digest = _blob(json.dumps(index, separators=(",", ":")).encode())[0]
    return archive, manifest_digest, inspect, index_digest


def _write_synthetic_docker_archive(
    root: Path,
    *,
    architecture: str = "amd64",
    user: str = "codegauge",
    labels: dict[str, str] | None = None,
) -> tuple[Path, str, str]:
    """Create a Docker archive with config and platform-manifest digest domains."""
    docker_config = {
        "architecture": architecture,
        "os": "linux",
        "config": {"User": user, "Labels": labels or {}},
        "rootfs": {"type": "layers", "diff_ids": []},
        "docker_archive_only": True,
    }
    docker_config_digest, docker_config_bytes = _blob(
        json.dumps(docker_config, separators=(",", ":")).encode()
    )
    config_name = f"blobs/sha256/{docker_config_digest.removeprefix('sha256:')}"
    platform_manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "digest": docker_config_digest,
            "size": len(docker_config_bytes),
        },
        "layers": [],
    }
    docker_platform_digest, platform_manifest_bytes = _blob(
        json.dumps(platform_manifest, separators=(",", ":")).encode()
    )
    index = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.index.v1+json",
        "manifests": [
            {
                "mediaType": "application/vnd.oci.image.manifest.v1+json",
                "digest": docker_platform_digest,
                "size": len(platform_manifest_bytes),
                "platform": {"os": "linux", "architecture": architecture},
            }
        ],
    }
    manifest = [
        {
            "Config": config_name,
            "RepoTags": ["codegauge:test"],
            "Layers": [],
        }
    ]
    archive = root / f"{architecture}.docker.tar"
    with tarfile.open(archive, "w") as output:
        files = {
            "manifest.json": json.dumps(manifest, separators=(",", ":")).encode(),
            "index.json": json.dumps(index, separators=(",", ":")).encode(),
            config_name: docker_config_bytes,
            f"blobs/sha256/{docker_platform_digest.removeprefix('sha256:')}": platform_manifest_bytes,
        }
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            output.addfile(info, io.BytesIO(content))
    return archive, docker_config_digest, docker_platform_digest


def test_verifier_accepts_distinct_docker_and_oci_config_digests() -> None:
    """Regression: Docker and OCI exports can carry distinct config digest domains."""
    with tempfile.TemporaryDirectory(prefix="codegauge-oci-config-domain-") as directory:
        root = Path(directory)
        oci_archive, _, inspect, index_digest = _write_synthetic_oci(root)
        docker_archive, docker_config_digest, docker_platform_digest = _write_synthetic_docker_archive(
            root,
            labels=inspect["Config"]["Labels"],
        )
        assert docker_archive.is_file()
        assert docker_config_digest != inspect["Id"]
        inspect["Id"] = docker_config_digest

        result = _run_verifier(
            root,
            oci_archive,
            index_digest,
            inspect,
            docker_archive=docker_archive,
        )

        assert result.returncode == 0, result.stderr
        evidence = json.loads((root / "evidence.json").read_text(encoding="utf-8"))
        assert evidence["docker_config_digest"] == docker_config_digest
        assert evidence["docker_image_id"] == docker_config_digest
        assert evidence["docker_image_id_domain"] == "config"
        assert evidence["docker_platform_digest"] == docker_platform_digest
        assert evidence["oci_config_digest"] != docker_config_digest


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


def _run_verifier(
    root: Path,
    archive: Path,
    output_digest: str,
    inspect: dict[str, object],
    *,
    docker_archive: Path | None = None,
    version: str = VERSION,
    architecture: str = "amd64",
    runtime_mode: str = "native",
    non_root: str = "1000\n",
    version_output: str | None = None,
) -> subprocess.CompletedProcess[str]:
    if docker_archive is None:
        config = inspect["Config"]
        assert isinstance(config, dict)
        labels = config["Labels"]
        assert isinstance(labels, dict)
        docker_archive, _, docker_platform_digest = _write_synthetic_docker_archive(
            root,
            architecture=architecture,
            user=str(config["User"]),
            labels=labels,
        )
        inspect["Id"] = docker_platform_digest
    inspect_path = root / "inspect.json"
    inspect_path.write_text(json.dumps(inspect), encoding="utf-8")
    metadata_path = root / "metadata.json"
    metadata_path.write_text(json.dumps({"containerimage.digest": output_digest}), encoding="utf-8")
    version_path = root / "version.txt"
    version_path.write_text(version_output or f"codegauge {version}\n", encoding="utf-8")
    profiles_path = root / "profiles.txt"
    profiles_path.write_text("java-jacoco-v1\n", encoding="utf-8")
    contract_path = root / "contract.json"
    contract_path.write_text(
        json.dumps(
            {
                "schema": "codegauge-result/v1",
                "tool": {"name": "codegauge", "version": version},
                "profile": "java-jacoco-v1",
                "analysis": {"status": "COMPLETE"},
            }
        ),
        encoding="utf-8",
    )
    non_root_path = root / "uid.txt"
    non_root_path.write_text(non_root, encoding="utf-8")
    evidence_path = root / "evidence.json"
    return subprocess.run(
        [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--oci-archive",
            str(archive),
            "--docker-archive",
            str(docker_archive),
            "--inspect-json",
            str(inspect_path),
            "--metadata-json",
            str(metadata_path),
            "--version",
            version,
            "--revision",
            REVISION,
            "--platform",
            f"linux/{architecture}",
            "--runtime-mode",
            runtime_mode,
            "--version-output",
            str(version_path),
            "--profiles-output",
            str(profiles_path),
            "--contract-output",
            str(contract_path),
            "--non-root-output",
            str(non_root_path),
            "--output",
            str(evidence_path),
        ],
        capture_output=True,
        text=True,
    )


def test_verifier_persists_digest_metadata_and_runtime_evidence() -> None:
    with tempfile.TemporaryDirectory(prefix="codegauge-oci-evidence-test-") as directory:
        root = Path(directory)
        archive, manifest_digest, inspect, index_digest = _write_synthetic_oci(root)
        result = _run_verifier(root, archive, index_digest, inspect)
        assert result.returncode == 0, result.stderr
        evidence = json.loads((root / "evidence.json").read_text(encoding="utf-8"))
        assert evidence["metadata_digest"] == index_digest
        assert evidence["platform_digest"] == manifest_digest
        assert evidence["oci_config_digest"] != evidence["docker_config_digest"]
        assert evidence["docker_image_id"] == evidence["docker_platform_digest"]
        assert evidence["platform"] == "linux/amd64"
        assert evidence["labels"]["org.opencontainers.image.version"] == VERSION
        assert evidence["labels"]["org.opencontainers.image.revision"] == REVISION
        assert evidence["runtime"]["mode"] == "native"
        assert evidence["runtime"]["non_root_uid"] == 1000
        assert evidence["runtime"]["version"] == f"codegauge {VERSION}"
        assert evidence["runtime"]["profiles"] == "java-jacoco-v1"


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
        inspect["Config"]["Labels"]["org.opencontainers.image.revision"] = "b" * 40
        result = _run_verifier(root, archive, index_digest, inspect)
        assert result.returncode != 0
        assert "label" in (result.stderr + result.stdout).lower()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--helper-only", action="store_true")
    args = parser.parse_args()

    if not args.helper_only:
        test_workflow_builds_locally_before_publication()
    test_workflow_asserts_runtime_contract_and_emulation_evidence()
    test_workflow_persists_evidence_and_publishes_only_verified_digests()
    test_verifier_persists_digest_metadata_and_runtime_evidence()
    test_verifier_accepts_distinct_docker_and_oci_config_digests()
    test_verifier_rejects_docker_id_drift()
    test_verifier_rejects_runtime_or_metadata_mismatch()
    test_verifier_requires_emulation_evidence_for_qemu()
    test_verifier_rejects_root_runtime()
    test_verifier_rejects_metadata_digest_drift()
    test_verifier_rejects_label_drift()
    print("OCI DISTRIBUTION TESTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
