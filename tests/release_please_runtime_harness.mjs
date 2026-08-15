#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const repositoryRoot = path.resolve(process.env.CODEGAUGE_ROOT);
const releasePleaseRoot = path.resolve(process.env.RELEASE_PLEASE_17_6_0_ROOT);
const releasePleasePackage = JSON.parse(
  fs.readFileSync(path.join(releasePleaseRoot, "package.json"), "utf8"),
);

if (releasePleasePackage.version !== "17.6.0") {
  throw new Error(
    `expected release-please 17.6.0, found ${releasePleasePackage.version}`,
  );
}

const { Manifest } = require(
  path.join(releasePleaseRoot, "build/src/manifest.js"),
);
const { Version } = require(
  path.join(releasePleaseRoot, "build/src/version.js"),
);

const config = JSON.parse(
  fs.readFileSync(path.join(repositoryRoot, "release-please-config.json"), "utf8"),
);
const manifestVersions = JSON.parse(
  fs.readFileSync(
    path.join(repositoryRoot, ".release-please-manifest.json"),
    "utf8",
  ),
);

const runtimePaths = Object.keys(manifestVersions);
const bootstrapSha = "b".repeat(40);
const commitSha = "c".repeat(40);

function effectiveConfig(packageConfig) {
  const value = (key, fallbackKey = key) =>
    packageConfig[key] ?? config[fallbackKey];
  return {
    releaseType: value("release-type"),
    component: packageConfig.component,
    packageName: packageConfig["package-name"],
    skipGithubRelease: value("skip-github-release"),
    skipChangelog: value("skip-changelog"),
    includeComponentInTag: value("include-component-in-tag"),
    extraFiles: packageConfig["extra-files"],
    initialVersion: packageConfig["initial-version"],
    skipSnapshot: packageConfig["skip-snapshot"],
    changelogPath: packageConfig["changelog-path"],
  };
}

const repositoryConfig = Object.fromEntries(
  Object.entries(config.packages).map(([releasePath, packageConfig]) => [
    releasePath,
    effectiveConfig(packageConfig),
  ]),
);

class ReadOnlyFakeScm {
  repository = {
    owner: "yacosta738",
    repo: "codegauge",
    defaultBranch: "main",
  };

  pullRequestCreates = [];
  releaseCalls = [];
  tagCalls = [];
  mutationCalls = [];

  async getFileContentsOnBranch(filePath, _branch) {
    const relativePath = filePath.replace(/^\/+/, "");
    const absolutePath = path.join(repositoryRoot, relativePath);
    if (!fs.statSync(absolutePath).isFile()) {
      throw new Error(`fake SCM file is missing: ${relativePath}`);
    }
    return {
      name: relativePath,
      path: relativePath,
      parsedContent: fs.readFileSync(absolutePath, "utf8"),
      sha: "d".repeat(40),
    };
  }

  async findFilesByGlobAndRef(glob, _ref, _prefix) {
    return [glob];
  }

  async *releaseIterator() {}

  async *tagIterator() {}

  async *pullRequestIterator() {}

  async *mergeCommitIterator() {
    yield {
      sha: commitSha,
      message: "feat: exercise the complete runtime release graph",
      files: [],
      pullRequest: undefined,
    };
    yield {
      sha: bootstrapSha,
      message: "chore: bootstrap",
      files: [],
      pullRequest: undefined,
    };
  }

  async createPullRequest(pullRequest, _targetBranch, _message, updates) {
    this.pullRequestCreates.push({ pullRequest, updates });
    return {
      ...pullRequest,
      number: 9001,
      sha: commitSha,
    };
  }

  async updatePullRequest() {
    this.mutationCalls.push("updatePullRequest");
    throw new Error("unexpected updatePullRequest call");
  }

  async createRelease(release) {
    this.releaseCalls.push(release);
    throw new Error("unexpected createRelease call");
  }

  async createTag(tag) {
    this.tagCalls.push(tag);
    throw new Error("unexpected createTag call");
  }

  async commentOnIssue() {
    this.mutationCalls.push("commentOnIssue");
    throw new Error("unexpected commentOnIssue call");
  }

  async removeIssueLabels() {
    this.mutationCalls.push("removeIssueLabels");
    throw new Error("unexpected removeIssueLabels call");
  }

