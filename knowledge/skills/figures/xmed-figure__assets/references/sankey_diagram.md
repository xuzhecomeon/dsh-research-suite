# 桑基图 (sankey_diagram)

> 桑基图描述数据的流动、转换、变化过程

## 文件要求

上传文件：样本数据表，必须包含Type列及至少一个分组列（如Group1）。Type表示桑基图第一层的分析对象或类别，Group1表示与Type关联的下一层分组；如需展示更多层级，可依次增加Group2、Group3等分组列。每行表示一条从Type依次流向各分组层级的完整路径。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| color_panel | string | 否 | turbo | 调色板，枚举：viridis、magma、inferno、plasma、cividis、rocket、mako、turbo |
| theme_base | string | 否 | theme_bw | 主题，枚举：theme_light、theme_minimal、theme_classic、theme_bw |
| width | number | 否 | 9 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 4 | 图像高度(in)，范围：1 ~ 20 |
