# Acceptance QA Report: `codegauge-distribution`

## 1. Identity

| Field | Value |
|---|---|
| Change | `codegauge-distribution` (R-F6) |
| Mode | OpenSpec |
| Phase | `sdd-qa` |
| Date | 2026-08-15 |
| Target branch | `fix/release-carrier-replay` |
| Target checkout | `/Users/acosta/Dev/agent-swarm/codegauge` |
| Target HEAD | `6b65654977f7b41ee9a964f9089a6629fd521d4e` |
| Final QA verdict | `BLOCKED` |

This is independent acceptance QA for observable local behavior. It does not claim hosted, operator,
registry, or product acceptance.

## 2. Source artifacts and technical-verification handoff

Read before testing:

- `openspec/changes/codegauge-distribution/proposal.md`
- All five delta specs under `openspec/changes/codegauge-distribution/specs/`
- `design.md`, `tasks.md`, `apply-progress.md`, `verify-report.md`, and `state.yaml`
- `openspec/config.yaml`

The authoritative final section of `verify-report.md` reports **PASS WITH WARNINGS** for the local
Phase 11 replay and fixture repair. It reports no local implementation defect and explicitly leaves
the protected hosted replay, downstream delivery, publication, native-target evidence, attestation,
failure injection, rollback, and independent acceptance outside its boundary. This QA run re-executed
the relevant local capabilities on the current branch rather than treating that handoff as acceptance.

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
