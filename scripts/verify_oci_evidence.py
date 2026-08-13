#!/usr/bin/env python3
"""Validate one locally exported OCI image and persist release evidence.

This verifier is deliberately registry-independent.  The release workflow builds
an OCI archive and a runnable Docker archive, then this script binds the two
outputs to the inspected image and runtime smoke results before publication.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from .oci_evidence import EvidenceError, verify
else:
    from oci_evidence import EvidenceError, verify


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oci-archive", type=Path, required=True)
    parser.add_argument("--docker-archive", type=Path, required=True)
    parser.add_argument("--inspect-json", type=Path, required=True)
    parser.add_argument("--metadata-json", type=Path, required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--platform", required=True)
    parser.add_argument("--runtime-mode", choices=("native", "qemu"), required=True)
    parser.add_argument("--version-output", type=Path, required=True)
    parser.add_argument("--profiles-output", type=Path, required=True)
    parser.add_argument("--contract-output", type=Path, required=True)
    parser.add_argument("--non-root-output", type=Path, required=True)
    parser.add_argument("--emulation-evidence", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        verify(
            oci_archive=args.oci_archive,
            docker_archive=args.docker_archive,
            inspect_json=args.inspect_json,
            metadata_json=args.metadata_json,
            version=args.version,
            revision=args.revision,
            platform=args.platform,
            runtime_mode=args.runtime_mode,
            version_output=args.version_output,
            profiles_output=args.profiles_output,
            contract_output=args.contract_output,
            non_root_output=args.non_root_output,
            emulation_evidence=args.emulation_evidence,
            output=args.output,
        )
    except EvidenceError as error:
        print(f"OCI EVIDENCE: FAIL: {error}", file=sys.stderr)
        return 1
    print(f"OCI EVIDENCE: PASS: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
