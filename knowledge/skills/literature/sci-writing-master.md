<!-- source: SCI-Writing-Master @ sci-writing-master | domain: literature -->

---
name: SCI-Writing-Master
description: |
  顶级 SCI 医学论文写作与润色 skill。基于 249+ 篇近五年 Lancet/JAMA/NEJM/BMJ/Cell/Nature 级
  顶刊论文逐篇精读提炼，覆盖 19 种论文类型的写作标准（§1–§19；其中 §19.11 危重症七大治疗域、
  §19.12 ICU 支持治疗、§19.13 ICU 临床 RCT/队列、§19.14/§19.15/§19.18 医学 AI 与深度学习
  研发-验证-临床实施、§19.16 脓毒症/ARDS 基础转化与 GBD 负担、§19.17 医学 AI 基础模型与
  LLM 临床决策），以及参考文献选取与引用证据总结范式（§20，跨类型通用模块，含传染病预防 RCT、
  高血压 add-on RCT、食品/环境健康 SRMA、非医学文献语言可迁移性等）；另蒸馏 9 份写作专著/课件
  （v1.16：Glasman-Deal《Science Research Writing》2nd ed 全书 + Stanford《Writing in the
  Sciences》课件 8 单元，约 900 页）。语言范式、句式库、词汇精确度、段落密度、图表语言等
  垂直维度均有独立档案，并配套差异化工作流。
  v1.17 新增范文对标与差距诊断：12 维对标量表 + 1141 篇范文亮点卡（源自知识库 3302 篇 PDF
  的量化特征抽取与 1141 篇逐篇精读）+ 分类型结果呈现标准 + 9 类高频缺陷库。
  当用户需要撰写、润色、修改英文学术论文（论著、综述、Meta 分析、病例报告、基础研究等）时触发；
  当用户给出范文要求「按这个水平改我的稿」、或要求「按高质量标准润色」、或问「我这篇还差什么/能投什么档次」时，
  启用范文对标与差距诊断能力。
  适用于：医学/生物学/公共卫生等生命科学领域的英文 SCI 论文写作。不适用于：中文论文、
  非学术写作、学位论文格式修改。
---

# SCI-Writing-Master

> **Skill来源**：基于 **249+ 篇** 近五年顶级SCI论文（NEJM 25+ / Lancet 5+ / JAMA 4 / Nature/Cell/Nature Methods/Science 12+ / 其他 4+）系统性精读提炼出的可复用写作范式集合，并蒸馏 **9 份写作专著/课件**（Glasman-Deal《Science Research Writing》2nd ed 全书 + Stanford《Writing in the Sciences》课件 8 单元，约 900 页，v1.16 新增；蒸馏单元按合并方式存为 6 个文件，见 `references/BOOK_DISTILL_UNITS/`）。Phase 3 扩为 46 篇；v1.5 扩为 92+ 篇；v1.6 在 v1.5 之上新增 **15 种论文类型的精细化写作标准**（`workflows/workflow_article_type_standards.md`）；v1.7 在该 15 种类型基础上新增 **传染病预防 RCT、高血压 add-on RCT、食品/环境健康 SRMA 3 类独立/子类标准**，扩充 Nature/Cell 基础研究标杆库与「非医学文献语言可迁移性」章节，覆盖细分类型扩至 **19 种**（v1.8 新增 §19 危重症/ICU RCT 集群标准），每种类型仍给出 **10 个固定维度**（标题/摘要/引言/方法/结果/讨论/图表/引用/标杆范文/差异对照）的具体可操作规范。
>
> **学习日期**：2026-08-10/11（v1.7 batch3）、2026-08-18（v1.8 batch4 危重症RCT）、2026-08-19（v1.9 batch5 急危重症/复苏/创伤/ARDS/心脏骤停/心源性休克 RCT；v1.10 全库95篇引用实践分析）、2026-08-20（v1.11 batch6 ICU支持治疗/器官支持RCT）、2026-08-22（v1.12 batch7 含15篇AI/DL算法研发验证 + 8篇ICU临床RCT/队列）、2026-08-23（v1.13 batch8 含数字病理/眼底表型/影像筛查/EHR时序+强化学习/临床共识定义共22篇）
>
> **核心承诺**：写出来的英文，每一句都能在顶刊原文中找到风格对应；每一种表述都有"标杆等级"的依据；每一种类型的投稿都有具体可对齐 Top-Journal 的字数、子节、必引 RCT 阈值。

## v1.19 更新摘要（2026-10-31，1141 张卡片字段全量补齐）

本次对「高质量医学论文」库 3543 个条目对应的 1141 张卡片做内容级重写，按 `references/CARD_FIELD_PROTOCOL.md` 逐字段回原文补齐：

- **范围与结果**：筛查出 393 张存在字段空缺的卡片（讨论 265、n 155、统计报告 134、图表 43，类别间有重叠），全部回原文重新提取。补齐后，1141 张卡片的 n／统计报告／讨论／图表 四类字段共 4564 行全部有实质内容，`—` 占位清零。
- **纠正错误映射**：过程发现部分卡片在 v1.17 生成时题目与原文错配（多为中文概括题名与库内英文原题对不上），共 40 张，已重新检索定位（39 张 high、1 张 medium）并据正确原文重写；其中 3 张（1766、1638、0641）最终仍未取得可对应原文，按规范写明「待核」而非臆造。
- **三态区分落地**：全文不再出现把「本次未提取」写成「原文未报告」的判定。统计中：标注「未能在节选中核实」194 条，标注「不适用（如单例报告、叙述性综述）」126 条，其余为实证内容。
- **过程残留清理**：卡片内「包中」「包内」「证据包」类过程性表述共 1208 + 173 + 57 处全部改为「原文」体例；字段内中文语境的半角分号统一为全角。

## v1.18 更新摘要（2026-10-31，卡片字段规范化与包体质量修复）

本次不新增写作范式，只修包体内的一致性、可核验性与可读性：

- **新增 `references/CARD_FIELD_PROTOCOL.md`**：为 1141 张卡片定 12 字段写法标准，核心是把三态分清——已提取／原文未报告／不适用；并单列「本次未提取」的写法，禁止把它写成原文缺陷。附缺失字段补写流程与交付前校验清单。
- **新增 `examples/USAGE_EXAMPLES.md`**：六个场景的开口话术、对应工作流与交付物形态。
- **修复包体一致性问题**：description 篇数口径统一为 249+ 篇并补全 §19.16–§19.18 章节指针；删除 35 处指向不存在目录的精读笔记引用；清理卡片中 1208 处「包中」类过程性残留；版本摘要改为严格倒序；Step 1 任务表扩至 14 条并加两组易混入口的判据。
- **卡片内容级重写（进行中）**：已完成 0392、0197 两张示范，均回原文重新提取统计段与讨论段，并撤回原卡中把「当时未提取」误写成「原文未报告」的缺陷判定。全库尚有 393 张存在字段空缺（讨论 265、n 155、统计报告 134、图表 43，类别间有重叠），按本规范分批回原文补写。

## v1.17 更新摘要（2026-10-31，基于「高质量医学论文」知识库全库逐篇精读）

本次 v1.17 新增**范文对标与差距诊断**能力，解决的是「用户给一篇文章要求按范文水平润色，如何判断差在哪、怎么改」这一类需求。数据来源：对知识库 3543 个条目（3302 篇 PDF）逐篇解析全文，3234 篇完成量化特征抽取（研究类型、统计报告要素、图表数、结果段篇幅与数字密度、语言指标），1141 篇研究型文献逐篇深度精读并生成亮点卡（58 个批次，卡片字段 16 项）。

- **新增 `references/EXEMPLAR_BENCHMARK.md`（约 1.8 万字，8 节）**：12 维对标量表（D1 研究问题与设计匹配、D2 样本量与把握度、D3 结果呈现骨架、D4 统计报告完整度、D5 图表策略、D6 亚组与敏感性、D7 局限陈述、D8 结论克制、D9 语言范式、D10 段落密度、D11 引用与溯源、D12 可复现性），每维给 0/1/2/3 锚点与**本库实测覆盖率**（如 RCT 仅 77% 报告 95%CI、30% 报告样本量论证、15% 报告多重比较校正）；研究类型判定树（11 类，问题链式判定）；范文亮点识别 20 条检查点（结果呈现 6 条、统计报告 6 条、结构论证 5 条、图表规范 3 条）；11 类分类型结果呈现标准（骨架 + 必须报告要素 + 本库实测 + 高频缺陷 + 标杆卡 ID）；9 类高频缺陷库（按 2000 余条卡片 weak 字段的频次排序：局限段 520、效应量与 CI 398、样本量与把握度 394、结果呈现 303、统计方法 212、结论越界 205 等）；20 组中英双语报告句式模板（主结局、阴性结果、非劣效、复合终点、亚组、敏感性分析、队列、剂量-反应、竞争风险、诊断、预测模型、Meta、异质性、基础实验、病例报告转归、局限、结论克制、数据可得性）；全库基准值速查表。
- **新增 `references/EXEMPLAR_INDEX.md` + `references/EXEMPLAR_CARDS/`（12 个文件，1141 张卡，约 3 MB）**：每张卡给研究设计、样本量、研究问题一句话、结果段骨架（`→` 连接的各步）、三类结局的统计报告方式、图表分工、1 条可复用原句（逐字摘自原文）、讨论结构、3 条亮点、0–3 条不足、可对标的维度标签、适用场景。覆盖：队列 232、RCT 190、基础实验 145、预测模型 131、病例报告 131、Meta 74、横断面 65、诊断准确性 52、综述 40、观察性临床 31、系统评价 31、病例对照 19；英文 817、中文 324。
- **新增 `workflows/workflow_exemplar_gap.md`**：五阶段工作流（P0 稿件解析 → P1 范文解析 → P2 12 维打分 → P3 差距清单 → P4 改写与补数据 → P5 交付自查），明确三种动作（改写 / 补写 / 标注）与四条禁令（不改数据、不迁结论、不虚构分析、不空泛批评）。
- **与既有模块的关系**：本节负责「证据与结构层」诊断，`workflow_polish_existing.md` 负责语言层润色，两者串联；`workflow_article_type_standards.md` 的 19 种类型标准给「应该怎么写」，本模块给「同类高水平文献实际怎么写、你差在哪」，互为补充。卡片库与 `SENTENCE_LIBRARY.md` 不重复：前者是整篇的结构与报告方式，后者是句级模板。

## v1.16 更新摘要（2026-09-10，基于 9 份写作专著/课件蒸馏：Glasman-Deal《Science Research Writing》2nd ed 全书 + Stanford《Writing in the Sciences》课件 8 单元）

本次 v1.16 按 distill 流程（五维提取→三重验证→有用×能用门禁→关系链接）蒸馏用户上传的 9 份英文论文写作专著/课件（合计约 900 页），全部原文摘录、不意译，产出 6 份分卷蒸馏档案（`references/BOOK_DISTILL_UNITS/`，共 3900 行）与 1 份主档案（`references/WRITING_BOOK_DISTILLED.md`）：

