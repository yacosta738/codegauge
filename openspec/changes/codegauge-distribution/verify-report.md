# Verification Report

**Change**: `codegauge-distribution`

## Fresh executor verification — 2026-08-15 (authoritative)

**Change**: `codegauge-distribution`
**Mode**: OpenSpec
**Verification scope**: current carrier-correlation diff, all five delta specs, design/tasks,
workflow topology, carrier/provenance/runtime tests, and relevant local quality/package checks
**Branch**: `fix/release-carrier-skip-unmatched`
**Checkout**: `HEAD=6c9e6dfd8507b12d37eef21b303cfe435e70abc9`, equal to `origin/main`, plus the
intentionally dirty 11-file remediation/artifact checkout
**Version under test**: `0.1.0`
**Baseline**: `6477eb1`
**Persistence mode**: OpenSpec
**Scope**: technical conformance only; observable acceptance remains with `sdd-qa`
**Safety boundary**: no commit, push, merge, repository-variable change, tag, release, upload,
publication, attestation, credential injection, or hosted write

### Completeness

| Metric | Result |
|---|---:|
| Task checkboxes | 28 |
| Complete | 24 |
| Incomplete | 4 |
| Requirements reviewed | 25 |
| Scenarios reviewed | 40 |
| Technical verdict | **PASS WITH WARNINGS** |

Incomplete tasks are hosted/acceptance gates only: `4.2`, `4.3`, `7.4`, and `8.4`. No local
implementation task is incomplete.

### Build, tests, and coverage evidence

| Command/check | Result |
|---|---|
| Carrier correlation runtime suite | **PASS**: zero-match skip, exact-one matching/full validation, neighboring ordinary PR, multiple-match rejection, malformed-shape rejection, wrong ref/SHA, private/unapproved/missing state, strict SemVer, idempotency, and conflicts |
| Carrier static/security suite | **PASS**: exact correlation-before-diff ordering, matched-only validation/mutation gates, full-SHA actions, permissions, token separation, concurrency, canonical tag topology, and no publication calls |
| Exact Release Please runtime | **PASS**: installed `17.6.0` fake SCM produced one synchronized PR, six optional pin rewrites to `0.2.0`, zero release calls, zero tag calls, and no private conformance candidate; private Stage-B mutation rejected |
| Provenance/distribution/bootstrap/README suites | **PASS** |
| OCI regression layers | **PASS**: primary, static, evidence, and failure suites |
| Python/package checks | **PASS**: `compileall`, npm package generation, and the hermetic no-match record probe |
| Locked Cargo gates | **PASS**: metadata, 31 workspace tests (0 failed/0 skipped), check, fmt, and Clippy `-D warnings` |
| Cargo package verification | **PASS**: all five runtime crates with locked local dependency patch verification; no publication |
| npm gates | **PASS**: wrapper typecheck, six npm tests, and wrapper plus six platform `npm pack --dry-run` checks |
| Workflow/container/whitespace gates | **PASS**: `actionlint`, ShellCheck, Dockerfile `buildx --check`, and `git diff --check` |
| Carrier mode probe | **PASS**: manual true/false, push variable true/false/unset, precedence, and invalid-value rejection |
| Hosted/publication checks | **NOT RUN** by safety boundary; no credentials or hosted state were used |
| Coverage | ➖ Not configured; `openspec/config.yaml` declares coverage unavailable |

The local no-match probe emitted `status=skipped`, reason `no-matching-release-please-pr`, and
explicit `not-run`/`not-started`/`not-dispatched` mutation statuses without creating a diff input.
The workflow itself remains hosted-only; this probe plus the checked-in runtime/static tests is not
hosted acceptance evidence.

### Spec compliance matrix

`✅ LOCAL` means a covering local runtime test or executable validator passed. `⚠️ PARTIAL` means
the local/static contract is green but hosted execution, publication, native target evidence, or
failure injection was unavailable or prohibited. No local scenario failed.

| ID | Scenario | Evidence | Result |
|---|---|---|---|
| CI-1 | Untrusted pull request has no release credentials | Workflow permissions inspection; no hosted PR run | ⚠️ PARTIAL |
| CI-2 | Mutable action reference blocks distribution | Full-SHA audit and actionlint; no injected mutable ref | ⚠️ PARTIAL |
| CI-3 | Baseline quality commands pass | Locked Cargo/Python suites | ✅ LOCAL |
| CI-4 | Existing lint failure remains blocking | `-D warnings` retained; no failure injection | ⚠️ PARTIAL |
| CI-5 | Incomplete target declaration blocks eligibility | Distribution/OCI negative validators | ✅ LOCAL |
| CI-6 | Failed preflight blocks later publishers | Workflow `needs` topology; no hosted injection | ⚠️ PARTIAL |
| CARGO-1 | Runtime graph packages/publishes in order | Five local package checks and workflow order; no registry publish | ⚠️ PARTIAL |
| CARGO-2 | Source fallback preserves CLI contracts | Locked workspace tests plus `version`/`profiles` runtime | ✅ LOCAL |
| CARGO-3 | Immutable source install preserves behavior | No canonical tag/release exists | ⚠️ PARTIAL |
| CARGO-4 | Distribution-only change preserves RFC-0001 | Workspace/conformance/CLI tests | ✅ LOCAL |
| CARGO-5 | Incomplete Cargo package stops upload | Positive package checks; no failure injection | ⚠️ PARTIAL |
| CARGO-6 | Cargo/version/provenance mismatch blocks release | Carrier/provenance drift mutations | ✅ LOCAL |
| NPM-1 | Only approved base and six platform packages are eligible | Generator, manifests, typecheck, tests, and seven pack dry-runs | ✅ LOCAL |
| NPM-2 | Supported runtime selects exactly one package | npm target-resolution tests | ✅ LOCAL |
| NPM-3 | Unsupported/missing optional dependency fails nonzero | npm negative tests | ✅ LOCAL |
| NPM-4 | npm arguments/stdio/exit status pass through | npm passthrough test | ✅ LOCAL |
| NPM-5 | Checksum mismatch blocks npm eligibility | Provenance/checksum regression validators | ✅ LOCAL |
| OCI-1 | Only approved GHCR identity is eligible | Workflow identity/permission static checks; no registry run | ⚠️ PARTIAL |
| OCI-2 | Unsupported OCI architecture is rejected | OCI negative suite | ✅ LOCAL |
| OCI-3 | Workspace-aware non-root image builds/runs | Dockerfile and local OCI evidence suites; no fresh hosted matrix | ⚠️ PARTIAL |
| OCI-4 | OCI label/runtime/root/digest drift fails | OCI evidence regression suite | ✅ LOCAL |
| OCI-5 | Failed architecture blocks manifest/tags | Fail-stop topology; no hosted failure injection | ⚠️ PARTIAL |
| REL-1 | Version/source provenance mismatch blocks release | Provenance identity and version-drift checks; no immutable hosted release | ⚠️ PARTIAL |
| REL-2 | Root updates survive exact v17.6.0 plugins | Exact fake-SCM runtime and effective-set evidence | ✅ LOCAL |
| REL-3 | Virtual root cannot publish as a fake package | Root carrier config/runtime checks and zero release calls | ✅ LOCAL |
| REL-4 | Private conformance stays outside Stage-A | Exact harness plus private mutation rejection | ✅ LOCAL |
| REL-5 | v17.6.0 empty-component/tag coupling is avoided | Component-tagged runtime chain | ✅ LOCAL |
| REL-6 | Six npm optional pins synchronize | Exact Node/linked-version runtime | ✅ LOCAL |
| REL-7 | Zero matching PRs are an auditable no-op | Classifier, CLI, record probe, and matched-only workflow gates; no hosted run | ✅ LOCAL / ⚠️ HOSTED |
| REL-8 | Exactly one matching PR enters full validation | Full carrier validator plus exact-one runtime fixture; no hosted run | ✅ LOCAL / ⚠️ HOSTED |
| REL-9 | Multiple/malformed PR data fails closed | Runtime classifier and CLI nonzero cases before diff fetch | ✅ LOCAL |
| REL-10 | Manual dry-run plans without mutation | Mode/plan probes and static mutation gates; no hosted run | ✅ LOCAL / ⚠️ HOSTED |
| REL-11 | Push variable `true` is plan-only | Mode normalization and static mutation gates; no hosted run | ✅ LOCAL / ⚠️ HOSTED |
| REL-12 | Unset/`false` preserves live default | Mode probe and live-only conditions; no hosted write | ✅ LOCAL / ⚠️ HOSTED |
| REL-13 | Invalid rehearsal mode fails closed | Invalid-value mode probe and static checks | ✅ LOCAL |
| REL-14 | Complete eight-target archive release is proven | Local archive/package validators; native hosted matrix absent | ⚠️ PARTIAL |
| REL-15 | Missing target blocks dependent channels | Archive failure validator | ✅ LOCAL |
| REL-16 | Gate failure blocks upload/publish | Workflow dependency topology; no hosted failure injection | ⚠️ PARTIAL |
| REL-17 | Credential exposure blocks promotion | Credential-free records/static inspection; no credential-bearing run | ⚠️ PARTIAL |
| REL-18 | Partial publication stops and exposes recovery | Documented ordered graph; no publication/rollback rehearsal | ⚠️ PARTIAL |

**Matrix summary:** 25 scenarios have executable local coverage, 15 remain partial external or
failure-injection boundaries, and 0 failed locally. The `REL-7`/`REL-8` hosted portions remain
explicitly unclaimed.

### Correctness

| Requirement/contract | Status | Evidence |
|---|---|---|
| Exact event correlation precedes diff/tree/version validation | ✅ LOCAL | `carrier-pr-selection`, static ordering check, and no-match record probe |
| Zero-match trusted main event is successful and non-mutating | ✅ LOCAL / ⚠️ HOSTED | Classifier/CLI, record fields, and matched-only conditions; hosted event unrun |
| Exactly one matching PR follows the existing full carrier path | ✅ LOCAL | Mixed ordinary/release fixture and `validate_carrier_event` |
| Multiple/malformed collection fails closed before diff | ✅ LOCAL | Shape validation, multiple-match runtime/CLI failures, and workflow order |
| Wrong base/ref/SHA and missing/unapproved/malformed state cannot mutate | ✅ LOCAL | Full validator negatives; wrong-context PRs are excluded as the safe zero-match path |
| Stage-A exact v17.6.0 graph/private boundary/no-write behavior | ✅ LOCAL | Fake-SCM output: one PR, six pins, zero release/tag calls, no private candidate |
| Dry-run/live/idempotency/conflict gates remain intact | ✅ LOCAL / ⚠️ HOSTED | Runtime planner, mode probe, static conditions; no hosted mutation |
| Full-SHA actions, permissions, token usage, concurrency | ✅ LOCAL | Static carrier/distribution suites and `actionlint` |
| Downstream canonical tag is the sole release trigger and post-gate release owner | ✅ LOCAL / ⚠️ HOSTED | Tag caller/reusable workflow topology; event delivery unrun |

### Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Component-tagged Stage A plus trusted post-merge carrier | ✅ | Current config/workflows preserve the two-stage split |
| Explicit five-crate list and non-Cargo root carrier | ✅ | Exact v17.6.0 runtime test excludes private conformance |
| Correlate event SHA before Stage-B validation | ✅ | Shared classifier runs before PR diff fetch and matched-only gates all later steps |
| Manual/variable dry-run is reversible | ✅ | Explicit input/variable normalization and no-mutation plan statuses remain present |
| Canonical tag is the downstream release trigger | ✅ LOCAL / ⚠️ HOSTED | Static/reusable topology passes; hosted delivery remains unobserved |

### Issues found

#### CRITICAL

None.

#### WARNING

1. Protected hosted rehearsal for an ordinary main push, the actual Release Please merge, and the
   manual/variable carrier dry-run remains unrun. PAT scope/masking/ref authorization, branch
   protection, tag delivery, and downstream workflow execution are not locally observable.
2. Publication, attestation, native non-host target evidence, partial-publication rollback, and
   failure-injection acceptance remain unavailable or explicitly prohibited; `sdd-qa` owns those
   acceptance scenarios.
3. The worktree is intentionally dirty, so strict-TDD commit ordering cannot be independently proved;
   `strict_tdd: true` is configured but the installed `strict-tdd-verify.md` module is absent.

#### SUGGESTION

1. Promote the hermetic carrier mode/record probe into a checked-in workflow-step harness after the
   protected hosted rehearsal, so the exact shell boundary is regression-tested without credentials.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Zero matching PRs skip before validation/diff/mutation and emit an auditable record | ✅ classifier/runtime | ✅ static/order + jq record probe | SUGGESTION | Confirmed locally |
| Exactly one matching PR reaches full validation and mutation mode gates | ✅ carrier runtime | ✅ workflow conditions/actionlint | SUGGESTION | Confirmed locally |
| Multiple or malformed PR data fails closed | ✅ runtime/CLI | ✅ collection-before-diff workflow | SUGGESTION | Confirmed locally |
| Wrong base/ref/SHA and private/unapproved/missing state cannot produce a tag | ✅ negative fixtures | ✅ validator/static mutation guards | SUGGESTION | Confirmed locally |
| Stage-A exact v17.6.0 graph has one PR, six pins, zero release/tag calls | ✅ package runtime | ✅ fake-SCM counters/private exclusion | SUGGESTION | Confirmed locally |
| Pins, permissions, concurrency, token boundaries, and canonical downstream gating | ✅ static suites | ✅ actionlint/topology inspection | SUGGESTION | Confirmed locally; hosted unrun |
| Hosted carrier/release/publication/acceptance | ✅ policy boundary | ❌ not executed or authorized | WARNING | Remaining external gate |

