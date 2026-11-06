---
name: research-stats
description: 科研统计融合技能，全程用 R 执行：六道数据闸门先于任何数字落地，方法必须与研究设计匹配，报告必须给效应量与 95% 置信区间。覆盖基线表、两组与多组比较、纵向轨迹、回归、生存分析、预测模型、可解释性、倾向评分与真实世界证据、诊断试验、Meta 分析、孟德尔随机化、复杂抽样、缺失值插补、样本量、相关一致性、数据清洗与统计报告审查。
whenToUse: 用户提出统计与数据分析需求时使用，包括做基线表、选检验、拟合回归、画生存曲线、建预测模型、跑 PSM 或 IPTW、做诊断试验、合并 Meta、做孟德尔随机化、处理 NHANES 加权数据、做多重插补、算样本量、算 ICC 与 Kappa、清洗数据或审查统计报告。
---

# 科研统计融合技能（v3.0.0）

本域把 31 个源技能融合成 18 张能力卡。所有卡共享同一条底线：**统计一律用 R 执行**，Python 统计栈只作方法选择逻辑与效应量基准的来源；任何统计数字落地前必过六道数据闸门；方法必须与研究设计匹配；报告必须给效应量与 95% 置信区间。未过闸门的 P 值不写进论文，这是本技能与「直接调个函数出结果」的根本区别。

## 一、本域任务判定树

先判断用户说的到底是哪件事，再进对应能力卡。判定顺序如下，命中即停：

1. 数据还没变成可分析形态（格式乱、码表不明、千分位、日期倒挂、含身份证号）→ `stats.clean`；若涉及患者隐私外传，先走本卡的本地扫描与分级。
2. 目的是描述样本特征或做 Table 1 → `stats.baseline`。
3. 比较两组 → `stats.twogroup`；三组以上或纵向重复测量 → `stats.multigroup`；要把多时点归成几条轨迹 → `stats.trajectory`。
4. 要估计暴露与结局的关联并调整混杂 → `stats.regression`；随访时间与事件状态已经存在 → `stats.survival`。
5. 要做一个能给出概率的临床工具 → `stats.prediction`；要解释已有模型为什么这样判 → `stats.interpret`。
6. 观察性数据里治疗不是随机分配的 → `stats.psm`；数据来自复杂抽样（NHANES 等）→ `stats.survey`。
7. 有金标准要评价某个指标 → `stats.diagnostic`；要把多项研究合并 → `stats.meta`；要用遗传工具推因果 → `stats.mr`。
8. 数据有缺失、不知道该删还是插补 → `stats.missing`；研究还没开始、要算需要多少例 → `stats.power`；要评价两个测量能不能互换 → `stats.corr`。
9. 稿子写完了但统计部分被审稿人质疑，或自己要交稿前核一遍 → `stats.reportaudit`。

三条越界规则：涉及文献检索与筛选流程（PRISMA 数字）先走文献域，本域只做合并计算；涉及论文文字润色走润色域；涉及绘图最终排版走绘图域——但统计图的数据与标注必须回到本域核对。**统计执行永远在本域，不外包。**

## 二、每张能力卡的融合 SOP

每节先给融合思路（取谁的什么、补谁的什么、为什么），再给可照做的步骤与阈值。卡内引用的技能均在 `knowledge/catalog.json` 中可查。

### stats.baseline 描述统计与基线表

融合思路：r-medical-stats 有闸门脚本与 tableone/gtsummary 三线表，但它不管「样本是怎么一步步排除出来的」；scholar-eda 有逐步排除记 N 前后与缺失分级，却没有医学检验的分流规则。本 SOP 取前者的闸门与检验树、后者的排除留痕与缺失分级，合起来才是一张能过审的 Table 1[1]。

1. 跑闸门 1–2：逐列核 `is.numeric` 与因子水平，千分位逗号按 `^[0-9,]+(\\.[0-9]+)?$` 修回数值并记录被改行数；年龄>120、BMI<10、日期倒挂逐列计数，为 0 才继续。
2. 记分析样本：按结局缺失、关键暴露缺失、失访、年龄界值逐条过滤，每步记录排除前 N、排除后 N 与原因，输出排除流程表；Table 1 的 N 必须等于该表末行。
3. 判分布：分组做 Shapiro-Wilk（每组 n≤50）或看偏度与 Q-Q（n>50），组间方差用 Levene；正态报均数±标准差，偏态报中位数（P25，P75）。
4. 选检验：两组 t 或 Mann-Whitney，多组 ANOVA 或 Kruskal-Wallis，分类卡方（期望频数<5 用 Fisher），配对用配对检验；每个 P 值同报统计量与自由度。
5. 出表：三线表给整体列、分组列、P 列、缺失列；格内 n<10 折叠不报百分比；表注写检验方法、缺失比例、SMD 阈值 0.1。
6. 留痕：关键变量出直方图或小提琴图，异常值标注不擅自删除；SVG、PDF、PNG 三格式，`sessionInfo` 写进 `out/logs`。

