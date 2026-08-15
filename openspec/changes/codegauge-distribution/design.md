# Design: Authorized R-F6 — two-stage release carrier

## Technical Approach

Option 1 is approved: Release Please 17.6.0 generates a synchronized version PR; a
post-merge carrier owns the `vX.Y.Z` tag. Stage 1 enables components so linked-versions forms
the runtime map and node-workspace rewrites npm pins, but creates no tag/release. Stage 2 validates
the merge, creates the tag, and starts the build/publish graph.

Stage 1 uses the explicit runtime package list already present in the manifest. It does not use the
v17.6.0 `cargo-workspace` plugin because that plugin discovers every member declared in the root
`Cargo.toml`, including the private conformance member. The non-Cargo Java root carrier owns the
runtime Cargo lock entries and internal runtime dependency version pins that the direct Rust
candidates cannot discover without that plugin; Cargo workspace membership remains unchanged for
builds and tests.

Source evidence: v17.6.0 empty components are skipped by linked-versions; true components link. Node
workspace rewrites optional dependencies. The action skips `Manifest.createReleases()` on
`skipGitHubRelease`; `BaseStrategy` skips the release candidate, while `GitHubApi.createRelease` may
create a ref/release. Stage 1 relies on the action boundary, not tag coupling: a PR plus zero
tags/releases. If suppression is removed, the would-be CLI artifact is `codegauge-cli-vX.Y.Z`; it fails.

## Architecture Decisions

| Decision | Choice | Rejected | Rationale |
|---|---|---|---|
| R-F6 | Two stages (approved option 1) | Upgrade/plugin | Matches 17.6.0 and isolates the tag invariant. |
| Private Cargo member | Explicit five-crate runtime list plus Java-carrier TOML updates | `cargo-workspace` member discovery | v17.6.0 has no Cargo workspace exclusion; keeping the plugin would propose the private conformance manifest. |
| Stage 1 | Global/action `skip-github-release: true`; `include-component-in-tag: true`; remove CLI `false` override | Component-tagged releases | Action skip bypasses release creation; package skips add defense in depth. |
| Carrier auth | Existing repository-scoped, fine-grained `RELEASE_PLEASE_TOKEN` (`contents:write`) creates tag | `GITHUB_TOKEN` tag push; new App now | Reuses authorization and triggers the tag workflow; its broader Stage-1 scope is a risk. |
| Release owner | Carrier creates only the tag; release workflow creates/verifies GitHub Release after gates | Release Please release in Stage 1 | The PR pass has no release URL and cannot create duplicates. |
| Hosted rehearsal | Manual `dry_run: true` or temporary `RELEASE_CARRIER_DRY_RUN=true` selects read-only carrier planning; unset/`false` is live | Permanent dry-run default or artifact/publisher writes | Rehearsal is explicit and reversible while the production push path remains live by default. |

## Data Flow

```text
main push -> version PR (linked map, no tag) -> merge -> carrier -> vX.Y.Z
          -> tag caller -> release-build -> gated release -> Cargo/npm/OCI
```

## Stage Contracts

Stage 1 keeps a PR, the Java `codegauge-root` carrier, the five runtime Cargo candidates, explicit
root-anchored Cargo lock/dependency carriers, and the package-relative npm path. The virtual Cargo
root has no identity; `codegauge-conformance` stays out of Release Please and `publish = false`.
Linked components share one version. No component artifact is acceptable.

### Private-candidate boundary evidence

The exact v17.6.0 `build/src/plugins/cargo-workspace.js` implementation (lines 45–84) reads the
root `workspace.members`, resolves every member with `findFilesByGlobAndRef`, appends the virtual
root, and parses each member manifest. Its `CargoWorkspace` and `WorkspacePluginOptions` interfaces
(`cargo-workspace.d.ts`, lines 41–56 and `workspace.d.ts`, lines 11–16) expose no member exclusion
or allowlist. The plugin's candidate creation path (`cargo-workspace.js`, lines 138–193) creates a
new Cargo candidate for any discovered package whose version is forced by the dependency graph.
`publish = false` is not consulted by this discovery path.

