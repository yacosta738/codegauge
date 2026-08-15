# Acceptance QA Report: codegauge-distribution (latest technical verify PASS WITH WARNINGS; acceptance rerun pending)

## Latest technical verification handoff — 2026-08-15

Fresh `sdd-verify` independently reran the generated-version/updater boundary and returned
**PASS WITH WARNINGS**. The exact Release Please `17.6.0` read-only fake-SCM produced the release
version `0.2.0`, exact 32-path effective changeset, one private manifest update containing only the
four approved dependency pins, six npm optional pin rewrites, one synchronized PR, and zero Stage-A
release/tag calls.

- The copied synchronized tree changed the golden through typed `$.tool.version`, changed exactly
  the four README and two model-contract annotated version lines, aligned public Cargo/npm/lock
  values, and passed `cargo test --workspace --locked` while conformance remained version `0.1.0`
  with `publish = false`.
- Stage-B accepted legitimate typed/annotated/TOML/npm/changelog/private-pin updates and rejected
  wrong-version, arbitrary, unannotated, malformed, filename-only, missing, duplicate, and
  truncated mutations.
- Current-tree Cargo, Python, npm, OCI, workflow, shell, package, and whitespace checks passed;
  exact workflow mode/no-match probes also passed without a diff fetch or mutation.
- QA remains **BLOCKED** pending the independent acceptance rerun and protected hosted evidence.
  This handoff makes no user/operator acceptance claim. No hosted writes, credentials, tags,
  releases, publication, variables, uploads, or attestations were used.

## Apply handoff — Phase 9 private conformance dependency-pin exception — 2026-08-15

The local implementation correcting hosted PR `#59` is complete for this apply slice. Acceptance QA
remains **BLOCKED** and has not been rerun: the hosted PR `#59` metadata failure is still the latest
hosted evidence until a separately authorized protected rerun proves the synchronized private pins.

- Local evidence now covers one exact v17.6.0 fake-SCM PR, 32 effective Stage-A paths, one private
  root-carrier manifest update changing only four dependency versions, six npm rewrites, and zero
  release/tag calls.
- Local Stage-B patch/content tests accept only the four approved private dependency replacements and
  reject package metadata/version/publish, dependency path, formatting/comment, truncated/missing
  patch, changelog, and other private-path mutations.
- The synchronized fixture passes `cargo metadata --locked` while retaining conformance package
  version `0.1.0` and `publish = false`; the requested local quality, package, OCI, workflow, and
  whitespace checks are green.
- This is implementation evidence only. `sdd-verify` must run next, followed by an independent QA
  rerun; no user/operator acceptance is claimed.
- No hosted writes occurred in this apply phase: no GitHub API mutation, workflow dispatch, repository
  variable change, tag, label, release, upload, attestation, registry publication, credential use,
  merge, push, or commit.

## Apply remediation handoff — 2026-08-15

The two local CRITICAL findings from the fresh technical verification were repaired by `sdd-apply`.
Acceptance QA remains **BLOCKED** and has not been rerun; this handoff is local implementation
evidence only.

- The typed golden updater now changes `$.tool.version`, the four intended README lines and two model
  contract lines use the exact Release Please 17.6.0 marker, and the exact 32-path fake-SCM result,
  six optional pins, one PR, and zero Stage-A release/tag calls remain green.
- A synchronized copied tree now reports the synchronized runtime version in the conformance golden
  and passes the complete `cargo test --workspace --locked` suite while conformance remains version
  `0.1.0` and `publish = false`.
- Stage-B validates complete patch/count/content metadata for typed/annotated/TOML/npm/root/generated
  paths and the private four-pin exception. Wrong versions, arbitrary content, unapproved markers,
  filename-only entries, duplicates, and missing/truncated patches are covered by local negatives.
- Focused/runtime/mutation, Python compileall, Cargo, npm, OCI, actionlint, ShellCheck, Dockerfile,
  package, and whitespace checks passed locally.
- `sdd-verify` must independently rerun the changed spec matrix before QA reruns. Hosted rehearsals,
  tags/releases, publication, credentials, variables, uploads, attestations, and registry writes were
  not performed.

## Fresh technical verification handoff — 2026-08-15

The Phase 9 `sdd-verify` rerun executed the requested local matrix but returned **FAIL**. The exact
Release Please `17.6.0` fake-SCM and current-tree quality checks passed: 32 effective Stage-A paths,
exactly four private dependency-version edits, synchronized public Cargo/npm/lock values, six npm
optional rewrites, one PR, zero release/tag calls, private/non-publishable boundaries, and local
dry-run/ordinary-main no-op guards were observed. The synchronized fixture's `cargo metadata --locked`
also passed.

QA must remain **BLOCKED** pending remediation of two local defects found by verification:

1. A synchronized effective-tree `cargo test --workspace --locked` run fails because the conformance
   golden still expects tool version `0.1.0` after the public runtime reaches `0.2.0`; the root generic
   carrier does not update that unmarked file.
2. Stage-B accepts a content-mutated approved generated file (`tests/golden/valid-methods.json`) by
   filename alone; the direct probe returned `generated-file mutation: ACCEPTED`.

No hosted rerun, publication, tag/release, credential, registry, or repository-variable write was
performed. `sdd-qa` remains the acceptance owner only after `sdd-apply` repairs the local defects and
`sdd-verify` passes again.

## Superseding hosted finding — 2026-08-15

Hosted PR `#59` established the real Stage-A boundary: the five public runtime Cargo packages and
npm packages synchronized to `0.2.0` with no release/tag calls, but merged-tree `cargo metadata
--locked` failed because the private conformance manifest still pinned its four runtime path
dependencies to `^0.1.0`. The earlier local exclusion-only result is historical and cannot be used
as acceptance of this corrected contract.

The pending acceptance contract is now: the Java root carrier may change only the four private
dependency `.version` fields to the synchronized runtime version; the private package version,
`publish = false`, lock identity, changelog/release/tag exclusion, and linked-component exclusion
must remain intact. Stage-B must accept that exact content and reject every other private or
unapproved mutation. This correction is now implemented locally but not hosted-verified; QA remains
`BLOCKED`.

## Technical verification handoff — carrier event-correlation fix — 2026-08-15