### stats.twogroup 两组比较

融合思路：r-medical-stats 给检验选择树与前提检查代码，statistical-analysis 给效应量基准（d 取 0.2、0.5、0.8）与「事后效能不作辩护」的判断，nature-statistics 给审稿人视角的图注规范。三者叠加才避免「只报一个 P 值」[2]。

1. 定独立单位：同一对象多部位、多时点的读数不算独立样本，按对象聚类或改用配对与混合模型。
2. 查前提：Shapiro-Wilk 与 Q-Q、Levene、IQR 标离群；结果写进结果段或附录，任一项违反说明改用了什么稳健方法。
3. 选检验：独立连续正态用 t（方差不齐用 Welch），偏态用 Mann-Whitney；配对用配对 t 或 Wilcoxon；二分类卡方，期望频数<5 用 Fisher。
4. 计效应量：连续给 Cohen's d 或 Hedges' g 与 95%CI，二分类给 RR 或 OR 与 95%CI；按小 0.2、中 0.5、大 0.8 解释，并声明这是约定不是临床阈值。
5. 出图与写句：箱线或小提琴叠个体点，配对数据出连线图；结果句同报统计量、df、精确 P 与效应量，P 保留三位小数，不出现 P=0.000。

### stats.multigroup 多组与重复测量

融合思路：r-medical-stats 给 RM-ANOVA、混合模型与 GEE 的决策树与球形检验；r-trajectory-models 补「多随机起点防局部最优」；statistical-analysis 补事后比较与 η²p 解释；statsmodels 只在无 R 时兜底。分工明确是因为 GEE 的稳健标准误与混合模型的随机效应回答的是不同问题[3]。

1. 判结构：等距多时点走重复测量或混合模型，多层嵌套（中心-患者）走多层模型；不能把多层数据压平。
2. 查球形：Mauchly 检验，违反用 Greenhouse-Geisser 并报 ε；严重违反或缺失多改混合模型或 GEE。
3. 定模型：写清固定效应（组、时间、组×时间）与随机效应（至少个体截距）；GEE 指定工作相关结构与稳健标准误并说明理由。
4. 事后比较：两两比较用 emmeans 或 Tukey，比较数超过 3 用 Holm 或 FDR，报校正后 P。
5. 出图：主图各组均值±95%CI 折线，辅图抽样 spaghetti；表给固定效应估计、95%CI、P、ICC。

### stats.trajectory 纵向轨迹分组

融合思路：r-trajectory-models 是唯一条目给 BIC 之外的四项指标（Avepp>0.7、OCC>5、entropy、每组占比≥5%）与「阶次必须统一才能比信息准则」；r-medical-stats 补轨迹作暴露后的回归与出图；scholar-eda 补时点缺失诊断。取三者才避免把局部最优当最优解[4]。

1. 宽转长：`pivot_longer` 带 `.value` 与时间列；时点少于 3 个或每组预期个体过少时先评估要不要做轨迹。
2. 定阶次跑组数：固定阶次跑 ng=1 到 5，比 AIC、BIC、SABIC、CIC；跨模型比较严禁改阶次。
3. 四项指标定模型：信息准则加 Avepp、OCC、占比；lcmm 先 `gridsearch(rep=100)` 再 `hlme` 精跑并报 loglik。
4. 重编号：模型组号随机，按轨迹均值高低重排并在表里注明，否则读者会把 Class 1 当最低组。
5. 后续分析：以轨迹组为暴露做多项 logistic（RRR 与 95%CI），并声明分组是数据驱动、敏感性用软分类概率或改组数复核。

### stats.regression 线性与 logistic 回归

融合思路：r-medical-stats 给 uni_multi 与 three_models 递进建模与 VIF、DW 诊断；r-aging-cohort-databases 给未调整、部分、完全调整策略与 RCS 非线性 P；r-nhanes-analysis 提醒抽样数据必须 svyglm。合起来是「既查共线又防过度调整」的一套[5]。

