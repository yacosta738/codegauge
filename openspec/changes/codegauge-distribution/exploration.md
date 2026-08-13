## Exploration: CodeGauge distribution

### Current State

Baseline is `yacosta738/codegauge` commit `6477eb1` (the merged RFC-0001 engine). The only
working-tree additions are the SDD bootstrap files under `.atl/` and `openspec/`; no application or
distribution files were changed during this exploration.

- CodeGauge is a virtual Cargo workspace with six crates and an inward-only graph:
  `codegauge-model -> codegauge-core -> codegauge-application -> codegauge-provider-jacoco ->
  codegauge-cli`, plus `codegauge-conformance` as a test boundary. The CLI package is named
  `codegauge-cli`, but its binary target is already named `codegauge`.
- Every member is version `0.1.0` and `publish = false`. The root `Cargo.toml` has only
  `[workspace]` and pinned shared dependencies; it has no `[package]`, publish metadata, license,
  repository, readme, or release package for `release-please` to bump. Internal path dependencies
  also have no registry `version` requirements. `cargo metadata --locked` reports null package
  metadata and an empty publish list.
- `codegauge-application` hard-codes `TOOL_VERSION = "0.1.0"`; the CLI, DTO tests, README, and
  golden/contract checks assert the current version. A future release must synchronize the displayed
  tool version with the released artifact without changing profile, schema, JSON, or exit-code
  semantics.
- The engine already computes lowercase SHA-256 digests for input artifacts and validates the
  64-hex contract. That is input provenance, not a release-archive checksum. The README release
  checklist already requires an immutable revision, target triples, and an artifact SHA-256, but no
  workflow produces those assets yet.
- There are no `.github/workflows/**`, npm files, Dockerfile, `.dockerignore`, release-please
  configuration, release manifest, license, or distribution-specific tests. `.gitignore` only
  covers generic Rust/Node build output.
- Existing quality evidence at this baseline: `cargo metadata --locked`, `cargo test
  --workspace --locked` (30 tests), `cargo fmt --all -- --check`, `tests/bootstrap_checks.py`, and
  `tests/readme_checks.py` pass. The required Clippy command is currently red before any
  distribution work: `cargo clippy --workspace --all-targets --locked -- -D warnings` rejects the
  pre-existing deprecated `quick_xml::Attribute::unescape_value` call in
  `crates/codegauge-provider-jacoco/src/lib.rs:237`. This is an existing quality-gate blocker, not
  a reason to alter engine behavior in this change.

The peer comparison is concrete:

| Area | CodeGauge now | `agentsync` | `file-organizer` |
|---|---|---|---|
| Hidden workflows | None | `.github/workflows/ci.yml` (284 lines) and `release.yml` (678 lines) | `ci.yml` (70 lines) and `release.yml` (626 lines) |
| Cargo publish model | Virtual workspace; all six members `publish=false`; no metadata | Root publishable package `agentsync` 1.48.0 with MIT/repository/readme/keywords/categories/excludes and release profile | Root publishable package `organiza` 0.3.0 with the same metadata and release profile |
| npm | None | `@dallay/agentsync` wrapper plus six generated platform packages; pnpm workspace | `@dallay/organiza` wrapper plus six generated platform packages; plain npm and one template |
| Release assets | None; only input SHA-256 provenance exists | Eight target archives, each with `.sha256` sidecar; six GNU-target npm packages | Same eight-archive/six-npm-package topology |
| Docker/OCI | None | Multi-stage `rust:1.97-alpine` -> `alpine:3.24`, non-root user, tini, OCI labels, Buildx/QEMU for `linux/amd64,linux/arm64` | Multi-stage `rust:1-alpine` -> `alpine:3.23`, same runtime safety pattern and multi-arch workflow |
| Release/version sync | No release config; six duplicated `0.1.0` values plus hard-coded tool version | `release-type: rust`, root package manifest, npm version and six optional-dependency JSONPaths | `release-type: rust`, npm version and six optional-dependency JSONPaths |
| CI permissions/toolchain | Not established; local toolchain is exact Rust/Cargo `1.97.1`, minimal profile, rustfmt + Clippy | CI/release mostly use `stable`; release has broad top-level write permissions and narrows npm/Docker jobs | CI is contents-read; release has broad top-level write permissions and narrows npm/Docker jobs; Docker/toolchain tags are less exact |
| Distribution tests | Strong engine unit/integration/conformance tests and Python contract checks; no package/image/workflow tests | Broad Rust, security, integration, and Docker E2E tests, but no dedicated release-package test suite | README regression tests; distribution behavior was primarily verified statically/manual in its archived change |

