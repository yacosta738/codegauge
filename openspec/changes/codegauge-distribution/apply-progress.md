# Apply Progress: CodeGauge distribution remediation

## Scope

- Change: `codegauge-distribution`
- Remediation units: `R-C`, `R-D`, `R-E`, `R-F1–R-F6` (Release Please ownership and tag carrier)
- Delivery strategy: `feature-branch-chain`
- Layer boundary: `distribution-e-oci-remediation`, based on the existing dirty worktree baseline;
  no branch or commit was created.
- Out of scope: registry credentials, publication, and branch/PR creation; `state.yaml` was updated
  only to record this apply handoff and the unresolved R-F6 blocker.

## Completed Tasks

- [x] R-C — Added typed npm preflight checksum, archive-manifest, package-version, source-revision,
  platform metadata, and base-wrapper eligibility checks.
- [x] R-C — Added a pure-local corrupted-archive regression test proving both platform and base npm
  publication eligibility are false.
- [x] R-C — Updated `npm-preflight` and `publish-npm` to checkout the exact requested tag, verify the
  checkout resolves to that tag, and reject npm version/source-revision drift before publication.
- [x] R-C — Extended Python distribution assertions and npm package tests; constrained the published
  base package file list to the wrapper entrypoint.
- [x] R-D — Restricted release execution to release-please workflow outputs (`release_tag`, exact
  `release_sha`, merged-main `main_sha`, and release URL); removed arbitrary pushed-tag publication
  and unsafe default/manual publication fallback.
- [x] R-D — Added `scripts/verify_release_provenance.py` for immutable tag/main identity, Cargo.lock,
  Cargo/npm versions, six platform pins, linked release-please components, archive manifests,
  checksums, binary version/profiles, and explicit native/cross-target evidence.
- [x] R-D — Changed GitHub Release handling to validate the release-please-created release and use
  `gh release upload --clobber`; removed duplicate `gh release create`.
- [x] R-D — Added focused provenance regression tests, archive binary-evidence metadata, and static
  distribution assertions for release workflow wiring and all six linked npm components.
- [x] R-E — Added `tests/oci_distribution_tests.py` with static ordering/failure-stop assertions and
  synthetic OCI verifier regression coverage for labels, output digests, runtime contracts, emulation,
  and non-root behavior.
- [x] R-E — Added `scripts/verify_oci_evidence.py` to inspect an OCI layout, validate BuildKit/config/
  manifest digests and OCI labels, require non-root/runtime evidence, and persist machine-readable
  per-architecture evidence.
- [x] R-E — Reworked `.github/workflows/release.yml` to export local OCI/Docker outputs without
  public/versioned architecture tags, load and inspect each architecture, run version/profiles/contract
  smoke and non-root checks, require explicit arm64 QEMU evidence, then push final architecture tags
  and create the version/latest manifest only from verified digests. Remote pushed config digests and
  final manifest child digests are checked against the per-architecture evidence before attestation.
- [x] R-E — Added OCI checks to CI/release static gates and preserved least-privilege scoped publishing
  plus final manifest artifact attestation.
- [x] Final remediation — Corrected every step-prefixed `actions/checkout` reference in CI and
  release workflows to the verified lowercase 40-hex v4.2.2 commit, retaining comments.
- [x] Final remediation — Added only `id-token: write` to the `publish-release` job permissions for
  `actions/attest-build-provenance`.
- [x] Final remediation — Extended `tests/distribution_checks.py` to validate both step-prefixed
  and direct `uses:` action references and to require the release attestation OIDC permission.
- [x] R-E digest-domain remediation — Reproduced the real Docker amd64/arm64 exporter outputs and
  confirmed that `docker image inspect` `.Id` is the Docker platform-manifest digest while the
  Docker archive config and OCI config are separate digest domains. Added the required
  `--docker-archive` input, validated Docker `manifest.json`/config/index data, compared inspect
  identity to Docker-derived identities, retained separate OCI config/platform/index/metadata
  evidence, and updated the release workflow and negative/positive tests.
- [x] D3 release-workflow topology — Reduced `release.yml` to an 84-line caller that preserves both
  trigger schemas and all five release inputs; added `release-build.yml` for provenance, quality,
  archive, Cargo/npm preflight, and release verification/artifacts; added `release-publish.yml` for
  gated ordered Cargo/GitHub Release/npm/OCI publication and final attestations. The caller passes
  every input to both reusable workflows and gates publication on the completed build workflow.
- [x] D3 OCI extraction — Moved the OCI build/inspect/runtime verification commands into
  `scripts/build_oci_release.sh`, retaining fail-stop local exports and evidence uploads in the
  build workflow before the publish caller runs. The publish workflow downloads and loads those
  verified Docker artifacts before registry login, push, manifest creation, or attestation.

## TDD Evidence

1. RED: `python3 tests/oci_distribution_tests.py` failed against the pre-remediation workflow because
   the architecture inspection step did not exist before the test assertions; subsequent focused RED
   runs also exposed missing local-output, digest, runtime, and failure-stop wiring.
2. GREEN: `python3 tests/oci_distribution_tests.py` passed after adding local OCI/Docker outputs,
   synthetic OCI verification, runtime evidence commands, and digest-gated publication.
3. REFACTOR: removed shell heredoc parsing that triggered actionlint/ShellCheck warnings, replaced it
   with `jq`, made BuildKit metadata/config/platform digests explicit, and re-ran focused tests plus
   actionlint.
4. Negative coverage passes for runtime version drift, missing QEMU evidence, root runtime, and
   metadata digest drift.
5. Final remediation RED: `python3 tests/distribution_checks.py` failed with malformed checkout
   references and missing `publish-release` OIDC permission.
6. Final remediation GREEN: the focused distribution regression passed after the two minimal
   workflow fixes; actionlint and all requested regression checks remained green.
7. R-E digest-domain RED: the new synthetic Docker/OCI fixture failed against the old verifier with
   `docker inspect image ID differs from the OCI config digest`, despite Docker inspect matching the
   Docker archive's config digest.
8. R-E digest-domain GREEN/REFACTOR: the verifier now passes the distinct-domain fixture, rejects
   Docker-ID drift, and handles the real Docker Buildx amd64/arm64 archives where inspect `.Id`
   matches the Docker platform-manifest digest; naming was split into `docker_config_digest`,
   `docker_platform_digest`, `oci_config_digest`, `platform_digest`, `oci_index_digest`, and
   `metadata_digest`.
9. D3 topology RED: updated the distribution, release-provenance, and OCI static checks to require
   the caller/reusable-workflow split before creating the new workflow files; the focused checks
   failed on missing build/publish workflows and caller jobs.
10. D3 topology GREEN/REFACTOR: the split caller and reusable workflows, cross-workflow artifact
    handoff, OCI helper extraction, and topology-aware assertions now pass the focused suites;
    actionlint and extracted workflow ShellCheck also pass.

## Commands Run

- `python3 tests/oci_distribution_tests.py` — exit 0; static ordering and synthetic OCI evidence/
  failure-path checks pass.
- `python3 tests/distribution_checks.py` — exit 0.
- `python3 tests/release_provenance_tests.py` — exit 0.
- `python3 tests/bootstrap_checks.py` — exit 0.
- `python3 tests/readme_checks.py` — exit 0.
- `python3 scripts/generate_npm_packages.py --check` — exit 0.
- `python3 -m py_compile tests/oci_distribution_tests.py scripts/verify_oci_evidence.py
  tests/distribution_checks.py` — exit 0.
- `actionlint .github/workflows/*.yml` — exit 0; extracted OCI shell blocks also pass ShellCheck.
- `cargo test --workspace --locked` — exit 0; 31 Rust tests passed, 0 failed, 0 skipped.
- `cargo check --workspace --locked` — exit 0.
- `cargo fmt --all -- --check` — exit 0.
- `cargo clippy --workspace --all-targets --locked -- -D warnings` — exit 0.
- `git diff --check` — exit 0.
- Real Docker Buildx amd64/arm64 export/build/load/inspect/runtime smoke and fixed verifier — exit 0;
  both architectures passed with non-root UID 100, version `codegauge 0.1.0`, profile
  `java-jacoco-v1`, complete contract JSON, and QEMU arm64 evidence. Evidence recorded distinct
  Docker config/platform and OCI config/platform/index/metadata digests.
- Synthetic R-E digest-domain RED — exit 1 against the pre-fix verifier with the expected OCI-config
  mismatch message; synthetic GREEN/negative suite — exit 0.
- ShellCheck extracted OCI workflow block — exit 0. Running ShellCheck directly on YAML is not a
  valid workflow check and reports unrelated YAML/expression parse noise.
- Exact fixed real-Docker digest evidence from `/tmp/codegauge-oci-r-e-fixed`:

  | Platform | Docker config | Docker platform manifest / inspect `.Id` | OCI config | OCI platform | OCI index | BuildKit metadata |
  |---|---|---|---|---|---|---|---|
  | `linux/amd64` | `sha256:83ecc5eeaa53d1d33723ee8c948cab7d76c1c9e4b1a4700dd4ec1932e2083bcd` | `sha256:8a8d58a63d44f397acbd0e09f4e38e553c94333dc01d1718c9df1a6897e181e2` | `sha256:83ecc5eeaa53d1d33723ee8c948cab7d76c1c9e4b1a4700dd4ec1932e2083bcd` | `sha256:8a8d58a63d44f397acbd0e09f4e38e553c94333dc01d1718c9df1a6897e181e2` | `sha256:0a3022741722c0f5ec54d205a15bc62cb8e125af1a2804c92b3f20ed9e4382d1` | `sha256:8a8d58a63d44f397acbd0e09f4e38e553c94333dc01d1718c9df1a6897e181e2` |
  | `linux/arm64` | `sha256:8cdaca1c1fd80ade07cb7ec506f31be8e1e89d2ecdea5a2219255129188b7821` | `sha256:300da2b8eda6c83d114881a08d77364b19d26601438e3d24f4ae75bba33aa9db` | `sha256:8cdaca1c1fd80ade07cb7ec506f31be8e1e89d2ecdea5a2219255129188b7821` | `sha256:300da2b8eda6c83d114881a08d77364b19d26601438e3d24f4ae75bba33aa9db` | `sha256:be1e4b6e180cc6fbcd3b3c7c64790f70bca0ef45eed79c0f0a77275af6153d27` | `sha256:300da2b8eda6c83d114881a08d77364b19d26601438e3d24f4ae75bba33aa9db` |
- GHCR pushes, final manifest creation, attestations, registry writes, and credentials were not run;
  the local Docker daemon was available for this remediation's real amd64/arm64 build/inspect/run
  smoke.
- Final remediation focused suite: `python3 tests/distribution_checks.py` — exit 0; all action
  references, including `- uses:` lines, have exact 40-character lowercase SHA refs and
  `publish-release` has `id-token: write`.
- D3 focused suite: `python3 tests/distribution_checks.py`, `python3 tests/release_provenance_tests.py`,
  and `python3 tests/oci_distribution_tests.py` — exit 0 after the reusable-workflow topology split.
- D3 workflow lint: `actionlint .github/workflows/*.yml` — exit 0; direct `shellcheck
  scripts/build_oci_release.sh` — exit 0; extracted workflow `run` blocks checked with ShellCheck
  at error severity — exit 0.
- D3 npm regression: `npm --prefix npm/codegauge test` — exit 0; 6 tests passed after retaining the
  existing required checksum publication regression in the TypeScript preflight boundary.
- D3 integrity: `git diff --check` — exit 0; no commit, branch, push, publication, credentials, or
  `state.yaml` mutation performed.

## D3 Review Workload Estimates

- `release.yml`: 84-line caller; against the staged 717-line monolith this is approximately 18
  additions plus 651 deletions (669 changed lines), while the resulting caller itself is reviewable.
- `release-build.yml`: 343 added lines, below the 400-line work-unit target.
- `release-publish.yml`: 329 added lines, below the 400-line work-unit target.
- `scripts/build_oci_release.sh`: 90 added lines; focused topology-test edits remain below the
  400-line test-layer budget and no unrelated production code was changed.

## Remaining

- Hosted release/tag verification, hosted multi-architecture build/runtime evidence, GHCR push, final
  manifest/attestation, and registry rollback rehearsal remain external gates; local real Docker
  amd64/arm64 build/load/inspect/runtime evidence for this remediation is complete.
- No branch, commit, push, publish, or state.yaml mutation was performed.

## R-F6 apply execution — 2026-08-14

### Layer and scope

- Change: `codegauge-distribution`; approved R-F6 two-stage Release Please/tag-carrier architecture.
- Work unit: F6.1 → F6.4 implementation and local verification on the existing
  `fix/release-please-root-files` branch; no commit, branch, merge, tag, publication, credential, or
  parent-repository mutation was performed.
- Stage A: Release Please `17.6.0` component-tagged synchronized version PR with the supported action
  `skip-github-release: true`; the action has no release outputs or publication caller.
- Stage B: trusted `main` push carrier derives the merged-tree version, validates one merged Release
  Please PR and the complete runtime graph, compare-and-creates one lightweight `vX.Y.Z`, closes the
  pending PR label, and relies on the non-`GITHUB_TOKEN` tag push to start the tag caller. Manual
  dispatch is explicit recovery plumbing and defaults to dry-run.

