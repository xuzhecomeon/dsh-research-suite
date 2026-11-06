# FAQ — science-figures

### Q: 中文显示为方块？
A: 脚本会自动检测中文并加载系统字体。如果未检测到，手动 `--cjk` 或 `--cjk-font <path>` 指定字体路径。

### Q: Windows 下 `python3` 报错？
A: 使用 `python` 替代 `python3`。

### Q: 安装 scienceplots 失败？
A: 需要 LaTeX 发行版 (MiKTeX/TeX Live)。如果不想装 LaTeX，skill 内置了等效样式作为后备，不影响使用。

### Q: 如何输出 PDF 矢量格式？
A: 输出文件名后缀写 `.pdf`：`--out figure.pdf`

### Q: 如何输出 SVG 矢量格式？
A: `--out figure.svg`

### Q: scienceplots 有哪些可用样式？
A: `--list-styles` 查看，或参考 `references/style-gallery.md`。

### Q: 饼图和 donut 图有什么区别？
A: 饼图 `--type pie`；donut 图 `--type pie --donut`（添加中心空心）。

### Q: 箱线图和 violin 图的区别？
A: 箱线图显示分位数；violin 图额外显示数据分布密度。

### Q: 3D 图支持什么格式？
A: `surface`（曲面）、`contour`（等高线）、`scatter3d`（3D 散点）。

### Q: 如何画多子图？
A: `--type subplots`，数据用 JSON 数组格式描述每个 panel。参考 `references/data-formats.md`。

### Q: 热力图 colormap 有哪些？
A: 支持所有 matplotlib colormap。常用：`RdBu_r`（推荐）、`viridis`、`plasma`、`coolwarm`、`YlOrRd`。

### Q: 图片太模糊？
A: 默认 300 DPI。用 `--dpi 600` 提高。

### Q: CSV 支持哪些图表类型？
A: bar, line, scatter, box, violin, histogram, density, pie, radar。heatmap/forest/surface/contour 建议用 JSON。
