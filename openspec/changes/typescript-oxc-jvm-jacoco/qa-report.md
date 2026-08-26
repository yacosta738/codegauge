# Acceptance QA Report: typescript-oxc-jvm-jacoco

## Identity

- Change: `typescript-oxc-jvm-jacoco`
- Mode: `openspec`
- QA phase: `qa`
- Date: `2026-08-26`
- Executor target: `/Users/acosta/Dev/agent-swarm/codegauge`
- Tested revision: `9b43a65` on `fix/carrier-gh-token-guard` (tracking `origin` at QA start)
- Feature/follow-ups: `1b0776e`, `df8526c`, and `cb24e54`

## Sources of Truth

- Proposal: `openspec/changes/typescript-oxc-jvm-jacoco/proposal.md`
- Specification: `openspec/changes/typescript-oxc-jvm-jacoco/spec.md`
- Design: `openspec/changes/typescript-oxc-jvm-jacoco/design.md`
- Tasks: `openspec/changes/typescript-oxc-jvm-jacoco/tasks.md`
- Technical verification: `openspec/changes/typescript-oxc-jvm-jacoco/verify-report.md`
- Phase state: `openspec/changes/typescript-oxc-jvm-jacoco/state.yaml`
- Repository contract: `README.md`, `openspec/config.yaml`
- Runtime acceptance sources: `crates/codegauge-cli/tests/cli.rs`,
  `crates/codegauge-provider-jacoco/tests/jacoco.rs`,
  `crates/codegauge-provider-typescript/tests/{api_probe.rs,provider.rs,typescript.rs}`,
  `crates/codegauge-conformance/tests/conformance.rs`, fixtures, schemas, and goldens.
- `verify-report.md` hands off passing local technical gates, the disabled quality runner, unavailable
  coverage, and the hosted Release Please limitations. This report independently exercises the
  observable CLI and local operator/release contracts; it does not convert local evidence into
  hosted or consumer-application acceptance.

## Target and Environment

- Target: standalone public `codegauge` CLI plus checked-in release/distribution contract behavior.
  There is no browser UI, service API, or persistent application state in this repository.
- Environment: macOS, locked Rust workspace, Python contract scripts with `jsonschema`, Node/npm
  wrapper tests, `actionlint`, and local Cargo package verification.
- Permissions: read-only local fixture and fake-SCM execution. No Cargo/npm/GitHub/GHCR credential
  was used; no publication, upload, tag, release, push, or registry mutation was run.
- Runner: `UNAVAILABLE`. No project-local `openspec/quality-runner.json` exists and the workspace
  `quality-runner/v1` manifest is disabled. QA therefore used explicit `fallback` shell/process
  execution; no deterministic runner/FSM envelope is claimed for local gates.
- Worktree baseline: clean and synchronized with `origin/fix/carrier-gh-token-guard` before QA
  artifact updates. QA changed no source, fixtures, schemas, tests, or release configuration.
- Fixture invocation note: the TypeScript coverage fixture embeds `../../fixtures/...` path keys;
  the CLI acceptance commands therefore run from `crates/codegauge-conformance` so source and
  coverage paths agree. A root invocation with those unchanged fixture bytes is an expected path
  correlation rejection, not a product failure.

## Capability Inventory

| Capability | Availability | Selected? | Rationale / rejection reason |
|---|---|---:|---|
| Public CLI execution through Cargo | available | Yes | Narrowest observable path for profiles, analysis, stdout/stderr, exits, and structured errors. |
| Rust workspace tests/check/format/Clippy/metadata | available | Yes | Local implementation and conformance gates are executable and locked. |
| Targeted CLI/provider/conformance suites | available | Yes | Directly exercises the acceptance surfaces beyond the aggregate workspace test. |
| Python release/provenance/carrier/distribution/OCI suites | available | Yes | Local release topology and synthetic OCI evidence are executable without publishing. |
| JSON Schema and golden comparison | available | Yes | `jsonschema` validates result/error documents; timestamp-masked outputs are compared to checked-in goldens. |
| npm wrapper build/test/package dry-run | available | Yes | `npm test` and non-publishing package inspection are executable locally. |
| Workflow syntax validation | available | Yes | `actionlint .github/workflows/*.yml` is installed and runnable. |
| Local Cargo package verification | available | Yes | All seven workspace packages can be packaged and verified without publishing. |
| Configured SDD quality runner/FSM | unavailable | No | Both configured runner locations are unavailable/disabled; `fallback` limitation recorded above. |
| Current hosted Release Please/release carrier acceptance | unavailable | No | No safe workflow target for the unmerged post-fix graph was available; no hosted rerun was invented. |
| Browser, accessibility, responsive, and locale testing | rejected | No | No browser/UI surface or localization contract exists for this CLI-only change. |
| Persistence/data-store testing | rejected | No | The target reads explicit artifacts and does not own persistent state. |
| Hosted Cargo/npm registries, GitHub Release, and GHCR | unavailable | No | Credentials and mutation were intentionally unavailable/prohibited. |
| Unauthorized/security endpoint testing | rejected | No | No authenticated or remote endpoint exists; hostile input and path-correlation rejection were tested locally. |
| Real Docker/QEMU cross-target execution | unavailable | No | OCI checks are synthetic/static; no real image build or registry push was authorized. |