### Completed R-F6 tasks

- [x] 1.1 — Source-faithful v17.6.0 regression now covers the virtual Cargo root candidate, exact
  13-entry linked map, Node optional dependency rewriting, root extra-file ownership, npm-relative
  path, private conformance exclusion, suppressed component-prefixed tags, and one Stage-A PR.
- [x] 1.2 — Carrier fixtures cover positive validation, wrong ref, unexpected merge SHA, duplicate
  merged PRs, graph drift, missing `Cargo.lock`/release manifest, invalid/bootstrap versions,
  conflicting/annotated tags, same-SHA idempotency, and existing-release conflicts.
- [x] 1.3 — Static checks cover Stage-A/Stage-B separation, action SHA pins, carrier permissions and
  secret selection, main/tag trigger invariants, concurrency, no tag deletion/force update, and
  post-gate release ownership.
- [x] 2.1 — Config and manifest now use component tags for linking, a Java root metadata carrier,
  root-anchored typed extra-files, package-relative npm metadata, a non-merging Node workspace,
  thirteen linked runtime paths, and release skips for every Stage-A candidate.
- [x] 2.2 — `.github/workflows/release-please.yml` is a pinned Release Please 17.6.0 version-PR-only
  job using the supported action skip input and `RELEASE_PLEASE_TOKEN`; it no longer consumes release
  outputs or invokes the release/publish workflow.
- [x] 3.1 — `verify_release_provenance.py` now provides pure carrier records, semver/tree/manifest/
  lockfile/private-boundary validation, merged-PR label/body/diff validation, clean-checkout support,
  ancestry validation for tag releases, and compare-and-create tag planning.
- [x] 3.2 — `release-tag-carrier.yml` is restricted to trusted `main` pushes, uses non-canceling
  concurrency and read-only workflow permissions, authenticates Git ref/label writes only with
  `RELEASE_PLEASE_TOKEN`, rejects conflicts, and never deletes or force-updates tags.
- [x] 3.3 — `release-on-tag.yml` is the canonical `v*.*.*` caller with guarded recovery dispatch;
  reusable release workflows now accept tag/SHA/recovery inputs, validate current-main ancestry, and
  create or verify the GitHub Release only after build/package gates.
- [x] 4.1 — Focused, static, locked Cargo, npm, package dry-run, OCI, and workflow checks pass.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** `python3 tests/release_provenance_tests.py` failed on the exact v17.6.0
   `LinkedVersions.preconfigure()` empty-component gate with the existing
   `include-component-in-tag: false` configuration; `python3 tests/release_carrier_tests.py` failed
   because the carrier boundary did not yet exist; and `python3 tests/distribution_checks.py` failed
   because the carrier workflow was absent.
2. **GREEN:** after enabling component tags, adding the supported Stage-A skip input, implementing the
   carrier validators/workflows, and wiring the tag caller, `tests/release_provenance_tests.py`,
   `tests/release_carrier_tests.py`, `tests/distribution_checks.py`, and `actionlint` all passed.
   The source-faithful test observed all 13 linked versions at `0.2.0`, six rewritten optional pins,
   root update ownership, and zero Stage-A tag/release operations.
3. **REFACTOR:** extracted carrier metadata, PR, semver, clean-tree, ancestry, release-slot, and tag
   plan helpers; added compare-and-create retry handling, PR label completion, recovery inputs, and
   exact full-SHA/static security checks; focused tests remained green.

### Local verification commands

- `python3 tests/release_carrier_tests.py` — PASS.
- `python3 tests/release_provenance_tests.py` — PASS.
- `python3 tests/distribution_checks.py` — PASS.
- `python3 tests/bootstrap_checks.py` — PASS.
- `python3 tests/readme_checks.py` — PASS.
- `python3 tests/oci_distribution_tests.py`, `tests/oci_distribution_static_tests.py`,
  `tests/oci_distribution_evidence_tests.py`, and `tests/oci_distribution_failure_tests.py` — PASS.
- `python3 -m compileall -q scripts tests` — PASS.
- `python3 scripts/generate_npm_packages.py --check` — PASS.
- `cargo metadata --locked --format-version 1` — PASS.
- `cargo test --workspace --locked` — PASS; 31 tests passed, 0 failed, 0 skipped.
- `cargo fmt --all -- --check` — PASS.
- `cargo clippy --workspace --all-targets --locked -- -D warnings` — PASS.
- `npm --prefix npm/codegauge run typecheck` and `npm --prefix npm/codegauge test` — PASS; 6 tests
  passed.
- `npm pack --dry-run` from the wrapper and all six platform package directories — PASS.
- `actionlint .github/workflows/*.yml` — PASS.
- `git diff --check` — PASS.

### External verification not performed

- Hosted Release Please 17.6.0 execution, the synchronized PR merge, PAT scope/masking/ref
  authorization, branch-protection behavior, carrier API race rehearsal, canonical tag delivery, and
  tag-triggered workflow execution were not run.
- No GitHub Release, Cargo/npm/GHCR publication, upload, attestation, tag, credential, or hosted
  dry-run write evidence is claimed.
- Native evidence for the seven non-host targets remains unavailable; existing local OCI/package
  checks were read-only/static or dry-run checks.

## Release Please root/config remediation

- [x] R-F1 — Added deterministic provenance regressions for the explicit `packages["."]` root
  candidate, root-anchored repository extra-files, package-relative npm extra-files, unprefixed
  linked tags, private conformance exclusion, and synchronized npm optional dependency versions.
- [x] R-F2 — Moved repository extra-files under the root package, anchored them with leading `/`
  paths, changed the npm wrapper extra-file to `package.json`, added the minimal non-merging
  `node-workspace` plugin, and linked the root candidate as `codegauge-root` to avoid a second
  root release candidate.
- [x] R-F3 — Imported `read_workspace_version` in the provenance regression and changed the CLI
  release-version assertion to derive its expected output from `env!("CARGO_PKG_VERSION")`.
- [x] R-F4 — Updated the distribution gate to inspect root-owned release extra-files rather than
  the removed inheritable top-level list.

### R-F TDD Evidence

1. RED: the baseline `python3 tests/release_provenance_tests.py` failed with
   `NameError: name 'read_workspace_version' is not defined`.
2. RED: after adding the regression assertions, the focused test failed because top-level
   `extra-files` were still present.
3. GREEN: after the configuration fix, the focused test failed on the hard-coded CLI
   `codegauge 0.1.0` assertion, proving the release-version regression was covered.
4. GREEN/REFACTOR: after deriving the CLI expected version from `CARGO_PKG_VERSION`, the focused
   provenance and CLI suites passed; the distribution gate was updated to the new root ownership
   boundary and passed.

### R-F Verification

- `python3 tests/release_provenance_tests.py` — exit 0; pass.
- `python3 tests/distribution_checks.py` — exit 0; pass.
- `python3 tests/bootstrap_checks.py` — exit 0; pass.
- `python3 tests/readme_checks.py` — exit 0; pass.
- `python3 -m compileall -q scripts tests` — exit 0; pass.
- `cargo metadata --locked --format-version 1` — exit 0; pass.
- `cargo test --workspace --locked` — exit 0; 31 tests passed, 0 failed, 0 skipped.
- `cargo fmt --all -- --check` — exit 0; pass.
- `cargo clippy --workspace --all-targets --locked -- -D warnings` — exit 0; pass.
- `actionlint .github/workflows/*.yml` — exit 0; pass.
- `git diff --check` — exit 0; pass.
- Additional focused checks: `cargo test -p codegauge-cli --test cli --locked`,
  `npm --prefix npm/codegauge test`, and `python3 scripts/generate_npm_packages.py --check` —
  exit 0; pass.

No commit, push, merge, tag, publication, package/release creation, credential use, or
`state.yaml` mutation was performed.

## E3a Test Layer

- [x] Replaced the executable `tests/distribution_checks.py` entrypoint with a 27-line runner
  that imports only the E3a helper module.
- [x] Added `tests/distribution_checks_e3a.py` with Cargo metadata/version/license, workspace
  member, private conformance, locked graph, baseline CI, and release caller/reusable-workflow
  topology/input propagation checks.
- [x] Preserved the former 732-line distribution suite byte-for-byte as
  `tests/distribution_checks_later.py`; npm, archive, OCI, and documentation checks remain
  available for later runner layers. Existing `release_provenance_tests.py` and
  `oci_distribution_tests.py` were not modified.
- [x] E3a implementation is 301 added lines across the runner and focused helper, excluding the
  preserved pre-existing untracked suite.

### E3a TDD and Verification

- RED: the pre-layer runner failed in an isolated copy when deferred OCI checks were unavailable.
- GREEN: the E3a runner passed after the deferred suite was removed from the isolated copy.
- Verification: distribution, bootstrap, README, Python compilation, and whitespace checks pass;
  no production files, branches, commits, credentials, publication, or `state.yaml` changes were
  made.

## Release Please Cargo parser compatibility follow-up

- [x] Confirmed all six crate package manifests declare the synchronized literal `version = "0.1.0"`
  and the root workspace version remains the canonical `0.1.0` value.
- [x] Confirmed `release-please-config.json` contains the TOML extra-file mapping for
  `/Cargo.toml` at `$.workspace.package.version`; the focused distribution regression accepts the
  configuration and rejects package-version drift.
- [x] Fresh focused validation passed: `tests/release_provenance_tests.py`,
  `tests/distribution_checks.py`, `tests/oci_distribution_static_tests.py`,
  `tests/oci_distribution_evidence_tests.py`, `tests/oci_distribution_failure_tests.py`,
  `python3 -m compileall -q scripts tests`, `cargo metadata --locked --no-deps --format-version 1`,
  `cargo check --workspace --all-targets --locked`, `actionlint`, and `git diff --check`.
- [x] No defect was exposed, so no additional production/configuration change was required and no
  task checkbox or `state.yaml` entry was mutated.
- [x] A local `release-please manifest-pr --dry-run` invocation was inspected but could not run:
  the repository has no installed/local release-please CLI, and `npx --no-install` refused to
  fetch the missing package. No credentials or hosted release operation were used.

## Verification recheck — 2026-08-14

- Fresh local quality evidence remains green: the focused Python checks, locked Cargo metadata/
  tests/check/fmt/Clippy, CLI integration tests, npm typecheck/tests, package generator check,
  actionlint, and `git diff --check` all exited 0; the workspace reported 31 passed tests.
- **CRITICAL verification finding:** the exact Release Please 17.6.0 `cargo-workspace` source skips
  a virtual root `Cargo.toml` without `[package].name` and returns candidates only from its package
  graph. Because the configured root candidate is `release-type: "rust"`, the new `packages["."]`
  candidate is consumed and dropped before its root extra-file updates can survive the plugin chain.
- R-F2 is therefore not behaviorally verified despite its apply checkbox. Removing the old inherited
  top-level `extra-files` list leaves no surviving Release Please owner for the repository-level
  README, fixture, contract test, CLI test, and root Cargo TOML update.
- The current regressions validate JSON shape and current npm version equality, but no passing test
  executes Release Please 17.6.0 to prove root-candidate survival, optional-pin rewriting, or one
  unprefixed release operation. The report records this as `FAIL`, not acceptance.
- No code, branch, commit, push, merge, tag, publication, credential, or registry state was changed
  during verification.

## Release Please virtual-root remediation — 2026-08-14

- [x] R-F1 — Replaced the static-only Release Please assertions with a deterministic model of the
  exact v17.6.0 `cargo-workspace`, `node-workspace`, `linked-versions`, and unprefixed-tag boundary.
  The regression uses the repository's real Cargo/package manifests, a new `0.2.0` version map, and
  effective candidate/update results rather than checking only JSON keys.
- [x] R-F2 — Changed `packages["."]` from the discarded virtual-root Rust candidate to a Java
  strategy used only as a typed root extra-file carrier. `initial-version: 0.1.0`,
  `skip-changelog`, `skip-snapshot`, and `skip-github-release` are explicit; no root `package-name`
  exists. A global release skip is overridden only for `codegauge-cli`, preserving the existing
  release workflow output and one unprefixed tag.
- [x] R-F3 — Preserved the earlier `read_workspace_version` import, dynamic `CARGO_PKG_VERSION` CLI
  assertion, package-relative npm path, and node-workspace optional-dependency synchronization.
- [x] R-F4 — Updated the release-artifacts spec, design decision, and task record to document the
  virtual-root boundary and the non-Cargo metadata-candidate rationale.

### Root-boundary TDD Evidence

1. RED: after adding `assert_release_please_17_6_0_root_pipeline`,
   `python3 tests/release_provenance_tests.py` failed at the modeled v17.6.0 Cargo workspace
   boundary because the existing `release-type: "rust"` root candidate was dropped.
2. GREEN: after changing the root candidate to the non-Cargo metadata strategy, adding the explicit
   skip/release ownership boundary, and updating the expected typed extra-files, the focused test
   passed. It observed root candidate retention, root update paths after linked merge, six optional
   pins rewritten to `0.2.0`, and exactly one `v0.2.0` operation for `codegauge-cli`.
3. REFACTOR: extracted candidate, Cargo workspace, Node optional-dependency, linked merge, and tag
   helpers while keeping the focused test green.

