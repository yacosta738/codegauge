# syntax=docker/dockerfile:1.26
FROM rust:1.99.0-alpine@sha256:0cce0a5e0e8ba67b455257a3a02a1d99005f382748789d6464460028810f1627 AS builder

ARG TARGETARCH
ARG CODEGAUGE_VERSION=unknown
ARG CODEGAUGE_REVISION=unknown

RUN apk add --no-cache musl-dev gcc
WORKDIR /workspace

COPY Cargo.toml Cargo.lock rust-toolchain.toml LICENSE README.md ./
COPY crates ./crates

RUN cargo build --release --locked --package codegauge-cli --bin codegauge \
    && test -x target/release/codegauge

FROM alpine:3.24@sha256:28bd5fe8b56d1bd048e5babf5b10710ebe0bae67db86916198a6eec434943f8b

ARG CODEGAUGE_VERSION=unknown
ARG CODEGAUGE_REVISION=unknown

RUN apk add --no-cache tini \
    && addgroup -S codegauge \
    && adduser -S -G codegauge -h /nonexistent -s /sbin/nologin codegauge

COPY --from=builder /workspace/target/release/codegauge /usr/local/bin/codegauge

LABEL org.opencontainers.image.title="CodeGauge" \
      org.opencontainers.image.description="Deterministic JaCoCo evidence CLI" \
      org.opencontainers.image.source="https://github.com/yacosta738/codegauge" \
      org.opencontainers.image.version="$CODEGAUGE_VERSION" \
      org.opencontainers.image.revision="$CODEGAUGE_REVISION"

USER codegauge
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/codegauge"]
