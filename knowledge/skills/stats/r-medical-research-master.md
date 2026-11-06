---
name: r-medical-research-master
description: R 语言医学统计与科研全流程总纲技能（九大领域一体化总入口）。当用户提出任何医学统计、临床科研数据分析、论文图表制作、科研绘图、统计方法选择、代码排错需求时，先加载本技能以定位应调用的子技能：临床预测模型 / 机器学习与可解释性 / 孟德尔随机化 / 七大老年数据库 / 倾向得分方法 / 网络药理学与单细胞 / 真实世界研究 / 纵向轨迹模型 / NHANES 数据挖掘。本技能还提供跨域通用的「数据质量六道闸门」「四个域的静默陷阱清单」「报告规范对照表（TRIPOD/PROBAST、STROBE-MR、GRoLTS、STROBE）」「统计方法选择决策树」「本机 R 环境调用配方」。触发场景：不确定该用哪个统计方法、拿到数据不知从何下手、要复核一项分析是否可靠、要写 Methods 或 Statistical Analysis 章节、或给出任意 R 代码要求运行调试。
agent_created: true
---

# R 语言医学统计 · 九域总纲

> ★★ **执行入口**：本技能负责**知识路由与自查**；**具体计算、出图、出表请用 `r-medical-stats`（双模式统计引擎）**。
> - 有 R 环境 → `r-medical-stats` 模式 A：直接执行并交付 SVG/PDF/PNG 图 + DOCX/XLSX 表
> - 无 R 环境（如 ima）→ `r-medical-stats` 模式 B：生成可直接运行的完整 R 脚本 + 运行说明
> - 需要「这个研究该用什么方法、容易踩什么坑」→ 继续看本技能的下方子技能路由表

## 一、子技能路由表（先定位，再执行）

| 用户需求 | 调用技能 | 覆盖内容 |
|---|---|---|
| **任何"用 R 做统计/画图/出表"的执行任务；不确定有没有 R 环境** | **`r-medical-stats`**（★ 执行引擎） | 双模式（直接执行 / 生成代码）+ **SVG 可编辑投稿级出图** + DOCX/XLSX 表 + 六道闸门 |
| 诊断/预后预测模型、列线图、ROC、校准、NRI/IDI、DCA、C-index、PH 假设、竞争风险 | **`r-clinical-prediction-model`** | Logistic/Cox 全流程 + TRIPOD/PROBAST |
| 二分类/生存多模型比较、SHAP 可解释性、ML 与 Logistic 的增量价值 | **`r-machine-learning-interpretability`** | 8 二分类 + 6 生存模型 + KernelSHAP |
| 孟德尔随机化、因果推断、工具变量、GWAS 汇总数据、共定位 | **`r-mendelian-randomization`** | 两样本/多变量/中介/药靶 MR + STROBE-MR |
| CHARLS/HRS/ELSA/SHARE 等老年队列、环境暴露、衰弱/认知、多重插补 | **`r-aging-cohort-databases`** | Harmonized 数据 + 8 模块分析流程 |
| 倾向得分匹配、IPTW、观察性研究的混杂控制 | **`r-propensity-score-methods`** | PSM/分层/加权/回归四法 + 反事实框架 |
| 网络药理学、成分-靶点、KEGG/GO 富集、单细胞测序、单细胞 eQTL MR | **`r-pharmacology-singlecell-mr`** | 富集 + Seurat + sc-eQTL MR |
| 真实世界研究、时依治疗、重叠加权、E-value | **`r-real-world-evidence`** | CCW + Overlap Weighting + E-value |
| 潜类别轨迹、GBTM/LCGM/GBMTM、重复测量异质性 | **`r-trajectory-models`** | 四项指标 + gridsearch + GRoLTS |
| NHANES、复杂抽样加权、加权 RCS、检出限处理 | **`r-nhanes-analysis`** | svy 系列 + 加权 RCS 自写实现 |
| 本机 R 环境调用、locale 问题、包安装 | **`local-r-clinical-stats`** | R 4.5.2 调用配方 |
| 论文撰写与润色 | **`chinese-medical-paper-writer`**（中文）/ **`sci-writing-master`**（英文） | — |

---

## 二、★★★ 数据质量六道闸门（任何分析开始前必跑）

从九个域的真实数据中提炼。**这六道闸门能拦住本仓 90% 的致命错误。**

