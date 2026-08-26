# TypeScript Oxc and JVM JaCoCo

## Purpose

Define collection and two profiles without changing CRAP policy.

## Requirements

### Requirement: Typed collection

The model MUST expose `InputRole`, `AnalysisInput { role, path }`, and `CollectionRequest`. In v1, the supported roles are only `coverage` and `source`; paths are explicit and read-only. The role/cardinality collection container is extensible for future inputs. `class-files`, `complexity`, `execution-data`, and `metadata` are future candidates only and are not current v1 roles or requirements.

#### Scenario: Provider receives declared inputs

- GIVEN `coverage=a.json`, `source=src`
- WHEN a collection request is built
- THEN provider receives typed roles and exact digests

### Requirement: Deterministic errors

Descriptors MUST declare required roles/cardinality. Missing, duplicate, unknown, malformed, unavailable, or uncorrelatable inputs MUST fail deterministically; providers MUST NOT guess or downgrade.

#### Scenario: Invalid collection is rejected

- GIVEN a required input is missing/duplicated/unreadable/uncorrelatable
- WHEN collection starts
- THEN stable input error returns; no score/downgrade

### Requirement: JVM profile

Only `jvm-jacoco-v1` is canonical; `java-jacoco-v1` and `kotlin-jacoco-v1` MUST be unsupported. It requires `coverage`. Complexity is `missed + covered`; instruction coverage is `covered/(missed+covered)`. Identities remain `java:<class_vm>#<name><descriptor>`, including generated methods. Output/provenance use `jacoco-cyclomatic`/`jacoco-instruction` under the renamed profile.

#### Scenario: JVM report

- GIVEN valid JaCoCo XML
- WHEN collected with `jvm-jacoco-v1`
- THEN measurements/provenance use the renamed profile

### Requirement: Kover boundary

Documentation MUST state native Kover is not a CRAP profile because it lacks `COMPLEXITY`; instructions MUST NOT proxy complexity. Kover `useJacoco()` output is consumed as JVM JaCoCo, not a Kotlin alias.

#### Scenario: Native Kover is not silently accepted

- GIVEN Kover XML without `COMPLEXITY`
- WHEN it is analyzed as `jvm-jacoco-v1`
- THEN evidence is incompatible; no CRAP symbol is produced

### Requirement: Oxc complexity

`typescript-oxc-istanbul-v1` MUST require `source`/`coverage` and discover functions, arrows, methods, constructors, getters, and setters with paths/spans. McCabe classic v1 is base 1 plus each `if`, ternary, loop (`for`, `for-in`, `for-of`, `while`, `do`), non-default `case`, `catch`, and `&&`/`||`. `switch`, `else`, `default`, `??`, returns, and TS annotations/types/interfaces/generics/assertions add none. Nested bodies MUST be excluded from parents.

#### Scenario: AST rules are observable

- GIVEN nested callables contain listed constructs
- WHEN Oxc analyzes source
- THEN each has deterministic complexity/spans; no name-only collision

### Requirement: Istanbul correlation

The provider MUST accept Istanbul-compatible JSON only, including Vitest Istanbul output; raw V8 MUST be rejected. It requires path keys and statement maps/counts, ignores `f`, `b`, and function/branch hits, and assigns each statement to the deepest callable. Coverage is owned statements with count `> 0` divided by owned statements. Path/span correlation MUST be unambiguous; malformed/unmatched artifacts MUST fail.

#### Scenario: Nested statements use deepest ownership

- GIVEN parent/nested callable statement spans
- WHEN statements are assigned
- THEN nested statements belong only to nested; zero-owned are omitted, not zeroed

### Requirement: CRAP core

The application MUST feed measurements into unchanged `crap-original-v1`, `cc²(1-cov)³ + cc`; thresholds, policy, downloads, autodetection, and LLM behavior remain absent.

#### Scenario: Score is calculated centrally

- GIVEN compatible measurements
- WHEN analysis completes
- THEN CRAP/summaries match existing semantics and formatting

### Requirement: CLI contract

`analyze` MUST accept repeated `--input role=path`; no provider flags or manifest is required. Malformed assignments/format are `CLI_ERROR=2`; missing paths `3`; unsupported profiles `4`; invalid artifacts `5`; partial/zero-compatible `6`; complete `0`. One JSON MUST go to stdout; diagnostics go to stderr.

#### Scenario: Multi-input invocation

- GIVEN repeated `--input role=path` and `--format json`
- WHEN the command runs
- THEN one newline-terminated JSON is stdout-only; diagnostics are stderr-only

### Requirement: Determinism and compatibility

Inputs/diagnostics MUST have stable role/path ordering; symbols sort bytewise by ID; paths use `/` without `realpath`; digests cover exact bytes. Fixtures MUST cover valid, nested, malformed, hostile, unavailable, and uncorrelatable artifacts. Conformance, golden, schema, README, and profile-list checks MUST cover both profiles, role provenance, rename, Kover/Vitest, and exits. Existing single-input provenance MUST remain consumable while an additive role-tagged list records all inputs. Assumption: these Oxc rules are v1; changes require profile v2.

#### Scenario: Reordered inputs remain identical

- GIVEN the same files in different input order
- WHEN both analyses run
- THEN timestamp-masked JSON/results are identical
