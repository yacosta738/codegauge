# Acceptance QA Report: `codegauge-distribution`

## 1. Identity

| Field | Value |
|---|---|
| Change | `codegauge-distribution` (R-F6) |
| Mode | OpenSpec |
| Phase | `sdd-qa` — Phase 15 hosted-evidence acceptance update |
| Date | 2026-08-15 |
| Target branch | `chore/release-record-hosted-replay` |
| Target checkout | `/Users/acosta/Dev/agent-swarm/codegauge` |
| Target HEAD | `8d1773413bbaa63661588b369d1c12bab2e2856e` |
| Final QA verdict | `BLOCKED` |

This is independent acceptance QA for observable local and explicitly evidenced hosted behavior. It does
not claim full operator, registry, publication, or product acceptance.

## Latest authoritative Phase 15 hosted-evidence acceptance update — 2026-08-15

### Identity and technical-verification handoff

- Change: `codegauge-distribution` (R-F6), OpenSpec mode, branch
  `chore/release-record-hosted-replay`.
- Target: `/Users/acosta/Dev/agent-swarm/codegauge`, corrected `main` checkout
  `HEAD=8d1773413bbaa63661588b369d1c12bab2e2856e`.
- Technical handoff: `verify-report.md` supplies **PASS WITH WARNINGS** local verification for the
  corrected private-hunk and npm-formatting parser boundaries. It remains technical evidence only;
  this update records the new hosted acceptance evidence.
- Required artifacts read: proposal, all five delta specs, design, tasks, verify report, prior QA
  report, `state.yaml`, and `openspec/config.yaml`.
- New concise evidence: `qa-evidence/2026-08-15-replay/phase-15-hosted-replay.json`.

### Target, environment, permissions, and limitations

- Host: macOS arm64; this change has no application-under-test, browser, HTTP API, data-store,
  locale, or persistence surface.
- Corrected hosted push run `31891322236` completed `SUCCESS` as a no-op at the corrected main SHA.
- Corrected hosted replay run `31891343893` was a successful `workflow_dispatch` on `main` with
  `replay_sha=fcc91b4850480945ae484c3ebdba18f8a4e38270` and `dry_run=true`; its validation and plan
  steps passed, while tag and label mutations were skipped.
- The replay plan records `replay=true`, `source_checkout_sha=8d1773413...`, the historical event SHA,
  `canonical_tag_ref=skipped`, `version_pr_label=skipped`, release workflow `not-dispatched`, and
  upload/publication/attestation `not-started`. It contains no credential values.
- Read-only GitHub inspection found no GitHub releases and no `v0.2.0` tag; local canonical tags are
  also absent. The temporary `RELEASE_CARRIER_DRY_RUN=true` variable was removed after the successful
  rehearsal; no live carrier run was performed.
- The orchestrator performed only the authorized dry-run dispatch and removed the temporary variable
  afterward. No tag/release creation, publication, upload, attestation, credential injection, or live
  carrier execution occurred.

### Capability inventory

| Capability | Availability | Selection | Rationale / disposition |
|---|---|---|---|
| Hosted ordinary-main carrier run | available | selected | Read-only observation of successful no-op run `31891322236`. |
| Hosted historical replay/dry-run | available | selected | Read-only observation of successful run `31891343893` with the approved replay SHA. |
| Hosted carrier plan/summary evidence | available | selected | Machine-readable plan facts prove current source SHA, replay SHA, validation, and skipped/not-started mutations. |
| Corrected private hunk-only parser | available | selected | The hosted replay reached and passed merged-tree/version-PR validation on corrected main. |
| Corrected npm hunk-only formatting parser | available | selected | The hosted replay reached and passed the same corrected Stage-B validation boundary for PR `#59`. |
| Existing local executable QA harnesses | available | selected | Prior independent local evidence remains the carry-forward baseline for Cargo, npm, OCI, archives, and parser negatives. |
| Read-only GitHub metadata | available | selected | Run status, conclusion, SHA, tag, and release state were queried without mutation. |
| Workflow/actionlint/ShellCheck/Dockerfile diagnostics | available | selected as diagnostics | Static-only checks remain `NOT TESTED` in the scenario matrix, even when clean. |
| Live tag/release/publication providers | available in principle | rejected | Explicit no-live-write boundary; no tag, release, registry, upload, or attestation action was authorized. |
| Native non-host targets | unavailable | rejected | No executable native/cross-target matrix was supplied. |
| Failure injection, rollback, and runtime secret-isolation rehearsal | unavailable | rejected | Requires protected provider state, credentials, and mutation. |
| Browser/accessibility/responsive/locale/API/data/persistence | unavailable | rejected | No corresponding product surface exists for this distribution/CLI/workflow change. |

### Incremental scenario matrix

| ID | Category | Scenario | Result | Evidence or reason |
|---|---|---|---|---|
| QA-P15-01 | hosted happy path/state transition | A corrected-main push with no matching Release Please carrier event completes as an auditable no-op without entering validation or mutation. | PASS | Run `31891322236` completed `SUCCESS`/no-op at `8d1773413...`; carrier validation, plan, tag, and label steps were skipped. |
| QA-P15-02 | hosted replay/state identity | Manual replay selects historical event `fcc91b4850480945ae484c3ebdba18f8a4e38270` while checking out current corrected main `8d1773413...`. | PASS | Run `31891343893`, `workflow_dispatch`, `refs/heads/main`, `headSha=8d1773413...`; carrier plan records `replay=true`, both SHAs, and `dry_run=true`. |
| QA-P15-03 | hosted parser boundary | The corrected private conformance hunk-only and base npm hunk-only formatting boundaries accept the real PR `#59` replay input. | PASS | Run `31891343893` passed merged-tree/version-PR validation on the corrected parser/npm commits; no pre-fix rejection occurred. |
| QA-P15-04 | hosted dry-run/no-write | Replay validates and computes the canonical `v0.2.0` plan without creating a tag, changing the carried PR label, dispatching downstream release, uploading, publishing, or attesting. | PASS | Replay validation and plan steps passed; `canonical_tag_ref` and `version_pr_label` are `skipped`, release workflow is `not-dispatched`, and upload/publication/attestation are `not-started`. |
| QA-P15-05 | hosted state boundary | Canonical live tag delivery and the downstream tag-triggered release workflow are observed. | BLOCKED | The temporary dry-run variable was removed after rehearsal, but no live carrier was authorized; no `v0.2.0` tag or GitHub Release exists. |
| QA-P15-06 | registry/publication | Cargo registry, npm, GitHub Release, GHCR, and dependent Cargo registry verification complete. | BLOCKED | Publication/uploads and registry credentials remain prohibited; synchronized runtime crates are not available in the public index. |
| QA-P15-07 | native target | All eight archive targets have executable native/cross-target runtime evidence. | BLOCKED | Only prior structural archive evidence exists; seven non-host target executions remain unrun. |
| QA-P15-08 | security | Hosted secret isolation, attestation, and credential-bearing promotion behavior are observed at runtime. | BLOCKED | The replay plan is credential-free, but protected secret isolation and attestation require a separate hosted/provider rehearsal. |
| QA-P15-09 | interrupted/rollback | Failure injection stops later channels and produces provider-backed recovery/rollback evidence. | BLOCKED | Disposable publication state and mutation were not authorized. |
| QA-P15-10 | workflow/security diagnostic | Immutable pins, permissions, actionlint, ShellCheck, and Dockerfile checks are acceptance behavior. | NOT TESTED | These remain static diagnostics; policy forbids recording static inspection as QA `PASS`. |
| QA-P15-11 | browser/accessibility/locale/persistence | Browser, accessibility, responsive, internationalization, API, data, or persistence behavior is exercised. | NOT TESTED | Not applicable: no such product surface exists. |

