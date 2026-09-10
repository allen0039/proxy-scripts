# 小红书上游快照

本目录保存 2026-09-10 获取的适配输入，不作为本仓库的安装入口。

- `RedPaper_remove_ads.lpx`：[可莉发布的 Loon 插件](https://kelee.one/Tool/Loon/Lpx/RedPaper_remove_ads.lpx)，标注 2026-06-01。
- `RedPaper_remove_ads.js`：[上游脚本](https://kelee.one/Resource/JavaScript/RedPaper/RedPaper_remove_ads.js)，标注 2026-02-14。
- 原作者：RuCu6、fmz200；发布目录：[可莉插件中心](https://hub.kelee.one)。

保留原始署名，上游内容权利归原作者所有。每天定时检查上游；转换及测试通过后自动更新快照和 Surge 发布文件，最新同步记录见同步后生成的 `sync.json`。

## 自动同步小红书上游

[同步工作流](https://github.com/allen0039/proxy-scripts/actions/workflows/sync-redpaper.yml)每天北京时间 **09:23** 检查原插件及原脚本（GitHub 调度可能延迟），也可在 Actions 页面点击 **Run workflow** 手动运行。

发现内容变化后，在临时目录转换为 Surge 版本，检查上游指令、适配结构、JavaScript 语法并执行模拟响应测试。全部通过才提交到 main，同时更新规范目录与根目录兼容入口。无变化不提交；下载失败、出现未知写法或测试失败时不发布，保留现有版本，可在 Actions 日志查看原因。上游结构变化时仍可能需要人工调整转换器，不能保证所有未来版本都可自动适配。

上游快照的同步时间和 SHA-256 在成功更新后记录到 `upstream/redpaper/sync.json`。上方旧日期仅表示首次快照版本。设备需刷新模块与脚本资源才能使用新版本。公开仓库长期无活动时，GitHub 可能暂停定时工作流，届时需重新启用。
