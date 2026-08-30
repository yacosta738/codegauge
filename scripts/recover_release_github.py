#!/usr/bin/env python3
"""GitHub adapter for the narrow historical release recovery boundary."""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - live workflow uses modern Python
    tomllib = None

from recover_release import (
    EXPECTED_DEFAULT_BRANCH,
    EXPECTED_PULL_REQUEST,
    HISTORICAL_MANIFEST_PATH,
    RECOVERY_ARTIFACT_PLAN,
    REPOSITORY_RE,
    RecoveryError,
    RecoveryPreflight,
    RecoveryRequest,
    ResourceSnapshot,
    SHA_RE,
)


CURRENT_GRAPH_PATHS = frozenset(
    {
        ".",
        "crates/codegauge-model",
        "crates/codegauge-core",
        "crates/codegauge-application",
        "crates/codegauge-provider-jacoco",
        "crates/codegauge-provider-typescript",
        "crates/codegauge-cli",
        "npm/codegauge",
        "npm/packages/codegauge-linux-x64-gnu",
        "npm/packages/codegauge-linux-arm64-gnu",
        "npm/packages/codegauge-darwin-x64",
        "npm/packages/codegauge-darwin-arm64",
        "npm/packages/codegauge-win32-x64-msvc",
        "npm/packages/codegauge-win32-arm64-msvc",
    }
)
HISTORICAL_GRAPH_PATHS = CURRENT_GRAPH_PATHS - {
    "crates/codegauge-provider-typescript"
}
HISTORICAL_RUNTIME_CRATES = (
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-cli",
)
CURRENT_RUNTIME_CRATES = HISTORICAL_RUNTIME_CRATES[:4] + (
    "codegauge-provider-typescript",
    "codegauge-cli",
)
NPM_PLATFORM_PACKAGES = (
    "@yacosta738/codegauge-linux-x64-gnu",
    "@yacosta738/codegauge-linux-arm64-gnu",
    "@yacosta738/codegauge-darwin-x64",
    "@yacosta738/codegauge-darwin-arm64",
    "@yacosta738/codegauge-win32-x64-msvc",
    "@yacosta738/codegauge-win32-arm64-msvc",
)
DOCKERFILE_PATH = "Dockerfile"


class HttpTransport(Protocol):
    def request(self, method: str, path: str, body: object = None) -> "ApiResponse": ...


@dataclass(frozen=True)
class ApiResponse:
    status: int
    headers: dict[str, str]
    body: Any


