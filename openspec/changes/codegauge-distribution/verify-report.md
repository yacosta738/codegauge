# Verification Report

> The Phase 11 and Phase 12 **PASS WITH WARNINGS** verdicts and apply handoffs below are retained as audit
> history. The latest authoritative Phase 13 fresh `sdd-verify` section is at the end of this file.

## Apply handoff — Phase 12 private conformance hunk context — 2026-08-15

Hosted run `31886141725` and the real PR `#59` files API response exposed a valid filename-bound
hunk-only patch for `crates/codegauge-conformance/Cargo.toml`:
`@@ -10,10 +10,10 @@ publish = false`, complete `10/10` hunk counts, four additions, four deletions, and
eight changes. Its context contains the description, `[dependencies]`, the four old/new dependency
lines, a blank line, `[dev-dependencies]`, and `schemars.workspace = true`; GitHub omits the following
`serde_json.workspace = true` context line. The prior validator therefore raised
`private conformance diff patch is truncated` even though `_parse_patch_hunks()` found complete counts.

The apply slice added an exact regression fixture/test and removed only the over-specific
`serde_json.workspace = true` required-context check. Hunk declared/actual counts, API metadata
counts, exact four dependency-key/path/version replacements, synchronized-version matching, private
package identity, and all other fail-closed validation remain enforced.

Local focused and relevant Cargo/npm/OCI/workflow/package/compile/whitespace checks passed after the
fix. This is an apply handoff, not a verification result: hosted run `31886141725` remains failure
evidence, no hosted replay success is claimed, and fresh `sdd-verify` is the next gate before
independent QA or any separately authorized protected hosted rehearsal. No hosted or publication
write occurred.

**Change**: `codegauge-distribution`

## Apply handoff — Phase 9 private conformance dependency-pin exception — 2026-08-15

The approved local implementation is now present, but this section is an apply handoff and is not a
replacement for a fresh `sdd-verify` report. The previous hosted PR `#59` evidence remains a failure:
it synchronized the five public runtime Cargo/npm surfaces to `0.2.0` with zero Stage-A release/tag
calls, then `cargo metadata --locked` failed on stale private conformance pins. A new hosted run is
required before that evidence can be considered corrected.

### Local implementation evidence

- The Java `codegauge-root` carrier owns exactly the four private TOML JSONPaths; no Cargo-workspace
  discovery plugin or conformance Release Please candidate/linked component was reintroduced.
- The exact installed Release Please `17.6.0` fake-SCM harness now records 32 effective paths, one
  root-carrier conformance manifest update whose content changes only four dependency versions, six
  npm optional pin rewrites, one synchronized PR, and zero release/tag calls.
- Carrier tests accept complete private patch metadata only for those four replacements and reject
  package identity/version/publish, dependency path, formatting/comment, truncated/missing patch,
  changelog, and other private-path mutations. A synchronized copied tree passes `cargo metadata
  --locked` while preserving conformance version `0.1.0` and `publish = false`.
- Focused carrier/provenance/distribution/static/runtime tests, Python compileall and package checks,
  locked Cargo metadata/tests/check/fmt/Clippy, npm typecheck/tests and seven pack dry-runs, OCI
  regression layers, actionlint, ShellCheck, Dockerfile check, and `git diff --check` passed locally.

### Handoff status

- Technical verification is **pending fresh `sdd-verify`** for this corrected boundary; no local result
  here claims hosted or operator acceptance.
- Hosted Stage-A rerun, merged-main carrier/tag delivery, publication, attestation, native target
  evidence, failure injection, and rollback remain unrun or prohibited.
- No hosted writes occurred in this apply phase: no GitHub API mutation, workflow dispatch, repository
  variable change, tag, label, release, upload, attestation, registry publication, credential use,
  merge, push, or commit.

## Superseding hosted finding — 2026-08-15

Hosted PR `#59` invalidates the prior exclusion-only private-member conclusion. Stage A did
synchronize the five public runtime Cargo/npm surfaces to `0.2.0` and made no release/tag calls,
but merged-tree `cargo metadata --locked` failed because the four conformance path dependencies
remained at `^0.1.0`. The corrected design permits only a root-carrier update of those four
dependency `.version` fields and requires a content-aware Stage-B allowlist. The exception is now
implemented locally by the Phase 9 apply slice but remains unhosted-verified; the prior local
`PASS WITH WARNINGS` section below is historical for this boundary, not acceptance of the correction.

## Prior local executor verification — 2026-08-15 (superseded for private pin boundary)

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
| Exact Release Please runtime | **PASS for prior exclusion-only boundary**: installed `17.6.0` fake SCM produced one synchronized PR, six optional pin rewrites to `0.2.0`, zero release calls, zero tag calls, and no private conformance candidate; the new hosted evidence requires a root-carrier pin update |
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
| REL-4 | Private conformance remains non-release/non-linked while four root-carrier pins align | Hosted PR `#59` failure; Phase 9 exception is not implemented | ❌ BLOCKED |
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

## Authoritative Phase 9 verification — 2026-08-15

### Scope and safety boundary

- Change: `codegauge-distribution`; branch: `fix/release-carrier-skip-unmatched`.
- Read the proposal, all five delta specs, design, tasks, state, apply progress, QA handoff, current
  implementation diff, and exact `release-please@17.6.0` source before judging the change.
- No commit, push, merge, repository-variable change, tag, label, release, upload, publication,
  attestation, credential injection, or hosted write was performed.
- `strict_tdd: true` is configured and the Cargo runner exists, but the installed
  `strict-tdd-verify.md` module is absent; dirty-worktree commit ordering is not independently
  provable.

### Completeness

| Metric | Result |
|---|---:|
| Task checkboxes | 35 |
| Complete | 29 |
| Incomplete | 6 (`4.2`, `4.3`, `7.4`, `8.4`, `9.6`, `9.7`) |
| Technical verdict | **FAIL** |

Tasks `4.2`, `7.4`, `8.4`, and `9.7` are hosted rehearsals; `4.3` is downstream acceptance QA.
Task `9.6` was executed but remains unchecked because the corrected synchronized-tree boundary
does not pass all local contracts.

### Build, tests, and coverage evidence

| Command/check | Result |
|---|---|
| Exact Release Please runtime | **PASS**: installed `17.6.0` fake SCM produced one synchronized PR, 32 effective paths, one private manifest update, six optional pin rewrites, `releaseCalls=0`, and `tagCalls=0` |
| Stage-A private update content | **PASS**: exactly four dependency-version line replacements; private package/name/publish and private lock version stayed unchanged; no private changelog or extra private path appeared |
| Stage-B carrier positives/negatives | **PASS** for exact private patch, private package/publish/name/path/key/feature/comment/format/truncated/missing-patch, unapproved npm/changelog, missing-root, malformed-SemVer, idempotency/conflict, and ordinary-main correlation cases |
| Current-tree Python/provenance/distribution/OCI checks | **PASS** |
| Current-tree locked Cargo metadata/tests/check/fmt/Clippy | **PASS**: metadata, 31 workspace tests, check, fmt, and `-D warnings` Clippy |
| Synchronized fixture `cargo metadata --locked` | **PASS**: public runtime packages `0.2.0`; conformance package `0.1.0` |
| Synchronized fixture `cargo test --workspace --locked` | **FAIL**: conformance golden test compares runtime tool version `0.2.0` with `tests/golden/valid-methods.json` value `0.1.0` |
| Cargo package checks | **PASS** using the workflow's exact local dependency patch configuration for all five public crates |
| npm typecheck/tests and seven pack dry-runs | **PASS**: 6 wrapper tests; seven package dry-runs |
| Action/workflow/ShellCheck/Dockerfile/diff checks | **PASS**: `actionlint`, `shellcheck`, Dockerfile `buildx --check`, and `git diff --check` |
| Generated-file mutation probe | **FAIL**: Stage-B accepted a content-mutated approved `tests/golden/valid-methods.json` entry by filename alone |
| Coverage | ➖ Not configured; `openspec/config.yaml` declares coverage unavailable |

The direct generated-file probe returned `generated-file mutation: ACCEPTED`. The synchronized-tree
failure was reproduced from the same Phase 9 fixture construction used by the carrier tests and failed
`golden_order_summary_digest_and_numbers_are_stable_except_timestamp` in `codegauge-conformance`.
The initial unpatched `cargo package` loop was an invocation failure against unpublished local crates;
the workflow-equivalent patched package commands passed and are the authoritative package evidence.

### Requested contract matrix

| Contract/scenario | Covering evidence | Result |
|---|---|---|
| Exact v17.6.0 effective Stage-A set is 32 paths | Runtime harness applies `mergeUpdates` and missing-file filtering, then asserts the exact path set | ✅ LOCAL |
| Private manifest contains exactly four dependency-version edits | Runtime updater line-pair assertion and carrier patch fixture | ✅ LOCAL |
| No private package-version/changelog/unrelated edits | Runtime private-line assertion and private-path negative fixtures | ✅ LOCAL |
| Five public Cargo versions, root Cargo metadata, npm versions/pins, and Cargo.lock converge | Runtime updater assertions and synchronized metadata probe | ✅ LOCAL for metadata/versions; ⚠️ synchronized workspace test exposes a root generated-contract defect |
| One synchronized PR and zero Stage-A release/tag calls | Read-only fake-SCM counters | ✅ LOCAL |
| Stage-B receives file status/count/patch metadata | Workflow `jq` projection plus static assertion and positive private patch | ✅ LOCAL |
| Private package/version/publish/name and unrelated private mutations fail closed | Content-aware private patch negatives | ✅ LOCAL |
| Unapproved npm, missing root, malformed SemVer, and ordinary correlation cases fail closed | Carrier runtime/static fixtures | ✅ LOCAL |
| Generated-diff mutation is rejected | Direct approved generated-file mutation probe | ❌ FAILING |
| Virtual root and conformance remain non-publishable/non-linked | Exact runtime/config/distribution/Cargo metadata checks | ✅ LOCAL |
| Canonical tag is Stage-B-only; Stage A makes no release/tag calls | Fake-SCM counters plus workflow/static topology | ✅ LOCAL |
| Dry-run guards and ordinary-main zero-match no-op | Runtime/static carrier suites and local mode/record probes | ✅ LOCAL; hosted execution unrun |
| Corrected synchronized tree passes the complete quality gate | Metadata passed; synchronized workspace test failed | ❌ FAILING |

### Correctness

| Requirement/contract | Status | Evidence |
|---|---|---|
| Exact four-field private root-carrier exception | ✅ | v17.6.0 updater and patch/content fixtures |
| Private package remains `0.1.0`, `publish = false`, lock/private, and unlinked | ✅ | Runtime harness, manifest checks, and metadata |
| Public Cargo/npm/lock synchronization and one PR/no Stage-A calls | ✅ | Exact fake-SCM output and updater assertions |
| Content-aware private Stage-B boundary | ✅ | Complete patch required; all tested private mutation negatives fail closed |
| Stage-B approved generated-file content boundary | ❌ | `tests/golden/valid-methods.json` content mutation was accepted by filename allowlist |
| Full corrected merged-tree quality gate | ❌ | Synchronized fixture conformance golden still expects `0.1.0` while runtime is `0.2.0` |
| Virtual root/conformance publication boundaries | ✅ | Root Java carrier/no package identity; conformance private and absent from candidate/linked sets |
| Canonical tag ownership and zero Stage-A release/tag calls | ✅ | Workflow conditions, static tests, and fake-SCM counters |
| Dry-run/live and ordinary-main no-op guards | ✅ local | Mode/record probes and matched-only workflow gates; hosted execution unrun |

### Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Java root carrier owns exactly four private dependency selectors | ✅ | Config and exact updater output match the design |
| Private conformance stays outside candidate/linked/release/tag graphs | ✅ | Runtime/config/distribution checks pass |
| Stage-B validates private content, not only filename | ✅ | Private path is content-aware and fails closed for tested mutations |
| Stage A has one PR and no release/tag; Stage B owns canonical tag | ✅ local | Fake-SCM counters and workflow/static topology; hosted event remains unrun |
| Corrected merged tree reaches the complete quality gate | ❌ | Conformance golden/version mismatch fails workspace tests |

### Issues found

#### CRITICAL

1. **Approved generated-file mutations are accepted.** `validate_stage_a_diff()` applies content
   validation only to `crates/codegauge-conformance/Cargo.toml`; an entry for the approved generated
   file `tests/golden/valid-methods.json` with a `0.1.0` → `9.9.9` patch was accepted. This violates
   the requested generated-diff mutation boundary.
2. **The synchronized effective tree fails workspace tests.** After applying the exact Phase 9
   public/private version updates, `cargo metadata --locked` passes, but the conformance golden test
   fails because the runtime reports `0.2.0` while the checked-in expected tool version remains
   `0.1.0`. The root generic extra-file updater cannot change that unmarked file, so the corrected
   Stage-A tree is not quality-gate compliant.

#### WARNING

1. Hosted Stage-A/merged-main carrier/tag rehearsal, publication, attestation, rollback/failure
   injection, and native non-host target evidence remain unavailable or prohibited. These are not the
   cause of the FAIL verdict.
2. The configured strict-TDD verifier module is absent and the intentionally dirty worktree prevents
   independent commit-order proof.

#### SUGGESTION

1. Add a source-faithful synchronized-tree test that applies all effective updates before running the
   complete locked workspace suite, and add content validation for every generated/root carrier file
   whose mutation is not intentionally permitted.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---------|---------|---------|----------|--------|
| Exact v17.6.0 fake-SCM yields 32 paths, four private edits, one PR, zero release/tag calls | ✅ runtime harness | ✅ updater/counter assertions | SUGGESTION | Confirmed locally |
| Private package/changelog/unrelated mutations fail closed | ✅ carrier negatives | ✅ source/config boundary | SUGGESTION | Confirmed locally |
| Approved generated-file content mutation is accepted | ✅ direct carrier probe | ✅ filename-only allowlist path | CRITICAL | Confirmed failure |
| Synchronized effective tree fails conformance golden/version test | ✅ temporary fixture cargo test | ✅ root generic updater has no version marker | CRITICAL | Confirmed failure |
| Virtual root/conformance remain non-publishable and canonical tag is Stage-B-only | ✅ runtime metadata | ✅ static workflow/config checks | SUGGESTION | Confirmed locally |
| Dry-run and ordinary-main no-op guards | ✅ runtime probes | ✅ static/matched-only gates | SUGGESTION | Confirmed locally; hosted unrun |
| Hosted rerun/publication/acceptance | ✅ policy boundary | ❌ not executed or authorized | WARNING | External gate remains |

