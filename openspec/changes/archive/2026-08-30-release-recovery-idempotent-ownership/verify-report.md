# Verification Report

**Change**: `release-recovery-idempotent-ownership`
**Mode**: OpenSpec; `fallback` execution evidence
**Date**: 2026-08-30
**Working directory**: `/Users/acosta/Dev/agent-swarm/codegauge`

This report verifies technical conformance only. It does not claim operator acceptance or
authorize live recovery. Acceptance remains the responsibility of `sdd-qa` after verification
returns PASS or PASS WITH WARNINGS.

## Verification basis and boundary

Reviewed: proposal, delta specification, design, tasks, apply progress, state, project
configuration, all recovery fixtures, changed release scripts/workflows/tests, the unrelated
main TypeScript specification for semantic-boundary comparison, and the previous stale
verification report.

The worktree contains the applied change on the user-approved dirty-`main` equivalent
boundary. No code, tag, release, registry, OCI, publication, commit, push, or other remote
mutation was performed by this verification. Only this report and the phase state are
updated.

Historical identity evidence checked locally:

- repository `yacosta738/codegauge`, protected branch `main`, PR `75`;
- merged SHA `cf46ba64bd2e723c28406ca6b7fc3c97d183f1d0`;
- historical tree `f9fca04cb359e843bd13ab7ff4db0ff1a9ba4a1c`;
- historical manifest has 13 entries; current manifest has 14, adding
  `crates/codegauge-provider-typescript`;
- the historical commit is an ancestor of `origin/main`.

## Previous CRITICAL findings — rework status

| # | Previous CRITICAL finding | Rework evidence | Status |
|---|---|---|---|
| 1 | Release Please effective root tag resolved to `codegauge-root-v0.3.0` instead of canonical `v0.3.0`. | `release-please-config.json:10` pins `"include-component-in-tag": false` for the root component; runtime harness asserts `'"rootReleaseTag": "codegauge-root-v0.3.0"' not in result.stdout` (`tests/release_please_runtime_tests.py:232`); rerun reports `rootReleaseTag: v0.3.0` and `releaseCandidatePaths: ["."]`. | RESOLVED |
| 2 | Publisher provenance lookup used `${RELEASE_REF#v}`, stripping the `v` from `git/ref/tags/...`. | `.github/workflows/release-publish.yml:202` queries `repos/${GITHUB_REPOSITORY}/git/ref/tags/${RELEASE_REF}` (full tag, including `v`); `${RELEASE_REF#v}` is used only for the separate `RELEASE_VERSION` variable (lines 253, 306, 389). | RESOLVED |
| 3 | Ambiguous `create_release` exception was audited as `partial-failure`, not `mutation-unknown`. | `scripts/recover_release.py:498-505` (create_tag), `:523-532` (create_release), and `:534-546` (post-release final preflight) all raise with `mutation="mutation-unknown"`; covered by 6 executable assertions in `tests/recover_release_tests.py` (lines 298, 331, 508, 512, 535, 538). The remaining `partial-failure` paths describe known-good create_tag + known-bad preflight, which is not ambiguous. | RESOLVED |
| 4 | Partial-publication inventory omitted required per-target immutable output fields and artifact locations. | `.github/workflows/release-publish.yml:371-550` (`publication-failure-inventory`) writes `schema: publication-failure-inventory/v1` with per-target entries that record `target`, `kind`, `canonical_version`, `canonical_reference`, `source_sha`, `published_digest_or_package_version`, `job_result`, `evidence_location`, plus envelope `canonical_version`, `canonical_reference`, `source_sha`, `merged_main_sha`, `policy`, `stop_chain`, `republish_policy`, `runbook`, `job_results`, `targets`; covered by `tests/release_recovery_safety_tests.py:54` which asserts every required field. | RESOLVED |

## Completeness

| Metric | Value |
|---|---:|
| Tasks total | 16 |
| Tasks marked complete | 16 |
| Tasks factually complete | 16 |
| Tasks requiring rework | 0 |

All 16 tasks in `tasks.md` are factually complete after the rework.

## Quality-runner and TDD mode