  async addIssueLabels() {
    this.mutationCalls.push("addIssueLabels");
    throw new Error("unexpected addIssueLabels call");
  }
}

const scm = new ReadOnlyFakeScm();
const releasedVersions = Object.fromEntries(
  runtimePaths.map((releasePath) => [
    releasePath,
    Version.parse(manifestVersions[releasePath]),
  ]),
);
const manifest = new Manifest(
  scm,
  "main",
  repositoryConfig,
  releasedVersions,
  {
    bootstrapSha,
    plugins: config.plugins,
    separatePullRequests: false,
    labels: ["autorelease: pending"],
    sequentialCalls: true,
  },
);

const pullRequests = await manifest.createPullRequests();
if (pullRequests.length !== 1 || scm.pullRequestCreates.length !== 1) {
  throw new Error(
    `expected one synchronized Stage-A PR, got ${pullRequests.length} results and ${scm.pullRequestCreates.length} fake creates`,
  );
}

if (scm.releaseCalls.length !== 0 || scm.tagCalls.length !== 0) {
  throw new Error(
    `Stage A called release/tag operations: releases=${scm.releaseCalls.length}, tags=${scm.tagCalls.length}`,
  );
}
if (scm.mutationCalls.length !== 0) {
  throw new Error(`Stage A made unexpected SCM mutations: ${scm.mutationCalls}`);
}

const updates = scm.pullRequestCreates[0].updates;
const generatedPaths = new Set(updates.map((update) => update.path));
const privateCandidatePaths = updates
  .map((update) => update.path)
  .filter((updatePath) => updatePath.startsWith("crates/codegauge-conformance/"));
if (privateCandidatePaths.length !== 0) {
  throw new Error(
    `Stage-A update set contains private conformance candidates: ${privateCandidatePaths.join(", ")}`,
  );
}
const expectedRootPaths = new Set([
  "Cargo.toml",
  "Cargo.lock",
  ".release-please-manifest.json",
  "README.md",
  "tests/golden/valid-methods.json",
  "crates/codegauge-model/tests/contracts.rs",
  "crates/codegauge-cli/tests/cli.rs",
]);
const expectedRuntimeChangelogs = new Set([
  ...[
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-cli",
  ].map((crate) => `crates/${crate}/CHANGELOG.md`),
  "npm/codegauge/CHANGELOG.md",
  ...[
    "codegauge-linux-x64-gnu",
    "codegauge-linux-arm64-gnu",
    "codegauge-darwin-x64",
    "codegauge-darwin-arm64",
    "codegauge-win32-x64-msvc",
    "codegauge-win32-arm64-msvc",
  ].map((pkg) => `npm/packages/${pkg}/CHANGELOG.md`),
]);
const expectedPackagePaths = new Set([
  "npm/codegauge/package.json",
  ...[
    "codegauge-linux-x64-gnu",
    "codegauge-linux-arm64-gnu",
    "codegauge-darwin-x64",
    "codegauge-darwin-arm64",
    "codegauge-win32-x64-msvc",
    "codegauge-win32-arm64-msvc",
  ].map((pkg) => `npm/packages/${pkg}/package.json`),
  ...[
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-cli",
  ].map((crate) => `crates/${crate}/Cargo.toml`),
]);

for (const expectedPath of [
  ...expectedRootPaths,
  ...expectedRuntimeChangelogs,
  ...expectedPackagePaths,
]) {
  if (!generatedPaths.has(expectedPath)) {
    throw new Error(`exact Release Please chain omitted update path: ${expectedPath}`);
  }
}

const optionalDependencyUpdate = updates.find(
  (update) => update.path === "npm/codegauge/package.json",
);
if (!optionalDependencyUpdate) {
  throw new Error("the exact chain did not generate the base npm package update");
}
const basePackagePath = path.join(repositoryRoot, "npm/codegauge/package.json");
const rewrittenBase = JSON.parse(
  optionalDependencyUpdate.updater.updateContent(
    fs.readFileSync(basePackagePath, "utf8"),
  ),
);
const releaseVersion = rewrittenBase.version;
const optionalVersions = Object.values(rewrittenBase.optionalDependencies ?? {});
if (
  optionalVersions.length !== 6 ||
  optionalVersions.some((version) => version !== releaseVersion)
) {
  throw new Error(
    `linked optional dependency rewrites are incomplete: ${JSON.stringify(rewrittenBase.optionalDependencies)}`,
  );
}