### Final verdict

**FAIL** — the exact Phase 9 fake-SCM, private content boundary, version synchronization, no-write
Stage-A counters, publication boundaries, and no-op guards pass locally, but two local contracts fail:
an approved generated-file mutation is accepted and the synchronized effective tree fails the locked
workspace test. Hosted rerun remains unrun, but it is not the sole blocker. No fix or external write was
performed. Hand off to **`sdd-apply`** for remediation, then rerun **`sdd-verify`** before
**`sdd-qa`**.

## Apply remediation handoff — 2026-08-15

The two CRITICAL local findings above were remediated by the assigned `sdd-apply` slice. This section
is an implementation handoff, not a fresh verification verdict and does not replace the failed
verification evidence above.

### Remediation evidence

- `release-please-config.json` now uses the Release Please 17.6.0 typed JSON updater for
  `/tests/golden/valid-methods.json` at `$.tool.version`. README has exactly four intended
  `x-release-please-version` markers and `crates/codegauge-model/tests/contracts.rs` has exactly two;
  the unrelated CLI fixture remains unmarked.
- The exact v17.6.0 read-only fake-SCM harness passes with the exact 32-path effective set, six npm
  optional pin rewrites, one synchronized PR, four private dependency pin edits, and zero Stage-A
  release/tag calls. The synchronized copied tree now updates the golden tool version and passes
  `cargo test --workspace --locked` while retaining conformance version `0.1.0`/`publish = false`.
- Stage-B now requires complete status/count/patch metadata and validates typed JSON/TOML/npm files,
  annotated generic lines, twelve generated changelog additions, and the four private pins. Focused
  mutations for wrong versions, arbitrary content, unapproved annotations, filename-only entries,
  duplicate paths, and missing/truncated patches fail closed.
- Focused carrier/static/provenance/distribution/runtime suites, compileall/package generation,
  locked Cargo metadata/tests/check/fmt/Clippy, five dirty-allowed local Cargo package checks, npm
  typecheck/tests/seven pack dry-runs, OCI layers, actionlint, ShellCheck, Dockerfile check, and
  `git diff --check` pass locally.

### Handoff status

- Fresh `sdd-verify` MUST rerun the full spec/design/task matrix and independently confirm both
  remediated boundaries. `sdd-qa` remains the acceptance owner and MUST NOT infer hosted acceptance
  from this apply evidence.
- Hosted Stage-A merge, ordinary-main/no-op and manual/variable carrier rehearsals, canonical tag
  delivery, publication, attestation, native target evidence, failure injection, rollback, and
  credentials remain unrun or prohibited.
- No hosted writes occurred during remediation: no GitHub API mutation, workflow dispatch, repository
  variable change, tag, label, release, upload, attestation, registry publication, credential use,
  merge, push, or commit.

## Historical Release Please 17.6.0 source inspection (continued)

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

## Fresh sdd-verify — generated-version/updater boundary — 2026-08-15

This is the authoritative verification section for the current dirty checkout on
`fix/release-carrier-skip-unmatched`. All earlier `FAIL` and apply-handoff sections are retained as
history. Verification stayed within the requested technical/no-write boundary and does not claim
operator or user acceptance.

### Scope and safety boundary

- **Change/mode:** `codegauge-distribution` / OpenSpec.
- **Checkout:** `/Users/acosta/Dev/agent-swarm/codegauge`, branch
  `fix/release-carrier-skip-unmatched`, intentionally dirty.
- **Release under test:** Release Please package `17.6.0`; synchronized runtime version `0.2.0`.
- **Strict TDD:** `strict_tdd: true` is configured; the requested `strict-tdd-verify.md` module is
  absent from the installed skill directory, so commit-order proof cannot be independently added.
- **Safety:** no commit, push, merge, repository-variable change, tag, label, release, upload,
  publication, attestation, credential injection, or hosted write was performed.

### Completeness

Excluding retained historical handoff checkboxes, the active task checklist contains 39
implementation/verification entries: 33 complete and 6 incomplete. The remaining entries are
external/downstream gates only: `4.2`, `4.3`, `7.4`, `8.4`, `9.7`, and `9.11`. Phase-9 local
verification task `9.6` is now complete.

| Metric | Result |
|---|---:|
| Active task checkboxes | 39 |
| Complete | 33 |
| Incomplete | 6; hosted rehearsal or independent QA |
| Local CRITICAL findings | 0 |
| Technical verdict | **PASS WITH WARNINGS** |

### Exact v17.6.0 effective changeset

`npx --yes release-please@17.6.0 --version` returned `17.6.0`. The package-level Manifest,
NodeWorkspace, linked-versions, merge, and updater chain ran against a read-only fake SCM. Its
effective result was:

```text
releaseVersion=0.2.0
effectivePathCount=32
privateDependencyUpdates=1 (exactly four dependency-version edits)
synchronizedPullRequests=1
releaseCalls=0
tagCalls=0
```

The harness applied the exact `mergeUpdates` and missing-file/create-if-missing filtering boundary,
not just the raw updater proposal list. The sorted effective path set was exactly:

```text
.release-please-manifest.json
Cargo.lock
Cargo.toml
README.md
crates/codegauge-application/CHANGELOG.md
crates/codegauge-application/Cargo.toml
crates/codegauge-cli/CHANGELOG.md
crates/codegauge-cli/Cargo.toml
crates/codegauge-cli/tests/cli.rs
crates/codegauge-conformance/Cargo.toml
crates/codegauge-core/CHANGELOG.md
crates/codegauge-core/Cargo.toml
crates/codegauge-model/CHANGELOG.md
crates/codegauge-model/Cargo.toml
crates/codegauge-model/tests/contracts.rs
crates/codegauge-provider-jacoco/CHANGELOG.md
crates/codegauge-provider-jacoco/Cargo.toml
npm/codegauge/CHANGELOG.md
npm/codegauge/package.json
npm/packages/codegauge-darwin-arm64/CHANGELOG.md
npm/packages/codegauge-darwin-arm64/package.json
npm/packages/codegauge-darwin-x64/CHANGELOG.md
npm/packages/codegauge-darwin-x64/package.json
npm/packages/codegauge-linux-arm64-gnu/CHANGELOG.md
npm/packages/codegauge-linux-arm64-gnu/package.json
npm/packages/codegauge-linux-x64-gnu/CHANGELOG.md
npm/packages/codegauge-linux-x64-gnu/package.json
npm/packages/codegauge-win32-arm64-msvc/CHANGELOG.md
npm/packages/codegauge-win32-arm64-msvc/package.json
npm/packages/codegauge-win32-x64-msvc/CHANGELOG.md
npm/packages/codegauge-win32-x64-msvc/package.json
tests/golden/valid-methods.json
```

The set contains the public runtime manifests/lock metadata, root carrier files, twelve generated
changelogs, seven npm manifests, and the one narrowly permitted private manifest. It contains no
private changelog, virtual-root package, or unapproved path.

### Generated-version/updater and synchronized-tree evidence

| Contract | Evidence | Result |
|---|---|---|
| Typed golden updater | Root config uses `type=json`, `/tests/golden/valid-methods.json`, `$.tool.version`; exact updater output is `0.2.0` and changes no other JSON value | ✅ PASS |
| README generic updater | Exactly four `x-release-please-version` markers; updater changes only those four intended lines to `0.2.0` | ✅ PASS |
| Model contract generic updater | Exactly two `x-release-please-version` markers; updater changes only those two tool-version lines | ✅ PASS |
| CLI contract fixture | No release-version marker and no generated mutation | ✅ PASS |
| Public runtime graph | Five Cargo package manifests, root workspace metadata, `Cargo.lock`, release manifest, npm wrapper, and six platform package versions converge to `0.2.0` in the fixture | ✅ PASS |
| npm optional pins | All six `optionalDependencies` are rewritten to `0.2.0` with one wrapper update | ✅ PASS |
| Private conformance pins | Exactly four TOML dependency `.version` selectors update to `0.2.0`; package version remains `0.1.0`, `publish = false`, identity/lock/changelog remain private | ✅ PASS |
| Synchronized workspace | Copied effective tree has golden `$.tool.version=0.2.0` and passes `cargo test --workspace --locked` | ✅ PASS |

The checked-in base fixture correctly remains at `0.1.0`; the release-version changes occur in the
effective Stage-A update and synchronized copied tree. `git diff --unified=0` shows only the six
intended README/contract marker additions; unrelated semver text is unchanged.

### Build, test, and coverage evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_please_runtime_tests.py` | **PASS**; exact `17.6.0`, 32 paths, four private edits, six npm rewrites, one PR, zero release/tag calls |
| `python3 tests/release_carrier_tests.py` | **PASS**; synchronized fixture, exact-one/multiple/malformed/no-match, content mutations, SemVer, idempotency, and conflicts |
| `python3 tests/release_carrier_static_tests.py` | **PASS**; event correlation, complete patch metadata, permissions, full-SHA, concurrency, and mutation gates |
| `python3 tests/release_provenance_tests.py` | **PASS** |
| `python3 tests/distribution_checks.py` | **PASS** |
| `python3 tests/bootstrap_checks.py`, `python3 tests/readme_checks.py` | **PASS** |
| `python3 -m compileall -q scripts tests` and npm package generation check | **PASS** |
| Synchronized copied-tree `cargo test --workspace --locked` | **PASS**; golden `0.2.0`, conformance package `0.1.0`, `publish=false` |
| Current-tree `cargo metadata --locked` | **PASS** |
| Current-tree `cargo test --workspace --locked` | **PASS**; 31 tests, 0 failed, 0 skipped |
| `cargo check --workspace --locked` | **PASS** |
| `cargo fmt --all -- --check` | **PASS** |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | **PASS** |
| Five runtime Cargo package checks with workflow-equivalent local dependency patches | **PASS**; no publication |
| npm wrapper typecheck/tests | **PASS**; 6 tests |
| Wrapper plus six platform `npm pack --dry-run` checks | **PASS**; 7 packages |
| OCI regression layers | **PASS**; primary, static, evidence, and failure suites |
| `actionlint .github/workflows/*.yml` | **PASS** |
| `shellcheck scripts/build_oci_release.sh` | **PASS** |
| `docker buildx build --check --progress=plain .` | **PASS**; no warnings |
| `git diff --check` | **PASS** |
| Exact carrier mode/no-match workflow probe | **PASS**; manual/push dry-run/live, invalid fail-closed, and no-match record without diff fetch |
| Coverage | **UNAVAILABLE**; no coverage tool or threshold is configured |

An unpatched local `cargo package` loop was also attempted and stopped at the expected unpublished
local-crate lookup. The workflow-equivalent `--config patch.crates-io...` package commands above are
the authoritative package check and passed for all five public crates.

### Stage-B content compliance matrix

| Mutation/flow | Covering runtime evidence | Result |
|---|---|---|
| Legitimate typed golden update | Exact JSON updater and copied-tree test | ✅ PASS |
| Legitimate annotated README/contracts update | Exact marker-count/updater assertions | ✅ PASS |
| Legitimate Cargo/TOML/npm version updates | Content-aware patch fixtures and exact runtime updater | ✅ PASS |
| Legitimate generated changelog addition | Twelve-path allowlist plus positive changelog fixture | ✅ PASS |
| Legitimate private four-field patch | Complete patch/count/context validation and exact updater | ✅ PASS |
| Wrong version in golden/README/contracts/generated content | Mutation fixtures fail with `ProvenanceError` | ✅ PASS |
| Arbitrary generated-file content | Generated-file mutation fixture fails closed | ✅ PASS |
| Unannotated or unapproved marker | Annotation fixtures fail closed; CLI generic file is no-op | ✅ PASS |
| Malformed generated changelog | Invalid/status/format fixture fails closed | ✅ PASS |
| Filename-only or missing patch metadata | Complete status/count/patch checks fail closed | ✅ PASS |
| Duplicate, truncated, or incomplete patch | Duplicate/count/context fixtures fail closed | ✅ PASS |
| Private package version/publish/name/path/key/feature/comment drift | Private four-pin negative matrix fails closed | ✅ PASS |

### Spec compliance matrix

`LOCAL` means a covering executable check passed. `PARTIAL` means the local/static boundary passed but
the hosted, immutable-release, publication, native-target, or failure-injection portion was not run.
No current local scenario is failing.

| Spec area/scenario | Evidence | Result |
|---|---|---|
| CI pinned toolchain/lock, baseline quality gate, effective-tree gate | Cargo metadata/test/check/fmt/Clippy, Python checks, synchronized fixture | ✅ LOCAL |
| CI immutable action references and least privilege | Static carrier/distribution suites plus actionlint | ✅ LOCAL / ⚠️ hosted runtime unrun |
| CI injected lint/preflight failure behavior | Gate topology and `-D warnings` are intact; no failure injection allowed | ⚠️ PARTIAL |
| Cargo approved graph and source fallback | Five patched package checks, locked workspace tests, CLI version/profiles | ✅ LOCAL / ⚠️ registry unrun |
| Cargo immutable revision and publication order | Workflow/static topology only; no canonical hosted release exists | ⚠️ PARTIAL |
| Cargo private stale-pin failure and corrected exception | Historical PR `#59` failure plus corrected four-pin synchronized fixture | ✅ LOCAL boundary / ⚠️ hosted rerun |
| Cargo RFC-0001 compatibility | 31 locked workspace tests and conformance suite | ✅ LOCAL |
| Cargo incomplete package failure | Positive package checks; no destructive package-file injection | ⚠️ PARTIAL |
| npm identity, target selection, missing/unsupported target, passthrough | npm typecheck/tests and seven pack dry-runs | ✅ LOCAL |
| npm checksum/publication ordering | Local validators/static gates; no registry publication | ✅ LOCAL / ⚠️ hosted publication unrun |
| OCI identity, architecture rejection, runtime metadata, non-root/digest checks | Four OCI suites and Dockerfile check | ✅ LOCAL / ⚠️ registry publication unrun |
| OCI failed-architecture stop and final manifest | Fail-stop static topology; no hosted failure injection | ⚠️ PARTIAL |
| Release provenance/version mismatch and root carrier survival | Exact `17.6.0` fake-SCM, 32-path effective set, provenance negatives | ✅ LOCAL |
| Release private candidate/linked/release boundary | Private manifest is not candidate/linked; exact four-pin root exception; zero Stage-A calls | ✅ LOCAL |
| Release linked versions and six optional pins | Exact NodeWorkspace/linked updater runtime | ✅ LOCAL |
| Release typed/annotated/generated/private content boundary | Stage-B content matrix above | ✅ LOCAL |
| Release no-match correlation | Exact workflow probe and classifier/CLI runtime tests | ✅ LOCAL / ⚠️ hosted event unrun |
| Release exact-one, multiple, malformed correlation | Carrier runtime/static tests | ✅ LOCAL |
| Release dry-run/live/idempotency/conflict behavior | Exact workflow mode probe plus tag planner tests | ✅ LOCAL / ⚠️ hosted event unrun |
| Release canonical tag-only downstream ownership | Workflow topology/static tests; no tag event delivery | ✅ LOCAL / ⚠️ hosted event unrun |
| Archives, checksums, gated publication, credential, rollback | Existing local validators/static checks; writes and failure injection prohibited | ⚠️ PARTIAL |

