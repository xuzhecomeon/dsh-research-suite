---
name: research-figures
description: 科研绘图与图件融合技能：用真实数据渲染出版级单图与统计图族，拼多面板主图，画四要素机制图与流程图，处理医学影像与去标识化，统一配色样式，交付终检报告与可复跑脚本包。
whenToUse: 用户要画论文配图、期刊图件、机制图、信号通路图、流程图、示意图、多面板组图、病理或影像图，或要核验 DPI、字号、字体、配色、图注、数据来源是否达标时使用。
---

# 科研绘图与图件：融合 SOP

本技能管的是「图」这一件事：把数据与机制变成能过期刊制作端的图件，并证明它过关。它不管统计推断（回 `research-stats`）、不管文献检索（回 `research-literature`）、不改研究结论。

执行顺序固定：先用 §一 的判定树选卡，再按 §二 该卡的编号步骤做，卡住时查 §三 常见错误，交图前跑 §四 自检。每张卡的触发词、门禁与可深读技能见 §五。

## 一、任务判定树

### 1.1 四类图先分清

| 图类 | 数据来源 | 主用卡 | 典型产物 |
|---|---|---|---|
| 数据图（单图） | 真实实验数据表 | `figures.render` | 柱状、折线、散点、箱线 |
| 统计图族 | 统计结果表（来自 R） | `figures.statplot` | 生存曲线、森林图、ROC、热图、火山图 |
| 机制图 | 文献机制 + 本课题证据 | `figures.mechanism` | 通路机制总图 |
| 示意图与流程 | 流程节点、检索计数 | `figures.flow`／`figures.schematic` | PRISMA、技术路线、细胞结构 |
| 影像与切片 | DICOM、WSI、显微照片 | `figures.imaging` | 影像对照、病理切片 |
| 拼版总图 | 上面几类产出 | `figures.panel` | 多面板主图 |
| 可编辑交付 | 参考图或草稿 | `figures.vector` | `.drawio`／`.svg` 源文件 |

### 1.2 判定步骤（按顺序问，问到一个就停）

1. 有没有数字要呈现？有 → 数据图或统计图族；没有 → 走第 3 步。
2. 图上是「量」还是「关系」？量 → `figures.statplot`（生存、森林、ROC、热图、火山图各用对应图型）；关系 → `figures.mechanism` 或 `figures.flow`。
3. 要表达的是「因果级联」还是「先后步骤」？因果级联 → `figures.mechanism`（四要素硬门）；先后步骤 → `figures.flow`。
4. 要画的是细胞、亚细胞器、组织切片这类**结构**？是 → `figures.schematic`（构件层），再回 `figures.mechanism` 拼整图。
5. 图里有患者影像、病理片、显微镜照片？是 → 先进 `figures.imaging` 去标识与取块，再进拼版。
6. 最终要交给别人改字改框？是 → `figures.vector` 出源文件，不要只交 PDF。
7. 无论哪条路径，收尾都要过 `figures.audit`，并复用 `figures.style` 的样式文件。

### 1.3 三条硬边界（越界即返工）

- **数据图不等于示意图。** 数据图必须由真实数据渲染，Python 或 R 均可；禁止用文生图、插画类技能顶替数据图。哪张图是「画的」哪张是「算的」，必须在数据清单里标出来。
- **机制图不等于流程图。** 机制图必须同时承载四类信息：分子机制、受累器官、实验动物与操作、胞内外信号分层，缺一类即不合格；流程图只讲先后与计数，别硬塞分子。
- **患者数据不出机。** 涉患者影像、病理、基因数据的图，全程本地处理，禁用任何需要上传数据的在线接口（`xiantao-plot-api`、`scientific-schematics`、`generate-image` 一类一律不用）。

### 1.4 触发词到卡的映射

「画一张图／按期刊要求出图／分辨率不够」→ `figures.render`；「生存曲线／森林图／ROC／热图聚类／火山图」→ `figures.statplot`；「多张图拼成一张／加 ABC／面板对齐」→ `figures.panel`；「机制图／通路图／机制示意」→ `figures.mechanism`；「细胞结构／亚细胞器／组织切片示意」→ `figures.schematic`；「流程图／PRISMA／技术路线」→ `figures.flow`；「可编辑的图／drawio／照这张重画」→ `figures.vector`；「DICOM／去标识／比例尺／切片切图」→ `figures.imaging`；「配色／期刊风格／统一字体」→ `figures.style`；「终检／投稿前检查／图注写什么」→ `figures.audit`。

