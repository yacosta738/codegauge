#!/usr/bin/env python3
"""Static and executable invariants for CodeGauge distribution artifacts.

This check intentionally has no third-party Python dependencies.  It is used by
the local quality gate and by CI before any registry publisher is eligible.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - the pinned runner is modern Python
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
VERSION = tomllib.loads((ROOT / "Cargo.toml").read_text(encoding="utf-8"))["workspace"]["package"]["version"] if tomllib else ""
REPOSITORY = "https://github.com/yacosta738/codegauge"
RUNTIME_CRATES = (
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-cli",
)
TARGETS = {
    "x86_64-unknown-linux-gnu": "tar.gz",
    "aarch64-unknown-linux-gnu": "tar.gz",
    "x86_64-unknown-linux-musl": "tar.gz",
    "aarch64-unknown-linux-musl": "tar.gz",
    "x86_64-apple-darwin": "tar.gz",
    "aarch64-apple-darwin": "tar.gz",
    "x86_64-pc-windows-msvc": "zip",
    "aarch64-pc-windows-msvc": "zip",
}
NPM_PACKAGES = {
    "@yacosta738/codegauge-linux-x64-gnu": ("linux", "x64"),
    "@yacosta738/codegauge-linux-arm64-gnu": ("linux", "arm64"),
    "@yacosta738/codegauge-darwin-x64": ("darwin", "x64"),
    "@yacosta738/codegauge-darwin-arm64": ("darwin", "arm64"),
    "@yacosta738/codegauge-win32-x64-msvc": ("win32", "x64"),
    "@yacosta738/codegauge-win32-arm64-msvc": ("win32", "arm64"),
}
ACTION_REF = re.compile(r"^[^@\s]+@[0-9a-f]{40}(?:\s+#.*)?$")
RELEASE_INPUTS = ("release_tag", "release_sha", "main_sha", "release_url", "dry_run")


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_toml(path: Path, errors: list[str]) -> dict[str, Any]:
    if tomllib is None:
        errors.append("Python tomllib is required for distribution checks")
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        errors.append(f"invalid TOML in {relative(path)}: {error}")
        return {}


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid JSON in {relative(path)}: {error}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{relative(path)} must contain a JSON object")
        return {}
    return value


def require_text(path: Path, fragments: tuple[str, ...], errors: list[str]) -> str:
    if not path.is_file():
        errors.append(f"missing {relative(path)}")
        return ""
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        if fragment not in text:
            errors.append(f"{relative(path)} is missing {fragment!r}")
    return text


def check_cargo(errors: list[str]) -> None:
    manifest_path = ROOT / "Cargo.toml"
    manifest = load_toml(manifest_path, errors)
    workspace = manifest.get("workspace", {})
    package_defaults = manifest.get("workspace", {}).get("package", {})
    expected_members = [f"crates/{name}" for name in (*RUNTIME_CRATES, "codegauge-conformance")]
    if workspace.get("members") != expected_members:
        errors.append("Cargo workspace members changed or are not in the approved order")
    if workspace.get("resolver") != "3":
        errors.append("Cargo workspace resolver must remain 3")
    if package_defaults.get("version") != VERSION:
        errors.append("workspace.package.version must be the synchronized release version")
    if package_defaults.get("repository") != REPOSITORY:
        errors.append("workspace.package.repository must identify the approved repository")
    if package_defaults.get("license") != "MIT":
        errors.append("workspace.package.license must be declared for crates.io publication")
    if package_defaults.get("readme") != "README.md":
        errors.append("workspace.package.readme must point to the public README")
    if package_defaults.get("rust-version") != "1.97.1":
        errors.append("workspace.package.rust-version must pin Rust 1.97.1")
    if not (ROOT / "LICENSE").is_file():
        errors.append("LICENSE is required before a crates.io package can be published")

    for name in (*RUNTIME_CRATES, "codegauge-conformance"):
        path = ROOT / "crates" / name / "Cargo.toml"
        data = load_toml(path, errors)
        package = data.get("package", {})
        if package.get("name") != name:
            errors.append(f"{relative(path)} has an unexpected package name")
        if package.get("version") != {"workspace": True}:
            errors.append(f"{relative(path)} must inherit workspace version")
        if package.get("edition") != {"workspace": True}:
            errors.append(f"{relative(path)} must inherit workspace edition")
        if package.get("rust-version") != {"workspace": True}:
            errors.append(f"{relative(path)} must inherit workspace rust-version")
        if package.get("license") != {"workspace": True}:
            errors.append(f"{relative(path)} must inherit workspace license")
        if package.get("repository") != {"workspace": True}:
            errors.append(f"{relative(path)} must inherit workspace repository")
        if name in RUNTIME_CRATES and package.get("publish") is False:
            errors.append(f"runtime crate {name} is still marked publish=false")
        if name == "codegauge-conformance" and package.get("publish") is not False:
            errors.append("conformance crate must remain private")
        if not package.get("description"):
            errors.append(f"{relative(path)} needs a crates.io description")
        if name in RUNTIME_CRATES and package.get("readme") != {"workspace": True}:
            errors.append(f"{relative(path)} must inherit the public README")

    app_source = ROOT / "crates" / "codegauge-application" / "src" / "lib.rs"
    source = require_text(app_source, ('env!("CARGO_PKG_VERSION")',), errors)
    if f'TOOL_VERSION:&str="{VERSION}"' in source or f'TOOL_VERSION: &str = "{VERSION}"' in source:
        errors.append("TOOL_VERSION must not be a second hard-coded release version")

    lock_text = require_text(ROOT / "Cargo.lock", tuple(f'name = "{name}"' for name in RUNTIME_CRATES), errors)
    for name in RUNTIME_CRATES:
        package_match = re.search(
            rf'name = "{re.escape(name)}"\s+version = "([^"]+)"', lock_text
        )
        if not package_match or package_match.group(1) != VERSION:
            errors.append(f"Cargo.lock does not carry version {VERSION} for {name}")


def check_workflows(errors: list[str]) -> None:
    ci = require_text(
        ROOT / ".github" / "workflows" / "ci.yml",
        (
            "cargo metadata --locked",
            "cargo test --workspace --locked",
            "cargo fmt --all -- --check",
            "cargo clippy --workspace --all-targets --locked -- -D warnings",
            "python3 tests/bootstrap_checks.py",
            "python3 tests/readme_checks.py",
            "permissions:\n  contents: read",
        ),
        errors,
    )
    release_build = require_text(
        ROOT / ".github" / "workflows" / "release-build.yml",
        (
            "x86_64-unknown-linux-gnu",
            "aarch64-unknown-linux-gnu",
            "x86_64-unknown-linux-musl",
            "aarch64-unknown-linux-musl",
            "x86_64-apple-darwin",
            "aarch64-apple-darwin",
            "x86_64-pc-windows-msvc",
            "aarch64-pc-windows-msvc",
            "sha256",
            "source_revision",
            "--locked",
            "ref: ${{ inputs.release_sha }}",
            "workflow_call:",
            "release_sha:",
            "main_sha:",
            "release_url:",
            "release-preflight:",
            "scripts/verify_release_provenance.py",
            "verify_release_provenance.py binary",
            "python3 tests/oci_distribution_tests.py",
            "codegauge version",
            "codegauge profiles",
            '--mode "${{ matrix.evidence_mode }}"',
            "binary-evidence",
            "npm pack --dry-run",
            "oci-preflight:",
            "bash scripts/build_oci_release.sh",
            "oci-build-evidence-",
        ),
        errors,
    )
    oci_builder = require_text(
        ROOT / "scripts" / "build_oci_release.sh",
        (
            "linux/amd64",
            "linux/arm64",
            "docker buildx build",
            "--output=type=oci,dest=",
            "--output=type=docker,dest=",
            "docker load --input",
            "docker image inspect --platform",
            "scripts/verify_oci_evidence.py",
            "--oci-archive",
            '--docker-archive "$DOCKER_ARCHIVE"',
            "--metadata-json",
            "--runtime-mode",
            "--non-root-output",
            "--contract-output",
            "--profiles-output",
            "docker run --rm",
        ),
        errors,
    )
    release_publish = require_text(
        ROOT / ".github" / "workflows" / "release-publish.yml",
        (
            "cargo publish",
            "npm publish",
            "ghcr.io/yacosta738/codegauge",
            "docker buildx imagetools inspect",
            "dry_run",
            "release_tag",
            "release_sha:",
            "main_sha:",
            "release_url:",
            "gh release upload",
            "--clobber",
            "attestations: write",
            "id-token: write",
            "packages: write",
            "actions/download-artifact@",
            "docker load --input",
            "published_digest",
            "published_config_digest",
            "docker buildx imagetools inspect --raw",
            "FINAL_RAW",
            "LATEST_DIGEST",
            "actions/attest@",
            "oci-evidence/",
            "workflow_call:",
        ),
        errors,
    )
    caller = require_text(
        ROOT / ".github" / "workflows" / "release.yml",
        ("workflow_call:", "workflow_dispatch:", *RELEASE_INPUTS),
        errors,
    )
    release_please = require_text(
        ROOT / ".github" / "workflows" / "release-please.yml",
        ("release-please-action", "contents: write", "pull-requests: write", "issues: write"),
        errors,
    )
    release = f"{release_build}\n{release_publish}\n{oci_builder}"
    for workflow_name in ("release-build", "release-publish"):
        invocation = re.search(
            rf"^  {workflow_name}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
            caller,
            re.MULTILINE | re.DOTALL,
        )
        if not invocation:
            errors.append(f"release caller is missing the {workflow_name} reusable-workflow job")
            continue
        body = invocation.group("body")
        for input_name in RELEASE_INPUTS:
            expression = f"{input_name}: ${{{{ inputs.{input_name} }}}}"
            if expression not in body:
                errors.append(f"release caller must pass {input_name} to {workflow_name}")
    if "needs: release-build" not in caller:
        errors.append("release-publish caller job must wait for the completed release-build workflow")
    if re.search(r"^\s+push:\s*$", caller, re.MULTILINE):
        errors.append("release publication must not be triggered by arbitrary pushed tags")
    if "gh release create" in release:
        errors.append("release-please must remain the only GitHub Release creator")
    if "gh release upload" not in release or "--clobber" not in release:
        errors.append("release assets must upload to the existing release with --clobber")
    if "inputs.release_tag ||" in release or "github.ref_name" in release:
        errors.append("release workflow must not fall back to an unsafe manual/default ref")
    if "uses: ./.github/workflows/release.yml" not in release_please:
        errors.append("release-please must call the release caller workflow")
    if "steps.release.outputs" not in release_please:
        errors.append("release-please outputs must be retained as release workflow inputs")
    if "--no-verify" in release:
        errors.append("release workflow must not weaken Cargo package verification with --no-verify")
    if "cargo package --locked" not in release:
        errors.append("release workflow must validate Cargo package contents with locked inputs")
    if "cargo publish -p codegauge-model --locked" not in release:
        errors.append("release workflow must publish Cargo crates with locked inputs")
    if not re.search(r"needs:\s+publish-cargo-model", release) or not re.search(r"needs:\s+publish-cargo-core", release):
        errors.append("Cargo publishers must form an explicit dependency-order chain")
    if not re.search(r"needs:\s+publish-npm", release) or not re.search(r"needs:\s+publish-release", release):
        errors.append("OCI publication must be gated after npm and GitHub Release publication")
    if "--workspace npm/packages/codegauge" in release:
        errors.append("npm publication must use explicit package paths to preserve platform ordering")
    if "secrets.NPM_TOKEN" in release and "NODE_AUTH_TOKEN" not in release:
        errors.append("npm credential wiring must be explicit and job-scoped")

    def job_block(workflow: str, job_name: str) -> str:
        match = re.search(
            rf"^  {re.escape(job_name)}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
            workflow,
            re.MULTILINE | re.DOTALL,
        )
        if not match:
            errors.append(f"release workflow is missing the {job_name} job")
            return ""
        return match.group("body")

    for job_name in ("npm-preflight", "publish-npm"):
        workflow = release_build if job_name == "npm-preflight" else release_publish
        block = job_block(workflow, job_name)
        if "ref: ${{ inputs.release_sha }}" not in block:
            errors.append(f"{job_name} must checkout the exact verified release SHA")
        if "fetch-depth: 0" not in block:
            errors.append(f"{job_name} must use a complete immutable-SHA checkout for tag verification")
        if 'git rev-parse "${RELEASE_TAG}^{commit}"' not in block:
            errors.append(f"{job_name} must verify that the checkout is the requested release tag")
        if "node npm/codegauge/dist/preflight.js" not in block:
            errors.append(f"{job_name} must run the typed npm publication preflight")
        if "--source-revision \"${SOURCE_REVISION}\"" not in block:
            errors.append(f"{job_name} must validate npm source-revision provenance")
    for job_name in ("archives", "cargo-preflight", "npm-preflight", "release-verify"):
        block = job_block(release_build, job_name)
        if "release-preflight" not in block:
            errors.append(f"{job_name} must remain downstream of release-preflight")
    for job_name in (
        "publish-cargo-model",
        "publish-cargo-core",
        "publish-cargo-application",
        "publish-cargo-provider",
        "publish-cargo-cli",
        "publish-release",
        "publish-npm",
        "publish-oci",
    ):
        block = job_block(release_publish, job_name)
        if "if: inputs.dry_run == false" not in block:
            errors.append(f"{job_name} must remain disabled for dry-run releases")
        if "release-preflight" in block:
            errors.append(f"{job_name} must use the release-build caller gate, not a cross-workflow need")
    if len(release_build.splitlines()) > 400:
        errors.append("release-build.yml exceeds the 400-line review target")
    if len(release_publish.splitlines()) > 400:
        errors.append("release-publish.yml exceeds the 400-line review target")
    for path, text in (
        (ROOT / ".github" / "workflows" / "ci.yml", ci),
        (ROOT / ".github" / "workflows" / "release.yml", caller),
        (ROOT / ".github" / "workflows" / "release-build.yml", release_build),
        (ROOT / ".github" / "workflows" / "release-publish.yml", release_publish),
        (ROOT / ".github" / "workflows" / "release-please.yml", release_please),
    ):
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("- uses:"):
                reference = stripped.removeprefix("- uses:").strip()
            elif stripped.startswith("uses:"):
                reference = stripped.removeprefix("uses:").strip()
            else:
                continue
            if reference.startswith("./"):
                continue
            if not ACTION_REF.match(reference):
                errors.append(f"{relative(path)} has a mutable or malformed action reference: {reference}")

    publish_release = job_block(release_publish, "publish-release")
    permission_match = re.search(
        r"^    permissions:\n(?P<body>(?:      [^\n]*\n)+)",
        publish_release,
        re.MULTILINE,
    )
    if not permission_match or "      id-token: write" not in permission_match.group("body"):
        errors.append("publish-release must grant id-token: write for build provenance attestation")
    if "contents: write" in ci or "packages: write" in ci or "id-token: write" in ci:
        errors.append("pull-request CI must not grant release permissions")

    target_occurrences = {target: len(re.findall(re.escape(target), release)) for target in TARGETS}
    missing_targets = [target for target, count in target_occurrences.items() if count == 0]
    if missing_targets:
        errors.append(f"release workflow is missing target declarations: {', '.join(missing_targets)}")
    if "cargo publish -p codegauge-model" not in release:
        errors.append("Cargo publication must begin with the leaf model crate")
    ordered = [release.find(f"cargo publish -p {name}") for name in RUNTIME_CRATES]
    if any(index < 0 for index in ordered) or ordered != sorted(ordered):
        errors.append("Cargo publication commands must follow dependency order")
    platform_indices = [
        release_publish.find(f"npm/packages/{name.removeprefix('@yacosta738/')}")
        for name in NPM_PACKAGES
    ]
    if any(index < 0 for index in platform_indices):
        errors.append("release workflow must publish every npm platform package")
    wrapper_index = release_publish.find("(cd npm/codegauge && npm publish")
    if wrapper_index < 0 or wrapper_index < max(platform_indices, default=-1):
        errors.append("npm platform packages must publish before the base wrapper")


def check_npm(errors: list[str]) -> None:
    base_path = ROOT / "npm" / "codegauge" / "package.json"
    base = load_json(base_path, errors)
    if base.get("name") != "@yacosta738/codegauge":
        errors.append("npm base package name is not approved")
    if base.get("version") != VERSION:
        errors.append("npm base package version is not synchronized")
    optional = base.get("optionalDependencies", {})
    if set(optional) != set(NPM_PACKAGES):
        errors.append("npm optionalDependencies must contain exactly the six GNU platform packages")
    if any(value != VERSION for value in optional.values()):
        errors.append("npm optional dependency versions must be exact synchronized pins")
    if any("musl" in name for name in optional):
        errors.append("npm must not claim musl platform packages")

    release_config = load_json(ROOT / "release-please-config.json", errors)
    release_manifest = load_json(ROOT / ".release-please-manifest.json", errors)
    linked_components = {
        component
        for plugin in release_config.get("plugins", [])
        if isinstance(plugin, dict) and plugin.get("type") == "linked-versions"
        for component in plugin.get("components", [])
    }
    expected_components = {name.removeprefix("@yacosta738/") for name in NPM_PACKAGES} | {
        "codegauge",
        *RUNTIME_CRATES,
    }
    if linked_components != expected_components:
        errors.append("release-please linked versions must include Cargo, base npm, and all six platform components")
    expected_manifest_paths = {
        "crates/codegauge-model",
        "crates/codegauge-core",
        "crates/codegauge-application",
        "crates/codegauge-provider-jacoco",
        "crates/codegauge-cli",
        "npm/codegauge",
        *(f"npm/packages/{name.removeprefix('@yacosta738/')}" for name in NPM_PACKAGES),
    }
    if set(release_manifest) != expected_manifest_paths:
        errors.append("release-please manifest must enumerate all Cargo/npm release components")
    if any(value != VERSION for value in release_manifest.values()):
        errors.append("release-please manifest versions must match the synchronized release version")

    package_template = require_text(
        ROOT / "npm" / "package.json.tmpl",
        ("__PACKAGE_NAME__", "__VERSION__", '"os"', '"cpu"', "__BINARY__"),
        errors,
    )
    for name, (os_name, cpu) in NPM_PACKAGES.items():
        path = ROOT / "npm" / "packages" / name.removeprefix("@yacosta738/") / "package.json"
        package = load_json(path, errors)
        if package.get("name") != name or package.get("version") != VERSION:
            errors.append(f"{relative(path)} has an unexpected name or version")
        if package.get("os") != [os_name] or package.get("cpu") != [cpu]:
            errors.append(f"{relative(path)} has incorrect os/cpu constraints")
        if package.get("bin", {}).get("codegauge") != "bin/codegauge" and os_name != "win32":
            errors.append(f"{relative(path)} must expose bin/codegauge")
        if not package.get("files"):
            errors.append(f"{relative(path)} must constrain published files")
        if os_name == "win32" and package.get("bin", {}).get("codegauge") != "bin/codegauge.exe":
            errors.append(f"{relative(path)} must expose the Windows executable")

    wrapper = require_text(
        ROOT / "npm" / "codegauge" / "src" / "index.ts",
        (
            "process.platform",
            "process.arch",
            "process.argv.slice(2)",
            "spawnSync",
            'stdio: "inherit"',
            "process.exitCode",
            "glibcVersionRuntime",
            "require.resolve",
        ),
        errors,
    )
    preflight = require_text(
        ROOT / "npm" / "codegauge" / "src" / "preflight.ts",
        (
            "checkNpmPublicationEligibility",
            "verifySha256Sidecar",
            "platformEligible",
            "baseEligible",
            "sourceRevision",
        ),
        errors,
    )
    npm_tests = require_text(
        ROOT / "npm" / "codegauge" / "test" / "index.test.mjs",
        ("wrapper source declares exact target resolution",),
        errors,
    )
    if "codegauge-linux-x64-gnu" not in wrapper or "codegauge-linux-arm64-gnu" not in wrapper:
        errors.append("wrapper target map is missing approved Linux GNU packages")
    if "musl" not in wrapper:
        errors.append("wrapper must explicitly reject musl Linux runtimes")
    if "package.json" not in package_template:
        errors.append("platform template must be package metadata, not an arbitrary archive")
    if not preflight or not npm_tests:
        errors.append("npm checksum publication regression coverage is missing")


def check_release_assets(errors: list[str]) -> None:
    script = ROOT / "scripts" / "package_release.py"
    text = require_text(
        script,
        (
            "tar.gz",
            "zip",
            "source_revision",
            "rust_toolchain",
            "sha256",
            "release-manifest-",
            "lower()",
            "0o755",
            "binary_evidence",
        ),
        errors,
    )
    release_path = ROOT / ".github" / "workflows" / "release.yml"
    build_path = ROOT / ".github" / "workflows" / "release-build.yml"
    publish_path = ROOT / ".github" / "workflows" / "release-publish.yml"
    release_workflow = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (release_path, build_path, publish_path)
        if path.is_file()
    )
    for target, extension in TARGETS.items():
        archive = f"codegauge-{VERSION}-{target}.{extension}"
        if archive not in text:
            # The script may construct the name from its arguments; the workflow still
            # has to carry the exact target and format declaration.
            if target not in release_workflow or extension not in release_workflow:
                errors.append(f"no archive naming evidence for {target}")
    if "sha256sum --check" not in release_workflow:
        errors.append("release workflow must verify SHA-256 sidecars before extraction/upload")

    if not script.is_file() or not text:
        return
    with tempfile.TemporaryDirectory(prefix="codegauge-distribution-") as directory:
        root = Path(directory)
        binary = root / "codegauge"
        evidence = root / "binary-evidence.json"
        binary.write_bytes(b"#!/bin/sh\nexit 0\n")
        binary.chmod(0o755)
        evidence.write_text(
            json.dumps(
                {
                    "mode": "cross-target",
                    "target": "x86_64-unknown-linux-gnu",
                    "execution": "not-run",
                }
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--binary",
                str(binary),
                "--target",
                "x86_64-unknown-linux-gnu",
                "--version",
                VERSION,
                "--revision",
                "a" * 40,
                "--rust-toolchain",
                "1.97.1",
                "--binary-evidence",
                str(evidence),
                "--output-dir",
                str(root / "out"),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append(f"package_release.py smoke check failed: {result.stderr.strip()}")
            return
        sidecar = root / "out" / f"codegauge-{VERSION}-x86_64-unknown-linux-gnu.tar.gz.sha256"
        if not sidecar.is_file():
            errors.append("package_release.py did not create a SHA-256 sidecar")
            return
        digest, filename = sidecar.read_text(encoding="utf-8").strip().split(maxsplit=1)
        archive = root / "out" / filename
        actual = hashlib.sha256(archive.read_bytes()).hexdigest()
        if digest != digest.lower() or digest != actual:
            errors.append("package_release.py emitted an invalid lowercase SHA-256 sidecar")

        invalid_version = subprocess.run(
            [
                sys.executable,
                str(script),
                "--binary",
                str(binary),
                "--target",
                "x86_64-unknown-linux-gnu",
                "--version",
                "not-a-release-version",
                "--revision",
                "a" * 40,
                "--rust-toolchain",
                "1.97.1",
                "--binary-evidence",
                str(evidence),
                "--output-dir",
                str(root / "invalid-version-out"),
            ],
            capture_output=True,
            text=True,
        )
        if invalid_version.returncode == 0:
            errors.append("package_release.py accepted an invalid synchronized release version")

        windows_binary = root / "codegauge.exe"
        windows_evidence = root / "windows-binary-evidence.json"
        windows_binary.write_bytes(b"MZ")
        windows_evidence.write_text(
            json.dumps(
                {
                    "mode": "cross-target",
                    "target": "x86_64-pc-windows-msvc",
                    "execution": "not-run",
                }
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--binary",
                str(windows_binary),
                "--target",
                "x86_64-pc-windows-msvc",
                "--version",
                VERSION,
                "--revision",
                "a" * 40,
                "--rust-toolchain",
                "1.97.1",
                "--binary-evidence",
                str(windows_evidence),
                "--output-dir",
                str(root / "windows-out"),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            errors.append(f"package_release.py rejected a Windows binary without Unix mode bits: {result.stderr.strip()}")


def check_oci_and_docs(errors: list[str]) -> None:
    dockerfile = require_text(
        ROOT / "Dockerfile",
        (
            "rust:1.97.1-alpine",
            "cargo build --release --locked --package codegauge-cli --bin codegauge",
            "COPY crates",
            "tini",
            "USER codegauge",
            "org.opencontainers.image.version",
            "org.opencontainers.image.revision",
        ),
        errors,
    )
    dockerignore = require_text(ROOT / ".dockerignore", ("target", "node_modules", ".git", ".atl"), errors)
    if "COPY src" in dockerfile and "COPY crates" not in dockerfile:
        errors.append("Dockerfile must copy the complete workspace, not assume a root src layout")
    release_path = ROOT / ".github" / "workflows" / "release.yml"
    release_workflow = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            ROOT / ".github" / "workflows" / "release.yml",
            ROOT / ".github" / "workflows" / "release-build.yml",
            ROOT / ".github" / "workflows" / "release-publish.yml",
        )
        if path.is_file()
    )
    if "ghcr.io/yacosta738/codegauge" not in release_workflow:
        errors.append("OCI publisher must use the approved GHCR identity")
    oci_test = ROOT / "tests" / "oci_distribution_tests.py"
    if not oci_test.is_file():
        errors.append("OCI publication requires focused local evidence tests")
    readme = require_text(
        ROOT / "README.md",
        (
            "@yacosta738/codegauge",
            "ghcr.io/yacosta738/codegauge",
            "codegauge-cli",
            "x86_64-unknown-linux-gnu",
            "aarch64-unknown-linux-musl",
            "source_revision",
            "rollback",
            "npm platform packages",
        ),
        errors,
    )
    if not dockerignore:
        errors.append(".dockerignore must be checked in for the workspace image")
    if not readme:
        errors.append("README distribution guidance is missing")


def main() -> int:
    errors: list[str] = []
    check_cargo(errors)
    check_workflows(errors)
    check_npm(errors)
    check_release_assets(errors)
    check_oci_and_docs(errors)
    if errors:
        print("DISTRIBUTION CHECKS: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DISTRIBUTION CHECKS: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
