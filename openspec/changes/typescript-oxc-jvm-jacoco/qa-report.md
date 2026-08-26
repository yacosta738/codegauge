# Acceptance QA Report: typescript-oxc-jvm-jacoco

## Identity

- Change: `typescript-oxc-jvm-jacoco`
- Mode: `openspec`
- QA phase: `qa`
- Date: `2026-08-26`
- Executor target: `/Users/acosta/Dev/agent-swarm/codegauge`

## Sources of Truth

- Proposal: `openspec/changes/typescript-oxc-jvm-jacoco/proposal.md`
- Specification: `openspec/changes/typescript-oxc-jvm-jacoco/spec.md`
- Design: `openspec/changes/typescript-oxc-jvm-jacoco/design.md`
- Tasks: `openspec/changes/typescript-oxc-jvm-jacoco/tasks.md`
- Technical verification: `openspec/changes/typescript-oxc-jvm-jacoco/verify-report.md`
- Repository contract: `README.md`, `openspec/config.yaml`
- Runtime acceptance sources: `crates/codegauge-cli/tests/cli.rs`,
  `crates/codegauge-provider-jacoco/tests/jacoco.rs`,
  `crates/codegauge-provider-typescript/tests/{api_probe.rs,provider.rs,typescript.rs}`,
  `crates/codegauge-conformance/tests/conformance.rs`, fixtures, schemas, and goldens.
- State was read but intentionally not changed: `state.yaml` still records `current_phase: verify`
  and `next: qa`, per the request not to modify state.

## Target and Environment

- Target: standalone public `codegauge` CLI; there is no browser UI, service API, or persistent
  application state in this repository.
- Local environment: macOS workspace, locked Rust workspace, Python contract scripts, Node/npm
  wrapper tests, `actionlint`, and Python `jsonschema` validation (`4.26.0`).
- Credentials and permissions: local read-only fixture execution only. No Cargo, npm, GitHub, or
  GHCR credential was used; no publication, upload, tag, release, or registry mutation was run.
- Runner status: `UNAVAILABLE`. No project-local `openspec/quality-runner.json` exists and the
  workspace `quality-runner/v1` manifest is disabled. QA therefore used explicit `fallback`
  shell/process execution; no deterministic runner/FSM envelope is claimed.
- Limitations: hosted publication and real cross-target/container release execution were not
  exercised. The worktree already contained the uncommitted change implementation; QA added only
  this report and did not edit source code or `state.yaml`.

## Capability Inventory

| Capability | Availability | Selected? | Rationale / rejection reason |
|---|---|---:|---|
| Public CLI execution through Cargo | available | Yes | Narrowest observable path for profiles, analysis, stdout/stderr, exits, and structured errors. |
| Rust workspace tests/check/format/Clippy | available | Yes | Local implementation and conformance gates are executable and locked. |
| Python contract/release/distribution scripts | available | Yes | Local release topology, provenance, carrier, and OCI synthetic evidence are executable. |
| JSON Schema and golden comparison | available | Yes | `jsonschema` validates result/error documents; timestamp-masked outputs are compared to checked-in goldens. |
| npm wrapper test | available | Yes | Local `npm test` builds and runs the six wrapper tests without publishing. |
| Workflow syntax validation | available | Yes | `actionlint .github/workflows/*.yml` is installed and runnable. |
| Configured SDD quality runner/FSM | unavailable | No | Both configured runner locations are unavailable/disabled; `fallback` limitation recorded above. |
| Browser, accessibility, responsive, and locale testing | rejected | No | No browser/UI surface or localization contract exists for this CLI-only change. |
| Persistence/data-store testing | rejected | No | The target reads explicit artifacts and does not own persistent state. |
| Hosted Cargo/npm registry publication | unavailable | No | Credentials and publication were intentionally not used. |
| Hosted GitHub Release and GHCR publication | unavailable | No | Hosted credentials/targets were intentionally not used; local fake-SCM/synthetic checks are not hosted acceptance. |
| Real Docker/QEMU cross-target execution | not established | No | No real image build, push, or cross-target artifact was required or attempted in this read-only QA run. |

## Scenario Matrix

Every applicable scenario below was executed with an observable CLI result or executable gate.
Error cases are successful QA scenarios when the required deterministic failure was observed.