### Final verdict

**PASS WITH WARNINGS** — every requested local contract and relevant local quality/package/workflow
check passed. Only hosted rehearsal, hosted delivery/publication, native target, failure-injection,
and independent acceptance evidence remain. Hand off explicitly to `sdd-qa`; this report makes no
user/operator acceptance claim.

## Previous fresh executor verification — 2026-08-15 (pre-correlation fix; superseded)

**Change**: `codegauge-distribution`
**Mode**: OpenSpec
**Verification scope**: current dirty diff, workflows, carrier/provenance/runtime tests, all OpenSpec
artifacts, QA handoff, and the requested local quality/package/container checks
**Safety boundary**: no commit, push, merge, repository-variable change, tag, release, upload,
publication, attestation, credential injection, or hosted write

### Completeness

| Metric | Result |
|---|---:|
| Task checkboxes | 24 |
| Complete | 21 |
| Incomplete | 3 |
| Requirements reviewed | 25 |
| Scenarios reviewed | 37 |
| Technical verdict | **PASS WITH WARNINGS** |

The remaining unchecked tasks are `4.2` (protected hosted rehearsal), `4.3` (combined verify/QA task;
independent QA is still pending), and `7.4` (hosted variable/manual rehearsal). No local implementation
task is incomplete.

### Build, tests, and coverage evidence

| Command/check | Result |
|---|---|
| Carrier/provenance/distribution/bootstrap/README tests | **PASS**: all seven focused Python commands exited 0 |
| Exact Release Please runtime | **PASS**: `17.6.0` fake SCM produced one synchronized PR, six optional pin rewrites, zero release calls, zero tag calls, and rejected the private mutation |
| OCI regression layers | **PASS**: primary, static, evidence, and failure suites |
| Python compile/package generation | **PASS**: `compileall -q scripts tests` and `generate_npm_packages.py --check` |
| Locked Cargo gates | **PASS**: metadata, 31 workspace tests (0 failed/0 skipped), check, fmt, and Clippy `-D warnings` |
| Cargo packages | **PASS**: all five runtime crates packaged and verified with `--locked --allow-dirty`; Cargo only warned that integration tests are not package contents |
| npm gates | **PASS**: typecheck, six npm tests, wrapper plus six platform `npm pack --dry-run` checks |
| Workflow/container/whitespace gates | **PASS**: actionlint, `shellcheck scripts/build_oci_release.sh`, Dockerfile `docker buildx build --check`, and `git diff --check` |
| Exact carrier mode probe | **PASS**: manual true/false, push variable true/false/unset, and invalid values were executed from the checked-in shell step; manual input precedence held |
| Exact dry-run plan probe | **PASS** with a read-only fake `gh`: `carrier-plan.json`, summary, and dry-run no-mutation guard passed; no POST/PUT/publish step was reached |
| Coverage | ➖ Not configured; `openspec/config.yaml` declares coverage unavailable |

The mode and plan probes are supplemental local execution evidence, not hosted acceptance evidence and
not committed test files. They did not expose a secret; the plan schema contains event identity,
validation results, tag observations, and mutation statuses only.

### Spec compliance matrix

`COMPLIANT` means the local covering check/test passed. `PARTIAL` means the local/static contract is
green but hosted execution, publication, native target evidence, or failure injection was unavailable
or prohibited. No scenario failed locally.

| ID | Scenario | Test/evidence | Result |
|---|---|---|---|
| CI-1 | Untrusted pull request is read-only and has no release credentials | workflow/static audit; no hosted PR run | ⚠️ PARTIAL |
| CI-2 | Mutable action reference blocks distribution | full-SHA static suite + actionlint; no injected mutable ref | ⚠️ PARTIAL |
| CI-3 | Baseline metadata/tests/fmt/Clippy/Python gates pass | Cargo and focused Python commands | ✅ COMPLIANT |
| CI-4 | Existing lint failure remains blocking | `-D warnings` inspection; no failure injection | ⚠️ PARTIAL |
| CI-5 | Incomplete target declaration blocks eligibility | distribution/OCI failure checks | ✅ COMPLIANT |
| CI-6 | Failed preflight blocks later publishers | reusable-workflow topology; no hosted failure injection | ⚠️ PARTIAL |
| CARGO-1 | Runtime crates publish in dependency order | five package verifications and workflow order; no registry publish | ⚠️ PARTIAL |
| CARGO-2 | Source fallback builds with released contracts | locked workspace tests/check and CLI integration coverage | ✅ COMPLIANT |
| CARGO-3 | Immutable recorded revision install preserves behavior | no canonical tag/release exists | ⚠️ PARTIAL |
| CARGO-4 | Distribution-only change preserves RFC-0001 behavior | workspace/conformance/CLI tests | ✅ COMPLIANT |
| CARGO-5 | Incomplete Cargo package stops before upload | positive package checks; no missing-file fixture | ⚠️ PARTIAL |
| CARGO-6 | Cargo/version/provenance mismatch blocks release | carrier/provenance drift mutations | ✅ COMPLIANT |
| NPM-1 | Only approved base and six same-scope packages are eligible | generator, manifest, typecheck, tests, seven pack dry-runs | ✅ COMPLIANT |
| NPM-2 | Supported runtime selects exactly one platform package | npm wrapper target-resolution tests | ✅ COMPLIANT |
| NPM-3 | Unsupported/missing optional dependency fails actionable and nonzero | npm missing/musl/unsupported tests | ✅ COMPLIANT |
| NPM-4 | npm arguments, stdio, and exit status pass through | npm passthrough test | ✅ COMPLIANT |
| NPM-5 | Checksum mismatch blocks platform and base packages | provenance/checksum validators; no publication run | ⚠️ PARTIAL |
| OCI-1 | Only approved GHCR identity is eligible | workflow identity/permission static checks; no registry run | ⚠️ PARTIAL |
| OCI-2 | Unsupported OCI architecture is rejected | OCI negative suite | ✅ COMPLIANT |
| OCI-3 | Workspace-aware non-root image builds and runs | Dockerfile check and synthetic/local OCI checks; no fresh multi-arch publish run | ⚠️ PARTIAL |
| OCI-4 | OCI label/runtime/root/emulation/digest drift fails | OCI evidence regression suite | ✅ COMPLIANT |
| OCI-5 | Failed architecture blocks manifest/tags | fail-stop topology; no hosted failure injection | ⚠️ PARTIAL |
| REL-1 | Version/source provenance mismatch blocks release | provenance identity and version drift checks; no immutable hosted release | ⚠️ PARTIAL |
| REL-2 | Root updates survive the exact v17.6.0 plugin pipeline | runtime fake SCM and effective-path evidence | ✅ COMPLIANT |
| REL-3 | Virtual root cannot publish as a fake package | root carrier config/runtime checks | ✅ COMPLIANT |
| REL-4 | Private conformance stays outside Stage-A updates | exact harness plus private mutation rejection | ✅ COMPLIANT |
| REL-5 | v17.6.0 empty-component/tag coupling is avoided | component-tagged runtime chain, zero release/tag calls | ✅ COMPLIANT |
| REL-6 | All six npm optional pins synchronize | exact Node workspace/updater execution | ✅ COMPLIANT |
| REL-7 | Manual carrier dry-run on main validates the merged graph and plans without mutation | manual event validator, exact mode step, plan/guard probe | ✅ COMPLIANT locally |
| REL-8 | `RELEASE_CARRIER_DRY_RUN=true` makes automatic push plan-only | exact push-variable mode execution + static workflow guards | ✅ COMPLIANT locally |
| REL-9 | Unset/`false` repository variable keeps the live path | exact push-unset/false mode execution and live conditional guards | ✅ COMPLIANT locally |
| REL-10 | Invalid manual/variable mode fails closed | exact invalid-value mode execution and static checks | ✅ COMPLIANT locally |
| REL-11 | Complete archive matrix has checksums/evidence | archive validators/package evidence; no fresh hosted target matrix | ⚠️ PARTIAL |
| REL-12 | Missing archive target blocks dependent channels | local fail-stop validators; no hosted publisher run | ⚠️ PARTIAL |
| REL-13 | Gate failure blocks upload/publish | workflow `needs`/conditional topology; no hosted injection | ⚠️ PARTIAL |
| REL-14 | Credential exposure fails promotion and does not leak tokens | credential-free plan/static inspection; no credential-bearing run | ⚠️ PARTIAL |
| REL-15 | Partial publication stops and exposes recovery | documented ordered graph; no publication/rollback rehearsal | ⚠️ PARTIAL |

**Matrix summary**: 20/37 scenarios locally compliant, 17/37 partial, 0/37 failing. The partial rows
are external acceptance or prohibited failure-injection boundaries, not observed local defects.

### Correctness

| Requirement/contract | Status | Evidence |
|---|---|---|
| Manual `workflow_dispatch` is main-only and shares PR/tree/version validation | ✅ | `validate_carrier_event` accepts the manual event on `refs/heads/main`; manual and push records match |
| Repository-variable mode precedence/defaults | ✅ locally | exact shell-step probe passed `true`, `false`, unset, manual precedence, and invalid-value cases |
| Auditable dry-run plan and summary | ✅ locally | exact plan step emitted credential-free `carrier-plan.json` and `GITHUB_STEP_SUMMARY` content |
| Dry-run no-mutation boundary | ✅ locally | plan guard records skipped tag/label, not-dispatched tag workflow, not-started publication; mutation steps are live-only |
| Live compare/create/no-op/conflict behavior | ✅ | pure tag-plan tests cover create, same-SHA no-op, conflicting SHA, annotated tag, and release conflict |
| Fail-closed trust, full SHA, least privilege, concurrency | ✅ locally | carrier tests/static audit/actionlint cover main ref, event SHA, token separation, read permissions, non-canceling group, and immutable action refs |
| Stage-A version graph/private boundary | ✅ | exact Release Please 17.6.0 fake-SCM chain and private-candidate mutation regression |
| Secret handling and temporary-variable documentation | ✅ locally | no token value is emitted by the plan/summary paths; README documents exact variable and deletion command |

### Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Component-tagged Release Please Stage A plus trusted post-merge carrier | ✅ | config, version-PR workflow, carrier, and canonical tag caller implement the split |
| Explicit five-crate list instead of `cargo-workspace` discovery | ✅ | runtime harness and config exclude private conformance |
| Java root metadata carrier with no package identity | ✅ | root candidate owns typed root files and skips release/changelog/snapshot |
| Manual/variable dry-run is temporary and reversible | ✅ | manual input and exact repository variable; README documents removal |
| Shared read-only collection/validation before mode-specific mutation | ✅ | carrier steps collect/validate/plan before live-only tag/label steps |
| Canonical tag is the only downstream release trigger | ✅ locally | tag caller and static topology pass; hosted event delivery remains unobserved |

### TDD compliance audit

| Check | Result |
|---|---|
| Strict TDD configured | ✅ `strict_tdd: true`; configured runner exists |
| RED → GREEN → REFACTOR for 7.1–7.3 | ✅ recorded in `apply-progress.md`; focused suites pass |
| Manual/variable/live/no-mutation regression presence | ✅ runtime manual/step probes plus checked-in static assertions |
| Tests committed before or with code | ⚠️ Cannot independently verify; worktree is intentionally dirty |
| Strict verifier module | ⚠️ `strict-tdd-verify.md` is absent from the installed skill directory |

### Issues found

#### CRITICAL

None.

#### WARNING

1. Protected hosted rehearsal for the variable-controlled merge and manual `dry_run: true` remains
   unrun, including PAT scope/masking/ref authorization, branch protection, tag delivery, and
   downstream workflow observation. No hosted write was attempted.
2. Publication, attestation, native non-host target evidence, and partial-publication rollback remain
   unavailable or explicitly prohibited; `sdd-qa` remains the acceptance owner.
3. The worktree is dirty, so commit-order TDD proof is unavailable, and the installed strict verifier
   module is missing.
4. The checked-in Release Please harness records raw updater proposals before the exact
   `GitHub.buildChangeSet` missing-file filter; the effective path set was probed read-only, but that
   effective-set assertion is not yet a committed harness assertion.

#### SUGGESTION

1. Promote the exact carrier mode/plan probe into a checked-in hermetic workflow-step harness, then
   rerun verification after hosted rehearsal.
2. Add the effective `GitHub.buildChangeSet` path assertion to the checked-in runtime harness.
3. Remove `RELEASE_CARRIER_DRY_RUN` immediately after the authorized hosted rehearsal.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Manual dispatch on main validates the same carrier graph | ✅ validator/source | ✅ exact manual-step probe | SUGGESTION | Confirmed locally |
| Variable `true` is plan-only; unset/`false` is live | ✅ exact shell cases | ✅ static mutation guards | SUGGESTION | Confirmed locally |
| Dry-run plan/summary is credential-free and no-mutation | ✅ exact plan output | ✅ conditional/static guards | SUGGESTION | Confirmed locally |
| Live tag path is idempotent and conflict-safe | ✅ pure planner | ✅ carrier mutation workflow/static tests | SUGGESTION | Confirmed locally |
| Stage-A graph has one PR, six pin rewrites, zero release/tag calls | ✅ exact package runtime | ✅ fake-SCM counters/private rejection | SUGGESTION | Confirmed locally |
| Hosted rehearsal/publication/acceptance | ✅ policy boundary | ❌ not executed or authorized | WARNING | Remaining external gate |
| Strict-TDD commit ordering | ✅ apply evidence | ❌ dirty worktree | WARNING | Cannot independently verify |