The prior hosted Stage-A evidence remains valid: Release Please created PR `#59` and no tag or GitHub
Release. Fresh `sdd-verify` verified the automatic Stage-B ordinary-main-push fix locally: zero
matching Release Please PRs are a successful auditable no-op, exactly one matching PR follows the
full carrier path, and multiple/malformed data fail closed. The new behavior is **not yet
hosted-verified**, and no hosted write, tag, label, release, upload, publication, or credential use was
performed. The QA verdict remains `BLOCKED`; this report makes no acceptance claim for the fix.

- Local technical verdict: **PASS WITH WARNINGS**.
- Local evidence: carrier correlation/static/runtime suites, exact Release Please `17.6.0` fake-SCM
  (one PR, six pins, zero release/tag calls, private exclusion), Cargo/npm/OCI/workflow/package checks.
- Remaining acceptance gates: protected hosted ordinary-main and Release Please rehearsals, hosted
  publication/tag delivery, native target evidence, failure injection/rollback, and independent QA.

## 1. Identity

- Change: `codegauge-distribution`
- Mode: OpenSpec
- Phase: `sdd-qa`
- Date: 2026-08-15
- QA verdict: `BLOCKED`
- Scope: authorized R-F6 two-stage Release Please 17.6.0 version-PR pass plus post-merge canonical-tag carrier

The scenario matrix below is the prior executable QA run and remains `BLOCKED` for the acceptance
gates it could not observe. The technical verification handoff above supersedes its source-state
description for the carrier fix, but does not upgrade it to QA acceptance. The older 2026-08-13 QA
record is retained below as historical evidence.

## 2. Source artifacts and technical verification handoff

### Source artifacts read

- `openspec/changes/codegauge-distribution/proposal.md`
- `openspec/changes/codegauge-distribution/specs/ci-quality-gates/spec.md`
- `openspec/changes/codegauge-distribution/specs/cargo-distribution/spec.md`
- `openspec/changes/codegauge-distribution/specs/npm-distribution/spec.md`
- `openspec/changes/codegauge-distribution/specs/release-artifacts/spec.md`
- `openspec/changes/codegauge-distribution/specs/oci-distribution/spec.md`
- `openspec/changes/codegauge-distribution/design.md`
- `openspec/changes/codegauge-distribution/tasks.md`
- `openspec/changes/codegauge-distribution/verify-report.md`
- `openspec/changes/codegauge-distribution/state.yaml`
- `openspec/changes/codegauge-distribution/apply-progress.md`
- `openspec/config.yaml`

### Current implementation inspected

- `release-please-config.json`, `.release-please-manifest.json`
- `.github/workflows/release-please.yml`
- `.github/workflows/release-tag-carrier.yml`
- `.github/workflows/release-on-tag.yml`
- `.github/workflows/release.yml`
- `.github/workflows/release-build.yml`
- `.github/workflows/release-publish.yml`
- `scripts/verify_release_provenance.py`
- `scripts/package_release.py`, `scripts/build_oci_release.sh`
- `tests/release_please_runtime_harness.mjs`, `tests/release_please_runtime_tests.py`
- `tests/release_carrier_tests.py`, `tests/release_carrier_static_tests.py`
- `tests/release_provenance_tests.py`, `tests/distribution_checks*.py`
- `tests/oci_distribution*.py`

### Technical handoff

The fresh authoritative technical-verification section in `verify-report.md` hands off `PASS WITH
WARNINGS` for the current carrier-fix checkout. Tasks 4.2/7.4/8.4 (protected hosted rehearsal) and
4.3 (downstream QA) remain incomplete. This QA report does not upgrade local evidence into hosted or
product acceptance.

The checked-in fake-SCM harness records the upstream raw `Update[]` proposals before the exact
v17.6.0 `GitHub.buildChangeSet` missing-file filtering boundary; its log therefore contains some
absent-file proposals. The latest verification handoff separately records the effective 31-path
changeset probe. QA treats the harness's requested one-PR/six-pin/zero-call/private-boundary result
as local evidence and does not treat either probe as hosted changed-file or publication evidence.

## 3. Target, environment, permissions, and limitations

- Local target: `/Users/acosta/Dev/agent-swarm/codegauge`.
- Checkout: branch `fix/release-carrier-skip-unmatched`, `HEAD=6c9e6dfd8507b12d37eef21b303cfe435e70abc9`.
- Worktree: intentionally dirty with the carrier-correlation remediation and prior R-F6 artifacts;
  QA made no source, workflow, credential, release, or registry changes.
- Host: macOS arm64.
- Toolchain observed in `/tmp/codegauge-rf6-qa.weKmyI/environment.log`: Rust/Cargo 1.97.1,
  Node 24.19.0, npm 11.17.0, Python 3.14.6, Docker 29.7.2, actionlint 1.7.12.
- Exact Release Please package: `npx --yes release-please@17.6.0 --version` returned `17.6.0`.
- Read-only remote tag inspection: `git ls-remote --refs origin 'refs/tags/v*.*.*'` exited 0 and
  returned no canonical tags.
- No hosted run target, release-please PR, merged-main carrier run, canonical tag, GitHub Release,
  registry namespace rehearsal, or release credentials were supplied or safely available.
- Explicit safety boundary honored: no commit, push, merge, tag creation, GitHub Release, Cargo
  publish, npm publish, GHCR push, upload, attestation, credential injection, or hosted write.
- A local CLI, package test surface, archive generator/validator, and Docker Buildx/QEMU surface are
  available. There is no deployed application, browser UI, API/data store, locale surface, or general
  hosted acceptance target for this distribution-only change.

## 4. Capability inventory

