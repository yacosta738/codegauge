# CI Quality Gates Specification

## Purpose

Provide deterministic, least-privilege checks that must pass before CodeGauge artifacts or registry
channels can be published.

## Requirements

### Requirement: Pinned and least-privilege automation

CI MUST use the repository-pinned Rust/Cargo 1.97.1 toolchain and committed `Cargo.lock`. Third-party
workflow actions MUST use immutable full-SHA references. Pull-request jobs MUST be read-only and MUST
NOT receive release credentials; write permissions SHALL be scoped to the job that needs them.

#### Scenario: Untrusted pull request

- GIVEN a workflow is triggered by a pull request
- WHEN the workflow starts
- THEN it runs without registry or release credentials and cannot publish artifacts

#### Scenario: Floating workflow dependency

- GIVEN a workflow action is referenced by a mutable tag
- WHEN the CI validation runs
- THEN the validation fails before any distribution job can start

### Requirement: Complete quality gate

The required gate MUST run `cargo metadata --locked`, locked workspace tests, format checking,
Clippy with `-D warnings`, and both Python contract checks. It MUST evaluate the merged Stage-A
tree after the root carrier's exact private conformance dependency-pin update. A release MUST NOT
proceed when a gate fails, is skipped, or is replaced by a weaker command.

#### Scenario: All baseline checks pass

- GIVEN the pinned toolchain and lockfile are available
- WHEN every required command succeeds
- THEN the quality gate is eligible to unlock distribution validation

#### Scenario: Existing lint failure

- GIVEN Clippy reports the known pre-existing deprecated `quick_xml` call
- WHEN the gate runs
- THEN CI reports a blocking failure and does not weaken the lint or silently change engine behavior

#### Scenario: Public version synchronization leaves private pins stale

- GIVEN the five public runtime Cargo packages and npm packages are synchronized to `0.2.0`
- AND the private conformance path dependencies remain at `^0.1.0`
- WHEN CI runs `cargo metadata --locked`
- THEN CI reports a blocking dependency-version failure before Stage-B tag, release, upload, or
  registry mutation

#### Scenario: Exact private pin exception is present

- GIVEN the private manifest changes only its four dependency `.version` fields to the synchronized
  runtime version
- WHEN the complete quality gate runs
- THEN locked metadata is eligible to pass while the private package version and non-publishability
  remain unchanged

#### Scenario: Effective Stage-A tree passes locked tests

- GIVEN the synchronized tree contains the typed golden update and exact README/contract marker
  replacements in addition to the public and private dependency version updates
- WHEN CI runs `cargo test --workspace --locked`
- THEN the conformance golden compares equal to the runtime tool version and the complete workspace
  suite passes before Stage-B tag or publication mutation

### Requirement: Distribution preflight evidence

Before publication, automation MUST validate the approved target matrix, Cargo/package metadata,
npm package contents, archive checksums, and OCI metadata. Each validation MUST leave logs or
machine-readable evidence sufficient to identify the failed channel and revision.

#### Scenario: Incomplete target declaration

- GIVEN a claimed target has no build and checksum evidence
- WHEN release preflight evaluates the matrix
- THEN preflight fails and no registry publisher is enabled

#### Scenario: Failed preflight

- GIVEN package validation fails after quality checks pass
- WHEN the release graph evaluates dependencies
- THEN later publication jobs remain blocked and the failure evidence is retained
