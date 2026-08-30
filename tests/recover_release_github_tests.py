#!/usr/bin/env python3
"""Focused contracts for the read/write GitHub recovery adapter."""

from __future__ import annotations

import base64
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from recover_release import RecoveryError, RecoveryPreflight  # noqa: E402
from recover_release_github import (  # noqa: E402
    ApiResponse,
    GitHubRecoveryAdapter,
    parse_link_next,
)
from recover_release_tests import (  # noqa: E402
    MANIFEST,
    REPOSITORY,
    SHA,
    TAG,
    TREE,
    VERSION,
    request,
)


class FakeTransport:
    def __init__(self, responses: list[ApiResponse]) -> None:
        self.responses = iter(responses)
        self.calls: list[tuple[str, str, object]] = []

    def request(self, method: str, path: str, body: object = None) -> ApiResponse:
        self.calls.append((method, path, body))
        return next(self.responses)


def response(status: int, body: object, *, headers: dict[str, str] | None = None) -> ApiResponse:
    return ApiResponse(status=status, headers=headers or {}, body=body)


def tag_body(sha: str = SHA) -> dict[str, object]:
    return {
        "ref": f"refs/tags/{TAG}",
        "object": {"sha": sha, "type": "commit", "url": "https://api.github.com/objects"},
        "url": "https://api.github.com/ref",
    }


def release_body(sha: str = SHA, tag: str = TAG) -> dict[str, object]:
    return {
        "id": 75,
        "tag_name": tag,
        "target_commitish": sha,
        "name": tag,
        "release_version": VERSION,
        "body": f"Historical recovery for {sha}",
        "draft": False,
        "prerelease": False,
        "html_url": "https://github.com/yacosta738/codegauge/releases/tag/v0.3.0",
    }


CURRENT_SHA = "c" * 40
CURRENT_TREE = "d" * 40
HISTORICAL_MANIFEST_BLOB = "e" * 40
CURRENT_CONTENT_BLOB = "f" * 40
HISTORICAL_PATHS = {
    ".",
    "crates/codegauge-model",
    "crates/codegauge-core",
    "crates/codegauge-application",
    "crates/codegauge-provider-jacoco",
    "crates/codegauge-cli",
    "npm/codegauge",
    "npm/packages/codegauge-linux-x64-gnu",
    "npm/packages/codegauge-linux-arm64-gnu",
    "npm/packages/codegauge-darwin-x64",
    "npm/packages/codegauge-darwin-arm64",
    "npm/packages/codegauge-win32-x64-msvc",
    "npm/packages/codegauge-win32-arm64-msvc",
}
CURRENT_PATHS = HISTORICAL_PATHS | {"crates/codegauge-provider-typescript"}


def _manifest(paths: set[str]) -> dict[str, str]:
    return {path: VERSION for path in sorted(paths)}


def _content(path: str, value: object, ref: str) -> tuple[str, ApiResponse]:
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    return (
        f"/repos/{REPOSITORY}/contents/{path}?ref={ref}",
        response(
            200,
            {
                "type": "file",
                "path": path,
                "sha": CURRENT_CONTENT_BLOB,
                "encoding": "base64",
                "content": base64.b64encode(text.encode()).decode(),
            },
        ),
    )