| Capability | Availability | Selection | Rationale / disposition |
|---|---|---|---|
| Exact Release Please 17.6.0 fake-SCM harness | available | selected | Executes the package-level Manifest/plugin chain against a no-write fake SCM. |
| Stage-B carrier validators and tag planner | available | selected | Pure local positive, negative, retry, and conflict behavior is executable. |
| Local Cargo/Rust quality and source runtime | available | selected | Pinned metadata, tests, check, fmt, Clippy, version, profiles, and package verification run locally. |
| Local Python provenance/distribution checks | available | selected | Version, lockfile, package graph, archive, private-boundary, and mutation checks run locally. |
| Local npm typecheck/test/package dry-run | available | selected | Wrapper behavior, package identity, target constraints, and seven dry-run packs run locally. |
| Local OCI Buildx/daemon/QEMU | available | selected | Both local `linux/amd64` and `linux/arm64` build/load/run/evidence paths run without a registry. |
| Workflow/actionlint/ShellCheck/Dockerfile diagnostics | available | selected as diagnostics | Executed for the requested security gates, but static inspection is not recorded as QA `PASS`. |
| Read-only Git remote metadata | available | selected | Empty `v*.*.*` remote tag listing recorded without hosted mutation. |
| Hosted GitHub Actions/PR/tag/release execution | unavailable | rejected | No safe target or authorized hosted rehearsal was supplied; absence cannot become a pass. |
| Cargo/npm/GHCR/GitHub publication and upload | available in principle | rejected | Explicitly prohibited by the user; no registry state was mutated. |
| Attestation/provenance publication | unavailable for QA | rejected | Requires a hosted identity-token/attestation run, explicitly prohibited here. |
| Native non-host archive target runners | unavailable | rejected | macOS arm64 cannot provide native evidence for the seven other archive targets. |
| Failure injection and rollback rehearsal | unavailable under policy | rejected | Requires disposable hosted/provider state or publication writes. |
| Browser/API/data/persistence | not applicable | rejected | No browser, HTTP API, database, or persistence contract is in scope. |
| Accessibility/responsive/internationalization/locale | not applicable | rejected | No UI or locale-dependent behavior exists in the target surface. |
| Manual/exploratory shell behavior | available | selected | Repeated commands, negative fixtures, checksum tampering, and local OCI smoke were exercised. |

## 5. Scenario matrix

`PASS` below means executable local behavior produced the specified result. Static-only evidence is
never recorded as `PASS`; those rows are `NOT TESTED` even when the diagnostic command exited 0.

| ID | Capability / acceptance scenario | Result | Evidence or reason |
|---|---|---|---|
| CI-1 | Untrusted pull request runs without release credentials or publication ability. | BLOCKED | No hosted PR target or isolated runner was available; local permission text cannot prove runtime secret isolation. |
| CI-2 | Mutable workflow action reference fails before distribution. | NOT TESTED | `actionlint` and full-SHA diagnostics exited 0 in `workflow/actionlint.log`; no mutable-reference injection was run, and static inspection is not acceptance. |
| CI-3 | Pinned metadata, locked tests, fmt, Clippy, and Python contract checks pass. | PASS | Successful commands are in `cargo/1.log`–`cargo/5.log` and `focused/4.log`–`focused/7.log`; workspace tests passed with 31 tests and 0 failures. |
| CI-4 | Known lint failure remains blocking without weakening the gate. | NOT TESTED | Clippy passed; no source/workflow failure injection was permitted. Rerun needs an isolated failing fixture or hosted run. |
| CI-5 | Incomplete target declaration blocks distribution eligibility. | PASS | Removing one archive manifest caused the validator to exit 1 (`expected 8 archive manifests, found 7`); evidence in `archives.log` and `archives-incomplete.log`. |
| CI-6 | Failed preflight blocks later publication jobs and retains evidence. | BLOCKED | Local workflow dependencies were only statically diagnosed; no hosted failure-injection run was available. |
| CARGO-1 | Complete runtime graph packages/publishes in dependency order. | BLOCKED | Five local `cargo package --locked --allow-dirty` checks passed in `cargo-corrected/*.log`; crates.io publication/order observation was prohibited. |
| CARGO-2 | Source install/build retains the CLI contracts. | PASS | Locked workspace build/tests and `cargo run ... version`/`profiles` passed; evidence in `cargo/2.log`, `cargo/6.log`, and `cargo/7.log`. |
| CARGO-3 | Immutable recorded Git revision installs with release behavior. | BLOCKED | No `vX.Y.Z` tag or immutable release revision exists; remote tag listing is empty in `hosted-read-only.log`. |
| CARGO-4 | Distribution-only change preserves RFC-0001 behavior/contracts. | PASS | Locked conformance, integration, and CLI tests all passed in `cargo/2.log`; no engine contract source was changed by QA. |
| CARGO-5 | Missing required Cargo package file stops before upload. | NOT TESTED | Positive package checks passed; no package-file deletion fixture was run. Rerun needs a temporary copied package fixture. |
| CARGO-6 | Manifest/lockfile/binary version mismatch blocks release validation. | PASS | `release_carrier_tests.py` and `release_provenance_tests.py` rejected graph/version/tag/source-revision mutations; evidence in `focused/2.log` and `focused/4.log`. |
| NPM-1 | Only the approved base and six same-scope platform packages are eligible. | PASS | Generator check, npm typecheck/tests, wrapper pack, and six platform `npm pack --dry-run` commands passed; evidence in `npm/*.log` and `focused/13.log`. |
| NPM-2 | Supported runtime selects exactly its matching platform package. | PASS | Local wrapper test suite passed target-resolution coverage on the available host/test fixture; evidence in `npm/tests.log`. |
| NPM-3 | Unsupported or missing optional dependency returns actionable nonzero error. | PASS | npm tests passed missing-dependency and musl/unsupported-target cases; evidence in `npm/tests.log`. |
| NPM-4 | Arguments, stdio, and child exit status pass through unchanged. | PASS | npm wrapper test suite passed the passthrough case; evidence in `npm/tests.log`. |
| NPM-5 | Checksum mismatch blocks platform and base npm eligibility. | PASS | The local corruption/provenance regressions passed, and the independent archive tamper fixture exited 1 before eligibility; evidence in `focused/4.log` and `archives-tampered.log`. |
| REL-1 | Release provenance is one immutable version/source identity from merged main. | BLOCKED | Local validators and drift negatives pass, but no immutable release-please tag, merged hosted PR, or GitHub Release exists. |
| REL-2 | Root updates survive the exact Release Please 17.6.0 plugin pipeline. | PASS | Exact fake-SCM chain produced the root carrier, five runtime Cargo updates, package/changelog updates, and one synchronized PR; latest technical probe also recorded the effective 31-path set. Evidence in `focused/1.log` and the latest `verify-report.md`. |
| REL-3 | Virtual root remains a non-publishable metadata carrier. | PASS | Current config and runtime harness preserve `release-type: java`, no root package identity, and skipped Stage-A release creation; evidence in `focused/1.log` and `focused/4.log`. |
| REL-4 | Private conformance remains non-release/non-linked while its four root-carrier dependency pins align. | BLOCKED | Hosted PR `#59` proved that exclusion-only Stage A leaves `cargo metadata --locked` broken; Phase 9 exact-pin implementation and rerun are pending. |
| REL-5 | v17.6.0 empty-component/tag coupling is avoided. | PASS | Component-tagged Stage A produced a full 13-component linked map while the fake SCM observed no release/tag calls; evidence in `focused/1.log`. |
| REL-6 | All six npm optional pins synchronize to the linked version. | PASS | Harness output recorded six optional dependency versions rewritten to `0.2.0`; evidence in `focused/1.log`. |
| REL-7 | Complete eight-target archive release has correct formats/checksums/evidence. | BLOCKED | Local synthetic packaging verified 8/8 archive formats, manifests, and checksums, but seven target binaries were explicitly `cross-target/execution=not-run`; evidence in `archives.log` and `archives/`. |
| REL-8 | Missing target evidence blocks release assets and dependent channels. | PASS | The incomplete archive fixture exited 1 before any publisher command; evidence in `archives-incomplete.log`. |
| REL-9 | Checksum/package/metadata failure blocks later upload/publishers. | BLOCKED | Local validators fail closed on tampered input, but no hosted graph or publisher failure injection was run; evidence of the local negative is in `archives-tampered.log`. |
| REL-10 | Credential exposure fails promotion and does not leak tokens. | BLOCKED | No credential-bearing run, login, upload, or attestation was permitted; static no-literal diagnostics are not runtime acceptance. |
| REL-11 | Partial publication stops later jobs and exposes recovery. | BLOCKED | Publication and rollback rehearsal were explicitly prohibited; no partial external state exists to inspect. |
| OCI-1 | Only `ghcr.io/yacosta738/codegauge` is eligible for publication. | BLOCKED | Local identity/permission diagnostics passed, but no GHCR login/push or registry observation was authorized. |
| OCI-2 | Unsupported architecture is rejected. | PASS | Executable OCI negative suite rejected `linux/ppc64le`; evidence in `focused/8.log`–`focused/11.log`. |
| OCI-3 | Workspace-aware non-root images build/run for amd64 and arm64. | PASS | `build_oci_release.sh` built, loaded, ran, and verified both local architectures with version/profile/contract/non-root evidence; evidence in `oci-local-build-corrected.log` and `oci/{amd64,arm64}.json`. |
| OCI-4 | OCI label/runtime/root/emulation/digest mismatch fails validation. | PASS | Positive and negative OCI evidence suites passed; real local evidence retained distinct Docker/OCI digest domains in `/tmp/codegauge-rf6-qa.weKmyI/oci/`. |
| OCI-5 | Failed architecture blocks manifest/tag publication. | BLOCKED | No registry manifest/tag publication or hosted architecture failure injection was run. |
| R-F6-A | Stage-A exact v17.6.0 fake-SCM creates one PR, rewrites six optional pins, makes no release/tag calls, and applies only the root-carrier private pin exception. | BLOCKED | The current harness still asserts private-path exclusion; it must be updated to expect one exact root-owned private manifest update after the hosted `#59` failure. |
| R-F6-B | Stage-B positive carrier validates one merged-main version PR and canonical tag record. | PASS | `python3 tests/release_carrier_tests.py` exited 0; copied-tree positive carrier record matched `v0.2.0` and the expected merge SHA. |
| R-F6-C | Stage-B accepts only the four private dependency-version edits and rejects private package/changelog/other-path mutations. | BLOCKED | The current validator rejects the entire private path; content-aware exception tests and implementation are pending in Phase 9. |
| R-F6-D | Tag planning is idempotent and conflict-safe. | PASS | Create, same-SHA no-op, different-SHA conflict, annotated-tag rejection, existing-release conflict, retry, and bootstrap-version cases passed in `focused/2.log`. |
| R-F6-E | Workflow security gates enforce full SHAs, least privilege, token separation, concurrency, and canonical topology. | NOT TESTED | `release_carrier_static_tests.py`, `distribution_checks.py`, `actionlint`, and ShellCheck exited 0, but this is static-only evidence and no hosted workflow acceptance is claimed. |
| R-F6-F | Canonical tag state transition delivers the tag-triggered downstream release graph. | BLOCKED | Local pure planning/topology diagnostics pass, but no hosted tag creation, event delivery, build/publish graph, release URL, or downstream run was available. |

