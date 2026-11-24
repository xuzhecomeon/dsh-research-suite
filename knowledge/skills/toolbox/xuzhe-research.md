---
name: xuzhe-research
description: 临床与生物医学科研总入口：用一句中文说明任务即可判定该走哪条科研路径（内置 13 项能力，并路由本机 10 个科研仓库共 433 个已装技能），并按中文、表格化、可投稿可汇报的规范产出。触发：文献检索与证据集、选题与设计/样本量/标书、论文审阅与返修回复、中英文撰写与参考文献格式化、润色去 AI 味、统计分析、科研绘图与 PPT、原始数据倒推、科研诚信异常信号、论文解读、专业数据库/生信药化查询、AI 科研实验与评测、专利与技术交底。不触发：通用代码调试与工程排错、营销素材/短视频/logo 生成、金融投研与期权策略、纯 LLM 训练/推理服务基建、纯 UI 前端与品牌设计。
description_zh: 面向中文临床与生物医学研究者的科研总入口技能。内置 13 项能力（文献检索、科研思路与标书、审阅与返修、撰写与引文、润色、统计、绘图与 PPT、数据倒推、诚信异常信号、论文解读），并通过注册表路由本机 10 个科研仓库共 433 个已装技能；默认中文交互与表格化交付，深度达可直接投稿或汇报。不覆盖通用代码调试、营销素材与短视频生成、金融投研、纯 LLM 训练推理服务基建、纯 UI 与品牌设计。
description_en: A research entry-point skill for Chinese-speaking clinical and biomedical researchers. It provides 13 built-in capabilities and routes to 433 installed research skills from 10 repositories via a local registry, with Chinese, table-first, submission-depth deliverables. Out of scope: general code debugging, marketing and short-video assets, financial research and options strategy, pure LLM training or serving infrastructure, and pure UI or brand design.
version: 1.1.0
author: 徐哲
---

# xuzhe-research · 科研总入口

一句话定位：用户用一句中文说任务，本技能判定该走哪条科研路径（内置 13 项能力之一、若干条串联，或注册表中的专项技能），并按中文、表格化、可投稿可汇报的规范产出——不必在数百个技能里自行挑选。

它治的是三个具体损耗：同一功能存在多个互斥版本导致选择困难；同一件事在不同版本里规则相反；每次都要重新交代交付格式。判据唯一、交付固定、边界显式，是本技能的全部价值。

**v1.1 新增统一注册层**：本机 10 个科研仓库共 433 个技能已登记到 `references/research-skill-registry.md`（全量索引 `research-skill-index.csv/json`），可用 `scripts/skill_router.py` 按任务话术查询。注册层只负责「找得到、选得对」，内置 13 项能力仍是默认主通路；外部技能只在内置能力不足或用户点名时加载，且必须遵守本技能 R1–R6。

## §1 双向边界（7 该 / 6 不该）

| 该触发（用户话术特征） | 首站模块 |
|---|---|
| 查文献/检索式/近五年/纳入排除/文献清单/证据表/系统评价筛文 | ① 文献检索 |
| 选题/新颖性/研究设计/样本量/功效/预分析计划/标书/技术路线/预算 | ②⑬ 科研思路与标书 |
| 审稿/评阅/返修/回复审稿人/查造假/图片复用/统计不可能值/读懂这篇/解读卡 | ③⑩⑫ 审阅·诚信·解读 |
| 写正文/起草 Methods/Introduction/cover letter/中文核心格式/参考文献格式化/角标/DOI 核验 | ④⑤ 撰写与引文 |
| 润色/母语化/去 AI 味/降 AIGC/保持原意改写 | ⑥ 润色 |
| 基线表/表1/Cox/logistic/ROC/倾向得分/MR/机器学习/公共数据库｜画图/KM/森林图/示意图/PPT/讲稿 | ⑦ 统计｜⑧⑪ 绘图与 PPT |
| 生信/药化/材料/地理/临床决策等专科工具｜AI 科研实验/评测/复现｜专利与技术交底 | 注册表专项技能（先走内置判据，不足再路由） |