| Capability | Status | Evidence/reason |
|---|---|---|
| `quality-runner/v1` | `UNAVAILABLE` | Workspace `../openspec/quality-runner.json` exists but has `enabled: false` and disabled control plane. |
| Standalone runner | `UNAVAILABLE` | No `scripts/sdd-quality-runner.mjs` exists in the project. |
| Strict TDD | `fallback` | `strict_tdd: true` is configured; the strict verifier module was not available in the injected/local skill tree. |
| Coverage | `UNAVAILABLE` | No coverage tool or threshold is configured. |

All command evidence below is therefore explicitly manual `fallback` evidence. No deterministic
runner envelope or coverage percentage is claimed. `apply-progress.md` records RED → GREEN
evidence for several units; the dirty worktree prevents independent verification of test/code
commit ordering for every task.

## Build and test execution (post-rework rerun)

| Command | Exit | Result | Status |
|---|---:|---|---|
| `python3 -m pytest -q tests/*_tests.py` | 0 | 98 passed in 10.46s | PASS |
| `python3 tests/release_please_runtime_tests.py` | 0 | Release Please 17.6.0 harness passed; reports `rootReleaseTag: v0.3.0`, `releaseCandidatePaths: ["."]`, `releaseCalls: 0`, `tagCalls: 0` | PASS |
| Direct bootstrap/readme/distribution/provenance/carrier/OCI checks | 0 | Every named check printed `PASS` | PASS |
| `cargo test --workspace --locked` | 0 | All workspace, integration, provider, conformance, and doc tests passed | PASS |
| `cargo fmt --all -- --check` | 0 | No diagnostics | PASS |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | 0 | No denied warnings | PASS |
| `cargo check --workspace --locked` | 0 | Workspace type-check passed | PASS |
| `npm test` from `npm/codegauge` | 0 | TypeScript build and 6 tests passed | PASS |
| `actionlint .github/workflows/*.yml` | 0 | No diagnostics | PASS |
| `python3 -m compileall -q scripts tests` | 0 | No diagnostics | PASS |
| `git diff --check` | 0 | No whitespace errors | PASS |
| Action-pin audit over `.github/workflows/*.yml` | 0 | 42 references; 0 unpinned refs | PASS |

The Release Please harness emits expected fake-SCM warnings (`Expected 14 releases, only
found 0`, missing release PRs/paths, placeholder title warnings). The harness is a read-only
fake SCM and does not prove a hosted tag or release was created. No hosted GitHub, Cargo, npm,
GHCR, or attestation run was performed.

The credential-free recovery fixture produced:

- `outcome: planned`;
- `no_writes: true` and `NO_WRITES: True`;
- intended operations `create-canonical-tag`, then `create-github-release`;
- the expected repository, SHA, 13-entry historical identity, and 14-entry current graph
  values.

The independent adapter preflight test passed with GET-only transport and verified repository,
default branch, PR merge state, merged SHA, historical tree/blob/manifest, current graph,
version files, 13-vs-14 counts, and the canonical two-operation artifact plan.

## Spec compliance matrix

An exact scenario is `COMPLIANT` only when a passing runtime test covers the complete
behavior.

