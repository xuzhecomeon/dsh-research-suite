---
name: r-nhanes-analysis
description: NHANES（美国国家健康与营养调查）数据挖掘 R 语言实战技能。覆盖复杂抽样权重的正确处理（svydesign + options(survey.lonely.psu="adjust") + nest=TRUE + 权重变量选择 + 多周期合并权重除以周期数）、加权描述与检验（svymean/svyby/svyttest/svytable/svychisq/svyquantile）、加权回归（svyglm + quasibinomial + svycoxph）、加权 RCS 曲线的自写实现（svy2rms + NHS_rcs）、多周期 XPT 数据合并（read.xport）、检出限（LOD/√2）处理、量表条目重叠规避、多模型策略与 ShowRegTable 出表、加权中介分析。触发场景：用户要用 NHANES 做研究、公共数据库挖掘、加权复杂抽样数据分析、加权剂量-反应曲线（RCS）、或给出 NHANES 相关 R 代码数据要求代为运行调试纠错。
agent_created: true
---

# NHANES 数据挖掘 · R 实战技能

## 五条铁律（先读）

1. **★★★ 必须用 `svy` 系列函数，绝不能用无权重方法。**
   `mean()` / `t.test()` / `chisq.test()` / `lm()` / `glm()` 在 NHANES 上会给出**有偏的点估计与过窄的 CI**。
   正确对应：`svymean` / `svyttest` / `svychisq` / `svyglm` / `svycoxph`。

2. **★★★ 必须设 `options(survey.lonely.psu = "adjust")`。**
   NHANES 某些层只含 1 个 PSU（lonely PSU），此时方差无法估计，`survey` 默认**报错**。
   - `"adjust"`：中心化调整（保守但可用）★ 推荐
   - `"certainty"`：视为确定层（贡献 0）
   - `"remove"`：剔除该层
   **这是 NHANES 分析最容易被忽略、却会让整个分析失败的一行。**

3. **权重变量必须与研究变量来源匹配，且多周期合并时除以周期数。**
   - MEC 体格/实验室指标 → `WTMEC2YR`；访谈 → `WTINT2YR`；1999–2002 特殊 → `WTMEC4YR`
   - **K 个 2 年周期合并 → `wt = wt / K`**（或用官方组合权重）；否则权重总量放大 K 倍
   - `svydesign(..., nest = TRUE)` —— PSU 编号在层内重复，必须声明嵌套

4. **缺失编码必须先转为 NA，量表条目重叠必须逐条核对。**
   - NHANES 的拒绝/不知道用 **7 / 9 / 77 / 99 / 777 / 999** 编码，不是 NA → 必须先清洗
   - ★★ **同一量表的条目可能同时构成暴露与结局**（criterion contamination）：
     例如研究"睡眠障碍 → 抑郁"时，PHQ-9 的第 3 题 `DPQ030` 本身就是睡眠条目，
     **必须从抑郁总分中剔除**，否则会夸大关联。本仓主复现文献正确处理了这一点。

5. **多周期同一指标可能有不同变量名与单位。**
   例：CRP 早期 `LBXCRP`（mg/dL）、后期 `LBXHSCRP`（mg/L）→ 必须**逐周期核对 Codebook** 并做单位换算。

## 标准流程

```
1. 读入 XPT：for (f in list.files(pattern="*.XPT")) assign(文件名, read.xport(f))
   ★ 建议改用 lapply 存入 list（避免污染全局环境）
2. 加周期标签（Year）→ 提取 SEQN/SDMVSTRA/SDMVPSU/WTMEC2YR
3. 分模块（人口学/暴露/结局/协变量）提取 → rename → full_join(by="SEQN")
4. ★ 缺失编码（7/9/777/999）转 NA
5. ★ 构建加权设计
   options(survey.lonely.psu = "adjust")
   design <- svydesign(id=~SDMVPSU, strata=~SDMVSTRA, weights=~wt, nest=TRUE, data=dat)
6. ★ 加权分位数分组：svyquantile(~x, design, c(.25,.5,.75)) → 程序化切分（不要硬编码）
7. 基线表：svyCreateTableOne(vars, strata, factorVars, data=design)
8. 回归：svyglm(...) 多模型策略（未调整 → 部分调整 → 完全调整）→ ShowRegTable()
9. 剂量-反应：★ svy2rms() + NHS_rcs()（见下）
10. 敏感性分析（E-value 等）；加权中介（CMAverse）
```

## ★★★ 加权 RCS 曲线的自写实现（本技能最有价值的技术资产）

**难题**：`rms` 包（提供 `rcs()` + `Predict()` 画 RCS）**不支持 survey 设计对象**；而 NHANES 必须加权。

**解法**：写 `svy2rms()` 把 `svyglm` / `svycoxph` 转成 rms 可识别对象（**元编程**：改写函数调用对象）。

**核心逻辑（阅读提炼，可直接复用）**
```r
svy2rms <- function(fit, by = NULL) {
  cal <- fit$call
  if (deparse(cal[[1]]) %in% c("ols","lrm","cph")) return(list(fit, eval(cal$data)))
  ## ★ 把 svy 函数替换为对应 rms 函数
  if (deparse(cal[[1]]) == "svycoxph")     cal[[1]] <- as.name("cph")
  else if (fit$family[[1]] == "gaussian")  cal[[1]] <- as.name("ols")
  else                                     cal[[1]] <- as.name("lrm")
  cal$family <- NULL
  ## ★ 抽数据 + 权重归一化（均值=1，避免数值问题）
  d <- fit$survey.design$variables
  d$weights <- (1/fit$survey.design$prob) / mean(1/fit$survey.design$prob)
  ## ★ 把 design 换成 data，注入 weights/normwt
  names(cal)[names(cal) == "design"] <- "data"
  cal[[3]] <- as.name(".svy2rms.data"); cal$weights <- as.name("weights")
  cal$normwt <- TRUE; cal$maxit <- 200; cal$tol <- 1e-09
  ## ★ 设置 datadist 后重新拟合
  old <- options(datadist = suppressWarnings(rms::datadist(d)))
  res <- list(fit = suppressWarnings(eval(cal)), data = d)
  options(old)
  res
}
```

