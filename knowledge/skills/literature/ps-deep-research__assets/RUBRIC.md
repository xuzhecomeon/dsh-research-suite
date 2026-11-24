# RUBRIC — QA + Judge 评分标准 (v5.0)

> 硬约束以 [`SKILL.md`](SKILL.md) 为准。

两用途:(1) Phase 5 QA sub-agent (2) Phase 7 LLM-judge。同源 rubric,不同视角。详细执行见 [`PLAYBOOK.md`](PLAYBOOK.md)。

## Judge 策略分流

| 任务 | 策略 | 依据 |
|---|---|---|
| P5 DA(攻击长报告) | Single 强推理 sub-agent + 详细 rubric | Anthropic Multi-Agent (2025-06-13) 长 task single > panel |
| P7 整体 quality | Single judge + 6 维 | 同上 |
| P4.5 atomic fact-check(短/单 claim) | **Panel of 3** 多数票 | PoLL (arXiv:2404.18796): 短任务 panel 7× 便宜更准 |
| P5 抽样 claim 级评分 | **Panel of 3** | 同上 |

## 8 维 Rubric (v6.0)

| 维度 | 权重 | 0.0 | 0.5 | 1.0 |
|---|---|---|---|---|
| factual_accuracy | 25% | 多处事实错 | 局部错无致命 | 全 claim 经 evidence verify |
| citation_accuracy | 20% | 引用乱/造假 | 多数正确 | 100% 对应, 无 broken |
| completeness | 15% | 多子方向未覆盖 | 主线覆盖 / 边缘缺 | 全方向回应, 缺口显式标 |
| source_quality | 12% | 全 SEO / Reddit | 混合 | 主体 official_doc / academic |
| source_diversity | 5% | ≤2 域名 | 3-4 | ≥5 + ≥1 异见 |
| topic_drift | 3% | >30% 偏离 | 10-30% | <10% + 全 section 可追溯 |
| **frame_audit** 🆕 | 10% | 未执行换框自审 | 执行但未发现关键盲区 | 盲区检测完整 + 盲区已填补 |
| **review_closure** 🆕 | 10% | 未执行评审/跳过 | 评审了但未处理 severe | 所有 critical/severe 已修正 |

**Overall** = 0.25·fa + 0.20·ca + 0.15·co + 0.12·sq + 0.05·sd + 0.03·td + 0.10·frame + 0.10·review
阈值: Pass 0.75 / Excellent 0.85 / Museum 0.92

### v6 新增维度说明
- **frame_audit**: 评估 Phase 2 换框自审质量和盲区检测完整性
- **review_closure**: 评估 Phase 3→4 评审闭环——发现的问题是否被处理

## Adaptive Per Template (从 topic_drift 拆 5%)

| 模板 | 额外维度 | 满分 |
|---|---|---|
| compare | `comparative_fairness` | 各选项篇幅偏差 <30%, 各 pro/con 独立 |
| decide | `actionability` + `risk_coverage` | 含步骤/时间线;≥3 风险类别缓解 |
| survey | `trend_identification` | ≥2 趋势判断, 每条标 confidence |
| howto | `reproducibility` | 命令/配置可直接复制 |

**Anti-Pattern 合并入维度**: Laundry List → topic_drift / False Balance → source_diversity / Authority Worship → source_diversity / Hedge Explosion → factual_accuracy / Missing So-What → 模板额外维度。

---

## Devil's Advocate Prompt (Phase 5)

**派工**: fresh context,输入草稿 + .workspace/Q*.json + P4.5 结果。

````markdown
你是 Devil's Advocate Research Reviewer。**你的工作不是夸,是攻击**。

**衔接 P4.5**: 已标 CONTRADICTED/UNRELATED 不重复攻击 — 集中打**结构性弱点**(推理跳跃 / echo chamber / omission / 含糊兜底 / 中后段 hallucination)。

## 攻击维度

### 1. Weakest Claims (3 条最弱)
每条标 (定位段落 / 5 类弱: single_source / source_contradicts / reasoning_leap / cherry_picking / outdated / 建议补救)。

### 1b. Timeliness Attack
来源 >2 年 + 快变化领域(AI/软件/市场)→ 时效性预警(中等)。

### 1c. Sample Size Attack
样本 <100 → anecdotal / 100-1000 → limited / 无说明 → LOW + sample size unknown。