## 6. Untested scope and rerun prerequisites

| Scope | Result | Reason / rerun prerequisite |
|---|---|---|
| Hosted Stage-A PR and zero-artifact observation | BLOCKED | Requires an isolated protected GitHub target and authorized repository-scoped token; capture one PR, exact diff, zero tags/releases, and secret-safe logs. |
| Merged-main carrier, compare/create race, canonical tag delivery | BLOCKED | Requires a permitted merged test PR and hosted run; capture one lightweight `vX.Y.Z` ref at the merge SHA, same-SHA retry no-op, and conflicting-SHA fail-closed behavior. |
| Tag-triggered build/release URL/downstream gating | BLOCKED | Requires the canonical tag event and a hosted dry-run; capture build `needs` completion, release identity, and no-publication behavior. |
| Cargo/npm/GitHub Release/GHCR publication | BLOCKED | Explicitly prohibited in this QA. Rerun only in an approved release window with scoped credentials and provider-safe test/release policy. |
| OCI final manifest and attestation | BLOCKED | Local architecture evidence is retained, but registry manifest creation and attestations require hosted `packages`/OIDC writes, which were prohibited. |
| Native evidence for seven non-host archive targets | BLOCKED | The local eight-target fixture marks seven binaries `execution=not-run`; rerun on the declared native/cross-target runner matrix with executable evidence for every claimed target. |
| Failure injection and non-atomic rollback | BLOCKED | No publication state may be mutated here. Rerun in a disposable/provider-supported rehearsal and capture stop order, retained evidence, deprecation/retag/corrected-patch recovery. |
| Missing Cargo package-file failure | NOT TESTED | No repository file was removed. Rerun against a temporary copied package fixture and prove no upload follows the failed preflight. |
| Browser, accessibility, responsive, locale, API, data, and persistence scenarios | NOT TESTED | Not applicable to this CLI/workflow/archive/OCI surface; no target UI/API/store exists. Do not invent a target. |

## 7. Findings

