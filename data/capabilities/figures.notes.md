# figures 域写作笔记（figures.json / research-figures.md）

## 一、76 条目录怎么聚的类

按 `catalog.json` 中 `domain === "figures"` 筛出 76 条、按字节降序后聚成七簇（数字为条目数）：

| 簇 | 条目数 | 代表条目（字节） | 结论 |
|---|---|---|---|
| 数据图渲染底座 | 12 | matplotlib 11514 / seaborn 19655 / plotly 7251 / matlab 10096 | 只取 matplotlib 做底座、seaborn 做补强 |
| 图表族生成器 | 6 | academic-figures 31545 / science-figures 6686 / xiantao-plot-api 20894 | academic-figures 主用；在线 API 类弃用 |
| 期刊与多面板规范 | 5 | scientific-visualization 25616 / nature-figure 11906 / figures-python 6301 | 三件互补：硬指标／证据架构／常量与清单 |
| 示意图与机制图 | 9 | medical-illustration 12018 / scientific-schematics 23932 / scientific-drawing 5442 | 只留可编辑矢量的那条 |
| 流程与矢量编辑 | 8 | drawio-reconstruction 22104 / fireworks-tech-graph 5738 / markdown-mermaid-writing 14976 | 拓扑用文本定、成品用 .drawio 交 |
| 影像与照片 | 7 | pydicom 13242 / histolab 20206 / airs-segment-anything-model 14002 | 只有本地解码与本地取块可进流程 |
| 文生图与外部服务 | 14 | ai-figure-studio 26072 / figures-diagram 4374 / generate-image 7116 | 整簇弃用，仅借纪律不借执行 |
| 其它（学者类大件） | 15 | scholar-analyze 82437 / scholar-eda 49498 / scholar-verify 29391 | 只有 scholar-verify 的表图对账可借用 |

## 二、四问的答案落在哪

- 最擅长：academic-figures 在图型覆盖面与门禁上最强（40 图型、PRISMA 数字自洽、重叠 exit 2）；scientific-visualization 在期刊硬指标上最细（栏宽、字号、Okabe-Ito、禁 jet）。
- 不做什么：academic-figures 明确不做无数据支撑的纯示意图；medical-illustration 只做矢量组件不做数据图；figures-diagram 只产提示词。
- 搬进协议：1.5 pt 面板对齐门（nature-figure）、字号门禁与重叠门禁（academic-figures）、15 项终检读数（scientific-visualization）、四要素与三语义箭头（medical-illustration）。
- 与谁冲突：scientific-schematics、ai-figure-studio、figures-diagram 会把「机制图」导向外部生图，与「机制图必须可控、可编辑、不标 [n]」直接冲突，故整簇弃用。

## 三、五个弃用条目与理由

| 技能 | 理由 |
|---|---|
| `xiantao-plot-api` | 数据经 requests 上传第三方接口，无法本地复核复现；涉患者数据绝不出机 |
| `scientific-schematics` | 经 OpenRouter 调外部生图模型，只出位图，分子标签与箭头语义不可控 |
| `ai-figure-studio` | 依赖本机 Illustrator 手工运行 .jsx，产物 .ai 不可复现、不可审计 |
| `generate-image` | 上传外部服务生成像素，实验图不可回溯，不得替代真实数据渲染 |
| `figures-diagram` | 只把需求转成生图提示词，自身不产出图件，不构成交付物 |

## 四、本机实测事实（只当环境记录，不写进对用户的硬性要求）

- Python 侧可用：matplotlib 3.11.2、Pillow 12.3.0、PyMuPDF 1.28.2；`import fitz` 有弃用警告，新写法 `import pymupdf`。
- 中文字体回退链在本机命中 Microsoft YaHei；未装 Noto Sans CJK SC。
- 本机**没有 Rscript**，故 MD §5.2 显式给出「无 R 时改用 Python 出图」的分支，不把 R 写成必需前置。
- 5.1／5.3／5.4 三段代码已在本机实跑：PNG 3598×2901 px、dpi 599.9988、PDF 最小字号 7.0 pt，`check_figure.py` 退出码 0。

## 五、校验记录

- `node scripts/verify-capabilities.mjs figures`：首轮 2 errors（两条 `limits` 只有 7 字）；改为「仅适用于示意场景」「偏重社科稿件流程」后 **9 capabilities, 0 errors, 0 warnings**。
- `node scripts/verify-package.mjs`：0 errors（3 warnings 属包级既有项，非本域产物）。
