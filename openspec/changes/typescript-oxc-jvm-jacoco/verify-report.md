# Verification Report

**Change**: `typescript-oxc-jvm-jacoco`
**Mode**: OpenSpec; `fallback` execution evidence because the configured quality runner is disabled
**Date**: 2026-08-25
**Working directory**: `/Users/acosta/Dev/agent-swarm/codegauge`

This is technical conformance verification only. It does not claim user/operator acceptance. The
next acceptance phase is `sdd-qa`; archive remains downstream of QA.

## Completeness

| Metric | Value |
|---|---:|
| Tasks total | 13 |
| Tasks complete | 13 |
| Tasks incomplete | 0 |

Tasks `1.1`–`5.1` are marked `[x]` in `tasks.md`. `apply-progress.md` records RED → GREEN →
REFACTOR evidence for the implementation and corrective release slices. `state.yaml` was not
modified; phase ownership remains with the orchestrator.

## Quality-runner status

| Manifest | Status | Reason |
|---|---|---|
| Project-local `openspec/quality-runner.json` | `UNAVAILABLE` | No project-local manifest exists. |
| Workspace `../openspec/quality-runner.json` | `UNAVAILABLE` | `quality-runner/v1` exists but `enabled: false`. |

The standalone runner was not used. All command evidence below is manual `fallback` evidence; no
deterministic runner envelope is claimed.

## Build, package, and test evidence

| Command | Exit | Parser/result | Status | Reason/evidence |
|---|---:|---|---|---|
| `cargo test --workspace --locked` | 0 | 59 passed, 0 failed, 0 ignored; doc tests passed | PASS | Workspace, model, core, application, JVM JaCoCo, TypeScript/Oxc, CLI, and conformance tests passed. |
| `cargo fmt --all -- --check` | 0 | No output | PASS | Formatting is clean. |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | 0 | Cargo finished successfully | PASS | No denied warnings. |
| `cargo check --workspace --locked` | 0 | Cargo finished successfully | PASS | All seven workspace members type-check. |
| `cargo metadata --locked --format-version 1` | 0 | JSON parsed; 7 workspace members; TypeScript provider present | PASS | Locked workspace graph is synchronized. |
| `actionlint .github/workflows/*.yml` | 0 | No diagnostics | PASS | All workflow YAML, including `release-publish.yml`, parses and validates. |
| Runtime `cargo package` preflight for model, core, application, JaCoCo, TypeScript, and CLI | 0 | Each package and verification completed | PASS | Local dependency patches were used to model the release-build package gate; expected test-exclusion warnings only. |
| `python3 tests/bootstrap_checks.py` | 0 | `BOOTSTRAP CHECKS: PASS` | PASS | Workspace boundary and dependency layering passed. |
| `python3 tests/readme_checks.py` | 0 | `README CHECKS: PASS` | PASS | Public contract fragments passed. |
| `python3 tests/distribution_checks.py` | 0 | `DISTRIBUTION CHECKS: PASS` | PASS | Release ownership and distribution topology passed. |
| `python3 tests/release_provenance_tests.py` | 0 | `RELEASE PROVENANCE TESTS: PASS` | PASS | Version, graph, private boundary, and provenance checks passed. |
| `python3 tests/release_carrier_tests.py` | 0 | `RELEASE CARRIER TESTS: PASS` | PASS | Carrier behavior passed. |
| `python3 tests/release_carrier_mode_tests.py` | 0 | `RELEASE CARRIER MODE TESTS: PASS` | PASS | Push/dispatch/replay mode checks passed. |
| `python3 tests/release_carrier_static_tests.py` | 0 | `RELEASE CARRIER STATIC TESTS: PASS` | PASS | Pinned actions, permissions, ownership, and publication boundaries passed. |
| `python3 tests/release_please_runtime_tests.py` | 0 | `RELEASE PLEASE V17.6.0 RUNTIME TESTS: PASS` | PASS | Read-only fake-SCM harness emitted expected warnings, made no release/tag mutations, and rejected private mutations. |
| `python3 tests/oci_distribution_tests.py` | 0 | `OCI DISTRIBUTION TESTS: PASS` | PASS | OCI workflow checks passed. |
| `python3 tests/oci_distribution_failure_tests.py` | 0 | `OCI DISTRIBUTION FAILURE TESTS: PASS` | PASS | Fail-stop and digest-drift checks passed. |
| `python3 tests/oci_distribution_static_tests.py` | 0 | `OCI DISTRIBUTION STATIC TESTS: PASS` | PASS | OCI build/publish topology passed. |
| `python3 tests/oci_distribution_evidence_tests.py` | 0 | `OCI DISTRIBUTION EVIDENCE TESTS: PASS` | PASS | Evidence validator checks passed. |
| `python3 -m pytest -q tests/*_tests.py` | 0 | 23 passed | PASS | Focused release, carrier, provenance, and OCI pytest suites passed. |
| `npm test` from `npm/codegauge` | 0 | TypeScript build and 6 Node tests passed | PASS | Wrapper resolution, passthrough, optional dependency, and musl rejection contracts passed. |
| `git diff --check` | 0 | No output | PASS | No whitespace errors. |
| `codegauge-core` diff/status audit | 0 | No tracked diff; worktree status clean | PASS | CRAP core remained untouched. |

