# QA Report — Release Recovery Idempotent Ownership

**Change**: `release-recovery-idempotent-ownership`
**Mode**: OpenSpec; `fallback` manual capability evidence
**Phase**: `sdd-qa`
**Date**: 2026-08-30
**Working directory**: `/Users/acosta/Dev/agent-swarm/codegauge`

This report evaluates observable user/operator behavior for the change. It does not
authorize live recovery. Acceptance QA reads the proposal capabilities, delta spec,
design, and target surface and walks each one through a capability-driven scenario
matrix. Static inspection is **not** used to produce `PASS`. Manual `fallback`
evidence is used because the configured quality runner and strict verifier module
are unavailable.

## 1. Identity and handoff

| Field | Value |
|---|---|
| Change | `release-recovery-idempotent-ownership` |
| Phase | `sdd-qa` (after `sdd-verify` PASS WITH WARNINGS) |
| Verify verdict handoff | `PASS WITH WARNINGS`, no CRITICAL/P0/P1 issues |
| Verify report | `openspec/changes/release-recovery-idempotent-ownership/verify-report.md` |
| Apply progress | `openspec/changes/release-recovery-idempotent-ownership/apply-progress.md` |
| State | `current_phase: verify`, `next: qa`; QA now closes |
| Quality runner | `../openspec/quality-runner.json` exists with `enabled: false`; no standalone runner |
| Strict TDD verifier | unavailable in injected/local skill tree |
| Coverage tool | not configured |
| Authoritative historical identity | `yacosta738/codegauge`, branch `main`, PR `75`, merged SHA `cf46ba64bd2e723c28406ca6b7fc3c97d183f1d0`, historical tree `f9fca04cb359e843bd13ab7ff4db0ff1a9ba4a1c` |

## 2. Target, environment, permissions, and limitations

| Dimension | Value |
|---|---|
| Target repository | `yacosta738/codegauge` (hosted GitHub) |
| Target surface | recovery scripts, recovery workflow, release-publish workflow, runbook, fixtures |
| Local working tree | dirty-`main` continuation, applied Units 1–5 plus Phase 5 rework, all changes staged in working tree only |
| Local Git facts | `cf46ba6` is an ancestor of `HEAD`; historical tree object resolves; historical manifest has 13 entries (no `crates/codegauge-provider-typescript`); current manifest has 14 |
| Hosted environment | not exercised; QA phase explicitly out-of-scope for remote mutations |
| Credentials | no tokens provided; live recovery path requires `GH_TOKEN` and `vars.RELEASE_RECOVERY_LIVE_ENABLED=true`, both operator-controlled |
| Permission to mutate | **NONE** for QA; hosted/operator evidence is out of scope for this phase |
| Limitations | (a) hosted GitHub tag/release CRUD is operator-only; (b) hosted registry/OCI/attestation is operator-only; (c) protected environment reviewers cannot be proven from YAML alone; (d) `quality-runner/v1` is `enabled: false` |

## 3. Capability inventory

Selected capabilities must produce observable evidence (live execution, harness
output, exact string assertions, contract-level file inspection). Static lookups
are recorded as **inspect** and never produce `PASS`.

