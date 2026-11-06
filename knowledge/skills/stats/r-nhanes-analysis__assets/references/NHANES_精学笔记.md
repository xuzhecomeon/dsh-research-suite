# NHANES 数据挖掘 · 精学笔记（R 语言医学统计全能体系 · 第九域）

> 学习对象：`NHANES/`（约 250 个文件：4 个 R 脚本 + 8 份课件 PDF + 150+ 个 XPT 数据文件 + 8 篇案例文献 + 快速搜索工具）
> 学习方法：代码逐行精读 + 数据资产勘察 → 问题清单化

---

## 0. 本域全景

### 0.1 课件体系（8 讲）

| 讲 | 标题 |
|---|---|
| 第一讲 | NHANES 数据库的挖掘和分析 |
| 第二讲 | NHANES 数据库及选题思路介绍 |
| 第三讲 | NHANES 变量介绍及筛选 |
| 第四讲 | NHANES 数据的整理及实操 |
| **第五讲** | **NHANES 数据权重介绍** ← ★★★ 本域最核心、最易出错的一讲 |
| 第六讲 | NHANES 统计思路与套路 |
| 第七讲 | NHANES R 语言数据分析 |
| — | NHANES 文章解读 |

### 0.2 脚本

| 脚本 | 内容 | 行数 |
|---|---|---|
| `分析.R` | **主分析流程**：加权设计 → 基线表 → 加权回归 → 维生素D 与肥胖 | 265 |
| `rcs_new.R` | ★★ **加权 RCS 曲线的自写实现**（`svy2rms` 函数） | 231 |
| `NHS_rcs（更新）.R` | 同上（更新版，含三种模型示例） | 271 |
| `数据代码/文献2-完整版.R` | ★★★ **836 行的完整论文复现**：睡眠障碍 × 炎症标志物 × 抑郁症状的中介分析（7 周期数据合并） | 836 |
| `数据代码/BMI/`、`健康状况/`、`人口学特征/`、`实验室检查/`、`睡眠/`、`吸烟/`、`血糖/`、`血压/`、`抑郁/`、`饮酒/`、`运动/`、`肾脏/` | **150+ 个 XPT 数据文件**，覆盖 1999–2018 各周期 | — |

### 0.3 ★ 辅助工具（本域独有）

| 文件 | 用途 |
|---|---|
| **`nhanes快速搜索工具.xlsx`** | ★★ 快速查找变量所属的 XPT 文件与周期 |
| **`综合指标整理.xlsx`** | ★★ 常用复合指标（如 TyG、AIP、SII 等）的计算公式与构成变量 |

> ★★ **这两个 Excel 是本域最实用的"非代码资产"** —— NHANES 挖掘的最大效率瓶颈就是"变量散落在哪个文件里"，
> 搜索工具直接解决这个问题。**建议纳入技能资产。**

---

## 1. ★★★ 权重处理（NHANES 的方法学命门）

### 1.1 加权设计的构建（课件第五讲的核心）

```r
library(survey)
options(survey.lonely.psu = "adjust")       # ★★ 处理"单 PSU 层"

study_design <- svydesign(
  data   = dat,
  id     = ~SDMVPSU,      # PSU（初级抽样单元）
  strata = ~SDMVSTRA,     # 层（stratum）
  weights= ~wt,           # 权重（WTMEC2YR 或 WTMEC4YR 等）
  nest   = TRUE)          # ★ PSU 嵌套于层内
```

**★★ 三个关键点**

1. **`options(survey.lonely.psu = "adjust")` 必须设置**
   - NHANES 的某些层只含 1 个 PSU（"lonely PSU"），此时方差无法估计 → `survey` 包默认报错
   - `"adjust"` 采用**中心化调整**（把该 PSU 的贡献按总体均值中心化）→ 保守但可用
   - 其他可选值：`"certainty"`（视为确定层，贡献 0）、`"remove"`（剔除）、`"fail"`（报错）
   - ★★ **这是 NHANES 分析中最容易被忽略、却会导致整个分析失败的一行**

2. **`nest = TRUE`**：NHANES 的 PSU 编号在不同层内会重复，必须声明嵌套

