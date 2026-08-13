# Apply Progress: CodeGauge distribution remediation

## Scope

- Change: `codegauge-distribution`
- Remediation units: `R-C`, `R-D`, `R-E`
- Delivery strategy: `feature-branch-chain`
- Layer boundary: `distribution-e-oci-remediation`, based on the existing dirty worktree baseline;
  no branch or commit was created.
- Out of scope: registry credentials, publication, branch/PR creation, and state.yaml mutation.

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
