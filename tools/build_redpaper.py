from pathlib import Path
import re
root = Path(__file__).resolve().parent.parent
source = (root/'upstream/redpaper/RedPaper_remove_ads.js').read_text()
source = source.replace('if (!$response.body) $done({});', 'if (!$response.body) return {};')
source = source.replace('JSON.parse($persistentStore.read(', 'readCache(')
# readCache("key")); -> readCache("key");
source = re.sub(r'readCache\(("[^"]+")\)\)', r'readCache(\1)', source)
source = source.replace('$done({});', 'return {};').replace('$done({ body: JSON.stringify(obj) });', 'return { body: JSON.stringify(obj) };')
# Set filtered list even when every item is an advertisement.
source = source.replace('      obj.data = modDatas;\n', '')
source = source.replace('    $persistentStore.write(JSON.stringify(newDatas), "redBookVideoFeed");', '    obj.data = modDatas;\n    $persistentStore.write(JSON.stringify(newDatas), "redBookVideoFeed");')
search = '''
// Loon response-body-json-replace equivalents, preserving the response envelope.
const searchPath = url.split("?")[0];
const replacements = {
  "/v1/search/banner_list": [["data", {}]],
  "/v1/search/hot_list": [["data.items", []]],
  "/v4/search/hint": [["data.hint_words", []]],
  "/v4/search/trending": [["data.queries", []], ["data.hint_word", {}]]
};
for (const [suffix, changes] of Object.entries(replacements)) {
  if (searchPath.endsWith(suffix)) {
    for (const [path, value] of changes) {
      const keys = path.split(".");
      let parent = obj;
      for (const key of keys.slice(0, -1)) parent = parent?.[key];
      if (parent && typeof parent === "object") parent[keys[keys.length - 1]] = value;
    }
    return { body: JSON.stringify(obj) };
  }
}
'''
source = source.replace('let obj = JSON.parse($response.body);', 'let obj = JSON.parse($response.body);\n'+search)
wrapper = '''// Surge adaptation, 2026-09-10. Original authors: RuCu6, fmz200; distributed by iKelee.
// Source: https://kelee.one/Resource/JavaScript/RedPaper/RedPaper_remove_ads.js
// Hosted Surge adaptation; source snapshot and build script are in this repository.
function readCache(key) {
  try { return JSON.parse($persistentStore.read(key) || "null"); }
  catch (_) { return null; }
}
function transform() {
'''+source+'''
}
let result = {};
try { result = transform(); }
catch (_) { console.log("[RedPaper Surge] 响应格式异常，本次保留原始响应。"); }
$done(result);
'''
(root/'Scripts/Surge').mkdir(parents=True, exist_ok=True)
(root/'Scripts/Surge/RedPaperSurge.js').write_text(wrapper)
# Compatibility entry for previously installed modules.
(root/'RedPaperSurge.js').write_text(wrapper)
lpx = (root/'upstream/redpaper/RedPaper_remove_ads.lpx').read_text()
lines=['#!name=小红书去广告与去水印（Surge 适配）','#!desc=基于可莉 Loon 插件，原作者 RuCu6、fmz200。启用重写与 MITM；脚本由 GitHub 自动下载。','', '[Rule]', 'AND,((PROTOCOL,QUIC),(DOMAIN-SUFFIX,xiaohongshu.com)),REJECT', '', '[Map Local]']
for pattern, action in re.findall(r'^(\^\S+) (reject-img|reject-dict)$',lpx,re.M):
    value='data-type=tiny-gif' if action=='reject-img' else 'data-type=text data="{}" header="Content-Type:application/json"'
    lines.append(pattern+' '+value+' status-code=200')
lines+=['','[Script]']
patterns=re.findall(r'^http-response (\S+) script-path=',lpx,re.M)
patterns+=re.findall(r'^(\^\S+) response-body-json-replace',lpx,re.M)
for n,pattern in enumerate(patterns,1):
    lines.append(f'redpaper-surge-{n:02} = type=http-response, pattern={pattern}, requires-body=true, max-size=5242880, timeout=10, script-path=https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Scripts/Surge/RedPaperSurge.js')
lines+=['','[MITM]','hostname = %APPEND% '+lpx.split('hostname=')[1].strip(),'']
(root/'Surge/Modules').mkdir(parents=True, exist_ok=True)
(root/'Surge/Modules/RedPaper_remove_ads.sgmodule').write_text('\n'.join(lines))
# Compatibility entry for previously installed subscriptions.
(root/'RedPaper_remove_ads.sgmodule').write_text('\n'.join(lines))
