# Release Artifacts and Channels Specification

## Purpose

Create traceable GitHub Release artifacts and coordinate Cargo/source, npm, and OCI channels without
pretending that cross-registry publication is atomic.

## Requirements

### Requirement: Immutable version provenance

The release process MUST derive one approved version from release metadata, create the release from
an immutable Git revision, and propagate that version and source identity to Cargo metadata, the
`codegauge version` output, npm packages, archives, and OCI metadata. Release-please configuration
MUST address the actual workspace packages and npm version pins rather than assuming the virtual
workspace root is publishable. A virtual workspace root MUST NOT be treated as a publishable Cargo
package by assumption. Publication MUST originate from merged `main` and its immutable release tag,
not from an unmerged pull request.

#### Scenario: Provenance mismatch

- GIVEN any channel reports a different version or source revision
- WHEN release validation compares the artifacts
- THEN the release is blocked before publication and the mismatching channel is identified

### Requirement: Virtual workspace root release ownership

Release-please configuration MUST give repository-level version and contract-file updates to an
effective candidate that survives the Release Please 17.6.0 workspace plugins. A virtual Cargo root
MUST NOT be configured as a Rust package candidate because it has no `[package].name`. A non-Cargo
metadata candidate MAY carry those updates only when it has no package identity and MUST skip its own
GitHub release; exactly one approved runtime component MUST create the unprefixed `vX.Y.Z` tag.

#### Scenario: Root updates survive the plugin pipeline

- GIVEN the repository has a virtual Cargo workspace and root-owned extra-files
- WHEN the Release Please 17.6.0 Cargo, Node, and linked-versions plugins process candidates
- THEN the root candidate remains effective, owns the root extra-file updates, optional npm pins are
  rewritten from the linked versions map, and exactly one unprefixed `vX.Y.Z` release operation remains

#### Scenario: Virtual root cannot publish as a fake package

- GIVEN the root candidate is used only to carry repository metadata updates
- WHEN Release Please prepares GitHub releases and package publication
- THEN the root has no Cargo/npm package identity and its skipped release cannot create a fake root
  package or a duplicate tag

### Requirement: Private workspace members stay outside the Stage-A candidate graph

Stage-A Release Please configuration MUST use an explicit list of the five approved runtime Cargo
packages when the repository workspace also contains a private conformance member. It MUST NOT use
the Release Please 17.6.0 `cargo-workspace` plugin for this graph because the exact packaged source
(`build/src/plugins/cargo-workspace.js`, lines 45–84 and 138–193; `workspace.d.ts`, lines 11–16)
scans every declared workspace member and exposes no supported member-exclusion option. The private
`crates/codegauge-conformance/Cargo.toml` MUST remain a Cargo workspace member for builds/tests,
MUST remain `publish = false`, and MUST be absent from the effective candidate and linked-component
sets. The non-Cargo root metadata carrier MAY own that existing manifest as a narrowly scoped
dependency-pin update, but it MUST NOT own the private package version, changelog, release metadata,
or any other private path.

#### Scenario: Exact v17.6.0 private-candidate boundary

- GIVEN the root Cargo workspace declares five runtime crates and private
  `codegauge-conformance`
- WHEN the exact Release Please 17.6.0 Manifest/plugin chain runs against a read-only fake SCM
- THEN it MUST create one synchronized PR with all five runtime Cargo candidates, the root metadata
  carrier, the linked versions map, six npm optional dependency rewrites, and one root-owned
  `crates/codegauge-conformance/Cargo.toml` dependency update, with zero release/tag calls
- AND the private manifest MUST NOT be a candidate or linked component, and its package version and
  `publish = false` state MUST remain unchanged

### Requirement: Hosted conformance dependency alignment is a root-carrier exception

The surviving Java root metadata carrier MUST own exactly these four TOML JSONPath updates in
`/crates/codegauge-conformance/Cargo.toml`, with every new value equal to the synchronized public
runtime version:

```text
$.dependencies["codegauge-application"].version
$.dependencies["codegauge-core"].version
$.dependencies["codegauge-model"].version
$.dependencies["codegauge-provider-jacoco"].version
```

The carrier MUST NOT update `[package].version`, `publish`, package identity, changelog, release
metadata, or any other file under `crates/codegauge-conformance/`. This exception exists because
hosted PR `#59` synchronized the five public runtime Cargo/npm surfaces to `0.2.0` with no release or
tag calls, then failed `cargo metadata --locked` because these private path pins remained `^0.1.0`.

#### Scenario: Hosted PR #59 exposes stale private pins

- GIVEN a merged Stage-A version PR synchronizes public runtime packages to `0.2.0`
- AND `codegauge-conformance` still requires the public path dependencies at `^0.1.0`
- WHEN CI runs `cargo metadata --locked`
- THEN the quality gate fails before Stage-B can create a tag, and the failure identifies private
  dependency alignment as the missing boundary

#### Scenario: Corrected private dependency update

- GIVEN the root carrier proposes the private manifest path
- WHEN the complete before/after content differs only at the four listed dependency `.version`
  fields and each new value is the synchronized runtime version
