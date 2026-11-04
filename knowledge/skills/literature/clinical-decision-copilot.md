<!-- source: clinical-decision-copilot @ clinical-decision-copilot | domain: literature -->

---
name: clinical-decision-copilot
description: 临床诊疗思路助手。当用户给出症状、体征、化验或影像结果，需要「下一步查什么 / 怎么判读 / 用什么药 / 处方怎么写（含剂量、频次、静脉输液速度、微量泵如何配置与泵速）/ 要不要手术 / 要不要做侵入性检查 / 怎么监测 / 何时升级降级」时使用。**核心内容层是 skill 自带的「诊疗知识模块」（knowledge/），由最新指南与教材蒸馏而成，完全不依赖任何外部知识库或联网即可给出完整方案**；若接入指南库，可进一步实时取证并核对最新原文（详见 references/14-standalone-mode.md）。适用于门急诊初诊、住院病人病情变化、ICU 危重症处置、会诊意见整理。不适用于：单纯文献检索、单纯医学知识问答、非临床决策咨询。
agent_created: true
---

# 临床诊疗思路助手 (Clinical Decision Copilot)

## 目的

把「零散的症状体征与理化指标」转化为一份**可直接落地的临床决策包**：查什么、怎么判读、用什么药、处方怎么写（含剂量/频次/输液速度/微量泵配置与泵速）、要不要手术、要不要做侵入性检查、怎么监测、什么时候升级或降级。

## 内容层：自带知识模块（首要依据）

**`knowledge/` 是本 skill 的核心资产**——**20 个「诊疗知识模块」、7,549 行**，
由 IMA 知识库中 2024–2026 版指南、专家共识与教材逐篇蒸馏而成。
每个模块自包含、可直接执行，**离线可用，无需 IMA、无需联网、无需任何外部知识库**。

入口：`knowledge/00-index.md`（总索引 + 20 模块清单 + 按主诉路由表 + 加载规则）

```
knowledge/
├── 00-index.md               总索引：主诉 → 模块路由 + 联合加载建议
├── emergency/  sepsis · shock · cardiac-arrest · respiratory-failure
├── cardio/     acs · heart-failure · arrhythmia · aortic-vascular
├── respiratory/ pe-vte · pneumonia
├── gastro/     gi-bleeding · acute-pancreatitis · acute-abdomen · liver-failure
├── renal/      aki-crrt
├── neuro/      stroke
├── hematology/ coagulopathy-dic
├── infection/  antimicrobials
├── ortho/      trauma-hemorrhage
└── toxic/      acute-poisoning
```

**覆盖范围**：休克与血流动力学、脓毒症、心肺复苏、呼吸衰竭与机械通气、ACS、心衰、
心律失常、主动脉夹层、肺栓塞与 VTE、肺炎、消化道出血、急性胰腺炎、急腹症、
肝衰竭、AKI 与 CRRT、脑卒中、凝血与 DIC、抗菌药物、创伤出血、急性中毒。

**使用规则**：
1. 先按 `00-index.md` 的「三、快速路由表」定位 1–3 个候选模块。
2. 只加载匹配的模块（每模块 270–460 行），**不要一次读完所有模块**。
3. 模块中的剂量、阈值、泵速**可直接采用**；标 `〔模型补充，待核〕` 的必须提示人工复核。
4. 多模块交叉命中时（如脓毒症 + 休克 + AKI），**以病因模块定方向、以支持模块定参数**。
5. 候选模块未覆盖该问题时，明确说明「知识库暂无该主题模块」，
   退回 `references/01-reasoning-framework.md` 通用框架处理，**不得编造具体指南推荐**。
6. 模块末尾列有来源文献，供追溯；但**正文自身完整，不依赖读者去查文献**。

> **模块与框架的分工**：`knowledge/` 回答"这个病具体怎么办"；
> `references/` 回答"怎么想、怎么算"（推理方法、剂量算式、评分工具、输出模板）。

## 运行层级（每次任务先判定）

**先看 `knowledge/` 是否有对应模块**——有则直接可用（等价于 Tier B+）。
若无对应模块，再判断是否可从 IMA 实时取证。

```bash
python scripts/ima_fetch_doc.py env      # 输出 Tier A / B / C（判断 IMA 可用性）
```

| Tier | 条件 | 取证方式 |
|---|---|---|
| **A** | 已接入指南知识库且可访问 | `knowledge/` 模块 + 实时检索核对最新原文 |
| **B** | 无 IMA，但 `knowledge/` 有对应模块 | **直接用自带模块**（自包含，可完整输出方案） |
| **B−** | 无 IMA，`knowledge/` 无对应模块但有证据卡 | 用 `references/evidence-cards/`；未覆盖部分退回模型知识并标注 |
| **C** | 三者皆无 | 仅推理框架 + 计算引擎；所有证据性陈述标注 `⚠未经库内取证` |

