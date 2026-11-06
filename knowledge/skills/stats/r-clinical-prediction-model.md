---
name: r-clinical-prediction-model
description: 临床预测模型（诊断模型 / 预后模型）R 语言全流程实战技能。覆盖：数据质量核查（含"0 值实为缺失码"陷阱）、建模人群与验证人群拆分、单因素/多因素变量筛选（含 Lasso）、Logistic 与 Cox 建模、列线图（诊断概率 / 中位生存时间 / 1-3-5 年生存率 / 动态交互式 / 反推评分公式）、区分度（AUC、C-index、时间依赖 ROC、DeLong 检验）、校准度（val.prob、calibrate、H-L 检验、校准斜率/截距）、NRI 与 IDI（含生存资料手工实现）、DCA 决策曲线（诊断版与生存版）、KM 曲线与 log-rank、PH 假设检验、TRIPOD/PROBAST 报告规范，以及 7 篇顶刊范文的写作范式与 40+ 条避坑清单。触发场景：用户要做/复现/审阅临床预测模型、风险评分、列线图、nomogram、ROC/AUC、校准曲线、NRI/IDI/DCA、C-index、竞争性风险之外的预后建模、以及"预测模型"相关论文的数据分析部分；或用户给出预测模型相关的 R 代码/数据要求代为运行、调试、纠错。
agent_created: true
---

# 临床预测模型 · R 全流程实战技能

## 何时用

- 用户要**建**预测模型（诊断 or 预后）、**复现**已发表模型、**审阅**预测模型论文的方法学
- 涉及关键词：临床预测模型、risk prediction model、nomogram / 列线图、风险评分 / risk score、
  ROC / AUC / c-statistic / C-index、calibration / 校准曲线 / H-L 检验、
  NRI / IDI / 净重新分类 / 综合判别改善、DCA / 决策曲线 / net benefit、
  内部验证 / 外部验证 / Bootstrap / 交叉验证、TRIPOD / PROBAST、EPV
- 用户给出预测模型相关的 `.R` / `.csv` / `.sav` 要求代为运行、修改、排错

## 三条铁律（先读）

1. **先做数据质量闸门，再建模。** 缺失率、**列类型核查**、0 值嫌疑、极端值、事件数、EPV 六道检查。
   本领域两个最高频的致命错误都**不报错**：
   ① **千分位逗号污染** —— `read.csv` 遇到 `"1,240.00"` 或空串会把整列读成字符型，
      建模时按因子处理生成数百个哑变量，C-index 虚高到 0.97（本域 PDAC 数据实测）；
   ② **0 值实为缺失码** —— 直接取对数得到 `-Inf`，导致 `shapiro.test` 返回 `NaN`。
2. **诊断模型用 Logistic，预后模型用 Cox。** 结局在「当下」→ 诊断；结局在「未来」→ 预后。
   预后模型必须有时间维度，且**时间单位必须常量化**（月→12/36/60，天→365/1095/1825）。
3. **区分度 ≠ 校准度，两者都要报。** 一个 AUC 0.87 的模型完全可能校准失败。
   本技能在真实数据上实证过：区分度最好的模型（AUC 0.865），其外部验证校准斜率最差（0.776）。

## 标准工作流（10 步）

```
0. 配置区：数据路径 / 结局名 / 时间与状态名 / 时间单位 / 预测因子 / 分类变量与参照组 / 评价时点
1. 数据读入 + 质量核查（缺失率表、0 值扫描、极端值、事件数、EPV）
2. 变量类型规范化（因子化、relevel 必须赋值回去、偏态变量对数转换）
3. 拆分（★ 按结局分层，不是按 id）
4. 变量筛选（单因素 P<0.2/0.1 → 多因素；或逐步回归 AIC；或 Lasso）
5. 建模（诊断 lrm / 预后 cph，均需 x=TRUE, y=TRUE；cph 还需 surv=TRUE）
6. 列线图（诊断概率 / 中位生存时间 / 1-3-5 年生存率 / 动态 regplot / 反推评分公式）
7. 区分度（AUC + 95%CI、C-index、时间依赖 ROC、DeLong 检验、ΔAUC）
8. 校准度（val.prob / calibrate + 校准斜率截距 + H-L / GiViTI）
9. 增量价值（NRI + IDI + AIC/BIC）
10. 临床效用（DCA 净收益）+ 风险分层（KM + log-rank）+ 外部验证
```

完整可运行骨架见 `assets/clinical_prediction_model.R`（诊断/预后双模式一体化，含全部 10 步）。

## 关键函数速查

| 需求 | 函数 | 要点 |
|---|---|---|
| Logistic 建模 | `rms::lrm(y ~ x, data, x=TRUE, y=TRUE)` | 列线图必须用 lrm，不能用 glm |
| Cox 建模 | `rms::cph(Surv(t,s) ~ x, data, surv=TRUE, x=TRUE, y=TRUE)` | 三参数缺一不可 |
| 数据打包 | `dd <- datadist(d); options(datadist="dd")` | lrm/cph/nomogram/calibrate 前置条件 |
| 列线图 | `nomogram(fit, fun=..., fun.at=..., funlabel=..., lp=FALSE)` | 诊断用反 logit；预后用 `Survival()` / `Quantile()` |
| 动态列线图 | `regplot(glm对象, observation=d[i,])` | 必须 glm 对象 |
| 反推评分 | `nomogramEx(nomo=nom, np=2, digit=9)` | 或本技能的自写归一化函数（更稳健） |
| ROC / AUC | `pROC::roc()` + `ci.auc()` + `roc.test()` | `roc.test` 即 DeLong 检验 |
| C-index | `summary(coxph)$concordance[1]` | ★ 不要用 `rcorrcens()` 的 C 列（那是 1−C） |
| 校准图（诊断） | `rms::val.prob(p, y)` | 输出含 Intercept / Slope / Brier / Emax |
| 校准图（预后） | `rms::calibrate(fit, cmethod="KM", method="boot", u=, m=, B=)` | `u` 与 `time.inc` 一致，`m` 是分组目标例数 |
| H-L 检验 | `ResourceSelection::hoslem.test(y, p, g=10)` | df = g−2；课程 `hl.ext2` 用 df = g−1 |
| 时间依赖 ROC | `timeROC::timeROC(..., iid=TRUE)` | ★ `$AUC[1]` 是占位值，第一个时点在下标 2 |
| 时间依赖 ROC（无模型） | `survivalROC::survivalROC(Stime, status, marker, predict.time, method="KM")` | ★ 不给 CI，需 Bootstrap |
| NRI（诊断） | `nricens::nribin(mdl.std, mdl.new, updown, cut, niter, alpha)` | 模型须 `glm(..., x=TRUE)` |
| NRI（预后） | `nricens::nricens(mdl.std, mdl.new, t0, updown, cut, niter)` | ★ 用 coxph 不用 cph；不加 surv=TRUE |
| IDI（诊断） | `PredictABEL::reclassification()` 或手工实现 | PredictABEL 已下架，优先手工 |
| IDI（预后） | 手工实现（survfit 求风险 → 病例/非病例均值差 → Z 检验） | 生存资料无现成包 |
| DCA（诊断） | `dcurves::dca()` / `rmda::decision_curve()` / 课程 `dca.r` | 净收益 = TP/N − FP/N × Pt/(1−Pt) |
| DCA（预后） | `stdca()`（生存版）/ `dcurves::dca(Surv~, time=)` | 事件率由 KM 估计 |
| KM + log-rank | `survfit()` + `survdiff(rho=0)` | 切点取整后须重验分组差异 |
| PH 假设 | `cox.zph(coxph_model, transform="rank", global=F)` | ★ 违反则分层 / 时依系数 / psm / 明说局限 |
| **PH 违反·分层** | `cph(..., + strat(var))` / `coxph(..., + strata(var))` | ★ rms 用 `strat()`、survival 用 `strata()`，两包不通用；**分层变量本身失去 HR，且分层越多 C-index 越低**（实测 0.808→0.735→0.595） |
| **PH 违反·时依系数** | `coxph(Surv(t,s) ~ x + tt(x), tt=function(x,t,...) x*log(t), x=TRUE, y=TRUE)` | ★ `tt()` **必须传数值型变量**，传因子报 `infinite predictor`；输出 β₀+β₁·log t 后可算分时段 HR |
| **PH 违反·参数模型** | `psm(Surv~..., dist="weibull"\|"loglogistic"\|"lognormal", data, x=TRUE, y=TRUE)` | ★ **无 `surv=` 参数**；★ Cox 偏似然 vs psm 全似然 → **AIC 跨族不可比**；支持 nomogram/calibrate/validate |
| **竞争风险·CIF** | `cmprsk::cuminc(time, status, group)` | ★ 1−KM 会**高估**累积发生率（实测 t=8 时高估 71%） |
| **竞争风险·Fine-Gray** | `cmprsk::crr(time, status, cov1, failcode, cencode)` | sHR 与病因别 HR 回答不同问题（实测 1.59 vs 2.52，差 58%） |
| **竞争风险·评价** | `riskRegression::CSC` + `Score(cause=1)` | ★ 有竞争风险时**不能用普通 timeROC** |
| 多重插补 | `mice(d, m=10, maxit=10, seed=500)` + `with()` + `pool()` | ★ 模型评价须**逐插补集算再合并**，不能先取一个完整集 |
| Lasso | `glmnet(x, y, family="binomial"|"cox")` + `cv.glmnet` | ★ x 必须先 `model.matrix` 转哑变量；y 不能因子化 |
| 缺失数据 | `mice(d, m=10, maxit=10, seed=500)` + `pool()` | 按变量类型选填补模型 |

## 高频陷阱（40+ 条完整版见 `references/避坑清单.md`）

**数据层**
- **★★★ 千分位逗号污染**：`read.csv` 遇到 `"1,240.00"` 或空串会把**整列读成字符型**，建模时按因子处理 → 生成数百个哑变量 → **C-index 虚高到 0.97、AIC 膨胀 10 倍，且完全不报错**。本域实测：`PDACdata.csv` 的 ALT/AST/CA199/id 均被污染。
- 0 值实为缺失码 → 取对数得 -Inf（实证：uPCX / UBMG / UNAG / BMI / TC 都存在）
- 因子标签与原始编码错位（如 `LN.dissection` 标签顺序反了 → 全篇结论方向颠倒）
- 时间单位不统一（同一课程内出现月/天三种单位混用）
- 验证集与建模集不同质（实证：事件率 22.2% vs 12.7%）
- **训练集干净、验证集脏**（实测：`Mean_CT_value_of_calculi` 只在验证集被污染）

**建模层**
- **PH 假设只打印不处理**（实证：7 个因子中 4 个违反，P<0.05）
- **`rcorrcens()` 输出的 C 列 = 1−C-index**（实证：C列 0.192 → 真 C 0.808）
- **`validate()` / `calibrate()` 中用 `predict(m, newdata=d)` 内联 → Bootstrap 失效**（optimism = 0）
- **`step()` 作用于 `cph(surv=TRUE)` → 每步重算生存曲线，实测 >30 min 不收敛**（改用 coxph）
- `relevel()` 不赋值回原变量 → 参照组设置无效
- `glmnet` 直接吃因子列 → 因子被当整数编码，隐含等距线性假设
- `createDataPartition(y = id)` → 丧失按结局分层功能
- H-L 检验排序实现错误（先改 p 再 `order(p)` → 观测与期望错配，卡方荒谬地巨大）
- `survfit()$surv` 是生存率，风险 = `1 − surv`（方向搞反 IDI/DCA 符号全错）
- 变量名与内容相反（把死亡率命名为 `...Survival.Probability`）
- **两套「PI」尺度不可混用**：评分型（0–100 分刻度）vs 模型型 lp（log-hazard 刻度）

**必做的 3 道防御性自检**
```r
# ① 类型闸门：本应数值却读成字符/因子 → 立即停止
bad <- expect_num[sapply(expect_num, function(v) v %in% names(d) && !is.numeric(d[[v]]))]
if (length(bad)) stop("这些列类型不对，检查千分位逗号/空值: ", paste(bad, collapse=", "))
# ② 参数个数闸门：参数数 ≈ 因子数×水平数；达数百即为误用
cat("模型参数个数 =", length(coef(model)), "\n")
# ③ 性能合理性闸门：C-index > 0.95 先怀疑数据泄漏/变量误编码，别先庆祝
```