1. 过闸门：连续结局 lm，二分类 glm，计数先试 Poisson 看过离散；二分类必核 EPV，每变量至少 10 个事件，不足先减变量或改 Firth。
2. 筛变量：单因素 P<0.2 或临床公认混杂入候选；把变量按混杂、暴露、中介分类，中介不进主模型。
3. 查共线：VIF>10 视为严重，5–10 需说明；|r|>0.8 的变量对只留一个；线性结局查残差 Q-Q 与 DW。
4. 三套模型：未调整、加人口学、再加临床混杂，同表并列 OR 或 β 与 95%CI 和 P；方向反转必须解释而非删掉。
5. 剂量反应：连续暴露用 `rcs(x,4)`，报整体 P 与非线性 P；交互显著才分层，分层写各层样本量与事件数。

### stats.survival 生存分析

融合思路：r-medical-stats 给 survfit 与 cox.zph；r-clinical-prediction-model 给竞争风险的关键教训——1−KM 会高估累积发生率（实测 t=8 时高估 71%），Fine-Gray 的 sHR 与病因别 HR 可差 58%；r-aging-cohort-databases 补离散波次用 cloglog。三张卡拼起来才不把竞争事件当删失[6]。

1. 核时间：统一单位（月或年）与随访起点；时间不得为负或 0，结局状态只有 0 与 1，竞争事件单列编码。
2. 出 KM：附风险人数表，组间 log-rank；有竞争事件时画累积发生率函数，中位生存报 95%CI 并注明是否达到。
3. Cox 与 PH：报 HR、95%CI、精确 P，跑 `cox.zph` 与 Schoenfeld 残差；违反时用时依 `tt()`、分层 `strata()` 或改参数模型，写明理由。
4. 竞争风险：cuminc 或 Fine-Gray 求 sHR 并同时报病因别 HR，两者不混用；多模型递进给未调整到完全调整。
5. 亚组：每组给事件数、HR、95%CI 与交互 P；亚组变量超过 5 个做多重校正，交互不显著不声称亚组获益。

### stats.prediction 预测模型开发

融合思路：r-clinical-prediction-model 有十步流程、TRIPOD 对照与列线图、校准、DCA 全套；r-medical-stats 补 bootstrap 乐观度校正与三格式出图；r-machine-learning-interpretability 补 DeLong 比较与防泄漏。scikit-survival 是弃用成员——它能算 C-index，但给不出列线图与校准曲线，且与 R 交付栈冲突[7]。

1. 定类型：结局在当下用 logistic，需随访时间用 Cox 并常量化时间；拆分按结局分层，拆分代码必须写在筛选与标准化之前。
2. 筛变量：单因素 P<0.2 或 Lasso；EPV≥10，分类变量按哑变量数计参数，超标先减变量。
3. 辨别度：AUC 带 95%CI（`ci.auc` 必须传 roc 对象），生存用 C-index 并说明是否校正乐观度；多模型比较用 DeLong 加 Holm。
4. 校准与效用：校准曲线看斜率与截距，配 Brier 与 H-L（df=组数−2）；DCA 覆盖临床决策阈值，与全治、全不治比较。
5. 验证与呈现：bootstrap 至少 200 次报校正后 C 指数与校准斜率；列线图给分值刻度与总分对应风险；缺外部验证写进局限性。

### stats.interpret 模型可解释性

融合思路：r-machine-learning-interpretability 有 kernelshap 与 shapviz 全流程；shap 补 SHAP 理论与图型；r-medical-stats 给一个硬自检——线性模型 SHAP 应还原为系数乘（特征值减基线均值），因此 logistic 的 SHAP 排序必须与 OR 排序一致，不一致即实现或编码错[8]。scikit-learn 弃用：只给预测标签，不给 SHAP 值与统计推断。

1. 定对象：解释只在验证集或新数据上做；全局用固定种子抽样的背景样本，个体用瀑布图，两类图不混。
2. 算 SHAP：kernelshap 需模型、特征矩阵、背景样本与预测函数；分类模型指定输出为概率，记录抽样种子与背景量。
3. 互校：SHAP 排序对 OR 排序，差异先查实现与编码；不允许把矛盾结果直接写进结论。
4. 出图：蜂群、依赖、瀑布三图；图注写背景样本、单位与方向。
5. 声明边界：SHAP 是模型内解释，不证明因果；同时报相对 logistic 的增量 AUC、NRI、IDI，增量不显著就不必上复杂模型。

