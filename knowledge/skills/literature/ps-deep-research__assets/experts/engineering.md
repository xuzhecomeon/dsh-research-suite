# Expert: Engineering & Architecture

> **权威来源**:
> - `donnemartin/system-design-primer` (280k★) — 系统设计事实标准
> - `joelparkerhenderson/architecture-decision-record` (11k★) — ADR 模板与最佳实践
> - Microsoft Azure Well-Architected Framework — 五大支柱（可靠性/安全/成本优化/运维卓越/性能效率）
> - Google SRE Book — 可靠性工程

## 评价标准

作为 researcher，在评估工程/架构相关 source 时，按以下优先级：

1. **官方文档 > 第三方总结** — vendor 官方 doc、RFC、spec 优先
2. **生产案例 > 理论分析** — 有具体公司/规模/数据的案例优先
3. **ADR 格式 > 博客** — 有 structured decision record（背景→决策→后果→替代方案）的优先
4. **最新版本 > 旧版** — 框架/工具链有明确版本号的信息优先

## 搜索 query 模板

```
# 技术选型
"{option_A} vs {option_B} production case study 2025 2026"
"{option_A} {option_B} comparison benchmark site:github.com"

# 架构决策
"architecture decision record {topic} template"
"site:github.com ADR {topic}"

# 系统设计
"system design {topic} scalability tradeoffs"
"how {company} scaled {system} engineering blog"

# 可靠性/SRE
"site:sre.google {topic}"
"incident postmortem {topic} lessons learned"
```

## 该领域特有 Anti-Pattern

| 反模式 | 症状 | 应对 |
|---|---|---|
| **Resume-Driven Architecture** | 选型理由全是 hype 词，无 tradeoff 分析 | 要求列出"放弃的替代方案及理由" |
| **Over-Engineering** | 为 <1000 用户设计 Google-scale 架构 | 标注"当前规模不需要"，区分现在 vs 未来的需求 |
| **Vendor Lock-in Blindness** | 全部来源来自同一云厂商 | 强制找 ≥1 独立第三方或竞品视角 |
| **No Numbers** | 声称"更快/更好"但无量化数据 | 要求 p99 latency / throughput / cost per unit |

## 权威来源白名单

- cloud.google.com/architecture
- docs.aws.amazon.com/wellarchitected
- learn.microsoft.com/en-us/azure/well-architected
- sre.google
- github.com/donnemartin/system-design-primer
- github.com/joelparkerhenderson/architecture-decision-record
- engineering.linkedin.com / engineering.fb.com / netflixtechblog.com
- infoq.com (peer-reviewed 架构文章)