### Architecture Evidence

- Release Please 17.6.0's Cargo workspace source skips a virtual root without `[package].name` and
  reconstructs returned candidates from package-backed graph nodes. The root is therefore outside
  both Cargo and Node workspace scopes by using `release-type: "java"`.
- The Java strategy is not a published root package: it carries only typed root extra-file updates,
  starts from the existing `0.1.0` manifest baseline, has no `package-name`, and explicitly skips
  its GitHub release/changelog/snapshot. The CLI is the sole release-capable component, so
  `include-component-in-tag: false` yields one unprefixed tag.
- This local regression models the exact v17.6.0 source boundary but does not execute the installed
  Release Please package or hosted action. Executable Release Please 17.6.0 behavior remains
  externally unverified pending a safe local package/hosted dry-run.

### Commands Run

- `python3 tests/release_provenance_tests.py` — RED exit 1 on the discarded Rust root candidate;
  GREEN/REFACTOR exit 0 after the configuration and model fix.
- `python3 tests/distribution_checks.py` — exit 0; pass.
- `python3 tests/bootstrap_checks.py` — exit 0; pass.
- `python3 tests/readme_checks.py` — exit 0; pass.
- `python3 -m compileall -q scripts tests` — exit 0; pass.
- `cargo metadata --locked --format-version 1` — exit 0; pass.
- `cargo test --workspace --locked` — exit 0; 31 passed, 0 failed, 0 skipped.
- `cargo fmt --all -- --check` — exit 0; pass.
- `cargo clippy --workspace --all-targets --locked -- -D warnings` — exit 0; pass.
- `actionlint .github/workflows/*.yml` — exit 0; pass.
- `npm --prefix npm/codegauge run typecheck` — exit 0; pass.
- `npm --prefix npm/codegauge test` — exit 0; 6 passed, 0 failed, 0 skipped.
- `python3 scripts/generate_npm_packages.py --check` — exit 0; pass.
- `git diff --check` — exit 0; pass.

## Verification recheck — 2026-08-14 (second apply)

- Fresh local verification passed for `tests/release_provenance_tests.py`, `tests/distribution_checks.py`,
  bootstrap/README checks, all four OCI regression layers, Python compilation, locked Cargo metadata,
  31 workspace tests, the 3-test CLI integration suite, Cargo check/fmt/Clippy, npm typecheck/tests,
  seven npm pack dry-runs, package generation, actionlint, and `git diff --check`.
- Exact `release-please@17.6.0` was available locally for a read-only `--version` check and its
  packaged source was inspected. The source confirms that the corrected Java root candidate survives
  Cargo/Node workspace filtering, typed `/...` root extra-files resolve at repository root, and the
  Node updater includes optional dependencies.
- A source-faithful local model passed root retention, exact five-file ownership, package-relative
  npm path, new-version optional-pin rewriting, private conformance exclusion, and exactly one
  `v0.2.0` CLI release operation. Four negative mutations were rejected.
- **CRITICAL verification finding:** the exact v17.6.0 `BaseStrategy.getComponent()` returns an empty
  component whenever `include-component-in-tag` is false. The exact `LinkedVersions.preconfigure()`
  skips empty components. The current global unprefixed-tag setting therefore leaves the configured
  13-component linked group empty; the regression helper uses JSON candidate components and manually
  unions updates instead of executing this gate. Optional dependency synchronization from the linked
  versions map is not behaviorally proven and is ineffective for a Cargo/root-only release path.
- No product code, workflow, branch, commit, tag, release, publication, credential, or registry state
  was changed during verification. The exact hosted Release Please dry-run and external publication
  gates remain unexecuted.

## Release Please v17.6.0 linked-version/tag blocker remediation — 2026-08-14

- [x] R-F5 — Reworked `tests/release_provenance_tests.py` into a source-faithful regression for the
  exact v17.6.0 strategy path: effective per-package config, Cargo virtual-root candidate retention,
  `BaseStrategy.getComponent()`, `LinkedVersions.preconfigure()`, the full Cargo/npm runtime versions
  map, `NodeWorkspace.combineDeps()`, `PackageJson.updateContent()` optional-dependency rewriting,
  linked candidate merging, and `TagName` unprefixed output. The assertion requires all 13 intended
  runtime paths (root metadata carrier, five runtime Cargo crates, npm wrapper, and six platform
  packages) to resolve to `0.2.0`; it does not merely check JSON keys or current literal pins.
- [x] R-F5 — Preserved the existing Java root candidate, five root-anchored extra-files, relative npm
  `package.json` extra-file, provenance import, dynamic `env!("CARGO_PKG_VERSION")` assertion, virtual
  Cargo root, and private `codegauge-conformance` boundaries. `release-please-config.json` was not
  changed because the exact source proves the apparent per-package workaround would violate the
  required tag contract.
- [x] R-F5 — Confirmed the exact source semantics from the installed `release-please@17.6.0` tarball:
  `BaseStrategy.getComponent()` returns `''` when `includeComponentInTag` is false;
  `LinkedVersions.preconfigure()` skips the falsy component before checking membership;
  `NodeWorkspace.combineDeps()` includes `optionalDependencies`; `PackageJson.updateContent()`
  rewrites them from its versions map; and `TagName` emits an unprefixed tag only for a falsy
  component.
- [x] R-F5 — A direct isolated runtime probe against the exact package showed named linked components
  force all fixture strategies to `0.2.0` but produce `codegauge-cli-v0.2.0`; the current global false
  configuration finds zero linked components. An empty string added to the linked component list was
  also rejected by the exact source because the plugin skips empty components before membership.

### Linked/tag TDD evidence

1. **RED:** after the source-faithful gate and full versions-map assertions were added,
   `python3 tests/release_provenance_tests.py` failed with
   `AssertionError: Release Please 17.6.0 LinkedVersions.preconfigure produced no full runtime map;
   include-component-in-tag=false makes every strategy component empty`.
   This is the expected failure against the current global `include-component-in-tag: false` config.
2. **GREEN:** not reached for the checked-in single-manifest architecture. The exact source probe
   proves that setting linked packages to `include-component-in-tag: true` would make preconfigure
   work but would emit a component-prefixed tag, violating the existing one-tag contract.
3. **REFACTOR:** the regression now derives the optional dependency rewrite from the simulated linked
   versions map and derives tag text from the simulated `getComponent()` result; no JSON-shape-only
   assertion was retained.

### Architecture decision required

Release Please 17.6.0 has no valid single built-in manifest configuration that both enables linked
version synchronization and makes the same strategy emit one unprefixed tag: the former requires a
truthy strategy component and the latter requires a falsy one. The smallest safe resolution is a
two-stage architecture: use component tags only while Release Please generates the synchronized
version PR (with release creation skipped), then use a trusted post-merge carrier to validate the
graph and create exactly one `vX.Y.Z` tag for the existing build/publish workflows. A supported
Release Please upgrade/plugin with independent linked-component lookup is the alternative. R-F6
remains unchecked until one of those architectures is implemented and independently verified.

### Commands Run

- `python3 tests/release_provenance_tests.py` — exit 1 (expected RED against the unresolved current
  single-manifest config; no false GREEN claim).
- Exact package source inspection: `npm pack release-please@17.6.0`, isolated package install, and
  read-only source/runtime probes — source gate confirmed; no GitHub API, credentials, tag, release,
  or publication operation.
- Exact `PackageJson` runtime probe against the installed v17.6.0 source — exit 0; all six optional
  dependency pins rewrote to `0.2.0` while `^`/`~` range prefixes were preserved.
- `python3 tests/distribution_checks.py` — exit 0.
- `python3 tests/bootstrap_checks.py` — exit 0.
- `python3 tests/readme_checks.py` — exit 0.
- `python3 tests/oci_distribution_tests.py`, `tests/oci_distribution_static_tests.py`,
  `tests/oci_distribution_evidence_tests.py`, and `tests/oci_distribution_failure_tests.py` — exit 0.
- `python3 -m compileall -q scripts tests` — exit 0.
- `python3 scripts/generate_npm_packages.py --check` — exit 0.
- `cargo metadata --locked --format-version 1 --no-deps` — exit 0; six workspace packages and no
  virtual-root package.
- `cargo test --workspace --locked` — exit 0; 31 passed, 0 failed, 0 skipped.
- `cargo test -p codegauge-cli --test cli --locked` — exit 0; 3 passed.
- `cargo check --workspace --locked`, `cargo fmt --all -- --check`, and
  `cargo clippy --workspace --all-targets --locked -- -D warnings` — exit 0.
- `npm --prefix npm/codegauge run typecheck` and `npm --prefix npm/codegauge test` — exit 0; 6 npm
  tests passed.
- `npm pack --dry-run` from the base package and each of the six platform package directories — exit 0;
  seven packages inspected.
- `actionlint .github/workflows/*.yml` — exit 0.
- `git diff --check` — exit 0.

The first attempted `npm --prefix npm/codegauge pack --dry-run` invocation was rejected by the local
npm CLI because it resolved the repository root; rerunning the same dry-run from each package
directory passed for all seven packages. This is a command-line invocation quirk, not a package
content failure.

### Remaining

- [ ] R-F6 — Implement the approved option-1 two-stage tag carrier that decouples linked-component
  lookup from canonical tag naming.
- [ ] Re-run the focused regression GREEN/REFACTOR and the complete conformance matrix.
- [ ] Run a safe hosted Release Please dry-run/tag rehearsal only after the architecture is executable;
  no hosted release, publication, credential, or registry evidence is claimed here.

## R-F6 architecture authorization — 2026-08-14

- [x] Option 1 is authorized: component-tagged Release Please 17.6.0 version PR with release
  creation skipped, followed by a trusted post-merge carrier for exactly one immutable `vX.Y.Z` tag.
- [ ] Implementation, hosted execution, tag/release creation, publication, and verification remain
  pending. This entry records the design decision only; no workflow or application code was changed.

## R-F6 task breakdown handoff — 2026-08-14

- [x] Replaced the stale whole-change checklist with the authorized R-F6 implementation breakdown;
  earlier A–E and R-C–R-F5 work remains documented above.
- [x] Ordered source-faithful RED tests before Stage 1 configuration, then carrier, tag workflow,
  verification, and hosted rehearsal; recorded feature-branch-chain dependencies.
- [ ] At this handoff, implementation, tag/release creation, publication, and SDD verification/QA
  remained pending; the verification entry below supersedes the verification portion.
- [x] No code, branch, commit, push, merge, tag, credential, registry write, or public release was
  performed while creating this task artifact.

## R-F6 verification — 2026-08-14

### Verification result

- [x] Re-ran the focused carrier, provenance, static workflow, Python, locked Cargo, npm, package,
  OCI, compileall, actionlint, ShellCheck, Dockerfile check, and diff suites locally.
- [x] Confirmed the immutable Release Please action boundary from the v5.0.0 source/lockfile:
  the action resolves `release-please` 17.6.0 and skips `Manifest.createReleases()` when
  `skip-github-release: true`.
- [x] Confirmed no local or remote `v*.*.*` tag was created and the worktree remained free of
  publication, credential, registry, and hosted workflow writes.
- [ ] R-F6 is not technically accepted: the carrier validation boundary has confirmed defects.

### Confirmed verification findings

1. `validate_stage_a_diff()` rejects a runtime `CHANGELOG.md` path. Exact Release Please 17.6.0
   Rust and Node strategies add `CHANGELOG.md` updates with `createIfMissing: true` unless
   `skip-changelog` is set; the current config sets that flag only on the root Java carrier.
   A legitimate Stage-A PR therefore fails in Stage B before tag creation.
2. The carrier diff pattern `npm/packages/codegauge-[^/]+/package.json` accepts an unapproved
   platform package path, and the carrier tree validator accepts a missing root-owned README.
3. `VERSION_RE` accepts malformed semver such as `1.01.0`, so the carrier can plan a malformed
   canonical tag before later Cargo validation.
4. The linked-version/no-publication regression is a source-faithful Python model plus static
   checks; no executable Release Please SCM/PR run was performed. Hosted Stage-A and tag-triggered
   behavior remains unproven under the explicit no-write boundary.

### Local evidence

- Focused carrier/provenance/distribution/OCI/Python suites passed before the semantic probes.
- The semantic probe intentionally failed with all four findings above, proving the missing
  negative coverage rather than treating static shape as sufficient.
- Rust 1.97.1 metadata/tests/check/fmt/Clippy, npm typecheck/tests and seven pack dry-runs,
  five Cargo package verifications, archive positive/missing-target checks, Dockerfile
  `buildx --check`, actionlint, ShellCheck, compileall, and `git diff --check` passed.

### Remaining gates

- [ ] Fix the carrier validation boundary, then rerun `sdd-verify`.
- [ ] Run the protected hosted Stage-A zero-artifact and tag-triggered dry-run rehearsal.
- [ ] Run `sdd-qa` for independent acceptance; no publication or registry write is authorized here.

## Stage-B carrier defect remediation — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; assigned slice is the four verified Stage-B carrier defects plus
  the requested exact Release Please runtime coverage.
- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Layer boundary: `trunk=main`, `parent_branch=fix/release-please-root-files`,
  `base=existing dirty remediation baseline`, `branch=fix/release-please-root-files`,
  `position=R-F6 carrier-defect repair after the existing F6.1–F6.4 work unit`; no Stack metadata,
  branch creation, commit, push, merge, tag, release, publication, credential, or parent-repository
  mutation was performed.
- Hosted Stage-A/tag rehearsal and QA remain out of scope and unchecked in `tasks.md`.

### Completed tasks

- [x] 5.1 — Replaced the broad npm diff regex with an exact allowlist derived from the base wrapper and
  six approved platform package names. Added the exact twelve runtime `CHANGELOG.md` paths generated
  by the v17.6.0 Rust/Node strategies; arbitrary, unknown, near-match, root, nested, and evil paths
  remain rejected.
- [x] 5.2 — Added an exact root-carrier presence check for `Cargo.toml`, `README.md`, the golden
  fixture, the model contract test, and the CLI test. Generated release-only files are not treated as
  baseline carrier files.
- [x] 5.3 — Replaced permissive version matching with strict SemVer 2.0 core, prerelease, and build
  metadata identifiers. Canonical tag planning now rejects leading-zero and malformed versions.
- [x] 5.4 — Added `tests/release_please_runtime_tests.py` and
  `tests/release_please_runtime_harness.mjs`. The exact installed `release-please@17.6.0` package
  executed its Manifest, Cargo workspace, Node workspace, linked-versions, and merge chain against a
  read-only fake SCM; it recorded one synchronized fake PR, runtime update paths, six rewritten npm
  optional pins, and zero release/tag calls. Missing exact package installations report `UNTESTED`
  rather than substituting JSON-shape assertions.
- [x] 5.5 — Focused and requested local checks are green; no hosted or publication state was touched.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** after adding exact changelog, npm allowlist, root-file mutation, and SemVer regressions,
   `python3 tests/release_carrier_tests.py` failed on the legitimate
   `crates/codegauge-model/CHANGELOG.md` path, reproducing the Stage-B defect before the production
   validator was changed.
2. **GREEN:** after replacing the regex with exact sets, adding root-file presence validation, and
   implementing strict SemVer 2.0 matching, `python3 tests/release_carrier_tests.py` passed all
   positive/negative mutations and canonical tag cases.
3. **REFACTOR:** the allowlist is derived from the approved runtime constants, the root ownership
   check is isolated as `validate_root_carrier_files`, and the SemVer fragments are shared by tag and
   version validation; focused tests remained green.
4. **Runtime coverage:** the exact v17.6.0 package-level chain passed with a no-write fake SCM and
   observed `generatedUpdatePaths`, `releaseVersion: 0.2.0`, all six optional dependency rewrites,
   `synchronizedPullRequests: 1`, `releaseCalls: 0`, and `tagCalls: 0`. This is local source/runtime
   evidence only, not hosted PR, tag, release, or publication evidence.

### Local verification commands

- `python3 tests/release_carrier_tests.py` — PASS.
- `python3 tests/release_carrier_static_tests.py` — PASS.
- `python3 tests/release_provenance_tests.py`, `tests/distribution_checks.py`,
  `tests/bootstrap_checks.py`, and `tests/readme_checks.py` — PASS.
- `python3 tests/release_please_runtime_tests.py` — PASS against exact installed `release-please`
  `17.6.0`; fake SCM recorded zero release/tag calls.
- `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` —
  PASS.
- `cargo +1.97.1 metadata --locked --format-version 1`, `test --workspace --locked`,
  `check --workspace --locked`, `fmt --all -- --check`, and locked Clippy with `-D warnings` — PASS
  (31 workspace tests, 0 failed).
- npm wrapper typecheck/tests — PASS (6 tests); wrapper plus six platform `npm pack --dry-run` checks —
  PASS (7 packages).
- All four OCI regression layers, `actionlint`, `shellcheck scripts/build_oci_release.sh`,
  `docker buildx build --check --progress=plain .`, and `git diff --check` — PASS.

### Remaining gates and risks

- [ ] 4.2 hosted Stage-A zero-artifact and tag-triggered no-publication rehearsal.
- [ ] 4.3 downstream `sdd-verify` and independent `sdd-qa`; no acceptance claim is made here.
- The exact runtime harness records the complete raw v17.6.0 update list. That raw list includes
  release-only absent lock/sample/changelog entries and a private conformance Cargo candidate created
  by the upstream Cargo workspace dependency graph; the harness does not apply those updates and does
  not claim hosted changed-file behavior. The carrier allowlist remains limited to the approved
  baseline/runtime set and this observation should be dispositioned by the next verification phase.
- No credentials, GitHub API writes, tags, releases, registry publication, upload, attestation, merge,
  push, or commit was performed.

## Verification recheck — 2026-08-15

- [x] Re-ran the focused carrier/static/provenance/distribution/Python/OCI suites, exact
  `release-please@17.6.0` runtime harness, locked Cargo metadata/tests/check/fmt/Clippy, five Cargo
  package checks, npm typecheck/tests and seven pack dry-runs, actionlint, ShellCheck, Dockerfile
  check, compileall, package generation, and `git diff --check`; all requested local commands passed.
- [x] Confirmed the requested exact-path behavior: all 12 approved runtime changelogs and the base
  wrapper plus six approved npm manifests pass; arbitrary/evil/near-match paths fail; every one of
  the five Java root-carrier file deletions fails closed; strict SemVer cases pass.
- [x] Confirmed the no-write runtime harness executes the exact Manifest/plugin chain and records one
  fake PR, six optional dependency rewrites, `releaseCalls=0`, and `tagCalls=0`.
- [ ] **Verification remains FAIL:** the exact runtime update list includes the existing private
  `crates/codegauge-conformance/Cargo.toml`, whose v17.6.0 CargoToml updater changes `0.1.0` to
  `0.1.1`; `validate_stage_a_diff()` rejects that unapproved path. The harness records proposed
  updates instead of applying `GitHub.buildChangeSet()`, so absent non-created files are additional
  raw proposals, but the existing conformance manifest is a real local defect.
- [ ] Hosted Stage-A/tag-triggered no-publication rehearsal and downstream QA remain prohibited or
  unavailable; no credentials, releases, tags, publication, or registry state were touched.

## Private Stage-A candidate boundary remediation — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; assigned slice is the remaining critical private-candidate
  boundary after the latest R-F6 verification failure.
- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Layer boundary: `trunk=main`, `parent_branch=fix/release-please-root-files`,
  `base=existing dirty remediation baseline`, `branch=fix/release-please-root-files`,
  `position=R-F6 private-candidate boundary repair`; no Stack metadata, branch creation, commit,
  push, merge, tag, release, publication, credential, or parent-repository mutation was performed.
- Cargo workspace membership, `publish = false`, Stage-B exact allowlists/root-file checks/SemVer
  hardening, full-SHA actions, permissions, concurrency, idempotency, and fail-closed behavior were
  left intact.

### Completed tasks

- [x] 6.1 — Added an exact-harness assertion that fails on any
  `crates/codegauge-conformance/*` Stage-A update and added a runtime regression that passes a
  mutated private manifest through `validate_stage_a_diff()` and requires `ProvenanceError`.
- [x] 6.2 — Removed the unsupported v17.6.0 `cargo-workspace` plugin from Stage A. The explicit
  five runtime Cargo candidates remain configured. The Java root metadata carrier now owns typed
  TOML updates for the five approved runtime `Cargo.lock` package entries and only the internal
  dependency version fields in the four dependent runtime manifests; the selectors do not address
  `codegauge-conformance`.
- [x] 6.3 — Extended the exact harness to verify all five runtime Cargo package versions, synchronized
  internal pins, private lock-version preservation, six npm optional pins, one synchronized PR, and
  zero release/tag calls. Updated the design/spec/task records with the exact v17.6.0 source
  boundary and the explicit-list architecture.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** after adding the private-path assertion to the existing exact v17.6.0 Manifest/plugin
   harness, `python3 tests/release_please_runtime_tests.py` exited 1 with
   `Stage-A update set contains private conformance candidates:
   crates/codegauge-conformance/Cargo.toml, crates/codegauge-conformance/CHANGELOG.md`. This was
   the real upstream `CargoWorkspace` graph defect, not a JSON-only test.
2. **GREEN:** after removing `cargo-workspace` and adding the explicit runtime/root-carrier
   boundary, the same exact harness passed and recorded `synchronizedPullRequests=1`, six optional
   dependency rewrites to `0.2.0`, `releaseCalls=0`, `tagCalls=0`, no private conformance path, and
   `PRIVATE CANDIDATE MUTATION: REJECTED`.
3. **REFACTOR:** kept Stage B unchanged, centralized the explicit root-carrier contract in the
   provenance validator/tests, added the Cargo.lock/private-preservation and internal-pin runtime
   assertions, and reran the focused carrier/provenance/static suites green.

### Local verification

- `python3 tests/release_please_runtime_tests.py` — PASS against exact installed Release Please
  `17.6.0`; one fake PR, six optional rewrites, zero release/tag calls, private path absent, private
  mutation rejected.
- `python3 tests/release_provenance_tests.py`, `tests/release_carrier_tests.py`,
  `tests/release_carrier_static_tests.py`, `tests/distribution_checks.py`,
  `tests/bootstrap_checks.py`, and `tests/readme_checks.py` — PASS.
- `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` —
  PASS; all four OCI regression layers — PASS.
- `cargo +1.97.1 metadata --locked --format-version 1`, workspace test/check/fmt/Clippy gates, and
  all five locked Cargo package verification commands — PASS (Cargo only warned that package tests
  are not included).
- npm wrapper typecheck/tests — PASS (6 tests); wrapper plus six platform `npm pack --dry-run`
  checks — PASS (7 packages).
- `actionlint .github/workflows/*.yml`, `shellcheck scripts/build_oci_release.sh`,
  `docker buildx build --check --progress=plain .`, and `git diff --check` — PASS.

### Remaining gates and risks

- [ ] Task `4.2` protected hosted Stage-A/tag-triggered no-publication rehearsal.
- [ ] Task `4.3` downstream `sdd-verify` and independent `sdd-qa`; no user/operator acceptance is
  claimed by apply.
- Exact hosted SCM changed-file filtering, PAT scope/ref authorization, branch protection, tag
  delivery, tag-triggered workflows, registry publication, attestation, rollback/failure injection,
  and native non-host target evidence remain externally unverified and unauthorized.

## R-F6 verification rerun — 2026-08-15

### Verification result

- [x] Re-ran `sdd-verify` against the current dirty checkout and updated OpenSpec artifacts.
- [x] The exact installed `release-please@17.6.0` Manifest/plugin chain ran against the read-only
  fake SCM: one synchronized PR, six optional-dependency rewrites to `0.2.0`, zero release calls,
  zero tag calls, and no private conformance candidate.
- [x] A read-only probe of the exact v17.6.0 `GitHub.prototype.buildChangeSet` filtered the raw
  `Update[]` proposals using the same missing-file/create-if-missing behavior as the real SCM. The
  effective set was exactly the approved 31 paths: seven root metadata/carrier files, five runtime
  Cargo manifests, twelve runtime changelogs, and seven npm manifests. It contained no
  `crates/codegauge-conformance/Cargo.toml`, virtual-root package, or unapproved path.
- [x] Stage-B positive, negative, mutation, strict-SemVer, idempotency, conflict, and canonical-tag
  tests passed; generated runtime changelogs were accepted and private/unapproved/missing/malformed
  states were rejected.
- [x] Full local Rust, Python, npm, OCI, workflow, shell, Dockerfile, package, and whitespace
  checks passed without credentials or hosted writes.

### Exact effective Stage-A path set

```text
Cargo.toml
Cargo.lock
.release-please-manifest.json
README.md
tests/golden/valid-methods.json
crates/codegauge-model/tests/contracts.rs
crates/codegauge-cli/tests/cli.rs
crates/codegauge-model/Cargo.toml
crates/codegauge-core/Cargo.toml
crates/codegauge-application/Cargo.toml
crates/codegauge-provider-jacoco/Cargo.toml
crates/codegauge-cli/Cargo.toml
crates/codegauge-model/CHANGELOG.md
crates/codegauge-core/CHANGELOG.md
crates/codegauge-application/CHANGELOG.md
crates/codegauge-provider-jacoco/CHANGELOG.md
crates/codegauge-cli/CHANGELOG.md
npm/codegauge/package.json
npm/codegauge/CHANGELOG.md
npm/packages/codegauge-linux-x64-gnu/package.json
npm/packages/codegauge-linux-x64-gnu/CHANGELOG.md
npm/packages/codegauge-linux-arm64-gnu/package.json
npm/packages/codegauge-linux-arm64-gnu/CHANGELOG.md
npm/packages/codegauge-darwin-x64/package.json
npm/packages/codegauge-darwin-x64/CHANGELOG.md
npm/packages/codegauge-darwin-arm64/package.json
npm/packages/codegauge-darwin-arm64/CHANGELOG.md
npm/packages/codegauge-win32-x64-msvc/package.json
npm/packages/codegauge-win32-x64-msvc/CHANGELOG.md
npm/packages/codegauge-win32-arm64-msvc/package.json
npm/packages/codegauge-win32-arm64-msvc/CHANGELOG.md
```