```r
## 闸门 1：列类型核查（拦"千分位逗号污染"）
expect_num <- c("age","size","bmi","glucose","cr","alt","ast","ca199")   # 按项目改
bad <- expect_num[sapply(expect_num, function(v) v %in% names(d) && !is.numeric(d[[v]]))]
if (length(bad)) stop("本应数值却读成字符/因子，检查千分位逗号或空值: ", paste(bad, collapse=", "))

## 闸门 2：不可能值扫描（拦"0 值实为缺失码"）
sapply(d[sapply(d, is.numeric)], function(v) sum(v == 0, na.rm = TRUE))

## 闸门 3：缺失率与缺失模式
sapply(d, function(x) round(mean(is.na(x))*100, 2))
mice::md.pattern(d)

## 闸门 4：事件数与 EPV（预测模型专用）
n_ev  <- sum(d$outcome == 1)
n_par <- length(predictors) + sum(sapply(cat_vars, function(v) length(unique(d[[v]]))-1))
cat("EPV =", round(n_ev/n_par, 1), ifelse(n_ev/n_par < 10, " ✗ 低于 10", " ✓"))

## 闸门 5：参数个数与性能合理性（拦"因子误用"、"数据泄漏"）
cat("模型参数个数 =", length(coef(model)), "\n")   # 达数百 → 必有因子被误用
cat("C-index =", round(C,3), "\n")                  # >0.95 先怀疑数据泄漏/变量误编码

## 闸门 6：方向核对（拦"等位基因方向反转"等符号错误）
## 结果必须与既往文献/临床常识方向一致，否则先查编码，再讨论结论
```

---

## 三、★★★ 各域的"静默陷阱"清单（共同特征：都不报错）

| 域 | 静默陷阱 | 后果 | 专属闸门 |
|---|---|---|---|
| **预测模型** | 千分位逗号污染（`"1,240.00"` → 整列变字符 → 高基数因子） | C-index 虚高到 **0.97**、AIC 膨胀 10 倍 | C-index > 0.95 → 查数据 |
| | 0 值实为缺失码 | `log(0) = -Inf` → `shapiro.test` 返回 NaN | 闸门 2 |
| | `rms::rcorrcens()` 的 `C` 列 = **1−C-index** | 直接报出去即严重错误 | 用 `(1+\|Dxy\|)/2` |
| | `validate()` 内联 `predict()` | Bootstrap 校正失效（optimism=0） | 直接喂 cph 对象 |
| **机器学习** | 先全量 `scale()` 再拆分 | 数据泄漏（实测 ΔAUC 0.0004，方向必然乐观） | 拆分后才标准化 |
| | 用**训练集** AUC 选超参数 | 选中训练 AUC=**1.0000** 的完美过拟合模型 | 查训练/验证落差 |
| | `ci.auc(auc值)` 传数值而非 roc 对象 | **15 处** AUC 的 95%CI 全部无效 | 传 roc 对象 |
| **孟德尔随机化** | **等位基因方向写反** | **beta 符号整体反转，SE/P/Q/SNP 数全部不变，零报警** | **先核对方向与文献一致** |
| | 部分 SNP 方向错误 | 向零衰减 + 最终失去显著性（50% 错误 → P 从 3.6e-25 变 0.074） | 回文 SNP 用 EAF 匹配 |
| | `NbDistribution=1000` | MR-PRESSO 的 P 值不稳定（1000 vs 5000 → 差 5 倍） | ≥5000 |
| **倾向得分** | `glm/coxph(weights=)` 当抽样权重用 | **CI 过窄、假阳性** | 必须 `svyglm`/`svycoxph` |
| | KM 图 P 值与 HR **硬编码字符串** | 匹配后图上仍显示匹配前的 HR | 动态生成 |
| **七大老年数据库** | 离散随访波次当连续时间用 Cox | 大量 ties，风险集定义不符前提 | 改 cloglog 离散时间模型 |
| | 定义了 `meth` 却没传给 `mice()` | 自定义插补方法**完全失效** | `method = meth` |
| | RCS 图 P for nonlinear **硬编码文本** | 换数据后图上 P 值是错的 | 从 `anova()` 动态取 |
| **真实世界** | `glm/coxph(weights=)` | 同倾向得分 | survey 设计 |
| | CCW 的 `NA > 365` → 传播 NA | `censored` 出现 NA，污染全部逻辑 | `!is.na(...)` 显式处理 |
| | 重复 `read.csv()` 覆盖填补结果 | 后续分析用的其实是**未填补**数据 | 只读一次 |
| **NHANES** | 用 `mean/t.test/lm` 代替 `svy` 系列 | 估计有偏、CI 过窄 | 只用 svy 系列 |
| | 未设 `options(survey.lonely.psu="adjust")` | 单 PSU 层导致分析**失败** | 必设 |
| | 多周期合并权重未除周期数 | 权重放大 K 倍 | `wt/K` |
| | 量表条目重叠（研究睡眠→抑郁时 PHQ-9 睡眠题仍计入总分） | 夸大关联 | 逐条核对 |
| **轨迹模型** | 比较不同组数时多项式阶次不一致 | AIC/BIC **不可比**，模型选择无效 | 统一 `d` |
| | `lcmm` 不用 `gridsearch` | 收敛到局部最优，类别解不可信 | 多随机起点 |