Reusable peer patterns are useful, but not copy-pasteable:

- Both peers use a release-please `rust` release, a release tag output, an eight-target matrix
  (Linux GNU + musl for x86_64/aarch64, macOS x64/arm64, Windows x64/arm64), `tar.gz` on Unix,
  `zip` on Windows, and one `.sha256` file per archive. The npm matrix intentionally publishes
  six GNU platform packages; musl is used for release assets/Docker only.
- Both use a plain npm template for platform packages with `os`/`cpu`, exact optional dependency
  pins, `require.resolve(<package>/package.json)`, inherited stdio, unchanged argv, and child exit
  status passthrough through `spawnSync`. This is the right contract-preserving wrapper shape for
  CodeGauge. `agentsync` adds pnpm because it has a developed npm workspace; CodeGauge has no such
  workspace, so the file-organizer plain-npm pattern is the smaller fit.
- Both release workflows pin third-party actions to full SHAs with version comments, use a
  release concurrency group, upload assets before/alongside publishing, publish platform npm
  packages before the base wrapper, and use `id-token: write` for npm provenance. They also use
  Docker metadata tags for exact semver, major/minor, major, and `latest`.
- Both peer Dockerfiles assume one root Cargo package with `COPY src ./src`; that will not work for
  CodeGauge's `crates/**` workspace. A workspace-aware build must copy all relevant manifests and
  sources and invoke the `codegauge` binary target explicitly. The peer builder tags are also not
  a complete reproducibility policy: `rust:1-alpine`, `alpine:3.x`, and `stable` are moving inputs.
- The peer release workflows declare a `dry_run` dispatch input but do not consume it. Their npm
  jobs create or rewrite package versions on the runner, and extract a single downloaded archive,
  but do not verify its `.sha256` sidecar before packaging. Their release publishers depend on the
  binary build, but the release graph does not itself run the full Rust/Python quality gate; that
  depends on branch protection/earlier CI. These are risks to avoid, not requirements to inherit.

Cargo is the main architectural constraint. A `cargo publish --dry-run` against the current CLI
member is rejected immediately because `package.publish` is false. Cargo's publishing contract
also requires a version for a local dependency that is intended for publication. Therefore a
single release workflow cannot simply flip `codegauge-cli` to publishable: its runtime path
dependencies are unpublished, unversioned local crates. `cargo package --list` also shows the CLI
test source but not the repository-level fixtures it references, while model/conformance tests
refer to repository-level schemas/goldens. The proposal must explicitly choose a registry model
and validate package contents; silently copying the single-package peer setup would produce a
non-publishable crate or expose incomplete tests.

### Affected Areas

- `Cargo.toml`, `crates/*/Cargo.toml`, and `Cargo.lock` — decide the Cargo publication graph,
  package metadata, version provenance, versioned path dependencies, lockfile synchronization, and
  package excludes/includes without changing the dependency direction.
- `crates/codegauge-application/src/lib.rs` and version assertions in `crates/**/tests`,
  `tests/readme_checks.py`, and `README.md` — only the release-version source needs consideration;
  profile/schema/metric/output/exit contracts must remain unchanged.
- `.github/workflows/ci.yml` (new) — locked Rust/Python quality gates, cross-OS tests, workflow
  pinning, least-privilege permissions, and static distribution checks.
- `.github/workflows/release.yml` (new) — release-please output, release-tag checkout, target
  matrix, archive/checksum creation and verification, registry gates, npm ordering, OCI publishing,
  and summary/rollback behavior.
- `release-please-config.json` and `.release-please-manifest.json` (new) — version provenance for
  the actual Cargo workspace package paths and npm wrapper/optional dependencies. A virtual root
  cannot be treated like the peer single-package roots; release-please's Cargo-workspace and
  linked-version behavior needs a focused design/test.
