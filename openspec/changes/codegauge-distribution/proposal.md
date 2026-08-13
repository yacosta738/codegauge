# Proposal: Production CI/CD and Distribution for CodeGauge

## Intent

Make merged `main` ship quality-gated Cargo/source, npm, OCI, and GitHub Release
distributions. Preserve RFC-0001 engine behavior, schemas, and result/error contracts.

## Scope

### In Scope
- Pinned CI: Rust 1.97.1, locked tests, fmt, Clippy, Python, and package checks.
- Cargo strategy, provenance, and package validation.
- Plain wrapper plus six GNU packages: pins, `os`/`cpu`, argv/stdio/exit passthrough.
- Eight archives/SHA-256, release-please, two-arch OCI, permissions, rollback.

### Out of Scope
- Engine/profile/schema/fixture/golden/JSON/error/exit semantics; crate redesign.
- Unverified platforms, namespace reservation, credentials, unrelated API/UX.

## Capabilities

### New Capabilities
- `ci-quality-gates`: CI.
- `cargo-distribution`: Cargo/source provenance.
- `npm-distribution`: Platform resolution.
- `release-artifacts`: Archives/checksums/releases.
- `oci-distribution`: OCI image.

### Modified Capabilities
- None; no relevant main specifications exist.

## Approach

Reuse peer topology with workspace builds and immutable pins; reject floating tags, inert
dry-runs, checksum omissions, and broad permissions. Publish after quality, target, package,
checksum, and metadata gates. Approved decisions:

1. **Cargo:** publish the coordinated versioned runtime graph to crates.io, with Git/source install
   retained as a fallback.
2. **npm/OCI names:** use `@yacosta738/codegauge` plus same-scope platform packages and
   `ghcr.io/yacosta738/codegauge`.
3. **Targets:** cover the complete viable matrix: eight archives, six npm targets, and OCI
   `linux/amd64`/`arm64`, rejecting any target that cannot produce evidence.

Verify checksums before upload/extraction; stop registries on failure. Slices: A Cargo/version;
B CI; C npm; D archives/Release; E OCI.

**Decision needed before apply: No**
**Chained PRs recommended: Yes**
**400-line budget risk: High**

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| Cargo manifests/lock | Modified | Versions/packages. |
| Workflows/release config | New | Gates/publishing/permissions. |
| `npm/` | New | Wrapper/tests. |
| Docker/docs | New/Modified | Image/install. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cargo crate exposure | High | Complete-graph metadata/package checks, dry-runs, dependency ordering, and immutable releases. |
| Existing Clippy blocks CI | High | Visible; separate no-semantic prerequisite. |
| Version/checksum drift | Med | One version and verification gates. |
| Non-atomic publication | High | Ordered jobs, stop-on-failure, corrected patch/deprecation. |
| Optional/permission failure | Med | Exact pins, platform errors, job-scoped OIDC. |

## Rollback Plan

Disable triggers; revert slices. After partial publication, stop later jobs, preserve history,
deprecate/retag bad npm/OCI artifacts, and ship a corrected patch; Cargo versions cannot be deleted.

## Dependencies

- Configure approved Cargo, npm, OCI, target, protection, and credential settings without committing secrets.

## Success Criteria

- [ ] Merged-main CI passes locked Rust/Python and distribution gates.
- [ ] `codegauge version`, manifests, npm, archives, and OCI labels share version/source identity.
- [ ] Claimed targets run or are rejected with evidence; archives/npm binaries pass SHA-256 checks.
- [ ] Failures leave logs, no leaked credentials, and a recovery action.