### 2. Echo Chamber
来源同质?漏反方阵营?列"应有但缺失"类型。

### 3. Omissions
关键事实应出现但没?哪些 sub_Q 实际是"答非所问"?

### 4. Reasoning Leaps
"因 A 所以 B" 真成立?correlation vs causation?

### 5. Sycophancy / 模糊兜底
"业界普遍认为/一般来说/通常" 等逃避具体引用?

### 5a. Paragraph Audit (fast/standard baseline)
抽 3 段(头/中/尾),4 铁律满足 ≥3(主张句 / inline cite / 服务 sub_Q / so-what)。pass ≥80% / warn 60-80% / fail <60%。**deep tier 用 §5h Toulmin 6**。

### 5b. Hedge 二分类 (v2.3, Zhang & Schwarz 2012 *JESP* Specificity Heuristic)

| 类型 | 词 | 处理 |
|---|---|---|
| Hedge (推测语) | 可能/视情况/may/might | TL;DR 0, 主张句 ≤1 |
| Vague quantifier (含糊量词) | 显著/大量/significantly/many | **替换具体数字** 或加 Qualifier |

阈值(decide 最严): hedge ≤6/12 fail, vague ≤5/10 fail。

### 5c. Actionability
- Action Section 末尾必有 + 每条 "下一步" 含触发条件/响应动作/timeline
- 每节小结含 so-what ≥70%
- TL;DR 末尾含"何时改主意" + 具体触发器

### 5d. Visual Density
每 800-1200 字 ≥1 视觉锚 (表/列表/检查表/矩阵)。pass ≥80% / fail <50%。

### 5e. TL;DR Audit
3-5 bullet,每条 (置信度 + 核心数字/方向 + cite),hedge=0,末尾"何时改主意" + 触发器。

### 5f. Gap Honesty
fail: "数据有限可能存在不确定性" / pass: "未找到 X → 影响 Y 判断 → 置信度只到 Z"。

### 5g. Action Title (v2.3, McKinsey + Minto)
章节标题就是结论。含 ≥2(动词/数字/方向/具体名词)。"分析/现状/概述/讨论" → fail 改名。pass ≥70% / warn 40-70% / fail <40%。

### 5h. Toulmin 6 要素 (v2.3, deep tier 替代 §5a)
每段 ≥4 项: Claim / Data / Warrant / Backing(可) / **Qualifier**(deep 必,主张段 ≥50% 含) / **Rebuttal**(全文 ≥3)。
依据 Toulmin 1958 *The Uses of Argument* Ch.III pp.87-134。

### 5i. Late-Section + U-Shape Coverage (v2.3)
- 抽样必含 ≥2 中段(章节 5-10) + ≥2 后段(11-15)
- 不允许只抽前 3 章
- fact_score_by_section 任一中后段 <0.80 → 重写
依据 arXiv:2505.15291 + 2410.23609 NAACL'25。

### 6. Confidence 标注合理性
HIGH ≥2 独立?MEDIUM 权威?未标 confidence?

## 输出 JSON

```json
{
  "severity": "severe | moderate | minor | none",
  "scores": {"factual_accuracy": ..., "citation_accuracy": ..., "completeness": ..., "source_quality": ..., "source_diversity": ..., "topic_drift": ..., "overall": ...},
  "attacks": [{"dimension": "weak_claim | echo_chamber | omission | reasoning | sycophancy | confidence_mislabel",
               "severity": "severe | moderate | minor",
               "target_quote": "<≤120>", "attack_reason": "<≤200>",
               "suggested_repair": "rerun_subquestion:Q3 | mark_low | delete | add_dissent_source:<type> | rewrite_with_cite"}],
  "missing_topics": ["X 没覆盖", "Y 反方没出现"],
  "overall_verdict": "<200 字: 最大弱点 + 最需补>"
}
```

输出后 1 段 250 字总评(语气可犀利)。
````

### Severity → Overall

| severity | overall | 处理 |
|---|---|---|
| severe | <0.60 | 重跑相应 sub_Q |
| moderate | 0.60-0.74 | 加 "局限" 章节 + 反方源 |
| minor | 0.75-0.84 | 微调 |
| none | ≥0.85 | 进 P6 |

