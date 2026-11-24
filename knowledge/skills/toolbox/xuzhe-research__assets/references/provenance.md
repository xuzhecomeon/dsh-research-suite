# 来源与许可（provenance）

> 记录来源技能目录名、模块、许可、吸收方式与未吸收项。**只记来源，不含任何方法正文**。写作口径统一为「重述式提炼」：方法、判据、清单结构可学；表达一律用本技能自己的语言重写，不逐字搬运第三方正文。

## A. 骨架技能（11 个，每模块恰好 1 个）

| 来源目录名 | 模块 | 许可 | 吸收方式 |
|---|---|---|---|
| biomed-literature-pipeline | 文献检索 | 未标注 | 骨架；实现层依赖整体废弃，检索规则重写 |
| idea-evaluator | 科研思路 | 未标注 | 骨架；五维框架改写为临床六设计类型 |
| pre-submission-reviewer | 论文审阅 | 未标注 | 骨架；范式移植为临床报告规范 |
| chinese-medical-paper-writer | 撰写与引文 | 用户自建 | 骨架；规则表近原文吸收，正文重写 |
| citation-management | 参考文献 | MIT | 骨架；只取流程与判据，不继承其脚本宣称 |
| paper-polish | 润色 | CC-BY-NC-SA-4.0 | 骨架但**整体重述**，未沿用原句与示例 |
| r-medical-research-master | 统计分析 | 用户自建 | 骨架；环境事实全部废弃，改运行时探测 |
| academic-figures | 绘图 | 用户自建 | 骨架；"图中严禁中文"改为按目标刊语种 |
| geng-academic-fraud-detector | 诚信异常信号 | 用户自建 | 骨架；人格化段落全部删除，只留检测维度 |
| pptx-generator | 科研 PPT | MIT-0 | 骨架；依赖库改为自写最小 OOXML |
| literature-close-read | 论文解读 | MIT | 骨架；契约式写法沿用结构不沿用文字 |

## B. 部分吸收（按簇，只记去向）

| 簇 | 来源目录名 | 许可 | 吸收去向 | 未吸收项 |
|---|---|---|---|---|
| 检索精度 | pubmed-database、openalex-database、aris-semantic-scholar、literature-review、scholar-lit-review | 未标注 | 检索式与多源去重 → evidence-search | 其接口实现与实测结论 |
| 深研与全文 | deep-research、ars-deep-research、nature-downloader、ps-deep-research | deep-research 为 CC-BY-NC-SA-4.0，余未标注 | 简报冻结、六道 gate、失败分类 → evidence-search | 重度编排与覆盖率闸门 |
| 设计与新颖性 | scholar-design、aris-idea-creator、aris-idea-discovery、aris-novelty-check、hypothesis-generation、brainstorming-research、aris-experiment-plan、clinical-research-design-extractor | 未标注 | 设计卡与三档新颖性 → study-design-and-grant | CS 范式（baseline／ablation／identification／DAG） |
| 标书 | arf-review-grant、aris-grant-proposal、nature-proposal-writer（目录名与内部名称不一致，引用以目录名为准） | 未标注 | 标书骨架与四视角预审 → study-design-and-grant | 其模板条款（一律改为用户提供或实时获取） |
| 审阅工序 | arf-review-paper、ars-academic-paper-reviewer、nature-reviewer、peer-review、paper-audit、aris-kill-argument、academic-pre-review-committee、scholar-respond | 未标注 | 双视角、先攻击后裁定、冲突意见处理 → manuscript-reading-review | 多智能体编排与版本契约 |
| 诚信核验 | aris-paper-claim-audit、aris-integrity-forensics、wang-paper-ct、scholar-verify、scientific-critical-thinking、arf-review-paper-code | 未标注 | 六式与七维合并为九维、claim 三态 → manuscript-reading-review | 评分分档与"检测器"式宣称 |
| 中文撰写 | sci-writing-master、writing-medical、scholar-write、medical-review-writer、literature-review-writing、paper-orchestration、ars-academic-paper；paper-writer、clinical-reports、cover-letter | paper-writer 为 CC-BY-NC-SA-4.0，余未标注 | 章节要素卡、证据锚点、综述三轴 → writing-and-citation | 变更日志与"更新摘要"段 |
| 英文范式 | science-figures、figures-python、scientific-visualization、airs-academic-plotting | 未标注 | 期刊预设、配色与统计严谨性 → figures-and-slides | 依赖库假设 |
| 润色去味 | wb-academic-polish、scholar-polish、humanizer-zh、humanizer、qinyan-paper-polish、paper-polisherskill、paper-revision-sop、stop-slop、no-ai-slop、style-journal-rewrite、paper-deweight-fd、academic-polish-s、writing-core | 未标注 | 四层模型、中英双语痕迹清单、空话分 → language-polish | "AI 率检测"与查重宣称 |
| 统计各域 | r-medical-stats、local-r-clinical-stats、r-clinical-prediction-model、r-machine-learning-interpretability、r-real-world-evidence、r-propensity-score-methods、r-nhanes-analysis、r-mendelian-randomization、r-trajectory-models、r-aging-cohort-databases、r-pharmacology-singlecell-mr、statistical-analysis、scholar-analyze、exploratory-data-analysis | 用户自建 | 六道闸门、静默陷阱、校准与 CCW → statistics | 全部环境事实（版本／路径／包数量） |
| 绘图实现 | wnmc-figure、ai-figure-studio、figure-designer、figures-diagram | 用户自建或未标注 | SVG 坑位清单、五阶段重绘、出图门禁 → figures-and-slides | 外部生图服务与 AI 内脚本依赖 |
| PPT 叙事 | aris-paper-slides、ima-lit-meta-ppt、dashi-ppt、paper-slide-deck、arf-explorable-pptx、ppt-design、html-ppt、elegant-ppt-builder | 未标注 | 讲型到时间预算、页型契约、坏 deck 清单 → figures-and-slides | 母版主题定制与外部项目生成器 |
| 解读与版本 | nature-paper-card、arf-paper-version | 未标注 | 卡片字段与版本差异栏 → manuscript-reading-review | — |
| 引文格式 | qinyan-citation、nature-ref-verifier、reference-verification、find-paper-references、paper-reference-formatter、format-references-zotero | 未标注 | 缺字段三条处理、三源交叉、五段报告 → writing-and-citation | 文献管理软件依赖 |

