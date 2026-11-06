# 分组直方图 (grouped_histogram)

> 分组直方图是一种用于展示多个组数据分布的图表类型。它通过将每个组的数据分布以直方图的形式并排放置，便于比较不同组之间的数据分布差异。

## 文件要求

上传文件：样本文件：必须包含以下两列——
Control：第一组数据，填写连续数值；
Case：第二组数据，填写连续数值。
可以继续增加其他连续数值列。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| first_group | string | 是 | Control | 第一组数据，从上传的样本文件中选择第一组的连续数值列；默认选择Control列 |
| first_group_name | string | 是 | Control | 第一组名称，设置第一组数据在图例中显示的名称 |
| second_group | string | 是 | Case | 第二组数据，从上传的样本文件中选择第二组的连续数值列；默认选择Case列 |
| second_group_name | string | 是 | Case | 第二组名称，设置第二组数据在图例中显示的名称 |
| color | string | 否 | type1 | 填充颜色，枚举：type1（#cc7833、#75aadb）、type2（#caddd3、#fea3a3）、type3（#e0e0e0、#ffeecc）；每组色值按顺序分别对应第一组和第二组 |
| width | number | 否 | 8 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 6 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| xtitle | string | 否 | Expression | x轴标题，最多输入50个字符 |
| ytitle | string | 否 | Count | y轴标题，最多输入50个字符 |
| title | string | 否 | Expression Histogram | 标题，最多输入50个字符 |
