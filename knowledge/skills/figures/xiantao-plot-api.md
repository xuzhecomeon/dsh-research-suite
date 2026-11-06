---
name: xiantao-plot-api
description: 仙桃学术图表生成工具，通过指定绘图模块名调用对应Python脚本生成火山图、热图、KM生存曲线、森林图、分组比较图、点线图、qPCR分析图、饼图、雷达图、韦恩图、一维柱状图、叠加柱状图、豆荚图、相关性散点图、折线图、配对图、限制性立方样条、山峦图、ROC曲线、词云图、GOKEGG分析、相关性热图、箱式图、UpSet图、内嵌柱状图、复杂数值热图、基线资料表、堆叠面积图、数据分布面积图等30种图表。支持自定义图表标题、坐标轴、颜色、字体、图例、聚类、统计方法等丰富绘图参数，不限制输入文件拓展名。
---
# xiantao-plot-api

# 仙桃学术图表生成工具 (模块化版本)

## 概述

通过用户指定的**绘图模块名**调用对应脚本进行图表生成。所有脚本位于 `scripts/` 目录，示例数据位于 `references/` 目录。共支持 **30 种图表/表格**模块。

## 前置检查（每一步执行前必须先做）

在调用任何脚本之前，必须先完成以下环境检测：

### 1. 检测 Python 命令

根据操作系统确定正确的 Python 命令：

| 操作系统      | Python 命令 |
| ------------- | ----------- |
| Linux / macOS | `python3` |
| Windows       | `python`  |

检测方法：先尝试 Linux/macOS 命令：

```bash
python3 --version
```

- 若命令**退出码为 0 且输出包含 "Python" 字样**（如 `Python 3.x.x`），则使用 `python3`。
- 若命令不存在、退出码非0、或**输出为空（如 Windows Store stub 不返回版本信息）**，则继续尝试 Windows 命令。

```bash
python --version
```

- 若命令**退出码为 0 且输出包含 "Python" 字样**，则使用 `python`。
- 若命令不存在、退出码非0、或**输出为空**，则判定为 Python 未安装。

**判定为 Python 未安装时**：通过 question 工具询问用户选择安装方式：

| 选项     | 操作                                                                                                                                        |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 自动安装 | Linux/macOS 使用包管理器安装（`apt install python3` / `brew install python3`），Windows 使用 `winget install Python.Python.3.12` 安装 |
| 自行安装 | 提示用户前往 https://www.python.org/downloads/ 下载安装，安装完成后重新执行本步骤                                                           |

用户选择后执行对应操作，安装完成后重新检测。

将检测到的 Python 命令记为变量 `{python}`，后续所有脚本调用均使用此变量。

### 2. 检测并安装必需包

所有脚本共用的导入依赖如下：

| 包名             | 类型             | 说明          |
| ---------------- | ---------------- | ------------- |
| `argparse`     | 标准库           | 参数解析      |
| `requests`     | **第三方** | HTTP 请求     |
| `json`         | 标准库           | JSON 处理     |
| `os`           | 标准库           | 操作系统接口  |
| `sys`          | 标准库           | 系统接口      |
| `base64`       | 标准库           | Base64 编解码 |
| `urllib.parse` | 标准库           | URL 解析      |
| `secrets`      | 标准库           | 安全随机数    |
| `string`       | 标准库           | 字符串工具    |

其中 `argparse`, `json`, `os`, `sys`, `base64`, `urllib.parse`, `secrets`, `string` 均为 Python 标准库模块，无需安装。仅 `requests` 为第三方包，需要检测并安装。

检测方法：使用 Python 逐一尝试导入。

```bash
{python} -c "import requests"
```

若导入失败（退出码非0），则安装：

```bash
{python} -m pip install requests
```

安装成功后继续执行后续步骤。

## 模块匹配规则

当用户输入模块名时，按以下流程处理：

1. **精确匹配**：若用户输入与某个模块名完全一致，直接使用该模块。
2. **模糊匹配**：若用户输入的模块名无精确匹配，则在下表所有模块名中进行**子串包含匹配**（即模块名包含用户输入或用户输入包含模块名）。
3. **无匹配**：若模糊匹配结果为空，直接回答"无相应模块"并列出所有可用模块供用户选择。
4. **多匹配**：若模糊匹配到多个模块（如输入"plot"匹配到 volcano_plot、km_plot、forest_plot、group_plot、line_point、radar_plot），则通过 question 工具让用户从匹配结果中选择。
5. **单匹配**：若模糊匹配恰好只有一个，直接使用该模块，无需询问用户。

