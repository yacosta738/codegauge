# Acceptance QA Report: codegauge-distribution

## Identity

- Change: `codegauge-distribution`
- Mode: OpenSpec
- QA phase: `sdd-qa`
- Date: 2026-08-13
- QA verdict: `BLOCKED`
- State handoff: `state.yaml` was not modified, as requested.

## Sources of Truth

- Proposal: `openspec/changes/codegauge-distribution/proposal.md`
- Specifications:
  - `openspec/changes/codegauge-distribution/specs/ci-quality-gates/spec.md`
  - `openspec/changes/codegauge-distribution/specs/cargo-distribution/spec.md`
  - `openspec/changes/codegauge-distribution/specs/npm-distribution/spec.md`
  - `openspec/changes/codegauge-distribution/specs/release-artifacts/spec.md`
  - `openspec/changes/codegauge-distribution/specs/oci-distribution/spec.md`
- Design: `openspec/changes/codegauge-distribution/design.md`
- Tasks: `openspec/changes/codegauge-distribution/tasks.md`
- Apply handoff: `openspec/changes/codegauge-distribution/apply-progress.md`
- Technical verification: `openspec/changes/codegauge-distribution/verify-report.md`
- State: `openspec/changes/codegauge-distribution/state.yaml`
- Configuration: `openspec/config.yaml`

Technical verification handed off as `PASS WITH WARNINGS`. It reports 11/28 scenarios locally
compliant, 17/28 partial, and no observed failures; the partial results include hosted release,
registry, immutable-tag, and non-host target limitations. This report is an independent acceptance
record and does not convert those partial results into product acceptance.

## Target and Environment

- Target: the local CodeGauge checkout at `/Users/acosta/Dev/agent-swarm/codegauge`, version `0.1.0`,
  current source revision `6477eb1f58fc2ea3f0ab9319eee59c4e463d32e4`.
- Source state: intentionally dirty distribution worktree; no commit, branch, push, publication, or
  production-code repair was performed.
- Host: macOS arm64.
- Tools: Rust/Cargo `1.97.1`, Node `v24.19.0`, npm `11.17.0`, Python `3.14.6`, Docker `29.4.0`,
  BuildKit `v0.32.2` via the running `pt-builder`, `actionlint`, and `shellcheck`.
- Docker: local daemon and arm64 emulation were available. No registry login or push was performed.
- GitHub: no local `v0.1.0` tag or corresponding GitHub Release exists. A read-only release lookup
  returned `release not found`.
- Credentials/permissions: no Cargo, npm, GHCR, or GitHub write operation was authorized or run.
  No registry token was injected into the QA commands.
- Limitations: hosted GitHub Actions execution, release-please tag creation, native execution on
  seven non-host archive targets, Cargo/npm/GHCR publication, final OCI manifest publication,
  attestation, and rollback rehearsal were not executable within the requested safety boundary.

## Capability Inventory

| Capability | Availability | Selected? | Rationale / rejection reason |
|---|---|---:|---|
| Local Cargo/source install and CLI runtime | available | yes | Executable target; used for version, profiles, analysis, errors, repeatability, and hostile-input checks. |
| Local Rust/Python/npm quality runners | available | yes | Produced observable command results for the local quality and package gates. |
| npm staged-package runtime | available | yes | Host is macOS arm64; staged matching platform package and synthetic child packages exercised wrapper behavior. |
| Archive/package generator and provenance validators | available | yes | Generated and verified a local eight-target archive fixture set without publication. |
| Docker Buildx/daemon/QEMU | available | yes | Built, loaded, inspected, and ran both `linux/amd64` and `linux/arm64` images locally. |
| Workflow/actionlint/ShellCheck audit | available | yes | Used for local diagnostics only; static evidence is not treated as acceptance of hosted behavior. |
| Git/GitHub read-only metadata | available | yes | Confirmed current revision and absence of the requested local/remote release target; no write operation. |
| Hosted GitHub Actions/release-please run | unavailable | no | No hosted run target was supplied or safely available in this environment. |
| Cargo/npm/GHCR/GitHub publication | available in principle | rejected | Explicitly prohibited by the request; no registry state was mutated. |
| Browser/API/data/persistence capability | not applicable | no | CodeGauge distribution is a CLI, package, workflow, archive, and OCI target; it has no browser/API/data-store surface. |
| Accessibility/responsive/locale capability | not applicable | no | No UI or locale-dependent acceptance contract is defined for this change. |
| Manual/exploratory shell checks | available | yes | Used for repeated invocation, negative paths, process passthrough, and local release smoke behavior. |

## Scenario Matrix

Every scenario has one allowed result: `PASS`, `FAIL`, `BLOCKED`, or `NOT TESTED`.