## C. 仅作指针（不内联任何文档）

| 簇 | 数量 | 处置 |
|---|---|---|
| 生物医学数据库取数 | 19 | 只在 statistics.md 的四列指针表出现：名称｜取数协议｜凭据/许可｜是否需密钥 |
| 统计建模底座（pydeseq2、scanpy、scvi-tools、deeptools、arboreto、datamol、deepchem、diffdock、anndata、medchem、molfeat、torchdrug、rdkit、umap-learn） | 14 | 一行说明"实现底座见外部技能，本技能只做方法与判据" |

## D. 明确未纳入

biorxiv-database、nature-academic-search、nature-literature-pipeline、qinyan-paper-search、reference-retrieval-skill、scientific-brainstorming、qinyan-topic-analysis、basic-research-design-extractor、nature-writing、biomedical-sci-manuscript、airs-ml-paper-writing、thesis-writing-companion、citation-manager、academic-reference-enhancer、bib-search-citation、nature-citation、paper-checker、prompts-collection、nature-polishing、scholar-causal、data-analysis-pro、scientific-schematics、scientific-graphical-abstract、xiantao-plot-api、sfkislev-flue-illustrator、scientific-drawing、nature-figure、scientific-slides、guizang-ppt-skill、codex-ppt、slides、frontend-slides、ppt-master、nature-paper2ppt、nature-image2ppt、sglk998、qinyan-paper-analysis、aris-deepxiv、nature-reader、nature-shared。

未纳入原因可归为四类：薄壳（正文在包内不存在的 references）、外部服务或 API key 依赖、与临床范式冲突、重复归口只需一版。体积型候选（ML 会议范式、学位论文产线、海报产线、LaTeX 产线）一律按外部指针处理，不搬正文。

## E. 审计前提（决定了本技能不继承任何宣称）

| 事实 | 数值 | 后果 |
|---|---|---|
| 仅有单文件的技能 | 720 个中 558 个 | 多数"技能"其实只是一份提示词文档 |
| 宣称脚本但文件缺失 | 223 个技能 | 任何"运行某脚本"的指令一律不继承 |
| 宣称参考文件但文件缺失 | 440 个技能 | "按需加载深入参考"是空指针 |

因此本技能不写"支持 N 种图表""继承某技能的某能力"，也不引用任何被淘汰技能的文件。凡宣称的能力必须在本包内有对应正文判据与脚本落点（SKILL.md §8、§10）；做不到的写"仅给方法与代码模板，不谎报已完成"。逐条逐候选的裁决明细在设计阶段产出，不随包分发；本表按簇归并，仅保证来源与许可可追溯。

GPL／LGPL 类来源（scikit-survival、denario、etetoolkit 等）**未纳入正文**，仅作外部指针，避免著佐权义务传染。许可标注为"未标注"者按"表达不可抄、方法可用"处理，一律重写；若需逐条核对许可原件，应回技能库读取各目录的 frontmatter 与 LICENSE，本包不复制其许可全文。

## F. v1.1 统一注册层（只登记，不内联）

| 来源仓库 | 条目数 | 许可/性质 | 吸收方式 |
|---|---:|---|---|
| Imbad0202/academic-research-skills | 5 | 多角色论文流水线 | 注册为「撰写与引文/审阅/文献检索」首选或备选；不搬正文 |
| K-Dense-AI/scientific-agent-skills | 177 | MIT（单技能许可各异） | 注册为「组学/药化/材料/统计/工具」专科实现；不搬正文 |
| Yuan1z0825/nature-skills | 24 | 未标注 | 注册为「检索/撰写/审阅/绘图/返修/专利」入口；不搬正文 |
| wanshuiyin/Auto-claude-code-research-in-sleep | 87 | 未标注（去重后） | 注册为「AI 科研实验/审阅/论文/专利」；不搬正文 |
| Orchestra-Research/AI-Research-SKILLs | 98 | MIT | 注册为「AI/ML 研究工程」；不搬正文 |
| HKUSTDial/Supervisor-Skills | 12 | CC BY-NC-SA 4.0 | 注册为「选题/引言/写作/投稿前评审/绘图建议」；不搬正文 |
| ChenLiu-1996/figures4papers | 1 | 论文图脚本库 | 注册为「科研绘图」实现参考；不搬正文 |
| huggingface/skills | 26 | 官方技能库 | 注册为「AI/ML 数据与模型操作」；不搬正文 |
| Master-cai/Research-Paper-Writing-Skills | 1 | MIT | 注册为「撰写与引文」；不搬正文 |
| Adkid-Zephyr/anti-defensive-writing-Skill | 2 | MIT | 注册为「润色与去 AI 味」；不搬正文 |

合计 433 条去重后技能目录，全部写入 `references/research-skill-index.csv/json` 与 `research-skill-registry.md`；调用时由 `scripts/skill_router.py` 查询。**未纳入正文**：全部外部技能的规则正文、脚本与参考文件；本技能只提供目录名、触发词、来源和冲突裁决，能力仍由内置 13 项与内置脚本承担。