| ID | Severity | Finding | Status |
|---|---|---|---|
| QA-001 | P1 | Hosted Stage-A, merged-main carrier, immutable canonical tag, tag event delivery, and downstream release provenance were not observable. | Open — acceptance blocker; requires authorized hosted rehearsal. |
| QA-002 | P1 | Cargo/npm/GitHub Release/GHCR publication, final manifest, and attestation were not executed. | Open — explicitly prohibited by safety scope; archive gate remains blocked. |
| QA-003 | P1 | Seven non-host archive targets lack native/executable evidence, and no immutable release artifact exists. | Open — requires the declared hosted/native target matrix and a canonical tag. |
| QA-004 | P2 | Hosted preflight failure propagation, missing-package failure, partial publication, and rollback were not injected. | Open — no observed implementation defect; rerun requires disposable failure fixtures/provider state. |
| QA-005 | P2 | Workflow/action security checks are static diagnostics only; no hosted least-privilege or secret-isolation observation exists. | Open — no observed static defect; acceptance remains untested. |

No `FAIL` scenario was observed in the executable local scope. No CRITICAL or P0 implementation
finding remains. **Yes: open P1 acceptance blockers remain** (QA-001 through QA-003), all caused by
missing/prohibited external acceptance evidence rather than a newly observed local code failure.

## 8. Final verdict

`BLOCKED`

### Verdict rationale

The local acceptance boundary is green only for the previously implemented exclusion-only behavior:
exact Release Please 17.6.0 fake-SCM behavior, six optional-pin rewrites, no Stage-A release/tag
calls, Stage-B positive/negative/idempotency/conflict behavior, local Cargo/npm/package quality,
archive/checksum validators, and real local amd64/arm64 OCI runtime evidence. Hosted PR `#59` proves
that this is insufficient because locked metadata still fails on stale private pins. The exact
root-carrier exception and content-aware Stage-B acceptance are unimplemented, and the requested
hosted transition, immutable release provenance, complete native target matrix, publication ordering,
attestation, and rollback cannot be observed under the explicit no-write/no-credential boundary. Per
the QA/archive policy, those `BLOCKED` scenarios cannot be converted to `PASS` or `PASS WITH WARNINGS`;
archive must remain gated.

## 9. Implementation handoff

- QA did not modify source code, workflows, credentials, release state, registries, or tags.
- `qa-report.md` is the auditable record for this run; evidence is under
  `/tmp/codegauge-rf6-qa.weKmyI/`.
- A subsequent apply slice added a temporary, credential-free hosted carrier rehearsal guard:
  manual `dry_run: true` and automatic `RELEASE_CARRIER_DRY_RUN=true` now select plan-only mode;
  unset/`false` remains live by default. This implementation update requires a fresh `sdd-verify`
  and independent QA rerun; it is not acceptance evidence for the hosted path.
- The prior QA handoff records verdict `BLOCKED`; after this apply slice, state returns to `sdd-verify`
  before QA is rerun. Do not archive until QA-001 through QA-003 are resolved or an explicit policy
  exception is approved; this production distribution change has no documentation-only exception.
- Hosted Stage-A/merged-main/tag-triggered rehearsal remains pending. No hosted writes, tag/label
  mutation, release dispatch, upload, publication, credential use, or registry state change was
  performed by the apply slice.
- This report does not claim Cargo, npm, GitHub Release, GHCR, attestation, hosted workflow, or product
  acceptance.

## Superseded prior QA record

The original 2026-08-13 QA record below is retained for audit history and is not the current verdict.

## Identity

- Change: `codegauge-distribution`
- Mode: OpenSpec
- QA phase: `sdd-qa`
- Date: 2026-08-13
- QA verdict: `BLOCKED`
- State handoff: `state.yaml` was not modified, as requested.

## Sources of Truth

- Proposal: `openspec/changes/codegauge-distribution/proposal.md`
- Specifications:
  - `openspec/changes/codegauge-distribution/specs/ci-quality-gates/spec.md`
  - `openspec/changes/codegauge-distribution/specs/cargo-distribution/spec.md`
  - `openspec/changes/codegauge-distribution/specs/npm-distribution/spec.md`
  - `openspec/changes/codegauge-distribution/specs/release-artifacts/spec.md`
  - `openspec/changes/codegauge-distribution/specs/oci-distribution/spec.md`
- Design: `openspec/changes/codegauge-distribution/design.md`
- Tasks: `openspec/changes/codegauge-distribution/tasks.md`
- Apply handoff: `openspec/changes/codegauge-distribution/apply-progress.md`
- Technical verification: `openspec/changes/codegauge-distribution/verify-report.md`
- State: `openspec/changes/codegauge-distribution/state.yaml`
- Configuration: `openspec/config.yaml`

Technical verification handed off as `PASS WITH WARNINGS`. It reports 11/28 scenarios locally
compliant, 17/28 partial, and no observed failures; the partial results include hosted release,
registry, immutable-tag, and non-host target limitations. This report is an independent acceptance
record and does not convert those partial results into product acceptance.

## Target and Environment

- Target: the local CodeGauge checkout at `/Users/acosta/Dev/agent-swarm/codegauge`, version `0.1.0`,
  current source revision `6477eb1f58fc2ea3f0ab9319eee59c4e463d32e4`.
- Source state: intentionally dirty distribution worktree; no commit, branch, push, publication, or
  production-code repair was performed.
- Host: macOS arm64.
- Tools: Rust/Cargo `1.97.1`, Node `v24.19.0`, npm `11.17.0`, Python `3.14.6`, Docker `29.4.0`,
  BuildKit `v0.32.2` via the running `pt-builder`, `actionlint`, and `shellcheck`.
- Docker: local daemon and arm64 emulation were available. No registry login or push was performed.
- GitHub: no local `v0.1.0` tag or corresponding GitHub Release exists. A read-only release lookup
  returned `release not found`.
- Credentials/permissions: no Cargo, npm, GHCR, or GitHub write operation was authorized or run.
  No registry token was injected into the QA commands.
- Limitations: hosted GitHub Actions execution, release-please tag creation, native execution on
  seven non-host archive targets, Cargo/npm/GHCR publication, final OCI manifest publication,
  attestation, and rollback rehearsal were not executable within the requested safety boundary.

## Capability Inventory