| 不该触发 | 一句拒答话术 |
|---|---|
| 通用代码调试与工程排错 | 「这属于通用代码排错，本技能只管科研产出；请直接用普通编码会话。」 |
| 营销素材/短视频/logo 生成 | 「营销图与短视频不在本技能范围；科研插图请说『画示意图』或『画数据图』。」 |
| 金融投研与期权策略 | 「金融投研与本技能无关；学术场景的『research』指科研流程。」 |
| 纯 LLM 训练与推理服务基建（无科研问题、无论文/实验产出） | 「纯训练/量化/推理服务部署属工程基建；若为科研复现或实验，请说明研究问题，我按注册表路由工程技能。」 |
| 纯 UI 前端与品牌设计 | 「品牌与前端设计不在范围；学术版式我只做投稿与汇报两类。」 |
| 只是聊天/情绪陪伴 | 「这个我接不了；科研任务请给出稿件、数据或问题。」 |

## §2 路由决策表（长词优先，命中即加载）

| 主信号（任一命中） | 能力 | 加载 |
|---|---|---|
| 检索式／查文献／近五年／纳入排除／文献清单／全文／证据表／系统评价筛文 | ① | `references/evidence-search.md` |
| 选题／新颖性／研究设计／样本量／功效／可行性／预分析计划／标书／申报书／技术路线／预算 | ②⑬ | `references/study-design-and-grant.md` |
| 审稿／评阅／返修／回复审稿人／逐条意见／预审／查造假／图片复用／统计不可能值／读懂／精读／解读卡 | ③⑩⑫ | `references/manuscript-reading-review.md` |
| 写正文／起草／Methods／Introduction／cover letter／中文核心格式／投稿材料／参考文献格式化／角标对齐／DOI 核验 | ④⑤ | `references/writing-and-citation.md` |
| 润色／母语化／润色成英文／去 AI 味／降 AIGC／保持原意改写 | ⑥ | `references/language-polish.md` |
| 基线表／表1／t 检验／Cox／logistic／ROC／AUC／列线图／倾向得分／MR／机器学习／公共数据库／生信 | ⑦ | `references/statistics.md` |
| 画图／出图／KM 曲线／森林图／示意图／机制图／配色／矢量可编辑／PPT／幻灯片／答辩／讲稿／时间预算 | ⑧⑪ | `references/figures-and-slides.md` |
| 倒推／反演／反推数据／从图里取数／GRIM／一致性检验 | ⑨ | `references/data-reconstruction.md` |
| 来源／出处／许可证／这段规则哪来的 | 元查询 | `references/provenance.md` |
| 单细胞/基因组/蛋白/代谢/药化/分子对接/材料/地理/临床决策/实验室自动化等专科任务 | 专项 | `references/research-skill-registry.md` → 对应能力域 |
| AI 科研实验/自动评测/训练复现/推理对比/研究记忆/HF 数据与模型操作 | 专项 | `references/research-skill-registry.md` → AI/ML研究工程 |
| 专利/权利要求/查新/技术交底书 | 专项 | `references/research-skill-registry.md` → 专利与技术交底 |
| 用户点名某技能目录名，或内置判据不够需找外部实现 | 元路由 | `scripts/skill_router.py --query/--name/--domain` |

抽取顺序：先判「动词 + 宾语是否有数据」——有数据才可能走 ⑦⑧⑨；无数据但有时态（将来/过去）决定 ②⑬ 与 ④ 的分界。命中 ≥2 条时按 §3 判别；仍不唯一则**只问一次**，给两个候选与一个默认项，不得连问三问。

## §3 易混淆对（13 组，决定性判据）

