# Release Recovery Specification

## Purpose

Define safe, authenticated recovery of a merged release into one canonical Git tag, GitHub Release, and ordered publication pipeline. The contract covers normal automation, explicit recovery, no-write validation, identity/provenance, and rollback without changing CodeGauge semantics.

## Requirements

### Requirement: Single canonical release owner

Release Please MUST be the sole creator and owner of canonical `vX.Y.Z` tags and GitHub Releases. Publication workflows MUST consume an existing canonical release and MUST NOT create fallback tags or releases.

#### Scenario: Release Please creates the release

- GIVEN a merged version change is eligible for release
- WHEN Release Please processes the merge
- THEN it creates or updates the canonical tag and GitHub Release
- AND downstream workflows only consume that identity

#### Scenario: Publication cannot backfill ownership

- GIVEN a publication workflow starts without a canonical tag or release
- WHEN it resolves release inputs
- THEN it fails closed
- AND it performs no tag, release, package, or image creation

### Requirement: Explicit recovery is dry-run-first and authenticated

Recovery MUST require explicit authorization, exact repository and merged-main SHA inputs, and a successful dry run before live writes. Dry run MUST validate intended identities, synchronized versions, manifests, and available publication artifacts without external writes.

#### Scenario: Dry run validates an eligible merge

- GIVEN the merged-main commit, expected version, and authorized recovery request match
- WHEN recovery runs in dry-run mode
- THEN it reports the canonical tag, release, and publication plan
- AND it creates no external resource

#### Scenario: Identity mismatch fails closed

- GIVEN the requested SHA, repository, version, tag, or release identity does not match
- WHEN recovery preflight runs
- THEN recovery fails deterministically
- AND no external write is attempted

### Requirement: Recovery is idempotent and reconciles existing resources

A repeated authorized recovery MUST converge on exactly one canonical tag and GitHub Release for the same immutable main SHA. Existing matching resources MAY be reconciled; conflicting resources MUST stop the operation without deletion or replacement.

#### Scenario: Repeated recovery is a no-op

- GIVEN a canonical tag and release already point to the expected SHA and version
- WHEN authorized recovery is rerun
- THEN it reports success without creating duplicates
- AND downstream publication is dispatched at most once per release identity

#### Scenario: Conflicting resource blocks recovery

- GIVEN the canonical tag or release exists with a different SHA or version
- WHEN recovery reconciles resources
- THEN it fails closed
- AND it does not delete the existing tag or release

### Requirement: Provenance and ordered publication are enforced

The pipeline MUST verify immutable SHA provenance, synchronized Cargo/npm/container versions, manifests, and checksums before publication. It MUST publish in the defined Cargo, npm, then OCI/image order, stopping downstream stages after any failure.

#### Scenario: Verified artifacts publish in order

- GIVEN all versions, manifests, checksums, and provenance match
- WHEN the canonical release dispatches publication
- THEN Cargo completes before npm and npm before OCI/image publication
- AND each published artifact records the canonical version and SHA

#### Scenario: Verification failure prevents publication

- GIVEN any provenance, version, manifest, checksum, or package-content check fails
- WHEN the release pipeline reaches its gate
- THEN publication is blocked
- AND no later registry or image write occurs

### Requirement: Recovery supports safe rollback

Recovery and publication MUST preserve existing tags and releases. On partial publication, the system MUST stop downstream jobs, inventory immutable outputs, and use target deprecation or rollback procedures without minting a new identity or committing credentials.

#### Scenario: Partial publication is halted

- GIVEN an earlier target has published and a later target fails
- WHEN failure handling runs
- THEN later publication stages stop
- AND immutable published outputs and rollback actions are recorded