## 二、每卡融合 SOP

每节结构固定：**判断何时用 → 融合取舍与证据 → 编号步骤（含数值阈值）→ 卡内红线**。步骤里的阈值都是可核的数值，不是形容词。

### 2.1 figures.render：出版级单图渲染

**何时用**：手上有数据表，要出一张能直接排进稿子的图。

**融合取舍与证据**：以 `matplotlib` 的对象式 API 作底座（唯一能给到 `fig.linewidth`、`ax.tick_params` 这一级控制[1]），`seaborn` 只用来先出探索稿（它的分面与箱线能省一轮手写，但默认主题偏演示风，必须换掉），`figures-python` 提供三套配色常量与「Figure／Data file／Real or mock／Source／Script／Outputs」六列数据清单表头[2]，`plotly` 仅在探索期给人看趋势（期刊不收交互图，终稿弃用）。取长补短的证据是：`figures-python` 的 rcParams 片段只给 10 项，`scientific-visualization` 另给了「位图 300–600 dpi、线稿 600–1200 dpi、绝不用 JPEG」的格式矩阵[3]，两者互补后本卡把「双格式落盘＋实测读数」写成门禁。

**步骤**：

1. 锁画布：按目标栏宽设 `figure.figsize`，单栏 89 mm（3.5 in）、双栏 183 mm（7.0 in）；字号按最终尺寸给，正文标注 8～9 pt、刻度 7 pt，缩放后不得低于 7 pt。
2. 定色板：类别 ≤8 用 Okabe-Ito 八色，连续量 viridis／cividis，发散量 RdBu_r 且以 0 为中心；禁 jet 与 rainbow。
3. 绘图形：分组比较画箱线叠个体散点；误差棒注明 SD／SEM／95%CI 三者之一，图注给 n。
4. 双格式落盘：600 dpi PNG 加矢量 PDF，`savefig.transparent=False`、`bbox='tight'`，不导 JPEG。
5. 读实测值：跑 §四 的检查脚本读 PNG 的 `info['dpi']` 与 PDF 每个 span 的 `size` 最小值，不达标重出。
6. 记数据来源：写进 `data-manifest.md`，mock 数据文件名前缀 `mock_`／`synthetic_` 并标「待真实实验替换」。

**样式文件（Python，全项目一份，不再在每张图里重设）**：

```python
# fig_style.py —— 项目内只 import 这一份
import matplotlib as mpl
from matplotlib import font_manager

CJK = ["Noto Sans CJK SC", "Microsoft YaHei", "SimHei", "Source Han Sans SC"]
have = {f.name for f in font_manager.fontManager.ttflist}
cjk = next((n for n in CJK if n in have), None)   # 找不到就打印警告，别静默出方框
SANS = ([cjk] if cjk else []) + ["Arial", "Helvetica", "DejaVu Sans"]
OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
             "#0072B2", "#D55E00", "#CC79A7", "#333333"]

def apply_style(single_col: bool = False) -> None:
    w = 3.5 if single_col else 7.0
    mpl.rcParams.update({
        "figure.figsize": (w, w * 0.72), "figure.dpi": 150,
        "savefig.dpi": 600, "savefig.bbox": "tight", "savefig.transparent": False,
        "font.family": "sans-serif", "font.sans-serif": SANS,
        "font.size": 8, "axes.titlesize": 9, "axes.labelsize": 8.5,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
        "axes.unicode_minus": False, "axes.linewidth": 0.8, "lines.linewidth": 1.0,
        "xtick.major.size": 3, "ytick.major.size": 3,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "axes.grid": False, "grid.alpha": 0.3,
        "axes.prop_cycle": mpl.cycler(color=OKABE_ITO),
    })
```

**卡内红线**：见 §三 第 1、3、8 条。

### 2.2 figures.statplot：统计图族

**何时用**：手上是统计结果表（HR／OR 及 95%CI、P 值、事件数、n），要出生存曲线、森林图、ROC、列线图、热图或火山图。

