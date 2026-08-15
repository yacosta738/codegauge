# Release Artifacts and Channels Specification

## Purpose

Create traceable GitHub Release artifacts and coordinate Cargo/source, npm, and OCI channels without
pretending that cross-registry publication is atomic.

## Requirements

### Requirement: Immutable version provenance

The release process MUST derive one approved version from release metadata, create the release from
an immutable Git revision, and propagate that version and source identity to Cargo metadata, the
`codegauge version` output, npm packages, archives, and OCI metadata. Release-please configuration
MUST address the actual workspace packages and npm version pins rather than assuming the virtual
workspace root is publishable. A virtual workspace root MUST NOT be treated as a publishable Cargo
package by assumption. Publication MUST originate from merged `main` and its immutable release tag,
not from an unmerged pull request.

#### Scenario: Provenance mismatch

- GIVEN any channel reports a different version or source revision
- WHEN release validation compares the artifacts
- THEN the release is blocked before publication and the mismatching channel is identified

### Requirement: Virtual workspace root release ownership

Release-please configuration MUST give repository-level version and contract-file updates to an
effective candidate that survives the Release Please 17.6.0 workspace plugins. A virtual Cargo root
MUST NOT be configured as a Rust package candidate because it has no `[package].name`. A non-Cargo
metadata candidate MAY carry those updates only when it has no package identity and MUST skip its own
GitHub release; exactly one approved runtime component MUST create the unprefixed `vX.Y.Z` tag.

#### Scenario: Root updates survive the plugin pipeline

- GIVEN the repository has a virtual Cargo workspace and root-owned extra-files
- WHEN the Release Please 17.6.0 Cargo, Node, and linked-versions plugins process candidates
- THEN the root candidate remains effective, owns the root extra-file updates, optional npm pins are
  rewritten from the linked versions map, and exactly one unprefixed `vX.Y.Z` release operation remains

#### Scenario: Virtual root cannot publish as a fake package

- GIVEN the root candidate is used only to carry repository metadata updates
- WHEN Release Please prepares GitHub releases and package publication
- THEN the root has no Cargo/npm package identity and its skipped release cannot create a fake root
  package or a duplicate tag

### Requirement: Private workspace members stay outside Stage-A updates

Stage-A Release Please configuration MUST use an explicit list of the five approved runtime Cargo
packages when the repository workspace also contains a private conformance member. It MUST NOT use
the Release Please 17.6.0 `cargo-workspace` plugin for this graph because the exact packaged source
(`build/src/plugins/cargo-workspace.js`, lines 45–84 and 138–193; `workspace.d.ts`, lines 11–16)
scans every declared workspace member and exposes no supported member-exclusion option. The private
`crates/codegauge-conformance/Cargo.toml` MUST remain a Cargo workspace member for builds/tests,
MUST remain `publish = false`, and MUST be absent from the effective Stage-A update set and linked
component set. The non-Cargo root metadata carrier MAY own explicit runtime Cargo lock/dependency
version selectors, but those selectors MUST exclude the private member.

#### Scenario: Exact v17.6.0 private-candidate boundary

- GIVEN the root Cargo workspace declares five runtime crates and private
  `codegauge-conformance`
- WHEN the exact Release Please 17.6.0 Manifest/plugin chain runs against a read-only fake SCM
- THEN it MUST create one synchronized PR with all five runtime Cargo candidates, the root metadata
  carrier, the linked versions map, and six npm optional dependency rewrites, with zero release/tag
  calls, and MUST NOT propose `crates/codegauge-conformance/Cargo.toml`
- AND a mutation containing that private manifest MUST be rejected by the unchanged Stage-B exact
  diff allowlist

### Requirement: Linked versions must not depend on tag naming

The release architecture MUST prove that every intended runtime Cargo crate, the npm wrapper, and all
six npm platform packages resolve to one version and that the wrapper's `optionalDependencies` are
rewritten from that synchronized versions map. Under the exact Release Please 17.6.0 source,
`include-component-in-tag: false` returns an empty strategy component and
`linked-versions` skips empty components. Therefore the release flow MUST either use a supported
Release Please implementation whose linked lookup is independent of tag naming, or separate the
component-tagged version-PR pass from a trusted post-merge carrier that creates exactly one unprefixed
`vX.Y.Z` tag. A configuration that merely lists component names while the effective strategy component
is empty is invalid and MUST remain blocked.

#### Scenario: v17.6.0 empty-component gate

- GIVEN the global unprefixed-tag contract is enabled under Release Please 17.6.0
- WHEN `LinkedVersions.preconfigure()` evaluates the configured strategies
- THEN the regression MUST observe a synchronized versions map for the full runtime graph, or report
  the exact architecture blocker instead of claiming that optional dependency synchronization passed

#### Scenario: Synchronized npm optional pins