| Capability | State | Selected? | Rationale |
|---|---|---|---|
| Python contract test suite (`python3 -m pytest -q tests/*_tests.py`) | available | **yes** | The change ships 23 recovery/runtime/safety tests. Direct execution produces observable evidence. |
| Release Please 17.6.0 runtime harness (`tests/release_please_runtime_tests.py`) | available | **yes** | The harness binds the actual release-please 17.6.0 NPM package. It asserts exact `rootReleaseTag: v0.3.0`. |
| `actionlint` workflow validator | available | **yes** | YAML contracts and dependency chains must parse and pin actions. |
| `cargo fmt --all -- --check` | available | **yes** | Format gate is part of the locked repository contract. |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | available | **yes** | Locked Clippy with `-D warnings` is a quality gate. |
| `cargo check --workspace --locked` | available | **yes** | Type-check gate. |
| `python3 -m compileall -q scripts tests` | available | **yes** | Bytecode compile gate for shipped Python. |
| `git diff --check` | available | **yes** | Whitespace gate. |
| `git cat-file -t f9fca04c…` and `git show …:.release-please-manifest.json` | available | **yes** | Local Git is the authoritative source for the historical 13-entry manifest and tree. |
| Quality runner (`quality-runner/v1`) | unavailable | rejected | `enabled: false` per `openspec/quality-runner.json`; cannot produce deterministic envelopes. |
| Strict TDD verifier module | unavailable | rejected | Not present in the injected/local skill tree. |
| Coverage tool | unavailable | rejected | Not configured; cannot claim a coverage percentage. |
| Hosted GitHub tag/release CRUD | blocked | rejected | QA phase is explicitly out of scope for remote mutations; no hosted token in this environment. |
| Hosted Cargo/npm/OCI publish + attestation | blocked | rejected | QA phase is explicitly out of scope for remote mutations; no registry credentials. |
| Protected-environment reviewer configuration | blocked | rejected | Cannot be proven from YAML alone; hosted configuration. |
| Live recovery (`--execute-live` path) | blocked | rejected | Operator-only authorization; QA must not perform live recovery. |

## 4. Scenario matrix

Every row maps to one of the 10 capabilities from the user brief. Each result is
the QA status of observable evidence, not of static inspection. Evidence IDs
point to the artifact that produced the result.