The prior Phase 14 executable local matrix remains the carry-forward evidence for the corrected local
parser/content boundaries, Release Please `17.6.0` harness, Cargo, npm, OCI, archive, package, and
negative behavior. No new local failure contradicts that evidence; this update upgrades only the
hosted no-op/replay/dry-run and corrected parser/npm capabilities supported by the two hosted runs.

### Untested and blocked scope

| Scope | Result | Rerun prerequisite |
|---|---|---|
| Corrected Stage-A/version-PR creation and zero-artifact lifecycle on corrected main | BLOCKED | Separately authorized protected Stage-A run; inspect the actual PR and zero release/tag calls. |
| Canonical live tag delivery and downstream release workflow | BLOCKED | Authorized live carrier event with `RELEASE_CARRIER_DRY_RUN=false`/unset and downstream run at the validated SHA. |
| Cargo/npm/GitHub Release/GHCR publication and dependent Cargo registry graph | BLOCKED | Approved release window, provider-safe namespace, scoped credentials, and staged/published synchronized crates. |
| Native evidence for seven non-host archives | BLOCKED | Native/cross-target runner matrix with executable evidence per declared target. |
| Attestation and hosted secret isolation | BLOCKED | Protected provider-backed execution with observable redacted logs and job permissions. |
| Failure injection and rollback | BLOCKED | Disposable provider-backed rehearsal recording stop order and recovery actions. |
| Workflow static diagnostics as runtime acceptance | NOT TESTED | A runtime scenario that exercises the protected workflow; static checks alone cannot change this result. |
| Browser/accessibility/responsive/locale/persistence | NOT TESTED | No rerun unless the change gains a corresponding product surface. |

### Findings

| ID | Severity | Finding | Status |
|---|---|---|---|
| QA-P15-001 | P1 | Corrected Stage-A/version-PR creation was not re-executed; the new evidence is a carrier replay of the already merged PR, not a new Stage-A run. | Open — acceptance blocker; protected Stage-A rehearsal required. |
| QA-P15-002 | P1 | Canonical live tag delivery and downstream release provenance remain unobserved because dry-run mode is still active. | Open — acceptance blocker; live carrier and downstream run required. |
| QA-P15-003 | P1 | Cargo/npm/GitHub Release/GHCR publication, final OCI state, and dependent Cargo registry verification remain unavailable. | Open — acceptance blocker; approved registry/provider rehearsal required. |
| QA-P15-004 | P1 | Seven non-host archive targets lack executable native evidence. | Open — target matrix evidence required. |
| QA-P15-005 | P1 | Hosted secret isolation, attestation, failure propagation, and rollback are not observed. | Open — disposable protected rehearsal required. |
| QA-P15-006 | P2 | Static workflow/security diagnostics cannot be promoted to acceptance results. | Open warning — no executable defect observed. |

No `FAIL` result and no `CRITICAL`/P0 implementation finding was observed. The new hosted replay and
push no-op are successful observable behaviors; the remaining P1 findings are acceptance blockers
caused by deliberately unrun live/provider/native scopes.

### Phase 15 verdict and implementation handoff

**Verdict: `BLOCKED`.** The corrected hosted replay, dry-run no-write boundary, ordinary-main no-op,
and corrected private/npm patch parser paths now have hosted success evidence. Acceptance remains
blocked by the deliberately unobserved live tag/downstream flow, Stage-A rerun, publication and
dependent registry graph, native targets, attestation/secret isolation, failure injection, and
rollback.

QA did not change source or workflows. The orchestrator performed only the authorized dry-run dispatch
and temporary-variable cleanup; no tags, releases, registries, credentials, or live carrier execution
were used. `sdd-archive` must remain gated; this is a production distribution change, not a
documentation/config-only exception, and no product or release acceptance is claimed.

### Orchestration decision recorded — 2026-08-15

The operator chose to stop at `qa` rather than execute `sdd-archive`. The authorized scope was the
protected dry-run rehearsal only; any live release will be performed manually by the operator under
their own authorization. Archive is intentionally deferred because six P1 blockers remain open and
the QA verdict is `BLOCKED`, which would otherwise violate the policy that requires `QA policy-allowed`
and no unresolved `CRITICAL/P0/P1` findings before archive. This section makes the decision explicit so
it is not silently re-interpreted as acceptance by a future reviewer or session.

## Historical Phase 14 independent acceptance QA — 2026-08-15

### Identity and technical-verification handoff

- Change: `codegauge-distribution` (R-F6), OpenSpec mode, branch
  `fix/release-carrier-private-patch-context`.
- Target: `/Users/acosta/Dev/agent-swarm/codegauge`, `HEAD=aa27efe0f6ce10707abd1c19f5b020a4db8dfa46`.
- Technical handoff: `verify-report.md` reports local **PASS WITH WARNINGS** for the Phase 13 npm
  formatting correction; it does not claim hosted replay, publication, or operator acceptance.
- Source artifacts read: proposal, all five delta specs, design, tasks, apply progress, verification
  report, state, and `openspec/config.yaml`.
- No application-under-test environment or general acceptance runner exists. This QA therefore uses
  only observable repository-local harnesses and package/runtime probes; static inspection is never
  recorded as a QA pass.

### Target, environment, permissions, and limitations

- Host/toolchain: macOS arm64; Rust/Cargo `1.97.1`; Node `24.19.0`; npm `11.17.0`; Python `3.14.7`;
  Docker `29.7.2`; actionlint `1.7.12`; ShellCheck `0.11.0`.
- Target version: `0.2.0`; local canonical `v*.*.*` tag list is empty.
- The real PR `#59` files API was fetched with a read-only unauthenticated GET. The raw response and
  normalized list are saved in `qa-evidence/2026-08-15-replay/phase-14-qa-pr59-files-api.json` and
  `.log`; the current validator accepted all 31 entries.
- Hosted runs `31886141725` and `31888439750` are recorded **only as historical pre-fix failures**:
  respectively the valid private hunk omitted optional trailing context, and the valid base npm hunk
  mixed seven version pairs with Release Please's deterministic `files` formatting. No corrected
  hosted replay success is claimed for either run.
- No dispatch, merge, push, variable mutation, tag/release creation, publication, upload, attestation,
  credential-bearing run, or live carrier execution occurred. QA did not modify source or workflows.

### Capability inventory