- `npm/package.json.tmpl`, `npm/codegauge/` (new) — plain-npm wrapper, six optional platform
  packages, exact pins, TypeScript build, and package-resolution/exit-code tests. The final npm
  scope/name is not present in the repository and must be confirmed before proposal.
- `Dockerfile` and `.dockerignore` (new) — workspace-aware multi-stage musl build, non-root/tini
  runtime, OCI labels, and exclusion of target/npm/CI/SDD material from the build context.
- `README.md`, `.gitignore`, `LICENSE`, and possibly `renovate.json` — install channels, target
  claims, release checksums, required secrets/permissions, rollback, generated npm artifacts, and
  immutable dependency/action/image pinning.
- `schemas/`, `fixtures/`, and existing conformance tests — packaging verification boundaries only;
  do not change schema IDs, fixture semantics, golden output, parser limits, or engine algorithms.

### Approaches

1. **Publish a coordinated runtime-crate workspace** — promote the publishable runtime graph
   (`model`, `core`, `application`, `provider`, and the CLI package) with complete Cargo metadata,
   registry-versioned local dependencies, a workspace/linked-version release configuration, and
   dependency-order publishing; keep `codegauge-conformance` private.
   - Pros: preserves the existing inward-only crate boundaries and binary implementation; supports
     a real `cargo install` channel; makes the current public library APIs intentionally versioned
     rather than duplicating engine code.
   - Cons: expands the public crates.io surface despite the README saying future consumers use the
     executable/contracts rather than CodeGauge crates; requires package-content decisions for
     repository-level fixtures/schemas; release-please and Cargo publish ordering are materially
     more complex; a bad registry release is non-deletable.
   - Effort: High.

2. **Keep engine crates private and distribute the executable through GitHub Releases, npm, and
   OCI; use Cargo only for source/build installation** — retain `publish=false`, build the explicit
   `codegauge` binary for archives/Docker, and document `cargo install --git` or local source builds
   instead of crates.io.
   - Pros: best preserves the RFC boundary and private crate graph; avoids exposing internal APIs,
     path-dependency publication, and crate registry rollback risk; smallest application impact.
   - Cons: does not provide the discoverable `cargo install codegauge` registry channel; may fail the
     stated distribution objective if crates.io is mandatory; version synchronization still must
     update the binary's displayed version.
   - Effort: Medium.

3. **Collapse or duplicate the engine into one publishable `codegauge` package** — create a single
   registry package containing the binary and all engine modules, leaving the current workspace as a
   test/development shape or replacing it.
   - Pros: one crate, one Cargo version, simple release-please and `cargo publish` topology.
   - Cons: invasive source/layout change, duplicated or weakened crate boundaries, high risk to
     RFC-0001 contracts and tests, and explicitly outside a distribution-only change.
   - Effort: High.

The peer channel topology itself has two useful options: retain parity (eight release archives,
six GNU npm packages, and two-architecture OCI images), or promise only the targets that can be
built and verified in CI. Parity is the stronger starting point because it is already exercised in
both peer workflows, but every target must have an artifact, verified checksum, and documented
runner; no platform may be claimed from a matrix entry alone.

### Recommendation

Proceed to proposal, but make the Cargo registry model and npm package namespace explicit decision
points before implementation. If a crates.io channel is required, choose Approach 1 and design the
workspace publication graph first; do not flip `publish=false` casually. If the RFC's “released
executable and result/error contract, not CodeGauge crates” boundary is authoritative, choose
Approach 2 and state that Cargo source installation is not crates.io publication.

For the rest of the distribution surface, reuse the file-organizer/agentsync topology with
CodeGauge-specific corrections:

- Keep engine semantics and public contracts frozen; make the displayed tool version derive from
  the synchronized release version so `codegauge version` matches archives/npm/OCI.
- Prefer plain npm, a committed TypeScript wrapper, one generated platform-package template, six
  exact optional dependencies, inherited stdio, unchanged argv, and exit-code passthrough.
- Use a workspace-aware Docker build targeting `codegauge`, exact Rust `1.97.1`, `--locked`, a
  minimal non-root/tini runtime, and immutable OCI metadata. Do not copy the peers' root `src/`
  assumptions or floating `stable`/`rust:1-alpine` tags.
