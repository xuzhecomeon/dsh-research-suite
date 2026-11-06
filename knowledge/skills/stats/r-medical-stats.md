---
name: r-medical-stats
description: R 语言医学统计与科研绘图通用引擎（双模式）。模式A【直接执行】：自动完成环境自检、读取用户数据、按需求执行统计分析并输出投稿级别的统计图与统计表，统计图默认交付可编辑 SVG（文本保持为 <text> 元素，可在 Illustrator/Inkscape 中改字号、改颜色、改标注）。模式B【生成代码】：当运行环境无法调用 R（如 ima 等不具备本地 R 的场景），或用户明确要求自己跑时，根据用户提供的数据表格生成自包含、可直接在 R/RStudio 中运行的完整统计与绘图脚本，含包安装检查、集中配置区、逐步注释与输出落盘。覆盖：描述性统计与基线表（表 1/三线表）、t 检验/方差分析/卡方/秩和、线性与 Logistic 回归、Cox 生存分析、ROC/AUC、校准曲线、决策曲线 DCA、列线图、RCS 剂量-反应曲线、森林图、KM 曲线、倾向得分匹配与 IPTW、中介分析、重复测量与混合模型（球对称校正/GEE/ICC）、缺失数据插补、机器学习与 SHAP、MLR3 工作流、孟德尔随机化、样本量与效能估算、多重比较校正、判别分析与一致性（Kappa/ICC/Bland-Altman）、期刊配色与色盲安全出图、R 包选型（什么任务用什么包）、tidyverse 数据整理、临床试验设计与统计（ITT/ANCOVA/成组序贯/多重比较）、常用科研图代码骨架（森林图/KM/热图/气泡图/列线图-ROC-校准-DCA 图组）、TRIPOD 报告规范。触发场景：任何「用 R 做医学统计」「画统计图」「做统计表」「做基线表」「投稿出图」「给我 R 代码」「帮我分析这份数据」「算样本量」「重复测量/球对称」「多重比较校正」「一致性分析」「该用哪个 R 包」「机器学习+SHAP 预测模型」「临床试验设计」的需求；不确定用哪个统计方法；需要可编辑矢量图；或给出 R 代码要人代为运行调试。
agent_created: true
---

# R 语言医学统计 · 通用引擎（双模式）

> **本技能是「引擎」，负责"怎么算、怎么画、怎么交付"；各研究领域"该用什么方法、该防什么坑"见 `references/07_domain_methodology.md`（已内置，无需任何外部技能）。**

---

## 〇、开工前必做：判断走哪条路

```
第 0 步：确认运行环境是否具备 R
├── 有 R（能执行 Rscript）→ 【模式A 直接执行】§1
└── 无 R（或用户明确要求自己跑）→ 【模式B 生成代码】§2
```

**如何判断**：尝试 `Rscript --version`（或技能环境中的等效方式）。
- 失败 → 走模式 B（**不要因为"没有 R"就拒绝任务**，生成代码同样是有价值的交付）
- 成功 → 走模式 A；但若用户说"给我代码我自己跑"，仍走模式 B

---

## 〇·补、环境实测陷阱速查（2026-09 本机 R 4.6.1 实测，踩过必查）

> 以下 7 条在**本机与多数新版 R 上都会真实触发**，且报错信息与病因往往对不上号，先查这里再查库内文档。

| # | 现象 / 报错 | 真实原因 | 正确写法 |
|---|---|---|---|
| 1 | `Rscript -e "含中文的代码"` → **Segmentation fault (exit 139)** | Windows 下命令行参数编码与 R 解析冲突 | **中文一律不过命令行**：写成 UTF-8 **无 BOM** 的 `.R` 文件再 `Rscript file.R` |
| 2 | `cannot open the connection`（读数据/存数据时报） | 90% 是**上级目录不存在**，不是文件路径写错 | `dir.create("data", showWarnings = FALSE)` 先建目录再 `save()`/`write_*()` |
| 3 | `could not find function "coxph"`，但你只调了 `survival::clogit()` | `clogit()` 内部在**调用方环境**查找 `coxph()`，命名空间前缀不够 | 必须 `library(survival)` 显式 attach |
| 4 | `could not find function "tidy"` | `tidy()`/`glance()` 属 **broom**，不在 tidyverse 核心包内 | `library(broom)` |
| 5 | `need at least two non-NA values to interpolate` | 完全分离（separation）时 `confint()` 的 profiler 失效 | `try(exp(confint(m)))` 包住；或直接用 `logistf()` / `brglm2` |
| 6 | mlr3 系列报错 `unused argument (stratify=)`、`Element with key 'pima' not found`、`has additional elements {'weight'}`、`Supervised tasks need at least one target column` | **mlr3 1.8 的 API 漂移**（详见 `references/31~33` 开头的兼容表） | `tsk("diabetes")`；分层用 `set_col_roles(col, roles="stratum", add_to="target")`；权重角色用 `weights_learner` |
| 7 | `LoadLibrary failure: 应用程序控制策略已阻止此文件` | 本机 AppLocker/WDAC 拦截该包 DLL | 重装一次常可恢复；仍失败则该包在本机不可用，走替代方案 |

**另有两个高频环境事实**：
- **中文字体**：出 SVG 时若中文变方框，需在 `theme()` 指定 `family = "SimSun"` / `"Microsoft YaHei"`，并确认 `showtext` 或 `cairo_pdf` 可用。
- **CRAN 镜像**：本机用清华镜像 `https://mirrors.tuna.tsinghua.edu.cn/CRAN/`；不加会显著变慢甚至超时。

---

## 一、模式 A：直接执行（Agent 有 R 环境）

### 1.1 五步工作流