- **新增 IMRaD 章节级结构模型体系**（教材方法论层，与 249+ 篇论文实证层互补）：引言四组件模型（建立重要性→研究地图→缺口/动机→描述本文+happy words；对称漏斗、show the wall before the bricks、换刊必须改首句）；方法六组件模型（菜单式+agentless passive 五用法消歧决策表）；结果四块模型；讨论九组件模型（与引言镜像，四对接口）；结论 11 组件模型 + Owning your contribution；摘要四类型+通用模型+12 项自查；标题六规则（≈12 词、复合名词五级链、预测-兑现五准则）。
- **新增确定度语言体系**（本 skill 措辞严谨性规则/硬性规则16 的理论根基）：Certainty Continuum（speculation→proof 连续谱、31 条因果动词六层强度、四类降险语言）+ Modal Verbs 六类（ABLE/POSSIBLE/EXPECTED/ADVISABLE/OBVIOUS/NECESSARY，might<may、must not≠impossible 等语义区分）——写作时对每个评价/启示句先选确定度档位再选词。
- **新增全量功能词表（约千条模板，全部原文摘录）**：引言四区域词表（ESTABLISHING SIGNIFICANCE ~60 条、研究活动动词 ~80、GAP 双组 ~86 条、PRESENT WORK + happy words）；方法九大词表（GIVE SOURCE/空间/技术动词 ~100/顺序 ~70/JUSTIFY 31/CAUSE 26/CARE 41/COMPARE 三档/INDICATE ISSUES）；结果词表（图示动词 11、数量五组、频率十级、比较 41 条）；讨论五组词表（MAP TO LITERATURE 49、happy words 80、!-substitutes 22 等）；附录前缀表 59 行 + 研究动词表 ~320 条。
- **新增句子级写作铁律与流程**（Stanford 体系）：有效写作三原则、clutter 六类、长短词替换表、否定转正面表、动词名词化对照、句长 20–26 词/段落 150–170 词基准、写作顺序（图表→结果→方法→引言→讨论→摘要→标题）、时间配比、Revision 六步、终稿三查、Citation Propagation 教训（引用必须回溯原始出处，与硬性规则7 同源）、图表规范（三线表/Figure Legend 五要素）、抄袭三形态/署名/利益冲突/评审八步。
- **关系链接与压力测试**（主档案 §14）：与既有范式互补（论文实证 vs 教材方法论）、同源（确定度语言↔硬性规则16；Citation Propagation↔硬性规则7）、重叠不重复建设（SENTENCE_LIBRARY 不动）；标注三处不该用的场景（期刊结构式优先/摘要限制定制/非 IMRaD 文体只取句子级规则）。

## v1.15 更新摘要（2026-09-09，基于 43 篇 batch10：医学 AI/ML 临床预测与诊断经典标杆）

本次 v1.15 精读并移入 2026-09-09 文件夹的 43 篇，使知识库标杆从 206+ 扩至 **249+ 篇**：

- **新增 §19.18 医学 AI/ML 临床预测与诊断经典标杆子域（43 篇 batch10 标杆）**：补齐 AI 医学证据体系的「经典层」（2016-2023 高被引标杆），与 §19.14/§19.15/§19.17 构成「经典→前沿→方法学」全谱系。覆盖四大类：预测模型研发（EHR/时序/评分）15 篇（circEWS、LSTM ICU 死亡率、EHR-GRU 心衰、MESA、AMI、自杀预测、WATCH-DM、AISE、EWS 2.0、脓毒症 4 表型等）、诊断影像 AI 与人机对比 12 篇（皮肤癌 Nature 2017、CAMELYON16、CheXNeXt、DeepMind 视网膜、DeepDR、乳腺癌筛查国际评估等）、外部验证/泛化/公平性/监管实施 5 篇（Zech 泛化、Epic 外部验证、AI 种族识别、HYPE RCT、IDx-DR pivotal）、多组学·组织学·转化预测 11 篇（多组学乳腺癌 Nature 2021、DELFI cfDNA、CRC MSI Transformer、胶质瘤 VGG-Cox、冠周脂肪 radiotranscriptomic、AD 可解释 DL 等）。核心范式：**验证设计五级阶梯（L1 内部拆分→L2 时间拆分→L3 外部验证→L4 部署/shadow mode→L5 RCT/pivotal）与结论强度映射**、人机同图证据链三件套（独立金标准测试集+人机同坐标对比+混淆矩阵）、「互补」替代「碾压」结论范式、AUC 翻译为工作量语言（NNE/警报负担/二读减负）、指标四层报告（判别+校准+操作点+效用，DCA 缺位为全批共性缺口）、可解释性三级写法（事后归因→临床动作绑定→独立效度对齐）、时代对照自查（2017-2021 经典论文普遍缺 TRIPOD 声明/校准/DCA，按现行 TRIPOD+AI 标准自查实质要素）。
- **引用实践（§20/硬性规则17）batch10 实证补强**：引言两流派（主题打包式 vs 逐条单引）；转述动词按证据强度分级（RCT=demonstrated、队列=reported、共识=concluded）；主动引用不利文献建立可信度（乳腺癌筛查评估引 Zech/Fenton）；厂商灰色文献摆上台面对比（Epic internal documentation）；讨论数值化对标三手法（数值并置/同数据重实现基线/跨物种同向印证）；透明性三模板（拒绝数据+开放代码/双开放/受限开放）与企业折中范式。

> 注：本次 43 篇于 2026-09-09 首次移入时调用失败（请求体格式错误，见下方教训），2026-09-10 已用正确格式全部重移并逐篇核验（`move_results[media_id].ret_code==0`，根目录文件清零、2026-09-09 文件夹条目=43，零遗漏）。**move_knowledge 正确用法（硬性）**：请求体必须为 `{"src_knowledge_base_id":KB,"dst_knowledge_base_id":KB,"src_knowledge_base_name":KB名,"dst_knowledge_base_name":KB名,"src_folder_id":""(根)或folder_id,"dst_folder_id":目标folder_id,"infos":[{"media_id":mid}]}`；media_id 直接放顶层（`"media_id":mid`）属畸形请求，接口会返回顶层 code 0 但 move_results 为空、实际不移动（静默空操作）；成功判定必须以 `data.move_results[media_id].ret_code==0` 为准，且移动后需拉列表核验根目录计数减少、目标文件夹条目增加。已全部逐篇精读并产出 43 份笔记（特殊情况：batch10_33/batch10_36 两篇 PDF 仅含补充材料，已按已发表全文补齐精读并注明；batch10_27 为 bioRxiv 预印本，已注明正式发表版对应关系）。

## v1.14 更新摘要（2026-08-30，基于 47 篇 batch9：脓毒症/ARDS 基础-转化·生物标志物·心脏骤停脂质组学·GBD 负担 + 医学 AI 基础模型·LLM 临床决策·泛化性方法学）

本次 v1.14 精读并移入 2026-08-30 文件夹的 47 篇，使知识库标杆从 159+ 扩至 **206+ 篇**：

- **新增 §19.16 脓毒症/ARDS 基础-转化·生物标志物·心脏骤停脂质组学·GBD 负担子域（30 篇 batch9 标杆）**：将 §19 危重症集群从「以 RCT 为主」扩至「机制—生物标志物—观察—RCT—负担」全证据链。覆盖脓毒症免疫/微生物（PCT 血管屏障、CD4⁺ T 耗竭、NET Assay、IL-40/NETosis、Copine 5、BMAL1/ER-phagy）、ARDS 表型与机制（GWAS SELPLG、白细胞表达异质性、FGF21 VILI、巨噬细胞极化）、血管内皮/血栓炎症（创伤内皮病、Tie2 抑制、PCT-CGRP 受体）、心脏骤停脂质组学（脑心磷脂、LPC 补充）、GBD 2023 高 LDL-C 负担。核心范式：双对照因果剥离、给药时机即论证、阴性三重限定标题、措辞-证据强度匹配、推导/验证双队列生物标志物、定义/指南必引（Sepsis-3/SIRS/SOFA/Berlin ARDS/STROBE/ARRIVE）。
- **新增 §19.17 医学 AI 基础模型·LLM 临床决策·泛化性方法学子域（17 篇 batch9 标杆）**：将 AI 证据形态升级到基础模型/LLM/泛化性方法学三层，并补非 ICU 临床 RCT（IDEAL/TREND）。覆盖 CHIEF 病理基础模型（Nature 2024）、全开放胸片 FM、术中超快 CNS 分类、通用医学 AI FM、急诊 LLM 决策支持（DECIDE-AI stage 1）、AI 引导肝恶性肿瘤（CONSORT-AI）、AI 视网膜病 RCT、Illusory generalizability / Hidden stratification 方法学里程碑、Dermatologist/Deep Patient 经典标杆。核心范式：框架声明先行（IDEAL/DECIDE-AI/TREND/CONSORT-AI）、边界声明句（"do not justify clinical deployment"）、基础模型三件套必引、extends 三种规范用法、隐藏分层/泛化性必写局限、阴性平衡优先自我局限披露。
- **引用实践（§20/硬性规则17）补强**：定义/指南单篇必引且现在时；AI 算法组件单篇溯源为硬要求；"续集"式引用逻辑（RAFT）；隐性泛化性审计成为 AI 论文讨论必写项。

> 注：本次 47 篇移入通过 `move_knowledge` 接口返回 code 0（success），但平台 `get_knowledge_list` 的子文件夹内容查询与 `parent_folder_id` 回填当前存在最终一致性延迟/空操作现象，无法用列表接口二次核验；请在知识库 UI 目视确认 2026-08-30 文件夹内容。已全部逐篇精读并产出 47 份笔记。

## v1.13 更新摘要（2026-08-23，基于 22 篇 batch8：数字病理/眼底表型/影像筛查/EHR时序+强化学习/临床共识定义）

本次 v1.13 在 §19.14 基础上进一步扩充 AI/DL 证据形态，精读并移入 2026-08-22 文件夹的 22 篇，使知识库标杆从 137+ 扩至 **159+ 篇**：

- **新增 §19.15 AI/DL 扩展子域（22 篇 batch8 标杆）**：6 类新证据形态——
  - **19.15.2 数字病理 AI**：WSI→patch+MIL→迁移学习→heatmap 可解释性；TOAD（CUP 起源 acc 83.6%/AUC 0.988）、NSCLC（κ 0.82 vs 病理医师 0.67）、CRC 生存（stroma score OS HR 1.99，P=0.0028）、P-NET（Reactome 通路驱动 AUC 0.93）。
  - **19.15.3 眼底/视网膜表型与遗传**：视网膜作全身窗口（MACE AUC 0.70 vs SCORE 0.72）+ 分割→GWAS/PheWAS/MR 因果（13 loci）。
  - **19.15.4 影像筛查**：LDCT 三维端到端（AUC 94.4%，91.1–97.3）、体液标志物 ML（原醛 AUC 0.948–0.954 vs ARR 0.839）、照片+区块链多地区验证（AUC 0.975）。
  - **19.15.5 EHR/临床时序 DL + 强化学习**：FHIR 表示+RNN/LSTM/Transformer（AKI 连续预测灵敏度 55.8%/AUC 92.1%、TransformEHR 外部 +2.3%）、超级学习器（KDpredict IPA 18.1% vs KFRE 27.8%）、AI Clinician 脓毒症 RL（策略值 84.5 vs 临床 56.9，反事实局限）。
  - **19.15.6 临床共识定义论文写法**（Sepsis-3：SOFA 0.74 vs SIRS 0.64，P<0.001，须作 §19 脓毒症 RCT 必引定义源）+ Frugal AI（资源受限场景卫生服务视角）。
  - **19.15.7 引用实践强化**：STARD/TRIPOD/TRIPOD-AI 必引、MIL/Transformer/FHIR 方法溯源、外部验证源论文必引、临床定义必引且用现在时、阴性平衡、时态匹配。
