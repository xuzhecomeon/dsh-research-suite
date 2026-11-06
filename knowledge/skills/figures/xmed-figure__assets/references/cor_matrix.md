# 相关性矩阵图 (cor_matrix)

> 相关性矩阵图是一种用于展示多个变量之间两两相关性的可视化工具，通常以矩阵的形式呈现，矩阵中的每个元素表示两个变量之间的相关系数

## 文件要求

上传文件：样本文件：每行代表一条观测记录，至少包含以下三列——
Species：分类变量，用于“分组列”参数；
A1、A2：连续数值变量，用于“数据列”参数。
可以继续增加A3、A4等连续数值列。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| group_col | string | 是 | Species | 分组列，从上传的样本文件中选择分类变量列，用于区分数据所属的分组；默认选择Species列 |
| data_col | string | 是 |  | 数据列，从上传的样本文件中选择需要进行相关性分析的连续数值列，至少选择2列； |
| color_palette | string | 否 | Set2 | 颜色面板，枚举：Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）；Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）；Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC） |
| width | number | 否 | 8 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 6 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| point_size | number | 否 | 1 | 散点大小，范围：1 ~ 5 |
| cor_size | number | 否 | 3 | 文本大小，控制矩阵中相关系数文本的大小，范围：1 ~ 10 |
| axis_text_size | number | 否 | 8 | 标签大小，控制变量标签的文字大小，范围：1 ~ 10 |
