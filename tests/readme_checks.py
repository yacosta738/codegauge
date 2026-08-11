#!/usr/bin/env python3
"""Small red/green contract checks for the CodeGauge README."""

from __future__ import annotations

import sys
from pathlib import Path


README = Path(__file__).resolve().parents[1] / "README.md"

REQUIRED_FRAGMENTS = (
    "measures evidence, not policy",
    "independent from agent-harness",
    "does not run Maven, Gradle, tests, or JaCoCo",
    "Rust/Cargo 1.97.1",
    "cargo metadata --locked",
    "cargo test --workspace --locked",
    "cargo fmt --all -- --check",
    "cargo clippy --workspace --all-targets --locked -- -D warnings",
    "codegauge analyze --profile java-jacoco-v1 --input PATH --format json",
    "codegauge profiles",
    "codegauge version",
    "crap-original-v1",
    "codegauge-result/v1",
    "codegauge-error/v1",
    "PARTIAL",
    "INCOMPATIBLE_MEASUREMENTS",
    "0/2/3/4/5/6/10",
    "COMPLEXITY",
    "INSTRUCTION",
    "missing evidence never becomes zero",
    "schemas/",
    "SHA-256",
    "analysis_timestamp",
    "64 MiB",
    "depth 128",
    "100,000 classes and methods",
    "16 counters per method",
    "1,000,000,000",
    "crap4java",
    "crap4go",
    "crap4clj",
    "Release checklist",
    "immutable Git revision",
    "artifact SHA-256",
    "cross-platform binaries were produced",
)


def main() -> int:
    text = " ".join(README.read_text(encoding="utf-8").replace("`", "").split())
    missing = [fragment for fragment in REQUIRED_FRAGMENTS if fragment not in text]
    if missing:
        print("README CHECKS: FAIL")
        for fragment in missing:
            print(f"- missing: {fragment}")
        return 1

    print("README CHECKS: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
