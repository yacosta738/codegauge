# Cargo Distribution Specification

## Purpose

Define safe Cargo registry and immutable source installation without exposing an incomplete workspace or changing RFC-0001 behavior.

## Requirements

### Requirement: Explicit Cargo publication model

The approved Cargo model MUST publish the complete public runtime graph in dependency order, with immutable source/Git installation as fallback. The virtual workspace root and private conformance crate MUST NOT be published. Public documentation MUST state both install paths and publication order.

#### Scenario: Registry graph is complete

- GIVEN publishable runtime crates have complete metadata and registry-resolvable local dependencies
- WHEN a release is prepared
- THEN packages are validated and published in dependency order before the binary crate

#### Scenario: Source fallback

- GIVEN a user selects the repository or an immutable Git revision
- WHEN source installation runs with the pinned locked workspace
- THEN it produces the explicit `codegauge` binary and the released contracts

### Requirement: Private conformance alignment

`codegauge-conformance` MUST remain a workspace/build-test member with its private package version and `publish = false`. When public runtime version `X.Y.Z` advances, exactly its four path dependency version fields MUST resolve to `X.Y.Z`; its package version, identity, publication state, and other content MUST remain unchanged.

#### Scenario: Stale private pins

- GIVEN public runtime manifests and the lockfile resolve to `X.Y.Z`
- AND the four conformance path pins remain on an older runtime version
- WHEN locked metadata runs
- THEN the gate fails before tagging or publication

#### Scenario: Corrected pins

- GIVEN only the four approved conformance dependency versions change to `X.Y.Z`
- WHEN metadata and workspace tests run
- THEN the graph passes, conformance remains private, and no publication candidate is created

### Requirement: Publishable package integrity

Each published runtime crate MUST have complete metadata, registry versions for local dependencies, and intentional package contents. A package MUST NOT publish if packaging or its declared tests require files absent from the package.

#### Scenario: Incomplete package

- GIVEN a package dry-run detects a missing required file or dependency
- WHEN the registry gate runs
- THEN that crate is not uploaded and dependent publication remains blocked

### Requirement: RFC-0001 compatibility and provenance

Distribution changes MUST NOT alter engine algorithms, profiles, schemas, fixtures, golden semantics, canonical JSON, structured errors, or exit mapping. Relevant manifests, lockfile, and `codegauge version` MUST report one release version. Cargo publication MUST stop on first failure; published versions MUST be corrected by a later version rather than deleted.

#### Scenario: Distribution-only release

- GIVEN manifests, wrappers, workflows, or packaging are updated
- WHEN contract checks compare the release with baseline behavior
- THEN public engine and result/error contracts remain unchanged

#### Scenario: Version mismatch

- GIVEN any relevant Cargo manifest or binary reports a different version
- WHEN provenance validation runs
- THEN Cargo and dependent channels are blocked