### stats.psm 倾向评分与真实世界证据

融合思路：r-real-world-evidence 给 cobalt 的 love.plot、ESS、重叠权重与 CCW；r-propensity-score-methods 给 ATT/ATE/ATO 反事实框架与 caliper=0.2 个 PS 标准差；r-medical-stats 补 E-value 与敏感性模板。关键口径三者一致：平衡看 |SMD|<0.1，不看 P 值[9]。

1. 定问题：写清比较哪两个策略、目标人群是谁，声明 ATT、ATE 或 ATO，估计量决定加权公式，不能事后挑。
2. 建 PS：logistic 以处理为因变量；匹配最近邻 caliper 取 0.2 个 PS 标准差，IPTW 用稳定化权重，极端权重按 1% 与 99% 截断，重叠人群用 1−e/e。
3. 核平衡：全表算 SMD，阈值 |SMD|<0.1 全表通过才算平衡；出 Love plot 与 PS 分布叠合图，不用 P 值判平衡。
4. 估效应：加权后用 survey 设计或稳健三明治方差，二分类与计数用 quasibinomial、quasipoisson；报权重范围、均值与 ESS=(Σw)²/Σw²。
5. 敏感性：至少三种（换估计量、改截断、排除极端 PS）；E-value 点估计与 CI 下限各给一个，解释需多大未测混杂才能推翻结论。

### stats.diagnostic 诊断试验与一致性

融合思路：r-medical-stats 给 pROC 与 2×2 全套；r-clinical-prediction-model 补 NRI、IDI 与 DeLong；statistical-analysis 补效应量基准。scikit-learn 弃用——`roc_auc_score` 不给 CI 也不做配对检验[10]。

1. 辨设计：同一批对象接受两指标为配对，两组独立则不能算配对一致性；2×2 四格加总必须等于样本量。
2. 算指标：敏感度、特异度、LR+、LR−、PPV、NPV 各带 95%CI；PPV 与 NPV 绑定本研究患病率，跨人群使用要说明。
3. ROC 与切点：AUC 用 `ci.auc(roc对象)`，切点按约登指数或临床可接受敏感度定，并在图上标出该点。
4. 比较：配对设计用 DeLong 加 Holm；增量价值报 NRI、IDI 与 95%CI，注明 NRI 是连续型还是分类型。
5. 局限：写清单中心、病例谱偏倚与未做外部验证；图注给金标准、样本量、患病率与切点。

### stats.meta Meta 分析

融合思路：全库没有专职 Meta 技能，ima-lit-meta-ppt 是唯一真正实现随机效应合并与森林图的条目（双反正弦变换、DL 法 tau²、HKSJ 校正、口径分层、14 类比例陷阱），但它偏比例型且无 metafor 包；r-medical-stats 补报告纪律与出图；statistical-analysis 补效应量类型选择。本卡必须如实标注公式为自实现并做交叉验证[11]。

1. 定效应量：二分类 OR 或 RR 取对数，连续用均数差，单组比例用双反正弦；声明随机效应模型与 tau² 估计法、是否 HKSJ。
2. 算合并：DL 法 tau²=(Q−df)/C，C=Σw−Σw²/Σw；研究数<10 时 Wald CI 偏窄，必须并列 HKSJ（实测约两倍宽）。
3. 查异质：报 I² 与 Q 的 P，I²>50% 做亚组；不同测量口径（病灶数、血管支数、患者数）分层各自合并，混池会让 I² 虚高。
4. 查偏倚：研究数≥10 才做漏斗图与 Egger，报截距与 P；补充剪补或留一法，写明每一步做了什么。
5. 出图与如实说明：森林图三栏（研究、效应量与 CI、权重）；方法段写软件为 R、无 metafor 时公式自实现并经交叉验证；检索与筛选给 PRISMA 数字。

### stats.mr 孟德尔随机化

融合思路：r-mendelian-randomization 是唯一给完整九步与四层多效性检验的技能，其最狠的教训是等位基因方向写反时全部 beta 反转而 SE 与 P 不变——唯一不会报错的致命错误；r-medical-research-master 补 STROBE-MR 报告条目；r-medical-stats 补方向核对闸门[12]。

