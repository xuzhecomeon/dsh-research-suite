---
name: r-trajectory-models
description: 纵向数据轨迹模型（组基轨迹模型 GBTM / 潜类别增长模型 LCGM / 多变量轨迹 GBMTM）R 语言实战技能。覆盖宽转长的多变量多时间点整形（pivot_longer + .value + names_pattern）、gbmt 包与 lcmm 包两条技术路线、模型选择的四项核心指标（AIC/BIC/CIC/SABIC + Avepp>0.7 + OCC>5 + 组占比 + entropy）、gridsearch 多随机起点处理局部最优、轨迹图绘制（总图/单组/未来外推）、轨迹分组提取与合并、多项 logistic 回归、以及 GRoLTS Checklist 报告规范。触发场景：用户要做潜类别轨迹分析、GBTM/LCGM/GMM/GBMTM、重复测量数据的异质性轨迹识别、轨迹分组后的结局分析，或给出轨迹模型相关 R 代码数据要求代为运行调试纠错。
agent_created: true
---

# 纵向轨迹模型 · R 实战技能

## 四条铁律（先读）

1. **★★★ 比较不同组数的模型时，多项式阶次必须统一。**
   本仓课程代码中 `gbtm3` 用了 `d=3` 而 `gbtm1/gbtm2/gbtm4/gbtm5` 用 `d=2` →
   **AIC/BIC 不可比、模型选择结论无效**。这是轨迹分析最严重的方法学错误。

2. **不只看 BIC 最小 —— 必须四项指标综合判断。**

   | 指标 | 判读标准 | 含义 |
   |---|---|---|
   | **AIC / BIC / SABIC / CIC** | 越小越好 | 拟合优度 vs 复杂度 |
   | **Avepp**（平均后验概率） | **> 0.7** | 每个轨迹组内个体被正确归类的平均概率 |
   | **OCC**（正确分类几率） | **> 5** | `(Avepp/(1−Avepp)) / (prior/(1−prior))` |
   | **Entropy** | 越接近 1 越好 | 分类清晰度（lcmm 提供） |
   | **组占比** | 每组 ≥ 5% | 过小的组不稳定 |

   → 只看 BIC 会得到"某组只有 3 人"的模型。**必须 + 临床可解释性**。

3. **`lcmm` 必须用 `gridsearch` 多随机起点。**
   潜类别模型的似然面有大量局部最优；单起点拟合可能收敛到局部最优 →
   loglik 偏小、类别解不稳定、换个起点得到完全不同的类别结构。
   ```r
   m2_gs <- gridsearch(rep = 100, maxiter = 10, minit = m1,   # m1 = ng=1 的稳定种子
                       hlme(fixed = y ~ 1+time+I(time^2), mixture = ~ 1+time+I(time^2),
                            ng = 2, subject = "ID", data = long_data))
   lcgm2a <- hlme(..., ng = 2, B = m2_gs$best, maxiter = 200)   # ★ 用最优起点精跑
   lcgm2a$loglik; lcgm2$loglik     # ★ 必须报告 loglik 对比以证明收敛
   ```

4. **轨迹模型的报告规范是 GRoLTS Checklist**（与 TRIPOD / STROBE-MR 同级）。
   投稿前必须逐项对照。核心报告项：模型选择指标、类别数与占比、Avepp/OCC、轨迹图形、命名依据、缺失处理、软件与版本。

## 标准流程

```
1. 宽转长（多变量 × 多时间点）
   long <- pivot_longer(wide, cols = starts_with(c("y1","y2")),
                        names_to = c(".value","time"), names_pattern = "(.+)(.)")
   long$time <- as.numeric(long$time)
2. 建模（两条路线）
   A. gbmt 包：gbmt(x.names=, unit=, time=, d=, ng=, data=, scaling=)
   B. lcmm 包：hlme(fixed=, mixture=, ng=, subject=, data=) + gridsearch
3. 模型选择：跑 ng = 1..5 → 汇总 AIC/BIC/CIC/SABIC/entropy/Avepp/OCC/组占比
4. 绘图：plot(model, bands=F) / plot(model, group=k) / plot(model, n.ahead=)
5. 分组提取：rownames_to_column(data.frame(group = model$assign), var="ID")
6. 合并回宽数据 → ★ 按轨迹高低重新编号（否则 Class 1 含义由算法随机决定）
7. 后续分析：基线表（strata=group）+ 多项 logistic（multinom）+ 生存分析等
```

