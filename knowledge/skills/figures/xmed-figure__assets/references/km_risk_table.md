# KM生存分析图 (km_risk_table)

> KM 生存分析图是一种用于展示不同组别随时间推移的生存概率变化的图表类型。它通过阶梯状曲线表示各时间点的生存率，并可结合风险表、置信区间等信息，直观比较不同组之间的生存差异。

## 文件要求

上传文件：样本文件：每行代表一条观测记录，必须包含以下三类数据列——
time：时间变量，填写随访时间或生存时间；
status：结局变量，填写结局或事件状态的分类编码；
自变量列：填写用于划分生存曲线组别的分类数据，至少包含1列。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| time_variable | string | 是 | time | 时间变量，从上传的样本文件中选择随访时间或生存时间列；默认选择time列 |
| status_variable | string | 是 | status | 结局变量，从上传的样本文件中选择结局或事件状态列；默认选择status列 |
| group_variable | string | 是 |  | 自变量，从上传的样本文件中选择用于划分生存曲线组别的分类变量列 |
| color_palette | string | 否 | Set1 | 调色板，枚举：Set1（#E41A1C、#377EB8、#4DAF4A、#984EA3、#FF7F00、#FFFF33、#A65628、#F781BF、#999999）；Set2（#66C2A5、#FC8D62、#8DA0CB、#E78AC3、#A6D854、#FFD92F、#E5C494、#B3B3B3）；Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）；Pastel1（#FBB4AE、#B3CDE3、#CCEBC5、#DECBE4、#FED9A6、#FFFFCC、#E5D8BD、#FDDAEC、#F2F2F2）；Pastel2（#B3E2CD、#FDCDAC、#CBD5E8、#F4CAE4、#E6F5C9、#FFF2AE、#F1E2CC、#CCCCCC）；各色值按自变量的分类顺序依次对应 |
| risk_table_judgement | number | 否 | 1 | 展示风险表，枚举：1（是）、0（否） |
| conf_int_judgement | number | 否 | 1 | 展示置信区间，枚举：1（是）、0（否） |
| width | number | 否 | 6 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 6 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| title_prex | string | 否 | KM Curve by | 标题前缀，最多输入50个字符 |
