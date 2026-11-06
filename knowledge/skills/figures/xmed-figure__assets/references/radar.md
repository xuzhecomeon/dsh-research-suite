# 雷达图 (radar)

> 雷达图是一种用于比较多变量数据的可视化图表类型。它通过将多个变量沿不同角度的轴辐射排列，并用线或面连接各变量的数值点，从而直观展示多个样本在不同指标上的差异与整体特征。

## 文件要求

上传文件：样本文件：首列为指标名称，其余每列对应一个样本，列名为样本名称；每行代表一个指标，各样本列填写对应指标的数值。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| color_palette | string | 否 | Pastel1 | 调色板，枚举：Set1（#E41A1C、#377EB8、#4DAF4A、#984EA3、#FF7F00、#FFFF33、#A65628、#F781BF、#999999）；Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）；Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）；Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC）；各色值按上传文件中的样本列顺序依次对应 |
| width | number | 否 | 6 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 6 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| plwd | number | 否 | 2 | 线条粗细，范围：1 ~ 5 |
| plty | number | 否 | 1 | 样本线条类型，枚举：1（实线）、2（虚线）、3（点线）、4（点划线）、5（长划线）、6（双点划线） |
| cglcol | string | 否 | grey | 背景线条颜色，枚举：grey、black、blue、red、yellow |
| cglty | number | 否 | 1 | 背景线条类型，枚举：1（实线）、2（虚线）、3（点线）、4（点划线）、5（长划线）、6（双点划线） |
| vlcex | number | 否 | 1 | 字体大小，界面允许范围：1 ~ 3，步长：0.1 |
| title | string | 否 |  | 标题，最多输入50个字符 |