| Capability | Availability | Selection | Rationale / disposition |
|---|---|---|---|
| Read-only real PR `#59` files API | available | selected | Validates the exact 31-entry response, patches, counts, and filename-bound identity locally. |
| Stage-B hunk/parser/content validator | available | selected | Executes the exact npm/private positive and fail-closed mutation matrix. |
| Exact Release Please `17.6.0` fake-SCM harness | available | selected | Observes the package chain, update paths, private pins, npm pins, and zero release/tag calls. |
| Carrier correlation, replay, and mode resolver | available | selected | Exercises push/manual/replay identity and invalid replay boundaries without GitHub writes. |
| Dry-run plan and no-write guard | available | selected | Runs extracted checked-in plan/guard steps with a fake GET-only `gh`. |
| Cargo workspace runtime and package preflight | available | selected | Runs locked quality gates and five workflow-equivalent local patched package checks. |
| npm wrapper and package dry-run | available | selected | Runs typecheck, six wrapper tests, and all seven `npm pack --dry-run` checks. |
| OCI executable regression layers | available | selected | Runs local OCI positive, static, evidence, and failure-boundary suites without registry writes. |
| Archive/checksum structural packaging | available | selected | Generates and verifies eight local archive/sidecar pairs and a tamper rejection. |
| Workflow/actionlint/ShellCheck/Dockerfile diagnostics | available | selected as diagnostics | Commands are useful evidence, but static-only results are reported as `NOT TESTED`. |
| Read-only Git metadata | available | selected | Records branch, HEAD, dirty boundary, diff check, and empty local canonical tags. |
| Hosted GitHub Actions/carrier/replay | unavailable | rejected | No authorized hosted target; user prohibited dispatch and live execution. |
| Cargo/npm/GitHub Release/GHCR publication | available in principle | rejected | Explicit no-publication/no-upload boundary. |
| Native non-host targets | unavailable | rejected | No native/cross-target runtime matrix was supplied; seven archive executions remain unrun. |
| Attestation, failure injection, rollback | unavailable | rejected | Requires protected provider state and mutation, both prohibited. |
| Browser/accessibility/responsive/locale/API/data/persistence | not applicable | rejected | This change has no corresponding product surface. |

### Scenario matrix

`PASS` is reserved for executable local behavior. `BLOCKED` means the target, permission, provider, or
environment was unavailable or explicitly prohibited. `NOT TESTED` means the scenario is not applicable
or only static inspection was available.

| ID | Category | Scenario | Result | Evidence or reason |
|---|---|---|---|---|
| QA-P14-01 | happy path/boundary | Exact real PR `#59` GitHub files API response has 31 entries and the current Stage-B validator accepts the complete list. | PASS | `phase-14-qa-pr59-files-api.json` and `.log`; `file_count=31`, validation `PASS`. |
| QA-P14-02 | happy path | Base `npm/codegauge/package.json` has seven approved version pairs and exactly the compact-to-three-line `files` rewrite, with API counts `10/8/18`. | PASS | Raw API patch plus normalized log lines 42–73; exact formatting only. |
| QA-P14-03 | negative/boundary/security | Arbitrary base formatting, unapproved keys, duplicate keys, wrong versions, truncated npm hunks, and platform formatting are rejected. | PASS | `phase-14-qa-npm-negative-matrix.json`; 8 negative cases rejected with fail-closed errors. |
| QA-P14-04 | negative/private boundary | Private conformance package/version/publish/path/key/feature mutations remain rejected while the exact four-pin hunk is accepted. | PASS | Focused carrier log and npm-negative matrix; private mutations are explicitly rejected. |
| QA-P14-05 | state transition | Exact Release Please `17.6.0` harness produces one synchronized fake PR, 32 local generated paths, four private pin edits, six npm rewrites, and zero release/tag calls. | PASS | `phase-14-qa-focused.log`; package `17.6.0`, `synchronizedPullRequests=1`, `releaseCalls=0`, `tagCalls=0`. |
| QA-P14-06 | state/security boundary | Carrier push/manual modes, valid historical replay identity, malformed/out-of-mode replay rejection, and total replay schema behave as specified. | PASS | `phase-14-qa-focused.log` and checked-in mode suite; no hosted replay is implied. |
| QA-P14-07 | repeated/no-write | Manual dry-run validates the 31-file fixture, plans `v0.2.0`, and skips every mutation. | PASS | `phase-14-qa-dry-run-plan.json`, `phase-14-qa-dry-run-gh-calls.log`, and summary; two fake GETs, no POST/PUT. |
| QA-P14-08 | happy/negative | Locked Cargo metadata, 31 workspace tests, check, fmt, Clippy, CLI contracts, and private `0.1.0` identity pass. | PASS | `phase-14-qa-cargo.log`; exit `0`, no failed/skipped workspace tests. |
| QA-P14-09 | package boundary | Five runtime Cargo packages pass workflow-equivalent local patched packaging/verification without publication. | PASS | `phase-14-qa-cargo-package.log`; all five packages verified. |
| QA-P14-10 | package/negative | Dependent Cargo package verification against the synchronized public registry graph is observed. | BLOCKED | No synchronized crates are published in the current crates.io index; publication was prohibited. |
| QA-P14-11 | happy/negative | npm wrapper resolves/rejects targets and preserves passthrough; seven package dry-runs complete. | PASS | `phase-14-qa-npm-wrapper.log` and seven `phase-14-qa-npm-pack-*.log` files; six tests and seven packs pass. |
| QA-P14-12 | happy/negative | Local OCI positive, evidence, metadata, non-root, and failure suites pass without registry access. | PASS | `phase-14-qa-oci.log`; four executable suites pass. |
| QA-P14-13 | package/negative | Eight archive/sidecar pairs verify locally and byte tampering is rejected. | PASS | `phase-14-qa-archive-structural.json`; `8/8` verified and tamper rejected. |
| QA-P14-14 | workflow/security diagnostic | Immutable workflow pins, permissions, ShellCheck, actionlint, Dockerfile, and whitespace checks are clean. | NOT TESTED | `phase-14-qa-workflow-diagnostics.log` exited `0`, but static-only inspection cannot produce QA `PASS`. |
| QA-P14-15 | hosted state transition | Corrected hosted replay of the actual PR `#59` boundary is observed. | BLOCKED | Runs `31886141725` and `31888439750` remain pre-fix failures only; no dispatch or hosted success evidence exists. |
| QA-P14-16 | hosted state transition | Downstream canonical tag delivery and tag-triggered release workflow are observed. | BLOCKED | No tag/ref, workflow delivery, or hosted target was authorized. |
| QA-P14-17 | native target | All eight archive targets have executable native/cross-target runtime evidence. | BLOCKED | Structural archives pass, but seven non-host executions remain `not-run`; no native target matrix exists. |
| QA-P14-18 | registry/publication | Cargo registry, npm, GitHub Release, and GHCR publication plus dependent verification are observed. | BLOCKED | Publication/upload and registry credentials are explicitly prohibited. |
| QA-P14-19 | security | Hosted credential isolation and attestation are observed at runtime. | BLOCKED | Requires protected hosted/provider execution and credentials. |
| QA-P14-20 | interrupted/rollback | Failure injection stops later channels and produces provider-backed rollback/recovery evidence. | BLOCKED | Disposable publication state and mutation are unavailable/prohibited. |
| QA-P14-21 | browser/accessibility/locale/persistence | Browser, accessibility, responsive, internationalization, API, data, or persistence behavior is exercised. | NOT TESTED | No such surface exists for this distribution/CLI/workflow change. |

### Untested and blocked scope