### Correctness

| Requirement/contract | Status | Evidence |
|---|---|---|
| Exact v17.6.0 effective set is 32 paths | ✅ | Runtime harness applies effective filtering and asserts the full sorted set |
| Golden updates only `$.tool.version` | ✅ | Typed updater deep comparison plus synchronized fixture |
| README/contracts change only intended annotated lines | ✅ | Four/two marker counts, updater line-pair assertions, current diff inspection |
| Public versions, root metadata, Cargo.lock, six npm pins converge | ✅ | Exact runtime harness and synchronized fixture |
| Private conformance changes only four dependency versions | ✅ | Updater pairs and Stage-B complete patch validator |
| Private package remains `0.1.0`, `publish=false`, non-linked/non-release | ✅ | Runtime updater, metadata, config, and lock assertions |
| Synchronized effective tree passes locked workspace tests | ✅ | Direct copied-tree execution |
| Stage-B rejects content mutations before mutation | ✅ | Wrong/arbitrary/unannotated/malformed/filename-only/truncated negatives |
| One PR and zero Stage-A release/tag calls | ✅ | Fake-SCM counters |
| Dry-run/live/no-match behavior | ✅ local | Exact workflow mode/no-match probe and static/matched-only gates |
| Hosted carrier/tag/publication acceptance | ⚠️ | Not executed or authorized; hand off to `sdd-qa` |

### Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Component-tagged Stage A plus trusted post-merge carrier | ✅ | Exact runtime and workflow/static checks preserve the two-stage split |
| Java root metadata carrier survives v17.6.0 filtering | ✅ | Fake-SCM runs the exact package chain and records root updates |
| Exactly five public Cargo candidates; conformance not a candidate/linked component | ✅ | Config/runtime/distribution checks |
| Root typed/annotated updater ownership | ✅ | JSONPath and exact marker contracts match config and updater behavior |
| Four-field private root-carrier exception | ✅ | Only approved dependency selectors are accepted |
| Stage-B content-aware fail-closed validation | ✅ | Complete metadata/content checks and mutation matrix |
| Stage A no release/tag; Stage B canonical tag ownership | ✅ local | Counters and static topology; hosted delivery unrun |
| Reversible manual/variable dry-run | ✅ local | Exact mode probe and mutation guards; hosted rehearsal unrun |

### Issues found

#### CRITICAL

None.

#### WARNING

1. The protected hosted rerun remains unexecuted: actual Release Please merge, ordinary-main no-match
   event, manual/variable carrier rehearsal, canonical tag delivery, and hosted downstream execution
   were not available or authorized. This is the sole remaining implementation/acceptance boundary;
   no local defect remains.
2. Independent `sdd-qa` remains required for acceptance scenarios involving hosted provenance,
   publication/attestation, native non-host targets, failure injection, and rollback. This report does
   not upgrade technical evidence into operator acceptance.
3. Strict-TDD commit ordering cannot be independently proven from the intentionally dirty worktree,
   and the configured strict verifier module is absent; this is an evidence/tooling limitation, not
   an observed implementation failure.

#### SUGGESTION

1. Keep the exact effective-path and mode probes in the checked-in regression surface when the hosted
   rerun is authorized, so the local boundary remains auditable without credentials.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---------|---------|----------|----------|--------|
| Exact `17.6.0` effective set is 32 paths with four private edits | ✅ runtime harness output | ✅ updater/path assertions | SUGGESTION | Confirmed locally |
| Golden typed updater and README/contracts intended occurrences | ✅ updater deep/line checks | ✅ config/diff/count checks | SUGGESTION | Confirmed locally |
| Six npm optional pins, one PR, zero Stage-A release/tag calls | ✅ fake-SCM counters | ✅ runtime/static boundary | SUGGESTION | Confirmed locally |
| Private package identity/version/publish and unrelated mutations | ✅ runtime updater | ✅ Stage-B negative matrix | SUGGESTION | Confirmed locally |
| Synchronized effective tree passes `cargo test --workspace --locked` | ✅ copied fixture execution | ✅ conformance golden/version assertions | SUGGESTION | Confirmed locally |
| Stage-B rejects wrong/arbitrary/unannotated/malformed/filename-only mutations | ✅ content matrix runtime probe | ✅ validator/source inspection | SUGGESTION | Confirmed locally |
| Dry-run/live/no-match behavior | ✅ exact workflow shell probe | ✅ classifier/static matched-only gates | SUGGESTION | Confirmed locally; hosted unrun |
| Hosted rerun, publication, and acceptance | ✅ no-write policy boundary | ❌ not executed or authorized | WARNING | External gate remains |

### Final verdict

**PASS WITH WARNINGS** — every requested local contract and quality check passed, including the exact
Release Please `17.6.0` 32-path effective changeset, synchronized golden/contracts/docs fixture,
private four-pin exception, locked workspace test, content-aware Stage-B mutation boundary, and
dry-run/live/no-match behavior. No local defect remains. The only remaining blocker is protected
hosted/acceptance evidence; hand off explicitly to **`sdd-qa`**. No hosted success, publication, or
operator acceptance is claimed.

## Apply handoff — hosted GitHub PR patch parser defect — 2026-08-15

This newest section records the apply correction and does not replace a fresh `sdd-verify` verdict.

### Hosted finding and fix

- Hosted run `#31878496886` reached validation for the real merged Release Please PR `#59` and failed
  with `RELEASE PROVENANCE: FAIL: .release-please-manifest.json diff has missing or unexpected file
  context`.
- GitHub `GET /pulls/59/files` returned a valid hunk-only `patch` beginning `@@ -1,15 +1,15 @@` and
  containing no `diff --git`, `---`, or `+++` headers. `_patch_change_lines()` incorrectly required
  complete local unified-diff headers and rejected the valid API entry.
- The parser now accepts exactly a complete single-file unified diff or a filename-bound GitHub
  PR-files hunk-only patch. It validates hunk bodies/counts, API additions/deletions/changes counts,
  status-specific headers, path identity when headers exist, and rejects missing, malformed,
  truncated, or unexpected multi-file sections. The private four-pin validator uses parsed hunk
  context for both forms.

### Local handoff evidence

- **RED:** the new API-shaped manifest fixture failed before the fix with the hosted missing-context
  error.
- **GREEN/REFACTOR:** carrier/static/provenance/runtime/distribution, bootstrap/README, OCI,
  compileall/package generation, locked Cargo metadata/tests/check/fmt/Clippy, five Cargo package
  checks, npm typecheck/tests/seven pack dry-runs, actionlint, ShellCheck, Dockerfile, and whitespace
  checks passed locally.
- The exact 32-path Stage-A changeset, private four-pin exception, generated-file content validation,
  no-match carrier no-op, dry-run/live gates, and no-publication contract remain preserved.
- No tag, GitHub Release, Cargo/npm/GHCR publication, upload, attestation, workflow dispatch,
  repository-variable change, credential use, merge, push, or hosted write occurred. Hosted run
  `#31878496886` found the bug, and this fix is **not yet hosted-verified**.

### Next gate

Fresh `sdd-verify` must validate this updated patch-form boundary, followed by independent `sdd-qa`
and a separately authorized protected hosted rerun. This apply handoff makes no operator or product
acceptance claim.

## Authoritative fresh sdd-verify — GitHub PR-files hunk-only parser — 2026-08-15

This is the authoritative technical verification section for the current dirty checkout. Earlier
sections remain audit history. Verification was local and read-only; it does not claim hosted,
operator, or product acceptance.

### Identity, scope, and safety

| Field | Value |
|---|---|
| Change | `codegauge-distribution` |
| Mode | OpenSpec |
| Checkout | `/Users/acosta/Dev/agent-swarm/codegauge` |
| Release Please | Exact installed `17.6.0` |
| Synchronized release version | `0.2.0` |
| Strict TDD | Configured true; verifier module is absent, and dirty-worktree commit ordering is not independently provable |
| Safety boundary | No commit, push, merge, variable, tag, label, release, upload, publication, attestation, credential, dispatch, or hosted write |

### Completeness

The active numbered task list contains 43 entries: 36 checked and 7 still open. Open entries are
`4.2`, `4.3`, `7.4`, `8.4`, `9.7`, `9.11`, and `10.4`; they are protected hosted rehearsals,
independent QA, or composite handoffs, not local implementation defects.

| Metric | Result |
|---|---:|
| Active numbered task entries | 43 |
| Complete | 36 |
| Incomplete | 7; hosted/downstream gates |
| Local CRITICAL findings | 0 |
| Technical verdict | **PASS WITH WARNINGS** |

### Exact Release Please 17.6.0 evidence

`python3 tests/release_please_runtime_tests.py` executed the package-level Manifest, NodeWorkspace,
linked-versions, merge, and updater chain against a read-only fake SCM. It passed with:

```text
releaseVersion=0.2.0
effectivePathCount=32
privateDependencyUpdates=1 (exactly four dependency-version edits)
synchronizedPullRequests=1
releaseCalls=0
tagCalls=0
```

The exact sorted effective path set was:

```text
.release-please-manifest.json
Cargo.lock
Cargo.toml
README.md
crates/codegauge-application/CHANGELOG.md
crates/codegauge-application/Cargo.toml
crates/codegauge-cli/CHANGELOG.md
crates/codegauge-cli/Cargo.toml
crates/codegauge-cli/tests/cli.rs
crates/codegauge-conformance/Cargo.toml
crates/codegauge-core/CHANGELOG.md
crates/codegauge-core/Cargo.toml
crates/codegauge-model/CHANGELOG.md
crates/codegauge-model/Cargo.toml
crates/codegauge-model/tests/contracts.rs
crates/codegauge-provider-jacoco/CHANGELOG.md
crates/codegauge-provider-jacoco/Cargo.toml
npm/codegauge/CHANGELOG.md
npm/codegauge/package.json
npm/packages/codegauge-darwin-arm64/CHANGELOG.md
npm/packages/codegauge-darwin-arm64/package.json
npm/packages/codegauge-darwin-x64/CHANGELOG.md
npm/packages/codegauge-darwin-x64/package.json
npm/packages/codegauge-linux-arm64-gnu/CHANGELOG.md
npm/packages/codegauge-linux-arm64-gnu/package.json
npm/packages/codegauge-linux-x64-gnu/CHANGELOG.md
npm/packages/codegauge-linux-x64-gnu/package.json
npm/packages/codegauge-win32-arm64-msvc/CHANGELOG.md
npm/packages/codegauge-win32-arm64-msvc/package.json
npm/packages/codegauge-win32-x64-msvc/CHANGELOG.md
npm/packages/codegauge-win32-x64-msvc/package.json
tests/golden/valid-methods.json
```

The private manifest is not a Release Please candidate or linked component. Its updater changes
only the four dependency `.version` fields; package version `0.1.0`, `publish = false`, identity,
lock entry, changelog exclusion, and release/tag exclusion remain intact. The six npm optional
dependencies all rewrite to `0.2.0`.

### Hunk-only and unified-diff parser evidence

The real `.release-please-manifest.json` fixture was shaped like a GitHub `GET /pulls/{number}/files`
entry: validated `filename`, `status`, `additions`, `deletions`, `changes`, and a patch beginning
`@@ -1,15 +1,15 @@` with no `diff --git`, `---`, or `+++` headers. It passed the complete manifest
content validator. The same real manifest also passed as a complete single-file unified diff.

Read-only generated matrices passed both patch forms for all 31 content-bearing Stage-A entries:
the 6 root/content carriers, 5 runtime Cargo manifests, 7 npm manifests, 12 generated changelogs,
and the private conformance manifest. The 32nd effective Release Please path is the intentionally
unmarked `crates/codegauge-cli/tests/cli.rs` fixture; it has no release-version marker and receives
no content mutation, so it is correctly absent from the changed-file patch matrix.

| Parser contract | Runtime evidence | Result |
|---|---|---|
| Hunk-only real release manifest | `_patch_change_lines()` plus `validate_stage_a_diff()` | ✅ PASS |
| Full unified release manifest | Same validator with matching file headers | ✅ PASS |
| Hunk-only all content-bearing entries | 31-entry generated matrix | ✅ PASS |
| Full unified all content-bearing entries | 31-entry generated matrix | ✅ PASS |
| Multi-hunk patch parsing | Two complete hunk fixture | ✅ PASS |
| Missing status/count/patch metadata | 9-case parser negative matrix and carrier fixtures | ✅ FAIL-CLOSED |
| Inconsistent additions/deletions/changes | Parser negative and carrier fixtures | ✅ FAIL-CLOSED |
| Truncated or malformed hunk/body | Parser negative and carrier fixtures | ✅ FAIL-CLOSED |
| Unexpected second file section | Hunk-only and full-diff negative fixtures | ✅ FAIL-CLOSED |
| Status/header/path identity | Added/modified and mismatched-header checks | ✅ FAIL-CLOSED |

### Stage-B content and behavior matrix

