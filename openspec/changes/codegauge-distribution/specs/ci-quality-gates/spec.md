# CI Quality Gates Specification

## Purpose

Provide deterministic, least-privilege checks that must pass before CodeGauge distribution or registry publication.

## Requirements

### Requirement: Pinned and least-privilege automation

CI MUST use Rust/Cargo 1.97.1, the committed `Cargo.lock`, and immutable full-SHA references for third-party actions. Pull-request jobs MUST be read-only, MUST NOT receive release credentials, and write permissions MUST be scoped to the job that requires them.

#### Scenario: Untrusted pull request

- GIVEN CI is triggered by a pull request
- WHEN the workflow starts
- THEN it runs without registry or release credentials and cannot publish artifacts

#### Scenario: Mutable action reference

- GIVEN a workflow action uses a mutable tag or non-immutable reference
- WHEN workflow validation runs
- THEN validation fails before any distribution job starts

### Requirement: Complete quality gate

The required gate MUST run locked metadata validation, workspace tests, formatting, Clippy with `-D warnings`, and both Python contract checks. A release MUST NOT proceed when a check fails, is skipped, or is replaced by a weaker command.

#### Scenario: All checks pass

- GIVEN the pinned toolchain and lockfile are available
- WHEN every required command succeeds
- THEN distribution preflight becomes eligible to run

#### Scenario: Contract or lint failure

- GIVEN any required Rust or Python check reports a failure
- WHEN the quality gate completes
- THEN the gate blocks all later release and publication jobs

### Requirement: Fail-closed distribution preflight

Before publication, automation MUST validate the approved target matrix, Cargo and npm metadata, package contents, checksums, OCI metadata, and version/source provenance. It MUST retain machine-readable or log evidence identifying the failed check and revision.

#### Scenario: Incomplete target evidence

- GIVEN a claimed target lacks a build, package, or checksum result
- WHEN preflight evaluates the matrix
- THEN it fails closed and no registry publisher is enabled

#### Scenario: Preflight failure

- GIVEN quality checks pass but distribution validation fails
- WHEN the release graph evaluates dependencies
- THEN later publishers remain blocked and failure evidence is retained
