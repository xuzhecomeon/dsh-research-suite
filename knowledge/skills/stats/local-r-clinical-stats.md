<!-- source: local-r-clinical-stats @ local-r-clinical-stats | domain: stats -->

---
name: local-r-clinical-stats
description: 直接调用本机已安装的 R 4.5.2 执行临床科研统计与绘图（不是生成代码给人跑，而是自己跑完并把统计结果与统计图交付）。本机 R 有一个隐蔽的 locale 阻断点必须先处理，否则 R 完全无法加载任何包。触发场景：需要用 R 做描述性统计、基线表（tableone/gtsummary）、组间比较、Logistic/Cox/线性混合回归、ROC 与 AUC、Kaplan-Meier 生存分析、森林图、列线图、剂量-反应曲线，或需要用 ggplot2 / patchwork / ComplexHeatmap / survminer 出版级出图，或用户提供 R 代码要求代为运行、修改、调试并返回结果与图片。
agent_created: true
---

# 本机 R 调用 · 临床统计与绘图

## 核心结论

本机 R **可以被我直接调用**：写完/改完 R 脚本 → 自己执行 → 把统计结果与图片交付给你。
关键前提是**清除外壳注入的 POSIX locale 变量**，否则 R 会连自己的扩展包都读不到。

## 环境事实

| 项 | 值 |
|---|---|
| R 版本 | 4.5.2 (2025-10-31 ucrt) |
| R_HOME | `<APP_DIR>\R-4.5.2` |
| Rscript | `<APP_DIR>\R-4.5.2\bin\Rscript.exe` |
| 扩展包 | 436 个（`R_HOME/library`，约 0.8 GB） |
| 用户库 | `<USER_HOME>\AppData\Local\R\win-library\4.5`（空） |

## ⚠️ 第一铁律：调用前必须清除 locale 变量

外壳环境预设 `LC_ALL=C.UTF-8`、`LANG=en_US.UTF-8`。这是 POSIX 取值，**Windows 版 R 无法识别**，启动时 locale 初始化失败，退化为 `codepage = 0`，后果是：

- `package 'compiler' does not have a namespace` → R 直接启动失败
- `unable to translate '<APP_DIR>/...' to native encoding` → 含中文的路径全部失效
- `installed.packages()` 返回 **0 个包**（436 个包全部"隐身"）
- `library(ggplot2)` 报 `there is no package called 'ggplot2'` 或 `not a valid installed package`

**只清空、不必赋任何值。** 清空后 `l10n_info()$UTF-8 = TRUE`、`codepage = 65001`，一切恢复正常，中文图表开箱即用。

> 排查记录：曾试图用 ASCII junction（`mklink /J D:\R452`）绕过中文安装路径——**这不是正解**，R 会把 junction 解析回真实中文路径，且与 locale 无关。根因是 locale，不是路径。不要再走这条路。

## 标准调用配方（PowerShell）

PowerShell 是唯一可靠通道（Bash 通道的本机 Git Bash 缺 `dirname`/`head`/`mkdir` 等基础命令）。

```powershell
Remove-Item Env:LC_ALL -ErrorAction SilentlyContinue
Remove-Item Env:LANG -ErrorAction SilentlyContinue
Remove-Item Env:LANGUAGE -ErrorAction SilentlyContinue
& "<APP_DIR>\R-4.5.2\bin\Rscript.exe" "script.R" *> "_r_output.log"
```

**必须重定向到文件再读**：本环境 PowerShell 的 stdout 不会被工具捕获（返回空），且控制台回显 UTF-8 会变乱码。

R 侧则应主动把结果写成 UTF-8 文件，不要依赖控制台：

```r
con <- file("results.txt", open = "wt", encoding = "UTF-8")
sink(con); sink(con, type = "message")
# ... 统计与 cat() 输出 ...
sink(type = "message"); sink(); close(con)
```

## ⚠️ 第二铁律：.R 脚本必须用 Write 工具生成

