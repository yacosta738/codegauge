#!/usr/bin/env python3
"""Verify release identity, package versions, archive manifests, and binary evidence.

The script is deliberately local and side-effect free apart from writing the requested
binary-evidence file.  GitHub publication jobs call it after checking out the exact
release-please SHA; local tests can exercise the pure validators without credentials.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - CI uses modern Python
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "yacosta738/codegauge"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SEMVER_RE = re.compile(r"^v(0|[1-9][0-9]*)\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")
RUNTIME_CRATES = (
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-cli",
)
NPM_PACKAGES = (
    "@yacosta738/codegauge-linux-x64-gnu",
    "@yacosta738/codegauge-linux-arm64-gnu",
    "@yacosta738/codegauge-darwin-x64",
    "@yacosta738/codegauge-darwin-arm64",
    "@yacosta738/codegauge-win32-x64-msvc",
    "@yacosta738/codegauge-win32-arm64-msvc",
)
TARGET_EXTENSIONS = {
    "x86_64-unknown-linux-gnu": "tar.gz",
    "aarch64-unknown-linux-gnu": "tar.gz",
    "x86_64-unknown-linux-musl": "tar.gz",
    "aarch64-unknown-linux-musl": "tar.gz",
    "x86_64-apple-darwin": "tar.gz",
    "aarch64-apple-darwin": "tar.gz",
    "x86_64-pc-windows-msvc": "zip",
    "aarch64-pc-windows-msvc": "zip",
}


class ProvenanceError(ValueError):
    """Raised when a release input or artifact is not release-safe."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ProvenanceError(f"unable to read JSON {path}: {error}") from error
    if not isinstance(value, dict):
        raise ProvenanceError(f"JSON {path} must contain an object")
    return value


def require_sha(value: str, field: str) -> str:
    if not SHA_RE.fullmatch(value):
        raise ProvenanceError(f"{field} must be a 40-character lowercase Git SHA")
    return value


def version_from_tag(tag: str) -> str:
    match = SEMVER_RE.fullmatch(tag)
    if not match:
        raise ProvenanceError(f"release tag must be an exact v-prefixed semver: {tag}")
    return tag[1:]


def validate_release_identity(
    *,
    release_tag: str,
    release_sha: str,
    main_sha: str,
    tag_revision: str,
    main_revision: str,
) -> str:
    """Validate the exact release-please tag and its merged-main revision.

    Both the release-please output SHA and the expected merged-main SHA are checked
    against the resolved tag.  A tag that merely happens to match the semver shape
    cannot pass this boundary.
    """

    version = version_from_tag(release_tag)
    require_sha(release_sha, "release_sha")
    require_sha(main_sha, "main_sha")
    require_sha(tag_revision, "tag revision")
    require_sha(main_revision, "main revision")
    if tag_revision != release_sha:
        raise ProvenanceError("release-please tag does not resolve to release_sha")
    if tag_revision != main_sha or main_revision != main_sha:
        raise ProvenanceError("release tag does not point to the expected merged-main commit")
    return version


