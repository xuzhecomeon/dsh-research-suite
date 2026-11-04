---
name: research-figures
description: 科研绘图与图件域：用真实数据渲染出版级单图与统计图族，拼多面板、画四要素机制图与流程示意，交付可编辑矢量、终检报告与复跑包。
whenToUse: 用户要画论文配图、期刊图件、机制图、流程图、示意图、多面板组图，或要核验 DPI、字号、字体、配色、图注、数据来源是否达标时使用。
---

# 科研绘图与图件（Research Figures）

本域负责整条图件链路：从「这张图要证明什么」开始，到成图、源文件、数据清单与终检报告落盘为止。图件是论文里唯一会被制作端（production）单独审一遍的物件，因此本域的默认交付不是一张图，而是一组可复核的文件。

## 一、本域边界

1. **本域只做图件本体与图件级校验。** 不选统计方法、不重跑统计模型、不解释结果（属 stats 域），不检索文献、不写正文（属 literature / writing 域），不改研究结论。若数据本身不足以支撑图型，退回补数据，不靠绘图技巧遮盖。
2. **数据图与示意图是两种东西，处理路径完全不同。** 数据图必须由真实数据经 Python 或 R 渲染（绘图不是统计，本域可以写绘图脚本）；示意图、机制图、流程图的正确路径是矢量组件拼装。**禁止用文生图或插画类技能顶替数据图**，也禁止用它们顶替机制图——生成模型给不出可控的分子名、箭头方向与器官解剖。
3. **涉患者数据的图全程本地处理。** 需上传外部服务的技能（在线绘图 API、云端生图、带 API key 的示意图服务）在本域一律不用于患者数据与未发表数据：一次外流不可回收，且脱离伦理审批与可复现边界。
4. **本域交付物必须是文件。** 成图（`.png`/`.tif`/`.eps`/`.svg`/`.pdf`）、可编辑源文件（`.py`/`.R`/`.drawio`/JSON spec）与数据来源说明三件齐备；只给一段代码或一句「已画好」不算交付。
5. **本域不承诺技能一定可用。** 若某技能的脚本、字体或外部依赖在本机缺失，按本文给的阈值与手工步骤执行，并在交付说明里写明哪些检查是手工做的、哪些未做（不得静默声称通过）。
6. **机制图 ≠ 流程图。** 这是本域最容易被画错的一条，判据见第四节与第五节的自检表：机制图必须同时承载分子机制、受累器官、实验动物与操作、胞内胞外信号分层四类信息，缺一类即不合格。

## 二、融合对比表

| 能力 | 主用技能 | 关键长处 | 明确短板 | 融合取舍 |
|---|---|---|---|---|
| 出版级数据图渲染 | `matplotlib` | 对象式 API 逐元素可控；rcParams 模板化；矢量与位图一次双出 | 默认配色与 10 pt 字号不能投稿；不做统计检验 | 以 matplotlib 为执行底座，借 `nature-figure` 的 figure contract 与 backend 互斥纪律，借 `figures-python` 的栏宽英寸与 manifest 规则 |
| 统计图族绘制 | `academic-figures` | 40 种图型；KM 自动风险表；PRISMA 数字自洽校验；像素重叠门禁 | 不做纯示意图；无三维与交互 | 主用其生成器与门禁，`science-figures` 补期刊风格，`seaborn` 兜底拼图；在线 API 弃用 |
| 多面板组合排版 | `scientific-visualization` | GridSpec 规范；面板字母锚点；13 项终检清单 | 只给规范与片段，不代管文件 | 借 `nature-figure` 的 1.5 pt 对齐门与碰撞审计做硬门，`matplotlib` 负责复杂版式 |
| 机制图（四要素） | `medical-illustration` | 代码生成原创矢量 SVG；亚细胞/细胞/器官组件；箭头三语义 | 透明度导出不可靠；无生物学正确性校验 | 用 `scientific-thinking-biology` 校核机制链条与层级，`figure-designer` 出布局草图；AI 临摹与外部生图弃用 |
| 流程与方法示意 | `academic-figures` | PRISMA 带数字自洽；diagram/composite 图型；期刊预设 | 不做无数据的装饰示意；节点样式自由度有限 | 先 `markdown-mermaid-writing` 用文本定拓扑，`fireworks-tech-graph` 校验连线，`scientific-drawing` 兜底骨架 |
| 可编辑矢量示意 | `drawio-reconstruction` | 逐元素清单；原生元素与裁切图分工；audit 记录 | 还原度优先于可编辑性；复杂插画仍靠位图 | 文字结构强制原生元素，`fireworks-tech-graph` 提供语义化 SVG，`medical-illustration` 提供生物元件 |
| 医学影像与照片 | `pydicom` | 读写 DICOM、按标签去标识化、保留层厚 | 仅容器能力，不做图像分析 | `airs-segment-anything-model` 做掩膜裁剪，`histolab` 做切片与染色归一；生成式修图弃用 |
| 配色与期刊风格 | `figures-python` | 成组配色常量；五色上限；450 dpi 双出 | 字体路径绑 mac；主题扩展有限 | 以 Okabe-Ito 为默认盘，`scientific-visualization` 补灰度与色盲判据，`science-figures` 补期刊预设 |
| 图表规范化终检 | `nature-figure` | PDF 文字与几何碰撞审计；exit 1 阻断交付；导出契约 | 偏 Nature 系刊规格；依赖其脚本 | `scientific-visualization` 出 13 项读数表，`scholar-verify` 做图—注—数据三方对账，`academic-figures` 提供复跑包思路 |

