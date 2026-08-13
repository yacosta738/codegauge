# npm Distribution Specification

## Purpose

Distribute the CodeGauge executable through a portable npm wrapper while keeping platform selection
and CLI process behavior transparent.

## Requirements

### Requirement: Approved package identity and target set

The approved npm scope and base package are `@yacosta738` and `@yacosta738/codegauge`. Platform
package names MUST use the same approved scope and the initial target declaration MUST explicitly
identify the six viable platform packages. No package may be published outside that scope.

#### Scenario: Approved npm ownership

- GIVEN the approved scope and package names are configured
- WHEN a release reaches the npm publisher
- THEN only the approved platform packages and `@yacosta738/codegauge` are eligible for publication

### Requirement: Deterministic platform resolution

The base package MUST select exactly one platform package from the approved target matrix using the
runtime operating-system and CPU values. Each platform package MUST declare matching `os` and `cpu`
constraints and an exact version pin. Musl or otherwise unapproved targets MUST NOT be claimed by the
npm channel merely because a release archive exists.

#### Scenario: Supported platform

- GIVEN a supported runtime and its exact optional dependency are installed
- WHEN the wrapper is invoked
- THEN it resolves the matching executable and does not select a different platform binary

#### Scenario: Unsupported or missing optional dependency

- GIVEN the runtime is outside the approved matrix or its package is unavailable
- WHEN the wrapper is invoked
- THEN it returns an actionable nonzero error without running an unrelated binary

### Requirement: Transparent CLI process compatibility

The wrapper MUST pass user arguments unchanged, inherit standard input/output/error, and return the
child process exit status. It MUST NOT rewrite CodeGauge JSON, diagnostics, profile names, or the
public exit mapping.

#### Scenario: CLI invocation through npm

- GIVEN a caller passes an analysis command and its arguments to the base package
- WHEN the wrapper starts the platform executable
- THEN arguments and stdio are preserved and the resulting exit status is unchanged

### Requirement: Verified package publication

Before a platform package is published, its executable MUST be extracted from the matching release
archive, verified against the archive SHA-256 sidecar, and confirmed executable. Platform packages
MUST publish before the base wrapper; a version mismatch, checksum failure, or packaging error MUST
prevent the base package from publishing.

#### Scenario: Checksum mismatch

- GIVEN an extracted executable does not match its archive checksum
- WHEN npm packaging is validated
- THEN the platform package and base wrapper remain unpublished and the mismatch is logged
