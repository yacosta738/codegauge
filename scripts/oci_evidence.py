#!/usr/bin/env python3
"""Validate one locally exported OCI image and persist release evidence.

This verifier is deliberately registry-independent.  The release workflow builds
an OCI archive and a runnable Docker archive, then this script binds the two
outputs to the inspected image and runtime smoke results before publication.
"""

from __future__ import annotations

import hashlib
import json
import re
import tarfile
from pathlib import Path
from typing import Any


SOURCE = "https://github.com/yacosta738/codegauge"
PROFILE = "java-jacoco-v1"
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class EvidenceError(ValueError):
    """Raised when an OCI output or runtime evidence is not releaseable."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvidenceError(f"invalid JSON evidence {path}: {error}") from error
    if not isinstance(value, dict):
        raise EvidenceError(f"JSON evidence {path} must be an object")
    return value


def _digest_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _archive_json(files: dict[str, bytes], name: str) -> dict[str, Any]:
    try:
        return json.loads(files[name].decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError(f"OCI archive is missing valid {name}") from error


def _load_oci_archive(
    path: Path, platform: str
) -> tuple[str, str, str, dict[str, Any], dict[str, Any]]:
    if not path.is_file():
        raise EvidenceError(f"OCI archive does not exist: {path}")
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(path, "r") as archive:
            for member in archive.getmembers():
                if member.isfile():
                    handle = archive.extractfile(member)
                    if handle is not None:
                        files[member.name] = handle.read()
    except (OSError, tarfile.TarError) as error:
        raise EvidenceError(f"cannot read OCI archive {path}: {error}") from error

    index_bytes = files.get("index.json")
    if index_bytes is None:
        raise EvidenceError("OCI archive is missing index.json")
    index_digest = _digest_bytes(index_bytes)
    index = _archive_json(files, "index.json")
    wanted_os, wanted_arch = platform.split("/", 1)
    candidates = [
        descriptor
        for descriptor in index.get("manifests", [])
        if isinstance(descriptor, dict)
        and descriptor.get("platform", {}).get("os") == wanted_os
        and descriptor.get("platform", {}).get("architecture") == wanted_arch
    ]
    if len(candidates) != 1:
        raise EvidenceError(f"OCI archive must contain exactly one {platform} image manifest")
    descriptor = candidates[0]
    manifest_digest = descriptor.get("digest")
    if not isinstance(manifest_digest, str) or not DIGEST_RE.fullmatch(manifest_digest):
        raise EvidenceError("OCI image manifest has no valid immutable digest")
    manifest_name = f"blobs/{manifest_digest.replace(':', '/')}"
    manifest_bytes = files.get(manifest_name)
    if manifest_bytes is None:
        raise EvidenceError(f"OCI archive is missing manifest blob {manifest_digest}")
    if _digest_bytes(manifest_bytes) != manifest_digest:
        raise EvidenceError("OCI manifest digest does not match its blob")
    manifest = _archive_json(files, manifest_name)
    config_descriptor = manifest.get("config", {})
    config_digest = (
        config_descriptor.get("digest") if isinstance(config_descriptor, dict) else None
    )
    if not isinstance(config_digest, str) or not DIGEST_RE.fullmatch(config_digest):
        raise EvidenceError("OCI image manifest has no valid config digest")
    config_name = f"blobs/{config_digest.replace(':', '/')}"
    config_bytes = files.get(config_name)
    if config_bytes is None or _digest_bytes(config_bytes) != config_digest:
        raise EvidenceError("OCI config digest does not match its blob")
    config = _archive_json(files, config_name)
    return index_digest, manifest_digest, config_digest, manifest, config


def _load_docker_archive(path: Path, platform: str) -> tuple[str, str | None]:
    """Return Docker config and, when present, platform-manifest digests."""
    if not path.is_file():
        raise EvidenceError(f"Docker archive does not exist: {path}")
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(path, "r") as archive:
            for member in archive.getmembers():
                if member.isfile():
                    handle = archive.extractfile(member)
                    if handle is not None:
                        files[member.name] = handle.read()
    except (OSError, tarfile.TarError) as error:
        raise EvidenceError(f"cannot read Docker archive {path}: {error}") from error

    try:
        manifest = json.loads(files["manifest.json"].decode("utf-8"))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError("Docker archive is missing valid manifest.json") from error
    if not isinstance(manifest, list) or len(manifest) != 1 or not isinstance(manifest[0], dict):
        raise EvidenceError("Docker archive must contain exactly one image manifest")

    config_name = manifest[0].get("Config")
    if not isinstance(config_name, str) or not config_name:
        raise EvidenceError("Docker archive manifest has no config reference")
    config_bytes = files.get(config_name)
    if config_bytes is None:
        raise EvidenceError(f"Docker archive is missing config {config_name}")
    try:
        config = json.loads(config_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError(f"Docker archive config {config_name} is not valid JSON") from error
    if not isinstance(config, dict):
        raise EvidenceError(f"Docker archive config {config_name} must be an object")

    config_digest = _digest_bytes(config_bytes)
    config_path = Path(config_name).as_posix()
    if config_path.startswith("blobs/sha256/"):
        referenced_digest = "sha256:" + config_path.removeprefix("blobs/sha256/")
        if not DIGEST_RE.fullmatch(referenced_digest):
            raise EvidenceError("Docker archive config reference has no valid digest")
        if referenced_digest != config_digest:
            raise EvidenceError("Docker archive config digest does not match its blob")

    config_platform = f"{config.get('os')}/{config.get('architecture')}"
    if config_platform != platform:
        raise EvidenceError(
            f"Docker archive config platform mismatch: expected {platform!r}, got {config_platform!r}"
        )

    platform_digest = None
    index_bytes = files.get("index.json")
    if index_bytes is not None:
        try:
            index = json.loads(index_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise EvidenceError("Docker archive has invalid index.json") from error
        if not isinstance(index, dict):
            raise EvidenceError("Docker archive index.json must be an object")
        candidates = [
            descriptor
            for descriptor in index.get("manifests", [])
            if isinstance(descriptor, dict)
            and descriptor.get("platform", {}).get("os") == platform.split("/", 1)[0]
            and descriptor.get("platform", {}).get("architecture") == platform.split("/", 1)[1]
        ]
        if len(candidates) != 1:
            raise EvidenceError(f"Docker archive must contain exactly one {platform} image manifest")
        platform_digest = candidates[0].get("digest")
        if not isinstance(platform_digest, str) or not DIGEST_RE.fullmatch(platform_digest):
            raise EvidenceError("Docker archive image manifest has no valid immutable digest")
        manifest_name = f"blobs/{platform_digest.replace(':', '/')}"
        manifest_bytes = files.get(manifest_name)
        if manifest_bytes is None or _digest_bytes(manifest_bytes) != platform_digest:
            raise EvidenceError("Docker archive image manifest digest does not match its blob")
        try:
            platform_manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise EvidenceError("Docker archive image manifest is not valid JSON") from error
        if not isinstance(platform_manifest, dict):
            raise EvidenceError("Docker archive image manifest must be an object")
        platform_config = platform_manifest.get("config", {})
        if (
            not isinstance(platform_config, dict)
            or platform_config.get("digest") != config_digest
        ):
            raise EvidenceError("Docker archive image manifest config differs from its config blob")

    return config_digest, platform_digest


def _non_root_user(user: object) -> bool:
    if not isinstance(user, str) or not user.strip():
        return False
    identity = user.strip().split(":", 1)[0]
    if identity in {"0", "root"}:
        return False
    try:
        return int(identity) > 0
    except ValueError:
        return True


def _read_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise EvidenceError(f"cannot read {label} evidence {path}: {error}") from error


def _validate_runtime(
    *,
    expected_version: str,
    runtime_mode: str,
    version_output: Path,
    profiles_output: Path,
    contract_output: Path,
    non_root_output: Path,
    emulation_evidence: Path | None,
) -> dict[str, Any]:
    version_text = _read_text(version_output, "version")
    expected_runtime_version = f"codegauge {expected_version}"
    if version_text != expected_runtime_version:
        raise EvidenceError(
            f"runtime version mismatch: expected {expected_runtime_version!r}, got {version_text!r}"
        )

    profiles_text = _read_text(profiles_output, "profiles")
    if profiles_text != PROFILE:
        raise EvidenceError(f"runtime profile mismatch: expected {PROFILE!r}, got {profiles_text!r}")

    contract = _read_json(contract_output)
    if contract.get("schema") != "codegauge-result/v1":
        raise EvidenceError("contract smoke returned an unexpected schema")
    if contract.get("profile") != PROFILE:
        raise EvidenceError("contract smoke returned an unexpected profile")
    if contract.get("analysis", {}).get("status") != "COMPLETE":
        raise EvidenceError("contract smoke did not produce COMPLETE analysis")

    uid_text = _read_text(non_root_output, "non-root")
    try:
        uid = int(uid_text)
    except ValueError as error:
        raise EvidenceError(f"non-root smoke returned a non-numeric UID: {uid_text!r}") from error
    if uid <= 0:
        raise EvidenceError(f"runtime is root: uid={uid}")

    if runtime_mode not in {"native", "qemu"}:
        raise EvidenceError(f"unsupported runtime mode: {runtime_mode}")
    emulation_text = None
    if runtime_mode == "qemu":
        if emulation_evidence is None:
            raise EvidenceError("qemu runtime requires explicit emulation evidence")
        emulation_text = _read_text(emulation_evidence, "emulation")
        if "linux/arm64" not in emulation_text:
            raise EvidenceError("emulation evidence does not advertise linux/arm64")

    runtime: dict[str, Any] = {
        "mode": runtime_mode,
        "non_root_uid": uid,
        "version": version_text,
        "profiles": profiles_text,
        "contract_schema": contract["schema"],
        "contract_status": contract["analysis"]["status"],
    }
    if emulation_text is not None:
        runtime["emulation_evidence"] = emulation_text
    return runtime


def verify(
    *,
    oci_archive: Path,
    docker_archive: Path,
    inspect_json: Path,
    metadata_json: Path,
    version: str,
    revision: str,
    platform: str,
    runtime_mode: str,
    version_output: Path,
    profiles_output: Path,
    contract_output: Path,
    non_root_output: Path,
    emulation_evidence: Path | None,
    output: Path,
) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise EvidenceError("source revision must be a lowercase 40-character SHA")
    if platform not in {"linux/amd64", "linux/arm64"}:
        raise EvidenceError(f"unsupported OCI platform: {platform}")

    index_digest, platform_digest, oci_config_digest, manifest, config = _load_oci_archive(
        oci_archive, platform
    )
    docker_config_digest, docker_platform_digest = _load_docker_archive(docker_archive, platform)
    labels = config.get("config", {}).get("Labels", {})
    if not isinstance(labels, dict):
        raise EvidenceError("OCI config labels are missing")
    expected_labels = {
        "org.opencontainers.image.version": version,
        "org.opencontainers.image.revision": revision,
        "org.opencontainers.image.source": SOURCE,
        "org.opencontainers.image.platform": platform,
    }
    for name, expected in expected_labels.items():
        if labels.get(name) != expected:
            raise EvidenceError(f"OCI label mismatch for {name}: expected {expected!r}")

    inspect = _read_json(inspect_json)
    architecture = platform.split("/", 1)[1]
    if inspect.get("Os") != "linux" or inspect.get("Architecture") != architecture:
        raise EvidenceError("docker inspect platform does not match the requested architecture")
    inspect_labels = inspect.get("Config", {}).get("Labels", {})
    if inspect_labels != labels:
        raise EvidenceError("docker inspect labels differ from the exported OCI config labels")
    user = inspect.get("Config", {}).get("User")
    if not _non_root_user(user):
        raise EvidenceError("docker inspect reports a root or missing runtime user")
    image_id = inspect.get("Id")
    if not isinstance(image_id, str) or not DIGEST_RE.fullmatch(image_id):
        raise EvidenceError("docker inspect did not return an immutable image ID")
    # Docker Engine versions have reported `.Id` as either the saved config
    # digest or the platform manifest digest. Both identities are derived from
    # and validated against the Docker archive; neither is the OCI config digest.
    docker_id_domains = {"config": docker_config_digest}
    if docker_platform_digest is not None:
        docker_id_domains["platform_manifest"] = docker_platform_digest
    image_id_domain = next(
        (domain for domain, digest in docker_id_domains.items() if image_id == digest),
        None,
    )
    if image_id_domain is None:
        expected_ids = ", ".join(
            f"{domain}={digest}" for domain, digest in docker_id_domains.items()
        )
        raise EvidenceError(
            f"docker inspect image ID {image_id} differs from Docker archive identity ({expected_ids})"
        )

    build_metadata = _read_json(metadata_json)
    metadata_digest = build_metadata.get("containerimage.digest")
    if not isinstance(metadata_digest, str) or not DIGEST_RE.fullmatch(metadata_digest):
        raise EvidenceError("BuildKit metadata has no immutable containerimage.digest")
    if metadata_digest not in {index_digest, platform_digest}:
        raise EvidenceError("BuildKit metadata digest differs from the OCI output digests")

    runtime = _validate_runtime(
        expected_version=version,
        runtime_mode=runtime_mode,
        version_output=version_output,
        profiles_output=profiles_output,
        contract_output=contract_output,
        non_root_output=non_root_output,
        emulation_evidence=emulation_evidence,
    )
    evidence: dict[str, Any] = {
        "architecture": architecture,
        "platform": platform,
        "version": version,
        "source_revision": revision,
        "metadata_digest": metadata_digest,
        "oci_index_digest": index_digest,
        "platform_digest": platform_digest,
        "oci_config_digest": oci_config_digest,
        "docker_config_digest": docker_config_digest,
        "docker_platform_digest": docker_platform_digest,
        "docker_image_id": image_id,
        "docker_image_id_domain": image_id_domain,
        "labels": expected_labels,
        "manifest_media_type": manifest.get("mediaType"),
        "runtime": runtime,
        "verified": True,
    }
    evidence["build_metadata"] = build_metadata
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence
