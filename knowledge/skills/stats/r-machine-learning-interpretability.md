---
name: r-machine-learning-interpretability
description: 临床机器学习建模与可解释性研究（R 语言）实战技能。覆盖二分类 8 模型（Logistic / 决策树 / 随机森林 / XGBoost / LightGBM / KNN / SVM / 神经网络）与生存数据 6 模型（RSF / CoxBoost / survivalsvm / GBM / Lasso-Cox / Cox）的完整流水线，含数据插补（missForest / MICE）、特征选择（先单后多 / Lasso）、超参数调优的正确做法（交叉验证而非训练集）、模型评价（AUC 及有效 95%CI、混淆矩阵、校准斜率截距 Brier、DCA）、**DeLong 检验与多重比较校正**、SHAP 可解释性（kernelshap + shapviz：蜂群图/依赖图/瀑布图/力导向图），以及 26 条高频陷阱与「课程原版 vs 修正版」量化对照。触发场景：用户要做/复现/审阅机器学习临床预测研究、SHAP 可解释性分析、多模型性能比较、ML 与 Logistic 的增量价值评估、或给出 ML 相关 R 代码/数据要求代为运行调试纠错。
agent_created: true
---

# 临床机器学习建模与可解释性 · R 实战技能

## 三条铁律（先读）

1. **标准化必须在拆分之后做。** 先对全量数据 `scale()` 再拆分 = **数据泄漏**。
   实测影响量化：AUC 乐观偏倚 0.0000–0.0004（**小到无法察觉，但方向必然乐观，且真实部署时无法迁移**）。
   → 正确做法：先拆分，再用**训练集的 μ/σ** 变换验证集（`caret::preProcess` 或 `recipes`）。

2. **超参数只能用交叉验证或验证集选，绝不能用训练集。**
   实测：用训练集 AUC 选参的 XGBoost，**选中了训练集 AUC = 1.0000（完美分类）的模型** ——
   这等价于"在所有候选中挑最过拟合的那一个"。**网格越宽，危害越大。**

3. **模型比较必须做 DeLong 检验 + 多重比较校正。**
   实测（627 例糖尿病数据，8 模型验证集）：

   | 对比（性能最好的 KNN 为参照） | ΔAUC | Holm 校正 P | 结论 |
   |---|---|---|---|
   | vs **Logistic** | 0.0096 | **0.8236** | **无差异** |
   | vs Random Forest | 0.0218 | 0.4127 | 无差异 |
   | vs SVM | 0.0023 | 0.8236 | 无差异 |
   | vs Neural Network | 0.0161 | 0.6249 | 无差异 |
   | vs XGBoost | 0.0292 | 0.1872 | 校正后无差异 |
   | vs LightGBM | 0.0335 | 0.0844 | 校正后无差异 |
   | vs Decision Tree | 0.1210 | **0.0004** | 显著（树更差） |

   → **7 个机器学习模型与最朴素的 Logistic 回归之间的 AUC 差异，经校正后全部没有统计学意义。**
   → **不要宣称"我的 ML 模型 AUC 更高"**；ML 论文的正确立论是**可解释性（SHAP）、变量筛选能力、自动捕捉非线性/交互**，而非区分度。

## 标准流水线（10 步）

```
1. 数据核查（缺失率、事件率、类别不平衡、0 值嫌疑）
2. 缺失插补（missForest 单次 / MICE 多重，<20% 才填）
3. 拆分（★ 按结局分层）→ 之后才做标准化（★ 训练集参数）
4. 特征选择（先单后多 / Lasso / 树重要性）
5. 建模（8 种二分类 或 6 种生存）
   ★ 超参一律 CV 选，不用训练集
6. 评价（验证集！）：
   区分度 AUC + 有效 95%CI（ci.auc(roc对象)）
   校准度 斜率/截距/Brier（★ 课程盲区，必报）
   临床效用 DCA（bootstraps ≥ 200）
7. ★ DeLong 检验 + Holm/FDR 校正
8. 重复交叉验证（5×5 或 10×10）给出 AUC 分布而非单点
9. SHAP 可解释性（kernelshap + shapviz）
10. 基线对照：与 Logistic 的增量价值（ΔAUC + NRI/IDI，见 r-clinical-prediction-model 技能）
```