```
① 环境自检
   · R 是否可用、版本
   · 所需包是否齐备（缺则装，国内用清华镜像）
   · locale 是否能正常输出中文（Windows 见 §4.1）
   · 输出目录是否存在（自动创建）

② 数据导入与六道闸门（★ 不可跳过，见 §5）
   列类型 → 不可能值 → 缺失率与模式 → 事件数与 EPV → 参数个数与性能合理性 → 方向核对
   → 任何一道不过，先停下来报告，不要带着问题往下算

③ 方法选择
   按 §6 的决策树确定方法；按 §7 对照表确定图表类型与输出格式

④ 执行分析
   · 用超时保护包裹长任务（Bootstrap/交叉验证可能耗时）
   · 把全部关键结果同时写入 UTF-8 结果文件（不要只依赖控制台）
   · ★ 长任务串行执行，不要并发跑多个 R 进程写同一文件

⑤ 交付
   · 统计结果：文字汇总（含效应量 + 95%CI + 精确 P 值）
   · 统计图：SVG（可编辑，必需）+ PDF（投稿用）+ PNG 300dpi（预览/备用）
   · 统计表：DOCX 或 XLSX（可编辑）
   · 分析脚本：一并交付，便于复现与修改
```

### 1.2 交付物清单（每次都要齐）

| 交付物 | 格式 | 说明 |
|---|---|---|
| **统计图** | **`.svg`（必须）** | 可编辑矢量图，文本保持 `<text>`，可在 AI/Inkscape 改字号/颜色/标注 |
| 统计图（投稿用） | `.pdf` | 多数期刊首选矢量格式 |
| 统计图（备用） | `.png` 300–600 dpi | 部分期刊要求位图 |
| **统计表** | `.docx` 或 `.xlsx` | ★ 表格不用 SVG（不便于编辑与排版），用 Word/Excel |
| 统计结果 | `.txt`（UTF-8） | 完整数值结果，便于核对 |
| **分析脚本** | `.R` | 用户可自行复核、修改、复跑 |

> ★ **一定要同时给 SVG**：期刊审稿常要求修改图的细节（字号、颜色、标签），
> 只有可编辑矢量图才能改；位图（PNG/TIFF）和部分 PDF 无法精细编辑。

---

## 二、模式 B：生成代码（无 R 环境，或用户自跑）

### 2.1 核心原则

**生成的脚本必须是"人类可读、可改、可复现"的，不能是黑箱。**

### 2.2 脚本的固定结构（六段式）

```r
# =====================================================================
# 【项目名】医学统计分析脚本
# 生成时间：____  |  用途：____
# 使用方法：① 安装 R 与 RStudio ② 修改下方【配置区】的路径与变量名
#           ③ 全选运行（Ctrl+Shift+Enter）④ 结果输出到 out_dir
# =====================================================================

## ========== 0. 配置区（★ 只需改这里） ==========
CFG <- list(
  data_path = "D:/mydata/data.csv",   # ← 改成你的数据文件路径
  out_dir   = "D:/mydata/output",     # ← 结果输出目录
  # —— 变量名（改成你数据里的实际列名）——
  outcome   = "outcome",              # 结局变量
  exposure  = "exposure",             # 暴露/分组变量
  time      = NULL,                   # 生存时间（无生存分析则留 NULL）
  status    = NULL,                   # 生存状态
  covariates= c("age","sex","bmi"),   # 协变量
  cat_vars  = c("sex"),               # 其中哪些是分类变量
  # —— 分析选项 ——
  do_baseline = TRUE, do_regression = TRUE, do_survival = FALSE,
  do_roc = TRUE, do_dca = TRUE, do_forest = TRUE,
  export_svg = TRUE, export_pdf = TRUE, export_png = TRUE
)

## ========== 1. 环境准备（自动装包，只装缺失的） ==========
need <- c("tableone","survival","survminer","pROC","rms","rmda",
          "ggplot2","patchwork","svglite","flextable","officer","dplyr")
for (p in need) if (!requireNamespace(p, quietly=TRUE))
  install.packages(p, repos = "https://mirrors.tuna.tsinghua.edu.cn/CRAN/")
invisible(lapply(need, library, character.only = TRUE))
dir.create(CFG$out_dir, showWarnings = FALSE, recursive = TRUE)

## ========== 2. 读数据 + 数据质量检查 ==========
## ========== 3. 统计分析（每步 print 关键结果）==========
## ========== 4. 出图（SVG + PDF + PNG 三格式）==========
## ========== 5. 出表（DOCX）==========
## ========== 6. 结果落盘 + 运行总结 ==========
```

### 2.3 生成代码时必须做到的 9 件事（第 9 条为注释规范，详见 `references/09_代码注释规范.md`）
## 9.【需修改】标记：所有依赖本地环境的值（数据路径/输出目录/变量名/项目名）必须
##    集中在配置区并标注【需修改】；正文零硬编码路径。其他 agent 平台的用户只改配置区。

| # | 要求 | 原因 |
|---|---|---|
| 1 | **顶部集中配置区**，只改配置不改逻辑 | 用户不会写 R，但会改字符串 |
| 2 | **自动装包 + 清华镜像** | 国内直连 CRAN 常失败 |
| 3 | **自动创建输出目录** | `dir.create(..., recursive=TRUE)` |
| 4 | **每一步 `cat()` 出中文提示** | 用户要知道"跑到哪了、这一步在干嘛" |
| 5 | **关键结果 `print()` 出来** | 用户看不到对象内容会以为没跑成功 |
| 6 | **变量名集中声明**，不散落在各段 | 便于替换 |
| 7 | **出错时给可操作的提示** | 如 `if (!file.exists(...)) stop("找不到数据文件，请检查 CFG$data_path")` |
| 8 | **末尾输出"结果清单"** | 告诉用户生成了哪些文件、在哪 |