## 三、融合协议

以下九个小节各对应一张能力卡。步骤里的阈值是硬门槛，不是建议值；达不到就回退重做，不靠说明文字打圆场。

### 3.1 出版级数据图渲染（figures.render）

1. **定结论与版式契约。** 先用一句话写出这张图要证明的结论，再列两三个支撑证据点。结论没写清就不进入写代码——这是 `nature-figure` 的 figure contract 纪律。
2. **锁 backend 与字体回退。** Python 用 matplotlib、R 用 ggplot2，全流程只用一个 backend，禁止一半 matplotlib 一半 Origin 拼。中文字体按 Noto Sans CJK → Microsoft YaHei → SimHei 依次回退，英文用 Arial/Helvetica，导出前跑一次缺字检查。
3. **按最终尺寸建画布。** `figsize` 直接设成排版尺寸：单栏 3.5 in（89 mm）、双栏 7.0 in（183 mm），不靠后期缩放。缩放是字号失控的根源：一张 7 in 的图缩到 3.5 in，8 pt 立刻变 4 pt。
4. **出图并双格式落盘。** 同一脚本导出 PNG（位图 ≥300 dpi，线条图建议 600 dpi）与 SVG/PDF。给投稿系统的位图与给编辑的矢量必须来自同一次运行 stdout，否则两版数字会不一致。
5. **按 100% 打印尺寸核对字号。** 最小刻度 ≥6～7 pt、轴标签 8～9 pt、panel 字母 8～12 pt 加粗；线宽 0.5～1.0 pt，坐标轴 0.8 pt。低于 7 pt 就整体上调字号或减内容。
6. **记录数据来源。** 交付 `data-manifest.md`，六列必须填满：Figure、Data file、Real/mock、Source、Script、Outputs。模拟数据文件名以 `mock_` / `synthetic_` 开头，并标「待真实实验替换」；不得把模拟数据的图写成「实验结果表明」。

### 3.2 统计图族绘制（figures.statplot）

1. **判定图型族。** 时间到事件 → KM 或累计发生率；效应量与异质性 → 森林图；诊断准确性 → ROC 与校准曲线；多变量预测 → 列线图；组学 → 热图与火山图。一张图只答一类问题，KM 与森林图不同图。
2. **先建数字表，再画图。** 统计输出落成 `group, n, estimate, ci_low, ci_high, p` 六列 CSV；图上所有标注数字从这张表读，不允许手敲。森林图纵轴顺序与表一致，KM 的 at-risk 行数等于该时点仍在随访的人数。
3. **按图型设必需要素。** 森林图 log 横轴 + 无效线（HR 用 x=1，均值差用 x=0）；ROC 画对角参考线并标 AUC 三位小数；火山图给 |log2FC| ≥1 与 P < 0.05 阈值线；热图给聚类树与色标真实数值；KM 给随访轴与 at-risk 表。
4. **过门禁。** 像素级文字重叠检查的真实重叠数必须为 0；字号按最终尺寸 ≥7 pt；同批图统一配色与线宽；显著性星号与 P 值对应关系写进图注，星号层级不超过四级。
5. **写图注。** 首句陈述发现，第二句给统计方法与 n，第三句给误差棒（SD / SEM / 95%CI）与检验名；缩写首现展开；图注编号与正文引用一一对应，不留孤儿图。

### 3.3 多面板组合排版（figures.panel）

