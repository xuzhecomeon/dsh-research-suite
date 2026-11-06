# 分组蜂群图 (beeswarm)

> 分组蜂群图是一种用于可视化分类数据分布的图表类型。它通过在分类轴上分散数据点，避免数据点之间的重叠，从而更清晰地展示数据的分布密度和趋势

## 文件要求

上传文件：样本文件：每行代表一条观测记录，必须包含以下三列——
group：主分组，填写每条观测记录所属的主要分类；
group2：颜色分组，填写每条观测记录所属的颜色分类；
y：数据列，填写用于绘制散点的连续数值。可以继续增加其他数据列。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| first_group | string | 是 | group | 主分组，从上传的样本文件中选择分类变量列，用于设置数据的主要分组；默认选择group列 |
| second_group | string | 是 | group2 | 颜色分组，从上传的样本文件中选择分类变量列，用于设置散点的颜色分组；默认选择group2列 |
| color_palette | string | 否 | Set1 | 颜色面板，枚举：Set1（#E41A1C、#377EB8、#4DAF4A、#984EA3、#FF7F00、#FFFF33、#A65628、#F781BF、#999999）；Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）；Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）；Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC） |
| data_col | string | 是 | y | 数据列，从上传的样本文件中选择连续数值列，用于设置散点对应的数值；默认选择y列 |
| point_size | number | 否 | 3 | 点大小，范围：1 ~ 10 |
| width | number | 否 | 8 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 6 | 图像高度(in)，范围：1 ~ 20 |
