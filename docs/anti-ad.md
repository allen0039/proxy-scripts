# anti-AD 基础去广告 · Surge

通过 `RULE-SET` 引用 [anti-AD 官方 Surge 规则](https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-surge.txt)，使用 `REJECT` 拦截匹配的广告和追踪域名。没有 HTTPS 解密、URL 重写或 JavaScript 脚本。

## 安装

在 Surge → 模块 → 安装新模块中粘贴并启用：

```text
https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Surge/Modules/anti-ad-base.sgmodule
```

无需安装 MITM 证书。Surge 需要成功下载模块及其引用的远程规则集；上游更新后，实际生效版本取决于 Surge 的规则资源更新与缓存。

## 测试建议

1. 想单独比较效果时，暂时关闭其他广告合集和广告规则，例如 adlite、Blockads 或已有的 Sukka 广告拦截规则。
2. 清理目标 App 的广告缓存，或完全退出后重新打开，观察开屏和正常功能。
3. 出现无法加载或登录等问题时，关闭本模块进行对比，并在 Surge 请求记录里检查被拒绝的域名。

本模块采用官方完整域名规则；“基础”指只做域名拦截，不代表规则量少或不会误拦截。与正常内容共用域名的广告、部分信息流广告及缓存广告仍可能出现。

可以与小红书专项模块搭配，但并非所有 App 广告都能通过这个基础模块去除。

## 来源与验证

- 来源：[privacy-protection-tools/anti-AD](https://github.com/privacy-protection-tools/anti-AD)
- 本仓库只托管 Surge 模块包装，不镜像规则数据。
- 2026-09-10 检查：官方规则地址可下载，返回版本标记 `20260908053822`，内容为 `DOMAIN-SUFFIX` 规则；尚未进行设备实测。
