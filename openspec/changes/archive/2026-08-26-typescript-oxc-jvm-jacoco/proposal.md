# Proposal: JVM JaCoCo Rename and TypeScript Oxc/Istanbul Provider

## Intent

CodeGauge 0.3.0 labels JVM JaCoCo as `java-jacoco-v1` and accepts one artifact. RFC-0001 (authoritative; absent here), exploration, and the user directive establish why now: JaCoCo is JVM-level, Kover lacks `COMPLEXITY`, and TypeScript needs a Rust-native join. This protects policy-free CRAP.

## Scope

### In Scope
- Canonical `jvm-jacoco-v1`; no `kotlin-jacoco-v1`.
- Typed `AnalysisInput { role, path }`; v1 exposes the `coverage` and `source` roles, and providers declare them while deterministically rejecting missing, duplicate, malformed, or unreliable inputs. The generic role container leaves `class-files`, `complexity`, `execution-data`, and `metadata` as future candidates; they are not current v1 roles. CLI repeats `--input role=path` for the supported coverage/source inputs.
- `typescript-oxc-istanbul-v1`: Oxc callable model, versioned McCabe classic complexity in Rust, Istanbul statement coverage per callable, deepest ownership (nested bodies excluded), and span correlation.
- Registration, fixtures, conformance, and docs.

### Out of Scope
- Native Kover CRAP/coverage-only; document missing `COMPLEXITY` and `useJacoco()` → `jvm-jacoco-v1`.
- No complexity-report/typhonjs/ESLint/tree-sitter/Node FFI/processes/raw V8/`typescript-v8-v1`, manifests, auto-detection, policy/thresholds, LLMs, downloads, or CRAP changes.

## Capabilities

### New Capabilities
- `jvm-jacoco`: canonical JVM JaCoCo semantics and role-based input.
- `typescript-oxc-istanbul`: TypeScript callable CRAP from Oxc and Istanbul JSON.

### Modified Capabilities
- None; `openspec/specs/` is empty.

## Approach

Order: multi-input contract → JVM migration → CLI inputs → Oxc parser/callables/McCabe → Istanbul parser/ownership/correlation → registration → fixtures/conformance/docs → verification. Preserve inward layering; keep CRAP in `codegauge-core`.

## Affected Areas

| Area | Impact |
|---|---|
| `Cargo.toml`, `Cargo.lock`; `codegauge-model`, `codegauge-application` | Profiles, inputs, provenance, Oxc deps. |
| `codegauge-provider-jacoco`, new `codegauge-provider-typescript`, `codegauge-cli`, `codegauge-conformance` | JVM migration, Oxc/Istanbul, registration, vectors; core unchanged. |
| `schemas/codegauge-result-v1.schema.json`, `fixtures/`, `tests/golden/`, `README.md`, contract scripts | Contracts, vectors, docs, checks. |

## Breaking Changes

Profile/enum values rename to `jvm-jacoco-v1`/`JvmJacocoV1`; CLI/request become role-tagged. Provenance/schema needs multiple inputs; versioning is unresolved. Exit mapping and CRAP stay stable.

## Compatibility Decision and Evidence

Clean rename, no alias: search found only repo-owned references and exploration found no external consumer. Pre-1.0 permits the break; alias only on concrete evidence.

## Risks

| Risk | Mitigation |
|---|---|
| Oxc API/MSRV drift | Exact pin; retain Rust 1.97.1 and locked tests. |
| Ambiguous spans | Deterministic deepest-owner and tie/outside rules. |
| Undiscovered consumer | Pre-merge search; alias only on evidence. |

## Rollback Plan

Before release, revert artifacts. After release, publish a corrective patch with a deprecated alias if evidence requires; never silently alter CRAP or schemas.

## Dependencies

Exact-pinned Oxc Rust crates; no Node, network, downloads, or external complexity dependency.

## Open Decisions for Spec/Design

Choose role names, schema/provenance version, Oxc pin, McCabe operators, callable identity, and span tie/outside behavior.

## Success Criteria

- Both profiles analyze required roles deterministically; Istanbul/Vitest JSON works and raw V8 is rejected.
- Missing/duplicate/malformed inputs reject deterministically; locked tests, fmt, Clippy, conformance, and Python checks pass.
