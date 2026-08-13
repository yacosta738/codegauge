#!/usr/bin/env python3
"""Executable E3a distribution checks.

Later distribution layers remain in separate modules until their checks are
added to this runner.
"""

from __future__ import annotations

import sys

from distribution_checks_e3a import run_checks


def main() -> int:
    errors = run_checks()
    if errors:
        print("DISTRIBUTION CHECKS: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DISTRIBUTION CHECKS: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