3. **权重变量的选择**
   | 权重 | 适用 |
   |---|---|
   | `WTMEC2YR` | MEC 检查（体格+实验室）2 年权重 |
   | `WTINT2YR` | 访谈 2 年权重 |
   | `WTMEC4YR` | 1999–2002 的 4 年权重（特殊） |
   - ★ **必须用与研究变量来源匹配的权重**：若用了实验室指标，必须用 `WTMEC2YR`
   - ★ **多周期合并时权重需除以周期数**（如 7 个 2 年周期 → `wt/7`）；或使用 NHANES 官方提供的组合权重

### 1.2 加权描述统计与差异性检验

```r
svymean(~Age, study_design)                         # 加权均值
svyby(~Age, ~Obesity, study_design, svymean)        # 分组加权均值
svyttest(Age ~ Obesity, study_design)               # 加权 t 检验（连续变量）
svytable(~Age_new, study_design)                    # 加权频数
svychisq(~Age_new + Obesity, study_design, statistic = "Chisq")   # 加权卡方（分类变量）
svyquantile(~vd, study_design, c(0.25, 0.5, 0.75))  # ★ 加权分位数（用于四分位分组）
```

> ★★ **不能用 `mean()` / `t.test()` / `chisq.test()`** —— 这些是无权重方法，会给出**有偏的点估计与过窄的 CI**。
> ★ `svyquantile()` 求加权四分位 → **在本数据上 Q1/Q2/Q3 = 42.1/58.9/72.3**，
> 脚本随后用这三个值硬编码分组（`ifelse(dat$vd<42.1, 1, ...)`）—— ★ 应改为**程序化取 `svyquantile` 的返回值**，
> 否则换数据/换权重即错。

### 1.3 加权回归

```r
## 线性回归（连续结局）
mod <- svyglm(vd ~ Age_new + Race_new + ..., design = study_design, family = "gaussian")

## Logistic 回归（二分类结局）★ 用 quasibinomial 而非 binomial
obesity_mod1 <- svyglm(status ~ vd_q4, design = study_design, family = quasibinomial)
obesity_mod2 <- svyglm(status ~ vd_q4 + Age_new, ...)
obesity_mod3 <- svyglm(status ~ vd_q4 + Age_new + Race_new + Marital_new + ...)   # 完全调整

ShowRegTable(obesity_mod3)      # tableone 包：直接输出 OR (95%CI) 格式的表
```

> ★★ **多模型策略（模型1 未调整 → 2 部分调整 → 3 完全调整）** —— 与第四域、第七域一致，环境流行病学标准做法 ✓
> ★ **`family = quasibinomial`** 而非 `binomial` —— 处理加权后的过离散，给出更稳健的 SE ✓（与第七域 CCW 脚本一致）
> ★ `tableone::ShowRegTable()` 一键把回归结果格式化为 `OR (95%CI)` 的表 → **可直接进论文**，很实用

---

## 2. ★★★ 加权 RCS 曲线的自写实现（`rcs_new.R` / `NHS_rcs.R`）

### 2.1 要解决的技术难题

**问题**：`rms` 包（提供 `rcs()` 与 `Predict()` 画 RCS 曲线）**不支持 `survey` 设计对象**；
而 NHANES 必须加权。二者不能直接结合。

**课程/资料的解法**：写一个 **`svy2rms()` 函数**把 `svyglm` / `svycoxph` 对象**转成 rms 可识别的对象**。

### 2.2 函数关键逻辑（阅读提炼）

```r
svy2rms <- function(fit, by = NULL) {
  cal <- fit$call
  ## ① 若已是 rms 对象（ols/lrm/cph）直接返回
  if (deparse(cal[[1]]) %in% c("ols","lrm","cph")) { ... return(res) }

  ## ② 按模型类型把调用函数替换为对应的 rms 函数
  if (deparse(cal[[1]]) == "svycoxph")      cal[[1]] <- as.name("cph")
  else if (fit$family[[1]] == "gaussian")   cal[[1]] <- as.name("ols")
  else                                       cal[[1]] <- as.name("lrm")

  ## ③ 把 survey 设计的数据抽出，★ 权重归一化（均值=1）
  .svy2rms.data <- fit$survey.design$variables
  .svy2rms.data$weights <- (1/fit$survey.design$prob) / mean(1/fit$survey.design$prob)

  ## ④ 把调用里的 design 换成 data，并注入 weights / normwt / maxit / tol
  names(cal)[names(cal) == "design"] <- "data"
  cal$weights <- as.name("weights"); cal$normwt <- TRUE
  cal$maxit <- 200; cal$tol <- 1e-09

  ## ⑤ 设置 datadist 后重新拟合 rms 模型
  options(datadist = suppressWarnings(rms::datadist(.svy2rms.data)))
  res <- list(fit = suppressWarnings(eval(cal)), data = .svy2rms.data)
  options(old)     # ★ 恢复原 options
  res
}
```

