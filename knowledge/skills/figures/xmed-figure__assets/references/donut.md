# 圆环图 (donut)

> 圆环图（也称为甜甜圈图）是一种常见的数据可视化工具，它是饼图的一种变体，主要用于展示数据的占比关系

## 文件要求

上传文件：样本文件，必须包含以下五列——
Type：数据类别；
low：区间下限值，须为数值；
high：区间上限值，须为数值；
group：分组名称；
number：图中显示的标签内容。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| data_col | string | 是 | group | 数据列，取值来源于上传文件第一行的列名；用于划分数据类别，并根据各类别出现的次数计算占比；默认选择group列 |
| color_palette | string | 是 | Set3 | 颜色面板，枚举：Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Spectral（#9E0142、#D53E4F、#F46D43、#FDAE61、#FEE08B、#FFFFBF、#E6F598、#ABDDA4、#66C2A5、#3288BD、#5E4FA2）；BrBG（#543005、#8C510A、#BF812D、#DFC27D、#F6E8C3、#F5F5F5、#C7EAE5、#80CDC1、#35978F、#01665E、#003C30）；PiYG（#8E0152、#C51B7D、#DE77AE、#F1B6DA、#FDE0EF、#F7F7F7、#E6F5D0、#B8E186、#7FBC41、#4D9221、#276419）；PuOr（#7F3B08、#B35806、#E08214、#FDB863、#FEE0B6、#F7F7F7、#D8DAEB、#B2ABD2、#8073AC、#542788、#2D004B） |
| width | number | 否 | 8 | 图像宽度(in)，范围：1～20 |
| height | number | 否 | 6 | 图像高度(in)，范围：1～20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| font_size | number | 否 | 8 | 字体大小，范围：8～20 |
| label_name | string | 否 |  | 图形注释 |
| label_size | number | 否 | 6 | 注释大小，范围：1～10 |