The checked-in fake SCM records the upstream raw proposals before `buildChangeSet`; those raw
proposals include absent files that v17.6.0 drops when `createIfMissing` is false. The effective-set
probe above exercised the exact v17.6.0 filtering boundary and is the evidence used by verification.

### Local verification commands

- `python3 tests/release_please_runtime_tests.py`, `tests/release_carrier_tests.py`,
  `tests/release_carrier_static_tests.py`, `tests/release_provenance_tests.py`,
  `tests/distribution_checks.py`, `tests/bootstrap_checks.py`, and `tests/readme_checks.py` — PASS.
- `python3 tests/oci_distribution_tests.py`, `tests/oci_distribution_static_tests.py`,
  `tests/oci_distribution_evidence_tests.py`, and `tests/oci_distribution_failure_tests.py` — PASS.
- `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` — PASS.
- `cargo +1.97.1 metadata --locked --format-version 1`, workspace tests (31 passed), check, fmt,
  locked Clippy, and five runtime `cargo package` checks — PASS.
- npm wrapper typecheck/tests (6 passed) and wrapper plus six platform `npm pack --dry-run` checks — PASS.
- `actionlint .github/workflows/*.yml`, `shellcheck scripts/build_oci_release.sh`,
  `docker buildx build --check --progress=plain .`, and `git diff --check` — PASS.

### Remaining warnings

- [ ] Task `4.2`: protected hosted Stage-A zero-artifact and tag-triggered no-publication rehearsal.
- [ ] Task `4.3`: downstream `sdd-qa` acceptance evidence.
- PAT scope/masking/ref authorization, branch protection, tag delivery, hosted workflow execution,
  publication, attestation, rollback/failure injection, and native non-host evidence remain outside
  the no-write boundary.
- The checked-in harness currently records raw proposals; the exact effective-set filtering probe was
  run read-only and was not committed as a harness change.

### Technical verdict

**PASS WITH WARNINGS** — every requested local contract passes, and the remaining risks are hosted or
acceptance evidence only. No commit, push, merge, tag, release, publication, upload, attestation,
credential injection, or hosted write was performed.

## R-F6 acceptance QA — 2026-08-15

### QA execution

- [x] Read the proposal, all five delta specs, design, tasks, latest verification report, state,
  apply progress, config, and current R-F6 implementation before testing.
- [x] Ran the exact installed Release Please `17.6.0` Manifest/plugin chain with a read-only fake SCM;
  observed one synchronized PR, six optional dependency rewrites, zero release/tag calls, and no
  private conformance candidate. The unchanged Stage-B private mutation was rejected.
- [x] Ran Stage-B positive/negative/root-presence/private-boundary/strict-SemVer/idempotency/conflict
  fixtures, provenance/version/lockfile checks, Cargo quality/package checks, npm checks, archive
  checksum/missing-target checks, OCI regression suites, and real local amd64/arm64 OCI build/load/run
  evidence without registry writes.
- [x] Ran actionlint, ShellCheck, Dockerfile `buildx --check`, and diff diagnostics. These remain
  static diagnostics, not acceptance passes.
- [x] Persisted the independent acceptance record at
  `openspec/changes/codegauge-distribution/qa-report.md`.

### QA boundary and verdict

- [ ] Hosted Stage-A/merged-main/tag-triggered rehearsal, publication, attestation, native non-host
  archive execution, failure injection, and rollback remain unrun because they require prohibited
  hosted writes, credentials, or unavailable native targets.
- [ ] No CRITICAL/P0 local implementation defect was observed; P1 acceptance blockers remain for
  hosted lifecycle/provenance, publication/attestation, and complete native target evidence.
- QA verdict: **BLOCKED**. This is an acceptance gate, not a product-acceptance claim.
- Recommended next phase: `sdd-archive` only after the blocked acceptance scope is resolved or an
  explicit policy exception is approved. No publication or registry mutation is authorized by this
  QA run.

## Temporary hosted carrier rehearsal guard — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; assigned slice is the temporary, auditable Stage-B carrier
  rehearsal guard requested for the authorized option-1 flow.
- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Layer boundary: `trunk=main`, `parent_branch=fix/release-please-root-files`,
  `base=existing dirty remediation baseline`, `branch=fix/release-please-root-files`,
  `position=F6.5 temporary hosted-rehearsal guard after F6.4`; no Stack metadata, branch creation,
  commit, push, merge, tag, release, publication, credential use, or parent-repository mutation was
  performed.
- Hosted rehearsal remains out of scope for apply and remains unchecked in `tasks.md` (`4.2` and
  `7.4`).

### Completed tasks

- [x] 7.1 — Added static carrier assertions and runtime carrier regressions for trusted
  `workflow_dispatch` on `main`, manual dry-run input handling, repository-variable push mode, live
  default behavior, conditional tag/label writes, and plan evidence.
- [x] 7.2 — Refactored `.github/workflows/release-tag-carrier.yml` to normalize manual `dry_run` or
  `vars.RELEASE_CARRIER_DRY_RUN`, share collection/validation, compute a read-only canonical tag plan,
  emit `carrier-record.json`/`carrier-plan.json` plus a workflow summary, and guard all tag/label
  mutations behind live mode. The workflow never directly dispatches `release-on-tag.yml`.
- [x] 7.3 — Documented the exact `RELEASE_CARRIER_DRY_RUN` variable, manual command, plan evidence,
  and variable cleanup in the README and updated the design/spec/QA handoff without claiming hosted
  execution.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** after adding the manual event and dry-run/mutation-plan assertions first,
   `python3 tests/release_carrier_tests.py`, `python3 tests/release_carrier_static_tests.py`, and
   `python3 tests/distribution_checks.py` failed. The runtime validator rejected
   `workflow_dispatch`, and the static suite reported the missing input, variable normalization, plan
   record, and conditional mutation contracts.
2. **GREEN:** after accepting trusted `workflow_dispatch` in
   `validate_carrier_event()` and adding the mode/plan/mutation guards to the carrier workflow, all
   three focused commands passed.
3. **REFACTOR:** separated the read-only GitHub ref/release observation and `carrier-plan.json` summary
   from the live tag/label steps, tightened shell quoting and invalid-value failure behavior, and
   reran `actionlint` with the focused suites green.

### Verification and remaining gates

- Final local verification passed: `python3 tests/release_carrier_tests.py`,
  `tests/release_carrier_static_tests.py`, `tests/release_provenance_tests.py`,
  `tests/distribution_checks.py`, `tests/bootstrap_checks.py`, `tests/readme_checks.py`, and
  `tests/release_please_runtime_tests.py` (one synchronized PR, six optional rewrites, zero release/
  tag calls, private mutation rejected).
- Final local verification passed: `tests/oci_distribution_tests.py`,
  `tests/oci_distribution_static_tests.py`, `tests/oci_distribution_evidence_tests.py`,
  `tests/oci_distribution_failure_tests.py`, `python3 -m compileall -q scripts tests`, and
  `python3 scripts/generate_npm_packages.py --check`.
- Final locked Rust gates passed: `cargo +1.97.1 metadata --locked --format-version 1`,
  `cargo +1.97.1 test --workspace --locked` (31 passed, 0 failed, 0 skipped), `cargo +1.97.1 check
  --workspace --locked`, `cargo +1.97.1 fmt --all -- --check`, and locked Clippy with `-D warnings`.
- Final package gates passed for all five runtime crates with locked `cargo package --allow-dirty`
  verification; the first clean-worktree invocation correctly stopped on the intentionally dirty
  README, then the configured dirty-worktree package command passed.
- Final npm gates passed: wrapper typecheck/tests (6 tests) and `npm pack --dry-run` for the wrapper
  plus all six platform packages (7 packages).
- Final workflow/OCI/whitespace gates passed: `actionlint .github/workflows/*.yml`,
  `shellcheck scripts/build_oci_release.sh`, `docker buildx build --check --progress=plain .`, and
  `git diff --check`.
- [ ] Task `4.2` / `7.4`: protected hosted Stage-A/merged-main/manual dry-run rehearsal and no-write
  observation remain pending.
- [ ] Task `4.3`: downstream `sdd-verify` and independent `sdd-qa` remain required; apply claims no
  operator or product acceptance.
- No hosted writes, GitHub API mutations, tag/label changes, release dispatch, upload, publication,
  attestation, credential injection, merge, push, or commit was performed.

## SDD verification executor rerun — 2026-08-15

### Scope and safety boundary

- Re-read the proposal, all five delta specs, design, tasks, current diff, workflows, carrier
  implementation/tests, apply history, state, and QA report before judging the implementation.
- No commit, push, merge, repository-variable change, tag, release, upload, registry publication,
  attestation, credential injection, or hosted write was performed.
- The checkout remains intentionally dirty; strict-TDD commit ordering is therefore not independently
  provable. `strict_tdd: true` is configured, but the referenced `strict-tdd-verify.md` module is not
  present in the installed skill directory.

### Fresh local evidence

- Carrier/provenance/distribution/bootstrap/README/runtime Python checks passed. The exact
  `release-please@17.6.0` fake-SCM run recorded one synchronized PR, six optional pin rewrites,
  zero release calls, zero tag calls, and rejected the private-candidate mutation.
- All four OCI regression layers, Python compileall, npm package generation, locked Cargo metadata,
  31 workspace tests, Cargo check/fmt/Clippy, five locked Cargo package checks, npm typecheck/tests,
  seven npm pack dry-runs, actionlint, ShellCheck, Dockerfile `buildx --check`, and `git diff --check`
  passed.
- The exact carrier mode step passed manual true/false, push variable true/false/unset, and invalid
  value cases. The exact dry-run plan/summary/guard steps passed with a read-only fake `gh`; the plan
  contained no credential field and recorded skipped tag/label, not-dispatched tag workflow, and
  not-started publication mutations. This supplemental probe was not added as a repository test.

### Remaining gates

- [ ] Task `4.2` protected hosted Stage-A/tag-triggered no-publication rehearsal.
- [ ] Task `4.3` downstream `sdd-qa` acceptance evidence.
- [ ] Task `7.4` hosted variable-controlled and manual carrier rehearsal.
- Hosted PAT scope/masking/ref authorization, branch protection, tag delivery, publication,
  attestation, rollback/failure injection, and native non-host target evidence remain unverified.

## Hosted conformance dependency-resolution failure — 2026-08-15

### Evidence and boundary correction

- Hosted PR `#59` is the first real Stage-A observation: the five public runtime Cargo packages and
  npm packages synchronized to `0.2.0`; Stage A made no release or tag calls.
- The merged PR then failed CI at `cargo metadata --locked` because
  `crates/codegauge-conformance/Cargo.toml` still required
  `codegauge-application`, `codegauge-core`, `codegauge-model`, and
  `codegauge-provider-jacoco` at `^0.1.0` while the workspace contained `0.2.0`.
- This invalidates the earlier exclusion-only expectation that the private manifest must be absent
  from the effective Stage-A update set. It does not invalidate the private candidate/release/tag
  boundary.

### Corrected minimal exception

- The Java `codegauge-root` metadata carrier must own the existing private manifest path through
  exactly four TOML JSONPaths: `$.dependencies["codegauge-application"].version`,
  `$.dependencies["codegauge-core"].version`, `$.dependencies["codegauge-model"].version`, and
  `$.dependencies["codegauge-provider-jacoco"].version`.
- The update value is the synchronized public runtime version only. The private
  `[package].version` remains `0.1.0`; `publish = false`, the private `Cargo.lock` package version,
  no conformance changelog, no release metadata, no linked component, and no private release/tag
  candidate remain mandatory.
- Stage-B must receive complete PR patch or verified before/after content. It may allow the private
  path only when the semantic and textual change set contains exactly those four dependency-version
  replacements. Package metadata/version, dependency keys/paths/features, comments/formatting,
  changelog, missing/truncated patch, or any other path must fail closed before tag/label/release/
  upload/publication mutation.
- The source-faithful v17.6.0 harness and carrier tests must expect one root-owned private update,
  32 effective Stage-A paths, four pins at the public version, six npm optional rewrites, one PR,
  and zero release/tag calls. `cargo metadata --locked` is the required convergence gate.

### Pending work and safety status

- [ ] Implement the Phase 9 RED/GREEN/REFACTOR tasks in `tasks.md`; no source or workflow fix was
  made in this entry.
- [ ] Re-run local verification, then obtain a separately authorized protected hosted rehearsal.
- The corrected boundary is designed but neither implemented nor hosted-verified. No commit, push,
  merge, tag, release, publication, credential use, upload, attestation, or parent-repository
  mutation was performed.

## Carrier event-correlation defect remediation — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; assigned slice is the hosted-discovered Stage-B carrier
  correlation defect.
- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Layer boundary: `trunk=main`, `base=origin/main`, `branch=fix/release-carrier-skip-unmatched`,
  `position=carrier event-correlation repair`; no Stack metadata.
- The prior hosted Stage-A rehearsal remains valid: Release Please created PR `#59` with no tag or
  GitHub Release. This slice does not claim hosted verification of the new carrier behavior.
- No commit, push, merge, repository-variable change, tag, label, release, upload, publication,
  attestation, credential use, or parent-repository mutation was performed.

### Completed tasks

