# 四象限图 (four_quadrant)

> 四象限图是一种用于分析和比较两个变量关系的图表类型。它通过将平面坐标系划分为四个象限，将数据点按变量取值分布到不同区域，从而直观展示变量间的协同、对立及分布特征。

## 文件要求

上传文件：样本文件：每行代表一条观测记录，必须包含以下三列——
diff.log2.fc：X轴数据，填写连续数值；
log2(fc)：Y轴数据，填写连续数值；
geneId：标签数据，填写每条观测记录对应的基因或对象标识。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| xcol | string | 是 | diff.log2.fc | X轴列，从上传的样本文件中选择连续数值列，用于设置散点的横坐标；默认选择diff.log2.fc列 |
| ycol | string | 是 | log2(fc) | Y轴列，从上传的样本文件中选择连续数值列，用于设置散点的纵坐标；默认选择log2(fc)列 |
| label_col | string | 是 | geneId | 标签列，从上传的样本文件中选择标签数据列，用于标识图中的数据点；默认选择geneId列 |
| font_size | number | 否 | 12 | 字体大小，范围：8 ~ 20 |
| edge_lty | string | 否 | dashed | 线条类型，枚举：solid（实线）、dashed（虚线）、dotted（点线）、dotdash（点划线）、longdash（长划线）、twodash（双点划线） |
| angle | number | 否 |  | 旋转角度，范围：0 ~ 360 |
| color_palette | string | 否 | Set1 | 调色板，枚举：Set1（#E41A1C、#377EB8、#4DAF4A、#984EA3、#FF7F00、#FFFF33、#A65628、#F781BF、#999999）；Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）；Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）；Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC） |
| border | bool | 否 | True | 展示边界，枚举：true（是）、false（否） |
| width | number | 否 | 6 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 5 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| xtitle | string | 否 | diff.log2.fc | x轴标题，最多输入50个字符 |
| ytitle | string | 否 | log2(fc) | y轴标题，最多输入50个字符 |
| title | string | 否 | Four Quadrant Plot | 图片标题，最多输入50个字符 |