| ID | Capability | Acceptance scenario | Result | Evidence or reason |
|---|---|---|---|---|
| CI-1 | Hosted CI | An untrusted pull request runs read-only without release credentials or publication ability. | BLOCKED | Local permission audit passed, but no hosted pull-request run or credential-isolation observation was available. |
| CI-2 | Workflow validation | A mutable action reference causes validation to fail before distribution starts. | BLOCKED | All 33 external workflow action references were locally audited as full 40-hex SHAs and `actionlint` passed; no mutable-reference injection was run. Static inspection is not acceptance execution. |
| CI-3 | Local quality runner | Pinned metadata, locked tests, format, Clippy, and Python contract/distribution checks all pass. | PASS | Exact local commands passed: `cargo +1.97.1 metadata --locked`, workspace tests, fmt, Clippy `-D warnings`, bootstrap, README, distribution, release-provenance, OCI, and npm-generator checks. Evidence log directory: `/tmp/codegauge-qa-quality.xCHfzU`. |
| CI-4 | Failure injection | A known Clippy failure remains blocking and does not weaken linting or engine behavior. | NOT TESTED | Current Clippy passes; no source or workflow mutation was made to inject a failure. Rerun requires an isolated failure-injection branch or hosted run. |
| CI-5 | Provenance validator | An incomplete target declaration prevents later distribution eligibility. | PASS | Removing one of eight archive manifests caused `verify_release_provenance.py archives` to exit nonzero with `expected 8 archive manifests, found 7`; no publisher was invoked. |
| CI-6 | Hosted release graph | A failed preflight blocks later publishers and retains failure evidence. | BLOCKED | Workflow dependency/fail-stop wiring was audited locally, but no hosted failure-injection run was permitted or available. |
| CARGO-1 | Cargo registry | The approved runtime graph packages and publishes in dependency order. | BLOCKED | All five runtime crates packaged locally and the leaf `cargo publish --dry-run` passed; actual crates.io publication/order observation was prohibited. |
| CARGO-2 | Cargo/source runtime | A repository/source install builds with the pinned lockfile and exposes the released contracts. | PASS | Real `cargo +1.97.1 install --path crates/codegauge-cli --locked` succeeded. Installed binary returned `codegauge 0.1.0`, `java-jacoco-v1`, and a `COMPLETE` `codegauge-result/v1` analysis. |
| CARGO-3 | Immutable source runtime | An immutable recorded Git revision installs and preserves version/profile/analysis behavior. | BLOCKED | The checkout has no `v0.1.0` tag or recorded release revision target; only the current dirty source was exercised. |
| CARGO-4 | RFC-0001 runtime audit | Distribution-only changes preserve RFC-0001 observable behavior and contracts. | PASS | Baseline `6477eb1` and current binaries matched exit codes, stdout JSON, stderr, version, profiles, and seven fixture behaviors after masking only `analysis_timestamp`; 9 cases passed. Evidence: `/tmp/codegauge-qa-rfc.R9LVn3/rfc-full-comparison.json`. |
| CARGO-5 | Cargo package failure path | A package missing a required file stops before registry upload. | NOT TESTED | Complete local package checks passed; no missing-file package rehearsal was run. Rerun requires an isolated temporary package fixture or hosted preflight failure. |
| CARGO-6 | Version/provenance validator | A manifest/binary/version mismatch blocks release validation. | PASS | Local provenance tests rejected version `9.9.9`, invalid tag identity, mismatched main SHA, wrong binary version, and archive source-revision drift. |
| NPM-1 | npm packaging | Only the approved base package and six same-scope platform packages are eligible. | PASS | Generator check, all six manifest checks, base `npm pack --dry-run`, six platform `npm pack --dry-run` checks, and local typed preflight passed. |
| NPM-2 | npm runtime | A supported runtime resolves exactly its matching optional dependency and executable. | PASS | On host `darwin/arm64`, the wrapper resolved `@yacosta738/codegauge-darwin-arm64`; real version, profiles, and analysis calls returned the expected contracts. |
| NPM-3 | npm negative runtime | Missing optional dependency, unsupported OS, and musl Linux return actionable nonzero errors without running another binary. | PASS | Missing dependency returned nonzero with an actionable reinstall message; process-platform overrides returned nonzero for `freebsd/x64` and Linux musl with explicit supported-target/libc messages. |
| NPM-4 | npm process passthrough | Arguments, stdin/stdout/stderr, and child exit status pass through unchanged. | PASS | Synthetic child received `analyze --profile java-jacoco-v1`, echoed stdin, emitted argv on stderr, and exited `17`; wrapper returned `17`. |
| NPM-5 | npm checksum gate | A corrupted archive/sidecar stops both platform and base package eligibility. | PASS | npm test passed the corruption regression with `platformEligible=false` and `baseEligible=false`; the release archive validator separately rejected tampered bytes with `archive checksum mismatch`. |
| REL-1 | Release provenance | A release is derived from an immutable release-please tag on merged `main`, with one version/source identity across channels. | BLOCKED | Local validator wiring and negative checks passed, but `v0.1.0` is absent locally and the GitHub Release lookup returned `release not found`; no hosted release-please execution was run. |
| REL-2 | Archive matrix | The complete eight-target release has correct formats, names, manifests, checksums, and executable/runtime evidence. | BLOCKED | Local packager created and verified 8/8 archive formats, names, lowercase sidecars, and manifests, but the local set used explicit cross-target `execution=not-run` evidence for non-host binaries; hosted/native matrix evidence was not available. |
| REL-3 | Archive negative gate | Missing target evidence prevents assets and dependent registries from proceeding. | PASS | Seven-of-eight manifest validation exited nonzero before any upload or publisher command. |
| REL-4 | Release ordering | Checksum/package/metadata failure prevents later channel publishers. | BLOCKED | Local validators and workflow dependency ordering were inspected; no hosted release graph was executed with an injected failing gate. |
| REL-5 | Release security | Credential exposure fails promotion and secrets do not enter artifacts/logs. | BLOCKED | No credential-bearing release run, registry login, or attestation was performed; local workflow audit found no committed token literal, but behavior on an exposed-token run was not exercised. |
| REL-6 | Partial publication recovery | A later npm/OCI failure stops subsequent jobs, retains history, and exposes a corrected recovery path. | BLOCKED | No publication or failure injection was allowed. README/workflow recovery guidance exists, but no observable partial-publication state or rollback rehearsal was produced. |
| OCI-1 | OCI publication | Only `ghcr.io/yacosta738/codegauge` is eligible for the approved image release. | BLOCKED | Local workflow identity/permission checks passed; GHCR login, push, and registry identity observation were explicitly not run. |
| OCI-2 | OCI negative validator | An unsupported architecture is rejected rather than claimed. | PASS | Executable OCI verifier negative test rejected `linux/ppc64le`. |
| OCI-3 | Local Docker runtime | Workspace-aware images build for amd64/arm64, run non-root with init, and expose version/profile/analysis contracts. | PASS | Real local Buildx builds and Docker loads passed for both architectures. Both reported `codegauge 0.1.0`, `java-jacoco-v1`, `codegauge-result/v1` `COMPLETE`, UID `100`, user `codegauge`, and `/sbin/tini` entrypoint. Evidence: `/tmp/codegauge-qa-oci.18eCHz/{amd64,arm64}.evidence.json`. |
| OCI-4 | OCI metadata/failure validator | Label, runtime version, root user, emulation, or digest mismatch prevents image eligibility. | PASS | Executable positive/negative verifier suite passed for label drift, runtime version drift, root UID, missing arm64 emulation evidence, metadata digest drift, and Docker/OCI digest-domain mismatch. |
| OCI-5 | OCI publication gate | A failed architecture prevents manifest/tag publication. | BLOCKED | Real positive amd64/arm64 builds passed, but no architecture failure injection or registry manifest publication was run. |
| RFC-1 | Manual/exploratory runtime | Repeated source invocations preserve results, while negative/boundary/hostile inputs preserve error mappings and schemas. | PASS | Source QA exercised repeatability, partial exit `6`, unsupported profile `4`, missing input `3`, malformed/duplicate/DOCTYPE input `5`, and unsupported format `2`; all outputs matched the expected JSON/error contracts. |
| RFC-2 | Immutable release runtime | The actual released tag/archive/image preserves RFC-0001 contracts after distribution publication. | BLOCKED | No immutable release tag, published archive, registry package, or remote OCI digest was available to run this acceptance smoke. |

