const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const script = fs.readFileSync(path.join(root, "Scripts/Common/BilibiliCC.js"), "utf8");
const surge = fs.readFileSync(path.join(root, "Surge/Modules/Bilibili_CC.sgmodule"), "utf8");
const qx = fs.readFileSync(path.join(root, "QuantumultX/Rewrite/Bilibili_CC.conf"), "utf8");

const surgePattern = new RegExp(surge.match(/pattern=([^,]+), requires-body/)[1]);
const qxPattern = new RegExp(qx.split("\n").find((line) => line.includes("url script-response-body")).split(" url ")[0]);
const urls = [
  "https://i0.hdslb.com/bfs/subtitle/example.json",
  "https://aisubtitle.hdslb.com/bfs/subtitle/example.json?auth_key=x",
  "https://aisubtitle.hdslb.com/bfs/ai_subtitle/prod/example?auth_key=x",
];
for (const pattern of [surgePattern, qxPattern]) {
  for (const url of urls) assert.match(url, pattern);
  assert.doesNotMatch("https://aisubtitle.hdslb.com/bfs/other/example", pattern);
  assert.doesNotMatch("https://evil.example/bfs/subtitle/example.json", pattern);
}

function run(body) {
  const output = [];
  vm.runInNewContext(script, {
    $response: { body },
    $done: (value) => output.push(value),
  }, { timeout: 3000 });
  assert.equal(output.length, 1);
  return output[0];
}

const source = JSON.stringify({ body: [
  { from: 0, to: 1, content: "歡迎來到臺灣，這是繁體字幕。" },
  { from: 1, to: 2, content: "Already English" },
] });
const converted = JSON.parse(run(source).body);
assert.equal(converted.body[0].content, "欢迎来到台湾，这是繁体字幕。");
assert.equal(converted.body[1].content, "Already English");
assert.equal(converted.body[0].from, 0);
assert.equal(Object.keys(run(JSON.stringify({ code: -101, message: "not logged in" }))).length, 0);
assert.equal(Object.keys(run("not json")).length, 0);
assert.equal(Object.keys(run(JSON.stringify({ body: [{ content: "简体字幕" }] }))).length, 0);
console.log("Bilibili CC: URL matching, conversion, and passthrough passed");
