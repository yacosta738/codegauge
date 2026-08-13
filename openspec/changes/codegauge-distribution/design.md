# Design: CodeGauge CI/CD and Distribution

## Technical Approach

Keep the virtual Cargo workspace as the source/build boundary and publish the coordinated runtime
Cargo graph to crates.io after package-content and dependency-order validation. Pinned, read-only CI
owns quality and static checks. A separate release workflow starts from an immutable release-please
tag, builds once, verifies artifacts/checksums, then publishes Cargo crates, GitHub assets, npm
packages, and OCI images in order. RFC-0001 engine behavior and profile/schema/metric/JSON/exit
contracts remain untouched.

## Architecture Decisions

| Decision | Choice | Alternative rejected | Rationale |
|---|---|---|---|
| Cargo channel | Publish the coordinated runtime graph to crates.io and retain source/Git installation as a fallback. | Publish one crate only or keep every crate private. | The approved registry channel must preserve path-dependency order, complete metadata, package contents, and RFC-0001 boundaries. |
| Version provenance | Keep one synchronized workspace/package version; derive `TOOL_VERSION` from `CARGO_PKG_VERSION`; use release-please Cargo-workspace/linked versions and update the root workspace version through a TOML extra-file. | Tag-only versioning or unsynchronized package constants. | Cargo remains the source/build boundary, while literal package versions are required because release-please's Cargo-workspace parser does not resolve `version.workspace = true`. |
| Target strategy | Enable the complete viable matrix: Linux x86_64/aarch64 GNU+musl, macOS x86_64/aarch64, and Windows x86_64/aarch64 MSVC; native macOS/Windows runners plus target-specific Linux toolchains; npm excludes musl, OCI uses musl. | Claim every Rust target without evidence. | Exact target commands, runner evidence, executable checks, and checksums prevent unsupported promises while covering every approved distribution target. |
| Publication security | Verify first; CI `contents:read`; plan `contents:write,issues:write,pull-requests:write`; assets/attestations `contents:write,attestations:write`; npm `id-token:write`; OCI `packages:write`. | Broad writes or long-lived tokens. | Limits blast radius; external registry credentials stay job-scoped. |

## Data Flow

```text
main -> release-please PR -> immutable tag -> quality/source gate
     -> target matrix -> archive + SHA-256 + manifest -> verify
     -> GitHub Release assets -> npm platform packages -> npm wrapper
     -> OCI multi-arch manifest -> attestations and release summary
```

The npm installer selects one exact `os`/`cpu` optional dependency. The wrapper resolves its
executable, preserves argv/stdio/exit status, and reports unsupported platforms. npm extraction
follows sidecar verification. OCI uses a workspace-aware multi-stage build, exact inputs, non-root
execution, and immutable source/version/revision labels.

Cargo, npm, and Docker caches are keyed by OS/architecture/target, toolchain, and lockfile; misses
never bypass a gate. Matrix failures, checksum/metadata drift, or missing targets fail aggregation.
A release concurrency group prevents duplicates; later writes stop after an earlier failure.

## File Changes

| File | Action | Description |
|---|---|---|
| `Cargo.toml`, `crates/*/Cargo.toml`, `Cargo.lock` | Modify | Inherited versions and source/package validation; preserve graph and private conformance crate. |
| `crates/codegauge-application/src/lib.rs`, version tests, `README.md` | Modify | Synchronized display version and channel docs; no engine changes. |
| `.github/workflows/ci.yml` | Create | Locked Rust/Python gates, cross-OS checks, pinned actions, read-only permissions. |
| `.github/workflows/release.yml`, release-please configs | Create | Tag-driven build/publish graph, linked versions, dry-run, permissions. |
| `npm/` | Create | TypeScript wrapper, platform template/generator, six optional packages under `@yacosta738`, tests. |
| `Dockerfile`, `.dockerignore` | Create | Workspace-aware musl build and minimal non-root multi-arch runtime. |
| `tests/distribution_checks.py` | Create | Manifest, target, package, checksum, and workflow invariants. |

## Interfaces / Contracts

Each release emits a manifest with `version`, immutable `source_revision`, `rust_toolchain`,
`target`, archive, and lowercase SHA-256; sidecars/assets must agree. The npm base package is
`@yacosta738/codegauge`, platform packages use the same approved scope, and the OCI image is
`ghcr.io/yacosta738/codegauge`. OCI labels include version, revision, source, and build epoch.
Archives and OCI digests receive GitHub/BuildKit provenance; npm uses trusted OIDC where enabled.
Cargo source provenance is the immutable tag plus manifest/lockfile validation; the default model
needs no Cargo registry secret.

## Testing Strategy

| Layer | What to test | Approach |
|---|---|---|
| Quality | Rust, fmt, Clippy, Python, and contract suites | Exact toolchain, `--locked`; never weaken `-D warnings`. |
| Static/package | Versions, targets, npm `os`/`cpu`, argv/stdio/exit | Python checks, TypeScript typecheck, `npm pack --dry-run`, fixtures. |
| Artifacts | Archives, executable bits, checksums, manifest, `version`/`profiles` | Matrix builds; native smoke tests and recorded cross-target evidence. |
| Release/OCI | Dry-run graph, labels, multi-arch manifest, provenance, rollback guards | Workflow/pin audit, Docker inspect/run, tag rehearsal without writes. |

## Migration / Rollout

No engine or data migration. The Cargo registry model, npm namespace, OCI registry/owner, complete
viable target matrix, and A→E chained-PR strategy are approved. First run the real dry-run, then
publish verified Cargo dependencies, GitHub assets, npm packages, and OCI images in their gated
order. On later failure, stop the graph, preserve logs/manifest, deprecate or supersede escaped
npm/OCI artifacts, and ship a corrected patch; released Cargo versions are not deletable.

## Resolved Decisions and Remaining Gate

- [x] Publish the coordinated runtime Cargo graph to crates.io.
- [x] Use `@yacosta738/codegauge` and same-scope platform packages.
- [x] Publish `ghcr.io/yacosta738/codegauge`.
- [x] Cover the complete viable target matrix defined above, with evidence for every claim.
- [x] Deliver through five chained PRs: A → B → C → D → E.
- [ ] Resolve the pre-existing Clippy failure in a separate no-semantic prerequisite before release gates can pass.