**融合取舍与证据**：`academic-figures` 主用，因为它把「40 种图型」与「PRISMA 数字自洽、像素级重叠门禁 exit 2、`audit_pdf.py --min-size --fail-below` 字号门禁」做成了可执行入口[4]；`science-figures` 补强，用于一次切换 8 种期刊风格并自动检测中文（`--cjk`）；`seaborn` 补强，出初稿快；`xmed-figure` **弃用**——它的 30 种 chartType 需要把 CSV 经 X-Med MCP 上传到云服务渲染，系统默认 dpi 只有 150[5]，涉患者数据直接违规，只借它的「图型—参数」对照表与组图布局公式（1→1×1、2→1×2、4→2×2、5／6→2×3、7+→ceil(n/3)×3）。

**步骤**：

1. 对表核数：HR／OR 的 95%CI、P 值、事件数、各组 n 抽 3 处与正文复核，对不上先改表。
2. 确认图型与方法匹配：ROC 只用于二分类结局，KM 必须有时间与结局两列并附风险表。
3. 按图型跑生成器（一份 JSON 数据，一张图一个脚本，脚本内不写本机绝对路径）。
4. 套期刊风格：`--style nature|lancet|science|cell|nejm|jama`，中文刊用 cma／cn-core 预设并确认中文字体命中。
5. 过门禁：重叠计数必须为 0，PDF 最小字号 ≥7 pt（把默认的 5 pt 主动收严到 7 pt）。
6. 同源出图注：用同一份数据生成图注，含 n、检验名、误差棒含义、显著性阈值。

**卡内红线**：见 §三 第 2、9 条。

### 2.3 figures.panel：多面板拼版

**何时用**：几张子图要合成一张主图（Fig. 1 这类）。

**融合取舍与证据**：`scientific-visualization` 主用，给出期刊栏宽表（Nature 单 89／双 183 mm、Science 55／175、Cell 85／178）与 panel 字母 8～12 pt 加粗的规范[3]；`nature-figure` 补强，它把「整图只回答一个 Results 级问题」写成 figure contract，并给出比较型面板裁剪矩形 **1.5 pt** 容差与 PDF 几何碰撞审计（输出 `FIX BEFORE DELIVERY` 即阻断导出、`NOT AUDITABLE` 不得声称通过）[6]；`academic-figures` 的 `composite` 图型用于简单拼版；`matplotlib` 的 GridSpec 兜住复杂嵌套。互补点很具体：前者管「尺寸对不对」，后者管「对齐与碰撞」，缺任一条就只能靠肉眼。

**步骤**：

1. 写 figure contract：一句话结论 + 每个面板的推断角色（不是每个面板一个指标）。
2. GridSpec 搭网格：`width_ratios`／`height_ratios` 定比例，整图宽按 89 mm 或 183 mm 换算，`wspace`／`hspace` 统一留白。
3. 面板字母：`ax.text(-0.15, 1.05, "A", transform=ax.transAxes, fontsize=10, fontweight="bold", va="top")`，A／B／C 大写、锚点全图一致。
4. 共享图例：整图只放一份（放不下用 `fig.legend` 置顶）。
5. 量对齐：比较型面板的裁剪矩形差 ≤1.5 pt，不等宽必须记录豁免理由。
6. 碰撞审计后导出：有阻断项不导出。

**R 侧等价做法（有 R 用 R，无 R 用 Python 出同一张图，`.R` 源文件照旧交付）**：

```r
# theme_pub.R —— 与 fig_style.py 一一对应
library(ggplot2)
theme_pub <- function(base_size = 8) {
  theme_classic(base_size = base_size) +
    theme(axis.text = element_text(size = 7, colour = "black"),
          axis.title = element_text(size = 8.5),
          legend.key = element_blank(), legend.frame = element_blank(),
          strip.background = element_blank(),
          plot.margin = margin(4, 4, 4, 4))
}
save_pub <- function(p, stem, w = 7.0, h = 5.0) {
  ggsave(paste0(stem, ".pdf"), p, width = w, height = h, device = cairo_pdf)  # 矢量
  ggsave(paste0(stem, ".png"), p, width = w, height = h, dpi = 600)          # 位图
}
# 若本机无 R：改用 2.1 的 fig_style.py 出同一张图，R 脚本仍随包交付供有 R 的合作者复跑
```

**卡内红线**：见 §三 第 5、10 条。

### 2.4 figures.mechanism：机制图（四要素硬门）