## Untested Scope

| Scope | Reason | Re-run prerequisite |
|---|---|---|
| Hosted pull-request CI permission isolation and injected workflow failures | No hosted runner execution was supplied; static checks cannot establish runtime acceptance. | Run CI on an untrusted PR and an isolated negative workflow fixture; capture job permissions, skipped downstream jobs, and retained logs. |
| Immutable release-please tag/main/release URL provenance | Current checkout has no `v0.1.0` tag and no matching GitHub Release. | Run from a release-please-created tag on merged `main`; capture tag SHA, main SHA, release URL, and positive validator output. |
| Native/runtime evidence for seven non-host archive targets | Local host is macOS arm64; cross-target packaging records `execution=not-run`. | Execute the configured native/cross-target hosted matrix and retain binary version/profile/contract evidence for every claimed target. |
| Cargo/npm/GitHub Release/GHCR publication and attestations | Explicitly prohibited; no registry state may be mutated in this QA run. | Obtain an approved release window and credentials, then run the gated dry-run/publication path with secret-safe logs. |
| Partial publication and rollback recovery | No publisher was allowed to fail after a prior channel succeeded. | Use a disposable release rehearsal or provider-supported test namespace; inject a later-channel failure and record stop/deprecation/corrected-patch actions. |
| Missing Cargo package-file failure rehearsal | Complete packages passed and production files must not be altered. | Use a temporary copied package fixture and verify that the registry gate exits before publication. |