**★ 三个巧妙之处**
1. **`cal[[1]] <- as.name("ols"/"lrm"/"cph")`**：直接**改写函数调用对象（call）**，
   把 `svyglm` 换成 `ols`/`lrm`，从而复用 rms 的 `Predict()` 与绘图能力 —— 这是 R 元编程（metaprogramming）的高级用法
2. **权重归一化**：`weights = (1/prob)/mean(1/prob)` —— 把权重缩放到均值 1，避免 `normwt=TRUE` 下的数值问题
3. **`options(datadist=...)` 前后保存与恢复** —— 避免污染全局设置（比只设不恢复更规范）

**配套函数**（同一份代码里）
- `rcsx(fit)` —— 从系数名/assign 中**解析出 RCS 变量名**（处理 `rcs(x, 4)` 这类调用）
- `getKnot()` —— 从 formula 中**解析节点数**（`rcs(x, 4)` → 4；未指定时按自由度推断）
- `NHS_rcs(fit, reference="median", pvalue_position=c(...))` —— **最终绘图函数**

**用法示例（脚本头部注释）**
```r
Svydesign <- svydesign(ids=~SDMVPSU, strata=~SDMVSTRA, weights=~WTMEC2YR, nest=TRUE, data=data)

#### Cox 模型 ####
fita <- svycoxph(Surv(Age, y) ~ rcs(SBP, 4), design = Svydesign)
plot_fita <- NHS_rcs(fita, reference = "median", pvalue_position = c(0.1, 0.85))

#### 线性模型 ####
fitb <- svyglm(vd ~ rcs(TC, 4), family = "gaussian", design = Svydesign)

#### Logistic 模型 ####
fitc <- svyglm(y ~ rcs(TC, 4), family = "quasibinomial", design = Svydesign)
```

> ★★★ **这是本域最值得固化的技术资产**：**NHANES（或任何复杂抽样数据）的加权 RCS 曲线**，
> 用现成包无法一步完成，必须自写转换函数。本域提供了完整可用的实现。
> ★ 注意：该实现依赖 `do`、`set`、`tmcn` 等辅助包做字符串处理，**可读性较差但你只需调用 `svy2rms()` + `NHS_rcs()`**。

**问题**
| # | 问题 | 严重度 |
|---|---|---|
| N1 | 函数内部用了 `<<-` 赋值（`.svy2rms.data <<- .svy2rms.data`、`chn <<- ...`）→ **污染全局环境** | 🟠 |
| N2 | `deparse(fit$call[[1]])` 单独一行**未赋值**（死代码） | 🟡 |
| N3 | `options(old)` 在设置 datadist 后恢复了**全部** options（包括 datadist）→ 可能把用户原设的 datadist 也清掉；更好的做法是只恢复 datadist | 🟡 |
| N4 | 依赖 `do` / `set` / `tmcn` 等较冷门的包 | 🟡 可复现性风险 |

---

## 3. ★★★ 完整论文复现（`文献2-完整版.R`，836 行）—— 本域最有价值的实战范例

**论文主题**：`Associations between sleep disturbance, inflammatory markers and depressive symptoms: Mediation analyses in a large NHANES community sample`
（睡眠障碍 × 炎症标志物 × 抑郁症状的中介分析）

### 3.1 数据流程（7 个周期 2005–2018）