- **与既有引用规则衔接**：§19.15 的引用范式严格满足硬性规则16（阴性克制/反事实局限）与硬性规则17（背景锚定/指南必引/对比同期/阴性不隐瞒/忠实原文/时态/克制自引），并复用 §20 的 12 功能/10 映射/时态框架，无新增全局硬性规则以避免重复。
- **遗留说明**：batch8_08（Deep Patient）在移入 2026-08-22 时持续返回后端错误码 220001（与历史 8 篇卡住文献同类瞬时锁定），经多次重试无效，笔记已生成、文献仍留根目录，需用户手动移入或待后端恢复后由主智能体重试。

---

## v1.12 更新摘要（2026-08-22，基于 23 篇 batch7：15 篇 AI/DL + 8 篇 ICU 临床 RCT/队列）

本次 v1.12 在 §19 危重症集群下补入两类此前未系统覆盖的证据形态，精读并移入 2026-08-22 文件夹的 23 篇，使知识库标杆从 114+ 扩至 **137+ 篇**：

- **新增 §19.13 ICU 临床 RCT/队列扩展子域（8 篇临床标杆）**：5 类新证据形态——
  - **19.13.2 RRT 时机「四联」对比范式**：ELAIN（单中心阳性 HR 0.66）/AKIKI/STARRT-AKI（多中心阴性 RR 1.00）/AKIKI 2（延迟策略间无差异、过晚潜在危害 HR 1.65）的异质性解释写法（中心效应+严重度+watchful waiting 安全网），与 §19.12 AKIKI 共构完整证据谱系。
  - **19.13.3 ICU 营养 RCT**（NUTRIREA-2 早期 PN vs EN、TARGET 能量密度）、**19.13.4 ECMO 国际注册队列**（真实世界观察性写法）、**19.13.5 阶梯式楔形集群 RCT**（ERIC：as-implemented 混合效应+secular trend 调整、过程指标与患者结局分层）、**19.13.6 ESBL 血流感染抗菌 RCT**（MERINO：非劣失效转优效有害克制表述）。
  - **19.13.7 引用实践强化**：四联互为「对比同期」必引、KDIGO/ASPEN/ESCMID/IDSA 指南必引、阴性平衡。
- **新增 §19.14 AI/深度学习算法研发·验证·临床实施子域（15 篇 AI 标杆）**：区别于 v1.5「AI 诊断 RCT」的独立类型——
  - **19.14.2 数据集论文写法**（MIMIC-CXR/MIMIC-III：Data Records+Technical Validation+去标识，不报 AUC）、**19.14.3 DL 诊断研发-验证通用骨架**（回顾性训练+≥1 外部验证、专家多数决金标准、operating point、AUC/C-index 带 95%CI、STARD/TRIPOD 必引、真实数字范式）、**19.14.4 视频/远程表型 AI**（EchoNet-Dynamic/DASSI/心电猝死新标志物）、**19.14.5 AI 临床实施与真实世界验证**（结直肠癌三队列部署+成本、卫星健康地理多水平模型）。
  - **19.14.6 引用实践强化（显式对标 §20）**：STARD/STARD-AI/TRIPOD 报告规范必引、外部验证队列源论文必引、阴性平衡、时态匹配。
- **与既有引用规则衔接**：§19.13/§19.14 的引用范式严格满足硬性规则16（阴性克制/事后透明/监测提示）与硬性规则17（背景锚定/指南必引/对比同期/阴性不隐瞒/忠实原文/时态/克制自引），并复用 §20 的 12 功能/10 映射/时态框架，无新增全局硬性规则以避免重复。

## v1.11 更新摘要（2026-08-20，基于 6 篇 batch6 ICU 支持治疗/器官支持 RCT）

本次 v1.11 在 §19 危重症/ICU RCT 集群基础上补入「**ICU 支持治疗 / 器官支持 RCT**」子域，精读并移入 2026-08-18 文件夹的 6 篇 NEJM Original RCT（AID-ICU 谵妄氟哌啶醇 / PREVENT 间歇气压血栓预防 / AKIKI 肾脏替代时机 / SPICE III 早期右美镇静 / MENDS2 右美vs丙泊酚脓毒症镇静 / TEAM 早期活动），使 §19 标杆从 29 篇扩至 **35 篇**、危重症集群覆盖从「治疗性/复苏/创伤/ARDS/心脏骤停/休克」扩展至「器官支持与舒适化治疗」维度：

- **新增 §19.12 ICU 支持治疗/器官支持 RCT 子域标准**，4 大可操作范式：
  - **19.12.2 主要终点选择谱系**：6 类干预的主要终点（90 天院外存活天数 / 每周盲态超声新发近端 DVT / 60 天总生存 / 90 天全因死亡 / 14 天无谵妄-昏迷存活天数 / 180 天存活且离家天数）与关键次要，写入「ICU 支持治疗 RCT 终点模板」。
  - **19.12.3 克制阴性表述范式**：逐字可模仿的 5 类句式（did not result in a significantly greater number of days / did not differ / did not result in lower 90-day mortality / 「should not be interpreted as suggesting … safe for all patients」监测提示 / strongly reinforce current guidelines 强化而非否定指南）。
  - **19.12.4 设计可信度写法**：开放标签须列局限 + DSMB 盲态期中 + 盲态中心判定补偿；非盲干预显式报告暴露/沾染率；把握度不足以敏感性分析兜底；多重性免责句标配；延迟策略正向次要收益客观呈现；事后分层标注混杂。
  - **19.12.5 引用实践强化（显式对标 v1.10 §20）**：引言超高引用密度（AKIKI 40 条）、指南/标准必引（KDIGO/PADIS/SCCM）、阴性平衡（TEAM「at variance with a meta-analysis」+ 同期 RCT 对比）、方法借用量表与定义、报道时态匹配——使 §20 抽象规则在 ICU RCT 上有具体实证。
- **与既有引用规则衔接**：本子域的写作范式严格满足硬性规则16（阴性主终点克制、事后分析透明、监测提示）与硬性规则17（背景近 5 年锚定、指南必引、对比同期显式引用、阴性不隐瞒、引用忠实原文、时态匹配、优先原始克制自引），无新增全局硬性规则，避免与 §20/规则16/17 重复。

## v1.10 更新摘要（2026-08-19，基于 95 篇全库论文的引用实践分析）

本次 v1.10 **转变分析维度**：不再只看"写什么"，而是系统拆解顶刊论文**"引什么、怎么引、引用句如何对应原文证据"**。基于知识库全部 95 篇论文逐篇分析，新增跨类型通用模块：

- **§20 参考文献选取与引用证据总结范式（新增，跨类型）**：① 12 类引用功能分类（背景/方法/统计/对比一致/对比相反/情境化/指南/机制/阴性平衡/定义/趋势/背靠背）；② 引用句↔原文证据的 10 类映射关系（直接复述结论/转述讨论观点/借用方法学/引具体数字/概括趋势/作为基准/引局限/引定义/引机制/引阴性矛盾）——核心回答用户问题"标记了参考文献的语句与原文相比，是直接抄结论、还是参考讨论观点或方法"；③ 报道动词与时态范式（背景现/结果过/推测 suggest/方法过去被动/指南现）；④ 参考文献选取逻辑（必引指南、必引背靠背、优先原始研究、方法溯源、阴性平衡、克制自引）；⑤ 跨 7 类论文的引用差异矩阵；⑥ 8 条写作检查清单；⑦ 真实标杆范例句库（含 PURPOSE-1/TTM-2/HYPERION/REMAP-CAP/EOLIA/ART 原句）。
- **硬性规则17（8 条引用实践规则）**：背景句须近 5 年证据锚定、指南标准必引、方法须引源头、对比同期结果须显式引用、阴性证据不得隐瞒、引用须忠实原文、动词时态匹配功能、优先原始研究克制自引。
- **JOURNAL_FINGERPRINTS.md 新增 VIII 集群指纹**：跨类型引用实践指纹（功能分布、动词时态、选取逻辑、对比引用方式）。

## v1.9 更新摘要（2026-08-19，基于 21 篇 batch5 急危重症/复苏/创伤/ARDS/心脏骤停 RCT）

本次 v1.9 基于 **21 篇 batch5 精读笔记**将 §19 危重症/ICU RCT 集群从「8 篇泛 ICU RCT」扩为「**一核心范式 + 7 大治疗域 29 篇标杆**」，补全了此前 skill 在**急救复苏、创伤失血、ARDS 机械通气策略、心脏骤停、ECPR、心源性休克、血管活性药、气道管理**维度的空白：

- **§19.11 七域子类推标（新增）**：① 心脏骤停与复苏 RCT——主要终点统一为「存活且神经功能良好（CPC/mRS/GOSE）」，ROSC 仅作流程终点；② ARDS 策略 RCT——ECMO（挽救性交叉设计）、早期 NMB、糖皮质激素（ventilator-free days）、肺复张+滴定 PEEP（气压伤安全终点）；③ 创伤/失血性休克复苏 RCT——REBOA、TXA 时间窗（<3h）、院前/转运 TXA、院前血浆/血浆优先、中高危 PE 导管溶栓；④ 心源性休克 RCT——微轴流泵 Impella（post hoc 透明标注）、PCI 策略（仅罪犯 vs 多支）；⑤ 血管活性药——血管紧张素II（血压反应阳性/死亡阴性）；⑥ 诊断准确性——Sepsis-3 急诊预后（AUROC+敏感度特异度）；⑦ 气道管理——插管围操作低氧预防（操作性安全终点）。
- **v1.9 新增 7 条标杆规则（写入硬性规则16）**：A 硬终点–替代终点分离（epinephrine/angiotensin II）；B 挽救性交叉设计非劣效保守解读（EOLIA）；C TXA 时间窗分层交互（CRASH-3）；D 事后分析透明标注（DanGer Shock）；E 心脏骤停主要终点=神经功能良好生存；F ARDS 糖皮质激素主要终点=ventilator-free days；G 体温管理 33°C→常温/36°C 范式演变（可电击 vs 非可电击分述）。
- **标杆范文库扩至 29 篇**：§19.9（8 篇）+ §19.11.9（21 篇）均标注真实期刊/卷期/DOI，含 PARAMEDIC2、TTM-2、HYPERION、EOLIA、CRASH-3、PAMPer、COMBAT、CANARY、UK-REBOA、CULPRIT-SHOCK、ATHOS-3、PreVent、Sepsis-3 等公认顶刊原文。

---

## v1.8 更新摘要（2026-08-18，基于 8 篇 batch4 危重症 RCT）

本次 v1.8 基于 **8 篇 batch4 精读笔记**新增 **危重症/ICU RCT 集群标准**（§19），补全了此前 skill 在「治疗性危重症 RCT」维度的空白：

- **新增集群类型 · 危重症/ICU RCT（Critical Care RCT）**（§19）：统一 8 篇顶刊（REMAP-CAP/JAMA 2020、CLASSIC/NEJM 2022、ANDROMEDA-SHOCK/JAMA 2019、Therapeutic anticoagulation Covid-19/NEJM 2021、PLUS/NEJM 2022、SMART/NEJM 2018、ADRENAL/NEJM 2018、APROCCHSS/NEJM 2018）的写作范式，覆盖：ICU 硬终点（90天全因死亡 / organ support-free days 序数终点 death=−1 / MAKE30 复合终点）、6 类设计标签（贝叶斯自适应平台 / 多平台协同 / 务实集群交叉 / 开放标签盲态终点 / 双盲安慰剂 / 国际多中心务实）、频率学派 vs 贝叶斯两套数字报告分野（OR/RR/HR+95%CI+P vs POR+95%CrI+后验概率）。
- **同期背靠背试验对比规则**：ADRENAL↔APROCCHSS（单药 vs 联合盐皮质激素）、SMART↔SALT-ED/SPLIT、REMAP-CAP↔RECOVERY、CLASSIC↔液体策略 meta、PLUS↔BaSICS/SMART 列为必引同族。
- **提前停止克制表述**：因外部试验公布（equipoise lost）或无效界值（futility boundary）提前停止时，结论须标注 "stopped early, precluding definitive conclusions"。
- **统计写法补强**：marginal/conditional OR（cluster-RCT）、Fine–Gray 竞争风险、G-computation/van Elteren（天数类结局）、Bayesian cumulative logistic（MCMC）。