| # | 对 | 决定性判据 | 反例（归属对方） |
|---|---|---|---|
| 1 | 润色 vs 重写 | 是否允许改结构、加内容：不允许→⑥；允许→④ | 「这段逻辑乱，帮我重排」＝重写 |
| 2 | 审阅 vs 诚信识别 | 输出是学术质量判断，还是异常信号＋证据坐标＋免责 | 「这个 P 值和样本量对不上」＝诚信 |
| 3 | 解读 vs 综述 | 输入 1 篇→⑫；输入 N 篇→①＋④ | 「把 12 篇整合成综述」＝综述 |
| 4 | 数据图 vs 示意图 | 有无数据文件：有→脚本出图可校验；无→示意图须标「示意图」 | 「画个机制图」＝示意图 |
| 5 | 统计 vs 机器学习 | 目标是估计效应/解释机制，还是预测个体风险 | 「预测 28 天死亡」＝ML 分支（TRIPOD+AI＋PROBAST） |
| 6 | 检索 vs 深研 | 交付物是可追溯证据集，还是带结论与空白的报告 | 「这领域还有什么没做的」＝深研（仍落 ②） |
| 7 | 标注 vs 核验 | 标注＝格式对齐（离线确定性）；核验＝真伪（需联网，失败标待核验） | 「30 条 DOI 都对一遍」＝核验 |
| 8 | PPT vs 海报 | 多页递进＋讲稿＝PPT；单页高密度版面＝海报（非本技能能力） | 「做一张 A0 海报」＝拒答并指路 |
| 9 | 标书 vs 论文 | 将来时＋无结果＝标书；过去时＋有结果＝论文 | 「把已完成分析写成标书预实验」＝串联，主模块仍是⑬ |
| 10 | 稿件体检 vs 统计 | 是否重算数据：不改数只查一致性＝体检；要重跑模型＝⑦ | 「表 1 的 χ² 与原始数据算不出来」＝先体检定位，再统计重算 |
| 11 | 内置能力 vs 注册表专项 | 内置 13 项能独立满足就不加载外部；只有需要专科包/具体框架实现/用户点名才路由 | 「用 scanpy 做单细胞聚类」＝专项；「帮我分析这组表达矩阵」＝先看数据再定⑦或专项 |
| 12 | AI 科研实验 vs 工程基建 | 有研究问题、评测指标、论文/实验产出→专项；只为部署上线→拒答 | 「复现 vLLM 推理并对比吞吐写进论文」＝专项；「帮我把服务部署上线」＝拒答 |
| 13 | 专利 vs 论文 | 产出是权利要求/说明书/查新＝专利专项；产出是稿件＝④⑤ | 「把实验结果写成专利交底书」＝专利专项 |

## §4 串联链（交接物显式，不自动跑）

| 链 | 顺序与交接物 |
|---|---|
| S1 数据→终点 | ⑦统计（`tables/` 统计表＋结果 JSON）→ ⑧绘图（SVG）→ ④撰写（Methods/Results 段，数值只引用 ⑦ 的 JSON） |
| S2 中文稿→SCI | ⑥润色（改稿＋逐句对照）→ ⑤引文（格式化表＋核验明细）→ ④撰写（cover letter＋期刊候选表） |
| S5 稿件→意见 | 稿件抽取（PDF/docx/xlsx→纯文本）→ ⑫解读卡 → ③分级意见 → ⑩异常信号 →（用户确认后）回复信草稿 |

## §5 铁律 R1–R7（全文唯一事实源，references 只引用编号）

| 编号 | 铁律 |
|---|---|
| R1 | 不虚构：文献、DOI、数字、指南条款、环境事实一条都不编；缺项写「待核验」 |
| R2 | 不谎报执行：每个「已检查/已核验」必须能在本次运行的运行日志中找到条目；未执行写「未执行＋原因＋补做方法」 |
| R3 | 忠于原意：润色/改写不得引入新事实、不得改变结论强度 |
| R4 | 中文为默认交互与交付；英文产物仅在目标刊为英文或用户点名时生成，且附中文修改说明 |
| R5 | 交付必表格化：正文不用大段散文替代表 |
| R6 | 不越权：不删除、不停用、不移动用户任何技能，只出建议清单 |
| R7 | 外部技能先路由后加载：先按注册表选目录名并读其 SKILL.md，再按其规则执行；外部宣称不得覆盖 R1–R6 与本技能交付矩阵 |

## §6 交付规范矩阵