### 2.4 附一份《运行说明》

除脚本外，还要给一份简短说明：R 与 RStudio 下载地址、如何修改路径、如何全选运行、
常见报错对照（找不到文件 / 包安装失败 / 中文乱码 / 内存不足）。

---

## 三、★★★ SVG 投稿级出图（本技能的核心要求）

### 3.1 首选方案：`svglite`

```r
library(svglite)

svglite("Fig1.svg", width = 7, height = 5,          # 英寸
        system_fonts = list(sans = "Arial",          # ★ 指定字体，保证跨机器一致
                            serif = "Times New Roman"))
print(p)          # p 是 ggplot / patchwork 对象
dev.off()
```

**为什么必须用 `svglite` 而不是内置 `svg()`**
- `svglite` 把文字写成 **`<text>` 元素** → 在 Illustrator/Inkscape 中**可直接改字号、颜色、内容、字体**
- R 内置 `svg()` 设备在某些情况下会把文字**转成路径（outline）** → 变成"死图"，改不了
- `svglite` 还支持 `system_fonts` 指定字体，避免换机器后字体回退

### 3.2 三格式同时输出（推荐封装成函数）

```r
save_fig <- function(p, name, w = 7, h = 5, base = CFG$out_dir) {
  if (CFG$export_svg) svglite::svglite(file.path(base, paste0(name, ".svg")), w, h,
                                       system_fonts = list(sans="Arial", serif="Times New Roman"))
  if (CFG$export_svg) { print(p); dev.off() }
  if (CFG$export_pdf) ggsave(file.path(base, paste0(name, ".pdf")), p, width=w, height=h, device=cairo_pdf)
  if (CFG$export_png) ggsave(file.path(base, paste0(name, ".png")), p, width=w, height=h, dpi=300)
  cat("  ✔ 已保存：", name, ".svg / .pdf / .png\n", sep="")
}
```

### 3.3 让 SVG 真正"可编辑"的 6 条实践

| # | 做法 | 说明 |
|---|---|---|
| 1 | 用 `svglite` 而非 `svg()` | 文本保持 `<text>` |
| 2 | `system_fonts` 显式指定字体 | 避免字体回退导致的排版错位 |
| 3 | **不要在出图时把图拼成位图** | 如 `grid::rasterGrob` / 图片插入会破坏矢量性 |
| 4 | 多面板用 `patchwork` / `cowplot` 拼 | 拼完整体输出 SVG，子图文本仍可编辑 |
| 5 | 图中文字尽量用 `geom_text`/`annotate` 而非图片 | 保证文字是文本元素 |
| 6 | 中文图：先用 `showtext` 注册中文字体，或 `system_fonts` 指定中文字体 | 否则 SVG 里中文可能变方块 |

### 3.4 多面板 SVG 示例（patchwork + svglite）

```r
library(patchwork)
p_all <- (p1 | p2) / (p3 | p4) +
  plot_annotation(tag_levels = "A")     # ★ A/B/C/D 标号
svglite("Fig2_composite.svg", width = 10, height = 9)
print(p_all)
dev.off()
```

### 3.5 期刊格式要求对照（交付前核对）

| 格式 | 适用 | 要点 |
|---|---|---|
| **SVG** | **可编辑源文件**（自己留档 + 返修时改图） | 文本可编辑 |
| PDF / EPS | 多数期刊**首选矢量** | 字体需嵌入；线条 ≥ 0.25 pt |
| TIFF | 部分期刊要求位图 | 300–600 dpi，LZW 无损压缩 |
| PNG | 预览、PPT、网页 | 300 dpi 以上 |
| **不要用 JPG** | — | 有损压缩，线条出现伪影 |

**通用规范**：字体 Arial 或 Times New Roman；字号 7–10 pt（终稿尺寸下）；线宽 ≥ 0.25 pt；
配色考虑色盲友好（`ggsci` / `viridis`）；避免纯红绿对比。

---

## 四、环境自检与跨 Agent 调用

### 4.1 ★ Windows 下的 locale 陷阱（必查）

若 R 出现「包加载失败 / 含中文的路径失效 / `installed.packages()` 返回 0 个包 / 中文乱码」，
**根因通常是外壳注入的 POSIX locale 变量**（`LC_ALL=C.UTF-8` 等），Windows 版 R 无法识别。

**处理**：调用 R 前先清除这三个环境变量（**只清空，不需赋值**）。

### 4.2 输出重定向（★ 不要依赖控制台）

控制台回显 UTF-8 中文常乱码，且部分环境的 stdout 不被捕获。**一律写入文件再读回**：

```r
con <- file("results.txt", open = "wt", encoding = "UTF-8")
sink(con); sink(con, type = "message")
# ... 全部分析与 cat() 输出 ...
sink(type = "message"); sink(); close(con)
```

### 4.3 脚本文件编码

**R 脚本必须保存为无 BOM 的 UTF-8**。带 BOM 时 R 会报 `unexpected input in "锘"` 并中止。
（Windows PowerShell 的 `Out-File -Encoding UTF8` 会产生 BOM，注意规避。）

### 4.4 长任务处理

- Bootstrap / 交叉验证 / 多次插补可能耗时数分钟到数十分钟 → **加超时保护，必要时后台运行**
- ★ **串行执行**：并发跑两个 R 进程写同一输出文件会互相拖慢（实测曾出现单脚本 1.5 小时未收敛，串行后 35 秒完成）
- 先跑"轻量段"（描述性统计、建模），把"重量段"（Bootstrap、多重插补、网格搜索）放在后面单独跑

