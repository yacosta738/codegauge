"""Focused E3a distribution checks shared by the executable runner.

This layer covers source/package provenance and the workflow topology that must
exist before later npm, archive, and OCI checks are enabled.
"""

from __future__ import annotations

import re
import json
import tomllib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/yacosta738/codegauge"
RUNTIME_CRATES = (
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-cli",
)
ALL_CRATES = (*RUNTIME_CRATES, "codegauge-conformance")
RELEASE_INPUTS = ("release_tag", "release_sha", "main_sha", "release_url", "dry_run", "recovery")
ACTION_REF = re.compile(r"^[^@\s]+@[0-9a-f]{40}(?:\s+#.*)?$")
EXPECTED_GRAPH = {
    "codegauge-model": (),
    "codegauge-core": ("codegauge-model",),
    "codegauge-application": ("codegauge-core", "codegauge-model"),
    "codegauge-provider-jacoco": ("codegauge-application", "codegauge-model"),
    "codegauge-cli": (
        "codegauge-application",
        "codegauge-model",
        "codegauge-provider-jacoco",
    ),
    "codegauge-conformance": (
        "codegauge-application",
        "codegauge-core",
        "codegauge-model",
        "codegauge-provider-jacoco",
    ),
}


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"missing or unreadable {relative(path)}: {error}")
        return ""


def load_toml(path: Path, errors: list[str]) -> dict[str, Any]:
    text = read_text(path, errors)
    if not text:
        return {}
    try:
        value = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        errors.append(f"invalid TOML in {relative(path)}: {error}")
        return {}
    return value if isinstance(value, dict) else {}


def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    text = read_text(path, errors)
    if not text:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        errors.append(f"invalid JSON in {relative(path)}: {error}")
        return {}
    return value if isinstance(value, dict) else {}


def require_fragments(path: Path, fragments: tuple[str, ...], errors: list[str]) -> str:
    text = read_text(path, errors)
    for fragment in fragments:
        if text and fragment not in text:
            errors.append(f"{relative(path)} is missing {fragment!r}")
    return text