| 模块名                | 功能                         | 对应脚本                     | 示例数据                                               |
| --------------------- | ---------------------------- | ---------------------------- | ------------------------------------------------------ |
| `volcano_plot`      | 差异基因火山图               | `volcano_plot_api.py`      | `volcano_plot_data.csv`                              |
| `heatmap_1anno`     | 差异基因热图                 | `heatmap_1anno_api.py`     | `heatmap_1anno_data.csv`                             |
| `km_plot`           | KM生存曲线                   | `km_plot_api.py`           | `km_plot_data.csv`                                   |
| `forest_plot`       | 森林图                       | `forest_plot_api.py`       | `forest_plot_data.xlsx`                              |
| `group_plot`        | 分组比较图                   | `group_plot_api.py`        | `group_plot_data.xlsx`                               |
| `line_point`        | 点线图                       | `line_point_api.py`        | `line_point_data.xlsx`                               |
| `pcr_analysis`      | qPCR分析图                   | `pcr_analysis_api.py`      | `pcr_analysis_data.xlsx`                             |
| `pie_chart`         | 饼图                         | `pie_chart_api.py`         | `pie_chart_data.xlsx`                                |
| `radar_plot`        | 雷达图                       | `radar_plot_api.py`        | `radar_plot_data.xlsx`                               |
| `veen_plot`         | 韦恩图                       | `veen_plot_api.py`         | `veen_plot_data.xlsx`                                |
| `bar_plot`          | 一维柱状图                   | `bar_plot_api.py`          | `bar_plot_data.xlsx`                                 |
| `bar_stack_table`   | 叠加柱状图（宽型数据）       | `bar_stack_table_api.py`   | `bar_stack_table_data.xlsx`                          |
| `bean_plot`         | 豆荚图                       | `bean_plot_api.py`         | `bean_plot_data.xlsx`                                |
| `cor_point_plot`    | 相关性散点图                 | `cor_point_plot_api.py`    | `cor_point_plot_data.xlsx`                           |
| `line_chart`        | 折线图                       | `line_chart_api.py`        | `line_chart_data.xlsx`                               |
| `pair_plot`         | 配对图                       | `pair_plot_api.py`         | `pair_plot_data.xlsx`                                |
| `rcs_binary`        | 诊断限制性立方样条           | `rcs_binary_api.py`        | `rcs_binary_data.xlsx`                               |
| `ridge_plot`        | 山峦图                       | `ridge_plot_api.py`        | `ridge_plot_data.xlsx`                               |
| `roc_curve`         | 诊断ROC曲线                  | `roc_curve_api.py`         | `roc_curve_data.xlsx`                                |
| `word_cloud`        | 词云图                       | `word_cloud_api.py`        | `word_cloud_data.xlsx`                               |
| `gokegg_analysis`   | GOKEGG富集分析               | `gokegg_analysis_api.py`   | `gokegg_analysis.xlsx`                               |
| `heatmap_cor_table` | 相关性热图(相关矩阵)         | `heatmap_cor_table_api.py` | `heatmap_cor_table.xlsx`                             |
| `bar_stack_stats`   | 叠加柱状图[统计]（长型数据） | `bar_stack_stats_api.py`   | `bar_stack_stats.xlsx`                               |
| `box_plot`          | 箱式图                       | `box_plot_api.py`          | `box_plot_data.csv`                                  |
| `upset_plot`        | UpSet图                      | `upset_plot_api.py`        | `upset_plot.xlsx`                                    |
| `bar_inline`        | 内嵌柱状图                   | `bar_inline_api.py`        | `bar_inline.xlsx`                                    |
| `heatmap_plot`      | 复杂数值热图                 | `heatmap_plot_api.py`      | `heatmap_plot_exp.xlsx` / `heatmap_plot_anno.xlsx` |
| `baseline_table`    | 基线资料表                   | `baseline_table_api.py`    | `baseline_table.xlsx`                                |
| `density_stack`     | 堆叠面积图                   | `density_stack_api.py`     | `density_stack.xlsx`                                 |
| `density_plot`      | 数据分布面积图               | `density_plot_api.py`      | `density_plot.xlsx`                                  |

