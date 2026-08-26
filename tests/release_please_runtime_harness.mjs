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
const { mergeUpdates } = require(
  path.join(releasePleaseRoot, "build/src/updaters/composite.js"),
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
const currentReleaseVersion = manifestVersions["."];

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
    const effectiveUpdates = [];
    for (const update of mergeUpdates(updates)) {
      const absolutePath = path.join(repositoryRoot, update.path);
      const exists = fs.existsSync(absolutePath);
      if (!exists && !update.createIfMissing) {
        continue;
      }
      const originalContent = exists
        ? fs.readFileSync(absolutePath, "utf8")
        : undefined;
      const updatedContent = update.updater.updateContent(originalContent);
      if (updatedContent) {
        effectiveUpdates.push(update);
      }
    }
    this.pullRequestCreates.push({ pullRequest, updates: effectiveUpdates });
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
const privateManifestPath = "crates/codegauge-conformance/Cargo.toml";
const privateCandidatePaths = updates
  .map((update) => update.path)
  .filter((updatePath) => updatePath.startsWith("crates/codegauge-conformance/"));
const privateUpdates = updates.filter((update) => update.path === privateManifestPath);
if (
  privateCandidatePaths.length !== privateUpdates.length ||
  privateUpdates.length !== 1 ||
  privateCandidatePaths.some((updatePath) => updatePath !== privateManifestPath)
) {
  throw new Error(
    `Stage-A private update set is not exactly one conformance dependency update containing five pin edits: ${privateCandidatePaths.join(", ")}`,
  );
}
const expectedRootPaths = new Set([
  "Cargo.toml",
  "Cargo.lock",
  ".release-please-manifest.json",
  "README.md",
  "tests/golden/valid-methods.json",
  "tests/golden/typescript-valid.json",
  "crates/codegauge-model/tests/contracts.rs",
  "crates/codegauge-cli/tests/cli.rs",
  privateManifestPath,
]);
const expectedRuntimeChangelogs = new Set([
  ...[
    "codegauge-model",
    "codegauge-core",
    "codegauge-application",
    "codegauge-provider-jacoco",
    "codegauge-provider-typescript",
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
    "codegauge-provider-typescript",
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
if (generatedPaths.size !== 35) {
  throw new Error(
    `expected the exact 35-path Stage-A effective update set, got ${generatedPaths.size}`,
  );
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
for (const goldenPath of [
  "tests/golden/valid-methods.json",
  "tests/golden/typescript-valid.json",
]) {
  const goldenUpdate = updates.find((update) => update.path === goldenPath);
  if (!goldenUpdate) {
    throw new Error(`the typed golden JSON updater was not generated for ${goldenPath}`);
  }
  const goldenBefore = JSON.parse(
    fs.readFileSync(path.join(repositoryRoot, goldenPath), "utf8"),
  );
  const goldenAfter = JSON.parse(
    goldenUpdate.updater.updateContent(
      fs.readFileSync(path.join(repositoryRoot, goldenPath), "utf8"),
    ),
  );
  const expectedGolden = structuredClone(goldenBefore);
  expectedGolden.tool.version = releaseVersion;
  if (JSON.stringify(goldenAfter) !== JSON.stringify(expectedGolden)) {
    throw new Error(
      `typed golden updater changed more than $.tool.version or kept the wrong version for ${goldenPath}: ${JSON.stringify(goldenAfter.tool)}`,
    );
  }
}

function assertAnnotatedVersionUpdater(updatePath, expectedLines) {
  const update = updates.find((candidate) => candidate.path === updatePath);
  if (!update) {
    throw new Error(`annotated root updater was not generated: ${updatePath}`);
  }
  const before = fs.readFileSync(path.join(repositoryRoot, updatePath), "utf8");
  const after = update.updater.updateContent(before);
  if (after === before) {
    throw new Error(`annotated root updater made no version substitutions: ${updatePath}`);
  }
  const beforeLines = before.split("\n");
  const afterLines = after.split("\n");
  const changed = beforeLines.flatMap((line, index) =>
    line === afterLines[index] ? [] : [[line, afterLines[index]]],
  );
  if (changed.length !== expectedLines) {
    throw new Error(
      `annotated updater changed ${changed.length} lines in ${updatePath}; expected ${expectedLines}`,
    );
  }
  for (const [oldLine, newLine] of changed) {
    if (
      !oldLine.includes("x-release-please-version") ||
      !newLine.includes("x-release-please-version") ||
       oldLine.replaceAll(currentReleaseVersion, releaseVersion) !== newLine
    ) {
      throw new Error(
        `annotated updater changed an unexpected line in ${updatePath}: ${JSON.stringify([oldLine, newLine])}`,
      );
    }
  }
}

assertAnnotatedVersionUpdater("README.md", 4);
assertAnnotatedVersionUpdater("crates/codegauge-model/tests/contracts.rs", 2);
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
  "codegauge-provider-typescript",
  "codegauge-cli",
]) {
  if (lockVersion(crate) !== releaseVersion) {
    throw new Error(`Cargo.lock carrier did not update runtime crate ${crate}`);
  }
}
if (lockVersion("codegauge-conformance") !== "0.1.0") {
  throw new Error("Cargo.lock carrier mutated the private conformance package");
}

const privateManifestPathOnDisk = path.join(repositoryRoot, privateManifestPath);
const privateBefore = fs.readFileSync(privateManifestPathOnDisk, "utf8");
const privateAfter = privateUpdates.reduce(
  (contents, update) => update.updater.updateContent(contents),
  privateBefore,
);
if (!/^version = "0\.1\.0"$/m.test(privateAfter)) {
  throw new Error("private conformance package version was changed");
}
if (!/^name = "codegauge-conformance"$/m.test(privateAfter)) {
  throw new Error("private conformance package identity was changed");
}
if (!/^publish = false$/m.test(privateAfter)) {
  throw new Error("private conformance publish=false boundary was changed");
}
for (const dependency of [
  "codegauge-application",
  "codegauge-core",
  "codegauge-model",
  "codegauge-provider-jacoco",
  "codegauge-provider-typescript",
]) {
  const dependencyPattern = new RegExp(
    `${dependency} = \\{ version = "${releaseVersion}", path = "../${dependency}" \\}`,
  );
  if (!dependencyPattern.test(privateAfter)) {
    throw new Error(`private dependency pin was not synchronized: ${dependency}`);
  }
}
const privateBeforeLines = privateBefore.split("\n");
const privateAfterLines = privateAfter.split("\n");
const changedPrivatePairs = privateBeforeLines.flatMap((beforeLine, index) => {
  const afterLine = privateAfterLines[index];
  return beforeLine === afterLine ? [] : [[beforeLine, afterLine]];
});
const expectedPrivatePairs = new Set(
  [
    "codegauge-application",
    "codegauge-core",
    "codegauge-model",
    "codegauge-provider-jacoco",
    "codegauge-provider-typescript",
  ].map((dependency) =>
    JSON.stringify([
      `${dependency} = { version = "${currentReleaseVersion}", path = "../${dependency}" }`,
      `${dependency} = { version = "${releaseVersion}", path = "../${dependency}" }`,
    ]),
  ),
);
if (
  changedPrivatePairs.length !== 5 ||
  changedPrivatePairs.some((pair) => !expectedPrivatePairs.has(JSON.stringify(pair)))
) {
  throw new Error(
    `private conformance updater changed unexpected lines: ${JSON.stringify(changedPrivatePairs)}`,
  );
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
  "crates/codegauge-provider-typescript/Cargo.toml": [
    "codegauge-application",
    "codegauge-model",
  ],
  "crates/codegauge-cli/Cargo.toml": [
    "codegauge-application",
    "codegauge-model",
    "codegauge-provider-jacoco",
    "codegauge-provider-typescript",
  ],
};
for (const [manifestPath, packageName] of Object.entries({
  "crates/codegauge-model/Cargo.toml": "codegauge-model",
  "crates/codegauge-core/Cargo.toml": "codegauge-core",
  "crates/codegauge-application/Cargo.toml": "codegauge-application",
  "crates/codegauge-provider-jacoco/Cargo.toml": "codegauge-provider-jacoco",
  "crates/codegauge-provider-typescript/Cargo.toml": "codegauge-provider-typescript",
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
      privateDependencyUpdates: privateUpdates.length,
      synchronizedPullRequests: scm.pullRequestCreates.length,
      releaseCalls: scm.releaseCalls.length,
      tagCalls: scm.tagCalls.length,
    },
    null,
    2,
  ),
);
console.log("RELEASE PLEASE V17.6.0 RUNTIME TESTS: PASS");