1. 筛工具：p<5e-8，clump 参数 10000 kb / 0.001 r²；报工具数、F 统计量与 R²，弱工具使 IVW 有偏。
2. 协调方向：`harmonise_data(action=2)` 后必须查 `table(mr_keep)` 与被剔 SNP，回文 SNP 用 EAF 匹配。
3. 主分析与敏感性：IVW 为主，Egger、加权中位数、加权众数并列；报 Cochran Q、Egger 截距、MR-PRESSO（NbDistribution≥5000）、留一法。
4. 方向与强度：Steiger 检验确认方向，报 F 与 R²；三假设逐条写——相关性靠工具强度、独立性靠设计、排他性靠多效性代理，禁止写「三假设均已满足」。
5. 出图与局限：散点、单 SNP 森林、留一法三图；局限写人群限制、样本重叠与残余多效性，方法段按 STROBE-MR 组织。

### stats.survey 复杂抽样与加权

融合思路：r-nhanes-analysis 给 svydesign、多周期权重与 lonely.psu 的完整教训（不设 `options(survey.lonely.psu="adjust")` 会直接失败）；r-aging-cohort-databases 补协变量与 Codebook 核对；r-real-world-evidence 补 ESS 与稳健方差。statsmodels 弃用：没有调查设计对象，权重会被当精度权重导致 CI 过窄[13]。

1. 对齐权重：体检用 WTMEC2YR、访谈用 WTINT2YR、1999–2002 用 WTMEC4YR；合并 K 个两年周期权重除以 K。
2. 清洗：7、9、77、99、777、999 转 NA；多周期同名变量核对单位（如 mg/dL 与 mg/L）；量表重叠条目剔除。
3. 建设计：`svydesign(ids=~PSU, strata=~STRATA, weights=~W, nest=TRUE)` 并设 lonely.psu；之后所有分析接设计对象。
4. 分析：描述用 svymean、svyquantile；回归用 svyglm 并指定 family，二分类与计数用 quasibinomial、quasipoisson；RCS 可经对称改写为 rms 模型。
5. 报告：给权重范围、ESS 与设计效应；敏感性对比未加权、排除极重权重与换周期集合。

### stats.missing 缺失值与多重插补

融合思路：r-aging-cohort-databases 给 MICE 的 m≥20、maxit 至收敛与 `pool()` 合并；scholar-eda 给 Little's MCAR 检验、影子矩阵与缺失分级（>20% 为重大限制）；r-clinical-prediction-model 给「逐插补集算指标再 Rubin 合并」的正确姿势[14]。三者缺一就会犯「先平均插补值再建模」的错。

1. 查模式：`md.pattern` 看是否成块，按变量算缺失比例；<5% 可完整病例并说明，5–20% 建议插补，>20% 写进局限。
2. 判机制：Little's MCAR 检验（p<0.05 拒绝 MCAR）加影子矩阵；MAR 需说明哪些观测变量解释缺失，MNAR 只能靠敏感性。
3. 设插补：连续 pmm、二分类 logreg、无序分类 polyreg、计数 poisson；m 取 max(缺失百分比, 20)，maxit≥10 并检查收敛；插补模型应含结局。
4. 合并：`with(imp, glm(...))` 后 `pool()` 做 Rubin 合并，不能先平均插补值再建模；报插补间方差与合并方差之比。
5. 敏感性：完整病例与插补结果并列；再做模式混合或 delta 调整，写明假设；出缺失模式图与插补分布对照。

### stats.power 样本量与效能计算

融合思路：r-medical-stats 给 15 种设计的样本量公式与函数（pwr、power.roc.test、wp.rmanova、Schoenfeld、Diggle）；statistical-analysis 给「事后效能不能当辩护」这条判断；r-clinical-prediction-model 给预测模型的 EPV 规则[15]。

1. 定设计：明确主结局类型与比较结构（两组、多组、配对、非劣效）；一个研究只用一个主结局算样本量。
2. 取参数：效应量来自文献、预试验或最小重要差异并注明出处；α 双侧 0.05，把握度 0.8 或 0.9；连续结局给标准差。
3. 套公式：两组连续用 pwr.t.test，二分类用 pwr.2p.test，生存用 Schoenfeld（需事件数），诊断用 power.roc.test，重复测量用 wp.rmanova 或 Diggle。
4. 放大与敏感性：按失访率换算（失访 20% 则除以 0.8）；效应量取保守与乐观两端各算一次，给效能随样本量变化曲线。
5. 已完成的回顾性研究：只报最小可检出效应并写进局限，事后效能不得用来证明设计合理。