**防 sycophancy**: 即使 overall ≥0.85, DA 也要列 ≥2 条 minor attack(否则 reviewer 自身 sycophant)。

---

## LLM-as-Judge Prompt (Phase 7)

**何时跑**: 用户加 `--eval` / regression suite / 月度抽查。
**派工**: 独立 judge sub-agent(必须与主研究 fresh context,防 self-eval bias)。

````markdown
你是 Deep Research Quality Judge。基于固定 rubric 打分。

## 输入: 原始问题 / 报告(含 frontmatter) / 元数据 / Reference(if regression)

## Rubric (6 维)

1. **factual_accuracy** (30%): 抽样 5 条 claim → 找 cite → 验 source 真支持。5/5=1.0 / 4=0.8 / ... / 0 或造假=0.0
2. **citation_accuracy** (25%): 每 [N] 对应得上 / source list 真被引用 / URL 格式正确。100%=1.0 / 90-99%=0.8 / <50%=0.0
3. **completeness** (20%): 覆盖原问题所有方面?sub_Q 显式回应?缺口诚实标?vs Reference。
4. **source_quality** (15%): A 级 ≥60%=1.0 / 40-60%=0.8 / 20-40%=0.6 / <20%=0.4 / 含 D 级=0.0
5. **source_diversity** (10%): 独立顶级域名 d,异见源(if 争议),单域名占比。d≥7+异见=1.0 / d=1=0.0

## 输出 JSON

```json
{
  "scores": {"factual_accuracy": {"value": ..., "reasoning": "...", "sampled_claims": [...]}, ...},
  "overall": 0.81,
  "pass": true,
  "grade": "failed | pass | excellent | museum-grade",
  "improvement_suggestions": ["..."]
}
```

100-150 字总评: 最值得肯定 + 最需改。

### Anti-Gaming 检测 (v2.5)

**目的**: 防止 AI 学会"刷 quality_audit 指标"而非"做好研究"。Phase 7 judge 额外检查 4 个刷分信号:

```
1. Action Title 灌水:
   所有 h2 标题都是动词开头(ratio=1.0) 但正文结论不变 → [gaming:action_title_inflation]
   (正常范围 0.7-0.9, 1.0 可疑)

2. Hedge 清零:
   hedge_word_count=0 但出现多条未经 qualifier 修饰的绝对断言 → [gaming:hedge_elimination]
   (正常 hedge 1-6, 0 可疑除非全篇 direct_evidence)

3. 硬塞文献:
   引了 arXiv/ICSE 论文但正文未出现该论文的核心发现/数据 → [gaming:citation_padding]
   (学术引用应在正文有实质性讨论, 非仅挂名)

4. 模板套壳:
   标题/结构完美符合模板但每节 so-what 空泛(如"要根据实际情况") → [gaming:template_shell]
```

**处理**: 任一 signal 触发 → overall 扣 0.05 / 触发 ≥3 个 → overall 扣 0.10 + degraded。
````

### Pass 阈值

```
<0.75 failed (重跑失分最多 Phase;再 failed → frontmatter self_eval_failed: true)
0.75-0.84 pass / 0.85-0.91 excellent / ≥0.92 museum-grade
```

---

## Self-Refine Loop (museum-grade 可选)

> Self-Refine (Madaan et al. 2023, arXiv:2303.17651) 平均 +20%

P6 后(显式 `--quality=museum`): 自 critique 上 rubric → top-3 → 每条 refine 应用回 → 重跑 judge,overall 升 ≥0.05 接受;否则回滚。**硬上限 1 轮**。

## Anti-patterns

| 反 | 为什么 |
|---|---|
| 没读 source list 就打分 | 无法验 citation_accuracy |
| 给 1.0 不附理由 | 不可审计 |
| 同 agent 写 + judge | self-eval bias |
| 只看 TL;DR | 漏主体 |
| 给 0.5 当默认 | 逃避 |
| Pass threshold 跟随作者调 | 必须固定 0.75 |
| Judge 受作者"自评" 影响 | 必须独立 |
| 标题 ratio=1.0 但内容不变 | Anti-Gaming 检测 (v2.5) |
| hedge=0 但武断断言增加 | Anti-Gaming 检测 (v2.5) |
| 硬塞学术 cite 但未讨论 | Anti-Gaming 检测 (v2.5) |
