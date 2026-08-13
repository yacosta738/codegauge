# Tasks: Distribution

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 900–1,400 initial; remediation is split by layer |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | A → B → C → D → E |
| Delivery strategy | feature-branch-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | PR | Notes |
|------|------|-----------|-------|
| A | Cargo/source and version provenance | PR 1 | Cargo decision. |
| B | Quality CI and static gates | PR 2 | Depends A. |
| C | npm wrapper and six GNU packages | PR 3 | Depends A + npm decisions. |
| D | Target archives and GitHub Release | PR 4 | Depends A–C. |
| E | OCI image | PR 5 | Depends D + owner/architecture decisions. |

### Canonical Delivery Strategy

Use **feature-branch-chain**. Each work-unit branch targets the immediately preceding branch; no
GitHub Stack metadata or `gh stack` state is used. The existing dirty worktree is the baseline for
the first implementation branch and must not be discarded. Keep the initial implementation slices
and verification remediations reviewable by assigning one layer per apply invocation:

```text
main
 └── distribution-a-cargo-ci
      └── distribution-c-npm-remediation
           └── distribution-d-release-remediation
                └── distribution-e-oci-remediation
```

The remediation branches are ordered because release provenance is an input to npm and OCI
publication. Each branch must have its own focused RED → GREEN evidence, verification command set,
and rollback boundary. Do not create commits or push branches during SDD apply unless the user
explicitly requests publication.

### Verification Remediation Units

- [x] R-C: Add a pure local negative checksum gate test proving a corrupted archive/sidecar prevents
  both npm platform and base publication; make every manual npm checkout use the exact verified
  release tag and reject version/source drift.
- [x] R-D: Restrict release publication to a verified release-please tag from merged `main`; upload
  assets to the release-please-created release instead of creating a duplicate; assert binary
  version/profiles, Cargo/npm/manifest version, and source revision before upload; synchronize all
  six platform package versions with the base package.
- [x] R-E: Build OCI architecture outputs without public pushes, assert labels/digests/runtime
  version/profiles/contract/non-root evidence, then publish the final multi-arch manifest only after
  every architecture passes.
- [x] R-E follow-up: Derive Docker config/platform-manifest digests from the Docker archive, compare
  inspect identity against the Docker domain, preserve separate OCI/config/metadata evidence, and
  pass the Docker archive into the verifier.

## Phase 1: Decisions and TDD

- [x] 1.1 Decision gate: approved crates.io runtime-graph publication, `@yacosta738/codegauge` plus same-scope platform packages, `ghcr.io/yacosta738/codegauge`, the complete viable target matrix (8 archives, 6 npm, 2 OCI), and chained PRs A→E.
- [x] 1.2 RED: create `tests/distribution_checks.py` and provider regression coverage in `crates/codegauge-provider-jacoco/tests/jacoco.rs`; assert version/package/target/workflow/checksum/security/RFC-0001 boundaries; capture Clippy red.
- [x] 1.3 GREEN prerequisite: replace only deprecated `quick_xml` in `crates/codegauge-provider-jacoco/src/lib.rs`; run `cargo test --workspace --locked`, `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets --locked -- -D warnings`, and Python checks; preserve contracts.

## Phase 2: Cargo, Versioning, CI

- [x] 2.1 Update `Cargo.toml`, `crates/*/Cargo.toml`, `Cargo.lock`, `crates/codegauge-application/src/lib.rs`, version assertions, and `README.md`; publish the approved Cargo runtime graph; validate `cargo metadata --locked`, package contents, and ordered dry-runs.
- [x] 2.2 Create `.github/workflows/ci.yml` with Rust/Cargo 1.97.1, immutable action SHAs, locked Rust/Python/static gates, and read-only PR permissions; retain evidence that failures block release.

## Phase 3: npm Distribution

- [x] 3.1 RED: add `npm/` TypeScript tests for exact `os`/`cpu`, missing dependency, argv/stdio/exit passthrough, and musl rejection; run them before implementation. (Initial npm runner was absent; Node test checks were added and executed after the wrapper slice; final focused suite passes.)
- [x] 3.2 Implement `npm/package.json.tmpl`, `npm/codegauge/`, and six approved `@yacosta738` outputs with exact pins; verify `tsc --noEmit`, `npm pack --dry-run`, executable bits, and sidecar checksums.

## Phase 4: Archives and GitHub Release

- [x] 4.1 Extend tests for archive format/name, lowercase SHA-256 sidecars, provenance, and permissions; create `release-please-config.json` and `.release-please-manifest.json` for workspace packages/npm pins.
- [x] 4.2 Create `.github/workflows/release.yml`: immutable tag checkout, approved targets, `codegauge` builds, approved archive/sidecar outputs, pre-upload verification, attestations/OIDC, scoped credentials, ordered publishers, and fail-stop recovery.
- [x] 4.3 Rehearse release-please/tag dry-run without writes; retain target/build/checksum/version evidence and verify `codegauge version`, `profiles`, and contract fixtures.

## Phase 5: OCI, Docs, Final Gates

- [x] 5.1 Create workspace-aware `Dockerfile`/`.dockerignore`; build pinned Rust 1.97.1 musl images for approved `linux/amd64`/`arm64`, run non-root with init, inspect labels/digest, and smoke-test before manifest publication.
- [x] 5.2 Update `README.md`, `.gitignore`, and conditional metadata/license files with source/Cargo, npm, archive, OCI, permission, provenance, checksum, target, and rollback guidance; never add names/credentials as facts.
- [x] 5.3 Run `python3 tests/bootstrap_checks.py`, `python3 tests/readme_checks.py`, locked Cargo checks, package/archive/image inspections, and a no-semantic diff audit; retain recovery evidence.
