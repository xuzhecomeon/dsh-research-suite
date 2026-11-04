---
name: research-stats
description: 科研统计融合技能（全程 R 执行）：六道数据闸门、方法-设计匹配与可核验报告。覆盖基线表、两组与多组比较、回归、生存、预测模型、可解释性、倾向评分、诊断试验、Meta、孟德尔随机化、复杂抽样、缺失值、样本量、一致性、数据清洗十六类任务。
whenToUse: 用户要做基线表、选统计检验、跑回归/生存/预测模型、PSM 与真实世界证据、诊断 ROC、Meta 分析、孟德尔随机化、NHANES 加权分析、缺失值插补、样本量计算、一致性评价或统计报告时加载。统计执行一律走 R，Python 只做抽取、文档与绘图排版。
---

# research-stats · 科研统计融合技能

这是一张能力卡：不打开任何原始 SKILL.md，按下面协议就能把统计做完并交得出去。原文只用来查更细的函数参数，七节正文按 `docs/CAPABILITY-SPEC.md` 固定结构组织。

## 一、本域边界

### 做什么

1. **数据到可发表结果**：基线表、两组比较、多组与重复测量、回归、生存、相关与一致性——每个数字都带效应量、95%CI 与精确 P。
2. **预测与诊断**：预测模型（列线图/ROC/校准/DCA/内部验证）、可解释性（SHAP、变量重要性、增量价值）、诊断试验（ROC/AUC/截断/似然比）。
3. **观察性因果**：倾向评分（PSM/IPTW/重叠加权）、克隆-删失-加权、E-value、孟德尔随机化三假设与多效性检验。
4. **证据综合**：效应量合并、异质性、发表偏倚、森林图；比例 Meta 的口径判定与 HKSJ 稳健方差。
5. **设计与数据**：样本量与效能、缺失机制与多重插补、复杂抽样加权、数据清洗与衍生变量；交付图（SVG+PDF+PNG）、表（DOCX/XLSX）、可重跑脚本与核查日志。

### 不做什么

1. **不做文献检索与筛选**：Meta 用的文献清单必须由用户或外部检索工具提供；不编造研究、不虚构 DOI。
2. **不做图片美化与期刊排版**：图形出到「可编辑、可复现」为止，投稿级配色与拼版转 research-figures。
3. **不代写论文主体**：只给方法段、结果段与表图注，语言润色转 research-polish / research-writing。
4. **不在没有 R 的环境里假装跑过**：无 Rscript 时走「模式 B」生成六段式脚本+运行说明，如实告知未执行。
5. **不把统计显著当临床重要，也不做无假设的因果宣称**：结论尺度是效应量与 CI，观察性因果必须随敏感性分析出现。

### 何时转出

| 场景 | 转去 | 理由 |
| --- | --- | --- |
| 论文结构、语言润色、投稿信 | research-writing / research-polish | 本域只给统计段落，不重写全文 |
| 图要投稿级美化、拼版、字体与栏宽 | research-figures | 本域只保证可编辑与数据可复现 |
| 要做汇报 PPT 或图集 | research-slides | 统计图→演示图是另一套版式 |
| 用户问「这个研究该怎么做」 | research-suite 总入口 | 设计问题先定研究问题与数据来源 |
| 文献检索、查重、引用格式 | 外部检索工具（本套件无此域） | 本域不虚构文献，也不替代检索 |

### 语言与执行边界

- **统计一律用 R**：检验、回归、生存、PSM、Meta、MR、加权分析全部落在 R，R 结果是唯一可交付的统计结论。
- **Python 只做非统计环节**：PDF/Word/Excel 抽取、批量文档生成、图形排版；`statsmodels`/`scikit-learn`/`scikit-survival` 仅在本机完全没有 R 时兜底，并在交付里注明「非 R 路线」。
- **两条调用铁律**：脚本 UTF-8 无 BOM（用 Write 生成，不要 PowerShell `Out-File -Encoding UTF8`）；调用前清空 `LC_ALL`/`LANG`/`LANGUAGE`，否则 locale 报错时连 `library()` 都读不到包。
- **写法能搬到别人机器**：配置区集中路径与变量名、正文零硬编码；「若本机有 `Rscript` 则直接执行，否则把脚本交给用户手工运行」——不把某台机器的绝对路径写成必须。

## 二、融合对比表

