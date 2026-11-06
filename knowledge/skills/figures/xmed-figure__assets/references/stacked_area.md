# 堆叠面积图 (stacked_area)

> 区域叠加图可以直观地显示不同物种或元素在特定区域内的分布和相对数量

## 文件要求

上传文件：
1.样本文件：首列为物种或分类名称，其余每列对应一个样本，列名为样本ID，数据为数值型相对丰度。 
2.分组文件：必须包含以下两列——
sample：样本ID，须与样本文件中的样本列名完全一致；
times：样本对应的时间点或排列顺序，用于确定横轴顺序。

## 常规参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| color_palette | string | 否 | Set3 | 颜色面板，枚举：Set3（#8DD3C7、#FFFFB3、#BEBADA、#FB8072、#80B1D3、#FDB462、#B3DE69、#FCCDE5、#D9D9D9、#BC80BD、#CCEBC5、#FFED6F）、Spectral（#9E0142、#D53E4F、#F46D43、#FDAE61、#FEE08B、#FFFFBF、#E6F598、#ABDDA4、#66C2A5、#3288BD、#5E4FA2）、BrBG（#543005、#8C510A、#BF812D、#DFC27D、#F6E8C3、#F5F5F5、#C7EAE5、#80CDC1、#35978F、#01665E、#003C30）、PiYG（#8E0152、#C51B7D、#DE77AE、#F1B6DA、#FDE0EF、#F7F7F7、#E6F5D0、#B8E186、#7FBC41、#4D9221、#276419）、PuOr（#7F3B08、#B35806、#E08214、#FDB863、#FEE0B6、#F7F7F7、#D8DAEB、#B2ABD2、#8073AC、#542788、#2D004B） |
| width | number | 否 | 8 | 图像宽度(in)，范围：1 ~ 20 |
| height | number | 否 | 6 | 图像高度(in)，范围：1 ~ 20 |

## 高级参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| xtitle | string | 否 | Times | x轴标题 |
| ytitle | string | 否 | Relative Abundance(%) | y轴标题 |
| title | string | 否 |  | 标题 |