**报告层**
- 只报 H-L 的 P 值不给校准图；不注明 H-L 自由度版本
- `survivalROC` 只报 AUC 点估计、无 95%CI
- `timeROC$AUC[1]` 当第一个时点；`confint(timeROC)$CI_AUC` 忘记 ÷100
- 模型未声明适用范围（列线图只能在建模人群变量取值范围内使用）
- 未对照 TRIPOD 清单、未用 PROBAST 自评偏倚风险

## 进阶：课程之外必须自己补的三件事

**① PH 假设被违反后的抉择流程**（本技能已实测）
```
cox.zph 发现违反 → 该变量效应是否随时间系统性变化？
  ├ 是，理论可解释 → 时依系数 Cox（tt()），报告分时段 HR    ★ 首选
  ├ 是，形式复杂     → 参数模型 psm（换到时间尺度解释）
  ├ 否但违反显著     → 分层 Cox（strat），代价是该变量无 HR
  └ 只想最小改动     → 保留 Cox 并在局限性中明说
```
实测警示：分层越多 C-index 越低（0.808→0.735→0.595→0.583）；时依模型曾把「淋巴血管侵犯」的 HR 从 6 个月的 **2.24** 揭示为 60 个月的 **1.11**（单一 HR 1.58 两头都错）。
→ **遇到 PH 违反不要只打印不处理**，那里藏着真实的临床信息。

**② 竞争风险**（真实数据无竞争事件时可用模拟演示方法学）
- `1 − KM` 高估累积发生率（实测 t=8 时高估 **71%**）→ 必须用 `cuminc()` 的 CIF
- 病因别 HR ≠ Fine-Gray sHR（实测 **2.52 vs 1.59**）：前者答机制、后者答预后
- 应报告**绝对风险差**而非只报 sHR（实测绝对风险差随时间是 +22.4%→+8.0%，而 sHR 恒定）
- 有竞争风险时**禁用普通 `timeROC`**，用 `riskRegression::Score(cause=1)`

**③ 多重插补 + 预测模型**
- 模型评价必须**逐插补集算再按 Rubin 合并**，不能先取一个完整集（会低估不确定性）
- 实测判读：若「插补间 SD ≪ Rubin 合并 SE」，说明不确定性主要来自抽样而非插补；
  若两者量级相当，则**必须做 MAR/MNAR 敏感性分析**

## 报告规范（投稿前逐条打勾）
**TRIPOD** 关键条目：研究设计与数据来源 / 参与者与纳排 / 结局定义 / 预测因子定义与测量时点 /
样本量与 EPV / 缺失数据处理 / 模型构建方法 / 变量选择方法 / 区分度 / 校准度 / 临床效用 /
内部验证方法 / 外部验证 / 模型呈现形式 / 局限性

**PROBAST** 四域：参与者 / 预测因子 / 结局 / 分析（分析域是最常出问题的一域）

## 范文范式（7 篇，详见 `references/案例文献范式.md`）

| 范式 | 文献 | 学什么 |
|---|---|---|
| 诊断 + 增量价值 | Imaizumi 2016 PLoS ONE 11(9):e0163507 | 单指标 vs 临床参数 vs 复合，三模型 + DCA |
| 诊断 + 评分化 | Hu 2018 PLoS ONE 13(8):e0201515 | 时间拆分外部验证 + GiViTI 校准带 |
| 预后 + 列线图 | Eom 2015 PLoS ONE 10(2):e0119671 | 8 中心按中心拆分 + C 0.831 + H-L 3.92 |
| 预后 + 对比分期 | Deng 2017 Sci Rep 7:11524 | C-index 0.720 vs TNM 0.613；讨论与局限性写法 |
| 预后 + ICU 谵妄 | Xing 2019 BMJ Open 9:e030733 | Strengths & limitations 专栏 |
| 机器学习 + 粗筛 | Liang 2020 JAMA Intern Med 180(8):1081 | 72 变量 LASSO→19→Logistic 10；缺失按类型填补 |
| 活模型更新 | Hippisley-Cox 2017 BMJ 357:j2099 | QRISK3 定期重新校准理念 |

## 相关技能

- 本机 R 环境调用与 locale 处理 → `local-r-clinical-stats`
- 统计方法描述/勘误、样本量估算、多重比较校正 → 优先参考 IMA 知识库「统计学」「一起学统计工具」
- 论文撰写与润色 → 中文 `chinese-medical-paper-writer`；英文 `sci-writing-master`
