# Design: CodeGauge distribution release ownership correction

## Technical Approach

Keep Release Please 17.6.0 inside the `codegauge` repository as the only version-PR, canonical-tag, and GitHub-Release owner. Its manifest continues to model the five public runtime Cargo packages plus npm packages, while the root metadata carrier handles repository-owned files and exactly four private conformance dependency pins. Release Please's successful merged-main operation creates the canonical unprefixed `vX.Y.Z` tag and its GitHub Release.

The custom `release-tag-carrier` becomes a **validator/correlator**, not a tag publisher. It finds the merged Release Please PR, validates the source tree, exact PR patch, version graph, tag/release identity, and release assets, then dispatches the downstream build/publication workflow using the already-existing Release Please tag and release. It MUST NOT call the Git refs API, create a tag, create a GitHub Release, or mutate Release Please labels. The current `Compare and create one immutable lightweight tag` step is therefore removed/replaced by an existing-release correlation step.

The validator correction remains narrow: accept the real Release Please PR #75 shape, including modified existing `CHANGELOG.md` files and the complete manifest/version updates produced by Release Please. Acceptance is content-based and allowlisted; filename-only or broad changelog acceptance is rejected. No engine, schema, fixture, JSON, error, or exit semantics change.

## Architecture Decisions

| Decision | Choice | Alternatives rejected | Rationale |
|---|---|---|---|
| Release owner | Release Please owns `vX.Y.Z` tag and GitHub Release in this repository. | Carrier-created tag/release; a separate release service; GitHub-generated tag only. | One authoritative release state avoids split-brain ownership and ensures the release notes/tag are produced by the versioning tool that generated the PR. |
| Carrier responsibility | Validate/correlate only, then dispatch downstream publication against the existing release. | Keep carrier tag creation; make carrier own the GitHub Release. | Removing tag writes eliminates the current ownership conflict and prevents a successful carrier from creating a release that Release Please never created. |
| Release identity | Require an existing Release Please release whose tag is exact `vX.Y.Z`, resolves to the validated merged SHA, and belongs to this repository. | Trust input tag/URL; infer from the latest release; accept any tag pointing at the SHA. | Exact tag, release ID/tag, SHA, version, and repository checks prevent cross-release or stale-release publication. |
| Stage-A provenance | Accept changed existing changelogs only when the PR's complete diff proves the expected Release Please files/version changes and no unapproved file/content changes. | Treat changelogs as newly added only; accept all changelog edits. | Release Please commonly updates existing changelogs; content allowlisting keeps the validator secure without rejecting legitimate output. |
| Scope | All workflows, permissions, and API calls target `${GITHUB_REPOSITORY}` for `yacosta738/codegauge`; no parent-repository dispatch or release path exists. | Reusable parent workflow; cross-repository release orchestration. | This is a sub-repository release, so ownership must remain local and auditable. |
| Conformance exception | Permit `crates/codegauge-conformance/Cargo.toml` only for four exact dependency `.version` replacements. Keep package version `0.1.0`, `publish = false`, and no release metadata. | Synchronize the private package; allow the whole file. | Repairs locked graph resolution without publishing conformance or permitting unrelated drift. |
| Patch validation | Support complete unified diffs and filename-bound GitHub hunk-only patches; preserve counts, exact replacements, identity checks, and malformed/truncated/multi-file rejection. | Filename-only acceptance; broad context matching. | GitHub legitimately omits context while the file path, hunk counts, and exact line mutations remain verifiable. |
| npm formatting | Validate seven approved version pairs separately from the base package's deterministic `files` formatting rewrite. | Count all formatting lines as version edits; permit platform formatting changes. | Matches Release Please output while keeping platform packages and unrelated edits fail-closed. |

## Data Flow

```text
Release Please 17.6.0 (CodeGauge repo)
  -> one synchronized version PR
  -> merge to main
  -> Release Please creates existing vX.Y.Z tag + GitHub Release
  -> carrier finds PR and correlates exact tag/release/SHA
  -> quality/provenance/target gates
  -> workflow_call release publication using existing release/tag
  -> ordered Cargo -> archives/checksums -> npm -> OCI publication
```

Dry-run/replay performs the same validation and release lookup but stops before any label mutation, downstream dispatch, upload, registry publication, tag creation, or release creation. A live carrier run is idempotent: if publication was already dispatched for the exact release identity, it records a no-op; if the Release Please release/tag is absent or points elsewhere, it fails closed and never creates a substitute.