| 能力 | 主用技能 | 关键长处 | 明确短板 | 融合取舍 |
| --- | --- | --- | --- | --- |
| stats.baseline | r-medical-stats | tableone 三线表+闸门 | 不判临床意义 | 闸门先跑，正态性按 n 分档 |
| stats.twogroup | r-medical-stats | 检验选择树+效应量 | 不覆盖三组 | 选择树为主，效应量基准借 statistical-analysis |
| stats.multigroup | r-medical-stats | LMM/GEE 决策树 | 不做轨迹分组 | 取混合模型；轨迹分组借 r-trajectory-models |
| stats.regression | r-medical-stats | 三模型递进/RCS | 不做因果识别 | 取三模型；datadist 规范借老年库技能 |
| stats.survival | r-medical-stats | Cox+PH 处置 | 不做预测校准 | 取 Cox/PH；时间 ROC 借预测技能 |
| stats.prediction | r-clinical-prediction-model | 10 步+TRIPOD+校准 | 不做 ML 调参 | 取全流程；bootstrap 借引擎技能 |
| stats.interpret | r-machine-learning-interpretability | kernelshap+DeLong | 不做模型开发 | 取解释流程；shap 仅作对照 |
| stats.psm | r-real-world-evidence | 四路线+ESS+E-value | 不解决未测混杂 | RWE 主流程，反事实框架借 PS 技能 |
| stats.diagnostic | r-medical-stats | pROC/DeLong/四格表 | 不做诊断路径研究 | 取 pROC；STARD 借预测技能 |
| stats.meta | ima-lit-meta-ppt | FT/DL/HKSJ+14 类陷阱 | 不覆盖正式检索 | 自实现合并+陷阱表，森林图借引擎 |
| stats.mr | r-mendelian-randomization | 九步+四层多效性 | 不解决弱工具根因 | 取主流程；药靶场景借药理 MR |
| stats.survey | r-nhanes-analysis | svydesign+周期合并 | 强绑定 NHANES | 取设计对象；ESS 借 RWE |
| stats.missing | r-aging-cohort-databases | MICE 规范+pool 陷阱 | 不覆盖 MNAR 建模 | 取 m≥20/method 显式；评价借预测技能 |
| stats.power | r-medical-stats | 15 种设计实现 | 不做自适应设计 | 取公式与段落模板；事后效能警示借统计技能 |
| stats.corr | r-medical-stats | ICC/Kappa/BA 四要素 | 不做潜变量模型 | 取四要素；相关前提借 statistical-analysis |
| stats.clean | r-medical-stats | read_any+六闸门 | 不做多表主键合并 | 取读入与闸门；脚本审计借 scholar-code-review |


## 三、融合协议

动手前先定：结局类型、预测还是解释、是否抽样数据；六道闸门必须全绿（见 §四）。

### 1. stats.baseline 描述统计与基线表

1. **核类型扫异常**：逐列标连续/分类/时间/ID；连续列含千分位逗号或空串先转数值并记被改行数；扫年龄>120、BMI<10 或>60、日期倒挂、实验室值 0（生理不可能→实为缺失码），越界清单回问来源，禁止自行改值。
2. **定分布出表**：每组 n<50 看 Shapiro-Wilk（p<0.05 判偏态），n≥50 以 Q-Q 图为主不单看 P；偏态报中位数(IQR)。基线表固定列总体/各组/SMD/缺失，行式 mean±SD、median[IQR]、n(%)，SMD>0.1 的变量表注点名。
3. **比较与出图**：t/秩和/卡方/Fisher 按类型选，同表比较>10 个变量用 Holm 或 FDR 并写比较次数；三线表只留顶线、表头线、底线，配箱线/小提琴（含个体点），图出 SVG+PDF+PNG、dpi=300。

### 2. stats.twogroup 两组比较

1. **前提**：两组各自 Shapiro-Wilk+Q-Q、Levene 方差齐，配对看差值分布；n>30/组轻度偏离可继续参数检验，方差不齐改 Welch t，差值偏态改 Wilcoxon。
2. **选检验与效应量**：2×2 任一格期望<5 用 Fisher，否则卡方；连续结局按独立/配对×正态性四种之一。参数检验报 Cohen's d 或均值差 95%CI（基准 d=0.2/0.5/0.8 注明出处），二分类报 OR/RR，非参数报 Hodges-Lehmann 中位数差 CI。
3. **版式**：中文期刊同报统计量与精确 P（t=2.31，P=0.023）；SCI 报 t(df)=2.31，P=0.023，d=0.46（95%CI 0.08–0.84）；P<0.001 才写不等式，其余三位小数。配箱线/小提琴（写抖动宽度）、配对连线图、堆叠条形图。

### 3. stats.multigroup 多组与重复测量

1. **落模型**：独立三组→ANOVA/Kruskal-Wallis；同一批人多次测量→RM-ANOVA，有缺失或时点不齐直接 `lmer(y ~ time*group + (1|id))`；要群体平均效应用 `geeglm(corstr="exchangeable")`+稳健 SE，两路线不混报。
2. **前提与交互**：残差 Q-Q、Levene，重复测量必跑 Mauchly（p<0.05 用 Greenhouse-Geisser ε 校正，ε<0.75 可改 Huyhn-Feldt）。time×group 交互 P<0.05 才做各时点比较，`emmeans` 出边际均值，Tukey/Holm 校正并报校正后 P。
3. **出图**：分组均值±SE 折线标交互 P；个体轨迹抽 30 条做 spaghetti（全画必糊）；模型表给 β/OR、95%CI、随机效应方差与 ICC。

### 4. stats.regression 线性与 logistic 回归

