# CHANGELOG

## v6.0 — 2026-06-30（架构级重构）

**触发**: v5 流水线架构遗漏 GLM/智谱 AI 案例暴露两个结构性问题——(1) Discovery Bootstrap 一次性 A-F 六维度无法发现「未知类别」，(2) 被动缺口标 `[gap]` 不追搜解疑。

**核心变更**:
1. **架构**: Pipeline → 四阶段递归研究（好奇循环 → 深度推理 → 同行评审 → 采纳优化 → 输出报告）
2. **deep-research 角色**: 全流程 orchestrator → 可调用工具
3. **Phase 2 新增换框自审**: 强制检测分类框架盲区
4. **Phase 3 同行评审必跑**: 独立 sub-agent 对抗验证（利益冲突隔离）
5. **并行优先**: 所有独立子任务同帧 spawn，[core] 方向 2 个交叉验证，其余 1 个
6. **停止条件**: REFLECT 清单 → 边际收益 vs 边际成本（多信号综合）

**文件变更**: SKILL.md 重写, PLAYBOOK.md 重写, ARCHITECTURE_v6.md 新增, RUBRIC.md 更新, REPORT_TEMPLATES.md 小幅更新

---

## v5.6.1 — 2026-06-02 (dogfood plugin-dev / skill-creator 审计后修)

**触发**: 装完官方 skill-creator + plugin-dev 后，用其 `skill-reviewer` agent + 两路独立审计本 skill（skill-creator 的 `quick_validate.py` 因本机缺 PyYAML 跳过）。两路**独立共识**指向同一缺陷：frontmatter description 零触发语义。

**修改**:

1. **description 加触发 + 边界（major，两路共识）**：原 description 全是「做什么 + 方法论清单（ReAct/Reflexion/...）」、无「何时该用/不该用」——skill 自动路由只读 description，导致漏触发（调研/论证利弊）+ 误触发（「X 是什么」单点事实、how-to），估触发准确率 ~67%。改为补正向触发词（选型/对比/调研/评估/综合/核实）+ 负向边界（单点事实/写代码/计算/how-to 不要用），删方法论清单（正文「学术基础」表本就有）。净字数持平、不臃肿，估准确率升至 ~95%。
2. **Step 0 行 29 拆行 + 「现状如何」消歧（minor）**：方向已锁那条从 ~140 字单行拆成「指令 + ①② + guard」嵌套 bullet（v5.6 加 guard 撑大的最难读行）；「X 现状如何」原既当行 29 已锁正例又当行 30 survey 伪装句，自相矛盾——行 29 改用明确单值例「X 的当前版本/配置是什么」，「现状如何」专归行 30 待定。
3. **删 Extract 后处理 item 4 悬挂残句（既有 bug）**：`跳过 = [no-schema-validate] degraded。` 末尾误粘的 `（std≥2, deep≥3），补搜。`（从 item 3 复制残留，非本次引入）删除。

**不做**: PLAYBOOK 未改，header v5.6 不动；命令文件 `/deep-research` 的 description 是显式调用、不受自动触发影响，不动。

## v5.6 — 2026-06-02 (方向闸：方向锁定自主直跑 + Step 0 瘦身)

**触发**: 方向毫无更改空间的问题（如「Anthropic 为啥见天重置我额度，我正常应该周六上午 11 点重置」），还展示计划 + 60s 窗口问研究方向，纯属仪式。v5.5 的「立即开始」要用户显式打字才跳，且 60s 自动推进依赖后台 timer re-wake——在不支持重唤的环境会降级成「等批准」阻塞。

**核心洞察**: Step 0 的真正决策不是「等不等」，而是「**有没有只有用户能拍板、且会改变研究什么的方向选择**」。答案为「无」时，展示计划→等窗口全是空转，且不该依赖 timer 重唤是否可用。把这个自判作为 Step 0 第一道闸，能同时（a）干掉无意义仪式（b）摆脱对 timer 重唤的依赖。

**修改**:

1. **SKILL.md Step 0 重构为「方向闸」**：① 方向已锁（现象/主张给全、无分叉、无缺关键约束的诊断/核实/查现状类，或显式 skip 词）→ 不展示计划、不起 timer，1-2 行压缩陈述直奔 Step 1；② 方向待定（survey/选型/范围口径需用户定/多解读/缺全局约束）→ 展示计划 + 60s 窗口（原 v5.5 机制压缩保留，含幽灵计时器 kill）。判不准默认待定（错锁方向代价 ≫ 多等 60s）。
2. **「立即开始」关键词折进「方向已锁」**：不再是独立分支，与自动判定收敛到同一直跑路径。
3. **Step 0 瘦身**：原三条重叠快路径（60s timer / 立即开始词 / 沉默）→ 一道顶部决策 + 仅「待定」分支保留 timer 机制；commands/PLAYBOOK/README 措辞对齐；PLAYBOOK header + footer v5.5→v5.6。
4. **独立多 agent 审计后加固（同批）**：① 条件① 补「现象/口径唯一 ≠ 归因框架/核实口径唯一」guard + 待定行点名「现状如何/有哪些/盘点」survey 伪装句——堵 prompt-salience 误锁（3 条对抗发现收敛到「范例句式显著度过高、可能盖过合取前提」）；② 两处 frontmatter description 去掉「需用户批准/等你批准」硬承诺（与「方向已锁直跑」语义冲突，软化不增字数、版本号 v5.0/v5.5 不升）。

