---
name: r-aging-cohort-databases
description: 七大老年数据库（HRS 家族 + CHARLS）数据挖掘 R 语言实战技能。覆盖公共老年队列数据的获取与注册、Harmonized 数据（跨库可比变量体系）的使用、CHARLS 原始数据（.dta）与 Codebook 对照、变量构建与编码表核查，以及全套统计分析流程：tableone 基线差异、单因素/多因素 Cox、多模型策略（未调整→部分调整→完全调整）、缺失数据多重插补（按变量类型指定 pmm/logreg/rf 方法）、趋势性分析（组中位数作节点值）、RCS 限制立方样条剂量-反应曲线、中介分析（mediation/CMAverse）、亚组分析与交互作用（jstable）、森林图（forestploter）。触发场景：用户要用 CHARLS/HRS/ELSA/SHARE/MHAS/TILDA 等老年队列做研究、环境暴露与老年健康、衰弱/认知/慢病结局、公共数据库挖掘论文，或给出相关 R 代码数据要求代为运行调试纠错。
agent_created: true
---

# 七大老年数据库 · R 分析实战技能

## 三条铁律（先读）

1. **先确认随访时间是"离散波次"还是"连续时间"。**
   本域课程数据 `time` 只有 **7–9 个唯一值** —— 这是 **CHARLS 的随访波次编号**，不是连续时间（年/月）。
   - 用 Cox 处理 → 同一时点有**大量并列事件（ties）**，Breslow/Efron 近似精度下降，
     且**离散时间下"风险集"的定义与连续时间模型的前提不符**
   - **正确路径两条**：① 改用 **cloglog 离散时间模型**（把数据展开为"人-波次"格式，
     `glm(event ~ time + ..., family = binomial(link = "cloglog"))`）；
     ② 若坚持 Cox，必须说明 ties 处理方法并在局限性中讨论
   > 本域课程的 8 个统计模块**全部用 Cox 且从未讨论这一点** —— 这是最重要的方法学缺口。

2. **中介分析不能用 `survreg` 喂给 `mediation::mediate()`。**
   `mediate()` 要求 `out.model` 是 **lm / glm 类**；`survreg` 返回 `survreg` 类 → 报错。
   正确做法：① 把结局二分类化后用 `glm`；② 用专门支持生存中介的
   `CMAverse` / `medflex` / `regmedint`；③ 或改用参数 AFT 框架并自行实现。

3. **多重插补的参数要达规范，且自定义方法必须真的传进去。**
   - `m`（插补数据集数）：课程用 **3**（并自认"通常为 5"）→ 现代建议 **m ≥ 20**（甚至 100×缺失率）
   - `maxit`：课程用 **20**（自认"通常为 50"）→ 应至收敛
   - ★★ **定义了 `meth` 却没传给 `mice()`** —— 自定义插补方法会**完全失效**（课程即犯此错）

## 标准分析流程（8 模块）

```
1. 数据导入 + 分类变量因子化
   ★ 有序分类（education/drink/smoke）用 factor() 会变无序；若做趋势分析应按数值处理
2. tableone 基线差异分析（★ 显式声明 nonnormal 变量，不要全靠自动判定）
3. 单因素 + 多因素 Cox
4. ★★ 多模型策略：模型1 未调整 → 模型2 部分调整 → 模型3 完全调整
   （环境流行病学黄金标准，展示效应估计的稳健性）
5. 缺失数据多重插补 → 回归
   · 按变量类型指定方法：pmm（连续）/ logreg（二分）/ rf 或 polyreg（多分类）
   · ★ method = meth 必须传给 mice()
   · 合并用 pool() ★ 不是 pool.syn()
6. 趋势性分析（四分位 → 取组中位数作节点值 → 线性趋势 P）
   + RCS 限制立方样条（cph + rcs(x, 4) + anova() 看 P for nonlinear + Predict() 出 HR 曲线）
7. 中介分析（X → M → Y）
8. 亚组分析 + 交互作用（jstable::TableSubgroupMultiCox）+ 森林图（forestploter::forest）
```

## 关键函数速查

