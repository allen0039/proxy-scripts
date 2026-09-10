# Surge 规则源

此目录收录规则源索引，后续自维护的 Surge `.list` 规则也放在这里。

| 规则 | 官方地址 | 使用方式 |
| --- | --- | --- |
| anti-AD | [anti-ad-surge.txt](https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-surge.txt) | 使用 [anti-AD 基础模块](../../Surge/Modules/anti-ad-base.sgmodule)，或在配置的 `[Rule]` 中引用 |

手动引用示例（放在最终兜底规则之前）：

```ini
RULE-SET,https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-surge.txt,REJECT
```

已安装基础模块时无需重复添加。这里不保存官方规则副本，以免副本与上游不同步。