1. **定整图结论与 panel 角色。** 整图只回答一个 Results 级问题；每个 panel 承担不同推断角色（现象、因果、对照、定量），不是把不同指标并排。指定一张 hero panel 给最大面积。
2. **先画空版式。** 用 GridSpec 或 `subplot_mosaic` 只画方框，确认行高比、跨列与留白，再填图。子图间距 `wspace` / `hspace` 取 0.08～0.15；共享坐标轴只保留最外侧刻度。
3. **全图一套字号表。** panel 字母 8～12 pt 加粗、轴标签 8～9 pt、刻度 6～7 pt、图例 7～8 pt。任何 panel 缩放后低于 7 pt，重排版式，不缩字。
4. **对齐并标字母。** 比较型 panel 的裁剪矩形容差 ≤1.5 pt；共享边、重复 gutter、字母锚点都要对齐。字母统一放左上外侧，锚点用 `ax.text(-0.15, 1.05, ...)` 固定为相对坐标，跨行跨列时改用 figure 坐标。不等宽 panel 在交付说明里记一条豁免。
5. **审计后导出。** 导出 PDF 后跑碰撞与字号审计；出现 FIX BEFORE DELIVERY 就不交付。审计工具不可用时，显式写「未自动审计」，不得声称通过。

### 3.4 机制图四要素（figures.mechanism）

这是本域的最高门槛，六步必须全走完。

1. **抽四要素清单。** 动笔前先列四张清单：①**分子机制**——至少两个具体分子或通路，写符号不写泛称（TLR4、MyD88、NF-κB、NLRP3、ASC、Caspase-1、GSDMD、RIPK1、RIPK3、MLKL、GPX4、ACSL4、MMP-2/9、ZO-1、Occludin、Claudin-5 这类）；②**受累器官**——脑、肺、肝、肾、心、肠、血管内皮中的实际项；③**实验动物与操作**——SD 或 Wistar 大鼠、雄性、SPF 级、周龄体重，加上造模参数、麻醉方式与剂量、立体定位坐标、给药剂量与途径；④**胞内胞外信号分层**——胞外配体与糖萼 → 膜受体 → 胞质级联 → 核内转录，并画出细胞间连接（紧密连接、黏附连接、桥粒）与基底膜。**缺任一类不出图。**
2. **校核链条方向。** 逐箭头核对：受体激活级联、抑制关系用 T 型、跨膜易位用虚线。方向与文献相反、把相关写成因果、把 marker 当 driver 的箭头全部回退。同一通路在膜、胞质、核三处出现时必须符号与方向一致。
3. **定横版分层版式。** 画布约 2400×1700 px 横版（宽高比约 7:5）；中心是细胞剖面（膜 / 胞质 / 核三层，占宽约六成），上挂器官面板，左挂动物与操作面板，右挂图例与证据分级，下压一行关键定量。器官只画实际受累项，不画无关器官凑数。
4. **用组件库落矢量。** 用组件拼装（膜、细胞器、器官、箭头、图例、面板字母），不手绘路径。避开发布版 svglib 不支持的 `filter` / `style` / `textPath` / `mask`；透明度导出位图会失真，改用浅底 + 实色描边近似；上下标有缺字风险时写 `CD8+`、`I2` 而不是上标字符；跨区连线用直线，弧线曲率 ≤15。
5. **标图例，不标编号。** 图内图例写清：实线 = 已报道、虚线 = 本课题推断、T 型 = 抑制。**机制图内不标 `[n]` 形式参考文献编号**——那是正文配图的做法；出处放图注或表。同一分子不得一处实线一处虚线。
6. **自检与导出。** 缩略图看布局 → 1:1 裁剪查重字与方框 → 抽查箭头语义。四要素每类至少两个具体元素才合格；图内文字必须是可编辑文字而非轮廓路径。导出 SVG + PNG（300 dpi）+ PDF，保留 JSON spec 或 `.py`。

### 3.5 流程与方法示意（figures.flow）

1. **用文本定拓扑。** 先写 Mermaid（或等价文本），节点名 ≤10 字，确认无环无歧义再转正式图。每条分支都要能回答是或否。
2. **先对数字。** PRISMA 四阶段（识别、筛选、合格、纳入）计数必须首尾闭合：识别数 − 重复 − 排除 = 筛选数，筛选数 − 排除 = 全文评估数，逐级到纳入。百分比保留一位小数，数字表与图同目录落 CSV。
3. **按用途定尺寸。** 论文单栏 89 mm / 双栏 183 mm；基金技术路线 A4 横版约 1200 px 宽。节点统一圆角矩形、单向箭头、判定分支用菱形标「是 / 否」；同层节点等宽等高，连线尽量正交。
4. **校验连线与文字。** 一条业务边只留一条连接线（双线会被读成两套关系）；文字出框、压线、穿框三项必须清零。
5. **导出与归档。** 出 SVG + PNG（≥300 dpi），保留 Mermaid 源与数字表，文件名带版本号，下一版只改数字不改版式。

### 3.6 可编辑矢量示意（figures.vector）