**何时用**：要把「某个通路在某个器官里被激活、用某模型验证过」讲成一张图。

**融合取舍与证据**：`medical-illustration` 主用——它提供百余原创矢量组件（亚细胞、细胞、组织器官、实验室器材）与三种语义箭头（激活／抑制／易位），并明确 svglib 的渲染限制（禁 filter、CSS style、textPath、mask；透明度导出不可靠须用实色近似）[7]；`scientific-thinking-biology` 补强，用来在画前按「分子→细胞→组织器官→个体」四层校因果、区分 marker 与 driver；`figure-designer` 补强，先出文字版布局与规则审计；`ai-figure-studio` 与 `scientific-schematics` **弃用**——一个依赖本机 Illustrator 手工跑 `.jsx`、产物 `.ai` 不可复现，一个经 OpenRouter 上传描述生图、分子标签不可控，只借前者「符号一律用 path 绘制」与后者「迭代评审阈值」两条纪律。

**四要素（缺一类即退回重画）**：

| 要素 | 必须出现的内容 | 判定 |
|---|---|---|
| ① 分子机制 | ≥2 个具体分子／通路名，且带可读通断关系（如 TLR4→MyD88→NF-κB；NLRP3／ASC／Caspase-1→GSDMD；RIPK1／RIPK3／MLKL；GPX4／ACSL4；MMP-2／9；ZO-1／Occludin／Claudin-5） | 数一数，不够就回文献 |
| ② 受累器官 | ≥2 个器官面板（脑、肺、肝、肾、心、肠、血管内皮），与正文表型一致 | 缺器官说明还是流程图 |
| ③ 动物与操作 | 品系（SD／Wistar 大鼠）、性别、SPF、造模参数、麻醉方式、立体定位坐标、给药剂量与途径，至少 4 项可读 | 一项都没有不是机制图 |
| ④ 胞内外分层 | 胞外配体／糖萼→膜受体→胞质级联→核内转录四层自外向内，画出细胞间连接与基底膜 | 全挤在一层就重画 |

**步骤**：

1. 列清单：四类各写一栏，每类 ≥2 个具体元素；写不出具体分子名，说明文献没读够。
2. 校链条：四层核对因果，只有文献或本课题数据支持的环节画实线，推断画虚线。
3. 出文字版布局：中心六成画细胞与四层区室，四周放器官面板、动物操作面板与图例。
4. 搭画布：横版 2400×1700 px，先画基底膜与细胞间连接，再自外向内叠四层，层间留 40 px 不跨层连线。
5. 标证据分级：实线＝已报道、虚线＝本课题推断、T 型＝抑制，图例三行齐全；**图内不标 [n] 文献编号**，出处写进图注或证据表。
6. 导出自检：`c.export(stem, formats=("svg", "png", "pdf"), dpi=300)`，再按四要素表打勾。

**卡内红线**：见 §三 第 4、6、11 条。

### 2.5 figures.schematic：细胞与分子元件示意

**何时用**：机制图一次画不成，先做构件层（细胞结构、亚细胞器、病原体、组织切片），或需要跨图复用同一批元件。

**融合取舍与证据**：`medical-illustration` 主用（组件以 `(x, y)` 为中心锚点、面板跨度 `x±w/2`，改版式须先算边界）[7]；`drawio-reconstruction` 补强，把「先建可见元素清单（id／包围盒／内容／介质／状态）」的方法搬过来[8]；`figure-designer` 兜底给版式；`document-illustrator` **弃用**（按文档主题生成装饰配图，不是实验图，只借配色情绪板思路）。

**步骤**：①按六组分类列元件 → ②先大结构后小分子叠画 → ③连线一条关系一条线，跨区一律直线（`curve` 弧度远超直觉）→ ④中文一律走 `text_el()`，`CD8⁺` 改写 `CD8+`、`I²` 改写 `I2` → ⑤导出 SVG／PNG／PDF 并留 JSON spec。

**卡内红线**：见 §三 第 6、12 条。

### 2.6 figures.flow：流程与方法示意

**何时用**：实验流程、PRISMA 筛选、技术路线、算法框架。

