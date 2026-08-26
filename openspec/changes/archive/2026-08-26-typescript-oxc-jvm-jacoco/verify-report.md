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

## Follow-up verification: provenance boundary fix (`df8526c`)

**Date**: 2026-08-26
**Trigger**: Hosted Release Please rehearsal showed that GitHub's PR-files API reports an
existing changelog as `status: modified` when Release Please inserts a new version section.  The
regression test and minimal validator change were delivered together in `df8526c` after the
feature baseline `1b0776e`.

This section is additive.  The original verification evidence and verdict above are preserved;
this follow-up records the post-hosted-dry-run validation and its remaining limitations.

### Follow-up source and artifact inspection

| Area | Evidence | Result |
|---|---|---|
| Fix scope | `scripts/verify_release_provenance.py` changes only `_validate_generated_changelog_patch`: permits `added`/`modified`, requires `# Changelog` in modified-file context, and retains addition-only/version-header/annotation checks. | ✅ Coherent |
| Regression coverage | `tests/release_carrier_tests.py::test_modified_generated_changelog_patch` models a hunk-only GitHub patch with `status: modified`, `# Changelog` context, no deletions, and the synchronized version header. | ✅ Present |
| Product/feature boundary | `git diff 1b0776e..df8526c` contains only the validator and its regression test; no Rust provider, model, core, CLI, schema, or release-graph product code changed in the follow-up. | ✅ Preserved |
| Task completeness | All 13 implementation tasks remain `[x]`; the follow-up is corrective release-provenance coverage under the existing verification/release boundary, not a new product task. | ✅ Complete |
| Design coherence | The fix remains in the release provenance validator, preserves strict hunk parsing and approved-path dispatch, and does not alter the inward Rust layering or CRAP semantics. | ✅ Coherent |

### Follow-up provenance boundary matrix

The focused executable matrix was run against the current `HEAD` (`df8526c`).

| Case | Runtime evidence | Result |
|---|---|---|
| Existing changelog, hunk-only `status: modified`, `# Changelog` context, additions only, synchronized version header | `python3 tests/release_carrier_tests.py`; direct validator matrix | ✅ ACCEPTED |
| Modified changelog with a deletion | Direct validator matrix; `_validate_generated_changelog_patch` rejects non-empty `deleted` lines | ✅ REJECTED |
| Arbitrary changelog replacement that includes a deletion | Existing `arbitrary generated-file content` regression plus direct matrix | ✅ REJECTED |
| Modified changelog with a valid header plus arbitrary extra release-note lines | Adversarial direct validator matrix | ✅ ACCEPTED (expected generated Release Please content) |
| Unapproved changelog path | Existing unapproved-path cases plus direct matrix (`crates/codegauge-evil/CHANGELOG.md`) | ✅ REJECTED |
| Missing patch or truncated/inconsistent hunk | Existing missing/truncated/malformed patch cases plus direct matrix | ✅ REJECTED |

The parser still validates GitHub change metadata, unified/hunk-only headers, every hunk's old/new
line counts, and addition/deletion counts before the generated-changelog contract runs.  Release
Please changelog lines are generated from commit messages and are intentionally not allowlisted:
the existing `status: added` contract already accepts arbitrary generated release-note lines, so
the equivalent `status: modified` additions-only form correctly accepts them as well.  Deletion,
path, patch-completeness, synchronized-version-header, and annotation rejection remain strict.

### Follow-up local execution evidence

All commands were executed from `/Users/acosta/Dev/agent-swarm/codegauge`.  The configured
`quality-runner/v1` manifest is disabled (`enabled: false`), so this is explicitly `fallback`
evidence rather than a runner envelope.