def _version_files(version: str, *, include_typescript: bool) -> dict[str, str]:
    files = {
        "Cargo.toml": f"[workspace.package]\nversion = \"{version}\"\n",
        "Cargo.lock": "\n".join(
            f'[[package]]\nname = "{crate}"\nversion = "{version}"\n'
            for crate in (
                "codegauge-model",
                "codegauge-core",
                "codegauge-application",
                "codegauge-provider-jacoco",
                *(('codegauge-provider-typescript',) if include_typescript else ()),
                "codegauge-cli",
            )
        ),
        "Dockerfile": (
            "FROM rust:1.97.1-alpine@sha256:" + "a" * 64 + "\n"
            "ARG CODEGAUGE_VERSION=unknown\n"
            "ARG CODEGAUGE_REVISION=unknown\n"
            "FROM alpine:3.24@sha256:" + "b" * 64 + "\n"
            "LABEL org.opencontainers.image.version=\"$CODEGAUGE_VERSION\" \\\n"
            "      org.opencontainers.image.revision=\"$CODEGAUGE_REVISION\"\n"
        ),
        "crates/codegauge-conformance/Cargo.toml": (
            '[package]\nname = "codegauge-conformance"\nversion = "0.1.0"\n'
            'publish = false\n\n[dependencies]\n'
            + "\n".join(
                f'{crate} = {{ version = "{version}", path = "../{crate}" }}'
                for crate in (
                    "codegauge-model",
                    "codegauge-core",
                    "codegauge-application",
                    "codegauge-provider-jacoco",
                    *(('codegauge-provider-typescript',) if include_typescript else ()),
                )
            )
            + "\n"
        ),
        "crates/codegauge-model/Cargo.toml": f'[package]\nname = "codegauge-model"\nversion = "{version}"\n',
        "crates/codegauge-core/Cargo.toml": f'[package]\nname = "codegauge-core"\nversion = "{version}"\n',
        "crates/codegauge-application/Cargo.toml": f'[package]\nname = "codegauge-application"\nversion = "{version}"\n',
        "crates/codegauge-provider-jacoco/Cargo.toml": f'[package]\nname = "codegauge-provider-jacoco"\nversion = "{version}"\n',
        "crates/codegauge-cli/Cargo.toml": f'[package]\nname = "codegauge-cli"\nversion = "{version}"\n',
        "npm/codegauge/package.json": json.dumps(
            {
                "name": "@yacosta738/codegauge",
                "version": version,
                "optionalDependencies": {
                    "@yacosta738/codegauge-darwin-arm64": version,
                    "@yacosta738/codegauge-darwin-x64": version,
                    "@yacosta738/codegauge-linux-arm64-gnu": version,
                    "@yacosta738/codegauge-linux-x64-gnu": version,
                    "@yacosta738/codegauge-win32-arm64-msvc": version,
                    "@yacosta738/codegauge-win32-x64-msvc": version,
                },
            }
        ),
    }
    if include_typescript:
        files["crates/codegauge-provider-typescript/Cargo.toml"] = (
            f'[package]\nname = "codegauge-provider-typescript"\nversion = "{version}"\n'
        )
    for package in (
        "codegauge-linux-x64-gnu",
        "codegauge-linux-arm64-gnu",
        "codegauge-darwin-x64",
        "codegauge-darwin-arm64",
        "codegauge-win32-x64-msvc",
        "codegauge-win32-arm64-msvc",
    ):
        files[f"npm/packages/{package}/package.json"] = json.dumps(
            {"name": f"@yacosta738/{package}", "version": version}
        )
    return files


class PreflightTransport:
    """Complete read-only GitHub fixture for the live preflight contract."""

    def __init__(self) -> None:
        historical_manifest = _manifest(HISTORICAL_PATHS)
        current_manifest = _manifest(CURRENT_PATHS)
        historical_manifest_text = json.dumps(historical_manifest, indent=2, sort_keys=True) + "\n"
        self.repository = {"full_name": REPOSITORY, "default_branch": "main"}
        self.pull = {
            "number": 75,
            "state": "closed",
            "merged": True,
            "merged_at": "2026-08-22T21:16:58Z",
            "merge_commit_sha": SHA,
            "base": {"ref": "main", "repo": {"full_name": REPOSITORY}},
        }
        self.commit = {
            "sha": SHA,
            "commit": {"tree": {"sha": TREE}},
        }
        self.branch_ref = {
            "ref": "refs/heads/main",
            "object": {"type": "commit", "sha": CURRENT_SHA},
        }
        self.current_commit = {
            "sha": CURRENT_SHA,
            "commit": {"tree": {"sha": CURRENT_TREE}},
        }
        self.historical_tree = {
            "sha": TREE,
            "truncated": False,
            "tree": [
                {"path": path, "type": "tree", "sha": "1" * 40}
                for path in sorted(HISTORICAL_PATHS - {"."})
            ]
            + [
                {
                    "path": ".release-please-manifest.json",
                    "type": "blob",
                    "sha": HISTORICAL_MANIFEST_BLOB,
                }
            ],
        }
        self.current_tree = {
            "sha": CURRENT_TREE,
            "truncated": False,
            "tree": [
                {"path": path, "type": "tree", "sha": "2" * 40}
                for path in sorted(CURRENT_PATHS - {"."})
            ]
            + [
                {
                    "path": ".release-please-manifest.json",
                    "type": "blob",
                    "sha": CURRENT_CONTENT_BLOB,
                }
            ],
        }
        self.historical_files = _version_files(VERSION, include_typescript=False)
        self.current_files = _version_files(VERSION, include_typescript=True)
        self.historical_files[".release-please-manifest.json"] = historical_manifest_text
        self.current_files[".release-please-manifest.json"] = json.dumps(
            current_manifest, indent=2, sort_keys=True
        ) + "\n"
        self.calls: list[tuple[str, str, object]] = []

    def request(self, method: str, path: str, body: object = None) -> ApiResponse:
        self.calls.append((method, path, body))
        if method != "GET":
            raise AssertionError(f"preflight attempted a write: {method} {path}")
        if path == f"/repos/{REPOSITORY}":
            return response(200, self.repository)
        if path == f"/repos/{REPOSITORY}/pulls/75":
            return response(200, self.pull)
        if path == f"/repos/{REPOSITORY}/commits/{SHA}":
            return response(200, self.commit)
        if path == f"/repos/{REPOSITORY}/git/ref/heads/main":
            return response(200, self.branch_ref)
        if path == f"/repos/{REPOSITORY}/commits/{CURRENT_SHA}":
            return response(200, self.current_commit)
        if path == f"/repos/{REPOSITORY}/git/trees/{TREE}?recursive=1":
            return response(200, self.historical_tree)
        if path == f"/repos/{REPOSITORY}/git/trees/{CURRENT_TREE}?recursive=1":
            return response(200, self.current_tree)
        if path == f"/repos/{REPOSITORY}/git/blobs/{HISTORICAL_MANIFEST_BLOB}":
            return response(
                200,
                {
                    "sha": HISTORICAL_MANIFEST_BLOB,
                    "encoding": "base64",
                    "content": base64.b64encode(
                        self.historical_files[".release-please-manifest.json"].encode()
                    ).decode(),
                },
            )
        if path == f"/repos/{REPOSITORY}/git/ref/tags/{TAG}":
            return response(404, {"message": "Not Found"})
        if path == f"/repos/{REPOSITORY}/releases/tags/{TAG}":
            return response(404, {"message": "Not Found"})
        prefix = f"/repos/{REPOSITORY}/contents/"
        if path.startswith(prefix) and "?ref=" in path:
            content_path, ref = path[len(prefix):].split("?ref=", 1)
            files = self.current_files if ref == CURRENT_SHA else self.historical_files
            if content_path not in files:
                return response(404, {"message": "Not Found"})
            content_path_value, content_response = _content(content_path, files[content_path], ref)
            assert content_path_value == path
            return content_response
        return response(404, {"message": "Not Found"})


