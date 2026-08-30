# Historical release recovery runbook

This runbook covers the exceptional recovery of the merged `v0.3.0` release from PR #75. It is
an operator procedure, not an automated rollback. CodeGauge behavior and the canonical release
identity are immutable once published.

## Before recovery

1. Run the default dry-run with
   `fixtures/release-recovery/v0.3.0-dry-run-request.json` and
   `fixtures/release-recovery/v0.3.0-empty-snapshot.json`.
2. Confirm the audit records the expected repository, PR, merged SHA, historical tree, 13-entry
   manifest, current 14-entry graph, synchronized versions, and the two-step artifact plan:
   canonical tag, then GitHub Release.
3. Obtain the normal protected-environment approval. Do not provide registry credentials to the
   planner or dry-run path.

## Disable live recovery

To stop or roll back recovery, first set the repository variable
`RELEASE_RECOVERY_LIVE_ENABLED` to anything other than `true` (or disable the workflow in GitHub).
The live job also requires approval for the protected `release-recovery-live` environment. Leave the
variable disabled after the approved operation and retain both machine and human audit artifacts.

## Preserve canonical resources

Never delete or force-move a canonical tag or GitHub Release. Do not use `git tag -f`, `git push
--force`, tag deletion, release deletion, or a replacement tag/release to repair a conflict. A
conflicting identity is a refusal that must be investigated, not overwritten.

Recovery writes only the canonical tag and then the GitHub Release. It does not publish Cargo, npm,
or OCI artifacts. A write whose result is ambiguous is recorded as `mutation-unknown`; do not retry
blindly until the remote tag and release have been re-read.

## Stop later publication stages

If any publication target fails, stop later publication stages immediately. Do not restart the
whole chain under a new identity; follow the inventory procedure below.

## Partial publication response

Publication jobs are dependency-ordered. If an earlier target succeeds and a later target fails,
stop later publication stages; do not restart the whole chain under a new identity. The failure
inventory must record, for every target, the canonical version, source SHA, package/image reference,
published digest or package version when known, job result, and audit-artifact location. The
`publication-failure-inventory` workflow job records job results and points operators here; it does
not delete, overwrite, or pretend to undo an external publication.

Inventory immutable outputs before taking any target action:

- Cargo crate name/version and crates.io publication or yank state;
- npm package name/version and deprecation state;
- OCI repository, immutable digest, architecture manifests, and mutable aliases;
- GitHub Release asset names and checksums; and
- the exact canonical tag and merged source SHA.

## Target deprecation and rollback

Use target-native, non-destructive controls only after the inventory is complete:

- mark an incorrect Cargo version yanked through the crates.io owner controls;
- mark an incorrect npm version deprecated with a clear operator message;
- stop promoting an incorrect OCI digest and coordinate registry-specific deprecation/retention
  handling without deleting or force-moving the canonical release tag; and
- direct consumers to the last known-good immutable version or digest while the incident is fixed.

Do not mint a new canonical identity to hide a partial publication, and do not commit credentials or
rollback commands into the repository. Record the operator, timestamp, reason, target state, and
follow-up issue with the recovery audit.