### Final verdict

**PASS WITH WARNINGS** — all requested local contracts and local quality/package/workflow checks pass;
the remaining risks are hosted rehearsal and acceptance evidence only. Hand off explicitly to
`sdd-qa`; do not claim user/operator acceptance from this technical report.

## Previous R-F6 verification handoff — 2026-08-15 (superseded by the fresh executor run)

This section is retained as prior technical handoff history. The fresh executor section above is now
authoritative for this verification phase.

### Completeness

| Metric | Result |
|---|---:|
| Checkboxes in current `tasks.md` | 20 |
| Checkboxes marked complete | 18 |
| Checkboxes marked incomplete | 2 |
| Requirements reviewed | 24 |
| Scenarios reviewed | 33 |
| Current technical verdict | **PASS WITH WARNINGS** |

Tasks `4.2` (protected hosted Stage-A/tag-triggered no-publication rehearsal) and `4.3` (downstream
QA) remain intentionally incomplete. Verification task `6.4` is complete. No incomplete local
contract or implementation defect was found.

### Safety boundary and checkout

- Checkout: `/Users/acosta/Dev/agent-swarm/codegauge`, branch `fix/release-please-root-files`,
  `HEAD=1623c7175dcc9dd07427c0a48a89054bb274bce1`, intentionally dirty.
- Toolchain: Rust/Cargo `1.97.1`, Node `24.19.0`, npm `11.17.0`, Python `3.14.6`.
- Exact installed `release-please` package: `17.6.0`.
- Local and read-only remote `v*.*.*` tag listings were empty.
- No GitHub API write, workflow dispatch, tag, GitHub Release, Cargo publish, npm publish, GHCR
  push, upload, attestation, merge, commit, or credential injection was performed.

### Current diff and artifact inspection

- Inspected the dirty diff for `release-please-config.json`, `.release-please-manifest.json`, all
  release workflows, `scripts/verify_release_provenance.py`, the R-F6 tests/harness, and the CLI
  version assertion.
- Read the current proposal, all five delta specs, design, tasks, apply progress, state, config,
  QA handoff, and prior verification history before judging the implementation.
- Stage A configuration contains the Java `codegauge-root` carrier, exactly five explicit runtime
  Cargo candidates, the npm wrapper, and six platform npm candidates. It contains no
  `cargo-workspace` plugin and no `crates/codegauge-conformance` Release Please candidate.
- `cargo metadata --locked --no-deps` reported six real packages (five runtime crates plus the
  private conformance crate), no virtual-root `codegauge` package, and preserved conformance as a
  workspace/build-test member.

### Build, test, and inspection evidence

| Command/check | Result and exact evidence |
|---|---|
| `python3 tests/release_please_runtime_tests.py` | PASS against exact `17.6.0`; one synchronized fake PR, six optional dependency versions rewritten to `0.2.0`, `releaseCalls=0`, `tagCalls=0`, private mutation rejected |
| Exact v17.6.0 effective changeset probe | PASS; exact `GitHub.prototype.buildChangeSet` semantics plus read-only fake SCM produced the approved 31-path effective set and dropped absent `createIfMissing=false` proposals |
| `python3 tests/release_carrier_tests.py` | PASS; generated changelog positives, private/unapproved/missing/root mutations, trust/ref/PR/SHA, strict SemVer, release conflict, tag conflict, and same-SHA idempotency |
| `python3 tests/release_carrier_static_tests.py` | PASS; full-SHA refs, Stage-A/Stage-B separation, token handling, read-only carrier permissions, trusted main, concurrency, canonical tag topology, and no force/delete |
| `python3 tests/release_provenance_tests.py`, `tests/distribution_checks.py`, `tests/bootstrap_checks.py`, `tests/readme_checks.py` | PASS |
| OCI regression layers | PASS: `oci_distribution_tests.py`, static, evidence, and failure suites |
| Python/package checks | PASS: `python3 -m compileall -q scripts tests`; `python3 scripts/generate_npm_packages.py --check` |
| Locked Cargo gates | PASS: metadata, workspace tests (31 passed, 0 failed, 0 skipped), check, fmt, and Clippy `-D warnings` |
| Cargo package verification | PASS for all five runtime crates; Cargo only warned that package tests are not included |
| npm gates | PASS: typecheck, 6 npm tests, and wrapper plus six platform `npm pack --dry-run` checks (7 packages) |
| Workflow/container/whitespace gates | PASS: `actionlint`, `shellcheck scripts/build_oci_release.sh`, `docker buildx build --check --progress=plain .`, and `git diff --check` |
| Coverage | Not configured; `openspec/config.yaml` declares coverage unavailable |

### Exact R-F6 runtime evidence

The checked-in harness executes the exact `Manifest`/`NodeWorkspace`/`LinkedVersions`/`Merge` chain
from `release-please@17.6.0` against a read-only fake SCM. It observes one synchronized PR, six
optional dependency rewrites, and zero release/tag calls. The raw `Update[]` passed to the SCM
contains absent generated proposals that the real v17.6.0 `GitHub.buildChangeSet` drops when
`createIfMissing` is false. A supplemental read-only probe invoked that exact packaged
`GitHub.prototype.buildChangeSet` implementation with the same fake file boundary; its effective
set was exactly:

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

This is seven root metadata files, five runtime Cargo manifests, twelve approved generated
changelogs, and seven npm manifests. The wrapper update rewrites all six `optionalDependencies` to
the synchronized `0.2.0` version. The effective set contains no private conformance manifest,
virtual-root package, or unapproved path.

### Requested R-F6 contract matrix

| Contract/scenario | Covering evidence | Result |
|---|---|---|
| Five explicit Cargo candidates plus Java root carrier | Current config, exact v17.6.0 chain, no `cargo-workspace` plugin | ✅ COMPLIANT |
| Effective Stage-A path set is exact and excludes private/virtual/unapproved paths | Exact packaged `GitHub.buildChangeSet` probe; 31 approved paths listed above | ✅ COMPLIANT |
| Six optionalDependency rewrites | Runtime harness output and updater execution | ✅ COMPLIANT |
| Exactly one synchronized PR; zero release/tag calls | Read-only fake SCM counters | ✅ COMPLIANT |
| Stage-B accepts legitimate generated changelogs | Twelve exact changelog positives in carrier tests | ✅ COMPLIANT |
| Stage-B rejects private/unapproved/missing/conflicting states | Private path, evil/near-match path, root-file deletion, tag/release conflict mutations | ✅ COMPLIANT |
| Strict SemVer 2.0 and canonical `vX.Y.Z` only | Leading-zero, malformed, prerelease/build, tag-shape, and planning tests | ✅ COMPLIANT |
| Idempotent tag planning | Same-SHA no-op; different-SHA/annotated/conflicting states fail closed | ✅ COMPLIANT |
| Full-SHA pins, least privilege, trusted main, concurrency | Static audit plus actionlint across all workflows | ✅ COMPLIANT locally |
| PAT/GITHUB_TOKEN handling and tag-triggered downstream gating | Stage-A/carrier PAT boundaries, post-gate GITHUB_TOKEN release ownership, canonical tag caller | ✅ COMPLIANT locally; hosted delivery unrun |

### Full specification compliance matrix

`COMPLIANT` means the local covering test/check passed. `PARTIAL` means the local/static portion
passed but hosted, immutable, publication, native-target, or failure-injection evidence was not run.
No current scenario is `FAILING`.

| ID | Scenario | Result |
|---|---|---|
| CI-1 | Untrusted pull request | ⚠️ PARTIAL |
| CI-2 | Floating workflow dependency | ⚠️ PARTIAL |
| CI-3 | All baseline checks pass | ✅ COMPLIANT |
| CI-4 | Existing lint failure remains blocking | ⚠️ PARTIAL |
| CI-5 | Incomplete target declaration | ✅ COMPLIANT |
| CI-6 | Failed preflight blocks later jobs | ⚠️ PARTIAL |
| CARGO-1 | Approved registry graph | ⚠️ PARTIAL |
| CARGO-2 | Source fallback remains available | ✅ COMPLIANT |
| CARGO-3 | Immutable source install | ⚠️ PARTIAL |
| CARGO-4 | Distribution-only change preserves RFC-0001 contracts | ✅ COMPLIANT |
| CARGO-5 | Incomplete Cargo package stops publication | ⚠️ PARTIAL |
| CARGO-6 | Version mismatch blocks release | ✅ COMPLIANT |
| NPM-1 | Approved base and six same-scope packages | ✅ COMPLIANT |
| NPM-2 | Supported platform selects one package | ✅ COMPLIANT |
| NPM-3 | Unsupported/missing optional dependency | ✅ COMPLIANT |
| NPM-4 | CLI args/stdio/exit passthrough | ✅ COMPLIANT |
| NPM-5 | Checksum mismatch blocks npm publication | ⚠️ PARTIAL |
| REL-1 | Provenance mismatch blocks release | ⚠️ PARTIAL |
| REL-2 | Root updates survive the v17.6.0 plugin pipeline | ✅ COMPLIANT |
| REL-3 | Virtual root cannot publish as a fake package | ✅ COMPLIANT |
| REL-4 | Private workspace member stays outside Stage-A updates | ✅ COMPLIANT |
| REL-5 | v17.6.0 empty-component gate is avoided | ✅ COMPLIANT |
| REL-6 | Synchronized npm optional pins | ✅ COMPLIANT |
| REL-7 | Complete archive release | ⚠️ PARTIAL |
| REL-8 | Missing target evidence blocks channels | ✅ COMPLIANT |
| REL-9 | Gate failure blocks upload | ⚠️ PARTIAL |
| REL-10 | Credential exposure is blocked | ⚠️ PARTIAL |
| REL-11 | Partial publication stops and exposes recovery | ⚠️ PARTIAL |
| OCI-1 | Only approved GHCR identity is eligible | ⚠️ PARTIAL |
| OCI-2 | Unsupported architecture is rejected | ✅ COMPLIANT |
| OCI-3 | Workspace-aware non-root image | ✅ COMPLIANT |
| OCI-4 | OCI labels/runtime/digest mismatch fails validation | ✅ COMPLIANT |
| OCI-5 | Failed architecture blocks manifest/tags | ⚠️ PARTIAL |

**Matrix summary:** 18/33 COMPLIANT, 15/33 PARTIAL, 0/33 FAILING. The partial rows are external
or failure-injection evidence, not observed local defects.

### Correctness

| Area | Status | Evidence/notes |
|---|---|---|
| Stage-A explicit runtime/private boundary | ✅ | Five explicit Cargo candidates, Java root carrier, no cargo-workspace discovery, no conformance update |
| Effective Stage-A updates and six npm rewrites | ✅ | Exact packaged changeset probe and runtime fake-SCM counters |
| Stage-A no-release/no-tag boundary | ✅ local | `skip-github-release` action/config plus zero release/tag calls; hosted action run remains unavailable |
| Virtual root and private conformance boundaries | ✅ | Cargo metadata has no virtual-root package; conformance remains a private build/test member |
| Stage-B exact diff/root-state boundary | ✅ | Exact allowlist, generated changelog positives, private/unapproved/missing mutations pass/fail as required |
| Stage-B SemVer/tag/idempotency/conflict behavior | ✅ | Strict SemVer 2.0, canonical tag planning, no-op and fail-closed conflict tests pass |
| Workflow pinning/security/topology | ✅ local | Full-SHA audit, least-privilege checks, trusted main, concurrency, PAT/GITHUB_TOKEN boundaries, actionlint |
| Canonical tag-triggered downstream release gating | ⚠️ | Static/local wiring passes; hosted tag delivery and post-gate release were not executed |

### Design coherence

| Design decision | Followed? | Evidence/notes |
|---|---|---|
| Option 1: component-tagged Stage A plus trusted post-merge carrier | ✅ | Current config and both carrier/tag workflows implement the split |
| Explicit five-crate list instead of v17.6.0 cargo-workspace | ✅ | Exact source boundary and runtime candidate/update evidence |
| Java root metadata carrier with no package identity | ✅ | `release-type: java`, typed root files, package/release/changelog/snapshot skips |
| Stage A creates one PR and no artifact | ✅ local / ⚠️ hosted | Fake SCM counters and action input pass; hosted execution remains unrun |
| Stage B creates one immutable canonical tag | ✅ local | Pure compare/create/no-op/conflict logic and canonical `vX.Y.Z` tests |
| Release workflow is tag-triggered and post-gate owned | ✅ local | `release-on-tag.yml`, reusable inputs, build `needs`, and publish ordering pass actionlint/static checks |
| Exact Stage-A diff is fail-closed | ✅ | Effective changeset contains only approved paths; Stage-B validator rejects all tested mutations |

### Issues

#### CRITICAL

None.

#### WARNING

1. Hosted Release Please execution, merged-main carrier execution, PAT scope/masking/ref
   authorization, branch protection, canonical tag delivery, tag-triggered workflow execution,
   registry publication, final OCI manifest/attestation, native non-host targets, and rollback /
   failure-injection rehearsal remain unrun or unauthorized.
2. Tasks `4.2` and `4.3` remain incomplete; this report makes no user/operator acceptance claim.
3. The worktree is intentionally dirty, so independent strict-TDD commit-order verification is not
   possible; `strict-tdd-verify.md` is absent from the installed skill directory.