## Scenario Matrix

Every local applicable scenario below has an observable runtime result or executable gate. Error
cases are `PASS` when the specified deterministic rejection is observed. Hosted runner statuses
are preserved separately and are not rewritten as hosted acceptance.

| ID | Capability | Acceptance scenario | Result | Evidence or reason |
|---|---|---|---|---|
| CLI-01 | Public CLI | `cargo run --quiet --locked -p codegauge-cli -- profiles` lists the two supported profiles in order. | PASS | Exit `0`; stdout exactly `jvm-jacoco-v1\ntypescript-oxc-istanbul-v1\n`. |
| CLI-02 | Public CLI | `cargo run --quiet --locked -p codegauge-cli -- version` reports the release version. | PASS | Exit `0`; stdout exactly `codegauge 0.3.0\n`. |
| JVM-01 | Public CLI + schema validation | From `crates/codegauge-conformance`: analyze `jvm-jacoco-v1` with `coverage=../../fixtures/jacoco/valid-methods.xml`. | PASS | Exit `6` is the expected `PARTIAL` fixture outcome; one newline-terminated result JSON on stdout, four diagnostics on stderr, 10 symbols, no `policy`. Result validates against `codegauge-result/v1`. |
| JVM-02 | Public CLI + provenance | Validate JVM CRAP, semantics, and exact-byte provenance from JVM-01. | PASS | `full()V` CRAP `7`, `zero()V` CRAP `12`, `partial(I)V` CRAP `8.323`; primary and role-tagged coverage digest is `6deddb631c24f78d5fe7eff07009a4d7c6714c2317689139bd4111e0cfd0bf2e`. |
| TS-01 | Public CLI + JSON Schema | From `crates/codegauge-conformance`, analyze with repeated inputs: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --input source=../../fixtures/typescript/valid.ts --format json`. | PASS | Exit `0`, `COMPLETE`, profile `typescript-oxc-istanbul-v1`, three symbols, one JSON document, and no stderr diagnostics. Result validated against `schemas/codegauge-result-v1.schema.json`. |
| TS-02 | Public CLI + provider semantics | Validate Oxc/McCabe and Istanbul statement measurements. | PASS | `outer` McCabe `2`, nested `inner` McCabe `1`, arrow McCabe `1`; statement coverage is outer `2/2`, inner `0/1`, arrow `1/1`; semantics are `typescript-oxc-mccabe-v1` and `istanbul-statement`. |
| TS-03 | Public CLI + ownership | Validate nested callable ownership rather than parent double-counting. | PASS | Outer owns two covered statements; nested `inner` owns its separate zero-hit statement. The nested statement is not counted in the outer coverage total. |
| TS-04 | Public CLI + golden/determinism | Reorder `--input` arguments, mask timestamps, validate schema, and compare the result to the TypeScript golden. | PASS | Both orderings exit `0`; masked documents are identical and equal `tests/golden/typescript-valid.json`. Coverage digest `dfaf31b9a0dcc1ab33d2d18d67e19f8081f348be4089a7415e003c2345cd1cff`; source digest `5afdd4a3af7761ebaaa7f170894e2da151b33733224f02ccd34bfc900e9ae38a`. |
| NEG-01 | Public CLI + structured errors | From `crates/codegauge-conformance`, native Kover fixture without `COMPLEXITY`: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --input coverage=../../fixtures/jacoco/native-kover.xml --format json` (run twice). | PASS | Both exits `6`; both documents validate against the error schema and are identical: `INCOMPATIBLE_MEASUREMENTS`, path `../../fixtures/jacoco/native-kover.xml`, digest `098853054f0db7e6723962f2caccff9618c125daceffb4a85a29e70e26dbdafc`. No CRAP downgrade was produced. |
| NEG-02 | Public CLI + structured errors | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/raw-v8.json --input source=../../fixtures/typescript/valid.ts --format json`. | PASS | Both exits `5`; identical `INVALID_INPUT` documents with raw-V8 path and exact digest `d0716154525bfd25114329f7e6c461661e22c2a927ddd201151b29906b615aa7`. |
| NEG-03 | Public CLI + structured errors | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/malformed.json --input source=../../fixtures/typescript/valid.ts --format json`. | PASS | Both exits `5`; identical `INVALID_INPUT` documents with path `../../fixtures/typescript/malformed.json` and digest `acd78e89e0c65ba1d98397c9a8ae43a39d8bda642e9d1d2c2cecd4075180419f`. |
| NEG-04 | Public CLI + role validation | From `crates/codegauge-conformance`, run twice each: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --format json`; `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --format json`. | PASS | JVM: exit `5`, `missing required input: coverage`; TypeScript: exit `5`, `missing required input: source`; structured documents and stderr are deterministic. |
| NEG-05 | Public CLI + input availability | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --input source=../../fixtures/typescript/missing.ts --format json`. | PASS | Both exits `3`; identical `INPUT_NOT_FOUND` documents with path `../../fixtures/typescript/missing.ts`. |
| NEG-06 | Public CLI + duplicate role validation | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --input coverage=../../fixtures/typescript/valid-coverage.json --input source=../../fixtures/typescript/valid.ts --format json`. | PASS | Both exits `5`; identical `INVALID_INPUT`, message `duplicate input: coverage=../../fixtures/typescript/valid-coverage.json`. |
| NEG-07 | Public CLI + path correlation | From `crates/codegauge-conformance`, run twice: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile typescript-oxc-istanbul-v1 --input coverage=../../fixtures/typescript/valid-coverage.json --input source=../../fixtures/typescript/tsx.tsx --format json`. | PASS | Both exits `5`; identical `INVALID_INPUT` with coverage path and digest `dfaf31b9a0dcc1ab33d2d18d67e19f8081f348be4089a7415e003c2345cd1cff`. |
| NEG-08 | Public CLI argument boundary | From `crates/codegauge-conformance`, run: `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --input coverage --format json`; `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --input covrage=../../fixtures/jacoco/valid-methods.xml --format json`; `cargo run --quiet --locked -p codegauge-cli -- analyze --profile unknown-v1 --input coverage=../../fixtures/jacoco/valid-methods.xml --format json`; `cargo run --quiet --locked -p codegauge-cli -- analyze --profile jvm-jacoco-v1 --input coverage=../../fixtures/jacoco/valid-methods.xml --format text`. | PASS | Exits/codes: `2/CLI_ERROR` for malformed assignment; `2/CLI_ERROR` for unknown role; `4/UNSUPPORTED_PROFILE`; `2/CLI_ERROR` for non-JSON format. |
| GATE-01 | Rust executable gates | Aggregate and targeted Rust test suites pass. | PASS | `cargo test --workspace --locked`: exit `0`, 59 passed, 0 failed, 0 ignored. Targeted CLI `5`, JaCoCo `10`, TypeScript `12`, and conformance `12` tests also pass. |
| GATE-02 | Rust quality gates | Format, type-check, Clippy, and metadata remain clean and locked. | PASS | `cargo fmt --all -- --check`, `cargo check --workspace --locked`, `cargo clippy --workspace --all-targets --locked -- -D warnings`, and `cargo metadata --locked --format-version 1` all exit `0`; metadata reports 7 members and the TypeScript provider. |
| GATE-03 | Workflow/release Python gates | Bootstrap, README, distribution, release provenance/carrier/mode/static, and Release Please runtime checks pass. | PASS | All named scripts exit `0` and print their `PASS` summaries; fake-SCM Release Please `17.6.0` reports `releaseCalls: 0` and `tagCalls: 0`. |
| GATE-04 | OCI Python gates | OCI distribution, failure, static, and evidence suites pass without a registry push. | PASS | All four scripts exit `0` and print `OCI ... TESTS: PASS`; evidence is synthetic/static only. |
| GATE-05 | Python focused suite | `python3 -m pytest -q tests/*_tests.py` passes. | PASS | Exit `0`; `24 passed in 7.02s`. |
| GATE-06 | npm wrapper | From `npm/codegauge`, `npm test` builds TypeScript and runs wrapper tests. | PASS | Exit `0`; TypeScript build succeeds with the `cb24e54` Node-types fix and Node test runner reports `6` passed, `0` failed. |
| GATE-07 | npm distribution dry-run | `npm run pack:dry-run` inspects the base package without publishing. | PASS | Exit `0`; tarball contents are only `dist/index.js` and `package.json`; no publish occurred. |
| GATE-08 | Cargo distribution dry-run | `cargo package --workspace --locked` packages and verifies the workspace. | PASS | Exit `0`; all seven members packaged and verified. Expected warnings only note excluded integration tests; no crate was published. |
| GATE-09 | Workflow/integrity | `actionlint .github/workflows/*.yml` and `git diff --check` pass. | PASS | Both exit `0`; actionlint emits no diagnostics and no whitespace errors are reported. |
| HOST-RUN-01 | Hosted runner evidence | Historical carrier run `32939386068` reports its executed selection/mode path. | PASS | Runner status is `PASS` with reason `no-matching-release-please-pr`; it validated only mode/selection and skipped full Release Please PR/provenance validation. It is not full hosted acceptance. |
| HOST-RUN-02 | Hosted runner evidence | Historical replay run `32939482165` replays PR `#75`. | FAIL | Runner status is `FAILURE`, preserved as QA `FAIL`. First error was the existing changelog returned as `status: modified`; this was reproduced and corrected in `df8526c`. A historical replay also cannot represent the later graph containing the TypeScript provider. |
| HOST-CURRENT | Hosted acceptance | Execute full hosted validation against the fixed, post-provider graph. | NOT TESTED | No safe workflow target was available for the unmerged branch/graph; no post-fix hosted rerun is claimed or invented. |
| N/A-01 | Browser/accessibility/responsive/locale | No browser or UI target exists. | NOT TESTED | Non-applicable to the standalone CLI; no browser acceptance claim is made. |
| N/A-02 | Persistence/interruption/state transition | No persistent store or long-lived service state exists. | NOT TESTED | Non-applicable; repeated CLI invocations and reordered input determinism were exercised instead. |