1. **先定目的**：预测→先按结局分层拆分再筛变量（先分后选）；关联→按临床先验列混杂，中介与碰撞变量不进模型；因果→转 stats.psm 先画 DAG。
2. **诊断与筛选**：连续结局查 LINE 四条并做 DW；VIF<5 安全、5–10 需说明、>10 必须处理；二分类 EPV=事件数/参数个数（分类按哑变量计）<10 用 Firth 或减变量；单因素 P<0.2（保守 0.1）入多因素，逐步 AIC 只作敏感性，Lasso 先 `model.matrix`。
3. **三模型与剂量反应**：出未调整/部分调整/完全调整三列并报入选变量数与 EPV；交互项整体检验 P<0.10 再解释，报分层 OR 或 RERI。`rms::rcs(x, 4)`（n<100 用 3 节点）取 P for nonlinear，按每 IQR/每 10 单位出曲线并标参考点；森林图 x 轴 log 并标无效线。

### 5. stats.survival 生存分析

1. **定义与 KM**：起点与终点唯一、单位统一写表注；随访为离散波次（唯一值≤10）改 cloglog 并说明 ties。KM 配风险人数表，报中位生存+95%CI；两组 log-rank、三组以上校正。
2. **Cox 与 PH**：报 HR+95%CI+精确 P，连续变量写每单位/每 IQR 量纲，分类 `relevel` 指定参照；`cox.zph` 查逐变量与全局 P，违反时 `tt()` 加时变效应（只接受数值型）或 `strata()` 分层（分层变量失去 HR 须说明），不得删变量掩盖。
3. **竞争风险与局限**：1−KM 会高估累积发生率，改 `cuminc`/Fine-Gray，同时报 sHR 与病因别 HR 并给指定时点绝对风险差；局限性写删失比例、事件数/EPV、是否考虑竞争风险与残余混杂。

### 6. stats.prediction 预测模型开发

1. **闸门+拆分**：六道闸门留痕；`createDataPartition(y = 结局)` 按结局分层，先拆分再筛变量与标准化（全量算均值方差即泄漏），拆分比例与种子写进方法段。
2. **建模+列线图**：诊断用 `lrm(x=TRUE, y=TRUE)`，预后用 `cph(x=TRUE, y=TRUE, surv=TRUE)`；列线图诊断反 logit 总分、预后 `Survival()`/`Quantile()` 指定时点，系数表与列线图必须能互算。
3. **区分度、校准与验证**：AUC+95%CI 用 `pROC::ci.auc(roc 对象)`；C-index 用 `summary(coxph)$concordance[1]`（rcorrcens 的 C 列是 1−C）；校准用 `val.prob`/`calibrate`（u 与 time.inc 一致、cmethod="KM"）+H-L（df=g−2）+Brier，斜率偏离 1 或截距偏离 0 要点明（实测 AUC 0.865 的模型外部校准斜率可低至 0.776）。`dcurves` 出 DCA，Bootstrap≥200 算 optimism 校正；无外部验证在局限性首句声明并按 TRIPOD 15 条核对。

### 7. stats.interpret 模型可解释性

1. **前置核查**：模型须在验证集或 CV 上评估过且无泄漏（标准化/插补在拆分后、超参由 CV 选）；不满足先回 stats.prediction，不在坏模型上解释。
2. **算 SHAP 并自检**：`kernelshap(model, X, bg_X, pred_fun)` 背景集 100–200 行、解释集≤1000 行，转 `shapviz` 出蜂群/依赖/瀑布。线性/Logistic 的 SHAP ≈ 系数×(x−基线均值)，排序必须与 OR/β 一致，不一致先修实现。
3. **增量价值与边界**：与 Logistic 比 ΔAUC+95%CI、NRI/IDI；多模型比较用 DeLong+Holm/FDR（实测 8 模型校正后常全无差异），报校正后 P。结果按重要性列 top10 并声明「模型解释非因果」，含个人标识列先脱敏。

### 8. stats.psm 倾向评分与真实世界证据

1. **DAG+估计量**：画 DAG 列混杂/中介/碰撞并写最小调整集；治疗组→ATT（PSM）、全人群→ATE（IPTW）、临床均势→ATO（重叠加权），声明后不改口径。
2. **拟合与平衡**：`glm(T ~ X, binomial)` 取 `fitted()`，X 只放混杂；PSM 用 MatchIt nearest、caliper=0.2×PS 的 SD、replace=FALSE、设种子。全表 |SMD|<0.1 才算平衡，配 `cobalt::love.plot(thresholds=c(m=.1))` 与 `bal.plot(which="both")`，不得用 P 值判平衡。
3. **效应、权重与敏感性**：IPTW 后用 `svyglm(quasibinomial)`/`svycoxph` 或 `coxph(weights=, robust=TRUE, cluster=id)`，匹配后用 clogit，二分类/计数用拟二项/拟泊松族。ESS=(Σw)²/Σw²，报权重 min/max/mean 与>10 的比例，必要时 1%/99% 截断作敏感性；E-value 给点估计与 CI 下限，结局发生率>15% 用 rare=FALSE 或改报 RR，再做负对照结局与 ATT/ATE 口径对比。