- Use release-please JSONPath updates for the base npm version and all six optional dependencies;
  use a workspace/linked-version configuration for Cargo; verify `Cargo.lock` and all manifests in
  the release PR. The release workflow should consume `dry_run` or remove the unused input.
- Add a release validation gate for locked tests, fmt, Clippy, Python contracts, package metadata,
  npm typecheck/package contents, target-matrix completeness, and Docker metadata before any
  registry publish. Generate `.sha256` sidecars and verify them before release upload and npm
  extraction; optionally publish one aggregate checksum manifest.
- Scope permissions per job: read-only CI; release-please contents/issues/pull-requests writes;
  release upload contents write; npm contents read + OIDC id-token write; Docker contents read +
  packages write; Cargo registry token only where needed. Document secrets and the unavoidable
  non-atomic rollback across crates.io, npm, GitHub Releases, and image registries.

Review workload is high. Use chained PRs with autonomous rollback and verification:

| Slice | Scope and finish condition | Verification / rollback |
|---|---|---|
| A — Cargo publication and version provenance | Decide Approach 1 vs 2; add only manifests/version source/lockfile/package-content rules and contract tests; no publish trigger | `cargo metadata`, package dry-runs, `codegauge version`, existing contract suite; revert metadata/version-only commit |
| B — CI and static release checks | Add least-privilege CI, pinned actions, cross-OS quality matrix, Python checks, workflow/package/checksum lint; no registry writes | action pin audit, YAML/actionlint, locked gates; remove workflow files without engine rollback |
| C — npm wrapper | Add plain npm wrapper, template, six platform mapping, exact-pin/version-sync tests, and generated-output ignores | `tsc --noEmit`, `npm pack --dry-run`, wrapper version/exit passthrough; delete npm slice |
| D — release archives and GitHub Release | Add release-please manifest/config plus cross-target builds, target-labelled archives, checksum generation/verification, and gated asset upload | dry-run/release-PR diff, archive matrix and SHA checks; disable/revert release workflow before merging a release PR |
| E — OCI image | Add workspace-aware Dockerfile, `.dockerignore`, Buildx/QEMU metadata and gated Docker Hub/GHCR push | Docker build/inspect/run on amd64/arm64 where available; remove Docker slice and retag/delete escaped images |

The combined change is forecast above the 400-line review budget; chained PRs are recommended.

Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High

### Risks

- Current Cargo publication is structurally blocked by a virtual root, `publish=false` members, and
  unversioned local dependencies; the registry strategy can change the intended public API surface.
- A root-style release-please config copied from either peer will not describe this workspace and may
  leave Cargo versions, `Cargo.lock`, npm pins, and `TOOL_VERSION` divergent.
- The current Clippy gate is already failing on a deprecated quick-xml API; adding CI/release gates
  without resolving or explicitly scoping this baseline failure will make the distribution change
  appear broken.
- CLI/package tests and conformance tests reference repository-level fixtures, schemas, and goldens;
  Cargo package contents must be validated before any crate is published.
- A workspace Dockerfile copied from the peers will omit `crates/**` and fail or build the wrong
  target. Floating Rust/Alpine/action/tool versions would undermine reproducibility.
- npm optional dependencies are optional by design: a missing or mismatched platform package can
  allow installation to finish and fail only when the wrapper runs. Exact pins, `os`/`cpu`, archive
  checksum verification, executable-bit checks, and supported-platform errors are required.
- Cross-registry publication is not atomic. A later npm, Cargo, GHCR, or Docker Hub failure can leave
  earlier artifacts live; release gating reduces exposure but rollback must be documented and tested.
- Peer release workflows use broad top-level write permissions and inert `dry_run` inputs; copying
  them would create avoidable security and operational risk.
- Registry names, npm scope, GHCR ownership, trusted-publishing/OIDC configuration, and secrets are
  external prerequisites and cannot be validated fully from this local workspace.
- The distribution surface is large enough to overload a single review; merge only through the
  autonomous slices above.

### Ready for Proposal

Yes. The orchestrator should tell the user that the engine and contracts are understood and untouched,
but the proposal must first lock (1) whether crates.io publication is mandatory or the executable-only
boundary wins, (2) the Cargo package/version topology, and (3) the npm/OCI names and supported target
matrix. No application or distribution implementation should begin from this exploration alone.
