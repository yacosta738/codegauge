#!/usr/bin/env python3
"""Red/green checks for the independent CodeGauge workspace boundary."""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - the pinned workspace uses modern tooling
    tomllib = None


ROOT = Path(__file__).resolve().parents[1]
CRATES = {
    "codegauge-model": set(),
    "codegauge-core": {"codegauge-model"},
    "codegauge-application": {"codegauge-model", "codegauge-core"},
    "codegauge-provider-jacoco": {"codegauge-model", "codegauge-application"},
    "codegauge-provider-typescript": {"codegauge-model", "codegauge-application"},
    "codegauge-cli": {
        "codegauge-model",
        "codegauge-application",
        "codegauge-provider-jacoco",
        "codegauge-provider-typescript",
    },
    "codegauge-conformance": {
        "codegauge-model",
        "codegauge-core",
        "codegauge-application",
        "codegauge-provider-jacoco",
        "codegauge-provider-typescript",
    },
}


def load_toml(path: Path, errors: list[str]) -> dict:
    if tomllib is None:
        errors.append("Python tomllib is required for manifest checks")
        return {}
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        errors.append(f"invalid TOML in {path.relative_to(ROOT)}: {error}")
        return {}


def main() -> int:
    errors: list[str] = []

    toolchain = ROOT / "rust-toolchain.toml"
    lockfile = ROOT / "Cargo.lock"
    manifest = ROOT / "Cargo.toml"
    if not toolchain.is_file():
        errors.append("missing rust-toolchain.toml")
    elif "1.97.1" not in toolchain.read_text(encoding="utf-8"):
        errors.append("rust-toolchain.toml must pin Rust 1.97.1")
    if not lockfile.is_file():
        errors.append("missing committed Cargo.lock")

    root_manifest = load_toml(manifest, errors) if manifest.is_file() else {}
    if not manifest.is_file():
        errors.append("missing workspace Cargo.toml")
    else:
        workspace = root_manifest.get("workspace", {})
        expected_members = sorted(f"crates/{name}" for name in CRATES)
        actual_members = sorted(workspace.get("members", []))
        if actual_members != expected_members:
            errors.append(f"workspace members must be exactly {expected_members}")
        if workspace.get("resolver") != "3":
            errors.append("workspace resolver must be 3")

    for name, allowed_dependencies in CRATES.items():
        crate_root = ROOT / "crates" / name
        crate_manifest = crate_root / "Cargo.toml"
        source = crate_root / "src" / ("main.rs" if name == "codegauge-cli" else "lib.rs")
        if not crate_manifest.is_file():
            errors.append(f"missing {crate_manifest.relative_to(ROOT)}")
            continue
        if not source.is_file():
            errors.append(f"missing {source.relative_to(ROOT)}")
        data = load_toml(crate_manifest, errors)
        if data.get("package", {}).get("name") != name:
            errors.append(f"{crate_manifest.relative_to(ROOT)} has the wrong package name")
        dependencies = set(data.get("dependencies", {}))
        internal_dependencies = dependencies.intersection(CRATES)
        if internal_dependencies != allowed_dependencies:
            errors.append(
                f"{name} internal dependencies must be exactly {sorted(allowed_dependencies)}"
            )

    core_source = ROOT / "crates" / "codegauge-core" / "src"
    if core_source.is_dir():
        source_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(core_source.rglob("*.rs"))
        )
        forbidden = (
            "codegauge-provider",
            "quick_xml",
            "serde_json",
            "std::fs",
            "std::net",
            "std::process",
            "std::os",
            "Command::",
        )
        for token in forbidden:
            if token in source_text:
                errors.append(f"codegauge-core contains forbidden I/O/provider token {token!r}")

    if errors:
        print("BOOTSTRAP CHECKS: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("BOOTSTRAP CHECKS: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