4. Coverage is unavailable and no threshold is configured.
5. The checked-in runtime harness records raw proposals before `buildChangeSet`; the exact effective
   filtering boundary was independently exercised read-only and passed, but that probe is not a
   committed harness change.

#### SUGGESTION

1. Make the checked-in fake SCM record/assert the exact effective `GitHub.buildChangeSet` paths so a
   future regression cannot rely on the supplemental probe to distinguish raw proposals from PR
   changed files.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Five explicit runtime Cargo candidates plus Java root carrier | ✅ config/source | ✅ exact v17.6.0 chain | SUGGESTION | Confirmed locally |
| Effective Stage-A set has exactly approved paths | ✅ exact `GitHub.buildChangeSet` | ✅ path-set comparison | SUGGESTION | Confirmed locally |
| Private conformance, virtual root, and unapproved paths excluded | ✅ config/metadata | ✅ runtime and mutation tests | SUGGESTION | Confirmed locally |
| Six optional pins, one synchronized PR, zero release/tag calls | ✅ updater/counters | ✅ exact harness output | SUGGESTION | Confirmed locally |
| Stage-B changelog, negative, strict-SemVer, idempotency, and conflict behavior | ✅ validator inspection | ✅ focused suite | SUGGESTION | Confirmed locally |
| Full-SHA, permissions, trusted main, concurrency, token handling, tag gating | ✅ workflow inspection | ✅ static suite/actionlint | SUGGESTION | Confirmed locally; hosted unrun |
| Hosted tag delivery/publication/acceptance QA | ✅ policy boundary | ❌ prohibited/unavailable | WARNING | Remaining external gate |

### Current final verdict

**PASS WITH WARNINGS** — every requested local contract and relevant local quality gate passes. The
remaining risks are hosted/acceptance evidence only, and no hosted write or publication was
performed. Hand off explicitly to **`sdd-qa`** for acceptance scenarios; do not claim user/operator
acceptance from this technical report.

## Superseded R-F6 verification — 2026-08-15

This section is authoritative for this re-verification. The local remediation checks requested by
the orchestrator pass, but the exact Release Please runtime still exposes one local Stage-A/Stage-B
integration defect. The technical verdict is **FAIL**; hosted and publication state was not touched.

### Completeness

| Metric | Result |
|---|---:|
| Checkboxes in current `tasks.md` | 16 |
| Checkboxes marked complete | 14 |
| Checkboxes marked incomplete | 2 |
| Requirements reviewed | 23 |
| Scenarios reviewed | 32 |
| Current technical verdict | **FAIL** |

Tasks `4.2` (protected hosted Stage-A/tag-triggered no-publication rehearsal) and `4.3`
(downstream QA) remain intentionally incomplete. Local task `5.5` and all four requested carrier
defect remediations were exercised. A checked implementation task is not accepted when the exact
runtime chain contradicts the Stage-B boundary.

### Safety boundary and checkout

- Checkout: `/Users/acosta/Dev/agent-swarm/codegauge`, branch `fix/release-please-root-files`,
  `HEAD=1623c7175dcc9dd07427c0a48a89054bb274bce1`, intentionally dirty.
- Toolchain: Rust/Cargo `1.97.1`, Node `24.19.0`, npm `11.17.0`, Python `3.14.6`.
- `npx --yes release-please@17.6.0 --version` returned `17.6.0`; the exact package was used by
  the runtime harness.
- Local and read-only remote `v*.*.*` tag listings were empty.
- No GitHub API write, workflow dispatch, tag, GitHub Release, Cargo publish, npm publish, GHCR
  push, upload, attestation, merge, commit, or credential injection was performed.

### Current diff inspected

- Release topology/config: `.github/workflows/release*.yml`, `release-please-config.json`, and
  `.release-please-manifest.json`.
- Carrier implementation/tests: `scripts/verify_release_provenance.py`,
  `tests/release_carrier_tests.py`, `tests/release_carrier_static_tests.py`,
  `tests/release_please_runtime_tests.py`, `tests/release_please_runtime_harness.mjs`,
  `tests/release_provenance_tests.py`, and distribution static checks.
- Existing contract touch: `crates/codegauge-cli/tests/cli.rs`; no engine implementation change.
- OpenSpec progress artifacts: `apply-progress.md`, `design.md`, `specs/release-artifacts/spec.md`,
  `tasks.md`, `state.yaml`, and this `verify-report.md`.

### Build, test, and inspection evidence

| Command/check | Result and exact evidence |
|---|---|
| `python3 tests/release_carrier_tests.py` | PASS; exact changelog positives, arbitrary/evil/near-match npm and changelog negatives, five root-file mutations, trust/ref/PR/SHA, tag conflict/idempotency, release conflict, and SemVer cases |
| `python3 tests/release_carrier_static_tests.py` | PASS; Stage-A/Stage-B separation, token selection, read-only defaults, full-SHA actions, tag topology, permissions, concurrency, and no force-update/delete |
| `python3 tests/release_please_runtime_tests.py` | PASS against exact `17.6.0`; `synchronizedPullRequests=1`, six optional dependency versions rewritten to `0.2.0`, `releaseCalls=0`, `tagCalls=0` |
| `python3 tests/release_provenance_tests.py`, `tests/distribution_checks.py`, `tests/bootstrap_checks.py`, `tests/readme_checks.py` | PASS |
| OCI regression layers | PASS: `oci_distribution_tests.py`, static, evidence, and failure suites |
| Python/package checks | PASS: `python3 -m compileall -q scripts tests`; `python3 scripts/generate_npm_packages.py --check` |
| Locked Cargo gates | PASS: metadata, workspace tests (31 passed, 0 failed, 0 skipped), check, fmt, and Clippy `-D warnings` |
| Cargo package verification | PASS for all five runtime crates; Cargo only warned that package tests are not included |
| npm gates | PASS: typecheck, 6 npm tests, and wrapper plus six platform `npm pack --dry-run` checks (7 packages) |
| Workflow/container/whitespace gates | PASS: `actionlint`, `shellcheck scripts/build_oci_release.sh`, `docker buildx build --check --progress=plain .`, and `git diff --check` |
| Coverage | Not configured; `openspec/config.yaml` declares coverage unavailable |

### Strict-TDD audit

| Check | Result |
|---|---|
| Strict TDD mode | Active in `openspec/config.yaml`; configured runner exists |
| RED → GREEN → REFACTOR evidence | Recorded for the carrier remediation in `apply-progress.md`; focused runtime and mutation suites pass |
| Commit ordering | Not independently provable because the worktree is intentionally dirty |
| Strict verifier module | `strict-tdd-verify.md` is absent from the installed skill directory |

### Requested contract matrix

| Contract/scenario | Covering evidence | Result |
|---|---|---|
| Exact approved Stage-A changelog paths | All 12 configured runtime changelog paths accepted by `validate_stage_a_diff`; root, nested, and evil changelog paths rejected | ✅ COMPLIANT locally |
| npm diff allowlist | Base wrapper plus all six approved platform `package.json` paths accepted; evil, x86 near-match, and `.bak` paths rejected | ✅ COMPLIANT locally |
| Java root carrier presence | Each of the five root-owned files was deleted in turn and `validate_carrier_tree()` rejected the mutation | ✅ COMPLIANT locally |
| Strict SemVer 2.0 | Valid prerelease/build identifiers accepted; leading-zero core/prerelease identifiers and malformed values rejected before tag planning | ✅ COMPLIANT locally |
| Stage-A Release Please runtime | Exact `Manifest.createPullRequests()` plugin chain ran with read-only fake SCM; one fake PR, six optional rewrites, zero release/tag calls | ✅ Requested harness behavior |
| Stage-B trusted event/ref/PR/SHA boundary | Pure carrier tests and workflow checks reject non-main refs, wrong event/merge SHA, duplicate/missing Release Please PRs, and malformed records | ✅ COMPLIANT locally |
| Stage-B tag trust/idempotency/conflict | Create, same-SHA no-op, annotated-tag rejection, different-SHA conflict, existing-release conflict, retry, and full lowercase SHA cases pass | ✅ COMPLIANT locally |
| Stage-B permissions/pinning/concurrency | Static audit and actionlint pass read-only defaults, `RELEASE_PLEASE_TOKEN` use, no `GITHUB_TOKEN` fallback, non-canceling groups, and full-SHA refs | ✅ COMPLIANT locally |
| Stage-A cannot publish; canonical tag is Stage-B-owned | Stage-A skip input/config and no-write harness pass; only `release-tag-carrier.yml` creates `refs/tags/vX.Y.Z` | ✅ Structural/local; hosted delivery unrun |
| Exact Stage-A output can pass Stage-B as a complete flow | Runtime update list includes a generated `crates/codegauge-conformance/Cargo.toml` candidate; the Stage-B allowlist rejects it | ❌ FAILING |

### Critical local defect

The exact v17.6.0 runtime chain creates an update proposal for the private workspace member
`crates/codegauge-conformance/Cargo.toml`. The harness output records that path. The upstream
`CargoWorkspace` plugin scans every Cargo workspace member, including `codegauge-conformance`, and
its `CargoToml` updater changes that existing file from `0.1.0` to `0.1.1` (confirmed locally).
`validate_stage_a_diff()` intentionally rejects the path because it is outside the approved
Stage-A set. Therefore the real synchronized PR would not pass the Stage-B carrier boundary, and
the design contract that private conformance remains outside Release Please is not currently
verified.

The harness is still genuine for the requested no-write Manifest/plugin/linked-version behavior,
but its fake `createPullRequest()` records proposed updates rather than invoking Release Please's
`GitHub.buildChangeSet()`. It therefore does not filter missing `createIfMissing: false` files like
the hosted SCM layer would. That explains the additional absent lock/sample/changelog proposals in
the raw list, but it does not remove the conformance defect: `crates/codegauge-conformance/Cargo.toml`
exists and its updater produces changed content.

### Correctness and design coherence

| Area | Status | Evidence/notes |
|---|---|---|
| Exact allowlists and root mutations | ✅ | Focused runtime mutation suite passed |
| SemVer/tag planning | ✅ | Strict regex and create/no-op/conflict tests passed |
| Stage-A no-release/no-tag boundary | ✅ local | Exact runtime fake SCM recorded zero release/tag calls; hosted action run remains unavailable |
| Linked runtime graph and six npm rewrites | ✅ local | Exact v17.6.0 plugin chain observed one synchronized PR and six rewritten pins |
| Private conformance exclusion | ❌ | Exact Cargo workspace plugin still emits an existing conformance manifest update proposal |
| Stage-B carrier security/idempotency | ✅ local | Pure validator, workflow static checks, actionlint, full-SHA audit |
| Canonical tag-triggered release wiring | ⚠️ | Static/local checks pass; tag delivery and post-gate release were not executed |

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Exact changelog allowlist accepts only the 12 approved runtime paths | ✅ source/constants | ✅ mutation suite | SUGGESTION | Confirmed locally |
| npm allowlist accepts only wrapper plus six approved platform manifests | ✅ exact set | ✅ positive/negative tests | SUGGESTION | Confirmed locally |
| Every Java root carrier file is required | ✅ validator | ✅ five deletion mutations | SUGGESTION | Confirmed locally |
| Strict SemVer 2.0 rejects leading zeros/malformed identifiers | ✅ regex | ✅ valid/invalid tag tests | SUGGESTION | Confirmed locally |
| Exact Release Please 17.6.0 chain records one PR, six rewrites, zero release/tag calls | ✅ `Manifest`/plugin execution | ✅ harness output | WARNING | Confirmed locally; no hosted SCM |
| Private conformance manifest is outside the effective Stage-A update set | ✅ exact runtime path | ✅ CargoToml updater changed existing file | CRITICAL | Confirmed defect |
| Stage-B ref/tag/idempotency/conflict/permissions/full-SHA/concurrency contracts | ✅ validators/workflows | ✅ focused/static/actionlint suites | SUGGESTION | Confirmed locally |
| Hosted tag delivery, publication, and acceptance QA | ✅ policy boundary | ❌ prohibited/unavailable | WARNING | Remaining external gate |

### Current final verdict

**FAIL** — all requested local carrier hardening checks and the exact no-write Release Please
runtime metrics pass, but the exact upstream Cargo workspace plugin still proposes a change to the
existing private conformance manifest. Because the Stage-B allowlist rejects that path, the complete
Stage-A-to-Stage-B contract has a local failure. Do not hand off to `sdd-qa` until the private
candidate/update boundary is repaired and this phase is rerun. Hosted/publication evidence remains
unrun and unauthorized.

## Prior R-F6 verification — 2026-08-14 (superseded)

This section is retained as historical audit evidence and is superseded by the 2026-08-15
re-verification above.
The local quality suites are green, but the Stage-B carrier boundary has confirmed fail-closed and
generated-diff defects. The technical verdict is **FAIL**; no hosted or publication state was touched.

### Completeness

| Metric | Result |
|---|---:|
| Checkboxes in current `tasks.md` | 11 |
| Checkboxes marked complete | 9 |
| Checkboxes marked incomplete | 2 |
| Requirements reviewed | 23 |
| Scenarios reviewed | 32 |
| Current technical verdict | **FAIL** |

Incomplete tasks are `4.2` (protected hosted Stage-A/tag-triggered no-publication rehearsal) and
`4.3` (downstream `sdd-qa`). They remain intentionally unrun under the user's no-hosted-write and
no-publication boundary. The implementation tasks `1.1` through `3.3` and local verification task
`4.1` are checked, but verification does not accept a checked task when source behavior contradicts
the contract.