**融合取舍与证据**：`markdown-mermaid-writing` 主用——文本即源，可 diff 可复现，且明确「不要一上来就用绘图库或 AI 画结构性关系图」[9]；`academic-figures` 补强，它的 PRISMA 图型自带数字自洽校验（对不上拒出图）；`fireworks-tech-graph` 补强，SVG 为唯一真源、带语义连线与碰撞校验；`scientific-drawing` 兜底，技术路线图的 A4 版式与「每框 ≤10 字」原则可借，但它没有脚本也没有门禁，阈值必须本 SOP 另补。

**步骤**：①Mermaid 写拓扑，一节点一件事，主干分叉 ≤2 层、节点 ≤20 → ②PRISMA 五框核数（识别减重复减排除＝纳入），对不上不出图 → ③出版级出图，框内每行 ≤10 字、箭头单向带条件标签 → ④校连线语义（一条关系一条线），无法视觉核验时显式声明跳过而非默认通过 → ⑤交付 PDF／SVG 与源文本。

**卡内红线**：见 §三 第 9 条。

### 2.7 figures.vector：可编辑矢量与参考图重建

**何时用**：交付要能被别人打开改字改框；或要复刻一张现有插图。

**融合取舍与证据**：`drawio-reconstruction` 主用，它的判断是「保真度优先、可编辑性次要」，并要求交付 `.drawio`＋PNG＋`audit.md` 三件套，用通用图标顶替风格特异图标属**阻断性缺陷**[8]；`fireworks-tech-graph` 补强，`validate`／`check` 校验元素标识、marker 引用与碰撞；`medical-illustration` 兜底给生物题材矢量；`Illustrator` **弃用**（需本机 Illustrator 加 Flue 桥，换台机器就断，发布版不可依赖）。

**步骤**：①建元素清单并编号（状态 pending／done／needs-fix）→ ②按介质落元素：文字与结构用原生对象，复杂插画用 PNG 裁切，只有简单图标才 SVG 重绘 → ③跑 `check_drawio.py` 与 `batch_verify.py` 对清单 → ④导出 ≥300 dpi PNG 预览并交出源文件与 audit。

**卡内红线**：见 §三 第 12 条。

### 2.8 figures.imaging：医学影像与病理切片

**何时用**：图里有 CT／MRI／PET、全片病理、显微镜照片。

**融合取舍与证据**：`pydicom` 主用（`dcmread` 读标签、匿名化改写、导像素）[10]；`histolab` 补强（`Slide` 加 `RandomTiler` 按 `level` 取块、固定 seed、H&E 染色归一化）[11]；`airs-segment-anything-model` 兜底（点框提示零样本分割出掩膜）[12]；`imaging-data-commons` 兜底（公共肿瘤影像检索与引用标注，用于写清数据来源）。

**步骤**：①清空 PatientName／PatientID／PatientBirthDate／StudyDate 等标识，原件只读、副本另存，留去标识化记录 → ②按倍率取块、固定 seed、染色归一 → ③分割关注区后裁剪，加比例尺与倍率（如 50 μm、×200）→ ④导 PNG 或无损 TIFF（≥300 dpi），图注写数据来源、伦理批件号、染色方法与倍率。

**卡内红线**：见 §三 第 7 条。

### 2.9 figures.style：配色与期刊风格

**何时用**：一组图要统一长相，或投稿前换刊。

**融合取舍与证据**：`figures-python` 主用（`NATURE_COLORS`、`CELL_COLORS`、`COLORBLIND_SAFE` 三套常量与 450 dpi 默认）[2]，但它的中文字体路径写死在 macOS，必须换成本 SOP 的回退链；`scientific-visualization` 补强给出 Okabe-Ito 八色完整值、禁 jet／rainbow、连续量 viridis 的红线[3]；`science-figures` 补强提供 8 种期刊风格切换与 `--cjk` 检测；`scientific-drawing` 兜底只用于非数据图。

**步骤**：①定色板（类别 ≤8、连续 viridis、发散 RdBu_r 以 0 为中心）→ ②定字体回退链并打印命中字体 → ③写一份样式文件（`fig_style.py` 或 `theme_pub.R`），全项目 import 同一份 → ④出彩色与灰度两版样张留档。

**卡内红线**：见 §三 第 3、8 条。

### 2.10 figures.audit：图表终检与交付

**何时用**：任何图交付前，最后一道。

