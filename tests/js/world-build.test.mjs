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