| Requirement/scenario | Covering executable evidence | Result |
|---|---|---|
| Generated-file wrong version/arbitrary content rejected | Golden/changelog mutation fixtures | ✅ LOCAL |
| Private package version/publish/name/path/key/feature/comment mutations rejected | Private four-pin negative matrix | ✅ LOCAL |
| Unapproved npm/changelog/private paths rejected | Exact allowlists and negative paths | ✅ LOCAL |
| Missing root carrier files rejected | Each root carrier deleted in copied-tree tests | ✅ LOCAL |
| Missing/filename-only patch rejected | Complete metadata/content requirement | ✅ LOCAL |
| Malformed SemVer rejected before tag planning | Leading-zero, malformed, prerelease/build cases | ✅ LOCAL |
| Tag conflicts and existing-release conflicts rejected | Tag planner and release-slot fixtures | ✅ LOCAL |
| Golden uses `$.tool.version` only | Exact Release Please typed updater and copied tree | ✅ LOCAL |
| README/contracts update only 4/2 annotated lines | Marker-count and line-pair assertions | ✅ LOCAL |
| Synchronized tree runs complete workspace tests | Copied effective tree; golden `0.2.0`, conformance `0.1.0`/`publish=false` | ✅ LOCAL |
| Ordinary main no-match | Classifier returns `status=skipped`, reason `no-matching-release-please-pr`; workflow gates before diff fetch | ✅ LOCAL |
| Manual/push dry-run/live mode | Exact mode matrix; invalid values fail closed | ✅ LOCAL |
| Stage A no release/tag writes | Fake-SCM counters | ✅ LOCAL |

### Build, test, and coverage evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_carrier_tests.py` | **PASS** |
| `python3 tests/release_carrier_static_tests.py` | **PASS** |
| `python3 tests/release_provenance_tests.py` | **PASS** |
| `python3 tests/release_please_runtime_tests.py` | **PASS**; exact 17.6.0, 32 paths, four private edits, six npm pins, one PR, zero release/tag calls |
| `python3 tests/distribution_checks.py` | **PASS** |
| `python3 tests/bootstrap_checks.py` and `python3 tests/readme_checks.py` | **PASS** |
| `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` | **PASS** |
| `cargo +1.97.1 metadata --locked --format-version 1` | **PASS** |
| `cargo +1.97.1 test --workspace --locked` | **PASS**; 31 passed, 0 failed, 0 skipped |
| `cargo +1.97.1 check --workspace --locked` | **PASS** |
| `cargo +1.97.1 fmt --all -- --check` | **PASS** |
| `cargo +1.97.1 clippy --workspace --all-targets --locked -- -D warnings` | **PASS** |
| Five workflow-equivalent locked `cargo package` checks with local dependency patches | **PASS**; no publication |
| npm wrapper typecheck and tests | **PASS**; 6 tests passed |
| Wrapper plus six platform `npm pack --dry-run` checks | **PASS**; 7 packages |
| OCI primary/static/evidence/failure suites | **PASS** |
| `actionlint .github/workflows/*.yml` | **PASS** |
| `shellcheck scripts/build_oci_release.sh` | **PASS** |
| `docker buildx build --check --progress=plain .` | **PASS**; no warnings |
| `git diff --check` | **PASS** |
| Coverage | **UNAVAILABLE**; no tool or threshold configured |

### Specification compliance matrix

`LOCAL` means a covering runtime test or executable validator passed. `PARTIAL` means local/static
evidence passed but hosted execution, publication, native-target evidence, or failure injection was
not run or was prohibited. No local scenario is failing.

| Spec area | Evidence | Result |
|---|---|---|
| CI pinned toolchain/lock and complete quality gate | Locked Cargo metadata/tests/check/fmt/Clippy plus Python checks | ✅ LOCAL |
| CI immutable actions and least privilege | Distribution/carrier static suites plus actionlint | ✅ LOCAL / ⚠️ hosted runtime unrun |
| Cargo private stale-pin failure and four-pin exception | Historical PR `#59` failure plus corrected synchronized fixture | ✅ LOCAL / ⚠️ hosted rerun |
| Cargo RFC-0001 compatibility | 31 locked workspace tests and conformance suite | ✅ LOCAL |
| Cargo package integrity/publication order | Five local package checks and workflow topology | ✅ LOCAL / ⚠️ registry unrun |
| npm identity, six target packages, resolution, passthrough | npm tests, generator, and seven pack dry-runs | ✅ LOCAL |
| OCI identity, architecture rejection, metadata, non-root/digest checks | Four OCI suites and Dockerfile check | ✅ LOCAL / ⚠️ registry unrun |
| Exact 32-path Stage-A graph and zero Stage-A writes | Exact fake-SCM runtime result | ✅ LOCAL |
| Typed/annotated/TOML/npm/generated/private Stage-B boundary | Positive and mutation matrices | ✅ LOCAL |
| Hunk-only GitHub PR-files patch form | Real manifest plus 31-entry hunk-only matrix | ✅ LOCAL |
| Ordinary-main zero-match correlation | Classifier/CLI/static matched-only gates | ✅ LOCAL / ⚠️ hosted event unrun |
| Dry-run/live/idempotency/conflict behavior | Mode probe, workflow guards, and tag planner | ✅ LOCAL / ⚠️ hosted event unrun |
| Canonical tag-only downstream ownership | Workflow topology/static checks | ✅ LOCAL / ⚠️ tag delivery unrun |
| Archives/checksums/publication/attestation/rollback | Existing local validators/static checks | ⚠️ PARTIAL; external writes prohibited |

### Correctness

| Contract | Status | Evidence |
|---|---|---|
| GitHub hunk-only manifest patch is accepted without file headers | ✅ | Real API-shaped fixture and full carrier validation |
| Full unified diffs remain accepted | ✅ | Full 31-entry matrix and existing carrier fixtures |
| Patch metadata/hunk counts are independently strict | ✅ | Parser checks declared counts, body counts, and API totals |
| Exact four private pins only | ✅ | Runtime updater pairs and content-aware private validator |
| Exact 32 effective paths, six npm pins, one PR, zero release/tag calls | ✅ | Read-only v17.6.0 fake-SCM harness |
| Generated/root/candidate mutations fail closed | ✅ | Content validator matrix |
| Synchronized workspace tests remain green | ✅ | Copied effective tree plus current workspace run |
| Ordinary no-match and dry-run/live gates remain intact | ✅ local | Classifier, static gates, and exact shell mode matrix |
| Hosted PR/carrier/tag/publication acceptance | ⚠️ | Not executed or authorized; downstream QA/hosted rerun |

### Design coherence

| Design decision | Result | Evidence |
|---|---|---|
| Component-tagged Stage A plus trusted post-merge carrier | ✅ | Runtime counters and workflow/static checks |
| Java root metadata carrier and private four-pin exception | ✅ | Exact updater selectors and private content matrix |
| Stage-B validates content, not filenames | ✅ | Typed/annotated/TOML/npm/changelog/private fixtures |
| Parser accepts GitHub hunk-only and complete unified forms only | ✅ | 31-entry positive matrix and parser negatives |
| Stage A owns no release/tag; Stage B owns canonical tag | ✅ local | Fake-SCM zero calls and workflow topology |
| No-match is a successful non-mutating carrier outcome | ✅ local | Classifier output and matched-only workflow conditions |
| Dry-run is reversible and live default is preserved | ✅ local | Manual/push mode matrix and mutation guards |

### Issues

#### CRITICAL

None.

#### WARNING

1. The protected hosted rerun remains unexecuted: the real merged PR/carrier path, ordinary-main
   hosted no-match event, manual/variable rehearsal, canonical tag delivery, and downstream hosted
   execution are not observable under the no-write boundary. This is the sole remaining technical
   implementation/host boundary; no local defect remains.
2. Independent `sdd-qa` remains required for acceptance scenarios involving hosted provenance,
   publication/attestation, native non-host targets, failure injection, and rollback. This report
   does not convert local technical evidence into operator acceptance.
3. Strict-TDD commit ordering cannot be independently proven from the intentionally dirty worktree;
   the configured `strict-tdd-verify.md` module is absent. This is an evidence/tooling limitation,
   not an observed implementation failure.

#### SUGGESTION

1. Preserve the 31-entry hunk-only matrix and the exact mode/no-match probes as checked-in regression
   evidence when the separately authorized hosted rerun is performed.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---------|---------|---------|----------|--------|
| Real GitHub hunk-only manifest patch is accepted | ✅ carrier runtime | ✅ 31-entry hunk-only matrix | SUGGESTION | Confirmed locally |
| Full unified diffs remain accepted | ✅ existing fixtures | ✅ full 31-entry matrix | SUGGESTION | Confirmed locally |
| Missing/truncated/inconsistent/malformed/unexpected patches fail closed | ✅ parser negatives | ✅ content validators/static gates | SUGGESTION | Confirmed locally |
| Exact 32-path graph, four pins, six npm pins, one PR, zero release/tag calls | ✅ exact v17.6.0 runtime | ✅ harness counters/path assertions | SUGGESTION | Confirmed locally |
| Generated/private/unapproved/root/SemVer/conflict boundaries | ✅ mutation matrix | ✅ validator/source inspection | SUGGESTION | Confirmed locally |
| Synchronized workspace and quality/package checks | ✅ Cargo/npm/Python/OCI execution | ✅ workflow/package/diff diagnostics | SUGGESTION | Confirmed locally |
| Ordinary no-match and dry-run/live gates | ✅ classifier/mode probes | ✅ static matched-only conditions | SUGGESTION | Confirmed locally; hosted unrun |
| Hosted rerun, publication, and acceptance | ✅ no-write policy boundary | ❌ not executed or authorized | WARNING | External gate remains |

### Final verdict

**PASS WITH WARNINGS** — every requested local contract passed, including the real GitHub-shaped
hunk-only manifest patch, full unified diffs, strict fail-closed parser negatives, exact 32-path
Release Please 17.6.0 result, private four-pin exception, generated/root content validation,
synchronized workspace tests, no-match behavior, and dry-run/live gates. No local defect remains.
The remaining blocker is the separately authorized hosted rerun and downstream acceptance evidence;
hand off explicitly to **`sdd-qa`**. No hosted success, publication, or operator acceptance is
claimed.

## Apply handoff — dry-run-only historical carrier replay — 2026-08-15

This is an implementation handoff for a new narrow recovery/rehearsal capability; it is not a fresh
technical verification verdict. The assigned branch is `fix/release-carrier-replay`, based on
`origin/main` at `98fd3c60c68d3ec2373429bb07ffa7e32e69f053`. The authorized historical event is
`fcc91b4850480945ae484c3ebdba18f8a4e38270` (hosted PR `#59` merge). The workflow keeps source code
at the current selected `main` checkout and substitutes the historical SHA only as normalized
`EVENT_SHA` for read-only commit/PR correlation, carrier validation, and tag-plan identity.

### Implementation evidence

- `replay_sha` is optional and rejected unless the event is `workflow_dispatch` on
  `refs/heads/main` with `dry_run=true`; malformed/non-40-hex values and live/push replay attempts
  fail closed before PR-file collection.
- Runtime tests correlate the exact historical SHA to one Release Please PR, run the complete carrier
  validator against the current tree, assert the expected `v0.2.0` tag plan SHA, and prove the source
  tree bytes remain unchanged. Absent replay keeps current-main dispatch identity; push/live/malformed
  negatives fail closed.
- `carrier-record.json`, `carrier-plan.json`, and the workflow summary identify replay mode, source
  checkout SHA, replay event SHA, dry-run state, and every tag/label/release/upload/publication/
  attestation mutation as skipped, not-started, or not-dispatched. No credential value is placed in
  those records.
- Local carrier/provenance/runtime/distribution/bootstrap/README, compileall, locked Cargo, npm
  typecheck/tests/seven pack dry-runs, OCI, actionlint, ShellCheck, Dockerfile, and diff checks pass.

### Verification and acceptance boundary

- Fresh `sdd-verify` must rerun the updated replay/spec matrix and inspect the workflow expressions;
  this apply handoff does not claim technical verification or user/operator acceptance.
- The capability is explicitly dry-run-only recovery/rehearsal plumbing. It is not production replay,
  does not enable live historical tagging, and is not hosted-passed evidence.
- The protected hosted replay, PAT scope/masking/ref authorization, branch protection, downstream
  event delivery, tag/label/release/upload/publication/attestation behavior, and independent QA remain
  unverified or prohibited.
- No commit, push, merge, repository-variable change, tag, label, release, upload, publication,
  attestation, credential use, or hosted write occurred.

## Fresh sdd-verify — Phase 11 replay mode — 2026-08-15

**Change**: `codegauge-distribution`
**Mode**: OpenSpec
**Branch**: `fix/release-carrier-replay`
**Checkout**: `HEAD=98fd3c60c68d3ec2373429bb07ffa7e32e69f053` (`origin/main`) plus the intentional
14-file dirty Phase 11 implementation/artifact diff
**Scope**: technical conformance only; no hosted or operator acceptance claim
**Safety boundary**: no commit, push, merge, repository-variable change, tag, label, release,
upload, publication, attestation, credential exposure, or hosted write

### Completeness

| Scope | Result |
|---|---|
| Phase 11 implementation tasks | 11.1 and 11.2 pass locally; 11.3 is not technically accepted because the workflow mode step fails for absent replay; 11.4 hosted replay remains pending |
| Local quality and distribution checks | Executed; all listed command suites passed |
| Replay-specific runtime matrix | Valid replay and all rejection cases pass; ordinary no-replay modes expose one local workflow defect |
| Coverage | Unavailable; `openspec/config.yaml` has no coverage tool or threshold |
| Technical verdict | **FAIL** |

### Build, tests, and coverage evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_carrier_tests.py` | **PASS**; replay selection, current-tree byte preservation, exact-one/missing/ambiguous/malformed PR cases, patch/content/version/private mutations, tag planning, and synchronized copied-tree workspace tests |
| `python3 tests/release_carrier_static_tests.py` | **PASS**; current-main checkout, normalized `EVENT_SHA` uses, mutation guards, records, permissions, full-SHA actions, concurrency, and canonical Stage-B ownership |
| `python3 tests/release_provenance_tests.py`, `tests/distribution_checks.py`, `tests/bootstrap_checks.py`, `tests/readme_checks.py` | **PASS** |
| `python3 tests/release_please_runtime_tests.py` | **PASS** against exact `release-please@17.6.0`; 32 generated paths, four private pin edits, six npm optional pin rewrites, one PR, zero release/tag calls |
| Python compile/package checks | **PASS**: `python3 -m compileall -q scripts tests`; npm package generator check |
| Locked Cargo checks | **PASS**: metadata, 31 workspace tests, check, fmt, Clippy `-D warnings`, and five workflow-equivalent runtime package checks |
| npm checks | **PASS**: wrapper typecheck/tests (6 tests) and wrapper plus six platform `npm pack --dry-run` checks |
| OCI/workflow checks | **PASS**: all four OCI suites, `actionlint`, `shellcheck scripts/build_oci_release.sh`, and Dockerfile `buildx --check` |
| `git diff --check` | **PASS** |
| Exact workflow mode-step probe | **FAIL** for ordinary no-replay modes; see CRITICAL finding below |