| # | Capability | Scenario | QA Status | Evidence / Reason |
|---|---|---|---|---|
| 1 | Recovery validation/planning/locking/execution are fail-closed and idempotent for `v0.3.0` | dry-run produces deterministic `NO_WRITES` plan with exact repository, SHA, 13-entry historical identity, and 14-entry current graph | **PASS** | `tests/recover_release_tests.py:63` `test_exact_request_produces_deterministic_no_write_plan`; `:77` `test_matching_resources_converge_to_no_op`; `:259` `test_live_execution_is_tag_then_release_and_rerun_is_no_op`; live CLI loopback at `:651` proves GET-only transport refuses without independent preflight. CLI fixture at `fixtures/release-recovery/v0.3.0-dry-run-request.json` mirrors the historical identity (`yacosta738/codegauge`, `cf46ba64b…`, `f9fca04cb…`, PR `75`). File lock concurrency at `:420`. |
| 1 | Recovery validation/planning/locking/execution are fail-closed and idempotent for `v0.3.0` | live execution by request path is rejected; only `--execute-live` + `RECOVER_RELEASE_LIVE` confirmation is accepted | **PASS** | `scripts/recover_release.py:672-678` and `:683-684` (`GH_TOKEN` check); `tests/recover_release_tests.py:544` `test_live_cli_requires_protected_execution_flag`, `:560` `test_live_cli_requires_confirmation_marker`, `:615` `test_live_cli_requires_a_github_token`. |
| 2 | Release Please root tag is exactly unprefixed `v0.3.0`; non-root paths cannot create competing GitHub Releases | Release Please 17.6.0 emits canonical root tag and refuses to create component releases | **PASS** | `tests/release_please_runtime_tests.py:210` `test_release_please_17_6_0_harness_proves_unprefixed_root_release_tag` asserts `'"rootReleaseTag": "v0.3.0"' in result.stdout` and rejects `'"rootReleaseTag": "codegauge-root-v0.3.0"'`. Runtime harness reports `releaseCalls: 0`, `tagCalls: 0` (dry-run). Live execution prints `RELEASE PLEASE V17.6.0 RUNTIME TESTS: PASS`. `release-please-config.json:10` pins `include-component-in-tag: false` for the root `.` package; all non-root packages (lines 119–139) have `skip-github-release: true`. |
| 3 | Publisher provenance lookup uses the full canonical tag without stripping `v` | tag lookup uses `tags/${RELEASE_REF}` | **PASS** | `.github/workflows/release-publish.yml:202` `gh api "repos/${GITHUB_REPOSITORY}/git/ref/tags/${RELEASE_REF}"` (full tag including `v`); `${RELEASE_REF#v}` is used only for `RELEASE_VERSION` derivation (`:253`, `:306`, `:389`). Verified by string inspection of the workflow YAML and confirmed by re-running `tests/recover_release_github_tests.py`. |
| 4 | Ambiguous `create_release` transport failures are audited as `mutation-unknown` | ambiguous POST exceptions and post-write final preflight failures raise `mutation="mutation-unknown"` | **PASS** | `scripts/recover_release.py:498-505` (`create_tag` ambiguous POST), `:523-532` (`create_release` ambiguous POST), `:534-546` (post-release final preflight). 6 executable assertions in `tests/recover_release_tests.py` at lines `:298`, `:331`, `:508`, `:512`, `:535`, `:538` (also `:540` recovery-guidance substring). The remaining `partial-failure` paths describe known-good create_tag + known-bad preflight, not ambiguous writes. |
| 5 | Publication failure inventory contains required immutable per-target fields and artifact locations | `publication-failure-inventory/v1` artifact lists every Cargo/npm/OCI target with required fields | **PASS** | `tests/release_recovery_safety_tests.py:54` `test_publication_failure_inventory_declares_schema_and_every_immutable_target` asserts schema, six required per-target fields, and enumerates 24 expected targets. Workflow `.github/workflows/release-publish.yml:371-552` writes the JSON with `needs:` chain and `if: always()`. Embed-smoke check in `apply-progress.md:147-148` reports valid 42-row JSON. |
| 6 | Default offline dry run is non-mutating; explicit live `--plan-only` is the only authenticated live preflight | dry-run plan never calls `create_tag` / `create_release`; live CLI without `--execute-live` is rejected | **PASS** | `scripts/recover_release.py:486-491` dry-run returns `plan_recovery(...)` without adapter mutation; `:701-705` requires `--snapshot` for dry-run; `:672-684` requires `--execute-live` for live and checks `GH_TOKEN`. `tests/recover_release_tests.py:365` `test_dry_run_never_calls_mutation_methods`, `:544` `test_live_cli_requires_protected_execution_flag`, `:586` `test_dry_run_cli_supports_an_explicit_no_write_plan`. |
| 7 | Recovery workflow declares the protected `release-recovery-live` environment, requires `RECOVER_RELEASE_LIVE`, exact confirmation, and least-privilege permissions | workflow gates and perms | **PASS** | `.github/workflows/release-recovery.yml:160` `environment: name: release-recovery-live`; `:121-130` `vars.RELEASE_RECOVERY_LIVE_ENABLED` check; `:154` `inputs.confirm_live == 'RECOVER_RELEASE_LIVE'`; `:43-44` workflow-scope `contents: read`; `:56-57` plan job `contents: read`; `:158-159` recover job `contents: write` only on the protected env. Concurrency group at `:48` keyed by repository + release_tag + merged_sha with `cancel-in-progress: false`. Tests `tests/release_recovery_safety_tests.py:28` and `:108` cover both the protected environment + disabled-by-default gate and the dry-run section's freedom from `RELEASE_PLEASE_TOKEN`. |
| 8 | Runbook documents disable, rollback, immutable-resource, and deprecation procedure without authorizing live recovery | runbook sections | **PASS** | `docs/release-recovery-runbook.md:18` "Disable live recovery", `:25` "Never delete or force-move", `:35` "Stop later publication stages", `:40` "Partial publication response", `:49` "Inventory immutable outputs", `:57` "Target deprecation and rollback". `tests/release_recovery_safety_tests.py:14` `test_rollback_runbook_documents_disable_preserve_stop_inventory_and_deprecation` enumerates the sections. The runbook never authorizes live recovery; it requires protected environment approval and an explicit live authorization marker. |
| 9 | Historical identity contract: repo, branch, PR, SHA, tree, manifest counts | local Git identity | **PASS** | `git cat-file -t f9fca04c…` returns `tree`; `git show f9fca04c…:.release-please-manifest.json` parses 13 entries (no `crates/codegauge-provider-typescript`); current `.release-please-manifest.json` has 14 entries; `git merge-base --is-ancestor cf46ba6 HEAD` returns 0 (cf46ba6 is an ancestor of HEAD); `git log cf46ba6 -1` reports `chore: release main (#75)`. |
| 10 | No application/provider semantic changes; locked language and provider gates pass | diff boundary and locked gates | **PASS** | `git diff --name-only` lists only: `.github/workflows/{release-publish,release-tag-carrier}.yml`, `release-please-config.json`, `scripts/verify_release_provenance.py`, and 5 test files. No `crates/**/{src,tests}/**`, `npm/codegauge/**`, or `schemas/**` paths were modified. `cargo test --workspace --locked` (run prior) passed; `cargo fmt --all -- --check` exits 0; `cargo clippy --workspace --all-targets --locked -- -D warnings` exits 0; `cargo check --workspace --locked` exits 0. |
| — | Whole-suite regression | all 98 Python tests pass | **PASS** | `python3 -m pytest -q tests/*_tests.py` → `98 passed in 10.41s`. |

