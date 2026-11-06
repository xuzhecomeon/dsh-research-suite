# 相关性热图 (cor_pheatmap)

> 相关性热图通过颜色梯度展示变量之间相关性

## 文件要求

上传文件：
1.样本丰度表：首列为基因名称，其余每列对应一个样本，列名为样本ID。


2.样本分组表：必须包含以下三列——


Sample：样本ID，须与丰度表中的样本列名完全一致；


Group：生物学分组（如处理组/对照组）；


Condition：实验条件标签（如Case/Control）。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| cut_off | number | 否 | 0.8 | 数值缺失率阈值，范围：0 ~ 1，步长：0.1 |
| cor_method | string | 否 | pearson | 相关性算法，枚举：pearson、kendall、spearman |
| color_panel | string | 否 | vik | 调色板，枚举：vik、vikO、broc、brocO、bam、bamO |
| color | object | 否 |  | 分组和条件标签颜色，根据样本分组文件中的Group列的值和Condition的值去配置每种类型的颜色；如："color":{"Condition":{"Control":"#E64B35CC","Case":"#4DBBD5CC"},"Group":{"A":"#E64B35CC","B":"#4DBBD5CC","C":"#00A087CC"}} |
| show_colnames | number | 否 |  | 展示列名，枚举：1（是）、0（否） |
| show_rownames | number | 否 |  | 展示行名，枚举：1（是）、0（否） |
| width | number | 否 | 5 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 4.2 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| font_size | number | 否 | 8 | 字体大小，范围：3 ~ 20 |
| title | string | 否 | plot of correlation pheatmap | 标题，最多输入50个字符 |