## Findings

| ID | Severity | Scenario / location | Evidence | Status |
|---|---|---|---|---|
| QA-001 | P1 | Hosted release provenance and cross-registry publication (`REL-1`, `REL-4`–`REL-6`, `OCI-1`, `RFC-2`) | No `v0.1.0` tag or GitHub Release; no Cargo/npm/GHCR/GitHub write or attestation run by policy. | Open — external acceptance gate; blocks archive. |
| QA-002 | P1 | Complete release target acceptance (`REL-2`, `CARGO-3`) | Local archive set is structurally complete, but non-host binary evidence is explicitly `cross-target/execution=not-run`; no immutable revision install. | Open — hosted/native target evidence required; blocks archive. |
| QA-003 | P2 | Failure-injection coverage (`CI-2`, `CI-4`, `CI-6`, `CARGO-5`, `OCI-5`) | Local actionlint/validators and fail-stop wiring pass, but no injected failing hosted/package/architecture run was performed. | Open — rerun prerequisite; no observed implementation failure. |
| QA-004 | P2 | Release recovery rehearsal (`REL-6`) | Recovery guidance is documented, but no partial publication state, registry deprecation, retag, or corrected-patch rehearsal exists. | Open — external rehearsal required; warning only after acceptance gate is unblocked. |

No `FAIL` result and no `CRITICAL`/P0 finding was observed in the executable local acceptance scope.

## Verdict

`BLOCKED`

### Rationale

Local acceptance evidence is strong for the executable surfaces: pinned source installation, version/
profiles/analysis and error contracts, npm host resolution and process passthrough, checksum stop paths,
archive generation and local verification, RFC-0001 runtime equivalence, and real non-root amd64/arm64
Docker builds all passed. However, the requested distribution capability includes acceptance of an
immutable release provenance chain, complete target evidence, ordered external publication, final OCI
manifest/attestation, and non-atomic recovery. Those scenarios were intentionally not executed because
publication, credentials, and registry mutation were prohibited and no hosted release target exists in
this environment. Under the QA/archive policy, acceptance-relevant `BLOCKED` scope normally blocks
archive; the verdict therefore cannot be `PASS` or `PASS WITH WARNINGS`.

## Evidence Summary

- Local quality suite: all exact Rust/Python distribution checks passed; `/tmp/codegauge-qa-quality.xCHfzU`.
- Cargo/source QA: installed binary passed version, profiles, complete/partial analysis, negative CLI,
  hostile input, and repeatability checks; `/tmp/codegauge-qa-source.YgP6tj/source-qa.json`.
- Cargo package QA: all five runtime crates passed locked package verification with local patch
  configuration; `/tmp/codegauge-qa-cargo-package.bftj1K`.
- npm QA: typecheck, 7 tests, base pack, and six platform packs passed; `/tmp/codegauge-qa-npm.wWkhpJ`.
- npm runtime QA: host package selection, analysis, missing dependency, unsupported platform, musl
  rejection, stdin/argv/exit passthrough passed; `/tmp/codegauge-qa-npm-runtime2.*`.
- Archive QA: 8/8 local archive formats, 8/8 lowercase sidecars, 8/8 manifests, positive provenance,
  checksum tamper rejection, and 7/8 incomplete-matrix rejection passed; `/tmp/codegauge-qa-archives.93hohU`.
- OCI QA: local verifier passed both architecture evidence files and preserved distinct Docker config,
  Docker platform, OCI config/platform/index, and BuildKit metadata digests; `/tmp/codegauge-qa-oci.18eCHz`.
- RFC-0001 audit: baseline/current runtime comparison passed for version, profiles, and all seven XML
  fixtures after masking only the timestamp; `/tmp/codegauge-qa-rfc.R9LVn3/rfc-full-comparison.json`.
- Workflow diagnostics: `actionlint`, `shellcheck`, distribution checks, release-provenance tests,
  and OCI tests passed. All workflow actions were locally confirmed to use immutable full-SHA refs.

## Limitations and Handoff

- QA did not modify source code, workflows, credentials, release state, or `state.yaml`.
- This report does not claim Cargo, npm, GitHub Release, GHCR, or product acceptance.
- Recommended next step: rerun `sdd-qa` from an immutable release-please tag on merged `main` with
  approved hosted-runner evidence and a safe, authorized release rehearsal. Run `sdd-archive` only
  after the blocked acceptance scenarios are resolved or an explicit policy exception is recorded.
