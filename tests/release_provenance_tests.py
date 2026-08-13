#!/usr/bin/env python3
"""Focused local regression checks for the R-D release provenance boundary."""

from __future__ import annotations

import re
import json
import tempfile
import sys
from pathlib import Path
from shutil import rmtree


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CALLER = ROOT / ".github" / "workflows" / "release.yml"
BUILD = ROOT / ".github" / "workflows" / "release-build.yml"
PUBLISH = ROOT / ".github" / "workflows" / "release-publish.yml"

from scripts.verify_release_provenance import (  # noqa: E402
    ProvenanceError,
    validate_archive_manifest,
    validate_linked_components,
    validate_package_versions,
    validate_release_identity,
    write_binary_evidence,
)


def main() -> int:
    caller = CALLER.read_text(encoding="utf-8")
    build = BUILD.read_text(encoding="utf-8")
    publish = PUBLISH.read_text(encoding="utf-8")
    release_please = (ROOT / ".github" / "workflows" / "release-please.yml").read_text(encoding="utf-8")
    config = (ROOT / "release-please-config.json").read_text(encoding="utf-8")

    assert "workflow_call:" in caller, "release caller must be callable by release-please"
    assert "workflow_dispatch:" in caller, "release caller must preserve manual rehearsal input"
    assert not re.search(r"^\s+push:\s*$", caller, re.MULTILINE), "arbitrary tag pushes must not start publication"
    for input_name in ("release_tag", "release_sha", "main_sha", "release_url", "dry_run"):
        assert f"{input_name}:" in caller, f"caller input is missing: {input_name}"
        assert f"{input_name}: ${{{{ inputs.{input_name} }}}}" in caller
    assert "uses: ./.github/workflows/release-build.yml" in caller
    assert "uses: ./.github/workflows/release-publish.yml" in caller
    assert "needs: release-build" in caller
    assert "secrets: inherit" in caller
    assert "permissions:\n      contents: write" in caller
    assert "inputs.release_tag ||" not in caller, "release jobs must not fall back to a default ref"
    assert "github.ref_name" not in caller, "release jobs must not consume the triggering ref"
    assert "workflow_call:" in build and "workflow_call:" in publish
    assert "release-preflight:" in build
    assert "scripts/verify_release_provenance.py" in build
    assert "verify_release_provenance.py binary" in build
    assert '--mode "${{ matrix.evidence_mode }}"' in build
    assert "gh release upload" in publish and "--clobber" in publish
    assert "gh release create" not in publish, "release-please is the only release creator"
    assert "release-preflight:" not in publish, "build preflight must gate the publish caller"
    assert "uses: ./.github/workflows/release.yml" in release_please
    assert "steps.release.outputs" in release_please

    for component in (
        "codegauge-linux-x64-gnu",
        "codegauge-linux-arm64-gnu",
        "codegauge-darwin-x64",
        "codegauge-darwin-arm64",
        "codegauge-win32-x64-msvc",
        "codegauge-win32-arm64-msvc",
    ):
        assert config.count(f'"{component}"') >= 2, f"linked release-please component is missing: {component}"

    validate_linked_components(ROOT)
    try:
        validate_package_versions("9.9.9", ROOT)
    except ProvenanceError:
        pass
    else:
        raise AssertionError("Cargo/npm version drift was accepted")
    assert (
        validate_release_identity(
            release_tag="v0.1.0",
            release_sha="a" * 40,
            main_sha="a" * 40,
            tag_revision="a" * 40,
            main_revision="a" * 40,
        )
        == "0.1.0"
    )
    for invalid in (
        {
            "release_tag": "0.1.0",
            "release_sha": "a" * 40,
            "main_sha": "a" * 40,
            "tag_revision": "a" * 40,
            "main_revision": "a" * 40,
        },
        {
            "release_tag": "v0.1.0",
            "release_sha": "a" * 40,
            "main_sha": "b" * 40,
            "tag_revision": "a" * 40,
            "main_revision": "b" * 40,
        },
    ):
        try:
            validate_release_identity(**invalid)
        except ProvenanceError:
            pass
        else:
            raise AssertionError("unsafe release provenance was accepted")

    directory = Path(tempfile.mkdtemp(prefix="codegauge-release-provenance-test-"))
    try:
        binary = directory / "codegauge"
        binary.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  version) printf 'codegauge 0.1.0\\n' ;;\n"
            "  profiles) printf 'java-jacoco-v1\\n' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        binary.chmod(0o755)
        native_evidence = directory / "native.json"
        write_binary_evidence(
            binary=binary,
            version="0.1.0",
            target="x86_64-unknown-linux-gnu",
            mode="native",
            output=native_evidence,
        )
        cross_evidence = directory / "cross.json"
        write_binary_evidence(
            binary=binary,
            version="0.1.0",
            target="aarch64-pc-windows-msvc",
            mode="cross-target",
            output=cross_evidence,
        )
        assert json.loads(cross_evidence.read_text(encoding="utf-8"))["execution"] == "not-run"
        try:
            write_binary_evidence(
                binary=binary,
                version="0.2.0",
                target="x86_64-unknown-linux-gnu",
                mode="native",
                output=directory / "wrong-version.json",
            )
        except ProvenanceError:
            pass
        else:
            raise AssertionError("binary version drift was accepted")

        manifest_path = directory / "release-manifest-x86_64-unknown-linux-gnu.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "version": "0.1.0",
                    "source_revision": "a" * 40,
                    "target": "x86_64-unknown-linux-gnu",
                    "archive": "codegauge-0.1.0-x86_64-unknown-linux-gnu.tar.gz",
                    "rust_toolchain": "1.97.1",
                    "sha256": "0" * 64,
                    "binary_evidence": json.loads(native_evidence.read_text(encoding="utf-8")),
                }
            ),
            encoding="utf-8",
        )
        validate_archive_manifest(manifest_path, "0.1.0", "a" * 40)
        tampered = json.loads(manifest_path.read_text(encoding="utf-8"))
        tampered["source_revision"] = "b" * 40
        manifest_path.write_text(json.dumps(tampered), encoding="utf-8")
        try:
            validate_archive_manifest(manifest_path, "0.1.0", "a" * 40)
        except ProvenanceError:
            pass
        else:
            raise AssertionError("archive source revision drift was accepted")
    finally:
        rmtree(directory)

    print("RELEASE PROVENANCE TESTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
