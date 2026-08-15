# Tasks: Authorized R-F6 — two-stage release carrier

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 650–1,000 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | F6.1 → F6.2 → F6.3 → F6.4 → F6.5 → F6.6 |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Base / dependency | Acceptance boundary |
|------|------|-------------------|---------------------|
| F6.1 | Source-faithful RED tests | existing remediation baseline | Tests fail on the blocked single-manifest path. |
| F6.2 | Stage 1 version-PR pass | F6.1 | One synchronized PR; zero tags/releases. |
| F6.3 | Stage 2 carrier | F6.2 | One validated immutable tag or fail closed. |
| F6.4 | Tag release wiring and gates | F6.3 | Tag-triggered build is safe; no publication in rehearsal. |
| F6.5 | Temporary carrier rehearsal guard | F6.4 | Manual/variable plan-only validation; live push default preserved. |
| F6.6 | Private conformance pin exception | F6.5 | Exact four-pin root-carrier update passes locked metadata; all other private mutations fail closed. |

Use the feature-branch chain; later units target the preceding branch. No Stack metadata.

## Phase 1: RED and source boundary

- [x] 1.1 **RED** — Extend `tests/release_provenance_tests.py` with the exact v17.6.0 component gate, 13-entry map, six pin rewrites, root/virtual/private boundaries, and tag assertions; prove the current false flag fails.
- [x] 1.2 **RED** — Add carrier fixtures for exactly one merged PR, graph/semver/metadata drift, missing/prefixed/release-conflict cases, retries, and token/dispatch contracts.
- [x] 1.3 **RED** — Extend `tests/distribution_checks.py` to require Stage 1/Stage 2 separation, full-SHA actions, least privilege, concurrency, and absence of a direct Release Please publication job.

## Phase 2: Stage 1 synchronized version PR

- [x] 2.1 **GREEN** — Update `release-please-config.json`/`.release-please-manifest.json`: enable component tags, skip Stage 1 releases, remove the blocked single-manifest path and CLI override; preserve Java root ownership, five root files, npm-relative file, 13 linked paths, virtual root, and private conformance.
- [x] 2.2 **GREEN** — Reduce `.github/workflows/release-please.yml` to a pinned 17.6.0 version-PR job; remove release outputs/coupling and prove one PR, synchronized Cargo/npm versions, and zero tags/releases.

## Phase 3: Stage 2 carrier and canonical tag

- [x] 3.1 Implement carrier validators in `scripts/verify_release_provenance.py` (or a focused helper): validate `main` push/event SHA, exactly one merged PR (base/label/body/diff), clean graph, metadata, provenance, and one `vX.Y.Z`.
- [x] 3.2 Create `.github/workflows/release-tag-carrier.yml`: `main` only, `release-carrier-main` with no cancel, read permissions and `RELEASE_PLEASE_TOKEN` only (never `GITHUB_TOKEN` fallback), compare/create one lightweight ref; same SHA no-ops, conflicts fail closed.
- [x] 3.3 Create `.github/workflows/release-on-tag.yml`; migrate release workflows to tag/SHA inputs. Tag push is canonical, dispatch is guarded recovery only, and post-gate release creation rejects conflicts/duplicates.

## Phase 4: Verification and safe rollout

- [x] 4.1 Run unit/static suites, actionlint, SHA audit, locked Cargo/Python/npm checks, and mutation negatives; retain RED → GREEN → REFACTOR evidence.
- [ ] 4.2 In an isolated/protected host, rehearse one Stage 1 PR with zero artifacts, then an authorized test tag/SHA and tag-triggered `dry_run`; prove no Cargo/npm/GHCR/upload writes.
- [ ] 4.3 Run `sdd-verify` and `sdd-qa`; require PASS/PASS WITH WARNINGS, no critical issues, and a no-publication boundary until separately authorized.

## Phase 5: Stage-B carrier defect remediation

- [x] 5.1 **RED/GREEN/REFACTOR** — Replace the broad Stage-A diff regex with exact approved runtime package and generated changelog sets; cover every positive path plus evil, unknown, near-match, and unapproved changelog mutations.
- [x] 5.2 **RED/GREEN/REFACTOR** — Require every original baseline Java root carrier file to exist in the merged tree; mutate each of the five baseline root-owned files and verify fail-closed validation.
- [x] 5.3 **RED/GREEN/REFACTOR** — Enforce SemVer 2.0 numeric leading-zero rules and prerelease/build identifier rules before canonical tag planning.
- [x] 5.4 **RED/GREEN/REFACTOR** — Add an isolated exact `release-please@17.6.0` Manifest/plugin-chain harness using a read-only fake SCM; record update paths, linked optional-pin rewrites, one fake PR, and zero release/tag calls.
- [x] 5.5 Re-run focused carrier/provenance/static regressions and the complete local Cargo, npm, OCI, workflow, shell, compile, and diff checks without hosted writes.

