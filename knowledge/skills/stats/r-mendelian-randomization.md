<!-- source: r-mendelian-randomization @ r-mendelian-randomization | domain: stats -->

---
name: r-mendelian-randomization
description: 孟德尔随机化（Mendelian Randomization）R 语言全流程实战技能。覆盖两样本 MR 标准流程（暴露/结局数据读取、p<5e-8 筛选、LD clump、等位基因协调 harmonise_data、IVW/MR-Egger/加权中位数/加权众数估计、OR 转换）、四层水平多效性检验（MR-Egger 截距 / MR-PRESSO / Cochran's Q / 留一法）、弱工具变量 F 值计算、EAF 匹配处理回文 SNP、双向 MR、多变量 MR（MVMR：mr_mvivw/mr_mvegger/mr_mvmedian + 条件 F + Q 统计量）、中介 MR（两步法 vs MVMR 框架）、药靶 MR 与共定位（coloc H4）、肠道菌群 MR、非线性 MR，以及 STROBE-MR 报告规范与 22 条陷阱清单（含 API token 泄露、等位基因方向反转这两个最高危问题）。触发场景：用户要做/复现/审阅孟德尔随机化研究、因果推断、工具变量分析、GWAS 汇总数据挖掘、共定位分析、或给出 MR 相关 R 代码/数据要求代为运行调试纠错。
agent_created: true
---

# 孟德尔随机化 · R 全流程实战技能

## 三条铁律（先读）

1. **效应方向错误是本域唯一的"零提示"致命错误。**
   `effect_allele` / `other_allele` 写反 → **全部 beta 符号系统性反转**，软件不报错、R² 不变、P 值不变，
   但**因果方向完全相反**。
   → **铁律**：拿到结果第一件事是**核对效应方向是否与既往文献一致**；若相反，先查等位基因，别急着讨论。

2. **等位基因协调是全流程技术含量最高、也最容易静默失败的一步。**
   `harmonise_data()` 会**静默剔除**无法协调的 SNP。必须追踪：
   ```r
   table(dat$mr_keep)
   print(dat[!dat$mr_keep, c("SNP","effect_allele.exposure","other_allele.exposure",
                              "effect_allele.outcome","other_allele.outcome",
                              "palindromic","ambiguous")])
   ```
   若 SNP 数从 50 降到 10，**结论可能完全翻转**。
   **回文 SNP（A/T、C/G）**无法从等位基因判断方向 → 必须用 **EAF 匹配**（1000 Genomes 参考频率）解决。

3. **MR 的三条假设只有第一条可检验，另两条靠设计与声明。**
   - 相关性：F 值 / p<5e-8（可检验）
   - 独立性：靠研究设计（同人群、调主成分）（不可直接检验）
   - 排他性：靠**水平多效性检验**作代理（只能部分检验）
   → 因此 **STROBE-MR 要求逐项声明**，且**敏感性分析决定论文上限**。

## 标准两样本 MR 流程（9 步）

```
1. 读暴露：read_exposure_data(本地) / extract_instruments(在线，参数名 outcomes 实指暴露 ID)
2. 筛工具：pval.exposure < 5e-8
3. LD clump：clump_data(clump_kb=10000, clump_r2=0.001)   ← 需 OpenGWAS token
4. 读结局：read_outcome_data(snps=, ...) / extract_outcome_data(snps=, outcomes='ieu-a-7')
5. 等位基因协调：harmonise_data(exp, out, action=2)  ★ 必须查 mr_keep
6. 主分析：mr(dat) → generate_odds_ratios(res) 报 OR(95%CI) 或 β(95%CI)
7. ★ 敏感性分析（四层）
   · mr_heterogeneity(dat)                       Cochran's Q
   · mr_pleiotropy_test(dat)                     MR-Egger 截距
   · run_mr_presso(dat, NbDistribution=5000+)    ★ 课程用 1000，功效不足
   · mr_singlesnp(dat) + mr_leaveoneout(dat)     单 SNP 效应 + 留一法
8. ★ 必补（课程缺失）：directionality_test()  Steiger 方向性检验
   ★ 建议补：mr_radial()                      径向 MR
9. 工具变量强度：单 SNP F 与总 F（推荐 add_rsq() 而非手写公式）
```

完整模板见 `references/孟德尔随机化_精学笔记.md` §1，脚本见第一域 `MR-code.R`。

## 关键函数速查

| 需求 | 函数 | 要点 |
|---|---|---|
| 本地读暴露 | `read_exposure_data(filename, sep, snp_col, beta_col, se_col, effect_allele_col, other_allele_col, eaf_col, pval_col, samplesize_col)` | 列名必须按实际文件改 |
| 在线取工具 | `extract_instruments(outcomes = 'ieu-a-2')` | ★ 参数名 `outcomes` 实际填**暴露 ID**（历史命名缺陷） |
| LD clump | `clump_data(dat, clump_kb=10000, clump_r2=0.001)` | ★ 需 `Sys.setenv(OPENGWAS_JWT=...)`；新版建议 `ieugwasr::ld_clump()` + 本地面板 |
| 协调 | `harmonise_data(exp, out, action=2)` | action：1=假设正链；2=推断（默认）；3=推断+保留报警 |
| 主分析 | `mr(dat, method_list=c("mr_ivw","mr_egger_regression","mr_weighted_median"))` | IVW 主分析；其余为敏感性 |
| OR | `generate_odds_ratios(res)` | 二分类报 OR；连续型报 β |
| 异质性 | `mr_heterogeneity(dat)` | Cochran's Q |
| 多效性 | `mr_pleiotropy_test(dat)` | MR-Egger 截距；★ 功效低，阴性≠无多效性 |
| 离群值 | `run_mr_presso(dat, NbDistribution=5000)` | 三步：全局→离群→剔除重估 |
| 留一法 | `mr_leaveoneout(dat)` + `mr_leaveoneout_plot()` | 看结论是否被单个 SNP 驱动 |
| 方向性 | `directionality_test(dat)` | **Steiger 检验，STROBE-MR 推荐必备** |
| 可视化 | `mr_scatter_plot` / `mr_forest_plot` / `mr_funnel_plot` | 散点/森林/漏斗 |
| **MVMR** | `mr_mvinput(bx, bxse, by, byse)` → `mr_mvivw` / `mr_mvegger` / `mr_mvmedian` | ★ clump r2 放宽到 **0.1** |
| MVMR 弱工具 | `MVMR::strength_mvmr(r_input, gencov)` | 条件 F 值；★ `gencov=0` 是假设不是事实 |
| MVMR 多效性 | `MVMR::pleiotropy_mvmr(r_input, gencov)` | Q 统计量 |
| 共定位 | `coloc::coloc.abf()` → 后验概率 **H4** | H4>0.8 支持共定位 |
| 药靶 MR | 用 eQTL/pQTL 作工具变量，p 阈值可放宽到 1e-5 | 功能性变异少 |

