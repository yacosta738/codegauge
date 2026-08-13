# CodeGauge

CodeGauge `0.1.0` is a standalone Rust CLI for deterministic JaCoCo evidence and the
`crap-original-v1` metric. It measures evidence, not policy: a score is never a quality verdict.

## Purpose and boundary

- CodeGauge is independent from `agent-harness`; the harness is a future consumer, not a dependency.
- The `java-jacoco-v1` provider reads an existing JaCoCo XML artifact. It does not run Maven, Gradle,
  tests, or JaCoCo, install dependencies, access the network, call an LLM, or mutate source.
- It does not auto-detect projects, read project configuration, generate reports, apply thresholds, or
  emit `PASS`/`FAIL`. Consumers own policy and workflow decisions.

## Prerequisites and checks

Use the pinned Rust/Cargo toolchain `1.97.1` from `rust-toolchain.toml` and keep `Cargo.lock` committed.
From the repository root:

```bash
cargo metadata --locked
cargo test --workspace --locked
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --locked -- -D warnings
```

The repository checks also include `python3 tests/bootstrap_checks.py` and
`python3 tests/readme_checks.py`.

## CLI `0.1.0`

The public interface is JSON-only for analysis and requires the exact profile, input, and format:

```text
codegauge analyze --profile java-jacoco-v1 --input PATH --format json
codegauge profiles
codegauge version
```

`profiles` prints exactly `java-jacoco-v1`. `version` prints exactly `codegauge 0.1.0`.
`analyze` writes exactly one result or structured error JSON document to stdout; human diagnostics go
to stderr. The only accepted format is `json`.

### Status and exits

`COMPLETE` means every reported method with required compatible evidence was measured. `PARTIAL`
means compatible symbols were measured while some evidence was omitted. `INCOMPATIBLE_MEASUREMENTS`
is a structured error when zero compatible symbols remain. CodeGauge has no PASS/FAIL or threshold.

| Exit | Meaning |
|---:|---|
| `0` | Complete result |
| `2` | `CLI_ERROR` (arguments or format) |
| `3` | `INPUT_NOT_FOUND` (missing/unreadable input) |
| `4` | `UNSUPPORTED_PROFILE` or `UNSUPPORTED_PROVIDER` |
| `5` | `INVALID_INPUT` (malformed, duplicate, invalid, or hostile artifact) |
| `6` | `PARTIAL` result or `INCOMPATIBLE_MEASUREMENTS` error |
| `10` | `INTERNAL_ERROR` |

Every nonzero outcome emits one JSON document on stdout, except `PARTIAL`, which emits one result
JSON document with exit `6`; diagnostics are stderr-only.
The public exit mapping is exactly `0/2/3/4/5/6/10`.

## Result and error contract

The checked-in JSON schemas are `schemas/codegauge-result-v1.schema.json` and
`schemas/codegauge-error-v1.schema.json`, with IDs `codegauge-result/v1` and `codegauge-error/v1`.
Results contain `schema`, `tool`, `profile`, `analysis`, `summary`, `symbols`, and `provenance`.
Errors contain `schema`, `tool`, `code`, `message`, and `details`; parseable-input errors include the
display path and exact artifact digest in `details`.

The tool/profile/schema versions are independent. `java-jacoco-v1` declares `crap-original-v1`; a
semantic provider change requires a new profile, not a silent change to v1.

### JaCoCo method semantics

- For each method, `COMPLEXITY` total is `missed + covered`; `INSTRUCTION` coverage is
  `covered / (missed + covered)`. `BRANCH`, `LINE`, `METHOD`, `CLASS`, and aggregate counters are ignored.
- The join key is exactly `java:<class_vm>#<name><descriptor>`. JVM descriptors preserve overloads.
  Reported constructors, `<clinit>`, synthetic, bridge, anonymous, and lambda/generated methods are
  included; no repository path is fabricated.
- Missing, invalid, unresolved, or zero-denominator required evidence is indeterminate: the method is
  omitted with a bounded diagnostic; missing evidence never becomes zero. Malformed structure, duplicate identities,
  missing identity fields, and invalid descriptors reject the artifact.

## Provenance and determinism

