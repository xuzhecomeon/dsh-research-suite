---
name: xmed-figure
description: "Scientific figure generation via X-Med MCP. Volcano, PCA, enrichment, survival, correlation. CSV/Excel upload, chart matching, parameter configuration, publication-grade multi-panel."
description_zh: "科研数据可视化：火山图、PCA、富集分析、生存分析等，自动图表匹配，发表级输出。"
description_en: "Scientific visualization: volcano, PCA, enrichment, survival, and more."
version: 1.0.9
homepage: https://x-med-kyy.dazd.cn
source_type: git
git_url: https://gitlab.dazd.cn/yusm1/xmed-figure-expert.git
allowed-tools: Read,Write,Bash
---

# 科研绘图 (xmed-figure)

> **MCP 连接器**：`xmed-mcp-service` | 出品方：迪安诊断科研云智能分析平台 | 官网：https://x-med-kyy.dazd.cn

通过智能科研云 MCP 生成科研数据可视化图表，全面覆盖科研场景的图表类型。

## 适用场景

- 科研数据可视化：差异表达、富集分析、生存分析、相关性分析等
- 发表级图表生成：支持 30 种图表类型，自动匹配参数
- 多面板组图：≥2 个图表时自动拼接为发表级组合图

## 不适用场景

- 非结构化数据（自由文本、图片、音频）
- 非科研绘图的通用图表（业务流程、财务报表、管理看板）
- 需要实时交互式可视化的场景（本服务为静态图表生成）

## 0. 前置准备（安装与环境配置）

**首次使用前**，安装所有 Python 依赖：

```bash
pip install -r scripts/requirements.txt
```

依赖包：`requests`（HTTP 请求）、`Pillow`（组图拼接）、`openpyxl`（Excel 读取）、`xlrd`（旧版 Excel 读取）。

> **工具权限**：本技能使用 Read（读取 reference 参数定义文件）、Write（生成图表输出文件）、Bash（执行 Python 脚本进行数据上传、转换和组图）。

> **MCP 连接配置**：本技能依赖 `xmed-mcp-service` MCP 连接器，需在 WorkBuddy 中完成 OAuth 授权后使用。授权后 MCP 工具（`get_chart_input_files`、`submit_analysis_task`、`wait_for_task`）自动可用，无需额外配置。

> **数据隐私**：上传的科研数据通过 MCP 服务传输至远程绘图引擎渲染，uploadKey 为临时令牌（过期自动失效）。请勿上传包含直接标识符（姓名、身份证号、手机号等）的敏感数据，任务完成后可联系平台管理员清理数据。

---

## 1. 图表类型匹配

### 1.1 场景关键词 → chartType 映射

| 场景关键词 | 候选 chartType | 优先级 |
|-----------|---------------|:--:|
| 差异表达 / 差异分析 / 上调下调 / log2FC / pvalue | volcano | 1 |
| 降维 / 聚类 / 分群 / 样本分布 | pca | 2 |
| 富集分析 / GO / KEGG / 通路 / 功能注释 | enrich_bar, enrich_bubble, enrich_point | 1 |
| 相关性 / 相关系数 | cor_pheatmap, cor_matrix, correlation_network | 2 |
| 韦恩 / 交集 / 并集 | venn, upset | 1 |
| 生存分析 / 生存曲线 / KM | km_risk_table | 1 |
| 随时间变化 / 趋势 / 时间序列 | dotline_columns, stacked_area, gantt | 2 |
| 分类 / 占比 / 组成 | donut, stacked_area | 2 |
| 比较 / 差异 / 对比 | bilateral_bar, dumbbell | 2 |
| 模型评估 / 分类器 / 诊断 | roc, nomogram | 1 |
| 网络 / 关系图 | correlation_network, sankey_diagram | 2 |

### 1.2 数据驱动推断

| 文件名关键词 | 推断 chartType |
|-------------|---------------|
| `*deg*` / `*diff*` / `*差异*` / `*DE*` | volcano |
| `*go*` / `*kegg*` / `*enrich*` / `*富集*` | enrich_bar, enrich_bubble, enrich_point |
| `*survival*` / `*生存*` | km_risk_table |
| `*correlation*` / `*cor*` / `*相关*` | cor_pheatmap, cor_matrix |
| `*venn*` / `*韦恩*` | venn |
| `*pca*` / `*降维*` | pca |

### 1.3 图表类型索引表

