// WORLD のソースの取り込みと、ビルドスクリプト・成果物の検査（006-wasm-world）
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const WORLD = path.join(ROOT, "third_party/world");

// TC-700-1
test("WORLD の src と world/ のヘッダが取り込まれている", () => {
  for (const f of ["harvest.cpp", "cheaptrick.cpp", "d4c.cpp", "synthesis.cpp", "common.cpp", "fft.cpp", "matlabfunctions.cpp"])
    assert.ok(existsSync(path.join(WORLD, "src", f)), f);
  for (const h of ["harvest.h", "cheaptrick.h", "d4c.h", "synthesis.h", "common.h", "fft.h", "matlabfunctions.h", "constantnumbers.h", "macrodefinitions.h"])
    assert.ok(existsSync(path.join(WORLD, "src/world", h)), h);
});

// TC-700-2
test("WORLD のライセンス文がある", () => {
  const text = readFileSync(path.join(WORLD, "LICENSE.txt"), "utf8");
  assert.ok(text.includes("Copyright (c) 2010  M. Morise"));
  assert.ok(text.includes("Redistribution and use in source and binary forms"));
});

// TC-701-1
test("COMMIT は取り込んだ 40 桁のコミットハッシュの 1 行である", () => {
  const lines = readFileSync(path.join(WORLD, "COMMIT"), "utf8").replace(/\n$/, "").split("\n");
  assert.deepEqual(lines, ["d625e7608ca23a870018f01e7c562ac683d9847f"]);
});

// ---------------------------------------------------------------- ビルドスクリプトと成果物

import { execFileSync } from "node:child_process";
import { mkdtempSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import os from "node:os";

const BUILD = path.join(ROOT, "engine/world/build.sh");
const ARTIFACTS = ["world.wasm", "world.mjs"];
const IMAGE = "emscripten/emsdk@sha256:41039722671531506a7d081828721e9ccde93125d91f88351e0fe4301606c7d4";
const sha256 = p => createHash("sha256").update(readFileSync(p)).digest("hex");

function build() {
  const out = mkdtempSync(path.join(os.tmpdir(), "world-build-"));
  execFileSync(BUILD, [out], { stdio: "pipe" });
  return out;
}

// TC-702-1
test("ビルドスクリプトは linux/arm64 のダイジェストでイメージを指定している", () => {
  assert.ok(readFileSync(BUILD, "utf8").includes(IMAGE));
});

// TC-703-1
test("ビルドスクリプトはタグだけでイメージを指定していない", () => {
  const text = readFileSync(BUILD, "utf8");
  const uses = [...text.matchAll(/emscripten\/emsdk(.{0,8})/g)];
  assert.ok(uses.length > 0);
  for (const m of uses) assert.ok(m[1].startsWith("@sha256:"), `タグ指定: emscripten/emsdk${m[1]}`);
});

// TC-704-1
test("linux/arm64 でビルドすると、コミット済みの成果物と同一のファイルが出る", () => {
  assert.equal(os.arch(), "arm64", "SPEC-704 は arm64 のマシンでだけ判定できる");
  const out = build();
  for (const f of ARTIFACTS) assert.equal(sha256(path.join(out, f)), sha256(path.join(ROOT, "engine/world", f)), f);
});

// TC-705-1
test("同じマシンで 2 回ビルドすると、出力は同一である", () => {
  const a = build(), b = build();
  for (const f of ARTIFACTS) assert.equal(sha256(path.join(a, f)), sha256(path.join(b, f)), f);
});

// TC-764-1
test("world.wasm と world.mjs のサイズの合計が 200KB 未満", () => {
  const total = ARTIFACTS.reduce((s, f) => s + statSync(path.join(ROOT, "engine/world", f)).size, 0);
  assert.ok(total < 204800, `${total} バイト`);
});