| Scope | Result | Rerun prerequisite |
|---|---|---|
| Corrected hosted Stage-A/version-PR rerun and hosted PR `#59` validation | BLOCKED | Separately authorized protected GitHub run; inspect zero Stage-A release/tag calls and corrected hunk acceptance. |
| Hosted ordinary-main carrier and dry-run historical replay | BLOCKED | Authorized protected events; replay must be manual on `main` with `dry_run=true` and the approved SHA. |
| Downstream tag delivery and release workflow | BLOCKED | Authorized canonical carrier/tag event and downstream run at the validated SHA. |
| Native target execution for seven non-host archives | BLOCKED | Native/cross-target runner matrix with executable evidence per target. |
| Dependent Cargo registry verification | BLOCKED | Staged/published synchronized runtime crates or an equivalent isolated registry rehearsal. |
| Cargo/npm/GitHub Release/GHCR publication | BLOCKED | Approved release window, provider-safe namespace, and scoped credentials. |
| Attestation and hosted secret isolation | BLOCKED | Protected provider-backed execution with observable redacted logs. |
| Failure injection and rollback | BLOCKED | Disposable provider-backed rehearsal recording stop order and recovery. |
| Browser/accessibility/responsive/locale/persistence | NOT TESTED | No rerun unless the change gains a corresponding product surface. |

### Findings

| ID | Severity | Finding | Status |
|---|---|---|---|
| QA-P14-001 | P1 | Corrected hosted replay/carrier acceptance is not observable; both named hosted runs are historical pre-fix failures only. | Open — acceptance blocker; protected hosted rerun required. |
| QA-P14-002 | P1 | Downstream tag delivery, registry/publication, release assets, attestation, and dependent Cargo registry verification are unavailable. | Open — acceptance blocker; explicitly prohibited in this QA. |
| QA-P14-003 | P1 | Seven non-host archive targets lack executable native/cross-target runtime evidence. | Open — target matrix evidence required. |
| QA-P14-004 | P1 | Hosted security isolation, failure propagation, and rollback are not observed. | Open — disposable protected rehearsal required. |
| QA-P14-005 | P2 | Workflow/actionlint/ShellCheck/Dockerfile checks are static diagnostics and cannot be promoted to QA acceptance results. | Open warning — no local executable defect observed. |

No local executable scenario failed, and no `CRITICAL`/P0 implementation finding was observed. The P1
findings are acceptance blockers caused by missing or prohibited external state, not a claim that the
corrected local validator failed.

### Phase 14 verdict and implementation handoff

**Verdict: `BLOCKED`.** The requested local executable capabilities pass, including the exact live PR
`#59` 31-file response, seven-pair npm formatting boundary, npm/private negative matrix, Release Please
`17.6.0`, carrier/replay/mode behavior, dry-run no-write plan, Cargo, npm, OCI, archive, and package
checks. Production acceptance remains blocked by the explicitly unrun hosted replay, downstream tag
delivery, native target evidence, registry/publication, attestation, dependent Cargo registry graph,
failure injection, and rollback scenarios.

QA made no source, workflow, variable, credential, tag, release, registry, or live-carrier changes.
`sdd-archive` must remain gated until the P1 acceptance blockers are resolved or an explicit policy
exception is recorded; this is not a documentation/config-only exception and no product acceptance is
claimed.

## Phase 13 verification handoff — 2026-08-15

This is a handoff update, not an independent QA rerun. The current dirty checkout has a fresh technical
verification result for the second hosted replay regression, while the acceptance matrix below remains
blocked until `sdd-qa` independently reruns its scenarios.

- Hosted run `31888439750` remains the pre-fix failure observation for the real PR `#59`
  `npm/codegauge/package.json` hunk-only entry: seven approved version pairs were mixed with the exact
  deterministic `files` array formatting rewrite, and the old validator rejected the `10/8` API counts.
- The exact read-only PR `#59` files API list now passes `validate_stage_a_diff(..., version="0.2.0")`;
  local focused tests and the platform/arbitrary-formatting negative probes pass.
- Technical evidence: `qa-evidence/2026-08-15-replay/phase-13-verify-api-file-list.json` and
  `qa-evidence/2026-08-15-replay/phase-13-verify-summary.md`.
- The current local result is technical **PASS WITH WARNINGS**, not QA acceptance. No corrected hosted
  replay, tag, release, publication, upload, attestation, credential-bearing run, or operator acceptance
  is claimed. The earlier hosted run `31886141725` remains a separate private-hunk pre-fix failure.

## Historical post-Phase 12 apply handoff — 2026-08-15

This QA report predates the focused private-conformance hunk-context correction on
`fix/release-carrier-private-patch-context` and is not acceptance evidence for that new checkout.
Hosted run `31886141725` remains a failure observation: the valid PR `#59` hunk-only patch was rejected
by an over-specific `serde_json.workspace = true` context requirement. The local regression/fix was
applied without hosted writes; fresh `sdd-verify`, independent QA, and any separately authorized
protected hosted replay remain required. No hosted replay success is claimed.

## Historical post-Phase 12 verification handoff — 2026-08-15

Fresh technical verification now covers the current
`fix/release-carrier-private-patch-context` checkout. The exact PR `#59` API-shaped private hunk-only
fixture reproduces the pre-fix rejection and passes after the one-line context correction; the exact
four-pin/private-identity boundary and all requested local Release Please `17.6.0`, Cargo, npm, OCI,
workflow, shell, package, compile, CLI, and whitespace checks also pass.

The technical verdict is **PASS WITH WARNINGS**. Hosted run `31886141725` remains failure evidence, not
hosted replay success. At this handoff point independent `sdd-qa` had not yet re-run acceptance
scenarios; the Phase 12 matrix is retained below for history. The protected hosted replay,
publication, attestation, native-target, failure-injection, and rollback boundaries remain blocked by
the no-write/no-secret constraint.

## Prior authoritative QA rerun — Phase 12 — 2026-08-15

This section is retained as the Phase 12 local QA matrix for the focused
`fix/release-carrier-private-patch-context` checkout. It records a fresh local capability run after the
private hunk-context correction. Static checks are retained as diagnostics only; they are not QA
`PASS` results. Hosted and provider-backed acceptance remains explicitly blocked.

### Source artifacts and technical-verification handoff

- Proposal: `openspec/changes/codegauge-distribution/proposal.md`
- Delta specifications: all five files under `openspec/changes/codegauge-distribution/specs/`
- Design: `openspec/changes/codegauge-distribution/design.md`
- Tasks: `openspec/changes/codegauge-distribution/tasks.md`
- Technical verification: `openspec/changes/codegauge-distribution/verify-report.md`
- State/config: `state.yaml` and `openspec/config.yaml`
- Fresh evidence: `qa-evidence/2026-08-15-replay/phase-12-qa-rerun-private-hunk.json`,
  `phase-12-qa-rerun-dry-run.json`, and `phase-12-qa-rerun-summary.md`

The Phase 12 `sdd-verify` handoff was **PASS WITH WARNINGS**. It identifies hosted run `31886141725` as
the Phase 12 pre-fix failure and does not claim the corrected hosted replay, tag delivery,
publication, attestation, native-target execution, failure injection, rollback, or operator acceptance.

### Target, environment, permissions, and limitations

- Target: local repository `/Users/acosta/Dev/agent-swarm/codegauge`, branch
  `fix/release-carrier-private-patch-context`, `HEAD=cdd91baf9cbd0fb416ecfe67977310253d9b7534`.
