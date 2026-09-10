# 小红书去广告与去水印 · Surge 适配版

基于可莉发布的 Loon 插件适配，原作者 RuCu6、fmz200。本仓库不是原作者的官方 Surge 版本。

## 链接安装

在 Surge → 模块 → 安装新模块中粘贴：

```text
https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Surge/Modules/RedPaper_remove_ads.sgmodule
```

[查看／下载模块](https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Surge/Modules/RedPaper_remove_ads.sgmodule)

模块会自动下载本仓库的 JS 脚本，无需手动复制文件。设备需要能访问 raw.githubusercontent.com。

1. 禁用旧的小红书 Loon 模块及其他重复处理小红书的脚本，再启用本模块。
2. 开启 Surge 的重写、MITM，并安装及完全信任 Surge CA 证书。
3. 清除小红书缓存、彻底退出后重开。先打开笔记／播放视频，再保存图片、视频或实况。

适配目标为 Surge iOS 5.22.0；Map Local 功能要求至少 iOS 5.9.1 或 Mac 5.5.1。

## 功能与限制

包含原插件的开屏、信息流、搜索、关注页广告及推荐内容清理，以及图片、视频、实况和评论实况去水印。原规则也会过滤部分直播、带货和推荐内容。

使用 Surge 原生 Rule、Map Local、Script、MITM 配置；MITM 域名采用追加方式。保留原作者主要脚本逻辑，增加异常响应原样放行、缓存容错，并修复视频列表全为广告时漏过滤的问题。响应体超过 5 MiB 时 Surge 会跳过脚本。

已通过 JavaScript 语法检查和 21 次模拟响应验证；尚未完成 iPhone Surge 实机验证。接口变化、缓存、MITM 排除规则及重复脚本可能影响结果。此模块修改媒体地址和保存配置，无法擦除原始像素中已嵌入的水印。

如果未生效，在 Surge 请求记录中检查小红书接口是否显示完整 HTTPS 路径、是否运行 redpaper-surge-*，以及是否出现脚本下载失败、超时或响应过大。每个响应只会运行第一个匹配脚本。

## 来源与构建

- 原作者：[RuCu6](https://github.com/RuCu6)、[fmz200](https://github.com/fmz200)
- 发布目录：[可莉插件中心](https://hub.kelee.one)
- [原插件](https://kelee.one/Tool/Loon/Lpx/RedPaper_remove_ads.lpx)，标注 2026-06-01
- [原脚本](https://kelee.one/Resource/JavaScript/RedPaper/RedPaper_remove_ads.js)，标注 2026-02-14
- 上游快照获取日期：2026-09-10。保留原作者署名；上游内容权利归原作者所有。

```sh
python3 tools/build_redpaper.py
node --check Scripts/Surge/RedPaperSurge.js
node tests/redpaper.cjs
```

upstream/redpaper/ 保存本次使用的源文件。本仓库不自动跟踪上游更新；Surge 自动下载的是本仓库发布的脚本。