### stats.corr 相关与一致性

融合思路：r-medical-stats 给 ICC、Kappa 与 Bland-Altman 四要素；statistical-analysis 给相关方法选择与效应量约定；r-medical-research-master 给一致性研究的报告规范。核心判断是「相关强不等于可互换」[16]。

1. 定类型：两连续看散点与离群，等级或偏态用 Spearman，二分类一致性用 Kappa；两次测量必须配对同一对象。
2. 算相关：Pearson 或 Spearman 带 95%CI 与样本量，P 只说明是否非零；r 按 0.1、0.3、0.5 三档解释并声明是约定。
3. 一致性：ICC 写明型号与 95%CI，配 Bland-Altman 看系统偏移与 95% 界限；分类用 Kappa 注明加权。
4. 界限：先预设临床可接受界限（如血压差 5 mmHg）再看数据，界限内比例与离群点都要报。
5. 结论：相关强度与一致可互换性分开写，二者冲突时以一致性为准判断能否互换。

### stats.clean 数据清洗与衍生变量

融合思路：r-medical-stats 给 read_any 多格式读入与千分位修复；local-r-clinical-stats 给「清 locale + 脚本无 BOM」这条能救命的环境规则；scholar-safety 给上传前的 PII 扫描与分级；exploratory-data-analysis 给多格式结构摘要；scholar-code-review 做交付前只读审计兜底[17]。

1. 扫描先行：本地命令扫身份证号、手机号、姓名地址；二进制格式（sav、dta、rds、parquet、xlsx、zip）无法 grep，默认黄灯需人工确认，计数为 0 不得判绿。
2. 统一编码：按码表核对因子水平与数字码（0/1 含义、7/9 是否缺失码），统一单位并记录换算，多来源合并建对照表。
3. 修陷阱：千分位按正则修回并记录行数；日期统一 ISO 并查倒挂；离群值标记不删除，删除须留方案。
4. 生衍生：每个衍生变量登记公式、单位与边界处理（如 eGFR 注明 CKD-EPI 版本），切点优先用公认标准。
5. 交付：清洗脚本 UTF-8 无 BOM、首行清 locale，输出清洗后数据、变量字典与清洗日志，交付前对脚本做只读审计。

### stats.reportaudit 统计报告审查

融合思路：nature-statistics 给三问框架（测量了什么、分析单位是什么、推断有多强）与 P0/P1/P2 分级，其红线是「缺信息写 AUTHOR_INPUT_NEEDED，绝不替作者编 p、n、df」；r-medical-stats 给六道闸门复核清单；r-medical-research-master 给 TRIPOD、STROBE、STROBE-MR 条目对照[18]。

1. 问单位：每组数字测的是细胞、视野、动物还是人；同一动物多切片、同一患者多时点算伪重复，把细胞数当 n 是 P0。
2. 核 n：n 是独立生物学重复还是技术重复，是否写进图注；多面板是否逐面板给 n。
3. 核推断：是否把统计显著写成临床重要、是否只报 P 无效应量与 CI、多重比较是否校正、是否把相关写成因果。
4. 核图表：图注必须给 n 定义、误差棒含义、检验、校正与精确 P；星号写 adjusted p 与校正方法；条形图隐藏分布、箱线未写须规则分别标 P1 或 P2。
5. 出报告：每条问题给位置、依据与建议改法，按 P0 必须改、P1 影响可信度、P2 规范性分级；缺失数字列入待补清单。

## 三、常见错误清单

以下错误全部「软件不报错、结果看着正常、审稿人一看就退」，是本域最需要防的 12 类：