def check_cargo(errors: list[str]) -> None:
    manifest = load_toml(ROOT / "Cargo.toml", errors)
    workspace = manifest.get("workspace", {})
    defaults = workspace.get("package", {})
    version = defaults.get("version")
    expected_members = [f"crates/{name}" for name in ALL_CRATES]

    if workspace.get("members") != expected_members:
        errors.append("Cargo workspace members changed or are not in the approved order")
    if workspace.get("resolver") != "3":
        errors.append("Cargo workspace resolver must remain 3")
    for key, expected in {
        "version": version,
        "edition": "2024",
        "rust-version": "1.97.1",
        "license": "MIT",
        "repository": REPOSITORY,
        "readme": "README.md",
    }.items():
        if defaults.get(key) != expected:
            errors.append(f"workspace.package.{key} is not synchronized to {expected!r}")

    license_text = require_fragments(
        ROOT / "LICENSE",
        ("MIT License", "Permission is hereby granted", "WITHOUT WARRANTY"),
        errors,
    )
    if not license_text:
        errors.append("LICENSE is required for publishable Cargo packages")

    for name in ALL_CRATES:
        path = ROOT / "crates" / name / "Cargo.toml"
        package = load_toml(path, errors).get("package", {})
        if package.get("name") != name:
            errors.append(f"{relative(path)} has an unexpected package name")
        for key in ("edition", "rust-version", "license", "repository", "readme"):
            if package.get(key) != {"workspace": True}:
                errors.append(f"{relative(path)} must inherit workspace {key}")
        if package.get("version") != version:
            errors.append(
                f"{relative(path)} must declare package.version equal to the workspace version for Release Please"
            )
        if not package.get("description"):
            errors.append(f"{relative(path)} needs package description metadata")
        if name in RUNTIME_CRATES and package.get("publish") is False:
            errors.append(f"runtime crate {name} must remain publishable")
        if name == "codegauge-conformance" and package.get("publish") is not False:
            errors.append("codegauge-conformance must remain private")

    source = require_fragments(
        ROOT / "crates" / "codegauge-application" / "src" / "lib.rs",
        ('env!("CARGO_PKG_VERSION")',),
        errors,
    )
    if re.search(r"TOOL_VERSION\s*:\s*&str\s*=\s*[\"']", source):
        errors.append("TOOL_VERSION must not duplicate a hard-coded release version")

    lock = load_toml(ROOT / "Cargo.lock", errors)
    if lock.get("version") != 4:
        errors.append("Cargo.lock must use lockfile format version 4")
    packages = {
        package.get("name"): package
        for package in lock.get("package", [])
        if isinstance(package, dict) and package.get("name")
    }
    if "codegauge" in packages:
        errors.append("the virtual workspace root must not become a Cargo package")
    for name, dependencies in EXPECTED_GRAPH.items():
        package = packages.get(name)
        if not package:
            errors.append(f"Cargo.lock is missing workspace package {name}")
            continue
        if package.get("version") != version:
            errors.append(f"Cargo.lock version drifted for {name}")
        actual = set(package.get("dependencies", []))
        missing = [dependency for dependency in dependencies if dependency not in actual]
        if missing:
            errors.append(f"Cargo.lock graph for {name} is missing {', '.join(missing)}")

    release_config = load_json(ROOT / "release-please-config.json", errors)
    if "extra-files" in release_config:
        errors.append("release-please root extra-files must be package-owned")
    root_package = release_config.get("packages", {}).get(".", {})
    extra_files = root_package.get("extra-files", [])
    if not any(
        isinstance(extra_file, dict)
        and extra_file.get("type") == "toml"
        and extra_file.get("path") == "/Cargo.toml"
        and extra_file.get("jsonpath") == "$.workspace.package.version"
        for extra_file in extra_files
    ):
        errors.append(
            "release-please must update the canonical workspace Cargo version"
        )
    if root_package.get("release-type") == "rust":
        errors.append("the virtual Cargo root must use a non-Cargo release candidate")
    if root_package.get("skip-github-release") is not True or "package-name" in root_package:
        errors.append("the root release candidate must be a non-publishable metadata carrier")
    if release_config.get("skip-github-release") is not True:
        errors.append("non-canonical release components must skip GitHub releases")
    if release_config.get("include-component-in-tag") is not True:
        errors.append("Stage A must enable component-tagged linked version lookup")
    if any(
        isinstance(plugin, dict) and plugin.get("type") == "cargo-workspace"
        for plugin in release_config.get("plugins", [])
    ):
        errors.append(
            "Stage A must not use cargo-workspace discovery because it scans private members"
        )
    if not any(
        isinstance(extra_file, dict)
        and extra_file.get("type") == "toml"
        and extra_file.get("path") == "/Cargo.lock"
        for extra_file in extra_files
    ):
        errors.append(
            "Stage A root carrier must update approved runtime Cargo.lock entries explicitly"
        )
    if release_config.get("packages", {}).get("crates/codegauge-cli", {}).get("skip-github-release", True) is not True:
        errors.append("Stage A must suppress the CLI component release")