### 9. stats.diagnostic 诊断试验

1. **金标准与 ROC**：病例定义、目标人群、排除标准唯一可复现，金标准无法判定者单列不确定组，STARD 流程图给每层人数；`pROC::roc(response, predictor, direction=, levels=)` 明确正类，AUC+95%CI 用 `ci.auc(roc 对象)`（传数值得到无效 CI），AUC<0.5 先查方向。
2. **比较与截断**：`roc.test(method="delong")` 给 AUC 差+CI，三个以上做 Holm/FDR；截断按 Youden 或临床可接受敏感度，四格全列并报敏感度/特异度/PPV/NPV/阳性与阴性似然比及 95%CI。
3. **效用与报告**：DCA 给临床阈值区间内净收益并对照 treat-all/treat-none；按 STARD 写方法（盲法、金标准、样本量依据），结果先 AUC 再截断处指标。

### 10. stats.meta Meta 分析

1. **口径与 k**：二分类 OR/RR、时间事件 HR、连续 MD（同量表）或 SMD；比例用 Freeman-Tukey `t=asin√(k/(n+1))+asin√((k+1)/(n+1))`、方差 `1/(n+0.5)`。k=1 报单值、k=2 报两值不合并、k≥3 才合并并报 I² 与 τ²；不同口径绝不混池。
2. **合并与异质性**：DL 法 `tau2=(Q−dfree)/C`、`C=Σw−Σw²/Σw`，CI 用 1.96×SE；REML 发散按尺度设上限（FT ≤2.467），k=3 优先 DL。Q+I²（>50% 中高度异质）+τ²；先做口径分层 Q_between（p<0.001 说明口径主导异质性，主分析限定单一口径）；k<10 用 HKSJ（`se=√(q/Σw)`，t 分布 df=k−1）并与 Wald 并列。实测混池 I² 81–97%，分层后 0–26%。
3. **偏差与交付**：k≥10 才做 Egger+漏斗图；二次数据（汇总综述、分母 100）必须排除；缺失=0 还是成对删除用闭合检验（Σk 是否等于分母）判定并表注。森林图三栏（标签+效应量/CI 线+方块面积∝权重/权重与 I²），Excel 三表保证可重跑。

### 11. stats.mr 孟德尔随机化

1. **工具与方向**：p<5e-8（药靶可放宽 1e-5）、`clump_kb=10000`、`clump_r2=0.001`（需 OPENGWAS_JWT 或本地 LD 面板），逐个算 F，F<10 为弱工具；`harmonise_data(action=2)` 会静默剔除 SNP，必须查 `table(dat$mr_keep)` 与被剔名单，回文 SNP 用 EAF 匹配。等位基因写反会让 β 全反向而 P/SE/Q 不变——零报警错误，必须逐 SNP 核对。
2. **主分析与四层敏感性**：IVW 为主，并列 MR-Egger、加权中位数、加权众数，报每 SD 或每单位暴露的 OR/β+95%CI；`mr_heterogeneity` 报 Q、`mr_pleiotropy_test` 报截距（功效低，阴性≠无多效性）、`run_mr_presso(NbDistribution≥5000)` 报全局与离群 SNP、`mr_leaveoneout` 查单点驱动。
3. **方向与报告**：`directionality_test` 报 Steiger P、`add_rsq` 报 R² 与 F；两样本重叠必须讨论，ancestry 不一致写进局限性。按 STROBE-MR 三假设逐条交代（相关性可检验、独立性靠设计、排他性靠多效性检验代理），散点/森林/漏斗/留一法四图齐。

### 12. stats.survey 复杂抽样与加权

1. **权重与设计**：MEC 检查→WTMEC2YR、访谈→WTINT2YR、1999–2002→WTMEC4YR，K 个两年周期合并权重除以 K；`svydesign(ids=~SDMVPSU, strata=~SDMVSTRA, weights=~wt, nest=TRUE)`，必设 `options(survey.lonely.psu="adjust")`，否则单 PSU 层无法估方差、分析直接失败。
2. **清洗**：7/9/77/99/777/999 先转 NA；量表条目重叠必须剔除（研究睡眠时抑郁量表含睡眠条目会人为制造相关）；跨周期变量名与单位不同（mg/dL vs mg/L）先统一。
3. **加权分析与报告**：`svyquantile` 程序化算切点（不硬编码某年分位数）、`svyCreateTableOne` 出加权基线、`svyglm` 多模型递进；加权 RCS 用 `svy2rms` 改写为 rms 模型（权重归一化、normwt=TRUE），因 rms 不支持 survey。报加权 ESS 与子人群敏感性，未加权结果仅作对照。

### 13. stats.missing 缺失值与多重插补

