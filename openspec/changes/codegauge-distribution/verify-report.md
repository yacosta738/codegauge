# Verification Report

**Change**: `codegauge-distribution`
**Version under test**: `0.1.0`
**Persistence mode**: OpenSpec
**Baseline**: `6477eb1`
**Scope**: technical conformance only; observable acceptance remains with `sdd-qa`
**State**: `openspec/changes/codegauge-distribution/state.yaml` was not modified.

## Completeness

| Metric | Value |
|---|---:|
| Task checkboxes reviewed | 17 |
| Tasks marked complete | 17 |
| Tasks marked incomplete | 0 |
| Requirements reviewed | 21 |
| Scenarios reviewed | 28 |

All R-C, R-D, R-E remediation tasks and implementation task checkboxes are marked complete. No
incomplete core or cleanup task was found.

## Build, test, and inspection evidence

| Command/check | Result |
|---|---|
| `cargo +1.97.1 metadata --locked --format-version 1` | PASS; 6 workspace members, 5 publishable runtime crates, private `codegauge-conformance` |
| `cargo +1.97.1 test --workspace --locked` | PASS; 31 tests passed, 0 failed, 0 skipped; doc tests ran |
| `cargo +1.97.1 check --workspace --locked` | PASS |
| `cargo +1.97.1 fmt --all -- --check` | PASS |
| `cargo +1.97.1 clippy --workspace --all-targets --locked -- -D warnings` | PASS |
| `python3 tests/bootstrap_checks.py` | PASS |
| `python3 tests/readme_checks.py` | PASS |
| `python3 tests/distribution_checks.py` | PASS |
| `python3 tests/release_provenance_tests.py` | PASS |
| `python3 tests/oci_distribution_tests.py` | PASS; static ordering plus synthetic positive/negative verifier coverage |
| `python3 scripts/generate_npm_packages.py --check` | PASS |
| `python3 -m py_compile tests/*.py scripts/*.py` | PASS |
| npm `typecheck` from `npm/codegauge` | PASS |
| npm `test` from `npm/codegauge` | PASS; 7 passed, 0 failed, 0 skipped |
| npm base `pack:dry-run` | PASS; wrapper package contains only `dist/index.js` and `package.json` |
| Six staged platform `npm pack --dry-run` checks | PASS; each staged executable is included with constrained package contents |
| Locked Cargo package verification for 5 runtime crates | PASS; local dirty worktree required `--allow-dirty` |
| Source fallback install | PASS; locked `cargo install --path crates/codegauge-cli`, then `version` and `profiles` |
| Native release binary smoke | PASS; host `aarch64-apple-darwin` binary returned `codegauge 0.1.0` and `java-jacoco-v1` |
| Synthetic archive matrix smoke | PASS; 8/8 formats, names, manifests, executable metadata, and lowercase SHA-256 sidecars |
| Incomplete archive negative gate | PASS; provenance validator rejected a 7/8 manifest set |
| Unsupported OCI architecture negative gate | PASS; verifier rejected `linux/ppc64le` |
| `actionlint .github/workflows/*.yml` | PASS |
| ShellCheck | PASS; 19 extracted workflow `run` blocks checked with GitHub expressions represented as shell variables |
| `git diff --check` | PASS |
| Full-SHA action audit | PASS; all 16 checkout refs use `11bd71901bbe5b1630ceea73d27597364c9af683` (v4.2.2) |
| Release attestation permission audit | PASS; `publish-release` has `id-token: write` and `attestations: write` |
| Real Docker amd64/arm64 build and runtime validation | PASS; Buildx export/load/inspect, version, profiles, contract, non-root, QEMU arm64, and fixed verifier all passed |

Coverage is not configured in `openspec/config.yaml`; no threshold exists.

### Real Docker digest-domain evidence

The fresh daemon run used local evidence at `/tmp/codegauge-verify-final.nYpqCj/oci-evidence` and
verified both architectures before any registry login or push. `docker image inspect .Id` matched the
Docker archive platform-manifest digest for both `linux/amd64` and `linux/arm64`; the verifier retained
separate `docker_config_digest`, `docker_platform_digest`, `oci_config_digest`, `platform_digest`,
`oci_index_digest`, and `metadata_digest` fields. The Docker archive was parsed independently from the
OCI archive, and Docker identity was compared only with Docker-derived identities. Runtime version,
profile, contract JSON, non-root UID 100, and arm64 QEMU evidence all passed.