class UrllibTransport:
    """Small standard-library transport for the protected live recovery path."""

    def __init__(self, token: str, *, base_url: str = "https://api.github.com", timeout: float = 30.0) -> None:
        if not isinstance(token, str) or not token:
            raise RecoveryError("GitHub API transport requires a token")
        parsed_url = urlparse(base_url) if isinstance(base_url, str) else None
        local_hosts = {"127.0.0.1", "localhost", "::1"}
        if (
            parsed_url is None
            or parsed_url.scheme not in {"https", "http"}
            or not parsed_url.netloc
            or parsed_url.username is not None
            or parsed_url.password is not None
            or (parsed_url.scheme != "https" and parsed_url.hostname not in local_hosts)
        ):
            raise RecoveryError("GitHub API base URL must use HTTP(S)")
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method: str, path: str, body: object = None) -> ApiResponse:
        if not isinstance(method, str) or not method:
            raise RecoveryError("GitHub API method must be non-empty")
        if not isinstance(path, str) or not path.startswith("/") or "://" in path:
            raise RecoveryError("GitHub API path must be an absolute API path")
        payload = None if body is None else json.dumps(body, separators=(",", ":")).encode()
        request = Request(
            f"{self.base_url}{path}",
            data=payload,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                status = response.status
                headers = {key: value for key, value in response.headers.items()}
                raw_body = response.read()
        except HTTPError as error:
            status = error.code
            headers = {key: value for key, value in error.headers.items()}
            raw_body = error.read()
        except (OSError, URLError, TimeoutError) as error:
            raise RecoveryError(f"GitHub API transport failed: {error}") from error

        if not raw_body:
            decoded: Any = None
        else:
            try:
                decoded = json.loads(raw_body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise RecoveryError("GitHub API returned malformed JSON") from error
        return ApiResponse(status=status, headers=headers, body=decoded)


NEXT_LINK_RE = re.compile(r"^<([^>]+)>;\s*rel=\"next\"$")


def parse_link_next(header: str | None) -> str | None:
    if not header:
        return None
    for value in header.split(","):
        value = value.strip()
        match = NEXT_LINK_RE.fullmatch(value)
        if match:
            return match.group(1)
        if 'rel="last"' in value:
            continue
        if "rel=" in value:
            raise RecoveryError("pagination Link header is malformed")
    return None


def _object(body: Any, label: str) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise RecoveryError(f"{label} must be a complete JSON object")
    return body


def _response_object(response: ApiResponse, label: str) -> dict[str, Any]:
    if response.status != 200:
        raise RecoveryError(f"{label} API request failed with HTTP {response.status}")
    return _object(response.body, label)


def _decode_base64_content(payload: dict[str, Any], label: str) -> bytes:
    if payload.get("encoding") != "base64" or not isinstance(payload.get("content"), str):
        raise RecoveryError(f"{label} must contain complete base64 file content")
    encoded = "".join(payload["content"].split())
    try:
        return base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as error:
        raise RecoveryError(f"{label} contains malformed base64 content") from error


def _decode_text_file(payload: dict[str, Any], path: str, ref: str) -> str:
    if payload.get("type") != "file" or payload.get("path") != path:
        raise RecoveryError(f"file response is not scoped to {path}")
    if payload.get("ref") is not None and payload.get("ref") != ref:
        raise RecoveryError(f"file response is not scoped to immutable ref {ref}")
    blob_sha = payload.get("sha")
    if not isinstance(blob_sha, str) or not SHA_RE.fullmatch(blob_sha):
        raise RecoveryError(f"{path} file response contains an invalid blob SHA")
    try:
        return _decode_base64_content(payload, path).decode("utf-8")
    except UnicodeDecodeError as error:
        raise RecoveryError(f"{path} file response is not valid UTF-8") from error


def _parse_json_text(text: str, path: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise RecoveryError(f"{path} is malformed JSON") from error
    if not isinstance(value, dict):
        raise RecoveryError(f"{path} must contain a JSON object")
    return value


def _parse_toml_text(text: str, path: str) -> dict[str, Any]:
    if tomllib is None:
        raise RecoveryError("Python tomllib is required for release recovery preflight")
    try:
        value = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise RecoveryError(f"{path} is malformed TOML") from error
    if not isinstance(value, dict):
        raise RecoveryError(f"{path} must contain a TOML table")
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _validate_manifest(
    manifest: object,
    *,
    expected_paths: frozenset[str],
    version: str,
    label: str,
) -> dict[str, str]:
    if not isinstance(manifest, dict) or set(manifest) != expected_paths:
        raise RecoveryError(f"{label} has an unexpected release graph")
    if any(not isinstance(path, str) for path in manifest):
        raise RecoveryError(f"{label} contains an invalid graph path")
    if any(value != version for value in manifest.values()):
        raise RecoveryError(f"{label} versions do not match the requested release")
    return manifest  # type: ignore[return-value]


def _validate_dockerfile(text: str, label: str) -> None:
    required_markers = (
        "FROM rust:1.97.1-alpine@sha256:",
        "FROM alpine:3.24@sha256:",
        "ARG CODEGAUGE_VERSION",
        "ARG CODEGAUGE_REVISION",
        "org.opencontainers.image.version",
        "org.opencontainers.image.revision",
    )
    if any(marker not in text for marker in required_markers):
        raise RecoveryError(f"{label} does not satisfy the immutable container contract")


def _validate_version_files(
    files: dict[str, str],
    *,
    version: str,
    runtime_crates: tuple[str, ...],
    label: str,
) -> None:
    cargo = _parse_toml_text(files["Cargo.toml"], f"{label} Cargo.toml")
    if cargo.get("workspace", {}).get("package", {}).get("version") != version:
        raise RecoveryError(f"{label} Cargo workspace version is not synchronized")

    lock = _parse_toml_text(files["Cargo.lock"], f"{label} Cargo.lock")
    packages = lock.get("package")
    if not isinstance(packages, list):
        raise RecoveryError(f"{label} Cargo.lock has no complete package list")
    lock_versions = {
        package.get("name"): package.get("version")
        for package in packages
        if isinstance(package, dict)
    }
    if any(lock_versions.get(crate) != version for crate in runtime_crates):
        raise RecoveryError(f"{label} Cargo.lock versions are not synchronized")

    for crate in runtime_crates:
        path = f"crates/{crate}/Cargo.toml"
        package = _parse_toml_text(files[path], f"{label} {path}").get("package", {})
        if package.get("name") != crate or package.get("version") != version:
            raise RecoveryError(f"{label} Cargo manifest version drift for {crate}")

    conformance = _parse_toml_text(
        files["crates/codegauge-conformance/Cargo.toml"],
        f"{label} conformance manifest",
    )
    conformance_package = conformance.get("package", {})
    if (
        conformance_package.get("name") != "codegauge-conformance"
        or conformance_package.get("version") != "0.1.0"
        or conformance_package.get("publish") is not False
    ):
        raise RecoveryError(f"{label} conformance package boundary drifted")
    dependencies = conformance.get("dependencies", {})
    if not isinstance(dependencies, dict):
        raise RecoveryError(f"{label} conformance dependencies are malformed")
    for crate in tuple(crate for crate in runtime_crates if crate != "codegauge-cli"):
        dependency = dependencies.get(crate)
        if (
            not isinstance(dependency, dict)
            or dependency.get("version") != version
            or dependency.get("path") != f"../{crate}"
        ):
            raise RecoveryError(f"{label} conformance dependency drift for {crate}")

    base = _parse_json_text(files["npm/codegauge/package.json"], f"{label} npm wrapper")
    if base.get("name") != "@yacosta738/codegauge" or base.get("version") != version:
        raise RecoveryError(f"{label} npm wrapper version is not synchronized")
    optional = base.get("optionalDependencies")
    if not isinstance(optional, dict) or set(optional) != set(NPM_PLATFORM_PACKAGES):
        raise RecoveryError(f"{label} npm platform graph is incomplete")
    if any(optional.get(package) != version for package in NPM_PLATFORM_PACKAGES):
        raise RecoveryError(f"{label} npm platform pins are not synchronized")
    for package in NPM_PLATFORM_PACKAGES:
        package_path = f"npm/packages/{package.removeprefix('@yacosta738/')}/package.json"
        document = _parse_json_text(files[package_path], f"{label} {package}")
        if document.get("name") != package or document.get("version") != version:
            raise RecoveryError(f"{label} npm package version drift for {package}")

    _validate_dockerfile(files[DOCKERFILE_PATH], label)


class GitHubRecoveryAdapter:
    """Adapter with strict response parsing and no publication endpoints."""

    def __init__(self, transport: HttpTransport, repository: str) -> None:
        if not isinstance(repository, str) or not REPOSITORY_RE.fullmatch(repository):
            raise RecoveryError("repository must be owner/name")
        self.transport = transport
        self.repository = repository

    def _get(self, path: str, label: str) -> ApiResponse:
        response = self.transport.request("GET", path)
        if response.status == 404:
            return response
        if response.status != 200:
            raise RecoveryError(f"{label} API request failed with HTTP {response.status}")
        if parse_link_next(response.headers.get("Link")) is not None:
            raise RecoveryError(f"{label} response uses unsupported pagination")
        _object(response.body, label)
        return response

    def _get_required(self, path: str, label: str) -> dict[str, Any]:
        response = self._get(path, label)
        return _response_object(response, label)

    def _file(self, path: str, ref: str) -> str:
        response = self._get(
            f"/repos/{self.repository}/contents/{path}?ref={ref}",
            f"{path} file response",
        )
        return _decode_text_file(_response_object(response, f"{path} file response"), path, ref)

    def _commit_tree(self, commit_sha: str, expected_tree: str, label: str) -> dict[str, dict[str, Any]]:
        commit = self._get_required(
            f"/repos/{self.repository}/commits/{commit_sha}", label
        )
        if commit.get("sha") != commit_sha:
            raise RecoveryError(f"{label} SHA does not match the requested commit")
        commit_details = _object(commit.get("commit"), f"{label} commit details")
        tree = _object(commit_details.get("tree"), f"{label} tree")
        if tree.get("sha") != expected_tree:
            raise RecoveryError(f"{label} tree does not match the requested immutable tree")
        tree_response = self._get_required(
            f"/repos/{self.repository}/git/trees/{expected_tree}?recursive=1",
            f"{label} contents",
        )
        if tree_response.get("sha") != expected_tree:
            raise RecoveryError(f"{label} contents are not scoped to the requested tree")
        if tree_response.get("truncated") is not False:
            raise RecoveryError(f"{label} contents are truncated")
        entries = tree_response.get("tree")
        if not isinstance(entries, list) or not entries:
            raise RecoveryError(f"{label} contents are incomplete")
        indexed: dict[str, dict[str, Any]] = {}
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise RecoveryError(f"{label} entry {index} is malformed")
            path = entry.get("path")
            entry_type = entry.get("type")
            entry_sha = entry.get("sha")
            if (
                not isinstance(path, str)
                or not path
                or path.startswith("/")
                or "\\" in path
                or ".." in path.split("/")
                or path in indexed
                or entry_type not in {"blob", "tree"}
                or not isinstance(entry_sha, str)
                or not SHA_RE.fullmatch(entry_sha)
            ):
                raise RecoveryError(f"{label} contains an invalid or duplicate tree entry")
            indexed[path] = entry
        return indexed

    def _historical_manifest(
        self,
        entries: dict[str, dict[str, Any]],
        request: RecoveryRequest,
    ) -> tuple[dict[str, str], str]:
        manifest_entry = entries.get(HISTORICAL_MANIFEST_PATH)
        if not manifest_entry or manifest_entry.get("type") != "blob":
            raise RecoveryError("historical manifest is missing from the immutable tree")
        blob_sha = manifest_entry["sha"]
        blob = self._get_required(
            f"/repos/{self.repository}/git/blobs/{blob_sha}",
            "historical manifest blob",
        )
        if blob.get("sha") != blob_sha:
            raise RecoveryError("historical manifest blob SHA does not match the tree")
        try:
            text = _decode_base64_content(blob, "historical manifest blob").decode("utf-8")
            manifest_value = json.loads(text)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RecoveryError("historical manifest contents are malformed JSON") from error
        manifest = _validate_manifest(
            manifest_value,
            expected_paths=HISTORICAL_GRAPH_PATHS,
            version=request.version,
            label="historical manifest",
        )
        digest = hashlib.sha256(_canonical_json(manifest).encode()).hexdigest()
        if digest != request.historical_manifest:
            raise RecoveryError("historical manifest digest does not match the request")
        return manifest, digest

    def _version_file_paths(self, runtime_crates: tuple[str, ...]) -> tuple[str, ...]:
        return (
            "Cargo.toml",
            "Cargo.lock",
            DOCKERFILE_PATH,
            "crates/codegauge-conformance/Cargo.toml",
            *(f"crates/{crate}/Cargo.toml" for crate in runtime_crates),
            "npm/codegauge/package.json",
            *(
                f"npm/packages/{package.removeprefix('@yacosta738/')}/package.json"
                for package in NPM_PLATFORM_PACKAGES
            ),
        )

    def _version_files(self, ref: str, runtime_crates: tuple[str, ...]) -> dict[str, str]:
        return {
            path: self._file(path, ref)
            for path in self._version_file_paths(runtime_crates)
        }

    def preflight(self, request: RecoveryRequest) -> RecoveryPreflight:
        """Resolve every release identity and compatibility input before any POST."""

        if request.repository != self.repository:
            raise RecoveryError("request repository does not match the trusted adapter repository")
        if request.default_branch != EXPECTED_DEFAULT_BRANCH:
            raise RecoveryError("recovery is restricted to the protected main branch")
        if request.pull_request != EXPECTED_PULL_REQUEST:
            raise RecoveryError(
                f"recovery requires the historical merged PR #{EXPECTED_PULL_REQUEST}"
            )
        if tuple(request.artifact_plan) != RECOVERY_ARTIFACT_PLAN:
            raise RecoveryError("recovery artifact plan is not the canonical tag-then-release plan")

        repository = self._get_required(
            f"/repos/{self.repository}", "repository identity response"
        )
        if repository.get("full_name") != self.repository:
            raise RecoveryError("repository identity response does not match the trusted repository")
        if repository.get("default_branch") != request.default_branch:
            raise RecoveryError("repository default branch does not match the request")

        pull = self._get_required(
            f"/repos/{self.repository}/pulls/{request.pull_request}",
            "merged release pull request response",
        )
        if pull.get("number") != request.pull_request:
            raise RecoveryError("merged release pull request number does not match the request")
        if pull.get("state") != "closed" or pull.get("merged") is not True:
            raise RecoveryError("historical release pull request is not merged")
        if not isinstance(pull.get("merged_at"), str) or not pull["merged_at"]:
            raise RecoveryError("historical release pull request has no merge timestamp")
        base = _object(pull.get("base"), "merged release pull request base")
        if base.get("ref") != request.default_branch:
            raise RecoveryError("historical release pull request targets the wrong branch")
        base_repo = _object(base.get("repo"), "merged release pull request base repository")
        if base_repo.get("full_name") != self.repository:
            raise RecoveryError("historical release pull request targets the wrong repository")
        if pull.get("merge_commit_sha") != request.merged_sha:
            raise RecoveryError("merged release pull request SHA does not match the request")

        historical_entries = self._commit_tree(
            request.merged_sha,
            request.historical_tree,
            "historical merged commit",
        )
        historical_manifest, _ = self._historical_manifest(historical_entries, request)
        historical_files = self._version_files(
            request.merged_sha,
            HISTORICAL_RUNTIME_CRATES,
        )
        _validate_version_files(
            historical_files,
            version=request.version,
            runtime_crates=HISTORICAL_RUNTIME_CRATES,
            label="historical snapshot",
        )

        branch_ref = self._get_required(
            f"/repos/{self.repository}/git/ref/heads/{request.default_branch}",
            "default branch reference",
        )
        if branch_ref.get("ref") != f"refs/heads/{request.default_branch}":
            raise RecoveryError("default branch reference is not scoped to main")
        branch_object = _object(branch_ref.get("object"), "default branch reference object")
        current_sha = branch_object.get("sha")
        if branch_object.get("type") != "commit" or not isinstance(current_sha, str) or not SHA_RE.fullmatch(current_sha):
            raise RecoveryError("default branch reference does not resolve to a commit")
        current_commit = self._get_required(
            f"/repos/{self.repository}/commits/{current_sha}",
            "current default branch commit",
        )
        if current_commit.get("sha") != current_sha:
            raise RecoveryError("current default branch commit SHA does not match the reference")
        current_details = _object(
            current_commit.get("commit"),
            "current default branch commit details",
        )
        current_tree_object = _object(
            current_details.get("tree"),
            "current default branch tree",
        )
        current_tree_sha = current_tree_object.get("sha")
        if not isinstance(current_tree_sha, str) or not SHA_RE.fullmatch(current_tree_sha):
            raise RecoveryError("current default branch tree SHA is malformed")
        self._commit_tree(
            current_sha,
            expected_tree=current_tree_sha,
            label="current default branch",
        )
        current_manifest_text = self._file(
            HISTORICAL_MANIFEST_PATH,
            current_sha,
        )
        current_manifest = _validate_manifest(
            _parse_json_text(current_manifest_text, "current release manifest"),
            expected_paths=CURRENT_GRAPH_PATHS,
            version=request.version,
            label="current release graph",
        )
        if not HISTORICAL_GRAPH_PATHS.issubset(set(current_manifest)):
            raise RecoveryError("current release graph is not compatible with the historical snapshot")
        current_files = self._version_files(current_sha, CURRENT_RUNTIME_CRATES)
        _validate_version_files(
            current_files,
            version=request.version,
            runtime_crates=CURRENT_RUNTIME_CRATES,
            label="current graph",
        )
        current_manifest_digest = hashlib.sha256(
            _canonical_json(current_manifest).encode()
        ).hexdigest()
        snapshot = self.snapshot(request)
        return RecoveryPreflight(
            repository=self.repository,
            default_branch=request.default_branch,
            pull_request=request.pull_request,
            merged_sha=request.merged_sha,
            historical_tree=request.historical_tree,
            historical_manifest=request.historical_manifest,
            historical_entry_count=len(historical_manifest),
            current_entry_count=len(current_manifest),
            graph_mismatch=set(historical_manifest) != set(current_manifest),
            artifact_plan=RECOVERY_ARTIFACT_PLAN,
            current_manifest_digest=current_manifest_digest,
            snapshot=snapshot,
        )

    def snapshot(self, request: RecoveryRequest) -> ResourceSnapshot:
        if request.repository != self.repository:
            raise RecoveryError("request repository does not match adapter repository")
        tag_response = self._get(
            f"/repos/{self.repository}/git/ref/tags/{request.tag}", "tag response"
        )
        release_response = self._get(
            f"/repos/{self.repository}/releases/tags/{request.tag}", "release response"
        )
        tag_exists = tag_response.status != 404
        release_exists = release_response.status != 404
        tag_sha: str | None = None
        tag_type: str | None = None
        if tag_exists:
            tag = _object(tag_response.body, "tag response")
            if tag.get("ref") != f"refs/tags/{request.tag}":
                raise RecoveryError("tag response is not scoped to the requested tag")
            target = _object(tag.get("object"), "tag response object")
            tag_sha = target.get("sha")
            tag_type = target.get("type")
            if not isinstance(tag_sha, str) or not SHA_RE.fullmatch(tag_sha):
                raise RecoveryError("tag response contains an invalid SHA")
            if tag_type != "commit":
                raise RecoveryError("tag response must resolve to a commit")
            if tag_sha != request.merged_sha:
                raise RecoveryError("canonical tag has a conflicting SHA")
        release_tag: str | None = None
        release_sha: str | None = None
        release_version: str | None = None
        release_draft: bool | None = None
        release_body_digest: str | None = None
        release_id: int | None = None
        if release_exists:
            release = _object(release_response.body, "release response")
            release_id = release.get("id")
            if not isinstance(release_id, int) or isinstance(release_id, bool) or release_id <= 0:
                raise RecoveryError("release response id is malformed")
            release_tag = release.get("tag_name")
            release_sha = release.get("target_commitish")
            if release_tag != request.tag:
                raise RecoveryError("release response is not scoped to the requested tag")
            if not isinstance(release_sha, str) or not SHA_RE.fullmatch(release_sha):
                raise RecoveryError("release response contains an invalid SHA")
            if release_sha != request.merged_sha:
                raise RecoveryError("canonical release has a conflicting SHA")
            release_version = release.get("release_version")
            if release_version is not None and not isinstance(release_version, str):
                raise RecoveryError("release response version is malformed")
            release_draft = release.get("draft")
            if not isinstance(release_draft, bool):
                raise RecoveryError("release response draft field is malformed")
            body = release.get("body")
            if not isinstance(body, str):
                raise RecoveryError("release response body is malformed")
            release_body_digest = hashlib.sha256(body.encode()).hexdigest()
        return ResourceSnapshot(
            tag_exists=tag_exists,
            tag_sha=tag_sha,
            tag_type=tag_type,
            release_exists=release_exists,
            release_tag=release_tag,
            release_sha=release_sha,
            release_version=release_version,
            release_draft=release_draft,
            release_body_digest=release_body_digest,
            release_id=release_id,
        )

    def create_tag(self, request: RecoveryRequest) -> None:
        response = self.transport.request(
            "POST",
            f"/repos/{self.repository}/git/refs",
            {"ref": f"refs/tags/{request.tag}", "sha": request.merged_sha},
        )
        if response.status not in {201, 422}:
            raise RecoveryError(f"canonical tag creation failed with HTTP {response.status}")
        if response.status == 201:
            _object(response.body, "tag creation response")

    def create_release(self, request: RecoveryRequest) -> None:
        response = self.transport.request(
            "POST",
            f"/repos/{self.repository}/releases",
            {
                "tag_name": request.tag,
                "target_commitish": request.merged_sha,
                "name": request.tag,
                "body": f"Historical release recovery for {request.version}.\n\nSource SHA: {request.merged_sha}\nSource PR: #{request.pull_request}",
                "draft": False,
                "prerelease": False,
            },
        )
        if response.status not in {201, 422}:
            raise RecoveryError(f"GitHub Release creation failed with HTTP {response.status}")
        if response.status == 201:
            _object(response.body, "release creation response")