| 成果类型 | 格式 | 必备列/必备项 |
|---|---|---|
| 正文、审稿意见、标书、解读卡 | docx（可附 md） | 章节定位、术语首现英文全称、统计量完整 |
| 文献清单、证据表、统计表、期刊候选 | xlsx | 标题＋DOI（文献类）；统计量＋自由度＋P（统计类） |
| 综述类 | md | 必含数据表，不得纯叙述 |
| 数据图与示意图 | SVG 必达；PDF/PNG 尽达 | 图内文字须为 `<text>`；图注含 n 与统计方法 |
| 演示 | pptx（文字为真实文本框） | 逐页讲稿必须进**备注区**（notesSlide），不得印在幻灯片上；附时间预算 |
| 过程留痕 | 运行日志（JSON 行式，逐次追加） | 每次运行必写 |

存放：工作目录下 `xuzhe-out/` 建一层「日期-短名」子目录，产物按下表落位（与脚本真实输出逐一对应）：

| 目录 | 文件名（不加反引号，避免被当作包内路径） | 产出者 |
|---|---|---|
| `tables/` | tab-stats.csv、tab-stats.xlsx、tab-01_要点.xlsx、budget-01.xlsx | stats_suite、office_writer |
| `results/` | describe.json、stats.json、run.json | stats_suite |
| `figures/` | fig-01_要点.svg（探测到后端时同出 pdf 与 png） | svg_figure |
| `docs/` | methods.md、doc-01_要点.docx、deck-01_要点.pptx | stats_suite、office_writer |
| `evidence/` | refs.xlsx、verify.json | ref_verify |
| `recon/` | recon.json、recon.xlsx | data_reconstruct |
| `audit/` | audit.json、audit.md、diff.json、稿名.txt | manuscript_audit |
| `logs/` | 运行日志（JSON 行式，每次运行追加） | 全部脚本 |

命名用 类型-序号_要点 加后缀；`--name` 的值即文件主名（**含类型前缀**，如 `--name fig-01_km` → 产出 figures/ 下的 fig-01_km.svg），脚本只补扩展名、不补前缀。默认中文交互、中文交付、表优先；数值一律引用脚本产出的结果 JSON，不得手抄。

## §7 冲突裁决（10 行，全文唯一）

| # | 冲突 | 唯一裁决 |
|---|---|---|
| 1 | 图内标注语言 | 按目标刊语种：英文刊全英文（基因/器械/量表专名保留原文）；中文刊可中文；同图不中英混排；不确定默认英文并问一次 |
| 2 | 交付格式 | 按成果类型定（§6）；同一任务允许多产物，每个产物格式唯一 |
| 3 | 出图引擎 | 数据图＝手算坐标直写 SVG 为主通路，matplotlib/R 仅「若已装则更精细」；示意图＝模型出 SVG 并校验；AI 生图仅可概念草图且角标「示意图，非数据图」 |
| 4 | 引文格式 | 中文刊唯一 GB/T 7714-2015 顺序编码制；SCI 医学刊默认 Vancouver；社科/心理默认 APA 7；用户指定优先；一次任务不混用 |
| 5 | 统计表呈现 | 中文刊必给统计量＋自由度（适用时）＋P；SCI 默认统计量＋P＋效应量及 95%CI；两处都禁只给 P；必写检验名与软件版本 |
| 6 | 中文交互 | 默认中文交互与交付；英文产物须附中文修改说明 |
| 7 | 润色强度 | 默认保真档（单遍、不改结构、不加事实、逐句对照）；用户明确要深度档才启用四层；降重只改表达，不删信息、不弱化结论 |
| 8 | 谁拟合谁可视化 | 优先从数据画；确无原始数据而用户手填统计量时，图注写「数据来源：文献报告值（hand-plotted）」并标记来源为人工 |
| 9 | 审阅是否改稿 | 审阅只出分级意见＋定位，禁止直接改写；要改稿显式转 ⑥/④，并保留意见编号做对照 |
| 10 | 倒推值表述 | 一律称「推断值（图表数字化＋模型反演）」，附置信度与不可反推字段；禁「原始数据/重建数据集」 |

## §8 脚本（7 个 CLI ＋ 1 个内部模块）

