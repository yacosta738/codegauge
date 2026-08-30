# Archive Report

## Identity

- Change: `release-recovery-idempotent-ownership`
- Mode: `openspec`
- Archive date: `2026-08-30`
- Archived to: `openspec/changes/archive/2026-08-30-release-recovery-idempotent-ownership/`
- Branch / HEAD at archive time: dirty-`main` continuation, HEAD `5b2fbde6bb6205c0140a3a5d315e8b2e02ce3632`
- Historical merged SHA for the recovery target (`v0.3.0`): `cf46ba64bd2e723c28406ca6b7fc3c97d183f1d0`
  ("chore: release main (#75)" on `yacosta738/codegauge@main`)

## Acceptance gate

- Required artifacts were present before archive: `proposal.md`, `specs/release-recovery/spec.md`,
  `design.md`, `tasks.md`, `apply-progress.md`, `verify-report.md`, `qa-report.md`, and
  `state.yaml`.
- Technical verification verdict: **PASS WITH WARNINGS** (see
  `openspec/changes/archive/2026-08-30-release-recovery-idempotent-ownership/verify-report.md`).
- Acceptance QA verdict: **PASS WITH WARNINGS** (see
  `openspec/changes/archive/2026-08-30-release-recovery-idempotent-ownership/qa-report.md`).
- No unresolved `CRITICAL`, `P0`, or `P1` finding was reported by either report.
- All 10 acceptance capabilities in the QA scenario matrix produced observable executable
  evidence (98-test Python suite, Release Please 17.6.0 runtime harness, locked Cargo
  test/fmt/clippy/check gates, `actionlint`, `python3 -m compileall`, `git diff --check`).
- The 7 open QA findings are all `P3` warnings (offline default dry-run, hosted
  protected-environment reviewers, unexercised hosted GitHub/registry/OCI/attestation
  behavior, unavailable quality runner / strict TDD verifier / coverage, broad dry-run caller
  permissions, dirty worktree, applied payload above the 400-line review budget). They are
  tracked in the preserved QA report and do not block archive.
- Four previously `CRITICAL` verify blockers (`codegauge-root-v0.3.0` root tag,
  `${RELEASE_REF#v}` strip, `mutation-unknown` audit semantics for ambiguous `create_release`,
  publication-failure-inventory per-target fields) were reworked and are now `RESOLVED` with
  passing executable tests.

## Historical identity contract

The new capability was introduced to recover `v0.3.0` in `yacosta738/codegauge`, which
remained untagged because the global and root Release Please configuration had suppressed
GitHub Release creation. The authoritative historical identity for that recovery is:

| Field | Value |
|---|---|
| Repository | `yacosta738/codegauge` |
| Protected branch | `main` |
| Pull request | `75` |
| Merged SHA | `cf46ba64bd2e723c28406ca6b7fc3c97d183f1d0` ("chore: release main (#75)") |
| Historical tree | `f9fca04cb359e843bd13ab7ff4db0ff1a9ba4a1c` |
| Historical `.release-please-manifest.json` entries | **13** (no `crates/codegauge-provider-typescript`) |
| Current `.release-please-manifest.json` entries | **14** (delta is the addition of `crates/codegauge-provider-typescript`) |

The local Git history confirms `cf46ba64b…` is an ancestor of `HEAD` and that the historical
tree object resolves. The durable main spec at `openspec/specs/release-recovery/spec.md`
records this context in a `Historical context` preamble so future readers understand why the
capability exists.

## Specs synced

The delta used the project's nested OpenSpec layout
(`specs/release-recovery/spec.md`). `openspec/specs/` had no main spec for the
`release-recovery` domain, and the proposal explicitly states:

> Modified Capabilities: None; `openspec/specs/` has no existing release capability. The new
> capability defines the complete contract.

Because there was no existing main spec, no ADDED/MODIFIED/REMOVED conflict resolution was
required. The complete delta was installed as the source-of-truth spec with a small
`Historical context` preamble that records the historical identity contract. No destructive
merge was performed.

| Domain | Action | Details |
|---|---|---|
| `release-recovery` | **Created** | 5 requirements, 9 scenarios. Requirements modified: 0. Requirements removed: 0. Prepended a `Historical context` section recording the historical identity contract. |

Installed source-of-truth spec:

- `openspec/specs/release-recovery/spec.md` — **Created**.

Preserved delta spec (audit trail):

- `openspec/changes/archive/2026-08-30-release-recovery-idempotent-ownership/specs/release-recovery/spec.md`

## Archive verification

- Main spec created and retained at `openspec/specs/release-recovery/spec.md`.
- Original change folder, including the proposal, delta spec, design, tasks, apply progress,
  verify report, QA report, and this archive report, was moved to:
  `openspec/changes/archive/2026-08-30-release-recovery-idempotent-ownership/`.
- `state.yaml` advanced to `current_phase: archive`, appended `archive` to `completed`,
  preserved `qa_verdict: PASS WITH WARNINGS`, added `archived: 2026-08-30`, and set
  `next: done`.
- The active changes directory no longer contains `release-recovery-idempotent-ownership`;
  the existing `typescript-oxc-jvm-jacoco` change had already been archived on `2026-08-26`.

## Live-recovery gate (NOT authorized by archive)

This archive does **not** authorize live recovery. The capability is durable; live execution
of the recovery workflow against `yacosta738/codegauge@main` remains an operator action that
requires every one of the following, all of which are explicitly out of scope for the SDD
pipeline:

1. `vars.RELEASE_RECOVERY_LIVE_ENABLED=true` set as a repository variable on
   `yacosta738/codegauge` (default is `false`).
2. Approval from the protected `release-recovery-live` GitHub Environment
   (`environment: name: release-recovery-live` in `.github/workflows/release-recovery.yml`).
   The required-reviewer roster is hosted configuration and cannot be verified from YAML alone.
3. An explicit operator invocation of the `release-recovery` workflow with the
   `confirm_live` input set to the exact marker `RECOVER_RELEASE_LIVE`, plus a `GH_TOKEN`
   with `contents: write` scoped to the protected environment.

The repository variable check is in `.github/workflows/release-recovery.yml`; the live
execution guard is in `scripts/recover_release.py` (lines 672-684 and the `--execute-live`
gate). The QA and verify reports both explicitly state that live recovery is operator-only
and was not performed during this SDD cycle.

## Mutability and tree state

- No remote mutations were performed: no commits, pushes, tags, releases, package
  publications, OCI pushes, attestations, registry writes, or environment changes.
- The dirty-`main` worktree was preserved exactly as it was at archive entry. The applied
  Units 1-5 and Phase 5 rework remain in the working tree (9 modified + 9 untracked files)
  for the operator to commit when they decide to. The archive did not stage, commit, or
  reset any of those files.
- The only filesystem mutations performed by `sdd-archive` are:
  1. Created `openspec/specs/release-recovery/spec.md` from the delta plus a small
     historical-context preamble.
  2. Created `openspec/changes/archive/2026-08-30-release-recovery-idempotent-ownership/`
     and copied the change artifacts there.
  3. Wrote `openspec/changes/archive/2026-08-30-release-recovery-idempotent-ownership/archive-report.md`
     (this file).
  4. Wrote the final `openspec/changes/archive/2026-08-30-release-recovery-idempotent-ownership/state.yaml`.
  5. Removed the now-empty `openspec/changes/release-recovery-idempotent-ownership/`
     directory and its `specs/` subtree.