## Release Please Cargo parser compatibility follow-up

The uncommitted follow-up is technically coherent with the pinned release tooling and is limited to
version-provenance compatibility:

| Boundary | Inspection result |
|---|---|
| Cargo package manifests | All six workspace crate manifests declare literal `version = "0.1.0"`; edition, toolchain, license, repository, and README fields still inherit workspace values; `codegauge-conformance` remains private. |
| Canonical workspace version | Root `Cargo.toml` retains `workspace.package.version = "0.1.0"`; `Cargo.lock` remains synchronized and the virtual workspace root is not a package. |
| Release Please configuration | `release-please-config.json` maps `{ "type": "toml", "path": "/Cargo.toml", "jsonpath": "$.workspace.package.version" }`, which targets the repository-root canonical version through the generic TOML updater. |
| Release Please compatibility | The exact `googleapis/release-please-action@45996ed1f6d02564a971a2fa1b5860e934307cf7` bundle is v5.0.0 and embeds release-please 17.6.0. The v17.6.0 Cargo workspace plugin requires each member `package.version` to be a string, while its generic TOML updater supports the configured JSONPath. |
| Provenance enforcement | `verify_release_provenance.py` now requires each crate manifest version to equal the requested release version; it does not relax the root, lockfile, npm, linked-component, archive, binary, or source-revision checks. |
| Scope | No RFC-0001 engine, profile, schema, fixture, golden, JSON, error, or exit behavior changed. `Cargo.lock` did not require a content change because the synchronized version remains `0.1.0`. |

### Fresh focused evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_provenance_tests.py` | PASS |
| `python3 tests/distribution_checks.py` | PASS |
| `python3 tests/oci_distribution_static_tests.py` | PASS |
| `python3 tests/oci_distribution_evidence_tests.py` | PASS |
| `python3 tests/oci_distribution_failure_tests.py` | PASS |
| `python3 -m compileall -q scripts tests` | PASS |
| `cargo metadata --locked --no-deps --format-version 1` | PASS |
| `cargo check --workspace --all-targets --locked` | PASS |
| `actionlint .github/workflows/*.yml` | PASS |
| `git diff --check` | PASS |

The focused provenance regression rejects a requested version drift (`9.9.9`) and the distribution
checks reject any crate manifest that does not contain the synchronized literal version or the root
TOML mapping. No Release Please CLI is installed, so an actual local `release-please` dry-run was not
fabricated; no hosted workflow, tag/release operation, credential use, registry publication, or
parent-repository gitlink update was performed.

**Follow-up result: PASS locally.** The fix is ready for PR review. This local result does not claim
hosted release-please, immutable-tag, non-host target, publication, or registry-attestation evidence.

## Prior critical finding recheck

| Prior finding / requested boundary | Fresh result | Evidence |
|---|---|---|
| Malformed/floating workflow action references | **CLOSED** | `distribution_checks.py`, actionlint, ShellCheck, and 33 external action references; 16 checkout refs are full SHA |
| Missing release attestation OIDC permission | **CLOSED** | `publish-release` grants both `id-token: write` and `attestations: write` |
| R-C checksum mismatch must block npm platform and base | **CLOSED** | npm regression returns `platformEligible=false` and `baseEligible=false` for corrupted archive bytes |
| R-C immutable npm checkout/source/version gate | **CLOSED structurally** | `npm-preflight` and `publish-npm` assert exact tag/SHA and source/version provenance |
| R-D release-please merged-main/tag/SHA provenance | **CLOSED structurally; hosted evidence pending** | release outputs, immutable checkout, validator, linked components, and negative identity/version tests pass |
| R-D duplicate GitHub Release creation | **CLOSED** | Existing release uses `gh release upload --clobber`; `gh release create` is absent |
| R-E pre-verification public OCI push | **CLOSED** | Local OCI/Docker exports, load, inspect, runtime checks, and verifier precede login/push |
| R-E synthetic OCI labels/runtime/non-root/digest negatives | **CLOSED** | Focused OCI suite passes all positive and negative verifier cases |
| R-E Docker/OCI digest-domain mismatch | **CLOSED** | Separate Docker archive parser, Docker identity comparison, distinct evidence fields, synthetic regression, and real amd64/arm64 verifier pass |
| RFC-0001 engine/profile/schema/fixture/golden/result/error/exit boundary | **CLOSED** | Protected semantic paths unchanged; 31 Rust/conformance tests pass; only release version provenance and the approved quick-xml API migration differ |