- [x] 8.1 — Added runtime/static regressions for ordinary `main` pushes with zero matching Release
  Please PRs, exactly one matching PR with a normal neighboring PR, multiple matches, malformed PR
  data, and the no-mutation workflow guard.
- [x] 8.2 — Added `classify_carrier_prs()` and the `carrier-pr-selection` CLI boundary. The carrier
  workflow now validates the read-only PR response, filters by exact `merge_commit_sha == GITHUB_SHA`,
  exits 0 with an auditable skipped `carrier-record.json`/summary for zero matches, and gates diff,
  tree, version, tag-plan, tag-ref, and label steps on `status=matched`.
- [x] 8.3 — Preserved the existing exact Stage-B validator, manual/variable dry-run precedence,
  live default, idempotency/conflict behavior, full-SHA actions, permissions, concurrency, and
  no-publication topology; updated the release-artifacts spec/design and verify/QA handoffs.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** after adding the new runtime/static assertions before production changes,
   `python3 tests/release_carrier_tests.py` failed with `ImportError` for the not-yet-existing
   classifier, and `python3 tests/release_carrier_static_tests.py` failed because the workflow still
   had the unconditional `test release_pr_count -eq 1` boundary and no skip/mutation guards.
2. **GREEN:** after implementing the classifier, CLI selection command, no-match record/summary, and
   matched-only workflow gates, `python3 tests/release_carrier_tests.py` and
   `python3 tests/release_carrier_static_tests.py` passed. The runtime suite covers zero-match skip,
   exactly-one full validation, multiple-match failure, malformed-data failure, and a CLI nonzero
   multiple-match path.
3. **REFACTOR:** replaced duplicated workflow `jq` candidate filters with the shared Python
   classifier, validated the GitHub PR response shape fail-closed, made the no-match record explicit,
   tightened shell quoting/ShellCheck handling, and reran focused tests plus `actionlint` green.

### Local verification

- `python3 tests/release_carrier_tests.py`, `tests/release_carrier_static_tests.py`,
  `tests/release_provenance_tests.py`, `tests/distribution_checks.py`, `tests/bootstrap_checks.py`,
  and `tests/readme_checks.py` — PASS.
- `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` —
  PASS.
- `python3 tests/oci_distribution_tests.py`, `tests/oci_distribution_static_tests.py`,
  `tests/oci_distribution_evidence_tests.py`, and `tests/oci_distribution_failure_tests.py` — PASS.
- `cargo +1.97.1 metadata --locked --format-version 1`, workspace tests (31 passed), check, fmt, and
  locked Clippy with `-D warnings` — PASS.
- npm wrapper typecheck/tests (6 passed) and wrapper plus six platform `npm pack --dry-run` checks —
  PASS (7 packages).
- `actionlint .github/workflows/*.yml`, `shellcheck scripts/build_oci_release.sh`,
  `docker buildx build --check --progress=plain .`, and `git diff --check` — PASS.
- A local read-only `jq` record probe confirmed the skipped record's `not-run`/`not-started`,
  `not-dispatched`, and `not-started` mutation statuses. This is supplemental local evidence, not
  hosted acceptance evidence.

### Remaining gates and risks

- [ ] 8.4 / 4.2 / 7.4 — protected hosted ordinary-main no-op, Release Please merge, and manual/variable
  dry-run rehearsal; the new no-match fix is not yet hosted-verified.
- [ ] 4.3 — fresh `sdd-verify` followed by independent `sdd-qa`; apply makes no user/operator
  acceptance claim.
- Publication, credentials, tag/label delivery, downstream workflow execution, attestation,
  rollback/failure injection, and native non-host target evidence remain outside this no-write slice.
- An extra local five-crate `cargo package` loop was attempted; the first package passed, while the
  second stopped on the repository's pre-existing unpublished local dependency not being present in
  the crates.io index. The requested Cargo metadata/test/check/fmt/Clippy checks passed, and no
  package/publication state was changed. The fresh verification rerun below supersedes that transient
  apply-time result and passed all five package checks with the local dependency patches.

## SDD verification executor rerun — 2026-08-15

### Result

- [x] Re-read the proposal, all five delta specs, design, tasks, current diff, implementation,
  workflow topology, state, and QA handoff before judging the change.
- [x] Fresh local verification passed: carrier correlation/runtime/static suites, exact
  `release-please@17.6.0` fake-SCM, provenance/distribution/bootstrap/README checks, all OCI layers,
  Python compilation/package generation, locked Cargo metadata/tests/check/fmt/Clippy, all five
  local Cargo package checks, npm typecheck/tests/seven pack dry-runs, actionlint, ShellCheck,
  Dockerfile check, and `git diff --check`.
- [x] Zero-match local record probe emitted `status=skipped`, reason
  `no-matching-release-please-pr`, and explicit validation/tag/label/release/publication no-op
  statuses without fetching a diff; exact-one, multiple, malformed, wrong-context, and mutation
  boundary probes remained green.
- [x] No commit, push, merge, repository-variable change, tag, label, release, upload, publication,
  attestation, credential injection, or hosted write was performed.

### Verification handoff

- Technical verdict: **PASS WITH WARNINGS**. No CRITICAL local defect was found.
- Hosted ordinary-main no-op, actual Release Please merge, manual/variable rehearsal, tag delivery,
  publication, attestation, rollback/failure injection, and native non-host target evidence remain
  unverified or prohibited.
- Independent `sdd-qa` remains the next phase and owns acceptance; no user/operator acceptance is
  claimed by this technical verification.

## Phase 9 apply — hosted conformance dependency-pin exception — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; assigned slice is the approved private conformance dependency-pin
  exception exposed by hosted PR `#59`.
- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`.
- Layer boundary: `trunk=origin/main`, `parent_branch=origin/main`, `base=origin/main`,
  `branch=fix/release-carrier-skip-unmatched`, `position=Phase 9 private pin exception`; no Stack
  metadata, branch creation, commit, push, merge, tag, release, publication, credential, or
  parent-repository mutation was performed.
- The private conformance package remains a workspace/build-test member at version `0.1.0` with
  `publish = false`; only its four runtime dependency version selectors converge to the synchronized
  public version.

### Completed tasks

- [x] 9.1 — The exact v17.6.0 fake-SCM harness now applies the source-faithful `mergeUpdates` and
  missing-file filter, asserts 32 effective paths including one root-carrier conformance manifest,
  six npm optional pin rewrites, one synchronized PR, and zero release/tag calls.
- [x] 9.2 — The harness verifies the private updater changes exactly the four approved dependency
  version lines while preserving the private package version, `publish = false`, and Cargo.lock
  conformance version; the four exact TOML JSONPaths are checked in provenance/distribution tests.
- [x] 9.3 — Carrier fixtures accept a complete four-line private patch and reject private package
  version/publish, dependency path, formatting/comment, truncated/missing patch, changelog, and other
  private-path mutations.
- [x] 9.4 — The Java root carrier owns the four conformance TOML entries, and the carrier workflow
  retains file status, addition/deletion/change counts, and unified patch content instead of only
  filenames.
- [x] 9.5 — `validate_stage_a_diff()` now fails closed unless the private file has exactly four
  complete dependency-version replacements whose new values equal the validated runtime version;
  private identity and synchronized-tree pin checks remain enforced.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** before the implementation changes, `release_carrier_tests.py` rejected the new positive
   private manifest entry as unapproved, `release_provenance_tests.py` rejected the missing root
   carrier paths, `distribution_checks.py` reported missing private selectors and patch metadata, and
   the exact runtime harness reported no private updater.
2. **GREEN:** after adding the four root-carrier entries, content-aware validator, workflow metadata
   retention, and fixture updates, the carrier, provenance, distribution, static, and exact
   `release-please@17.6.0` runtime suites passed. The runtime result records one private merged update,
   32 effective paths, six npm rewrites, one PR, and zero release/tag calls.
3. **REFACTOR:** the validator centralizes the private manifest path/dependency contract, validates
   unified patch metadata and changed-line sets, preserves the non-release/private identity, and the
   fake SCM now mirrors v17.6.0 `GitHub.buildChangeSet` filtering without any hosted API.

### Handoff and remaining gates

- [ ] Task 9.6 — Fresh `sdd-verify` must rerun the corrected boundary and full conformance matrix.
- [ ] Task 9.7 — A separately authorized protected hosted rerun must prove PR `#59`-equivalent
  metadata succeeds; the existing hosted PR `#59` evidence remains a failure until that new run.
- QA remains `BLOCKED`; this apply slice provides local implementation/test evidence only and makes no
  user/operator acceptance claim.
- No hosted writes occurred in this phase: no GitHub API mutation, workflow dispatch, repository
  variable change, tag, label, release, upload, attestation, registry publication, credential use,
  merge, push, or commit was performed.

## Phase 9 verification rerun — 2026-08-15

### Execution

- [x] Re-read the proposal, all five delta specs, design, tasks, current implementation diff, state,
  QA handoff, and prior apply evidence before judging the Phase 9 boundary.
- [x] Ran the exact installed `release-please@17.6.0` fake-SCM chain. It produced 32 effective paths,
  one root-carrier private manifest update with exactly four dependency-version line replacements,
  synchronized public Cargo/npm/lock values, six optional pin rewrites, one PR, and zero release/tag
  calls. The private package remained `0.1.0`, `publish = false`, and outside candidate/linked sets.
- [x] Focused private patch/content, unapproved npm, missing-root, malformed-SemVer, dry-run, and
  ordinary-main no-match tests passed. Current-tree Rust/Python/npm/OCI/workflow/package and diff
  checks also passed; synchronized-fixture `cargo metadata --locked` passed with public packages at
  `0.2.0` and conformance at `0.1.0`.

### Local defects found

- [ ] The synchronized effective-tree `cargo test --workspace --locked` probe fails in
  `codegauge-conformance` (`golden_order_summary_digest_and_numbers_are_stable_except_timestamp`):
  the generated binary reports tool version `0.2.0`, while `tests/golden/valid-methods.json` remains
  at `0.1.0`. The root generic extra-file updater is a no-op for that file because it has no
  Release Please version marker.
- [ ] Stage-B accepts a content-mutated approved generated file (`tests/golden/valid-methods.json`)
  because content validation is restricted to the private conformance manifest; the direct carrier
  probe returned `generated-file mutation: ACCEPTED`.

### Handoff

- Technical verification result: **FAIL**. These are local defects, not hosted-only limitations; no
  fix was made in this verify phase.
- Hosted Stage-A/merged-main/tag rehearsal, publication, attestation, rollback/failure injection,
  and native non-host evidence remain unrun or prohibited and cannot upgrade the verdict.
- No commit, push, merge, repository-variable change, tag, label, release, upload, attestation,
  registry publication, credential injection, or hosted write occurred.