**融合取舍与证据**：`nature-figure` 主用，它的三件套（`validate_figure.py`、`audit_pdf_text.py`、`audit_figure_collisions.py`）＋`FIX BEFORE DELIVERY` 阻断语义把「过关」定义成可判定状态[6]；`scientific-visualization` 补强给 13 项终检清单与十坑清单[3]；`academic-figures` 补强给重叠像素门禁与 `.audit.json` 数字对账侧车[4]；`figure-designer` 兜底，用它的 CRITICAL／MAJOR／MINOR 分级排修复顺序。

**步骤**：①读实测值（PNG 读 `info['dpi']`，PDF 遍历 span 取最小 `size`）→ ②核字体与缺字 → ③核图注四要素（n、统计方法、误差棒含义、显著性阈值）→ ④抽 3 处图上数字回查源表 → ⑤出 `figure-audit.md` 报告并按 CRITICAL 优先修。

**检查脚本（可直接跑，返回码 0 合格、2 有不合格项）**：

```python
# check_figure.py —— 逐图给读数，不做「看着还行」的判断
import sys, json
from PIL import Image
MIN_DPI, MIN_FONT_PT = 300, 7.0

def check_png(p):
    im = Image.open(p); dpi = im.info.get("dpi", (None, None))
    return {"file": p, "pixels": im.size, "dpi": dpi,
            "dpi_ok": bool(dpi[0] and dpi[0] >= MIN_DPI)}

def check_pdf(p):
    try:
        import pymupdf as fitz           # PyMuPDF ≥1.24 的新入口，避免弃用警告
    except ImportError:
        try:
            import fitz                  # 旧版本回退
        except ImportError:
            return {"file": p, "note": "未装 PyMuPDF，字号须手工核验"}
    doc = fitz.open(p); sizes, fonts = [], set()
    for page in doc:
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                for sp in ln["spans"]:
                    if sp["text"].strip():
                        sizes.append(round(sp["size"], 2)); fonts.add(sp["font"])
    return {"file": p, "pages": doc.page_count, "fonts": sorted(fonts),
            "min_font_pt": min(sizes) if sizes else None,
            "font_ok": bool(sizes) and min(sizes) >= MIN_FONT_PT}

if __name__ == "__main__":
    rep = [check_pdf(p) if p.lower().endswith(".pdf") else check_png(p) for p in sys.argv[1:]]
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    bad = [r for r in rep if r.get("dpi_ok") is False or r.get("font_ok") is False]
    sys.exit(2 if bad else 0)            # exit 2 = 有不合格项，阻断交付
```

**卡内红线**：见 §三 第 1、2 条。

## 三、常见错误清单

按踩坑代价从高到低排；每条都给「症状 → 正确做法」。

1. **只写 dpi 参数不读实测值。** 症状：脚本里写了 600，导出图其实是 150。做法：跑 §四 检查脚本读 `info['dpi']`，读数进报告。
2. **字号按屏幕口径设。** 症状：屏幕上很大，缩到 89 mm 后只剩 5 pt。做法：按最终尺寸设，正文 8～9 pt、刻度 7 pt，缩放后复测。
3. **默认配色直接投。** 症状：红绿并列，色盲读者与黑白打印都分不清。做法：Okabe-Ito 八色起步，另导灰度图自查。
4. **把机制图画成流程图。** 症状：只有方框加箭头，没有分子名、没有器官、没有动物参数。做法：回 §2.4 四要素表逐条打勾。
5. **面板字母用 6 pt 或小写。** 症状：拼版后 A／B／C 看不清或被裁掉。做法：8～12 pt 加粗、统一锚点 `(-0.15, 1.05)`。
6. **用 `CD8⁺`、`I²` 直接进图。** 症状：中文渲染管线里变成方框。做法：改写 `CD8+`、`I2`，出图后放大查。
7. **把原始 DICOM 直接外发**或走后台上传接口渲染。症状：患者标识随头文件流出。做法：先本地去标识，任何需要上传数据的接口一律不用。
8. **一张图塞六种颜色。** 症状：图例比数据还抢眼。做法：类别色 ≤8，超了就合并或直接标注。
9. **PRISMA 数字对不上就出图。** 症状：框里数字与检索记录差几条，审稿人一眼看出。做法：五框核数，对不上先改记录。
10. **机制图里标 [n] 文献编号。** 症状：图内塞满上标，读者读不出主线。做法：编号移入图注或独立证据表，图内只留线型语义。
11. **透明叠加做层次。** 症状：导出后深浅失控或整块变实心。做法：用实色近似（浅底＋深描边）。
12. **交 PDF 却要求可编辑。** 症状：对方改不动一个字，只能重画。做法：同时交 `.drawio`／`.svg`／绘图脚本。
13. **图注缺 n 与误差棒含义。** 症状：审稿意见第一条就是它。做法：图注四要素逐项打勾。
14. **用文生图顶数据图。** 症状：柱子高度与数据无关，数值无法回溯。做法：数据图只走真实数据渲染。
15. **一个脚本写死本机绝对路径。** 症状：换台机器跑不动。做法：路径相对化，R 与 Python 双实现并交付源文件。

