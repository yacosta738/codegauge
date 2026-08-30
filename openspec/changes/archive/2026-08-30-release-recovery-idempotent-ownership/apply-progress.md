# Apply progress — Units 1–5 plus Phase 5 critical rework

## Scope

Applied Unit 1 tasks 1.1–1.3 (Release Please canonical ownership), Unit 2 tasks 2.1–2.4 (no-write recovery planner, strict GitHub adapter, recovery workflow, auditable outcomes), Unit 3 tasks 3.1–3.3 (historical 13-entry vs current 14-entry graph, exact merged-commit provenance, Cargo → npm → OCI publication order and at-most-once dispatch, Dockerfile/checksum/asset verification), Phase 4 tasks 4.1–4.4 (recovery contracts, runtime/read-only checks, and repository gates), and Phase 5 tasks 5.1–5.2 (rollback runbook, audit-only publication failure inventory, protected live gate, least-privilege read paths, and final workflow/script/fixture review).

## Boundary exception

The recorded `feature-branch-chain` strategy expected a separate PR 2 base branch and worktree, but no recoverable Unit 2 / PR 2 branch or commit exists locally or in `refs/`. The user explicitly approved continuation on the existing dirty `main` worktree as the dependency-equivalent boundary. No reset, stash, discard, commit, push, or remote write was performed.

## Unit 3 TDD evidence

1. Added focused pytest tests to `tests/release_provenance_tests.py`:
   - `test_historical_release_provenance_allows_13_entry_snapshot_against_current_14_entry_graph` (validates `historical_entry_count == 13`, `current_entry_count == 14`, `graph_mismatch is True`).
   - `test_historical_provenance_rejects_a_different_tree_or_graph_without_subset` (rejects mismatched tree, paths outside the current graph, and traversal-invalid paths).
   - `test_release_assets_validate_manifests_checksums_and_required_inputs`, `test_release_assets_can_require_an_exact_target_matrix`, `test_release_assets_reject_a_tampered_checksum_sidecar`.
   - `test_publication_contract_is_serial_and_at_most_once_per_release_identity`, `test_publication_contract_rejects_parallel_or_fallback_writers`.
2. Ran the new tests against the previous production code:
   - `python3 -m pytest -q tests/release_provenance_tests.py -k historical_release_provenance` — RED (function did not exist).
   - `python3 -m pytest -q tests/release_provenance_tests.py -k publication_contract_is_serial` — RED (function did not exist).
3. Implemented the minimum production code in `scripts/verify_release_provenance.py`:
   - `_validate_historical_manifest_paths` and `validate_historical_provenance` to anchor the historical 13-entry release by exact commit/tree, validate the 13 historical paths against the current 14-entry graph, require synchronized Cargo/npm/Dockerfile versions, and return `(historical_entry_count, current_entry_count, graph_mismatch)`.
   - `validate_release_assets` to verify every release manifest, archive byte digest, and checksum sidecar; reject tampered sidecars and incomplete target matrices.
   - `publication_order(workflow)` to require coarse `cargo → npm → oci` order, the explicit `needs: publish-release` / `needs: publish-npm` gates, and forbid any fallback release identity creation.
   - `release_dispatch_count(workflow)` to require exactly one tag-triggered dispatch and the non-canceling identity lock.
4. Updated `validate_stage_a_configuration` to refuse any remaining global/root/package-level `skip-github-release` while keeping root metadata carrier guarantees (`skip-changelog`, `skip-snapshot`, no `package-name`).
5. Updated `tests/release_carrier_static_tests.py` to assert the new recovery workflow contract surface (explicit historical recovery name, dry-run + protected live path, workflow-scope `contents: read`).
6. Updated `tests/distribution_checks_e3a.py` to align with the Unit 1 canonical ownership change (root remains a metadata carrier without `package-name`, but `skip-github-release` is no longer globally/CLI-suppressed).
7. Final focused suite:
   - `python3 -m pytest -q tests/release_provenance_tests.py tests/recover_release_tests.py tests/recover_release_github_tests.py tests/release_carrier_static_tests.py tests/release_carrier_mode_tests.py tests/oci_distribution_static_tests.py tests/oci_distribution_failure_tests.py` — **50 passed**.
   - `python3 tests/release_provenance_tests.py` — PASS (`RELEASE PROVENANCE TESTS: PASS`).
   - `python3 tests/release_carrier_static_tests.py` — PASS.
   - `python3 tests/release_carrier_mode_tests.py` — PASS.
   - `python3 tests/release_carrier_tests.py` — PASS.
   - `python3 tests/distribution_checks.py` — PASS (`DISTRIBUTION CHECKS: PASS`).
   - `python3 tests/oci_distribution_tests.py` — PASS.
   - `python3 tests/oci_distribution_evidence_tests.py` — PASS.
   - `python3 tests/bootstrap_checks.py` — PASS.
   - `python3 tests/readme_checks.py` — PASS.
   - `python3 -m compileall -q scripts tests` — PASS.
   - `git diff --check` — PASS.