## 通用用法

```bash
{python} scripts/<模块名>_api.py --file_path <数据文件> --plot_save <输出文件.pdf> [其他参数]
```

不限制文件拓展名，支持任意格式。**注意：**

- 词云图 (`word_cloud`) 模块输出为 PNG 格式
- GOKEGG分析 (`gokegg_analysis`) 和 基线资料表 (`baseline_table`) 模块输出为 Excel 表格 (.xlsx)
- 复杂数值热图 (`heatmap_plot`) 模块使用 `--exp_path` 和 `--anno_path` 两个输入参数（表达谱+注释），而非 `--file_path`
- 其余模块输出为 PDF 格式

### 使用示例数据快速运行

```bash
{python} scripts/volcano_plot_api.py --file_path references/volcano_plot_data.csv --plot_save volcano.pdf
{python} scripts/km_plot_api.py --file_path references/km_plot_data.csv --plot_save km.pdf
{python} scripts/heatmap_1anno_api.py --file_path references/heatmap_1anno_data.csv --plot_save heatmap.pdf
```

各模块完整参数通过 `--help` 查看：

```bash
{python} scripts/<模块名>_api.py --help
```

---

## 模块详情

匹配到具体模块后，详细参数见 `references/` 目录下对应的参数文件。

### 1. 火山图 (`volcano_plot`)

**脚本：** `volcano_plot_api.py` | **示例数据：** `volcano_plot_data.csv` | **详细参数：** `references/volcano_plot.md`

### 2. 热图 (`heatmap_1anno`)

**脚本：** `heatmap_1anno_api.py` | **示例数据：** `heatmap_1anno_data.csv` | **详细参数：** `references/heatmap_1anno.md`

### 3. KM生存曲线 (`km_plot`)

**脚本：** `km_plot_api.py` | **示例数据：** `km_plot_data.csv` | **详细参数：** `references/km_plot.md`

### 4. 森林图 (`forest_plot`)

**脚本：** `forest_plot_api.py` | **示例数据：** `forest_plot_data.xlsx` | **详细参数：** `references/forest_plot.md`

### 5. 分组比较图 (`group_plot`)

**脚本：** `group_plot_api.py` | **示例数据：** `group_plot_data.xlsx` | **详细参数：** `references/group_plot.md`

### 6. 点线图 (`line_point`)

**脚本：** `line_point_api.py` | **示例数据：** `line_point_data.xlsx` | **详细参数：** `references/line_point.md`

### 7. qPCR分析图 (`pcr_analysis`)

**脚本：** `pcr_analysis_api.py` | **示例数据：** `pcr_analysis_data.xlsx` | **详细参数：** `references/pcr_analysis.md`

### 8. 饼图 (`pie_chart`)

**脚本：** `pie_chart_api.py` | **示例数据：** `pie_chart_data.xlsx` | **详细参数：** `references/pie_chart.md`

### 9. 雷达图 (`radar_plot`)

**脚本：** `radar_plot_api.py` | **示例数据：** `radar_plot_data.xlsx` | **详细参数：** `references/radar_plot.md`

### 10. 韦恩图 (`veen_plot`)

**脚本：** `veen_plot_api.py` | **示例数据：** `veen_plot_data.xlsx` | **详细参数：** `references/veen_plot.md`

### 11. 一维柱状图 (`bar_plot`)

**脚本：** `bar_plot_api.py` | **示例数据：** `bar_plot_data.xlsx` | **详细参数：** `references/bar_plot.md`

### 12. 叠加柱状图 (`bar_stack_table`)

**脚本：** `bar_stack_table_api.py` | **示例数据：** `bar_stack_table_data.xlsx` | **详细参数：** `references/bar_stack_table.md`

### 13. 豆荚图 (`bean_plot`)

**脚本：** `bean_plot_api.py` | **示例数据：** `bean_plot_data.xlsx` | **详细参数：** `references/bean_plot.md`

### 14. 相关性散点图 (`cor_point_plot`)

