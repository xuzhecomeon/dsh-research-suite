# Deep Research v6 — 架构设计

> **设计原则**：研究不是一条流水线，而是四个可递归组合的研究阶段。deep-research 不是 orchestrator，是各阶段中按需调用的工具。

---

## 1. 范式转换：v5 → v6

| 维度 | v5（当前） | v6（目标） |
|---|---|---|
| **核心隐喻** | Pipeline：一次性顺序执行 | 四阶段递归研究：探索 → 推理 → 评审 → 优化 |
| **发现模式** | 被动：A-F 六维度搜，缺口标 `[gap]` | 主动：好奇循环广泛探索 → 深度推理主动检测盲区 → 同行评审对抗验证 |
| **框架演化** | 固定：A-F 六维度一次性定义 | 动态：深度推理阶段主动检测框架盲区，可触发子好奇循环补全 |
| **停止条件** | REFLECT 饱和判断 | 各阶段有独立收敛条件 + 硬迭代上限 |
| **deep-research 角色** | 全流程 orchestrator（monolith） | 可调用工具——各阶段按需 invoke |
| **主 agent 职责** | 协调器 | 研究者——在每个阶段有清晰的角色切换 |

---

## 2. 架构总览：四阶段递归研究

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     主 agent：研究者（角色随阶段切换）                       │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Phase 1: 好奇循环（Curiosity Loop）                              │    │
│  │  目标：广泛探索，建立生态图，发现分类维度                            │    │
│  │  角色：探索者                                                      │    │
│  │  停止：边际收益 < 边际成本                                          │    │
│  │  输出：{实体图, 分类维度, 开放问题, 确信度}                          │    │
│  └──────────────────────────┬──────────────────────────────────────┘    │
│                             ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Phase 2: 深度推理循环（Deep Reasoning Loop）                     │    │
│  │  目标：分析、综合、盲区检测、形成判断                                │    │
│  │  角色：分析者                                                      │    │
│  │  能力：                                                           │    │
│  │    - 换框自审（强制）：我用的分类框架遗漏了什么？                     │    │
│  │    - 可 spawn 子好奇循环（填补盲区）                                │    │
│  │    - 可 spawn 子深度推理循环（深挖子问题）                           │    │
│  │  停止：所有盲区已填补 + 判断稳定且可证伪                              │    │
│  │  输出：{核心判断, 反事实, 置信度, 证据链}                            │    │
│  └──────────────────────────┬──────────────────────────────────────┘    │
│                             ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Phase 3: 同行评审（Peer Review）                                  │    │
│  │  目标：对抗性验证，找出弱点、矛盾、遗漏                              │    │
│  │  角色：反对者（独立 sub-agent，fresh context）                      │    │
│  │  能力：                                                           │    │
│  │    - 攻击最弱 claim                                               │    │
│  │    - 检测 echo chamber                                            │    │
│  │    - 可 spawn 子好奇循环（验证性搜索）                               │    │
│  │    - 可 spawn 子深度推理循环（深挖矛盾）                             │    │
│  │  停止：所有 severe 问题已处理 + 无新实质性攻击                        │    │
│  │  输出：{攻击向量, 严重度, 建议修正}                                  │    │
│  └──────────────────────────┬──────────────────────────────────────┘    │
│                             ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Phase 4: 采纳与优化（Adopt & Optimize）                           │    │
│  │  目标：根据评审意见修正判断、补充证据、优化论证                        │    │
│  │  角色：编辑者                                                      │    │
│  │  能力：                                                           │    │
│  │    - 对 severe 问题逐条修正                                        │    │
│  │    - 可 spawn 子好奇循环（补充缺失证据）                             │    │
│  │    - 可 spawn 子深度推理循环（重新论证争议结论）                     │    │
│  │  停止：所有 severe/moderate 已处理 + 二次评审通过                    │    │
│  │  输出：{修正后的判断, 证据补丁, 修正记录}                            │    │
│  └──────────────────────────┬──────────────────────────────────────┘    │
│                             ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Phase 5: 输出报告                                                 │    │
│  │  目标：从研究者状态切换到写作者状态，交付顾问级报告                    │    │
│  │  输出：最终报告（含 Central Thesis + 反事实 + 置信度 + 下一步）       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### 递归关系

