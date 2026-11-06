# PCA (pca)

> PCA图通过降维呈现样本间的相似性和分组结构

## 文件要求

上传文件：
1.样本丰度表：首列为基因名称，其余每列对应一个样本，列名为样本ID。


2.样本分组表：必须包含以下三列——


Sample：样本ID，须与丰度表中的样本列名完全一致；


Group：生物学分组（如处理组/对照组）；


Condition：实验条件标签（如Case/Control）。

最小特征数：≥10 个基因/变量

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| color | object | 否 | "" | 散点颜色，取样本分组文件对应的生物学分组的列值A,B,C...，分组配色方案:

如：{
 "A": "#E64B35CC",
  "B": "#4DBBD5CC",
  "C": "#00A087CC"

}
，也支持传入期刊颜色。 |
| ellipse_ci | bool | 否 | True | 置信椭圆，枚举：true（显示）、false（不显示） |
| labels_show | bool | 否 | True | 显示标签，枚举：true（显示）、false（不显示） |
| type | string | 否 | type1 | 主题颜色，枚举：type1（黑白主题）、type3（彩色玻璃主题） |
| width | number | 否 | 4 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 4.2 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| font_face | string | 否 | bold | 字体样式，枚举：bold、plain、italic |
| font_family | string | 否 | arial | 字体，枚举：arial、time new roman、serif |
| font_size | number | 否 | 12 | 字体大小，范围：8 ~ 20 |
| border | bool | 否 | True | 图形边框，枚举：true（是）、false（否） |
| line_width | number | 否 | 0.8 | 坐标轴线宽度，范围：0.5 ~ 1 |
| angle | string | 否 |  | 坐标轴标签角度，枚举：0、45、90 |
| legend_position | string | 否 | right | 图例位置，枚举：none、right、left、top、bottom |
| title | string | 否 | plot of pca | 标题 |