- GIVEN the linked versions map contains the full runtime graph at version `X.Y.Z`
- WHEN the v17.6.0 Node workspace/package-json updater processes `npm/codegauge/package.json`
- THEN every platform entry in `optionalDependencies` is rewritten to its corresponding synchronized
  platform version, including any supported range prefix, and the final release carrier emits only
  `vX.Y.Z`

### Requirement: Auditable hosted carrier rehearsal

The Stage-B carrier MUST accept only trusted `push` or `workflow_dispatch` events resolved to
`refs/heads/main`. A manual dispatch MUST expose a required boolean `dry_run` input. An automatic
push MUST derive its mode from the explicit repository variable `RELEASE_CARRIER_DRY_RUN`, accepting
only `true`, `false`, or unset; unset and `false` MUST preserve the live production default and any
unknown value MUST fail closed. The manual input MUST take precedence for a manual run.

Both modes MUST collect and validate the same merged Release Please version PR, exact Stage-A diff,
tree/version/provenance/lockfile/metadata boundaries, and canonical `vX.Y.Z` tag plan. Dry-run mode
MUST emit a credential-free machine-readable carrier plan and workflow-summary record, and MUST NOT
create or update a Git ref, mutate Release Please labels, dispatch `release-on-tag.yml`, upload a
release asset, or invoke any registry publisher. Live mode MUST retain the existing tag compare/create,
race retry, and label handoff behavior.

#### Scenario: Manual carrier dry-run

- GIVEN `release-tag-carrier.yml` is dispatched on `main` with `dry_run: true`
- WHEN the carrier collects the merged Release Please PR and validates the merged tree
- THEN it emits the canonical tag plan and explicit skipped-mutation evidence
- AND it MUST NOT create a tag, change labels, dispatch the tag workflow, upload, or publish

#### Scenario: Automatic push rehearsal variable

- GIVEN `RELEASE_CARRIER_DRY_RUN` is temporarily set to the exact value `true`
- WHEN the synchronized Release Please version PR is merged into `main`
- THEN the automatic carrier performs the same read-only validation and plan generation
- AND it MUST skip tag-ref and label writes so the merge cannot start the live tag path

#### Scenario: Live default after rehearsal

- GIVEN `RELEASE_CARRIER_DRY_RUN` is absent or set to `false`
- WHEN a trusted synchronized version PR merge pushes `main`
- THEN the carrier remains in live mode and preserves the canonical tag compare/create and label handoff

#### Scenario: Invalid rehearsal configuration

- GIVEN the dispatch input or repository variable contains a value other than the accepted booleans
- WHEN the carrier resolves its mode
- THEN it fails closed before any tag or label mutation

### Requirement: Approved archive matrix and checksums

The release MUST use the approved complete viable target matrix of eight archives: Linux GNU and
musl for x86_64 and aarch64, macOS x64 and arm64, and Windows x64 and arm64. Every approved target
MUST have the correct platform archive format (`tar.gz` on Unix-like targets and `zip` on Windows),
a version/target-identifiable name, and a lowercase SHA-256 sidecar. Each sidecar MUST be verified
before GitHub upload and before any archive extraction for packaging. A target that cannot produce
reproducible build and runtime evidence MUST be rejected rather than claimed.

#### Scenario: Complete archive release

- GIVEN the complete viable target matrix has been approved
- WHEN all target builds finish
- THEN every approved target has one archive and checksum, and each checksum verifies the archive

#### Scenario: Missing target evidence

- GIVEN a matrix entry has no archive or sidecar
- WHEN release assets are prepared
- THEN the GitHub Release and dependent registry publishers remain blocked

### Requirement: Ordered, gated channel publication

GitHub Release assets MUST be uploaded only after quality, target, package, checksum, and metadata
gates pass. If npm is enabled, platform packages MUST publish before the base wrapper. If Cargo
registry publication is enabled, dependencies MUST publish before dependents. OCI publication MUST
wait for its architecture and runtime gates.

#### Scenario: Gate failure before upload

- GIVEN a checksum or package gate fails
- WHEN the release graph reaches publication
- THEN no later channel publisher runs and the failure remains auditable

### Requirement: Provenance and publication security

Release metadata MUST record the source revision, version, target, and artifact checksums. Publishing
jobs MUST use only the credentials and permissions they require, use trusted OIDC provenance where
the registry supports it, and MUST NOT place tokens in artifacts, logs, or repository files.

#### Scenario: Credential exposure check

- GIVEN a release job emits an artifact or log containing a registry token
- WHEN security validation runs
- THEN the release fails and the affected publication is not promoted

### Requirement: Non-atomic failure recovery

On any publication failure, the workflow MUST stop later publishers, retain logs and successful
artifact history, and expose a recovery action. Escaped npm or OCI artifacts MUST be deprecated,
retagged, or superseded by a corrected patch; Cargo versions already published MUST NOT be treated
as deletable. Release triggers MAY be disabled while recovery is performed.

#### Scenario: Partial publication

- GIVEN GitHub assets publish but an npm or OCI publisher fails
- WHEN the failure is recorded
- THEN later jobs stop, the partial state is documented, and a corrected release path is identified