- Host/toolchain: macOS arm64; Rust/Cargo `1.97.1`; Node `24.19.0`; npm `11.17.0`; Python `3.14.7`;
  Docker `29.7.2`; actionlint `1.7.12`; ShellCheck `0.11.0`.
- Exact local Release Please package: `17.6.0`; checked-in release version: `0.2.0`.
- Permissions/safety: no GitHub token, workflow dispatch, API mutation, repository-variable change,
  tag, label, release, upload, registry publication, attestation, merge, push, credential, or live
  carrier execution was performed. The fake `gh` used by the dry-run probe returned only 404 reads.
- Worktree: intentionally dirty before QA with the focused validator/test and OpenSpec handoff changes;
  QA did not modify source or workflow implementation. Local tags remain empty.
- Product surface: this is a distribution/CLI/workflow change; there is no browser UI, HTTP API, data
  store, locale surface, or persistence contract.

### Capability inventory

| Capability | Availability | Selected? | Rationale / disposition |
|---|---|---|---|
| Exact Release Please `17.6.0` fake-SCM harness | available | selected | Executes the installed package chain against a read-only fake SCM and observes effective paths/counters. |
| Stage-B private hunk/parser/content validators | available | selected | Executes the exact PR #59 fixture plus positive, negative, truncation, count, and unapproved-mutation cases. |
| Carrier mode/replay resolver | available | selected | Runs checked-in shell extraction and Python resolver for push/manual/dry-run/replay boundaries. |
| Dry-run plan/guard with fake `gh` | available | selected | Runs exact checked-in plan and guard steps with GET-only fake API responses and inspects mutation statuses. |
| Cargo/Rust workspace runtime | available | selected | Runs locked metadata, workspace tests, check, fmt, Clippy, and CLI contract tests locally. |
| npm wrapper and package dry-run | available | selected | Runs typecheck, six wrapper tests, and seven `npm pack --dry-run` package checks. |
| Archive generator/provenance validator | available | selected | Generates an isolated eight-target structural matrix and verifies checksum tampering fails closed; only host execution is native. |
| OCI executable regression layers | available | selected | Runs local OCI positive/static/evidence/failure suites without a registry; remote publication is not exercised. |
| Workflow/actionlint/ShellCheck diagnostics | available | selected as diagnostics | Commands exited zero, but static inspection is recorded as `NOT TESTED`, never as QA acceptance. |
| Read-only Git metadata | available | selected | Records branch/HEAD and empty local canonical tag state. |
| Hosted GitHub Actions/PR/carrier/replay | unavailable | rejected | No authorized hosted target or credentials; user prohibited dispatch/live execution. |
| Cargo/npm/GitHub Release/GHCR publication | available in principle | rejected | Explicit no-publication boundary. |
| Native non-host archive runners | unavailable | rejected | The host can execute only `aarch64-apple-darwin`; seven declared targets remain unexecuted. |
| Attestation, provider-backed rollback, failure injection | unavailable | rejected | Requires hosted identity/provider mutation, explicitly prohibited. |
| Browser/accessibility/responsive/locale/API/data/persistence | not applicable | rejected | No corresponding product surface exists in this change. |
| Manual/exploratory local shell behavior | available | selected | Repeated local runs, boundary mutations, checksum tampering, and source-immutability checks were exercised. |

### Scenario matrix

| ID | Category | Acceptance scenario | Result | Evidence or reason |
|---|---|---|---|---|
| QA-P12-01 | happy path/boundary | Exact PR #59 API hunk-only private patch with `@@ -10,10 +10,10 @@ publish = false`, four additions/deletions, eight changes, and no trailing `serde_json.workspace = true` context is accepted. | PASS | `phase-12-qa-rerun-private-hunk.json`; actual/declared counts are complete and all four approved dependency pins validate. |
| QA-P12-02 | negative/boundary | Missing, inconsistent-count, truncated, malformed, orphaned, unexpected-section, and multi-file full/hunk-only patches fail closed. | PASS | `python3 tests/release_carrier_tests.py` passed the complete parser negative matrix. |
| QA-P12-03 | unauthorized/security | Wrong-version, arbitrary, unapproved marker, filename-only, generated-content, and private package/version/publish/name/path/key/feature/formatting/truncation mutations fail closed. | PASS | `python3 tests/release_carrier_tests.py` and `python3 tests/release_please_runtime_tests.py` passed the mutation matrix. |
| QA-P12-04 | happy path/state transition | Exact Release Please `17.6.0` harness produces 32 effective paths, one private four-pin update, six npm optional rewrites, one synchronized PR, and zero release/tag calls. | PASS | `phase-12-qa-rerun-summary.md`; runtime output recorded `packageVersion=17.6.0`, `privateDependencyUpdates=1`, `synchronizedPullRequests=1`, `releaseCalls=0`, `tagCalls=0`. |
| QA-P12-05 | negative/state transition | No-op/wrong-version Stage-A fixture mutations and private package/publish/unapproved-path mutations are rejected. | PASS | Runtime wrapper printed `PRIVATE DEPENDENCY PIN UPDATE: ACCEPTED`; all listed private mutations printed `REJECTED`. |
| QA-P12-06 | happy path/negative | Carrier mode preserves push live default, manual dry-run/live precedence, and rejects invalid values. | PASS | `python3 tests/release_carrier_mode_tests.py` passed. |
| QA-P12-07 | happy path/security boundary | Valid manual replay selects the historical SHA while retaining current checkout identity; replay on push/live/malformed/non-main is rejected before collection. | PASS | `python3 tests/release_carrier_tests.py` and mode tests passed; replay input matrix is preserved under `qa-evidence/2026-08-15-replay/`. |
| QA-P12-08 | no-write/state transition | Exact dry-run plan and guard emit a canonical `v0.2.0` create plan and skip/not-start/not-dispatch every mutation. | PASS | `phase-12-qa-rerun-dry-run.json`; fake `gh` recorded only two reads and zero write-method calls. |
| QA-P12-09 | happy path/negative | Locked Cargo metadata/tests/check/fmt/Clippy and CLI version/profile/contract behavior remain executable. | PASS | Fresh Cargo commands passed; workspace tests reported 31 passed, 0 failed, 0 skipped. |
| QA-P12-10 | happy path/negative | npm wrapper resolution, missing/unsupported target rejection, passthrough, typecheck, tests, and seven package dry-runs behave as specified. | PASS | Fresh npm typecheck/tests passed (6 tests); all seven `npm pack --dry-run` checks passed. |
| QA-P12-11 | happy path/negative | Eight archive/checksum sidecars validate in an isolated structural matrix and byte tampering fails closed. | PASS | Fresh temporary matrix generated 8/8; intact verification exit 0; tampered verification exit 1 with checksum mismatch. Seven entries explicitly recorded `execution=not-run`. |
| QA-P12-12 | happy path/negative | Local OCI regression, evidence, and failure layers preserve approved architecture/non-root/metadata failure boundaries without registry writes. | PASS | Four OCI executable regression suites passed; no registry was contacted. |
| QA-P12-13 | repeated/exploratory | Repeated local capability runs preserve source/workflow bytes and expected results. | PASS | Focused, Cargo, npm, archive, OCI, Python, and package dry-run runs completed; `git diff --check` passed and no source/workflow file was changed by QA. |
| QA-P12-14 | security diagnostics | Workflow pins, permissions, concurrency, ShellCheck, Dockerfile, and actionlint checks are observed as runtime acceptance behavior. | NOT TESTED | Diagnostics exited zero, but policy forbids static inspection from producing a QA `PASS`. |
| QA-P12-15 | hosted state transition | Corrected hosted Stage-A PR, ordinary-main no-op, merged PR #59-equivalent carrier, and protected hosted replay are observed. | BLOCKED | No authorized hosted target/credential; user prohibited dispatch and live carrier execution. The prior hosted run `31886141725` remains failure evidence. |
| QA-P12-16 | hosted state transition | Canonical tag delivery and downstream release workflow are observed at the validated merge SHA. | BLOCKED | No tag creation, hosted event delivery, or downstream workflow run was allowed. |
| QA-P12-17 | native-target boundary | All eight archive targets have executable native/cross-target runtime evidence suitable for release acceptance. | BLOCKED | Only `aarch64-apple-darwin` ran natively; seven target records are deliberately `execution=not-run`. |
| QA-P12-18 | registry/publication | Cargo registry graph, npm publication, GitHub Release assets, and GHCR manifest are observed. | BLOCKED | Publication and upload were explicitly prohibited; dependent Cargo package verification still lacks synchronized crates in the public index. |
| QA-P12-19 | attestation/security | Hosted credential isolation, OIDC attestation, and secret-safe publication behavior are observed at runtime. | BLOCKED | Requires protected hosted/provider execution and credentials, both unavailable/prohibited. |
| QA-P12-20 | interrupted/rollback | Publication failure stops later channels and produces provider-backed recovery/rollback evidence. | BLOCKED | Requires disposable publication state and mutation/failure injection, explicitly prohibited. |
| QA-P12-21 | browser/accessibility/responsive/locale/persistence | Browser, accessibility, responsive, internationalization, API, data, and persistence behavior is exercised. | NOT TESTED | Not applicable: no such surface exists for this distribution/CLI/workflow change. |

