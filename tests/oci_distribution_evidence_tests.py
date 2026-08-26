#!/usr/bin/env python3
"""Positive OCI/Docker evidence checks and synthetic archive builders."""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = ROOT / "scripts" / "verify_oci_evidence.py"
VERSION = "0.1.0"
REVISION = "a" * 40


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
    manifest_digest, manifest_bytes = _blob(
        json.dumps(manifest, separators=(",", ":")).encode()
    )
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
    manifest = [{"Config": config_name, "RepoTags": ["codegauge:test"], "Layers": []}]
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
    profiles_path.write_text("jvm-jacoco-v1\ntypescript-oxc-istanbul-v1\n", encoding="utf-8")
    contract_path = root / "contract.json"
    contract_path.write_text(
        json.dumps(
            {
                "schema": "codegauge-result/v1",
                "tool": {"name": "codegauge", "version": version},
                "profile": "jvm-jacoco-v1",
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


def test_verifier_accepts_distinct_docker_and_oci_config_digests() -> None:
    """Regression: Docker and OCI exports can carry distinct config digest domains."""
    with tempfile.TemporaryDirectory(prefix="codegauge-oci-config-domain-") as directory:
        root = Path(directory)
        oci_archive, _, inspect, index_digest = _write_synthetic_oci(root)
        docker_archive, docker_config_digest, docker_platform_digest = _write_synthetic_docker_archive(
            root, labels=inspect["Config"]["Labels"]
        )
        assert docker_archive.is_file()
        assert docker_config_digest != inspect["Id"]
        inspect["Id"] = docker_config_digest

        result = _run_verifier(
            root, oci_archive, index_digest, inspect, docker_archive=docker_archive
        )

        assert result.returncode == 0, result.stderr
        evidence = json.loads((root / "evidence.json").read_text(encoding="utf-8"))
        assert evidence["docker_config_digest"] == docker_config_digest
        assert evidence["docker_image_id"] == docker_config_digest
        assert evidence["docker_image_id_domain"] == "config"
        assert evidence["docker_platform_digest"] == docker_platform_digest
        assert evidence["oci_config_digest"] != docker_config_digest


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
        assert evidence["runtime"]["profiles"] == "jvm-jacoco-v1\ntypescript-oxc-istanbul-v1"


def run_tests() -> None:
    test_verifier_accepts_distinct_docker_and_oci_config_digests()
    test_verifier_persists_digest_metadata_and_runtime_evidence()


if __name__ == "__main__":
    run_tests()
    print("OCI DISTRIBUTION EVIDENCE TESTS: PASS")
