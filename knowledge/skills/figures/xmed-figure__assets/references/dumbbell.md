# 哑铃图 (dumbbell)

> 哑铃图是一种数据可视化图表，主要用于比较同一组数据在两个不同时间点、条件或类别下的变化情况。其核心在于通过线段连接两个数据点，形成类似“哑铃”的形状，直观展示差异或变化趋势

## 文件要求

上传文件：样本数据，必须包含ID、Group1、Group2列，其中ID为比较对象标识，Group1和Group2为两组数值数据；可继续增加Group3、Group4等数值列。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| ID | string | 是 | ID | ID列，取值来源于上传文件第一行的列名，默认选择ID列 |
| Group1 | string | 是 | Group1 | 第一组数据，取值来源于上传文件第一行的列名，默认选择Group1列 |
| Group2 | string | 是 | Group2 | 第二组数据，取值来源于上传文件第一行的列名，默认选择Group2列 |
| color_x | string | 否 | #b1cb41 | 第一组数据颜色 |
| color_xend | string | 否 | #45a0e2 | 第二组数据颜色 |
| point_size | number | 否 | 2 | 点大小，范围：1 ~ 10 |
| line_size | number | 否 | 0.5 | 线宽，范围：0 ~ 1 |
| line_color | string | 否 | #808080 | 线颜色 |
| dot_guide | number | 否 |  | 是否显示引导线，枚举：1（是）、0（否） |
| width | number | 否 | 6 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 4.2 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| title | string | 否 | dumbbell plot | 标题 |
| xtitle | string | 否 | x axis | X轴 |
| ytitle | string | 否 | y axis | Y轴 |