| 图表名称 | chartType | 描述 |
|----------|-----------|------|
| 火山图 | volcano | 通过散点的位置和颜色展示差异分析结果 |
| 样本-鉴定柱形图 | protein_number | 通过柱形高度展示样本特征或鉴定结果 |
| PCA | pca | 通过降维呈现样本间的相似性和分组结构 |
| 组-CV柱形图 | cv_analysis | 通过柱形高度表示不同组别的数据变异程度 |
| 相关性热图 | cor_pheatmap | 通过颜色梯度展示变量之间相关性 |
| 富集条形图 | enrich_bar | 通过条形长度和颜色展示功能富集分析结果 |
| 富集气泡图 | enrich_bubble | 通过气泡的大小、颜色和位置展示功能富集分析结果 |
| 富集-点图 | enrich_point | 通过点的大小、颜色和位置展示功能富集分析结果 |
| 桑基图 | sankey_diagram | 描述数据的流动、转换、变化过程 |
| 韦恩图 | venn | 用图形直观表示集合之间逻辑关系 |
| 哑铃图 | dumbbell | 比较同一组数据在两个不同条件下的变化情况 |
| 分层聚类图 | cluster_tree | 展示数据层次聚类结果 |
| 堆叠面积图 | stacked_area | 显示不同物种在特定区域内的分布和相对数量 |
| 双向柱状图 | bilateral_bar | 比较方向相反的两组数据 |
| 甘特图 | gantt | 展示项目的进度和成果 |
| 圆环图 | donut | 展示数据的占比关系 |
| 交集关系图 | upset | 通过矩阵布局展示集合的交集大小 |
| 三元组图 | ternary | 以三元组形式表示的关系图 |
| 相关性矩阵图 | cor_matrix | 展示多个变量之间两两相关性 |
| 诺莫图 | nomogram | 将多因素回归分析结果可视化 |
| 分组蜂群图 | beeswarm | 可视化分类数据分布 |
| 分组直方图 | grouped_histogram | 展示多个组数据分布 |
| KM生存分析图 | km_risk_table | 展示不同组别随时间推移的生存概率变化 |
| 雷达图 | radar | 比较多变量数据 |
| ROC 曲线图 | roc | 评估二分类模型预测性能 |
| 散点图 | scatter | 展示两个连续变量之间的关系 |
| 四象限图 | four_quadrant | 分析和比较两个变量关系 |
| 线性回归 | linear_regression | 展示两个变量间线性关系 |
| 点线图 | dotline_columns | 结合数据点与连线 |
| 相关性网络图 | correlation_network | 展示变量之间相关性关系 |

---

## 2. 脚本调用

### upload_files.py — 上传文件

```bash
python scripts/upload_files.py <file1.csv> [file2.csv ...] --data-names <name1>[,name2...] --upload-key <key>
```

| 参数 | 必填 | 说明 |
|------|:--:|------|
| `files` (位置) | ✅ | 文件路径列表 |
| `--data-names` | ✅ | dataFileName 映射，逗号分隔，与文件顺序一一对应 |
| `--upload-key` | ✅ | 文件上传临时令牌，由 `get_chart_input_files` 返回 |

> **`--data-names` 必须与 `get_chart_input_files` 返回的 `dataFileName` 一致**

### convert_to_csv.py — 格式转换

```bash
python scripts/convert_to_csv.py <文件> [output] [--sheet 0]
```

| 参数 | 必填 | 说明 |
|------|:--:|------|
| `file` (位置) | ✅ | 待转换文件 (.xlsx/.xls/.tsv/.txt) |
| `output` | | 输出 CSV 路径，默认同目录同名 `.csv` |
| `--sheet` | | Excel 工作表索引，默认 0 |

转换后自动输出前 5 行数据预览，检查列名和格式是否正确。

### download_results.py — 下载结果图

```bash
python scripts/download_results.py --urls "url1,url2" --output-dir ./output
```

| 参数 | 必填 | 说明 |
|------|:--:|------|
| `--urls` | ✅ | 图片 URL 列表，逗号分隔 |
| `--output-dir` | | 输出目录，默认 `./output` |

### compose_figure.py — 发表级多面板组图

```bash
python scripts/compose_figure.py \
  --images "./output/result_1.png,./output/result_2.png" \
  --title "Figure 1. Analysis overview" \
  --output figure1.png
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--images` | 必填 | 本地图片路径，逗号分隔 |
| `--layout` | 自动推算 | 1→1×1, 2→1×2, 3→1×3, 4→2×2, 5/6→2×3, 7+→ceil(n/3)×3（每行最多 3 列，自动换行） |
| `--labels` | 自动 A/B/C... | 面板标签（左上角粗体） |
| `--title` | 无 | 顶部标题 |
| `--font-size` | 14 | 标签字号，范围：8 ~ 24 |
| `--output` | `figure_combined.png` | 输出文件 |
| `--dpi` | 300 | 分辨率 |
| `--format` | `png` | 输出格式 png/pdf |

