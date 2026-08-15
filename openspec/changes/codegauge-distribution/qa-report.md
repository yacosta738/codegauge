# Acceptance QA Report: `codegauge-distribution`

## 1. Identity

| Field | Value |
|---|---|
| Change | `codegauge-distribution` (R-F6) |
| Mode | OpenSpec |
| Phase | `sdd-qa` |
| Date | 2026-08-15 |
| Target branch | `fix/release-carrier-private-patch-context` |
| Target checkout | `/Users/acosta/Dev/agent-swarm/codegauge` |
| Target HEAD | `cdd91baf9cbd0fb416ecfe67977310253d9b7534` |
| Final QA verdict | `BLOCKED` |

This is independent acceptance QA for observable local behavior. It does not claim hosted, operator,
registry, or product acceptance.

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
scenarios; the current authoritative rerun is recorded below. The protected hosted replay,
publication, attestation, native-target, failure-injection, and rollback boundaries remain blocked by
the no-write/no-secret constraint.

## Current authoritative QA rerun — 2026-08-15

This section supersedes the earlier QA matrix below for the focused
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

The latest `sdd-verify` handoff is **PASS WITH WARNINGS**. It identifies hosted run `31886141725` as
the authoritative pre-fix failure and does not claim the corrected hosted replay, tag delivery,
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