### Coverage

Coverage is `UNAVAILABLE`, not a pass claim. `openspec/config.yaml` explicitly declares coverage
unavailable and configures no coverage tool or threshold.

## Spec compliance matrix

A scenario is marked compliant only where a covering runtime test passed.

| Requirement/scenario | Passing runtime evidence | Result |
|---|---|---|
| Typed collection — declared `coverage` and `source` inputs reach the provider with digests | Application typed-input/provenance tests; TypeScript provider and CLI integration tests | ✅ COMPLIANT |
| Deterministic errors — missing, duplicate, malformed, unavailable, and uncorrelatable inputs fail without downgrade | Application pre-I/O validation; CLI syntax/duplicate tests; JaCoCo and TypeScript hostile vectors | ✅ COMPLIANT |
| JVM report — canonical `jvm-jacoco-v1` measurements/provenance | Conformance golden/result tests and JaCoCo integration tests | ✅ COMPLIANT |
| Kover boundary — native Kover without `COMPLEXITY` produces no CRAP symbol | `native_kover_without_complexity_is_incompatible` | ✅ COMPLIANT |
| Oxc complexity — callable discovery, classic McCabe increments, and nested exclusion | Callable/span and `calculates_classic_mccabe_and_excludes_nested_callable_bodies` tests | ✅ COMPLIANT |
| Istanbul correlation — Istanbul-only `statementMap`/`s`, deepest ownership, path and span rules | Istanbul parser, raw-V8 rejection, ownership, path, UTF-16/UTF-8, boundary, and duplicate tests | ✅ COMPLIANT |
| CRAP core — central unchanged `crap-original-v1` calculation | Core formula tests, conformance formula/golden tests, and clean core audit | ✅ COMPLIANT |
| CLI contract — repeated `--input ROLE=PATH`, stable exits, stdout/stderr separation | Five CLI integration tests, including TypeScript multi-input invocation | ✅ COMPLIANT |
| Determinism/compatibility — stable ordering, digests, schema/goldens, reordered inputs | JVM repeatability, TypeScript reordered-input, schema, and golden tests | ✅ COMPLIANT |

**Scenario summary: 9/9 scenarios have passing runtime coverage.**

## Correctness review (spec first)

| Requirement | Status | Evidence |
|---|---|---|
| Typed `coverage`/`source` collection | ✅ Implemented | `InputRole`, `AnalysisInput`, `InputSet`, descriptor cardinality, deterministic sorting, duplicate detection, bounded reads, exact-byte SHA-256, and role-tagged provenance are present and tested. |
| Provider validation | ✅ Implemented | JVM requires exactly one coverage input; TypeScript requires exactly one coverage and one or more source inputs. |
| Canonical JVM profile and Kover boundary | ✅ Implemented | `JvmJacocoV1`/`jvm-jacoco-v1` is registered; legacy names reject; missing Kover `COMPLEXITY` is incompatible; README directs `useJacoco()` output to the JVM profile. |
| Oxc callable/McCabe semantics | ✅ Implemented | Exact Oxc `0.147.0` pins, syntactic traversal, span IDs, specified decision nodes, and nested-body exclusion are present and tested. |
| Istanbul parsing/correlation/ownership | ✅ Implemented | Strict `statementMap`/`s`, raw-V8 rejection, normalized one-to-one paths, UTF-16-to-UTF-8 conversion, deepest ownership, and deterministic invalid-input handling are present and tested. |
| CRAP/result/error contracts | ✅ Implemented | Core formula is unchanged; result/error schemas, canonical JSON, digests, timestamps, symbols, and statuses pass runtime conformance. |
| CLI behavior | ✅ Implemented | Repeatable typed inputs, exit mapping, stdout/stderr separation, and profile listing pass runtime tests. |
| Release graph and workflow ownership | ✅ Implemented | Publishable TypeScript provider is in Cargo, Release Please config/manifest, linked versions, lock selectors, package order, and publish order; actionlint and release checks pass. |