## Phase 6: Private Stage-A candidate boundary remediation (historical baseline)

- [x] 6.1 **RED** — Extend the exact v17.6.0 fake-SCM harness to fail when the Stage-A update set contains `crates/codegauge-conformance/Cargo.toml`, and add the private-candidate Stage-B mutation rejection.
- [x] 6.2 **GREEN** — Remove the unsupported `cargo-workspace` discovery plugin from Stage A; exact v17.6.0 source evidence is `build/src/plugins/cargo-workspace.js:45-84,138-193` and `build/src/plugins/workspace.d.ts:11-16`, which provide no member exclusion. Retain the five explicit runtime Cargo candidates and use the non-Cargo Java root carrier for the approved public runtime lock/dependency TOML selectors without changing Cargo workspace membership. This exclusion-only result is superseded by Phase 9 for the four private pins.
- [x] 6.3 **REFACTOR** — Assert the five runtime Cargo versions, private lock preservation, six npm optional rewrites, one synchronized PR, and zero release/tag calls in the exact harness; document the v17.6.0 source boundary in the design/spec. The old assertion that no private manifest path may appear is retained as candidate protection, not as the final dependency-alignment contract.
- [x] 6.4 Re-run `sdd-verify`; hosted Stage-A/tagged no-publication rehearsal and downstream QA remain governed by tasks `4.2` and `4.3` and are not performed in this apply slice.

## Phase 7: Temporary hosted carrier rehearsal guard

- [x] 7.1 **RED/GREEN/REFACTOR** — Add static and runtime regressions for trusted manual `workflow_dispatch` on `main`, explicit `dry_run` normalization, repository-variable push rehearsal, live default behavior, and fail-closed invalid mode values.
- [x] 7.2 **GREEN** — Refactor `release-tag-carrier.yml` to share collection/validation, emit `carrier-record.json` and `carrier-plan.json`, and conditionally skip tag-ref/label mutations and all downstream release/publish paths in dry-run mode while retaining live push behavior.
- [x] 7.3 **REFACTOR** — Document `RELEASE_CARRIER_DRY_RUN`, the manual `dry_run=true` command, plan evidence, and variable cleanup; update the OpenSpec design/spec and QA handoff without claiming hosted execution.
- [ ] 7.4 Run the protected hosted rehearsal for both the variable-controlled merge and manual `dry_run: true`; inspect the plan record and prove no hosted write. This remains pending and is not executed by apply.

## Phase 8: Carrier event-correlation defect remediation

### Layer boundary

- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Trunk/base: `origin/main`; branch: `fix/release-carrier-skip-unmatched`; no Stack metadata.
- Scope: correlate the trusted event SHA before Stage-B validation so ordinary `main` pushes are
  auditable successful no-ops while the exact-one, multiple, and malformed paths remain fail-closed.

- [x] 8.1 **RED** — Extend the existing runtime/static carrier suites with ordinary-main zero-match,
  exactly-one-match full-path, multiple-match failure, malformed-data failure, and no-mutation guard
  regressions; confirm the pre-fix workflow/test boundary fails.
- [x] 8.2 **GREEN** — Add the read-only carrier PR classifier and CLI boundary, make the workflow emit a
  skipped `carrier-record.json`/summary and exit 0 for zero matching Release Please PRs, and gate all
  later validation/tag/label steps on exactly one matching PR.
- [x] 8.3 **REFACTOR** — Preserve the existing dry-run/live, exact diff/version/private/root/SemVer,
  idempotency/conflict, full-SHA, permissions, concurrency, and no-publication contracts; rerun the
  focused and complete local checks without hosted writes. The prior private-path rejection is now
  the baseline to narrow with Phase 9's exact four-field exception.
- [ ] 8.4 Run a new protected hosted rehearsal for an ordinary feature-PR main push and the actual
   Release Please merge; prove the former is a successful no-op and the latter still follows the
   existing dry-run/live carrier path. This remains pending and is not executed by apply.

## Phase 9: Hosted conformance dependency-pin exception (local apply complete; verify/hosted pending)

### Layer boundary

- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Trigger: hosted PR `#59` synchronized the five public runtime Cargo/npm surfaces to `0.2.0`
  without release/tag calls, then `cargo metadata --locked` failed because the private conformance
  manifest still required `^0.1.0`.
- Scope: root-carrier-owned dependency pins only; no application code, workflow behavior, release,
  tag, publication, or hosted verification in this planning update.

- [x] 9.1 **RED** — Update `tests/release_please_runtime_harness.mjs` and
  `tests/release_please_runtime_tests.py` expectations to require the private manifest as one
  root-carrier update (32 effective paths), while asserting it is absent from candidate/linked
  components, has package/lock version `0.1.0`, keeps `publish = false`, has no changelog update,
  and still records one PR plus zero release/tag calls.
- [x] 9.2 **RED** — Add harness assertions for the exact four private TOML JSONPaths and a positive
  updater result changing only those dependency versions to the synchronized public version.
- [x] 9.3 **RED** — Extend `tests/release_carrier_tests.py` with complete patch/content fixtures that
  accept only the four dependency-version replacements and reject package-version/publish/name,
  dependency-key/path/feature, comment/formatting, changelog, truncated-patch, and other-path
  mutations.
- [x] 9.4 **GREEN** — Add the four root-carrier TOML entries and make the carrier retain complete PR
  file patches or verified before/after contents; Stage-B must fail closed when content is absent.
- [x] 9.5 **REFACTOR** — Update `scripts/verify_release_provenance.py`, provenance/distribution
  checks, and acceptance criteria so private conformance remains non-publishable/non-release while
  its four runtime dependency pins converge; run `cargo metadata --locked` on the synchronized
  fixture.
- [x] 9.6 Re-ran the focused local harness/carrier suites and fresh `sdd-verify` on 2026-08-15.
  The exact 32-path synchronized fixture, locked workspace tests, typed/annotated updater boundary,
  and content-aware Stage-B mutation matrix now pass. This is technical verification only; hosted
  rerun and independent QA remain separate tasks.
- [ ] 9.7 Perform the protected hosted rerun only when authorized; prove PR `#59`-equivalent metadata
  succeeds, Stage A still makes no release/tag calls, and the corrected private mutation is accepted.
  This task remains unchecked and is not executed here.

## Historical verification handoff — 2026-08-15 (pre-Phase-8)

The `sdd-verify` executor reran the local carrier, provenance, distribution, bootstrap, README,
Release Please runtime, compile, Cargo, npm, OCI, package, workflow-lint, ShellCheck, Dockerfile,
and diff checks successfully. The exact carrier mode and plan steps were also exercised with a
read-only fake GitHub CLI; this is local evidence only. Tasks `4.2`, `4.3`, and `7.4` remain
intentionally unchecked because the protected hosted rehearsal and independent acceptance QA were
not performed under the no-write boundary.

The first hosted Stage-A rehearsal remains valid: it created PR `#59` and produced no tag or GitHub
Release. The automatic Stage-B run that observed the preceding feature-PR merge is the defect being
fixed by Phase 8; the Phase-8 no-match behavior has local regression evidence only and is not yet
hosted-verified.

## Verification handoff — 2026-08-15 (Phase 8)

Fresh `sdd-verify` completed against the dirty `fix/release-carrier-skip-unmatched` checkout. All
local implementation tasks are complete and all requested local carrier, exact Release Please
17.6.0, Cargo, npm, OCI, workflow, package, and whitespace checks passed. The four remaining
unchecked tasks are external/downstream gates: `4.2`, `7.4`, and `8.4` hosted rehearsals plus `4.3`
verification/QA handoff. Technical verdict: **PASS WITH WARNINGS**. The next phase is `sdd-qa`;
this task artifact does not claim hosted or operator acceptance.

## Superseding hosted finding — 2026-08-15

Hosted PR `#59` is now the authoritative boundary correction for the private member. Its public
version synchronization and zero Stage-A release/tag calls were successful, but merged-tree
`cargo metadata --locked` failed because the four conformance path pins remained at `^0.1.0`.
The prior exclusion-only Phase 6 result is historical and does not satisfy the corrected contract.
Phase 9 is intentionally unchecked: no implementation, workflow change, hosted rerun, tag, release,
publication, or verification success is claimed.

## Phase 9 verification handoff — 2026-08-15

- [x] Focused carrier, exact `release-please@17.6.0` fake-SCM, provenance, distribution, Cargo, npm,
  OCI, workflow, shell, package, and whitespace checks were executed without hosted writes.