```
Phase 2（深度推理）──可 spawn──→ Phase 1（子好奇循环）
        │                              │
        │                    ┌─────────┘
        │                    ↓
        │             Phase 2（子深度推理循环）
        │                    │
        │           ┌────────┘
        │           ↓
        │    Phase 1（子好奇循环）
        │           ...
        │
Phase 3（同行评审）──可 spawn──→ Phase 1（验证性搜索）
        │                   ──→ Phase 2（深挖矛盾）
        │
Phase 4（采纳优化）──可 spawn──→ Phase 1（补证据）
                               ──→ Phase 2（重新论证）
```

**递归深度硬上限**：fast ≤ 1, standard ≤ 2, deep ≤ 3 层嵌套。

### Workflows 编排铁律

```
🔴 每个 Phase 内，所有独立的子任务必须同帧并行 spawn，不串行等待。

Phase 1（好奇循环）每轮：
  主 agent 生成 N 个 curiosity_questions
  → 同帧 spawn N 个 deep-research 工具调用（每个内部走 sub-agent）
  → 等待全部返回 → 综合

Phase 2（深度推理）每轮：
  主 agent 换框自审 → 产出 {盲区 × K, 矛盾 × M, 弱支撑 × J}
  → 同帧 spawn K + M + J 个子任务
  → 等待全部返回 → 综合 → 更新判断

Phase 3（同行评审）：
  可同帧 spawn 2-3 个独立 reviewer sub-agent（不同视角）
  → 等待全部返回 → 合并去重 → 输出评审报告

Phase 4（采纳优化）：
  多条独立的补证据任务 → 同帧 spawn
  → 等待全部返回 → 逐条处理

### 冗余策略（防浪费）

```
🔴 不是所有子方向都值得 2 个 sub-agent——区别对待：

核心方向（直接影响 Central Thesis 或分类框架）：
  → 派 2 个独立 sub-agent，同种子问题，不同 query seeds
  → 返回后交叉验证——一致 → 高置信度，不一致 → 标记 [conflict] 并追因
  → 每个 Phase 每轮核心方向 ≤2 个（避免冗余爆炸）

非核心方向（填充性信息、验证性搜索、边缘覆盖）：
  → 只派 1 个 sub-agent
  → 原则：能 1 个搞定的不派 2 个

主 agent 派工前必须标注：
  [core] direction_A → 2 sub-agents
  [fill] direction_B → 1 sub-agent
  [verify] direction_C → 1 sub-agent
```

🛑 反模式：
  ❌ 主 agent 一个一个串行调 sub-agent（如先搜 A，等结果，再搜 B）
  ❌ 所有子方向无差别派 2 个——非核心方向是浪费
  ✅ 主 agent 把所有独立搜索需求一次性发出，同时等结果
  ✅ 核心方向 2 个独立验证，其余 1 个
```

---

## 3. Phase 1：好奇循环（Curiosity Loop）

### 3.1 目标

广泛探索，不设预设分类框架。让搜索结果本身揭示「这个领域怎么分」。

### 3.2 角色分工（🔴 核心约束）

```
主 agent = 协调者：发问、派工、综合、判断（不亲自搜/读 ≥3 个来源）
sub-agent = 执行者：搜、读、摘录（不带判断，只返回结构化发现）
```

**每轮 Curiosity Loop 的并行派工模式**：

```
主 agent: 发问 → 生成 3-6 条 curiosity_questions
              ↓
         同帧并行 spawn 多个 deep-research 工具调用
         （每个 deep-research 内部走 sub-agent 搜+读+摘录）
              ↓
         等待所有返回 → 综合发现 → 更新框架
              ↓
         判断边际收益 → 继续/收敛
```

### 3.3 循环体（主 agent 视角）