## Local Gate Results

The exact commands and results above are the local execution record. The named Python
release/carrier/provenance/distribution/OCI suites were run from the repository root:

```text
python3 tests/bootstrap_checks.py
python3 tests/readme_checks.py
python3 tests/distribution_checks.py
python3 tests/release_provenance_tests.py
python3 tests/release_carrier_tests.py
python3 tests/release_carrier_mode_tests.py
python3 tests/release_carrier_static_tests.py
python3 tests/release_please_runtime_tests.py
python3 tests/oci_distribution_tests.py
python3 tests/oci_distribution_failure_tests.py
python3 tests/oci_distribution_static_tests.py
python3 tests/oci_distribution_evidence_tests.py
python3 -m pytest -q tests/*_tests.py
```

All commands exited `0`. `release_carrier_tests.py` includes the `df8526c` regression for a
modified generated changelog. `release_please_runtime_tests.py` intentionally uses fake SCM and
reports expected warnings; it made zero release/tag calls. Local Cargo/npm checks and synthetic
OCI/release checks prove local contracts only, not registry, GitHub Release, GHCR, or cross-target
hosted operations.

The targeted Rust commands were also run explicitly:

```text
cargo test --locked -p codegauge-cli --test cli
cargo test --locked -p codegauge-provider-jacoco --test jacoco
cargo test --locked -p codegauge-provider-typescript --tests
cargo test --locked -p codegauge-conformance --test conformance
```

