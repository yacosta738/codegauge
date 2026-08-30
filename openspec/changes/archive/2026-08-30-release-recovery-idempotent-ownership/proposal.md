# Proposal: Idempotent Release Recovery and Ownership

## Intent

Recover merged `v0.3.0`, which remained untagged because global and root Release Please configuration suppress GitHub Release creation. The workflow can succeed while no canonical release exists. Recovery must restore one owner and prevent duplicate tags, releases, publications, or uploads.

## Scope

### In Scope
- Make Release Please the sole owner of canonical `vX.Y.Z` tags and GitHub Releases.
- Add explicit authenticated recovery with dry-run validation, idempotent reruns, and fail-closed identity checks.
- Keep the carrier limited to merged-main correlation and downstream dispatch; publication workflows must not create fallback releases.
- Verify provenance, synchronized versions, manifests, checksums, ordering, and failure behavior without external writes.

### Out of Scope
- CodeGauge engine, provider, profile, schema, or scoring semantics.
- Replacing Release Please, redesigning distribution targets, or committing credentials.
- Unrelated dependency, CI, or documentation cleanup.

## Capabilities

### New Capabilities
- `release-recovery`: Contract for explicit merged-release recovery into the canonical tag, GitHub Release, and publication pipeline, including dry-run, idempotency, provenance, and rollback.

### Modified Capabilities
- None; `openspec/specs/` has no existing release capability. The new capability defines the complete contract.

## Approach

Remove Release Please’s GitHub-release suppression while preserving version-file updates. Exercise effective Release Please 17.6.0 behavior with a no-write runtime harness. Harden carrier and recovery around exact main SHA, tag/release identity, resource reconciliation, and explicit live authorization. Preserve ordered Cargo/npm/container publication and require dry-run-first recovery plus deterministic Python contracts.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `release-please-config.json`, `.release-please-manifest.json` | Modified | Ownership and synchronized versions. |
| `.github/workflows/{release-please,release-tag-carrier,release-on-tag,release,release-build,release-publish}.yml` | Modified | Stage boundaries, recovery, provenance, ordering, and ownership. |
| `scripts/verify_release_provenance.py`, `tests/*release*` | Modified | Identity, idempotency, checksum, runtime, and no-write contracts. |
| `Cargo.toml`, `Cargo.lock`, `crates/*/Cargo.toml`, `npm/**/package.json`, `Dockerfile` | Verified/Modified | Distribution metadata and artifact contracts. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Duplicate or mismatched resources | Med | Dry-run, exact lookup, reconciliation, fail closed. |
| Partial registry/image publication | Med | Preflight, immutable SHA provenance, ordering, target rollback. |

## Rollback Plan

Disable live recovery and revert this change set. Never delete an existing tag or release. For partial publication, stop downstream jobs, inventory immutable versions, and use registry/image deprecation or rollback rather than a new identity.

## Dependencies

- Release Please 17.6.0, repository-scoped token, GitHub permissions, and hosted runners.
- Cargo/npm/OCI credentials for live verification; local tests remain credential-free.

## Success Criteria

- [ ] Exactly one canonical tag and GitHub Release is created or reconciled.
- [ ] Dry-run and repeated authorized recovery are deterministic, idempotent, and fail closed on mismatch.
- [ ] Local provenance, carrier, runtime, package, checksum, and workflow tests pass without writes.
- [ ] Ordering, artifact identity, rollback, and unavailable hosted evidence are auditable.