- Historical note: task `9.6` was not accepted at this earlier handoff because the synchronized
  effective-tree workspace test failed in the conformance golden and Stage-B accepted a mutated
  approved generated file (`tests/golden/valid-methods.json`) by path alone. Both local defects were
  remediated by tasks `9.8` and `9.9` and are superseded by the later verification handoff.
- [ ] Task `9.7` remains pending and prohibited until the corrected local boundary receives a
  separately authorized protected hosted rerun.

## Phase 9 local defect remediation — assigned apply slice

### Layer boundary

- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Trunk/integration base: `origin/main`; branch: `fix/release-carrier-skip-unmatched`; position:
  Phase 9 local synchronized-tree and Stage-B content boundary repair. No Stack metadata.
- Scope is limited to the two latest local CRITICAL findings. Hosted rehearsal, tag/release,
  publication, credentials, variables, and parent-repository state remain out of scope.

- [x] 9.8 **RED/GREEN/REFACTOR** — Use the typed JSON updater for
  `/tests/golden/valid-methods.json` at `$.tool.version`; annotate only the four intended README
  lines and two contract fixture lines with the exact v17.6.0 `x-release-please-version` marker;
  prove the exact 32-path runtime update set and synchronized fixture `cargo test --workspace --locked`.
- [x] 9.9 **RED/GREEN/REFACTOR** — Require complete patch/count metadata and validate exact typed,
  annotated, TOML, npm, generated-changelog, and private-pin substitutions for every approved
  Stage-A path; reject wrong versions, arbitrary content, unapproved annotations, filename-only
  entries, and missing/truncated patches.
- [x] 9.10 — Run the focused/runtime/mutation suites and the complete local Cargo, Python, npm, OCI,
  workflow, ShellCheck, Dockerfile, package, and whitespace checks without hosted writes.
- [ ] 9.11 — Fresh `sdd-verify` completed locally on 2026-08-15; run independent `sdd-qa`. The
  protected hosted rerun remains separately authorized work and is not performed here.

## Phase 10: Hosted GitHub PR patch parser remediation

### Layer boundary

- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Trunk/base: `origin/main`; branch: `fix/release-private-pins-rehearsal-v2`; position: hosted
  Stage-B hunk-only PR-files patch parser repair after the Phase 9 private-pin exception. No Stack
  metadata, branch creation, commit, push, merge, tag, release, publication, credential, variable, or
  parent-repository mutation is permitted.
- Hosted run `#31878496886` reached validation for merged Release Please PR `#59` and exposed the
  parser mismatch. Preserve the exact 32-path Stage-A changeset, private four-pin exception,
  generated-file content validation, no-match carrier no-op, dry-run/live gates, and no-publication
  contract.

- [x] 10.1 **RED** — Add an actual GitHub PR-files API-shaped hunk-only
  `.release-please-manifest.json` entry, retain complete unified-diff fixtures, and reject missing,
  inconsistent, malformed/truncated, and unexpected multi-section patches.
- [x] 10.2 **GREEN** — Make `_patch_change_lines()` accept only complete single-file unified diffs or
  filename-bound GitHub hunk-only patches, validating hunk bodies/counts, path/status/header checks,
  and rejecting unexpected sections or incomplete input.
- [x] 10.3 **REFACTOR** — Re-run carrier/provenance/runtime/distribution and full local checks; update
  the specification and verification/QA handoff with hosted run `#31878496886`, the local fix, and
  the explicit not-hosted-verified/no-tag-release-publication boundary.
- [ ] 10.4 — Fresh `sdd-verify` completed locally on 2026-08-15; independent `sdd-qa` and a
  separately authorized protected hosted rerun remain pending. This phase does not claim hosted
  verification or acceptance.

## Phase 10 verification handoff — 2026-08-15

Fresh technical verification passed the parser correction locally. The exact installed
`release-please@17.6.0` chain still produces 32 effective paths, one synchronized PR, four private
dependency pin edits, six npm optional pin rewrites, and zero Stage-A release/tag calls. Complete
unified-diff fixtures and filename-bound GitHub PR-files hunk-only fixtures pass for all 31
content-bearing changed entries (the 32nd effective path is the intentionally unmarked CLI fixture
with no content mutation); malformed, missing, truncated, inconsistent-count, and unexpected-section
patches fail closed. The synchronized workspace, Stage-B content validators, ordinary-main no-match
classifier, and dry-run/live gates remain green. Only independent QA and the separately authorized
hosted rerun remain outside this local verification boundary.

