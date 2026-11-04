<!-- source: r-propensity-score-methods @ r-propensity-score-methods | domain: stats -->

---
name: r-propensity-score-methods
description: 倾向得分方法（Propensity Score Methods）R 语言全流程实战技能。覆盖混杂偏倚的识别与应对体系、反事实框架与潜在结局、倾向得分的计算与四大用法（PSM 匹配 / PS 分层 / IPTW 加权 / PS 作为协变量回归）、Robins 与 Hernán 两种权重公式、ATT/ATE/ATO 估计量的区别与选择、MatchIt 匹配参数（caliper=0.2 SD 规范）、WeightIt 加权、平衡性诊断（SMD<0.1 而非 P 值）、生存资料加权分析（RISCA::ipw.log.rank、svycoxph）、权重诊断（ESS/权重范围/截断）、缺失数据的倾向得分方法、E-value 敏感性分析。触发场景：用户要做/复现/审阅倾向得分匹配、IPTW、加权分析、观察性研究的混杂控制、真实世界研究、单臂比较基线不均衡的调整，或给出 PSM/IPW 相关 R 代码数据要求代为运行调试纠错。
agent_created: true
---

# 倾向得分方法 · R 全流程实战技能

## 三条铁律（先读）

1. **★★★ 用了 IPTW 权重，就必须用"能正确处理抽样权重的方差估计器"。**
   这是本域**最常被审稿人质疑的错误**：

   | 做法 | 点估计 | **标准误** |
   |---|---|---|
   | `glm(..., weights = w)` | ✓ | **✗ 错误**（`weights=` 被当作**精度权重**，非抽样权重） |
   | `coxph(..., weights = w)` | ✓ | **✗ 错误** |
   | **`svyglm(..., design = svydesign(...))`** | ✓ | **✓ 正确** |
   | **`svycoxph(..., design = ...)`** | ✓ | **✓ 正确** |
   | `coxph(..., weights=w, robust=TRUE, cluster=id)` | ✓ | ✓ 正确（三明治方差） |

   直接用 `weights=` 报出的 **CI 通常过窄**（假阳性风险上升）。

2. **必须先声明估计的是 ATT 还是 ATE。**
   - **PSM 匹配** → 默认 **ATT**（治疗组的平均治疗效应）
   - **IPTW（Robins/Hernán 权重）** → 默认 **ATE**
   - **ATO / 重叠权重** → 只在"临床可均等选择"的人群
   二者临床含义完全不同：ATT 问"对已治疗的人有效吗"，ATE 问"全人群都治疗会怎样"。
   **且 ATE 需要更强的重叠性（positivity）假设。**

3. **平衡性判断用 SMD < 0.1，不用 P 值。**
   加权/匹配后样本量"变大"，P 值会过度敏感（几乎必然显著）。
   Austin 明确建议：**以标准化均数差（SMD）< 0.1 作为平衡标准**。

## 标准流程

```
1. 明确因果问题：暴露 T、结局 Y、候选混杂 X（★ 排除中介）
2. 声明估计量：ATT / ATE / ATO
3. 估计 PS：glm(T ~ X, family=binomial) 或 WeightIt / MatchIt
4. 选择方法（可多法并报作敏感性分析）
   ├ PSM 匹配：matchit(method="nearest", distance="glm", ratio=1,
   │                    caliper=0.2, replace=FALSE, m.order="random")   ← 0.2 = PS 的 0.2 SD
   ├ IPTW 加权：Robins 1/e(X) 与 1/(1−e(X))；Hernán 乘 P(T=1) 稳定化
   └ PS 回归：模型中仅放入 PS
5. ★ 平衡性诊断：SMD < 0.1 + Love plot / PS 分布叠合图
6. ★ 权重诊断（IPTW 必报）：权重范围、均值、**ESS = (Σw)²/Σw²**、极端权重比例
7. ★ 效应估计：svyglm / svycoxph / coxph(robust=TRUE, cluster=id)
8. ★ 敏感性分析：权重截断（1%/99%）、ATT vs ATE、E-value
```

## 关键函数速查