```
1. 发问：我现在最疑惑/最好奇/最不确定的是什么？
   → 生成 3-6 个 curiosity_questions（无产品名/公司名）

2. 🔴 并行派工（同帧 spawn，不等结果）：
   主 agent 先标注每个 curiosity_question 的类型：
   - [core] → 派 2 个独立 sub-agent（不同 query seeds，交叉验证）
   - [fill] / [verify] → 派 1 个 sub-agent
   
   所有 sub-agent 同帧发出。
   
   deep-research 工具内部：
   ├─ spawn researcher sub-agent（搜 + extract）
   ├─ researcher 返回结构化 findings
   └─ 返回 {findings, discovered_entities, new_questions, ...}

3. 综合（所有返回后）：
   - 跨 sub-agent 去重（同 source_url 合并）
   - 交叉验证（矛盾 findings → 标记 [conflict]）
   - 更新实体图和分类维度
   - 新产生的好奇问题 → 加入下一轮队列

4. 判断：边际收益还值得吗？
   - 值 → 回到步骤 1（用新 curiosity_questions）
   - 不值 → 收敛，进入 Phase 2
```

### 3.3 初始启动：极宽搜索（Round 0）

在进入结构化探索之前，先做 2-3 条极宽 query 摸清领域形状：

| # | 类型 | 例子 | 目的 |
|---|---|---|---|
| 1 | 领域全景 | `AI coding agent company landscape 2026` | 发现有什么 |
| 2 | 换框探索 | `autonomous software engineering vs code completion tools 2026` | 发现分类方式 |
| 3 | 边缘视角 | `lesser known open source AI coding tools alternatives 2026` | 避免只看到头部 |

这些 query 不做结构化预设——让搜索结果本身揭示领域结构。

### 3.4 结构化扩展（Round 1+）

基于 Round 0 的发现，用演化中的维度框架系统化搜索。v5 的 A-F 六维度作为初始模板（可动态增减）：

- 维度 A — 领先者/主流方案
- 维度 B — 挑战者/新兴者
- 维度 C — 地区性/独立玩家（**强制 ≥2 种公司类型分搜，如平台公司 + 模型公司**）
- 维度 D — 反方/失败案例
- 维度 E — 开源/独立/非商业生态
- 维度 F — 换框重搜（换分类框架，非换话题）
- 维度 G+ — 研究过程中涌现的新维度

### 3.5 收敛条件（→ Phase 2）

满足以下**任一**即进入 Phase 2（不需要全部满足）：

| 条件 | 判据 |
|---|---|
| 连续 2 轮未发现新分类维度 | 框架已稳定 |
| 连续 2 轮新实体全属 `impact: filler` | 只有填充性信息 |
| 硬迭代上限 | fast=1, standard=3, deep=5 轮 |
| 用户指定方向且探索已覆盖 | 不需要无限探索 |

---

## 4. Phase 2：深度推理循环（Deep Reasoning Loop）

### 4.1 目标

带着 Phase 1 产出的生态图和开放问题，做深度分析：形成判断、检测盲区、交叉验证。

### 4.2 🔴 换框自审（主 agent 执行，强制首步，不可跳过）

深度推理循环启动时必须先执行这一步。这是针对 v5 分类框架盲区问题的最小化精确修复。
**这是主 agent 少数亲自执行的步骤之一**——因为换框是元认知动作，sub-agent 没有足够的上下文来做。

```
换框自审（主 agent 强制执行）：

1. 我目前用什么分类框架理解这个领域？
2. 如果我是另一个学科/市场/视角的专家，会用什么不同的框架？
3. 有没有「我根本不知道存在的类别」？
4. 我的分类框架本身有哪些盲区？
```

换框自审产出：`{已发现盲区列表, 需要 spawn 子好奇循环的方向, 需要深挖的矛盾点}`

### 4.3 并行派工模式

