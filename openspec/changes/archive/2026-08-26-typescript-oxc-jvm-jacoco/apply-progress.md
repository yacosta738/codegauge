# Apply Progress: Foundation / Contracts + JVM / CLI + Oxc / McCabe + Istanbul Join + Integration

## Work unit

- Change: `typescript-oxc-jvm-jacoco`
- Slice: work units 1–5, tasks 1.1–1.3, 2.1–2.2, 3.1–3.5, 4.1–4.2, and 5.1
- Delivery: one working branch with sequential tested slices
- Branch: `fix/carrier-gh-token-guard`
- Position: 5 of 5; no stacked-PR topology

## Completed tasks

- [x] 1.1 Added RED contract coverage for typed inputs and verified the pinned Rust 1.97.1
  toolchain plus `cargo metadata --locked`.
- [x] 1.2 Added `InputRole` (`Coverage`, `Source`), `AnalysisInput`, deterministic input-role
  parsing, `InputSet`, cardinality validation, duplicate detection, and stable ordering.
- [x] 1.3 Generalized `CollectionRequest`, `MetricProvider`, provider descriptors, and
  `Analyzer` to use typed multi-input collections; added additive role-tagged provenance while
  preserving the legacy single-coverage path and CRAP/error behavior.
- [x] 2.1 Renamed the JVM JaCoCo profile to `JvmJacocoV1` / `jvm-jacoco-v1`, updated the JaCoCo
  descriptor and coverage requirement, rejected both legacy profile names and native Kover
  reports without `COMPLEXITY`, and refreshed the required schema/golden references.
- [x] 2.2 Changed the CLI to repeatable `--input ROLE=PATH` arguments with `ArgAction::Append`,
  `split_once('=')`, typed role parsing, deterministic syntax/duplicate/missing-input errors,
  and preserved JSON stdout plus stderr diagnostics and exit mappings.
- [x] 3.1 Added `codegauge-provider-typescript` to the workspace with exact Oxc `0.147.0`
  dependencies, generated the locked dependency graph, and added the parser compile seam.
- [x] 3.2 Added Oxc-backed parsing and callable discovery for functions, arrows, class/object
  methods, constructors, getters, and setters with normalized paths, UTF-8 byte spans, and
  span-based TypeScript identities.
- [x] 3.3 Added classic McCabe v1 traversal with the specified decision increments and excluded
  nested callable bodies from parent complexity.
- [x] 3.4 Added strict Istanbul `FileCoverage`/bundle parsing for `path`, `statementMap`, and `s`,
  rejected raw V8 and malformed coverage, ignored function/branch hit maps, and added deepest
  callable ownership with duplicate-span detection and omission of statements outside callables.
- [x] 3.5 Added canonical source/coverage path correlation, one-to-one path validation, line/column
  conversion to Oxc UTF-8 byte spans, typed callable observations, and deterministic rejection of
  invalid, duplicate, ambiguous, and unmatched inputs.
- [x] 4.1 Registered the TypeScript profile in the application/CLI path, emitted dynamic profile
  provenance and role-tagged `provenance.inputs`, and synchronized the checked-in result schema
  without changing the error schema or CRAP semantics.
- [x] 4.2 Added TypeScript fixtures, hostile/reordered/TSX conformance vectors, and the stable
  `typescript-valid.json` golden; verified IDs, digests, profile output, statuses, and exits.
- [x] 5.1 Updated README, release/static contract checks, and canonical profile references; ran the
  full Rust, Python, formatting, Clippy, check, and diff verification suite.

## TDD evidence

- RED: `cargo test -p codegauge-model -p codegauge-application --locked` failed before
  implementation because `AnalysisInput`, `InputRole`, `Provenance.inputs`, and `InputSet` did
  not exist.
- RED refinement: the normalized duplicate-path and pre-I/O required-role tests failed against
  the first implementation, proving both tests exercised real behavior.
- GREEN: focused model/application/JaCoCo tests pass after the minimum implementation.
- REFACTOR: formatted model/provider changes, kept only typed path/slice/vector input adapters,
  and passed focused Clippy with `-D warnings`.
- JVM/CLI RED: `cargo test -p codegauge-model -p codegauge-application -p codegauge-provider-jacoco
  -p codegauge-conformance -p codegauge-cli --locked` first failed because the new contract tests
  referenced the absent `JVM_JACOCO_V1` constant and `ProfileId::JvmJacocoV1` variant.
- JVM/CLI GREEN: the same focused command passed after the profile rename, typed CLI parser, native
  Kover incompatibility fixture, schema, and golden updates were implemented.
- JVM/CLI REFACTOR: `cargo fmt --all -- --check`, focused Clippy with `-D warnings`, and
  `git diff --check` pass.
- Oxc RED: `cargo test -p codegauge-provider-typescript --test api_probe --locked` first failed
  because the new crate had no parser module.
- Oxc GREEN: the compile seam passed after adding the pinned parser adapter; the TypeScript
  fixture suite initially exposed an incorrect test slice length, then passed after correcting
  the test expectation.
