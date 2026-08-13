import { existsSync } from "node:fs";
import { createRequire } from "node:module";
import { env } from "node:process";
import { dirname, join } from "node:path";
import { spawnSync } from "node:child_process";

type Target = {
  readonly packageName: string;
  readonly binaryName: string;
};

const TARGETS: Readonly<Record<string, Target>> = {
  "linux-x64": {
    packageName: "@yacosta738/codegauge-linux-x64-gnu",
    binaryName: "codegauge",
  },
  "linux-arm64": {
    packageName: "@yacosta738/codegauge-linux-arm64-gnu",
    binaryName: "codegauge",
  },
  "darwin-x64": {
    packageName: "@yacosta738/codegauge-darwin-x64",
    binaryName: "codegauge",
  },
  "darwin-arm64": {
    packageName: "@yacosta738/codegauge-darwin-arm64",
    binaryName: "codegauge",
  },
  "win32-x64": {
    packageName: "@yacosta738/codegauge-win32-x64-msvc",
    binaryName: "codegauge.exe",
  },
  "win32-arm64": {
    packageName: "@yacosta738/codegauge-win32-arm64-msvc",
    binaryName: "codegauge.exe",
  },
};

const resolvePackage = createRequire(__filename);

function hasGlibc(): boolean {
  const report = process.report?.getReport() as { header?: { glibcVersionRuntime?: string } } | null;
  return Boolean(report?.header?.glibcVersionRuntime);
}

function targetKey(): string {
  return `${process.platform}-${process.arch}`;
}

function unsupportedPlatform(): never {
  if (process.platform === "linux" && !hasGlibc()) {
    throw new Error(
      "CodeGauge npm packages require a glibc Linux runtime; musl or unknown libc runtimes are unsupported.",
    );
  }
  throw new Error(`CodeGauge does not provide a binary for ${process.platform}/${process.arch}. Supported targets are Linux GNU, macOS, and Windows MSVC x64/arm64.`);
}

function executablePath(target: Target): string {
  let packageJson: string;
  try {
    packageJson = resolvePackage.resolve(`${target.packageName}/package.json`); // require.resolve-compatible package lookup
  } catch {
    throw new Error(`Missing optional dependency ${target.packageName}; reinstall @yacosta738/codegauge for ${process.platform}/${process.arch}.`);
  }
  const binary = join(dirname(packageJson), "bin", target.binaryName);
  if (!existsSync(binary)) {
    throw new Error(`Optional dependency ${target.packageName} is incomplete: ${target.binaryName} is missing.`);
  }
  return binary;
}

function main(): void {
  if (process.platform === "linux" && (env.CODEGAUGE_LIBC === "musl" || !hasGlibc())) {
    unsupportedPlatform();
  }
  const target = TARGETS[targetKey()];
  if (!target) {
    unsupportedPlatform();
  }
  const result = spawnSync(executablePath(target), process.argv.slice(2), {
    stdio: "inherit",
    windowsHide: false,
  });
  if (result.error) {
    throw new Error(`Unable to start CodeGauge: ${result.error.message}`);
  }
  process.exitCode = result.status ?? 1;
}

try {
  main();
} catch (error: unknown) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = process.exitCode || 1;
}
