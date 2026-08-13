#!/usr/bin/env bash

set -euo pipefail

: "${RELEASE_REF:?RELEASE_REF is required}"
: "${RELEASE_SHA:?RELEASE_SHA is required}"

mkdir -p oci-evidence
printf '%s\n' linux/amd64 linux/arm64
SOURCE_REVISION="${RELEASE_SHA}"
RELEASE_VERSION="${RELEASE_REF#v}"
BUILD_EPOCH="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
CONTRACT_INPUT="oci-evidence/contract-input.xml"
printf '%s\n' '<report><class name="C"><method name="m" desc="()V"><counter type="COMPLEXITY" missed="0" covered="1"/><counter type="INSTRUCTION" missed="0" covered="1"/></method></class></report>' > "$CONTRACT_INPUT"
# The local Docker exporter cannot carry attestations. GitHub's
# registry attestation is emitted only after the verified manifest.
for architecture in amd64 arm64; do
  STAGING_IMAGE="codegauge-oci-${architecture}:${RELEASE_SHA}"
  OCI_ARCHIVE="oci-evidence/${architecture}.oci.tar"
  DOCKER_ARCHIVE="oci-evidence/${architecture}.docker.tar"
  METADATA_JSON="oci-evidence/${architecture}.metadata.json"
  INSPECT_JSON="oci-evidence/${architecture}.inspect.json"
  VERSION_OUTPUT="oci-evidence/${architecture}.version.txt"
  PROFILES_OUTPUT="oci-evidence/${architecture}.profiles.txt"
  CONTRACT_OUTPUT="oci-evidence/${architecture}.contract.json"
  NON_ROOT_OUTPUT="oci-evidence/${architecture}.uid.txt"
  EMULATION_EVIDENCE="oci-evidence/${architecture}.emulation.txt"
  EVIDENCE_OUTPUT="oci-evidence/${architecture}.json"
  if [[ "$architecture" == "arm64" ]]; then
    runtime_mode="qemu"
  else
    runtime_mode="native"
  fi

  docker buildx build --platform "linux/${architecture}" \
    --build-arg CODEGAUGE_VERSION="$RELEASE_VERSION" \
    --build-arg CODEGAUGE_REVISION="$SOURCE_REVISION" \
    --label org.opencontainers.image.version="$RELEASE_VERSION" \
    --label org.opencontainers.image.revision="$SOURCE_REVISION" \
    --label org.opencontainers.image.source="https://github.com/yacosta738/codegauge" \
    --label org.opencontainers.image.platform="linux/${architecture}" \
    --label org.opencontainers.image.created="$BUILD_EPOCH" \
    --provenance=false \
    --sbom=false \
    --metadata-file "$METADATA_JSON" \
    --tag "$STAGING_IMAGE" \
    --output=type=oci,dest="$OCI_ARCHIVE" \
    --output=type=docker,dest="$DOCKER_ARCHIVE" .

  docker load --input "$DOCKER_ARCHIVE" | tee "oci-evidence/${architecture}.load.log"
  docker image inspect --platform "linux/${architecture}" --format '{{json .}}' "$STAGING_IMAGE" > "$INSPECT_JSON"

  if [[ "$architecture" == "arm64" ]]; then
    docker run --rm --platform "linux/${architecture}" \
      --entrypoint /bin/sh "$STAGING_IMAGE" -c 'uname -m' > "$EMULATION_EVIDENCE"
    test "$(tr -d '\r\n' < "$EMULATION_EVIDENCE")" = "aarch64"
    printf '%s\n' 'platform=linux/arm64' 'runtime_mode=qemu' 'evidence=platform-run' >> "$EMULATION_EVIDENCE"
  else
    docker run --rm --platform "linux/${architecture}" \
      --entrypoint /bin/sh "$STAGING_IMAGE" -c 'uname -m' > "$EMULATION_EVIDENCE"
    test "$(tr -d '\r\n' < "$EMULATION_EVIDENCE")" = "x86_64"
    printf '%s\n' 'platform=linux/amd64' 'runtime_mode=native' 'evidence=platform-run' >> "$EMULATION_EVIDENCE"
  fi
  docker run --rm --platform "linux/${architecture}" \
    "$STAGING_IMAGE" version > "$VERSION_OUTPUT"
  docker run --rm --platform "linux/${architecture}" \
    "$STAGING_IMAGE" profiles > "$PROFILES_OUTPUT"
  docker run --rm --platform "linux/${architecture}" \
    --mount "type=bind,src=$(pwd)/${CONTRACT_INPUT},dst=/tmp/contract.xml,readonly" \
    "$STAGING_IMAGE" \
    analyze --profile java-jacoco-v1 --input /tmp/contract.xml --format json > "$CONTRACT_OUTPUT"
  docker run --rm --platform "linux/${architecture}" \
    --entrypoint /bin/sh "$STAGING_IMAGE" -c 'id -u' > "$NON_ROOT_OUTPUT"

  python3 scripts/verify_oci_evidence.py \
    --oci-archive "$OCI_ARCHIVE" \
    --docker-archive "$DOCKER_ARCHIVE" \
    --inspect-json "$INSPECT_JSON" \
    --metadata-json "$METADATA_JSON" \
    --version "$RELEASE_VERSION" \
    --revision "$SOURCE_REVISION" \
    --platform "linux/${architecture}" \
    --runtime-mode "$runtime_mode" \
    --version-output "$VERSION_OUTPUT" \
    --profiles-output "$PROFILES_OUTPUT" \
    --contract-output "$CONTRACT_OUTPUT" \
    --non-root-output "$NON_ROOT_OUTPUT" \
    --emulation-evidence "$EMULATION_EVIDENCE" \
    --output "$EVIDENCE_OUTPUT"
done