**不做**: 不加 PreToolUse 硬拦（软 prompt guard + 默认待定兜底即可，硬拦反易卡错方向）；不引入新 hook/Python；description 版本号不升（避免臃肿）。

## v5.5 — 2026-06-01 (计划 gate：60s best-effort 自动推进 + 立即开始)

**触发**: Step 0 是"必须等批准"的无限等待，人走开就永久卡住。要 60s 窗口（超时自动跑 / 期间可改 / 可即时开始），及 `立即开始` 一词直接跳过窗口。

**核心洞察**: Claude Code 用户输入驱动、非时钟驱动，无原生"空闲超时"（AskUserQuestion 无超时 / 无 UserIdle hook / Cron 不精确）。唯一能做"沉默自动推进"的是后台计时进程退出触发 re-invoke——标准 build 不保证。故设计为 **best-effort + 优雅降级**：自动推进是增强，缺失时退化为"等批准"（老行为），任何环境都不丢功能、不卡死。

**修改**:

1. **SKILL.md Step 0**：「必须等批准」→ 审批窗口（展示计划 → `sleep 60`（run_in_background）让出 → 超时重唤自动跑）。三条正确性：① 用户窗口内插话**先 `TaskStop` 掉计时器再行动**（防幽灵计时器二次开跑，头号 bug）② 重唤先查研究是否已开始、防重复 ③ 不重唤则降级为等待。
2. **立即开始**：commands/deep-research.md 解析 `$ARGUMENTS` 含「立即开始/马上开始/直接开始/不用确认/skip」→ 跳过窗口直奔执行；argument-hint 加 `[立即开始]`。
3. **PLAYBOOK** Phase 1（Standard/Deep）措辞对齐；header v5.4→v5.5。

**不做**: 不加 PreToolUse 硬拦（防错方向）；不引入 hook/Python（timer 即 sleep，立即开始命令级解析够）；description frontmatter 不动（避免臃肿）。

## v5.4 — 2026-05-27 (执行纪律强化：硬门禁 + 砍仪式)

**触发**: AI 编程工具深度研究真实执行（2026-05-27）。deep tier 任务中主 agent 0 个 sub-agent spawn、全自己搜、跳 REFLECT → 漏掉 Opus 4.7 / GPT-5.3-Codex / DeepSeek V4 等关键最新数据。事后诊断：v5.3 的机制本身够用，但 agent 进门后第一件事不是遵守规则，而是按自己的理解开干。

**核心洞察**: 加更多 checklist 治不了「不读规则」的病。Agent 在顶部最可能停的位置放最少、最硬的规则才可能被遵守。

**修改**:

1. **新增「执行前硬门禁」**（SKILL.md 顶部，触发条件之前）
   - 3 行：spawn 几个 researcher？/ 模板准备了？/ freshness 参数用了？
   - 任一答不出 → 立即停，不进入 Phase 0
   - 位置优先于所有其他内容（agent 进门第一眼撞上）

2. **删除 Pre-Report Freshness Audit JSON**（~32 行）
   - 放在 REFLECT 之后 → agent 已经跳过 REFLECT → 不可能执行
   - 时效性检查保留在 REFLECT 第 1 项（执行时机正确）
   - 覆盖度检查保留在 REFLECT 第 2 项 + Discovery Bootstrap 维度 C/E

3. **Discovery Bootstrap 增加维度 E** — 开源/独立/非商业生态
   - 触发：R02 实测Latest Releases Sweep 抓到 17 个主 agent 完全不知道的新玩家（多来自开源/独立生态）
   - 生态图从 A-D 四维度 → A-E 五维度

4. **新增「最高优先级反模式」**（铁律下方，执行流程之前）
   - 一行：主 agent 自己搜 = 研究作废。发现即停，改派 sub-agent 重跑。

5. **同步清理**
   - Frontmatter 18→17 字段（移除 phase_freshness_audit）
   - 黄金法则 #6 去掉「交付前过 Freshness Audit」引用
   - 反模式表移除 Pre-Report Self-Check 条目
   - Phase 完整性表移除 Pre-Report Freshness Audit 行

**设计原则**:
- 不加水，只改结构：信息顺序从「参考文档式」→「执行门禁式」
- 最小可行规则放在最大可见位置
- 砍掉放错位置的检查（及时性 > 完备性）

**预期效果**:
- 执行前自检完成率：0% → 目标 >90%（3 行门禁在顶部，跳过难度 > 遵守难度）
- 总行数：2337 → 1674（-28%）。CHANGELOG 691→93（历史归档为摘要表），PLAYBOOK 272→218（去重+修复过期引用），SKILL.md 243→232