- THEN Stage-B accepts the path, `cargo metadata --locked` is eligible to pass, and the private
  package version remains its private/non-release value

#### Scenario: Private manifest mutation outside the exception

- GIVEN the Stage-A diff contains the private manifest
- WHEN it changes package version, `publish`, dependency keys/paths/features, comments/formatting,
  a changelog, or any other private/unapproved path
- THEN Stage-B fails closed before tag, label, release, upload, or publication mutation

### Requirement: Root carrier content matches its configured updater

Stage-A's effective root carrier MUST use the Release Please 17.6.0 updater appropriate to each
file. `/tests/golden/valid-methods.json` MUST use the typed JSON path `$.tool.version`. README and
`crates/codegauge-model/tests/contracts.rs` MAY use the generic updater only on exact
`x-release-please-version` marker lines; unrelated semver text MUST remain unmarked. The CLI
integration fixture has no release-version marker and MUST NOT be changed by the root generic
updater. Stage-B MUST retain complete file patch/content metadata and reject filename-only, wrong
version, arbitrary-content, unapproved-marker, malformed, missing, or truncated updates for every
approved root/candidate/generated path. The twelve generated changelogs are permitted only as
complete Release Please changelog additions.

#### Scenario: Synchronized golden and contract fixtures

- GIVEN the effective Stage-A update set synchronizes the public runtime to `0.2.0`
- WHEN the typed and annotated root updaters run
- THEN the golden's `tool.version` and both model contract fixture tool versions become `0.2.0`
- AND the README's four intended release-version lines become `0.2.0`
- AND no unrelated semver text is replaced

#### Scenario: Content-mutated approved carrier file

- GIVEN a merged Stage-A PR lists an approved golden, README, contract, candidate, or generated path
- WHEN its complete patch contains `9.9.9`, arbitrary content, an unapproved marker, or missing/
  truncated patch data
- THEN Stage-B fails closed before tag, label, release, upload, or publication mutation

### Requirement: Linked versions must not depend on tag naming

The release architecture MUST prove that every intended runtime Cargo crate, the npm wrapper, and all
six npm platform packages resolve to one version and that the wrapper's `optionalDependencies` are
rewritten from that synchronized versions map. The private conformance crate is not part of that
linked version map; its four path dependency pins are updated by the root carrier to consume the
same runtime version. Under the exact Release Please 17.6.0 source,
`include-component-in-tag: false` returns an empty strategy component and
`linked-versions` skips empty components. Therefore the release flow MUST either use a supported
Release Please implementation whose linked lookup is independent of tag naming, or separate the
component-tagged version-PR pass from a trusted post-merge carrier that creates exactly one unprefixed
`vX.Y.Z` tag. A configuration that merely lists component names while the effective strategy component
is empty is invalid and MUST remain blocked.

#### Scenario: v17.6.0 empty-component gate

- GIVEN the global unprefixed-tag contract is enabled under Release Please 17.6.0
- WHEN `LinkedVersions.preconfigure()` evaluates the configured strategies
- THEN the regression MUST observe a synchronized versions map for the full runtime graph, or report
  the exact architecture blocker instead of claiming that optional dependency synchronization passed

#### Scenario: Synchronized npm optional pins

- GIVEN the linked versions map contains the full runtime graph at version `X.Y.Z`
- WHEN the v17.6.0 Node workspace/package-json updater processes `npm/codegauge/package.json`
- THEN every platform entry in `optionalDependencies` is rewritten to its corresponding synchronized
  platform version, including any supported range prefix, and the final release carrier emits only
  `vX.Y.Z`

### Requirement: Auditable hosted carrier rehearsal

The Stage-B carrier MUST accept only trusted `push` or `workflow_dispatch` events resolved to
`refs/heads/main`. A manual dispatch MUST expose a required boolean `dry_run` input. An automatic
push MUST derive its mode from the explicit repository variable `RELEASE_CARRIER_DRY_RUN`, accepting
only `true`, `false`, or unset; unset and `false` MUST preserve the live production default and any
unknown value MUST fail closed. The manual input MUST take precedence for a manual run.

Both modes MUST collect and validate the same merged Release Please version PR, exact Stage-A diff,
tree/version/provenance/lockfile/metadata boundaries, and canonical `vX.Y.Z` tag plan. Dry-run mode
MUST emit a credential-free machine-readable carrier plan and workflow-summary record, and MUST NOT
create or update a Git ref, mutate Release Please labels, dispatch `release-on-tag.yml`, upload a
release asset, or invoke any registry publisher. Live mode MUST retain the existing tag compare/create,
race retry, and label handoff behavior.

Before tree or version validation, the carrier MUST correlate merged Release Please PRs to the exact
trusted event SHA. Zero matching PRs on a trusted `main` push or dispatch MUST be a successful no-op:
the carrier MUST emit a skipped/no-matching-release record and summary, and MUST NOT run carrier
validation or any tag, label, release, upload, or publication path. Exactly one matching PR MUST enter
the full validation flow. More than one matching PR, an invalid PR collection, or malformed PR data
MUST fail closed before mutation.