| Requirement | Scenario | Passing test/evidence | Result |
|---|---|---|---|
| Single canonical release owner | Release Please creates the canonical `vX.Y.Z` release | `test_release_please_runtime_emits_canonical_root_tag` (`tests/release_please_runtime_tests.py:211`) asserts `'"rootReleaseTag": "codegauge-root-v0.3.0"' not in result.stdout`; rerun reports `rootReleaseTag: v0.3.0` and `releaseCandidatePaths: ["."]`. | COMPLIANT |
| Single canonical release owner | Publication cannot backfill ownership | `test_publication_contract_rejects_parallel_or_fallback_writers`; carrier static checks; root config pins `include-component-in-tag: false`. | COMPLIANT |
| Explicit recovery | Dry run validates an eligible merge | `test_exact_request_produces_deterministic_no_write_plan`; CLI fixture probe; credential-free fixture produced `outcome: planned` with `no_writes: true`. | COMPLIANT |
| Explicit recovery | Identity mismatch fails closed | `test_preflight_rejects_remote_identity_or_graph_mismatch`; CLI expected-identity gates; all preflight transport calls are GET-only before any POST. | COMPLIANT |
| Idempotent recovery | Repeated recovery is a no-op | `test_live_execution_is_tag_then_release_and_rerun_is_no_op`; loopback adapter. | COMPLIANT locally; hosted concurrency remains operator evidence. |
| Idempotent recovery | Conflicting resource blocks recovery | `test_conflicting_resources_are_never_replaced`; `test_conflicting_remote_identity_fails_before_writes`. | COMPLIANT |
| Provenance/publication | Verified artifacts publish in Cargo → npm → OCI order | `test_publication_contract_is_serial_and_at_most_once_per_release_identity`; checksum/asset tests; `release-publish.yml:202` uses full `tags/${RELEASE_REF}` (no `v` stripping). | COMPLIANT locally; hosted registry/image behavior is unavailable. |
| Provenance/publication | Verification failure prevents later writes | checksum negative tests, OCI failure tests, dependency-chain inspection; `release-publish.yml:374` `needs:` chain and `if: always()` fail-stop inventory. | COMPLIANT locally; hosted registry/image behavior is unavailable. |
| Safe rollback | Partial publication is halted and recorded | `test_publication_failure_inventory_declares_schema_and_every_immutable_target` (`tests/release_recovery_safety_tests.py:54`) asserts schema `publication-failure-inventory/v1` plus every required per-target field; runbook and audit-only job prohibit deletion/force-move/new identities. | COMPLIANT |
| Mutation audit semantics | Ambiguous write is audited as `mutation-unknown` | 6 executable assertions in `tests/recover_release_tests.py` (lines 298, 331, 508, 512, 535, 538) for tag and release exception paths. | COMPLIANT |

**Compliance summary**: 9/9 scenarios locally conformant. Hosted/operator evidence gaps remain
scoped to `sdd-qa`.

## Correctness review (spec first)

| Requirement | Status | Evidence |
|---|---|---|
| Release Please sole owner of canonical `vX.Y.Z` identity | COMPLIANT | `release-please-config.json:10` pins `"include-component-in-tag": false` for the root component; runtime harness enforces exact `v0.3.0`. |
| Independent authenticated live preflight | COMPLIANT locally | `GitHubRecoveryAdapter.preflight()` binds repository/default branch/PR/merge SHA/tree/blob/manifest/current graph/version files and artifact plan before POST; complete fake transport tests pass. Hosted evidence is unavailable. |
| Default dry-run has no external recovery mutation | COMPLIANT | Default workflow path has no recovery secret and the planner never calls mutation methods. |
| Idempotent tag/release reconciliation | COMPLIANT locally | Tag-then-release order, conflict refusal, rerun no-op, and convergence checks pass. Ambiguous release POST is now audited as `mutation-unknown`. |
| Mutation audit semantics | COMPLIANT | `scripts/recover_release.py:498-505` (create_tag), `:523-532` (create_release), and `:534-546` (post-release final preflight) all raise `mutation="mutation-unknown"`; covered by 6 executable assertions. |
| Provenance, versions, manifests, checksums | COMPLIANT locally | Historical 13-entry vs current 14-entry validation, synchronized version checks, Docker markers, archive manifests, byte checksums, and target matrix checks pass. |
| Ordered publication and fail-stop | COMPLIANT locally | Dependency order and negative contracts pass; `.github/workflows/release-publish.yml:202` queries the canonical tag with full `RELEASE_REF`; `needs:` chain enforces fail-stop. |
| Safe rollback/inventory | COMPLIANT | Runbook, audit-only inventory job with full per-target immutable fields, no deletion/force-move, target-native deprecation. |
| CodeGauge semantic boundary | COMPLIANT | No engine/provider/profile/schema files were changed; Cargo and npm gates passed. |

## Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Release Please is the only normal tag/release writer | Yes | Root config pinned; non-root paths use `skip-github-release: true`. |
| Historical snapshot is the recovery source of truth | Yes | GitHub adapter validates immutable historical tree and manifest independently. |
| Dry-run first and protected live path | Yes locally | Separate plan/live branches, exact confirmation, disabled-by-default repository variable, read-only plan token, and `release-recovery-live` environment declaration are present. Hosted environment approval settings cannot be verified locally. |
| Live recovery mutates only tag then release | Yes | Adapter exposes only the two POST boundaries and tests verify order/payloads. |
| Repository/identity concurrency guard | Yes locally | Workflow group derives from repository, tag, and merged SHA with `cancel-in-progress: false`; job lock path uses the same identity. |
| Cargo → npm → OCI order and stop chain | Yes | `needs:` chain and static/negative tests pass; hosted execution is unavailable. |
| Carrier validates/correlates and dispatches downstream | Yes | Carrier validates read-only and the canonical tag trigger starts publication directly. |
| No application/provider semantic changes | Yes | Changed-file boundary and locked language tests confirm this. |