- Callable RED: `cargo test -p codegauge-provider-typescript --test typescript --locked` first
  failed because the callable module was absent.
- Callable GREEN: parser/callable fixtures passed after the Oxc visitor implementation, including
  normalized paths, UTF-8 byte offsets, function/arrow/class-object method/ctor/get/set kinds,
  and unique span identities.
- McCabe RED: the same TypeScript fixture suite first failed because the complexity module was
  absent.
- McCabe GREEN/REFACTOR: classic decision-count and nested-exclusion cases passed; formatting and
  the focused Clippy run pass with `-D warnings`.
- Istanbul RED: `cargo test -p codegauge-provider-typescript --test typescript --locked` first
  failed because the Istanbul, ownership, and correlation modules were absent.
- Istanbul GREEN: the same focused suite passed after adding strict `statementMap`/`s` parsing,
  deepest ownership, normalized path joins, and typed observations.
- Istanbul REFACTOR: fixed the Oxc/UTF-16-to-UTF-8 coordinate conversion, added zero-line and
  out-of-range boundary cases, and passed focused formatting and Clippy with `-D warnings`.

## Verification

- `cargo test -p codegauge-model -p codegauge-application -p codegauge-provider-jacoco --locked`:
  PASS (model, application, and 9 existing JaCoCo integration tests).
- `cargo fmt --all -- --check`: PASS.
- `cargo metadata --locked --format-version 1`: PASS.
- `cargo clippy -p codegauge-model -p codegauge-application -p codegauge-provider-jacoco
  --all-targets --locked -- -D warnings`: PASS.
- Narrow compatibility check `cargo check -p codegauge-cli -p codegauge-conformance --locked`:
  PASS.
- Existing JaCoCo conformance check `cargo test -p codegauge-conformance --locked`: PASS (6
  conformance tests, including schema and golden compatibility).
- Current focused verification `cargo test -p codegauge-model -p codegauge-application
  -p codegauge-provider-jacoco -p codegauge-conformance -p codegauge-cli --locked`: PASS (8 model,
  9 application, 10 JaCoCo, 8 conformance, and 4 CLI integration tests, plus doc tests).
- Current focused Clippy `cargo clippy -p codegauge-model -p codegauge-application
  -p codegauge-provider-jacoco -p codegauge-conformance -p codegauge-cli --all-targets --locked
  -- -D warnings`: PASS.
- `cargo fmt --all -- --check`: PASS after the JVM/CLI slice.
- `cargo test -p codegauge-provider-typescript --locked`: PASS (compile seam, 3 TypeScript
  fixture tests, and doc tests).
- `cargo check -p codegauge-provider-typescript --locked`: PASS with all six Oxc crates pinned to
  `0.147.0` under Rust `1.97.1`.
- `cargo metadata --locked --format-version 1`: PASS; the new TypeScript provider is present in
  the locked workspace graph.
- `cargo clippy -p codegauge-provider-typescript --all-targets --locked -- -D warnings`: PASS.
- `cargo fmt --all -- --check`: PASS after the Oxc/McCabe slice.
- `git diff --check`: PASS.
- Focused compatibility command covering the new provider plus model/application/JaCoCo,
  conformance, and CLI crates: PASS.
- `cargo test -p codegauge-provider-typescript --locked`: PASS (compile seam and 10 TypeScript
  parser/callable/complexity/Istanbul/correlation tests, plus doc tests).
- `cargo check -p codegauge-provider-typescript --locked`: PASS.
- `cargo clippy -p codegauge-provider-typescript --all-targets --locked -- -D warnings`: PASS.
- `cargo fmt --all -- --check`: PASS after the Istanbul join slice.
- `cargo metadata --locked --format-version 1`: PASS with `serde_json` and all six Oxc crates
  pinned in the workspace graph.
- `git diff --check`: PASS after the Istanbul join slice.
- Focused compatibility command
  `cargo test -p codegauge-model -p codegauge-application -p codegauge-provider-jacoco
  -p codegauge-conformance -p codegauge-cli --locked`: PASS.
- Integration RED: application, CLI, schema, and conformance tests initially failed because the
  TypeScript profile constant/variant, provider registration, golden, and TSX fixture were absent.
- Integration GREEN/REFACTOR: those tests passed after registration, dynamic profile serialization,
  role provenance, fixtures/golden, and TSX coverage were added; formatting and focused checks pass.
- Full verification: `cargo test --workspace --locked` PASS (all workspace tests and doc tests);
  `cargo fmt --all -- --check` PASS; `cargo clippy --workspace --all-targets --locked -- -D warnings`
  PASS; `cargo check --workspace --locked` PASS; `git diff --check` PASS.
- Static verification: `python3 tests/bootstrap_checks.py` PASS; `python3 tests/readme_checks.py`
  PASS; `python3 -m pytest -q tests/oci_distribution_static_tests.py tests/oci_distribution_evidence_tests.py
  tests/release_provenance_tests.py` PASS (5 tests).

## Corrective release synchronization