```
主 agent: 换框自审 → 产出 {盲区, 矛盾, 弱支撑}
              ↓
         同帧并行 spawn：
         ├─ 子好奇循环 × N（填补盲区——每个盲区一个独立 sub-agent）
         ├─ 子深度推理循环 × M（深挖矛盾——每个矛盾一个独立 sub-agent）
         └─ 验证搜索 × K（核心结论只有 1 源 → 验证）
              ↓
         等待所有返回 → 综合 → 更新判断
              ↓
         再次换框自审（有没有新盲区？）
              ↓
         判断收敛 → 继续/进入 Phase 3
```

### 4.4 循环体（主 agent 视角）

```
1. 换框自审（主 agent 强制执行，见上）

2. 盲区检测：
   - 检查分类框架：是否有类别被遗漏？
   - 检查结论：哪些核心结论只有 1 个来源支撑？
   - 检查对立面：哪个方向的 findings 全同向？
   - 检查冲突：不同来源之间是否有矛盾？

3. 🔴 并行派工（同帧 spawn，所有子任务一起发）：
   主 agent 先标注每个子任务的类型：
   ┌─ [core] 盲区（影响 Central Thesis）→ spawn 2 个独立子好奇循环
   ├─ [fill] 盲区（填充性覆盖）→ spawn 1 个子好奇循环
   ├─ [core] 矛盾（可能推翻结论）→ spawn 2 个独立子深度推理
   ├─ [fill] 矛盾 → spawn 1 个子深度推理
   └─ [verify] 弱支撑 → spawn 1 个验证搜索 sub-agent

4. 综合（所有返回后）→ 更新 Central Thesis + 反事实 + 置信度

5. 自我拷问 → 回到步骤 1 或收敛
```

### 4.4 收敛条件（→ Phase 3）

| 条件 | 判据 |
|---|---|
| 所有盲区已填补（换框自审无新发现） | 框架完备 |
| Central Thesis 可证伪且置信度可标注 | 判断成熟 |
| 每个核心结论 ≥2 独立来源 | 证据充分 |
| 反方视角已充分纳入（非 echo chamber） | 视角平衡 |
| 硬迭代上限 | ≤ 4 个子循环（含子好奇 + 子推理） |

---

## 5. Phase 3：同行评审（Peer Review）

### 5.1 目标

对抗性验证。切出独立视角，攻击 Phase 2 的产出。

### 5.2 🔴 必须独立 sub-agent 执行（可并行多个视角）

主 agent 不能自己评审自己的工作（利益冲突）。Phase 3 必须派独立 sub-agent（fresh context），只接收：

- Phase 2 的核心判断 + 证据摘要（不是全部 findings）
- 关键实体和维度
- 盲区检测结果

**推荐并行模式**（standard/deep tier）：同帧 spawn 2-3 个 reviewer，各自从不同视角攻击：
- Reviewer A：证据可靠性（抽样验证 source 是否支撑 claim）
- Reviewer B：逻辑与框架（假二分、范畴错误、循环论证）
- Reviewer C：覆盖度与遗漏（盲区、利益相关方、反方视角）

三个 reviewer 返回后，主 agent 合并去重，输出统一评审报告。

### 5.3 评审内容

```
同行评审 sub-agent 任务：

1. 攻击最弱 claim：
   - 抽样 3-5 条核心 claim，验证 source 是否真实支撑
   - 找到置信度最低但被当作事实陈述的 claim

2. Echo chamber 检测：
   - 所有核心结论的来源是否来自同一生态位？
   - 是否有任何方向的 findings 100% 同向？

3. 遗漏检测：
   - 是否有重要利益相关方未覆盖？
   - 是否有「不做」选项未被考虑？
   - 是否有隐含时间窗口假设？

4. 逻辑审计：
   - 是否有假二分（将连续谱系简化为二选一）？
   - 是否有范畴错误（不同层面概念放在同维比较）？
   - 是否有循环论证？

5. 可 spawn 子好奇循环或子推理循环进行验证
```

### 5.4 输出

