# OCI Distribution Specification

## Purpose

Ship a reproducible, secure CodeGauge container for approved Linux architectures without changing executable behavior.

## Requirements

### Requirement: Explicit OCI identity and architecture approval

The approved image MUST be `ghcr.io/yacosta738/codegauge`, initially for `linux/amd64` and `linux/arm64` only. Other architectures MUST NOT be claimed without explicit approval and build evidence.

#### Scenario: Approved image identity

- GIVEN approved registry identity and credentials are configured
- WHEN an image release is requested
- THEN only the approved image name is eligible for publication

#### Scenario: Unsupported architecture

- GIVEN a consumer requests an architecture outside the approved matrix
- WHEN image selection occurs
- THEN the channel rejects the request without serving an unverified image

### Requirement: Reproducible non-root workspace image

The image build MUST use Rust/Cargo 1.97.1 and locked dependencies, build the explicit `codegauge` binary from the complete workspace, and run it in a minimal non-root runtime with reliable signal handling.

#### Scenario: Workspace-aware build

- GIVEN a clean approved release revision
- WHEN an approved architecture image is built
- THEN it contains the intended binary and does not assume a root `src` layout

### Requirement: OCI provenance and behavior

Each image MUST expose release version and immutable source revision metadata, record its digest, and preserve profile, schema, JSON, result/error, and exit contracts.

#### Scenario: Metadata mismatch

- GIVEN image labels or runtime version differ from release provenance
- WHEN image inspection runs
- THEN the image fails validation and is excluded from the multi-architecture channel

### Requirement: Gated multi-architecture publication

Every approved architecture MUST build, inspect, and pass runtime smoke checks before a manifest or channel tag is published. Tags MUST derive from the approved release version and MUST NOT point to an unverified image.

#### Scenario: One architecture fails

- GIVEN an approved architecture build or smoke check fails
- WHEN OCI publication evaluates
- THEN the manifest and later OCI tags remain unpublished and recovery evidence identifies the architecture