## Unit 3 findings

- `scripts/verify_release_provenance.py` now accepts the historical 13-entry snapshot while still requiring the current graph to be a superset and the immutable commit/tree to match. The script does not require current graph equality with the historical graph.
- `validate_release_assets` enforces an eight-target matrix (linux gnu/musl, darwin, windows × x64/arm64), matching the canonical `release-out/` archive set, and refuses any checksum sidecar that does not match the archive bytes and the manifest.
- `publication_order` forbids `gh release create/edit/delete`, `git tag`, and `git push` in the publish workflow, ensuring Recovery and the carrier remain the only canonical tag/release creators.
- `release_dispatch_count` enforces a single tag-triggered dispatch per release identity with a non-canceling concurrency lock.
- No CodeGauge engine/provider/profile/schema files were touched; the change set is limited to release metadata, scripts, workflows, and tests.
- `state.yaml` advanced to `current_phase: apply`, `completed` includes `apply-slice-4`, and `next: verify`.

## Phase 4 TDD and verification evidence

1. Added and passed recovery contracts covering:
   - merged-but-untagged planning, historical replay, tolerated current-graph mismatch, and fallback refusal;
   - repeated no-op recovery, conflicting identity refusal, partial-failure rerun, tag-convergence gating, and repository lock behavior;
   - malformed/truncated request, snapshot, API, pagination, URL, and repository boundaries;
   - live authorization/confirmation/token gates and dry-run `NO_WRITES` audit semantics;
   - ordered tag-then-release loopback reconciliation and release identity tracking.
2. Ran the focused release/recovery/provenance/carrier/OCI matrix:
   - `python3 -m pytest -q tests/release_provenance_tests.py tests/recover_release_tests.py tests/recover_release_github_tests.py tests/release_carrier_static_tests.py tests/release_carrier_mode_tests.py tests/oci_distribution_static_tests.py tests/oci_distribution_failure_tests.py` — **73 passed**.
   - Direct release, carrier, distribution, OCI, evidence, and Release Please checks — **PASS**.
   - Release Please 17.6.0 read-only runtime harness — **PASS**, with expected fake-SCM warnings and `releaseCalls: 0`, `tagCalls: 0`.
3. Ran repository gates:
   - `python3 tests/bootstrap_checks.py`, `python3 tests/readme_checks.py`, and `python3 -m compileall -q scripts tests` — **PASS**.
   - `cargo test --workspace --locked`, `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets --locked -- -D warnings`, and `cargo check --workspace --locked` — **PASS**.
   - `actionlint .github/workflows/release-recovery.yml` and `git diff --check` — **PASS**.
4. No live GitHub, npm, OCI, tag, release, or publication mutation was performed.

## Remaining work

- Phase 5 / tasks 5.1–5.2 implementation is complete.
- SDD verification, acceptance QA, and archive remain pending.
- Hosted dry-run validation is still pending; any live `v0.3.0` recovery, tag creation, GitHub Release creation, or publication requires a separate explicit operator authorization after all reports pass.

## Phase 5 TDD and hardening evidence

1. Added failing safety contracts before the Phase 5 implementation for:
   - disabling live recovery behind `vars.RELEASE_RECOVERY_LIVE_ENABLED` and the protected `release-recovery-live` environment;
   - preserving canonical tags/releases and stopping later publication stages;
   - recording an audit-only publication failure inventory with no rollback, deletion, or force-move;
   - using the default read-only GitHub token in the carrier; and
   - keeping recovery actions pinned and the dry-run section free of the live recovery secret.
2. Implemented the minimum hardening in `docs/release-recovery-runbook.md`, `.github/workflows/release-recovery.yml`, `.github/workflows/release-publish.yml`, and `.github/workflows/release-tag-carrier.yml`. Added checked-in recovery request/snapshot fixtures under `fixtures/release-recovery/`.
3. TDD and static results:
   - `python3 -m pytest -q tests/release_recovery_safety_tests.py tests/recover_release_tests.py tests/recover_release_github_tests.py` — **62 passed**.
   - `python3 -m pytest -q tests/*_tests.py` — **94 passed**.
   - `python3 tests/release_carrier_static_tests.py`, `python3 tests/release_carrier_mode_tests.py`, `python3 tests/release_carrier_tests.py`, distribution/OCI checks, bootstrap/readme checks, and Release Please 17.6.0 runtime harness — **PASS**.
   - `actionlint .github/workflows/*.yml`, `python3 -m compileall -q scripts tests`, and `git diff --check` — **PASS**.
