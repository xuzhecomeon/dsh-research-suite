# 富集气泡图 (enrich_bubble)

> 富集气泡图通过气泡的大小、颜色和位置展示功能富集分析结果

## 文件要求

上传文件：富集信息表，必须包含Description、GeneRatio、Count、pvalue列，其中Description为富集条目或通路名称，GeneRatio为输入基因集中注释到该条目或通路的基因数占输入基因总数的比例，Count为注释到该条目或通路的基因数量，pvalue为该条目富集显著性检验的未经校正P值。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| top_number | number | 否 | 20 | Top值，范围：5 ~ 30 |
| width | number | 否 | 6 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 5.2 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| font_face | string | 否 | bold | 字体样式，枚举：bold、plain、italic |
| font_family | string | 否 | arial | 字体，枚举：arial、time new roman、serif |
| font_size | number | 否 | 12 | 字体大小，范围：8 ~ 20 |
| border | bool | 否 | True | 图形边框，枚举：true（是）、false（否） |
| legend_position | string | 否 | right | 图例位置，枚举：none、right、left、top、bottom |
| xtitle | string | 否 | count | x轴标题 |
| ytitle | string | 否 | Description | y轴标题 |
| title | string | 否 | enrich_bubble | 标题 |
| angle | string | 否 |  | 坐标轴标签角度，枚举：0、45、90 |