### Safety boundary and environment

- Local checkout: macOS arm64, Rust/Cargo `1.97.1`, Node `24.19.0`, npm `11.17.0`, Python `3.14.6`,
  Docker Buildx, actionlint, and ShellCheck.
- Exact `release-please@17.6.0 --version` returned `17.6.0`.
- Read-only inspection of `release-please-action` v5.0.0 confirms its package lock resolves
  `release-please` `17.6.0`; its action source skips `Manifest.createReleases()` when
  `skip-github-release` is true and still runs `createPullRequests()`.
- `git tag --list 'v*.*.*'` and read-only `git ls-remote --refs origin 'refs/tags/v*.*.*'` returned
  no canonical release tag.
- No GitHub API write, workflow dispatch, tag, GitHub Release, Cargo publish, npm publish, GHCR
  push, upload, attestation, credential injection, branch, merge, or commit was performed.

### Build, test, and inspection evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_carrier_tests.py` | PASS; positive carrier record/CLI, wrong ref/SHA, duplicate PR, graph/lock/manifest drift, bootstrap, tag conflict, annotated tag, release conflict, and same-SHA no-op paths |
| `python3 tests/release_provenance_tests.py` | PASS; source-faithful v17.6.0 root/link/node model and existing provenance negatives |
| `python3 tests/distribution_checks.py` | PASS; E3a topology plus carrier/static security checks |
| `python3 tests/bootstrap_checks.py`, `python3 tests/readme_checks.py` | PASS |
| OCI regression layers (`tests/oci_distribution_*.py`) | PASS; static ordering, synthetic evidence, and negative failure-stop paths |
| `python3 -m compileall -q scripts tests` | PASS |
| `python3 scripts/generate_npm_packages.py --check` | PASS |
| `cargo +1.97.1 metadata --locked --format-version 1` | PASS |
| `cargo +1.97.1 test --workspace --locked` | PASS; 31 passed, 0 failed, 0 skipped |
| `cargo +1.97.1 run --locked -p codegauge-cli -- version/profiles` | PASS; `codegauge 0.1.0`, `java-jacoco-v1` |
| `cargo +1.97.1 check --workspace --locked` | PASS |
| `cargo +1.97.1 fmt --all -- --check` | PASS |
| `cargo +1.97.1 clippy --workspace --all-targets --locked -- -D warnings` | PASS |
| Five locked Cargo package verifications with local dependency patches | PASS; packaging/build verification completed; Cargo warned that package tests are not included |
| npm typecheck and tests | PASS; 6 tests passed |
| `npm pack --dry-run` for wrapper plus six platform packages | PASS; 7 packages |
| Synthetic 8-target archive packaging/provenance check | PASS; positive set and missing-target negative |
| `docker buildx build --check --progress=plain .` | PASS; no Dockerfile warnings |
| `actionlint .github/workflows/*.yml` | PASS |
| `shellcheck scripts/build_oci_release.sh` | PASS |
| `git diff --check` | PASS |
| Semantic carrier probes | **FAIL**; four contract defects reproduced (see Issues) |
| Coverage | Not configured; `openspec/config.yaml` declares coverage unavailable |

### Local proof versus remaining hosted verification

**Locally proven:** the exact action source has a release-free Stage-A branch; the checked-in
configuration enables component-tagged linked lookup, preserves the Java root carrier and path
boundaries, excludes the virtual Cargo root/private conformance package, and models the v17.6.0
linked map plus six optional-dependency rewrites. Pure carrier validators and tag planning pass the
positive, negative, conflict, and retry fixtures. Workflow action pins, concurrency, permissions,
canonical tag inputs, post-gate release ownership, Cargo/npm/OCI quality gates, and no-secret
literal checks pass static/runtime local checks.

**Not proven or not permitted:** an actual Release Please SCM run that creates/updates the PR, a
hosted Stage-A observation showing zero tags/releases, a merged-main carrier run, the PAT's scope/
masking/ref authorization, branch protection, compare-and-create race against GitHub, tag event
delivery, tag-triggered workflow execution, native evidence for seven non-host targets, registry
publication, final OCI manifest/attestation, or rollback/failure injection. These are external
gates, not local success claims.

### Spec compliance matrix

`COMPLIANT` means the relevant local runtime/static evidence passed. `PARTIAL` means local proof
exists but hosted, immutable, publication, or failure-injection evidence is absent. `FAILING` means
the current implementation contradicts the scenario, independent of hosted availability.

| ID | Scenario | Covering evidence | Result |
|---|---|---|---|
| CI-1 | Untrusted pull request | CI permissions/secrets inspection; no hosted PR run | ⚠️ PARTIAL |
| CI-2 | Floating workflow dependency | Full-SHA static audit and actionlint; no mutation run | ⚠️ PARTIAL |
| CI-3 | All baseline checks pass | Fresh locked Cargo/Python/format/Clippy suite | ✅ COMPLIANT |
| CI-4 | Existing lint failure remains blocking | `-D warnings` is retained; no injected failure | ⚠️ PARTIAL |
| CI-5 | Incomplete target declaration | Fresh 8-target archive positive/missing-target negative | ✅ COMPLIANT |
| CI-6 | Failed preflight blocks later jobs | Workflow `needs`/fail-stop inspection; no hosted injection | ⚠️ PARTIAL |
| CARGO-1 | Approved registry graph | Five Cargo package verifications and dependency ordering; no registry publish | ⚠️ PARTIAL |
| CARGO-2 | Source fallback remains available | Locked source CLI run and workspace tests | ✅ COMPLIANT |
| CARGO-3 | Immutable source install | No release tag or immutable install target exists | ⚠️ PARTIAL |
| CARGO-4 | Distribution-only change preserves RFC-0001 contracts | 31 locked workspace tests and conformance suite | ✅ COMPLIANT |
| CARGO-5 | Incomplete Cargo package stops publication | Positive package checks only; no missing-file injection | ⚠️ PARTIAL |
| CARGO-6 | Version mismatch blocks release | Carrier graph drift and provenance version negatives | ✅ COMPLIANT |
| NPM-1 | Approved base and six same-scope packages | Generator, manifest, typecheck, tests, and seven pack dry-runs | ✅ COMPLIANT |
| NPM-2 | Supported platform selects one package | Current wrapper target-resolution tests | ✅ COMPLIANT |
| NPM-3 | Unsupported/missing optional dependency | Current missing-dependency and musl/unsupported tests | ✅ COMPLIANT |
| NPM-4 | CLI args/stdio/exit passthrough | Current npm passthrough test | ✅ COMPLIANT |
| NPM-5 | Checksum mismatch blocks npm publication | Prior corruption evidence; no fresh publication rehearsal | ⚠️ PARTIAL |
| REL-1 | Channel version/source mismatch blocks release | Carrier tree/version/provenance validators and negatives | ✅ COMPLIANT |
| REL-2 | Root updates survive v17.6.0 plugin pipeline | Source-faithful model passes, but actual Stage-B diff rejects generated changelog paths | ❌ FAILING |
| REL-3 | Virtual root/private carrier cannot publish a fake package | Java carrier config, Cargo metadata, private-boundary checks; no actual release | ⚠️ PARTIAL |
| REL-4 | v17.6.0 empty-component gate is avoided | Exact source inspection plus `include-component-in-tag: true` model | ✅ COMPLIANT |
| REL-5 | Synchronized npm optional pins | Source-faithful model and exact Node updater source; no generated PR run | ⚠️ PARTIAL |
| REL-6 | Complete archive/checksum matrix | Local synthetic 8-target matrix; seven non-host binaries were not natively run | ⚠️ PARTIAL |
| REL-7 | Missing target evidence blocks channels | Fresh validator negative found 7/8 manifests and stopped | ✅ COMPLIANT |
| REL-8 | Gate failure blocks upload/publish | Static ordering and reusable-workflow needs; no hosted failure injection | ⚠️ PARTIAL |
| REL-9 | Credential exposure is blocked and secrets stay out | Static secret/permission inspection; no credential-bearing run | ⚠️ PARTIAL |
| REL-10 | Partial publication stops and exposes recovery | Static ordered graph/recovery path; no publication failure rehearsal | ⚠️ PARTIAL |
| OCI-1 | Only approved GHCR identity is eligible | Static identity/permission inspection; no registry push | ⚠️ PARTIAL |
| OCI-2 | Unsupported architecture is rejected | Executable synthetic OCI negative test | ✅ COMPLIANT |
| OCI-3 | Workspace-aware non-root image | Dockerfile check and existing local OCI evidence; no fresh full multi-arch build here | ⚠️ PARTIAL |
| OCI-4 | OCI labels/runtime/digest mismatch fails | Executable positive/negative verifier suite | ✅ COMPLIANT |
| OCI-5 | Failed architecture blocks manifest/tags | Static fail-stop checks; no registry/failure injection | ⚠️ PARTIAL |

**Matrix summary:** 12/32 COMPLIANT, 19/32 PARTIAL, 1/32 FAILING. The failing scenario is a
local implementation defect in the carrier's Stage-A diff boundary, not merely an unavailable host.

### R-F6 contract checks

| Contract | Status | Evidence |
|---|---|---|
| Stage A uses Release Please 17.6.0 and creates PRs without releases/tags | ⚠️ Local source/static proof only | v5.0.0 action source/lock, exact package version, config, and static checks; no SCM run |
| Java root carrier owns five root files | ✅ Locally modeled | Exact root candidate/path model and configuration assertions pass |
| Virtual Cargo root and conformance remain non-publishable | ✅ | Cargo metadata and carrier boundary tests pass |
| Component-linked 13-path runtime map | ✅ Locally modeled | Source-faithful v17.6.0 strategy-component model passes |
| Six npm optional pins rewrite from linked map | ⚠️ Locally modeled | Node workspace/updater source and model pass; generated PR not executed |
| Stage B trusts only merged `main`/event SHA | ✅ Pure validator + static workflow proof | Positive carrier test and wrong-ref/SHA/duplicate negatives pass |
| Stage B tag compare/create/no-op/conflict behavior | ✅ Pure runtime proof | Same-SHA, missing, annotated, conflicting, bootstrap, and release-conflict tests pass |
| Stage B exact diff and malformed-state fail-closed boundary | ❌ | Changelog false rejection plus unapproved-path, missing-root-file, and malformed-semver acceptance |
| Canonical tag starts existing tag-driven release workflow | ⚠️ Static proof only | Tag caller/actionlint pass; no event delivery run |
| Existing publish graph remains canonical-tag/gate controlled | ✅ Static workflow proof | Tag-only caller, build `needs`, post-gate release ownership, and publisher ordering pass |

### Correctness

| Area | Status | Evidence |
|---|---|---|
| Stage-A release-free action boundary | ✅ Source-supported | v5.0.0 source gates `Manifest.createReleases()` on `skip-github-release` |
| Effective root candidate survives Cargo/Node filtering | ✅ Locally modeled | Java candidate is non-Cargo and exact source keeps non-Rust candidates out of Cargo graph reconstruction |
| Root metadata ownership/path anchoring | ✅ Structural/model evidence | Five `/...` root paths and package-relative npm path match v17.6.0 `BaseStrategy.addPath` semantics |
| Private Cargo boundaries | ✅ | No virtual-root package; `codegauge-conformance` stays `publish = false` and unlinked |
| Linked map and optional dependency updater | ⚠️ Model/source only | Exact source supports it and model passes, but no actual SCM/PR run |
| Trusted carrier event/tag planner | ✅ | Runtime validator/tag-plan tests pass |
| Carrier diff allowlist | ❌ | Rejects expected runtime changelogs, accepts unapproved npm package paths, and does not require every root carrier file |
| Carrier semver validation | ❌ | Leading-zero minor/patch versions are accepted |
| Tag-triggered release/gate wiring | ✅ Structural | Canonical `v*.*.*` caller and build/publish inputs/needs pass actionlint/static checks |
| Secrets/publication boundary | ⚠️ | No literals or unauthorized writes; hosted credential scope and publication behavior were not run |

### Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Option 1: component-tagged Stage A plus trusted post-merge carrier | ✅ | Implemented in config and the two new workflows |
| Stage A creates one synchronized version PR and no release | ✅ structurally / ⚠️ hosted | Action source and static checks pass; no hosted PR observation |
| Java root metadata carrier, no package identity | ✅ | `release-type: java`, no `package-name`, explicit release/changelog/snapshot skips |
| Virtual root/private conformance stay out of publication | ✅ | Cargo and Release Please boundaries pass locally |
| Stage B uses read-only default permissions and `RELEASE_PLEASE_TOKEN` for ref/label writes | ✅ | Carrier workflow/static security suite pass |
| Exactly one immutable `vX.Y.Z` tag and idempotent retry | ✅ pure logic / ⚠️ hosted | Compare-and-create plan passes; GitHub race was not rehearsed |
| Existing release workflow is canonical-tag driven and post-gate owns GitHub Release | ✅ structural | `release-on-tag.yml`, caller, build gates, and publish checks pass |
| Stage-A PR diff is exact and fail-closed | ❌ | Current allowlist is both over-restrictive for generated changelogs and under-restrictive for unexpected/missing state |

### Strict-TDD audit

| Check | Result |
|---|---|
| Strict TDD mode | Active in `openspec/config.yaml`; configured runner exists |
| RED → GREEN → REFACTOR evidence | Apply progress records RED/GREEN/REFACTOR for R-F6; focused suites are green before semantic defects are considered |
| Tests committed before implementation | ⚠️ Cannot verify; worktree is intentionally dirty |
| Negative coverage quality | ❌ Missing semver, exact npm-path, root-file-presence, and generated-changelog cases; semantic probes exposed all four |
| Strict verifier module | ⚠️ `strict-tdd-verify.md` is absent from the installed skill directory |