4. Repository gates:
   - `cargo test --workspace --locked`, `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets --locked -- -D warnings`, and `cargo check --workspace --locked` — **PASS**.
5. Credential-free checked-in dry-run produced `outcome: planned`, `NO_WRITES: true`, and the exact canonical tag-then-release artifact plan. No live GitHub, npm, OCI, tag, release, or publication mutation was performed.

## Phase 5 findings

- The live recovery job is the only recovery write boundary, requires the explicit confirmation marker, uses a protected environment, and is disabled unless `RELEASE_RECOVERY_LIVE_ENABLED=true`.
- Recovery concurrency is keyed by repository, release tag, and merged SHA rather than a caller-controlled request path.
- The read-only carrier uses `github.token` with workflow/job `contents: read`; the live recovery job retains the existing repository-scoped release token only for its two permitted GitHub writes.
- No application, engine, provider, profile, or schema files were changed by the recovery hardening slice.
- SDD verification, acceptance QA, and archive remain pending; the existing failed `verify-report.md` is not being rewritten as PASS.

## Phase 5 critical rework evidence

The continuation stayed within the assigned Phase 5 / tasks 5.1–5.2 slice and the approved
feature-branch-chain dirty-main-equivalent boundary. The four regression tests were run before the
corresponding fixes and initially returned **4 failed**.

1. Canonical Release Please identity:
   - Added a root-only `include-component-in-tag: false` override and kept the global component-tag
     default for linked runtime candidates.
   - Marked non-root Cargo/npm candidates as version carriers with `skip-github-release: true`, so
     Release Please 17.6.0 still generates one merged/root GitHub Release rather than duplicate
     component releases.
   - Updated the effective-config validator and provenance contracts.
   - Extended the actual Release Please 17.6.0 read-only harness through `Manifest.buildReleases()`.
     It now proves `rootReleaseTag: v0.3.0`, `releaseCandidatePaths: ["."]`, 35 synchronized update
     paths, one private dependency update, and zero release/tag mutations. The harness uses a
     controlled `Release-As: 0.3.0` commit footer and synthetic pre-release updater inputs so the
     checked-in recovery target remains `0.3.0` while updater transformations are still exercised.
2. Ambiguous release mutation:
   - `execute_recovery()` now classifies every exception from the GitHub Release write as
     `mutation-unknown`, including transport-wrapped `RecoveryError` instances, and classifies a
     post-write final-read/non-convergence failure as unknown when a release write was attempted.
   - Mutation plans now set `no_writes: false`; machine and human audit records include deterministic
     re-read-before-retry guidance and forbid delete, force-move, replacement, or blind retry.
   - Updated the existing release-failure rerun contracts and added the direct `OSError` regression.
3. Publisher identity:
   - Changed the GitHub tag API lookup to use the exact `${RELEASE_REF}` (`tags/v0.3.0`) instead of
     stripping the `v` prefix.
4. Publication inventory:
   - Replaced the aggregate Markdown-only record with a JSON `publication-failure-inventory/v1`
     artifact.
   - Every target row carries `canonical_version`, `canonical_reference`, `source_sha`,
     `published_digest_or_package_version`, `job_result`, and `evidence_location`.
   - The inventory enumerates six Cargo crates, seven npm packages, eight GitHub Release archives,
     eight checksum sidecars, eight release-manifest evidence files, OCI architecture/final/latest
     references, and the attestation target (42 rows total). It records `UNKNOWN` where a registry
     digest or package version is not available to the audit-only job and preserves the dependency
     stop chain without any publication writer.

## Phase 5 critical rework verification

- Four focused regressions — **4 passed**.
- `python3 -m pytest -q tests/*_tests.py` — **98 passed**.
- Release Please 17.6.0 runtime harness — **PASS**, with `rootReleaseTag: v0.3.0`, one release
  candidate path (`.`), and `releaseCalls: 0`, `tagCalls: 0`.
- Embedded publication-inventory script smoke check — **PASS**, valid JSON with 42 target rows and
  all required per-target fields.
- Bootstrap/readme/distribution/carrier/OCI checks, Python compileall, actionlint for all workflows,
  and `git diff --check` — **PASS**.
- `cargo test --workspace --locked`, `cargo fmt --all -- --check`,
  `cargo clippy --workspace --all-targets --locked -- -D warnings`, and
  `cargo check --workspace --locked` — **PASS**.
- No live GitHub, tag, release, Cargo, npm, OCI, or publication mutation was performed.

The existing `verify-report.md` remains the historical failed report; SDD verification must rerun
against the updated implementation. Acceptance QA and archive remain pending.