def test_preflight_authenticates_repository_merge_snapshot_graph_and_artifact_plan() -> None:
    transport = PreflightTransport()
    adapter = GitHubRecoveryAdapter(transport, REPOSITORY)

    result = adapter.preflight(request())

    assert isinstance(result, RecoveryPreflight)
    assert result.repository == REPOSITORY
    assert result.default_branch == "main"
    assert result.pull_request == 75
    assert result.merged_sha == SHA
    assert result.historical_tree == TREE
    assert result.historical_entry_count == 13
    assert result.current_entry_count == 14
    assert result.graph_mismatch is True
    assert result.artifact_plan == ("canonical-tag", "github-release")
    assert result.snapshot.tag_exists is False
    assert result.snapshot.release_exists is False
    assert all(method == "GET" for method, _, _ in transport.calls)
    assert transport.calls[0][1] == f"/repos/{REPOSITORY}"
    assert any(f"/pulls/75" in path for _, path, _ in transport.calls)
    assert any("git/trees/" in path for _, path, _ in transport.calls)
    assert any("git/blobs/" in path for _, path, _ in transport.calls)
    assert any("contents/.release-please-manifest.json" in path for _, path, _ in transport.calls)


@pytest.mark.parametrize(
    "boundary, message",
    [
        ("repository", "repository identity"),
        ("pull", "SHA"),
        ("manifest", "historical manifest"),
        ("current", "current release graph"),
    ],
)
def test_preflight_rejects_remote_identity_or_graph_mismatch(
    boundary: str, message: str
) -> None:
    transport = PreflightTransport()
    if boundary == "repository":
        transport.repository["full_name"] = "attacker/example"
    elif boundary == "pull":
        transport.pull["merge_commit_sha"] = "b" * 40
    elif boundary == "manifest":
        transport.historical_files[".release-please-manifest.json"] = "{}"
    else:
        current = json.loads(transport.current_files[".release-please-manifest.json"])
        current.pop("npm/codegauge")
        transport.current_files[".release-please-manifest.json"] = json.dumps(current)

    with pytest.raises(RecoveryError, match=message):
        GitHubRecoveryAdapter(transport, REPOSITORY).preflight(request())

    assert all(method == "GET" for method, _, _ in transport.calls)


def test_missing_resources_are_read_as_recoverable() -> None:
    transport = FakeTransport([response(404, {"message": "Not Found"}), response(404, {"message": "Not Found"})])
    adapter = GitHubRecoveryAdapter(transport, REPOSITORY)

    snapshot = adapter.snapshot(request())

    assert snapshot.tag_exists is False
    assert snapshot.release_exists is False
    assert [call[0] for call in transport.calls] == ["GET", "GET"]


@pytest.mark.parametrize("repository", ["owner", "owner/", "/repo", "owner/name/extra", "owner/name space"])
def test_adapter_rejects_noncanonical_repository_scope(repository: str) -> None:
    with pytest.raises(RecoveryError, match="repository"):
        GitHubRecoveryAdapter(FakeTransport([]), repository)


