# B 站 CC 繁体字幕转简体

基于 [ddgksf2013 的原规则](https://github.com/ddgksf2013/Rewrite/blob/master/Function/Bilibili_CC.conf)重新适配。旧的 `deezertidal/private/master/js-backup/...` 地址已经失效。本仓库提供自己的转换脚本，并覆盖已知的两类字幕正文地址：`/bfs/subtitle/*.json` 和 `/bfs/ai_subtitle/prod/*`。

## 安装

- **Surge**：在「模块 → 安装新模块」中粘贴：

  ```text
  https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Surge/Modules/Bilibili_CC.sgmodule
  ```

- **Quantumult X**：在「重写 → 远程资源」中添加：

  ```text
  https://raw.githubusercontent.com/allen0039/proxy-scripts/main/QuantumultX/Rewrite/Bilibili_CC.conf
  ```

启用相应客户端的 HTTPS 解密，并安装、信任其 CA 证书。模块或重写文件已包含 `aisubtitle.hdslb.com` 和 `i0.hdslb.com` 的 MITM 主机名。停用其他匹配同一字幕地址的脚本，更新远程资源后重新播放有繁体 CC 字幕的视频。

## 工作方式与限制

脚本只转换响应 JSON 中 `body[].content` 的繁体字，保留时间轴和其他字段。错误响应、非 JSON、不同结构或已是简体的响应会原样通过。它不会替视频生成字幕，也不会自动选择繁体字幕轨道。

已经用模拟字幕响应验证脚本和两类地址的匹配；尚未完成 Surge 或 Quantumult X 的设备实测。B 站也可能使用其他字幕地址、需要登录或返回不同格式。若没有生效，请在请求记录中检查字幕正文 URL 是否命中脚本，并确认 HTTPS 解密、证书、字幕轨道及远程资源更新状态。请勿分享含 `auth_key` 或 Cookie 的完整请求地址。

## 来源、许可和构建

原规则及原转换思路来自 [ddgksf2013](https://github.com/ddgksf2013/Rewrite/blob/master/Function/Bilibili_CC.conf)。本仓库的脚本使用 [OpenCC JS 1.4.2](https://github.com/nk2028/opencc-js) 的繁转简字库与转换器，按其 `MIT AND Apache-2.0` 许可保留了 [许可及第三方声明](../vendor/opencc-js-1.4.2/)。响应处理和两种客户端配置由本仓库维护，未复制原作者的 JavaScript 文件。

从仓库根目录重新生成并验证脚本：

```sh
python3 tools/build_bilibili_cc.py
node --check Scripts/Common/BilibiliCC.js
node tests/bilibili_cc.cjs
```