**脚本：** `cor_point_plot_api.py` | **示例数据：** `cor_point_plot_data.xlsx` | **详细参数：** `references/cor_point_plot.md`

### 15. 折线图 (`line_chart`)

**脚本：** `line_chart_api.py` | **示例数据：** `line_chart_data.xlsx` | **详细参数：** `references/line_chart.md`

### 16. 配对图 (`pair_plot`)

**脚本：** `pair_plot_api.py` | **示例数据：** `pair_plot_data.xlsx` | **详细参数：** `references/pair_plot.md`

### 17. 诊断限制性立方样条 (`rcs_binary`)

**脚本：** `rcs_binary_api.py` | **示例数据：** `rcs_binary_data.xlsx` | **详细参数：** `references/rcs_binary.md`

### 18. 山峦图 (`ridge_plot`)

**脚本：** `ridge_plot_api.py` | **示例数据：** `ridge_plot_data.xlsx` | **详细参数：** `references/ridge_plot.md`

### 19. 诊断ROC曲线 (`roc_curve`)

**脚本：** `roc_curve_api.py` | **示例数据：** `roc_curve_data.xlsx` | **详细参数：** `references/roc_curve.md`

### 20. 词云图 (`word_cloud`)

**脚本：** `word_cloud_api.py` | **示例数据：** `word_cloud_data.xlsx` | **详细参数：** `references/word_cloud.md`（输出为 PNG 格式）

### 21. GOKEGG分析 (`gokegg_analysis`)

**脚本：** `gokegg_analysis_api.py` | **示例数据：** `gokegg_analysis.xlsx` | **详细参数：** `references/gokegg_analysis.md`（输出为 xlsx 表格）

### 22. 相关性热图（相关矩阵）(`heatmap_cor_table`)

**脚本：** `heatmap_cor_table_api.py` | **示例数据：** `heatmap_cor_table.xlsx` | **详细参数：** `references/heatmap_cor_table.md`

### 23. 叠加柱状图[统计] (`bar_stack_stats`)

**脚本：** `bar_stack_stats_api.py` | **示例数据：** `bar_stack_stats.xlsx` | **详细参数：** `references/bar_stack_stats.md`（适用于长型数据，支持统计检验）

### 24. 箱式图 (`box_plot`)

**脚本：** `box_plot_api.py` | **示例数据：** `box_plot_data.csv` | **详细参数：** `references/box_plot.md`

### 25. UpSet图 (`upset_plot`)

**脚本：** `upset_plot_api.py` | **示例数据：** `upset_plot.xlsx` | **详细参数：** `references/upset_plot.md`

### 26. 内嵌柱状图 (`bar_inline`)

**脚本：** `bar_inline_api.py` | **示例数据：** `bar_inline.xlsx` | **详细参数：** `references/bar_inline.md`

### 27. 复杂数值热图 (`heatmap_plot`)

**脚本：** `heatmap_plot_api.py` | **示例数据：** `heatmap_plot_exp.xlsx` + `heatmap_plot_anno.xlsx` | **详细参数：** `references/heatmap_plot.md`（使用 `--exp_path` 和 `--anno_path` 两个输入参数）

### 28. 基线资料表 (`baseline_table`)

**脚本：** `baseline_table_api.py` | **示例数据：** `baseline_table.xlsx` | **详细参数：** `references/baseline_table.md`（输出为 xlsx 表格）

### 29. 堆叠面积图 (`density_stack`)

**脚本：** `density_stack_api.py` | **示例数据：** `density_stack.xlsx` | **详细参数：** `references/density_stack.md`

### 30. 数据分布面积图 (`density_plot`)

**脚本：** `density_plot_api.py` | **示例数据：** `density_plot.xlsx` | **详细参数：** `references/density_plot.md`

## 注意事项

- **不要修改脚本内容**：直接通过命令行参数控制绘图行为，避免修改 `scripts/` 下任何 `.py` 文件
- **报错排查**：运行出错时会显示具体错误信息，根据提示调整参数或数据文件即可，无需修改脚本

## 快速参考

### 同时生成多个图表