## TDD compliance audit

| Metric | Status | Evidence |
|---|---|---|
| RED → GREEN evidence per task | Partial | `apply-progress.md` records RED → GREEN for Unit 3 and Phase 5 safety contracts, not every task. |
| Tests committed before or with production code | Cannot verify | Recovery files and tests are uncommitted in the dirty worktree. |
| Evidence production code was committed before tests | None found | No contrary commit sequence was found; this is not proof of every task's ordering. |
| Ambiguous release-write regression test | Present | `tests/recover_release_tests.py` lines 298, 331, 508, 512, 535, 538 assert `mutation-unknown` for tag and release exception paths. |

## Verdict table

Judge A is source/spec inspection. Judge B is executable evidence or a deterministic local
probe.

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Root release tag is exactly `v0.3.0`; non-root paths cannot create competing GitHub Releases | OK | OK | RESOLVED | Closed |
| Publisher provenance lookup uses the full canonical tag without stripping `v` | OK | OK | RESOLVED | Closed |
| Ambiguous `create_release` transport failure audited as `mutation-unknown` | OK | OK | RESOLVED | Closed |
| Publication failure inventory contains required per-target immutable output fields and artifact locations | OK | OK | RESOLVED | Closed |
| Default offline dry run does not independently validate remote version files/manifests | OK | OK | WARNING | Scoped limitation; live plan-only path covers it |
| Protected environment approval configuration cannot be verified locally | OK | OK | WARNING | Hosted/operator evidence required |
| Hosted GitHub, registry, OCI, and attestation behavior was not exercised | OK | OK | WARNING | Prohibited/unavailable in this phase |
| Quality runner, strict verifier module, and coverage are unavailable | OK | OK | WARNING | Manual `fallback` evidence only |
| Dry-run caller path still receives write-capable reusable-workflow permissions | OK | n/a | WARNING | Least-privilege hardening opportunity |
| Dirty worktree prevents independent TDD commit-order verification | OK | OK | WARNING | Apply-progress evidence is partial |
| Applied change exceeds the 400-line review budget | OK | OK | WARNING | Approx. 568 tracked diff lines plus 17 untracked files / 3,703 untracked lines |

## Issues found

### CRITICAL

None. All four previous CRITICAL blockers are resolved and covered by passing executable
tests in the current worktree.

### WARNING

- Evidence is manual `fallback`; the configured quality runner is disabled and coverage is
  not configured.
- No live GitHub preflight, canonical resource reconciliation, package publication, OCI push,
  or attestation was performed.
- The default fixture dry run is intentionally offline and validates request/snapshot shape;
  complete remote/version-file validation requires the explicit live `--plan-only` path.
- The `release-on-tag.yml` caller passes write-capable permissions to the reusable release
  workflow even when `dry_run` is true; the actual publication jobs are conditionally
  skipped, but the permission boundary is broader than the dry-run intent.
- Protected-environment required reviewers/settings are hosted configuration and cannot be
  proven from YAML alone.
- Strict-TDD commit ordering cannot be independently verified in the uncommitted dirty
  worktree.
- The applied payload is above the 400-line review budget; the approved dirty-main
  continuation and `auto-chain` forecast remain recorded in the task artifacts.

### SUGGESTION

- Keep hosted dry-run and operator acceptance in `sdd-qa`; do not authorize live recovery
  until `sdd-qa` accepts and the protected environment approves.
- Narrow the dry-run caller permissions to match the dry-run intent when feasible.

## Final verdict

**PASS WITH WARNINGS**

The four previous CRITICAL blockers are resolved and covered by passing executable tests in
the current worktree. Local build and test gates are green; compliance matrix is fully
conformant on the available executable evidence. Hosted and operator-only evidence gaps are
scoped warnings. Advance to `sdd-qa` for acceptance; do not archive or perform live recovery
until `sdd-qa` accepts.