1. **建可见元素清单。** 画布、标题、面板、文字块、图标、箭头、留白关系，逐项给 id、位置、内容、拟用介质与状态（pending / done / needs-fix）。清单没建完不开工。
2. **选介质。** 文字、框、连线用原生元素（保证能改）；风格特异或高细节图标用裁切位图；只有简单干净且能还原形状的图标才用 SVG 重绘。用通用图标替换风格特异图标属阻断性缺陷；裁切图出现白边接缝就换透明底或垫同色块。
3. **重建并导出。** 在 `.drawio` 排布后导出 PNG 预览，1:1 与参考图逐项比对，差异写进 `audit.md`；原生元素按语义命名成组，字体统一成可移植字体，画布与参考图等比。
4. **视觉核验后交付。** 在目标阅读尺寸下看文字完整性、对比度、字体替换、留白与箭头方向；看不了图就写「视觉核验跳过」，不得声称视觉正确。

### 3.7 医学影像与照片处理（figures.image）

1. **定边界并去标识化。** DICOM 清空患者姓名、患者 ID、出生日期、检查日期、机构名、设备序列号与注释字段；烧录在像素里的姓名用黑框覆盖并记录位置；导出文件重命名成序号，映射表单独存放且不进交付包。
2. **标定比例尺。** DICOM 用 PixelSpacing 换算，显微图用物镜倍数与相机像素尺寸换算；比例尺画成带数值的线段，长度取整到 10 或 100 微米；同组图比例尺必须同长。
3. **处理与裁剪。** 只做亮度对比度的线性调整与必要裁剪，同图各 panel 用同一查找表；禁非线性锐化制造虚假结构；裁剪留目标结构外沿一成余量；拼版给每个 panel 标字母与比例尺。
4. **导出并回读。** TIFF（无损，位深 8 或 16）或 PNG，位图 ≥300 dpi，sRGB；不做 JPEG 中转；导出后回读 DPI 与像素尺寸核验。
5. **合规核对。** 伦理批件号、去标识化记录、数据可用性声明三项齐全才出图；图注写模态、层厚或放大倍数、n 与处理软件版本。

### 3.8 配色与期刊风格（figures.style）

1. **定主调色板。** 默认 Okabe-Ito 八色（`#E69F00 / #56B4E9 / #009E73 / #F0E442 / #0072B2 / #D55E00 / #CC79A7 / #000000`），按类别数截取；连续量用 viridis / cividis，发散量用 RdBu_r 并让 0 居中；禁 jet 与彩虹色带。
2. **过灰度与色盲。** 成图转灰度看相邻类别亮度差，再跑红绿色盲模拟；两条都过不了就换明度差更大的组合。关键差异不能只靠颜色，必须叠加线型、点型或直接标数值。
3. **定期刊主题文件。** 栏宽、字号表、线宽、刻度朝向、是否保留边框、导出格式与 dpi 写成一份 rcParams 或 theme 文件，全项目 import 同一份，禁止各图各调。
4. **跨图一致性核对。** 同批图缩略图并排看，同指标颜色、字体、线宽、图例位置必须一致；改主题后同批图全部重出。

### 3.9 图表规范化终检（figures.audit）

1. **收齐三件。** 每张图必须有成图、绘图脚本、数据来源；缺脚本或来源的图判为不可交付。用重跑比对哈希或修改时间识别陈旧图。
2. **机械核验指标。** 逐图读 DPI、像素尺寸、格式、字号、字体、线宽，与期刊阈值比对成表。阈值：位图 ≥300 dpi，线条图 ≥600 dpi 或直接矢量，最终尺寸字号 ≥7 pt，英文无衬线，中文无缺字。
3. **图注与数字对账。** 图注含 n、统计方法、误差棒含义；图上数字抽三处回源数据核对。对不上判 CRITICAL；不可追溯标 UNTRACEABLE，可推导但未留痕标 DERIVED-UNVERIFIED。
4. **出分级报告。** 项 / 读数 / 阈值 / 结论四列，按 CRITICAL / MAJOR / MINOR 分级并给前三条修复动作；结论写「通过」「带条件通过」「不通过」之一。
5. **复跑与归档。** 命令、依赖版本、数据副本、成图与报告打包，照 README 能重出同一张图；归档目录带日期与图号。

## 四、判据与红线

以下每条都写成「若……则……否则……」的可执行判定，不依赖品味。