> 所有图片自动缩放到最小宽度，每行独立取最大高度，保持视觉平衡。输出 JSON 校验信息。

### check_files.py — 检查文件要求

```bash
python scripts/check_files.py <chartType> --server-data '<json>'
```

| 参数 | 必填 | 说明 |
|------|:--:|------|
| `chartType` (位置) | ✅ | 图表类型代号 |
| `--server-data` | ✅ | `get_chart_input_files` MCP 返回的 JSON 字符串 |

输出 JSON：`{chartType, referenceRequirements, serverFiles: [{dataFileName, showFileName}], uploadKey, uploadExpire}`

### run_analysis — 一键执行分析

通过 MCP 工具直接完成：`submit_analysis_task` → `wait_for_task` → 下载结果。

- 提交任务 → `submit_analysis_task(chartType, files, params)`
- 轮询等待 → `wait_for_task(taskId, waitSeconds=25)` 循环直到 `FINISHED` / `FAILED`
- 下载结果 → `python scripts/download_results.py --urls "url1,url2" --output-dir ./output`

### 公共参数

#### 期刊配色方案

当用户指定期刊配色时，使用以下预定义方案：

| 期刊 | 颜色值 |
|------|--------|
| NPG | `#E64B35FF`, `#4DBBD5FF`, `#00A087FF`, `#3C5488FF`, `#F39B7FFF`, `#8491B4FF`, `#91D1C2FF`, `#DC0000FF`, `#7E6148FF`, `#B09C85FF` |
| AAAS | `#3B4992FF`, `#EE0000FF`, `#008B45FF`, `#631879FF`, `#008280FF`, `#BB0021FF`, `#5F559BFF`, `#A20056FF`, `#808180FF`, `#1B1919FF` |
| NEJM | `#BC3C29FF`, `#0072B5FF`, `#E18727FF`, `#20854EFF`, `#7876B1FF`, `#6F99ADFF`, `#FFDC91FF`, `#EE4C97FF` |
| Lancet | `#00468BFF`, `#ED0000FF`, `#42B540FF`, `#0099B4FF`, `#925E9FFF`, `#FDAF91FF`, `#AD002AFF`, `#ADB6B6FF`, `#1B1919FF` |
| JAMA | `#374E55FF`, `#DF8F44FF`, `#42B540FF`, `#0099B4FF`, `#925E9FFF`, `#FDAF91FF`, `#AD002AFF`, `#ADB6B6FF`, `#1B1919FF` |
| JCO | `#0073C2FF`, `#EFC000FF`, `#868686FF`, `#CD534CFF`, `#7AA6DCFF`, `#003C67FF`, `#8F7700FF`, `#3B3B3BFF`, `#A73030FF`, `#4A6990FF` |
| UCSCGB | `#FF0000FF`, `#FF9900FF`, `#FFCC00FF`, `#66FF00FF`, `#00FF00FF`, `#00FF66FF`, `#00FFCCFF`, `#00CCFFFF`, `#0066FFFF`, `#0000FFFF`, `#6600FFFF`, `#CC00FFFF`, `#FF00CCFF`, `#FF0066FF`, `#FF9999FF`, `#FFCC99FF`, `#FFFF99FF`, `#CCFF99FF`, `#99FF99FF`, `#99FFCCFF`, `#99FFFFFF`, `#99CCFFFF`, `#9999FFFF`, `#CC99FFFF`, `#FF99FFFF`, `#FF99CCFF` |
| IGV | `#5050FFFF`, `#CE3D32FF`, `#749B58FF`, `#F0E685FF`, `#466983FF`, `#BA6338FF`, `#5DB1DDFF`, `#802268FF`, `#6BD76BFF`, `#D595A7FF`, `#924822FF`, `#837B8DFF`, `#C75127FF`, `#D58F5CFF`, `#7A65A5FF`, `#E4AF69FF`, `#3B1B53FF`, `#CDDEB7FF`, `#612A79FF`, `#AE1F63FF`, `#E7C76FFF`, `#5A655EFF`, `#CC9900FF`, `#99CC00FF`, `#A9A9A9FF`, `#746D75FF`, `#6600FFFF`, `#0066CCFF`, `#FFCC99FF`, `#99CCFFFF`, `#CC99FFFF`, `#FF99CCFF`, `#CCFF99FF`, `#99FFCCFF`, `#99FF99FF`, `#FFCC66FF`, `#FF9900FF`, `#FF6600FF`, `#6666FFFF`, `#9966FFFF`, `#FF66FFFF`, `#66FF66FF`, `#66FFCCFF`, `#66FFFFFF`, `#66CCFFFF`, `#CC66FFFF`, `#FF66CCFF`, `#CCFF66FF`, `#FFFF66FF`, `#FFCCFFFF`, `#CCCCFFFF` |