### Untested and blocked scope

| Scope | Result | Rerun prerequisite |
|---|---|---|
| Hosted Stage-A/version PR and corrected private hunk validation | BLOCKED | Separately authorized protected GitHub run; inspect PR #59-equivalent metadata and zero Stage-A writes. |
| Hosted ordinary-main no-op and historical replay | BLOCKED | Authorized protected events; replay must be `workflow_dispatch`, `main`, `dry_run=true`, and the approved historical SHA. |
| Canonical tag delivery/downstream release | BLOCKED | Authorized tag carrier and downstream workflow run at the validated SHA. |
| Cargo/npm/GitHub Release/GHCR publication and attestation | BLOCKED | Approved release window, scoped credentials, provider-safe namespace, and no-write rehearsal boundary. |
| Native evidence for seven non-host archives | BLOCKED | Native/cross-target runner matrix with executable evidence per declared target. |
| Failure injection and rollback | BLOCKED | Disposable provider-backed rehearsal that records stop order and recovery actions. |
| Hosted secret isolation and least-privilege runtime behavior | BLOCKED | Protected/untrusted hosted runs with observable redacted logs and job permissions. |
| Browser/accessibility/responsive/locale/persistence | NOT TESTED | No rerun unless the change gains a corresponding product surface. |

### Findings

| ID | Severity | Scenario/location | Evidence | Status |
|---|---|---|---|---|
| QA-P12-001 | P1 | Hosted Stage-A, ordinary-main carrier, historical replay, canonical tag delivery, and downstream provenance are not observable. | No authorized hosted target; run `31886141725` is pre-fix failure evidence. | Open — acceptance blocker; requires protected hosted rerun. |
| QA-P12-002 | P1 | Registry publication, GitHub Release/GHCR outputs, attestation, and dependent Cargo registry verification are unavailable. | No publication or upload permitted; synchronized crates are absent from the public index. | Open — acceptance blocker. |
| QA-P12-003 | P1 | Seven non-host archive targets lack executable native acceptance evidence. | Fresh structural matrix records seven `execution=not-run` entries. | Open — requires target matrix evidence. |
| QA-P12-004 | P1 | Hosted failure injection, credential isolation, and rollback are not observed. | Requires hosted/provider mutation prohibited by this QA. | Open — requires disposable protected rehearsal. |
| QA-P12-005 | P2 | Static workflow/security diagnostics cannot be promoted to acceptance results. | `actionlint`, ShellCheck, and static suites exited zero but are recorded as `NOT TESTED`. | Open warning — policy limitation, no local behavior failure observed. |

No local executable scenario failed, and no CRITICAL/P0 implementation finding was observed. The P1
findings are acceptance blockers caused by unavailable or prohibited external state, not observed
failures in the corrected local validator.

### Current verdict

`BLOCKED`

Local executable acceptance capabilities pass for the exact PR #59 hunk-only correction, all requested
fail-closed parser/private mutation cases, Release Please `17.6.0`, carrier modes/replay, dry-run
no-write behavior, Cargo/npm behavior, archive checksum boundaries, and local OCI regressions. The
verdict cannot be `PASS` or `PASS WITH WARNINGS` because hosted replay, downstream tag delivery,
registry/publication, attestation, seven native targets, and rollback remain acceptance-relevant
`BLOCKED` scope under the explicit no-write/no-secret boundary.

### Current implementation handoff

- QA did not fix code or modify workflows, variables, credentials, tags, releases, registries, or the
  live carrier.
- The exact PR #59 failure remains documented as failure evidence; the local correction is accepted by
  the executable local matrix only.
- Archive remains gated: this is a production distribution change, not a documentation/config-only
  exception. Re-run the authorized protected hosted acceptance scenarios before `sdd-archive`.

## 2. Source artifacts and technical-verification handoff

Read before testing:

- `openspec/changes/codegauge-distribution/proposal.md`
- All five delta specs under `openspec/changes/codegauge-distribution/specs/`
- `design.md`, `tasks.md`, `apply-progress.md`, `verify-report.md`, and `state.yaml`
- `openspec/config.yaml`

The latest technical section of `verify-report.md` reports **PASS WITH WARNINGS** for the Phase 12
private hunk-context correction. It reports no local implementation defect and explicitly leaves the
protected hosted replay, downstream delivery, publication, native-target evidence, attestation,
failure injection, rollback, and independent acceptance outside its boundary. This QA report remains a
blocked acceptance handoff rather than a claim that technical verification is operator acceptance.

## 3. Target, environment, permissions, and limitations

- Host: macOS arm64.
- Toolchain: Rust/Cargo `1.97.1`, Node `24.19.0`, npm `11.17.0`, Python `3.14.7`, Docker client
  `29.7.2` / server `29.4.0`, actionlint `1.7.12`, ShellCheck `0.11.0`.
- Exact local Release Please package: `17.6.0`.
- Current checked-in runtime version: `0.2.0`; the fake-SCM harness calculates the next local
  candidate as `0.3.0` for the current commit set.
- No GitHub token, registry credential, workflow dispatch, repository-variable change, tag, label,
  release, upload, publication, attestation, push, merge, or live carrier execution was performed.
- A read-only remote tag query could not authenticate over the repository's SSH remote; local tag
  listing was empty. No hosted target or credentials were available.
- QA added only this report and `qa-evidence/`; source and workflow files were not changed.
- There is no browser UI, HTTP API, data store, locale surface, or persistence contract for this
  distribution/CLI/workflow change.

