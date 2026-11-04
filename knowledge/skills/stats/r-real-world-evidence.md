<!-- source: r-real-world-evidence @ r-real-world-evidence | domain: stats -->

---
name: r-real-world-evidence
description: 真实世界研究（RWE）R 语言实战技能。覆盖倾向得分匹配与加权的进阶方法：cobalt 平衡性诊断（love.plot 以 SMD<0.1 为阈值、bal.plot 重叠性检查）、重叠加权 Overlap Weighting（PSweight，估计 ATO、天然规避极端权重、报告 ESS）、克隆删失加权 Clone-Censor-Weight（序贯试验模拟，处理时依混杂）、E-value 未测量混杂敏感性分析、survey 设计下的正确方差（svyglm + svycoxph + quasibinomial）、缺失数据的九种填补方法对比。触发场景：用户要做真实世界研究、观察性疗效比较、时依治疗/时依暴露分析、未测量混杂敏感性分析、单臂/非随机比较的因果推断，或给出 PSM/IPTW/CCW/E-value 相关 R 代码数据要求代为运行调试纠错。
agent_created: true
---

# 真实世界研究 · R 实战技能

## 三条铁律（先读）

1. **★★★ 用了权重就必须用 survey 设计（或三明治稳健方差）。**
   `glm(weights=)` / `coxph(weights=)` 把权重当**精度权重**，IPTW/CCW 的是**抽样权重** → **点估计对、标准误错（CI 通常过窄）**。
   **正确**：`svyglm(..., design = svydesign(...))` / `svycoxph(...)`，
   或 `coxph(..., weights=w, robust=TRUE, cluster=id)`。
   ★ **二分类/计数结局用 `family = quasibinomial()` / `quasipoisson()` 而非 `binomial()`** —— 处理加权后的过离散。

2. **平衡性看 SMD < 0.1，不看 P 值。** 用 `cobalt`：
   ```r
   love.plot(m.out, thresholds = c(m = .1), abs = TRUE, var.order = "unadjusted",
             line = FALSE, grid = FALSE, position = "top",
             shapes = c("circle","triangle"), colors = c("red","blue"))
   bal.plot(m.out, var.name = "distance", which = "both", type = "density")   # ★ 重叠性检查
   ```
   加权/匹配后样本量"变大"，P 值会过度敏感。

3. **必须报告权重诊断与 E-value。**
   - **ESS（有效样本量）= (Σw)²/Σw²** —— `PSweight::SumStat(...)[["ess"]]`
   - 权重范围 / 均值 / 极端权重比例
   - **E-value**：未测量混杂需要多强才能推翻结论（`EValue::evalues.OR/RR`）
     ★ 同时报**点估计的 E-value** 与 **CI 下限的 E-value**（后者才决定显著性是否稳健）
     ★ 结局不罕见（>15%）时必须 `rare = FALSE` 或直接报 RR

## 四种方法的选择

| 目标 | 方法 | 函数 | 估计量 |
|---|---|---|---|
| 治疗组的效应 | PSM 匹配 | `MatchIt::matchit(caliper=0.2, ratio=1)` | **ATT** |
| 全人群的效应 | IPTW | 手工 `1/e(X)` 或 `WeightIt::weightit(estimand="ATE")` | **ATE** |
| 临床均势人群 | **重叠加权** | `PSweight(weight="overlap")` | **ATO** |
| **时依治疗/暴露** | **克隆删失加权 CCW** | 手工实现（见下） | 假设试验 |

> ★ **重叠加权（Overlap Weighting）的优势**：权重 = `1−e(X)` / `e(X)`，**永远在 [0,1] 之间**
> → **天然规避 IPTW 的极端权重爆炸问题**；估计 ATO，在重叠差时比 ATE 更稳健、更可解释。

## ★★★ 克隆删失加权（CCW）—— 处理时依混杂

**要解决的问题**：协变量**既是后续治疗的预测因子、又是结局的中间变量**时，
调基线有残余混杂，调时依协变量又阻断因果通路。