| Capability | Availability | Selected? | Rationale / rejection reason |
|---|---|---:|---|
| Local Cargo/source install and CLI runtime | available | yes | Executable target; used for version, profiles, analysis, errors, repeatability, and hostile-input checks. |
| Local Rust/Python/npm quality runners | available | yes | Produced observable command results for the local quality and package gates. |
| npm staged-package runtime | available | yes | Host is macOS arm64; staged matching platform package and synthetic child packages exercised wrapper behavior. |
| Archive/package generator and provenance validators | available | yes | Generated and verified a local eight-target archive fixture set without publication. |
| Docker Buildx/daemon/QEMU | available | yes | Built, loaded, inspected, and ran both `linux/amd64` and `linux/arm64` images locally. |
| Workflow/actionlint/ShellCheck audit | available | yes | Used for local diagnostics only; static evidence is not treated as acceptance of hosted behavior. |
| Git/GitHub read-only metadata | available | yes | Confirmed current revision and absence of the requested local/remote release target; no write operation. |
| Hosted GitHub Actions/release-please run | unavailable | no | No hosted run target was supplied or safely available in this environment. |
| Cargo/npm/GHCR/GitHub publication | available in principle | rejected | Explicitly prohibited by the request; no registry state was mutated. |
| Browser/API/data/persistence capability | not applicable | no | CodeGauge distribution is a CLI, package, workflow, archive, and OCI target; it has no browser/API/data-store surface. |
| Accessibility/responsive/locale capability | not applicable | no | No UI or locale-dependent acceptance contract is defined for this change. |
| Manual/exploratory shell checks | available | yes | Used for repeated invocation, negative paths, process passthrough, and local release smoke behavior. |

## Scenario Matrix

Every scenario has one allowed result: `PASS`, `FAIL`, `BLOCKED`, or `NOT TESTED`.

| ID | Capability | Acceptance scenario | Result | Evidence or reason |
|---|---|---|---|---|
| CI-1 | Hosted CI | An untrusted pull request runs read-only without release credentials or publication ability. | BLOCKED | Local permission audit passed, but no hosted pull-request run or credential-isolation observation was available. |
| CI-2 | Workflow validation | A mutable action reference causes validation to fail before distribution starts. | BLOCKED | All 33 external workflow action references were locally audited as full 40-hex SHAs and `actionlint` passed; no mutable-reference injection was run. Static inspection is not acceptance execution. |
| CI-3 | Local quality runner | Pinned metadata, locked tests, format, Clippy, and Python contract/distribution checks all pass. | PASS | Exact local commands passed: `cargo +1.97.1 metadata --locked`, workspace tests, fmt, Clippy `-D warnings`, bootstrap, README, distribution, release-provenance, OCI, and npm-generator checks. Evidence log directory: `/tmp/codegauge-qa-quality.xCHfzU`. |
| CI-4 | Failure injection | A known Clippy failure remains blocking and does not weaken linting or engine behavior. | NOT TESTED | Current Clippy passes; no source or workflow mutation was made to inject a failure. Rerun requires an isolated failure-injection branch or hosted run. |
| CI-5 | Provenance validator | An incomplete target declaration prevents later distribution eligibility. | PASS | Removing one of eight archive manifests caused `verify_release_provenance.py archives` to exit nonzero with `expected 8 archive manifests, found 7`; no publisher was invoked. |
| CI-6 | Hosted release graph | A failed preflight blocks later publishers and retains failure evidence. | BLOCKED | Workflow dependency/fail-stop wiring was audited locally, but no hosted failure-injection run was permitted or available. |
| CARGO-1 | Cargo registry | The approved runtime graph packages and publishes in dependency order. | BLOCKED | All five runtime crates packaged locally and the leaf `cargo publish --dry-run` passed; actual crates.io publication/order observation was prohibited. |
| CARGO-2 | Cargo/source runtime | A repository/source install builds with the pinned lockfile and exposes the released contracts. | PASS | Real `cargo +1.97.1 install --path crates/codegauge-cli --locked` succeeded. Installed binary returned `codegauge 0.1.0`, `java-jacoco-v1`, and a `COMPLETE` `codegauge-result/v1` analysis. |
| CARGO-3 | Immutable source runtime | An immutable recorded Git revision installs and preserves version/profile/analysis behavior. | BLOCKED | The checkout has no `v0.1.0` tag or recorded release revision target; only the current dirty source was exercised. |
| CARGO-4 | RFC-0001 runtime audit | Distribution-only changes preserve RFC-0001 observable behavior and contracts. | PASS | Baseline `6477eb1` and current binaries matched exit codes, stdout JSON, stderr, version, profiles, and seven fixture behaviors after masking only `analysis_timestamp`; 9 cases passed. Evidence: `/tmp/codegauge-qa-rfc.R9LVn3/rfc-full-comparison.json`. |
| CARGO-5 | Cargo package failure path | A package missing a required file stops before registry upload. | NOT TESTED | Complete local package checks passed; no missing-file package rehearsal was run. Rerun requires an isolated temporary package fixture or hosted preflight failure. |
| CARGO-6 | Version/provenance validator | A manifest/binary/version mismatch blocks release validation. | PASS | Local provenance tests rejected version `9.9.9`, invalid tag identity, mismatched main SHA, wrong binary version, and archive source-revision drift. |
| NPM-1 | npm packaging | Only the approved base package and six same-scope platform packages are eligible. | PASS | Generator check, all six manifest checks, base `npm pack --dry-run`, six platform `npm pack --dry-run` checks, and local typed preflight passed. |
| NPM-2 | npm runtime | A supported runtime resolves exactly its matching optional dependency and executable. | PASS | On host `darwin/arm64`, the wrapper resolved `@yacosta738/codegauge-darwin-arm64`; real version, profiles, and analysis calls returned the expected contracts. |
| NPM-3 | npm negative runtime | Missing optional dependency, unsupported OS, and musl Linux return actionable nonzero errors without running another binary. | PASS | Missing dependency returned nonzero with an actionable reinstall message; process-platform overrides returned nonzero for `freebsd/x64` and Linux musl with explicit supported-target/libc messages. |
| NPM-4 | npm process passthrough | Arguments, stdin/stdout/stderr, and child exit status pass through unchanged. | PASS | Synthetic child received `analyze --profile java-jacoco-v1`, echoed stdin, emitted argv on stderr, and exited `17`; wrapper returned `17`. |
| NPM-5 | npm checksum gate | A corrupted archive/sidecar stops both platform and base package eligibility. | PASS | npm test passed the corruption regression with `platformEligible=false` and `baseEligible=false`; the release archive validator separately rejected tampered bytes with `archive checksum mismatch`. |
| REL-1 | Release provenance | A release is derived from an immutable release-please tag on merged `main`, with one version/source identity across channels. | BLOCKED | Local validator wiring and negative checks passed, but `v0.1.0` is absent locally and the GitHub Release lookup returned `release not found`; no hosted release-please execution was run. |
| REL-2 | Archive matrix | The complete eight-target release has correct formats, names, manifests, checksums, and executable/runtime evidence. | BLOCKED | Local packager created and verified 8/8 archive formats, names, lowercase sidecars, and manifests, but the local set used explicit cross-target `execution=not-run` evidence for non-host binaries; hosted/native matrix evidence was not available. |
| REL-3 | Archive negative gate | Missing target evidence prevents assets and dependent registries from proceeding. | PASS | Seven-of-eight manifest validation exited nonzero before any upload or publisher command. |
| REL-4 | Release ordering | Checksum/package/metadata failure prevents later channel publishers. | BLOCKED | Local validators and workflow dependency ordering were inspected; no hosted release graph was executed with an injected failing gate. |
| REL-5 | Release security | Credential exposure fails promotion and secrets do not enter artifacts/logs. | BLOCKED | No credential-bearing release run, registry login, or attestation was performed; local workflow audit found no committed token literal, but behavior on an exposed-token run was not exercised. |
| REL-6 | Partial publication recovery | A later npm/OCI failure stops subsequent jobs, retains history, and exposes a corrected recovery path. | BLOCKED | No publication or failure injection was allowed. README/workflow recovery guidance exists, but no observable partial-publication state or rollback rehearsal was produced. |
| OCI-1 | OCI publication | Only `ghcr.io/yacosta738/codegauge` is eligible for the approved image release. | BLOCKED | Local workflow identity/permission checks passed; GHCR login, push, and registry identity observation were explicitly not run. |
| OCI-2 | OCI negative validator | An unsupported architecture is rejected rather than claimed. | PASS | Executable OCI verifier negative test rejected `linux/ppc64le`. |
| OCI-3 | Local Docker runtime | Workspace-aware images build for amd64/arm64, run non-root with init, and expose version/profile/analysis contracts. | PASS | Real local Buildx builds and Docker loads passed for both architectures. Both reported `codegauge 0.1.0`, `java-jacoco-v1`, `codegauge-result/v1` `COMPLETE`, UID `100`, user `codegauge`, and `/sbin/tini` entrypoint. Evidence: `/tmp/codegauge-qa-oci.18eCHz/{amd64,arm64}.evidence.json`. |
| OCI-4 | OCI metadata/failure validator | Label, runtime version, root user, emulation, or digest mismatch prevents image eligibility. | PASS | Executable positive/negative verifier suite passed for label drift, runtime version drift, root UID, missing arm64 emulation evidence, metadata digest drift, and Docker/OCI digest-domain mismatch. |
| OCI-5 | OCI publication gate | A failed architecture prevents manifest/tag publication. | BLOCKED | Real positive amd64/arm64 builds passed, but no architecture failure injection or registry manifest publication was run. |
| RFC-1 | Manual/exploratory runtime | Repeated source invocations preserve results, while negative/boundary/hostile inputs preserve error mappings and schemas. | PASS | Source QA exercised repeatability, partial exit `6`, unsupported profile `4`, missing input `3`, malformed/duplicate/DOCTYPE input `5`, and unsupported format `2`; all outputs matched the expected JSON/error contracts. |
| RFC-2 | Immutable release runtime | The actual released tag/archive/image preserves RFC-0001 contracts after distribution publication. | BLOCKED | No immutable release tag, published archive, registry package, or remote OCI digest was available to run this acceptance smoke. |