1. **若**这张图有坐标轴与真实数值，**则**必须由数据渲染（Python/R），**否则**用文生图或插画技能「画」出来的数据图一律不交付——生成模型会伪造数据点、伪造误差棒。
2. **若**只有统计数据没有个体值，**则**画森林图或点估计加置信区间，**否则**用箱线图与散点冒充分布即属编造。
3. **若**图涉及患者或未发表个体数据，**则**本地脚本渲染并本地去标识化，**否则**任何在线绘图 API、云端生图、带 key 的生图服务都不得使用。
4. **若**要画机制图，**则**分子机制、受累器官、动物与操作、胞内胞外分层四类各至少两个具体元素，**否则**缺一类即不合格，退回补内容而不是补装饰。
5. **若**机制图要表达证据来源，**则**用线型图例（实线已报道、虚线本课题推断、T 型抑制），**否则**不要在图内标 `[n]` 参考文献编号。
6. **若**作者要求用文生图一次生成机制图，**则**改走矢量组件拼装，**否则**分子名、箭头方向、器官解剖三样都不可控且不可改，返工成本高于重画。
7. **若**成图位图低于 300 dpi（线条图低于 600 dpi），**则**重跑脚本出高 dpi 或矢量，**否则**靠图像软件放大等于把 300 dpi 门槛永久钉死。
8. **若**最小字号在最终尺寸下低于 7 pt，**则**上调字号或减内容，**否则**整张图缩放到栏宽后审稿人会直接指出不可读。
9. **若**图内含中文，**则**跑一次字体回退并把实际用字写进交付说明，**否则**不得交付带方框或缺字的图。
10. **若**是彩色图，**则**通过灰度与红绿色盲两项检查，**否则**关键类别不能只靠颜色区分，必须叠加线型或点型。
11. **若**是多面板图，**则** panel 字母用大写 A/B/C、8～12 pt 加粗、同一锚点，比较型 panel 裁剪容差 ≤1.5 pt，**否则**字母位置漂移与面板不等宽会被要求重排。
12. **若**图要投中文核心期刊，**则**用中文栏宽与字号预设、宋体/黑体正文，**否则**直接套英文刊模板会被退改。
13. **若**图注缺 n、缺统计方法或缺误差棒含义，**则**补到三项齐全，**否则**按 MAJOR 处理，不进入交付包。
14. **若**图上数字与源 CSV 对不上，**则**判 CRITICAL 并回退重出，**否则**不得以「四舍五入差异」为由放过——先查未取整值再判定。
15. **若**审计脚本不可用，**则**手工核验并显式标注「未自动审计」，**否则**不得声称已通过审计。
16. **若**只有一张位图没有源脚本，**则**判为不可交付并要求补脚本，**否则**勘误阶段无法重出，风险不可控。

## 五、模板与校验

### 5.1 Python 出版级 rcParams 全套模板

```python
# fig_style.py —— 全项目共用一份；不要在各图里重新设 rcParams
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 1) 中文字体回退链：找不到就退到同族，并在日志里打印实际用字
CJK_CANDIDATES = ["Noto Sans CJK SC", "Microsoft YaHei", "SimHei", "Source Han Sans SC"]
available = {f.name for f in font_manager.fontManager.ttflist}
cjk = next((n for n in CJK_CANDIDATES if n in available), None)
if cjk is None:
    print("[warn] 未找到中文字体，图内中文会显示为方框；请安装 Noto Sans CJK 或 SimHei")
print("[info] 实际中文字体:", cjk)

SANS = ([cjk] if cjk else []) + ["Arial", "Helvetica", "DejaVu Sans"]

OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
             "#0072B2", "#D55E00", "#CC79A7", "#333333"]

def apply_style(single_col: bool = False) -> None:
    """single_col=True 用 3.5 in 单栏，否则 7.0 in 双栏（89 / 183 mm）。"""
    width = 3.5 if single_col else 7.0
    mpl.rcParams.update({
        # 版面与尺寸
        "figure.figsize": (width, width * 0.72),
        "figure.dpi": 150,
        "savefig.dpi": 600,               # 位图 ≥300，线条图给 600
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "savefig.transparent": False,
        # 字体与字号（pt；8～9 正文标注，6～7 刻度）
        "font.family": "sans-serif",
        "font.sans-serif": SANS,
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8.5,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "text.usetex": False,
        "axes.unicode_minus": False,      # 负号不要变方框
        # 线条
        "axes.linewidth": 0.8,
        "lines.linewidth": 1.0,
        "lines.markersize": 4,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "xtick.direction": "out",
        "ytick.direction": "out",
        # 去装饰
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "axes.grid": False,
        "grid.alpha": 0.3,
        "grid.linewidth": 0.5,
        "axes.prop_cycle": mpl.cycler(color=OKABE_ITO),
    })

def panel_letter(ax, letter: str, dx: float = -0.15, dy: float = 1.05, size: float = 10):
    """统一 panel 字母锚点：相对坐标固定，整图一致。"""
    ax.text(dx, dy, letter, transform=ax.transAxes,
            fontsize=size, fontweight="bold", va="top", ha="left")

def save_all(fig, stem: str) -> None:
    """双格式落盘：位图给投稿系统，矢量给排版。"""
    fig.savefig(f"{stem}.png")            # 用 rcParams 的 600 dpi
    fig.savefig(f"{stem}.pdf")           # 矢量
```