### 4.5 无法调用 R 时的降级策略

| 情况 | 处理 |
|---|---|
| 无 R | 走**模式 B** 生成代码（不是"做不了"） |
| 有 R 但缺包且装不上 | ① 换清华镜像 ② 用替代包 ③ 手写公式实现（如 TwoSampleMR 已归档 → 手写 IVW/MR-Egger） |
| 图无法生成 | 至少交付统计结果 + 出图代码，并说明失败原因 |

---

## 五、★★★ 数据质量六道闸门（任何分析开始前必跑）

**这六道能拦住绝大多数致命错误，且它们的共同点是：不跑就完全不会发现。**

```r
## 闸门 1：列类型核查 —— 拦"千分位逗号污染"
##   "1,240.00" 或空串会让 read.csv 把整列读成字符型，
##   建模时被当作因子 → 生成数百个哑变量 → C-index 虚高到 0.97（而软件不报错）
expect_num <- c("age","size","bmi","glucose","cr")        # 按项目改
bad <- expect_num[sapply(expect_num, function(v) v %in% names(d) && !is.numeric(d[[v]]))]
if (length(bad)) stop("本应数值却读成字符/因子，检查千分位逗号或空值: ", paste(bad, collapse=", "))

## 闸门 2：不可能值扫描 —— 拦"0 值实为缺失码"
##   实验室指标/体格的 0 值在生理上不可能 → 直接 log(0) = -Inf，shapiro.test 返回 NaN
sapply(d[sapply(d, is.numeric)], function(v) sum(v == 0, na.rm = TRUE))

## 闸门 3：缺失率与缺失模式
sapply(d, function(x) round(mean(is.na(x)) * 100, 2))
mice::md.pattern(d)

## 闸门 4：事件数与 EPV（预测模型专用）
##   EPV = 事件数 / 参数个数；分类变量按哑变量个数算参数
n_ev  <- sum(d[[CFG$outcome]] == 1)
cat("EPV =", round(n_ev / n_par, 1), ifelse(n_ev/n_par < 10, " ✗ 低于 10", " ✓"))

## 闸门 5：参数个数与性能合理性 —— 拦"因子误用""数据泄漏"
cat("模型参数个数 =", length(coef(model)), "\n")   # 达数百 → 必有因子被误用
cat("C-index =", round(C, 3), "\n")                 # > 0.95 先怀疑数据问题，别先庆祝

## 闸门 6：方向核对 —— 拦符号错误
##   结果方向必须与既往文献/临床常识一致；不一致时第一件事是查编码，而不是讨论结论
```

**各领域高频静默陷阱（完整版见 `references/07_domain_methodology.md` §九）**

| 领域 | 静默陷阱 | 后果 |
|---|---|---|
| 预测模型 | 千分位逗号污染 | C-index 虚高到 0.97 |
| 机器学习 | 拆分前做全量标准化；用训练集选超参 | 训练 AUC = 1.0 |
| **孟德尔随机化** | **效应等位基因方向写反** | **beta 符号反转，SE/P/Q 全不变，零报警** |
| 倾向得分 / 真实世界 | `glm(weights=)` 当抽样权重用 | CI 过窄、假阳性 |
| NHANES | 用 `mean`/`lm` 代替 `svy` 系列；未设 `lonely.psu` | 估计有偏 / 分析失败 |
| 轨迹模型 | 比较不同组数时多项式阶次不一致 | AIC/BIC 不可比 |

---

## 六、统计方法选择决策树

> **不确定用哪个 R 包？** → `references/25_R包选型速查与核心包速用卡.md`（按 15 类临床科研任务查包 + 15 个高频包速用卡）
> **要现成的完整可运行代码？** → 实操代码层：`26` tidyverse 语法 · `27` 数据整理与批量建模 · `28` 组间比较与基线表 · `29` 回归与生存分析 · `30` 临床预测模型全流程 · `31` 机器学习算法核心 · `32` mlr3 工作流 · `33` 机器学习与 SHAP · `34` 科研绘图代码骨架 · `35` 临床试验设计与统计 · `36` 预测模型与生存分析方法学前沿 · `37` IMA 知识库主题地图
> **定位**：以上 25–37 是**实操代码层**（完整代码 + 参数 + 踩坑）；`07_domain_methodology.md` 与 `14_统计结果解读手册.md` 是**方法学与解读层**。两层配合使用，不要重复通读。