## Spec compliance matrix

`COMPLIANT` means a covering local test/check passed at runtime. `PARTIAL` means the implementation
and local evidence pass but a hosted, registry, immutable-revision, or non-host execution remains
unavailable. No scenario is failing.

| ID | Scenario | Covering evidence | Result |
|---|---|---|---|
| CI-1 | Untrusted pull request | Read-only CI permission audit; no hosted PR run | ⚠️ PARTIAL |
| CI-2 | Floating workflow dependency | Full-SHA audit, `distribution_checks.py`, and actionlint; no injected mutable-ref run | ⚠️ PARTIAL |
| CI-3 | All baseline checks pass | Locked Cargo, Python, npm, formatter, and Clippy suite | ✅ COMPLIANT |
| CI-4 | Existing lint failure remains blocking | `-D warnings` retained and current Clippy passes; no injected failing workflow run | ⚠️ PARTIAL |
| CI-5 | Incomplete target declaration blocks publishers | 7/8 archive negative gate exits nonzero | ✅ COMPLIANT |
| CI-6 | Failed preflight blocks later jobs and retains evidence | Workflow `needs`, fail-stop shell, and always-uploaded OCI evidence audit; no hosted failure injection | ⚠️ PARTIAL |
| CARGO-1 | Approved registry graph publishes in dependency order | Metadata/package checks and explicit model → core → application → provider → CLI publisher order; no registry publication by request | ⚠️ PARTIAL |
| CARGO-2 | Source fallback remains available | Real locked `cargo install --path` plus `version`/`profiles` smoke; no immutable Git checkout | ⚠️ PARTIAL |
| CARGO-3 | Immutable source install preserves released contracts | Current source contract suite and binary smoke; no recorded-revision install | ⚠️ PARTIAL |
| CARGO-4 | Distribution-only change preserves RFC-0001 contracts | Protected-path diff audit plus 31 passing Rust/conformance tests | ✅ COMPLIANT |
| CARGO-5 | Incomplete Cargo package stops publication | Five package verification runs pass; no injected missing-file package rehearsal | ⚠️ PARTIAL |
| CARGO-6 | Version mismatch blocks release | Version drift, invalid identity, binary drift, and archive-manifest negative checks | ✅ COMPLIANT |
| NPM-1 | Only approved base and six same-scope packages are eligible | Distribution, generator, linked-component, and pack checks | ✅ COMPLIANT |
| NPM-2 | Supported runtime selects exactly one matching package | Six static mappings, exact `os`/`cpu` manifests, and host wrapper resolution checks | ⚠️ PARTIAL |
| NPM-3 | Unsupported or missing dependency returns actionable nonzero error | Missing-dependency and musl rejection tests; non-host runtime execution is conditional | ⚠️ PARTIAL |
| NPM-4 | Args, stdio, and child exit status pass through unchanged | npm runtime test preserves stdin/stdout and child exit `17` | ✅ COMPLIANT |
| NPM-5 | Checksum mismatch blocks platform and base publication | Corrupted-archive regression returns both eligibility flags false | ✅ COMPLIANT |
| REL-1 | Provenance mismatch blocks before publication | Release identity/package/binary/archive negative validators; no hosted release | ⚠️ PARTIAL |
| REL-2 | Complete eight-archive release has formats and verified sidecars | Fresh 8-target packaging/archive validation passes; 7 target binaries are synthetic/cross-target locally | ⚠️ PARTIAL |
| REL-3 | Missing target evidence blocks assets and registries | 7/8 manifest negative gate fails as required | ✅ COMPLIANT |
| REL-4 | Gate failure blocks later publishers | Static dependency/order/fail-stop checks; no hosted rehearsal | ⚠️ PARTIAL |
| REL-5 | Credential exposure fails promotion and tokens stay out of artifacts/logs | Scoped permissions and no credential literals pass; no credential-bearing run by request | ⚠️ PARTIAL |
| REL-6 | Partial publication stops later jobs and exposes recovery | Ordered `needs`, fail-stop shell, retained evidence, and rollback documentation; no failure injection/rollback rehearsal | ⚠️ PARTIAL |
| OCI-1 | Only approved GHCR identity is eligible | Static identity/permission checks pass; no registry write | ⚠️ PARTIAL |
| OCI-2 | Unsupported architecture is rejected | Runtime verifier negative test rejects `linux/ppc64le` | ✅ COMPLIANT |
| OCI-3 | Workspace-aware locked non-root image builds with init | Real amd64/arm64 Buildx builds, loads, runtime smoke, non-root UID, and verifier pass | ✅ COMPLIANT |
| OCI-4 | Label/runtime metadata mismatch fails validation | Synthetic label/runtime/root/emulation/digest negatives plus real positive verifier pass | ✅ COMPLIANT |
| OCI-5 | One architecture fails before manifest/tags | Static loop/failure-stop/order checks; no injected failing architecture or registry rehearsal | ⚠️ PARTIAL |

