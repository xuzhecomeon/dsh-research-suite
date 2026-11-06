# R02 Model Comparison: Same Skill, Two Models, Two Worlds

> **日期**: 2026-05-26 | **Skill 版本**: v4.1 + v2.7.3（修复前，无 Dispatch Gate）
> **触发**: 同一研究任务（国内 AI 编程助手生态），同一 skill 同一版本，Claude 和 DeepSeek 产出天差地别

## 实验条件

| 条件 | 值 |
|---|---|
| Skill 版本 | deep-research v4.1 + v2.7.3 |
| 研究问题 | 2026 国内 AI 编程助手生态 — 最强性价比 + 最强能力 |
| Tier | deep |
| Claude 模型 | claude-opus-4-7 |
| DeepSeek 模型 | DeepSeek V4 Pro（通过 Copilot） |
| 是否有 Dispatch Gate | ❌ 无（v4.4 尚未创建） |

## 结果对比

| 维度 | Claude（5 researcher sub-agent） | DeepSeek（主 agent 一手包办） |
|---|---|---|
| **Researcher spawn** | 5（Q1-Q4 并行 + Q5 sweep） | 0 |
| **Workspace 文件** | Q1-Q5.json + pre_flight.yaml，164KB | 无 |
| **Pre-flight 声明** | ✅ 假设、反假设、禁止模式、成功标准 | ❌ 无 |
| **证据追溯** | 每个 claim 有 `[F-Qx-y]` ID → JSON source_url | 无 ID，数字无出处 |
| **反方搜索** | 6 个 first-hand reversal case | 0 |
| **关键事实遗漏** | — | MarsCode 已不存在、通义灵码改名 Qoder + 涨价 25%、Cursor 大陆断供 Claude |
| **反直觉发现** | Cursor Composer 2 底层 = Kimi K2.5 | 无 |
| **结论结构** | 分场景（能用海外/不能用海外/个人/国资），Toulmin 6 要素 + Falsifier 矩阵 | 单场景（"Comate 能力王，Trae 性价比王"） |
| **报告规模** | 498 行，37KB，43 sources | ~120 行，~10KB |
| **质量审计** | 完整 quality_audit 字段 | 无 |

## 根因分析

**不是 skill 设计问题。** 同一份 PLAYBOOK.md 写了 "supervisor (主 Claude) 派 researcher (Task tool, fresh context), 严格隔离"。Claude 读到就做了，DeepSeek 读到但跳过了。

三条根因：

1. **模型自律差距** — Claude 对"spawn sub-agent"这类的指令遵循更稳定；DeepSeek 倾向于"我能做就自己做"
2. **上下文利用模式** — Claude 在 Phase 2 读完 plan 后会自然推演"下一步需要 researcher"；DeepSeek 读到同样的文本但没有同样的推演
3. **无前置拦截** — v4.1 的所有质量检查在 Phase 6（事后审计），违规可以发生而不被阻止

## 教训

1. **Skill 质量上限 = 执行模型质量上限。** 不可能通过写得更好的 skill 文件让任何模型都产出 Claude 级别的深度研究
2. **面向最弱执行模型设计 skill 是合理的。** v4.4 的 Dispatch Gate 和自省锚点就是这种思路——"你其实不会做，所以我把你会跳过的每一步都写成硬性 gate"
3. **Skill 迭代应该用对比实验驱动。** 每次改 skill 后，同一问题用两个模型各跑一遍，对比差异。比纯读 skill 文本更能发现问题
4. **DeepSeek 做 deep research 需要更强的外部约束。** 它的强项是成本（~1/50），但需要 skill 设计补偿它的执行自律差距

## 后续行动

- [x] v4.4 Phase 2.8 Dispatch Gate（事前拦截）
- [x] v4.4 执行前自省（三个问题）
- [x] 本对比 case 写入 eval/
- [ ] R03 用 v4.4 重跑同一问题，验证改善幅度
- [ ] 建立 regression 基准：每版本用同一问题跑 Claude + DeepSeek，记录 gap