**已知风险**:
- 硬门禁对强推理模型（Opus 4.7）效果待验证（对话记录中的违规者就是 Opus 4.7）
- 如果 agent 连顶部 3 行也跳过，需要更根本的机制（如 hook-level enforcement）

## v5.0.1 — 2026-05-27 (post-release: L1 regression 问题集 + A 股实测评估)

**触发**: 用户要求评估 deep-research skill 价值，对比普通对话 vs deep-research 同 prompt（A股基金投资研究）产出。随后要求优化并提交。

**A 股实测发现**（degraded 状态仍全面碾压）:
- 即使 anysearch 限流导致 3 个 researcher 失败（degraded: true），deep-research 输出在估值分析、风险覆盖、来源可追溯、自我认知等维度仍远超普通对话
- 核心差异：Central Thesis 驱动 vs 数据罗列、反方视角 vs 无风险分析、信息缺口诚实 vs 无自我认知
- 详见评估：用户桌面 `desktop/research/` 两份对比报告

**修改**:
1. **L1 regression 问题集建成**（`eval/questions/INDEX.md`）
   - 12 题：4 模板（survey/compare/decide/howto）× 3 难度（easy/medium/hard）
   - 每题固定 pass criteria，禁止回调
   - 套件通过条件：≥10/12 overall ≥0.75，0 题 <0.55，平均 factuality ≥0.80
   - baseline 尚未运行
2. **EVAL.md 更新**: L1 状态从"未提供完整题包"→"问题集已建成，待 baseline"

**未改**:
- SKILL.md/PLAYBOOK.md 不做修改（v5.0 Pareto 简化后已足够紧凑，triage 新增内容与简化哲学冲突）

---

## 历史版本摘要（v1.0 — v4.9.3，2026-05-26）

| 版本 | 关键改动 | 教训/结果 |
|---|---|---|
| v4.9.3 | 真实执行数据驱动：researcher prompt + output schema；frontmatter ~100→15 字段 | Phase 完成率 45%，5/6 researcher 返回自然语言而非 JSON |
| v4.9.1 | 独立 sub-agent 审计后降级 v4.8/v4.9；撤 PRISMA/Cochrane/Kappa 宣称 | 5:1 抽审 N 远不达 Kappa 推断要求，「合规」宣称是学术装饰 |
| v4.9 | Evidence Quality 借鉴（后被降级） | 预防性升级，无具体 bug 驱动 — over-engineering 信号 |
| v4.8 | Stage-Gate 10 闸门系统（后被降级） | 复合通过率 19.7%，audit-of-audit 嫌疑 |
| v4.7 | Phase 4.8 Logic Audit 6 项 | 真实 bug：推荐 Claude Code 时漏了 Opus 4.7 |
| v4.5 | 知识过时假设 + 不打断纪律 + Phase 2.6 Latest Releases Sweep | R02 实测：Sweep 抓到 17 个全新玩家，含 DeepSeek V4 |
| v4.4 | Dispatch Gate 事前拦截 | DeepSeek spawn 0 researcher 而 Claude spawn 5 — 需要事前拦截 |
| v4.3 | Discovery Bootstrap + Dependency Mining（数据驱动防遗漏） | 「谁被漏了」应由数据回答，不由模型记忆 |
| v4.2 | Invisible Layer Check 防 Frame Blindness | 生态题因按产品形态分解遗漏 DeepSeek（基础设施层） |
| v3.2 | HDIR 五轮循环（后被 v2.7.3 撤） | LLM judge：HDIR 仍是 ReAct+Reflexion 包装，原创性 0.78 |
| v3.1 | 顾问级输出：Central Thesis + 三幕结构 + 顾问语气 | 从 findings dump 升级为顾问分析 |
| v3.0 | Info Saturation Protocol：停止条件从「量」→「质」 | 5 项 Saturation Checklist |
| v2.9 | 搜索量从「配额制」→「按需+饱和制」 | deep ≥80 搜索是配额制错误，修正为 ≥30 |
| v2.8 | 搜索量对齐 GPT DR（200-800 次） | 移除 URL 硬上限，用 info saturation 替代 |
| v2.7 | dev-time hook harness + fixture 自测 | 从「逻辑正确」→「实测正确」 |
| v2.4 | R03 实测后系统补强：反方搜索/Extract Gate/AI confabulation lint | 主 agent 4 项 metrics 50%+ 谎报 |
| v2.3 | Research-Informed Quality：10 项论文依据 enhancement | 修 5 处错误 attribution（CHI→IUI, DeepHalluBench 不存在等） |
| v2.0 | Museum Grade：八阶段 + supervisor-researcher 双层 | 首个完整工作流 |
| v1.0 | 初始六阶段：Plan→Search→Read→Reflect→Synthesize→Report | 基于 9 篇行业资源 |

完整细节见 git history `git log -- skills/deep-research/CHANGELOG.md`。