### Issues

#### CRITICAL

1. **The carrier rejects a legitimate Release Please Stage-A diff.** The exact v17.6.0 Rust and
   Node strategies add `CHANGELOG.md` updates with `createIfMissing: true` unless `skip-changelog`
   is configured. Every runtime package in the current config inherits `skip-changelog: false`; only
   the root Java carrier skips it. `validate_stage_a_diff()` allows no runtime `CHANGELOG.md`, and
   the fresh probe rejected `crates/codegauge-model/CHANGELOG.md`. A real synchronized PR therefore
   cannot pass Stage B to create its canonical tag.
2. **The carrier is not fail-closed for unexpected or missing root state.** The broad
   `npm/packages/codegauge-[^/]+/package.json` pattern accepts `codegauge-evil/package.json`, and
   `validate_carrier_tree()` accepts a copied tree with the root-owned `README.md` removed. Both
   states were reproduced locally.
3. **Malformed semver is accepted before tag creation.** `VERSION_RE` accepts `1.01.0` and
   `1.2.03`; the carrier can consequently plan a malformed `vX.Y.Z` ref before later Cargo checks.
4. **The required Stage-A behavior lacks an exact Release Please SCM runtime covering test.** The
   passing regression is a source-faithful Python model plus static checks. It does not execute
   `Manifest.createPullRequests()` against a fake/isolated SCM or observe the action's no-tag/no-
   release side-effect boundary. Under the verification contract this remains `UNTESTED`, even
   though the exact upstream source was inspected and the hosted run was intentionally prohibited.

#### WARNING

1. Hosted Release Please execution, merged-main carrier execution, PAT scope/masking/ref
   authorization, branch protection, canonical tag delivery, tag-triggered workflow execution,
   registry publication, final OCI manifest/attestation, native non-host targets, and rollback /
   failure-injection rehearsal remain unrun.
2. Tasks `4.2` and `4.3` remain incomplete because they require protected hosted rehearsal and
   downstream acceptance QA; no user/operator acceptance is claimed.
3. Worktree dirtiness prevents independent strict-TDD commit-order verification.
4. Coverage is unavailable and no threshold is configured.

#### SUGGESTION

1. Make the Stage-A diff contract agree with the exact v17.6.0 generated update set (or explicitly
   disable changelog generation for every runtime candidate), then add exact-set tests.
2. Tighten semver parsing, enumerate the six approved npm paths, require all five root-owned files,
   and add mutation regressions for each rejected state.
3. Add a fake-SCM or disposable hosted dry-run that executes the exact Release Please 17.6.0
   `Manifest` plugin chain and records the generated PR update paths, optional pins, and zero
   release/tag calls.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Release Please action v5.0.0 resolves release-please 17.6.0 | ✅ upstream source/lock | ✅ exact `--version` | SUGGESTION | Confirmed locally |
| Stage A skips release/tag creation | ✅ action source | ✅ workflow/static checks | WARNING | Local source proof; hosted unrun |
| Java root carrier survives plugin boundary | ✅ exact source | ✅ passing model | WARNING | Confirmed locally |
| Linked map contains all 13 paths | ✅ exact plugin source/model | ⚠️ no actual PR | WARNING | Source/model only |
| npm optional dependencies are updater-managed | ✅ Node source | ✅ passing model | WARNING | Source/model only |
| Carrier positive/negative/idempotency logic | ✅ validator inspection | ✅ carrier test suite | SUGGESTION | Confirmed locally |
| Generated runtime changelog is rejected | ✅ Rust/Node source | ✅ semantic probe | CRITICAL | Confirmed defect |
| Unapproved npm diff path is accepted | ✅ regex inspection | ✅ semantic probe | CRITICAL | Confirmed defect |
| Missing root-owned file is accepted | ✅ validator inspection | ✅ copied-tree probe | CRITICAL | Confirmed defect |
| Leading-zero semver is accepted | ✅ regex inspection | ✅ semantic probe | CRITICAL | Confirmed defect |
| Exact Stage-A SCM/no-publication runtime proof | ❌ no integration run | ❌ no hosted run | CRITICAL | UNTESTED |
| Full-SHA/permissions/concurrency/tag topology | ✅ static audit | ✅ actionlint | SUGGESTION | Confirmed locally |
| Hosted tag delivery and registry publication | ✅ policy boundary | ❌ prohibited/unavailable | WARNING | Remaining external gate |

### Current final verdict

**FAIL** — local quality, Cargo, npm, OCI-static, source-faithful Release Please, carrier-positive,
and workflow-security checks pass, but Stage B cannot accept the legitimate Stage-A PR update set
and is not fail-closed for several malformed/unexpected states. Exact hosted release/tag/publication
behavior remains unverified and unauthorized. Do not proceed to acceptance QA until the carrier
boundary is corrected; then rerun `sdd-verify` and hand off to `sdd-qa`.

## Historical re-verification before the R-F6 carrier — 2026-08-14 (superseded)

This section supersedes the historical first re-verification and apply handoff below. The second
apply corrected the discarded virtual-root Rust candidate: the current root candidate is Java,
non-publishable, and survives the exact Cargo/Node workspace filtering boundary in the local
source-faithful model. The non-Release-Please local command set is green, but the exact v17.6.0 source
exposes a second release-graph defect: the global `include-component-in-tag: false` makes every
strategy's `getComponent()` return an empty component, so `linked-versions` preconfiguration skips
every configured component. The checked-in regression now executes that strategy-component gate and
remains RED against the current config. Optional dependency synchronization from the linked versions
map is therefore correctly blocked and the technical verdict remains **FAIL**.

### Completeness

| Metric | Result |
|---|---:|
| Task checkboxes in `tasks.md` | 23 |
| Checkboxes marked complete | 22 |
| Checkboxes marked incomplete | 1 |
| Requirements reviewed | 23 |
| Scenarios reviewed | 33 |
| Current technical verdict | **FAIL** |

22 of 23 task checkboxes are marked complete; the remaining R-F6 architecture task and the source
level contract failure are explicit. The root-candidate retention and path-ownership portion of R-F2
passes local verification; the linked-versions/optional-pin portion remains a core release requirement
failure.

### Build, test, and inspection evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_provenance_tests.py` | RED/FAIL as expected; source-faithful linked strategy gate blocks the unresolved config before optional-pin synchronization can be claimed |
| `python3 tests/distribution_checks.py` | PASS; Cargo/package/workflow topology and root metadata-carrier assertions |
| `python3 tests/bootstrap_checks.py` | PASS |
| `python3 tests/readme_checks.py` | PASS |
| `python3 tests/oci_distribution_tests.py` plus static/evidence/failure suites | PASS |
| `python3 -m compileall -q scripts tests` | PASS |
| `python3 scripts/generate_npm_packages.py --check` | PASS |
| `cargo metadata --locked --format-version 1 --no-deps` | PASS; 6 packages, virtual root absent, `codegauge-conformance` present |
| `cargo test --workspace --locked` | PASS; 31 passed, 0 failed, 0 skipped |
| `cargo test -p codegauge-cli --test cli --locked` | PASS; 3 passed |
| `cargo check --workspace --locked` | PASS |
| `cargo fmt --all -- --check` | PASS |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | PASS |
| `npm --prefix npm/codegauge run typecheck` | PASS |
| `npm --prefix npm/codegauge test` | PASS; 6 passed, 0 failed, 0 skipped |
| `npm pack --dry-run` for base plus six platform packages | PASS; 7 packages |
| `actionlint .github/workflows/*.yml` | PASS |
| `git diff --check` | PASS |
| `npx --yes release-please@17.6.0 --version` | PASS; exact package reports `17.6.0` |
| Negative root-boundary mutation harness | PASS; 4/4 rejected virtual-root Rust, missing root file, missing node component, and duplicate CLI release mutations |
| Coverage | Not configured; `openspec/config.yaml` declares coverage unavailable |

The exact v17.6.0 source was fetched/read-only and the package tarball was inspected locally. The
source confirms: `cargo-workspace` appends the root path, skips a manifest without
`[package].name`, and rebuilds in-scope candidates from the package graph; non-Rust candidates are
returned out of scope; `BaseStrategy` resolves leading `/` extra-file paths at repository root;
`node-workspace` includes `optionalDependencies`; and `PackageJson` rewrites those dependencies.
The Java strategy does not require a Java manifest for typed object extra-files because its base
strategy adds those updates.

The same exact source also confirms `BaseStrategy.getComponent()` returns `''` whenever
`includeComponentInTag` is false, while `LinkedVersions.preconfigure()` skips empty components.
The current config sets the global flag to false and lists 13 named linked components, so the
effective linked preconfiguration group is empty. The checked-in regression now runs that gate,
requires a full 13-path versions map, and only then applies the optional dependency updater and tag
assertions. It is source-faithful local coverage of the defect, not a passing runtime covering test
for the unresolved single-manifest contract.

### Spec compliance matrix

`COMPLIANT` requires a passed local covering test or inspected prior runtime evidence. `PARTIAL`
means the local/static portion passes but hosted, immutable, publication, native-target, or
failure-injection evidence was not run. `FAILING` means the current implementation or regression
does not satisfy the effective source contract.

| ID | Scenario | Evidence | Result |
|---|---|---|---|
| CI-1 | Untrusted pull request | Local permissions audit; no hosted PR run | ⚠️ PARTIAL |
| CI-2 | Floating workflow dependency | Full-SHA audit and actionlint; no mutation injection | ⚠️ PARTIAL |
| CI-3 | All baseline checks pass | Fresh locked Cargo/Python/fmt/Clippy checks | ✅ COMPLIANT |
| CI-4 | Existing lint failure remains blocking | `-D warnings` retained; no failure injection | ⚠️ PARTIAL |
| CI-5 | Incomplete target declaration blocks publishers | Prior recorded 7/8 negative provenance gate | ✅ COMPLIANT |
| CI-6 | Failed preflight blocks later jobs and retains evidence | Workflow fail-stop wiring; no hosted injection | ⚠️ PARTIAL |
| CARGO-1 | Approved registry graph publishes in dependency order | Package/order inspection; no crates.io publication | ⚠️ PARTIAL |
| CARGO-2 | Source fallback remains available | Prior local source-install evidence; no immutable release revision | ⚠️ PARTIAL |
| CARGO-3 | Immutable source install preserves contracts | No release tag or immutable install target | ⚠️ PARTIAL |
| CARGO-4 | Distribution-only change preserves RFC-0001 contracts | Fresh 31-test workspace/conformance suite | ✅ COMPLIANT |
| CARGO-5 | Incomplete Cargo package stops publication | Complete package checks; no missing-file injection | ⚠️ PARTIAL |
| CARGO-6 | Version mismatch blocks release | Fresh provenance test rejects version, identity, binary, and archive drift | ✅ COMPLIANT |
| NPM-1 | Only approved base and six same-scope packages are eligible | Config, generator, pack dry-runs, and package tests | ✅ COMPLIANT |
| NPM-2 | Supported runtime selects exactly one matching package | Prior host runtime evidence plus current wrapper suite | ✅ COMPLIANT |
| NPM-3 | Unsupported/missing dependency returns actionable nonzero error | Current missing-dependency and musl tests | ✅ COMPLIANT |
| NPM-4 | Args, stdio, and child exit status pass through | Current npm passthrough test | ✅ COMPLIANT |
| NPM-5 | Checksum mismatch blocks platform and base publication | Prior recorded corruption regression and validator evidence | ✅ COMPLIANT |
| REL-1 | One immutable merged-main provenance across channels | Root boundary fixed, but linked preconfigure is bypassed and no executable/hosted release run exists | ❌ FAILING |
| REL-2 | Complete eight-archive release has verified formats/sidecars | Prior local matrix evidence; no hosted/native complete release | ⚠️ PARTIAL |
| REL-3 | Missing target evidence blocks assets/registries | Prior recorded 7/8 negative gate | ✅ COMPLIANT |
| REL-4 | Gate failure blocks later publishers | Static ordering/needs checks; no hosted rehearsal | ⚠️ PARTIAL |
| REL-5 | Credential exposure fails promotion and tokens stay out of artifacts/logs | Permission/literal audit; no credential-bearing run | ⚠️ PARTIAL |
| REL-6 | Partial publication stops later jobs and exposes recovery | Workflow/recovery inspection; no publication/failure injection | ⚠️ PARTIAL |
| OCI-1 | Only approved GHCR identity is eligible | Static identity/permission checks; no registry write | ⚠️ PARTIAL |
| OCI-2 | Unsupported architecture is rejected | Current executable OCI negative suite | ✅ COMPLIANT |
| OCI-3 | Workspace-aware locked non-root image builds with init | Prior real local amd64/arm64 Buildx evidence | ✅ COMPLIANT |
| OCI-4 | Label/runtime metadata mismatch fails validation | Current positive/negative OCI verifier suite | ✅ COMPLIANT |
| OCI-5 | One failed architecture blocks manifest/tags | Static fail-stop checks; no failure injection | ⚠️ PARTIAL |

**Scenario summary:** The original 30-scenario matrix remains 12/30 compliant, 17/30 partial, and
1/30 failing. Three new source-faithful linked/tag scenarios are now explicitly tracked; the current
configuration fails their linked-map gate, which is the same core Release Please version-linking/
provenance boundary rather than merely an external publication limitation.