| 需求 | 函数 | 要点 |
|---|---|---|
| 估计 PS | `glm(T ~ X, family = binomial(link="logit"))` + `fitted()` | |
| 匹配 | `MatchIt::matchit(f, data, method="nearest", distance="glm", ratio=1, caliper=0.2, replace=FALSE)` | ★ `caliper` 默认单位是 PS 的 SD |
| 取匹配数据 | `MatchIt::match.data(m_out)` | 会产生 `subclass`（配对/层编号） |
| 平衡性 | `summary(m_out)` + `plot(summary(m_out))` + `plot(m_out, type="jitter"/"hist")` | Love plot / 抖动图 / 直方图 |
| **加权** | `WeightIt::weightit(f, data, method="ps", estimand="ATE", stabilize=TRUE)` | ★ `stabilize=TRUE` 显著降方差 |
| 手工权重 | Robins：`ifelse(T==1, 1/ps, 1/(1-ps))`；Hernán：`ifelse(T==1, pt/ps, (1-pt)/(1-ps))` | `pt` 用 `mean(T)` **不要硬编码** |
| 加权基线表 | `tableone::svyCreateTableOne(..., test=TRUE)` + `svydesign(ids=id, weights=w)` | ★ 平衡看 SMD 不看 P |
| **加权 GLM** | `survey::svyglm(y ~ T, design = svydesign(...))` | ★ 正确 SE |
| **加权 Cox** | `survey::svycoxph(Surv(t,s) ~ T, design = ...)` 或 `coxph(..., robust=TRUE, cluster=id)` | ★ 正确 SE |
| **加权 log-rank** | `RISCA::ipw.log.rank(time, status, treat, weights = w)` | 普通 `survdiff()` 不接受权重 |
| 权重诊断 | `ESS = sum(w)^2 / sum(w^2)`；`range(w)`；`summary(w)` | ★ IPTW 论文必报项 |

## 高频陷阱（24 条完整版见 `references/倾向得分_精学笔记.md`）

**🔴 致命级**
- **`glm(weights=)` / `coxph(weights=)` 直接报 SE** → CI 过窄（见铁律 1）
- **KM 图上的 P 值与 HR 硬编码字符串**：课程匹配前与匹配后用**完全相同的字符串**，
  于是匹配后的 KM 图上显示的仍是**匹配前的** HR → 读者误以为匹配后效应不变。**必须动态生成**
- 脚本中混入**未加 `#` 的中文注释行** → R 解析报错、脚本中断
- **`cluster = subclass` 未加引号/`$`** → 报错（应 `cluster = ~subclass` 或 `d$subclass`）
- **`factor(T + strata(subclass), data = ...)` 括号错位** → 正确应为 `factor(T) + strata(subclass), data = ...`
- `frailty()`、`strata()` 混入 `factor()` 内部的同类括号错误
- 变量名大小写不一致（`age` vs `Age`）→ 报错

**🟠 严重级**
- **权重分布诊断缺失**（应报 ESS、权重范围、极端权重比例）
- **权重截断缺失**（1%/99% 截断 + 敏感性分析）
- **重叠性（positivity）检查缺失**（PS 分布叠合图；重叠差时 ATE 不可靠）
- **未声明 ATT / ATE**
- 平衡性以 P 值而非 SMD 为准
- E-value / 未测量混杂敏感性分析缺失
- PSM 后未报告样本损失（匹配前 n → 匹配后 n）
- `survfit(weights=)` 的 CI 未考虑权重估计的不确定性
- 复制粘贴导致的 design 错配（`svym21` 用了 `e1w2` 而非 `e1w21`）

**🟡 工程级**
- `pt` 硬编码（`73/189`、`689/(689+3972)`）→ 应用 `mean(T)` 或 `glm(T~1)` 拟合值
- `MatchIt` 的 `m.order="random"` 未设种子 → 不可复现
- `factor(x, level=)` 少了 s（靠部分匹配生效）；且与下一行重复因子化
- 注释错误（把分类协变量标为"分组变量"）
- `setwd("D:/...")` 硬编码

## 反事实框架（理解一切 PS 方法的钥匙）

```
e(X) = P(T = 1 | X)      ← 倾向得分
两大定理：
① 平衡性：在 e(X) 的同一水平上，X 与 T 独立 → 只需在 1 个维度上平衡，即可平衡所有 X（降维）
② 无偏性：满足可忽略性 + 重叠性时，e(X) 分层内的效应估计无偏
```

| 效应量 | 含义 | 方法 |
|---|---|---|
| **ATE** | 全人群治疗 vs 全人群不治疗 | IPTW（Robins 权重） |
| **ATT** | 治疗组治疗 vs 治疗组不治疗 | PSM 匹配、ATT 权重 |
| **ATO** | 仅在"临床可均等选择"的人群 | 重叠权重 |

## 相关技能

- 预测模型 / 生存分析 / 竞争风险 → `r-clinical-prediction-model`
- 机器学习与 SHAP → `r-machine-learning-interpretability`
- 孟德尔随机化（工具变量视角的混杂控制）→ `r-mendelian-randomization`
- 老年队列（CHARLS/HRS 等，含多重插补与中介）→ `r-aging-cohort-databases`
- 本机 R 环境调用与 locale 处理 → `local-r-clinical-stats`