#### Scenario: Ordinary main push has no matching Release Please PR

- GIVEN a trusted `push` or `workflow_dispatch` on `refs/heads/main`
- AND the GitHub pull-request collection contains zero merged Release Please PRs whose
  `merge_commit_sha` equals `GITHUB_SHA`
- WHEN the carrier correlates the event before fetching the version-PR diff
- THEN the workflow exits successfully with `status=skipped` and reason
  `no-matching-release-please-pr`
- AND it emits `carrier-record.json` plus a workflow summary proving carrier validation, tag, label,
  release, upload, and publication paths were not run

#### Scenario: Exactly one Release Please PR matches the event SHA

- GIVEN a trusted `main` event with exactly one merged Release Please PR whose `merge_commit_sha`
  equals `GITHUB_SHA`
- WHEN the carrier correlates the pull requests
- THEN it fetches that PR's diff and continues the existing exact tree, version, provenance, tag-plan,
  dry-run, live, idempotency, and conflict validation flow

#### Scenario: Multiple matching Release Please PRs or malformed data

- GIVEN a trusted `main` event with more than one matching Release Please PR or malformed GitHub PR
  collection data
- WHEN the carrier correlates the pull requests
- THEN it fails closed before fetching the diff or performing any mutation

#### Scenario: Manual carrier dry-run

- GIVEN `release-tag-carrier.yml` is dispatched on `main` with `dry_run: true`
- WHEN the carrier collects the merged Release Please PR and validates the merged tree
- THEN it emits the canonical tag plan and explicit skipped-mutation evidence
- AND it MUST NOT create a tag, change labels, dispatch the tag workflow, upload, or publish

#### Scenario: Automatic push rehearsal variable

- GIVEN `RELEASE_CARRIER_DRY_RUN` is temporarily set to the exact value `true`
- WHEN the synchronized Release Please version PR is merged into `main`
- THEN the automatic carrier performs the same read-only validation and plan generation
- AND it MUST skip tag-ref and label writes so the merge cannot start the live tag path

#### Scenario: Live default after rehearsal

- GIVEN `RELEASE_CARRIER_DRY_RUN` is absent or set to `false`
- WHEN a trusted synchronized version PR merge pushes `main`
- THEN the carrier remains in live mode and preserves the canonical tag compare/create and label handoff

#### Scenario: Invalid rehearsal configuration

- GIVEN the dispatch input or repository variable contains a value other than the accepted booleans
- WHEN the carrier resolves its mode
- THEN it fails closed before any tag or label mutation

### Requirement: Approved archive matrix and checksums

The release MUST use the approved complete viable target matrix of eight archives: Linux GNU and
musl for x86_64 and aarch64, macOS x64 and arm64, and Windows x64 and arm64. Every approved target
MUST have the correct platform archive format (`tar.gz` on Unix-like targets and `zip` on Windows),
a version/target-identifiable name, and a lowercase SHA-256 sidecar. Each sidecar MUST be verified
before GitHub upload and before any archive extraction for packaging. A target that cannot produce
reproducible build and runtime evidence MUST be rejected rather than claimed.

#### Scenario: Complete archive release

- GIVEN the complete viable target matrix has been approved
- WHEN all target builds finish
- THEN every approved target has one archive and checksum, and each checksum verifies the archive

#### Scenario: Missing target evidence

- GIVEN a matrix entry has no archive or sidecar
- WHEN release assets are prepared
- THEN the GitHub Release and dependent registry publishers remain blocked

### Requirement: Ordered, gated channel publication

GitHub Release assets MUST be uploaded only after quality, target, package, checksum, and metadata
gates pass. If npm is enabled, platform packages MUST publish before the base wrapper. If Cargo
registry publication is enabled, dependencies MUST publish before dependents. OCI publication MUST
wait for its architecture and runtime gates.

#### Scenario: Gate failure before upload

- GIVEN a checksum or package gate fails
- WHEN the release graph reaches publication
- THEN no later channel publisher runs and the failure remains auditable

### Requirement: Provenance and publication security

Release metadata MUST record the source revision, version, target, and artifact checksums. Publishing
jobs MUST use only the credentials and permissions they require, use trusted OIDC provenance where
the registry supports it, and MUST NOT place tokens in artifacts, logs, or repository files.

#### Scenario: Credential exposure check

- GIVEN a release job emits an artifact or log containing a registry token
- WHEN security validation runs
- THEN the release fails and the affected publication is not promoted

### Requirement: Non-atomic failure recovery

On any publication failure, the workflow MUST stop later publishers, retain logs and successful
artifact history, and expose a recovery action. Escaped npm or OCI artifacts MUST be deprecated,
retagged, or superseded by a corrected patch; Cargo versions already published MUST NOT be treated
as deletable. Release triggers MAY be disabled while recovery is performed.

#### Scenario: Partial publication

- GIVEN GitHub assets publish but an npm or OCI publisher fails
- WHEN the failure is recorded
- THEN later jobs stop, the partial state is documented, and a corrected release path is identified
