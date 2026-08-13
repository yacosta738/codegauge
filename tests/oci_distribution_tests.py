#!/usr/bin/env python3
"""Compatibility runner for the reviewable OCI distribution test layers."""

from __future__ import annotations

import argparse

if __package__:
    from . import oci_distribution_evidence_tests as evidence
    from . import oci_distribution_failure_tests as failure
    from . import oci_distribution_static_tests as static
else:
    import oci_distribution_evidence_tests as evidence
    import oci_distribution_failure_tests as failure
    import oci_distribution_static_tests as static


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--helper-only", action="store_true")
    args = parser.parse_args()

    static.run_tests(include_build_ordering=not args.helper_only)
    evidence.run_tests()
    failure.run_tests()
    print("OCI DISTRIBUTION TESTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
