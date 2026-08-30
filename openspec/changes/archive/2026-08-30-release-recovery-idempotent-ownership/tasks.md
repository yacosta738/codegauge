# Tasks: Idempotent Release Recovery and Ownership

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 350–500 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |
| Current slice | Phase 5 / tasks 5.1–5.2 |

Decision needed before apply: No — resolved with the safest recommended chained delivery
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
Feature-branch-chain warning: dedicated feature/tracker branch is unavailable; user-approved dirty-main equivalent boundary is in effect for this continuation.
Current slice: Phase 5 / tasks 5.1–5.2, continuing from the approved dirty-main equivalent of the applied Units 1–4 boundary
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Restore Release Please ownership and harden normal release consumers | PR 1 | `base: main`; applied in the current approved dirty worktree boundary; config/workflow guards and focused tests |
| 2 | Add historical recovery planner and explicit dry-run/live workflow | PR 2 | `base: PR 1 branch`; applied in the current approved dirty worktree boundary; planner/adapter, lock, auth, audit, no-write tests |
| 3 | Complete provenance/publication verification and historical fixtures | PR 3 | `base: PR 2 branch`; applied in the current approved dirty worktree boundary; ordered publication, manifests/checksums, integration tests |

## Phase 1: Ownership and Release Boundaries

- [x] 1.1 Remove root/package `skip-github-release` suppression in `release-please-config.json`; preserve `.release-please-manifest.json` synchronized versions and add effective Release Please 17.6.0 regression coverage.
- [x] 1.2 Update `.github/workflows/release-please.yml` so pinned Release Please owns canonical tags/releases with `contents: write`, main-branch gating, and no competing release writer.
- [x] 1.3 Harden `.github/workflows/release-tag-carrier.yml`, `release-on-tag.yml`, `release.yml`, `release-build.yml`, and `release-publish.yml` to require one verified tag/release identity and never backfill missing resources.

## Phase 2: Recovery Planner and Workflow
- [x] 2.1 Add a test-first recovery planner/validator under `scripts/` that accepts exact repository, version/tag, merged SHA/PR, historical tree/manifest, mode, authorization marker, and derived idempotency key.
- [x] 2.2 Add the GitHub read/write adapter with complete-response/pagination validation, exact SHA and release identity checks, repository-scoped concurrency locking, and non-destructive tag/release reconciliation.
- [x] 2.3 Add the dedicated recovery workflow with separate default dry-run and protected, explicitly authorized live path; live operations may only reconcile canonical tag then GitHub Release.
- [x] 2.4 Record machine-readable and human-readable audit output for `NO_WRITES`, refusal, no-op, partial failure, and mutation outcomes without credentials or publication capability.


## Phase 3: Provenance and Publication Integration

- [x] 3.1 Extend `scripts/verify_release_provenance.py` and release fixtures to validate historical 13-entry snapshot versus current 14-entry graph, synchronized Cargo/npm/container versions, immutable SHA, manifests, and checksums.
- [x] 3.2 Preserve and enforce downstream Cargo → npm → OCI/image publication order in `.github/workflows/release*.yml`; stop later stages after failure and dispatch at most once per release identity.
- [x] 3.3 Verify `Cargo.toml`, `Cargo.lock`, `crates/*/Cargo.toml`, `npm/**/package.json`, `Dockerfile`, and release assets without changing CodeGauge engine/provider/profile/schema behavior.

## Phase 4: Testing and Verification

- [x] 4.1 Add failing-then-passing Python/unit contracts for merged-but-untagged detection, historical replay, tolerated current-graph mismatch, missing/mismatched identities, and publication fallback refusal.
- [x] 4.2 Test repeated recovery no-op, conflicting tag/release refusal, partial failure rerun, concurrent lock behavior, truncated/malformed API or manifest refusal, and live authorization/confirmation gates.
- [x] 4.3 Test dry-run `NO_WRITES`, provenance/audit fields, ordered publication, downstream dispatch idempotency, and effective Release Please runtime behavior with the read-only harness.
- [x] 4.4 Run focused release tests plus `python3 tests/bootstrap_checks.py`, `python3 tests/readme_checks.py`, `cargo test --workspace --locked`, `cargo fmt --all -- --check`, and locked clippy/check gates.

## Phase 5: Release Verification and Cleanup

- [x] 5.1 Confirm recovery rollback behavior: disable live recovery, never delete/force-move canonical resources, stop partial publication, and document immutable artifact deprecation handling in workflow comments/configuration.
- [x] 5.2 Review changed workflows/scripts/fixtures for pinned actions, least-privilege credentials, no external writes in dry-run, and absence of application/provider semantic changes.

### Phase 5 rework evidence

Tasks 5.1–5.2 were revalidated after the failed verification report. The rework adds exact
unprefixed Release Please root-tag runtime coverage, `mutation-unknown` audit semantics for
ambiguous release writes, exact publisher tag lookup, and a JSON per-target immutable publication
inventory. Focused regressions and the configured repository gates pass; SDD verification and QA
remain downstream phases.