1. **模式与机制**：汇总每变量缺失率与每行完整度，`mice::md.pattern` 画模式矩阵并找共缺失簇；Little 检验只作参考，更可靠的是缺失与观测变量的关联（系统关联→MAR）与缺失原因（病情重者未复查→MNAR），判断写进方法段。
2. **策略与执行**：关键变量缺失<5% 可完全案例分析并说明，5%–40% 用多重插补，>40% 不插补改报缺失或加缺失指示变量，结局变量不得插补；m≥20（正式分析 20–50）、maxit 至链收敛，method 按类型（连续 pmm、二分类 logreg、有序 polr），插补模型必须含结局与全部分析变量。
3. **合并与敏感性**：`with(mids) + pool()` 按 Rubin 合并，禁止手工平均；模型性能逐插补集算再合并；敏感性至少做（MAR vs MNAR、m 数量、插补变量集）三选二并同表对照。

### 14. stats.power 样本量与效能计算

1. **定参数**：只设一个主要结局（多终点要校正）；效应量取文献区间中点或最小临床重要差异并写来源；双侧 α=0.05、power=0.80（探索性 0.90），失访按同类研究 10%–20%。
2. **选公式**：两组连续 `pwr.t.test`、两组率 `pwr.2p.test`、多组 `pwr.anova.test`、重复测量 `wp.rmanova`、生存用 Schoenfeld 先算事件数再折人数、诊断 `power.roc.test`、预测模型按 EPV≥10 反推。
3. **留证与敏感性**：脚本落盘可重跑并输出参数表（效应量假设、α、power、失访、样本量/事件数）；效应量取保守/基准/乐观三档给区间，招募不可行时改报现有样本能检出的最小效应量，不用事后效能。方法段写软件版本、检验类型、效应量及依据、α 与 power、失访假设与最终样本量（例：d=0.5、双侧 α=0.05、power=0.80 每组 64 例，按 15% 失访扩至每组 76 例）。

### 15. stats.corr 相关与一致性

1. **定问题**：两个不同变量的关系→相关；同一量纲的重复测量（重测/评分者/两法）→一致性；量表条目→信度（Cronbach α 或 ω）。选错系数是这块最常见的错误。
2. **系数**：双变量正态且线性用 Pearson，否则 Spearman，报 r 或 ρ+95%CI 与样本量并看散点图（Anscombe 陷阱）；连续测量报 ICC(2,1)（多次取均值报 ICC(2,k)）并写明模型、类型、定义三要素，分类用 Cohen/Fleiss Kappa，有序用加权 Kappa。
3. **Bland-Altman**：差值对均值作图，报偏差与 95% LoA（偏差±1.96SD），查比例偏倚与离群点，异方差改画百分比差或回归法 LoA。阈值：ICC>0.90 优、0.75–0.90 良、0.50–0.75 中（Koo & Li），Kappa>0.80 强。

### 16. stats.clean 数据清洗与衍生变量

1. **读入与缺失码**：`read_any` 按扩展名识别 csv/xlsx/sav/dta；连续列被读成字符查千分位逗号、空串、单位后缀，修复后强转数值并记被改行数；-9/7/9/77/99/777/999 按变量字典转 NA 并记录；0 值先做生理核查（血压 0、BMI 0 是缺失码），查日期倒挂与重复 ID。
2. **类型与衍生**：ID 不进模型，分类转因子 `relevel` 后赋值回变量，单位统一（mg/dL 与 mmol/L 不混用）；衍生变量写公式与单位（BMI=kg/m²、eGFR 用 CKD-EPI 2021、变化率=(后−前)/前），衍生后跑边界核查（BMI 10–60、eGFR>0），越界回溯原始值而非截断。
3. **审计复现**：记录每步输入/输出行数、被改值计数与规则编号；同一脚本从原始文件重跑核对行数与关键统计量；原始文件只读，输出写新文件。


## 四、判据与红线

### 4.1 六道数据闸门（任何统计数字落地前必过）

| 闸门 | 检查什么 | 通过标准 | 不过怎么办 |
| --- | --- | --- | --- |
| 1 列类型 | 千分位逗号/空串是否把数值列读成字符，分类码表是否一致 | 连续列 `is.numeric` 为真；因子水平与码表对齐 | 修读入后重跑并记录被改行数；字符列不得直接进模型 |
| 2 不可能值 | 年龄>120、BMI<10 或>60、血压<50、日期倒挂、实验室值 0 | 越界计数为 0 或每个都有来源确认 | 列清单回问来源；0 值按缺失码处理，不 log、不代入 |
| 3 缺失模式 | 每变量缺失率、共缺失簇、机制（MCAR/MAR/MNAR） | 缺失率表齐全，机制有文字判断与依据 | >40% 的变量不进主分析；机制不明加敏感性分析 |
| 4 事件数与 EPV | 事件数 / 参数个数（分类按哑变量计） | EPV≥10，或已用 Firth/减变量/合并分类补救 | EPV<10 不许把该模型 P 值写进论文，只作探索并标注 |
| 5 参数与性能 | 系数个数是否数百、AUC 是否 0.5–1、C-index 是否>0.95、R² 是否为负 | 全部落在合理区间 | C-index>0.95 先查泄漏（拆分前标准化、验证集选参、结局当特征） |
| 6 方向核对 | 暴露—结局方向是否合临床常识，OR/HR 是否方向反 | 方向一致或已查明编码原因 | 第一件事查编码（0/1 反向、参照组选错），不是讨论结论 |