```
Q1 结局类型？
├── 连续      → 线性回归（lm / svyglm(gaussian)）→ 剂量反应用 RCS
│               └── 完整代码 + LINE 假设 + VIF/DW 诊断 → references/29
├── 二分类    → Logistic → ROC / 校准曲线 / DCA / NRI / IDI
│               └── EPV 与 Firth 小样本补救 → references/29；全流程 → references/30
├── 生存      → Cox / 参数生存模型(psm) / 机器学习生存模型
│   ├── PH 违反？    → 时依系数 tt() / 分层 strata() / psm
│   ├── 竞争事件？   → Fine-Gray；★ 用 cuminc 而非 1−KM
│   └── 随访是离散波次？→ cloglog 离散时间模型
├── 计数      → Poisson / 负二项
└── 重复测量  → 混合效应模型 / GEE / 轨迹模型
                └── RM-ANOVA vs LMM vs GEE 决策树、球形校正、ICC、奇异拟合
                    → `references/21_重复测量与纵向数据分析.md`（代码实测）

Q2 研究目的？
├── 设计阶段样本量 → `references/20_样本量与效能估算.md`（数字全部实测）
│                   └── 临床试验设计四原则/方案选择/成组序贯 → references/35
├── 预测 → 区分度 + 校准度 + 临床效用(DCA) + 内部/外部验证
│          └── 列线图→ROC→校准→DCA→Bootstrap→外部验证 的逐卡代码 → references/30
│          └── 机器学习 + SHAP 路线 → references/33（算法原理 → references/31）
├── 因果（观察性）→ 倾向得分 / IPTW / 克隆删失加权 + E-value
├── 因果（遗传工具变量）→ 孟德尔随机化
├── 中介 → 观察性用 CMAverse；遗传用 MVMR 框架（优于两步法）
└── 关联 → 多模型策略（未调整 → 部分调整 → 完全调整）

Q3 数据来源？
├── 复杂抽样（NHANES / CHARLS / HRS）→ 必须加权（svydesign + svy 系列）
├── 公共 GWAS 汇总数据 → 孟德尔随机化（注意等位基因方向）
├── 单细胞 → Seurat；细胞类型特异 eQTL → sc-eQTL MR
├── 多中心/多表拼接/批量建模 → tidyverse 数据整理与分组嵌套建模 → references/27
└── 常规临床数据 → 注意离散时间、缺失编码、隐私脱敏

Q4 用哪些敏感性分析？
├── 未测量混杂 → E-value
├── 时依混杂   → 克隆删失加权
├── 缺失数据   → MICE + MAR/MNAR 敏感性分析
├── 多重比较   → Holm / FDR → `references/22_多重比较校正与分类一致性.md`（五法实测对照）
├── 多重共线性 → VIF
└── 过拟合     → Bootstrap / 交叉验证校正
```

**交付前最后一道闸**：走完 ①-⑤ 后，按 `references/24_交付前自检清单.md` 逐阶段打勾
（统计量+P 双呈现、上标引用数校验、禁词/AI 痕迹、SVG 可编辑、脚本纯 ASCII——可跑脚本一次审计）。

---

## 七、研究目的 → 图表类型对照（摘要，完整版见 `references/05_chart_selection_guide.md`）

| 需求 | 图 | 表 | 核心函数 |
|---|---|---|---|
| 基线特征 | — | Table 1 | `tableone::CreateTableOne` / `gtsummary` |
| 组间差异 | 箱线/小提琴/条形 | Table 1 | `ggplot2` |
| 二分类预测 | **ROC 曲线** | AUC 表 | `pROC::roc` |
| 校准度 | **校准曲线** | 校准指标表 | `rms::val.prob` / `calibrate` |
| 临床效用 | **DCA 决策曲线** | 净收益表 | `rmda` / `dcurves` |
| 多因素效应 | **森林图** | 回归结果表 | `forestploter` / `ggplot2` |
| 生存分析 | **KM 曲线** / 累积发生率 | 中位生存表 | `survminer` / `cmprsk` |
| 预后模型 | **列线图** | 评分表 | `rms::nomogram` |
| 剂量-反应 | **RCS 曲线** | 非线性检验 | `rms::rcs` + `Predict` |
| 亚组分析 | **森林图（含交互 P）** | 亚组表 | `jstable` |
| 中介分析 | 路径图 | 效应分解表 | `CMAverse` |
| 机器学习 | SHAP 蜂群/依赖/瀑布图 | 模型性能表 | `kernelshap` + `shapviz` |
| 孟德尔随机化 | 散点/森林/漏斗/留一法 | MR 结果表 | `references/07` §四 |
| 轨迹 | **轨迹图** | 模型选择指标表 | `gbmt` / `lcmm` |
| 纵向/重复测量 | 折线图 / 意大利面图 | 时间点比较表 | `ggplot2` / `lme4` |
| 多指标综合 | 热图 / 相关矩阵 | 相关系数表 | `pheatmap` / `corrplot` |

> **每一类图的输出格式一律：SVG（可编辑）+ PDF（投稿）+ PNG 300dpi（预览）。**

---

## 八、领域方法学（★ 本技能自包含，无需外部依赖）

**本技能负责"怎么算、怎么画、怎么交付"；具体领域"该用什么方法、容易踩什么坑"请看
`references/07_domain_methodology.md`（已内置压缩版，可独立使用）。**

| 研究领域 | 主要方法 | 在本技能中的位置 |
|---|---|---|
| **诊断/预后预测模型** | Logistic / Cox + 列线图 + 校准 + NRI/IDI + DCA | `references/07` §一 |
| **机器学习与 SHAP** | 8 二分类 + 6 生存模型 + KernelSHAP | `references/07` §二 |
| **倾向得分 / 混杂控制** | PSM / IPTW / 重叠加权 / 克隆删失加权 / E-value | `references/07` §三 |
| **孟德尔随机化** | 两样本 / 多变量 / 中介 / 药靶 MR + 共定位 | `references/07` §四 |
| **老年队列（CHARLS/HRS 等）** | 多模型策略 + 多重插补 + RCS + 中介 + 亚组 | `references/07` §五 |
| **NHANES 与复杂抽样** | svydesign + svy 系列 + 加权 RCS | `references/07` §六 |
| **纵向轨迹模型** | GBTM / LCGM / GMBTM + gridsearch | `references/07` §七 |
| **网络药理学与单细胞** | KEGG/GO 富集 + Seurat + sc-eQTL MR | `references/07` §八 |
| **跨领域静默陷阱总表** | 12 条"不报错但致命"的错误 + 专属闸门 | `references/07` §九 |

> **给不同环境的说明**
> - **在 WorkBuddy / 具备技能系统的 agent 中**：若环境中同时存在 `r-clinical-prediction-model`、
>   `r-mendelian-randomization` 等专门技能，可用它们获取更深入的领域细节（数百 KB 笔记）；
>   但**不依赖它们也能完整工作** —— `references/07` 已覆盖每个领域的核心方法、关键函数与致命陷阱。
> - **在 ima 等仅能导入单个 ZIP 的环境中**：只导入本技能即可，`references/07` 就是领域方法学的入口。
> - **本机 R 调用与 locale 问题**：见 `references/04_environment_and_cross_agent.md`（已内置）。

