# Tasks: JVM JaCoCo / TypeScript Oxc-Istanbul

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | 850–1,100; ≤400 production/slice |
| Suggested split | PR1→PR5 |
| Delivery strategy | ask-on-risk |

Decision needed before apply: Resolved — single working branch, sequential tested slices
Chained PRs recommended: No — no intermediate PRs; preserve work-unit boundaries locally
Chain strategy: one branch, five sequential slices, stop on failing verification before continuing
400-line budget risk: High

### Suggested Work Units

| Unit | Deliverable | PR | Depends |
|---|---|---|---|
| 1 | contracts | 1 | — |
| 2 | JVM/CLI | 2 | 1 |
| 3 | Oxc/McCabe | 3 | 1 |
| 4 | Istanbul join | 4 | 3 |
| 5 | integration/docs | 5 | 2–4 |

## Phase 1: Foundation / Contracts

- [x] 1.1 **RED:** baseline tests in `crates/codegauge-model/tests/contracts.rs` and `crates/codegauge-application/tests/application.rs`; **GREEN:** verify Rust 1.97.1/Oxc 0.147.0 API/MSRV; **REF/VERIFY:** `cargo metadata --locked`, stop drift (spec §Typed collection; design §Contracts).
- [x] 1.2 *(after 1.1)* **RED:** role/cardinality/error/order cases in `crates/codegauge-model/tests/contracts.rs`; **GREEN:** only `Coverage`/`Source`, `AnalysisInput`, `InputSet`, `CollectionRequest` and sorted artifacts in `model`/`application`; **REF/VERIFY:** preserve legacy coverage (spec §§Typed collection, Deterministic errors).
- [x] 1.3 *(after 1.2)* **RED:** descriptor case in `crates/codegauge-application/tests/application.rs`; **GREEN:** migrate `MetricProvider`/`Analyzer`, diagnostics and role provenance; **REF/VERIFY:** CRAP/error v1 unchanged (spec §CRAP core; design §Provenance).

## Phase 2: JVM / CLI

- [x] 2.1 *(after 1.3)* **RED:** rename/Kover cases in `crates/codegauge-model/tests/contracts.rs`, `crates/codegauge-provider-jacoco/tests/jacoco.rs`, `crates/codegauge-conformance/tests/conformance.rs`; **GREEN:** `jvm-jacoco-v1`/`JvmJacocoV1`, `coverage`; **REF/VERIFY:** old names/native Kover reject (spec §§JVM profile, Kover; design §JVM Migration).
- [x] 2.2 *(after 2.1)* **RED:** malformed/unknown/duplicate/missing `--input role=path` cases in `crates/codegauge-cli/tests/cli.rs`; **GREEN:** `ArgAction::Append`, `split_once('=')`, role parsing in `crates/codegauge-cli/src/main.rs`; **REF/VERIFY:** exits 2/3/4/5/6 and JSON stdout/stderr (spec §CLI; design §CLI).

## Phase 3: TypeScript Provider

- [x] 3.1 *(after 1.3)* **RED:** compile seam `crates/codegauge-provider-typescript/tests/api_probe.rs`; **GREEN:** new crate with exact `=0.147.0` pins for `oxc_allocator/parser/ast/ast_visit/span/syntax` in `Cargo.toml`/`Cargo.lock`, minimal adapter; **REF/VERIFY:** `cargo check --locked`, never bump toolchain.
- [x] 3.2 *(after 3.1)* **RED:** fixture-first spans in `crates/codegauge-provider-typescript/tests/typescript.rs`; **GREEN:** `parser.rs`/`callable.rs` for function/arrow/method/ctor/get/set identities; **REF/VERIFY:** `/` paths and UTF-8 spans.
- [x] 3.3 *(after 3.2)* **RED:** unit/property/golden cases in `crates/codegauge-provider-typescript/tests/typescript.rs`; **GREEN:** `complexity.rs`, classic v1, nested exclusion; **REF/VERIFY:** increments only `if`/ternary/loops/non-default-case/`catch`/`&&`/`||`.
- [x] 3.4 *(after 3.2)* **RED:** raw-V8/malformed/statement/deepest-owner cases in `crates/codegauge-provider-typescript/tests/typescript.rs`; **GREEN:** `istanbul.rs`/`ownership.rs` use `statementMap` + `s`; **REF/VERIFY:** reject raw V8, ignore function/branch hits; omit zero-owned.
- [x] 3.5 *(after 3.4)* **RED:** non-ASCII/path/boundary/duplicate/ambiguous/unmatched cases in `crates/codegauge-provider-typescript/tests/typescript.rs`; **GREEN:** `correlation.rs` canonical join/observations; **REF/VERIFY:** one-to-one paths, deterministic `INVALID_INPUT` (design §Correlation).

## Phase 4: Integration / Conformance

- [x] 4.1 *(after 2.2, 3.5)* **RED:** tests in `crates/codegauge-application/tests/application.rs`, `crates/codegauge-cli/tests/cli.rs`, `crates/codegauge-model/tests/schemas.rs`; **GREEN:** register `typescript-oxc-istanbul-v1`, descriptor, `provenance.inputs` and output; **REF/VERIFY:** result schema only; error v1/`crap-original-v1` stay (spec §Determinism; design §Provenance).
- [x] 4.2 *(after 4.1)* **RED:** fixtures/goldens first in `fixtures/typescript/`, `tests/golden/`, then `crates/codegauge-conformance/tests/conformance.rs`; **GREEN:** nested/hostile/Vitest-normalized/reordered/TSX-scope-decision vectors; **REF/VERIFY:** IDs, digests, profiles, exits.

## Phase 5: Documentation / Full Verification

- [x] 5.1 *(after 4.2)* **RED:** `tests/readme_checks.py` assertions; **GREEN:** `README.md`; **REF/VERIFY:** run `cargo test --workspace --locked`, `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets --locked -- -D warnings`, `cargo check --workspace --locked`, `python3 tests/bootstrap_checks.py`, `python3 tests/readme_checks.py`; guard no raw-V8-parser/Kover-profile/complexity-report/typhonjs/ESLint/tree-sitter/manifest-only-CLI/policy/downloads/language-autodetection.

**Acceptance:** all spec scenarios pass; `codegauge-core` is untouched. **Rollback:** pre-release revert; post-release corrective patch only, with evidence-based alias if required; never silently alter CRAP/schema semantics.