They exited `0` with `5`, `10`, `12`, and `12` tests respectively.

## Hosted Evidence Ledger

| Run | Preserved runner status | QA mapping | Meaning |
|---|---|---|---|
| `32939386068` | `PASS` | `PASS` for the limited executed path | Reason `no-matching-release-please-pr`; only mode/selection was validated, so it is not full hosted acceptance. |
| `32939482165` | `FAILURE` | `FAIL` | Historical PR `#75` replay failed first on GitHub's `status: modified` changelog handling. `df8526c` fixes that representation locally; the historical replay is also stale relative to the later TypeScript-provider graph. No safe post-fix hosted rerun was claimed. |

## Untested Scope

| Scope | Reason | Re-run prerequisite |
|---|---|---|
| Full hosted Release Please/carrier acceptance on the current graph | Run `32939386068` skipped full validation; run `32939482165` is a failed historical replay and cannot represent the later provider graph. The workflow cannot be safely pointed at the unmerged post-fix branch for this phase. | An authorized workflow target that resolves the fixed branch/commit and current graph, or an explicit archive exception. Do not replay PR `#75` as a substitute. |
| Cargo registry publication | No registry credentials; publication prohibited. | Authorized release window and Cargo registry credentials; run publish verification without changing profile/schema contracts. |
| npm registry publication | No npm credentials; publication prohibited. | Authorized release window and npm provenance/registry credentials; verify package resolution after publication. |
| GitHub Release/tag/upload and carrier mutation | Hosted mutations were prohibited. | Authorized repository access and a safe dry-run/rehearsal target; inspect hosted records before any live mutation. |
| GHCR publication and real image digest/runtime matrix | No registry credentials or real push; OCI evidence was synthetic/static. | Authorized GHCR target, Docker/QEMU/toolchain matrix, and immutable digest evidence for each architecture. |
| Configured quality runner/FSM | Runner manifest absent/disabled. | Enable and configure the project/workspace runner, then rerun QA preserving its envelope. |
| Coverage measurement | `openspec/config.yaml` declares coverage unavailable and no tool/threshold is configured. | Add an approved coverage capability and threshold before making a coverage claim. |
| Browser, responsive, accessibility, locale, persistence | No such target surface exists in this CLI-only repository. | Not applicable unless a separate consumer application is added. |