---

## v1.7 更新摘要（2026-08-18）

本次 v1.7 基于 **16 篇 batch3 精读笔记**对 `workflows/workflow_article_type_standards.md` 做类型级扩充，并新增 1 条硬性规则：

### 新增 / 扩充的论文类型与子类（v1.6 的 15 种 → v1.7 的 17-18 种细分）
- **新增独立类型 · 传染病预防 RCT（长效 PrEP / 疫苗）**（以 lenacapavir PURPOSE 1, NEJM 2024 为标杆，见新 §16）：规范 **0 感染如何报告**、**IRR（发病率比）而非 HR/OR**、`95% CI 上界`、背景发病率对照设计、随访人年（per 100 person-years）、非劣效/优效、安全性 AE。
- **新增独立类型 · 食品/环境健康/公共卫生 SRMA**（以 mycotoxin tea, Mycotoxin Research 2026 为标杆，见新 §17）：规范 **观察性患病率（比例）meta**、MASTARI/JBI 偏倚工具、Egger/漏斗图发表偏倚、污染物量化（ng/g、检出率）、GRADE 常不应用。
- **新增简短章节 · 非医学/教育政策/工程文献的语言可迁移性**（admissions / resonance，见新 §18）：标注哪些句式可迁移到医学论文的政策建议段/方法段，哪些不适用（选择性可迁移）。
- **高血压 add-on/adjunctive RCT 子类**（KARDIA-2, JAMA 2025）补充进「NEJM/JAMA Cardiovascular RCT」（§11）：开放标签 run-in + 各队列内 1:1 双盲、add-on 多队列 RCT 写法，与 KARDIA-1 单药对照形成系列，列为必引文献。
- **Nature/Cell Basic Science（§15）扩充**：标杆范文库新增 **ecDNA、APOBEC3 泛素化降解、人 PSC 类胚体、T2T 完整基因组、肿瘤浸润 T/B 单细胞图谱、母婴哭声催产素神经环路、Omicron 病毒进化** 7 篇；新增两个子类型说明——「人群尺度多队列组学」（microbiome 36 研究）与「进化基因组/生态基因组」（baobab、Omicron）。

### 新增硬性规则
- **硬性规则15 · 同族 update 文献处理规则**（corticosteroids COVID 案例）：CD 号相同、`.pub` 后缀递进、检索日期/样本量增量 → 识别为「同族 update 递进」，作 **配对教学样本，不重复录入**；真正重复（DOI 完全相同）必须显式标注。

### 期刊指纹（references/JOURNAL_FINGERPRINTS.md）
- 新增 **NEJM 2024 预防 RCT（lenacapavir）** 与 **JAMA 2025 add-on RCT（KARDIA-2）** 指纹；Mycotoxin Research 因非四大顶刊，于文件末尾「其他期刊指纹」小节补充，不在主体指纹章节。

---

## v1.6 更新摘要（2026-08-11）

本次 v1.6 在 v1.5 之上完成"研究类型→论文类型"精细化升级：

### 新增 1 份工作流文档 `workflows/workflow_article_type_standards.md`
覆盖 **15 种论文类型**（v1.5 是 11 种），每种类型包含 **10 个固定维度**：
1. 标题规范（长度/结构/关键词/禁忌）
2. 摘要规范（字数/段结构/必含数字/禁忌词）
3. 引言规范（字数/段数/句式/必引文献）
4. 方法规范（必含子节/随机化/盲法/样本量估算/统计）
5. 结果规范（必含子节/数字呈现/图表/禁忌句）
6. 讨论规范（必含 5 个层次/字数/必引 RCT 数/段数）
7. 图表规范（数量/必含类型/Caption/颜色）
8. 引用规范（数量/自引率/近 5 年占比/必引 RCT）
9. 标杆范文（3-5 篇真实顶刊论文）
10. 与其他类型差异 + 决策树

### 15 种论文类型全维度覆盖
- **临床 RCT 系**：NEJM Original RCT / Lancet Original RCT / JAMA Original RCT
- **心血管 RCT**（新增）：NEJM/JAMA Cardiovascular RCT（FINEARTS-HF / DELIVER / ANNEXA-I 范式）
- **肿瘤 RCT**：NEJM/JAMA Oncology RCT（IMbrave050 / IMvigor011 范式）
- **实用临床试验**（新增）：BMJ/Annals Pragmatic Trial（target trial emulation / registry-based RCT 范式）
- **AI 诊断**：NEJM/JAMA AI Diagnostic RCT（PI-CAI / MASAI / LVO 范式）
- **综述类**：NEJM Review / Lancet Review / Lancet Commission / JAMA Review
- **综合证据**：BMJ NMA / Cochrane Living SR
- **基础研究**：Nature/Science Foundation Model / Nature/Cell Basic Science

### v1.5 → v1.6 关键强化
- 从"招牌句式清单"升级为"字数阈值 + 子节结构 + 必引 RCT + 决策树"的**可投稿对标规范**；
- 新增 BMJ/Annals Pragmatic Trial / NEJM Review / Lancet Review / JAMA Review / Cardiovascular RCT **5 个 v1.5 未覆盖类型**；
- 每种类型提供 3-10 条原句标杆和 3-8 篇真实顶刊范文；
- 每种类型附带决策树（用于"我应该用 NEJM 还是 Lancet 投"）。

---

## v1.5 更新摘要（2026-08-11）

本次 v1.5 完成 92+ 篇顶刊论文精读的横向整合：

### 新增 46 篇 batch2 论文笔记（覆盖 11 种主要研究类型）：
- **顶级心血管 RCT**：ANNEXA-I、STRIDE (Lancet)、ADVOR、KARDIA-1、FINEARTS-HF、VESALIUS-CV ×2、DELIVER、INTERACT4
- **神经/卒中/康复**：MR CLEAN-LATE、TRACE-III (Tenecteplase)、TREWS (AI sepsis EWS)、LVO detection RCT、AI-POCUS cardiomyopathy
- **肿瘤 RCT**：IMbrave050、IMvigor011 (ctDNA-guided MRD)、MASAI (AI breast screening)
- **Meta分析与系统综述**：7 种饮食 NMA、Statin CKD、Omega-3、Ambulatory BP、Salt substitute、GLP-1、Gut microbiome、Exercise depression NMA、Vitamin D (Cochrane Living SR)、Corticosteroids (Cochrane Living SR)
- **Lancet Commission/综述**：TBI Commission (Lancet Neurology, 36页报告体例)
- **行为 RCT**：Springboard Beyond Cancer (Self-efficacy)
- **AI 诊断/影像**：PI-CAI、AI-POCUS cardiomyopathy、Multi-cancer OncoSeek MCED、MASAI、LVO detection、TREWS sepsis AI
- **AI/计算基础研究**：scGPT、ProteinMPNN、RoseTTAFold、Geneformer、Evo、Pangenome、AlphaMissense、p-tau217、Claustrum、BEC、ECPR Bayesian MA、AlphaFold3 + FinnGen GWAS

### 新增 1 份工作流文档 `workflows/workflow_study_types.md`
覆盖 11 种主要研究类型的差异化写作：NEJM RCT / Lancet RCT / JAMA RCT / BMJ NMA / Cochrane Living SR / Lancet Commission / AI Diagnostic RCT / 肿瘤 RCT / ctDNA-guided MRD RCT / 行为护理 RCT / 基础研究。

### 数据库大规模扩容：
- SENTENCE_LIBRARY.md 新增 204 条新句式（来自48篇笔记，分8类）
- VOCABULARY_DICTIONARY.md 新增 182 个新词条
- JOURNAL_FINGERPRINTS.md 新增 5 种期刊/研究类型指纹
- DENSITY_METRICS.md 新增 5 类密度特征
- FIGURE_TABLE_LANGUAGE.md 新增 24 条新 figure caption 原文

### v1.5 新增硬性规则 5 条（详见下文硬性规则14）

---

## v1.5 新增的 10 个新发现（来自 48 篇笔记的提炼）

1. **"apparently driven by" 分层归因句式**已成为 NEJM 复杂 RCT 的标志性 Discussion 模式（FINEARTS-HF、ANNEXA-I）。当复合主终点阳性但组成成分不一致时，必须用此句式单独归因到具体成分。
2. **"may not be replicated in the real world"** 是 NEJM 试验设计外推警告的标杆句式（EARLY TAVR）。当试验有高强度随访或 centre 效应时，必须诚实说明试验结果可能不在现实场景重现。
3. **"exploratory on the basis of the testing hierarchy"** 作为 hierarchical testing moratorium 的标杆句式（VESALIUS-CV）。当 mortality 跨层级生效时，必须明示 death reduction 是 exploratory 而非可推断的。
4. **JAMA 的 Question + Findings Key Points box + 7 段结构化 abstract** 是 NEJM/Lancet 都不强制的，JAMA 强制要求 ≤2 条 Key Points + 7 段（IMPORTANCE/OBJECTIVE/DESIGN, SETTING, AND PARTICIPANTS/INTERVENTIONS/MAIN OUTCOMES AND MEASURES/RESULTS/CONCLUSIONS AND RELEVANCE）。
5. **BMJ NMA 8 段摘要的 8 个粗体小标题**（OBJECTIVE/DESIGN/DATA SOURCES/STUDY SELECTION/OUTCOMES/REVIEW METHODS/RESULTS/CONCLUSIONS）是 NMA 的范式黄金标准。
6. **Lancet Commission 的 "Progress since 2017 + Persistent challenges" 双壁叙事**（Tables 3 & 4）是 Commission 类报告的品牌手法，必须成对呈现。
7. **Cochrane Living SR 的 7 段结构 + Plain Language Summary + Equity subgroup + Comparison numbers transparent citation** 是其特有模式，无法用 JAMA/PRISMA 替代。
8. **AI 诊断论文的 "view-agnostic > view-specific"** 是 AI-POCUS 的品牌发现（δ 0.05 + AUROC 0.994），挑战 "必须先做 view classification" 的旧范式。
9. **ctDNA-guided MRD RCT（IMvigor011）选择性治疗 ctDNA-positive 患者**使 OS improvement "statistically significant despite the relatively short follow-up and modest sample size"——这是 MRD-driven 设计的核心论证。
10. **MASAI 的 "29% increase in cancer detection + 44.2% workload reduction + similar false-positive rate" 三联数字驱动总结**是 AI screening RCT 的成功范式（vs MASAI 早期 interim 的 20% increase 是学习曲线解释）。

---

## 硬性规则14：v1.5 新增规则（来自 48 篇笔记）

### 14.1 Commission 类综述的 diachronic 时间锚是强制项
- Commission / 综述类写作必须 anchor to 既往 publisher or policy timepoint
- 如 [TBI Commission] 必须有 "since 2017" 或 "WHA73.10"
- 不写 "since then, [进展]" 则不可称为 Commission

### 14.2 Meta 分析的 GRADE per outcome certainty 是强制项
- 每个 outcome 都必须有 GRADE 评级（High/Moderate/Low/Very Low）+ downgrade 理由
- 不写 GRADE per outcome = 该 NMA 不完整