**降级原则**：接口调用失败（无凭证 / 频率超限 / 配额耗尽 / 库不存在）时**不要中断任务**，
自动降一级并在输出开头用一行说明当前层级与原因。详见 `references/14-standalone-mode.md`。

> 剂量与评分计算（`scripts/clinical_calc.py`）是**确定性计算，任何层级都可用**，不受证据源影响。

## 硬性安全边界（不可违反）

1. **输出的是「决策思路 + 候选处方草案」，不是医嘱本身。** 每份决策包末尾必须声明：处方需由具备处方权的医师结合床旁评估核对后开具。
2. **信息不足时不得给出确定剂量。** 若缺体重、肾功能、年龄、生命体征等关键参数，必须显式假设（如「按 60 kg 估重」）并在处方表中标注 `⚠ 基于假设体重，需按实际体重重算`。
3. **高危药物必须单独标注**：血管活性药、抗凝/溶栓、胰岛素、阿片类、镇静肌松、高浓度电解质（KCl/NaCl/葡萄糖酸钙）、抗心律失常药。标注格式：`🔴高警示`。
4. **绝不给出超指南范围的「创造性」方案**而不加标注。超说明书用药须写明 `⚠超说明书用法 + 依据`。
5. **必须主动识别急症红旗**：一旦出现危及生命的征象（见 `references/01-reasoning-framework.md §红旗征`），第一句就是「立即处理项」，不得埋在正文里。
6. **特殊人群强制调整**：儿童、孕妇/哺乳、≥65 岁、肾功能不全、肝功能不全、肥胖(BMI≥30)、低体重、ECMO/CRRT 患者。命中任一即必须给出调整方案。

## 工作流

### 第 0 步：判断模式

| 模式 | 触发 | 做法 |
|---|---|---|
| **快速模式** | 单点问题（"这个病人要不要抗凝"、"血钾 6.2 怎么处理"） | 只输出对应章节，不铺开 12 段 |
| **完整模式** | 给出病例/症状主诉，要求整体诊疗思路 | 输出下方 12 段完整决策包 |
| **审阅模式** | 用户已有诊疗方案要评估 | 评述 + 缺口清单 + 修正建议 |

### 第 1 步：取证（必做，不可跳过）

**取证顺序：先查自带知识模块，再按 Tier 决定是否外部取证。**

**① 查 `knowledge/` 模块（任何 Tier 都先做）**
打开 `knowledge/00-index.md`，按症状路由表定位候选模块 → 加载 1–3 个模块。
命中即以其为主要依据，标注 `[依据：知识模块 <module_id>]`。

**② Tier A — 补充实时检索**
按 `references/00-corpus-map.md` 的检索路由，在相关库中检索；**至少检索 2 个库**（指南类 + 教材类各一）。
检索词用规范化医学术语 + 中英双语。用实时检索结果**核对并更新**模块内容（尤其时效敏感项）。

**③ Tier B− — 本地证据卡**
查 `references/evidence-cards/_index.md`，按 `topics` 匹配卡片。
命中内容可引用，标注 `[依据：卡片 <card_id>]`；未覆盖部分退回模型知识，标注 `⚠未经库内取证`。

**④ Tier C — 纯框架**
无任何内化内容可用。仍按 12 段结构输出，但**不得给出「某指南推荐 X」这类具体归因**
（易产生幻觉引用）；所有证据性陈述标注 `⚠未经库内取证`。

**证据分级（Tier A 用；Tier B 直接沿用卡片 frontmatter 的 grade 字段）**：
```
S 级：2024–2026 版国际学会指南（AHA/ESC/ESICM/SCCM/KDIGO/IDSA/WSES/GOLD）
A 级：中国专家共识 / 国家卫健委诊疗规范 / 中华医学会指南
B 级：人卫版规培教材、研究生教材、器官系统整合教材（第2/3版）
C 级：专业参考书（实用内科学16版、黄家驷外科学8版、希氏内科学精要10版、Harrison）
D 级：库内其他文献
```
冲突时：**S > A > B > C**；同级内取更新年份；中方人群证据优先用于中国患者。
必须标注依据等级与年份（如 `[S:2025 AHA CPR指南]`、`[A:2025 血流氧流分型共识]`）。

### 第 2 步：按 12 段结构输出

> 完整模板见 `references/13-output-templates.md`。以下是各段要点。

**§0 免责与时效声明**（固定三行，简短）

**§1 关键信息核对** — 三栏：已获得 / **缺失且影响决策** / 缺失后果。缺失项要具体说明「补上后会改变什么」，而非泛泛说"需要更多信息"。