## 4. Capability inventory

| Capability | Availability | Selection | Rationale / disposition |
|---|---|---|---|
| Exact Release Please `17.6.0` fake-SCM harness | available | selected | Executes the package-level Manifest/NodeWorkspace/linked-version chain without writes. |
| Stage-B carrier, parser, replay, and tag-plan validators | available | selected | Pure local positive, negative, boundary, idempotency, and source-immutability behavior is executable. |
| Extracted carrier mode and dry-run plan steps | available | selected | Runs checked-in shell logic with temporary files and a fake read-only `gh`; no live API is contacted. |
| Cargo/Rust quality and source runtime | available | selected | Locked metadata/tests/check/fmt/Clippy and version/profile behavior run locally. |
| npm typecheck/test/package dry-run | available | selected | Wrapper resolution, negative targets, passthrough, and seven package manifests are executable. |
| Archive generator/provenance validator | available | selected | Eight structural archive/checksum fixtures and tamper/incomplete negatives run locally. |
| Docker Buildx/OCI runtime | available | selected | Isolated local amd64/arm64 builds, runtime contract, non-root, and evidence validation run without a registry. |
| Workflow/actionlint/ShellCheck/Dockerfile checks | available | selected as diagnostics | Useful evidence, but static inspection is not recorded as QA `PASS`. |
| Read-only Git metadata | available | selected | Current branch/HEAD and local tag state were recorded; remote SSH access failed. |
| Hosted GitHub Actions/PR/carrier/replay | unavailable | rejected | No safe hosted target or authorized credentials; user prohibited live carrier execution. |
| Cargo/npm/GitHub Release/GHCR publication and uploads | available in principle | rejected | Explicitly prohibited by the scope. |
| Native non-host archive runners | unavailable | rejected | macOS arm64 cannot provide native execution for seven declared archive targets. |
| Attestation and provider-backed rollback rehearsal | unavailable | rejected | Requires hosted identity/publication state and mutation, both prohibited. |
| Browser/accessibility/responsive/locale/API/data/persistence | not applicable | rejected | No such product surface exists in this change. |
| Manual/exploratory local shell behavior | available | selected | Repeated commands, boundary mutations, checksum tampering, and local OCI smoke were exercised. |

## 5. Scenario matrix

`PASS` means executable local behavior produced the expected observable result. Static-only checks are
`NOT TESTED`, even when the diagnostic command exited zero. Hosted/provider constraints are `BLOCKED`.

| ID | Category | Scenario | Result | Evidence or reason |
|---|---|---|---|---|
| R-F6-A1 | happy path | Stage A exact Release Please version-PR chain creates one synchronized fake PR, 32 effective paths, one four-pin private update, six npm rewrites, and zero release/tag calls. | PASS | `qa-evidence/2026-08-15-replay/release-please-runtime.log`; exact package `17.6.0`, `synchronizedPullRequests=1`, `privateDependencyUpdates=1`, `releaseCalls=0`, `tagCalls=0`. |
| R-F6-A2 | boundary | Historical Python wrapper fixture models `0.1.0 -> 0.2.0`; no-op and wrong-version replacements fail closed. | PASS | `release-please-runtime.log`; `PRIVATE DEPENDENCY PIN UPDATE: ACCEPTED` and all listed private mutations rejected. |
| R-F6-B1 | happy path | Stage B validates one trusted main event and produces canonical `v0.2.0` carrier data. | PASS | `release-carrier.log`; copied-tree carrier fixture and exact-one validation passed. |
| R-F6-B2 | negative/boundary | Full unified diffs and GitHub PR-files hunk-only patches accept only configured typed, annotated, npm, changelog, and private-pin content. | PASS | `release-carrier.log`; malformed, missing, truncated, count-inconsistent, multi-section, wrong-version, arbitrary, and filename-only cases rejected. |
| R-F6-B3 | state transition/repeated | Canonical tag planning handles create, same-SHA no-op, conflicting SHA, annotated tag, existing release, and bootstrap-version cases. | PASS | `stage-b-tag-plan-matrix.json`; expected success/failure statuses matched. |
| R-F6-C1 | state transition | Ordinary main event with no matching Release Please PR exits as an auditable no-op before diff validation. | PASS | `ordinary-main-no-op.json`: `status=skipped`, `reason=no-matching-release-please-pr`, count `0`. |
| R-F6-C2 | boundary | Exact checked-in mode resolver preserves push live default, manual dry-run/live precedence, and invalid-value rejection. | PASS | `release-carrier-mode.log`; extracted resolver tests passed. This is local mode behavior, not hosted execution. |
| R-F6-C3 | mutation guard | Dry-run plan and guard run with fake read-only GitHub responses and prove no mutation method is called. | PASS | `dry-run-plan-probe.json`, `carrier-plan.json`, `carrier-plan-summary.md`; plan/guard exit `0`, fake calls were GET-only, tag/label/publication statuses were skipped/not-started/not-dispatched. |
| R-F6-D1 | happy path | Valid manual replay uses the historical SHA as `EVENT_SHA` while retaining the current checkout SHA. | PASS | `replay-input-matrix.json` and `release-carrier.log`; source bytes remained unchanged in the replay fixture. |
| R-F6-D2 | negative/security boundary | Replay on push, live manual dispatch, malformed SHA, or non-main ref fails before collection. | PASS | `replay-input-matrix.json`; all four negative cases returned the expected nonzero result. |
| R-F6-D3 | repeated/interrupted | Replay and normal dispatch records retain total boolean replay fields and null/none replay-event behavior when replay is absent. | PASS | `release-carrier-mode.log`; normal and replay mode matrix passed. |
| CARGO-1 | negative | Stale private pins block locked metadata; the exact four corrected pins allow metadata while private version remains `0.1.0`. | PASS | `private-pin-graph-matrix.json`; stale fixture returned `101`, corrected fixture returned `0`. |
| CARGO-2 | happy path | Pinned Cargo metadata, workspace tests, check, fmt, Clippy, CLI version, and profiles pass. | PASS | `cargo-metadata.log`, `cargo-test.log`, `cargo-check.log`, `cargo-fmt.log`, `cargo-clippy.log`, `cargo-cli-*.log`; 31 tests passed, zero failed/skipped. |
| CARGO-3 | external boundary | All dependent Cargo packages can be fully package-verified against their registry dependency graph. | BLOCKED | `cargo-package-core.log` and dependent logs fail because the synchronized runtime crates are not present in the crates.io index; no publication was allowed. |
| CARGO-4 | negative | Missing/invalid release archive evidence is rejected before downstream channels. | PASS | `archives-incomplete.log`; validator rejected 7/8 manifests. |
| NPM-1 | happy path | Approved wrapper and six same-scope platform packages typecheck, test, and pack. | PASS | `npm-typecheck.log`, `npm-tests.log`, seven `npm-pack-*.log`; six wrapper tests passed and seven dry-runs passed. |
| NPM-2 | negative/boundary | Missing optional dependency and musl/unsupported target paths fail without running an unrelated binary. | PASS | `npm-tests.log`; all six npm tests passed, including missing dependency and musl rejection. |
| NPM-3 | process compatibility | npm arguments, inherited streams, and child exit status pass through unchanged. | PASS | `npm-tests.log`; passthrough test passed. |
| ARCH-1 | happy path | Eight archive names, formats, manifests, lowercase SHA-256 sidecars, and source/version metadata validate. | PASS | `archives/archive-verify.log`; local structural fixture validated all eight entries. Seven entries explicitly carry cross-target `execution=not-run`. |
| ARCH-2 | negative | Archive byte tampering is rejected by checksum validation. | PASS | `archives-tampered.log`; expected checksum failure returned `1`. |
| ARCH-3 | native-target boundary | Every declared archive target has executable native/cross-target runtime evidence suitable for release acceptance. | BLOCKED | Only the host target was native; seven target fixtures record `execution=not-run`. Native/cross-target hosted matrix is required. |
| OCI-1 | happy path | Local workspace-aware images for linux/amd64 and linux/arm64 build, run, expose version/profile/contract output, and run non-root. | PASS | `oci-local-build.log` and `oci-local/`; isolated Buildx run passed both architectures and OCI evidence validation without registry publication. |
| OCI-2 | negative/boundary | Unsupported architecture, root runtime, label/version/digest drift, and missing emulation evidence fail closed. | PASS | `oci-regression.log`, `oci-evidence-tests.log`, `oci-failure-tests.log`; executable synthetic negatives passed. |
| OCI-3 | external boundary | Approved GHCR identity, final multi-arch manifest, remote digest, attestation, and registry tag are observable. | BLOCKED | No registry login/push/manifest/attestation was authorized or run. |
| SEC-1 | unauthorized/security | Untrusted PR secret isolation, hosted least privilege, and mutable-action rejection are observed at runtime. | BLOCKED | No hosted runner or credential-bearing target was available. |
| SEC-2 | static diagnostic | Workflow full-SHA, permissions, concurrency, actionlint, ShellCheck, and Dockerfile checks are clean. | NOT TESTED | `distribution-checks.log`, `carrier-static.log`, `actionlint.log`, `shellcheck.log`, and `dockerfile-check.log` are static diagnostics; policy forbids turning static inspection into QA `PASS`. |
| REL-1 | hosted state transition | Stage A hosted PR, merged-main ordinary no-op, corrected merged Release Please carrier, and canonical tag delivery are observed. | BLOCKED | No hosted workflow target, PR run, or authorized dispatch was supplied. |
| REL-2 | hosted replay | Authorized historical replay of `fcc91b4...` runs on current main and emits a no-publication hosted record. | BLOCKED | User explicitly prohibited live carrier/dispatch; local replay is not hosted evidence. |
| REL-3 | interrupted/rollback | A later publication failure stops subsequent publishers and exposes recovery/rollback evidence. | BLOCKED | Requires disposable provider state or publication mutation, both prohibited. |
| EXP-1 | exploratory/repeated | Repeated local quality, carrier, archive, npm, and OCI checks preserve results without source mutation. | PASS | All selected local commands passed or returned expected negative results; `git diff --check` passed and only QA evidence is untracked. |
| UI-1 | browser/accessibility/responsive/locale/persistence | Browser, accessibility, responsive, internationalization, API, data, or persistence behavior. | NOT TESTED | Not applicable: this change has no UI/API/store/locale acceptance surface. |