> 闸门 5、6 建模后才判：顺序固定「闸门 1–4 → 建模 → 闸门 5–6 → 结果段」，无留痕视为没做。

### 4.2 红线（踩到就退回重做，不解释）

1. **不过闸门出 P 值**：闸门记录缺失，或 EPV<10 仍写「差异有统计学意义」。
2. **先筛后分**：用全量数据选变量、调超参、算均值方差，再做拆分或交叉验证。
3. **只报 P 不报效应量**：OR/HR/β/d 与 95%CI 必须同句出现。
4. **裸权重**：PS/抽样权重直接进 `glm(weights=)`/`coxph(weights=)`，或 NHANES 用 `lm`/`mean`/`t.test`。
5. **P 值判平衡**：PSM/IPTW 后不说 |SMD|<0.1 与 Love plot，只说「两组均衡（P>0.05）」。
6. **1−KM 冒充竞争风险**：有竞争事件仍用 1−KM 报累积发生率（实测可高估 70%+），或对竞争风险用普通 timeROC。
7. **PH 不检验**：Cox 不跑 `cox.zph`，或违反后删变量掩盖。
8. **MR 方向不核**：不查 `harmonise` 剔除与等位基因方向就报 IVW（β 全反但 P/SE 不变）。
9. **Meta 混口径**：不同分母定义/部位/量表直接混池；k<3 强行合并；缺失=0 与成对删除不判定。
10. **插补后手工平均**：`with(mids)` 后不 `pool()`；或 m=3、method 未显式传入。
11. **事后效能**：用观测到的效应量反算 power 当结论（应报能检出的最小效应量）。
12. **无声明因果**：观察性数据直接写「A 导致 B」，或 MR 只报 IVW 不报三假设与多效性。

### 4.3 冲突裁决顺序

1. **研究设计 > 统计方法**：设计（RCT/队列/横断面/复杂抽样）决定方法族，不为跑得通改设计口径。
2. **目的 > 变量可得性**：预测保「先分后选+校准」，关联保混杂先验，因果保 DAG 与阳性对照；冲突时以用户声明的目的为准并写代价。
3. **主分析 > 敏感性分析**：主分析限定预设的单一口径，其它口径进敏感性表，不在主表混。
4. **可解释 > 高区分度**：AUC 只高 0.01 而校准更差、变量更多时选简单模型；模型比较必须 DeLong+多重校正后才说「更好」。
5. **完整报告 > 显著性**：全部计划分析（含阴性）都要报，阴性只能解释不能删。
6. **可复现 > 本机跑通**：宁可选依赖少、参数少的写法，不写依赖某台机器路径或某包版本的代码。

## 五、模板与校验

### 5.1 R 分析脚本骨架（可直接跑）

覆盖「读数据→闸门 1–4→基线表→回归/生存→闸门 5/6→三格式出图→留痕」。改配置区即可；缺包只提示不中断。