| 需求 | 函数 | 要点 |
|---|---|---|
| 基线表 | `tableone::CreateTableOne(vars, strata, factorVars, data, addOverall=TRUE)` | ★ `print(..., nonnormal=)` 显式声明偏态变量 |
| 单/多因素 Cox | `coxph(Surv(time, status) ~ ...)` | ★ 离散时间数据慎用（见铁律 1） |
| 单多因素合并表 | `autoReg::autoReg(fit, uni=TRUE, milti=TRUE, threshold=0.05)` | 一次输出单/多因素 |
| 缺失模式 | `VIM::aggr(d, numbers=TRUE, sortVars=TRUE)` | 可视化缺失模式 |
| **多重插补** | `mice::mice(d, m=20, maxit=50, seed=, method=meth)` | ★ **method=meth 必须传** |
| 插补方法指定 | `make.method()` → `meth["age"]<-"pmm"`；`meth[cat]<-"logreg"`；`meth[multi]<-"rf"` | 按变量类型分层指定 |
| **合并插补结果** | `pool(with(imp, coxph(...)))` | ★ **不是 `pool.syn()`** |
| 趋势分析 | 四分位分组 → `group_by %>% mutate(trend = median(x))` → Cox | 组中位数作节点值 |
| **RCS** | `cph(Surv ~ rcs(x, 4) + ..., data)`；`anova(rcs1)`；`Predict(rcs1, x, fun=exp, ref.zero=TRUE)` | ★ `datadist()` 必须先设；**P 值要动态取不要硬编码** |
| 中介分析 | `mediation::mediate(med.fit, out.fit, treat, mediator, sims=1000)` | ★ `out.fit` 须 lm/glm；连续暴露须给 `treat.value`/`control.value` |
| 亚组分析 | `jstable::TableSubgroupMultiCox(formula=Surv~X, var_subgroups=c(...), data)` | 一次给出各亚组 HR + P for interaction |
| 森林图 | `forestploter::forest(data, est, lower, upper, ci_column, ref_line)` | ★ 列名不要硬编码 |

## 高频陷阱（20 条完整版见 `references/七大老年数据库_精学笔记.md`）

**🔴 致命级**
- **`pool.syn(fit)`** —— `pool.syn()` 属 `mitools`/合成数据，**不适用于 `mice` 的 `mira` 对象** → 应 `pool(fit)`
- **定义了 `meth` 却没传给 `mice()`** → 自定义插补方法完全失效
- **`survreg` 喂给 `mediate()`** → 报错（见铁律 2）
- **RCS 图上的 "P for nonlinear" 是硬编码文本** → 换数据后图上的 P 值是错的，而代码不报错
- **RCS 参考线数值与注释不一致**（注释提到 VD/维生素 D → 明显是从别的分析复制粘贴残留）

**🟠 严重级**
- **离散随访波次却全程用 Cox**（见铁律 1）
- **`m=3, maxit=20` 低于规范**（课程自认）
- **完全缺 PH 假设检验**（`cox.zph`）
- **中介分析未指定对比量**：`mediate(treat="PM25")` 对连续暴露默认按 1 单位 → 应显式给 IQR/10 μg/m³
- **多重比较校正缺失**（亚组分析多水平）
- 因果中介的双向敏感性分析缺失（E-value）
- 亚组森林图列名硬编码（`names(plot_df) <- c(...)` → jstable 版本变即静默错位）
- `datadist(x)` 设置后未重置 → 后续数据集 `cph`/`lrm` 会用错 datadist
- tableone 未显式指定 `nonnormal`

**🟡 工程级**
- `setwd("D:/BaiduSyncdisk/...")` 硬编码含个人网盘路径
- `read.csv()` 未指定 `fileEncoding`
- 随机种子仅局部设置
- **可识别 ID（如 12/18 位编码）未脱敏**
- 高度相关变量同时入模（tyg/bmi/tygbmi/newglu/newtg）未报 VIF

## 公共数据库通用要点

**Harmonized 数据（第三讲核心）**
- Gateway to Global Aging Data 提供**跨库可比的 Harmonized 变量**
- 变量命名有固定前缀规则（如 `r` + 波次 + 变量名，`h` 前缀为 household 层）
- ★ 使用时必须对照 **Harmonized Codebook**，并核对原始问卷（`CHARLS_2020_Questionnaire`）
- **变量构建后要与 Codebook 逐条比对编码**（缺失码 9/99、跳转逻辑）

**样本量与权重**
- 老年队列多数是**复杂抽样设计** → 描述性统计需考虑权重（`survey` 包）
- 本域课程的 `data.csv` 已做完整案例筛选（5569/5675），**论文中必须报告筛选流程与排除例数**

**效应量表述**
- 对"每单位"效应很小的连续暴露（如 PM2.5 的 HR≈1.01），应报告
  **每 IQR 或每 10 μg/m³ 的 HR**，否则读者会误判为"无效应"

## 相关技能

- 倾向得分 / IPTW / 混杂控制 → `r-propensity-score-methods`
- 预测模型 / 列线图 / RCS 生存分析 → `r-clinical-prediction-model`
- 孟德尔随机化（遗传工具变量）→ `r-mendelian-randomization`
- NHANES 数据挖掘（同为公共数据库范式）→ 见第八域笔记
- 本机 R 环境调用与 locale 处理 → `local-r-clinical-stats`