#### 输出图片默认参数

系统默认输出 dpi=150，png 格式。

---

## 3. MCP 工具参考

### `get_chart_input_files`

| 参数 | 类型 | 必填 |
|------|------|------|
| chartType | string | ✅ |

返回 `{inputFiles: [{dataFileName, showFileName}], uploadKey, uploadExpire}`

### `submit_analysis_task`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chartType | string | ✅ | 图表代号 |
| files | map\<string,string\> | ❌ | `{dataFileName: fileId}` |
| instanceId | string | ❌ | 复用已有数据仅重新调参 |
| params | map\<string,object\> | ❌ | 图表参数 |

返回 `{taskId, instanceId, status: "SUMMITED"}`

### `wait_for_task`

| 参数 | 类型 | 必填 |
|------|------|------|
| taskId | string | ✅ |
| waitSeconds | number | ❌ 默认 25，上限 25 |

| 返回 status | 含义 |
|-------------|------|
| `ANALYSIS` | 继续轮询 |
| `FINISHED` | 终态，含 `results` URL 数组 |
| `FAILED` | 终态，含 `failReason` |

### `get_task_result`

| 参数 | 类型 | 必填 |
|------|------|------|
| taskId | string | ✅ |

立即返回 `{status, results, failReason, taskDetail}`

---

## 4. 错误处理

| 错误码 | 动作 |
|--------|------|
| `UNKNOWN_CHART` | 引导用户从索引表中选择；当前未覆盖的图表类型可访问官网 https://x-med-kyy.dazd.cn 查看 |
| `NO_INPUT` | 提示用户上传文件或提供历史 instanceId |
| `INPUT_FILES_INCOMPLETE` | 对照 `inputFiles` 向用户补收缺失文件 |
| `INVALID_PARAMS_JSON` | 检查参数 JSON 格式后重试 |
| `TASK_NOT_FOUND` | 确认 taskId 或重新提交 |
| `UPSTREAM_ERROR` | 告知后端系统异常，建议稍后重试 |
| `MCP_UNAVAILABLE` | MCP 服务不可达时提示用户检查网络，稍后重试，或联系管理员 |

### 脚本级错误码

| 错误码 | 来源 | 动作 |
|--------|------|------|
| `FILE_NOT_FOUND` | upload_files.py | 检查文件路径是否正确，文件是否被移动或删除 |
| `NETWORK_ERROR` | upload_files.py | 检查网络连接，稍后重试 |
| `HTTP {code}` | upload_files.py | 根据状态码排查：5xx 后端异常稍后重试，4xx 检查参数 |
| `INVALID_RESPONSE` | upload_files.py | 检查 MCP 服务是否正常运行 |
| `DOMAIN_NOT_ALLOWED` | download_results.py | 下载 URL 域名不在白名单，检查 MCP 返回的结果 URL 是否正确 |
| `DOWNLOAD_FAILED` | download_results.py | 网络下载失败，稍后重试 |
| `NO_URLS` | download_results.py | 未提供图片 URL，检查 MCP 任务结果是否包含图片 |
| `INVALID_CHART_TYPE` | check_files.py | chartType 不在支持列表中，引导用户从索引表选择 |
| `INVALID_SERVER_DATA` | check_files.py | MCP 返回数据格式异常，重试 `get_chart_input_files` |

### uploadKey 过期恢复

`uploadKey` 有过期时间（`uploadExpire`），过期后上传会失败：

1. 重新调用 `get_chart_input_files(chartType)` 获取新的 uploadKey
2. 使用新 key 重新执行 `upload_files.py --upload-key <new-key>`
3. 无需重新提交任务实例

---

## 5. 示例：火山图

1. 用户说"画火山图" → 匹配 `volcano`
2. 调用 `get_chart_input_files("volcano")` → 告知用户上传差异分析文件
3. 用户上传 → 运行 `python scripts/upload_files.py deg_result.csv --data-names sample_raw_data --upload-key xyzabc`
4. 读取 `references/volcano.md` → 确认参数
5. 调用 `submit_analysis_task("volcano", {"sample_raw_data":"111"}, {"cutoff_pvalue":0.05,"dfc":2,"type":"type1"})`
6. 循环 `wait_for_task` 直到 `FINISHED`
7. 展示本地结果图片，再解读数据分布