```yaml
review_output:
  attacks:
    - claim_id: string
      severity: critical | severe | moderate | minor
      attack_vector: string
      evidence: string
  echo_chamber_detected: boolean
  missing_perspectives: [string]
  logic_flaws: [string]
  overall_verdict: pass | conditionally_pass | needs_revision
  recommended_actions:
    - action: string
      priority: high | medium | low
```

### 5.5 收敛条件（→ Phase 4）

| 条件 | 判据 |
|---|---|
| `overall_verdict: pass` | 无 critical/severe |
| 所有 critical/severe 已标记为需要在 Phase 4 处理 | conditionally_pass |
| 硬上限 | 2 轮评审（第二轮验证修正） |

---

## 6. Phase 4：采纳与优化（Adopt & Optimize）

### 6.1 目标

根据评审意见，逐条修正。不是「全部照改」，而是「逐条判断是否采纳」。

### 6.2 处理逻辑

```
1. 读取 Phase 3 评审报告，逐条判断是否采纳：
   ├─ critical + severe → 必须处理
   ├─ moderate → 建议处理，可记录为 known limitation
   └─ minor → 自主决定

2. 🔴 需要补证据的条目 → 同帧并行 spawn 子好奇循环 sub-agent
   （不要一条一条串行补——把所有补证据需求一次性发出）

3. 需要重新论证的条目 → 同帧并行 spawn 子深度推理 sub-agent

4. 所有 sub-agent 返回后 → 逐条修正：
   ├─ 修正判断（改变结论）→ 更新 Central Thesis + 反事实
   ├─ 补充证据（弱支撑）→ 加引用
   ├─ 增加限定条件（边界不清）→ 加 Qualifier
   ├─ 标注不确定性（证据不足）→ 降置信度 + 标 [uncertain]
   └─ 记录为已知局限（不修）→ 标 [known-limitation]

5. 修正后可选再次评审（Phase 3 R2）
```

### 6.3 收敛条件（→ Phase 5）

| 条件 | 判据 |
|---|---|
| 所有 critical + severe 已处理 | — |
| moderate 已处理或标注为 known limitation | — |
| 如启动 Phase 3 R2 → `overall_verdict: pass` | — |

---

## 7. Phase 5：输出报告

### 7.1 目标

从研究者状态切换到写作者状态。不是 findings dump——是顾问级分析报告。

### 7.2 输出结构

```
1. Central Thesis（一句）+ 反事实
2. 核心发现（按论证逻辑组织，非按 sub_Q 罗列）
3. 竞争格局 / 对比分析（如适用）
4. 风险与反方视角
5. 顾问判断 + 可执行下一步
6. 信息缺口标注
7. 追问钩子
```

报告标准沿用 v5 的 `WRITING_STYLE.md` 和 `REPORT_TEMPLATES.md`。

---

## 8. 停止条件：各阶段独立 + 全局硬限制

### 8.1 各阶段收敛条件（汇总）

| 阶段 | 收敛条件 | 硬上限 |
|---|---|---|
| Phase 1 好奇循环 | 连续 2 轮未发现新维度 或 新实体全 filler | fast=1, standard=3, deep=5 轮 |
| Phase 2 深度推理 | 盲区填补完毕 + 判断可证伪 | ≤4 子循环 |
| Phase 3 同行评审 | overall_verdict: pass 或 conditionally_pass | 2 轮 |
| Phase 4 采纳优化 | 所有 critical/severe 已处理 | — |

### 8.2 全局硬限制

| 约束 | fast | standard | deep |
|---|---|---|---|
| 总时间 | ≤10min | ≤30min | ≤60min |
| 总递归深度 | ≤1 层 | ≤2 层 | ≤3 层 |
| 总搜索（全阶段） | ≤5 | ≤20 | ≤40 |
| 总 extract（全阶段） | ≤3 | ≤12 | ≤20 |

### 8.3 🟢 反停止信号（任意阶段命中 → 继续）