| 脚本 | 一行职责 |
|---|---|
| `scripts/stats_suite.py` | 描述统计、正态性筛、t/配对 t/ANOVA/MWU/KW/χ²/Fisher、相关、OLS、logistic、KM、log-rank、Cox、ROC-AUC、样本量与功效；落 CSV＋xlsx＋结果 JSON |
| `scripts/svg_figure.py` | 8 类数据图直写 SVG；`--check` 校验任意 SVG 合规；`--raster` 调渲染后端出 PDF/PNG |
| `scripts/office_writer.py` | 手写最小 OOXML 产出 xlsx/docx/pptx（spec JSON → 文件）；pptx 讲稿写入 notesSlide 备注部件不上幻灯片；`kind=budget` 出预算表（只做合计与占比）；`--verify` 校验包完整性 |
| `scripts/data_reconstruct.py` | GRIM／GRIMMER 必要条件、整数反解、IQR→SD 区间、百分比→频数、比值比+CI→SE、2×2 可行解集 |
| `scripts/manuscript_audit.py` | 稿件抽取（PDF/docx/xlsx→文本）与一致性体检（数字、图表号、引文序号、样本量、术语变体）+`--diff` 原意核对 |
| `scripts/ref_verify.py` | DOI **结构**校验（DOI 无校验位）、ISSN/ISBN 校验位、在线核验三态、GB/T 7714 与 Vancouver/APA 格式化、角标对齐 |
| `scripts/skill_router.py` | 从注册表按话术/能力域/技能名查候选目录名：`--query`／`--domain`／`--name`／`--list-domains`／`--json`／`--selftest` |
| `scripts/_shared.py` | 内部共享模块：环境探测、路径、日志、JSON 校验；无命令行入口，不计入脚本数 |

统一参数：`--probe`（打印探测结果与降级决定）、`--selftest`、`--fixtures`、`--json`、`--out`、`--log`。退出码：0 成功；2 输入非法可修正；3 产物结构不完整；4 依赖/网络缺失已降级；9 内部断言失败。脚本只输出信号与数值，结论由模型给；模型只引用脚本数值，不手抄。

调用契约（最小 spec，`--help` 里同样可查；表中花括号是 JSON 字面量，不是待替换的占位符）：

| 脚本 | 取值全集 | 最小 spec |
|---|---|---|
| stats_suite | `compare`／`corr`／`linreg`／`logistic`／`km`／`logrank`／`cox`／`roc`／`samplesize` | `{"analyses":[{"type":"compare","value":"cr","by":"group"},{"type":"cox","time":"time","status":"status","x":["cr"]}]}` |
| svg_figure | `km`／`forest`／`box`／`scatter`／`column`／`line`／`roc`／`waterfall` | `{"type":"km","series":[{"name":"A","points":[[0,1.0],[3,0.9]]}],"annotations":[{"text":"HR 0.62 (0.41-0.94)"}]}`；森林图可用 `xticks_n`（2–8，默认 5）控制刻度数，窄 HR 区间会自动省略拥挤刻度 |
| office_writer | `kind`＝`xlsx`／`docx`／`pptx`／`budget` | xlsx：`{"kind":"xlsx","sheets":[{"name":"tab-01","headers":["变量","P"],"rows":[["年龄","0.32"]],"widths":[18,8]}]}`；budget：`{"kind":"budget","items":[{"item":"实验耗材","unit_price":1200,"quantity":10,"note":"单价来源：2025 年招标价"}]}`（`quantity` 必填，写错键名即报错） |
| data_reconstruct | `grim`／`grimmer`／`iqr`／`percent`／`ratio`／`table2x2`／`vectors` | `{"items":[{"type":"grim","n":24,"mean":62.5,"decimals":1,"lo":18,"hi":105}]}` |
| manuscript_audit | 无 spec，走文件参数 | `--audit draft.docx`／`--extract draft.pdf`／`--diff old.md new.md` |
| ref_verify | `--style`＝`gbt7714`／`vancouver`／`apa` | `{"references":[{"authors":"Singer M; Deutschman CS","title":"Sepsis-3","journal":"JAMA","year":"2016","volume":"315","issue":"8","pages":"801-810","doi":"10.1001/jama.2016.0287"}]}` |

四条硬约束：① 字段写错、漏字段、JSON 语法错、文件不存在、顶层非对象 → **exit 2 ＋ 定位信息**（如 `无法解析 spec.json 的 JSON：3:7 Expecting value`），**全仓不得把 Traceback 落给用户**；② 列名不存在时列出输入实际列名；③ xlsx 的 `headers` 是表头（加粗＋冻结首行），`rows` 是数据，两者不混用；④ `status` 只接受 0/1，出现其它编码按「非 0 即事件」处理并输出显式警告，不静默吞掉。

