import { createHash } from "node:crypto";
import { createReadStream, existsSync, readFileSync, statSync } from "node:fs";
import { basename, join } from "node:path";

export interface ReleaseArchive {
  readonly archivePath: string;
  readonly checksumPath: string;
  readonly manifestPath: string;
  readonly archiveName: string;
  readonly target: string;
}

export interface PlatformArtifact {
  readonly packageName: string;
  readonly packageJsonPath: string;
  readonly binaryPath: string;
  readonly binaryName: string;
  readonly archive: ReleaseArchive;
  readonly expectedOs: string;
  readonly expectedCpu: string;
  readonly requiresExecutable: boolean;
}

export interface NpmPublicationPreflight {
  readonly releaseVersion: string;
  readonly sourceRevision: string;
  readonly basePackageJsonPath: string;
  readonly platformArtifacts: readonly PlatformArtifact[];
}

export interface NpmPublicationEligibility {
  readonly platformEligible: boolean;
  readonly baseEligible: boolean;
  readonly failures: readonly string[];
}

interface JsonObject {
  readonly [key: string]: unknown;
}

interface NpmTarget {
  readonly packageDirectory: string;
  readonly packageName: string;
  readonly target: string;
  readonly archiveExtension: "tar.gz" | "zip";
  readonly os: string;
  readonly cpu: string;
  readonly binaryName: string;
  readonly requiresExecutable: boolean;
}

const NPM_TARGETS: readonly NpmTarget[] = [
  {
    packageDirectory: "codegauge-linux-x64-gnu",
    packageName: "@yacosta738/codegauge-linux-x64-gnu",
    target: "x86_64-unknown-linux-gnu",
    archiveExtension: "tar.gz",
    os: "linux",
    cpu: "x64",
    binaryName: "codegauge",
    requiresExecutable: true,
  },
  {
    packageDirectory: "codegauge-linux-arm64-gnu",
    packageName: "@yacosta738/codegauge-linux-arm64-gnu",
    target: "aarch64-unknown-linux-gnu",
    archiveExtension: "tar.gz",
    os: "linux",
    cpu: "arm64",
    binaryName: "codegauge",
    requiresExecutable: true,
  },
  {
    packageDirectory: "codegauge-darwin-x64",
    packageName: "@yacosta738/codegauge-darwin-x64",
    target: "x86_64-apple-darwin",
    archiveExtension: "tar.gz",
    os: "darwin",
    cpu: "x64",
    binaryName: "codegauge",
    requiresExecutable: true,
  },
  {
    packageDirectory: "codegauge-darwin-arm64",
    packageName: "@yacosta738/codegauge-darwin-arm64",
    target: "aarch64-apple-darwin",
    archiveExtension: "tar.gz",
    os: "darwin",
    cpu: "arm64",
    binaryName: "codegauge",
    requiresExecutable: true,
  },
  {
    packageDirectory: "codegauge-win32-x64-msvc",
    packageName: "@yacosta738/codegauge-win32-x64-msvc",
    target: "x86_64-pc-windows-msvc",
    archiveExtension: "zip",
    os: "win32",
    cpu: "x64",
    binaryName: "codegauge.exe",
    requiresExecutable: false,
  },
  {
    packageDirectory: "codegauge-win32-arm64-msvc",
    packageName: "@yacosta738/codegauge-win32-arm64-msvc",
    target: "aarch64-pc-windows-msvc",
    archiveExtension: "zip",
    os: "win32",
    cpu: "arm64",
    binaryName: "codegauge.exe",
    requiresExecutable: false,
  },
];