| # | 信号 | 直觉 |
|---|---|---|
| C1 | 发现新分类维度（改变了对领域的理解） | 框架在进化 |
| C2 | 新证据推翻或显著修正已有结论 | 结论在变化 |
| C3 | 某方向所有 findings 同向（echo chamber） | 缺反方 |
| C4 | 意外发现重要的未知实体（serendipity） | 追 |
| C5 | 核心结论只有 1 个来源 | 需验证 |

---

## 9. 工具接口：deep-research 作为可调用单元

### 9.1 调用契约

```yaml
deep-research:
  description: >
    对指定主题执行一轮聚焦的搜索+阅读，返回结构化发现。
    在四阶段的任意阶段中被主 agent 按需调用。

  input:
    topic: string
    scope: broad | focused
    phase: curiosity | deep_reasoning | peer_review | optimize
    known_dimensions: [{name, entities}]
    known_entities: [{name, type, needs_deep_dive, reason}]
    curiosity_questions: [string]     # 🔴 必填——无疑惑不搜索
    max_rounds: number
    freshness: "month" | "week" | "year"

  output:
    findings: [finding]
    discovered_dimensions: [{name, description, confidence, entity_count}]
    discovered_entities: [{name, type, confidence, impact, needs_deep_dive}]
    answered_questions: [string]
    new_questions: [string]
    framework_stable: boolean
    marginal_value: {new_dimensions, decision_affecting, filler}
    should_continue: boolean
```

### 9.2 调用时机

| 阶段 | 调用 deep-research 的场景 |
|---|---|
| Phase 1 | 需要批量探索时（≥3 个方向）；非 trivial 搜索 |
| Phase 2 | spawn 子好奇循环时；批量验证证据时 |
| Phase 3 | 验证评审 sub-agent 的怀疑时 |
| Phase 4 | 补充缺失证据时 |

### 9.3 不调用 deep-research 的场景

| 场景 | 做法 |
|---|---|
| 单次事实核实（≤2 搜索） | 主 agent 直接搜 |
| 搜索结果 80% 已见过 | 不搜——收敛 |
| 纯阅读 1-2 个页面 | 主 agent 直接 extract |

---

## 10. Tier 映射与并行度

| Tier | Phase 1 上限 | Phase 1 每轮并行 sub-agent | Phase 2 子循环 | Phase 3 | Phase 4 | 总搜索 |
|---|---|---|---|---|---|---|
| **fast** | 1 轮 | 1-2 并行 | 0 子循环 | 跳过 | 跳过 | ≤5 |
| **standard** | 3 轮 | 3-5 并行 | ≤2 子循环（并行 spawn） | 1-2 并行 reviewer | 处理 critical | ≤20 |
| **deep** | 5 轮 | 5-8 并行 | ≤4 子循环（并行 spawn） | 2-3 并行 reviewer | 处理 critical+severe | ≤40 |

**并行度说明**：
- Phase 1 每轮：curiosity_questions 的数量 = 并行 sub-agent 数。例如一轮 5 个疑惑 → 5 个 deep-research 工具同帧发出
- Phase 2 每轮：盲区数 + 矛盾数 + 弱支撑数 = 并行子任务数。最多不超过 tier 的 Phase 2 子循环上限
- Phase 3：2-3 个不同视角的 reviewer 并行（如一个攻击 evidence，一个攻击 logic，一个攻击 coverage）
- 所有并行 sub-agent 共享同样的 tier 约束（每次 deep-research 调用 ≤20 搜索 / ≤12 extract）

---

## 11. 与 v5 的关系

### 11.1 保留的 v5 资产

| v5 资产 | v6 映射 |
|---|---|
| Researcher Prompt 模板 + output schema | deep-research 工具内部保留 |
| Toulmin 写作标准 | Phase 5 报告写作 |
| WRITING_STYLE.md / REPORT_TEMPLATES.md | 不变 |
| 三 Tier（fast/standard/deep） | 映射到阶段上限（见第 10 节） |
| Freshness & Coverage Sweep | Phase 1 Round 1 固定组成部分 |
| 中英双语搜索 | Phase 1 首轮固定检查 |
| Dispatch Gate | deep-research 工具调用前自检 |
| Researcher Output Validator | deep-research 工具内部 |

