# figures 域写作笔记（v3）

## 一、36 条源技能怎么聚的类（按 dir 去重后 35 条）

| 簇 | 条数 | 代表（字节） | 结论 |
|---|---|---|---|
| 数据图底座 | 4 | matplotlib 11454／seaborn 19601／plotly 7199／figures-python 6233 | matplotlib 主用，其余补强或兜底 |
| 统计图生成器 | 4 | academic-figures 31534／science-figures 6606／xmed-figure 15008／csv-data-summarizer 5692 | academic-figures 主用，xmed 弃用 |
| 期刊规范与拼版 | 4 | scientific-visualization 20526×3／nature-figure 11840 | 同名三来源同判，拆成 panel／style／audit |
| 机制与示意图 | 5 | medical-illustration 11937／ai-figure-studio 26012／scientific-schematics 23850／figure-designer 7661／document-illustrator 11648 | 只留可编辑矢量一条链 |
| 流程与矢量 | 4 | drawio-reconstruction 22022／fireworks-tech-graph 5658／markdown-mermaid-writing 14888／scientific-drawing 5356 | 文本定拓扑，交 .drawio 源文件 |
| 影像与切片 | 3 | imaging-data-commons 34425；pydicom／histolab 取自 toolbox 域 | 本地解码与取块才进流程 |
| 文生图与外部服务 | 6 | infographics 18071／aris-paper-illustration-image2 20237／generate-image 7048／figures-diagram 4304／Illustrator 1801／xiantao-plot-api 20822 | 整簇弃用，只借纪律 |
| 域外 | 8 | workbuddy-smartsheet 27789／tencent-docs／tencent-saas-docs／aris-auto-review-loop-llm 8600／geopandas 7117／pymatgen 20034／nature-reader 3902／scholar-conceptual 21271 | 不属图件生产 |

## 二、四问的答案

- 最擅长：academic-figures（40 图型、PRISMA 数字自洽、重叠 exit 2）；scientific-visualization（栏宽、字号、Okabe-Ito、禁 jet）；nature-figure（1.5 pt 对齐门、碰撞审计）；medical-illustration（百余矢量组件、激活／抑制／易位三语义箭头）。
- 不做什么：academic-figures 不做无数据示意图；medical-illustration 不做数据图；figure-designer 只出建议；scientific-drawing 无脚本无门禁。
- 搬进协议：1.5 pt 对齐门、exit 2 重叠门、13 项终检、四要素与实线／虚线／T 型、PRISMA 五框核数。
- 与谁冲突：xmed-figure 与全部文生图技能把「机制图」导向外部渲染，与「可控可编辑、图内不标 [n]」直接冲突。

## 三、10 个弃用条目分三类

- **数据出机**：xiantao-plot-api（requests 调在线接口）、scientific-schematics（OpenRouter 生图）、infographics（Nano Banana Pro）、aris-paper-illustration-image2（Codex 位图）、xmed-figure（X-Med MCP 上传 CSV，默认 150 dpi）、generate-image（通用文生图）。
- **本机依赖**：ai-figure-studio（本机 Illustrator 跑 .jsx，产物 .ai 不可复现）、Illustrator（需装 Illustrator 与 Flue 桥）。
- **不出图件**：figures-diagram（只产提示词）、document-illustrator（装饰配图，非实验图）。

## 四、本机实测（只当环境记录，不写成对用户的硬性要求）

- matplotlib 3.11.2、Pillow 12.3.0、PyMuPDF 1.28.2；中文回退链命中 Microsoft YaHei；`import pymupdf as fitz` 可消弃用警告。
- 本机没有 Rscript，故 MD 写明「有 R 用 R、无 R 用 Python 出同一张图，.R 源文件照旧交付」。
- MD 两段 python 已实跑：PNG 3705×2987 px、dpi 599.9988、PDF 最小字号 7.0 pt，check_figure.py exit 0。

## 五、校验记录

- `verify-capabilities figures`：首轮 38 errors，全是 best_at／limits／take 只有 6～7 字；补到 8 字以上后 **10 capabilities, 0 errors, 0 warnings**。
- `verify-ledger figures`：**35 entries, 0 errors, 0 warnings**（源 36 条，scientific-visualization 两条同名 dir 合并为一条判定）。
