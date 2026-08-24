# Release Artifacts Specification

## Purpose

Create traceable GitHub Release artifacts and coordinate Cargo, source, npm, and OCI channels without assuming atomic publication.

## Requirements

### Requirement: Immutable version provenance

The release MUST derive one approved version and immutable source revision from merged `main`; both MUST reach Cargo metadata, `codegauge version`, npm, archives, and OCI metadata. The virtual root MUST NOT publish; one runtime component MUST create `vX.Y.Z`.

#### Scenario: Provenance mismatch

- GIVEN a channel reports a different version or source revision
- WHEN release validation compares provenance
- THEN publication is blocked and the mismatching channel is identified

### Requirement: Safe Release Please candidate graph

Stage A MUST include the five public runtime Cargo packages and exclude private conformance. A non-Cargo root carrier MAY own repository metadata and four private dependency-version fields, but MUST NOT change other private content.

#### Scenario: Private member exclusion

- GIVEN the workspace contains five runtime crates and private conformance
- WHEN Release Please 17.6.0 processes candidates
- THEN one synchronized version PR excludes conformance as a release candidate and performs no release/tag operation

#### Scenario: Unapproved private mutation

- GIVEN the Stage-A diff changes private package metadata, keys, paths, features, or content outside four approved pins
- WHEN Stage B validates the diff
- THEN it fails closed before mutation

### Requirement: Auditable carrier modes

Stage B MUST accept trusted `push` or `workflow_dispatch` on `refs/heads/main`. Manual dispatch MUST require boolean `dry_run`; push mode MUST accept only `true`, `false`, or unset. Both modes MUST validate identically. Dry-run MUST emit credential-free evidence and MUST NOT mutate refs, labels, releases, uploads, or registries.

#### Scenario: No matching Release Please PR

- GIVEN zero merged Release Please PRs match the effective event SHA
- WHEN correlation runs
- THEN the carrier exits successfully as skipped and records that mutation paths did not run

#### Scenario: Invalid or multiple matches

- GIVEN PR data is malformed or more than one matching PR exists
- WHEN correlation runs
- THEN it fails closed before diff fetch or mutation

#### Scenario: Manual dry-run

- GIVEN main is dispatched with `dry_run=true`
- WHEN validation completes
- THEN the canonical tag plan and skipped-mutation evidence are emitted without publication

### Requirement: Dry-run-only historical replay

The carrier MAY accept `replay_sha` only for manual main `dry_run=true`; it MUST be lowercase 40-hex. Replay MUST keep current-main checkout, use that SHA for lookup, emit both SHAs, and stop before mutations. Other contexts MUST fail closed.

#### Scenario: Authorized replay

- GIVEN current main is checked out and a valid replay SHA is supplied in manual dry-run mode
- WHEN identity resolves
- THEN lookup uses the replay SHA, source validation uses current main, and every write is skipped

### Requirement: Approved archives and ordered publication

The release MUST produce eight archives: Linux GNU/musl x86_64/aarch64, macOS x64/arm64, and Windows x64/arm64. Unix MUST use `tar.gz`, Windows `zip`, and every archive a lowercase SHA-256 sidecar verified before upload/extraction. Cargo dependencies precede dependents, npm platforms precede the wrapper, and OCI waits for architecture/runtime gates.

#### Scenario: Complete archive release

- GIVEN all approved targets build successfully
- WHEN assets are prepared
- THEN every target has one identifiable archive and verifying checksum

#### Scenario: Missing target or gate failure

- GIVEN any target, package, checksum, or metadata gate fails
- WHEN publication evaluates dependencies
- THEN later uploads and publishers do not run and evidence is retained

### Requirement: Secure non-atomic recovery

Publishing jobs MUST use least privilege and trusted OIDC where supported; tokens MUST NOT enter artifacts/logs. On failure, later publishers stop, history remains available, and recovery uses deprecation, retagging, superseding releases, or a later Cargo version rather than deletion.

#### Scenario: Partial publication

- GIVEN assets publish but npm or OCI publication fails
- WHEN the failure is recorded
- THEN later jobs stop, partial state is documented, and a corrected recovery path is identified