| ID | Capability | Acceptance scenario | Result | Evidence or reason |
|---|---|---|---|---|
| CLI-01 | Public CLI | `cargo run --quiet --locked -p codegauge-cli -- profiles` lists the two supported profiles in order. | PASS | Exit `0`; stdout exactly `jvm-jacoco-v1\ntypescript-oxc-istanbul-v1\n`. |
| CLI-02 | Public CLI | `cargo run --quiet --locked -p codegauge-cli -- version` reports the release version. | PASS | Exit `0`; stdout exactly `codegauge 0.3.0\n`. |
| JVM-01 | Public CLI + schema validation | From the repository root: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --input coverage=fixtures/jacoco/valid-methods.xml --format json`. | PASS | Exit `6` is the expected `PARTIAL` fixture outcome; one newline-terminated JSON document on stdout and four diagnostic lines on stderr. Profile is `jvm-jacoco-v1`; 10 symbols; no `policy` field/text. |
| JVM-02 | Public CLI + provenance | Validate JVM CRAP, semantics, and exact-byte provenance from JVM-01. | PASS | `full()V` CRAP `7`, `zero()V` CRAP `12`, `partial(I)V` CRAP `8.323`; primary and role-tagged coverage digest is `6deddb631c24f78d5fe7eff07009a4d7c6714c2317689139bd4111e0cfd0bf2e`. |
| TS-01 | Public CLI + JSON Schema | From `crates/codegauge-conformance`, analyze with repeated inputs: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --input source=../../fixtures/typescript/valid.ts --format json`. | PASS | Exit `0`, `COMPLETE`, profile `typescript-oxc-istanbul-v1`, three symbols, one JSON document, and no stderr diagnostics. Result validated against `schemas/codegauge-result-v1.schema.json`. |
| TS-02 | Public CLI + provider semantics | Validate Oxc/McCabe and Istanbul statement measurements. | PASS | `outer` McCabe `2`, nested `inner` McCabe `1`, arrow McCabe `1`; statement coverage is outer `2/2`, inner `0/1`, arrow `1/1`; semantics are `typescript-oxc-mccabe-v1` and `istanbul-statement`. |
| TS-03 | Public CLI + ownership | Validate nested callable ownership rather than parent double-counting. | PASS | Outer owns two covered statements; nested `inner` owns its separate zero-hit statement. The nested statement is not counted in the outer coverage total. |
| TS-04 | Public CLI + golden/determinism | From `crates/codegauge-conformance`: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input source=../../fixtures/typescript/valid.ts --input coverage=../../fixtures/typescript/valid-coverage.json --format json`; validate schema, compare timestamp-masked output to the TypeScript golden, and compare both orderings. | PASS | Reordered invocation also exits `0`; both masked documents are identical and equal `tests/golden/typescript-valid.json`. Coverage digest is `dfaf31b9a0dcc1ab33d2d18d67e19f8081f348be4089a7415e003c2345cd1cff`; source digest is `5afdd4a3af7761ebaaa7f170894e2da151b33733224f02ccd34bfc900e9ae38a`. |
| NEG-01 | Public CLI + structured errors | From `crates/codegauge-conformance`, native Kover fixture without `COMPLEXITY`: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --input coverage=../../fixtures/jacoco/native-kover.xml --format json` (run twice). | PASS | Both exits `6`; both documents validate against the error schema and are identical: `INCOMPATIBLE_MEASUREMENTS`, path `../../fixtures/jacoco/native-kover.xml`, digest `098853054f0db7e6723962f2caccff9618c125daceffb4a85a29e70e26dbdafc`. No CRAP downgrade was produced. |
| NEG-02 | Public CLI + structured errors | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/raw-v8.json --input source=../../fixtures/typescript/valid.ts --format json`. | PASS | Both exits `5`; identical `INVALID_INPUT` documents with raw-V8 path and exact digest `d0716154525bfd25114329f7e6c461661e22c2a927ddd201151b29906b615aa7`. |
| NEG-03 | Public CLI + structured errors | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/malformed.json --input source=../../fixtures/typescript/valid.ts --format json`. | PASS | Both exits `5`; identical `INVALID_INPUT` documents with path `../../fixtures/typescript/malformed.json` and digest `acd78e89e0c65ba1d98397c9a8ae43a39d8bda642e9d1d2c2cecd4075180419f`. |
| NEG-04 | Public CLI + role validation | From `crates/codegauge-conformance`, run twice each: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --format json`; `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --format json`. | PASS | JVM: exit `5`, `missing required input: coverage`; TypeScript: exit `5`, `missing required input: source`; structured documents and stderr are deterministic. |
| NEG-05 | Public CLI + input availability | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --input source=../../fixtures/typescript/missing.ts --format json`. | PASS | Both exits `3`; identical `INPUT_NOT_FOUND` documents with path `../../fixtures/typescript/missing.ts`. |
| NEG-06 | Public CLI + duplicate role validation | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --input coverage=../../fixtures/typescript/valid-coverage.json --input source=../../fixtures/typescript/valid.ts --format json`. | PASS | Both exits `5`; identical `INVALID_INPUT`, message `duplicate input: coverage=../../fixtures/typescript/valid-coverage.json`. |
| NEG-07 | Public CLI + path correlation | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --input source=../../fixtures/typescript/tsx.tsx --format json`. | PASS | Both exits `5`; identical `INVALID_INPUT` with coverage path and digest `dfaf31b9a0dcc1ab33d2d18d67e19f8081f348be4089a7415e003c2345cd1cff`. |
| NEG-08 | Public CLI argument boundary | From `crates/codegauge-conformance`, run: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --input coverage --format json`; `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --input covrage=../../fixtures/jacoco/valid-methods.xml --format json`; `cargo run --quiet --locked -p codegauge-cli -- analyze --profile unknown-v1 --input coverage=../../fixtures/jacoco/valid-methods.xml --format json`; `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --input coverage=../../fixtures/jacoco/valid-methods.xml --format text`. | PASS | Exits/codes: `2/CLI_ERROR` for malformed assignment; `2/CLI_ERROR` for unknown role; `4/UNSUPPORTED_PROFILE`; `2/CLI_ERROR` for non-JSON format. |
| GATE-01 | Rust executable gates | `cargo test --workspace --locked`, `cargo check --workspace --locked`, `cargo fmt --all -- --check`, and `cargo clippy --workspace --all-targets --locked -- -D warnings`. | PASS | All exit `0`; workspace test output reports `59 passed, 0 failed, 0 ignored`; check, format, and Clippy are clean. |
| GATE-02 | Local workflow/docs gates | `actionlint .github/workflows/*.yml`; `python3 tests/bootstrap_checks.py`; `python3 tests/readme_checks.py`. | PASS | All exit `0`; actionlint has no diagnostics; bootstrap and README checks print `PASS`. |
| GATE-03 | Local release/distribution gates | `python3 tests/distribution_checks.py`; `python3 tests/release_provenance_tests.py`; `python3 tests/release_carrier_tests.py`; `python3 tests/release_carrier_mode_tests.py`; `python3 tests/release_carrier_static_tests.py`. | PASS | Each exits `0` and prints its corresponding `*_TESTS: PASS` result. These are local/static or copied-tree checks, not hosted publication. |
| GATE-04 | Release Please runtime | `python3 tests/release_please_runtime_tests.py`. | PASS | Exit `0`; exact Release Please `17.6.0` fake-SCM harness passes, reports `releaseCalls: 0`, `tagCalls: 0`, accepts the intended private pin update, and rejects private package-version/publish-flag/path mutations. Expected Release Please warnings are present. |
| GATE-05 | OCI local distribution gates | `python3 tests/oci_distribution_tests.py`; `python3 tests/oci_distribution_failure_tests.py`; `python3 tests/oci_distribution_static_tests.py`; `python3 tests/oci_distribution_evidence_tests.py`. | PASS | Each exits `0` and prints `PASS`; evidence is synthetic/static and does not claim a real image build or registry push. |
| GATE-06 | Local Python test suite | `python3 -m pytest -q tests/*_tests.py`. | PASS | Exit `0`; `23 passed in 6.07s`. |
| GATE-07 | Local npm wrapper | From `npm/codegauge`, `npm test`. | PASS | Exit `0`; TypeScript build completed and Node test runner reports `6` passed, `0` failed. No npm publish was performed. |
| GATE-08 | Additional local integrity gates | `cargo metadata --locked --format-version 1`; `git diff --check`. | PASS | Both exit `0`. |
| N/A-01 | Browser/accessibility/responsive/locale | No browser or UI target exists. | NOT TESTED | Non-applicable to the standalone CLI; no browser acceptance claim is made. |
| N/A-02 | Persistence/interruption/state transition | No persistent store or long-lived service state exists. | NOT TESTED | Non-applicable; repeated CLI invocations and reordered input determinism were exercised instead. |
| HOST-01 | Cargo/npm/GitHub Release/GHCR hosted paths | Registry publication, hosted release/tag/upload, and GHCR push. | NOT TESTED | Intentionally not run without hosted credentials and because publication was prohibited for this QA phase. Local release checks do not replace hosted acceptance. |

## Local Gate Results

The exact commands and results above are the local execution record. The following distinctions are
intentional:

- `python3 tests/distribution_checks_e3a.py` was also invoked and exited `0`, but produced no output
  because it is a support module without a standalone `__main__` runner; it is not counted as an
  independent pass.
- The configured quality runner was not used. All QA evidence is explicitly `fallback` evidence.
- Local Cargo/npm tests and synthetic OCI/release checks prove local contracts only; they do not
  prove registry, GitHub Release, GHCR, or cross-platform hosted operations.

## Untested Scope

| Scope | Reason | Re-run prerequisite |
|---|---|---|
| Cargo registry publication | No registry credentials; publication prohibited. | Authorized release window and Cargo registry credentials; run publish verification without changing profile/schema contracts. |
| npm registry publication | No npm credentials; publication prohibited. | Authorized release window and npm provenance/registry credentials; verify package resolution after publication. |
| GitHub Release/tag/carrier hosted execution | No hosted API/Actions execution was authorized. | Authorized repository access and a dry-run/rehearsal target; inspect hosted records before any live mutation. |
| GHCR publication and real image digest/runtime matrix | No registry credentials or real push; OCI evidence was synthetic/static. | Authorized GHCR target, Docker/QEMU/toolchain matrix, and immutable digest evidence for each architecture. |
| Browser, responsive, accessibility, locale, persistence | No such target surface exists in this CLI-only repository. | Not applicable unless a separate consumer application is added. |
| Configured quality runner/FSM | Runner manifest absent/disabled. | Enable and configure the project/workspace runner, then rerun QA preserving its envelope. |

## Findings

| ID | Severity | Scenario / location | Evidence | Status |
|---|---|---|---|---|
| QA-001 | P2 | Configured QA runner unavailable | `verify-report.md` records project runner `UNAVAILABLE` (no project manifest; workspace runner disabled); this report uses literal `fallback` execution. | Open warning; manual runtime evidence is complete but deterministic runner enforcement is unavailable. |
| QA-002 | P2 | Hosted Cargo/npm/GitHub Release/GHCR acceptance | No credentials or hosted mutation was used; local fake-SCM and synthetic OCI checks explicitly do not exercise registries or hosted release infrastructure. | Open acceptance gap; archive normally requires a credentialed rerun or an explicit policy exception. |
| QA-003 | P3 | Coverage measurement | `openspec/config.yaml` declares coverage unavailable and no tool/threshold is configured. | Accepted limitation; no coverage pass/fail claim is made. |
| QA-004 | P3 | Design-document freshness | `verify-report.md` notes the two resolved Oxc/Istanbul design questions remain unchecked in `design.md`. | Documentation warning; no observed CLI acceptance failure. |

No `CRITICAL`, `P0`, or `P1` finding was observed.

## Verdict

**PASS WITH WARNINGS**

### Rationale

The executable public CLI target produced the expected profile list, JVM JaCoCo measurements and
CRAP values, TypeScript Oxc/McCabe plus Istanbul statement coverage, deepest nested ownership,
provenance, schemas, goldens, deterministic reordered results, and deterministic structured
negative errors. All requested local Rust, workflow, documentation, release/distribution,
provenance/carrier, Release Please runtime, Python, OCI synthetic, and npm gates exited successfully.

The warnings are real acceptance boundaries: the configured QA runner is unavailable and hosted
Cargo/npm/GitHub Release/GHCR publication and real cross-target execution were not tested. This
is not a claim of hosted product acceptance or of acceptance for a future `agent-harness` consumer.

## Limitations and Handoff

- QA did not modify source code, fixtures, schemas, tests, or `state.yaml`; only this
  `qa-report.md` was written.
- No implementation fix is requested from the observed local behavior.
- Handoff for release/operator acceptance is the untested hosted scope in `Untested Scope`; do
  not infer hosted success from the local fake-SCM or synthetic OCI results.
- Archive policy: `verify-report.md` and this report now exist, but normal archive policy should
  **not** proceed yet because acceptance-relevant hosted paths are `NOT TESTED`. Re-run QA with an
  authorized hosted target or obtain an explicit archive exception with the warning visible. The
  QA verdict must remain `PASS WITH WARNINGS`; this report does not authorize archiving.
