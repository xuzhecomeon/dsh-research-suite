# 韦恩图 (venn)

> 韦恩图（Venn Diagram）是一种用图形直观表示集合（或群体）之间逻辑关系的工具

## 文件要求

上传文件：样本数据，至少包含两列，第一行为集合名称，每列填写对应集合的元素。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| n_cols | string | 是 | 1,2 | 列序号，根据上传文件第一行的列名生成可选项，取值为从1开始的列位置序号；至少选择2列，默认选择前2列 |
| color_panel | string | 否 | turbo | 标签调色板，枚举：viridis、magma、inferno、plasma、cividis、rocket、mako、turbo |
| set_size | number | 否 | 5 | 标签大小，范围：1 ~ 10 |
| label_alpha | number | 否 | 0.5 | 标签透明度，范围：0 ~ 1 |
| label | string | 否 | count | 区域标签格式，枚举：both、count、percent、none |
| width | number | 否 | 6 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 4.2 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| label_color | string | 否 | black | 区域标签颜色，枚举：black、blue |
| fill_color | string | 否 | type1 | 区域颜色面板，枚举：type1（#CFFFFF, #C79DC9）、type2（#F3E5F5, #FF80AB）、type3（#FFF3E0, #FFCC80）；两个颜色值分别为区域填充色的渐变起始色和结束色。 |
| font_size | number | 否 | 8 | 区域标签大小，范围：8 ~ 20 |
| edge_lty | string | 否 | dashed | 线条类型，枚举：solid、dashed |
| expand_mult | number | 否 | 0.1 | 空白区比率，范围：0 ~ 1 |
