# 点线图 (dotline_columns)

> 点线图是一种结合数据点与连线的图表类型。它通过在坐标轴上标注各个数据点，并用直线将其依序连接，既能显示单个数据值，又能清晰反映数据随时间或类别的变化趋势。

## 文件要求

上传文件：样本文件：每列对应一组数据，第一行为数据列名称，其余各行填写连续数值。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| color_palette | string | 否 | Set1 | 调色板，枚举：Set1（#E41A1C、#377EB8、#4DAF4A、#984EA3、#FF7F00、#FFFF33、#A65628、#F781BF、#999999）；Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）；Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）；Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC）；各色值按上传文件中的数据列顺序依次对应 |
| width | number | 否 | 6 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 5 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| x_title | string | 否 | variable | x轴标题，最多输入50个字符 |
| y_title | string | 否 | value | y轴标题，最多输入50个字符 |
| title | string | 否 | Dot-Line Plot by Columns | 图片标题，最多输入50个字符 |
| title_size | number | 否 | 10 | 图片标题大小，最小值：1 |
