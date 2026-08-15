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
- [ ] Task `9.6` is not accepted: the synchronized effective-tree workspace test fails in the
  conformance golden because the root generic carrier does not update its embedded tool version,
  and Stage-B accepts a mutated approved generated file (`tests/golden/valid-methods.json`) by path
  alone.
- [ ] Task `9.7` remains pending and prohibited until the local defects are corrected and a protected
  hosted rerun is separately authorized.

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
- [ ] 9.11 — Fresh `sdd-verify` is complete locally; run independent `sdd-qa`. The protected hosted
  rerun remains separately authorized work and is not performed here.