| Command | Exit | Result | Evidence |
|---|---:|---|---|
| `python3 tests/release_carrier_tests.py` | 0 | PASS | `RELEASE CARRIER TESTS: PASS`; includes the new modified-changelog regression and existing negative boundary cases. |
| `python3 -m pytest -q tests/release_carrier_tests.py` | 0 | PASS | 4 passed. |
| `python3 -m pytest -q tests/*_tests.py` | 0 | PASS | 24 passed. |
| `python3 tests/release_provenance_tests.py`, `release_carrier_mode_tests.py`, `release_carrier_static_tests.py` | 0 | PASS | All three named suites printed their `PASS` summaries. |
| `python3 tests/bootstrap_checks.py`, `readme_checks.py`, `distribution_checks.py` | 0 | PASS | All three printed `PASS`. |
| `python3 tests/oci_distribution_tests.py`, `oci_distribution_failure_tests.py`, `oci_distribution_static_tests.py`, `oci_distribution_evidence_tests.py` | 0 | PASS | All four printed `PASS`. |
| `python3 tests/release_please_runtime_tests.py` | 0 | PASS | Exact Release Please `17.6.0` was made available through `npx`; the read-only fake-SCM harness ended with `RELEASE PLEASE V17.6.0 RUNTIME TESTS: PASS`, `releaseCalls: 0`, and `tagCalls: 0`. |
| `cargo test --workspace --locked` | 0 | PASS | 59 passed, 0 failed, 0 ignored; Rust unit, integration, provider, CLI, conformance, and doc tests passed. |
| `cargo fmt --all -- --check` | 0 | PASS | No formatting diagnostics. |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | 0 | PASS | No denied warnings. |
| `cargo check --workspace --locked` | 0 | PASS | All workspace members type-checked. |
| `cargo metadata --locked --format-version 1` | 0 | PASS | Locked workspace graph parsed successfully. |
| `actionlint .github/workflows/*.yml` | 0 | PASS | No workflow diagnostics. |
| `git diff --check` | 0 | PASS | No whitespace errors; the current uncommitted files are listed in the working-tree note below. |
| `npm test` from `npm/codegauge` | 0 | PASS | With `npm/codegauge/tsconfig.json` (`compilerOptions.types: ["node"]`, commit `cb24e54`), TypeScript builds and all 6 Node tests pass. |

The npm gate is green and reproducible from commit `cb24e54`.  The change is outside `df8526c`
(`git diff 1b0776e..df8526c` has no npm-file changes); it is recorded separately as a focused
TypeScript build fix.  Dependency installation created only ignored local test artifacts.
Working-tree accounting: this phase changes only `verify-report.md` and preserves `state.yaml` at
`verify -> qa`; the implementation/config commits were already pushed.

### Hosted evidence and limitations

| Hosted run | Observed result | Verification meaning |
|---|---|---|
| `32939386068` | PASS with `no-matching-release-please-pr` | Carrier mode/selection path only; it skipped before full Release Please PR file/provenance validation. It is not full hosted acceptance evidence. |
| `32939482165` replay of historical PR `#75` | FAILURE | The validator rejected the real existing-changelog representation because GitHub returned `status: modified`; the root cause was reproduced locally and corrected in `df8526c`. The hosted replay was not rerun after the fix in this phase. |

Other limitations remain unchanged from the original report: coverage is unavailable, the
configured quality runner is disabled, and registry/GitHub Release/GHCR publication was not
performed.  `strict_tdd: true` is configured, but the referenced `strict-tdd-verify.md` module is
not present in the available skill tree; commit ordering is therefore not independently enforced
by that module.  The regression-plus-fix commit and runtime RED/GREEN evidence are inspectable.

### State tracking

Because this follow-up verifies a post-QA code change, `state.yaml` was moved back to
`current_phase: verify` with `next: qa`; the prior QA artifact is preserved but must be rerun after
this follow-up.  No archive action was taken.

### Follow-up issues and verdict

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| `df8526c` accepts the real GitHub hunk-only modified changelog form while retaining structural negative boundaries | ✅ | ✅ | — | Confirmed |
| Arbitrary generated Release Please release-note lines are accepted for additions-only changelogs | ✅ | ✅ | — | Confirmed expected behavior; not an allowlist contract |
| Existing JVM/TypeScript feature behavior still passes the locked Rust and conformance gates | ✅ | ✅ | — | Confirmed |
| Hosted run `32939386068` skipped full validation because no matching Release Please PR existed | ✅ | ✅ | WARNING | Confirmed limitation |
| Hosted run `32939482165` has not been replayed after `df8526c` | ✅ | ✅ | WARNING | Re-run required for hosted confirmation |
| Configured quality runner is disabled; evidence is manual `fallback` | ✅ | ✅ | WARNING | Confirmed limitation |
| `npm test` requires `compilerOptions.types: ["node"]` in the tsconfig | ✅ | ✅ | — | Confirmed and reproducible from `cb24e54` |

**Follow-up verdict: PASS WITH WARNINGS.**  The real hosted changelog representation is accepted,
arbitrary generated release-note lines are accepted as intended, all local Rust/Python/workflow/
npm gates pass from committed changes, and no CRITICAL issue remains.  Warnings are limited to the
disabled quality runner/coverage and the hosted replay still awaiting rerun on the fixed current
graph.  Do not archive before `sdd-qa` records that hosted acceptance evidence.