The exact `Resolve carrier mode` shell body was extracted from the checked-in workflow and run with
temporary local outputs. A valid manual replay selected `EVENT_SHA=fcc91b4850480945ae484c3ebdba18f8a4e38270`
and recorded the current checkout SHA. Push/live/malformed/wrong-ref rejection cases failed closed as
expected. However, every no-replay case failed before producing outputs because `jq -er '.replay'`
returns exit status 1 for the valid JSON boolean `false` under `set -euo pipefail`.

### Spec compliance matrix

| Requirement/scenario | Covering evidence | Result |
|---|---|---|
| Authorized manual replay uses the historical event SHA | Resolver unit/CLI, exact mode-step probe, replay carrier fixture | ✅ LOCAL for the replay branch |
| Replay keeps current-main source checkout/tree | Checkout/static assertions, source/replay fields, copied-tree byte-preservation test | ✅ LOCAL |
| Normalized `EVENT_SHA` drives PR lookup, carrier validation, tag plan, and tag target | Static workflow assertions plus replay resolver/tag-plan tests | ✅ LOCAL wiring |
| Replay is rejected on push, live dispatch, malformed SHA, wrong ref/event | Resolver/CLI negative matrix and exact mode-step probe | ✅ LOCAL |
| Missing/ambiguous/malformed PR data fails closed before diff validation | Classifier, CLI, and carrier runtime negatives | ✅ LOCAL |
| Patch/content/version/private mutations fail closed | Full/hunk-only parser and Stage-B mutation matrix | ✅ LOCAL |
| Replay records are credential-free and all mutation paths are non-mutating | Static record/mutation guards and plan schema checks | ✅ LOCAL static/pure evidence |
| Missing replay preserves manual current-SHA behavior | Exact workflow mode-step probe | ❌ **FAIL**: mode step exits on `jq -er` false |
| Push variable true/live/unset behavior remains unchanged | Exact workflow mode-step probe | ❌ **FAIL**: all no-replay push modes exit before outputs |
| Exact 32-path Release Please 17.6.0 changeset, private four-pin exception, six npm pins, and zero Stage-A writes | Read-only fake-SCM runtime harness | ✅ LOCAL |
| Hunk-only/full patch validation and no-match behavior | Carrier runtime/static suites | ✅ LOCAL |
| One canonical tag remains Stage-B-only | Runtime zero-call counters and workflow topology/static gates | ✅ LOCAL |

### Correctness

| Requirement/contract | Status | Evidence |
|---|---|---|
| Valid replay identity is separated from source checkout identity | ✅ | `resolve_carrier_event_sha`, replay fixture, and exact shell probe |
| Historical PR lookup/validation/tag-plan identity uses normalized `EVENT_SHA` | ✅ | Workflow source inspection/static test and replay tag-plan SHA assertion |
| Replay cannot enter tag/label mutation | ✅ | Live conditions require both `dry_run=false` and `replay=false`; static guard passed |
| Existing Stage-B exact content/private/version/idempotency/conflict gates remain green | ✅ | Focused carrier/provenance/runtime suites |
| Ordinary current-SHA dispatch and push dry-run/live modes | ❌ | Checked-in mode shell exits on valid `false` replay output before writing `GITHUB_OUTPUT` |

### Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Current-main checkout with historical SHA only as read-only event identity | ✅ | Checkout remains `github.sha`; resolver emits separate source/event values |
| Replay is manual and dry-run-only | ✅ | Resolver rejects push/live/non-main/malformed replay inputs |
| Same exact correlation and Stage-B validation boundary | ✅ | Replay fixture invokes the normal carrier validator against the current tree |
| Mutation-free auditable records | ✅ | Record/plan fields and static no-publication guards are present |
| Absent replay preserves prior behavior | ❌ | Mode-step boolean extraction defect breaks the ordinary path |

### Issues found

#### CRITICAL

1. **Ordinary carrier mode resolution aborts when replay is absent.** In
   `.github/workflows/release-tag-carrier.yml:75`, `replay_mode="$(jq -er '.replay' <<<"$event_resolution")"`
   uses `jq --exit-status` on a boolean. The valid `false` value intentionally returns status 1;
   with `set -euo pipefail`, the step exits before writing `dry_run`, `mode`, `event_sha`, or
   `source_checkout_sha` outputs. This breaks manual dispatch without replay and all push variable
   modes, violating the ordinary current-SHA/live-dry-run contract. The valid replay branch (`true`)
   is not affected. No fix was made during verification.

#### WARNING

1. The separately authorized hosted replay remains unexecuted under the no-write boundary; no hosted
   PR lookup, plan record, tag/label delivery, or downstream workflow acceptance is claimed.

#### SUGGESTION

1. The configured strict-TDD verifier module is absent from the installed skill directory and the
   intentionally dirty worktree prevents independent commit-order proof; this is an evidence/tooling
   limitation, not the cause of the failure.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Valid replay selects historical `EVENT_SHA` while retaining current source SHA | ✅ resolver/runtime | ✅ exact workflow mode probe/static wiring | SUGGESTION | Confirmed locally |
| Replay rejects push/live/malformed/wrong-context inputs | ✅ resolver/CLI | ✅ exact mode-step rejection cases | SUGGESTION | Confirmed locally |
| Exact Stage-B parser/private/content/version/mutation boundaries remain green | ✅ carrier runtime | ✅ provenance/static/runtime suites | SUGGESTION | Confirmed locally |
| Exact 32-path Release Please 17.6.0 graph, four private pins, six npm pins, zero Stage-A writes | ✅ fake-SCM runtime | ✅ path/counter assertions | SUGGESTION | Confirmed locally |
| Absent replay preserves manual and push behavior | ✅ source inspection identifies `jq -e` | ✅ extracted workflow runtime reproduces exit 1 | CRITICAL | Confirmed defect |
| Hosted replay and downstream acceptance | ✅ policy boundary | ❌ not executed or authorized | WARNING | External gate remains |

### Final verdict

**FAIL** — a local workflow defect remains in the ordinary no-replay mode path. The replay-specific
branch and all pure validation/distribution checks are green, but the implementation cannot preserve
normal manual current-SHA behavior or push dry-run/live modes until the boolean extraction is corrected.
Hand off to **`sdd-apply`** for the minimal test-first repair, then rerun `sdd-verify`; do not hand off
to `sdd-qa` as a passing technical phase. No hosted success, publication, or operator acceptance is
claimed.

## Apply remediation handoff — Phase 11 total replay schema and normal mode repair — 2026-08-15

This section records the follow-up implementation only; it is not a fresh `sdd-verify` verdict. The
assigned branch remains `fix/release-carrier-replay`, based on `origin/main`, with no hosted writes.

### Repair evidence

- Added `tests/release_carrier_mode_tests.py` before the production workflow repair. Its RED run exited
  1 on the normal push case because the checked-in mode step aborted while reading valid `replay=false`
  with `jq -er '.replay'`.
- Replaced that extraction with a safe jq default/type check: absent/null replay defaults to boolean
  `false`, valid false serializes to `false` with exit 0, and any present non-boolean fails closed.
- The same checked-in test now passes normal push, normal manual `dry_run=true`, normal manual
  `dry_run=false`, valid manual replay, and push/live/malformed replay rejection cases.
- Carrier records and summaries now emit a total boolean `replay` field. They always identify the
  current source checkout; replay mode additionally identifies the historical replay event SHA, while
  ordinary mode emits an explicit null/none replay SHA. The dry-run plan guard uses a safe default/type
  check rather than `jq -e` on a possibly false boolean.

### Local commands

The focused carrier/mode/static/provenance/runtime/distribution suites, Python compile/package checks,
locked Cargo metadata/tests/check/fmt/Clippy, npm typecheck/tests and seven pack dry-runs, all OCI
regressions, actionlint, carrier-mode ShellCheck, Dockerfile `buildx --check`, and `git diff --check`
all exited 0 after the repair. The five workflow-equivalent locked Cargo package checks also passed
with local dependency patches; the unpatched exploratory loop stopped at the expected unpublished
crate lookup. No tag, label, release, upload, publication, attestation, credential, repository-variable
change, hosted dispatch, merge, push, or commit was performed.

### Boundary

Fresh `sdd-verify` must rerun the Phase 11 spec matrix and inspect the exact workflow record/summary
schema before QA. The protected hosted replay and independent acceptance QA remain pending; this apply
handoff does not claim technical verification or hosted/operator success.

## Fresh sdd-verify — Phase 11 replay default repair — 2026-08-15

**Change**: `codegauge-distribution`
**Mode**: OpenSpec
**Branch**: `fix/release-carrier-replay`
**Scope**: Replay default repair plus full local regression of the Release Please 17.6.0, private
four-pin, Stage-B, Cargo, npm, OCI, and workflow contracts.
**Safety boundary**: No commit, push, merge, tag, label, release, upload, registry publication,
attestation, credential injection, repository-variable change, hosted dispatch, or other hosted write.

### Completeness

| Scope | Result |
|---|---|
| Phase 11 local implementation tasks 11.1–11.3a | Complete; focused mode/replay and carrier suites pass |
| Phase 11 hosted replay task 11.4 | Incomplete; explicitly not run under the no-write boundary |
| Prior local Release Please/conformance wrapper gate | **FAIL**; exact wrapper fixture rejects a no-op manifest replacement |
| Local distribution/quality gates | Pass except the failing wrapper command above |
| Coverage | Not configured; `openspec/config.yaml` declares coverage unavailable |

### Build, tests, and coverage evidence

| Command/check | Result |
|---|---|
| `npx --yes release-please@17.6.0 --version` | **PASS**: exact package reports `17.6.0` |
| `python3 tests/release_carrier_mode_tests.py` | **PASS**: normal push/manual dry-run/manual live no-replay defaults, valid replay, and replay negatives |
| `python3 tests/release_carrier_tests.py` | **PASS**: replay PR/tree/patch validation, source immutability, no-match, Stage-B, hunk-only/full patch, idempotency/conflicts |
| `python3 tests/release_carrier_static_tests.py` | **PASS**: normalized `EVENT_SHA`, current-main checkout, replay-false mutation guards, pins, permissions, concurrency |
| `python3 tests/release_provenance_tests.py` | **PASS** |
| `python3 tests/release_please_runtime_tests.py` | **FAIL**: exact Node harness passes, then wrapper rejects `release metadata contains an unexpected version replacement` |
| Exact Node `release-please@17.6.0` harness | **PASS**: one synchronized PR, 32 generated paths, four private pins, six npm rewrites, zero release/tag calls |
| `python3 tests/distribution_checks.py`, bootstrap, README | **PASS** |
| OCI regression layers (four commands) | **PASS** |
| Python compile/package-generation checks | **PASS** |
| `cargo metadata --locked --format-version 1` | **PASS** |
| `cargo test --workspace --locked` | **PASS**: 31 passed, 0 failed, 0 skipped |
| `cargo check --workspace --locked`, fmt, locked Clippy `-D warnings` | **PASS** |
| Five workflow-equivalent locked Cargo package checks with local patches | **PASS**; no publication |
| npm typecheck/tests and wrapper plus six platform `npm pack --dry-run` | **PASS**: 6 tests, 7 packs |
| `actionlint .github/workflows/*.yml`, carrier/OCI ShellCheck, Dockerfile `buildx --check` | **PASS** |
| `git diff --check` | **PASS** |

The failing Python wrapper command was rerun with its exit code captured as `1`. The exact failure is
deterministic: `tests/release_please_runtime_tests.py:102-104` reads the current
`.release-please-manifest.json` values (`0.2.0`) as the old side while constructing a required
`0.2.0` replacement; `_validate_release_manifest_patch()` correctly rejects that unchanged value.
This is a local test-fixture defect, not an unavailable hosted capability, and it prevents claiming the
full prior Release Please/conformance gate is green.

### Replay behavior matrix

| Scenario | Covering runtime evidence | Result |
|---|---|---|
| Normal push, no replay | Extracted checked-in mode step plus mode test; `replay=false`, current SHA, `live` | ✅ PASS |
| Normal manual dry-run, no replay | Extracted mode step plus mode test; `replay=false`, current SHA, `dry-run` | ✅ PASS |
| Normal manual live, no replay | Extracted mode step plus mode test; `replay=false`, current SHA, `live` | ✅ PASS |
| Valid replay | Resolver, carrier fixture, and tag-plan tests; historical SHA becomes `EVENT_SHA`, current source SHA remains separate | ✅ PASS |
| Replay validates PR/tree/patch and never mutates | Exact-one replay PR fixture, full carrier validation, four-pin patch, hunk/full patch tests, and source-byte comparison | ✅ PASS |
| Replay on push/live/malformed/wrong ref | Resolver/CLI and extracted workflow-mode negative tests | ✅ PASS; fail closed |
| Missing replay record/summary schema | Mode/record assertions; boolean false and replay SHA null/none boundary | ✅ PASS |
| Hosted replay/no-publication observation | Not run; task 11.4 is explicitly prohibited here | ⚠️ NOT TESTED |

### Specification compliance matrix

`PASS` below means a covering local runtime test or executable validator passed. `PARTIAL` means the
local implementation is intact but the scenario requires hosted execution, publication, native target
evidence, or failure injection. The Release Please wrapper row is `FAIL` because its test fixture exits
nonzero; this is independent of the passing exact Node harness.

| Spec area / scenarios | Evidence | Result |
|---|---|---|
| CI pinned toolchain, locked graph, tests, fmt, Clippy, Python checks | Cargo and Python commands above | ✅ PASS |
| CI least privilege/full-SHA/workflow topology | Static carrier/distribution tests and actionlint | ✅ PASS locally; hosted isolation untested |
| Private stale-pin failure and corrected four-pin exception | Private positive/negative Stage-B fixtures and synchronized-tree workspace test | ✅ PASS |
| Golden `$.tool.version`, README markers, model contracts, CLI no-op | Carrier content matrix and runtime/provenance suites | ✅ PASS |
| Hunk-only and complete unified patch parsing | Carrier runtime mutation suite | ✅ PASS |
| Stage-B exact paths/content/SemVer/idempotency/conflict | Carrier/provenance/static suites | ✅ PASS |
| Exact Release Please 17.6.0 plugin chain | Node harness passes; Python wrapper fixture fails as described | ❌ FAIL |
| Cargo source/package contracts | Locked workspace and five package checks | ✅ PASS locally |
| npm identity/resolution/passthrough/checksum checks | npm tests, generator, and seven dry-run packs | ✅ PASS locally |
| OCI identity/architecture/metadata/failure validators | Four OCI regression layers and Dockerfile check | ✅ PASS locally |
| Replay default/replay identity/no-mutation scenarios | Replay behavior matrix above | ✅ PASS locally |
| Hosted carrier/tag/release/publication/native-target acceptance | No hosted writes or authorized target | ⚠️ PARTIAL / downstream |

