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