完整可运行脚本见 `assets/F_ml_binary.R`。

## 关键函数速查

| 需求 | 函数 | 要点 |
|---|---|---|
| 随机森林插补 | `missForest::missForest(d)` | 单次插补，不反映插补不确定性 |
| 多重插补 | `mice::mice(d, m=10, maxit=10, seed=500)` + `with()` + `pool()` | 模型评价须逐插补集算再 Rubin 合并 |
| Lasso | `glmnet(x, y, family="binomial"\|"cox", alpha=1)` + `cv.glmnet` | ★ x 须先 `model.matrix` 转哑变量；y 不能因子化 |
| 拆分层抽样 | `caret::createDataPartition(y=结局, p=0.7)` | ★ 用**结局**分层，不是 id |
| 交叉验证 | `caret::trainControl(method="repeatedcv", number=5, repeats=5, classProbs=TRUE, summaryFunction=twoClassSummary)` | ★ 因子水平必须是合法变量名（No/Yes），用 0/1 会报错 |
| XGBoost 调参 | `xgb.cv(nfold=5, early_stopping_rounds=20, prediction=TRUE)` | 用 `test_auc_mean` 最大选参 |
| LightGBM 调参 | `lgb.cv(nfold=5, early_stopping_rounds=...)` | ★ `nrounds` 要设大（500–2000）再早停；最终模型用 `best_iter` |
| 决策树剪枝 | `rpart.control(cp = 标量)` | ★ `cp` 必须是数值，传 `$bestTune`（data.frame）会失效 |
| **AUC 及 CI** | `pROC::roc()` + `ci.auc(roc对象)` | ★ **`ci.auc()` 必须传 roc 对象，传 AUC 数值会得到无效 CI** |
| **DeLong 检验** | `pROC::roc.test(roc1, roc2)` | 多模型比较须 `p.adjust(method="holm")` |
| 校准度 | `rms::val.prob(p, y, pl=FALSE)` | 输出 Brier / Intercept / Slope / Eavg / S:p；★ Slope<1 过拟合，S:p<0.05 校准欠佳 |
| DCA | `rmda::decision_curve(..., bootstraps=200)` | ★ bootstraps=10 过少；报**验证集**结果 |
| **SHAP** | `kernelshap::kernelshap(model, X, bg_X, pred_fun, type)` → `shapviz::shapviz()` | 模型无关，8 种模型可统一用 |
| SHAP 可视化 | `sv_importance(kind="bar"\|"beeswarm"\|"both")`、`sv_dependence(v=, color_var=)`、`sv_waterfall(row_id=)`、`sv_force(row_id=)` | ★ `sv_force` 在新版 shapviz 已弃用；`size=` 应改 `linewidth=` |
| 生存 ML | `randomForestSRC::rfsrc`、`CoxBoost`、`survivalsvm`、`gbm(distribution="coxph")` | 见下方陷阱 |
| 生存 ML 评价 | `timeROC::timeROC(iid=TRUE)`、`survcomp::concordance.index`、`riskRegression::Score(metrics=c("AUC","Brier"))` | ★ 报验证集；`$AUC[1]` 是占位值 |

## 高频陷阱（26 条完整版见 `references/机器学习_精学笔记.md`）

**🔴 致命级（会使结论错误）**
- **标准化在拆分之前** → 数据泄漏（实测 ΔAUC 0.0004，方向必然乐观）
- **`ci.auc(auc_value)`** 传数值而非 roc 对象 → 本域课程 **15 处** 相同错误，所有 AUC 的 95%CI 全部无效
- **用训练集 AUC 选超参**（XGBoost 与神经网络各一处）→ 必然选中最过拟合组合
- **LightGBM 验证集 label 写成训练集的** → 内部评估全失效
- **`rpart(cp = $bestTune)`** 传 data.frame 而非标量 → 剪枝失效
- **`xgb.train(params = 含 nrounds 的列表)`** → 非法参数
- **`lgb.cv(nrounds=10, early_stopping=10)`** → 早停形同虚设
- **最终模型未用 CV 的 best_iter**
- 生存线：**`Cindex_RSF <- summary_CoxBoost$concordance[1]`** → 点估计来自 CoxBoost、CI 用 RSF 的 SE，**两者不匹配**

