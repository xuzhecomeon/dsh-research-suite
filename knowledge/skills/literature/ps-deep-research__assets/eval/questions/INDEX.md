# L1 Regression Question Set (v5.0)

12 题覆盖 4 模板 × 3 难度。每题固定 pass criteria，禁止根据输出回调阈值。

## 题目清单

### SURVEY

| ID | 难度 | 题目 | 关键词 | 测试重点 |
|---|---|---|---|---|
| S1 | easy | 2026年国内AI编程助手市场有哪些主要玩家？各自定位是什么？ | 生态/格局/市场 | Discovery Bootstrap + 生态分层 |
| S2 | medium | 2025-2026年大模型上下文窗口扩展的主流技术路线有哪些？各自的代表模型和取舍 | 技术路线/对比 | 技术深度 + 多路线覆盖 |
| S3 | hard | 具身智能（Embodied AI）在2024-2026年的关键进展、主要参与者和商业化现状 | 前沿/跨域 | 信息来源稀疏 + 需要区分 hype vs 实质 |

### COMPARE

| ID | 难度 | 题目 | 关键词 | 测试重点 |
|---|---|---|---|---|
| C1 | easy | 2026年前端主流框架（React/Next.js vs Vue/Nuxt vs Svelte/SvelteKit）对比：生态、性能、学习曲线 | 选型/对比 | 多维度矩阵 + 各选项 fair coverage |
| C2 | medium | Turbopack vs Vite vs Rspack 在2026年的构建性能、生态兼容性和生产可用性对比 | 技术对比/benchmark | benchmark 数据交叉验证 + 版本时效 |
| C3 | hard | 国内RAG场景下主流向量数据库（Milvus/Qdrant/Weaviate/Chroma/Elasticsearch）对比：性能、成本、运维复杂度 | 选型/对比/深度 | 多维度 + 中文场景 + 反方观点 |

### DECIDE

| ID | 难度 | 题目 | 关键词 | 测试重点 |
|---|---|---|---|---|
| D1 | easy | 小型外贸公司（<10人）2026年应该自建Shopify独立站还是专注亚马逊平台？ | 商业决策 | 选项≥2 + 风险登记 + 决策触发器 |
| D2 | medium | 2026年个人开发者应该订阅GitHub Copilot还是Cursor Pro？从功能、成本、生态整合角度分析 | 选型/投资 | 选项完备性 + 时效性 + 反方 |
| D3 | hard | 中型SaaS公司2026年核心后端应该继续自建Kubernetes集群还是迁移到托管云平台（如AWS Fargate/GCP Cloud Run）？结合成本结构、运维负担和长期锁定风险 | 架构决策 | CFA 5要素 + 反方观点 + 风险登记 + 成本/TCO数据 |

### HOWTO

| ID | 难度 | 题目 | 关键词 | 测试重点 |
|---|---|---|---|---|
| H1 | easy | 如何为Next.js项目配置从GitHub Actions到Vercel的CI/CD流水线（含lint/test/deploy）？ | 配置/教程 | 步骤可复现 + 命令可直接复制 |
| H2 | medium | 如何在现有React SPA项目中渐进式迁移到Next.js App Router？给出分阶段方案和每阶段验证标准 | 迁移/操作指南 | 步骤分解 + 风险 + 回滚方案 |
| H3 | hard | 如何从零训练一个垂直领域（法律/医疗）的中文大模型：数据准备、基座选型、微调策略、评估和部署全流程 | 训练/全流程 | 多阶段 + 资源估算 + 常见陷阱 |

## Pass Criteria（固定，禁止回调）

### 单题通过条件

```
overall ≥ 0.75（按 RUBRIC.md 6维加权）
factual_accuracy ≥ 0.70
citation_accuracy ≥ 0.70
无 citation 造假（一票否决）
无 [single_option_decide]（decide 模板）
无未处理的反方缺失（dissent_sources < 1 → fail）
```

### 套件通过条件

```
≥10/12 题 overall ≥ 0.75
0 题 overall < 0.55
平均 factual_accuracy ≥ 0.80
citation 造假 = block release
```

### 模板维度要求

| 模板 | 额外判定维度 | pass 阈值 |
|---|---|---|
| survey | trend_identification | ≥ 0.70 |
| compare | comparative_fairness | ≥ 0.70 |
| decide | actionability + risk_coverage | 均 ≥ 0.70 |
| howto | reproducibility | ≥ 0.75 |

## 运行命令

```bash
# 单题
~/.claude/skills/deep-research/hooks/verify.sh scan <report.md> --json

# 全量 regression（未来）
# for q in questions/*.md; do
#   /deep-research "$(cat $q)" --quality=deep --eval --output results/$(basename $q .md)/
# done
```

## 目录结构

```
eval/
├── questions/
│   ├── INDEX.md          ← 本文件
│   ├── S1-*.md ... S3-*.md
│   ├── C1-*.md ... C3-*.md
│   ├── D1-*.md ... D3-*.md
│   └── H1-*.md ... H3-*.md
├── baselines/            ← 首次通过后的报告作为 baseline
└── results/              ← 每次回归的输出（不提交，太大）
```

## 版本记录

- **v5.0** (2026-05-27): 初始 12 题创建。尚未运行，无 baseline。