> **共同教训**：**"能跑出结果" ≠ "结果正确"**。
> 每个域都必须建立该域特有的"合理性闸门"——不依赖软件报错，而依赖**量级与方向的常识判断**。

---

## 四、统计方法选择决策树

```
Q1 结局类型？
├── 连续 → 线性回归（svyglm(gaussian) / lm）→ 剂量反应用 RCS
├── 二分类 → Logistic（或 quasibinomial 加权时）→ ROC/校准/DCA/NRI/IDI
├── 生存（时间+状态）→ Cox / psm / RSF / GBM
│   ├── PH 违反？→ 时依系数 tt() / 分层 strat() / psm
│   ├── 有竞争事件？→ Fine-Gray (crss) / cause-specific；★ 用 cuminc 不要用 1−KM
│   └── 随访为离散波次？→ cloglog 离散时间模型
├── 计数 → Poisson / 负二项
└── 重复测量 / 多次随访 → 混合效应模型 / GEE / 轨迹模型（GBTM/LCGM/GBMTM）

Q2 研究目的？
├── 预测 → 预测模型技能（TRIPOD + 区分度 + 校准度 + DCA + 外部验证）
├── 因果（观察性）→ 倾向得分 / IPTW / CCW / 双重稳健估计 + E-value
├── 因果（遗传工具变量）→ 孟德尔随机化（STROBE-MR）
├── 中介 → 观察性：CMAverse/mediation；遗传：MVMR 框架 > 两步法
└── 关联/描述 → 多模型策略（未调整→部分调整→完全调整）

Q3 数据来源？
├── 复杂抽样（NHANES/CHARLS）→ 加权设计 svydesign + svy 系列
├── 公共 GWAS 汇总数据 → MR 技能（注意等位基因方向）
├── 单细胞 → Seurat；细胞类型特异 eQTL → sc-eQTL MR
└── 常规临床数据库 → 注意离散时间、缺失编码、隐私脱敏

Q4 是否存在以下威胁？（决定必须做哪些敏感性分析）
├── 未测量混杂 → E-value（观察性）/ MR（遗传工具变量）
├── 时依混杂 → CCW（克隆删失加权）
├── 缺失数据 → MICE（MAR）/ 模式混合模型（MNAR）+ 敏感性分析
├── 多重比较 → Holm / FDR 校正
├── 多重共线性 → VIF
├── 过拟合 → Bootstrap / 交叉验证 校正
└── 数据泄漏 → 拆分后标准化 + 训练/验证落差检查
```

---

## 五、报告规范对照表（投稿前逐项打勾）

| 研究类型 | 报告规范 | 载于 |
|---|---|---|
| 预测模型开发/验证 | **TRIPOD** + **PROBAST**（偏倚风险自评） | `r-clinical-prediction-model` |
| 孟德尔随机化 | **STROBE-MR** + MR 统计学共识 | `r-mendelian-randomization` |
| 轨迹模型 | **GRoLTS Checklist** | `r-trajectory-models` |
| 观察性研究（PS/IPTW/RWE） | **STROBE** + E-value | `r-propensity-score-methods` / `r-real-world-evidence` |
| NHANES / 复杂抽样 | STROBE + 抽样权重报告要求 | `r-nhanes-analysis` |
| 机器学习 | 借用 TRIPOD + 报校准/SHAP | `r-machine-learning-interpretability` |

**TRIPOD 关键条目**：设计/数据来源 · 纳排 · 结局定义 · 预测因子定义与测量时点 · 样本量与 EPV · 缺失处理 ·
建模方法 · 变量选择 · 区分度 · **校准度** · 临床效用 · 内部验证 · **外部验证** · 模型呈现 · 局限性

**STROBE-MR 关键条目**：三假设逐项说明 · 数据来源与样本重叠 · 工具变量选择（p 阈值/clump/F 值） ·
等位基因协调与被剔除 SNP · 主分析 + 敏感性分析 · **Steiger 方向性** · 多效性四检验 · 弱工具讨论 · 局限性

---

## 六、本机 R 环境调用配方（Windows）