### Correctness

| Contract | Status | Evidence |
|---|---|---|
| Absent replay safely defaults to boolean `false` | ✅ | Extracted workflow mode test passes all normal modes |
| Normal push no-match/live behavior is preserved | ✅ locally | Classifier no-match tests plus live mode output; hosted event remains unrun |
| Replay accepts only manual dry-run lowercase 40-hex SHA | ✅ | Resolver/CLI and mode negative matrix |
| `EVENT_SHA` is used for historical lookup/validation/tag-plan identity | ✅ | Static use audit, resolver output, replay carrier/tag-plan assertions |
| Current-main checkout remains the source tree | ✅ | Checkout inspection and source/replay SHA separation |
| PR/tree/patch/private validation remains exact and fail closed | ✅ | Replay carrier fixture, four-pin, hunk/full, malformed and mutation negatives |
| Replay cannot mutate tag/label/release/upload/publication/attestation | ✅ locally | Replay-false live guards, plan status assertions, and no-write tests |
| Exact prior Release Please wrapper gate remains green | ❌ | Fixture no-op manifest replacement causes exit 1 |

### Design coherence

| Design decision | Followed? | Notes |
|---|---|---|
| Current-main checkout plus historical read-only `EVENT_SHA` | ✅ | Workflow checkout remains bound to `github.sha`; resolver separates source/event identity |
| Replay is manual and dry-run-only | ✅ | Resolver and workflow reject push/live/non-main/malformed replay values |
| Same exact correlation and Stage-B path | ✅ locally | Replay fixture enters the normal carrier validator and tag-plan path |
| Total credential-free record/summary schema | ✅ locally | Normal and replay mode tests verify boolean and SHA fields |
| Existing two-stage Release Please/private-pin architecture | ⚠️ | Exact Node chain passes, but the Python wrapper fixture blocks full technical acceptance |

### Issues found

#### CRITICAL

1. **Exact Release Please runtime wrapper fails its positive private-pin boundary.**
   `tests/release_please_runtime_tests.py` constructs `.release-please-manifest.json` patch lines from
   the current `0.2.0` manifest and also uses `0.2.0` as the synchronized target. The generated patch is
   therefore a no-op, and `validate_stage_a_diff()` correctly raises
   `ProvenanceError: release metadata contains an unexpected version replacement`. The exact Node
   `release-please@17.6.0` harness passes before this wrapper assertion, so the defect is in the checked-in
   verification fixture boundary. No fix was made in this verify phase.

#### WARNING

1. The separately authorized hosted replay (task 11.4), hosted PR/tag delivery, publication,
   attestation, native non-host evidence, rollback, and independent acceptance QA were not run under
   the explicit no-write boundary. They are not evidence of hosted success.
2. The worktree is intentionally dirty, so commit-order proof for strict TDD is unavailable; the
   configured `strict-tdd-verify.md` module is absent from the installed skill directory.

#### SUGGESTION

1. Repair the positive `release_please_runtime_tests.py` fixture to model an actual old-to-new manifest
   version replacement, rerun the exact wrapper and full matrix, then hand off to `sdd-qa`.
2. Remove the temporary replay input after the authorized no-publication rehearsal if normal live carrier
   operation is the only remaining use case.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Normal push/manual no-replay modes emit `replay=false` and preserve live/dry-run behavior | ✅ mode test | ✅ extracted workflow execution | SUGGESTION | Confirmed locally |
| Valid replay separates source SHA and `EVENT_SHA` | ✅ resolver/carrier runtime | ✅ static normalized-SHA audit | SUGGESTION | Confirmed locally |
| Replay validates PR/tree/patch and preserves source bytes | ✅ carrier fixture | ✅ Stage-B hunk/full/private mutation suite | SUGGESTION | Confirmed locally |
| Replay negatives fail closed before collection/mutation | ✅ resolver/CLI/mode runtime | ✅ workflow guards | SUGGESTION | Confirmed locally |
| Exact Node Release Please 17.6.0 chain has four pins, six npm rewrites, zero calls | ✅ harness | ✅ counter/path assertions | WARNING | Confirmed locally |
| Python Release Please/conformance wrapper positive boundary | ✅ captured exit 1 | ✅ validator traceback identifies no-op fixture | CRITICAL | Confirmed defect |
| Cargo/npm/OCI/workflow/local quality checks | ✅ executable suites | ✅ independent command reruns | SUGGESTION | Confirmed locally |
| Hosted replay and downstream acceptance | ✅ policy boundary | ❌ not executed or authorized | WARNING | Pending external gate |

### Final verdict

**FAIL** — the replay default repair itself is locally green and no replay-specific local defect remains,
but the exact prior Release Please/conformance wrapper check exits 1 on a stale no-op manifest fixture.
The hosted replay is not the sole remaining blocker. Do not hand off to `sdd-qa` as a passing technical
phase; hand off to `sdd-apply` to repair the fixture, then rerun verification.

## Apply handoff — deterministic Release Please wrapper fixture — 2026-08-15

This is an apply implementation handoff after the Phase 11 **FAIL** above; it is not a replacement
technical verification verdict. The assigned branch is `fix/release-carrier-replay`, using the
`feature-branch-chain` strategy from `origin/main`. No hosted or parent-repository state was changed.

### Repair evidence

- Added executable RED coverage in `tests/release_please_runtime_tests.py` for an explicit historical
  `0.1.0` → `0.2.0` manifest and npm wrapper fixture, the exact 13 manifest paths, and six optional
  dependency paths. The RED run failed because the old fixture emitted current `0.2.0` values as its
  deleted side.
- `stage_a_prefix()` now verifies that the checked-out manifest and npm wrapper already have the exact
  target path/value shape, but constructs all deleted lines from named `BASELINE_VERSION` constants and
  all added lines from `TARGET_VERSION` constants. It does not use current values as the historical side.
- The positive fixture passes `validate_stage_a_diff()`. Explicit no-op and wrong-version manifest
  mutations are rejected by the same validator, so the fixture cannot silently accept a real no-op.
- The exact Node `release-please@17.6.0` harness and all carrier boundaries remain unchanged: 32 paths,
  four private pins, six npm optional rewrites, one PR, zero release/tag calls, private mutation
  negatives, hunk/full patch parsing, replay/default modes, synchronized Cargo tests, and no-write
  mutation guards.

### Local apply evidence

- Focused wrapper and carrier/provenance/static/mode/distribution/bootstrap/README/OCI Python suites,
  Python compile/package checks, locked Cargo metadata/tests/check/fmt/Clippy, five local Cargo package
  verifications, npm typecheck/tests and seven pack dry-runs, actionlint, ShellCheck, Dockerfile check,
  and `git diff --check` all passed after the repair.
- No commit, push, merge, tag, label, release, upload, publication, attestation, credential,
  repository-variable change, hosted dispatch, or parent-repository mutation occurred.

### Handoff

Fresh `sdd-verify` must rerun the Phase 11 replay/spec matrix and replace the current **FAIL** verdict
only after independently confirming the focused wrapper. `sdd-qa` and hosted task 11.4 remain pending;
this handoff makes no hosted or operator acceptance claim.

## Final local SDD verification — Phase 11 replay and fixture repair — 2026-08-15

This is the authoritative technical verification section for the current dirty checkout. Earlier
verification and apply sections remain audit history. Verification was local and read-only; it does
not claim hosted, operator, or product acceptance.

### Identity and safety

| Field | Value |
|---|---|
| Change / mode | `codegauge-distribution` / OpenSpec |
| Branch / checkout | `fix/release-carrier-replay` / `HEAD=98fd3c60c68d3ec2373429bb07ffa7e32e69f053` plus intentional dirty diff |
| Release Please | Exact installed `17.6.0` |
| Fixture target | Historical `0.1.0 -> 0.2.0` for the Python Stage-B wrapper fixture |
| Strict TDD | `strict_tdd: true`; strict verifier module unavailable and dirty-worktree commit ordering not independently provable |
| Safety boundary | No commit, push, merge, variable, tag, label, release, upload, publication, attestation, credential, dispatch, or hosted write |

### Completeness

| Scope | Result |
|---|---|
| Phase 11 local tasks `11.1`–`11.3b` | **5/5 complete and locally verified** |
| Phase 11 hosted task `11.4` | **Pending**; protected hosted replay is intentionally not run |
| Local CRITICAL findings | **0** |
| Coverage | **Unavailable**; no tool or threshold is configured |
| Technical verdict | **PASS WITH WARNINGS** |

### Exact Release Please 17.6.0 evidence

`python3 tests/release_please_runtime_tests.py` executed the exact package-level Manifest,
NodeWorkspace, linked-versions, merge, and updater chain against a read-only fake SCM. It passed the
requested result boundary:

```text
packageVersion=17.6.0
effectivePathCount=32
privateDependencyUpdates=1 (exactly four dependency-version edits)
synchronizedPullRequests=1
releaseCalls=0
tagCalls=0
```

The six npm optional dependencies were rewritten by the exact updater, and the private package
identity/version/publish boundary remained intact. The current checked-in manifest is already
`0.2.0`, so this next-release Node harness run reports its calculated next release as `0.3.0`; the
separate Python wrapper fixture intentionally models the historical `0.1.0 -> 0.2.0` Stage-B change.

### Build, test, and coverage evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_please_runtime_tests.py` | **PASS**; deterministic target-shape guards, historical `0.1.0 -> 0.2.0` positive fixture, no-op/wrong-version rejection, exact Node `17.6.0` chain |
| `python3 tests/release_carrier_tests.py` | **PASS**; replay/source-byte preservation, no-match, exact-one/multiple/malformed PRs, hunk/full patches, content/private/generated/version/idempotency/conflict negatives, synchronized copied-tree workspace test |
| `python3 tests/release_carrier_mode_tests.py` | **PASS**; normal push/manual dry-run/manual live defaults, valid replay, push/live/malformed replay rejection, total boolean schema |
| `python3 tests/release_carrier_static_tests.py` | **PASS**; full-SHA actions, least privilege, current-main checkout, normalized `EVENT_SHA`, replay mutation guards, canonical Stage-B tag ownership |
| `python3 tests/release_provenance_tests.py` | **PASS** |
| `python3 tests/distribution_checks.py`, `tests/bootstrap_checks.py`, `tests/readme_checks.py` | **PASS** |
| `python3 tests/oci_distribution_tests.py` plus static/evidence/failure layers | **PASS** |
| `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` | **PASS** |
| `cargo +1.97.1 metadata --locked --format-version 1` | **PASS** |
| `cargo +1.97.1 test --workspace --locked` | **PASS**; 31 passed, 0 failed, 0 skipped |
| `cargo +1.97.1 check --workspace --locked` | **PASS** |
| `cargo +1.97.1 fmt --all -- --check` | **PASS** |
| `cargo +1.97.1 clippy --workspace --all-targets --locked -- -D warnings` | **PASS** |
| Five workflow-equivalent locked runtime `cargo package` checks with local dependency patches | **PASS**; no publication |
| npm wrapper typecheck/tests | **PASS**; 6 tests passed |
| Wrapper plus six platform `npm pack --dry-run` checks | **PASS**; 7 packages |
| `actionlint .github/workflows/*.yml` | **PASS** |
| `shellcheck scripts/build_oci_release.sh` and extracted carrier mode | **PASS** |
| `docker buildx build --check --progress=plain .` | **PASS**; no warnings |
| `git diff --check` | **PASS** |

### Specification compliance matrix

`LOCAL` means a covering runtime test or executable validator passed. `PARTIAL` means the local
boundary is green but hosted execution, publication, native-target evidence, or failure injection was
not run or was prohibited. No current local scenario is failing.

| Spec area / scenarios | Evidence | Result |
|---|---|---|
| CI pinned toolchain, lockfile, tests, fmt, Clippy, Python checks | Locked Cargo/Python command matrix | ✅ LOCAL |
| CI immutable actions and least privilege | Carrier/distribution static suites and actionlint | ✅ LOCAL / ⚠️ hosted isolation unrun |
| Cargo stale private pins and exact four-pin exception | Positive/negative private fixtures and synchronized-tree tests | ✅ LOCAL |
| Cargo RFC-0001/source compatibility | 31 locked workspace tests and conformance suite | ✅ LOCAL |
| Cargo package integrity/order and registry publication | Five package checks and workflow topology | ✅ LOCAL / ⚠️ registry unrun |
| npm identity, six targets, resolution, passthrough, checksum boundary | npm tests, generator, seven pack dry-runs, provenance checks | ✅ LOCAL |
| OCI identity, architecture, metadata, non-root/digest/failure validators | Four OCI layers and Dockerfile check | ✅ LOCAL / ⚠️ registry unrun |
| Exact 32-path Stage-A graph and zero Stage-A writes | Exact fake-SCM runtime counters/path assertions | ✅ LOCAL |
| Typed golden, annotated README/contracts, TOML/npm/generated/private content | Positive and mutation matrices | ✅ LOCAL |
| Hunk-only GitHub PR-files and full unified patch forms | Real manifest fixture and parser matrix | ✅ LOCAL |
| Ordinary-main zero-match correlation | Classifier/CLI/static matched-only gates | ✅ LOCAL / ⚠️ hosted event unrun |
| Manual/push dry-run/live and replay identity/no-mutation behavior | Exact shell mode matrix, resolver, carrier fixture, static guards | ✅ LOCAL / ⚠️ hosted replay unrun |
| Canonical tag is Stage-B-only | Stage-A zero-call counters and carrier/tag workflow topology | ✅ LOCAL / ⚠️ tag delivery unrun |
| Archive/checksum/publication/attestation/rollback acceptance | Existing local validators/static checks | ⚠️ PARTIAL; external writes prohibited |

### Correctness