---

## 九、本技能资产

| 文件 | 用途 |
|---|---|
| **`assets/lib/lib_00_common.R`** | ★★ 通用基座：read_any（自动识别 csv/xlsx/sav/dta + 千分位逗号修复）/ data_gates（六道闸门）/ save_fig（三格式出图，cairo 中文安全）/ svg_check / table1 / with_datadist |
| `assets/lib/lib_01_regression.R` | 回归：线性/Logistic/有序/泊松/Cox/条件Logistic · uni_multi 单因素筛选→多因素 · three_models 三模型递进 · forest_plot · subgroup_analysis 亚组+交互P · rcs_dose_response RCS（含加权版，用 splines::ns+svyglm 破解 rms 不支持 survey） |
| `assets/lib/lib_02_prediction.R` | 预测模型：roc_eval/roc_compare(DeLong) · calibration_eval(校准截距/斜率/Brier/HL检验内联) · nri_eval · idi_eval · dca_eval(dcurves 优先) · nomogram_plot · survival_roc(KM法+cutoff) · cindex_eval · bootstrap_validate · ph_assumption · competing_risk(Fine-Gray) |
| `assets/lib/lib_03_ps.R` | 倾向得分：ps_compute · smd_table(手写SMD) · psm_pipeline(含 clogit 条件logistic) · ps_weight(IPTW/重叠加权+ESS) · ps_effect(★svyglm/svycoxph 正确SE，并对照展示 glm(weights=) 的SE偏差) · e_value · ps_missing(MatchThem) |
| `assets/lib/lib_04_mr.R` | 孟德尔随机化（手写全套，TwoSampleMR 已归档仍可用）：mr_harmonise(回文/EAF) · mr_fstat · mr_ivw/mr_egger/mr_wmedian/mr_median/mr_wmode · mr_loo · mr_presso · mr_steiger · mr_analyse(一站式) · mr_mvmr(多元WLS) · mr_mediation(med_cal 正确SE公式) |
| `assets/lib/lib_05_missing_trajectory.R` | 缺失诊断+MICE（method 必须真传进 mice / with.mids 陷阱 / pool 正确用法）· 宽转长 · GBTM 轨迹模型（自实现多随机起点，弃 gridsearch；ng>1 必须传 B；AIC/BIC 同阶次才可比 + Avepp/OCC 诊断） |
| `assets/lib/lib_06_ml.R` | 机器学习：防泄漏流水线（预处理参数只在训练集估）· Lasso/RF/GBM/NB/KNN/SVM 二分类对比（训练AUC落差闸门）· ΔAUC Bootstrap · SHAP 蜂群图（fastshap）· 生存 ML（RSF/Lasso-Cox/GBM-Cox）C-index 对比 |
| `assets/lib/lib_07_causal.R` | 因果推断：ps_diagnose（PS重叠诊断）· aipw_ate（AIPW双稳健+SuperLearner）· tmle_ate · dml_plr（DoubleML）· g_formula（G公式标准化+Bootstrap）· causal_mediation（ACME/ADE/中介占比） |
| `assets/lib/lib_08_forest.R` | 期刊级森林图：forest_subgroup（亚组分析一键出图表）· forest_raw（forestploter 表+图式，柳叶刀风格）· forestplot_style（分层加粗备选） |
| `assets/lib/lib_09_singlecell.R` | 单细胞：sc_qc_pipeline(QC质控) · sc_standard_pipeline(V5整合/聚类) · sc_annotate · sc_subcluster · sc_pseudobulk · sc_cellchat(CellChat) · sc_monocle2(拟时序) |
| `assets/lib/lib_10_reporting.R` | 投稿级报告：theme_submission/save_submission(三格式出图) · figure_legend(中英图注) · interpret(结果解读) · results_para(12类场景中英结果段) · cn_text(中文文本外置，规避 Windows 源码编码问题) |
| `assets/lib/lib_11_palette.R` | ★ 配色引擎（实测）：pal_journal(npg/nejm/lancet/jama/aaas) · pal_okabe(色盲安全标杆) · pal_seq/pal_div/pal_vir(连续/发散) · cb_safe(色盲三级判定，Machado 2009 模拟+CIELAB ΔE) · style_figure(一键配色+检查) · JW(期刊栏宽 mm→in) · svg_fonts_cn(中文 SVG 字体) |
| `assets/medical_stats_template.R` | ★ **模式 A 的完整可跑模板**：环境自检 → 数据检查 → 描述统计 → 回归 → ROC/校准/DCA/森林图 → SVG+PDF+PNG → DOCX 表 → 结果落盘 |
| `assets/svg_export_helpers.R` | ★ **SVG 出图辅助函数**：`save_fig()` 三格式一键输出、`init_svg_fonts()` 字体注册、多面板拼图并导出 SVG |
| `assets/codegen_guide.md` | ★ **模式 B 的代码生成规范**：六段式结构、8 条硬要求、《运行说明》模板 |
| `references/01_dual_mode_workflow.md` | 两种模式的完整流程与交付标准 |
| `references/02_svg_publication_guide.md` | SVG 可编辑性原理、字体、多面板、期刊格式要求 |
| `references/03_tables_and_output_formats.md` | 从 R 出 DOCX/XLSX 表的四条路径与选择 |
| `references/04_environment_and_cross_agent.md` | locale、重定向、编码、长任务、降级策略 |
| `references/05_chart_selection_guide.md` | 完整的图-表-函数对照表（含代码骨架） |
| `references/06_data_quality_gates.md` | 六道闸门的完整实现与各领域陷阱清单 |
| **`references/20_样本量与效能估算.md`** | 15 种设计的样本量（pwr/power.roc.test/wp.rmanova/Schoenfeld/Diggle），数字全部实测 |
| **`references/21_重复测量与纵向数据分析.md`** | RM-ANOVA(afex)/LMM(lme4+ICC)/GEE 决策树、奇异拟合处理、中英模板，代码实测 |
| **`references/22_多重比较校正与分类一致性.md`** | p.adjust 五法实测对照、判别分析 LDA/QDA、Kappa/ICC/Bland-Altman 四要素 |
| **`references/23_期刊配色系统与出图流水线.md`** | 期刊调色板+色盲三级判定(ΔE)+栏宽尺寸+SVG 流水线，配 `lib_11_palette.R` |
| **`references/24_交付前自检清单.md`** | 7 阶段交付闸门（统计量+P 双呈现/上标数校验/禁词/AI 痕迹/编码），含可跑自检脚本 |