**用法（三种模型都支持）**
```r
Svydesign <- svydesign(ids=~SDMVPSU, strata=~SDMVSTRA, weights=~WTMEC2YR, nest=TRUE, data=data)

## Cox
fita <- svycoxph(Surv(Age, y) ~ rcs(SBP, 4), design = Svydesign)
NHS_rcs(fita, reference = "median", pvalue_position = c(0.1, 0.85))
## 线性
fitb <- svyglm(vd ~ rcs(TC, 4), family = "gaussian", design = Svydesign)
## Logistic ★ quasibinomial
fitc <- svyglm(y ~ rcs(TC, 4), family = "quasibinomial", design = Svydesign)
```
★ 配套 `rcsx(fit)`（解析 RCS 变量名）与 `getKnot()`（解析节点数）也需一并复use。

## 关键函数速查

| 需求 | 函数 | 要点 |
|---|---|---|
| 加权设计 | `svydesign(id=~SDMVPSU, strata=~SDMVSTRA, weights=~wt, nest=TRUE, data=)` | ★ 先设 `options(survey.lonely.psu="adjust")` |
| 加权均值/分组 | `svymean()` / `svyby(~y, ~g, design, svymean)` | — |
| 加权 t 检验 | `svyttest(y ~ g, design)` | 连续变量 |
| 加权卡方 | `svychisq(~a + b, design, statistic="Chisq")` | 分类变量 |
| 加权频数 | `svytable(~a, design)` / `svytable(~a+b, design)` | — |
| **加权分位数** | `svyquantile(~x, design, c(.25,.5,.75))` | ★ 用于四分位分组 |
| 加权线性回归 | `svyglm(y ~ x, design, family="gaussian")` | — |
| **加权 Logistic** | `svyglm(y ~ x, design, family = quasibinomial())` | ★★ 用 quasibinomial 处理过离散 |
| 加权 Cox | `svycoxph(Surv(t,s) ~ x, design)` | — |
| 加权基线表 | `tableone::svyCreateTableOne(vars, strata, factorVars, data=design)` | — |
| 回归出表 | `tableone::ShowRegTable(model)` | ★ 直接输出 OR (95%CI) 格式 |
| **加权 RCS** | 自写 `svy2rms()` + `NHS_rcs()` | ★★★ 见上 |
| 读 XPT | `foreign::read.xport()` / `haven::read_xpt()` | — |
| **加权中介** | `CMAverse`（推荐）> 自写 bootstrap | ★ `mediation` 不支持 survey 权重 |
| 混合暴露 | `bkmr::kmbayes()`（BKMR）/ `wqs` | ★ 课程缺，待补方向 |

## 高频陷阱

**🔴 致命级**
- 用 `mean/t.test/chisq.test/lm/glm` 代替 `svy` 系列 → 估计有偏、CI 过窄
- **未设 `options(survey.lonely.psu = "adjust")`** → 单 PSU 层导致方差无法估计、分析失败
- **多周期合并时权重未除以周期数** → 权重总量放大 K 倍
- **缺失编码 7/9/777/999 未转 NA** → 被当作真实数值纳入分析
- **量表条目重叠未剔除**（如研究睡眠→抑郁时 PHQ-9 的睡眠条目仍计入抑郁总分）

**🟠 严重级**
- 权重变量与研究变量来源不匹配（用访谈权重分析实验室指标）
- 四分位切点**硬编码**（`ifelse(x<42.1, 1, ...)`）→ 应程序化取 `svyquantile` 返回值
- 多周期同一指标变量名/单位不同却未核对（CRP 的 `LBXCRP` vs `LBXHSCRP`）
- 未做加权中介（`mediation` 不支持 survey，需用 `CMAverse`）
- 未报告加权后的**有效样本量 ESS**

**🟡 工程级**
- `for + assign` 批量读取污染全局环境（建议 lapply 存 list）
- 手动切换工作目录（`Session → Set Working Directory`）
- `svy2rms()` 内部用 `<<-` 污染全局；`options(old)` 恢复全部 options（可能清掉用户 datadist）
- 依赖 `do` / `set` / `tmcn` 等冷门包

## ★ 本域的两个非代码资产（建议随技能一起保留）

| 文件 | 用途 |
|---|---|
| `nhanes快速搜索工具.xlsx` | NHANES 挖掘的最大效率瓶颈是"变量散落在哪个 XPT"—— 该工具直接解决 |
| `综合指标整理.xlsx` | 常用复合指标（TyG、AIP、SII 等）的计算公式与构成变量 |

## NHANES 典型研究范式（本仓 8 篇案例）

关联分析 + 多模型 / 剂量-反应（RCS）/ 倾向得分（PSM+RCS）/ 生存分析（COX）/ 中介分析 / **混合暴露（BKMR）** / 轨迹

## 相关技能

- 倾向得分（PSM、重叠加权）→ `r-propensity-score-methods` / `r-real-world-evidence`
- 剂量-反应 RCS 与预测模型 → `r-clinical-prediction-model`
- 老年队列（CHARLS 等，同为公共数据库挖掘）→ `r-aging-cohort-databases`
- 本机 R 环境调用 → `local-r-clinical-stats`
