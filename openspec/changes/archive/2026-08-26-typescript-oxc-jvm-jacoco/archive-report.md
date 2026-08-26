# Archive Report

## Identity

- Change: `typescript-oxc-jvm-jacoco`
- Mode: `openspec`
- Archive date: `2026-08-26`
- Branch/HEAD: `fix/carrier-gh-token-guard` / `a1967ab`

## Acceptance gate

- Required artifacts were present before archive: `proposal.md`, `spec.md`, `design.md`,
  `tasks.md`, `verify-report.md`, `qa-report.md`, `state.yaml`, and `openspec/config.yaml`.
- Technical verification verdict: **PASS WITH WARNINGS**.
- Acceptance QA verdict: **PASS WITH WARNINGS**.
- No unresolved `CRITICAL`, `P0`, or `P1` finding was reported.
- `HOST-CURRENT` remains **NOT TESTED** because no safe hosted target was available for the
  unmerged current graph. This is an explicit archive exception authorized by the user in the
  archive request. The exception does not convert hosted acceptance into `PASS`; the original QA
  verdict and hosted evidence ledger remain preserved in `qa-report.md`.
- The historical hosted failure and the unavailable runner/coverage/publication paths remain
  visible as warnings in the preserved verification and QA reports. No registry, release, tag,
  upload, or publication action was performed.

## Specs synced

The change used the repository's legacy root delta layout (`spec.md`) rather than a nested
`specs/{domain}/spec.md` directory. Because `openspec/specs/` had no main spec, the complete delta
was installed as the source-of-truth spec:

- `openspec/specs/typescript-oxc-jvm-jacoco/spec.md` — **Created**; 9 requirements, 9 scenarios.
- Requirements modified: 0.
- Requirements removed: 0.

No destructive merge was required.

## Archive verification

- Main spec created and retained at `openspec/specs/typescript-oxc-jvm-jacoco/spec.md`.
- State advanced to `current_phase: archive`, appended `archive` to `completed`, and set
  `next: none`.
- The complete change folder, including the original QA evidence and this report, was moved to:
  `openspec/changes/archive/2026-08-26-typescript-oxc-jvm-jacoco/`.
- Product code and workflows were not changed.