### 实操代码层（2026-09-29 IMA 六库蒸馏并入 · 152 张方法卡片 · 全部代码实测）

> 这批文件解决的是「**知道用什么方法，但写不出能跑的代码**」。每张卡固定 8 栏：适用场景 / 前提与假设 / **R 实现（完整可运行）** / 结果怎么读 / 常见错误 / 报告写法（中英各一句）/ 库内依据 / 存疑备注。
> 溯源：卡片标注的「库内依据」已用 6 个知识库的完整标题清单（75 837 条）逐条核验，**646 条候选引用 0 条编造**；缺失内容均如实标注。
> **代码实测**：138 个 R 代码块经 5 轮本机实跑，逐块修正（详见 `assets/ima_distillation_audit.md` 编译审计报告）。
> **⚠ 使用前必读**（每份文件头部均有「卡片使用须知」）：① 卡片间存在**递进依赖**，单独运行报 `object not found` 时先跑前一张卡；② 标 `read.csv("xxx.csv")` 的卡片**需自备数据文件**；③ `31/32/33` 开头的**兼容表**记录了 mlr3 1.8 的全部 API 漂移，照抄旧教程前先看它。
> **⚠ 已下架包**（CRAN 已移除，`install.packages` 必失败）：`rmda`→`dcurves` · `regplot`/`VRPM`→`rms::plot(nomogram())` · `vip`→`caret::varImp`/`iml` · `gghalves`→`ggdist::stat_halfeye()`。各使用点已就地标注。

| 文件 | 用途 |
|---|---|
| **`references/25_R包选型速查与核心包速用卡.md`** | ★ 15 类临床科研任务的包选型表（55 行）+ dplyr/tidyr/ggplot2/survival/rms/pROC/gtsummary/tableone/glmnet/xgboost/mice/MatchIt/timeROC/forestplot/caret 15 个高频包速用卡 |
| `references/26_tidyverse语法体系.md` | 管道与向量化、dplyr 五大动词、tidyr 宽长转换、purrr 泛函迭代、stringr/forcats；每卡带「与 base R 写法对照」 |
| `references/27_tidyverse数据整理与建模实践.md` | 导入清洗（含中文编码）、多表连接、缺失/异常值、批量建模（group_nest + map）、broom 整理、批量出图落盘 |
| `references/28_统计描述与组间比较实操.md` | ★ 基线表（表 1）最高频链路：正态性判断 → t/秩和/ANOVA/KW → 卡方/Fisher → 多重校正 → gtsummary/tableone 三线表 |
| `references/29_回归与生存分析实操.md` | 线性回归 LINE 诊断、共线性与正则化、Logistic（EPV/Firth）、KM 与 Cox（PH 假设） |
| `references/30_临床预测模型实操全流程.md` | ★ Nomogram → ROC/AUC → 校准曲线 → DCA → Bootstrap 内部验证 → 数据划分与外部验证 → TRIPOD |
| `references/31_机器学习算法核心与模型评估.md` | 偏差-方差、嵌套 CV、正则化、树与集成（RF/GBM/XGBoost）、SVM/KNN/NB、降维聚类、评估指标与 Bootstrap CI |
| `references/32_mlr3工作流与实战.md` | mlr3verse 全流程：Task/Learner/Measure/Resampling/Tuning/Benchmark/Pipeline/viz + 不平衡数据正确用法 |
| `references/33_机器学习与SHAP实操.md` | ★ 防数据泄露、特征筛选（LASSO/Boruta/RFE）、多模型比较、XGBoost + SHAP（蜂群/依赖/瀑布/决策图）与临床措辞 |
| `references/34_科研绘图与配色代码骨架.md` | 配色（RColorBrewer/ggsci/顶刊/中国传统色）+ 森林图/KM/热图/气泡图/堆积图/Nomogram-ROC-校准-DCA 图组代码骨架 |
| `references/35_临床试验设计与统计方法.md` | 科研设计四原则、样本量、多重比较、非参数选择、χ² 列联表、GEE 与多水平、ITT/mITT/PP 与缺失数据、ANCOVA、成组序贯 |
| `references/36_预测模型与生存分析方法学前沿.md` | 英文预印本库前沿：多分类模型、全生命周期缺失、最小样本量、校准与 ECE 误区、Brier、贝叶斯 DCA、DAG 因果思维、模型迁移与更新、删失偏倚、复发事件、竞争风险、左截断 ROC |
| `references/37_IMA知识库主题地图.md` | 六库导航：哪个去哪个库查、两大地图（一起学统计工具 20 495 条 / 统计学 31 828 篇）、接口能力边界、**库内缺口清单** |
| `references/38_统计量倒推原始数据.md` | ★★ **从已发表统计量倒推患者级原始数据（数据溯源重建）**：F2 描述性统计 AUC 天花板定律、AUC Inflation 定律（组内仿射校准陷阱）、`mk_iqr_exact`/`mk_iqr_lat`（任意 n 下 type-7 分位数机器精度复现）、共线性 β 符号不稳与种子搜索法、竞争性吸收定律、RNG 确定性铁律、10 篇实证可复现率规律。**方法学训练/模拟数据/可重复性检验场景必读** |