## Phase 11: Dry-run-only historical carrier replay

### Layer boundary

- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Trunk/base: `origin/main`; parent branch: `origin/main`; branch:
  `fix/release-carrier-replay`; position: manual historical replay guard after the corrected
  hunk-only parser on current `main`. No Stack metadata.
- Scope is limited to one safe `workflow_dispatch` replay of hosted merge
  `fcc91b4850480945ae484c3ebdba18f8a4e38270` with `dry_run=true`. The source checkout remains the
  current selected `main` tree. No tag, label, release, upload, registry publication, attestation,
  credential, repository-variable, merge, push, commit, or parent-repository mutation is allowed.

- [x] 11.1 **RED** — Add runtime/static regressions for replay event SHA selection, exact PR
  correlation/validation, source-tree immutability, replay on push/live/malformed SHA rejection,
  absent replay current-main behavior, explicit normalized `EVENT_SHA`, and replay mutation guards.
- [x] 11.2 **GREEN** — Add the validated `carrier-event-sha` boundary and optional `replay_sha` input;
  keep checkout/current-tree validation on main, route all historical lookup/validation/tag-plan
  identities through `EVENT_SHA`, and stop replay before every mutation.
- [x] 11.3 **REFACTOR** — Emit credential-free source/replay/dry-run/mutation records and summaries;
  preserve ordinary push no-match, exact-one PR, strict content/private/version, live default,
  idempotency/conflict, permissions, concurrency, full-SHA, and canonical ownership contracts. Update
  design/spec/verification/QA handoffs with the dry-run-only limitation.
- [x] 11.3a **RED/GREEN/REFACTOR** — Repair the carrier mode boolean boundary so absent replay
  safely defaults to `replay=false` for normal push/manual dry-run/manual live paths, while replay
  records and summaries remain total and replay stays manual dry-run-only.
- [x] 11.3b **RED/GREEN/REFACTOR** — Replace the stale positive wrapper fixture with an explicit
  historical `0.1.0` to `0.2.0` Stage-A patch builder; verify the checked-out manifest/npm files are
  already at the target shape and reject no-op or wrong-version manifest replacements.
- [ ] 11.4 Run the separately authorized protected hosted replay and inspect its no-publication
  record. This apply slice does not run hosted workflows and does not claim hosted success.

## Phase 11 verification handoff — 2026-08-15

- [x] Re-ran the local Phase 11 resolver, carrier, exact Release Please, Cargo, npm, OCI, workflow,
  package, compile, and diff checks without hosted writes.
- [x] Behaviorally accept task 11.3: the exact `Resolve carrier mode` shell step now defaults an
  absent replay field to a validated boolean `false`, and the checked-in normal push/manual dry-run/
  manual live matrix proceeds with the existing mode/no-op behavior. Replay remains valid only for
  `workflow_dispatch` + `dry_run=true` + a lowercase 40-hex SHA.
- [ ] Task 11.4 remains pending: separately authorized hosted replay and no-publication record
  inspection are not performed under the no-write boundary.

## Phase 11 fresh verification after mode repair — 2026-08-15

- [x] Re-ran the checked-in normal push/manual dry-run/manual live mode matrix. Absent replay now
  resolves to `replay=false` and preserves the current event SHA and existing live/dry-run mode.
- [x] Re-ran valid replay and replay-negative cases. Replay remains limited to manual
  `workflow_dispatch` on `refs/heads/main` with `dry_run=true` and a lowercase 40-hex SHA; the
  current checkout SHA stays separate and the pure validator/tag-plan fixture preserves source bytes.
- [x] Re-ran Stage-B content/private/hunk-only/full-patch, synchronized-tree, Cargo, npm, OCI, workflow,
  package, compile, and whitespace checks; those local suites passed.
- [x] The earlier wrapper failure was superseded by task `11.3b`: the deterministic fixture now models
  `0.1.0 -> 0.2.0`, guards the checked-out target shape, and rejects no-op/wrong-version replacements.
  The exact Node `release-please@17.6.0` harness and the full wrapper/conformance gate now pass.
- [ ] Task 11.4 remains pending: separately authorized hosted replay and no-publication record
  inspection are not performed under the no-write boundary.

### Historical verification handoff (superseded)

The earlier technical verification was **FAIL** because the exact Release Please runtime wrapper had a
local no-op fixture defect. Task `11.3b` repaired that fixture; the final local verification handoff
below is authoritative. Independent `sdd-qa` and the hosted replay remain downstream and no hosted or
publication write was performed.