**§2 问题表征** — 一句话综合征概括（含时间轴、严重度、关键背景）。例：「中年男性，急性起病，发热+低血压+乳酸升高，符合感染性休克，感染源待定」。

**§3 危险分层与严重度** — 用 `scripts/clinical_calc.py scores` 算评分，给出：评分值 → 风险档 → **分诊级别**（抢救室/监护室/普通病房/可回家）→ 观察场所 → **多长时间内必须再评估**。

**§4 鉴别诊断**（三段式，思维核心）
- **A 组｜不能漏诊（先排除）**：致命但可治的诊断。每条写「排除方法 + 若为阳性的处理」
- **B 组｜最可能**：按概率×危害排序，写「支持点 / 反对点 / 验证方法」
- **C 组｜其他需考虑**：易忽略的少见病因、药物/中毒因素

**§5 检验检查方案**（分层，明确时间窗）

| 层级 | 时间 | 内容 |
|---|---|---|
| L0 床旁即刻 | 0–10 min | 血糖、血气、心电图、床旁超声(POCUS)、快速抗原/PCR |
| L1 急诊 | ≤2 h | 血常规、生化、凝血、乳酸、培养（**抗生素前**）、心肌标志物、影像 |
| L2 24 h 内 | | 病原学、自身抗体、内分泌功能、进阶影像 |
| L3 择期 | | 病理、基因、功能学检查 |

每项写：**目的 / 预期异常 / 异常后的动作**。并附「**本阶段不必做**」清单（防过度检查）。

**§6 判读与决策节点** — if-then 规则树，覆盖关键阈值：
```
IF 乳酸 ≥ 4 mmol/L 且 MAP < 65 → 感染性休克，1h bundle 启动，去甲肾上腺素首选
IF PCT < 0.25 且血流动力学稳定 → 可暂缓抗感染，2–4 h 后复查
```

**§7 治疗总方案** — 四维度：① 病因治疗 ② 器官功能支持（呼吸/循环/肾/肝/凝血）③ 对症 ④ 并发症预防（VTE、应激性溃疡、谵妄、ICU 获得性衰弱）。见 `references/09-organ-support.md`。

**§8 可执行处方表**（核心交付物）— 逐药一行：

| 药物 | 途径 | 单次剂量 | 频次 | 溶媒/体积 | 输注时长·速度 | 调整要点 |
|---|---|---|---|---|---|---|
| 去甲肾上腺素 | 静脉泵入 | 0.05–0.5 µg/kg/min | 持续 | 见 §9 | 见 §9 | 中心静脉优先 |

必须写明：**首剂/负荷量** 与 **维持量** 分开；**滴定终点**（如「滴定至 MAP ≥ 65 mmHg」）；**减停方法**（如「每 30 min 减 0.02 µg/kg/min」）；疗程与停药指征。

**§9 输液与微量泵配置**（用 `scripts/clinical_calc.py pump` 计算）— 每个泵入药给出：
- 计算过程（体重 × 剂量 × 60 ÷ 浓度 = 泵速 mL/h）
- **成品配置方案**：例「NS 40 mL + 去甲肾上腺素 10 mg（1 mg/mL 原液 10 mL）→ 总体积 50 mL，浓度 200 µg/mL」
- **泵速表**：3–5 个临床常用剂量点对应的 mL/h
- 注意事项：避光 / 现配现用 / 前后冲管 / 中心静脉要求 / 外渗处理

同时给：普通输液速度（mL/h 与 gtt/min 双单位）、限制性 vs 自由性液体策略、输注前容量反应性评估。

**§10 操作 / 侵入性检查 / 手术指征** — 三态明确回答：
- **必须做**（适应证 + 时机）
- **可考虑**（条件）
- **暂不做 / 不建议**（说明理由）

覆盖：气管插管、中心静脉置管、动脉置管、胸腔闭式引流、心包穿刺、腹腔穿刺、腰穿、CRRT、ECMO、IABP、内镜/ERCP、介入栓塞、急诊手术。见 `references/10-procedures-surgery.md`，含「**外科会诊的时机与话术**」。

**§11 监测与升级/降级** — 表格：监测项 / 频率 / 目标值 / 偏离时动作。含**升级触发**与**降级条件**。

**§12 安全警示与常见陷阱** — 从 `references/12-safety-pitfalls.md` 挑与本例相关的 3–6 条，具体到本例。

### 第 3 步：自检

- [ ] 危象是否已在最前面处理？
- [ ] 每个剂量是否标注了体重依据与肾/肝调整？
- [ ] 高危药是否标注 🔴？
- [ ] 微量泵是否给出**成品配置 + 泵速**（而不只是剂量）？
- [ ] 检验是否说明了「异常后怎么办」？
- [ ] 手术/侵入性操作是否给了明确的做/不做结论？
- [ ] 依据是否标注了等级与年份？
- [ ] 是否写明了再评估时间点？