def workflow_section(text: str, heading: str, next_heading: str | None = None) -> str:
    match = re.search(rf"^  {re.escape(heading)}:\s*$", text, re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    if next_heading:
        end_match = re.search(rf"^  {re.escape(next_heading)}:\s*$", text[start:], re.MULTILINE)
        end = start + end_match.start() if end_match else len(text)
    else:
        end_match = re.search(r"^  [A-Za-z0-9_-]+:\s*$", text[start:], re.MULTILINE)
        end = start + end_match.start() if end_match else len(text)
    return text[start:end]


def workflow_input_names(text: str, heading: str) -> set[str]:
    section = workflow_section(text, heading)
    inputs = re.search(r"^    inputs:\s*$", section, re.MULTILINE)
    if not inputs:
        return set()
    body = section[inputs.end() :]
    end = re.search(r"^    [A-Za-z0-9_-]+:\s*$", body, re.MULTILINE)
    if end:
        body = body[: end.start()]
    return set(re.findall(r"^      ([A-Za-z0-9_-]+):\s*$", body, re.MULTILINE))


def job_block(workflow: str, name: str) -> str:
    match = re.search(
        rf"^  {re.escape(name)}:\s*$\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\s*$|\Z)",
        workflow,
        re.MULTILINE | re.DOTALL,
    )
    return match.group("body") if match else ""


def check_ci(errors: list[str]) -> None:
    path = ROOT / ".github" / "workflows" / "ci.yml"
    ci = require_fragments(
        path,
        (
            "pull_request:",
            "push:\n    branches: [main]",
            "permissions:\n  contents: read",
            "rustup toolchain install 1.97.1",
            "cargo metadata --locked",
            "cargo test --workspace --locked",
            "cargo fmt --all -- --check",
            "cargo clippy --workspace --all-targets --locked -- -D warnings",
            "python3 tests/bootstrap_checks.py",
            "python3 tests/readme_checks.py",
        ),
        errors,
    )
    if any(permission in ci for permission in ("contents: write", "packages: write", "id-token: write")):
        errors.append("baseline CI must not receive release write permissions")
    if "secrets." in ci:
        errors.append("baseline CI must not consume release secrets")
    for line in ci.splitlines():
        stripped = line.strip()
        if stripped.startswith("- uses:") or stripped.startswith("uses:"):
            reference = stripped.split(":", 1)[1].strip()
            if not ACTION_REF.match(reference):
                errors.append(f"{relative(path)} has a mutable or malformed action reference: {reference}")


def check_release_topology(errors: list[str]) -> None:
    workflow_dir = ROOT / ".github" / "workflows"
    caller_path = workflow_dir / "release.yml"
    caller = require_fragments(
        caller_path,
        ("workflow_call:", "workflow_dispatch:", "uses: ./.github/workflows/release-build.yml", "uses: ./.github/workflows/release-publish.yml"),
        errors,
    )
    if re.search(r"^  push:\s*$", caller, re.MULTILINE):
        errors.append("release caller must not publish from an arbitrary push or tag")
    for heading in ("workflow_call", "workflow_dispatch"):
        if workflow_input_names(caller, heading) != set(RELEASE_INPUTS):
            errors.append(f"release caller {heading} inputs are incomplete or unexpected")

    build = require_fragments(workflow_dir / "release-build.yml", ("workflow_call:",), errors)
    publish = require_fragments(workflow_dir / "release-publish.yml", ("workflow_call:",), errors)
    for name, workflow in (("release-build", build), ("release-publish", publish)):
        if workflow_input_names(workflow, "workflow_call") != set(RELEASE_INPUTS):
            errors.append(f"{name} reusable workflow inputs are incomplete or unexpected")

    build_job = job_block(caller, "release-build")
    publish_job = job_block(caller, "release-publish")
    if "uses: ./.github/workflows/release-build.yml" not in build_job:
        errors.append("release caller must invoke the release-build reusable workflow")
    if "uses: ./.github/workflows/release-publish.yml" not in publish_job:
        errors.append("release caller must invoke the release-publish reusable workflow")
    if "needs: release-build" not in publish_job:
        errors.append("release-publish must wait for release-build")
    for job_name, block in (("release-build", build_job), ("release-publish", publish_job)):
        for input_name in RELEASE_INPUTS:
            expression = f"{input_name}: ${{{{ inputs.{input_name} }}}}"
            if expression not in block:
                errors.append(f"release caller must propagate {input_name} to {job_name}")
    if "cargo publish" in caller or "npm publish" in caller or "gh release upload" in caller:
        errors.append("release caller must contain topology only, not publisher commands")

    release_please = require_fragments(
        workflow_dir / "release-please.yml",
        ("skip-github-release: true", "config-file: release-please-config.json", "manifest-file: .release-please-manifest.json"),
        errors,
    )
    if "uses: ./.github/workflows/release.yml" in release_please or "release_created" in release_please:
        errors.append("Stage A must not couple Release Please to publication outputs")
    tag_caller = require_fragments(
        workflow_dir / "release-on-tag.yml",
        ("tags: [\"v*.*.*\"]", "workflow_dispatch:", "uses: ./.github/workflows/release.yml", "secrets: inherit"),
        errors,
    )
    if "github.ref_name" not in tag_caller or "github.sha" not in tag_caller:
        errors.append("canonical tag caller must pass the tag and commit event values")


def run_checks() -> list[str]:
    errors: list[str] = []
    check_cargo(errors)
    check_ci(errors)
    check_release_topology(errors)
    return errors