### Correctness

| Area | Status | Evidence |
|---|---|---|
| Effective root candidate survives v17.6.0 Cargo/Node filtering | ✅ Source-supported / locally modeled | Root is `release-type: java`; virtual Cargo root is not a Rust candidate and remains out of scope |
| Root candidate owns all repository extra-files | ✅ Locally modeled | Exact five root paths resolve from typed `/...` entries through BaseStrategy path rules |
| Java carrier is non-publishable | ✅ | No `package-name`, explicit `skip-github-release`, `skip-changelog`, `skip-snapshot` |
| Virtual Cargo root and conformance package boundaries | ✅ | Fresh metadata and conformance tests; `publish = false` remains present |
| One unprefixed tag and no duplicate root/tag candidate | ⚠️ Structural / blocked at linked map | Global tag setting plus only CLI `skip-github-release: false` has the right tag shape, but the current linked map is not formed |
| npm package-relative extra-file path | ✅ | `npm/codegauge` owns `package.json` with package-relative path; exact source `addPath` inspected |
| Optional dependency synchronization from linked versions | ❌ | Exact source makes `getComponent()` empty under the global unprefixed-tag flag, so linked preconfigure skips all components; source-faithful regression remains RED before claiming the rewrite |
| `read_workspace_version` import and invocation | ✅ | Fresh provenance regression passes |
| Dynamic CLI version assertion | ✅ | `env!("CARGO_PKG_VERSION")` and fresh 3-test CLI suite pass |
| RFC-0001 behavior and private conformance | ✅ | Fresh locked workspace/conformance tests pass; no product-code change in this remediation |

### Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Keep the virtual Cargo workspace as the build boundary | ✅ | Cargo metadata and locked tests preserve the six-member workspace |
| Do not publish the virtual root or private conformance crate | ✅ | No virtual-root Cargo package; conformance is private and absent from Release Please packages |
| Root metadata is owned by a surviving non-Cargo candidate | ✅ | Java carrier survives Cargo/Node source boundary and owns typed updates in the model |
| Use linked-versions to synchronize the full runtime graph | ❌ | Current unprefixed-tag setting disables the source strategy-component lookup used by linked preconfiguration |
| Use package-owned, correctly anchored extra-files | ✅ | Root `/...` paths and nested npm `package.json` path match v17.6.0 source semantics |
| Synchronize npm dependencies without a second workspace merge | ⚠️ | `node-workspace merge:false` is configured and source supports optional dependencies, but the linked versions map is not formed by the current strategy path |
| Preserve one unprefixed release tag | ⚠️ | Tag shape is structurally unprefixed, but the synchronized release path is blocked; no hosted Release Please tag/release operation was run |

### Strict-TDD audit

| Check | Result |
|---|---|
| Strict TDD mode | Active in `openspec/config.yaml`; runner exists |
| RED → GREEN → REFACTOR evidence | RED is documented in `apply-progress.md`; GREEN is blocked by the unresolved architecture |
| Source/package runtime boundary RED phase | ✅ Exact source-faithful local model and isolated package probes; no full SCM/hosted run |
| Commit ordering proof | ⚠️ Worktree is intentionally dirty; cannot verify commits-before-code |
| Strict verifier module | ⚠️ `strict-tdd-verify.md` is absent from the installed skill directory |

### Issues

#### CRITICAL

1. **The current linked-versions path is ineffective under the exact v17.6.0 source.** The global
   `include-component-in-tag: false` causes `BaseStrategy.getComponent()` to return an empty string.
   `LinkedVersions.preconfigure()` explicitly skips empty components, so the configured 13-component
   linked group produces no strategy group and no linked version map. A Cargo/root-driven release
   therefore cannot rely on this configuration to rewrite the base npm optional dependency pins.
2. **The effective source path proves a configuration incompatibility.** The updated regression
   executes the `getComponent()`/linked preconfigure gate and fails because the current config forms
   no linked map. Per-package tag inclusion is source-proven to restore linking but produces a
   component-prefixed tag, so R-F6 must implement the two-stage carrier or a supported plugin upgrade.

#### WARNING

1. External-hosted verification remains unavailable: no hosted Release Please dry-run, merged-main
   tag, GitHub Release, native seven non-host archive targets, Cargo/npm/GHCR publication, final OCI
   manifest/attestation, credential-bearing run, or rollback/failure-injection rehearsal was run.
2. The worktree is intentionally dirty, so strict-TDD commit ordering cannot be independently proven.
3. The configured strict-TDD verifier module is missing from the installed skill directory.
4. Coverage is unavailable and no threshold is configured.
5. `qa-report.md` remains a prior `BLOCKED` acceptance handoff; this report is technical only and
   does not claim user/operator acceptance.

#### SUGGESTION

1. Implement the two-stage synchronized version-PR/tag-carrier architecture (or a supported
   Release Please upgrade/plugin) and rerun the source-faithful regression plus a safe hosted dry-run.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Root candidate changed from discarded Rust to non-Cargo Java | ✅ config/source | ✅ focused test | WARNING | Confirmed |
| Root candidate survives v17.6.0 Cargo/Node boundary | ✅ exact source | ✅ local model | WARNING | Confirmed locally; package not executed |
| Typed root extra-files are owned by the surviving root candidate | ✅ path semantics | ✅ focused test | WARNING | Confirmed locally; generated PR not executed |
| Virtual Cargo root remains non-publishable | ✅ Cargo metadata | ✅ distribution/Cargo tests | CRITICAL (prior) | Closed |
| `codegauge-conformance` remains private and unlinked | ✅ manifest | ✅ metadata/distribution tests | CRITICAL (prior) | Closed |
| One unprefixed tag and no duplicate root release | ✅ source/config | ⚠️ linked map is blocked; no hosted release operation | WARNING | Tag shape only; synchronized path unresolved |
| npm `package.json` path is package-relative | ✅ exact BaseStrategy source | ✅ focused test | WARNING | Confirmed locally |
| Optional dependency updater includes optionalDependencies | ✅ exact Node source | ✅ source-faithful model | CRITICAL | Updater is covered, but the current linked map is not formed |
| LinkedVersions preconfigure runs for current config | ✅ exact source | ✅ current global flag | CRITICAL | Confirmed defect |
| `read_workspace_version` import and call | ✅ source | ✅ provenance test | SUGGESTION | Closed |
| Dynamic CLI version assertion | ✅ source | ✅ 3 CLI tests | SUGGESTION | Closed |
| External hosted/tag/publication verification | ✅ policy boundary | ✅ no write run | WARNING | Explicit external risk |

### Current final verdict

**FAIL** — the corrected root candidate and non-Release-Please quality suites pass, but the exact
Release Please 17.6.0 source shows that the current global unprefixed-tag setting disables the
linked-versions preconfiguration path. The updated source-faithful regression proves that no linked
versions map exists for the current config; the full release provenance contract remains unsatisfied
until the tag/link architecture is resolved. No publication or external state was touched.

Technical verification stops here. Hand off to **`sdd-design`/`sdd-apply`** to resolve the
linked-versions/tag architecture, then rerun **`sdd-verify`** before returning to **`sdd-qa`**. The
external hosted verification risk remains even after that local fix.

## Historical pre-remediation verification

| Metric | Result |
|---|---:|
| Task checkboxes in `tasks.md` | 20 |
| Checkboxes marked complete | 20 |
| Checkboxes marked incomplete | 0 |
| Technical task status | **R-F2 fails verification** despite its checkbox being marked complete |
| Requirements reviewed | 21 |
| Scenarios reviewed | 28 |

The task file contains no unchecked boxes, but the root/config remediation is not accepted merely
because the checkbox is checked. R-F2 is a core task because the new root candidate is the only owner
of the repository-level extra-files after the top-level list was removed.

## Historical build, test, and inspection evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_provenance_tests.py` | PASS; static Release Please/config assertions and provenance regressions completed |
| `python3 tests/distribution_checks.py` | PASS |
| `python3 tests/bootstrap_checks.py` | PASS |
| `python3 tests/readme_checks.py` | PASS |
| `python3 -m compileall -q scripts tests` | PASS |
| `cargo metadata --locked --no-deps --format-version 1` | PASS; 6 workspace members/packages, no virtual `codegauge` package, private conformance member remains present |
| `cargo test --workspace --locked` | PASS; 31 passed, 0 failed, 0 skipped |
| `cargo test -p codegauge-cli --test cli --locked` | PASS; 3 passed |
| `cargo check --workspace --locked` | PASS |
| `cargo fmt --all -- --check` | PASS |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | PASS |
| `npm --prefix npm/codegauge run typecheck` | PASS |
| `npm --prefix npm/codegauge test` | PASS; 6 passed, 0 failed, 0 skipped |
| `python3 scripts/generate_npm_packages.py --check` | PASS |
| `actionlint .github/workflows/*.yml` | PASS |
| `git diff --check` | PASS |
| Coverage | Not configured; no threshold exists in `openspec/config.yaml` |

The metadata inspection also showed `codegauge-conformance` is not a publishable Cargo package and
the virtual workspace root is not a Cargo package. No local Release Please CLI is installed, so an
actual 17.6.0 manifest dry-run was not fabricated. The exact v17.6.0 source was inspected read-only.

## Historical Release Please 17.6.0 source inspection

The following source references were inspected at the exact requested version:

- `src/strategies/base.ts`: a leading `/` makes an extra-file path repository-root-relative;
  otherwise a non-root package path is prefixed once by `addPath`.
- `src/plugins/node-workspace.ts`: the workspace graph combines `optionalDependencies` with the
  other dependency maps, and dependent packages are updated through the package JSON updater.
- `src/updaters/node/package-json.ts`: the updater rewrites matching optional dependency versions
  from its versions map while preserving supported range prefixes.
- `src/plugins/workspace.ts`: `merge: false` leaves workspace candidates separate for a later
  linking plugin instead of consuming them in an internal merge.
- `src/plugins/cargo-workspace.ts`: the plugin appends `.` to the Cargo member scan, but skips a
  manifest with no `[package].name`; it then constructs returned candidates only from the package
  graph.

References:

- https://raw.githubusercontent.com/googleapis/release-please/v17.6.0/src/strategies/base.ts
- https://raw.githubusercontent.com/googleapis/release-please/v17.6.0/src/plugins/cargo-workspace.ts
- https://raw.githubusercontent.com/googleapis/release-please/v17.6.0/src/plugins/workspace.ts
- https://raw.githubusercontent.com/googleapis/release-please/v17.6.0/src/plugins/node-workspace.ts
- https://raw.githubusercontent.com/googleapis/release-please/v17.6.0/src/updaters/node/package-json.ts

### Root candidate failure

`release-please-config.json` now declares `packages["."]` with `component: "codegauge-root"` and
`release-type: "rust"`. That candidate is therefore in scope for the v17.6.0 `cargo-workspace`
plugin. During `CargoWorkspace.buildAllPackages`, the repository root `Cargo.toml` is parsed, has
no `[package].name` because it is a virtual workspace, and is skipped before its candidate is added
to `candidatesByPackage`. `WorkspacePlugin.run` then derives `orderedPackages` from that graph and
returns candidates for graph packages only. The root candidate is discarded.

This is not a theoretical path concern: it is the same source path that logs
`Unable to find root candidate pull request` for a virtual Cargo workspace. Because the previous
top-level `extra-files` list was removed, the root README, fixture, contract test, CLI test, and
root-owned TOML update are not actually owned by a candidate that survives the configured plugin
chain. The configuration shape is correct, but the effective Release Please behavior is not.

### Configuration boundaries that do pass inspection

- Root extra-files are root-anchored with `/`, and nested npm `package.json` is package-relative;
  these path forms match v17.6.0 `BaseStrategy.addPath` semantics.
- `node-workspace` is present with `merge: false`; the current base optional dependency map exactly
  equals the six platform package versions, and v17.6.0 source confirms optional dependencies are
  managed by this plugin/updater path.
- `include-component-in-tag: false` remains set; the linked-versions group contains the root
  component, five publishable Cargo components, the base npm component, and six platform components.
- `codegauge-conformance` is absent from Release Please packages and linked components, while its
  Cargo manifest remains `publish = false`.
- `read_workspace_version` is imported from `scripts.verify_release_provenance` and called by the
  regression; the CLI assertion uses `env!("CARGO_PKG_VERSION")` and the focused Cargo test passes.

These passing structural checks do not prove that Release Please generates one release PR containing
the root updates, nor do they prove exactly one hosted unprefixed `vX.Y.Z` release operation.

## Historical spec compliance matrix

`COMPLIANT` requires a covering test/check that passed at runtime. `PARTIAL` means local structural
or host evidence exists but the hosted, immutable, publication, or failure-injection portion was not
executed. `FAILING` means the inspected implementation violates the scenario.