## 关键函数速查

| 需求 | 函数 | 要点 |
|---|---|---|
| 宽转长 | `tidyr::pivot_longer(names_to=c(".value","time"), names_pattern="(.+)(.)")` | ★ 多变量 × 多时间点的标准范式 |
| GBTM（简便） | `gbmt::gbmt(x.names, unit, time, d, ng, data, scaling=0)` | `d` = 多项式阶次；`ng` = 组数 |
| LCGM/GMM | `lcmm::hlme(fixed, mixture, ng, subject, data)` | `mixture` 在 ng>1 时必设 |
| 多起点 | `lcmm::gridsearch(rep=100, maxiter=, minit=, hlme(...))` | ★★ 避免局部最优 |
| 指标汇总 | `lcmm::summarytable(m1..m5, which=c("G","loglik","AIC","BIC","SABIC","entropy","%class"))` | 一次给全 |
| Avepp | `model$appa`（gbmt）/ `model$pprob`（lcmm） | 要求 > 0.7 |
| OCC | `(appa/(1-appa)) / (prior/(1-prior))` | 要求 > 5 |
| 组占比 | `prop.table(table(model$assign))` | 每组 ≥ 5% |
| 绘图 | `plot(model, bands=F, titles=, xlab=, ylab=)` | `bands=F` 不画 CI |
| 未来外推 | `plot(model, n.ahead=3)` | ★ 多项式外推风险大，需谨慎 |
| 分组提取 | `tibble::rownames_to_column(data.frame(group=model$assign), var="ID")` | ★ 命名向量→数据框 |
| 多轨迹 | `gbmt(x.names = c("y1","y2","y3"), ...)` | ★ 与单变量版**唯一区别** |
| 多项 logistic | `nnet::multinom(group ~ x1 + x2) %>% broom::tidy(exponentiate=TRUE)` | 直接给 OR |

## 高频陷阱

**🔴 致命级**
- **模型比较时多项式阶次不一致**（如 `ng=3` 用 `d=3` 而其余用 `d=2`）→ AIC/BIC 不可比，模型选择结论无效
- **`lcmm` 不用 `gridsearch`** → 可能收敛到局部最优，类别解不可信

**🟠 严重级**
- 只看 BIC 不报 Avepp / OCC / 组占比
- `ggplot(long, aes(x=time, y=y, group=ID)) + geom_line()` → **画全部个体轨迹（数千条）→ 糊图**；
  应画**分组平均轨迹 ± CI**，或抽样作 spaghetti plot
- `gbmt()` 未设随机种子（轨迹模型含随机初始化 → 不可复现）
- 用 `n.ahead` 外推未来轨迹却未讨论不确定性
- 未对照 GRoLTS Checklist

**🟡 工程级**
- `plot(model, group=k)` 分多张图未合并（建议 `patchwork`）
- `pad_vectors()` 的"行=类别数、列=组数"语义易混淆
- 多个模型（直接拟合 vs gridsearch 精跑）并存但未说明以哪个为准

## 三类研究设计的区分（选题时最重要）

| 设计 | 轨迹的角色 | 案例（本仓） |
|---|---|---|
| 轨迹作**暴露** | 轨迹分组 → 预测结局 | 尿量轨迹 → 脓毒症 AKI |
| 轨迹作**结局** | 暴露 → 轨迹分组 | 社会/智力活动 → 认知轨迹 |
| 轨迹作**预测因子** | 轨迹 → 进入预测模型 | 步速轨迹 → 列线图 |

## 相关技能

- 预测模型（轨迹作预测因子时）→ `r-clinical-prediction-model`
- 老年队列（认知/衰弱轨迹数据来源）→ `r-aging-cohort-databases`
- 生存分析（轨迹分组后做生存曲线）→ `r-clinical-prediction-model`
- 本机 R 环境调用 → `local-r-clinical-stats`
