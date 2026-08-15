## Canonical release carrier plan
- record: carrier-plan.json
- mode: dry-run
- replay: false
- source checkout SHA: 6b65654977f7b41ee9a964f9089a6629fd521d4e
- effective event SHA: 6b65654977f7b41ee9a964f9089a6629fd521d4e
- dry-run: true
- replay event SHA: none

```json
{
  "event": {
    "name": "workflow_dispatch",
    "ref": "refs/heads/main",
    "sha": "6b65654977f7b41ee9a964f9089a6629fd521d4e"
  },
  "replay": false,
  "source_checkout_sha": "6b65654977f7b41ee9a964f9089a6629fd521d4e",
  "replay_event_sha": null,
  "mode": {
    "dry_run": true,
    "normalized": "dry-run",
    "replay": false
  },
  "carrier": {
    "tag": "v0.2.0",
    "version": "0.2.0"
  },
  "validation": {
    "merged_release_please_pr": "passed",
    "merged_tree": "passed",
    "stage_a_diff": "passed",
    "version": "passed",
    "provenance": "passed",
    "lockfile": "passed",
    "metadata": "passed",
    "changed_file_count": 32
  },
  "tag_plan": {
    "action": "create",
    "sha": "6b65654977f7b41ee9a964f9089a6629fd521d4e",
    "tag": "v0.2.0",
    "version": "0.2.0"
  },
  "existing_ref": null,
  "existing_release": false,
  "mutations": {
    "canonical_tag_ref": "skipped",
    "version_pr_label": "skipped",
    "release_on_tag_workflow": "not-dispatched",
    "release_asset_upload": "not-started",
    "cargo_publication": "not-started",
    "npm_publication": "not-started",
    "oci_publication": "not-started",
    "attestation": "not-started",
    "publication": "not-started"
  }
}
```