def test_matching_tag_and_release_are_returned_with_exact_identity() -> None:
    transport = FakeTransport([response(200, tag_body()), response(200, release_body())])
    adapter = GitHubRecoveryAdapter(transport, REPOSITORY)

    snapshot = adapter.snapshot(request())

    assert snapshot.tag_sha == SHA
    assert snapshot.tag_type == "commit"
    assert snapshot.release_tag == TAG
    assert snapshot.release_sha == SHA
    assert snapshot.release_version == VERSION
    assert snapshot.release_id == 75
    assert len(snapshot.release_body_digest or "") == 64


def test_conflicting_remote_identity_fails_before_writes() -> None:
    transport = FakeTransport([response(200, tag_body()), response(200, {**release_body(), "target_commitish": "b" * 40})])
    adapter = GitHubRecoveryAdapter(transport, REPOSITORY)

    with pytest.raises(RecoveryError, match="conflicting"):
        adapter.snapshot(request())

    assert all(call[0] == "GET" for call in transport.calls)


@pytest.mark.parametrize(
    "body, message",
    [
        ({"ref": f"refs/tags/{TAG}"}, "tag response"),
        ({"tag_name": TAG, "target_commitish": SHA}, "release response"),
        ({"tag_name": TAG, "target_commitish": "not-a-sha", "id": 1, "body": ""}, "SHA"),
    ],
)
def test_malformed_resource_responses_fail_closed(body: object, message: str) -> None:
    status = 200
    responses = [response(status, body), response(404, {"message": "Not Found"})]
    if "release" in message or "SHA" in message:
        responses = [response(404, {"message": "Not Found"}), response(status, body)]
    adapter = GitHubRecoveryAdapter(FakeTransport(responses), REPOSITORY)

    with pytest.raises(RecoveryError, match=message):
        adapter.snapshot(request())


def test_writes_are_narrow_and_use_tag_then_release_payloads() -> None:
    transport = FakeTransport([response(201, tag_body()), response(201, release_body())])
    adapter = GitHubRecoveryAdapter(transport, REPOSITORY)

    adapter.create_tag(request())
    adapter.create_release(request())

    assert transport.calls[0] == (
        "POST",
        f"/repos/{REPOSITORY}/git/refs",
        {"ref": f"refs/tags/{TAG}", "sha": SHA},
    )
    assert transport.calls[1][0:2] == ("POST", f"/repos/{REPOSITORY}/releases")
    assert transport.calls[1][2]["tag_name"] == TAG
    assert transport.calls[1][2]["target_commitish"] == SHA
    assert "publish" not in str(transport.calls)


def test_paginated_link_must_be_well_formed() -> None:
    assert parse_link_next('<https://api.github.com/a?page=2>; rel="next"') == "https://api.github.com/a?page=2"
    assert parse_link_next('<https://api.github.com/a?page=2>; rel="last"') is None
    with pytest.raises(RecoveryError, match="pagination"):
        parse_link_next('https://api.github.com/a?page=2; rel="next"')


def test_pagination_with_next_link_is_rejected_before_recovery_can_truncate() -> None:
    transport = FakeTransport(
        [
            response(200, tag_body()),
            response(
                200,
                release_body(),
                headers={"Link": '<https://api.github.com/repos/yacosta738/codegauge/releases?page=2>; rel="next"'},
            ),
        ]
    )
    adapter = GitHubRecoveryAdapter(transport, REPOSITORY)

    with pytest.raises(RecoveryError, match="pagination"):
        adapter.snapshot(request())


def test_transport_responses_must_be_complete_objects() -> None:
    transport = FakeTransport([response(200, {"ref": f"refs/tags/{TAG}", "object": {"sha": SHA, "type": "commit"}}), response(200, {"id": 1})])
    adapter = GitHubRecoveryAdapter(transport, REPOSITORY)

    with pytest.raises(RecoveryError, match="release response"):
        adapter.snapshot(request())


def test_urllib_transport_decodes_loopback_responses_without_exposing_token() -> None:
    import recover_release_github as recovery_github

    transport_type = getattr(recovery_github, "UrllibTransport", None)
    assert transport_type is not None

    observed_authorization: list[str | None] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            observed_authorization.append(self.headers.get("Authorization"))
            body = b'{"message":"missing"}'
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, _: str, *__: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    server.block_on_close = False
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        transport = transport_type(
            "secret-token",
            base_url=f"http://127.0.0.1:{server.server_port}",
        )
        result = transport.request("GET", "/missing")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    assert result.status == 404
    assert result.body == {"message": "missing"}
    assert observed_authorization == ["Bearer secret-token"]


@pytest.mark.parametrize("base_url", ["http://github.example", "https://user:secret@github.example"])
def test_urllib_transport_rejects_insecure_or_credentialed_base_urls(base_url: str) -> None:
    import recover_release_github as recovery_github

    with pytest.raises(RecoveryError, match="base URL"):
        recovery_github.UrllibTransport("secret-token", base_url=base_url)
