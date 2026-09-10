# Proxy Scripts · 代理工具规则、模块与脚本合集

Allen 的个人代理工具资源仓库，集中维护分流规则、去广告模块和脚本。按客户端分类，目前提供 **Surge** 模块；后续按需加入 Loon、Quantumult X 等工具的适配版本。

## 模块安装

在 Surge → 模块 → 安装新模块中，粘贴下方对应地址。

| 模块 | 功能 | MITM | 安装地址与说明 |
| --- | --- | --- | --- |
| anti-AD 基础去广告 | 通过官方规则集拦截广告、追踪域名 | 不需要 | [模块地址](https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Surge/Modules/anti-ad-base.sgmodule) · [使用说明](docs/anti-ad.md) |
| 小红书去广告与去水印 | 开屏、信息流、搜索等内容清理及保存去水印 | 需要 | [模块地址](https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Surge/Modules/RedPaper_remove_ads.sgmodule) · [使用说明](docs/redpaper.md) |

**anti-AD 基础模块：**

```text
https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Surge/Modules/anti-ad-base.sgmodule
```

**小红书模块：**

```text
https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Surge/Modules/RedPaper_remove_ads.sgmodule
```

模块依赖的规则和脚本由 Surge 下载，设备需要能访问相应地址。anti-AD 做域名拦截，小红书模块处理 App 接口，两者可配合使用；避免再同时启用重复处理小红书接口的脚本合集。

## 目录结构

```text
Surge/Modules/       Surge 可直接安装的模块
Scripts/Surge/       Surge 使用的 JavaScript 脚本
Rules/Surge/         Surge 规则源索引；后续存放自维护规则
docs/              各模块的使用说明和限制
tools/             构建工具
tests/             脚本验证
upstream/redpaper/ 小红书上游原始快照与来源说明
```

新增客户端时使用对应名称的目录，例如 `Loon/Plugins/`、`QuantumultX/Rewrite/`、`Scripts/Loon/`、`Rules/Loon/`；只在确认跨客户端兼容后才放入 `Scripts/Common/`。上游快照用于适配和追溯，安装时使用上方模块目录中的发布版本。

新增资源应同时添加使用说明、来源署名及首页安装链接。涉及脚本改动时，运行相应验证。

## 开发与验证

在仓库根目录执行：

```sh
python3 tools/build_redpaper.py
node --check Scripts/Surge/RedPaperSurge.js
node tests/redpaper.cjs
```

小红书脚本和模块由构建工具生成，修改适配逻辑时编辑 `tools/build_redpaper.py`，避免重新构建覆盖手工改动。anti-AD 模块直接维护，不需要构建。

## 旧仓库迁移

本仓库原名 `redbooknoads`，现改名为 `proxy-scripts`。根目录的 `RedPaper_remove_ads.sgmodule` 和 `RedPaperSurge.js` 保留为兼容入口，由构建工具与规范路径同步生成；新安装请使用上方分类目录中的地址。

已安装的用户建议将模块订阅地址更新为新地址。GitHub 的旧仓库重定向不应作为永久安装地址使用。

## 来源

- anti-AD：[privacy-protection-tools/anti-AD](https://github.com/privacy-protection-tools/anti-AD)。本仓库模块直接引用官方规则，不复制或自动修改上游规则。
- 小红书：基于可莉发布的 Loon 插件适配，原作者 RuCu6、fmz200，详见[来源与构建说明](docs/redpaper.md#来源与构建)。这是个人 Surge 适配版本。

保留各资源原作者署名，上游内容权利及许可归相应作者或项目。模块效果会受 App 版本、接口与缓存影响，当前未完成设备实测。
