# Science Figures

> **Publication-quality academic figure generator** — 17 chart types, 8 journal styles, CJK support, pure local Python.

Generate publication-ready figures for academic papers, theses, and posters with a single command. Powered by [scienceplots](https://github.com/garrettj403/SciencePlots) + matplotlib. No GUI, no cloud, no data leaving your machine.

```bash
python scripts/gen_figure.py --type bar --data data.json --out figure.png --style nature
```

![Bar chart example](https://img.shields.io/badge/chart-bar-blue) ![Nature style](https://img.shields.io/badge/style-nature-success)

---

## Features

- **17 chart types**: bar, grouped bar, heatmap, scatter, line, box, violin, forest, histogram, density, pie, donut, radar, 3D surface, contour, 3D scatter, multi-panel subplots
- **8 journal styles**: Nature, Science, IEEE, Springer, Lancet, ACS, APS, AAAS
- **CJK auto-detection**: automatically loads Chinese/Japanese/Korean fonts when needed
- **Bulk subplots**: compose multiple chart types into a single multi-panel figure
- **No LaTeX required**: built-in fallback styles when scienceplots not installed
- **Vector output**: PNG, SVG, PDF all supported
- **Cross-platform**: Windows, macOS, Linux

## Installation

```bash
# 1. Clone the repository
git clone https://gitee.com/Zichuantju/science-figures.git
cd science-figures

# 2. Install dependencies
pip install matplotlib numpy scipy scienceplots  # optional but recommended
```

> **Note**: `scienceplots` requires LaTeX. If you don't have LaTeX installed, the generator falls back to built-in equivalent styles automatically.

## Quick start

```bash
# Basic bar chart (grouped)
python scripts/gen_figure.py --type bar --data examples/bar.json --out bar.png

# Scatter with trend line, IEEE style
python scripts/gen_figure.py --type scatter --data examples/scatter.csv --out scatter.svg --style ieee

# 3D surface with contour floor projection, Science style
python scripts/gen_figure.py --type surface --data examples/surface.json --out surface.png --style science --contour-floor

# Multi-panel subplots
python scripts/gen_figure.py --type subplots --data examples/panels.json --out combined.png --layout 2x2
```

## Chart types

| Type | `--type` | Description |
|------|----------|-------------|
| Bar chart | `bar` / `grouped_bar` | Grouped bars with error bars and significance markers |
| Heatmap | `heatmap` | Annotated matrix heatmap, customizable colormap |
| Scatter plot | `scatter` | Scatter with optional regression trend line and grouping |
| Line chart | `line` | Line plot with optional error bands |
| Box plot | `box` / `boxplot` | Box plot with jittered scatter overlay |
| Violin plot | `violin` | Violin plot with inner box statistics |
| Forest plot | `forest` | Meta-analysis forest plot with overall diamond |
| Histogram | `histogram` | Histogram with optional KDE density overlay |
| Density plot | `density` | KDE density curves, multi-group |
| Pie chart | `pie` | Pie or donut chart with percentage labels |
| Radar chart | `radar` / `spider` | Multi-variable radar/spider chart |
| 3D surface | `surface` | 3D surface with optional contour floor |
| Contour plot | `contour` | Filled or line-only contour plot |
| 3D scatter | `scatter3d` | 3D scatter with grouping |
| Subplots | `subplots` | Multi-panel composite with mixed chart types |

## Journal styles

| `--style` | Journal | Font family |
|-----------|---------|-------------|
| `nature` | Nature | Sans-serif |
| `science` | Science | Sans-serif |
| `ieee` | IEEE | Serif |
| `springer` | Springer | Serif |
| `lancet` | The Lancet | Serif |
| `aaas` | Science/AAAS | Sans-serif |
| `acs` | ACS | Sans-serif |
| `aps` | APS (Physical Review) | Serif |

## CLI options

| Argument | Description | Default |
|----------|-------------|---------|
| `--type` / `-t` | Chart type (required) | — |
| `--data` / `-d` | Data file path (JSON/CSV) | — |
| `--out` / `-o` | Output file path (.png/.svg/.pdf) | — |
| `--style` / `-s` | Journal style | `nature` |
| `--title` | Figure title (`\n` for newline) | — |
| `--xlabel` | X-axis label | — |
| `--ylabel` | Y-axis label | — |
| `--width` | Figure width (inches) | style default |
| `--height` | Figure height (inches) | style default |
| `--dpi` | Output resolution | 300 |
| `--cjk` | Force CJK font mode | auto-detect |
| `--cjk-font` | Path to CJK font file | auto-detect |
| `--legend` / `--no-legend` | Show/hide legend | shown |
| `--show-values` | Show value labels on bars | off |
| `--trend` / `--no-trend` | Regression line (scatter) | shown |
| `--cmap` | Colormap (heatmap/contour/surface) | `RdBu_r` / `viridis` |
| `--vmin` / `--vmax` | Color scale range | auto |
| `--center` | Diverging colormap center | — |
| `--kde` / `--no-kde` | KDE overlay (histogram) | shown |
| `--bins` | Histogram bin count | `auto` |
| `--density` | Normalize histogram | off |
| `--donut` | Donut chart (pie) | off |
| `--filled` / `--no-filled` | Filled contour | filled |
| `--contour-floor` | Contour floor on 3D surface | off |
| `--layout` | Subplot layout (`auto`, `2x2`, etc.) | `auto` |
| `--list-styles` | List available styles | — |

## Data format

Input is **JSON** or **CSV/TSV**. Columnar data auto-detects structure.

### JSON examples

**Bar chart:**
```json
{
  "labels": ["Group A", "Group B", "Group C"],
  "series": { "Series 1": [10.5, 20.3, 15.2], "Series 2": [12.0, 18.7, 16.5] },
  "errors": { "Series 1": [1.2, 0.8, 1.5], "Series 2": [0.9, 1.1, 0.7] },
  "significance": { "0": "***", "1": "ns" }
}
```

**Scatter plot:**
```json
{
  "x": [1.2, 2.3, 3.1, 4.5],
  "y": [5.1, 6.2, 4.8, 7.3],
  "groups": ["A", "A", "B", "B"]
}
```

**Forest plot (meta-analysis):**
```json
{
  "labels": ["Study A", "Study B", "Study C"],
  "estimates": [1.2, 0.8, 1.5],
  "ci_low": [0.9, 0.5, 1.1],
  "ci_high": [1.6, 1.3, 2.0],
  "overall": { "estimate": 1.1, "ci_low": 0.85, "ci_high": 1.35 },
  "ref_line": 1.0
}
```

**Multi-panel subplots:**
```json
[
  {
    "type": "bar",
    "data": {"labels": ["A", "B"], "series": {"X": [1, 2]}},
    "title": "Panel A",
    "xlabel": "Group",
    "ylabel": "Value"
  },
  {
    "type": "scatter",
    "data": {"x": [1, 2, 3], "y": [4, 5, 6]},
    "title": "Panel B"
  }
]
```

See [references/data-formats.md](references/data-formats.md) for all formats and CSV equivalents.

## Project structure

```
science-figures/
├── scripts/
│   ├── gen_figure.py         # CLI entry point
│   ├── fig_core.py           # Core engine: style, labels, saving
│   ├── data_loader.py        # JSON/CSV data loading with format detection
│   ├── style_manager.py      # scienceplots integration + built-in fallbacks
│   ├── font_detector.py      # CJK font auto-detection
│   ├── fig_bar.py            # Grouped bar chart
│   ├── fig_heatmap.py        # Heatmap
│   ├── fig_scatter.py        # Scatter plot
│   ├── fig_line.py           # Line chart
│   ├── fig_box.py            # Box + violin plot
│   ├── fig_forest.py         # Forest plot (meta-analysis)
│   ├── fig_distribution.py   # Histogram + density plot
│   ├── fig_pie.py            # Pie + donut chart
│   ├── fig_radar.py          # Radar/spider chart
│   ├── fig_3d.py             # 3D surface, contour, 3D scatter
│   └── fig_subplots.py       # Multi-panel subplot composition
└── references/
    ├── data-formats.md        # Full data format documentation
    ├── style-gallery.md       # Style and color palette reference
    └── faq.md                 # Troubleshooting and FAQs
```

## Dependencies

| Package | Required | Notes |
|---------|----------|-------|
| `matplotlib` | Yes | Core plotting |
| `numpy` | Yes | Numeric operations |
| `scipy` | Yes | KDE, trend lines |
| `SciencePlots` | No | Enhanced journal styles (recommended) |

## Comparison with academic-figures

| Feature | science-figures | academic-figures |
|---------|:---------------:|:----------------:|
| Chart types | **17** | 7 |
| Journal styles | **8** (scienceplots) | 4 (custom themes) |
| Histogram / density | Yes | — |
| Pie / donut | Yes | — |
| Radar / spider | Yes | — |
| 3D (surface/contour/scatter) | Yes | — |
| Multi-panel subplots | Yes | — |
| CJK auto-detection | Yes | — |
| Vector output (PDF/SVG) | Yes | — |
| Modular architecture | Yes | Single script |

## License

This project is open source. See the LICENSE file for details.

---

Built for researchers who need publication-ready figures without GUI tools or cloud services.