function isJsonObject(value: unknown): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function readJsonObject(path: string): JsonObject {
  let value: unknown;
  try {
    value = JSON.parse(readFileSync(path, "utf8")) as unknown;
  } catch (error: unknown) {
    throw new Error(`unable to read JSON ${path}: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (!isJsonObject(value)) {
    throw new Error(`JSON ${path} must contain an object`);
  }
  return value;
}

function stringValue(value: unknown, field: string, path: string): string {
  if (typeof value !== "string") {
    throw new Error(`${path} must contain string field ${field}`);
  }
  return value;
}

function stringArrayValue(value: unknown, field: string, path: string): readonly string[] {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string")) {
    throw new Error(`${path} must contain string array field ${field}`);
  }
  return value;
}

async function sha256File(path: string): Promise<string> {
  const digest = createHash("sha256");
  const stream = createReadStream(path);
  for await (const chunk of stream) {
    digest.update(chunk);
  }
  return digest.digest("hex").toLowerCase();
}

export async function verifySha256Sidecar(archivePath: string, checksumPath: string): Promise<string> {
  let sidecar: string;
  try {
    sidecar = readFileSync(checksumPath, "utf8").trim();
  } catch (error: unknown) {
    throw new Error(`unable to read checksum sidecar ${checksumPath}: ${error instanceof Error ? error.message : String(error)}`);
  }
  const match = /^([0-9a-f]{64})  (.+)$/.exec(sidecar);
  if (!match || basename(archivePath) !== match[2]) {
    throw new Error(`invalid checksum sidecar for ${archivePath}`);
  }
  const actual = await sha256File(archivePath);
  if (match[1] !== actual) {
    throw new Error(`checksum mismatch for ${archivePath}: expected ${match[1]}, got ${actual}`);
  }
  return actual;
}

function verifyArchiveManifest(
  artifact: PlatformArtifact,
  releaseVersion: string,
  sourceRevision: string,
  digest: string,
): void {
  const manifest = readJsonObject(artifact.archive.manifestPath);
  if (manifest.version !== releaseVersion) {
    throw new Error(`${artifact.archive.target} manifest version drift: ${String(manifest.version)}`);
  }
  if (manifest.source_revision !== sourceRevision) {
    throw new Error(`${artifact.archive.target} source revision drift: ${String(manifest.source_revision)}`);
  }
  if (manifest.archive !== artifact.archive.archiveName) {
    throw new Error(`${artifact.archive.target} manifest archive drift: ${String(manifest.archive)}`);
  }
  if (manifest.sha256 !== digest) {
    throw new Error(`${artifact.archive.target} manifest checksum drift: ${String(manifest.sha256)}`);
  }
}

function verifyPlatformPackage(artifact: PlatformArtifact, releaseVersion: string): void {
  const packageJson = readJsonObject(artifact.packageJsonPath);
  if (packageJson.name !== artifact.packageName || packageJson.version !== releaseVersion) {
    throw new Error(`${artifact.packageName} package name/version drift`);
  }
  if (JSON.stringify(stringArrayValue(packageJson.os, "os", artifact.packageJsonPath)) !== JSON.stringify([artifact.expectedOs])) {
    throw new Error(`${artifact.packageName} os constraint drift`);
  }
  if (JSON.stringify(stringArrayValue(packageJson.cpu, "cpu", artifact.packageJsonPath)) !== JSON.stringify([artifact.expectedCpu])) {
    throw new Error(`${artifact.packageName} cpu constraint drift`);
  }
  if (!isJsonObject(packageJson.bin) || packageJson.bin.codegauge !== `bin/${artifact.binaryName}`) {
    throw new Error(`${artifact.packageName} binary mapping drift`);
  }
  if (!existsSync(artifact.binaryPath)) {
    throw new Error(`${artifact.packageName} binary is missing: ${artifact.binaryPath}`);
  }
  if (artifact.requiresExecutable && (statSync(artifact.binaryPath).mode & 0o111) === 0) {
    throw new Error(`${artifact.packageName} binary is not executable`);
  }
}

export async function checkNpmPublicationEligibility(
  input: NpmPublicationPreflight,
): Promise<NpmPublicationEligibility> {
  const platformFailures: string[] = [];
  const baseFailures: string[] = [];
  const digests = new Map<string, string>();

  for (const artifact of input.platformArtifacts) {
    try {
      const digest = await verifySha256Sidecar(artifact.archive.archivePath, artifact.archive.checksumPath);
      digests.set(artifact.packageName, digest);
      verifyArchiveManifest(artifact, input.releaseVersion, input.sourceRevision, digest);
      verifyPlatformPackage(artifact, input.releaseVersion);
    } catch (error: unknown) {
      platformFailures.push(error instanceof Error ? error.message : String(error));
    }
  }

  try {
    const basePackage = readJsonObject(input.basePackageJsonPath);
    if (basePackage.name !== "@yacosta738/codegauge" || basePackage.version !== input.releaseVersion) {
      throw new Error("npm base package name/version drift");
    }
    if (!isJsonObject(basePackage.optionalDependencies)) {
      throw new Error("npm base package optionalDependencies are missing");
    }
    const expectedPackages = input.platformArtifacts.map((artifact) => artifact.packageName).sort();
    const actualPackages = Object.keys(basePackage.optionalDependencies).sort();
    if (JSON.stringify(actualPackages) !== JSON.stringify(expectedPackages)) {
      throw new Error("npm base package platform dependency set drift");
    }
    for (const artifact of input.platformArtifacts) {
      if (basePackage.optionalDependencies[artifact.packageName] !== input.releaseVersion) {
        throw new Error(`npm base package pin drift for ${artifact.packageName}`);
      }
    }
  } catch (error: unknown) {
    baseFailures.push(error instanceof Error ? error.message : String(error));
  }

  const platformEligible = platformFailures.length === 0 && digests.size === input.platformArtifacts.length;
  const baseEligible = platformEligible && baseFailures.length === 0;
  return {
    platformEligible,
    baseEligible,
    failures: [...platformFailures, ...baseFailures],
  };
}

export async function verifyReleaseArchives(
  releaseVersion: string,
  sourceRevision: string,
  archives: readonly ReleaseArchive[],
): Promise<void> {
  const failures: string[] = [];
  for (const archive of archives) {
    try {
      const digest = await verifySha256Sidecar(archive.archivePath, archive.checksumPath);
      const manifest = readJsonObject(archive.manifestPath);
      if (manifest.version !== releaseVersion || manifest.source_revision !== sourceRevision || manifest.archive !== archive.archiveName || manifest.sha256 !== digest) {
        throw new Error(`${archive.target} release manifest version/source/checksum drift`);
      }
    } catch (error: unknown) {
      failures.push(error instanceof Error ? error.message : String(error));
    }
  }
  if (failures.length > 0) {
    throw new Error(failures.join("\n"));
  }
}

function requiredOption(args: readonly string[], name: string): string {
  const index = args.indexOf(name);
  const value = index >= 0 ? args[index + 1] : undefined;
  if (!value || value.startsWith("--")) {
    throw new Error(`missing ${name}`);
  }
  return value;
}

function buildPlatformArtifacts(releaseOut: string, npmRoot: string, releaseVersion: string): readonly PlatformArtifact[] {
  return NPM_TARGETS.map((target) => {
    const archiveName = `codegauge-${releaseVersion}-${target.target}.${target.archiveExtension}`;
    const packageDirectory = join(npmRoot, "packages", target.packageDirectory);
    return {
      packageName: target.packageName,
      packageJsonPath: join(packageDirectory, "package.json"),
      binaryPath: join(packageDirectory, "bin", target.binaryName),
      binaryName: target.binaryName,
      archive: {
        archivePath: join(releaseOut, archiveName),
        checksumPath: join(releaseOut, `${archiveName}.sha256`),
        manifestPath: join(releaseOut, `release-manifest-${target.target}.json`),
        archiveName,
        target: target.target,
      },
      expectedOs: target.os,
      expectedCpu: target.cpu,
      requiresExecutable: target.requiresExecutable,
    };
  });
}

async function runCli(args: readonly string[]): Promise<number> {
  const releaseVersion = requiredOption(args, "--release-version");
  const sourceRevision = requiredOption(args, "--source-revision");
  const releaseOut = requiredOption(args, "--release-out");
  const npmRoot = requiredOption(args, "--npm-root");
  const artifacts = buildPlatformArtifacts(releaseOut, npmRoot, releaseVersion);
  if (args.includes("--archives-only")) {
    await verifyReleaseArchives(
      releaseVersion,
      sourceRevision,
      artifacts.map((artifact) => artifact.archive),
    );
    console.log("NPM ARCHIVE PREFLIGHT: PASS");
    return 0;
  }

  const result = await checkNpmPublicationEligibility({
    releaseVersion,
    sourceRevision,
    basePackageJsonPath: join(npmRoot, "codegauge", "package.json"),
    platformArtifacts: artifacts,
  });
  console.log(`NPM PREFLIGHT: platformEligible=${result.platformEligible} baseEligible=${result.baseEligible}`);
  for (const failure of result.failures) {
    console.error(`- ${failure}`);
  }
  return result.platformEligible && result.baseEligible ? 0 : 1;
}

if (require.main === module) {
  runCli(process.argv.slice(2)).catch((error: unknown) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}
