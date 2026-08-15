# Design: Hosted conformance dependency-pin exception for R-F6

## Technical Approach

Keep the authorized two-stage Release Please 17.6.0 architecture: Stage A creates one
component-tagged synchronization PR with `skip-github-release: true`; Stage B owns the single
canonical `vX.Y.Z` tag after merged-main validation. The hosted PR `#59` proved that the previous
private-member exclusion was too broad: the five public runtime Cargo packages and npm packages
reached `0.2.0` with zero release/tag calls, but `cargo metadata --locked` failed because the
private conformance manifest still pinned all four path dependencies to `^0.1.0`.

The minimal exception keeps `codegauge-conformance` outside Release Please's candidate, linked,
release, and tag graphs. The surviving Java `codegauge-root` metadata carrier additionally owns
four typed TOML updates in that existing private manifest. Those updates change only dependency
`.version` fields to the synchronized runtime version. The private package's own
`[package].version = "0.1.0"`, `publish = false`, lock entry, and absence of changelog/release
metadata remain unchanged.

Stage B must validate file content, not only filenames. It may accept the private manifest path only
when either a complete single-file unified diff or a GitHub PR-files API hunk-only patch (whose
validated entry supplies the filename) proves exactly those four replacements; missing, truncated,
malformed, or multi-file patch data fails closed.

## Manual historical replay guard

The carrier has a deliberately narrow recovery/rehearsal path for an already merged `main` event.
`workflow_dispatch` exposes optional `replay_sha`, but the value is valid only when the required
`dry_run` input is `true`. Push events and live dispatches reject any non-empty replay value before
GitHub PR-file collection. A missing replay value keeps ordinary dispatch behavior: the effective
event SHA is the current `GITHUB_SHA` for the selected `refs/heads/main` source checkout.

Replay never checks out the historical commit. `actions/checkout` remains bound to the current
selected main revision, and the workflow records that source checkout SHA separately. A small
read-only resolver emits one normalized `EVENT_SHA`: the validated replay SHA in replay mode, or
the current event SHA otherwise. Only that output is used for commit/PR lookup, carrier
`--event-sha`, and canonical tag-plan identity. This prevents a later command from silently
falling back to `GITHUB_SHA` while keeping current-main code (including the corrected hunk-only
parser) in the validation tree.

Replay proceeds through the same exact PR correlation, tree, version, provenance, private-pin, and
tag-plan validation as a normal carrier event. It stops before tag-ref creation, Release Please
label updates, tag-workflow dispatch, release-asset uploads, registry publication, or attestation.
The record and workflow summary identify `replay`, `source_checkout_sha`, `replay_event_sha`,
`dry_run`, and each mutation as `skipped`, `not-started`, or `not-dispatched`; they contain no
credential values. The schema is total: every resolver/record/summary path emits the boolean
`replay`, with absent replay defaulting to `false`; replay mode emits both the current source
checkout SHA and the historical replay event SHA, while ordinary mode records a null/none replay
event SHA. Boolean extraction uses a jq default and type check so a valid `false` value cannot abort
a shell step. This is a dry-run-only hosted recovery rehearsal, not production replay and not evidence
that the hosted run passed.

```text
workflow_dispatch(main, dry_run=true, replay_sha=fcc91b4...)
  -> checkout current selected main revision (corrected parser)
  -> resolve EVENT_SHA=fcc91b4... and record source checkout SHA separately
  -> GET commit/EVENT_SHA/pulls -> exactly one Release Please PR
  -> GET that PR's files -> exact Stage-B tree/content/private validation
  -> read-only canonical vX.Y.Z plan at EVENT_SHA
  -> carrier-plan.json + summary: every mutation skipped/not-started
  -> stop (no tag, label, release, upload, publish, or attestation)
```

The root carrier's other version-bearing files use the updater that matches their content. The
conformance golden is a typed JSON updater at `$.tool.version`; README and model contract fixtures
remain generic updaters, but only their intended release-version lines carry the exact
`x-release-please-version` marker supported by Release Please 17.6.0. The CLI integration fixture
has no release-version marker and therefore must not receive a content mutation. Stage B validates
complete patch metadata for every approved root/candidate/generated carrier file: typed JSON, TOML,
npm JSON, and annotated lines permit only the configured version substitutions; the twelve generated
changelogs require a complete Release Please-shaped addition; and the private manifest keeps its
separate four-pin exception. Filename-only acceptance is not permitted.

## Architecture Decisions