```
1. 批量读取 XPT（每个子目录用同一模式）
   files <- list.files(pattern="*.XPT")
   for (file in files) {
     perpos <- which(strsplit(file,"")[[1]] == ".")
     assign(gsub(" ","", substr(file, 1, perpos-1)), read.xport(file))
   }
   ## ★★ 用文件名自动生成变量名（如 DEMO_D.XPT → DEMO_D），再 rbind 多周期
2. 加周期标签：DEMO_D$Year <- "2005-2006" ... DEMO_J$Year <- "2017-2018"
3. 提取权重与设计变量：SEQN, SDMVSTRA, WTMEC2YR, SDMVPSU, Year
4. 分模块提取并合并（人口学 / 睡眠 / 炎症 / 抑郁 / 协变量）
5. 变量重命名（rename 成可读名）
6. full_join 合并
```

### 3.2 ★★★ 三个专业级的技术细节（本域最有价值的部分）

**① 检出限（LOD）处理**
```r
CRP2$CRP_mg_l = ifelse(CRP2$LBDHRPLC == 1, CRP2$LBXHSCRP/sqrt(2), CRP2$LBXHSCRP)
```
> ★★ **低于检出限的值用 `LOD / √2` 替代** —— 这是处理"低于检测下限"的**国际通行标准方法**。
> 若直接当作 0 或直接用 LOD，都会产生偏倚。**这是环境/实验室数据清洗的必备知识**。

**② 单位换算与跨周期变量名不一致的处理**
```r
CRP1$CRP_mg_l <- CRP1$LBXCRP * 10      # CRP_D/E/F 单位是 mg/dL → 转 mg/L
## 后期周期用高敏 CRP（HSCRP_I/J），变量名不同 → 分两次处理再合并
```
> ★★ **NHANES 的同一指标在不同周期可能用不同变量名/不同单位**（如 CRP 早期 `LBXCRP`、后期 `LBXHSCRP`）。
> **必须逐周期核对 Codebook**，否则会静默产生错误数据。

**③ 避免暴露与结局变量的条目重叠**
```r
## 抑郁量表，变量名一样，直接合并，DPQ030 涉及睡眠障碍，不用于计算抑郁评分
DPQ_dat <- rbind(DPQ_D[,c("SEQN","DPQ010","DPQ020","DPQ030","DPQ040",...)], ...)
```
> ★★ **PHQ-9 的第 3 题（DPQ030）本身就是"睡眠"相关条目**。本研究的暴露是"睡眠障碍"，
> 若把 DPQ030 计入抑郁总分，会造成**暴露-结局的条目重叠（criterion contamination）** → 夸大关联。
> **作者明确把 DPQ030 排除在抑郁评分之外 —— 这是非常专业、非常必要的处理，课程资料做得很好。**
> ★ 这类"同一量表条目同时构成暴露与结局"的陷阱在量表类研究中极常见，**必须逐条目核对**。

### 3.3 问题

| # | 问题 | 严重度 |
|---|---|---|
| N5 | **用 `for + assign` 批量读取会产生大量全局变量**（DEMO_D...DEMO_J、CBC_D...CBC_J、DPQ_D...DPQ_J...） | 🟡 可读性差、易污染环境；建议改为 `lapply(read.xport)` 存入 list |
| N6 | **7 个 2 年周期合并时的权重处理未见明确说明** | 🔴 多周期合并必须 `wt/7`（或使用官方组合权重）；否则权重总量放大约 7 倍。**需核实后 400 行是否有处理** |
| N7 | 子目录切换是手动的（注释："在菜单中 Session-Set Working Directory-Choose Directory… 选择数据的睡眠文件夹"） | 🟠 应改为程序化 `setwd()` 或直接用绝对路径读取 |
| N8 | 未见对**缺失值的系统处理说明**（NHANES 的缺失编码如 7/9/777/999 必须先转为 NA） | 🟠 这是 NHANES 数据清洗的另一大陷阱 |
| N9 | 未见**加权中介分析**的实现细节（`mediation` 包不支持 survey 权重） | 🟠 加权中介需要用 `CMAverse` / 自写 bootstrap，**这是本复现的关键技术难点**，需细读后 400 行 |

---

## 4. 数据资产