```r
# ===== 0. 配置区（只改这里）=====
cfg <- list(data_file="data/raw.csv", out_dir="out", outcome="event",
            time=NULL, exposure="ldl", group="sex",
            covariates=c("age","sex","bmi","sbp"), seed=20261104)
dir.create(file.path(cfg$out_dir,"figures"), recursive=TRUE, showWarnings=FALSE)
set.seed(cfg$seed)   # 调用前清空 LC_ALL/LANG/LANGUAGE；脚本存为 UTF-8 无 BOM

# ===== 1. 依赖（缺包只提示）=====
for (p in c("survival","pROC","rms","tableone","ggplot2"))
  if (!requireNamespace(p, quietly=TRUE)) message("缺包：", p)

# ===== 2. 读数据 =====
d <- read.csv(cfg$data_file, stringsAsFactors=FALSE,
              na.strings=c("","NA","NULL","-9","999","9999"))

# ===== 3. 闸门 1–4 =====
chr <- names(d)[vapply(d, is.character, logical(1))]
fix <- chr[vapply(chr, function(v) any(grepl("^[0-9,]+(\\.[0-9]+)?$", d[[v]])), logical(1))]
for (v in fix) d[[v]] <- as.numeric(gsub(",", "", d[[v]]))        # 闸门 1
lim <- list(age=c(0,120), bmi=c(10,60), sbp=c(50,300))            # 闸门 2
for (v in intersect(names(lim), names(d))) {
  n <- sum(d[[v]] < lim[[v]][1] | d[[v]] > lim[[v]][2], na.rm=TRUE)
  if (n > 0) message("闸门2：", v, " 有 ", n, " 个不可能值，回查来源")
}
miss <- data.frame(var=names(d), pct=round(100*vapply(d, function(x) mean(is.na(x)), 1), 1))
write.csv(miss, file.path(cfg$out_dir,"gate_missing.csv"), row.names=FALSE)   # 闸门 3
y <- d[[cfg$outcome]]                                              # 闸门 4
npar <- sum(vapply(d[cfg$covariates], function(x)
  if (is.character(x) || is.factor(x)) length(unique(x))-1 else 1, numeric(1)))
if (length(unique(na.omit(y))) == 2) {
  epv <- sum(y == 1, na.rm=TRUE)/npar; cat("EPV =", round(epv,1), "\n")
  if (epv < 10) stop("EPV<10：减变量/合并分类/改 Firth，不得把该模型 P 值写进论文")
}

# ===== 4. 基线表 =====
if (requireNamespace("tableone", quietly=TRUE)) {
  tab <- tableone::CreateTableOne(vars=unique(c(cfg$exposure,cfg$group,cfg$covariates)),
          strata=cfg$group, data=d, addOverall=TRUE)
  print(tab, smd=TRUE, showAllLevels=TRUE)      # SMD>0.1 的变量要在表注点名
}

# ===== 5. 建模 + 闸门 5/6 =====
rhs <- paste(c(cfg$exposure, cfg$covariates), collapse=" + ")
if (is.null(cfg$time)) {
  m <- glm(as.formula(paste(cfg$outcome, "~", rhs)), data=d, family=binomial())
  est <- exp(cbind(OR=coef(m), confint(m))); print(est)
  write.csv(est, file.path(cfg$out_dir,"model_or.csv"))
  if (requireNamespace("pROC", quietly=TRUE)) {
    r1 <- pROC::roc(d[[cfg$outcome]], fitted(m), quiet=TRUE)
    print(pROC::ci.auc(r1)); cat("AUC =", round(as.numeric(pROC::auc(r1)),3), "\n")
    if (as.numeric(pROC::auc(r1)) < 0.5) warning("AUC<0.5：先查结局编码方向")
  }
} else {
  f <- as.formula(paste0("survival::Surv(", cfg$time, ",", cfg$outcome, ") ~ ", rhs))
  m <- survival::coxph(f, data=d)
  est <- exp(cbind(HR=coef(m), confint(m))); print(est)
  write.csv(est, file.path(cfg$out_dir,"model_hr.csv"))
  print(survival::cox.zph(m))       # 任一 P<0.05 → 用 tt() 或 strata() 处置
}

# ===== 6. 出图：同图名三格式 =====
save_fig <- function(p, name, w=6, h=5) for (ext in c("svg","pdf","png"))
  ggplot2::ggsave(file.path(cfg$out_dir,"figures",paste0(name,".",ext)), p,
                  width=w, height=h, dpi=300)

# ===== 7. 留痕 =====
sink(file.path(cfg$out_dir,"sessionInfo.txt")); print(sessionInfo()); sink()
```

### 5.2 统计报告模板（双版式）

**中文期刊 · 方法段**

> 采用 R 4.4.1 完成统计分析。连续变量经 Shapiro-Wilk 检验与 Q-Q 图判断分布，正态者以 x̄±s 表示、用两独立样本 t 检验，偏态者以 M(P25, P75) 表示、用 Mann-Whitney U 检验；分类变量以 n(%) 表示，用 χ² 检验（期望频数<5 用 Fisher 精确检验）。多因素 logistic 回归报告 OR 及 95%CI，用 Hosmer-Lemeshow 检验与校准曲线评价校准度，以 P<0.05 为差异有统计学意义，多重比较用 Holm 校正；缺失数据用多重插补（m=20）并按 Rubin 规则合并。

**中文期刊 · 结果段**

> 共纳入 1 234 例，其中 312 例（25.3%）发生主要结局。两组年龄差异有统计学意义（t=2.31，P=0.023），BMI 差异无统计学意义（Z=−1.42，P=0.156）。多因素分析显示，X 每增加 1 个标准差结局风险增加 42%（HR=1.42，95%CI 1.18–1.71，P<0.001）；模型区分度 0.78（95%CI 0.74–0.82）、校准斜率 0.93、Brier 评分 0.14，比例风险假定未见违反（全局 P=0.32）。

**SCI · Statistical analysis**

> All analyses were performed with R 4.4.1 (R Foundation, Vienna). Continuous variables are presented as mean ± SD or median (IQR) and compared with the Student t test or Mann–Whitney U test; categorical variables as n (%) with the χ² or Fisher exact test. Multivariable Cox regression estimated hazard ratios (HRs) with 95% confidence intervals (CIs); proportional hazards were checked with scaled Schoenfeld residuals. Discrimination used the AUC with DeLong 95% CI; calibration used the calibration slope, intercept and Brier score. Missing data were handled by multiple imputation (m = 20) with Rubin's rules. Two-sided P < 0.05 was significant; multiplicity was controlled with the Holm method.

**SCI · Results**

> Of 1,234 participants (median age 62 [IQR 54–70]; 48.2% women), 312 (25.3%) had the primary outcome over a median follow-up of 5.2 years. After adjustment, each 1-SD increase in X was associated with a higher risk (HR 1.42, 95% CI 1.18–1.71; P < 0.001). The model achieved an AUC of 0.78 (95% CI 0.74–0.82), a calibration slope of 0.93 and a Brier score of 0.14; no violation of proportional hazards was detected (global P = 0.32).