| Decision | Choice | Rejected | Rationale |
|---|---|---|---|
| Private ownership | Root Java carrier owns the four private dependency selectors | Reintroduce `cargo-workspace` or make conformance a candidate | v17.6.0 discovers every workspace member; the carrier is the smallest owner that fixes the real Cargo graph without publishing private code. |
| Private diff boundary | Allow one private manifest path only for four exact `.version` replacements | Filename-only allowlist or broad private-manifest acceptance | PR #59 showed that path exclusion lets a merged public version graph fail locked metadata; content restriction prevents package/changelog/other-path drift. |
| Private identity | Keep package version `0.1.0`, `publish = false`, and no linked component | Synchronize the private package version or add a release candidate | The conformance crate is a build/test consumer, not a distribution artifact; only its runtime dependency requirements must follow public packages. |
| Stage-B ownership | Preserve one unprefixed canonical tag and zero Stage-A release/tag calls | Let the private update create a release/tag | The exception repairs dependency resolution only and cannot weaken the existing fail-closed release boundary. |
| Root content ownership | Match each file to its Release Please 17.6.0 typed or exact marker updater | Broad generic replacement or filename-only acceptance | The golden JSON needs `$.tool.version`; marker lines make README/contracts deterministic; patch validation rejects drift and arbitrary generated content. |
| Historical replay identity | Keep current-main source checkout; substitute only a validated read-only `EVENT_SHA` | Checkout the old merge or reuse `GITHUB_SHA` in one command | The corrected parser must validate the old event's PR against current-main code without allowing a tag/label/release/publication mutation. |

## Data Flow

```text
Release Please 17.6.0
  -> root carrier: public graph + exact private dependency pins
  -> one PR (#59 shape), zero release/tag calls
  -> merged main: cargo metadata --locked
  -> Stage-B filename/content diff gate
  -> trusted carrier validates graph -> one vX.Y.Z tag -> downstream release flow
```

## File Changes

| File | Action | Description |
|---|---|---|
| `release-please-config.json` | Modified | Add four root-carrier TOML entries and use the typed golden JSON updater without adding a private package candidate. |
| `scripts/verify_release_provenance.py` | Modified | Validate exact typed/annotated/root/candidate/generated patches, the four private pins, private identity checks, and separated source/event replay SHA. |
| `.github/workflows/release-tag-carrier.yml` | Modified | Preserve complete PR file patches/content, normalize `EVENT_SHA`, and add a dry-run-only historical replay guard; fail closed if unavailable or live. |
| `tests/release_please_runtime_harness.mjs` | Modified | Prove the typed golden updater, exact marker substitutions, 32 effective paths, and zero Stage-A writes. |
| `tests/release_please_runtime_tests.py`, `tests/release_carrier_tests.py`, `tests/release_carrier_static_tests.py`, `tests/release_provenance_tests.py`, `tests/distribution_checks_e3a.py` | Modified | Cover synchronized-tree tests, positive/negative content-aware carrier boundaries, replay SHA selection, and mutation-free workflow wiring. |
| `openspec/changes/codegauge-distribution/**` | Modify now | Record the hosted failure, corrected contract, pending tasks, and blocked state. |

No application/workflow implementation or release, tag, or registry state changes in this update.

## Interfaces / Contracts

The root carrier must add these exact TOML JSONPaths for
`/crates/codegauge-conformance/Cargo.toml`:

```text
$.dependencies["codegauge-application"].version
$.dependencies["codegauge-core"].version
$.dependencies["codegauge-model"].version
$.dependencies["codegauge-provider-jacoco"].version
```

Stage-B input must retain each PR file's `filename`, status/count metadata, and either a complete
single-file unified diff or a GitHub PR-files API hunk-only patch (or verified before/after contents).
Both patch forms must contain at least one complete hunk, match every declared hunk and
additions/deletions/changes count, and contain no unexpected file section. Typed JSON/TOML/npm files
and annotated generic root files must prove exactly the configured version replacements. The twelve
generated changelog paths are accepted only as complete Release Please changelog additions. For the
private path, the changed-key set must equal those four paths, every new value must equal the
synchronized public version, and package version/publish/name plus all other bytes must be unchanged.
Changelog, package-version, dependency, formatting, arbitrary-content, annotation, truncated-patch,
malformed-patch, or unapproved-path mutation is rejected.

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Runtime harness | Exact v17.6.0 root-carrier behavior | Assert one PR, 32 effective paths including the private manifest, four pins at `0.2.0`, private package/lock at `0.1.0`, six npm rewrites, and zero release/tag calls. |
| Carrier unit | Diff exception | Accept the exact four replacements; reject private package version, changelog, formatting/other-key, truncated-patch, and unrelated-path mutations. |
| Carrier replay unit | Historical event identity and no mutation | Select `fcc91b4850480945ae484c3ebdba18f8a4e38270` only for manual `dry_run=true`, correlate/validate the matching PR, reject push/live/malformed inputs, and preserve source-tree bytes. |
| Integration | Locked graph | Run `cargo metadata --locked` on the synchronized fixture and preserve non-publishable conformance membership. |
| Integration | Synchronized workspace behavior | Apply the complete effective Stage-A updates to a copied tree and run `cargo test --workspace --locked`; the golden tool version must equal the synchronized runtime version. |
| Acceptance | Hosted boundary | Rehearse a protected Stage-A merge and confirm the corrected PR passes metadata without creating a Stage-A release/tag; do not claim this until actually observed. |

## Migration / Rollout

No migration. Apply after RED coverage; rerun local verification before any protected hosted
rehearsal. The replay input is temporary recovery plumbing and must not be used to create a tag or
release; remove it after the authorized no-publication rehearsal if the operator still wants the
normal live carrier only.

## Open Questions

- [ ] None blocking the design; the protected hosted replay remains an explicit acceptance gate, not
  evidence available in this phase.