**Scenario summary**: 11/28 compliant, 17/28 partial, 0/28 failing. Partial results are external or
host-matrix limitations, not observed implementation failures.

## Correctness

| Area | Status | Evidence |
|---|---|---|
| Cargo graph, metadata, contents, and order | ✅ Implemented | Locked metadata, five package verifications, source install, and ordered publisher audit pass |
| RFC-0001 compatibility boundary | ✅ Implemented | Protected engine/schema/fixture/golden paths are unchanged; contracts and exit mappings pass |
| CI permissions and action pinning | ✅ Implemented | CI is read-only; all external action refs are immutable full SHAs |
| Release archive provenance attestation | ✅ Implemented structurally | Release publisher has the required OIDC and attestation permissions |
| npm identity and platform behavior | ✅ Implemented / host-partial | Exact scope, six packages, pins, constraints, musl rejection, missing dependency, staged packs, and passthrough pass |
| npm checksum publication gate | ✅ Implemented | Typed preflight and corrupted-archive regression keep both publication paths ineligible |
| Release-please provenance and release coordination | ✅ Implemented structurally / hosted-partial | Exact outputs, merged-main checks, existing-release upload, no duplicate creation, and linked components pass local checks |
| Release binary/archive provenance | ✅ Implemented / target-partial | Native host evidence, explicit cross-target evidence, eight archive formats, manifests, and checksums pass locally |
| OCI identity, build gate, evidence, and final manifest | ✅ Implemented | Real amd64/arm64 images pass the corrected Docker/OCI digest-domain verifier before any registry operation |
| Archive/checksum/manifest integrity | ✅ Implemented | Deterministic packager and positive/negative provenance validators pass |
| Security and documentation | ✅ Implemented structurally | Scoped permissions, fixed release OIDC wiring, rollback guidance, and no committed credential literals pass |

## Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Coordinated runtime Cargo graph with private conformance crate | ✅ Yes | Metadata, package verification, and publisher chain preserve the approved graph |
| One workspace version from `CARGO_PKG_VERSION` | ✅ Yes | Binary, Cargo manifests/lock, npm manifests, release manifests, and archive validators use synchronized `0.1.0` evidence |
| Complete eight-target archive and six-package npm matrix | ✅ Structural / external-partial | All declarations and staged packaging pass; seven non-host Rust binaries were not built natively locally |
| Pinned read-only CI and scoped release permissions | ✅ Yes | Full-SHA actions, read-only CI, and release attestation permissions pass audit |
| Immutable release tag → quality → artifacts → ordered channels | ✅ Structural / hosted-partial | Exact SHA checkout, release-please outputs, gates, existing-release upload, npm ordering, and OCI pre-push ordering are present |
| Workspace-aware minimal non-root OCI image | ✅ Yes | Actual amd64/arm64 builds use the workspace, pinned images, `tini`, non-root user, immutable labels, and corrected digest evidence |

## TDD compliance audit

| Check | Result |
|---|---|
| RED → GREEN → REFACTOR evidence | ✅ Confirmed in `apply-progress.md` for R-C/R-D/R-E, including the digest-domain RED fixture and GREEN/REFACTOR real Docker rerun |
| Tests committed before or with code | ⚠️ Cannot verify from commits; implementation remains an intentionally dirty uncommitted worktree |
| RED phase evidence | ✅ Documented for distribution, release, checksum, and OCI digest-domain tests |
| Strict-TDD helper module | ⚠️ Configured `strict_tdd: true`, but the installed skill directory does not contain `strict-tdd-verify.md`; apply-progress RED/GREEN/REFACTOR evidence and fresh execution were used |

## Issues found

### CRITICAL

None.

### WARNING

1. Hosted release-please/tag provenance rehearsal was not run. The local validator, immutable-output
   wiring, versions, linked components, and negative tests pass, but GitHub-hosted execution remains
   an external gate.