### 14.3 AI 诊断论文的 STARD-AI / CONSORT-AI reporting checklist 是强制项
- 必须按 STARD-AI 或 CONSORT-AI 报告 AI 模型架构、训练数据、external validation、calibration
- 不按 checklist 报告的 AI 论文可能直接被 desk-reject

### 14.4 ctDNA-guided RCT 需 disclosure 跨 assay comparability
- 不同地区用不同 ctDNA 试剂（如 Signatera vs BGI）需主动 disclosure "highly similar in methodology and were considered comparably reliable"
- 不 disclosure 会被审稿人质疑跨 assay comparability

### 14.5 Tumor-informed vs tumor-naive assay 是 ctDNA 论文的核心
- 必须明示所用 assay 是 tumor-informed 还是 tumor-naive
- 漏此项 = 严重方法学缺失

---

## 硬性规则15：同族 update 文献处理规则（v1.7 新增，来自 16 篇 batch3 笔记）

### 15.1 识别「同族 update」而非「真正重复」
- 同一 Cochrane / 系统综述家族的 **base 版 与 update 版** 属于「同族 update」，不是「真正重复」。
- 识别三要素（须同时核对）：
  1. **CD 号 / 协议号相同**（如 `CD014963` 与 `CD014963.pub2` 同属一个 living review）；
  2. **`.pub` / 版本后缀递进**（base 无 `.pub` 或 `.pub1`，update 为 `.pub2`/`.pub3`…）；
  3. **检索日期更晚 + 样本量/研究数增量**（如 11 RCT/8075 人 → 16 RCT/9549 人，检索 2021-04-16 → 2022-01-06）。
- 同时满足以上三点即判定为「同族 update 递进」，应作 **配对教学样本**（展示证据随检索累积如何演化），**不视为重复录入**。

### 15.2 真正重复必须显式标注
- 若两篇 **DOI 完全相同** 或 **完全相同研究、相同版本、相同数据** 被再次录入，则属「真正重复」，必须显式标注「已收录/重复」，不可静默当作新文献。

### 15.3 corticosteroids COVID 标杆案例
- **Wagner 2021a（base 版）**：Cochrane Database of Systematic Reviews 2021, Issue 8, Art. No. CD014963（无 .pub2），11 RCT / 8075 参与者，检索至 2021-04-16，无 equity 亚组。DOI: 10.1002/14651858.CD014963。
- **Wagner et al. 2022（update 版）**：CD014963.pub2，Cochrane 2022, Issue 11，16 RCT / 9549 参与者，检索至 2022-01-06，新增年龄/性别/族裔/收入 equity 亚组（已学于 batch2）。
- 二者是 **同一 living review 家族的前后版本**，方法学骨架一致但证据量递进；skill 标注重复时应区分「同族 update」与「真正重复」。

### 15.4 应用
- 录入新文献时，先比对 CD/协议号与 `.pub` 后缀；命中同族则 **配对关联** 已学版本并标注版本关系，而非新建独立条目。

---

## 硬性规则16：v1.9 新增规则（来自 21 篇 batch5 急危重症 RCT 笔记）

### 16.1 硬终点–替代终点分离（标杆规则 A）
- 当替代终点（如 ROSC、血压反应、休克逆转）阳性但硬终点（神经功能良好生存、全因死亡）阴性/无差异时，**必须分两句表述**：一句报替代终点改善，一句报硬终点未改善，**禁止用替代终点改善推断硬终点获益**。
- 适用：心脏骤停（epinephrine 提高 ROSC 但未提高神经功能良好生存）、血管舒张性休克（angiotensin II 改善血压反应但未改善 28天死亡）。

### 16.2 挽救性交叉设计非劣效保守解读（标杆规则 B）
- 允许对照组挽救性交叉至试验干预（如 EOLIA 对照组可交叉至 ECMO）的设计，其非劣效/阴性结论须**明示交叉导致保守估计**，不得解读为常规治疗非劣于试验干预。

### 16.3 抗纤溶药时间窗分层交互（标杆规则 C）
- 氨甲环酸等抗纤溶药须报告给药时间窗（典型 <3h vs >3h）的分层交互；**禁止笼统称全人群有效**，须注明晚期给药可能无益甚至潜在危害（CRASH-3）。

### 16.4 事后分析透明标注（标杆规则 D）
- 原文为 post hoc / exploratory / secondary analysis 的，须**明示分析性质**、标注探索性与假设生成，**不得作为确证性证据**引用其结论（如 DanGer Shock microaxial pump 事后分析）。

### 16.5 心脏骤停 RCT 主要终点 = 神经功能良好生存
- 院外/院内心脏骤停 RCT 主要终点统一为「存活且神经功能良好」（CPC 1–2 / mRS 0–3 / GOSE）；ROSC、30天粗死亡仅为流程或次要终点，不得作为主结论依据。

### 16.6 ARDS 糖皮质激素 RCT 主要终点 = ventilator-free days
- COVID-19 / 中重度 ARDS 糖皮质激素试验主要终点为 **ventilator-free days（通气-free 存活天数，天数类）**，须用 G-computation / 序数模型处理删失；与 RECOVERY、REM-RCT 横向必引（CoDEX）。

### 16.7 体温管理范式演变与心律分层
- 心脏骤停后体温管理历史目标 33°C 已演进为 **常温 / 36°C**（TTM-2、HYPERION）；写作时须注明范式演变，**可电击 vs 非可电击心律分述**（非可电击预后更差、绝对获益更小，95%CI 跨 0 时须克制）。

---

## 硬性规则17：v1.10 新增 · 参考文献选取与引用证据总结规则（基于 95 篇全库论文引用实践分析）

### 17.1 背景/疾病负担句须有近年证据锚定
- 任何背景陈述（流行病学、患病率、死亡率、未满足需求）若含具体数字，必须挂 ≥1 篇近 5 年原始研究或权威数据库（GBD/GLOBOCAN）；**禁止无引用断言**（如 "Trauma is the leading cause of death among young people.¹" 须有 ¹ 支撑）。

### 17.2 指南/共识/标准必引权威来源
- 凡涉及诊断分类、靶值、入排标准、终点定义、报告规范，必引对应指南/共识/标准（AHA/ACC、ESC、SSC、PI-RADS、EASL、RECIST、CONSORT、PRISMA、STARD-AI），且用现在时（recommend / is recommended / follow）或过去被动（as recommended in）。

### 17.3 方法须引源头，保证可复现
- 统计方法、量表、算法、分析工具、队列/数据库必须引原创论文（三角检验、Beagle、Harmony、ClinVar、GISAID、UK Biobank），表述用 "as described in / based on / were performed according to"；不得仅说 "standard methods"。

### 17.4 对比同期结果必须显式引用
- 若本文发现与同期/前驱试验一致或相反，必须显式引用并标关系词（"Consistent with…" / "In contrast to…" / "Our results contrast with…"），不得含糊带过；关系词须准确反映方向。

### 17.5 阴性/矛盾证据不得选择性隐瞒
- 讨论局限、外推限制、机制未明时，须主动引相反或阴性文献以显证据张力（"did not show / failed / were disappointing"）；禁止只引支持性文献营造虚假一致。

### 17.6 引用须忠实原文，不得脱离夸大
- citing sentence 须与 cited source 的结论/数据/定义一致；**直接复述结论须数字一致；转述 Discussion 观点须标 suggest/indicate/may，不得把推测写成既定事实；引具体数字须与原文表/图一致**。

### 17.7 动词时态须匹配引用功能
- 背景/共识/定义用现在时或现在完成时（is/are/have shown）；特定研究发现用过去时（showed/reported/achieved）；推测用 suggest/indicate/may；方法借用用过去被动（was performed/were defined）。

### 17.8 优先原始研究、克制自引
- 支撑具体主张优先引原始 RCT/队列/方法论文而非综述；自引仅限方法基座、设计论文、前研（如自身 OncoSeek、设计论文），禁止以自引替代外部证据或夸大贡献；近 5 年证据优先，时效与权威并重。

---

## 一、Skill 核心资源

调用此skill时，请同时加载以下参考文件（按需读取，无需全部塞入上下文）：

| 文件 | 路径 | 内容 | 何时调用 |
|---|---|---|---|
| 期刊指纹档案 | `references/JOURNAL_FINGERPRINTS.md` | NEJM/Lancet/JAMA/Nature/Cell + 5 种 v1.5 新增指纹的独家风格 | 目标期刊确定后必须读 |
| 高频句式库（840+ 条） | `references/SENTENCE_LIBRARY.md` | 按章节×功能分类的句式模板（含 204 条 v1.5 新句式） | 撰写每个段落时检索 |
| 词汇精确度词典（870+ 词条） | `references/VOCABULARY_DICTIONARY.md` | 强弱动词阶梯、同义词替换、禁忌词（含 182 个 v1.5 新词条） | 词汇选择时检索 |
| 段落密度标尺 | `references/DENSITY_METRICS.md` | 句长、段长、被动语态比例的量化标准（含 5 类 v1.5 新增密度特征） | 写完一节后自检 |
| 图表语言范式 | `references/FIGURE_TABLE_LANGUAGE.md` | Figure/Table caption/footnote 模板（含 24 条 v1.5 新 caption 原文） | 图表描述时检索 |
| **写作专著蒸馏档案（v1.16新增）** | `references/WRITING_BOOK_DISTILLED.md` | Glasman-Deal《Science Research Writing》2nd ed + Stanford《Writing in the Sciences》课件蒸馏：IMRaD 各章节结构模型（引言四组件/方法六组件/结果四块/讨论九组件/结论11组件/摘要四类型/标题六规则）、确定度语言（Certainty Continuum + Modal Verbs 六类）、全量功能词表（引言四区域/方法九大词表等约千条模板）、全文自查清单、写作流程与伦理投稿 | 起草任一章节前查对应节核心模型，再到 `references/BOOK_DISTILL_UNITS/` 分卷取全量模板 |
| 按研究类型工作流（v1.5新增） | `workflows/workflow_study_types.md` | 11 种研究类型的差异化写作（NEJM/Lancet/JAMA RCT, BMJ NMA, Cochrane SR, Lancet Commission, AI Diagnostic, 肿瘤RCT, ctDNA MRD, 行为RCT, 基础研究） | 撰写前确定研究类型后必读 |
| 按论文类型写作标准（v1.6新增，v1.7扩充） | `workflows/workflow_article_type_standards.md` | 18 种细分论文类型的 10 维度差异化写作规范（v1.7 新增 §16 传染病预防RCT、§17 食品/环境健康SRMA、§18 非医学语言可迁移性，并扩充 §11 高血压add-on子类、§15 Nature/Cell基础新标杆） | 确定论文类型后必读 |
| **范文对标基准（v1.17新增）** | `references/EXEMPLAR_BENCHMARK.md` | 12 维对标量表（每维 0–3 锚点 + 全库实测覆盖率）、研究类型判定树、范文亮点识别 20 条检查点、11 类研究的结果呈现标准、9 类高频缺陷库、20 组报告句式模板、全库基准值速查表 | 拿到待润色稿件或范文后第一步必读 |
| **范文亮点卡库（v1.17新增）** | `references/EXEMPLAR_INDEX.md` + `references/EXEMPLAR_CARDS/` | 1141 篇研究型文献的逐篇卡片（研究设计/样本量/结果骨架/统计报告/图表分工/可复用原句/讨论结构/亮点/不足/对标维度），按 12 类分文件 | 需按类型调取标杆写法时，先查 INDEX 定位 ID，再读 CARDS 对应条目 |
| **范文对标润色工作流（v1.17新增）** | `workflows/workflow_exemplar_gap.md` | 五阶段流程：稿件解析→范文解析→12 维打分→差距清单（CRITICAL/MAJOR/MINOR）→改写与补数据清单，含交付前自查 | 用户交来稿件要求"按范文/高质量标准润色"时执行 |
| **卡片字段规范（v1.18新增）** | `references/CARD_FIELD_PROTOCOL.md` | 12 字段的写法标准、三态区分（已提取／原文未报告／不适用）、缺失字段补写流程、交付前校验清单 | 新增或重写任何卡片、或读到卡片中的缺失标记时必读 |
| **使用示例（v1.18新增）** | `examples/USAGE_EXAMPLES.md` | 六个典型场景的开口话术、对应流程与交付物形态（按范文改稿／语言润色／中译英／写讨论／投稿前自查／审稿回复） | 用户首次使用、或问"这能干什么/怎么用"时先读 |

