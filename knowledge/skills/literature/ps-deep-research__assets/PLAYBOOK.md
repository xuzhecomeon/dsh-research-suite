# PLAYBOOK (v6.0)

四阶段递归研究操作手册。硬约束以 [`SKILL.md`](SKILL.md) 和 [`ARCHITECTURE_v6.md`](ARCHITECTURE_v6.md) 为准。

---

## 执行概览

```
Phase 1: 好奇循环     → 探索生态，发现维度
Phase 2: 深度推理     → 换框自审，盲区检测，形成判断
Phase 3: 同行评审     → 独立对抗验证
Phase 4: 采纳优化     → 逐条修正
Phase 5: 输出报告     → 顾问级交付
```

---

## Phase 1：好奇循环

### 进入条件
- 用户触发 deep-research
- 或被 Phase 2/3/4 作为子循环 spawn

### 操作流程

```
Round 0 — 极宽搜索（建立初始生态图）
─────────────────────────────────────
主 agent: 生成 2-3 条极宽 query（无产品名/公司名）
         例: "AI coding agent company landscape 2026"
              "lesser known open source AI coding tools 2026"
         → 调 deep-research(topic, scope="broad")
         → 返回 → 建立初始实体图和分类维度

Round 1+ — 结构化扩展
─────────────────────────────────────
1. 主 agent: 基于已有框架，生成 3-6 个 curiosity_questions
   - 使用 v5 A-F 六维度作为初始模板（可动态增减）
   - 维度 C 强制 ≥2 种公司类型分搜
   - query 不含具体产品名/公司名

2. 主 agent: 标注每个 question 类型
   [core] → 影响中央判断 → 2 sub-agent
   [fill] → 填充性覆盖   → 1 sub-agent
   [verify] → 验证性搜索 → 1 sub-agent
   每轮 [core] ≤2 个

3. 🔴 同帧并行 spawn:
   每个 question → 1 次 deep-research 调用
   [core] question → 2 次 deep-research 调用（不同 query seeds）
   deep-research 内部: spawn researcher sub-agent → 搜+读+摘录 → 返回 findings

4. 综合（所有返回后）:
   - 跨 sub-agent URL 去重
   - [core] 方向: 2 个 sub-agent 的 findings 交叉验证
     - 一致 → 置信度提升
     - 矛盾 → 标 [conflict]，列为 Phase 2 深挖点
   - 更新: 实体图、分类维度、curiosity_questions 队列

5. 判断: 边际收益还值得吗？
   ┌─ 本轮发现新分类维度？ → 继续
   ├─ 本轮有实体改变理解？ → 继续
   ├─ 连续 2 轮无新维度且新实体全 filler？ → 收敛
   ├─ 达硬上限？(fast=1, std=3, deep=5) → 收敛
   └─ 否则 → 继续
```

### 退出条件
- 连续 2 轮无新分类维度
- 或新实体全 filler
- 或达硬迭代上限
- → 输出: `{实体图, 分类维度, 开放问题, [conflict] 标记}` → 进入 Phase 2

---

## Phase 2：深度推理循环

### 进入条件
- Phase 1 收敛
- 或被 Phase 2/3/4 作为子循环 spawn

### 🔴 换框自审（强制首步）

```
主 agent 回答以下 4 问（这是主 agent 少数亲自做的事之一）:

1. 我目前用什么分类框架理解这个领域？
2. 如果换一个学科/市场/视角，会用什么不同框架？
3. 有没有「我根本不知道存在的类别」？
4. 我的分类框架本身有哪些盲区？

输出: {已发现盲区, 需填补方向, 需深挖矛盾}
```

### 操作流程

```
每轮:
1. 换框自审 → 产出盲区 + 矛盾 + 弱支撑列表

2. 标注类型:
   [core] 盲区/矛盾 → 2 sub-agent
   [fill] 盲区/矛盾 → 1 sub-agent
   [verify] 弱支撑    → 1 sub-agent

3. 🔴 同帧并行 spawn:
   [core] 盲区     → 2× 子好奇循环 (Phase 1)
   [fill] 盲区     → 1× 子好奇循环
   [core] 矛盾     → 2× 子深度推理 (Phase 2)
   [fill] 矛盾     → 1× 子深度推理
   [verify] 弱支撑 → 1× 验证搜索

4. 综合（所有返回后）:
   - 交叉验证 [core] 方向
   - 更新 Central Thesis + 反事实
   - 标注每个结论的置信度 (HIGH/MEDIUM/LOW)
   - 检查: 每个核心结论 ≥2 独立来源？

5. 自我拷问:
   - 「这个判断有没有我不敢质疑的假设？」
   - 「如果判断是错的，最可能因为哪个假设不成立？」
   - 「有没有第 3 种解释我没考虑到？」

6. 再次换框自审 → 有新盲区？→ 继续 / 无 → 收敛
```

### 退出条件
- 换框自审无新发现
- Central Thesis 可证伪 + 每个核心结论 ≥2 源
- 反方视角已充分纳入（非 echo chamber）
- 或达硬上限（≤4 子循环）
- → 输出: `{Central Thesis, 反事实, 置信度, 证据链}` → 进入 Phase 3

---

## Phase 3：同行评审

### 进入条件
- Phase 2 收敛

### 🔴 必须独立 sub-agent

主 agent 不得自审。派独立 sub-agent（fresh context），只传:
- Phase 2 的核心判断 + 证据摘要
- 关键实体和维度
- 盲区检测结果

### 推荐并行模式 (std/deep)

