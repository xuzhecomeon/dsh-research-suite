# 相关性网络图 (correlation_network)

> 相关性网络图是一种用于展示变量之间相关性关系的图表类型。它通过节点表示变量，边表示变量间的相关性，并用颜色或线型区分正相关与负相关，从而直观揭示数据中潜在的关联结构与网络特征。

## 文件要求

上传文件：样本文件：每行代表一组变量间的相关关系，必须包含以下五列——
Data1：相关关系中的第一个变量名称；
Data2：相关关系中的第二个变量名称；
rho：相关系数，填写数值；
pvalue：相关性检验的显著性P值，填写数值；
relation：相关方向，填写positive或negative。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| base_node_size | number | 否 | 2 | base大小，设置网络节点的基础大小，范围：1 ~ 20 |
| degree_scale_factor | number | 否 | 0.5 | scale因子，设置节点大小随连接度变化的缩放系数，范围：0.1 ~ 10 |
| set_size | number | 否 | 3 | 标签大小，范围：1 ~ 10 |
| edge_color_palette | string | 否 | Set1 | 边缘调色板，枚举：Set1（#E41A1C、#377EB8、#4DAF4A、#984EA3、#FF7F00、#FFFF33、#A65628、#F781BF、#999999）；Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）；Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）；Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC） |
| node_color_palette | string | 否 | YlGnBu | 节点调色板，枚举：Reds、Blues、Greens、YlOrRd、YlGnBu |
| width | number | 否 | 8 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 8 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| title | string | 否 | Correlation Network | 图片标题，最多输入50个字符 |