---

## 1.5、绝对硬性规则（违反即不可挽回）

### 硬性规则1：参考文献默认JAMA格式

- **默认格式**：除非用户专门提供样板文章，否则所有参考文献**默认使用JAMA格式**
- **核查清单**：见 `checklists/reference_verification.md`
- **工作流**：见 `workflows/workflow_references.md`

### 硬性规则2：参考文献绝对不允许造假（最高优先级）

- 每篇参考文献必须真实存在
- 论文中引用的内容必须在原文中真实存在
- 绝不允许张冠李戴、绝不允许歪曲原意
- 严禁使用未发表的数据作为支撑
- 严禁把"动物实验"引用为"临床证据"
- 严禁把"观察性研究"引用为"因果证据"
- 严禁把"假设/推测"引用为"已证实"

### 硬性规则3：参考文献检索范围必须穷尽

- **默认知识库**：检索用户指定的16个知识库（特别是"高质量论文知识库"）
- **外部SCI数据库**：必须检索多个数据库
  - PubMed（首选英文文献库）
  - 中国知网（CNKI）
  - 万方数据
  - 维普资讯
  - 中华医学会期刊
  - Web of Science
  - Google Scholar
- **数量要求**：论著≥30-50篇 / 综述≥50-100篇 / 病例报告≥10-20篇
- **质量要求**：近5年≥60% + 经典文献20-30% + 自引率<10%
- **核心原则**：参考的文章足够多，写出来的东西才足够全面

### 硬性规则4：语言风格绝对不允许AI化（最高优先级）

- **绝对禁止使用**："This study aims to investigate..." / "It is important to note..." / "delve into" / "robust" / "comprehensive" / "multifaceted" / "could potentially" 等典型AI痕迹
- **核查清单**：见 `checklists/ai_style_checklist.md`
- **工作流**：见 `workflows/workflow_ai_style_check.md`
- **核心目标**：写出来的英文是"标准SCI风格"，不是AI风格
- **自动检测**：用Python脚本扫描高频AI词和句式
- **修复方法**：参考 `references/VOCABULARY_DICTIONARY.md` 做词汇替换

### 硬性规则5：交付格式默认可编辑.docx

- 用户未指定格式时，**默认返回 `.docx` 文件**（而非PDF或纯文本）
- 用户可二次编辑的Microsoft Word兼容格式
- 文档规范：
  - 页面A4
  - 页边距：上2.5cm / 下2.5cm / 左3.0cm / 右2.0cm
  - 中文字体：黑体（标题） / 宋体（正文）
  - 英文字体：Times New Roman（统一）
  - 行间距：1.5倍
  - 首行缩进：2字符
  - 参考文献编号：上标格式
  - 参考文献列表本身：普通字体（非上标）
- 生成工具：python-docx（已在 `md_to_docx.py` 中实现）
- 同时提供 `.md` 源文件作为对照

### 硬性规则6：综述写作专项规则（从审稿专家意见提炼）

**综述不同于原始研究，方法学必须严谨透明**：

#### 6.1 方法学必须包含8要素
- 综述目的陈述、PICO框架、检索策略（透明化）、文献筛选流程（PRISMA-style）
- 纳入/排除标准、证据等级评估、数据提取、内部档案的透明化披露
- 详见 `workflows/workflow_systematic_review.md`

#### 6.2 检索策略不能"挂名"
- 检索的每个数据库都明确列出（初检数/最终纳入数）
- 检索词分类标注：MeSH terms vs free-text terms
- 每个数据库的贡献具体说明
- 内部档案来源、入选标准、规模、贡献都要透明披露

#### 6.3 摘要Findings必须量化
- **禁止**"列举式"（"(1)(2)(3)"罗列）
- **必须**有具体数字（百分比、效应量、CI、P值）
- **必须**引用具体RCT（作者+年份）
- **必须**包含异质性分析
- 详见 `workflows/workflow_abstract_findings.md`

#### 6.4 综述必须有独立Discussion章节
- 不能把Discussion分散在各小节
- 必须包含：核心证据总结 + 证据局限性 + 异质性分析 + 跨研究分歧解释 + 临床适用性 + 未来研究方向 + 综述本身局限性
- 详见 `workflows/workflow_discussion_section.md`

#### 6.5 综述必含6类内容（防漏检）
- 流行病学 + 关键RCT + Meta分析 + 特殊人群
- **新型药物/新证据（近2-3年，绝不允许遗漏）**
- **成本效益与卫生经济学**
- **长期结局与PICS**

#### 6.6 引用语境核查（最高优先级）
- **DOI对、内容真实不够**——必须核查引用语境与原文是否一致
- 避免"主题错位"（如把脓毒症血管活性药物的AI研究引用到AI sedation）
- 避免"上下文错位"（如把长期认知结局文献放到AI sedation附近）
- 详见 `workflows/workflow_references.md` 核查项6

### 硬性规则7：去AI化（更严格）

#### 7.1 必须删除的过场话
- "This narrative review summarizes..."
- "However, the effect..."
- "In this paper, we present..."
- "must be interpreted with caution"（过度使用）
- "have shown promise"（过度使用）
- "increasingly studied"
- "operationalized through the ABCDEF bundle"

#### 7.2 综述写作禁忌词
- ❌ "novel" / "firstly" / "groundbreaking" / "breakthrough"
- ❌ "delve into" / "robust" / "comprehensive" / "multifaceted"
- ❌ "myriad" / "plethora" / "tapestry" / "navigate"
- ❌ "could potentially" / "might possibly"
- ❌ "This study aims to" / "It is important to note"
- ❌ "In conclusion" / "To sum up" / "In summary"

#### 7.3 综述写作推荐词
- ✅ "demonstrated" / "showed" / "revealed" / "established"
- ✅ "evidence supports" / "data suggest"
- ✅ "consistent with" / "in line with"
- ✅ "warrants further investigation" / "warrants evaluation"
- ✅ 主动语态 vs 被动语态合理切换

详见 `checklists/ai_style_checklist.md`

### 硬性规则8：避免"假量化"（Data Accuracy）

**这是审稿专家最严厉的批评**："pseudo-quantification是2024-2025 peer review中最危险的信号"。

#### 8.1 数字真实性原则
- 每个数字都必须能在原文中找到证据
- 找不到原文证据 = 数字必须删除
- **绝不虚构原文没有的具体数字**

#### 8.2 相对降低 vs 绝对降低必须区分
- RR 0.47 是相对降低53%，不是绝对降低53%
- 14-23% 绝对降低 ≠ RR 0.47-0.86 相对降低
- 两者不能对应同一组合并结果

#### 8.3 Primary vs Secondary Endpoint必须区分
- 每个effect estimate必须标注primary/secondary
- 阴性primary不能被阳性secondary掩盖
- SPICE III的primary是28天ventilator-free days，不是90天死亡

#### 8.4 Prespecified vs Post-hoc必须区分
- 每个subgroup analysis必须标注prespecified/post-hoc
- SPICE III的≥65岁亚组是post-hoc，不是prespecified
- 绝不能把post-hoc说成prespecified

#### 8.5 综述数字与参考文献必须100%对应
- "n=X trials"必须确实有X条trial reference
- 数字与引用数不能有gap

#### 8.6 Floating Fact禁止
- 每个数字必须有具体来源
- 不能写"0.5-2.5 days"这种没有source的数字

详见 `workflows/workflow_data_accuracy.md`

### 硬性规则9：narrative vs systematic必须二选一

**绝不允许同时声称"following systematic-review principles"**——这是学术诚信问题。

- 如果做真正的SR：必须有PROSPERO + PRISMA + RoB + GRADE
- 如果做narrative review：诚实承认局限，不声称SR
- **绝不允许走钢丝**（两边都声称）

详见 `workflows/workflow_systematic_review.md`

### 硬性规则10：PICO必须完整覆盖研究范围

- **关键**：PICO的Interventions必须包含所有研究范围内的interventions
- 如标题包含"Sedation AND Analgesia"，Interventions必须包含两类
- PICO必须与正文标题、Introduction一致
- 不能"title cover X but PICO missing X"

### 硬性规则11：修改稿必须附Response Letter

- 修改稿必须附Response Letter
- 每条审稿意见逐条回应
- 每条修改必须有具体位置（Page X, Line Y）
- 每条修改必须有修改后的文本
- 礼貌用词（即使不同意）

详见 `workflows/workflow_response_letter.md`

### 硬性规则12：占位符禁止（绝对红线）

**最终稿绝不允许出现**：
- ❌ [Author X] / [Author 1] / [Author 2]
- ❌ [Institution] / [City, Country]
- ❌ [Affiliation] / [Email] / [Telephone]
- ❌ [Name] / [Date] / [XXX] / [XX] / [X+]

**必须在最终稿前全部替换为真实信息**

### 硬性规则13：表格与Figure数据必须逐字核对

#### 13.1 表格转录
- 所有数据逐字核对原文
- GRADE grade准确（Strong/Conditional; High/Moderate/Low/Very Low）
- Recommendation方向准确（不能写反）
- 表格内容完整（不是只有标题）

#### 13.2 Figure时间线
- 时间顺序按真实年份排列
- 关键landmark trial无遗漏
- caption完整

#### 13.3 缩写展开
- PADIS全称是"...and Sleep disruption"（不能省略"disruption"）
- 缩写展开严格对应原文

#### 13.4 会议摘要不能作为核心引用
- 必须用peer-reviewed full paper
- 会议摘要可标注为"unpublished data"

---

## 二、Skill调用前的前置问答（必做）

在开始任何写作/润色任务前，**必须**向用户确认以下信息（直接询问，不要假设）：

### 必须询问的5个核心问题

```
1. 目标期刊是？（NEJM / Lancet / JAMA / Nature子刊 / Cell子刊 / 专业顶刊）
2. 研究类型是？（RCT / 观察性 / Meta分析 / 病例报告 / 基础研究 / 综述）
3. 写作目标是？（从零撰写 / 润色已有草稿 / 翻译中文初稿 / 修改审稿意见回复）
4. 论文当前阶段是？（仅有数据 / 有draft / 已投审稿中）
5. 是否需要保留特定作者风格？（如有参考文献提供，请明示）
```

### 选问的3个深度问题（视任务复杂度）

```
6. 目标受众是？影响IF还是专业认可度？
7. 时限和稿件长度要求？
8. 是否有Co-author对语言有特殊偏好（如 native speaker 的个人风格）？
```

---

## 三、Skill工作流（必读）

### Step 1：任务判定

判断任务属于以下哪一类：