const cargoLockUpdate = updates.find((update) => update.path === "Cargo.lock");
if (!cargoLockUpdate) {
  throw new Error("the explicit runtime Cargo carrier did not generate Cargo.lock");
}
const rewrittenCargoLock = cargoLockUpdate.updater.updateContent(
  fs.readFileSync(path.join(repositoryRoot, "Cargo.lock"), "utf8"),
);
const lockVersion = (packageName) => {
  const escapedName = packageName.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const match = rewrittenCargoLock.match(
    new RegExp(`name = "${escapedName}"\\nversion = "([^"]+)"`),
  );
  return match?.[1];
};
for (const crate of [
  "codegauge-model",
  "codegauge-core",
  "codegauge-application",
  "codegauge-provider-jacoco",
  "codegauge-cli",
]) {
  if (lockVersion(crate) !== releaseVersion) {
    throw new Error(`Cargo.lock carrier did not update runtime crate ${crate}`);
  }
}
if (lockVersion("codegauge-conformance") !== "0.1.0") {
  throw new Error("Cargo.lock carrier mutated the private conformance package");
}

const runtimeCargoDependencies = {
  "crates/codegauge-core/Cargo.toml": ["codegauge-model"],
  "crates/codegauge-application/Cargo.toml": [
    "codegauge-core",
    "codegauge-model",
  ],
  "crates/codegauge-provider-jacoco/Cargo.toml": [
    "codegauge-application",
    "codegauge-model",
  ],
  "crates/codegauge-cli/Cargo.toml": [
    "codegauge-application",
    "codegauge-model",
    "codegauge-provider-jacoco",
  ],
};
for (const [manifestPath, packageName] of Object.entries({
  "crates/codegauge-model/Cargo.toml": "codegauge-model",
  "crates/codegauge-core/Cargo.toml": "codegauge-core",
  "crates/codegauge-application/Cargo.toml": "codegauge-application",
  "crates/codegauge-provider-jacoco/Cargo.toml": "codegauge-provider-jacoco",
  "crates/codegauge-cli/Cargo.toml": "codegauge-cli",
})) {
  const manifestUpdate = updates.find((update) => update.path === manifestPath);
  const rewrittenManifest = manifestUpdate?.updater.updateContent(
    fs.readFileSync(path.join(repositoryRoot, manifestPath), "utf8"),
  );
  if (
    !rewrittenManifest ||
    !new RegExp(`name = "${packageName}"\\nversion = "${releaseVersion}"`).test(
      rewrittenManifest,
    )
  ) {
    throw new Error(`runtime Cargo package was not synchronized: ${manifestPath}`);
  }
}
for (const [manifestPath, dependencies] of Object.entries(runtimeCargoDependencies)) {
  const manifestUpdate = updates.find((update) => update.path === manifestPath);
  if (!manifestUpdate) {
    throw new Error(`explicit runtime package omitted Cargo manifest update: ${manifestPath}`);
  }
  const rewrittenManifest = manifestUpdate.updater.updateContent(
    fs.readFileSync(path.join(repositoryRoot, manifestPath), "utf8"),
  );
  for (const dependency of dependencies) {
    const escapedDependency = dependency.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    if (
      !new RegExp(
        `${escapedDependency} = \\{ version = "${releaseVersion}",`,
      ).test(rewrittenManifest)
    ) {
      throw new Error(
        `runtime Cargo dependency ${dependency} was not synchronized in ${manifestPath}`,
      );
    }
  }
}

for (const changelogPath of expectedRuntimeChangelogs) {
  const changelogUpdate = updates.find((update) => update.path === changelogPath);
  if (!changelogUpdate?.createIfMissing) {
    throw new Error(`runtime changelog is not an exact generated update: ${changelogPath}`);
  }
}

console.log(
  JSON.stringify(
    {
      packageVersion: releasePleasePackage.version,
      generatedUpdatePaths: [...generatedPaths].sort(),
      releaseVersion,
      optionalDependencyVersions: rewrittenBase.optionalDependencies,
      synchronizedPullRequests: scm.pullRequestCreates.length,
      releaseCalls: scm.releaseCalls.length,
      tagCalls: scm.tagCalls.length,
    },
    null,
    2,
  ),
);
console.log("RELEASE PLEASE V17.6.0 RUNTIME TESTS: PASS");