## Phase 11 final local verification handoff — 2026-08-15

- [x] Fresh verification passed the exact Node `release-please@17.6.0` fake-SCM harness with 32 effective
  paths, one root-carrier private manifest update containing exactly four dependency pins, six npm
  optional rewrites, one synchronized PR, and zero release/tag calls.
- [x] Fresh verification passed the deterministic Python wrapper fixture: historical `0.1.0 -> 0.2.0`
  patches, current-target manifest/npm shape guards, and fail-closed no-op/wrong-version mutations.
- [x] Fresh verification passed synchronized copied-tree `cargo test --workspace --locked`, current
  Cargo metadata/check/fmt/Clippy gates, all carrier/replay/patch/content/private/generated/version/
  no-match/dry-run/live suites, npm/OCI/package checks, workflow lint/security checks, and diff checks.
- [ ] Task `11.4` remains pending: the separately authorized protected hosted replay and its
  no-publication record inspection are not run under the no-write boundary.

### Final handoff

Technical verification is **PASS WITH WARNINGS**. No local implementation defect remains; the hosted
replay is the only remaining blocker for this Phase 11 slice. Hand off to `sdd-qa` for independent
acceptance. No hosted success, publication, or operator acceptance is claimed.

## Phase 12: Private conformance PR-files hunk-context correction

### Layer boundary

- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Trunk/base: `origin/main`; parent branch: `origin/main`; branch:
  `fix/release-carrier-private-patch-context`; position: focused Stage-B private hunk-context
  regression after the Phase 11 replay/fixture repair. No Stack metadata.
- Hosted run `31886141725` and the real PR `#59` files API response are the authoritative failure
  evidence for this slice. The run failed on a valid private hunk-only patch; no hosted replay success
  is claimed.
- Scope is limited to the exact carrier regression fixture, the private context allowlist, and honest
  OpenSpec handoff updates. No workflow, release, tag, publication, credential, variable, or hosted
  state mutation is permitted.

- [x] 12.1 **RED** — Add the exact PR `#59` API-shaped private hunk-only fixture with
  `@@ -10,10 +10,10 @@ publish = false`, four additions/deletions, eight changes, no
  `serde_json.workspace = true` context, and prove the current validator raises
  `private conformance diff patch is truncated`.
- [x] 12.2 **GREEN** — Remove only the over-specific `serde_json.workspace = true` context requirement;
  retain hunk declared/actual counts, API counts, exact four dependency replacements, synchronized
  version matching, private identity, and all other fail-closed checks.
- [x] 12.3 **REFACTOR/LOCAL VERIFY** — Run the focused carrier/provenance/static/mode/runtime suites
  and the complete relevant local Cargo, npm, OCI, workflow, package, compile, and diff checks without
  hosted writes.
- [x] 12.4 — Fresh `sdd-verify` passed against this corrected local boundary; hand off to independent
  `sdd-qa`. No operator or acceptance claim is made by verification.
- [ ] 12.5 — Obtain a separately authorized protected hosted replay/validation run and inspect its
  no-publication evidence. This task remains pending and is not executed here.

## Phase 12 apply handoff — 2026-08-15

The hosted failure is preserved as failure evidence, not converted into a success claim. The local
regression now models the exact GitHub PR-files response shape and the validator relaxes only the
missing trailing context requirement. Fresh `sdd-verify` subsequently passed; the protected hosted
replay and independent QA remain separate, unchecked work.

## Phase 12 verification handoff — 2026-08-15

- [x] Task `12.4` — Fresh `sdd-verify` passed on
  `fix/release-carrier-private-patch-context`. The exact PR `#59` API hunk-only fixture reproduces the
  pre-fix `private conformance diff patch is truncated` rejection and passes after the one-line context
  allowlist correction. Complete hunk/API counts, the exact four approved keys, old/new versions,
  private identity, truncation, and unapproved-mutation boundaries remain covered by passing runtime
  tests.
- [x] The complete relevant local Release Please `17.6.0`, carrier/provenance, Cargo, npm, OCI,
  workflow, shell, package, compile, CLI, and whitespace checks passed without hosted writes.
- [ ] Task `12.5` — Protected hosted replay/validation remains pending and must not be represented as
  successful. Independent `sdd-qa` is the next phase and owns acceptance evidence.

Technical verdict: **PASS WITH WARNINGS**. Hosted run `31886141725` remains the authoritative pre-fix
failure observation; no hosted replay success, publication, tag, release, or operator acceptance is
claimed.
