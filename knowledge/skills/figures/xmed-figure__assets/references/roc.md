# ROC 曲线图 (roc)

> ROC 曲线图是一种用于评估二分类模型预测性能的图表类型。它通过绘制不同阈值下的灵敏度与 1-特异性关系曲线，反映模型在各种判别标准下的分类能力，曲线下面积（AUC）可量化整体表现。

## 文件要求

上传文件： 
1.样本丰度表：必须包含Sample列和至少1个数值特征列；Sample：样本ID；其余每列对应一个特征，列名为特征名称，填写各样本对应的特征数值。 
2.样本分组表：必须包含以下两列——
Sample：样本ID，须与样本丰度表中的Sample列完全一致；
Group：样本所属分组，必须至少包含2个不同的分组值。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| gene_columns | string | 是 |  | 特征名称，从上传的样本丰度表中选择用于绘制ROC曲线的数值特征列，至少选择1列 |
| group_labels | string | 是 |  | 比较组，取值来源于上传的样本分组表中Group列的分组值，必须选择2个分组 |
| color_palette | string | 否 | Set1 | 调色板，枚举：Set1（#E41A1C、#377EB8、#4DAF4A、#984EA3、#FF7F00、#FFFF33、#A65628、#F781BF、#999999）；Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）；Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）；Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC）；各色值按所选特征列的顺序依次对应ROC曲线 |
| width | number | 否 | 6.5 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 4 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| title | string | 否 | ROC Curves for Multiple Genes | 标题，最多输入50个字符 |