| ID | Scenario | Covering evidence | Result |
|---|---|---|---|
| CI-1 | Untrusted pull request | Workflow permission inspection; no hosted PR run | ⚠️ PARTIAL |
| CI-2 | Floating workflow dependency | Full-SHA audit/actionlint; no mutable-ref injection | ⚠️ PARTIAL |
| CI-3 | All baseline checks pass | Fresh locked Cargo/Python/format/Clippy checks | ✅ COMPLIANT |
| CI-4 | Existing lint failure remains blocking | `-D warnings` retained and current Clippy passes; no injected failure | ⚠️ PARTIAL |
| CI-5 | Incomplete target declaration blocks publishers | Previously recorded 7/8 archive negative gate passed | ✅ COMPLIANT |
| CI-6 | Failed preflight blocks later jobs and retains evidence | Workflow needs/fail-stop inspection; no hosted failure injection | ⚠️ PARTIAL |
| CARGO-1 | Approved registry graph publishes in dependency order | Package/order checks; no registry publication | ⚠️ PARTIAL |
| CARGO-2 | Source fallback remains available | Prior locked source-install smoke; no immutable revision | ⚠️ PARTIAL |
| CARGO-3 | Immutable source install preserves contracts | No release tag or immutable install target exists | ⚠️ PARTIAL |
| CARGO-4 | Distribution-only change preserves RFC-0001 contracts | Fresh 31-test workspace/conformance suite | ✅ COMPLIANT |
| CARGO-5 | Incomplete Cargo package stops publication | Complete package checks; no missing-file rehearsal | ⚠️ PARTIAL |
| CARGO-6 | Version mismatch blocks release | Passing provenance test rejects `9.9.9` and binary drift | ✅ COMPLIANT |
| NPM-1 | Only approved base and six same-scope packages are eligible | Config, generator, package tests, and prior pack checks | ✅ COMPLIANT |
| NPM-2 | Supported runtime selects exactly one matching package | Wrapper target-resolution tests and prior host smoke | ✅ COMPLIANT |
| NPM-3 | Unsupported/missing dependency returns actionable nonzero error | npm missing-dependency and musl tests | ✅ COMPLIANT |
| NPM-4 | Args, stdio, and child exit status pass through | npm passthrough test | ✅ COMPLIANT |
| NPM-5 | Checksum mismatch blocks platform and base publication | Prior corrupted-archive regression; no new failure run in this rerun | ⚠️ PARTIAL |
| REL-1 | One immutable merged-main provenance across channels | Static config test passes, but root candidate is discarded by the v17.6.0 Cargo plugin and no release run exists | ❌ FAILING |
| REL-2 | Complete eight-archive release has verified formats/sidecars | Prior local matrix evidence; no hosted/native complete release | ⚠️ PARTIAL |
| REL-3 | Missing target evidence blocks assets/registries | Previously recorded 7/8 negative gate passed | ✅ COMPLIANT |
| REL-4 | Gate failure blocks later publishers | Static ordering/needs checks; no hosted rehearsal | ⚠️ PARTIAL |
| REL-5 | Credential exposure fails promotion and tokens stay out of artifacts/logs | Permission/literal audit; no credential-bearing run | ⚠️ PARTIAL |
| REL-6 | Partial publication stops later jobs and exposes recovery | Workflow/recovery inspection; no failure injection/publication | ⚠️ PARTIAL |
| OCI-1 | Only approved GHCR identity is eligible | Static identity/permission checks; no registry write | ⚠️ PARTIAL |
| OCI-2 | Unsupported architecture is rejected | Prior executable verifier negative test | ✅ COMPLIANT |
| OCI-3 | Workspace-aware locked non-root image builds with init | Prior real local amd64/arm64 Buildx evidence | ✅ COMPLIANT |
| OCI-4 | Label/runtime metadata mismatch fails validation | Prior positive/negative verifier suite | ✅ COMPLIANT |
| OCI-5 | One failed architecture blocks manifest/tags | Static ordering/fail-stop checks; no failure injection | ⚠️ PARTIAL |

**Scenario summary**: 12/28 compliant, 15/28 partial, 1/28 failing. The failing scenario is a
core Release Please provenance/configuration boundary, not an external publication limitation.

## Historical correctness

| Area | Status | Evidence |
|---|---|---|
| Root candidate owns repository extra-files in effective v17.6.0 flow | ❌ Missing | `cargo-workspace` skips the virtual root and drops the `rust` root candidate |
| Root and nested path declarations | ✅ Structural / runtime-unproven | Exact v17.6.0 path semantics match `/...` root paths and `package.json` nested path |
| npm optional dependency synchronization | ✅ Structural / runtime-unproven | Current pins match; v17.6.0 node-workspace source includes and updates optional dependencies |
| Workspace/Cargo package boundary | ✅ Implemented | Cargo metadata has no virtual root package; five runtime crates are publishable and conformance is private |
| Single unprefixed tag and linked versions | ⚠️ Structural only | Config preserves `include-component-in-tag: false` and linked group; no Release Please execution proves one tag/release |
| `read_workspace_version` import | ✅ Implemented | Import and invocation execute in `release_provenance_tests.py` |
| Dynamic CLI version assertion | ✅ Implemented | `env!("CARGO_PKG_VERSION")` assertion passes in the 3-test CLI integration suite |
| RFC-0001 behavior and private conformance | ✅ Preserved | Fresh workspace tests: 31 passed; no engine contract paths changed in this diff |

## Historical design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Keep the virtual Cargo workspace as the build boundary | ✅ Yes | Cargo metadata and locked tests preserve the six-member workspace |
| Do not publish the virtual root/private conformance crate | ✅ Yes | No root Cargo package; `codegauge-conformance` remains private and absent from Release Please packages |
| One synchronized version from Cargo provenance | ✅ Partially | Literal Cargo versions and dynamic CLI assertion pass, but root extra-file propagation is lost |
| Use Cargo-workspace/linked-versions semantics | ⚠️ Deviated in effect | The root candidate is configured as Rust and is consumed/dropped by Cargo-workspace rather than surviving to linked release processing |
| Use package-owned, correctly anchored extra-files | ✅ Declaration / ❌ effective ownership | Path syntax is correct, but no surviving root candidate owns the files |
| Synchronize npm workspace dependencies without a second merge | ✅ Structurally | `node-workspace merge:false` and linked-versions remain configured; runtime Release Please graph is untested |
| Preserve one unprefixed release tag | ⚠️ Structurally | `include-component-in-tag:false` remains; hosted/tag creation was not run |

## Historical TDD compliance audit

| Check | Result |
|---|---|
| RED → GREEN → REFACTOR evidence | ✅ Documented in `apply-progress.md` for R-F1/R-F2/R-F3 |
| Tests committed before or with code | ⚠️ Cannot verify; the six-file implementation remains uncommitted |
| RED phase for import/config/version regressions | ✅ Documented; the focused provenance test first failed on the missing import/top-level extra-files and the CLI assertion exposed the hard-coded version |
| RED phase for root candidate survival | ❌ Missing; no test executes Release Please 17.6.0's plugin chain |
| Strict-TDD verifier module | ⚠️ `strict_tdd: true` is configured, but `strict-tdd-verify.md` is absent from the installed skill directory |

## Historical issues found

### CRITICAL

1. **R-F2 is behaviorally incorrect for Release Please 17.6.0.** The root candidate is configured
   with `release-type: "rust"`, so `cargo-workspace` consumes it as an in-scope Cargo candidate,
   skips the virtual root because it has no package name, and returns no root candidate. With the
   top-level `extra-files` removed, the intended repository-level files are not updated by the
   effective plugin chain. This violates the root ownership/version-provenance requirement and
   leaves a core task incomplete.
2. **The root-candidate and single-release behavior has no passing runtime covering test.** The
   current Python regression asserts JSON configuration shape only; it does not run Release Please
   17.6.0 or inspect generated update paths. Under the verification contract this is `UNTESTED`,
   independently blocking a PASS.

### WARNING

1. No local Release Please CLI or hosted 17.6.0 dry-run was available; hosted merged-main/tag,
   publication, registry attestation, and rollback evidence remain external and were intentionally
   not run.
2. The worktree is intentionally dirty, so commit ordering for strict TDD cannot be independently
   proven from Git history.
3. The strict-TDD verifier module requested by the configured mode is missing from the installed
   skill directory; `apply-progress.md` was used as the available RED/GREEN/REFACTOR evidence.
4. Coverage is not configured.
5. The existing `qa-report.md` remains a prior `BLOCKED` acceptance handoff; this technical report
   does not claim operator or user acceptance.

### SUGGESTION

1. Add a safe Release Please 17.6.0 integration regression (fake SCM or isolated dry-run) that
   proves root extra-file updates survive `cargo-workspace`, that optional pins are rewritten, and
   that the linked release produces the intended single unprefixed tag.
2. Re-run `sdd-qa` only after the root-candidate behavior is corrected; keep hosted publication and
   registry acceptance separate from technical verification.

## Historical verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Root candidate is declared under `packages["."]` | ✅ | ✅ static regression | WARNING | Config shape confirmed |
| Root candidate survives v17.6.0 `cargo-workspace` | ❌ | ❌ no passing integration test; source flow drops it | CRITICAL | Confirmed failure |
| Root `/...` paths and nested npm `package.json` path | ✅ | ⚠️ no generated PR | WARNING | Structural only |
| npm optional dependency pins are current and updater-managed | ✅ | ⚠️ current equality/npm tests, no Release Please run | WARNING | Structurally supported |
| `read_workspace_version` import and invocation | ✅ | ✅ provenance test passed | SUGGESTION | Closed |
| CLI version assertion follows `CARGO_PKG_VERSION` | ✅ | ✅ 3 CLI tests passed | SUGGESTION | Closed |
| Virtual root is not a Cargo package; conformance remains private | ✅ | ✅ metadata and 31 tests passed | CRITICAL (prior) | Closed |
| Unprefixed tag and linked-version configuration remains present | ✅ | ⚠️ no Release Please/tag run | WARNING | Structurally preserved |

## Historical final verdict

**FAIL** — local quality, Cargo, npm, configuration, and provenance regressions pass, but the
implemented root-candidate fix does not survive the exact Release Please 17.6.0 Cargo workspace
plugin flow. Root extra-files therefore are not proven to be applied, and the missing runtime
covering test independently prevents compliance. No publication or external state was touched.

Technical verification stops here. Hand off to **`sdd-apply`** to correct the root candidate/plugin
boundary, then rerun **`sdd-verify`** before returning to **`sdd-qa`**.

## Historical apply remediation handoff — superseded by current re-verification

The apply remediation changed the configuration boundary without changing the prior verdict above:

- `packages["."]` is now a non-Cargo Java metadata candidate with `initial-version: "0.1.0"`, typed
  root-anchored extra-files, no `package-name`, and explicit `skip-changelog`, `skip-snapshot`, and
  `skip-github-release` settings. A global release skip is overridden only for `codegauge-cli`.
- The new deterministic regression models the exact v17.6.0 Cargo/Node/linked plugin boundary and
  passed locally. It proves root-candidate retention and root update ownership, rewrites all six
  optional pins to a new `0.2.0` map, and leaves exactly one unprefixed `v0.2.0` operation.
- TDD evidence is recorded in `apply-progress.md`: the new regression first failed because the
  virtual-root Rust candidate was dropped, then passed after the configuration fix and remained
  green after helper refactoring.
- The exact Release Please 17.6.0 npm package/action was not executed locally and no hosted dry-run,
  tag, release, publication, credential, or registry operation was performed. The source-faithful
  local model is evidence for re-verification, not a hosted execution claim. `sdd-verify` MUST rerun
  the full conformance matrix and replace this report's prior `FAIL` verdict only if independently
  satisfied.

## Apply handoff — v17.6.0 linked-version/tag boundary — 2026-08-14

The apply remediation added a source-faithful regression and intentionally leaves the technical
verdict **FAIL/BLOCKED** for the current single-manifest architecture. The regression now follows the
effective v17.6.0 path rather than manually unioning JSON candidate components:

- It derives each strategy's component exactly as `BaseStrategy.getComponent()` does. With the
  checked-in global `include-component-in-tag: false`, every strategy component is `''`.
- It applies the exact `LinkedVersions.preconfigure()` falsy guard (`if (!component) continue`) before
  linked-component membership. The configured named components therefore produce no linked version
  map, so the test fails before it can claim optional dependency synchronization.
- It requires a synchronized map for all 13 intended runtime paths, applies the map to the six npm
  platform packages through the `PackageJson` optional-dependency update semantics, and derives the
  resulting release tag from the source-faithful `TagName` behavior.

Exact installed `release-please@17.6.0` source/runtime probes provide the following evidence:

| Configuration | Exact source result |
|---|---|
| Current global `include-component-in-tag: false` | `LinkedVersions` finds zero group components; no linked versions map is formed. |
| Add `""` to `linked-versions.components` | Still zero; the plugin skips the empty component before membership testing. |
| Set linked package strategies to `include-component-in-tag: true` | Linked strategies are forced to the primary version and npm optional pins are update-capable, but `TagName` emits `codegauge-cli-vX.Y.Z`, not `vX.Y.Z`. |

This proves a v17.6.0 built-in single-manifest configuration cannot simultaneously use the required
unprefixed tag and the linked preconfiguration path. The current config was not changed to the
per-package `true` workaround because that would silently violate the existing tag contract. The
required follow-up is a two-stage synchronized version-PR/tag-carrier architecture or a supported
Release Please implementation whose linked lookup is independent of tag naming.

### Local versus hosted evidence

- **Local source-faithful proof:** exact v17.6.0 package source was inspected and isolated runtime
  probes confirmed the empty-component gate, the working component-tagged linked path, the optional
  dependency updater coverage, and the prefixed-tag consequence. The new regression correctly remains
  RED against the current config.
- **Not proven locally or hosted:** a full Release Please SCM/manifest PR run, merged-main release tag,
  GitHub Release, external publication, or failure-injection rehearsal. After R-F6 is implemented,
  hosted verification must prove the real merged PR update set, one `vX.Y.Z` tag/release, all Cargo/npm
  versions, and rewritten optional pins before technical verification can pass.