**未实现（明示，不得表述成已完成）**：多标签／一对多编码（一行多个诊断或多种用药）必须先拆成计数列或虚拟变量列再分析；Shapiro-Wilk 未实现（用 Jarque-Bera 替代）；GRIMMER 只做必要条件不做全枚举；docx／pptx 只做结构校验，未在 Office 中渲染验证。

## §9 环境与降级（先跑 `--probe`）

| 探测项 | 探测方式 | 缺失时行为 |
|---|---|---|
| Python 版本与第三方包 | 运行时导入尝试 | 主逻辑全部 stdlib-only，缺包只影响增强通路 |
| R 及扩展包 | 可执行文件存在性＋包加载 | 降级为「生成 R 代码＋显式未执行」 |
| 渲染后端（PDF/PNG） | 依次尝试外部转换器与系统图形接口 | SVG 照出，PDF/PNG 显式「未生成＋原因＋补做方法」 |
| 网络 | 一次只读连通性检查 | 检索只给检索式；引文全部标「待核验」 |
| PDF 文本层 | 抽取时判定 | 无文本层即报「未提取到文本层」，要求粘贴正文或改用外部 PDF 工具，禁止猜测补全 |

三条通路，每次交付必须在说明里点明走了哪条：

| 通路 | 含义 | 适用 |
|---|---|---|
| A 真执行 | 脚本真跑，产物齐全，日志有条目 | 统计、出表、出图、倒推、体检、核验 |
| B 出代码不执行 | 给出可运行脚本与运行说明，明确标「未执行」 | 缺 R/缺包/缺网络时的统计与建模 |
| C 只给方法 | 给判据、模板、检索式，不产出文件 | 缺全部依赖且用户只要方法 |

执行后端由探测决定，禁止假设任一后端存在：

| 后端 | 触发条件 | 覆盖 | 上限 |
|---|---|---|---|
| P-stdlib | 任何 Python 3.9+（必达基线） | 全部能力：统计自算、SVG 直写、xlsx/docx/pptx 手写、PDF 抽取、DOI 结构校验、倒推求解 | 无字体栅格化；PDF 只保拉丁文本；pptx 只 2 版式 |
| P-rich | 探测到 openpyxl／matplotlib／numpy＋scipy | openpyxl 与 matplotlib 的版式增强（xlsx 样式、更细排版）；**统计数值 v1 一律 stdlib 自算，不做交叉校验**（numpy／scipy 未接线，装了也不会改变结果） | 仍无 python-docx／python-pptx，docx 与 pptx 照走手写 |
| P-COM | Office／WPS 已注册且用户显式要求 | 复杂表格、域代码、目录、精细母版 | 非幂等、拉起 GUI、不进任何自检；失败必须回退并留痕 |
| 渲染后端 | soffice／inkscape／cairosvg | SVG → PDF/PNG | 全缺时 PNG 不可达，显式报「未生成＋原因＋补做方法」 |

**每次交付必写一行**：本次通路＝统计…／绘图…／xlsx…／docx…／pptx…，且与运行日志的 `chosen` 一致；写不出这行即视为未交付。

## §10 references 索引（按需加载，不全量读）

| 文件 | 何时加载 | 一句话边界 |
|---|---|---|
| `references/evidence-search.md` | 检索、筛文、证据集 | 只交证据集与筛选留痕，不下结论 |
| `references/study-design-and-grant.md` | 选题、设计、样本量、标书 | 只谈未做的事（将来时） |
| `references/manuscript-reading-review.md` | 审阅、解读、诚信异常 | 三产出版块；只出意见不改稿 |
| `references/writing-and-citation.md` | 撰写、引文格式与核验 | 只做成稿与引文流水线 |
| `references/language-polish.md` | 润色、去 AI 味 | 只改表达，不改结构、不加事实 |
| `references/statistics.md` | 任何数据分析 | 只做从数据到统计量 |
| `references/figures-and-slides.md` | 出图、示意图、PPT | 只做视觉产物 |
| `references/data-reconstruction.md` | 倒推、GRIM | 只做数值反解与置信度 |
| `references/provenance.md` | 索要来源、许可审查 | 只记来源与许可，不含方法正文 |
| `references/research-skill-registry.md` | 需要专科工具/框架实现/用户点名技能/内置不够 | 只做路由与边界，不内联外部技能正文；内置 13 项仍优先 |
| `references/research-skill-index.csv` / `.json` | 机器检索、脚本查询 | 全量 433 条：目录名｜能力域｜来源仓库｜触发词｜摘要 |

