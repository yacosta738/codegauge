# Phase 13 local verification — 2026-08-15

Checkout: `fix/release-carrier-private-patch-context`, `HEAD=aa27efe0f6ce10707abd1c19f5b020a4db8dfa46`, intentionally dirty.

## Regression evidence

- Hosted run `31888439750` remains **pre-fix failure evidence**. The exact real PR `#59` API list was
  read-only fetched; it contains 31 entries and now passes `validate_stage_a_diff(..., version="0.2.0")`.
- The base npm entry contains seven approved version pairs plus the exact `files` compact-to-three-line
  rewrite (`10` additions, `8` deletions). The pre-fix validator rejects the same list by counting
  formatting lines as version edits.
- Current negative probes reject platform-package formatting, altered base `files` content, arbitrary
  base formatting, and unapproved base keys.

## Commands

- `python3 tests/release_carrier_tests.py` — PASS.
- `python3 tests/release_carrier_static_tests.py`, `tests/release_carrier_mode_tests.py`,
  `tests/release_provenance_tests.py`, `tests/distribution_checks.py`, `tests/bootstrap_checks.py`,
  and `tests/readme_checks.py` — PASS.
- `python3 tests/release_please_runtime_tests.py` — PASS against exact Release Please `17.6.0`;
  32 generated paths, four private pins, six npm rewrites, one PR, zero release/tag calls.
- `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` — PASS.
- Locked Cargo metadata/tests/check/fmt/Clippy and five local-patch package verifications — PASS;
  31 workspace tests passed, zero failed/skipped.
- npm typecheck/tests and seven package dry-runs — PASS; six tests and seven packages.
- Four OCI suites, `actionlint`, `shellcheck scripts/build_oci_release.sh`, Dockerfile `buildx --check`,
  and `git diff --check` — PASS.

No hosted replay, dispatch, tag, release, publication, upload, attestation, credential-bearing run,
variable mutation, merge, push, or commit was performed. This evidence is technical only; independent
`sdd-qa` remains pending.