## 高频陷阱（22 条完整版见 `references/孟德尔随机化_精学笔记.md`）

**🔴 致命级**
- **API JWT token 明文硬编码在脚本里**（课程 `MR-code.R` L67）：既是凭据泄露，且该 token 的 `exp` 已过期（2024-08-08）→ 直接跑会失败。**实践中应改为环境变量或 `~/.Renviron`**
- **`setwd(D:\R)`** —— R 中字符串必须加引号，会被解析为对象名 → 脚本首行即报错
- **`exp_dat <- exp_dat.csv`** —— 应为 `read.csv("exp_dat.csv")` → 报错
- **`dat1 <- dat[-c(60,69),]` 硬编码行号删离群值** → 行号依赖排序，应改按 SNP 名删除
- **`Ft <- r3*(338903-2)/(1-r3)` 硬编码样本量** → 换数据集忘记改即总 F 值错误
- **VCF 本地读取 `effect_allele_col="REF"` 疑似写反** → GWAS-VCF 规范中 **ES 对应 ALT**；按课程写法会**全部 beta 符号反转**（**最高危的静默错误**）

**🟠 严重级（方法学完整性）**
- `run_mr_presso(NbDistribution=1000)` —— 课程注释自认应 ≥5000
- **完全缺少 Steiger 方向性检验**（STROBE-MR 推荐必备）
- **完全缺少径向 MR**
- **MVMR 中 `gencov=0` 固定不变** —— 同源数据（如 GSCAN 的吸烟与饮酒）存在样本重叠，应 `phenocov_mvmr()` 估计
- **中介效应用 Sobel 法 + 参数化 Bootstrap + 又转回正态近似**（三处自相矛盾）：
  ① Sobel 功效低于 Bootstrap；② `rnorm(1, beta, se)` 是参数化 Bootstrap（依赖正态）；
  ③ 算出 Bootstrap 分布后又用 `±1.96×sd` 转回正态 → 应直接 `quantile(x, c(.025,.975))`
- 中介 MR 未做 MVMR 框架对照（两步法无法控制 X-M 共同上游）
- **样本重叠（sample overlap）问题全篇未讨论**
- 多重比较校正缺失（多菌群、多暴露场景）
- `harmonise_data` 后未追踪被剔除 SNP 及原因

**🟡 工程级**
- `clump_data()` 在新版已弃用（改 `ld_clump()`，并建议用本地 LD 面板）
- `action=1` 与 `action=2` 在不同脚本间混用，未统一声明
- 手写 F 值公式（建议 `add_rsq()`）
- 大量注释代码与运行代码混排，可读性差
- `setwd("D:/R")` 硬编码；MR-PRESSO/Bootstrap 未设随机种子

## STROBE-MR 报告要点（投稿前逐条打勾）

- 研究设计与假设（三假设逐项说明）
- 数据来源：暴露与结局 GWAS 的人群、样本量、 ancestry、是否重叠
- 工具变量选择：p 阈值、clump 参数、F 值（单 SNP 与总）
- 等位基因协调方法与**被剔除 SNP 的处理**
- 主分析方法（IVW）+ 敏感性分析（MR-Egger / weighted median / mode）
- **方向性检验（Steiger）**
- **多效性检验（截距 + PRESSO + Q + 留一法）**
- 弱工具偏倚的讨论
- 样本重叠与人群分层的说明
- 局限性：MR 假设不可完全检验、线性假设、单一 ancestry 的外推限制

## 常用 GWAS 资源（课程数据来源）

| 资源 | 用途 |
|---|---|
| **IEU OpenGWAS**（`ieu-a-*`、`ebi-a-*`、`ukb-*`） | 在线提取暴露/结局，`extract_instruments` / `extract_outcome_data` |
| **TwoSampleMR** | 主分析包 |
| **MVMR** | 多变量 MR |
| **coloc** | 共定位 |
| GIANT（BMI）、CARDIoGRAMplusC4D（CAD）、GSCAN（吸烟/饮酒）、GCST90020053（虚弱指数） | 课程实操数据集 |
| 1000 Genomes / PLINK 频率文件 | EAF 匹配、本地 clump |

## 相关技能

- 预测模型 / 生存分析 / 竞争风险 → `r-clinical-prediction-model`
- 机器学习与 SHAP → `r-machine-learning-interpretability`
- 本机 R 环境调用与 locale 处理 → `local-r-clinical-stats`
- 论文撰写与润色 → 中文 `chinese-medical-paper-writer`；英文 `sci-writing-master`
- 文献检索与批量下载 → `reference-retrieval-skill` / `nature-literature-pipeline`
