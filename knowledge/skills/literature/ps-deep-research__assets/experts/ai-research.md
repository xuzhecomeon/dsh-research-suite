# Expert: AI & LLM Research

> **权威来源**:
> - `anthropics/anthropic-cookbook` — Anthropic 官方最佳实践
> - `openai/openai-cookbook` — OpenAI 官方示例与指南
> - `langchain-ai/open_deep_research` (11.5k★) — 深度研究 agent 参考实现
> - `microsoft/generative-ai-for-beginners` (70k★) — 微软 AI 课程

## 评价标准

1. **官方 API 文档 > 第三方教程** — provider 官方 doc 是最高权威
2. **有 benchmark 数据的 > 主观评价** — 量化对比优先
3. **最近一年 > 1年前** — AI 领域变化极快，一年前的内容可能已过时
4. **独立 benchmark > 厂商自报** — LMSYS Chatbot Arena / GAIA / BrowseComp 等第三方评测优先

## 搜索 query 模板

```
# LLM provider 对比
"{provider} enterprise SLA SOC2 HIPAA compliance 2026"
"{provider_A} vs {provider_B} pricing benchmark 2026"

# 技术实践
"site:docs.anthropic.com {topic}"
"site:platform.openai.com {topic}"
"RAG best practices production 2026"

# 研究前沿
"site:arxiv.org {topic} 2025 2026"
"state of {ai_subfield} 2026 survey"

# Agent 架构
"multi-agent system architecture production 2026"
"deep research agent benchmark evaluation 2025 2026"
```

## 该领域特有 Anti-Pattern

| 反模式 | 症状 | 应对 |
|---|---|---|
| **Benchmark Shopping** | 选择性地引用对某个模型有利的 benchmark | 交叉引用 ≥2 独立评测（LMSYS + GAIA + BrowseComp） |
| **Demo-Driven Claims** | 基于 demo/toy example 声称 production readiness | 要求标注"无生产案例验证" |
| **Vendor Hype** | 来源全是某厂商的 marketing blog | 强制找 ≥1 独立第三方评测或用户社区反馈 |
| **No Cost Analysis** | 只比较能力，不比较 token cost / latency | 每条 provider 对比必须含 cost 维度 |

## 权威来源白名单

- docs.anthropic.com / platform.openai.com / ai.google.dev
- arxiv.org (AI/CL/LG 分类)
- lmsys.org (Chatbot Arena)
- github.com/anthropics/anthropic-cookbook
- github.com/openai/openai-cookbook
- github.com/langchain-ai/open_deep_research
- huggingface.co/spaces (open LLM leaderboard)
