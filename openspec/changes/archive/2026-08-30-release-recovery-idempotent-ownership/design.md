# Technical Design: Idempotent Release Recovery and Ownership

## Context and root cause

PR #75 merged the historical `v0.3.0` release PR, but the canonical `v0.3.0` tag and GitHub Release were never created. Release Please was configured with `skip-github-release: true` at global/root scope, so the workflow could complete without materializing the canonical release identity. The next Stage A run then detected a merged release PR without its tag and stopped before producing the next release candidate.

The recovery must repair the historical release without treating the current `main` graph as the source of truth for an old release. It must also make the normal path fail closed when the release identity is incomplete.

## Ownership boundaries

- **Release Please** is the only writer for canonical `vX.Y.Z` tags and GitHub Releases. Its configuration must not suppress GitHub Release creation.
- **Release carrier** is read-only with respect to release identity. It validates an existing merged-main release, records/correlates provenance, and dispatches downstream workflows. It never creates tags, releases, or release labels.
- **`release-on-tag.yml`** consumes an existing canonical tag/release and publishes artifacts in the established order. It never creates a missing tag or GitHub Release as a fallback. Missing or conflicting identity is a hard failure.
- **Recovery workflow/script** is an explicit operator tool for exceptional historical reconciliation. It is not a second normal release owner and is disabled unless the operator supplies an exact target and an explicit live authorization.

## Alternatives and decision

### Regenerate from current `main`

Rejected for historical recovery. It is simple, but it evaluates the current dependency/provider graph and can produce metadata that does not describe the historical `v0.3.0` tree. This is the failure observed when the 13-entry historical manifest was compared with the current 14-entry graph.

### Reconstruct from a historical snapshot

Chosen. Resolve the exact merged commit for `v0.3.0`, read its tree and release manifest/version files at that commit, and validate all derived data against that snapshot. The current tree may be used only for an explicit compatibility check; it must not be required to contain the same graph. This preserves historical provenance and makes replay deterministic.

### GitHub-native/manual recovery

Useful as an emergency last resort, but not sufficient as the durable design. Manual tag/release creation is difficult to audit, easy to repeat inconsistently, and can bypass the normal ownership and publication guards. The implementation may expose a tightly guarded live operation, but the operation must use the same validation plan and audit record as automation.

## Recovery contract

The recovery input is a structured request containing:

- exact repository owner/name;
- target version and canonical tag, for example `0.3.0` and `v0.3.0`;
- exact merged-main commit SHA for PR #75;
- source release PR number and merge status;
- historical manifest/tree reference;
- mode: `dry-run` or explicitly authorized `live`;
- an operator-provided authorization marker for live mode;
- an idempotency key derived from repository, tag, target SHA, and operation type.

The planner resolves and validates, without writes:

1. repository identity and default branch;
2. PR merge state and exact merge SHA;
3. historical version files and manifest at the target commit;
4. canonical tag name and tag target;
5. existing tag and GitHub Release, if any;
6. release body/provenance and artifact plan;
7. that no current-graph mismatch invalidates the historical snapshot;
8. that the operation is not an attempt to publish artifacts.

Dry-run output is a machine-readable and human-readable plan containing `NO_WRITES`, the resolved target SHA, tag/release state, intended operations, provenance digest, and reasons for any refusal. It must not invoke tag creation, release creation, registry upload, package publication, or downstream publication dispatch.

Live mode is a separate command/job path. It refuses to run unless the same plan has passed, the authorization marker is present, the repository and SHA still match, and the operator explicitly confirms the planned mutation. Live mode may reconcile only the canonical tag and GitHub Release; artifact publication remains a separate downstream action triggered only after the release identity is complete.

## Idempotency and concurrency

- If the canonical tag already points to the exact target SHA, tag creation is a no-op.
- If the tag exists at another SHA, recovery fails closed; it never force-moves or deletes a tag.
- If the GitHub Release exists for the canonical tag with matching identity, release creation is a no-op; metadata may be reconciled only through an explicitly planned, non-destructive update.
- If a release exists for the tag but points to a conflicting target or immutable provenance, recovery fails closed.
- A missing tag and missing release are reconciled in dependency order: tag first, then release. A partial failure produces an auditable state and a rerunnable plan; it does not roll back or delete an existing canonical tag/release.
- A repository-scoped lock/idempotency key prevents concurrent live recoveries for the same `(tag, target SHA)`. Re-runs re-read remote state and converge to no-op or a precise conflict.
- API responses must be complete before planning. Truncated, malformed, paginated, or unexpectedly patched manifest/API data is a hard failure, never a best-effort reconstruction.

## Provenance and audit

Every plan and live execution records repository, source PR, target SHA, historical snapshot reference, version, tag, release ID, operation mode, actor, timestamp, idempotency key, validation results, and downstream publication status. Provenance must identify the exact commit that owns the release. Logs must avoid credentials and must make `NO_WRITES`, refusal, no-op, and mutation outcomes distinguishable.

## Preventing accidental publication

Recovery has no registry credentials and no publication dispatch capability in its dry-run path. The live recovery path creates/reconciles only the canonical tag and GitHub Release. Carrier and `release-on-tag.yml` keep explicit guards that reject missing/ambiguous release identity. Cargo/npm/OCI workflows remain downstream consumers and can start only from a verified canonical tag/release; a recovery rerun cannot itself upload packages or images.

## Expected repository changes

- Remove the global/root `skip-github-release` suppression from `release-please-config.json` and add a regression assertion for effective release creation.
- Add a small, testable recovery planner/validator under the existing release scripts, with an adapter for GitHub reads/writes and a no-write default.
- Add a dedicated recovery workflow with separate dry-run and explicitly authorized live paths; the live path must use protected environment/approval controls.
- Strengthen carrier and `release-on-tag.yml` checks so missing, mismatched, or incomplete release identity fails closed without fallback creation.
- Extend provenance/static/runtime tests and fixtures with the historical 13-entry manifest/tree and current 14-entry graph.

No application/provider behavior changes are included.

## TDD and verification strategy

1. Add failing unit/regression tests for merged-but-untagged detection, historical snapshot replay, current-graph mismatch tolerance, conflicting tags/releases, partial resources, concurrent/repeated recovery, truncated API patches, and dry-run `NO_WRITES`.
2. Implement the smallest planner/adapter and workflow changes needed to make those tests pass.
3. Run focused release provenance, carrier behavior/static, recovery planner, and workflow contract tests.
4. Run the no-write runtime harness and verify it cannot call mutation/publication adapters.
5. Run OpenSpec verification against proposal/spec/tasks.
6. Perform hosted dry-run validation only after the workflow is present. Any live `v0.3.0` recovery, tag creation, GitHub Release creation, or publication requires a separate explicit operator authorization after all reports pass.