**表注**写呈现方式与检验方法、校正方法与次数、缺失与排除例数；**图注**写样本量、图形含义（点=个体、横线=中位数）、软件与图尺寸。

### 5.3 交付前自检清单（按顺序打勾）

1. 六道闸门有记录文件，不只是一句「已检查」；2. 每个模型报事件数与参数个数，EPV≥10 或说明补救；3. 效应量+95%CI，P 三位小数（<0.001 除外）；4. 量纲写明（每单位/每 IQR/每 SD）；5. 多重校正方法与比较次数齐；6. 拆分代码在筛变量与标准化之前；7. `cox.zph` 有结果与处置，竞争风险未用 1−KM；8. |SMD|+Love plot+ESS+E-value 齐，未用 P 值判平衡；9. 复杂抽样全程 `svy` 并写权重来源/周期数；10. MR 方向核对/三假设/Egger/MR-PRESSO/Steiger/重叠齐；11. Meta 有 k 判定/I²/τ²/口径分层/k<10 时 HKSJ；12. 脚本无 BOM 可重跑，图三格式、表 DOCX/XLSX 齐。

## 六、交付物

```text
<项目>/
├─ data/raw/        原始数据（只读，永不覆盖）
├─ data/clean/      清洗后数据 + 衍生变量表 + 数据字典
├─ scripts/         00_gates.R 01_baseline.R 02_model.R 03_figures.R 04_report.R
├─ out/tables/      DOCX 三线表 + XLSX（含 SMD、缺失列）
├─ out/figures/     同名 .svg/.pdf/.png，dpi=300
├─ out/logs/        闸门记录、清洗日志、sessionInfo、run_meta
└─ out/report/      统计报告 DOCX + 方法/结果段 Markdown
```

文件命名：`<日期>_<分析类型>_<核心变量>_v<N>`，如 `20261104_cox_ldl_v2.csv`。交付必须齐三样：**可重跑的脚本**、**结果表与图**、**方法与结果段落草稿**。

## 七、来源索引

| 能力 | 主用技能 → 原文路径（相对包根） | 补强 / 兜底 |
| --- | --- | --- |
| stats.baseline | r-medical-stats → knowledge/skills/stats/r-medical-stats.md | r-aging-cohort-databases、exploratory-data-analysis |
| stats.twogroup | r-medical-stats → knowledge/skills/stats/r-medical-stats.md | statistical-analysis |
| stats.multigroup | r-medical-stats → knowledge/skills/stats/r-medical-stats.md | statistical-analysis、r-trajectory-models |
| stats.regression | r-medical-stats → knowledge/skills/stats/r-medical-stats.md | r-medical-research-master |
| stats.survival | r-medical-stats → knowledge/skills/stats/r-medical-stats.md | r-clinical-prediction-model、scikit-survival |
| stats.prediction | r-clinical-prediction-model → knowledge/skills/stats/r-clinical-prediction-model.md | r-medical-stats |
| stats.interpret | r-machine-learning-interpretability → knowledge/skills/stats/r-machine-learning-interpretability.md | shap、r-medical-stats |
| stats.psm | r-real-world-evidence → knowledge/skills/stats/r-real-world-evidence.md | r-propensity-score-methods、scholar-causal |
| stats.diagnostic | r-medical-stats → knowledge/skills/stats/r-medical-stats.md | r-clinical-prediction-model |
| stats.meta | ima-lit-meta-ppt → knowledge/skills/slides/ima-lit-meta-ppt.md | r-medical-stats、statistical-analysis |
| stats.mr | r-mendelian-randomization → knowledge/skills/stats/r-mendelian-randomization.md | r-pharmacology-singlecell-mr |
| stats.survey | r-nhanes-analysis → knowledge/skills/stats/r-nhanes-analysis.md | r-real-world-evidence |
| stats.missing | r-aging-cohort-databases → knowledge/skills/stats/r-aging-cohort-databases.md | r-clinical-prediction-model |
| stats.power | r-medical-stats → knowledge/skills/stats/r-medical-stats.md | statistical-analysis、r-medical-research-master |
| stats.corr | r-medical-stats → knowledge/skills/stats/r-medical-stats.md | statistical-analysis |
| stats.clean | r-medical-stats → knowledge/skills/stats/r-medical-stats.md | r-clinical-prediction-model、scholar-code-review |

**降级与弃用**：`statsmodels`、`scikit-learn`、`scikit-survival` 只作无 R 时兜底并注明非 R 路线；`shap` 仅作 Python 侧对照；`exploratory-data-analysis` 只出分布图与离群点核查，不改数据；`local-r-clinical-stats` 是运行通道（清 locale、无 BOM 脚本、重定向日志）而非方法来源；chinese-medical-paper-writer、sci-writing-master 只提供报告句式，统计结论不由它们产生。
