#!/usr/bin/env python3
"""Generate the six checked-in npm platform manifests from one template."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = json.loads(
    (ROOT / "npm" / "codegauge" / "package.json").read_text(encoding="utf-8")
)["version"]
TARGETS = {
    "codegauge-linux-x64-gnu": ("linux", "x64", "Linux x64 GNU"),
    "codegauge-linux-arm64-gnu": ("linux", "arm64", "Linux arm64 GNU"),
    "codegauge-darwin-x64": ("darwin", "x64", "macOS x64"),
    "codegauge-darwin-arm64": ("darwin", "arm64", "macOS arm64"),
    "codegauge-win32-x64-msvc": ("win32", "x64", "Windows x64 MSVC"),
    "codegauge-win32-arm64-msvc": ("win32", "arm64", "Windows arm64 MSVC"),
}


def expected(name: str, os_name: str, cpu: str, target: str) -> dict[str, object]:
    return {
        "name": f"@yacosta738/{name}",
        "version": VERSION,
        "description": f"CodeGauge executable for {target}",
        "license": "MIT",
        "repository": "yacosta738/codegauge",
        "os": [os_name],
        "cpu": [cpu],
        "bin": {"codegauge": "bin/codegauge"},
        "files": [
            "package.json",
            "bin/codegauge.exe" if os_name == "win32" else "bin/codegauge",
        ],
        "engines": {"node": ">=18"},
    }


def render(value: dict[str, object]) -> str:
    return json.dumps(value, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail when a generated file is stale")
    args = parser.parse_args()
    template = (ROOT / "npm" / "package.json.tmpl").read_text(encoding="utf-8")
    errors: list[str] = []
    for name, (os_name, cpu, target) in TARGETS.items():
        package_dir = ROOT / "npm" / "packages" / name
        path = package_dir / "package.json"
        expected_text = template.replace("__PACKAGE_NAME__", f"@yacosta738/{name}")
        expected_text = expected_text.replace("__VERSION__", VERSION)
        expected_text = expected_text.replace("__TARGET__", target)
        expected_text = expected_text.replace("__OS__", os_name).replace("__CPU__", cpu)
        expected_text = expected_text.replace(
            "__BINARY__", "codegauge.exe" if os_name == "win32" else "codegauge"
        )
        actual = path.read_text(encoding="utf-8") if path.is_file() else ""
        if args.check:
            if json.loads(actual or "{}") != json.loads(expected_text):
                errors.append(str(path.relative_to(ROOT)))
        else:
            package_dir.mkdir(parents=True, exist_ok=True)
            generated = expected(name, os_name, cpu, target)
            generated["bin"] = {
                "codegauge": "bin/codegauge.exe" if os_name == "win32" else "bin/codegauge"
            }
            path.write_text(render(generated), encoding="utf-8")
    if errors:
        print("stale generated npm manifests:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
