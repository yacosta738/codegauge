# Phase 12 local QA rerun — 2026-08-15

Checkout: `fix/release-carrier-private-patch-context`, `cdd91baf9cbd0fb416ecfe67977310253d9b7534`.

Focused executable results:

- `python3 tests/release_carrier_tests.py` — PASS. This includes the exact PR #59 filename-bound
  hunk-only private patch, full unified-diff and hunk-only parser boundaries, missing/inconsistent/
  truncated/malformed/multi-section patches, typed/annotated/generated/npm mutations, all private
  package/path/key/feature/formatting/truncation mutations, replay selection, no-match, trust, and
  tag-plan cases.
- `python3 tests/release_please_runtime_tests.py` — PASS. Exact package `17.6.0`; 32 generated
  effective paths, one private four-pin update, six npm optional rewrites, one synchronized PR, and
  zero release/tag calls. No-op, wrong-version, package-version, publish-flag, and unapproved-path
  mutations were rejected.
- `python3 tests/release_carrier_mode_tests.py` — PASS. Push/manual live and dry-run defaults,
  replay-only manual dry-run, malformed replay, non-main, and total boolean replay schema cases pass.
- Extracted checked-in dry-run plan and guard with a fake read-only `gh` — PASS. Only GET-shaped
  lookups occurred; no POST/PUT/PATCH/DELETE method was called, and all tag/label/release/upload/
  registry/attestation mutations were skipped, not-started, or not-dispatched.
- Fresh local Cargo, npm, archive/tamper, OCI synthetic, Python, and package dry-run capabilities
  passed. Static workflow diagnostics also exited zero but remain `NOT TESTED` in the QA matrix by
  policy because static inspection is not observable acceptance behavior.

Safety boundary: no GitHub workflow dispatch, API mutation, repository-variable change, tag, release,
registry publication, upload, attestation, merge, push, credential, or source/workflow change was
performed by QA.