```bash
# 火山图
{python} scripts/volcano_plot_api.py --file_path references/volcano_plot_data.csv --plot_save volcano.pdf

# KM曲线
{python} scripts/km_plot_api.py --file_path references/km_plot_data.csv --plot_save km.pdf

# 热图
{python} scripts/heatmap_1anno_api.py --file_path references/heatmap_1anno_data.csv --plot_save heatmap.pdf
```

### 查看脚本帮助

```bash
{python} scripts/volcano_plot_api.py --help
{python} scripts/km_plot_api.py --help
{python} scripts/heatmap_1anno_api.py --help
{python} scripts/forest_plot_api.py --help
# ... 等
```

## 目录结构

```
SKILL.md                         # 本技能说明
scripts/                         # Python脚本
├── volcano_plot_api.py          # 火山图
├── heatmap_1anno_api.py         # 热图
├── km_plot_api.py               # KM生存曲线
├── forest_plot_api.py           # 森林图
├── group_plot_api.py            # 分组比较图
├── line_point_api.py            # 点线图
├── pcr_analysis_api.py          # qPCR分析图
├── pie_chart_api.py             # 饼图
├── radar_plot_api.py            # 雷达图
├── veen_plot_api.py             # 韦恩图
├── bar_plot_api.py              # 一维柱状图
├── bar_stack_table_api.py       # 叠加柱状图
├── bean_plot_api.py             # 豆荚图
├── cor_point_plot_api.py        # 相关性散点图
├── line_chart_api.py            # 折线图
├── pair_plot_api.py             # 配对图
├── rcs_binary_api.py            # 诊断限制性立方样条
├── ridge_plot_api.py            # 山峦图
├── roc_curve_api.py             # 诊断ROC曲线
├── word_cloud_api.py            # 词云图
├── gokegg_analysis_api.py       # GOKEGG分析
├── heatmap_cor_table_api.py     # 相关性热图
├── bar_stack_stats_api.py       # 叠加柱状图[统计]
├── box_plot_api.py              # 箱式图
├── upset_plot_api.py            # UpSet图
├── bar_inline_api.py            # 内嵌柱状图
├── heatmap_plot_api.py          # 复杂数值热图
├── baseline_table_api.py        # 基线资料表
├── density_stack_api.py         # 堆叠面积图
└── density_plot_api.py          # 数据分布面积图
references/                      # 示例数据和参数文档
├── *.csv / *.xlsx               # 示例数据文件（31个）
├── volcano_plot.md              # 火山图参数
├── heatmap_1anno.md             # 热图参数
├── km_plot.md                   # KM生存曲线参数
├── forest_plot.md               # 森林图参数
├── group_plot.md                # 分组比较图参数
├── line_point.md                # 点线图参数
├── pcr_analysis.md              # qPCR分析图参数
├── pie_chart.md                 # 饼图参数
├── radar_plot.md                # 雷达图参数
├── veen_plot.md                 # 韦恩图参数
├── bar_plot.md                  # 一维柱状图参数
├── bar_stack_table.md           # 叠加柱状图参数
├── bean_plot.md                 # 豆荚图参数
├── cor_point_plot.md            # 相关性散点图参数
├── line_chart.md                # 折线图参数
├── pair_plot.md                 # 配对图参数
├── rcs_binary.md                # 诊断限制性立方样条参数
├── ridge_plot.md                # 山峦图参数
├── roc_curve.md                 # 诊断ROC曲线参数
├── word_cloud.md                # 词云图参数
├── gokegg_analysis.md           # GOKEGG分析参数
├── heatmap_cor_table.md         # 相关性热图参数
├── bar_stack_stats.md           # 叠加柱状图[统计]参数
├── box_plot.md                  # 箱式图参数
├── upset_plot.md                # UpSet图参数
├── bar_inline.md                # 内嵌柱状图参数
├── heatmap_plot.md              # 复杂数值热图参数
├── baseline_table.md            # 基线资料表参数
├── density_stack.md             # 堆叠面积图参数
└── density_plot.md              # 数据分布面积图参数
```

本 SKILL.md 所在目录即为 skill 根目录。`scripts/` 和 `references/` 等相对路径均相对于此根目录。

### 渐进式披露说明

匹配到具体模块后，加载对应的 `references/<模块名>.md` 文件获取完整参数表和示例。SKILL.md 中仅保留模块概述，避免一次性呈现过多信息。