The supported boundary is therefore to omit `cargo-workspace` from Stage A and configure the five
approved runtime Cargo paths explicitly. Each direct Rust strategy updates its own package manifest;
the Java root carrier uses v17.6.0's typed TOML extra-file updater to update the five runtime
`Cargo.lock` package entries and only the internal dependency version fields in the four dependent
runtime manifests. The selectors exclude `codegauge-conformance`, while Cargo's real workspace
membership is preserved.

The exact read-only fake-SCM harness now asserts that the effective update proposals contain no
`crates/codegauge-conformance/Cargo.toml`, that all five runtime Cargo manifests and the lock entries
reach `0.2.0`, that the private lock entry remains `0.1.0`, and that a Stage-B mutation containing
the private manifest is rejected. It still records one synchronized PR, six npm optional pin
rewrites, and zero release/tag calls.

Stage 2 is a trusted `push` to `main` plus an explicit `workflow_dispatch` rehearsal entry point,
with concurrency `release-carrier-main`, no cancellation, full-SHA actions, and read permissions plus
scoped tag secret. It must identify exactly one merged Release
Please PR (base `main`, merge SHA = event SHA, label/body/diff), then reject dirty/unexpected state, missing
root/lockfile/target metadata, virtual-root publication, private linkage, version/provenance/metadata
drift, malformed semver, an existing release, or prefixed artifacts. It recomputes `v${workspace_version}`.
Compare-and-create is idempotent: absent tag creates one lightweight ref at the SHA; same-SHA is
a no-op; different-SHA fails closed and never starts release.

The carrier first classifies the read-only `/commits/{sha}/pulls` response with the shared provenance
helper. It validates the response shape, filters Release Please candidates by exact
`merge_commit_sha == GITHUB_SHA`, and fetches the version-PR file list only for exactly one match. A
trusted ordinary `main` push with zero matches is a successful no-op: it writes a credential-free
`carrier-record.json` with `status=skipped`, reason `no-matching-release-please-pr`, and explicit
`not-run`/`not-started` mutation statuses, then exits before tree/version/diff/tag/label validation.
Multiple matches or malformed PR data fail closed before the diff fetch. Every later validation, plan,
tag-ref, and label step requires the collection step's `matched` output, so the no-match path cannot
reach a mutation even when live mode is the normalized default.

### Temporary hosted rehearsal mode

The carrier accepts the trusted `push` and `workflow_dispatch` events only when the checked-out ref is
`refs/heads/main`. A manual dispatch exposes a required boolean `dry_run` input. An automatic push
normalizes the explicit repository Actions variable `RELEASE_CARRIER_DRY_RUN`; the exact values
`true`, `false`, and unset are accepted, with unset/`false` preserving the live production default.
The manual input takes precedence for a manual run, and unknown values fail closed.

Collection and validation are shared by both modes. The carrier then performs a read-only compare and
canonical tag plan, writing `carrier-record.json` and `carrier-plan.json` and rendering the sanitized
plan in the workflow summary. In dry-run mode the tag-ref POST, Release Please label PUT, tag-triggered
workflow, asset upload, and every registry publisher are skipped by job-step conditions; the plan
records each skipped mutation explicitly. Live push mode retains the existing compare/create race
handling and label handoff. The plan is emitted as a summary/JSON record rather than uploaded as a
release or registry asset.

The carrier uses `RELEASE_PLEASE_TOKEN`, never a `GITHUB_TOKEN` fallback, for both read-only planning
and live ref/label writes. GitHub says `GITHUB_TOKEN`-created pushes do not start workflows; tokenized
tag creation is intentional. The downstream `v*.*.*` caller's explicit `workflow_dispatch` with
`GITHUB_TOKEN` is recovery-only (dispatch is an exception). It passes tag/SHA to `release.yml`;
preflight checks tag identity and main ancestry, not equality with later `origin/main`. After
build/checksum/metadata gates, publish creates or verifies the tag release; conflicts fail.