## Untested Scope

| Scope | Reason | Re-run prerequisite |
|---|---|---|
| Hosted pull-request CI permission isolation and injected workflow failures | No hosted runner execution was supplied; static checks cannot establish runtime acceptance. | Run CI on an untrusted PR and an isolated negative workflow fixture; capture job permissions, skipped downstream jobs, and retained logs. |
| Immutable release-please tag/main/release URL provenance | Current checkout has no `v0.1.0` tag and no matching GitHub Release. | Run from a release-please-created tag on merged `main`; capture tag SHA, main SHA, release URL, and positive validator output. |
| Native/runtime evidence for seven non-host archive targets | Local host is macOS arm64; cross-target packaging records `execution=not-run`. | Execute the configured native/cross-target hosted matrix and retain binary version/profile/contract evidence for every claimed target. |
| Cargo/npm/GitHub Release/GHCR publication and attestations | Explicitly prohibited; no registry state may be mutated in this QA run. | Obtain an approved release window and credentials, then run the gated dry-run/publication path with secret-safe logs. |
| Partial publication and rollback recovery | No publisher was allowed to fail after a prior channel succeeded. | Use a disposable release rehearsal or provider-supported test namespace; inject a later-channel failure and record stop/deprecation/corrected-patch actions. |
| Missing Cargo package-file failure rehearsal | Complete packages passed and production files must not be altered. | Use a temporary copied package fixture and verify that the registry gate exits before publication. |

## Findings

| ID | Severity | Scenario / location | Evidence | Status |
|---|---|---|---|---|
| QA-001 | P1 | Hosted release provenance and cross-registry publication (`REL-1`, `REL-4`–`REL-6`, `OCI-1`, `RFC-2`) | No `v0.1.0` tag or GitHub Release; no Cargo/npm/GHCR/GitHub write or attestation run by policy. | Open — external acceptance gate; blocks archive. |
| QA-002 | P1 | Complete release target acceptance (`REL-2`, `CARGO-3`) | Local archive set is structurally complete, but non-host binary evidence is explicitly `cross-target/execution=not-run`; no immutable revision install. | Open — hosted/native target evidence required; blocks archive. |
| QA-003 | P2 | Failure-injection coverage (`CI-2`, `CI-4`, `CI-6`, `CARGO-5`, `OCI-5`) | Local actionlint/validators and fail-stop wiring pass, but no injected failing hosted/package/architecture run was performed. | Open — rerun prerequisite; no observed implementation failure. |
| QA-004 | P2 | Release recovery rehearsal (`REL-6`) | Recovery guidance is documented, but no partial publication state, registry deprecation, retag, or corrected-patch rehearsal exists. | Open — external rehearsal required; warning only after acceptance gate is unblocked. |