## Findings

| ID | Severity | Scenario / location | Evidence | Status |
|---|---|---|---|---|
| QA-001 | P2 | Configured QA runner unavailable | `verify-report.md` records project runner `UNAVAILABLE` (no project manifest; workspace runner disabled); this report uses literal `fallback` execution. | Open warning; manual runtime evidence is complete but deterministic runner enforcement is unavailable. |
| QA-002 | P2 | Current hosted Release Please/carrier acceptance | `32939386068` skipped on `no-matching-release-please-pr`; `32939482165` failed as a historical PR replay and cannot model the later TypeScript graph. | Open acceptance gap; archive normally requires a safe hosted rerun or explicit policy exception. |
| QA-003 | P2 | Historical modified-changelog replay | `32939482165` first failed on GitHub's `status: modified` changelog representation; `df8526c` adds the regression and validator fix, and local carrier/provenance suites pass. | Resolved locally; hosted confirmation remains pending and is not represented as PASS. |
| QA-004 | P3 | Coverage measurement | `openspec/config.yaml` explicitly declares coverage unavailable. | Accepted limitation; no coverage pass/fail claim is made. |
| QA-005 | P3 | Design-document freshness | `verify-report.md` notes the two resolved Oxc/Istanbul design questions remain unchecked in `design.md`. | Documentation warning; no observed local CLI acceptance failure. |

No `CRITICAL`, `P0`, or `P1` finding was observed.

## Verdict

**PASS WITH WARNINGS**

### Rationale

All requested local executable gates passed: locked Rust tests, targeted CLI/provider/conformance
tests, format/check/Clippy/metadata, Cargo package verification, actionlint, release/carrier/
provenance/distribution/OCI Python suites, focused pytest, npm build/tests, and package dry-run.
The observable CLI produced the expected JVM and TypeScript results, provenance, schema/golden
matches, deterministic reordered output, and structured negative outcomes. The `df8526c` changelog
boundary fix and `cb24e54` TypeScript npm build fix are both covered by current local evidence.

Warnings remain material: the configured runner and coverage are unavailable; `32939386068` did
not execute full hosted validation; `32939482165` is a failed historical replay; and no hosted
registry/release/GHCR or cross-target operation was performed. This is not a claim of hosted
product acceptance or of acceptance for a future consumer application.

## Limitations and Handoff

- QA did not modify source code, fixtures, schemas, tests, workflows, or release configuration.
- QA writes this report and the phase state handoff only; no commit, push, tag, release, publication,
  or registry mutation is performed.
- No implementation fix is requested from the current local behavior. The changelog failure is
  already addressed by `df8526c`; the npm build issue is already addressed by `cb24e54`.
- Do not infer hosted success from the local fake-SCM, synthetic OCI, or historical run records.
- State advances to `qa -> archive` for lifecycle tracking, but normal archive policy should **not**
  proceed while `HOST-CURRENT` is `NOT TESTED`. Re-run QA with a safe authorized hosted target or
  obtain an explicit archive exception with this warning visible. The QA verdict remains
  `PASS WITH WARNINGS` and does not authorize archiving.