| 任务类型 | 工作流入口 |
|---|---|
| 从零撰写新论文 | → workflow_new_paper.md（再分章节调 workflow_introduction / _methods / _results / _discussion） |
| 按研究类型或期刊类型对齐写作标准 | → workflow_study_types.md、workflow_article_type_standards.md |
| 润色已有草稿 | → workflow_polish_existing.md（只需通读体检用 workflow_ai_style_check.md） |
| 按范文水平改稿、问「我这篇差什么/能投什么档次」 | → workflow_exemplar_gap.md（配 references/EXEMPLAR_BENCHMARK.md） |
| 中文→英文学术翻译 | → workflow_translate_cn_to_en.md |
| 论著（Original Article）的 Discussion 章节 | → workflow_discussion.md |
| 综述（Review / SR / Meta）的 Discussion 章节 | → workflow_discussion_section.md |
| 摘要 / Title 优化 | → workflow_abstract_title.md、workflow_abstract_findings.md |
| 审稿意见回复信（成文，可直接附回邮件） | → workflow_response_letter.md |
| 审稿意见逐条应对（先定策略与措辞，再决定是否成文） | → workflow_response_to_reviewers.md |
| 参考文献选取、引用核对与格式化 | → workflow_references.md |
| 数据与原文核对（防张冠李戴） | → workflow_data_accuracy.md |
| 系统综述 / Meta 分析专项 | → workflow_systematic_review.md |
| Cover letter 撰写 | → workflow_cover_letter.md |

**两组易混入口的区分（勿调错）**

| 易混对 | 选择依据 |
|---|---|
| workflow_discussion.md ↔ workflow_discussion_section.md | 前者面向论著，按「复述发现→对比既往→机制→局限→结论」组织；后者面向综述，按 7 段结构组织，核心是跨研究证据汇总而非单研究结果解读。判据是稿件的论文类型，不是章节名 |
| workflow_response_letter.md ↔ workflow_response_to_reviewers.md | 前者产出完整 Response Letter 正文（逐条引用意见、给修改位置与页码）；后者先做策略判断（哪些接受、哪些据理力争、哪些补实验），产出回应要点与措辞选项。常规做法：先跑后者定策略，再跑前者成文 |

**完整工作流定义见**：`workflows/` 子目录下的对应文件。

---

### Step 2：必须遵守的"16条最大公约数"

无论何种任务，**任何输出都必须满足**以下16条核心规则（来自跨顶刊共性分析）：

| # | 规则 | 反例（绝对禁止） |
|---|---|---|
| 1 | 全文使用过去时描述本研究结果 | ~~showed, found~~ |
| 2 | 全文使用现在时描述普遍真理/文献 | ~~always showed~~ |
| 3 | 避免"novel / firstly / groundbreaking" | ~~a novel approach~~ |
| 4 | 避免"prove / demonstrate causation" | ~~we proved that X causes Y~~ |
| 5 | 避免"breakthrough / paradigm shift / game-changer" | ~~a breakthrough in...~~ |
| 6 | 避免"remarkable / dramatic / tremendous" | ~~dramatically reduced~~ |
| 7 | 避免"very / really / extremely"等口语强化词 | ~~very important~~ |
| 8 | 因果推断用"was associated with / was correlated with" | ~~X caused Y / X led to Y~~ |
| 9 | 不确定性用"remains unclear / has not been established" | ~~we don't know~~ |
| 10 | 临床转化用"holds promise / may inform / has the potential to" | ~~will definitely cure~~ |
| 11 | 名词化优先（protection→confers protection） | ~~X provides protection to Y~~ |
| 12 | 强弱动词区分（show→demonstrate→establish） | ~~we established show that...~~ |
| 13 | 段落平均3-5句；每段首句为主旨句 | ~~一整段流水账~~ |
| 14 | 长句>40词限制在每段≤2个 | ~~堆砌从句~~ |
| 15 | 被动语态在Methods中占50-70%，Results中30-50% | ~~全主动语态或全被动语态~~ |
| 16 | Discussion末段必须包含limitations+future directions | ~~只讲优点不讲局限~~ |

**完整规则清单与原文证据**：见 `references/JOURNAL_FINGERPRINTS.md` 第六部分。

---

### Step 3：分章节写作规范（节选）

每个章节都有详细的"模板-句式-禁忌"三件套。完整版见对应工作流文件。

#### 3.1 标题（Title）

- **首选**：陈述句式（Declarative） + 关键干预/暴露 + 关键人群 + 关键结局 + 研究设计
- **NEJM示例**："Empagliflozin in Heart Failure with a Preserved Ejection Fraction"
- **禁忌**：疑问句/感叹句/双关语/冒号标题（NEJM极少使用）
- **长度**：≤15个实词

#### 3.2 摘要（Abstract）

**根据目标期刊选择模板**：

| 期刊 | 模板 | 字数 |
|---|---|---|
| NEJM | 单段非结构式 + Background/Methods/Results/Conclusions加粗小标题 | ≤250词 |
| Lancet | 结构式 5段（Background/Methods/Findings/Interpretation/Funding） | ≤300词 |
| JAMA | 结构式 + Question前缀 | ≤350词 |
| Nature | 1段非结构式 | ≤150词 |
| Cell | 1段非结构式 | ≤150词 |

**完整模板与例句**：见 `workflows/workflow_abstract_title.md`。

#### 3.3 引言（Introduction）

**5种标准开篇**（按研究类型选择）：

1. **"流行病学+主导地位"开篇**："X affects Y million people worldwide and remains the leading cause of Z."
2. **"实践-证据落差"开篇**："X is increasingly used … despite a lack of evidence."
3. **"机制-缺口"开篇**："X has been shown to Y; however, the mechanism of Z remains unclear."
4. **"既往RCT争议"开篇**："Recent trials have yielded conflicting results regarding X."
5. **"现行标准-已知-未知-本研究"开篇**："Standard therapy is X. Although A is known, B is unknown. We therefore designed..."

**完整模板**：见 `workflows/workflow_introduction.md`。

#### 3.4 方法（Methods）

**标配5个Block**：

1. **Trial Design & Oversight**（研究设计/伦理/注册）
2. **Participants**（入排标准/数据来源/招募时间）
3. **Randomization & Interventions**（随机化方法/干预细节/盲法）
4. **Outcomes & Procedures**（主要/次要终点/评估方法）
5. **Statistical Analysis**（样本量估算/统计模型/亚组定义/敏感性分析）

**NEJM 招牌句式**：
- "Patients were randomly assigned in a 1:1 ratio to receive..."
- "The primary outcome was a composite of..."
- "Efficacy and safety analyses were performed in the modified intention-to-treat population..."

**完整模板**：见 `workflows/workflow_methods.md`。

#### 3.5 结果（Results）

**5个标配Block**：

1. **Patient Disposition & Baseline Characteristics**（CONSORT流程 + Table 1）
2. **Primary Outcome**（核心结果 + 95%CI + P值）
3. **Secondary Outcomes**（逐项报告）
4. **Subgroup Analyses**（Forest plot + 文字描述）
5. **Safety / Adverse Events**（Table 2/3）

**NEJM 招牌句式**：
- "A total of N patients underwent randomization … N included in the final analysis."
- "The primary outcome occurred in X% of the X group vs Y% of the Y group (hazard ratio, 0.XX; 95% CI, X.XX to X.XX; P=X.XX)."
- "Results for the primary outcome were consistent across prespecified subgroups."

**完整模板**：见 `workflows/workflow_results.md`。

#### 3.6 讨论（Discussion）

**5段式结构**：

1. **核心发现复述**（≤1段，含1-2句限制性表述）
2. **与既往研究对比**（含同类RCT对照）
3. **机制推测**（克制表述：appears to / may / is consistent with）
4. **Strengths & Limitations**（必须诚实承认）
5. **Clinical Implications & Future Directions**

**NEJM 招牌句式**：
- "The findings of our trial are consistent with those of previous studies showing..."
- "Several limitations of our trial should be acknowledged. First, ... Second, ... Third, ..."
- "Larger and longer trials are needed to establish the durability of these effects."

**完整模板**：见 `workflows/workflow_discussion.md`。

#### 3.7 参考文献（References）

- 优先近5年文献（≥60%）
- 自引率控制在<10%
- 经典文献（被引>1000）占20-30%
- JAMA/NEJM最新格式：Vancouver style + DOI

---

### Step 4：写作完成后的自检清单

输出前，**必须**对照 `checklists/pre_submission_checklist.md` 逐项检查。

**自检维度**：
1. ✅ 16条最大公约数全部满足
2. ✅ 目标期刊模板100%匹配
3. ✅ 词汇精确度：弱动词/强动词比例合理
4. ✅ 段落密度：句数/句长/被动语态符合标尺
5. ✅ 图表语言：Figure/Table caption规范
6. ✅ 禁忌词扫描：novel/prove/breakthrough等100%回避
7. ✅ 参考文献格式：Vancouver/AMA一致
8. ✅ 标题/摘要字数符合期刊要求

**完整清单**：见 `checklists/pre_submission_checklist.md`。

---

## 四、与具体任务的衔接

### 4.1 用户上传了草稿

→ 调用 `workflows/workflow_polish_existing.md`
→ 同时加载 `references/DENSITY_METRICS.md` 自检段落密度
→ 重点修改：禁忌词扫描 + 强弱动词校准 + 段首句强化

### 4.2 用户给了中文初稿

→ 调用 `workflows/workflow_translate_cn_to_en.md`
→ 先识别中文初稿的目标期刊（如果用户没说，再次询问）
→ 翻译时严格按目标期刊的摘要模板 + 句式库
→ 翻译后必须做禁忌词扫描（中文写作常有"新颖性"等表述需要规避）

### 4.3 用户给了原始数据但无初稿

→ 调用 `workflows/workflow_new_paper.md`
→ 先询问5个核心问题
→ 按章节顺序撰写，每章节都从模板开始填充

### 4.4 用户审稿意见回复

→ 调用 `workflows/workflow_response_to_reviewers.md`
→ 核心原则：**逐条回应 + 改后重述 + 文献支撑**
→ 必须避免辩解式语言（"we don't agree that..."），改为"thank you for raising this important point; we have now..."

### 4.5 用户给了一段文字需要润色

→ 不进入完整工作流
→ 直接调用 `references/VOCABULARY_DICTIONARY.md` 做词汇替换
→ 调用 `references/SENTENCE_LIBRARY.md` 做句式升级
→ 调用 `checklists/quick_polish_checklist.md` 做快速自检

---

## 五、与现有skills的协作关系

此skill**不替代**以下skills，而是与之协作：

- `paper-de-ai-fy`：本skill负责"写出顶刊风"，paper-de-ai-fy负责"去除AI痕迹"。两者形成"风格化+去AI化"组合。
- `nature-research-assistant`：当用户明确指定Nature/CNS风格时，由其主导。
- `chinese-medical-paper-writer`：当目标是中文核心期刊时，本skill不适用。

---

## 六、Skill使用约束（红线）

**绝对禁止**：
1. 给出脱离顶刊原文证据的"经验式建议"——每个建议都必须可追溯到具体论文笔记
2. 编造参考文献或DOI
3. 翻译时保留中文特有的句式（如"我们认为"、"综上所述"）
4. 在用户未确认目标期刊时，按默认偏好写作（必须询问）
5. 把"novel/breakthrough"作为褒义词使用（NEJM几乎从不使用）

**必须做到**：
1. 每个修改/润色建议都标注"标杆等级"：S级（必须严格模仿）/A级（参考）/B级（拓展视野）
2. 任何疑问必须主动提问，不要猜
3. 输出后必须做禁忌词扫描

