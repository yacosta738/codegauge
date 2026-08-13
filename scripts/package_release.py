#!/usr/bin/env python3
"""Create one deterministic CodeGauge release archive and lowercase SHA-256 sidecar."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import shutil
import stat
import tarfile
import tempfile
import zipfile
from pathlib import Path


UNIX_TARGETS = {
    "x86_64-unknown-linux-gnu",
    "aarch64-unknown-linux-gnu",
    "x86_64-unknown-linux-musl",
    "aarch64-unknown-linux-musl",
    "x86_64-apple-darwin",
    "aarch64-apple-darwin",
}
WINDOWS_TARGETS = {"x86_64-pc-windows-msvc", "aarch64-pc-windows-msvc"}
TARGETS = UNIX_TARGETS | WINDOWS_TARGETS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--target", required=True, choices=sorted(TARGETS))
    parser.add_argument("--version", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--rust-toolchain", required=True)
    parser.add_argument("--binary-evidence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def metadata(args: argparse.Namespace, archive: str, binary_evidence: dict[str, object]) -> dict[str, object]:
    return {
        "version": args.version,
        "source_revision": args.revision,
        "rust_toolchain": args.rust_toolchain,
        "target": args.target,
        "archive": archive,
        "binary_evidence": binary_evidence,
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().lower()


def make_archive(args: argparse.Namespace, root: Path, archive: Path) -> None:
    binary_name = "codegauge.exe" if args.target in WINDOWS_TARGETS else "codegauge"
    binary = root / binary_name
    shutil.copy2(args.binary, binary)
    if args.target in UNIX_TARGETS:
        binary.chmod(0o755)
        with archive.open("wb") as archive_stream:
            with gzip.GzipFile(fileobj=archive_stream, mode="wb", mtime=0) as gzip_stream:
                with tarfile.open(fileobj=gzip_stream, mode="w", format=tarfile.PAX_FORMAT) as output:
                    info = output.gettarinfo(binary, arcname=binary_name)
                    info.mtime = 0
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    with binary.open("rb") as stream:
                        output.addfile(info, stream)
    else:
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as output:
            info = zipfile.ZipInfo(binary_name, date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = (0o100755 << 16)
            output.writestr(info, binary.read_bytes())


def main() -> int:
    args = parse_args()
    if not re.fullmatch(r"(0|[1-9][0-9]*)\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?", args.version):
        raise SystemExit("--version must be a valid synchronized semver release version")
    if len(args.revision) != 40 or any(character not in "0123456789abcdef" for character in args.revision):
        raise SystemExit("--revision must be a 40-character lowercase immutable Git revision")
    if not args.binary.is_file():
        raise SystemExit(f"binary does not exist: {args.binary}")
    try:
        binary_evidence = json.loads(args.binary_evidence.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"binary evidence is not valid JSON: {error}") from error
    if not isinstance(binary_evidence, dict) or binary_evidence.get("target") != args.target:
        raise SystemExit("binary evidence must identify the exact release target")
    if binary_evidence.get("mode") not in {"native", "cross-target"}:
        raise SystemExit("binary evidence must be native or cross-target")
    if binary_evidence.get("mode") == "native" and binary_evidence.get("execution") != "native":
        raise SystemExit("native binary evidence must record native execution")
    if binary_evidence.get("mode") == "cross-target" and binary_evidence.get("execution") != "not-run":
        raise SystemExit("cross-target binary evidence must explicitly record that execution was not run")
    if binary_evidence.get("mode") == "native":
        if binary_evidence.get("version") != f"codegauge {args.version}\n":
            raise SystemExit("native binary version does not match release metadata")
        if binary_evidence.get("profiles") != "java-jacoco-v1\n":
            raise SystemExit("native binary profiles do not match the released profile contract")
    if args.target in UNIX_TARGETS and not args.binary.stat().st_mode & stat.S_IXUSR:
        raise SystemExit("release binary must be executable")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    extension = "zip" if args.target in WINDOWS_TARGETS else "tar.gz"
    name = f"codegauge-{args.version}-{args.target}.{extension}"
    archive = args.output_dir / name
    with tempfile.TemporaryDirectory(prefix="codegauge-release-") as directory:
        make_archive(args, Path(directory), archive)
    digest = sha256(archive)
    sidecar = archive.with_name(f"{archive.name}.sha256")
    sidecar.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    manifest = archive.with_name(f"release-manifest-{args.target}.json")
    manifest.write_text(
        json.dumps(metadata(args, archive.name, binary_evidence) | {"sha256": digest}, indent=2) + "\n",
        encoding="utf-8",
    )
    recorded_digest, recorded_name = sidecar.read_text(encoding="utf-8").split()
    if recorded_name != archive.name or recorded_digest != digest:
        raise SystemExit("generated SHA-256 sidecar did not verify")
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
