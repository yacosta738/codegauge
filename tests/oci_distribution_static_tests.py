#!/usr/bin/env python3
"""Static checks for OCI build ordering, evidence handoff, and publication gates."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BUILD_WORKFLOW = ROOT / ".github" / "workflows" / "release-build.yml"
PUBLISH_WORKFLOW = ROOT / ".github" / "workflows" / "release-publish.yml"
OCI_BUILD_SCRIPT = ROOT / "scripts" / "build_oci_release.sh"


def job_block(workflow: str, job_name: str) -> str:
    match = re.search(
        rf"^  {job_name}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing {job_name} job"
    return match.group("body")


def test_workflow_builds_locally_before_publication() -> None:
    build_workflow = BUILD_WORKFLOW.read_text(encoding="utf-8")
    publish_workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")
    script = OCI_BUILD_SCRIPT.read_text(encoding="utf-8")
    build_job = job_block(build_workflow, "oci-preflight")
    publish_job = job_block(publish_workflow, "publish-oci")

    build_start = script.index("docker buildx build")
    inspect_start = next(
        script.index(fragment)
        for fragment in ("docker image inspect", "docker buildx imagetools inspect")
        if fragment in script
    )
    build_block = script[build_start:inspect_start]
    assert "--output=type=oci,dest=" in build_block
    assert "--push" not in build_block
    assert "--tag \"$STAGING_IMAGE\"" in build_block

    smoke_start = script.index(" version", inspect_start)
    evidence_start = script.index("scripts/verify_oci_evidence.py", smoke_start)
    login_start = publish_job.index("docker/login-action")
    push_start = publish_job.index("docker push", login_start)
    manifest_start = publish_job.index("docker buildx imagetools create", push_start)

    assert "docker load --input" in script
    assert build_start < inspect_start < smoke_start < evidence_start
    assert login_start < push_start < manifest_start
    assert "bash scripts/build_oci_release.sh" in build_job
    assert "needs: [release-preflight, release-verify]" in build_job
    assert "if: inputs.dry_run == false" in build_job
    assert "needs: publish-npm" in publish_job
    assert "name: Download verified OCI build artifacts" in publish_job
    assert "docker load --input" in publish_job

    assert "docker image inspect --platform" in script
    assert "--oci-archive" in script[evidence_start:]
    assert '--docker-archive "$DOCKER_ARCHIVE"' in script[evidence_start:]
    assert "--inspect-json" in script[evidence_start:]
    assert "--version-output" in script[evidence_start:]
    assert "--profiles-output" in script[evidence_start:]
    assert "--contract-output" in script[evidence_start:]
    assert "--non-root-output" in script[evidence_start:]
    assert "--output" in script[evidence_start:]
    assert "org.opencontainers.image.platform" in script
    assert "org.opencontainers.image.version" in script
    assert "org.opencontainers.image.revision" in script
    assert "org.opencontainers.image.source" in script


def test_workflow_asserts_runtime_contract_and_emulation_evidence() -> None:
    workflow = OCI_BUILD_SCRIPT.read_text(encoding="utf-8")
    job = job_block(BUILD_WORKFLOW.read_text(encoding="utf-8"), "oci-preflight")

    assert "docker/setup-qemu-action@" in job
    assert 'runtime_mode="qemu"' in workflow
    assert 'runtime_mode="native"' in workflow
    assert "--runtime-mode \"$runtime_mode\"" in workflow
    assert 'docker run --rm --platform "linux/${architecture}"' in workflow
    assert "--entrypoint /bin/sh" in workflow
    assert "id -u" in workflow
    assert " version" in workflow
    assert " profiles" in workflow
    assert "analyze --profile java-jacoco-v1" in workflow
    assert "--input /tmp/contract.xml" in workflow
    assert "--format json" in workflow
    assert "contract-result" not in workflow


def test_workflow_persists_evidence_and_publishes_only_verified_digests() -> None:
    build_workflow = BUILD_WORKFLOW.read_text(encoding="utf-8")
    workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")
    job = job_block(workflow, "publish-oci")
    script = OCI_BUILD_SCRIPT.read_text(encoding="utf-8")

    assert "mkdir -p oci-evidence" in script
    assert "oci-evidence/${architecture}.json" in script
    assert "name: OCI architecture evidence" in build_workflow
    assert "name: Download verified OCI build artifacts" in job
    evidence_step = job[job.index("name: OCI architecture evidence") :]
    assert "if: always()" in evidence_step
    assert "actions/upload-artifact@" in evidence_step
    assert "path: oci-evidence/" in evidence_step

    publish_start = job.index("name: Publish final verified OCI digests")
    publish_end = job.index("name: OCI architecture evidence", publish_start)
    publish = job[publish_start:publish_end]
    assert 'docker tag "$STAGING_IMAGE" "$FINAL_TAG"' in publish
    assert "published_digest" in publish
    assert "docker buildx imagetools inspect --raw" in publish
    assert "published_config_digest" in publish
    assert "oci_config_digest" in publish
    assert '"$IMAGE@${amd64_digest}"' in publish
    assert '"$IMAGE@${arm64_digest}"' in publish
    assert 'docker buildx imagetools inspect --raw "$IMAGE:${RELEASE_VERSION}"' in publish
    assert "jq -e" in publish
    assert '"$IMAGE:latest"' in publish
    assert 'printf \'manifest_digest=%s\\n\' "$FINAL_DIGEST" >> "$GITHUB_OUTPUT"' in publish
    assert "subject-digest: ${{ steps.publish-manifest.outputs.manifest_digest }}" in job
    assert "actions/attest@" in job
    assert "push-to-registry: true" in job

    # Upload evidence may run after a failed architecture, but publication is
    # success-gated rather than using an unconditional always() condition.
    assert "if: always()" not in publish
    assert "set -euo pipefail" in publish


def run_tests(*, include_build_ordering: bool = True) -> None:
    if include_build_ordering:
        test_workflow_builds_locally_before_publication()
    test_workflow_asserts_runtime_contract_and_emulation_evidence()
    test_workflow_persists_evidence_and_publishes_only_verified_digests()


if __name__ == "__main__":
    run_tests()
    print("OCI DISTRIBUTION STATIC TESTS: PASS")