## File Changes

| File | Action | Purpose |
|---|---|---|
| `release-please-config.json` | Modify | Stage-1 tags/skips; preserve root/npm paths and linked graph. |
| `.github/workflows/release-please.yml` | Modify | Version-PR-only action; explicit skip; remove release job. |
| `.github/workflows/release-tag-carrier.yml` | Create | PR/provenance validation, normalized manual/variable dry-run planning, conditional tag/label mutation, concurrency/retry. |
| `.github/workflows/release-on-tag.yml` | Create | `v*.*.*` trigger calling reusable release workflow. |
| `.github/workflows/release.yml`, `release-build.yml`, `release-publish.yml` | Modify | Carrier inputs and post-gate release creation. |
| `scripts/verify_release_provenance.py`, `tests/release_provenance_tests.py`, `tests/distribution_checks.py`, `tests/release_carrier_static_tests.py`, `tests/release_carrier_tests.py` | Modify | Linking, carrier negatives/idempotency, trusted event modes, dry-run mutation gates, and workflow gates. |
| `tests/release_please_runtime_harness.mjs`, `tests/release_please_runtime_tests.py` | Modify | Exact v17.6.0 private-candidate exclusion, runtime Cargo carriers, and Stage-B mutation regression. |
| `README.md` | Modify | Document the temporary variable, manual dry-run command, plan evidence, and live-default cleanup. |

## Interfaces / Contracts

Carrier record: `{version, tag: "vX.Y.Z", merge_sha, version_pr_number}`; every SHA is lowercase
40-hex. The rehearsal plan wraps that record with the trusted event identity, normalized mode,
`tag_plan`, existing-ref/release observations, and explicit `mutations` statuses. Inputs are
`release_tag`, `release_sha`, `main_sha`; `release_url` is empty until creation. No credential enters
records, summaries, or artifacts.

## Testing Strategy and Acceptance

- **Local:** exact 17.6.0 fixture; require a 13-entry map, five runtime Cargo manifests, private
  lock/package boundaries, six rewritten pins, exact paths, private-candidate rejection, one PR, and
  zero mocked release/tag calls. Test the action skip and prefixed-tag paths.
- **Carrier:** reject wrong PR/SHA/version/lockfile/metadata, dirty/unexpected state, missing targets,
  prefixed/conflicting tags, and release conflicts; same-SHA retry is a no-op. Run actionlint,
  full-SHA audits, and locked Cargo/Python/npm checks.
- **Hosted dry-run:** the protected rehearsal must exercise both the variable-controlled push and
  manual `dry_run: true` carrier paths, show one PR diff and no tag/label/release/upload/publish writes,
  and retain the carrier plan summary/JSON record. The hosted rehearsal remains pending in this apply
  slice; no hosted evidence is claimed.

Acceptance is exactly one `vX.Y.Z` ref at the version-PR merge SHA, no Stage-1 component tag/release,
one tag-triggered build, and fail-closed conflict/recovery behavior. No implementation or verification
success is claimed.

## Migration / Rollback

Replace the blocked global `include-component-in-tag: false` setup atomically with Stage 1 and both
carrier workflows; no existing `v0.1.0` tag/release exists. Rollback disables triggers and reverts
config. Never move/delete a tag: retry its SHA after repair; bad content needs a corrected patch.

## Open Questions / Risks Before Merge

- [ ] Confirm `RELEASE_PLEASE_TOKEN` is fine-grained, masked, repository-scoped, and ref-authorized;
  otherwise provision a contents-write-only App token.
- [ ] Confirm branch protection, tag delivery, action bundling, and recovery in hosted dry-run.