## Phase 9 local CRITICAL defect remediation apply — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; branch: `fix/release-carrier-skip-unmatched`.
- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`; trunk/integration base:
  `origin/main`; parent branch: `origin/main`; position: local synchronized-tree and Stage-B content
  boundary repair. The checkout was already an intentionally dirty remediation baseline; no branch,
  commit, push, merge, Stack metadata, parent-repository, hosted, or release state was created.
- Scope was limited to the two latest local CRITICAL findings: the stale conformance golden after
  effective Stage-A synchronization and filename-only acceptance of approved carrier content.

### Completed tasks

- [x] 9.8 — Changed the root golden carrier to Release Please 17.6.0 typed JSON
  `$.tool.version`; added exactly four README and two model-contract `x-release-please-version`
  markers; left the CLI fixture unmarked. The exact runtime harness still observes 32 effective
  paths, six optional npm pin rewrites, one PR, and zero Stage-A release/tag calls.
- [x] 9.9 — Added complete patch/count/content validation for approved typed JSON/TOML/npm files,
  annotated generic lines, twelve generated changelogs, and the four private TOML pins. Stage-B
  rejects wrong versions, arbitrary content, unapproved markers, filename-only entries, duplicate
  paths, and missing/truncated patches before mutation.
- [x] 9.10 — Added synchronized copied-tree assertions for the golden runtime version and complete
  `cargo test --workspace --locked`, plus positive and negative carrier fixtures for the golden,
  README, contracts, generated content, annotations, and metadata boundaries.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** before the implementation changes, the new synchronized fixture assertion failed because
   `tests/golden/valid-methods.json` still reported `0.1.0`; the exact runtime harness omitted the
   expected effective README path; and the new carrier mutation fixtures exposed filename-only
   acceptance. The focused commands exited nonzero at those assertions.
2. **GREEN:** after the typed JSON config, exact generic markers, complete fixture synchronization,
   and content-aware validator were implemented, the exact `release-please@17.6.0` harness passed
   with 32 paths, four private pins, six npm rewrites, one PR, and zero release/tag calls. The copied
   synchronized tree passed metadata and `cargo test --workspace --locked`; all carrier mutation
   negatives failed closed.
3. **REFACTOR:** centralized patch metadata parsing, version-token/annotation checks, typed JSON,
   manifest, TOML, npm, changelog, and private-pin validators; generalized duplicate/content gates;
   and added static config assertions. Focused suites remained green.

### Local verification evidence

- `python3 tests/release_carrier_tests.py`, `tests/release_carrier_static_tests.py`,
  `tests/release_provenance_tests.py`, `tests/distribution_checks.py`, `tests/bootstrap_checks.py`,
  `tests/readme_checks.py`, and exact `tests/release_please_runtime_tests.py` — PASS.
- `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` — PASS.
- `cargo metadata --locked`, `cargo test --workspace --locked`, `cargo check --workspace --all-targets
  --locked`, `cargo fmt --all -- --check`, and locked Clippy `-D warnings` — PASS.
- Five runtime `cargo package --locked --allow-dirty` checks with local dependency patch configuration — PASS.
- npm wrapper typecheck/tests (6 tests) and wrapper plus six platform `npm pack --dry-run` checks — PASS.
- All four OCI regression layers, `actionlint`, `shellcheck scripts/build_oci_release.sh`, Dockerfile
  `docker buildx build --check --progress=plain .`, and `git diff --check` — PASS.
- No hosted writes occurred: no GitHub API mutation, workflow dispatch, repository-variable change,
  tag, label, release, upload, attestation, registry publication, credential use, merge, push, or
  commit. Fresh `sdd-verify`, independent QA, and protected hosted rehearsal remain downstream.

## Fresh sdd-verify — generated-version/updater boundary — 2026-08-15

### Verification result

- [x] Read the proposal, all five delta specs, design, tasks, current diff, implementation, state,
  QA handoff, and configuration before judging the remediation.
- [x] Exact Release Please `17.6.0` fake-SCM execution produced the exact 32-path effective changeset,
  release version `0.2.0`, one private conformance manifest update, exactly four private dependency
  pin edits, six npm optional pin rewrites, one synchronized PR, and zero Stage-A release/tag calls.
- [x] The synchronized copied tree updated `tests/golden/valid-methods.json` through `$.tool.version`,
  the four README marker lines and two model-contract marker lines, public Cargo/npm/lock versions,
  and the four private pins; `cargo test --workspace --locked` passed while conformance remained
  `0.1.0` and `publish = false`.
- [x] Stage-B accepted legitimate typed/annotated/TOML/npm/changelog/private updates and rejected
  wrong-version, arbitrary, unannotated, malformed, filename-only, duplicate, missing, and
  truncated mutations.
- [x] Current-tree Cargo, Python, npm, OCI, workflow, shell, package, and whitespace checks passed.
- [x] Exact workflow mode/no-match probes passed for manual and automatic dry-run/live behavior,
  invalid-mode fail-closed handling, and the successful no-match record without a diff fetch.
- [x] No commit, push, merge, repository-variable change, tag, label, release, upload, publication,
  attestation, credential injection, or hosted write was performed.

### Handoff

- Technical verdict: **PASS WITH WARNINGS**; no local implementation defect remains.
- Hosted Release Please merge/carrier/tag rehearsal and independent `sdd-qa` remain pending or
  prohibited under the no-write boundary. This verification does not claim operator acceptance.

## Phase 10 apply — hosted GitHub PR patch parser defect — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; branch: `fix/release-private-pins-rehearsal-v2`.
- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`; trunk/base:
  `origin/main`; position: Stage-B PR-files hunk-only patch parser repair after the Phase 9 private
  conformance pin exception. The branch was clean before this slice; no branch, commit, push, merge,
  tag, release, publication, credential, repository-variable, or parent-repository mutation was
  performed.
- Hosted run `#31878496886` reached validation for the real merged Release Please PR `#59` and failed
  with `RELEASE PROVENANCE: FAIL: .release-please-manifest.json diff has missing or unexpected file
  context`. GitHub `GET /pulls/59/files` supplied a valid hunk-only `patch` beginning
  `@@ -1,15 +1,15 @@` without `diff --git`, `---`, or `+++` headers; the old parser incorrectly required
  local full-diff headers.
- The exact 32-path Stage-A changeset, private four-pin exception, generated-file content validation,
  no-match carrier no-op, dry-run/live gates, and no-publication contract remain unchanged.

### Completed tasks

- [x] 10.1 **RED** — Added an API-shaped hunk-only `.release-please-manifest.json` entry with
  `filename`, `status`, `additions`, `deletions`, `changes`, and the 15-line hunk. Retained full
  unified-diff fixtures and added malformed, missing, inconsistent-count, truncated, multi-hunk, and
  unexpected multi-section regressions.
- [x] 10.2 **GREEN** — `_patch_change_lines()` now accepts exactly a complete single-file unified
  diff or a filename-bound GitHub PR-files hunk-only patch. It validates every hunk header/body count,
  API additions/deletions/changes metadata, status-specific headers, path identity where headers are
  present, and rejects malformed, truncated, or unexpected file sections. The private conformance
  validator now uses parsed hunk context so the four-pin exception also works with API patches.
- [x] 10.3 **REFACTOR** — Corrected test full-diff hunk counts, kept exact runtime fixtures valid, and
  updated the release-artifacts/design contract plus verification/QA handoff. Local checks passed;
  the fix is not yet hosted-verified.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** before the parser change, `python3 tests/release_carrier_tests.py` failed on the actual
   hunk-only manifest entry with `ProvenanceError: .release-please-manifest.json diff has missing or
   unexpected file context`, reproducing the hosted defect locally.
2. **GREEN:** after the parser and private-validator changes,
   `python3 tests/release_carrier_tests.py` passed the hunk-only and full unified-diff positives plus
   missing/count/malformed/truncated/multi-section negatives. Carrier static, provenance, exact
   Release Please runtime, and distribution tests also passed.
3. **REFACTOR:** hunk parsing was centralized, declared hunk counts are checked independently of API
   metadata, full-diff headers remain strict, and the existing path/content/version/private/dry-run/
   live/no-publication boundaries stayed green.

### Local verification evidence

- `python3 tests/release_carrier_tests.py`, `tests/release_carrier_static_tests.py`,
  `tests/release_provenance_tests.py`, `tests/release_please_runtime_tests.py`, and
  `tests/distribution_checks.py` — PASS.
- No tag, GitHub Release, Cargo/npm/GHCR publication, upload, attestation, workflow dispatch,
  repository-variable change, credential use, merge, push, or hosted write occurred. Hosted run
  `#31878496886` found the bug; this fix is not yet hosted-verified.

## Phase 10 technical verification — 2026-08-15

### Verification result

- [x] Fresh `sdd-verify` re-read the proposal, all five delta specs, design, tasks, current diff,
  implementation, state, and QA handoff before judging the parser correction.
- [x] The real `.release-please-manifest.json` fixture passes as a GitHub PR-files API-shaped
  filename-bound hunk-only patch beginning `@@ -1,15 +1,15 @@`; the complete unified-diff form also
  passes. A read-only generated matrix passed both forms for all 31 content-bearing Stage-A entries
  (the 32nd effective path is the intentionally unmarked CLI fixture with no content mutation).
- [x] Hunk headers/body counts, additions/deletions/changes metadata, status/path/header rules, and
  unexpected-section handling fail closed for missing, truncated, inconsistent, malformed, and
  multi-section patches. The private conformance four-pin validator passes with hunk-only context too.
- [x] Exact Release Please `17.6.0` fake-SCM output remains 32 effective paths, four private pins,
  six npm optional rewrites, one PR, and zero release/tag calls. Synchronized workspace tests and all
  requested local Cargo/Python/npm/OCI/workflow/package/whitespace checks pass.
- [x] Ordinary-main no-match classification still emits the successful skipped record, and the
  manual/automatic dry-run/live mode matrix remains green with invalid values failing closed.

### Handoff

- Technical verdict: **PASS WITH WARNINGS**; no local implementation defect remains.
- Independent `sdd-qa`, the protected hosted rerun, hosted tag/release/publication evidence, native
  non-host target evidence, and failure-injection/rollback evidence remain outside this no-write phase.
- No commit, push, merge, repository-variable change, tag, label, release, upload, publication,
  attestation, credential injection, or hosted write was performed.

## Phase 11 apply — dry-run-only historical carrier replay — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; branch: `fix/release-carrier-replay` based on `origin/main` at
  `98fd3c60c68d3ec2373429bb07ffa7e32e69f053`.
- Delivery strategy: `auto-chain`; chain strategy: `feature-branch-chain`; trunk/base:
  `origin/main`; parent branch: `origin/main`; position: manual historical replay guard after the
  corrected GitHub PR-files hunk-only parser. The assigned slice is self-contained and no Stack
  metadata is used.
- Authorized scope: one no-publication manual `workflow_dispatch` rehearsal for historical merge
  `fcc91b4850480945ae484c3ebdba18f8a4e38270` with `dry_run=true`. The checkout stays on the current
  selected `main` source tree; the historical SHA is read-only event identity only.
- Prohibited state changes honored: no commit, push, merge, tag, label, release, upload, registry
  publication, attestation, credential exposure/use, repository-variable change, or parent-repository
  mutation occurred.

### Completed tasks

- [x] 11.1 — Added runtime/static RED coverage for exact replay SHA selection, exact Release Please
  PR correlation and full validation, source-tree byte preservation, push/live/malformed replay
  rejection, absent-replay current-main behavior, normalized `EVENT_SHA`, mutation guards, and
  credential-free record fields.
- [x] 11.2 — Added `resolve_carrier_event_sha()` and the `carrier-event-sha` CLI boundary. The
  workflow accepts optional `replay_sha`, rejects it unless the event is manual `dry_run=true`,
  keeps checkout/current-tree validation on main, and routes commit/PR lookup, carrier validation,
  tag planning, and any live tag target through `EVENT_SHA`.
- [x] 11.3 — Added source/replay/dry-run fields and complete mutation statuses to
  `carrier-record.json`, `carrier-plan.json`, and `GITHUB_STEP_SUMMARY`; explicit replay-false live
  guards preserve canonical tag ownership and ordinary push variable/live defaults. Updated README,
  design/spec/tasks, and verify/QA handoff boundaries. Current-main test fixtures were made baseline
  aware of public `0.2.0` and private conformance `0.1.0` state without changing product contracts.
- [ ] 11.4 — Protected hosted replay remains pending and is not performed by apply. No hosted pass or
  production replay claim is made.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** before implementation, `python3 tests/release_carrier_tests.py` failed because the
   replay resolver did not exist, and `python3 tests/release_carrier_static_tests.py` reported the
   missing `replay_sha`, normalized event identity, source/replay record, and mutation guard
   contracts.
2. **GREEN:** after adding the resolver/CLI and workflow wiring, replay tests passed the exact
   `fcc91b...` selection, exactly-one PR correlation/full validation, source-tree immutability, absent
   replay current-main behavior, push/live/malformed negatives, and plan SHA equality. Static checks
   passed the current-main checkout, explicit `EVENT_SHA` uses, replay-false mutation conditions,
   full mutation record, and no-publication topology.
3. **REFACTOR:** grouped GitHub output writes to satisfy ShellCheck/actionlint, moved PR correlation
   ahead of tree validation, centralized event identity selection, made the plan/summary audit fields
   explicit, and retained all existing strict content/private/version/idempotency/conflict gates.

### Local verification evidence

- `python3 tests/release_carrier_tests.py`, `tests/release_carrier_static_tests.py`,
  `tests/release_provenance_tests.py`, `tests/release_please_runtime_tests.py`,
  `tests/distribution_checks.py`, `tests/bootstrap_checks.py`, `tests/readme_checks.py`,
  `python3 -m compileall -q scripts tests`, and `python3 scripts/generate_npm_packages.py --check` —
  PASS. The exact Release Please runtime emitted expected no-release/no-tag fake-SCM warnings and
  ended with `RELEASE PLEASE V17.6.0 RUNTIME TESTS: PASS`.
- `cargo metadata --locked --format-version 1`, `cargo test --workspace --locked`,
  `cargo check --workspace --locked`, `cargo fmt --all -- --check`, and locked Clippy with
  `-D warnings` — PASS.
- npm wrapper typecheck/tests plus `npm pack --dry-run` for the wrapper and all six platform package
  directories — PASS (six npm tests, seven packs).
- `tests/oci_distribution_tests.py`, `tests/oci_distribution_static_tests.py`,
  `tests/oci_distribution_evidence_tests.py`, and `tests/oci_distribution_failure_tests.py` — PASS.
- `actionlint .github/workflows/*.yml`, `shellcheck scripts/build_oci_release.sh`,
  `docker buildx build --check --progress=plain .`, and `git diff --check` — PASS.

### Handoff

- Technical verification must rerun the updated replay/spec matrix; independent `sdd-qa` remains the
  acceptance owner. This apply record does not claim operator acceptance or hosted success.
- The replay path is explicitly dry-run-only and must remain blocked from tag, label, release, upload,
  publication, and attestation mutation. Hosted replay, PAT scope/masking/ref authorization, branch
  protection, and downstream event delivery remain unverified.
- No hosted writes occurred.

## Phase 11 verification — dry-run-only historical carrier replay — 2026-08-15

### Verification result

- [x] Re-read the proposal, all five delta specs, design, tasks, current diff, implementation,
  state, QA handoff, and configuration before judging the replay slice.
- [x] Executed the focused carrier/provenance/static/runtime suites, exact Release Please `17.6.0`
  fake-SCM, synchronized copied-tree Cargo tests, locked Cargo gates, five package checks, npm gates,
  OCI layers, workflow diagnostics, Dockerfile check, compile/package checks, and whitespace check.
