const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const moduleText = fs.readFileSync(path.join(root, "Surge/Modules/Bilibili_remove_ads.sgmodule"), "utf8");
const jsonScript = fs.readFileSync(path.join(root, "Scripts/Surge/BilibiliAdJSON.js"), "utf8");

for (const filename of ["BilibiliAdJSON.js", "BilibiliAdProto.js"]) {
  const url = `https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Scripts/Surge/${filename}`;
  assert.ok(moduleText.includes(url), `${filename} must be self-hosted`);
}
assert.ok(!moduleText.includes("deezertidal/private"));
assert.ok(moduleText.includes("binary-body-mode=true"));

const jsonPattern = new RegExp(moduleText.match(/bilibili-ad-json =[^\n]*pattern=([^,]+), requires-body/)[1]);
assert.match("https://app.bilibili.com/x/v2/feed/index?fnval=0", jsonPattern);
assert.match("https://app.bilibili.com/x/v2/splash/show", jsonPattern);

let result;
const response = { code: 0, data: { items: [
  { card_type: "cm_v2", card_goto: "ad_web_s" },
  { card_type: "small_cover_v10", card_goto: "video" },
] } };
vm.runInNewContext(jsonScript, {
  $request: { url: "https://app.bilibili.com/x/v2/feed/index?fnval=0", method: "GET" },
  $response: { body: JSON.stringify(response) },
  $done: (value) => { result = value; },
  $notification: { post: () => {} },
  console: { log: () => {} },
}, { timeout: 2000 });
assert.equal(JSON.parse(result.body).data.items.length, 1);
assert.equal(JSON.parse(result.body).data.items[0].card_goto, "video");
console.log("Bilibili ads: self-hosted URLs, endpoint matching, feed filtering passed");
