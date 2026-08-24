# npm Distribution Specification

## Purpose

Distribute CodeGauge through a portable npm wrapper with deterministic platform selection and transparent CLI behavior.

## Requirements

### Requirement: Approved package identity and target set

The approved npm scope and base package MUST be `@yacosta738` and `@yacosta738/codegauge`. The six GNU-target platform packages MUST use that scope and be the only eligible platform packages.

#### Scenario: Approved ownership

- GIVEN the approved scope, base package, and six platform package names are configured
- WHEN npm publication is planned
- THEN only those seven packages are eligible for publication

### Requirement: Deterministic platform resolution

The base package MUST select exactly one platform package from the approved operating-system/CPU matrix. Each platform package MUST declare matching exact `os`, `cpu`, and version constraints. Unapproved or musl targets MUST fail closed even when an archive exists.

#### Scenario: Supported platform

- GIVEN a supported GNU runtime and its exact optional dependency is installed
- WHEN the wrapper is invoked
- THEN it resolves only the matching executable

#### Scenario: Unsupported or missing package

- GIVEN the runtime is outside the matrix or its optional dependency is unavailable
- WHEN the wrapper is invoked
- THEN it returns an actionable nonzero error without running another binary

### Requirement: Transparent CLI process compatibility

The wrapper MUST pass arguments unchanged, inherit stdin/stdout/stderr, and return the child exit status. It MUST NOT rewrite CodeGauge output, diagnostics, profiles, or exit mapping.

#### Scenario: Invocation through npm

- GIVEN a caller supplies an analysis command and arguments
- WHEN the platform executable starts
- THEN arguments, stdio, and resulting exit status are unchanged

### Requirement: Verified ordered publication

Before publication, each platform executable MUST be extracted from its matching release archive, verified against the lowercase SHA-256 sidecar, and confirmed executable. Platform packages MUST publish before the base wrapper; any mismatch or packaging error MUST block all npm publication.

#### Scenario: Checksum mismatch

- GIVEN an extracted executable fails archive checksum verification
- WHEN npm packaging validation runs
- THEN the platform package and base wrapper remain unpublished and the mismatch is recorded
