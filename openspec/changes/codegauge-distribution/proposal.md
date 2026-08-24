# Proposal: Production CI/CD and Distribution for CodeGauge

## Intent

Enable merged `main` to ship CodeGauge through quality-gated Cargo/source, npm, OCI, and GitHub Release channels. Address the virtual workspace's missing publication metadata, workflows, packages, images, checksums, and version provenance while preserving RFC-0001 behavior, schemas, and result/error contracts.

## Scope

### In Scope
- Pinned Rust 1.97.1 CI: locked metadata/tests, format, Clippy, Python contracts, and package checks.
- Coordinated public Cargo runtime publication with immutable source fallback; keep private conformance unpublished and align only its four runtime dependency pins.
- Base npm wrapper plus six GNU-target packages with exact `os`/`cpu`, transparent argv/stdio/exit handling, archive extraction, and checksum verification.
- Eight target archives with SHA-256 sidecars, two-stage Release Please 17.6.0 orchestration, and `linux/amd64`/`arm64` OCI publication with provenance and smoke gates.
- Least-privilege permissions, fail-closed validation, ordered publication, and recovery evidence.

### Out of Scope
- Engine/profile/schema/fixture/golden/JSON/error/exit semantics or crate redesign.
- Unverified platforms, namespace reservation, live credential provisioning, and unrelated API/UX.

## Capabilities

### New Capabilities
- `ci-quality-gates`: deterministic pre-publication CI and permissions.
- `cargo-distribution`: Cargo graph, source installation, and provenance.
- `npm-distribution`: platform resolution and wrapper behavior.
- `release-artifacts`: archives, checksums, and GitHub Releases.
- `oci-distribution`: reproducible multi-architecture image publication.

### Modified Capabilities
- None; `openspec/specs/` has no existing main capabilities.

## Approach

Preserve the inward-only crate graph and public contracts. Stage A uses Release Please 17.6.0 to create one synchronized component PR with no GitHub release; a root metadata carrier owns repository and contract-file updates without becoming a fake Cargo package. Stage B validates the merged tree, exact private-conformance hunk, version graph, immutable revision, and metadata, then creates the canonical `vX.Y.Z` tag. Quality, target, package, checksum, and metadata gates precede ordered Cargo, archive, npm, and OCI publication. Approved identities are `@yacosta738/codegauge` and `ghcr.io/yacosta738/codegauge`; unsupported targets fail closed.

**Decision needed before apply: No**
**Chained PRs recommended: Yes**
**400-line budget risk: High**

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `Cargo.toml`, `crates/*/Cargo.toml` | Modified | Versions, metadata, registry pins, private exception. |
| `.github/workflows/`, release config | New/Modified | CI, release stages, permissions, gates. |
| `npm/`, `scripts/`, `tests/` | New/Modified | Wrapper, packages, generators, validators, contracts. |
| `Dockerfile`, `README.md`, release assets | New/Modified | OCI image, install guidance, archives, provenance. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Incomplete Cargo graph or stale private pins | High | Locked metadata, graph checks, ordered publication, fail-closed validation. |
| Existing Clippy failure blocks adoption | High | Keep visible as a prerequisite; do not weaken the gate. |
| Non-atomic cross-channel publication | High | Stop later jobs, preserve evidence, issue corrected releases. |
| Version, checksum, target, or permission drift | Med | Immutable pins, sidecars, target rejection, job-scoped credentials. |

## Rollback Plan

Disable release triggers and stop downstream jobs. Revert workflow/configuration slices. Do not delete published Cargo versions; deprecate or supersede incorrect npm packages, OCI tags, or archives, preserve evidence, and issue a corrected patch release.

## Dependencies

- Approved Cargo, npm, GHCR, GitHub protection, target-runner, and credential configuration; no secrets committed.

## Success Criteria

- [ ] Merged-main CI and distribution gates pass on the pinned toolchain.
- [ ] CLI output, manifests, npm, archives, and OCI metadata share version/source identity.
- [ ] Every claimed target has executable/checksum evidence; unsupported targets are rejected.
- [ ] Failures produce auditable logs without credential leakage and a recovery path.
