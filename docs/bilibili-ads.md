# B 站去广告模块

旧的 `deezertidal/private/js-backup` 脚本地址返回 404。旧「哔哩哔哩去广告」和 `Bili1080P` 模块会持续请求这些地址，即使主配置已经加入新的 CC 字幕脚本。

在 Surge 的「模块 → 安装新模块」中安装本仓库的替代去广告模块：

```text
https://raw.githubusercontent.com/allen0039/proxy-scripts/main/Surge/Modules/Bilibili_remove_ads.sgmodule
```

停用或删除旧「哔哩哔哩去广告」模块，避免同一响应重复处理。新模块的两个脚本均由本仓库托管，改写开屏、推荐、动态和视频页的部分广告数据。需开启 Surge 的 MITM 和脚本功能，并信任 CA 证书；字幕繁转简继续由 [CC 字幕模块](bilibili-cc.md)或现有配置负责。

原旧模块的 `Bili1080P` 是独立的账号信息改写，脚本源已失效；本模块不提供画质解锁，也不改变账号权益。暂未在设备上验证全部广告场景，B 站接口变化可能影响效果。

脚本来自 [app2smile/rules](https://github.com/app2smile/rules/tree/master/js)，按 MIT 许可保留了[来源和许可声明](../vendor/app2smile-bilibili/)。本仓库保存脚本副本，不自动同步上游修改。
