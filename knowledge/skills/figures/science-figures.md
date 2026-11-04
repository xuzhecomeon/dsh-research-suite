<!-- source: science-figures @ science-figures__skillhub | domain: figures -->

---
name: science-figures
description: >
  基于 scienceplots 库的出版级学术论文配图生成器。支持 bar/grouped_bar/heatmap/scatter/line/box/violin/forest/
  histogram/density/pie/donut/radar/surface/contour/scatter3d/subplots 共 17 种图表类型，
  8 种期刊风格 (ieee/nature/springer/aaas/science/lancet/acs/aps)，中文自动检测，300DPI PNG/SVG/PDF 输出。
  纯本地运行，数据不出本机。适用于学术论文、学位论文、期刊投稿、会议海报等场景。
  触发词："论文配图"、"画图"、"柱状图"、"热力图"、"散点图"、"森林图"、"箱线图"、"折线图"、"小提琴图"、
  "直方图"、"饼图"、"雷达图"、"3D图"、"曲面图"、"等高线图"、"子图"、"make a figure"、"generate chart"、
  "plot data"、"create chart"、"science figure"、"publication figure"、"journal figure"。
---

# Science Figures — 学术论文配图生成器 (scienceplots)

一行命令从 JSON/CSV 数据生成出版级学术图表。基于 **scienceplots** + **matplotlib**，纯本地运行。

## 快速开始

```bash
# 基本用法
python scripts/gen_figure.py --type bar --data data.json --out figure.png

# 指定期刊风格
python scripts/gen_figure.py --type scatter --data data.json --style ieee --out scatter.png

# 3D 曲面图
python scripts/gen_figure.py --type surface --data data.json --style science --out surface.png

# 多子图组合
python scripts/gen_figure.py --type subplots --data panels.json --layout 2x2 --out combined.png
```

## 支持的图表类型 (17种)

| 类型 | `--type` | 说明 | 关键参数 |
|------|----------|------|----------|
| 柱状图 | `bar` / `grouped_bar` | 分组柱状图+误差线+显著性标记 | `--show-values` |
| 热力图 | `heatmap` | 带注释矩阵热力图 | `--cmap`, `--vmin`, `--vmax`, `--center` |
| 散点图 | `scatter` | 散点+趋势线+分组着色 | `--trend`, `--no-trend` |
| 折线图 | `line` | 折线图+误差带 | — |
| 箱线图 | `box` / `boxplot` | 箱线图+散点抖动 | — |
| 小提琴图 | `violin` | 小提琴+内部箱线 | — |
| 森林图 | `forest` | 效应量+置信区间(元分析) | JSON专用 |
| **直方图** | `histogram` | 直方图+KDE叠加 | `--kde`, `--bins`, `--density` |
| **密度图** | `density` | KDE密度曲线 | — |
| **饼图** | `pie` | 饼图/环形图 | `--donut`, `--no-pct` |
| **雷达图** | `radar` | 多变量雷达/蜘蛛图 | — |
| **3D曲面** | `surface` | 3D曲面图 | `--cmap`, `--contour-floor` |
| **等高线** | `contour` | 2D等高线/填充等高线 | `--filled`, `--cmap` |
| **3D散点** | `scatter3d` | 3D散点图+分组 | — |
| **子图组合** | `subplots` | 多Panel组合布局 | `--layout` |
| (alias) | `donut` | donut图 | 等同 `pie --donut` |

## 期刊风格 (8种，基于 scienceplots)

| `--style` | 期刊 | 字体 |
|-----------|------|------|
| `ieee` | IEEE | Serif |
| `nature` | Nature | Sans-serif |
| `springer` | Springer | Serif |
| `aaas` | Science/AAAS | Sans-serif |
| `science` | Science | Sans-serif |
| `lancet` | The Lancet | Serif |
| `acs` | ACS | Sans-serif |
| `aps` | APS | Serif |

> **依赖**：推荐安装 `pip install SciencePlots`（需要 LaTeX）。如未安装，内置等效样式作为后备。

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--type` / `-t` | 图表类型 | 必填 |
| `--data` / `-d` | 数据文件路径 (JSON/CSV) | 必填 |
| `--out` / `-o` | 输出文件 (.png/.svg/.pdf) | 必填 |
| `--style` / `-s` | 期刊风格 | nature |
| `--title` | 标题 (\\n换行) | 无 |
| `--xlabel` | X轴标签 | 无 |
| `--ylabel` | Y轴标签 | 无 |
| `--cjk` | 强制启用中文字体 | 自动检测 |
| `--cjk-font` | 指定中文字体路径 | 无 |
| `--width` | 图宽(英寸) | 按风格 |
| `--height` | 图高(英寸) | 按风格 |
| `--dpi` | 输出DPI | 300 |
| `--legend` / `--no-legend` | 图例开关 | 显示 |
| `--show-values` | 柱状图数值标签 | 关闭 |
| `--trend` / `--no-trend` | 散点趋势线 | 显示 |
| `--cmap` | 热力图/曲面配色 | RdBu_r/viridis |
| `--vmin` / `--vmax` | 热力图数值范围 | 自动 |
| `--center` | 发散色条中心值 | 无 |
| `--kde` / `--no-kde` | 直方图KDE叠加 | 显示 |
| `--bins` | 直方图分箱数 | auto |
| `--density` | 直方图归一化 | 关闭 |
| `--donut` | 饼图转环形图 | 关闭 |
| `--filled` / `--no-filled` | 填充等高线 | 填充 |
| `--contour-floor` | 3D曲面投影等高线 | 关闭 |
| `--layout` | 子图布局 (auto/RxC) | auto |
| `--list-styles` | 列出所有风格 | — |

## 数据格式

支持 JSON 和 CSV。CSV 自动推断数据格式。详见 [references/data-formats.md](references/data-formats.md)。

## 文件结构

```
science-figures/
├── SKILL.md                         # 本文档
├── scripts/
│   ├── gen_figure.py                # 主入口 (CLI)
│   ├── fig_core.py                  # 核心引擎
│   ├── style_manager.py             # scienceplots 样式管理
│   ├── data_loader.py               # 数据加载
│   ├── font_detector.py             # CJK/字体检测
│   ├── fig_bar.py                   # 柱状图
│   ├── fig_heatmap.py               # 热力图
│   ├── fig_scatter.py               # 散点图
│   ├── fig_line.py                  # 折线图
│   ├── fig_box.py                   # 箱线图 + 小提琴图
│   ├── fig_forest.py                # 森林图
│   ├── fig_distribution.py          # 直方图 + 密度图
│   ├── fig_pie.py                   # 饼图 + 环形图
│   ├── fig_radar.py                 # 雷达图
│   ├── fig_3d.py                    # 3D曲面/等高线/3D散点
│   └── fig_subplots.py              # 多子图组合
└── references/
    ├── data-formats.md              # 数据格式详细说明
    ├── style-gallery.md             # 样式预览
    └── faq.md                       # 常见问题
```

## 与 academic-figures 对比

| 特性 | academic-figures | science-figures |
|------|:---:|:---:|
| 图表类型 | 7 种 | **17 种** |
| 样式/主题 | 4 种自定主题 | **8 种 scienceplots 期刊风格** |
| 直方图/密度图 | 无 | 有 |
| 饼图/环形图 | 无 | 有 |
| 雷达图 | 无 | 有 |
| 3D 图 | 无 | surface/contour/scatter3d |
| 子图组合 | 无 | 有 |
| 架构 | 单文件脚本 | 模块化拆分 |
| 数据格式别名 | 有限 | 更宽松的 key 自动匹配 |
| PDF 输出 | 无 | 有 |