1. **千分位当字符**：数值列含逗号被读成因子，模型把每行当类别，C-index 可虚高到 0.97，先查列类型。
2. **0 值当真实值**：实验室 0 常是缺失码，BMI 为 7、年龄 200 是编码错，闸门 2 必须逐列计数。
3. **伪重复**：把细胞数、多部位读数当独立样本，n 虚增，P 值严重偏小；按个体聚类或换算到个体。
4. **先筛后分**：先在全量数据筛变量再拆分，乐观偏倚不可逆；拆分必须按结局分层且在最前面。
5. **训练集选超参**：用训练集 AUC 挑模型，选中训练集 AUC 接近 1 的过拟合模型，比较必须用验证集或交叉验证。
6. **EPV 不足**：二分类每变量事件数少于 10 仍硬塞变量，OR 有偏且 CI 过窄；减变量或 Firth。
7. **权重当精度权重**：`glm(weights=)`、`coxph(weights=)` 直接喂 PS 或抽样权重，CI 过窄；必须用 survey 或稳健方差。
8. **匹配后用 P 值判平衡**：加权后样本变大 P 必显著；平衡看全表 |SMD|<0.1 与 Love plot。
9. **1−KM 当累积发生率**：竞争事件存在时高估（实测高估 71%），应画累积发生率函数并区分 sHR 与病因别 HR。
10. **PH 未检验**：直接报单一 HR，效应随时间变化时结论失真；必须跑 cox.zph 与 Schoenfeld 残差。
11. **MR 方向写反**：全部 beta 反转而 SE 与 P 不变，是唯一零提示的致命错误；协调后必查 mr_keep 与回文 SNP。
12. **Meta 混口径**：不同测量口径混池使 I² 虚高（混池 81–97%，分层后 0–26%），必须分层各自合并。

另有三类表述错误要一并改掉：只报 P<0.05 不报精确值；只报统计显著不报效应量；把相关、SHAP 重要性或 AUC 增量写成因果证据。

## 四、交付前自检

交付任何统计产物前，按下面四步走完，任一步不过就回退修改，不带着问题交稿。

**第一步：闸门复核。** 六道闸门逐条打勾——①列类型核对（连续、分类、时间、ID 各就各位）②不可能值（年龄、BMI、日期倒挂计数为 0 或已回问）③缺失模式（MCAR、MAR、MNAR 与比例已写明）④事件数与 EPV（二分类与 Cox 每变量事件数≥10，写出事件数与参数数）⑤参数与性能合理性（OR 或 HR 量级合理、AUC 在 0.5–1、R² 非负）⑥方向核对（暴露与结局的方向与临床常识一致，编码未倒置）。任一道不过，结果只内部参考，不写进论文。

**第二步：报告完整度。** 每个效应量必须带 95%CI；每个 P 值给精确值（保留三位小数，不写 P=0.000，不写 P<0.05 了事）；每个检验同报统计量与自由度；多重比较写明校正方法（Holm、FDR 或 Tukey）；敏感性分析写明做了什么、结论是否改变；方法与软件版本写进方法段。

**第三步：图与表。** 图件同时给 SVG、PDF、PNG（≥300 dpi），SVG 可编辑再交排版；表格用三线表并给 DOCX 与 XLSX 双份；图注给 n 的定义、误差棒含义、检验名称与精确 P；表注给缺失比例、检验方法与 SMD 阈值。

**第四步：留痕。** `sessionInfo()`、数据版本、脚本路径、随机种子写入 `out/logs`；脚本 UTF-8 无 BOM，首行清 `LC_ALL`、`LANG`、`LANGUAGE` 再调 `Rscript`；若本机没有 R，按模式 B 交付六段式脚本与运行说明，并如实告知未实际运行，不伪造输出。

可直接复用的最小 R 骨架（闸门到出图，按需增删）：

```r
# 0 环境：先清 locale 再加载包，否则连 library() 都可能报错
Sys.unsetenv(c("LC_ALL", "LANG", "LANGUAGE"))
suppressPackageStartupMessages({ library(survival); library(pROC); library(tableone) })
set.seed(20261106)

# 1 读数据：数值列去千分位后转数值，字符列保持原样
d <- read.csv("data/analysis.csv", stringsAsFactors = FALSE, check.names = FALSE)
num_cols <- c("age", "bmi", "sbp")
for (v in num_cols) d[[v]] <- as.numeric(gsub(",", "", d[[v]]))

# 2 闸门：类型、不可能值、缺失率、EPV，任一不过就停
stopifnot(all(vapply(d[num_cols], is.numeric, logical(1))))
bad <- d$age > 120 | d$bmi < 10 | d$bmi > 60
missing_rate <- sapply(d[num_cols], function(x) mean(is.na(x)))
n_event <- sum(d$event == 1, na.rm = TRUE)
n_par <- length(num_cols) + 1L
if (any(bad, na.rm = TRUE)) stop("闸门 2 未过：存在不可能值，先回查来源")
if (n_event / n_par < 10) stop("闸门 4 未过：EPV<10，先减变量或改 Firth")

# 3 基线表与建模（示例：二分类结局）
tab <- CreateTableOne(vars = num_cols, strata = "group", data = d, addOverall = TRUE)
fit <- glm(event ~ age + bmi + group, data = d, family = binomial())
or_ci <- exp(cbind(OR = coef(fit), confint(fit)))

# 4 性能与假定：AUC 带 CI，生存再跑 cox.zph
roc_obj <- roc(d$event, fitted(fit), quiet = TRUE)
auc_ci <- ci.auc(roc_obj)                     # 必须传 roc 对象，传数值得到无效 CI
ph <- cox.zph(coxph(Surv(time, event) ~ age + bmi + group, data = d))

# 5 出图三格式与留痕
save_fig <- function(p, name) {
  ggsave(paste0("out/fig/", name, ".pdf"), p, width = 6, height = 4)
  ggsave(paste0("out/fig/", name, ".png"), p, dpi = 300)
  svglite::svglite(paste0("out/fig/", name, ".svg"), width = 6, height = 4); print(p); dev.off()
}
writeLines(capture.output(sessionInfo()), "out/logs/sessionInfo.txt")
```