### 数据倒推工具层（2026-09-30 batch01 四篇闭环实战并入 · 与 references/38 配套）

> 38 号文档是**定律层**（为什么），本层是**工具与证据层**（怎么做 + 怎么验收）。倒推任务两层配合使用：
> 读 `38` 明白数学边界 → 按 `43` 的七步流程走 → 查 `39` 的取值证据 → 用 `assets/data_reverse/` 工具链生成与验收 → 按 `42` 归因差距 → 用 `40` 的六式过强制验收关。

| 文件 | 用途 |
|---|---|
| **`references/43_倒推算法总纲.md`** | 七步标准工作流（可倒推性评估 → 约束优先级 → 潜因子设计 → 生成 → 自检 → 六式验收 → 逐格对标）；分组时点泛化豁免、纵向随访门控等工程约定 |
| **`references/39_指标取值范围证据库.md`** | ★★ **244 个临床指标的证据化取值范围**（典型/宽/硬三档区间 + 分布形态 + 证据备注，自动生成勿手改）。来源：训练库论文实测 + 每篇倒推后回填滚动累积。**生成数据前必查；新增指标改 `assets/data_reverse/ranges_lib.py` 后跑 `gen_ranges_doc.py` 重新生成** |
| `references/40_六式打假自审.md` | ★ 耿同学六式（合成数据反向使用）：分布形态/末位数字/组间边界/统计异常/临床逻辑/变量一致性 + 四项法定豁免 + 阈值标定表 + 六条临床逻辑铁律（登记唯一性/OI-PF 拆键/治疗目标区间/有界轨迹/排序法） |
| `references/41_倒推实战案例.md` | 4 篇完整复盘（AP并发ARDS 含 AUC 模型 / 肺栓塞溶栓配对时点 / 药物中毒 197 例 / 儿童 ARDS 的 ECMO 纵向 7 时点），20+ 真实踩坑与解法、优先级铁律、何时停止调参 |
| `references/42_倒推差距分析方法.md` | 差距四类归因（A 信息量上限 / B 小样本波动 / C 梯度压缩 / D 原文瑕疵）、报告模板、质量红线、交付自检清单 |
| **`assets/data_reverse/ranges_lib.py`** | 取值范围与关系约束库（VARS 244 / RELATIONS 125）：`check_univariate` 三档判罚、`check_relations`、证据回填 `save_evidence` |
| `assets/data_reverse/check_csv.py` | **第一关**：CSV 合理性自检（范围+关系+未登记扫描，时点列泛化豁免 `_TP_SUFFIX`），输出 0-100 分 |
| `assets/data_reverse/data_fraud_audit.py` | **第二关（强制）**：耿同学六式打假自审，末位数字卡方（原始字符串+归一化+四项豁免）、CV 经验区间（523 篇 6667 对 mean±SD 标定）、临床逻辑矛盾扫描；6/6 才算过关 |
| `assets/data_reverse/gen_lib.R` | R 生成函数库：`fit_lnorm_ms` 位移对数正态闭式、`align_rank` 秩空间加权重排、`mk_traj_core` 有界纵向轨迹、`mk_age_block` 分块矩匹配、`repair_to` 精确计数修正 |
| `assets/data_reverse/gen_ranges_doc.py` | 由 ranges_lib.py 自动导出 39 号取值范围库文档（防手工失同步） |
| `assets/data_reverse/build_xlsx.py` | 交付 XLSX 生成（变量字典 + 原始数据 + 说明与免责三 sheet） |
| `assets/data_reverse/make_cmp_template.R` | 表 1/2/3 逐格对标模板（mine vs paper 双行输出 + 偏差百分比） |
| `assets/data_reverse/范例_gen_01…04.R` | 4 篇完整可复现生成脚本（含 AUC 模型篇 / 配对时点篇 / 197 例多约束篇 / ECMO 纵向篇）+ 变量字典与差距报告范例 |
| `assets/data_reverse/证据库_滚动累积.md` | 每篇倒推后回填的实测范围（滚动累积，check_csv 自动追加） |

**倒推任务验收双关卡（缺一不可）**：
```bash
python assets/data_reverse/check_csv.py <cohort.csv> --tag P01      # 目标 100/100
python assets/data_reverse/data_fraud_audit.py <cohort.csv> P01     # 目标 6/6
```
Windows 陷阱：R 生成脚本注释一律英文（中文注释 Rscript 解析失败）；修改 Python 模块后删 `__pycache__`；`VARS` 字典新增后必跑去重审计（同名键后者静默覆盖）。

---

## 十、三条铁律（印在最后，但最重要）

1. **图必须给 SVG（可编辑），表必须给 DOCX/XLSX。** 期刊返修要改图的字号颜色标注 —— 只有矢量可编辑文件能改。
2. **没有 R 不是拒绝任务的理由。** 走模式 B 生成可直接运行的完整脚本 + 运行说明，同样是合格交付。
3. **任何分析前先跑六道闸门。** 本领域最危险的错误（逗号污染、0 值当缺失码、等位基因方向反、权重当精度权重）
   **全都不报错** —— 不主动检查就永远发现不了。