## 四、交付前自检

### 4.1 期刊图件终检清单（逐项给读数，不给结论词）

| 检查项 | 阈值 | 读数方法 |
|---|---|---|
| 位图 dpi | ≥300（线稿 600） | PIL 读 `info['dpi']` |
| 矢量格式 | PDF／EPS／SVG 至少一种 | 文件存在性 |
| 最小字号 | ≥7 pt | PyMuPDF 遍历 span |
| 字体 | 英文 Arial／Helvetica，中文宋体／黑体 | PDF 内嵌字体名 |
| 缺字 | 无方框、无豆腐块 | 放大目视 + 字体名核对 |
| 类别色数 | ≤8 | 数图例与 `prop_cycle` |
| 灰度可辨 | 相邻类别仍可分 | 导灰度图目视并记录 |
| 色盲友好 | 不含红绿对立 | 对照 Okabe-Ito |
| 单位 | 轴标签带单位（括号内） | 逐轴读 |
| 误差棒 | 注明 SD／SEM／95%CI | 读图注 |
| 样本量 | 图注有 n | 读图注 |
| 显著性 | 星号与图注阈值一致 | 对照统计表 |
| panel 标注 | A／B／C 大写 8～12 pt | 量字号 |
| panel 对齐 | 矩形差 ≤1.5 pt | 脚本量取 |
| 图注四要素 | n／方法／误差棒／显著性 | 逐项打勾 |
| 数字对账 | 抽 3 处一致 | 回查源表 |
| 数据来源 | 有出处与去标识化说明 | 读 manifest |
| 三件套 | 成图＋脚本＋数据来源 | 文件清单 |

### 4.2 机制图四要素自检表（填完才算过）

| 要素 | 本图命中的具体元素 | 证据来源 | 线型 | 判定 |
|---|---|---|---|---|
| ① 分子机制 | 例：TLR4、MyD88、NF-κB | 文献 3 篇 + 本课题 WB | 实线 | 待填 |
| ② 受累器官 | 例：海马、肺、肠 | 组织病理 | — | 待填 |
| ③ 动物与操作 | 例：SD 大鼠、雄性、SPF、侧脑室注射 5 μL | 方法学 | — | 待填 |
| ④ 胞内外分层 | 胞外配体／糖萼→膜受体→胞质级联→核内转录 | 文献 | 实线＋虚线 | 待填 |

自检口令：四行任一行写不出具体元素，就不算机制图；图内不得出现 [n]。

### 4.3 交付报告模板

```markdown
# 图件交付报告：{项目}_{稿件}
## 环境
Python {版本}（matplotlib {版本}）｜R {版本}（未安装则写「无 R，用 Python 出同一张图」）
## 逐图读数
| 图号 | 格式 | 像素 | 实测 dpi | 最小字号 | 字体 | 结论 |
|---|---|---|---|---|---|---|
| Fig1 | PNG+PDF | 3598×2901 | 600 | 7.0 pt | Arial | 通过 |
## 门禁结果
- 机制图四要素：4/4 命中（附表）
- 数字对账：3/3 一致
- 碰撞与对齐审计：无阻断项
## 问题与修复
- CRITICAL：… → 已重出
- MAJOR：… → 已改图注
## 数据与伦理
数据来源：…｜去标识化：已执行（附记录表）｜伦理批件号：…
```

### 4.4 复跑包结构（交这一份，审稿人问「怎么算的」才答得上）

```
repro/
  README.md          # 命令、依赖版本、预期输出
  data/              # 数据副本（mock 数据加前缀 mock_）
  scripts/           # .py 与 .R 双实现
  outputs/           # 成图 + audit.json + figure-audit.md
```

