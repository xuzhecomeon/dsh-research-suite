# Expert: General (Fallback)

> **来源**: PLAYBOOK researcher prompt 精炼 + 通用研究质量维度（权威性 / 时效性 / 多源一致 / 反方）。
> 当研究主题不匹配任何内置领域 expert 时使用此模板。

## 评价标准

1. **权威性**: official_doc > academic > known blog > community
2. **时效性**: 快速变化领域优先 12 个月内来源
3. **多源一致**: ≥2 独立来源确认 → HIGH confidence
4. **反对意见**: 争议主题必须包含反方来源

## 搜索 query 模板

```
# 综述型
"{topic} comprehensive overview 2025 2026"
"state of {topic} survey"

# 比较型
"{A} vs {B} comparison objective analysis"

# 实操型
"how to {task} best practices production guide"

# 观点型
"{topic} controversy debate different perspectives"
```

## 通用 Anti-Pattern

| 反模式 | 应对 |
|---|---|
| 信息茧房（同域名重复） | source diversity ≥3 独立域名 |
| SEO 内容农场 | authority ranking 优先 |
| 过时信息 | 标注来源日期，>2 年降权 |
| 无引用主张 | 强制 claim-evidence 追溯 |

## 通用权威来源

- 官方文档（.gov / .edu / vendor 官方 domain）
- Wikipedia（线索，非结论来源）
- arXiv / 顶级会议论文
- 知名技术博客（需交叉验证）