## 5. Untested scope and rerun prerequisites

Hosted, operator-only, or out-of-scope evidence is recorded here. The QA verdict
does not depend on any of these items.

| Scenario | QA status | Reason | Rerun prerequisite |
|---|---|---|---|
| Hosted GitHub tag `refs/tags/v0.3.0` exists and points to `cf46ba64b…` | **NOT TESTED** | Live recovery is operator-only; QA must not perform remote mutations. | After `vars.RELEASE_RECOVERY_LIVE_ENABLED=true` and protected-environment approval, run the live workflow with `confirm_live=RECOVER_RELEASE_LIVE`. |
| Hosted GitHub Release for `v0.3.0` exists with matching identity | **NOT TESTED** | Same as above. | Same as above. |
| Hosted crates.io `codegauge-*` crates published for `0.3.0` | **NOT TESTED** | Cargo registry credentials and live workflow not exercised. | Operator runs the publish workflow; checks crates.io owner console. |
| Hosted npm `@yacosta738/codegauge*` packages published for `0.3.0` | **NOT TESTED** | npm token and live workflow not exercised. | Operator runs the publish workflow; checks npmjs.com. |
| Hosted GHCR `ghcr.io/yacosta738/codegauge:0.3.0{,-amd64,-arm64,-latest}` published and attested | **NOT TESTED** | OCI registry credentials not exercised. | Operator runs the publish workflow; inspects GHCR digests. |
| `release-recovery-live` protected-environment reviewers configuration | **BLOCKED** | Hosted configuration; not derivable from YAML. | Operator verifies GitHub repository settings → Environments. |
| Quality runner `quality-runner/v1` envelopes | **NOT TESTED** | `enabled: false`; control plane disabled. | Enable the runner (`openspec/quality-runner.json:enabled=true`) and rerun `sdd-verify` + `sdd-qa`. |
| Strict TDD verifier module commit-ordering report | **NOT TESTED** | Module not present in the injected/local skill tree. | Wire the strict verifier; rerun. |
| Code coverage threshold | **NOT TESTED** | No coverage tool configured. | Add `cargo-llvm-cov` (or equivalent); rerun. |
| Independent TDD commit-order audit (per-task RED→GREEN) | **BLOCKED** | The dirty worktree prevents post-hoc `git log` reconstruction. | Commit the changes and rerun. |

## 6. Findings

Severity uses the SDD scale `CRITICAL`, `P0`, `P1`, `P2`, `P3`. `CRITICAL` and
`P0`/`P1` block archive; `P2`/`P3` are warnings unless config says otherwise.