## 五、能力卡索引表

| 能力卡 | 能力 | 主用技能 | 关键口径与闸门 | 转出目标 |
|---|---|---|---|---|
| stats.clean | 数据清洗与衍生变量 | r-medical-stats | 千分位修复、码表转 NA、PII 扫描分级 | 文献域（筛选流程）、绘图域（成图） |
| stats.baseline | 描述统计与基线表 | r-medical-stats | 闸门 1–2、排除流程 N 前后一致 | 写作域（表格文字） |
| stats.twogroup | 两组比较 | r-medical-stats | 前提检查、效应量与 95%CI 同报 | 写作域（结果段） |
| stats.multigroup | 多组与重复测量 | r-medical-stats | 球形检验与 ε、ICC、校正方法 | 轨迹卡、写作域 |
| stats.trajectory | 纵向轨迹分组 | r-trajectory-models | 阶次统一、Avepp>0.7、每组≥5% | 回归卡、生存卡 |
| stats.regression | 线性与 logistic 回归 | r-medical-stats | EPV≥10、VIF>10 处置、三套模型 | 预测卡、写作域 |
| stats.survival | 生存分析 | r-medical-stats | HR+95%CI+PH 检验、竞争风险单列 | 预测卡（预后） |
| stats.prediction | 预测模型开发 | r-clinical-prediction-model | 先分后选、校准与 DCA、外部验证局限 | 绘图域（列线图）、写作域 |
| stats.interpret | 模型可解释性 | r-machine-learning-interpretability | SHAP 排序对 OR 排序互校 | 预测卡、报告审查卡 |
| stats.psm | 倾向评分与真实世界证据 | r-real-world-evidence | 全表 SMD 绝对值<0.1、ESS、E-value | 生存卡、写作域 |
| stats.diagnostic | 诊断试验与一致性 | r-medical-stats | AUC 带 CI、配对 DeLong、患病率绑定 | 写作域、绘图域（ROC） |
| stats.meta | Meta 分析 | ima-lit-meta-ppt | 研究数<10 不做 Egger、口径分层、HKSJ | 文献域（PRISMA）、绘图域（森林图） |
| stats.mr | 孟德尔随机化 | r-mendelian-randomization | 方向核对、Egger 截距、MR-PRESSO 5000 | 写作域（STROBE-MR） |
| stats.survey | 复杂抽样与加权 | r-nhanes-analysis | 权重来源匹配、lonely.psu、ESS | 回归卡、缺失卡 |
| stats.missing | 缺失值与多重插补 | r-aging-cohort-databases | m≥20、pool 合并、MNAR 敏感性 | 全部建模卡 |
| stats.power | 样本量与效能计算 | r-medical-stats | 参数来源、失访放大、事后效能禁作辩护 | 选题域（研究设计） |
| stats.corr | 相关与一致性 | r-medical-stats | ICC 型号、Bland-Altman 界限、Kappa | 诊断卡、写作域 |
| stats.reportaudit | 统计报告审查 | nature-statistics | 分析单位、n 定义、P0/P1/P2 分级 | 润色域（改句）、写作域 |

使用顺序建议：数据类任务从 `stats.clean` 起步，建模类任务按「基线 → 比较 → 回归或生存 → 预测或解释」推进，投稿前固定用 `stats.reportaudit` 自查一遍；跨卡时上游的闸门结论与参数（EPV、权重、缺失比例、SMD）必须传递到下游，不允许各卡重新拍脑袋。