2. Cargo crates.io, GitHub Release upload, npm publication, GHCR push, final multi-architecture
   manifest, registry attestation, credentials, and rollback rehearsal were intentionally not run.
   No credentials were used and no registry state was mutated.
3. Seven non-host archive targets were represented by explicit cross-target evidence/synthetic archive
   smoke locally, not native execution. Hosted/native runner evidence remains required before claiming
   those binaries as released.
4. Local Cargo package verification required `--allow-dirty`; the release workflow uses a clean
   immutable checkout and does not use that flag.
5. The worktree is intentionally dirty, so commit ordering for strict TDD cannot be independently
   proven from Git history.
6. No coverage threshold is configured.
7. The exact Release Please CLI dry-run remains unavailable because no local CLI is installed; exact
   v17.6.0 source/action-bundle inspection plus focused local regressions provide compatibility
   evidence without claiming executable hosted release behavior.

### SUGGESTION

1. During `sdd-qa`, run the capability-driven install, hosted-release rehearsal, and registry-free
   acceptance scenarios; keep `qa-report.md` separate from this technical verification report.
2. Preserve the synthetic Docker/OCI digest-domain regression and the real Docker evidence shape when
   changing BuildKit or Docker Engine versions.

## Verdict table

Judge A is source/spec inspection. Judge B is fresh local execution evidence; neither column represents
a delegated agent.

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| All external workflow actions use immutable full-SHA refs | ✅ | ✅ | CRITICAL (prior) | Closed |
| Release archive attestation has `id-token: write` and `attestations: write` | ✅ | ✅ | CRITICAL (prior) | Closed |
| R-C checksum mismatch blocks npm platform and base | ✅ | ✅ | CRITICAL (prior) | Closed |
| R-D merged-main/tag/SHA provenance wiring | ✅ | ⚠️ hosted run unavailable | WARNING | Structurally closed; hosted gate pending |
| R-D existing release upload without duplicate creation | ✅ | ✅ | WARNING (prior) | Closed locally |
| Six npm linked components and exact pins | ✅ | ✅ | WARNING (prior) | Closed locally |
| R-E no pre-verification public architecture push | ✅ | ✅ | CRITICAL (prior) | Closed |
| R-E synthetic OCI labels/runtime/non-root/digest negatives | ✅ | ✅ | CRITICAL (prior) | Closed |
| R-E real OCI positive evidence | ✅ | ✅ real Docker amd64/arm64 | CRITICAL (prior) | Closed |
| Docker inspect ID vs Docker platform-manifest identity | ✅ | ✅ | CRITICAL (prior) | Closed |
| Docker/OCI config, platform, index, and metadata evidence remain separately recorded | ✅ | ✅ | WARNING | Closed |
| Release Please 17.6.0 Cargo parser compatibility and root TOML version mapping | ✅ | ✅ focused regressions and Cargo metadata/check | WARNING | Closed locally; CLI/hosted rehearsal unavailable |
| RFC-0001 algorithms/schemas/goldens/contracts | ✅ | ✅ 31 Rust tests | CRITICAL | Preserved |
| Registry publication, final attestation, and rollback rehearsal | ✅ | ⚠️ intentionally not run | WARNING | External gate pending |

## Final verdict

**PASS WITH WARNINGS** — all implementation tasks are complete; the Release Please Cargo parser
compatibility follow-up is minimal, preserves version/package provenance, and passes its fresh focused
regressions plus Cargo metadata/check. Locked Cargo quality gates, Python distribution/provenance/OCI
tests, npm typecheck/tests/pack, generator checks, actionlint/ShellCheck, archive/checksum smoke,
RFC-0001 boundary checks, and fresh real Docker amd64/arm64 validation pass.
The prior critical checkout-pin, attestation-permission, checksum, release-provenance, and OCI
digest-domain findings are closed. Remaining warnings are explicitly external hosted release/tag,
non-host native target, publication, final registry-attestation, and rollback-rehearsal gates.

PR readiness is **READY** for this follow-up. No technical blocker was found in the inspected diff or
fresh safe checks. Release/archive readiness remains blocked by the acceptance limitations recorded in
`qa-report.md`, and the branch is six commits behind `origin/main`.

Technical verification is complete. Hand off to **`sdd-qa`** for acceptance scenarios and
`qa-report.md`; do not treat this report as user/operator acceptance.