| Requirement / contract | Status | Evidence |
|---|---|---|
| Exact Node `17.6.0` result: 32 paths, four private pins, six npm rewrites, one PR, zero calls | ✅ | Fake-SCM harness and wrapper assertions |
| Python fixture is historical `0.1.0 -> 0.2.0` and target-shape guarded | ✅ | `release_please_runtime_tests.py` executable tests |
| No-op and wrong-version replacements fail closed | ✅ | Wrapper mutation tests and Stage-B validator |
| Synchronized effective tree passes locked workspace tests | ✅ | Copied-tree `cargo test --workspace --locked`; golden `0.2.0`, conformance `0.1.0`/`publish=false` |
| Exact private four-field exception only | ✅ | Private updater pairs and content-aware mutation matrix |
| Replay uses historical `EVENT_SHA` while checkout/source remains current main | ✅ | Resolver, workflow static audit, replay carrier fixture |
| Replay rejects push/live/malformed/wrong-ref input | ✅ | Resolver/CLI and extracted workflow mode negatives |
| Replay cannot mutate tag/label/release/upload/publication/attestation | ✅ | Replay-false live conditions, dry-run plan statuses, source-byte comparison |
| No-match is successful and pre-diff/non-mutating | ✅ | Classifier/CLI and matched-only workflow gates |
| Canonical tag ownership remains Stage-B-only | ✅ local | Stage-A zero calls and carrier-only tag ref mutation |

### Design coherence

| Design decision | Result | Evidence |
|---|---|---|
| Component-tagged Stage A plus trusted post-merge carrier | ✅ | Exact runtime counters and workflow/static checks |
| Java root carrier with private four-pin exception | ✅ | Exact selectors, updater output, and private content matrix |
| Stage-B validates content, not filenames | ✅ | Typed/annotated/TOML/npm/changelog/private fixtures |
| Current-main checkout plus historical read-only event identity | ✅ | Checkout remains `github.sha`; only normalized `EVENT_SHA` drives historical uses |
| Replay is manual and dry-run-only | ✅ | Resolver and workflow mode rejection matrix |
| Mutation-free replay records are total and credential-free | ✅ | Normal/replay mode assertions and plan/record schema guards |
| Stage A owns no release/tag; Stage B owns canonical tag | ✅ local | Fake-SCM counters and workflow topology |

### Issues

#### CRITICAL

None.

#### WARNING

1. The separately authorized protected hosted replay (`tasks.md` task `11.4`) and its no-publication
   record inspection remain unrun under the explicit no-write boundary. This is the sole remaining
   blocker for the requested replay slice; no local implementation defect remains.
2. Independent `sdd-qa` still owns hosted/operator acceptance scenarios. No hosted provenance,
   publication, attestation, native non-host target, failure-injection, or rollback acceptance is
   claimed by this technical report.

#### SUGGESTION

1. Coverage remains unavailable because no coverage tool or threshold is configured. The strict-TDD
   verifier module is also unavailable, so commit-order proof cannot be reconstructed from this dirty
   worktree.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---------|---------|----------|----------|--------|
| Exact Node `17.6.0` graph has 32 paths, four private edits, six npm rewrites, one PR, zero calls | ✅ runtime harness | ✅ path/counter assertions | SUGGESTION | Confirmed locally |
| Python wrapper models `0.1.0 -> 0.2.0` and guards current target shape | ✅ executable fixture tests | ✅ source inspection | SUGGESTION | Confirmed locally |
| No-op/wrong-version, generated/private/content/version/patch mutations fail closed | ✅ mutation matrix | ✅ validator/static review | SUGGESTION | Confirmed locally |
| Synchronized workspace and all local Cargo/npm/OCI/package checks pass | ✅ command execution | ✅ copied-tree/runtime evidence | SUGGESTION | Confirmed locally |
| Current-main/replay SHA separation and replay mutation-free boundary | ✅ resolver/mode/carrier runtime | ✅ workflow static guards | SUGGESTION | Confirmed locally |
| Full-SHA, least privilege, and canonical Stage-B-only tag topology | ✅ static suite/actionlint | ✅ workflow inspection | SUGGESTION | Confirmed locally; hosted delivery unrun |
| Protected hosted replay and independent acceptance | ✅ no-write policy boundary | ❌ not executed or authorized | WARNING | Remaining external gate |

### Final verdict

**PASS WITH WARNINGS** — every requested local contract and quality check passed, including the exact
Release Please `17.6.0` metrics, deterministic `0.1.0 -> 0.2.0` wrapper fixture, synchronized workspace
tests, carrier/replay/patch/content/private/generated/version/no-match/dry-run/live behavior, and
workflow safety boundaries. No local defect remains. The only remaining blocker for this slice is the
separately authorized hosted replay and downstream acceptance evidence; hand off explicitly to
**`sdd-qa`**. No hosted success, publication, or operator acceptance is claimed.

## Authoritative fresh sdd-verify — Phase 12 private PR-files hunk context — 2026-08-15

This section supersedes the Phase 12 apply handoff at the start of this file and is authoritative for
the current checkout. Verification was local and read-only. It proves technical conformance only and
does not claim hosted, operator, or product acceptance.

### Identity, scope, and safety

| Field | Value |
|---|---|
| Change / mode | `codegauge-distribution` / OpenSpec |
| Checkout | `/Users/acosta/Dev/agent-swarm/codegauge` |
| Branch / HEAD | `fix/release-carrier-private-patch-context` / `cdd91baf9cbd0fb416ecfe67977310253d9b7534` plus the intentional dirty diff |
| Release Please | Exact installed `17.6.0` |
| Synchronized version | `0.2.0` |
| Toolchain | Rust/Cargo `1.97.1`, Python `3.14.7`, Node `24.19.0`, npm `11.17.0` |
| Strict TDD | Configured true; RED/GREEN/REFACTOR evidence is recorded, but the installed strict verifier module is absent and dirty-worktree commit ordering is not independently provable |
| Safety boundary | No commit, push, merge, variable, tag, label, release, upload, publication, attestation, credential, dispatch, or hosted write |

### Completeness

| Scope | Result |
|---|---|
| Phase 12 local tasks `12.1`–`12.4` | Complete and locally verified |
| Phase 12 protected hosted task `12.5` | Pending; intentionally not run |
| Local CRITICAL findings | 0 |
| Coverage | Unavailable; `openspec/config.yaml` declares no coverage tool or threshold |
| Technical verdict | **PASS WITH WARNINGS** |

### Specification compliance matrix

| Specification requirement/scenario | Covering executable evidence | Result |
|---|---|---|
| Hosted run `31886141725` records the valid PR `#59` failure | OpenSpec failure record plus exact old-validator replay; the omitted `serde_json.workspace = true` context caused `private conformance diff patch is truncated` | ✅ Failure preserved honestly |
| Exact PR `#59` API hunk-only fixture is accepted after the correction | `test_private_conformance_api_hunk_only_patch`; header `@@ -10,10 +10,10 @@ publish = false`, complete `10/10` hunk, `4/4/8` API counts, no `serde_json` context | ✅ LOCAL |
| Pre-fix behavior rejects that same valid fixture | Read-only execution of `HEAD:scripts/verify_release_provenance.py` against the exact fixture returned `private conformance diff patch is truncated` | ✅ Conceptual RED reproduced |
| Complete declared and actual hunk counts remain required | Parser positive plus declared-count, body-truncation, API-addition, API-deletion, and API-change-count negatives | ✅ LOCAL |
| Private exception changes exactly four approved dependency `.version` fields | Positive fixture and exact dependency-key set validation for application, core, model, and provider-jacoco | ✅ LOCAL |
| Old/new versions and synchronized target remain strict | Positive `0.1.0 -> 0.2.0` fixture plus old-equals-new and wrong-new-version negatives | ✅ LOCAL |
| Truncation and unapproved private mutations fail closed | Nine-case private boundary matrix plus existing package/publish/name/path/key/feature/comment/truncation tests | ✅ LOCAL |
| Exact Release Please 17.6.0 Stage-A graph remains intact | Read-only fake-SCM runtime: 32 paths, one private update with four edits, six npm pins, one PR, zero release/tag calls | ✅ LOCAL |
| Synchronized Cargo tree and private identity remain valid | Locked copied-tree workspace test and current Cargo metadata; conformance remains `0.1.0` and `publish = false` | ✅ LOCAL |
| Cargo, npm, OCI, workflow, shell, package, and whitespace gates | Fresh command matrix below | ✅ LOCAL |
| Protected hosted replay and acceptance | Not executed under the explicit no-write/no-secret boundary | ⚠️ PENDING; no hosted success claimed |

### Exact hunk regression evidence

The checked-in `private_conformance_api_hunk_only_patch()` fixture is filename-bound and contains no
`diff --git`, `---`, or `+++` headers. Its hunk declares ten old and ten new lines, its body supplies
those complete counts, and its API metadata declares four additions, four deletions, and eight changes.
The current validator accepted it. A read-only load of the pre-fix validator from `HEAD` rejected the
same entry because it required the context line GitHub omitted. A second executable matrix accepted the
positive and rejected nine focused negatives: declared hunk mismatch, actual truncation, additions
mismatch, deletions mismatch, changes mismatch, unapproved key, unapproved path, old version equal to
the target, and new-version drift.

The production diff is intentionally one-line narrow: `_validate_private_conformance_patch()` no
longer requires `serde_json.workspace = true`. Hunk parsing, declared/actual counts, API counts,
exact four dependency keys, dependency paths, valid old versions, synchronized new versions, private
package identity, and all other fail-closed boundaries remain enforced.

### Build, test, package, and static evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_carrier_tests.py` | **PASS** |
| `python3 tests/release_carrier_static_tests.py` | **PASS** |
| `python3 tests/release_carrier_mode_tests.py` | **PASS** |
| `python3 tests/release_provenance_tests.py` | **PASS** |
| `python3 tests/release_please_runtime_tests.py` | **PASS**; exact `17.6.0`, 32 paths, four private edits, six npm pins, one PR, zero release/tag calls |
| `python3 tests/distribution_checks.py` | **PASS** |
| `python3 tests/bootstrap_checks.py` and `python3 tests/readme_checks.py` | **PASS** |
| Four `tests/oci_distribution_*.py` regression layers | **PASS** |
| `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` | **PASS** |
| `cargo +1.97.1 metadata --locked --format-version 1` | **PASS**; private conformance `0.1.0`, non-publishable |
| `cargo +1.97.1 test --workspace --locked` | **PASS**; 31 passed, 0 failed, 0 skipped |
| `cargo +1.97.1 test -p codegauge-cli --test cli --locked` | **PASS**; 3 passed |
| `cargo +1.97.1 check --workspace --locked` | **PASS** |
| `cargo +1.97.1 fmt --all -- --check` | **PASS** |
| `cargo +1.97.1 clippy --workspace --all-targets --locked -- -D warnings` | **PASS** |
| Five workflow-equivalent locked `cargo package` checks with local dependency patches | **PASS**; no publication |
| CLI `version` / `profiles` contract | **PASS**; `codegauge 0.2.0` / `java-jacoco-v1` |
| npm typecheck and tests | **PASS**; 6 tests passed |
| Wrapper plus six platform `npm pack --dry-run` checks | **PASS**; 7 packages |
| `actionlint .github/workflows/*.yml` | **PASS** |
| `shellcheck scripts/build_oci_release.sh` | **PASS** |
| `docker buildx build --check --progress=plain .` | **PASS**; no warnings |
| `git diff --check` | **PASS** |

### Correctness

| Contract | Status | Evidence |
|---|---|---|
| Valid PR-files hunk-only patch passes without trailing optional context | ✅ | Exact PR `#59` fixture and current validator |
| Pre-fix false rejection is reproduced, not rewritten as hosted success | ✅ | Old validator execution and preserved run `31886141725` failure record |
| Hunk and API counts are independently strict | ✅ | Parser count checks plus focused negative matrix |
| Four private pins are the complete approved mutation set | ✅ | Exact key/path/version positive and mutation negatives |
| Private package remains version `0.1.0`, `publish = false`, and non-release | ✅ | Copied-tree metadata and private mutation tests |
| Stage-A 17.6.0 no-release/no-tag boundary remains intact | ✅ local | Fake-SCM counters and runtime assertions |
| Existing replay/no-match/dry-run/live and no-publication boundaries remain intact | ✅ local | Carrier mode/static/runtime suites and full local matrix |
| Hosted replay, tag delivery, publication, and acceptance | ⚠️ | Not executed or authorized; downstream QA/hosted task remains pending |

### Design coherence

| Design decision | Result | Evidence |
|---|---|---|
| Remove only the over-specific private trailing-context requirement | ✅ | Production diff removes exactly one required-context entry |
| Keep the root-carrier four-pin exception narrow | ✅ | Exact four selectors and content-aware private validator remain unchanged |
| Keep Stage A release/tag-free and Stage B canonical-tag-owned | ✅ local | Runtime zero-call counters and workflow/static checks |
| Keep hosted replay separate from local verification | ✅ | Run `31886141725` remains failure evidence; no replay was dispatched |

### Issues

#### CRITICAL

None.

#### WARNING

1. The separately authorized protected hosted replay/validation for the corrected PR `#59` boundary was
   not run. Hosted run `31886141725` remains a failure observation, not a passing replay, and no hosted
   tag, release, publication, or downstream acceptance is claimed.
2. Independent `sdd-qa` remains required for hosted/provider/native-target, publication, attestation,
   failure-injection, rollback, and operator-acceptance scenarios. This report is technical only.
3. Strict TDD is configured and apply-progress records RED/GREEN/REFACTOR, but the worktree is dirty and
   the installed `strict-tdd-verify.md` module is unavailable, so commit-order proof is not possible.

#### SUGGESTION

1. Retain the exact hunk-only fixture and focused negative matrix when the separately authorized hosted
   replay is performed; remove temporary replay plumbing afterward if it is no longer needed.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---------|---------|---------|----------|--------|
| Pre-fix validator rejects the exact PR `#59` hunk-only fixture | ✅ old source execution | ✅ exact fixture omits required context | SUGGESTION | Confirmed historical RED |
| Current validator accepts the exact hunk-only fixture | ✅ carrier runtime | ✅ direct positive count/key matrix | SUGGESTION | Confirmed locally |
| Declared/actual hunk and API counts fail closed | ✅ parser implementation | ✅ nine focused negatives | SUGGESTION | Confirmed locally |
| Exactly four approved private dependency mutations remain required | ✅ validator/source | ✅ positive plus mutation matrix | SUGGESTION | Confirmed locally |
| Exact Release Please 17.6.0 graph and zero Stage-A release/tag calls | ✅ fake-SCM runtime | ✅ path/counter assertions | SUGGESTION | Confirmed locally |
| Cargo/npm/OCI/workflow/package/whitespace checks | ✅ executable command matrix | ✅ static/package diagnostics | SUGGESTION | Confirmed locally |
| Hosted replay and independent acceptance | ✅ no-write policy boundary | ❌ not executed or authorized | WARNING | Remaining external gate |