### 11.2 明确移除的 v5 模式

| v5 模式 | 移除原因 |
|---|---|
| 主 agent 亲自执行 ≥3 次搜索 | 上下文污染；v6 必须走 deep-research 工具或 sub-agent |
| 一次性 A-F Bootstrap | 替换为 Phase 1 的好奇循环（迭代 + 框架演化） |
| 被动缺口标 `[gap]` | 替换为 Phase 2 的主动盲区检测 + 子好奇循环填补 |
| Pipeline 固定顺序 | 替换为四阶段的递归组合 |

---

## 12. 反模式

| ❌ | ✅ |
|---|---|
| 主 agent 亲手搜/读 ≥3 个来源（上下文污染） | 调 deep-research 工具或 spawn sub-agent |
| 主 agent 串行一个一个发 sub-agent（浪费时间） | 🔴 同帧并行 spawn——所有独立子任务一起发出 |
| 所有子方向无差别派 2 个 sub-agent（浪费资源） | 🔴 核心方向 2 个交叉验证，非核心 1 个，派工前标注 [core]/[fill]/[verify] |
| 主 agent 试图替代 sub-agent 做判断（"我觉得这个 finding 不对"） | 主 agent 只综合 sub-agent 返回的 findings，不越俎代庖 |
| Phase 1 的搜索 query 含具体产品/公司名 | 用描述性语言：「行业头部」「新兴挑战者」「地区替代方案」 |
| Phase 2 跳过换框自审直接进入分析 | 换框自审是强制首步——不可跳过 |
| Phase 3 主 agent 自己评审自己的工作 | 必须派独立 sub-agent（fresh context） |
| 把 deep-research 当「一键生成报告」调 | 它返回发现，不是报告——综合和判断在主 agent |
| 发现盲区后标 `[gap]` 跳过 | Phase 2 必须 spawn 子好奇循环填补 |
| sub-agent 返回 raw dump 原样转给用户 | 主 agent 提炼→综合→形成判断→再呈现 |
| 在循环中失去进度感 | 每阶段完成时 ≤1 句进度通知 |

### 主 agent 亲自做的（仅此 3 类）

| 可以亲自做 | 原因 |
|---|---|
| 发问（生成 curiosity_questions） | 需要全局上下文和元认知——sub-agent 没有 |
| 换框自审 | 需要跨 sub-agent 的综合视角——sub-agent 看不到全貌 |
| 综合 + 判断（从 sub-agent findings 形成 Central Thesis） | 这是研究的「决策层」——必须主 agent 拍板 |

其余一切搜索、阅读、摘录、验证、数据提取——全部走 sub-agent。

---

## 13. 文件变更计划

| 文件 | 变更 |
|---|---|
| `SKILL.md` | 重写：四阶段触发条件、调用契约、停止条件 |
| `PLAYBOOK.md` | 重写：各阶段操作手册、决策树、递归规则 |
| `ARCHITECTURE_v6.md`（本文） | 已完成 |
| `REPORT_TEMPLATES.md` | 小幅更新：输出包含盲区检测和评审记录 |
| `WRITING_STYLE.md` | 不变 |
| `RUBRIC.md` | 更新：评分项增加「换框自审」「盲区检测」「评审闭环」 |
| `CHANGELOG.md` | 新增 v6 条目 |
| `eval/` | 新增 v6 评估用例（分类框架盲区检测的反事实测试） |

---

## 14. 一句话总结

> **v5 = 工厂流水线（搜→读→写），v6 草案 = 好奇心循环（问→搜→重组），v6 终稿 = 四阶段递归研究：先广泛探索建立生态图（好奇），再深度推理检测盲区（推理），再对抗评审找出弱点（评审），再逐条修正优化论证（采纳），最后交付顾问级报告。每个阶段都可以递归调用前面的阶段——因为真正的研究不是在一条线上前进，而是在一张网上来回穿梭。**