## §11 外部指针（统一走注册表，卸载不退化）

**总入口**：`references/research-skill-registry.md` 覆盖本次 10 个科研仓库共 433 个已装技能（15 个能力域）。原手列指针保留为常用捷径：

| 技能目录名 | 用途 | 何时提示 |
|---|---|---|
| `r-medical-research-master` / `r-medical-stats` | R 九域统计与执行配方 | 需复杂实现且 R 可用 |
| `chinese-medical-paper-writer` | 中文刊格式细节 | 投中文核心刊需更细版式 |
| `sci-writing-master` | 英文学术范式对照 | 需审稿人视角范例 |
| `r-clinical-prediction-model` / `r-nhanes-analysis` | 预测模型、加权抽样实现 | 加权复杂抽样、RCS 自写 |
| `pptx-posters` / `latex-posters` | 会议海报（非本技能能力） | 用户明确要海报 |
| `pdf` / `markitdown` | 复杂版式 PDF 转文本 | 稿件无文本层或版式复杂 |

**注册表中本次新增的高频入口**（完整 433 条查注册表/索引）：

| 能力域 | 代表技能目录名 | 何时加载 |
|---|---|---|
| 文献检索与证据 | `ars-deep-research`、`ars-sr-screener`、`nature-academic-search`、`nature-downloader` | 深度检索、系统评价筛文、全文获取、MeSH 策略 |
| 撰写与引文 | `ars-academic-paper`、`ars-academic-pipeline`、`research-paper-writing`、`nature-paper2word` | 多角色写作流水线、论文故事线、Word 成稿 |
| 审阅返修与诚信 | `ars-academic-paper-reviewer`、`nature-reviewer`、`nature-response`、`rebuttal-guidance` | 多视角审稿、逐条回复、返修包一致性 |
| 润色与去 AI 味 | `anti-defensive-writing`、`anti-defensive-writing-en`、`paper-polish` | 去防御性写作、中英定制润色 |
| 科研绘图与演示 | `scientific-figure-making`、`nature-figure`、`nature-image2ppt`、`aris-paper-talk` | 论文级 Matplotlib 图、图片转可编辑 PPT、讲稿 |
| 统计/组学/药化 | `statistical-analysis`、`scanpy`、`rdkit`、`diffdock`、`pydeseq2` | 专科实现，内置判据不足时 |
| AI/ML 研究工程 | `airs-autoresearch`、`aris-auto-review-loop`、`hf-cli`、`huggingface-datasets`、`huggingface-llm-trainer` | 有研究问题的实验复现、评测、数据与模型操作 |
| 专利与技术交底 | `aris-patent-pipeline`、`aris-patent-review`、`nature-paper-to-patent` | 专利检索、交底书、权利要求草稿 |

原则：任一内置能力必须可独立完成；外部技能只提供更精细或专科实现，不提供必需能力；探测不到就静默走内置路径，不报错、不提示缺失。调用外部技能前先写一行路由理由到运行日志（候选、选中、理由），再加载其 SKILL.md。

## §12 不做什么（非目标）

| # | 非目标 |
|---|---|
| 1 | 不删除、不停用、不迁移任何现有技能，只出建议清单 |
| 2 | 不用图像生成模型冒充数据图 |
| 3 | 不编造文献、DOI、指南条款、环境事实 |
| 4 | 不越权：不写用户技能目录、不改用户原始数据 |
| 5 | 不做通用助手：闲聊、通用代码、办公排版不接 |
| 6 | 不做数据工程：格式转换、数据库运维不接 |
| 7 | 不把外部技能正文搬入本包；注册层只登记目录名与触发词 |
