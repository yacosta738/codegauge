# OCI Distribution Specification

## Purpose

Ship a reproducible, secure CodeGauge container for approved Linux architectures without changing
the executable's public behavior.

## Requirements

### Requirement: Explicit OCI identity and architecture approval

The approved OCI image is `ghcr.io/yacosta738/codegauge`, with `linux/amd64` and `linux/arm64` as
the initial architecture matrix. No other architecture MAY be claimed without an explicit decision
and build evidence.

#### Scenario: Approved OCI identity

- GIVEN the approved registry identity and credentials are configured in the release environment
- WHEN an image release is requested
- THEN only `ghcr.io/yacosta738/codegauge` is eligible for publication

#### Scenario: Unsupported architecture

- GIVEN a consumer requests an architecture outside the approved matrix
- WHEN image selection occurs
- THEN the channel rejects the request rather than serving an unverified image

### Requirement: Reproducible workspace image

The image build MUST use Rust/Cargo 1.97.1 and locked dependencies, build the explicit `codegauge`
binary from the complete Cargo workspace, and use a minimal runtime that runs as a non-root user
with reliable init and signal handling.

#### Scenario: Workspace-aware build

- GIVEN a clean checkout of the approved release revision
- WHEN the image is built for an approved architecture
- THEN it contains the intended `codegauge` binary and does not rely on a single-root-`src` layout

### Requirement: OCI provenance and behavior

Each published image MUST expose the released version and immutable source revision in OCI metadata,
record its immutable digest, and produce the same profile, schema, JSON, result/error, and exit
contracts as the release binary.

#### Scenario: Metadata mismatch

- GIVEN an image label or runtime version differs from release provenance
- WHEN image inspection runs
- THEN the image fails validation and is not added to the multi-architecture channel

### Requirement: Gated multi-architecture publication

Every approved architecture MUST build, inspect, and pass a runtime smoke check before a manifest or
channel tag is published. Tags MUST be derived from the approved release version and MUST NOT point
to an unverified or partially built image.

#### Scenario: One architecture fails

- GIVEN the `linux/arm64` build or smoke check fails
- WHEN the OCI publication graph evaluates
- THEN the manifest and later OCI tags are not published, and recovery evidence identifies the failed architecture