def read_workspace_version(root: Path = ROOT) -> str:
    if tomllib is None:
        raise ProvenanceError("Python tomllib is required for release provenance checks")
    try:
        document = tomllib.loads((root / "Cargo.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ProvenanceError(f"unable to read workspace Cargo.toml: {error}") from error
    version = document.get("workspace", {}).get("package", {}).get("version")
    if not isinstance(version, str):
        raise ProvenanceError("workspace Cargo.toml has no package version")
    return version


def validate_package_versions(version: str, root: Path = ROOT) -> None:
    """Assert the Cargo and all twelve npm package manifests share one version."""

    if read_workspace_version(root) != version:
        raise ProvenanceError("Cargo workspace version does not match the release tag")

    lock_path = root / "Cargo.lock"
    if not lock_path.is_file():
        raise ProvenanceError("Cargo.lock is required for release provenance")
    lock_text = lock_path.read_text(encoding="utf-8")
    for crate in RUNTIME_CRATES:
        match = re.search(rf'name = "{re.escape(crate)}"\s+version = "([^"]+)"', lock_text)
        if not match or match.group(1) != version:
            raise ProvenanceError(f"Cargo.lock version drift for {crate}")

    for crate in RUNTIME_CRATES:
        path = root / "crates" / crate / "Cargo.toml"
        if not path.is_file() or tomllib is None:
            raise ProvenanceError(f"missing Cargo manifest for {crate}")
        package = tomllib.loads(path.read_text(encoding="utf-8")).get("package", {})
        if package.get("version") != {"workspace": True}:
            raise ProvenanceError(f"{crate} must inherit the workspace version")

    base_path = root / "npm" / "codegauge" / "package.json"
    base = load_json(base_path)
    if base.get("name") != "@yacosta738/codegauge" or base.get("version") != version:
        raise ProvenanceError("npm base package version/name does not match the release tag")
    optional = base.get("optionalDependencies")
    if not isinstance(optional, dict) or set(optional) != set(NPM_PACKAGES):
        raise ProvenanceError("npm base package does not declare exactly six approved platform packages")
    if any(value != version for value in optional.values()):
        raise ProvenanceError("npm optional dependency pins do not match the release tag")

    for package_name in NPM_PACKAGES:
        package_path = root / "npm" / "packages" / package_name.removeprefix("@yacosta738/") / "package.json"
        package = load_json(package_path)
        if package.get("name") != package_name or package.get("version") != version:
            raise ProvenanceError(f"npm platform package version drift: {package_name}")


def validate_linked_components(root: Path = ROOT) -> None:
    config = load_json(root / "release-please-config.json")
    linked = [
        component
        for plugin in config.get("plugins", [])
        if isinstance(plugin, dict) and plugin.get("type") == "linked-versions"
        for component in plugin.get("components", [])
    ]
    expected = {crate for crate in RUNTIME_CRATES} | {"codegauge"} | {
        package.removeprefix("@yacosta738/") for package in NPM_PACKAGES
    }
    missing = sorted(expected - set(linked))
    if missing:
        raise ProvenanceError(f"release-please linked-versions is missing: {', '.join(missing)}")


def validate_archive_manifest(path: Path, version: str, source_revision: str) -> dict[str, Any]:
    manifest = load_json(path)
    target = manifest.get("target")
    archive = manifest.get("archive")
    digest = manifest.get("sha256")
    if manifest.get("version") != version:
        raise ProvenanceError(f"{path.name} version drift")
    if manifest.get("source_revision") != source_revision:
        raise ProvenanceError(f"{path.name} immutable source revision drift")
    if manifest.get("rust_toolchain") != "1.97.1":
        raise ProvenanceError(f"{path.name} Rust toolchain drift")
    if target not in TARGET_EXTENSIONS:
        raise ProvenanceError(f"{path.name} contains an unapproved target")
    expected_archive = f"codegauge-{version}-{target}.{TARGET_EXTENSIONS[target]}"
    if archive != expected_archive:
        raise ProvenanceError(f"{path.name} archive name drift")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ProvenanceError(f"{path.name} must contain a lowercase SHA-256 digest")
    evidence = manifest.get("binary_evidence")
    if not isinstance(evidence, dict) or evidence.get("target") != target:
        raise ProvenanceError(f"{path.name} is missing target-aware binary evidence")
    if evidence.get("mode") == "native":
        if evidence.get("execution") != "native":
            raise ProvenanceError(f"{path.name} native evidence is not executable evidence")
        if evidence.get("version") != f"codegauge {version}\n" or evidence.get("profiles") != "java-jacoco-v1\n":
            raise ProvenanceError(f"{path.name} native version/profiles evidence drift")
    elif evidence.get("mode") == "cross-target":
        if evidence.get("execution") != "not-run":
            raise ProvenanceError(f"{path.name} cross-target evidence must state execution was not run")
    else:
        raise ProvenanceError(f"{path.name} has an unknown binary evidence mode")
    return manifest


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive_set(release_out: Path, version: str, source_revision: str) -> None:
    manifests = sorted(release_out.glob("release-manifest-*.json"))
    if len(manifests) != len(TARGET_EXTENSIONS):
        raise ProvenanceError(f"expected {len(TARGET_EXTENSIONS)} archive manifests, found {len(manifests)}")
    seen_targets: set[str] = set()
    for manifest_path in manifests:
        manifest = validate_archive_manifest(manifest_path, version, source_revision)
        target = str(manifest["target"])
        if target in seen_targets:
            raise ProvenanceError(f"duplicate archive target evidence: {target}")
        seen_targets.add(target)
        archive_path = release_out / str(manifest["archive"])
        sidecar_path = release_out / f"{archive_path.name}.sha256"
        if not archive_path.is_file() or not sidecar_path.is_file():
            raise ProvenanceError(f"missing archive or checksum sidecar for {target}")
        recorded_digest, recorded_name = sidecar_path.read_text(encoding="utf-8").split()
        if recorded_name != archive_path.name or recorded_digest != manifest["sha256"]:
            raise ProvenanceError(f"{target} checksum sidecar does not match its manifest")
        if sha256(archive_path) != recorded_digest:
            raise ProvenanceError(f"{target} archive checksum mismatch")
    if seen_targets != set(TARGET_EXTENSIONS):
        raise ProvenanceError("archive matrix is incomplete")


def write_binary_evidence(
    *,
    binary: Path,
    version: str,
    target: str,
    mode: str,
    output: Path,
) -> None:
    if target not in TARGET_EXTENSIONS:
        raise ProvenanceError(f"unapproved binary target: {target}")
    if not binary.is_file():
        raise ProvenanceError(f"release binary does not exist: {binary}")
    if mode == "native":
        try:
            version_output = subprocess.run([str(binary), "version"], check=True, capture_output=True, text=True).stdout
            profiles_output = subprocess.run([str(binary), "profiles"], check=True, capture_output=True, text=True).stdout
        except (OSError, subprocess.CalledProcessError) as error:
            raise ProvenanceError(f"native release binary smoke test failed: {error}") from error
        evidence: dict[str, Any] = {
            "mode": "native",
            "target": target,
            "execution": "native",
            "version": version_output,
            "profiles": profiles_output,
        }
        if version_output != f"codegauge {version}\n" or profiles_output != "java-jacoco-v1\n":
            raise ProvenanceError("native release binary version/profiles do not match release metadata")
    elif mode == "cross-target":
        evidence = {
            "mode": "cross-target",
            "target": target,
            "execution": "not-run",
            "reason": "target-aware evidence recorded without pretending the binary is native",
        }
    else:
        raise ProvenanceError("binary evidence mode must be native or cross-target")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def git_revision(ref: str) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", f"{ref}^{{commit}}"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as error:
        raise ProvenanceError(f"unable to resolve Git revision for {ref}: {error}") from error


def validate_inputs(args: argparse.Namespace) -> None:
    version = version_from_tag(args.release_tag)
    tag_revision = git_revision(args.release_tag)
    main_revision = git_revision("refs/remotes/origin/main")
    validate_release_identity(
        release_tag=args.release_tag,
        release_sha=args.release_sha,
        main_sha=args.main_sha,
        tag_revision=tag_revision,
        main_revision=main_revision,
    )
    if main_revision != args.main_sha:
        raise ProvenanceError("origin/main does not match the expected merged-main SHA")
    if not args.release_url or f"/releases/tag/{args.release_tag}" not in args.release_url:
        raise ProvenanceError("release-please URL does not identify the requested release tag")
    validate_package_versions(version)
    validate_linked_components()
    if not args.dry_run:
        try:
            subprocess.run(
                ["gh", "release", "view", args.release_tag, "--repo", args.repository, "--json", "tagName,url"],
                check=True,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            raise ProvenanceError(f"release-please-created GitHub Release is not available: {error}") from error


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(description=__doc__)
    subcommands = command.add_subparsers(dest="command", required=True)

    inputs = subcommands.add_parser("inputs")
    inputs.add_argument("--release-tag", required=True)
    inputs.add_argument("--release-sha", required=True)
    inputs.add_argument("--main-sha", required=True)
    inputs.add_argument("--release-url", required=True)
    inputs.add_argument("--repository", default=REPOSITORY)
    inputs.add_argument("--dry-run", action="store_true")

    binary = subcommands.add_parser("binary")
    binary.add_argument("--binary", type=Path, required=True)
    binary.add_argument("--version", required=True)
    binary.add_argument("--target", required=True)
    binary.add_argument("--mode", choices=("native", "cross-target"), required=True)
    binary.add_argument("--evidence-output", type=Path, required=True)

    archives = subcommands.add_parser("archives")
    archives.add_argument("--release-version", required=True)
    archives.add_argument("--source-revision", required=True)
    archives.add_argument("--release-out", type=Path, required=True)
    return command


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "inputs":
            validate_inputs(args)
            print("RELEASE INPUT PROVENANCE: PASS")
        elif args.command == "binary":
            write_binary_evidence(
                binary=args.binary,
                version=args.version,
                target=args.target,
                mode=args.mode,
                output=args.evidence_output,
            )
            print(f"BINARY PROVENANCE: PASS ({args.mode}, {args.target})")
        else:
            validate_sha = require_sha(args.source_revision, "source_revision")
            validate_archive_set(args.release_out, args.release_version, validate_sha)
            print("RELEASE ARCHIVE PROVENANCE: PASS")
        return 0
    except ProvenanceError as error:
        print(f"RELEASE PROVENANCE: FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