No `FAIL` result and no `CRITICAL`/P0 finding was observed in the executable local acceptance scope.

## Verdict

`BLOCKED`

### Rationale

Local acceptance evidence is strong for the executable surfaces: pinned source installation, version/
profiles/analysis and error contracts, npm host resolution and process passthrough, checksum stop paths,
archive generation and local verification, RFC-0001 runtime equivalence, and real non-root amd64/arm64
Docker builds all passed. However, the requested distribution capability includes acceptance of an
immutable release provenance chain, complete target evidence, ordered external publication, final OCI
manifest/attestation, and non-atomic recovery. Those scenarios were intentionally not executed because
publication, credentials, and registry mutation were prohibited and no hosted release target exists in
this environment. Under the QA/archive policy, acceptance-relevant `BLOCKED` scope normally blocks
archive; the verdict therefore cannot be `PASS` or `PASS WITH WARNINGS`.

## Evidence Summary

- Local quality suite: all exact Rust/Python distribution checks passed; `/tmp/codegauge-qa-quality.xCHfzU`.
- Cargo/source QA: installed binary passed version, profiles, complete/partial analysis, negative CLI,
  hostile input, and repeatability checks; `/tmp/codegauge-qa-source.YgP6tj/source-qa.json`.
- Cargo package QA: all five runtime crates passed locked package verification with local patch
  configuration; `/tmp/codegauge-qa-cargo-package.bftj1K`.
- npm QA: typecheck, 7 tests, base pack, and six platform packs passed; `/tmp/codegauge-qa-npm.wWkhpJ`.
- npm runtime QA: host package selection, analysis, missing dependency, unsupported platform, musl
  rejection, stdin/argv/exit passthrough passed; `/tmp/codegauge-qa-npm-runtime2.*`.
- Archive QA: 8/8 local archive formats, 8/8 lowercase sidecars, 8/8 manifests, positive provenance,
  checksum tamper rejection, and 7/8 incomplete-matrix rejection passed; `/tmp/codegauge-qa-archives.93hohU`.
- OCI QA: local verifier passed both architecture evidence files and preserved distinct Docker config,
  Docker platform, OCI config/platform/index, and BuildKit metadata digests; `/tmp/codegauge-qa-oci.18eCHz`.
- RFC-0001 audit: baseline/current runtime comparison passed for version, profiles, and all seven XML
  fixtures after masking only the timestamp; `/tmp/codegauge-qa-rfc.R9LVn3/rfc-full-comparison.json`.
- Workflow diagnostics: `actionlint`, `shellcheck`, distribution checks, release-provenance tests,
  and OCI tests passed. All workflow actions were locally confirmed to use immutable full-SHA refs.

## Limitations and Handoff

- QA did not modify source code, workflows, credentials, release state, or `state.yaml`.
- This report does not claim Cargo, npm, GitHub Release, GHCR, or product acceptance.
- Recommended next step: rerun `sdd-qa` from an immutable release-please tag on merged `main` with
  approved hosted-runner evidence and a safe, authorized release rehearsal. Run `sdd-archive` only
  after the blocked acceptance scenarios are resolved or an explicit policy exception is recorded.

## Latest apply handoff — hosted GitHub PR patch parser defect — 2026-08-15

QA remains **BLOCKED** and was not rerun. This section records the implementation handoff only.

- Hosted run `#31878496886` reached validation for the real merged Release Please PR `#59` and found
  that the validator rejected GitHub's valid hunk-only `.release-please-manifest.json` patch because
  it had no local `diff --git`, `---`, or `+++` headers.
- The parser fix accepts exactly a complete single-file unified diff or a filename-bound GitHub
  PR-files hunk-only patch, with strict hunk/body/count, status/header, path, and unexpected-section
  checks. Local RED/GREEN evidence and the full carrier/provenance/runtime/distribution quality
  matrix passed.
- The exact 32-path Stage-A changeset, private four-pin exception, generated-file content validation,
  no-match carrier no-op, dry-run/live gates, and no-publication contract remain preserved.
- No tag, GitHub Release, Cargo/npm/GHCR publication, upload, attestation, workflow dispatch,
  repository-variable change, credential use, merge, push, or hosted write occurred. Hosted run
  `#31878496886` found the bug, and this fix is **not yet hosted-verified**.
- `sdd-verify` must rerun before independent QA. The protected hosted rerun remains separately
  authorized work; this handoff makes no user/operator acceptance claim.

## Latest technical verification handoff — Phase 10 parser fix — 2026-08-15

Acceptance QA remains **BLOCKED** and was not rerun. Fresh technical verification returned
**PASS WITH WARNINGS** with no local implementation defect; this report does not claim hosted or
operator acceptance.

- The real `.release-please-manifest.json` fixture passed as a filename-bound GitHub PR-files
  hunk-only patch with no `diff --git`, `---`, or `+++` headers, and the complete unified-diff form
  also passed. Read-only matrices passed both forms for all 31 content-bearing Stage-A entries;
  the exact Release Please effective set remains 32 paths because the unmarked CLI fixture has no
  content mutation.
- Strict hunk/body and additions/deletions/changes count validation rejected missing metadata,
  missing patches, malformed/truncated/inconsistent hunks, and unexpected multi-file sections.
- The exact `release-please@17.6.0` fake-SCM still records version `0.2.0`, 32 effective paths,
  exactly four private dependency pins, six npm optional pin rewrites, one synchronized PR, and
  zero release/tag calls. The private package remains `0.1.0` and `publish = false`.
- Stage-B validators still reject generated-file wrong versions/arbitrary content, private package
  and unrelated mutations, unapproved paths, missing roots, malformed SemVer, duplicate/truncated
  patches, and tag/release conflicts. The synchronized copied workspace passes `cargo test
  --workspace --locked`.
- Current Cargo/Python/npm/OCI/workflow/package/whitespace checks and the ordinary-main no-match plus
  dry-run/live mode probes passed locally. No hosted writes, credentials, tags, releases, registry
  publication, uploads, attestations, variables, merges, pushes, or dispatches were used.

QA remains blocked on the independent acceptance rerun and separately authorized hosted evidence for
the real merged PR/carrier path, tag delivery, publication/attestation, native target coverage, and
failure-injection/rollback. Run `sdd-qa` next; do not archive from this technical handoff alone.