| ID | Severity | Description | Status | Evidence |
|---|---|---|---|---|
| F-QA-01 | P3 | The default fixture dry-run is offline and validates request/snapshot shape only; complete remote/version-file validation requires the explicit live `--plan-only` path. | OPEN (warning) | `tests/recover_release_tests.py:701-705` requires snapshot only for dry-run; verify-report warning table line 4. |
| F-QA-02 | P3 | Protected-environment approval configuration cannot be verified from YAML alone. | OPEN (warning) | Hosted-only. |
| F-QA-03 | P3 | Hosted GitHub, registry, OCI, and attestation behavior was not exercised. | OPEN (warning) | QA is out of scope for remote mutations. |
| F-QA-04 | P3 | Quality runner, strict verifier module, and coverage tool are unavailable. | OPEN (warning) | All three disabled/missing. |
| F-QA-05 | P3 | The `release-on-tag.yml` caller passes write-capable permissions to the reusable release workflow even when `dry_run` is true; the publication jobs are conditionally skipped, but the permission boundary is broader than the dry-run intent. | OPEN (warning) | Carryover from verify-report warning table. Not in scope for this change. |
| F-QA-06 | P3 | Dirty worktree prevents independent TDD commit-order verification. | OPEN (warning) | `git status` reports 9 modified + 9 untracked. |
| F-QA-07 | P3 | The applied payload is above the 400-line review budget; the `auto-chain` forecast and chained-PR rationale remain in `tasks.md`. | OPEN (warning) | Approx. 814 insertions + 60 deletions across 9 modified files plus 9 untracked files. |

No `CRITICAL`, `P0`, or `P1` findings.

## 7. Final verdict

**Verdict**: `PASS WITH WARNINGS`

**Rationale**:

- All 10 acceptance capabilities from the user brief have observable,
  executable evidence and are recorded as `PASS` (scenario matrix above).
- The 98-test Python suite, Release Please 17.6.0 runtime harness, locked Cargo
  gates (test/fmt/clippy/check), `actionlint`, `python3 -m compileall`, and
  `git diff --check` all pass locally.
- The four previous CRITICAL blockers from the prior verify report
  (`rootReleaseTag`, `RELEASE_REF#v` strip, `mutation-unknown` audit,
  publication-inventory fields) are resolved and covered by passing tests.
- The 7 open findings are all `P3` warnings. None are `CRITICAL`, `P0`, or `P1`.
- Hosted, operator-only evidence (live recovery, hosted tag/release CRUD,
  registry/OCI publication, protected-environment reviewers, quality-runner
  envelopes) is recorded as `NOT TESTED` or `BLOCKED` per the sdd-qa protocol
  and is not part of this verdict.

**Implementation handoff for `sdd-archive`**:

- `verify-report.md` and `qa-report.md` both exist; both are `PASS WITH WARNINGS`.
- No `CRITICAL`, `P0`, or `P1` findings are open. `P3` warnings are recorded in
  §6 and may be tracked in follow-up tasks but do not block archive.
- The recovery change is documentation/config-heavy plus a tightly scoped
  recovery workflow. The proposal explicitly authorizes a docs/config-only-style
  exception framing for archive if the operator decides the warnings are
  non-blocking. By SDD policy, documentation/config-only changes MAY proceed
  with explicit rationale and a visible warning; this change touches both code
  and config and is therefore **not** the docs/config-only exception — the
  verdict here is `PASS WITH WARNINGS`, and the gate is clean.
- Do not authorize live recovery from this report. Live recovery requires
  `vars.RELEASE_RECOVERY_LIVE_ENABLED=true`, the protected-environment approval,
  and an explicit operator invocation.

## 8. Skill resolution and self-checks

- Skill resolution: `none` (the orchestrator injected no `## Project Standards`
  block; this phase skill runs standalone with the SDD common protocol).
- Static-inspection check: no scenario received `PASS` from static inspection
  alone. Every `PASS` is backed by an executable test, a contract assertion in
  the test files, or a verifiable local Git/file fact.
- Mutation check: zero remote mutations were performed. No tag, release, push,
  commit, registry write, OCI push, or publication was attempted.
- Output ordering: this report is the final phase artifact; it precedes the
  return envelope.