- [x] The exact checked-in carrier mode shell body accepted a valid manual replay and rejected push,
  live, malformed, and wrong-ref replay inputs before collection.
- [ ] Ordinary no-replay behavior is technically verified. The extracted mode step exits before
  outputs for manual no-replay and every push variable mode because `jq -er '.replay'` returns status
  1 for the valid JSON boolean `false` under `set -euo pipefail`.

### Confirmed local evidence

- Pure replay resolution selects the authorized historical SHA only for manual `dry_run=true`, keeps
  the current source SHA separate, and routes the replay fixture through the normal carrier validator
  and expected tag plan without changing copied-tree bytes.
- Exact Release Please `17.6.0` runtime still records 32 generated paths, the private four-pin
  root-carrier update, six npm optional pin rewrites, one synchronized PR, and zero release/tag calls.
- Missing/ambiguous/malformed PRs, hunk-only/full patches, content/version/private mutations, no-match
  behavior, canonical Stage-B tag ownership, and all listed local quality/package checks pass.

### CRITICAL local finding

`release-tag-carrier.yml` uses `jq -er '.replay'` when reading the resolver's boolean output. `jq -e`
intentionally exits nonzero for `false`; with `set -e`, the mode step aborts before `GITHUB_OUTPUT` is
written. This breaks absent replay on manual dispatch and push dry-run/live/unset modes. The defect is
reported only; no implementation fix was made in verification.

### Handoff

- Technical verdict: **FAIL**; task 11.3 is not behaviorally accepted until the mode-step defect is
  repaired and the exact shell matrix is green.
- Task 11.4 protected hosted replay remains pending and prohibited here. No hosted pass, production
  replay, tag, label, release, upload, publication, attestation, credential, or operator acceptance
  claim is made.
- Next phase: `sdd-apply` for a test-first minimal repair, followed by a fresh `sdd-verify` and then
  independent `sdd-qa` if verification passes.

## Phase 11 apply remediation — total replay schema and normal mode repair — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; branch: `fix/release-carrier-replay`; chain strategy:
  `feature-branch-chain`; trunk/integration base and parent branch: `origin/main`; position: local
  repair after the Phase 11 replay verification finding.
- Scope: repair the carrier's optional replay boolean extraction and make record/summary replay fields
  explicit and total. The source checkout, normalized `EVENT_SHA`, replay rejection, no-match, exact
  Stage-B, private-pin, version, idempotency/conflict, and mutation boundaries remain unchanged.
- No commit, push, merge, tag, release, upload, publication, attestation, credential, repository
  variable, hosted workflow dispatch, or parent-repository mutation occurred.

### Completed work

- [x] Added `tests/release_carrier_mode_tests.py` covering normal push, manual dry-run, and manual live
  mode without `replay_sha`; each requires successful mode resolution and `replay=false`. The same
  executable test keeps valid replay limited to manual `workflow_dispatch` + `dry_run=true` + a valid
  lowercase 40-hex SHA and retains push/live/malformed rejection cases.
- [x] Replaced the failing `jq -er '.replay'` extraction with a `jq -r` default/type-check boundary:
  absent/null replay becomes boolean `false`, false serializes safely, and non-boolean values fail
  closed.
- [x] Made carrier records and summaries emit a top-level boolean `replay`, source checkout SHA, and
  replay event SHA/null-or-none representation on every path; replay paths identify the historical
  event SHA explicitly. The dry-run plan guard uses the same safe boolean default/type check.
- [x] Updated the release-artifacts design/spec and task handoff to document the total schema and the
  normal-mode regression repair. Hosted replay task 11.4 remains unchecked.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** after adding the executable workflow-step tests, `python3
   tests/release_carrier_mode_tests.py` exited 1 at `test_normal_push_defaults_to_live_without_replay`;
   the pre-fix mode step aborted before outputs because `jq -er '.replay'` treated valid `false` as a
   failed result.
2. **GREEN:** after the minimal workflow repair, `python3 tests/release_carrier_mode_tests.py` exited
   0. Normal push, manual dry-run, manual live, valid replay, and replay-negative cases passed.
3. **REFACTOR:** the records/summaries were normalized to the explicit total replay schema and the
   dry-run plan guard was changed to the same default/type-checked boolean extraction. The focused
   mode, carrier, static, and provenance suites remained green.

### Commands run

- `python3 tests/release_carrier_mode_tests.py` — RED exit 1 before the fix; GREEN exit 0 after the
  fix.
- `python3 tests/release_carrier_static_tests.py`, `python3 tests/release_carrier_tests.py`, and
  `python3 tests/release_provenance_tests.py` — exit 0.
- `python3 tests/release_please_runtime_tests.py` — exit 0; exact Release Please 17.6.0 fake-SCM
  result retained 32 generated paths, four private pins, six npm pins, one PR, and zero release/tag
  calls.
- `python3 tests/distribution_checks.py`, `python3 tests/bootstrap_checks.py`, `python3
  tests/readme_checks.py`, `python3 -m compileall -q scripts tests`, and `python3
  scripts/generate_npm_packages.py --check` — exit 0.
- `cargo metadata --locked --format-version 1`, `cargo test --workspace --locked`, `cargo check
  --workspace --locked`, `cargo fmt --all -- --check`, and `cargo clippy --workspace --all-targets
  --locked -- -D warnings` — exit 0; workspace tests reported 31 passed, 0 failed, 0 skipped.
- The initial unpatched local `cargo package` loop stopped at the expected unpublished local
  dependency lookup. The exact workflow-equivalent five-crate package commands with local
  `patch.crates-io` paths and `--allow-dirty` then passed packaging and verification for all five
  runtime crates; no publication occurred.
- `npm --prefix npm/codegauge run typecheck`, `npm --prefix npm/codegauge test`, and wrapper plus
  six platform `npm pack --dry-run` checks — exit 0; six npm tests and seven package dry-runs passed.
- `python3 tests/oci_distribution_tests.py`, `python3 tests/oci_distribution_static_tests.py`,
  `python3 tests/oci_distribution_evidence_tests.py`, `python3 tests/oci_distribution_failure_tests.py`,
  `shellcheck scripts/build_oci_release.sh`, and ShellCheck on the extracted carrier mode step — exit 0.
- `actionlint .github/workflows/*.yml`, `docker buildx build --check --progress=plain .`, and
  `git diff --check` — exit 0.

### Handoff

- Fresh `sdd-verify` must rerun the Phase 11 mode/record/summary matrix; this apply artifact does not
  claim technical verification, hosted success, or operator acceptance.
- QA remains blocked pending fresh verification, independent acceptance, and the separately authorized
  hosted replay/no-publication observation.

## Phase 11 fresh verification after mode repair — 2026-08-15

### Executed evidence

- The extracted `Resolve carrier mode` step passed normal push with no replay, manual dry-run/live with
  no replay, valid manual replay, and push/live/malformed/wrong-ref replay rejection. Absent replay emits
  a boolean `false`; valid replay separates the current source checkout SHA from `EVENT_SHA`.
- `release_carrier_tests.py` passed exact replay PR correlation, current-tree/private four-pin/full
  Stage-B validation, source-byte immutability, tag-plan identity, no-match, hunk-only/full-patch, and
  mutation-negative coverage. Static carrier checks also passed normalized `EVENT_SHA` and replay-false
  mutation guards.
- Current local quality/distribution evidence passed: provenance/distribution/bootstrap/README, all OCI
  regression layers, compile/package checks, locked Cargo metadata/tests/check/fmt/Clippy, five patched
  Cargo package checks, npm typecheck/tests/seven dry-run packs, actionlint, ShellCheck, Dockerfile
  `buildx --check`, and `git diff --check`.

### Local blocker found

- `python3 tests/release_please_runtime_tests.py` exits 1 after the exact installed
  `release-please@17.6.0` Node harness passes. Its positive `stage_a_prefix()` fixture reads the current
  `.release-please-manifest.json` values (`0.2.0`) as the old side of a required `0.2.0` replacement,
  so `validate_stage_a_diff()` correctly rejects the no-op with `release metadata contains an unexpected
  version replacement`. This stale fixture prevents claiming the full prior Release Please/conformance
  check is green.

### Handoff

- Technical verdict: **FAIL**; no code or workflow fix was made during verification.
- Next action: `sdd-apply` repairs the failing test fixture, then rerun `sdd-verify` before `sdd-qa`.
- No commit, push, merge, tag, label, release, upload, publication, attestation, credential,
  repository-variable change, hosted dispatch, or other hosted write occurred.

## Phase 11 apply remediation — deterministic Release Please wrapper fixture — 2026-08-15

### Layer and scope

- Change: `codegauge-distribution`; branch: `fix/release-carrier-replay`; delivery strategy:
  `auto-chain`; chain strategy: `feature-branch-chain`.
- Trunk/integration base: `origin/main`; parent branch: `origin/main`; position: test-fixture repair
  after the Phase 11 replay-default verification blocker. No Stack metadata is used.
- Scope is limited to `tests/release_please_runtime_tests.py` and the related OpenSpec handoff records.
  The exact Node `release-please@17.6.0` harness, 32-path/private-four-pin/npm-six-pin/no-write
  boundaries, carrier workflows, source tree, and product code are unchanged.
- No commit, push, merge, tag, label, release, upload, registry publication, attestation, credential,
  repository-variable change, hosted dispatch, or parent-repository mutation occurred.

### Completed work

- [x] Added explicit `BASELINE_VERSION = "0.1.0"`, `TARGET_VERSION = "0.2.0"`, exact 13-entry
  manifest-path, five-runtime-crate, and six-optional-dependency fixture constants.
- [x] Made `stage_a_prefix()` verify the checked-out manifest and wrapper are exactly at the target
  shape, then build every patch line from the historical baseline to the target without reading current
  values as the old side.
- [x] Added executable positive and negative fixture tests: the historical fixture passes the existing
  Stage-B validator, while one no-op manifest replacement and one wrong-version replacement fail closed.
- [x] Kept the private four-pin fixture and all exact Release Please/Stage-B carrier boundaries intact.

### TDD RED → GREEN → REFACTOR evidence

1. **RED:** after adding `test_stage_a_prefix_builds_historical_fixture()` and the no-op/wrong-version
   mutation assertions, `python3 tests/release_please_runtime_tests.py` exited 1 at the historical
   manifest assertion because the old `stage_a_prefix()` emitted current `0.2.0` values as both sides.
2. **GREEN:** after the deterministic fixture builder was implemented, the focused wrapper passed the
   exact Node harness and Stage-B positive/negative checks: one PR, 32 generated paths, four private
   pins, six npm optional rewrites, zero release/tag calls, and all private mutations rejected.
3. **REFACTOR:** reused named baseline/target/path constants across the private fixture and wrapper
   validation, added current-target shape guards, and retained `git diff --check` plus Python compile
   validation.

### Local verification evidence

- Focused Python suites passed: `release_please_runtime_tests.py`, `release_carrier_tests.py`,
  `release_carrier_static_tests.py`, `release_carrier_mode_tests.py`, `release_provenance_tests.py`,
  `distribution_checks.py`, `bootstrap_checks.py`, `readme_checks.py`, and all four OCI regression
  layers.
- `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` —
  PASS.
- Locked Cargo metadata, 31 workspace tests, check, fmt, locked Clippy, and five workflow-equivalent
  runtime package verifications with local dependency patches — PASS.
- npm wrapper typecheck/tests (6 tests) and wrapper plus six platform `npm pack --dry-run` checks —
  PASS.
- `actionlint`, `shellcheck scripts/build_oci_release.sh`, Dockerfile `buildx --check`, and
  `git diff --check` — PASS.

### Handoff

- Fresh `sdd-verify` must rerun the Phase 11 replay and exact Release Please matrix; this apply record
  does not claim technical verification or operator acceptance.
- Task 11.4 protected hosted replay and no-publication record inspection remain unchecked and are not
  performed under the no-write boundary. QA remains blocked pending fresh verification and independent
  acceptance.

## Phase 11 final local verification — 2026-08-15

### Verification result

- [x] The exact installed `release-please@17.6.0` Node harness passed with 32 effective paths, one
  private conformance manifest update containing exactly four dependency-version edits, six npm optional
  rewrites, one synchronized PR, and zero release/tag calls.
- [x] The Python wrapper fixture passed its explicit historical `0.1.0 -> 0.2.0` positive path, current
  manifest/npm target-shape guards, and no-op/wrong-version rejection tests.
- [x] Synchronized copied-tree workspace tests and all prior carrier, replay, hunk/full-patch, content,
  private, generated, version, no-match, dry-run/live, Cargo, npm, OCI, workflow, package, compile, and
  whitespace checks passed locally.
- [x] Workflow inspection and runtime probes confirmed immutable external action SHAs, least privilege,
  current-main checkout versus replay `EVENT_SHA` separation, replay mutation guards, and Stage-B-only
  canonical tag ownership.
- [ ] Task `11.4` remains pending: protected hosted replay/no-publication observation is not performed.

### Handoff

Technical verification is **PASS WITH WARNINGS**. No local defect remains; hosted replay and independent
acceptance are the remaining downstream boundary. No hosted write, credential, tag, release, publication,
upload, attestation, variable change, merge, push, or commit occurred.
