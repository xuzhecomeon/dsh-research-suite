# Data Format Reference

Input: JSON (`.json`) or CSV (`.csv`/`.tsv`). All values are floats unless noted.

---

## Bar Chart (`--type bar` / `--type grouped_bar`)

```json
{
  "labels": ["Group A", "Group B", "Group C"],
  "series": {
    "Series 1": [10.5, 20.3, 15.2],
    "Series 2": [12.0, 18.7, 16.5]
  },
  "errors": {
    "Series 1": [1.2, 0.8, 1.5],
    "Series 2": [0.9, 1.1, 0.7]
  },
  "significance": {
    "Series 1:0": "***",
    "Series 1:1": "*",
    "Series 1:2": "NS"
  }
}
```

### CSV equivalent
```
Group,Series1,Series2
A,10.5,12.0
B,20.3,18.7
C,15.2,16.5
```

---

## Heatmap (`--type heatmap`)

```json
{
  "matrix": [[10, -5, 3], [8, 12, -2], [-1, 7, 15]],
  "row_labels": ["Row A", "Row B", "Row C"],
  "col_labels": ["Col 1", "Col 2", "Col 3"],
  "cbar_label": "Value (units)"
}
```

Override range: `--vmin -20 --vmax 45 --cmap RdBu_r --center 0`

---

## Scatter Plot (`--type scatter`)

```json
{
  "x": [1.2, 2.3, 3.1, 4.5],
  "y": [5.1, 6.2, 4.8, 7.3],
  "groups": ["A", "A", "B", "B"]
}
```

`--trend` to show regression line with correlation coefficient.

---

## Line Chart (`--type line`)

```json
{
  "labels": ["Jan", "Feb", "Mar"],
  "series": {
    "Revenue": [42, 48, 55],
    "Profit": [12, 15, 18]
  },
  "errors": {
    "Revenue": [3, 2, 4],
    "Profit": [1, 1.5, 2]
  }
}
```

### CSV equivalent
```
Month,Revenue,Profit
Jan,42,12
Feb,48,15
Mar,55,18
```

---

## Box Plot / Violin (`--type box` / `--type violin`)

```json
{
  "labels": ["Treatment A", "Treatment B", "Control"],
  "series": {
    "Treatment A": [10, 12, 11, 13, 10, 14],
    "Treatment B": [8, 9, 10, 7, 11, 9],
    "Control": [5, 6, 4, 7, 5, 6]
  }
}
```

---

## Forest Plot (`--type forest`)

```json
{
  "labels": ["Study A", "Study B", "Study C"],
  "estimates": [1.2, 0.8, 1.5],
  "ci_low": [0.9, 0.5, 1.1],
  "ci_high": [1.6, 1.3, 2.0],
  "overall": {
    "estimate": 1.1,
    "ci_low": 0.85,
    "ci_high": 1.35
  },
  "ref_line": 1.0
}
```

---

## Histogram (`--type histogram`)

```json
{
  "values": [1.2, 2.3, 2.1, 3.4, 2.8, 3.1, 2.9, 3.5, 4.0, 3.8],
  "name": "Measurement"
}
```

Or multi-series:
```json
{
  "series": {
    "Group A": [1.2, 2.3, 2.1, 3.4, 2.8],
    "Group B": [2.1, 2.9, 3.5, 3.1, 3.8]
  }
}
```

`--kde` overlay a KDE density curve. `--bins 15` set bins. `--density` normalize.

---

## Density Plot (`--type density`)

Same format as histogram with `"series"`. Each series gets a KDE curve.

---

## Pie / Donut Chart (`--type pie` with `--donut`)

```json
{
  "labels": ["Category A", "Category B", "Category C", "Category D"],
  "values": [35, 25, 20, 20]
}
```

Or:
```json
{
  "labels": ["A", "B", "C", "D"],
  "series": {
    "Distribution": [35, 25, 20, 20]
  }
}
```

`--donut` for donut chart. `--no-pct` to hide percentages.

---

## Radar / Spider Chart (`--type radar`)

```json
{
  "labels": ["Speed", "Power", "Accuracy", "Endurance", "Agility"],
  "series": {
    "Athlete A": [90, 75, 85, 80, 88],
    "Athlete B": [70, 88, 78, 92, 72]
  }
}
```

---

## 3D Surface (`--type surface`)

```json
{
  "x": [1, 2, 3, 4, 5],
  "y": [1, 2, 3, 4, 5],
  "matrix": [
    [0, 1, 2, 3, 4],
    [1, 2, 3, 4, 5],
    [2, 3, 4, 5, 6],
    [3, 4, 5, 6, 7],
    [4, 5, 6, 7, 8]
  ]
}
```

`--contour-floor` to show contour projection on floor. `--cmap viridis`.

---

## 3D Scatter (`--type scatter3d`)

```json
{
  "x": [1.2, 2.3, 3.1, 4.5, 5.0],
  "y": [5.1, 6.2, 4.8, 7.3, 6.8],
  "z": [3.2, 4.1, 2.8, 5.5, 4.9],
  "groups": ["A", "A", "B", "B", "C"]
}
```

---

## Contour Plot (`--type contour`)

```json
{
  "matrix": [[10, 5, 3, 1], [8, 12, 2, 0], [1, 7, 15, 2], [0, 3, 5, 8]],
  "x": [0, 1, 2, 3],
  "y": [0, 1, 2, 3]
}
```

`--no-filled` for line-only contour. `--cmap viridis`.

---

## Multi-panel Subplots (`--type subplots`)

```json
[
  {
    "type": "bar",
    "data": {"labels": ["A", "B"], "series": {"X": [1, 2], "Y": [3, 4]}},
    "title": "Panel A",
    "xlabel": "Group",
    "ylabel": "Value"
  },
  {
    "type": "scatter",
    "data": {"x": [1, 2, 3], "y": [4, 5, 6]},
    "title": "Panel B",
    "xlabel": "X",
    "ylabel": "Y"
  }
]
```

`--layout 2x2` or `--layout auto`.
