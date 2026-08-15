# Tasks: Authorized R-F6 — two-stage release carrier

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 650–1,000 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | F6.1 → F6.2 → F6.3 → F6.4 → F6.5 |
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

## Phase 6: Private Stage-A candidate boundary remediation

- [x] 6.1 **RED** — Extend the exact v17.6.0 fake-SCM harness to fail when the Stage-A update set contains `crates/codegauge-conformance/Cargo.toml`, and add the private-candidate Stage-B mutation rejection.
- [x] 6.2 **GREEN** — Remove the unsupported `cargo-workspace` discovery plugin from Stage A; exact v17.6.0 source evidence is `build/src/plugins/cargo-workspace.js:45-84,138-193` and `build/src/plugins/workspace.d.ts:11-16`, which provide no member exclusion. Retain the five explicit runtime Cargo candidates and use the non-Cargo Java root carrier for the approved runtime lock/dependency TOML selectors without changing Cargo workspace membership.
- [x] 6.3 **REFACTOR** — Assert the five runtime Cargo versions, private lock preservation, six npm optional rewrites, one synchronized PR, and zero release/tag calls in the exact harness; document the v17.6.0 source boundary in the design/spec.
- [x] 6.4 Re-run `sdd-verify`; hosted Stage-A/tagged no-publication rehearsal and downstream QA remain governed by tasks `4.2` and `4.3` and are not performed in this apply slice.

## Phase 7: Temporary hosted carrier rehearsal guard

- [x] 7.1 **RED/GREEN/REFACTOR** — Add static and runtime regressions for trusted manual `workflow_dispatch` on `main`, explicit `dry_run` normalization, repository-variable push rehearsal, live default behavior, and fail-closed invalid mode values.
- [x] 7.2 **GREEN** — Refactor `release-tag-carrier.yml` to share collection/validation, emit `carrier-record.json` and `carrier-plan.json`, and conditionally skip tag-ref/label mutations and all downstream release/publish paths in dry-run mode while retaining live push behavior.
- [x] 7.3 **REFACTOR** — Document `RELEASE_CARRIER_DRY_RUN`, the manual `dry_run=true` command, plan evidence, and variable cleanup; update the OpenSpec design/spec and QA handoff without claiming hosted execution.
- [ ] 7.4 Run the protected hosted rehearsal for both the variable-controlled merge and manual `dry_run: true`; inspect the plan record and prove no hosted write. This remains pending and is not executed by apply.

## Verification handoff — 2026-08-15

The `sdd-verify` executor reran the local carrier, provenance, distribution, bootstrap, README,
Release Please runtime, compile, Cargo, npm, OCI, package, workflow-lint, ShellCheck, Dockerfile,
and diff checks successfully. The exact carrier mode and plan steps were also exercised with a
read-only fake GitHub CLI; this is local evidence only. Tasks `4.2`, `4.3`, and `7.4` remain
intentionally unchecked because the protected hosted rehearsal and independent acceptance QA were
not performed under the no-write boundary.