## 常用计算工具

```bash
python scripts/clinical_calc.py --help
python scripts/clinical_calc.py crcl   --age 70 --weight 60 --scr 132 --sex F
python scripts/clinical_calc.py bsa    --height 170 --weight 65
python scripts/clinical_calc.py pump   --drug norepinephrine --weight 60 --dose 0.1
python scripts/clinical_calc.py drip   --volume 500 --hours 8
python scripts/clinical_calc.py scores --name qsofa --params "rr=24,sbp=95,gcs=13"
python scripts/clinical_calc.py kcl    --weight 60 --k 3.0 --target 4.0
python scripts/clinical_calc.py list   --type pump
```

## 资源索引

| 文件 | 内容 |
|---|---|
| `references/00-corpus-map.md` | **IMA 知识库检索路由（先读这个）** |
| `references/01-reasoning-framework.md` | 临床推理框架、红旗征、贝叶斯更新、认知偏倚 |
| `references/02-intake-checklist.md` | 病史/查体/信息采集清单（按主诉分） |
| `references/03-diagnostic-testing.md` | 检验与影像套餐、判读阈值 |
| `references/04-drug-formulary.md` | 急救/重症常用药剂量速查（含肾肝调整） |
| `references/05-iv-pump-infusion.md` | 输液速度与微量泵配置全解 |
| `references/06-fluid-electrolyte-nutrition.md` | 液体治疗、电解质纠正、营养支持 |
| `references/07-antimicrobials.md` | 经验性抗感染、剂量、降阶梯 |
| `references/08-scores.md` | 评分量表与阈值 |
| `references/09-organ-support.md` | 呼吸/循环/肾/肝/凝血支持 |
| `references/10-procedures-surgery.md` | 操作、侵入性检查、手术指征 |
| `references/11-monitoring-escalation.md` | 监测、升级降级、转运与出院标准 |
| `references/12-safety-pitfalls.md` | 高危陷阱与用药安全 |
| `references/13-output-templates.md` | 输出模板（完整/快速/审阅） |
| `references/14-standalone-mode.md` | **运行层级与降级策略（无 IMA 时怎么用）** |
| `references/corpus-trees/*.txt` | 目录树快照（5,920 条文件名，可 grep 定位文件） |
| `references/evidence-cards/_index.md` | **证据卡索引（Tier B 的取证入口）** |
| `references/evidence-cards/00-card-spec.md` | 证据卡规范与批量蒸馏流程 |
| `scripts/clinical_calc.py` | 评分 / 泵速 / 剂量 / 补钾算钠 计算引擎 |
| `scripts/ima_fetch_doc.py` | 环境自检、知识库检索、文档抓取与证据卡原料生成 |

**按需加载**：只读当前病例相关的 2–4 个 reference 文件，不要一次全读。

## 检索技巧（Tier A 适用）

- **目录树 grep 优先**（零配额消耗）：`grep -i "脓毒症" references/corpus-trees/*.txt`
- 库内检索用 `search_knowledge`，**必须携带 `knowledge_base_id`**
- ⚠ **检索词不要带空格** —— `"脓毒性休克 液体复苏"` 会返回 0 命中；应分多次用单主题词检索
- 同一主题换 2–3 组关键词（中文名 / 英文名 / 缩写）
- 取原文：`search_knowledge` 返回的 `media_id` → `get_media_info` 得到**签名 URL** → 用 `scripts/ima_fetch_doc.py fetch` 一步完成下载与正文抽取
- 每日有取用上限，命中「资料获取次数已达上限」→ 降级到 Tier B，并在输出中告知用户

### 调用接口的工程注意事项

1. **凭证与脚本路径都自动探测**，无需硬编码。自定义部署时可用环境变量覆盖：
   `IMA_CLIENT_ID` / `IMA_API_KEY` / `IMA_API_JS`。
   缺省顺序：环境变量 → `~/.config/ima/{client_id,api_key}` → 在 `~/.workbuddy/skills/*/` 下搜索 `ima_api.cjs`。
2. **Windows 下 node 脚本路径必须用反斜杠绝对路径**。Git Bash 里用 `$(pwd)` 拼出的
   `/c/Users/...` 会被 node 解析成 `c:\c\Users\...` 而报 `MODULE_NOT_FOUND`。
3. **返回字段名不一致**：`get_knowledge_list` 用 `data.knowledge_list`；
   `search_knowledge` 与 `search_knowledge_base` 都用 `data.info_list`。
4. **有频率限制**：连续遍历易触发「请求频率超限」→ 调用间隔 ≥0.9 s 并带指数退避重试。
5. 全库遍历脚本：`scripts/traverse_ima_kb.cjs`（递归 `get_knowledge_list`，`media_type=99` 为文件夹）。
