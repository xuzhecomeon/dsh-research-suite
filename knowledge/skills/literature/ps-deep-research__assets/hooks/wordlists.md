# Hook 词表依据 (v2.5)

> 每个词带"为什么收录"的来源 + 选词理由。词表本身有 unit test,新增/删除走 PR + test。

## Hedge(推测语)

> 学术依据: Specificity Heuristic (Zhang & Schwarz 2012 *JESP*) — 模糊度对说服力的折损。

| 词 | 类别 | 来源/理由 |
|---|---|---|
| 可能 | zh 推测 | 高频模糊副词,R03 报告 9 次 hit |
| 或许 / 也许 | zh 推测 | 等价"可能" |
| 视情况 / 看具体 | zh 兜底 | 决策型报告的反 pattern — 不给条件就是不交付 |
| 大致 / 大概 / 估计 / 貌似 / 看起来 | zh 模糊 | 量化/事实判断时降低锐度 |
| 似乎 / 应该是 | zh 弱断言 | 等价 "seems to" |
| may / might / could / possibly / perhaps / arguably / probably | en 推测 | OpenAI DR / Anthropic CoT 报告高频 |
| seems to / appears to / in some cases / it is likely | en 弱断言 | 学术写作典型 hedge |

**阈值**: standard ≤12, deep ≤10, decide ≤6;超过 → `[hedge-words]` 偷工标记。

## Vague Quantifier(含糊量词)

> 与 hedge 区分: 数量级模糊 vs 真值不确定。决策型报告必须给具体数。

| 词 | 类别 | 来源/理由 |
|---|---|---|
| 显著 / significantly | 程度 | 没数字的"显著"= 没说 |
| 大量 / 许多 / 多数 / 大部分 / many / a lot of / a number of | 数量 | 决策必须给 N |
| 经常 / 频繁 / often | 频率 | 给频率必须给 per X |
| 较多 / 部分 / 一些 / several / various / some | 模糊集合 | 不算数 |
| 相对 / 相当 / 不少 / relatively / fairly / quite / somewhat / considerable | 程度 | 等价"显著" |

**阈值**: standard ≤10, deep ≤8, decide ≤5;超过 → `[vague-quantifiers]`。

## Weak H2(无 Action Title)

> McKinsey Action Title + Minto Pyramid Principle: 章节标题就是结论。

| 词 | 为什么算 weak |
|---|---|
| 分析 / 讨论 / 介绍 / 概述 / 说明 / 关于 | 动词但无结论方向 |
| 现状 / 背景 / 内容 / 信息 | 名词无结论 |
| 局限 / 缺口 | 通用兜底标题(局限本身要给具体内容)|
| 总结 / 结论 / 附录 / 其他 | 模板兜底 |

**阈值**: action_title_ratio ≥ 0.70 pass,< 0.70 → `[no-reasoning-tags]`。

## Rebuttal(反驳/反方语)

> Toulmin Rebuttal 元素: 主张必须含反方处理。

匹配: `Rebuttal | 例外: | 反方: | 反对 | 但.*不成立 | 然而.*并非 | 尽管.*仍 | critics argue | opponents claim | counter-argument`

**阈值**: deep ≥3, standard ≥1。

## Confab Candidates(AI Confabulation 候选)

> 触发 Phase 4 Step 7 lint 的数字+单位 token,主 agent 后续按 evidence_span 比对。

匹配: `\d+\.?\d*\s*(MB|GB|KB|TB|%|x|×|倍|ms|s |秒|分钟|min|hour|小时|天|day|month|月|year|年)`

**用法**: hook 不判定真假(只数候选);Phase 4.5 fact-checker 逐个验。

## 词表演化原则

1. 每次 R0X regression 实测发现新词 → 必加 + 加 unit test 防回归
2. 新增词必有真实出处(R03/Rxx report 某行某词触发)
3. 删词需 2 次 regression 验证"删了也不漏检"
4. 词表 hash 写入 frontmatter `quality_audit.scan_wordlist_hash`,跨版本可追溯