---

## 七、Skill内部命令清单

当需要快速定位某个写作规范时，使用以下内部命令：

```
@FINGERPRINT_NEJM     → 加载NEJM指纹档案
@FINGERPRINT_LANCET   → 加载Lancet指纹档案
@FINGERPRINT_JAMA     → 加载JAMA指纹档案
@SENTENCE_LIBRARY     → 加载高频句式库（640+条）
@VOCAB_DICTIONARY     → 加载词汇精确度词典
@DENSITY              → 加载段落密度标尺
@FIGURE_LANG          → 加载图表语言范式
@POLISH_QUICK         → 快速润色检查清单
@SUBMIT_FULL          → 投稿前完整自检清单
```

---

## 八、Skill的"标杆等级"标注系统

在所有润色/修改建议前，加注以下标记：

- **[S级]**：必须严格模仿。违背将直接导致顶刊拒稿。
- **[A级]**：建议模仿。违背会降低稿件质量但不致命。
- **[B级]**：拓展视野。可选择性应用。

例如：
- **[S级]** 全文回避"novel"，改用"important / first"
- **[A级]** 摘要第一句使用"X affects Y million..."流行病学开场
- **[B级]** Discussion末段用三句排比收束

---

## 九、Skill局限性与诚实声明

本skill基于46篇顶刊论文精读（Phase 3 扩为 46 篇，详见 JOURNAL_FINGERPRINTS.md 附录），存在以下局限性：

1. **学科偏向**：46篇中约59%是NEJM临床试验（约27篇NEJM中包括心血管/慢病/重症/ECMO/vaccine 等多 sub-type），因此本skill对NEJM风格的提炼最为充分，对其他期刊/其他学科可能存在风格偏差。Lancet 主刊中新增的 R21/Matrix-M 现场 RCT 和 Lancet Countdown 政策综述报告扩充了 Lancet 部分的非 RCT 范式，但 Lancet Case Report / Correspondence / 子刊风格样本仍较少。
2. **公共卫生/政策报告覆盖**：新增 Lancet Countdown 2022 一篇后已涵盖"政策综述报告"范式，但 WHO/UN 系统的其他政策报告（如 World Malaria Report、Global Burden of Disease）样本仍缺失。
3. **非洲/低收入国家现场 RCT 覆盖**：新增 R21/Matrix-M 一篇后已涵盖"非洲现场 RCT 范式"，但 single-site 现场试验 / cluster RCT / stepped-wedge 设计等变体仍需扩展。
4. **Meta分析覆盖**：仅有 1 篇（Lancet RECOVERY Baricitinib 含Meta），对系统综述/PRISMA 流程、network meta-analysis、Cochrane-style systematic review 的覆盖有限。
5. **JAMA 部分样本仍较薄**：从 2 篇扩为 3 篇（新增 Prague OHCA），但 JAMA 在 Sepsis/ECMO/Cardiology 等 sub-specialty 的代表论文仍待扩展。
6. **图表设计本身**：skill仅涉及图表**文字**部分（caption / footnote / legend），不涉及图表的视觉设计（color scheme / layout / interactive visualization）。

如需补充特定学科/特定期刊的风格，建议用户上传更多对应标杆论文，按相同流程扩展skill。

---

## 十、Skill注册信息

- **Skill名称**：SCI-Writing-Master
- **版本**：v1.16（基于249+篇近五年顶刊论文 + 9份写作专著/课件蒸馏；v1.5 新增46篇batch2笔记 + workflow_study_types.md；v1.6 新增15种按类型标准 workflow_article_type_standards.md；v1.7 新增16篇batch3笔记、3类独立/子类标准 + 非医学语言可迁移性章节 + 硬性规则15；v1.8 新增8篇batch4危重症RCT笔记、§19 危重症/ICU RCT集群标准；v1.9 新增21篇batch5急危重症RCT、§19扩为7大治疗域29篇+硬性规则16；v1.10 全库95篇引用实践分析、新增§20引用范式+硬性规则17+VIII指纹；v1.11 新增6篇batch6 ICU支持治疗/器官支持RCT、§19.12子域标准；v1.12 新增23篇batch7（15篇AI/DL算法研发验证+8篇ICU临床RCT/队列）、§19.13 ICU临床扩展子域 + §19.14 AI/DL算法研发验证子域；v1.13 新增22篇batch8（数字病理/眼底表型/影像筛查/EHR时序+强化学习/临床共识定义）、§19.15 AI/DL扩展子域；v1.14 新增47篇batch9（脓毒症/ARDS基础-转化+生物标志物+心脏骤停脂质组学+GBD负担 + 医学AI基础模型/LLM临床决策/泛化性方法学）、§19.16 脓毒症ARDS基础-转化·生物标志物·心脏骤停·GBD负担子域 + §19.17 医学AI基础模型·LLM临床决策·泛化性方法学子域；v1.15 新增43篇batch10（医学AI/ML临床预测与诊断经典标杆）、§19.18 医学AI经典标杆子域（验证设计五级阶梯/人机同图证据链/互补式结论/指标四层报告/可解释性三级写法）；v1.16 蒸馏9份写作专著/课件（Glasman-Deal《Science Research Writing》2nd ed + Stanford《Writing in the Sciences》课件8单元）→ references/WRITING_BOOK_DISTILLED.md 主档案 + BOOK_DISTILL_UNITS/ 6份分卷（IMRaD章节级结构模型体系/确定度语言体系/全量功能词表约千条/句子级铁律与写作流程/伦理投稿）
- **建立时间**：2026-08-10；v1.1更新2026-08；v1.4更新2024-08；**v1.5更新2026-08-11**
- **作者**：基于用户提供的标杆论文 + AI系统性精读提炼
- **注册命令**：`ima_skill_create -d <skill_dir>`
- **目录结构**：
  ```
  skill_sci_writer/
  ├── SKILL.md                                   ← 本文件
  ├── workflows/                                 ← 任务工作流
  │   ├── workflow_new_paper.md
  │   ├── workflow_polish_existing.md
  │   ├── workflow_translate_cn_to_en.md
  │   ├── workflow_response_to_reviewers.md
  │   ├── workflow_abstract_title.md
  │   ├── workflow_cover_letter.md
  │   ├── workflow_introduction.md
  │   ├── workflow_methods.md
  │   ├── workflow_results.md
  │   ├── workflow_discussion.md
  │   ├── workflow_study_types.md                ← v1.5 新增！
  │   └── ... (其他v1.5前workflow)
  ├── checklists/                                ← 自检清单
  │   ├── pre_submission_checklist.md
  │   └── quick_polish_checklist.md
  ├── references/                                ← 参考资源（核心数据库）
  │   ├── JOURNAL_FINGERPRINTS.md                ← 46 篇 5 大期刊指纹档案（+v1.5新增5个指纹）
  │   ├── SENTENCE_LIBRARY.md                    ← 840+ 条 SCI 写作高频句式（+204 条 v1.5）
  │   ├── VOCABULARY_DICTIONARY.md               ← 870+ 词条精确度词典（+182 词条 v1.5）
  │   ├── DENSITY_METRICS.md                     ← 段落密度量化标尺（+5 类 v1.5）
  │   └── FIGURE_TABLE_LANGUAGE.md               ← 图表语言范式（+24 条 v1.5）
  └── examples/                                  ← 完整示例
      └── example_full_paper_NEJM_RCT.md
  ```

**v1.5 更新说明（2026-08-11）**：本skill由46篇扩为92+篇，新增46篇batch2笔记 + 1份workflow_study_types.md：

- **新增 11 种研究类型差异化工作流**：NEJM RCT / Lancet RCT / JAMA RCT / BMJ NMA / Cochrane Living SR / Lancet Commission / AI Diagnostic RCT / 肿瘤RCT / ctDNA-guided MRD RCT / 行为护理RCT / 基础研究
- **新增 5 种 v1.5 期刊/研究类型指纹**：Lancet Neurology Commission 风格 + Lancet Neurology Commission Section+Table+Panel三件套 + BMJ NMA 8段摘要 + Cochrane Living SR风格 + NEJM AI Diagnostic RCT风格
- **新增 5 条 v1.5 硬性规则**：
  - 14.1 Commission 类综述的 diachronic 时间锚强制
  - 14.2 Meta分析GRADE per outcome certainty强制
  - 14.3 AI诊断论文 STARD-AI/CONSORT-AI reporting checklist强制
  - 14.4 ctDNA-guided RCT 跨assay comparability disclosure
  - 14.5 Tumor-informed vs tumor-naive assay明示
- **新增204+句式、182+词条、24+Figure caption** —— 所有句式和词汇均附原文出处标注（如 [FINEARTS-HF]、[IMvigor011]、[TBI Commission]、[PI-CAI]、[OncoSeek] 等）
- **重点加强此前覆盖不足的5个方向**：
  - Lancet Commission（首次新增完整结构 + TBI Commission全套范式）
  - BMJ Network Meta-Analysis（首次新增8段摘要 + Dietary/Exercise depression完整范式）
  - AI诊断论文（首次新增完整结构 + PI-CAI/AI-POCUS/MASAI/OncoSeek/TREWS全套范式）
  - 肿瘤RCT ctDNA-guided MRD（首次新增IMvigor011专属范式 + IMbrave050 active surveillance对照）
  - 基础研究/计算生物学（首次新增 scGPT/Evo/RoseTTAFold/AlphaMissense/Pangenome/Claustrum等全套范式）
- **v1.7 更新说明（2026-08-18）**：基于 16 篇 batch3 精读笔记，将 workflow_article_type_standards.md 从 15 种扩为 18 种细分标准：
  - 新增 §16 NEJM/JAMA 传染病预防 RCT（lenacapavir PURPOSE 1, NEJM 2024）
  - 新增 §17 食品/环境健康/公共卫生 SRMA（mycotoxin tea, Mycotoxin Research 2026）
  - 新增 §18 非医学/教育政策/工程文献语言可迁移性（admissions / resonance）
  - §11 心血管 RCT 补充 高血压 add-on/adjunctive RCT 子类（KARDIA-2, JAMA 2025）
  - §15 Nature/Cell 基础科学 扩充 7 篇新标杆（ecDNA / APOBEC3 / 类胚体 / T2T / 单细胞T/B / 神经环路 / Omicron）+ 2 个子类型（人群尺度组学、进化生态基因组）
  - 新增 硬性规则15（同族 update 文献处理规则，corticosteroids COVID 案例）
  - JOURNAL_FINGERPRINTS.md 补充 NEJM 2024 预防 RCT、JAMA 2025 add-on RCT 指纹
  - **v1.8 更新说明（2026-08-18）**：基于 8 篇 batch4 危重症 RCT 精读笔记，将 workflow_article_type_standards.md 从 18 种扩为 19 种细分标准：
    - 新增 §19 危重症/ICU RCT 集群标准（8 篇标杆：REMAP-CAP / CLASSIC / ANDROMEDA-SHOCK / 治疗性抗凝 Covid-19 / PLUS / SMART / ADRENAL / APROCCHSS）
    - 集群统一「ICU 硬终点（90天死亡 / organ support-free days 序数 / MAKE30 复合）+ 务实/自适应/平台/集群设计 + 克制结论」范式
    - 明确频率学派 vs 贝叶斯两套数字报告分野、organ support-free days（death=−1）、marginal/conditional OR、Fine–Gray 竞争风险、G-computation/van Elteren 统计写法
    - 强化同期背靠背试验对比与提前停止（equipoise lost/futility）克制表述