用 PowerShell `Out-File -Encoding UTF8`（PS 5.1）生成的 `.R` 带 BOM，R 报 `unexpected input in "锘"` 并中止。**一律用 Write 工具写 R 脚本**，它生成无 BOM 的 UTF-8。

## 工作流

1. **确认数据**：读取用户提供的数据文件（csv/xlsx → `readxl`/`data.table`）。患者数据不外传，全程本地。
2. **写脚本**：用 Write 工具写 `.R`；中文标签在脚本里用 `\uXXXX` 转义最稳妥，也可直接写中文（脚本为 UTF-8，R 4.5 可正常解析）。
3. **执行**：上面的 PowerShell 配方，重定向日志。
4. **读回**：Read 工具读 R 写出的 UTF-8 结果文件与 PNG 图（Read 可直接看图）。
5. **交付**：统计结果文字 + 图片；必要时附 Excel/CSV 结果表。

## 出图规范（用户偏好）

- 中文直接可用，无需额外配置字体。
- 配色遵循**中国习惯**：风险增加 / 阳性 / 上调 → **红**（如 `#D6473F`）；保护因素 / 阴性 / 下调 → **绿**（如 `#2E8B57`）。
- 出版级：`ggsave(..., dpi = 300)`；多面板用 `patchwork`。
- 常用：`theme_classic(base_size = 11~13)` + `ggsci` 期刊配色。
- 森林图本机**没有 `forestplot` 包**，用 ggplot2 `geom_pointrange` + `scale_x_log10()` 自建（模板见下）。

## 包可用性

完整清单见 `references/包清单与缺失清单.md`。要点：

**✓ 齐备**：tableone、gtsummary、compareGroups、Hmisc、psych、gt、flextable、rms、lme4、lmerTest、nlme、glmnet、MASS、car、emmeans、multcomp、sandwich、lmtest、ordinal、broom、insight、survival、survminer、riskRegression、pec、prodlim、cmprsk、mets、ggDCA、autoReg、dcurves、pROC、DynNom、ggplot2、ggpubr、patchwork、cowplot、gridExtra、ggrepel、ggsci、scales、RColorBrewer、corrplot、circlize、ComplexHeatmap、pheatmap、ggtext、gplots、DiagrammeR、igraph、svglite、ragg、rmarkdown、knitr、kableExtra、bookdown、officer、data.table、dplyr、tidyr、readxl、openxlsx、writexl、haven

**✗ 缺失（17）**：DescTools、geepack、lavaan、mediation、marginaleffects、survIDINRI、VennDiagram、UpSetR、forestplot、Cairo、showtext、sysfonts、limma、DESeq2、edgeR、clusterProfiler、Biobase

装包走清华镜像（见用户长期记忆）：
```r
install.packages("forestplot", lib = "<APP_DIR>/R-4.5.2/library",
                 repos = "https://mirrors.tuna.tsinghua.edu.cn/CRAN/")
```

**已知瞬时故障**：`rms` 首次加载可能报 `SparseM.dll` 被「应用程序控制策略」拦截（`LoadLibrary failure`），这是安全软件首次扫描所致，**重试即通过**，无需处理。

## 可复用模板

`assets/template_clinical_stats.R` 是一份跑通的完整模板，覆盖：基线表 → 组间比较 → 多因素 Logistic（OR 森林图）→ ROC/AUC/最佳阈值 → KM + log-rank + Cox → patchwork 三面板 300 dpi 组图 → UTF-8 结果文件。

用法：复制到工作区 → 改数据读入与变量名 → 按上面的配方执行。

## 交付前自检

- [ ] 结果文件是 UTF-8 且中文可读（用 Read 打开确认，不要相信控制台）
- [ ] 图片已用 Read 目视确认：中文无豆腐块、坐标轴/图例/标题无重叠
- [ ] 统计量有单位与精度（AUC 三位小数、P 值用 `<0.001` 而非 `0`）
- [ ] 未使用模拟数据冒充真实结果；凡模拟数据必须显式标注
- [ ] 患者数据仅落地本机工作区，不上传任何云端服务
