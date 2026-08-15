#!/usr/bin/env python3
"""Run the exact Release Please 17.6.0 chain against a read-only fake SCM."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "release_please_runtime_harness.mjs"

sys.path.insert(0, str(ROOT))

from scripts.verify_release_provenance import ProvenanceError, validate_stage_a_diff  # noqa: E402


def find_exact_package() -> Path | None:
    configured = os.environ.get("RELEASE_PLEASE_17_6_0_ROOT")
    candidates = [Path(configured)] if configured else []
    candidates.extend(
        path.parent
        for path in Path.home().joinpath(".npm", "_npx").glob(
            "*/node_modules/release-please/package.json"
        )
    )
    candidates.append(ROOT / "node_modules" / "release-please")
    for candidate in candidates:
        if candidate is None:
            continue
        package_json = candidate / "package.json"
        try:
            if json.loads(package_json.read_text(encoding="utf-8")).get("version") == "17.6.0":
                return candidate
        except (OSError, json.JSONDecodeError):
            continue
    return None


def main() -> int:
    package_root = find_exact_package()
    if package_root is None:
        print(
            "RELEASE PLEASE V17.6.0 RUNTIME TESTS: UNTESTED "
            "(exact package is not installed; no JSON-shape substitute was claimed)"
        )
        return 0

    environment = {
        **os.environ,
        "CODEGAUGE_ROOT": str(ROOT),
        "RELEASE_PLEASE_17_6_0_ROOT": str(package_root),
    }
    result = subprocess.run(
        ["node", str(HARNESS)],
        check=False,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        return result.returncode

    try:
        validate_stage_a_diff(
            [
                "Cargo.toml",
                "Cargo.lock",
                ".release-please-manifest.json",
                "npm/codegauge/package.json",
                "crates/codegauge-conformance/Cargo.toml",
            ]
        )
    except ProvenanceError:
        print("PRIVATE CANDIDATE MUTATION: REJECTED")
    else:
        print("PRIVATE CANDIDATE MUTATION: ACCEPTED")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
