# 双向柱状图 (bilateral_bar)

> 双向柱状图是一种特殊的柱状图，常用来比较方向相反的两组数据

## 文件要求

上传文件：样本文件，必须包含以下两列——
value：数值数据，正负号决定柱形的显示方向；
pathway：每条数据对应的标签名称。
文件可增加其他列，绘图时从上传文件列名中分别选择数据列和标签列。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| x_col | string | 是 | value | 数据列，取值来源于上传文件第一行的列名，必须为数值列，默认选择value列 |
| y_col | string | 是 | pathway | 标签列，取值来源于上传文件第一行的列名，默认选择pathway列 |
| data_color | string | 是 | type1 | 颜色，枚举：type1（#2f73bb、#ae4531）、type2（#F3E5F5、#FF80AB）、type3（#FFF3E0、#FFCC80）；两个颜色值依次对应正值（>0）和负值（<0）的柱形颜色 |
| right_label_text | string | 是 | Up | 标签(>0) |
| left_label_text | string | 是 | Down | 标签(<0) |
| width | number | 否 | 8 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 6 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| ytitle | string | 否 | Normalized Enrichment Score | X轴标题 |
| axis_text_size | number | 否 | 12 | X轴标题大小，范围：1 ~ 20 |
| label_size | number | 否 | 4 | Y轴标题大小，范围：1 ~ 10 |
| title | string | 否 |  | 标题 |
| title_size | number | 否 | 14 | 标题大小，范围：1 ~ 20 |
