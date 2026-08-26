import test from "node:test";
import assert from "node:assert/strict";
import { chmod, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const targetPackage = {
  "darwin-x64": "codegauge-darwin-x64",
  "darwin-arm64": "codegauge-darwin-arm64",
  "linux-x64": "codegauge-linux-x64-gnu",
  "linux-arm64": "codegauge-linux-arm64-gnu",
  "win32-x64": "codegauge-win32-x64-msvc",
  "win32-arm64": "codegauge-win32-arm64-msvc",
}[`${process.platform}-${process.arch}`];
const binaryName = process.platform === "win32" ? "codegauge.exe" : "codegauge";
const fakePackage = join(root, "node_modules", "@yacosta738", targetPackage ?? "unsupported");
const wrapper = join(root, "dist", "index.js");

test("wrapper source declares exact target resolution and passthrough contracts", async () => {
  const source = await readFile(join(root, "src", "index.ts"), "utf8");
  for (const fragment of [
    "process.platform",
    "process.arch",
    "process.argv.slice(2)",
    "spawnSync",
    'stdio: "inherit"',
    "process.exitCode",
    "require.resolve",
    "codegauge-linux-x64-gnu",
    "codegauge-linux-arm64-gnu",
    "musl",
  ]) {
    assert.match(source, new RegExp(fragment.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  }
});

test("wrapper has no musl optional package", async () => {
  const packageJson = JSON.parse(await readFile(join(root, "package.json"), "utf8"));
  assert.equal(Object.keys(packageJson.optionalDependencies).some((name) => name.includes("musl")), false);
});

test("base package does not publish its internal preflight helper", async () => {
  const packageJson = JSON.parse(await readFile(join(root, "package.json"), "utf8"));
  assert.deepEqual(packageJson.files, ["dist/index.js"]);
});

test("wrapper reports a missing optional dependency without running another binary", () => {
  if (!targetPackage) return;
  const result = spawnSync(process.execPath, [wrapper, "version"], {
    encoding: "utf8",
    env: { ...process.env, CODEGAUGE_LIBC: "glibc" },
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /Missing optional dependency/);
});

test("wrapper preserves arguments, inherited streams, and child exit status", async () => {
  if (!targetPackage || process.platform === "win32") return;
  const binary = join(fakePackage, "bin", binaryName);
  await mkdir(join(fakePackage, "bin"), { recursive: true });
  await writeFile(
    join(fakePackage, "package.json"),
    JSON.stringify({ name: `@yacosta738/${targetPackage}`, version: "0.1.0" }),
  );
  await writeFile(
    binary,
    '#!/usr/bin/env node\nprocess.stdin.pipe(process.stdout); console.log(JSON.stringify(process.argv.slice(2))); process.exitCode = 17;\n',
  );
  await chmod(binary, 0o755);
  try {
    const result = spawnSync(process.execPath, [wrapper, "analyze", "--profile", "jvm-jacoco-v1"], {
      input: "stdin",
      encoding: "utf8",
      env: { ...process.env, CODEGAUGE_LIBC: "glibc" },
    });
    assert.equal(result.status, 17);
    assert.match(result.stdout, /stdin/);
    assert.match(result.stdout, /jvm-jacoco-v1/);
  } finally {
    await rm(fakePackage, { recursive: true, force: true });
  }
});

test("wrapper rejects a musl Linux runtime before optional dependency lookup", () => {
  if (process.platform !== "linux") return;
  const result = spawnSync(process.execPath, [wrapper], {
    encoding: "utf8",
    env: { ...process.env, CODEGAUGE_LIBC: "musl" },
  });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /musl/);
});