## File Changes

| File | Action | Description |
|---|---|---|
| `release-please-config.json`, `.github/workflows/release-please.yml` | Modify | Make the Release Please-owned canonical tag/release explicit; keep repository-local scope and least privilege needed to update its PR/release. |
| `scripts/verify_release_provenance.py` | Modify | Validate Release Please PR #75 changelog/manifest shape and exact existing tag/release/SHA correlation. |
| `.github/workflows/release-tag-carrier.yml` | Modify | Remove Git refs/tag creation and label writes; query existing Release Please release/tag, then dispatch publication only after correlation. |
| `.github/workflows/release.yml`, `.github/workflows/release-publish.yml` | Modify | Require and revalidate the existing Release Please tag/release; never create a release as fallback. |
| `tests/release_carrier_tests.py`, `tests/release_carrier_static_tests.py` | Modify | RED tests for no tag/release API calls, exact release correlation, PR #75 changelog fixture, dry-run/replay, and fail-closed negatives. |
| `tests/release_please_runtime_tests.py`, `tests/release_please_runtime_harness.mjs` | Modify | Assert one repository-local Release Please PR/release/tag path and no carrier side effects. |
| `openspec/changes/codegauge-distribution/design.md` | Modify | Record this ownership model for implementation and verification. |

## Interfaces / Contracts

- Carrier validates the PR diff only when declared/actual hunk counts and API additions/deletions/changes agree; existing changelogs are allowed only on the approved Release Please paths/content.
- The carrier record MUST include `repository`, `version`, `tag`, `tag_sha`, `release_id`, `release_tag`, `release_url`, and `main_sha`; `tag_sha == main_sha` and `release_tag == tag` are mandatory.
- Release publication MUST receive the exact existing Release Please `release_tag`, `release_sha`, `main_sha`, and `release_url`; it MUST fail if the release is missing, draft/unpublished when a published release is required, or has a different tag/SHA.
- Release Please uses its repository-scoped token only in the Release Please workflow. The carrier uses a read-only token for lookup/validation and a narrowly scoped dispatch capability only if GitHub requires it; no carrier token may have `contents: write` for tag/release creation.
- Replay input is `^[0-9a-f]{40}$`, valid only for manual main dry-run. Dry-run evidence contains no credentials and marks tag/release creation and all downstream mutations as skipped or not-started.

## Testing Strategy

| Layer | What to test | Approach |
|---|---|---|
| RED unit | Ownership and provenance | Static tests fail if carrier contains Git refs/release creation, if publish contains release-creation fallback, or if Release Please is not the configured owner; pure validator tests cover exact release correlation and PR #75 changelog fixture. |
| GREEN integration | Release Please graph and locked workspace | Read-only v17.6.0 fake-SCM harness, `cargo metadata --locked`, workflow static/security tests, and carrier tests. |
| Acceptance | Hosted boundary | Authorized dry-run/replay proves one local Release Please release/tag is correlated and every mutation is skipped; authorized live run proves publication consumes that exact release and no carrier-created tag/release exists. |

## Permissions, Idempotency, Rollback

- `release-please.yml`: `contents: write`, `pull-requests: write`, and `issues: write` only for the Release Please job, using `RELEASE_PLEASE_TOKEN`; no parent-repository permissions.
- `release-tag-carrier.yml`: `contents: read` for lookup and validation; dispatch permission only where unavoidable. It must not request or use `contents: write` and must never call `POST /git/refs` or `gh release create`.
- `release.yml`/`release-publish.yml`: read-only release/tag verification plus the existing registry-specific publish permissions. Asset upload is allowed only to the pre-existing Release Please release after all build gates pass.
- Concurrency is keyed by exact release tag. Replays remain read-only. If a release/tag is wrong or missing, stop and repair/re-run Release Please rather than creating a substitute. If a downstream channel fails, preserve the exact release and rerun only the idempotent publication stage.

## Migration / Rollout

1. Write RED tests against the current carrier tag/release writes and release-publish fallback.
2. Implement the smallest workflow/validator change until focused tests pass.
3. Run local static, pure-validator, runtime-harness, Cargo metadata, and whitespace checks.
4. Run an authorized hosted dry-run/replay; verify existing Release Please release/tag correlation and zero mutation.
5. Run the live release only under explicit operator authorization; archive remains gated until verify and QA are policy-allowed.

## Open Questions

- [ ] None blocking. The owner model is fixed; hosted live evidence and external registry credentials remain operational gates, not design decisions.
