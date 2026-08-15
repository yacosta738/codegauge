# Cargo and Source Distribution Specification

## Purpose

Define a safe crates.io and source installation channel without exposing an incomplete workspace
graph or changing RFC-0001 behavior by accident.

## Requirements

### Requirement: Explicit Cargo publication model

The approved Cargo model is coordinated crates.io publication of the complete runtime graph, with
source/Git installation retained as a fallback. The system MUST NOT publish the virtual workspace
root by assumption, omit required runtime dependencies, or publish a crate without complete
metadata and package-content validation. Public documentation MUST state both supported install
paths and the dependency publication order.

#### Scenario: Approved registry graph

- GIVEN the approved runtime graph has complete metadata and registry versions for local dependencies
- WHEN a release is prepared
- THEN crates are packaged and published in dependency order before the binary crate is published

#### Scenario: Source fallback remains available

- GIVEN a user cannot or does not want to use crates.io
- WHEN a user installs from the repository or an immutable Git revision
- THEN the explicit `codegauge` binary builds with the pinned locked workspace and the same contracts

### Requirement: Reproducible source installation

Source builds MUST use Rust/Cargo 1.97.1, the committed lockfile, and the existing inward-only
`model -> core -> application -> provider -> CLI` dependency direction. Source installation MUST
produce the `codegauge` binary and MUST preserve profile, schema, JSON, result/error, and exit
contracts.

#### Scenario: Immutable source install

- GIVEN a user selects a recorded Git revision
- WHEN the source installation completes
- THEN `codegauge version`, `profiles`, and analysis behavior match the released contracts

### Requirement: Private conformance dependency alignment

The private `codegauge-conformance` crate MUST remain a workspace/build-test member with its own
private package version and `publish = false`. When the public runtime graph advances to `X.Y.Z`,
its four path dependency `.version` fields for application, core, model, and provider-jacoco MUST
also resolve to `X.Y.Z` before the merged tree reaches Stage-B. The root metadata carrier owns those
four pin updates; it MUST NOT synchronize the private `[package].version` or publish the crate.

#### Scenario: Stale private pins block the locked graph

- GIVEN public runtime manifests and `Cargo.lock` resolve to `0.2.0`
- AND `crates/codegauge-conformance/Cargo.toml` still requires its four path dependencies at
  `^0.1.0`
- WHEN `cargo metadata --locked` runs on the merged tree
- THEN the quality gate fails before any canonical tag or distribution publisher is enabled

#### Scenario: Corrected private pins preserve non-publishability

- GIVEN the root carrier changes only the four private dependency version fields to `0.2.0`
- WHEN `cargo metadata --locked` and the workspace tests run
- THEN the graph resolves, the conformance package remains `0.1.0` and `publish = false`, and no
  Cargo publication candidate is created for it

#### Scenario: Synchronized effective tree runs the complete workspace suite

- GIVEN the effective Stage-A updates set the public runtime and the four private dependency pins to
  `0.2.0`
- AND the root typed/annotated carriers update the golden and contract tool-version expectations
- WHEN `cargo test --workspace --locked` runs on the synchronized tree
- THEN every workspace test passes while the conformance package remains private at version `0.1.0`

### Requirement: RFC-0001 compatibility boundary

Distribution work MUST NOT alter the RFC-0001 engine algorithms, profile or schema identifiers,
fixture/golden semantics, canonical JSON, structured error documents, or public exit mapping. Only
the synchronized release-version value MAY change as part of version provenance.

#### Scenario: Distribution-only change

- GIVEN a release updates manifests, wrappers, workflows, or image packaging
- WHEN contract checks compare the release with the baseline
- THEN engine behavior and public result/error contracts remain unchanged

### Requirement: Publishable package integrity

If crates.io is approved, every published runtime crate MUST have complete metadata, registry
versions for publishable local dependencies, and an intentional package contents rule. A package
MUST NOT be published when its build or declared tests require repository fixtures, schemas, or
goldens that are absent from the package.

#### Scenario: Cargo package is incomplete

- GIVEN `cargo package` or its dry-run detects an unavailable required file
- WHEN the registry gate runs
- THEN publication stops before the affected crate is uploaded

### Requirement: Version provenance and registry failure handling

The released version MUST be consistent across relevant Cargo manifests, `Cargo.lock`, and
`codegauge version`. Registry publication, when enabled, MUST follow dependency order and stop on
the first failure; an already published Cargo version MUST be treated as non-deletable and corrected
with a later version.

#### Scenario: Version mismatch

- GIVEN a manifest or binary reports a different release version
- WHEN release validation compares provenance
- THEN Cargo publication and dependent channels are blocked
