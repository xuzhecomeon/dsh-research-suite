# 线性回归 (linear_regression)

> 线性回归图是一种用于展示两个变量间线性关系的图表类型。 它通过在散点图上绘制回归直线，直观反映变量之间的趋势方向和强度，并可用于预测一个变量在另一变量变化下的取值。

## 文件要求

上传文件：样本文件：每行代表一条观测记录，必须包含以下三列——
x：自变量，填写连续数值；
y：因变量，填写连续数值；
group：分组变量，填写每条观测记录所属的分类分组。可以继续增加其他数据列。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| xcol | string | 是 | x | X轴列，从上传的样本文件中选择连续数值列，作为线性回归的自变量；默认选择x列 |
| ycol | string | 是 | y | Y轴列，从上传的样本文件中选择连续数值列，作为线性回归的因变量；默认选择y列 |
| group | string | 是 | group | 分组列，从上传的样本文件中选择分类变量列，用于按分组绘制数据点及回归关系；默认选择group列 |
| point_size | number | 否 | 3 | 点的大小，范围：1 ~ 10 |
| color_palette | string | 否 | Set1 | 调色板，枚举：Set1（#E41A1C、#377EB8、#4DAF4A、#984EA3、#FF7F00、#FFFF33、#A65628、#F781BF、#999999）；Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）；Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）；Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC）；各色值按group列中的分组出现顺序依次对应 |
| width | number | 否 | 6 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 5 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| x_title | string | 否 | x | x轴标题，最多输入50个字符 |
| y_title | string | 否 | y | y轴标题，最多输入50个字符 |
| title | string | 否 | Linear Regression Plot | 图片标题，最多输入50个字符 |