The input digest is SHA-256 of the exact bytes read, rendered as lowercase 64-hex. Provenance records
the display path, provider semantics, and UTC RFC3339 `analysis_timestamp` ending in `Z`; unknown
metadata is absent, not fabricated. Goldens mask only `analysis_timestamp`.

Symbols sort bytewise by `symbol.id`; paths use `/` without `realpath` or inferred prefixes. Compatible
summary values are unrounded until canonical serialization. All numbers are finite binary64, rendered
round-half-even to 12 decimals with trailing zeroes and `-0` removed. JSON is fixed-order UTF-8 and
newline-terminated.

## Security limits

Input is read-only UTF-8 XML with an optional BOM. The parser limits are 64 MiB, depth 128,
100,000 classes and methods, 16 counters per method, and 1,000,000,000 per required count. DTD/DOCTYPE,
entities, external resolution, unsupported encodings, network access,
commands, installation, source mutation, and plugins are rejected or absent.

## References and future integration

`crap4java`, `crap4go`, and `crap4clj` are non-normative inspiration only: CodeGauge copies no code,
dependencies, or runners from them. A future `agent-harness` integration consumes a released
executable and its result/error contract, not CodeGauge crates, the formula, or build/test runners.

## Distribution channels

The approved release version is synchronized across the `codegauge-cli` binary, the publishable
Cargo runtime graph, npm packages, archives, and OCI metadata. The registry/source channels are:

- Cargo: the runtime crates publish in dependency order — `codegauge-model`, `codegauge-core`,
  `codegauge-application`, `codegauge-provider-jacoco`, then `codegauge-cli` — with source/Git at an
  immutable revision retained as a fallback. The virtual workspace root is not a package.
- npm: install `@yacosta738/codegauge`; it selects exactly one of the six GNU platform packages:
  `@yacosta738/codegauge-linux-x64-gnu`, `@yacosta738/codegauge-linux-arm64-gnu`,
  `@yacosta738/codegauge-darwin-x64`, `@yacosta738/codegauge-darwin-arm64`,
  `@yacosta738/codegauge-win32-x64-msvc`, or `@yacosta738/codegauge-win32-arm64-msvc`.
  Linux musl is intentionally rejected by npm even though musl release archives exist.
- Archives: the complete viable matrix is `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`,
  `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`, `x86_64-apple-darwin`,
  `aarch64-apple-darwin`, `x86_64-pc-windows-msvc`, and `aarch64-pc-windows-msvc`. Unix archives
  are `tar.gz`; Windows archives are `zip`; every archive has a lowercase SHA-256 sidecar and a
  manifest containing `source_revision`.
- OCI: `ghcr.io/yacosta738/codegauge` publishes only verified `linux/amd64` and `linux/arm64`
  images, runs as the non-root `codegauge` user, and carries immutable version/source labels.

Release automation is intentionally ordered and fail-stop: quality, package, target, checksum, and
metadata gates run before upload; Cargo dependencies precede dependents; npm platform packages
precede the wrapper; and OCI publication follows the archive/npm gates. Dry runs are safe only when
the workflow's `dry_run` input is honored. No registry credential belongs in this repository.

### Provenance and rollback

Each release records its immutable Git `source_revision`, Rust toolchain, target, archive name, and
lowercase SHA-256. Publication across Cargo, GitHub Releases, npm, and GHCR is not atomic. If a later
publisher fails, later jobs stop, logs and successful artifacts remain auditable, and recovery uses
a corrected patch: Cargo versions cannot be deleted, while escaped npm or OCI artifacts must be
deprecated, superseded, or retagged according to registry policy. Disable release triggers while
recovering when necessary.

## Release checklist

- [ ] Release from an immutable Git revision; retain the exact `codegauge 0.1.0` version and profile/schema IDs.
- [ ] Keep `rust-toolchain.toml` pinned to Rust/Cargo `1.97.1` and `Cargo.lock` committed.
- [ ] Run `cargo metadata --locked`, `cargo test --workspace --locked`, fmt, and clippy with locked inputs.
- [ ] Publish an artifact SHA-256 for every binary/archive actually released and record its pinned target triple.
- [ ] Verify `codegauge version`, `codegauge profiles`, JSON stdout/error contracts, and timestamp-masked goldens.
- [ ] Do not claim cross-platform binaries were produced unless each claimed target has a corresponding artifact and checksum.