## 五、能力卡索引表

### 5.1 十张卡与主用技能

| 能力卡 | 能力 | 主用技能 | 关键门禁 | 深读 |
|---|---|---|---|---|
| `figures.render` | 出版级单图渲染 | matplotlib | dpi ≥300、最小字号 ≥7 pt | matplotlib、figures-python |
| `figures.statplot` | 统计图族 | academic-figures | 图型匹配、重叠=0、数字对账 | academic-figures |
| `figures.panel` | 多面板拼版 | scientific-visualization | 对齐 ≤1.5 pt、碰撞无阻断 | nature-figure |
| `figures.mechanism` | 机制图四要素 | medical-illustration | 四要素各 ≥2 项、无 [n] | medical-illustration |
| `figures.schematic` | 细胞与分子元件 | medical-illustration | 风格一致、无方框字 | medical-illustration |
| `figures.flow` | 流程与方法示意 | markdown-mermaid-writing | PRISMA 数字自洽、每框 ≤10 字 | academic-figures |
| `figures.vector` | 可编辑矢量重建 | drawio-reconstruction | 文字为对象、元素清单对齐 | drawio-reconstruction |
| `figures.imaging` | 医学影像与切片 | pydicom | 已去标识、有比例尺与倍率 | pydicom、histolab |
| `figures.style` | 配色与期刊风格 | figures-python | 类别色 ≤8、灰度可辨 | scientific-visualization |
| `figures.audit` | 图表终检与交付 | nature-figure | 四项读数、三件套齐全 | nature-figure、academic-figures |

### 5.2 本域 36 个源技能的判定（融合 16、仅索引 1、弃用 10、域外 8）

**融合进卡的**：`scientific-visualization`（3 处同名来源同判）、`academic-figures`、`matplotlib`、`seaborn`、`figures-python`、`nature-figure`、`science-figures`、`scientific-drawing`、`medical-illustration`、`drawio-reconstruction`、`fireworks-tech-graph`、`markdown-mermaid-writing`、`figure-designer`、`plotly`、`pydicom`、`histolab`、`airs-segment-anything-model`、`imaging-data-commons`。

**仅入索引**：`csv-data-summarizer`（只做 CSV 速览，可当数据体检入口，无出版级门控）。

**弃用（都写了理由）**：`xmed-figure`（云服务上传 CSV、默认 150 dpi）、`scientific-schematics`（OpenRouter 外部生图）、`generate-image`（通用文生图、无数据依据）、`infographics`（Nano Banana Pro 只出位图）、`document-illustrator`（装饰性配图）、`figures-diagram`（只产提示词）、`aris-paper-illustration-image2`（Codex 位图）、`ai-figure-studio`（依赖本机 Illustrator）、`Illustrator`（需本机软件与桥）、`xiantao-plot-api`（requests 上传数据）。

**域外**：`workbuddy-smartsheet`、`tencent-docs`、`tencent-saas-docs`（文档协作），`aris-auto-review-loop-llm`（审稿回环），`geopandas`、`pymatgen`（领域数据处理），`nature-reader`（文献精读），`scholar-conceptual`（理论建构）。

### 5.3 深读路径

各技能原文在插件 `knowledge/skills/` 下按域分目录：`figures/<slug>.md`（本域 36 条）、`toolbox/`（pydicom、histolab、airs-segment-anything-model）、`data/scientific-thinking-biology.md`、`writing/scholar-verify.md`。用 `research_kb_read` 按技能名深读，不要凭记忆复述技能能力。

### 5.4 引用来源

[1] `knowledge/skills/figures/matplotlib.md`
[2] `knowledge/skills/figures/figures-python.md`
[3] `knowledge/skills/figures/scientific-visualization.md`
[4] `knowledge/skills/figures/academic-figures.md`
[5] `knowledge/skills/figures/xmed-figure.md`
[6] `knowledge/skills/figures/nature-figure.md`
[7] `knowledge/skills/figures/wnmc-figure.md`
[8] `knowledge/skills/figures/drawio-reconstruction.md`
[9] `knowledge/skills/figures/markdown-mermaid-writing.md`
[10] `knowledge/skills/toolbox/pydicom.md`
[11] `knowledge/skills/toolbox/histolab.md`
[12] `knowledge/skills/toolbox/airs-segment-anything-model.md`
