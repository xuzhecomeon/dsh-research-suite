# 火山图 (volcano)

> 火山图通过散点的位置和颜色展示差异分析结果

## 文件要求

上传的文件列名必须包含：基因名列 + log2FC列 + pvalue列

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| xcol | string | 是 | log2FC | x 轴数据列名，必须从用户上传的差异蛋白文件列名中选择 |
| ycol | string | 是 | pvalue | y 轴数据列名，必须从用户上传的差异蛋白文件列名中选择 |
| labels | string | 否 | "" | 标签数据列名，从用户上传的差异蛋白文件列名中选择 |
| cutoff_pvalue | number | 否 | 0.05 | 显著性水平阈值，范围：0.01 ~ 1 |
| dfc | number/string | 否 | 2 | 差异倍数，范围：0 ~ 100 |
| color | string | 否 | color1 | 散点颜色主题，枚举：color1（#BB0021FF, #808180FF, #008280FF）、color2（#EE0000FF, #1B1919FF, #008B45FF）、color3（#631879FF, #1B1919FF, #3B4992FF）；rgba颜色值分别对应上调/不显著/下调。 |
| type | string | 否 | type1 | 主题颜色，枚举：type1（黑白主题）、type3（彩色玻璃主题） |
| width | number | 否 | 6 | 图像宽度（英寸），范围：1 ~ 20 |
| height | number | 否 | 5 | 图像高度（英寸），范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| font_face | string | 否 | bold | 字体样式， 枚举：bold、plain、italic |
| font_family | string | 否 | arial | 字体，枚举：arial、time new roman、serif |
| font_size | number | 否 | 12 | 字体大小，范围：8 ~ 20 |
| border | bool | 否 | True | 图形边框，枚举：true （是）、false （否） |
| line_width | number | 否 | 0.8 | 坐标轴线宽度，范围：0.5 ~ 1 |
| angle | string | 否 |  | 坐标轴标签角度，枚举：0、45、90 |
| legend_position | string | 否 | right | 图例位置，枚举：none、right、left、top、bottom |
| xtitle | string | 否 | log2FC | x 轴标题 |
| ytitle | string | 否 | -log10(pvalue) | y 轴标题 |
| title | string | 否 | plot of volcano | 图表标题 |