```
同帧 spawn 2-3 个 reviewer:

Reviewer A — 证据可靠性:
  "抽样 3-5 条核心 claim，验证 source 是否真实支撑。
   找到置信度最低但被当作事实陈述的 claim。"

Reviewer B — 逻辑与框架:
  "检查假二分、范畴错误、循环论证。
   检查分类框架是否有遗漏。"

Reviewer C — 覆盖度与遗漏:
  "检查 echo chamber、利益相关方遗漏、'不做'选项。
   可 spawn 子好奇循环验证。"
```

### 输出

```yaml
review_output:
  attacks: [{claim_id, severity: critical|severe|moderate|minor, attack_vector, evidence}]
  echo_chamber_detected: boolean
  missing_perspectives: [string]
  logic_flaws: [string]
  overall_verdict: pass | conditionally_pass | needs_revision
```

### 退出条件
- overall_verdict: pass 或 conditionally_pass
- 或 2 轮评审
- → 进入 Phase 4

---

## Phase 4：采纳与优化

### 操作流程

```
1. 读取 Phase 3 评审报告

2. 分类处理:
   critical + severe → 必须处理
   moderate → 处理或标 known-limitation
   minor → 自主决定

3. 🔴 同帧并行 spawn 补证据/重新论证:
   所有需要补证据的条目 → spawn 子好奇循环
   所有需要重新论证的条目 → spawn 子深度推理

4. 逐条修正:
   - 改变结论 → 更新 Central Thesis + 反事实
   - 弱支撑 → 加引用
   - 边界不清 → 加 Qualifier
   - 证据不足 → 降置信度 + 标 [uncertain]
   - 不修 → 标 [known-limitation]

5. 可选: 再次 Phase 3 评审
```

### 退出条件
- 所有 critical+severe 已处理
- moderate 已处理或标 known-limitation
- → 进入 Phase 5

---

## Phase 5：输出报告

从研究者切换到写作者。遵循 [`WRITING_STYLE.md`](WRITING_STYLE.md) 和 [`REPORT_TEMPLATES.md`](REPORT_TEMPLATES.md)。

### 输出结构
1. Central Thesis（一句）+ 反事实
2. 核心发现（按论证逻辑组织）
3. 竞争格局/对比分析（如适用）
4. 风险与反方视角
5. 顾问判断 + 可执行下一步
6. 信息缺口标注
7. 追问钩子

### 质量自检
- 跑 `hooks/verify.sh scan <report.md>`
- Logic Self-Check 6 项（见下方）

---

## Logic Self-Check（6 项）

| # | 检查项 | 判据 |
|---|---|---|
| 1 | 默认值陷阱 | 推荐配置时穷举了所有选项？ |
| 2 | 选项完备性 | ≥2 选项含 fallback？ |
| 3 | 假二分 | 是否将连续谱系简化为二选一？ |
| 4 | 范畴错误 | 不同层面概念是否放同维比较？ |
| 5 | 循环论证 | 结论是否依赖自身？ |
| 6 | 未检验假设 | 隐含前提是否已声明？ |

---

## 递归规则

```
Phase 2 可 spawn → Phase 1 (子好奇循环)
       可 spawn → Phase 2 (子深度推理)

Phase 3 可 spawn → Phase 1 (验证性搜索)
       可 spawn → Phase 2 (深挖矛盾)

Phase 4 可 spawn → Phase 1 (补证据)
       可 spawn → Phase 2 (重新论证)

递归深度硬上限: fast≤1, standard≤2, deep≤3
```

---

## Dispatch Gate（每次 spawn 子任务前）

```
🔴 Dispatch Gate:
[ ] 所有子任务已标注类型？([core]/[fill]/[verify])
[ ] [core] 方向 ≤2 个？
[ ] 所有独立子任务同帧发出？（不等不串行）
[ ] 每个 deep-research 调用传了 curiosity_questions？
[ ] 主 agent 本轮不亲自搜/读？
```

---

## Researcher Output Validator

deep-research 工具内部使用。主 agent 收到 findings 后:
- 跑 `python3 hooks/validate_researcher_output.py <output.json> --json`
- fail → 退回重出（最多 1 次）
- warn（resilience 不达标）→ 放行标 warning
- pass → 放行

---

## 中英双语

topic 含 [中国/国内/A股/港股/政策] → Phase 1 Round 0 中英各一轮。

---

## Frontmatter

```yaml
quality_audit:
  declared_tier: deep
  actual_tier: deep
  degraded: false
  degradation_reasons: []
  duration_minutes: 47
  phase1_rounds: 3
  phase2_sub_loops: 2
  phase3_reviewers: 3
  phase3_verdict: pass
  total_subagents_spawned: 12
  total_searches: 23
  total_extracts: 18
  official_sources: 6
  dissent_sources: 2
  newest_source_date: "2026-06-30"
  geographic_coverage: ["CN", "US", "EU"]
  word_count: 4500
```

---

## 参考

- 架构设计: [`ARCHITECTURE_v6.md`](ARCHITECTURE_v6.md)
- 硬约束: [`SKILL.md`](SKILL.md)
- 写作标准: [`WRITING_STYLE.md`](WRITING_STYLE.md)
- 模板骨架: [`REPORT_TEMPLATES.md`](REPORT_TEMPLATES.md)
- 评分标准: [`RUBRIC.md`](RUBRIC.md)
- 版本演进: [`CHANGELOG.md`](CHANGELOG.md)

---

**版本**: v6.0。硬约束以 SKILL.md 和 ARCHITECTURE_v6.md 为准。**最后更新**: 2026-06-30