**五步实现**
```r
## ① 克隆：每个患者复制两份，分别分到 A=0 与 A=1
data[, id := .I]
cloned <- data[rep(1:.N, each = 2)]
cloned[, A := rep(0:1, length.out = .N), by = id]      # ★ 用 length.out 更稳健

## ② 定义"干预违背"的删失规则（t = 宽限期）
cloned[A == 1, censored := as.integer(exposure_status == 0 |
                                     (!is.na(exposure_time) & exposure_time > GRACE))]   # ★ 显式处理 NA
cloned[A == 0, censored := as.integer(exposure_status == 1 &
                                     !is.na(exposure_time) & exposure_time <= GRACE)]

## ③ 定义结局（固定随访窗）
cloned[, Y := as.integer(time <= FOLLOWUP & status == 1 & censored == 0)]

## ④ 删失模型 → IPCW 权重（★ 必须含处理变量 A 与基线协变量）
cens_m <- glm(censored ~ A + X1 + X2, data = cloned, family = binomial())
cloned[, p_uncens := 1 - predict(cens_m, type = "response")]
cloned[, weight := ifelse(censored == 0, 1/p_uncens, 0)]
ana <- cloned[censored == 0]

## ⑤ survey 设计下分析
design <- svydesign(ids = ~1, weights = ~weight, data = ana)
svyglm(Y ~ A + X1 + X2, design = design, family = quasibinomial())
svycoxph(Surv(time, Y) ~ A + X1 + X2, design = design)
```
★ **必须做**：`GRACE` / `FOLLOWUP` 的**多窗口敏感性分析**；权重截断；ESS 报告；
★ **还必须写出目标试验的完整要素**（资格标准/治疗策略/分配/随访起点/结局/因果对比/分析计划）。

## 关键函数速查

| 需求 | 函数 | 要点 |
|---|---|---|
| PS 估计 | `glm(T ~ X, family=binomial)` + `fitted()` | — |
| 匹配 | `MatchIt::matchit(..., caliper=0.2, ratio=1, replace=FALSE, m.order="random")` | ★ caliper 单位是 PS 的 SD；★ 设种子 |
| **平衡性** | `cobalt::love.plot(thresholds=c(m=.1))` + `bal.plot(type="density")` | ★★ 优于 P 值 |
| 加权 | `WeightIt::weightit(estimand="ATE", stabilize=TRUE)` | ★ stabilize 降方差 |
| **重叠加权** | `PSweight::PSweight(weight="overlap", yname=, family=)` + `SumStat()` | ★ `SumStat[["ess"]]` |
| **加权分析** | `survey::svyglm(..., family=quasibinomial())` / `svycoxph()` | ★★ 唯一正确路径 |
| 加权设计 | `svydesign(ids=~id, weights=~w, data=)` | — |
| 出表 | `tableone::ShowRegTable()`（回归）/ `svyCreateTableOne()`（基线） | 直接可进论文 |
| **E-value** | `EValue::evalues.OR(est, lo, hi, rare=)` / `evalues.RR()` + `bias_plot()` | ★ 数值从模型动态取 |
| 缺失填补 | `mice()`（首选）/ `missForest()`（次选） | ★ 均值/中位数/众数填补不推荐 |

## 高频陷阱（完整版见 `references/真实世界_精学笔记.md`）

**🔴 致命级**
- `glm/coxph(weights=)` 直接报 SE → CI 过窄（见铁律 1）
- **CCW 的 `NA > 365` 返回 NA → `ifelse` 传播 NA，污染 `censored`** → 必须显式 `!is.na(...)`
- **脚本中重复 `read.csv()` 覆盖前面的填补结果**（`缺失数据代码.R` 读 3 次 →
  `BMI_imp1/2/3` 全部丢失，后续分析用的其实是未填补数据）
- 填补函数内部 `as.numeric(df)` 结果未赋值（死代码）→ `mode_imputation` 返回字符

**🟠 严重级**
- `365` / `400` 硬编码（应参数化 + 多窗口敏感性分析）
- `OW[,-12]` 硬编码列号删除
- E-value 数值硬编码（应从模型取）；未说明 `rare` 参数
- 未声明 ATT / ATE / ATO
- 未做权重截断敏感性分析；未报告 ESS/权重范围
- 未写出目标试验要素（CCW 的规范要求）
- KNN / missForest 是单次插补，不反映不确定性

**🟡 工程级**
- `A := rep(0:1, .N/2)` 依赖行序（应用 `length.out=.N`）
- `Y` 被定义两次（后者覆盖前者）
- 硬编码他人用户名路径；`factor(x, level=)` 少 s

## 与 `r-propensity-score-methods` 的关系

★ **两域是同一方法体系的两个版本，本技能更完整。推荐以本技能为标准流程**：

| 环节 | 第五域 | **本域（更完整）** |
|---|---|---|
| 平衡性诊断 | tableone + SMD | **cobalt: love.plot(thresholds=.1) + bal.plot** ✓ |
| 重叠性检查 | ❌ | ✓ |
| 权重诊断 | ❌ | ✓ **ESS** |
| 加权方差 | 给了但未强调 | ✓ **svyglm+svycoxph+quasibinomial** |
| 敏感性分析 | ❌ | ✓ **E-value** |
| 时依混杂 | ❌ | ✓ **CCW** |

## 相关技能

- 倾向得分基础（ATT/ATE、反事实框架、Robins/Hernán 权重）→ `r-propensity-score-methods`
- 预测模型 / 生存分析 / 竞争风险 → `r-clinical-prediction-model`
- 老年队列（多重插补、中介）→ `r-aging-cohort-databases`
- 孟德尔随机化（工具变量视角）→ `r-mendelian-randomization`
