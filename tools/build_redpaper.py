from pathlib import Path
import json
import re
root = Path(__file__).resolve().parent.parent
source = (root/'upstream/redpaper/RedPaper_remove_ads.js').read_text()
# Fail closed when upstream changes the structures our adapter patches.
required = ['if (!$response.body) $done({});', 'let obj = JSON.parse($response.body);',
            '      obj.data = modDatas;\n',
            '    $persistentStore.write(JSON.stringify(newDatas), "redBookVideoFeed");']
for marker in required:
    if source.count(marker) != 1:
        raise ValueError('Upstream JS structure changed; adapter review required: ' + marker)
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
# Reject unsupported Loon directives rather than silently omitting them.
section = None
json_rewrites = []
reject_rules = []
script_patterns = []
for raw in lpx.splitlines():
    line = raw.strip()
    if not line or line.startswith('#'):
        continue
    if line.startswith('['):
        if line not in ['[Rule]', '[Rewrite]', '[Script]', '[MitM]']:
            raise ValueError('Unsupported upstream section: ' + line)
        section = line
        continue
    valid = False
    if section == '[Rule]':
        valid = re.sub(r'\s+', '', line) == 'AND,((PROTOCOL,QUIC),(DOMAIN-SUFFIX,xiaohongshu.com)),REJECT'
    elif section == '[Rewrite]':
        legacy_reject = re.fullmatch(r'(\^\S+) (reject-img|reject-dict)', line)
        modern = re.fullmatch(r'(request|response) if \$\{url\} ~= /(\^\S+)/i then (.+)', line)
        if legacy_reject:
            reject_rules.append(legacy_reject.groups())
            valid = True
        elif ' response-body-json-replace ' in line:
            json_rewrites.append(line)
            valid = True
        elif modern:
            kind, pattern, action = modern.groups()
            reject = re.fullmatch(r'reject_(img|dict)\(200\)', action)
            replace = re.fullmatch(r'response\.json\.replace\((.+)\)', action)
            if kind == 'request' and reject:
                reject_rules.append((pattern, 'reject-' + reject.group(1)))
                valid = True
            elif kind == 'response' and replace:
                args = json.loads('[' + replace.group(1) + ']')
                if len(args) == 2:
                    paths, values = args
                    paths = [paths] if isinstance(paths, str) else paths
                    values = [values] if isinstance(values, str) else values
                    if (isinstance(paths, list) and isinstance(values, list)
                            and len(paths) == len(values)
                            and all(isinstance(item, str) for item in paths + values)):
                        pairs = ' '.join(f'{path} {value}' for path, value in zip(paths, values))
                        json_rewrites.append(f'{pattern} response-body-json-replace {pairs}')
                        valid = True
    elif section == '[Script]':
        legacy = re.fullmatch(r'http-response (\S+) script-path=https://kelee\.one/Resource/JavaScript/RedPaper/RedPaper_remove_ads\.js, requires-body=true, tag=.+', line)
        modern = re.fullmatch(r'response if \$\{url\} ~= /(\^\S+)/i then script\("https://kelee\.one/Resource/JavaScript/RedPaper/RedPaper_remove_ads\.js"\) with tag="[^"]+", requires_body=true', line)
        if legacy or modern:
            script_patterns.append((legacy or modern).group(1))
            valid = True
    elif section == '[MitM]':
        valid = bool(re.fullmatch(r'hostname=[a-zA-Z0-9*., -]+', line))
    if not valid:
        raise ValueError('Unsupported upstream directive: ' + line)
# These four JSON rewrites are currently implemented in the adapter above.
expected_json = (root/'tools/redpaper-json-rewrites.txt').read_text().splitlines()
if json_rewrites != expected_json:
    raise ValueError('Upstream JSON rewrites changed; adapter review required')
lines=['#!name=小红书去广告与去水印（Surge 适配）','#!desc=基于可莉 Loon 插件，原作者 RuCu6、fmz200。启用重写与 MITM；脚本由 GitHub 自动下载。','', '[Rule]', 'AND,((PROTOCOL,QUIC),(DOMAIN-SUFFIX,xiaohongshu.com)),REJECT', '', '[Map Local]']
for pattern, action in reject_rules:
    value='data-type=tiny-gif' if action=='reject-img' else 'data-type=text data="{}" header="Content-Type:application/json"'
    lines.append(pattern+' '+value+' status-code=200')
lines+=['','[Script]']
patterns = script_patterns + [line.split(' response-body-json-replace ', 1)[0] for line in json_rewrites]
for n,pattern in enumerate(patterns,1):
    lines.append(f'redpaper-surge-{n:02} = type=http-response, pattern={pattern}, requires-body=true, max-size=5242880, timeout=10, script-path=https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Scripts/Surge/RedPaperSurge.js')
lines+=['','[MITM]','hostname = %APPEND% '+lpx.split('hostname=')[1].strip(),'']
(root/'Surge/Modules').mkdir(parents=True, exist_ok=True)
(root/'Surge/Modules/RedPaper_remove_ads.sgmodule').write_text('\n'.join(lines))
# Compatibility entry for previously installed subscriptions.
(root/'RedPaper_remove_ads.sgmodule').write_text('\n'.join(lines))