| 类别 | 文件 | 周期覆盖 |
|---|---|---|
| 人口学 | `DEMO_B` ~ `DEMO_J`、`P_DEMO` | 1999–2018 |
| 体格/BMI | `BMX`、`BMX_B` ~ `BMX_J` | 1999–2018 |
| 血压 | `BPX`、`BPX_B` ~ `BPX_J`、`BPQ`、`BPQ_B` ~ `BPQ_J` | 1999–2018 |
| 血糖/糖化/OGTT | `DIQ`、`GHB`、`GLU`、`OGTT`、`L10AM` 等（各周期） | 1999–2018 |
| 实验室 | `CBC`、`CRP`/`HSCRP`、`ALB_CR`、`L11`/`L16`/`L25` | 1999–2018 |
| 睡眠/抑郁 | `SLQ`、`DPQ` | 各周期 |
| 吸烟/饮酒 | `SMQ`、`DR1TOT`/`DR2TOT`/`DRXTOT` | 各周期 |
| 运动 | `PAQ`、`PAQIAF` | 各周期 |
| 肾脏 | `KIQ_U` | 各周期 |
| 健康状况 | `MCQ` | 各周期 |
| 合并数据 | `NHANES数据分析资料/new_dat.csv` | 已合并的分析数据集 |

**辅助工具（★ 建议纳入技能资产）**
- `nhanes快速搜索工具.xlsx`
- `综合指标整理.xlsx`

---

## 5. 案例文献（8 篇，覆盖 NHANES 的典型范式）

| # | 主题 | 范式 |
|---|---|---|
| 1 | 脑卒中影响因素 | 关联分析 + 多模型 |
| 2 | 睡眠时间与抑郁 | 关联分析 |
| 3 | **代谢相关性脂肪肝（PS 法）** | **倾向得分**（与第五/七域交叉） |
| 4 | 维生素D | 关联分析 + 剂量反应 |
| 5 | **膳食指数与帕金森（PSM + RCS）** | ★ **PSM + 加权 RCS 组合**（与本域 `NHS_rcs` 直接对应） |
| 6 | **甘油三酯血糖指数与死亡（COX）** | 生存分析（与第一域交叉） |
| 7 | **醛类物质与死亡（贝叶斯核机制回归 BKMR）** | ★★ **混合暴露的交互与联合效应**（BKMR，前沿方法） |
| 8 | **睡眠障碍 × 炎症 × 抑郁（中介）** | ★ 本域主复现文献 |

> ★★ 案例 7（**BKMR / WQS** 类混合暴露分析）是 NHANES 挖掘的一个独立前沿方向 —— **课程脚本中未涉及，是待补的方向**。

---

## 6. 本域能力清单与关键纪律

**已掌握**
- 加权设计构建（`svydesign` + `options(survey.lonely.psu="adjust")` + `nest=TRUE`）
- 加权描述/检验/回归（`svymean`/`svyby`/`svyttest`/`svytable`/`svychisq`/`svyquantile`/`svyglm`/`svycoxph`）
- **加权 RCS 曲线的自写实现**（`svy2rms()` + `NHS_rcs()`）
- 多周期数据合并（`read.xport` + 循环 assign + rbind）
- **检出限（LOD/√2）处理**
- 量表条目重叠的规避（DPQ030 排除）
- 多模型策略 + `ShowRegTable()` 出表
- 加权中介分析（待细读）

**★★★ 五条关键纪律（本域最应内化的）**
1. **必须用 `svy` 系列函数**，不能用 `mean/t.test/chisq.test`（无权重方法会给出有偏估计与过窄 CI）
2. **必须设 `options(survey.lonely.psu = "adjust")`**（否则单 PSU 层导致方差无法估计）
3. **权重必须与研究变量来源匹配**（用实验室指标 → `WTMEC2YR`；访谈 → `WTINT2YR`）
4. **多周期合并时权重必须除以周期数**（或使用官方组合权重）
5. **缺失编码（7/9/777/999）必须先转 NA**；**量表条目重叠必须先逐条核对**

**待办**
- 细读 `文献2-完整版.R` 的后 400 行（加权中介的实现细节 + N6/N8 的核实）
- 视觉精读 8 讲课件（尤其**第五讲 权重介绍**）
- 实跑复现（脚本 `O_nhanes.R`）：加权设计 + 基线表 + 多模型回归 + 加权 RCS
- ★ 补做课程缺失的两项：**加权中介分析**（比 `mediation` 更适合 survey 的 `CMAverse`）+ **BKMR 混合暴露**
- 产出技能：`r-nhanes-analysis`

---
*第一阶段（代码精读）完成时间：2026-09-16*
