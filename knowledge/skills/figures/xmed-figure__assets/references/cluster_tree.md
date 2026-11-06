# 分层聚类图 (cluster_tree)

> 分层聚类图是一种用于展示数据层次聚类结果的可视化工具

## 文件要求

上传文件：
1.样本文件：首列必须为ID，表示样本ID；其余每列对应一个聚类特征，列名为特征名称，数据须为数值型。 
2.分组文件：必须包含以下两列——
Sample：样本ID，须与样本文件ID列中的样本ID完全一致；
Group：样本所属分组（如A/B/C或处理组/对照组）。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| method | string | 否 | average | 聚类算法，枚举：ward.D、ward.D2、single、complete、average、mcquitty、median、centroid |
| color_panel | string | 否 | Set1 | 颜色面板，枚举：Set1（#E41A1C、#377EB8、#4DAF4A、#984EA3、#FF7F00、#FFFF33、#A65628、#F781BF、#999999）、Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）、Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）、Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）、Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC） |
| theme_base | string | 否 | theme_bw | 颜色主题，枚举：theme_light、theme_minimal、theme_classic、theme_bw |
| width | number | 否 | 6 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 4.2 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| title | string | 否 | cluster tree plot | 标题 |
| xtitle | string | 否 | x axis | X轴 |
| ytitle | string | 否 | y axis | Y轴 |
| angle | number | 否 | 90 | 坐标轴标签角度，枚举：0、45、90 |
| legend_position | string | 否 | right | 图例位置，枚举：none、left、right、bottom、top、inside |