```powershell
Remove-Item Env:LC_ALL  -ErrorAction SilentlyContinue
Remove-Item Env:LANG    -ErrorAction SilentlyContinue
Remove-Item Env:LANGUAGE -ErrorAction SilentlyContinue
& "D:\软件安装\R-4.5.2\bin\Rscript.exe" "脚本.R"
```
**三条要点**
1. **必须先清除 `LC_ALL`/`LANG`/`LANGUAGE`**（POSIX locale 会让 Windows 版 R 加载包失败、中文路径失效）
2. **脚本用 Write 工具生成**（无 BOM UTF-8）；PowerShell 的 `Out-File -Encoding UTF8` 带 BOM → R 报 `unexpected input in "锘"`
3. **输出重定向到 UTF-8 文件再读回**（控制台回显中文会乱码）：
   ```r
   con <- file("out.txt", open="wt", encoding="UTF-8")
   sink(con); sink(con, type="message"); ... ; sink(type="message"); sink(); close(con)
   ```
4. **长任务串行执行**（并发跑两个 R 进程写同一 sink 文件会互相拖慢：实测单脚本 1h39m 未收敛，串行后 35 秒）

**已验证可用包**（本机 436+）：rms、survival、Hmisc、pROC、ResourceSelection、survivalROC、timeROC、nricens、
nomogramEx、regplot、glmnet、caret、mice、nnet、randomForest、xgboost、lightgbm、kknn、neuralnet、rpart、
partykit、missForest、kernelshap、shapviz、rmda、dcurves、riskRegression、pec、cmprsk、randomForestSRC、
CoxBoost、survivalsvm、gbm、gbmt、lcmm、survey、tableone、compareGroups、cobalt、WeightIt、PSweight、
forestploter、jstable、clusterProfiler、org.Hs.eg.db、Seurat、EValue、coloc、MendelianRandomization、ieugwasr

**已从 CRAN 归档（不可直接安装）**：`TwoSampleMR`、`MVMR`、`RadialMR`、`PredictABEL`、`DMwR`
→ **替代方案**：① 用 GitHub（`remotes::install_github("MRCIEU/TwoSampleMR")`，需 Rtools）；
② **从第一性原理手写**（本仓 `H2_mr_manual.R` 已实现 IVW/MR-Egger/加权中位数/众数/Q/MR-PRESSO/留一法/Steiger）

---

## 七、九域交叉关系图

```
                     ┌─────────────────────────────┐
                     │  因果推断（三个层次）          │
                     │  · 随机化/RCT（设计）          │
                     │  · 倾向得分/IPTW/CCW（观察性） │
                     │  · 孟德尔随机化（遗传工具变量） │
                     └──────────┬──────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
   预测 vs 因果            混杂控制技术              中介分析
        │                       │                       │
┌───────▼──────┐    ┌──────────▼─────────┐   ┌─────────▼─────────┐
│ 预测模型      │    │ 倾向得分方法        │   │ 观察性：CMAverse   │
│ 机器学习      │◄───│ 真实世界研究(CCW)   │   │ 遗传：MVMR 框架    │
│ 轨迹模型      │    │ (共享 svydesign)    │   │ (优于两步法)       │
└───────┬──────┘    └──────────┬─────────┘   └───────────────────┘
        │                      │
        │            ┌─────────▼──────────┐
        │            │ 公共数据库挖掘       │
        └───────────►│ · NHANES（加权）    │
                     │ · 七大老年数据库     │
                     │   （Harmonized）     │
                     └─────────┬──────────┘
                               │
                     ┌─────────▼──────────┐
                     │ 组学与分子机制       │
                     │ · 网络药理学（富集） │
                     │ · 单细胞 + sc-eQTL MR│
                     └────────────────────┘
```

**技术栈的共同底座**：`survival`（生存分析）· `survey`（加权）· `rms`（列线图/RCS）· `ggplot2`（绘图）·
`mice`（缺失）· `caret`/`glmnet`（机器学习）—— **九个域共享同一套底层工具，只是组合方式不同。**

---

## 八、使用本总纲的方式

1. **收到需求 → 查 §1 路由表定位子技能** → 加载对应子技能执行
2. **任何分析开始前 → 跑 §2 六道闸门**
3. **分析结束前 → 对照 §3 该域的静默陷阱清单逐条自查**
4. **写 Methods/Statistical Analysis → 查 §4 决策树确认方法选择理由**
5. **投稿前 → 查 §5 对照该研究类型的报告规范逐项打勾**

> **本总纲的定位**：不是替代子技能，而是**在子技能之前提供"该找谁"与"该防什么"的两层导航**。
> 九个域的知识量太大，直接记忆不可行；**先定位、再执行、后自查**，是可持续的工作方式。