### 5.2 R / ggplot2 出版主题模板

```r
# theme_pub.R —— 与 5.1 的 rcParams 对齐：单栏 89 mm、双栏 183 mm
library(ggplot2)

okabe_ito <- c("#E69F00", "#56B4E9", "#009E73", "#F0E442",
               "#0072B2", "#D55E00", "#CC79A7", "#333333")

theme_pub <- function(base_size = 8, base_family = "sans") {
  theme_classic(base_size = base_size, base_family = base_family) +
    theme(
      axis.line        = element_line(linewidth = 0.4, colour = "black"),
      axis.ticks       = element_line(linewidth = 0.4, colour = "black"),
      axis.ticks.length = unit(1.5, "pt"),
      axis.text        = element_text(size = 7,   colour = "black"),
      axis.title       = element_text(size = 8.5, colour = "black"),
      legend.title     = element_text(size = 8),
      legend.text      = element_text(size = 7),
      legend.key.size  = unit(8, "pt"),
      legend.frame     = element_blank(),
      plot.title       = element_text(size = 9, hjust = 0),
      strip.text       = element_text(size = 7, face = "bold"),
      panel.grid       = element_blank(),
      plot.margin      = margin(2, 2, 2, 2, unit = "pt")
    )
}

# 双栏 183 mm = 7.2 in；单栏 89 mm = 3.5 in
save_pub <- function(p, stem, width = 7.2, height = 4.8) {
  ggplot2::ggsave(paste0(stem, ".pdf"), p, width = width, height = height,
                  units = "in", device = cairo_pdf)
  ggplot2::ggsave(paste0(stem, ".png"), p, width = width, height = height,
                  units = "in", dpi = 600, bg = "white")
}

# 用法：p + scale_colour_manual(values = okabe_ito) + theme_pub()，再 save_pub(p, "Fig2B")
```

若本机有 R（`Rscript -e 'source("theme_pub.R")'` 能跑通）直接用它；缺 `cairo_pdf` 时退化为 `ggsave(..., device = "pdf")` 并记一句「缺 Cairo，中文可能需嵌入字体」。若本机没有 R，不要为出图临时装环境：改用 5.1 的 Python 模板出同一张图，`.R` 源文件照旧交付供复现，并在图件清单写明实际出图后端。

### 5.3 多面板拼版（GridSpec + A/B/C）

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from fig_style import apply_style, panel_letter, save_all

apply_style(single_col=False)                     # 双栏 7.0 in
fig = plt.figure(figsize=(7.0, 5.6))
gs = GridSpec(2, 3, figure=fig, height_ratios=[1.0, 0.85],
              wspace=0.12, hspace=0.18)           # 间距 0.08～0.15 量级

axes = [
    fig.add_subplot(gs[0, 0:2]),   # A hero panel：跨两列
    fig.add_subplot(gs[0, 2]),     # B
    fig.add_subplot(gs[1, 0]),     # C
    fig.add_subplot(gs[1, 1]),     # D
    fig.add_subplot(gs[1, 2]),     # E
]
for ax, letter in zip(axes, "ABCDE"):
    panel_letter(ax, letter)                       # 同一锚点 -0.15, 1.05
# ... 填数据 ...
save_all(fig, "Fig3")
```

交付前用 5.4 核对最小字号与实际 dpi；比较型 panel 再量一次裁剪矩形，容差 ≤1.5 pt。

### 5.4 图件终检脚本（可跑，给读数）

```python
# check_figure.py —— 逐图给实测读数，不做「看着还行」的判断
import sys, json
from PIL import Image

MIN_DPI, MIN_FONT_PT = 300, 7.0

def check_png(path: str) -> dict:
    im = Image.open(path)
    dpi = im.info.get("dpi", (None, None))
    return {"file": path, "format": im.format, "pixels": im.size,
            "dpi": dpi, "dpi_ok": bool(dpi[0] and dpi[0] >= MIN_DPI)}