- [x] Added the publishable `codegauge-provider-typescript` crate to the Release Please package
  graph, linked-version group, checked-in manifest, Cargo.lock selector, dependency-version
  selectors, build order, and publish order; retained `codegauge-conformance` as private.
- [x] Added the provider's five private-conformance version pins and synchronized strict validator,
  carrier, distribution, provenance, and Release Please runtime expectations.
- [x] Added `tests/golden/typescript-valid.json` as a typed root release carrier so future linked
  releases update the TypeScript golden's `tool.version` together with the existing golden.
- [x] Corrected proposal/spec role scope to current v1 `coverage`/`source` only; no speculative
  production roles or policy behavior were introduced.

### Corrective TDD evidence

- RED: `test_publishable_typescript_provider_is_in_release_graph` failed because the provider
  package path was absent from the Release Please graph.
- GREEN: the graph/config/workflow/validator/runtime updates made the focused provenance and
  Release Please tests pass.
- RED refinement: carrier fixtures exposed stale four-pin private hunks, old manifest hunk counts,
  and historical golden/version assumptions; each failure was fixed with dynamic counts and the
  provider-aware fixture data.
- REFACTOR: added the TypeScript golden to the typed root carrier, made copied-release fixtures
  normalize from the checked-in version, and preserved strict patch-count/content assertions.

### Corrective verification

- `python3 tests/release_carrier_tests.py`: PASS.
- `python3 tests/release_please_runtime_tests.py`: PASS; expected Release Please warnings are
  emitted by the read-only fake-SCM harness before the final pass summary.
- `python3 -m pytest -q tests/release_provenance_tests.py tests/release_please_runtime_tests.py
  tests/oci_distribution_static_tests.py tests/oci_distribution_evidence_tests.py`: PASS (8 tests).
- `python3 tests/distribution_checks_e3a.py`: PASS.
- `python3 tests/bootstrap_checks.py && python3 tests/readme_checks.py`: PASS.
- `cargo test --workspace --locked`: PASS; `cargo fmt --all -- --check`: PASS;
  `cargo clippy --workspace --all-targets --all-features --locked -- -D warnings`: PASS;
  `cargo check --workspace --all-targets --all-features --locked`: PASS; `git diff --check`: PASS.

## Boundary and remaining work

- Remaining: none in the assigned implementation slice. Historical old-profile references may
  remain in proposal/design/exploration artifacts; runtime and release contract references were
  updated to the canonical names. Release graph synchronization now includes the TypeScript
  provider and both typed goldens.
- `state.yaml` was intentionally not modified; the orchestrator owns phase state.

## Corrective SDD apply slice: release ownership and workflow blockers

- [x] Corrected the three JaCoCo provider indentation errors in
  `.github/workflows/release-publish.yml` without changing job order or publish commands.
- [x] Updated `tests/release_provenance_tests.py` to use canonical version `0.3.0`, require
  `gh release view` and `gh release upload`, reject `gh release create`, and verify that
  `skip-github-release` is owned by parsed `release-please-config.json` rather than inline
  `.github/workflows/release-please.yml` text.
- [x] Updated `tests/distribution_checks_e3a.py` to require the config/manifest markers while
  rejecting an inline workflow `skip-github-release` marker; `distribution_checks.py` now passes
  alongside `release_carrier_static_tests.py`.

### Corrective TDD evidence

- RED: `actionlint .github/workflows/*.yml` failed on the JaCoCo provider indentation and reusable
  workflow loading; `python3 tests/release_provenance_tests.py` failed because the fixture expected
  `0.2.0`; `python3 tests/distribution_checks.py` failed because it required an inline
  `skip-github-release: true` marker.
- GREEN: the minimum indentation, version/ownership assertion, and config-owned distribution
  check changes made all four corrective checks pass.
- REFACTOR: preserved strong negative assertions for release creation and inline config markers;
  no release graph, publish behavior, profile semantics, or production code was changed.

### Corrective verification

- `actionlint .github/workflows/*.yml`: PASS.
- `python3 tests/release_provenance_tests.py`: PASS (`RELEASE PROVENANCE TESTS: PASS`).
- `python3 tests/distribution_checks.py`: PASS (`DISTRIBUTION CHECKS: PASS`).
- `python3 tests/release_carrier_static_tests.py`: PASS.
- `python3 -m pytest -q tests/release_provenance_tests.py tests/release_please_runtime_tests.py
  tests/oci_distribution_static_tests.py tests/oci_distribution_evidence_tests.py`: PASS (8 tests).
- `cargo test --workspace --locked`: PASS (all workspace tests and doc tests).
- `cargo fmt --all -- --check`: PASS.
- `cargo clippy --workspace --all-targets --locked -- -D warnings`: PASS.
- `cargo check --workspace --locked`: PASS.
- `python3 tests/bootstrap_checks.py`: PASS.
- `python3 tests/readme_checks.py`: PASS.
- `git diff --check`: PASS.

### Corrective boundary

- No changes were made to `state.yaml`.
- No Oxc/Istanbul/JVM/model code, profile semantics, CRAP core, release graph membership, or new
  release behavior was introduced.