**🟠 严重级**
- DCA `bootstraps=10` 过少；训练集与验证集 DCA 都做但正文应只报验证集
- 无 DeLong 检验 → "8 个模型 AUC 从 0.81 到 0.93"被误读为性能梯度
- 校准曲线用 `geom_smooth(loess)` 平滑 0/1 结局 → 非标准；应用分组观测率或 `val.prob`
- `size=` 在 ggplot2 ≥3.4 已弃用（改 `linewidth=`）
- Logistic/树模型用原始变量、KNN/SVM/NN 用标准化变量 → 口径不一致须分别说明
- 结局变量反复 `factor()` / `as.numeric()-1` / `factor()` → 状态混乱，`as.numeric(factor)` 依赖水平顺序
- SVM 概率为 Platt 近似，须声明
- 硬编码列号取变量（`d[, 2:14]`）
- 仅单次 70/30 拆分，无重复交叉验证
- 生存：C-index 全部算在**训练集**上

**🟡 工程级**
- `missForest` 连续调用两次（第一次结果被丢弃）
- `DMwR` 已从 CRAN 下架（2021 归档）
- 安装了 `ROSE`/`DMwR` 但未实际调用过采样；也未报告类别不平衡程度
- 随机种子散落各处（123/12/111/11/1…），无法复现
- 硬编码 `setwd("D://...")`

## 校准度：本域最被忽视、却最致命的一环

实测 8 模型校准指标（验证集）：

| 模型 | Brier | 校准斜率 | 校准检验 P |
|---|---|---|---|
| Logistic | 0.1045 | 1.012 | 0.362 |
| Decision Tree | 0.1634 | **0.657** | **<0.0001** |
| Random Forest | 0.1144 | 1.027 | 0.593 |
| SVM | **0.0951** | 1.054 | 0.294 |
| KNN（AUC 最高） | 0.0977 | **1.196** | 0.236 |
| Neural Network | 0.1114 | **0.555** | **0.0004** |
| XGBoost | 0.1210 | 0.830 | 0.185 |
| LightGBM | 0.1205 | 0.925 | 0.748 |

- **AUC 最高的 KNN，校准斜率偏离 1 最远**（1.196）
- **决策树与神经网络的校准检验 P<0.001 → 预测概率在统计上不可靠，绝不能用于临床绝对风险告知**
- **8 个模型的校准截距全为负** → 系统性低估风险，须在讨论中说明

> **区分度最好的模型与概率最可靠的模型不是同一个。** ML 论文的表格里**必须有校准斜率/截距/Brier**。

## SHAP 可解释性要点

- `kernelshap` 是**模型无关**的 → 8 种模型能共用一套 SHAP 代码（这是课程的技术亮点）
- `glm` 可直接 `pred_fun = stats::predict, type="response"`
- `rpart` 需 `pred_fun` 返回概率矩阵；`kknn`/`neuralnet` 需自写 wrapper
- **不同模型的 `shapviz` 对象结构不同**（`rpart` 需取 `$Yes`）——最常见卡点
- **一致性自检**：线性模型中 SHAP ≈ 系数 ×(变量 − 基线均值)，故 **Logistic 的 SHAP 排序必与 OR 排序一致**；不一致即为实现有误
- 实测 SHAP 排序（糖尿病）：glucose(0.166) > bmi(0.069) > hyperlip(0.067) > exercise(0.054) > pedigree(0.046) > pregnant(0.042) > age(0.038) —— 与临床常识一致

## 数据隐私红线

`elder2.csv` 的 `ID` 列为 **18 位中国大陆居民身份证号**（如 `330121194907190845`）。
**分析前必须脱敏（哈希化或删除该列），且不得随数据文件外传。**

## 相关技能

- 预测模型 / 列线图 / NRI / IDI / PH 假设 / 竞争风险 → `r-clinical-prediction-model`
- 本机 R 环境调用与 locale 处理 → `local-r-clinical-stats`
- 论文撰写与润色 → 中文 `chinese-medical-paper-writer`；英文 `sci-writing-master`