### Final verdict

**PASS WITH WARNINGS** — the exact PR `#59` hunk-only regression reproduces the pre-fix rejection and
passes with the one-line correction; private counts, four-key/version/identity boundaries, truncation
and mutation negatives, the exact Release Please `17.6.0` runtime, and all requested local Cargo/npm/
OCI/workflow/shell/package/whitespace checks pass. Hosted run `31886141725` remains failure evidence;
no hosted replay success or acceptance is claimed. Hand off explicitly to **`sdd-qa`**.

## Authoritative fresh sdd-verify — Phase 13 second hosted replay regression — 2026-08-15

This section is authoritative for the current dirty checkout. It proves technical conformance only. The
hosted run named below is preserved as pre-fix failure evidence; no corrected hosted replay, publication,
operator acceptance, or product acceptance is claimed.

### Identity, scope, and safety

| Field | Value |
|---|---|
| Change / mode | `codegauge-distribution` / OpenSpec |
| Checkout | `/Users/acosta/Dev/agent-swarm/codegauge` |
| Branch / HEAD | `fix/release-carrier-private-patch-context` / `aa27efe0f6ce10707abd1c19f5b020a4db8dfa46` plus the intentional dirty diff |
| Implementation diff | `scripts/verify_release_provenance.py`, `tests/release_carrier_tests.py` |
| Release Please | Exact installed `17.6.0` |
| Synchronized version | `0.2.0` |
| Toolchain | Rust/Cargo `1.97.1`, Python `3.14.7`, Node `24.19.0`, npm `11.17.0` |
| Hosted evidence | Run `31888439750` is a pre-fix failure observation; the exact PR `#59` files API was read-only fetched |
| Safety boundary | No commit, push, merge, variable, tag, label, release, upload, publication, attestation, credential-bearing run, dispatch, or hosted write |

### Completeness

| Scope | Result |
|---|---|
| Phase 13 local tasks `13.1`–`13.4` | Complete and verified |
| Phase 13 protected hosted task `13.5` | Pending; intentionally not run |
| Existing protected hosted/acceptance tasks | Still pending under the no-write/no-secret boundary |
| Local CRITICAL findings | 0 |
| Coverage | Unavailable; `openspec/config.yaml` declares no coverage tool or threshold |
| Technical verdict | **PASS WITH WARNINGS** |

### Hosted regression and exact API evidence

The exact read-only `GET /repos/yacosta738/codegauge/pulls/59/files` response contains 31 file entries
and passes `validate_stage_a_diff(..., version="0.2.0")`. The saved safe metadata snapshot is
`openspec/changes/codegauge-distribution/qa-evidence/2026-08-15-replay/phase-13-verify-api-file-list.json`.
The `npm/codegauge/package.json` entry declares ten additions, eight deletions, and eighteen changes.
Its seven approved version pairs are the wrapper `version` plus six approved optional dependencies;
the remaining changes are exactly:

```text
-  "files": ["dist/index.js"],
+  "files": [
+    "dist/index.js"
+  ],
```

Read-only execution of the pre-fix validator from `HEAD` against that exact API list reproduced the
RED failure:

```text
npm/codegauge/package.json contains an unexpected number of package version edits
```

The current validator partitions approved version-key lines from formatting lines, accepts only that
exact base-package rewrite, and keeps platform-package formatting, altered base `files` content,
arbitrary base formatting, and unapproved base keys rejected. The focused fixture and command evidence
are summarized in `qa-evidence/2026-08-15-replay/phase-13-verify-summary.md`.

### Specification compliance matrix

`LOCAL` means a covering runtime test or executable validator passed. `PARTIAL` means local evidence is
green but hosted execution, publication, native-target, failure-injection, rollback, or acceptance
evidence was not run or was prohibited. No local scenario failed.

| Specification requirement/scenario | Covering executable evidence | Result |
|---|---|---|
| Real PR `#59` base npm hunk-only rewrite is accepted | Read-only 31-entry API list; base entry `10/8/18`; current `validate_stage_a_diff` | ✅ LOCAL |
| Pre-fix second regression remains recorded honestly | `HEAD` validator rejects the same API list on the base npm edit count | ✅ Failure preserved |
| Seven approved npm version pairs remain strict | `test_release_please_npm_base_api_hunk_only_patch` plus exact API validation | ✅ LOCAL |
| Exact base `files` compact-to-three-line rewrite is the only formatting allowance | Current validator source and positive fixture | ✅ LOCAL |
| Platform formatting and arbitrary base edits fail closed | Executable mutation probes for platform formatting, altered `files`, arbitrary formatting, and unapproved keys | ✅ LOCAL |
| Private conformance hunk-only omission of optional trailing context remains accepted | Existing PR `#59` private fixture and focused carrier suite | ✅ LOCAL |
| Carrier/parser count, truncation, path, private, replay, no-match, and mutation negatives remain strict | `release_carrier_tests.py`, static, mode, provenance suites | ✅ LOCAL |
| Exact Release Please `17.6.0` no-write runtime remains intact | Fake-SCM harness: 32 generated paths, four private pins, six npm rewrites, one PR, zero release/tag calls | ✅ LOCAL |
| Locked Cargo graph and workspace behavior remain valid | Metadata, 31 workspace tests, check, fmt, Clippy, five package checks | ✅ LOCAL |
| npm wrapper and seven package boundaries remain valid | Typecheck, six npm tests, seven `npm pack --dry-run` checks | ✅ LOCAL |
| OCI/workflow/shell/package/whitespace gates pass | Four OCI suites, actionlint, ShellCheck, Dockerfile check, diff check | ✅ LOCAL |
| Corrected hosted replay and downstream acceptance | Not executed under the explicit no-write/no-secret boundary | ⚠️ PENDING; no hosted success claimed |

### Build, test, package, and static evidence

| Command/check | Result |
|---|---|
| `python3 tests/release_carrier_tests.py` | **PASS**; new npm hunk fixture plus existing carrier/private/parser negatives |
| `python3 tests/release_carrier_static_tests.py` | **PASS** |
| `python3 tests/release_carrier_mode_tests.py` | **PASS** |
| `python3 tests/release_provenance_tests.py` | **PASS** |
| `python3 tests/release_please_runtime_tests.py` | **PASS**; exact `17.6.0`, 32 generated paths, four private edits, six npm pins, one PR, zero release/tag calls |
| `python3 tests/distribution_checks.py`, `tests/bootstrap_checks.py`, `tests/readme_checks.py` | **PASS** |
| Four `tests/oci_distribution_*.py` regression layers | **PASS** |
| `python3 -m compileall -q scripts tests` and `python3 scripts/generate_npm_packages.py --check` | **PASS** |
| `cargo +1.97.1 metadata --locked --format-version 1` | **PASS** |
| `cargo +1.97.1 test --workspace --locked` | **PASS**; 31 passed, 0 failed, 0 skipped |
| `cargo +1.97.1 check --workspace --locked` | **PASS** |
| `cargo +1.97.1 fmt --all -- --check` | **PASS** |
| `cargo +1.97.1 clippy --workspace --all-targets --locked -- -D warnings` | **PASS** |
| Five workflow-equivalent locked runtime `cargo package` checks with local dependency patches | **PASS**; no publication |
| npm typecheck/tests | **PASS**; six tests passed |
| Wrapper plus six platform `npm pack --dry-run` checks | **PASS**; seven packages |
| `actionlint .github/workflows/*.yml` | **PASS** |
| `shellcheck scripts/build_oci_release.sh` | **PASS** |
| `docker buildx build --check --progress=plain .` | **PASS**; no warnings |
| `git diff --check` | **PASS** |

### Correctness

| Contract | Status | Evidence |
|---|---|---|
| Exact real PR `#59` API list passes the current Stage-B validator | ✅ | 31-entry read-only API validation at version `0.2.0` |
| Hosted run `31888439750` remains pre-fix failure evidence | ✅ | Old validator rejection is reproduced locally; no success rewrite |
| Version edits are partitioned from formatting edits | ✅ | Current `_validate_npm_package_patch` implementation and positive hunk fixture |
| Base formatting allowance is exact and platform-scoped out | ✅ | Exact constants plus executable platform/arbitrary negative probes |
| Existing private/parser/carrier/replay/no-match boundaries remain intact | ✅ | Focused runtime/static/mode/provenance suites |
| Exact Release Please graph and zero Stage-A release/tag calls remain intact | ✅ local | Fake-SCM output and counters |
| Hosted replay, tag delivery, publication, and acceptance | ⚠️ | Not executed or authorized; downstream `sdd-qa` remains pending |

### Design coherence

| Design decision | Result | Evidence |
|---|---|---|
| Validate content rather than filenames | ✅ | Exact API list plus hunk/parser and mutation tests |
| Permit only the deterministic base npm `files` rewrite | ✅ | Three exact added lines and one exact deleted line |
| Keep platform package formatting fail-closed | ✅ | Platform mutation rejection |
| Preserve private four-pin and hunk-only boundaries | ✅ | Existing private fixture and negative matrix remain green |
| Keep hosted replay separate from local verification | ✅ | Run `31888439750` remains pre-fix failure evidence; no dispatch/replay occurred |

### Issues

#### CRITICAL

None.

#### WARNING

1. The separately authorized corrected hosted replay/validation for run `31888439750`'s boundary was not
   run. No hosted tag, release, publication, upload, attestation, or downstream acceptance is claimed.
2. Independent `sdd-qa` remains required for hosted/provider/native-target, publication, attestation,
   failure-injection, rollback, and operator-acceptance scenarios. This report is technical only.
3. Strict TDD is configured and the RED/GREEN/REFACTOR history is recorded, but the worktree is dirty
   and `strict-tdd-verify.md` is unavailable, so commit-order proof is not possible.

#### SUGGESTION

1. Retain the exact API metadata snapshot and focused negative probes when the protected replay is
   eventually authorized; remove temporary replay plumbing afterward if it is no longer needed.

### Verdict table

| Finding | Judge A | Judge B | Severity | Status |
|---|---|---|---|---|
| Pre-fix validator rejects the exact PR `#59` npm hunk-only entry | ✅ old-source execution | ✅ exact `10/8` API counts and seven version pairs | SUGGESTION | Confirmed historical RED |
| Current validator accepts the exact real PR `#59` API file list | ✅ read-only API execution | ✅ positive fixture and full carrier suite | SUGGESTION | Confirmed locally |
| Only exact base `files` formatting rewrite is allowed | ✅ source/constants | ✅ platform/arbitrary negative probes | SUGGESTION | Confirmed locally |
| Private/parser/carrier/replay negative boundaries remain strict | ✅ focused runtime suites | ✅ static/mode/provenance checks | SUGGESTION | Confirmed locally |
| Release Please `17.6.0`, Cargo, npm, OCI, workflow, shell, package, and whitespace checks | ✅ command execution | ✅ evidence summary and no-write boundary | SUGGESTION | Confirmed locally |
| Corrected hosted replay and independent acceptance | ✅ safety policy boundary | ❌ not executed or authorized | WARNING | Remaining external gate |

### Final verdict

**PASS WITH WARNINGS** — the exact real PR `#59` API file list now passes, the pre-fix rejection is
reproduced honestly, the new npm hunk-only fixture and existing carrier/private/parser negatives pass,
the formatting allowance is exact and not broadened to platform or arbitrary base edits, and all
requested local Release Please `17.6.0`, Cargo, npm, OCI, workflow, shell, package, compile, and
whitespace checks pass. Hosted run `31888439750` remains pre-fix failure evidence; no hosted replay
success, publication, tag, release, or operator acceptance is claimed. Hand off explicitly to **`sdd-qa`**.


## Phase 10 fresh verification — Release Please owner correction — 2026-08-24

### Status

**PASS WITH WARNINGS** for the local ownership-correction slice. Hosted/live release acceptance remains **NOT TESTED/BLOCKED** and is not claimed.

### Evidence

- `python3 -m py_compile tests/release_carrier_static_tests.py` — PASS
- `python3 tests/release_carrier_static_tests.py` — PASS (`RELEASE CARRIER STATIC TESTS: PASS`)
- `git diff --check` — PASS
- `actionlint` — NOT RUN in this handoff; available locally and should be run before merge.
- Carrier forbidden-marker scan — PASS: no tag/ref/release/label mutation commands or release fallback token are present in `.github/workflows/release-tag-carrier.yml`.
- Release Please workflow — PASS: runs on `main`, keeps `contents: write` and `RELEASE_PLEASE_TOKEN`, and no longer sets `skip-github-release`.
- Publish workflow — PASS locally by static contract: read-only `gh release view` plus exact tag/ref SHA checks, then upload to the existing release with `RELEASE_PLEASE_TOKEN`; no `gh release create` fallback.

### Phase 10 task classification

| Task | Status | Evidence / limitation |
|---|---|---|
| 10.1 | PASS | Static ownership assertions and forbidden carrier mutation markers pass. |
| 10.2 | NOT TESTED in this slice | Existing validator/runtime fixtures are preserved, but this handoff did not rerun the broader fixture suite. |
| 10.3 | PARTIAL | Existing provenance validator and carrier correlation remain in place; exact hosted Release Please tag/release identity was not exercised. |
| 10.4 | PASS locally | Carrier is read-only and retains dry-run/replay-safe correlation; hosted dispatch not exercised. |
| 10.5 | PASS locally | Publish requires existing release and uploads only after verification; hosted release/upload not exercised. |
| 10.6 | PASS locally | Explicit repository scope and least-privilege carrier/release permissions are statically present; hosted permission behavior not exercised. |
| 10.7 | PASS locally | Focused static test contract passes; downstream fake-host/runtime harness not rerun in this slice. |
| 10.8 | PARTIAL | Focused Python, static, and whitespace checks pass; actionlint and full release-please runtime harness remain outstanding. |

### Risks and blockers

1. No hosted dry-run/replay or live release evidence was collected for this corrective slice.
2. `release-publish.yml` still has unrelated registry authentication using `secrets.GITHUB_TOKEN`; the static test scopes release-credential checks to GitHub Release operations and does not treat that registry credential as a release-owner violation.
3. Phase 10 task checklist and `state.yaml` still need orchestration updates; do not run `sdd-archive` until hosted QA policy gates and prior unresolved P1 blockers are cleared.

### Next recommended action

Run `actionlint` plus the focused runtime/provenance harness, then delegate `sdd-qa` for an authorized read-only hosted dry-run/replay. Keep live release and archive gated on explicit authorization and clean verification/QA reports.