## Design coherence

| Design decision | Followed? | Evidence |
|---|---|---|
| Inward-only `model -> core -> application -> provider -> CLI` layering | ✅ Yes | Bootstrap checks and Cargo metadata passed; `codegauge-core` is unchanged and clean. |
| Only `Coverage`/`Source` are v1 roles | ✅ Yes | Corrected proposal/spec/design agree; model exposes only the two roles. |
| Additive role-tagged provenance with legacy primary coverage input | ✅ Yes | `provenance.input` remains primary and `provenance.inputs` records typed artifacts. |
| Exact Oxc crates and syntactic traversal | ✅ Yes | Six Oxc crates are pinned to `=0.147.0`; no rejected parser/runtime dependency was introduced. |
| Deepest ownership and UTF-16-to-UTF-8 correlation | ✅ Yes | Implementation and non-ASCII runtime tests agree. |
| CLI `--input ROLE=PATH` and stable exits | ✅ Yes | CLI integration tests and README checks pass. |
| Release graph covers publishable runtime crates while conformance stays private | ✅ Yes | Release provenance, carrier, runtime, distribution, package, and workflow checks pass. |
| Open design questions | ⚠️ Documentation drift only | `design.md` still leaves Istanbul-column and Oxc-API questions unchecked even though checked-in fixtures/API probes and all relevant tests pass. |

## Issues found

### Verdict table

Judge A is source/spec inspection; Judge B is runtime or executable audit evidence.

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Required Cargo, workflow, Python, focused pytest, npm, package, and diff gates pass | ✅ | ✅ | — | Confirmed |
| Specification scenarios lack covering runtime tests | ❌ | ❌ | — | None found; 9/9 covered |
| Quality runner is disabled; no deterministic runner envelope exists | ✅ | ✅ | WARNING | Confirmed; manual `fallback` evidence |
| Coverage tool/threshold is not configured | ✅ | ✅ | WARNING | Confirmed; no coverage claim made |
| Hosted Release Please/GitHub Release, Cargo registry, npm registry, Docker/GHCR, and credentials were not exercised locally | ✅ | ✅ | WARNING | Not tested; local/static evidence passes, operator/QA evidence remains required |
| Strict-TDD commit ordering is independently unverifiable in this uncommitted worktree | ✅ | ✅ | WARNING | Apply-progress records RED → GREEN → REFACTOR; standard verification used because no runner exists |
| Actual tracked diff is 2,051 changed lines while the task forecast marked 400-line budget risk High and selected one branch | ✅ | ✅ | WARNING | Review-load risk, not a technical conformance failure; delivery decision is recorded in `tasks.md`/`apply-progress.md` |
| `design.md` open-question checkboxes remain stale | ✅ | ❌ | SUGGESTION | Documentation drift; runtime/API evidence resolves both questions |

### CRITICAL

None.

### WARNING

- Quality-runner enforcement was unavailable, so this report uses manual `fallback` evidence.
- Coverage is not configured; no coverage pass/fail claim is made.
- Hosted registry, GitHub Release, Docker/GHCR, and credential-backed publication paths require
  `sdd-qa`/operator acceptance evidence and were not run locally.
- The working tree is uncommitted, so test commit ordering cannot be audited independently.
- The implementation exceeds the default review budget; the single-branch delivery decision is
  recorded, but reviewers should treat the change as a high-workload slice.

### SUGGESTION

- Mark the two resolved `design.md` open questions complete or add links to the checked-in fixture
  and API-probe evidence.

## Final verdict

**PASS WITH WARNINGS**

All 13 tasks are complete, all nine specification scenarios have passing runtime coverage, the
required local build/test/lint/package/workflow/release/OCI/npm gates pass, and no CRITICAL issue
remains. Warnings are limited to unavailable deterministic runner/coverage configuration, hosted
publication paths, uncommitted TDD ordering, and review workload. Hand off technical evidence to
`sdd-qa` for independent acceptance testing; do not archive before QA completes.