## 6. Untested scope, reason, and rerun prerequisite

| Scope | Result | Rerun prerequisite |
|---|---|---|
| Hosted Stage-A version PR and zero-artifact observation | BLOCKED | Protected GitHub target and scoped credential; capture PR diff, zero tag/release calls, and secret-safe logs. |
| Hosted ordinary-main no-op and corrected carrier | BLOCKED | Authorized merged-main events; inspect skipped record and exact-one validation run. |
| Hosted historical replay/no-publication record | BLOCKED | Authorized `workflow_dispatch` on `main` with `dry_run=true` and the approved replay SHA; inspect record/summary without enabling live mutations. |
| Canonical tag delivery and downstream release workflow | BLOCKED | Hosted carrier/tag event and downstream run; no tag creation was allowed in this QA. |
| Cargo/npm/GitHub Release/GHCR publication and attestation | BLOCKED | Approved release window, provider-safe namespace, and scoped credentials; no publication was allowed here. |
| Full dependent Cargo package verification | BLOCKED | Staged/published runtime crates or an equivalent isolated registry rehearsal; current crates.io index has no synchronized runtime packages. |
| Native evidence for seven non-host archives | BLOCKED | Declared native/cross-target runner matrix with executable evidence per target. |
| Failure injection and non-atomic rollback | BLOCKED | Disposable provider-backed rehearsal that can safely record stop order and correction/deprecation actions. |
| Hosted secret isolation and least-privilege runtime behavior | BLOCKED | Untrusted PR and protected release runs with observable job permissions and redacted logs. |
| Browser/accessibility/responsive/locale/persistence | NOT TESTED | No rerun needed unless the change gains a corresponding product surface. |

## 7. Findings

| ID | Severity | Finding | Status |
|---|---|---|---|
| QA-001 | P1 | Hosted Stage-A, ordinary-main carrier, historical replay, canonical tag delivery, and downstream release provenance were not observable. | Open — acceptance blocker; requires an authorized protected hosted rehearsal. |
| QA-002 | P1 | Cargo registry completion, npm/GitHub Release/GHCR publication, final OCI manifest, and attestation were not executed. | Open — explicitly prohibited; archive remains gated. |
| QA-003 | P1 | Seven non-host archive targets have no executable native evidence, and no immutable published release exists. | Open — requires the declared target matrix and immutable release. |
| QA-004 | P1 | Dependent Cargo package verification cannot resolve synchronized runtime crates from crates.io in this pre-publication checkout. | Open — requires staged/published registry graph or an equivalent safe registry rehearsal. |
| QA-005 | P2 | Hosted security isolation, failure propagation, publication interruption, and rollback were not injected; workflow checks are static diagnostics only. | Open — no local implementation failure observed; requires disposable hosted/provider rehearsal. |

No `FAIL` result and no CRITICAL/P0 implementation finding was observed in the executable local scope.
The P1 findings are acceptance blockers caused by unavailable or prohibited external state, not a claim
that the local implementation failed.

## 8. Final verdict

`BLOCKED`

Local executable capabilities for Stage A, Stage B, no-op classification, dry-run guard, replay input
validation, parser/content boundaries, Cargo locked behavior, npm behavior, archive validators, and
local OCI runtime behavior passed. The final verdict cannot be `PASS` or `PASS WITH WARNINGS` because
hosted historical replay, downstream tag delivery, immutable release provenance, publication,
attestation, native target acceptance, complete registry package verification, and rollback remain
acceptance-relevant `BLOCKED` scope under the explicit no-write/no-secret boundary.

## 9. Implementation handoff

- QA did not modify source, workflows, credentials, variables, tags, releases, registries, or the live
  carrier.
- Persisted evidence is under `openspec/changes/codegauge-distribution/qa-evidence/2026-08-15-replay/`.
- `qa-report.md` is the current acceptance audit record; older report content was superseded because it
  described earlier branches and pre-repair failures.
- Archive must remain gated until QA-001 through QA-004 are resolved or an explicit policy exception is
  recorded. This is a production distribution change, not a documentation-only exception.
- This report does not claim Cargo, npm, GitHub Release, GHCR, attestation, hosted workflow, or product
  acceptance.