def check_pdf_fonts(path: str) -> dict:
    """PDF 内每个文字 span 的 size 即 pt；取最小值与最小值出处。"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return {"file": path, "note": "未安装 PyMuPDF，字号需手工核验"}
    doc = fitz.open(path)
    sizes, names = [], set()
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if span["text"].strip():
                        sizes.append(round(span["size"], 2))
                        names.add(span["font"])
    return {"file": path, "pages": doc.page_count,
            "min_font_pt": min(sizes) if sizes else None,
            "font_ok": bool(sizes) and min(sizes) >= MIN_FONT_PT,
            "fonts": sorted(names)}

if __name__ == "__main__":
    report = []
    for p in sys.argv[1:]:
        report.append(check_pdf_fonts(p) if p.lower().endswith(".pdf") else check_png(p))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    bad = [r for r in report
           if r.get("dpi_ok") is False or r.get("font_ok") is False]
    sys.exit(2 if bad else 0)      # exit 2 = 有不合格项，阻断交付
```

用法：`python check_figure.py Fig3.png Fig3.pdf`；`exit 2` 即不交付。这个脚本只核 DPI 与字号两项，图注、数字对账、去标识化仍需按 5.5 清单人工过。

### 5.5 期刊图件终检清单

| # | 检查项 | 合格判据 | 判定 |
|---|---|---|---|
| 1 | 位图 dpi | ≥300（照片/显微）；线条图 ≥600 或纯矢量 | 有读数 |
| 2 | 文件格式 | PDF/EPS/SVG 优先；栅格用 TIFF/PNG；无 JPEG | 有清单 |
| 3 | 画布尺寸 | 单栏 89 mm / 双栏 183 mm（中文刊按刊物要求） | 有读数 |
| 4 | 最小字号 | 最终尺寸下 ≥7 pt（正文标注 ≥8 pt） | 有读数 |
| 5 | 字体 | 英文 Arial/Helvetica；中文宋体或黑体；无缺字 | 有字体名 |
| 6 | 配色 | 色盲友好、灰度可辨、类别 ≤8 色、无 jet、非仅靠颜色编码 | 有检查图 |
| 7 | panel 标注 | 大写 A/B/C、8～12 pt 加粗、锚点统一 | 有记录 |
| 8 | 单位与轴 | 轴标签带单位、无截断轴、无三维 | 目视 |
| 9 | 误差棒 | 注明 SD/SEM/95%CI，且给 n | 图注核对 |
| 10 | 显著性 | 星号与 P 值对应一致，层级 ≤4 | 图注核对 |
| 11 | 图注 | 含 n、统计方法、误差棒含义；首句陈述发现 | 三点齐全 |
| 12 | 数据对账 | 图上数字抽 3 处与源 CSV 一致 | 有记录 |
| 13 | 去标识化 | 影像/照片无患者信息，有记录 | 有记录 |
| 14 | 三件套 | 成图 + 源脚本 + 数据来源齐全 | 缺一不交付 |

### 5.6 机制图四要素自检表

| 要素 | 必填内容 | 合格判据 | 常见错法 |
|---|---|---|---|
| ① 分子机制 | 至少两个具体分子/通路符号，箭头带通断关系 | 图内可直接读出级联顺序 | 只写「炎症通路」这类泛称；把 marker 当 driver |
| ② 受累器官 | 实际受累器官（脑/肺/肝/肾/心/肠/血管内皮） | 器官面板与正文表型一致 | 画无关器官凑版面；器官与通路无连线 |
| ③ 动物与操作 | 品系、性别、SPF、周龄体重、造模参数、麻醉与剂量、定位坐标、给药途径 | 关键参数能在图内或图注读到 | 只写「大鼠模型」；缺剂量与途径 |
| ④ 胞内胞外分层 | 胞外配体/糖萼 → 膜受体 → 胞质级联 → 核内转录；细胞间连接与基底膜 | 四层可辨且不串层 | 受体画在胞内；缺基底膜与连接结构 |
| 附：证据分级 | 实线=已报道、虚线=本课题推断、T 型=抑制 | 图例三行齐全且与线型一致 | 同一分子一处实线一处虚线 |
| 附：文献编号 | 机制图内不出现 `[n]` | 图内无编号，出处进图注 | 照抄正文配图习惯标 `[n]` |

四要素每类至少命中两个具体元素才达标；任一类为 0 即回退第 3.4 节第 1 步重列清单。

### 5.7 交付报告格式

```markdown
## 图件终检报告 · 项目名 / 日期

| 项 | 读数 | 阈值 | 结论 |
|---|---|---|---|
| 位图 dpi | 600 | ≥300 | 通过 |
| 最小字号 | 6.2 pt | ≥7 pt | 不通过（CRITICAL）|
| 字体 | Arial + Noto Sans CJK | 无缺字 | 通过 |
| 数据对账 | 3/3 一致 | 3/3 | 通过 |

### 分级问题
- CRITICAL：Fig2B 最小字号 6.2 pt（轴标签被缩图）→ 重出，上调至 8 pt
- MAJOR：Fig3 图注缺误差棒含义

### 结论
不通过（1 项 CRITICAL 待修）；修复后重跑 check_figure.py 并复检。
```

## 六、交付物

一次完整交付的目录结构：

```text
figures/
  Fig1.png            # 位图，≥300 dpi（线条图 600）
  Fig1.pdf            # 矢量，投稿/排版首选
  Fig2.png
  Fig2.svg
  mechanism/
    Fig4_mechanism.svg      # 机制图矢量源
    Fig4_mechanism.png      # 300 dpi 预览
    Fig4_mechanism.pdf      # 印刷用矢量
    Fig4_spec.json          # 组件与坐标 spec，可再编辑
  scripts/
    fig_style.py            # 全项目统一样式
    Fig1.py                 # 一图一脚本，可独立复跑
    Fig2.R
  data-manifest.md          # Figure|Data file|Real/mock|Source|Script|Outputs
  figure-audit.md           # 终检报告（5.7 格式）
  repro/                    # 复跑包：命令 + 依赖版本 + 数据副本 + README
```

命名与记录约定：

- 文件名一律 `Fig<序号><面板>.png`，不出现「最终版」「改3」这类词；版本用 `-v2` 后缀并保留旧版。
- 源脚本一图一份，脚本里不写死本机绝对路径；数据路径用相对路径或环境变量。
- `data-manifest.md` 六列必须填满；模拟数据以 `mock_` / `synthetic_` 开头并标「待真实实验替换」。

## 七、来源索引

| 技能名 | 原文路径 | 本域用途 |
|---|---|---|
| `matplotlib` | `knowledge/skills/figures/matplotlib.md` | 单图渲染底座、rcParams 模板、矢量导出 |
| `nature-figure` | `knowledge/skills/figures/nature-figure.md` | figure contract、backend 互斥、1.5 pt 对齐门、碰撞审计 |
| `figures-python` | `knowledge/skills/figures/figures-python.md` | 栏宽英寸、配色常量、data manifest 纪律 |
| `seaborn` | `knowledge/skills/figures/seaborn.md` | 统计图与分面兜底 |
| `academic-figures` | `knowledge/skills/figures/academic-figures.md` | 40 图型生成器、PRISMA 数字自洽、字号与重叠门禁 |
| `science-figures` | `knowledge/skills/figures/science-figures.md` | 17 图型与 8 种期刊风格切换 |
| `scientific-visualization` | `knowledge/skills/figures/scientific-visualization.md` | 期刊栏宽/字号/配色硬指标、13 项终检清单 |
| `medical-illustration` | `knowledge/skills/figures/medical-illustration.md` | 矢量组件库、箭头三语义、SVG 导出约束 |
| `scientific-thinking-biology` | `knowledge/skills/stats/scientific-thinking-biology.md` | 机制链条校核、生物学层级对位 |
| `figure-designer` | `knowledge/skills/figures/figure-designer.md` | 核心图布局顾问、分级审计 |
| `drawio-reconstruction` | `knowledge/skills/figures/drawio-reconstruction.md` | 参考图重建 .drawio、元素清单与 audit |
| `fireworks-tech-graph` | `knowledge/skills/figures/fireworks-tech-graph.md` | 语义化 SVG、连线与碰撞校验 |
| `markdown-mermaid-writing` | `knowledge/skills/figures/markdown-mermaid-writing.md` | 文本定拓扑、可 diff 的源 |
| `scientific-drawing` | `knowledge/skills/figures/scientific-drawing.md` | 技术路线/示意图兜底骨架与配色 |
| `pydicom` | `knowledge/skills/format/pydicom.md` | DICOM 读写、去标识化、像素输出 |
| `airs-segment-anything-model` | `knowledge/skills/figures/airs-segment-anything-model.md` | 零样本分割、掩膜裁剪 |
| `histolab` | `knowledge/skills/stats/histolab.md` | 病理全片取块、染色归一化 |
| `xiantao-plot-api` | `knowledge/skills/figures/xiantao-plot-api.md` | 弃用：数据经 requests 上传第三方接口 |
| `scientific-schematics` | `knowledge/skills/figures/scientific-schematics.md` | 弃用：经 OpenRouter 外部生图，只出位图 |
| `ai-figure-studio` | `knowledge/skills/figures/ai-figure-studio.md` | 弃用：依赖本机 Illustrator 手工运行，不可复现 |
| `generate-image` | `knowledge/skills/figures/generate-image.md` | 弃用：上传外部服务、生成像素不可回溯 |
| `figures-diagram` | `knowledge/skills/figures/figures-diagram.md` | 弃用：只产提示词不产图件 |
