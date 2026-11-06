---
name: biomed-literature-pipeline
description: 全生物医学领域文献调研流水线（不限专业）。当用户需要「检索某专业/某方向近几年的文献」「系统梳理某疾病/某技术的研究前沿」「批量下载文献全文」「生成带标题与 DOI 的 Excel 文献清单」「找未来研究方向」时使用。支持：① 引导式确认检索方向（任意临床/基础医学专业，中英文均可）；② 英文通道：Europe PMC 多路径检索 + 相关性过滤；③ 中文通道：Europe PMC 中文语种检索（覆盖中华医学会系列/CSCD/北大核心期刊）+ OpenAlex + 核心期刊白名单过滤；④ 多通道批量下载开放获取全文，含「网页全文转 PDF」；⑤ PDF 按论文标题命名；⑥ 生成 Excel 文献清单（语种/来源库/期刊等级/下载状态）；⑦ 代理库（知网 / 中华医学会）直连检索与**中文全文 PDF 下载**（用户有代理库账号时首选，知网已验证）；⑧ 无账号时生成中文库（知网/万方/SinoMed）检索指引与导出文件导入兜底；⑨ 输出研究前沿报告 + 面向不同科研条件的研究方向评估。触发词：文献检索、方向调研、近5年文献、批量下载论文、文献库、前沿报告、研究方向、SCI论文、中文核心期刊、知网、万方、CSCD、北大核心、中华医学会、下载中文文献。
agent_created: true
---

# 生物医学文献调研流水线（Biomed Literature Pipeline）

一套面向**任意生物医学专业与研究方向**的端到端「检索 → 下载 → 命名 → 清单 → 报告」工作流。

> **与旧版（emcc-literature-pipeline）的区别**：本版不再限定急诊/重症，任何临床或基础医学方向都可用；检索源从「仅 SCI」扩展为 **SCI + 中文核心期刊（中华医学会系列 / CSCD / 北大核心）** 双轨。

## 何时使用

- 用户说「检索 XX 方向近几年的文献」「帮我查 XX 病的文献」「XX 领域研究进展如何」
- 用户要为一个方向做**研究前沿调研**，并希望拿到**可下载的全文**
- 用户要**找未来研究方向**（需要先有文献库作依据）
- 用户点名要**中文文献 / 核心期刊 / 知网 / 万方 / CSCD / 北大核心**

## 核心原则（不可违反）

1. **PDF 文件名必须是论文标题** —— 不加 PMID 前缀、不加序号、不加年份。重名时追加 `_2`、`_3`。
2. **相关性过滤必做** —— 顶刊按被引排序会抓来大量无关高被引论文。必须要求标题（或摘要兜底）命中本方向关键词。
3. **方向推荐必须适配用户医院条件** —— 先问清实验室、经费、随访、多中心协调能力，再推荐"能落地"的方向，并**如实说明优缺点**；不做"多中心/高大上"的默认推荐。
4. **中文核心文献要主动争取** —— 中文核心刊在开放数据源中覆盖有限，必须走"EPMC 中文语种通道 + 中文库检索指引 + 导出导入"三条路，不能只跑英文通道了事。
5. **患者数据不出本机** —— 本流水线只处理公开文献。

## 环境要求

- Python 3（需 `requests`、`openpyxl`）
- 网络可访问 `ebi.ac.uk`（Europe PMC）、`api.openalex.org`、`api.unpaywall.org`（无需 API key）
- 网页全文转 PDF 通道需 `bs4` + `lxml` + `pymupdf`（缺失时自动降级并提示）
- **代理库下载通道（Step 5B）**：需 `playwright`（浏览器用系统 Edge，`channel="msedge"`）；凭据文件 `~/.workbuddy/credentials/cn_proxy.json`

---

## 工作流

### Step 0：引导式信息筛选（必做，不要跳过）

向用户确认三件事：

```
1) 检索方向：具体是哪个专业 / 哪个病种 / 哪项技术？
   —— 用户给中文即可；但**务必同时准备英文关键词**（中文刊在 Europe PMC 的题录是英文翻译，
      且 SCI 检索需要英文），由你（Agent）负责翻译与扩展同义词。
2) 时间范围：默认近 5 年，可调整。
3) 目标产出：只要 Excel 清单，还是同时要 PDF 全文 + 前沿报告？
4) 是否包含中文文献？（默认包含）
```

> **不要自行缩小用户的方向范围**。用户说"急诊和重症方向"就覆盖全领域子方向，说"骨科创伤"就覆盖该方向主要病种。
> 主题清单示例见 `references/topics_examples.md`；中文核心期刊白名单见 `references/cn_journals.json`。

### Step 1：检索（中英双轨）

**方式一：单方向快速检索**

```bash
python scripts/pipeline.py search --out <工作目录> \
  --topic "骨盆骨折出血" \
  --keywords "pelvic fracture;hemorrhage;bleeding;hemodynamic instability" \
  --years 2021-2026 --lang both
```

- `--topic`：中文或英文方向关键词，也可直接给布尔表达式
- `--keywords`：**英文关键词，分号分隔**（中文通道与英文通道都会用；建议把同义表达都列上）
- `--lang`：`both`（默认）/ `en` / `en_only` / `cn` / `cn_only`
- `--cn-query`：可选，直接指定中文通道使用的英文布尔检索式

**方式二：多子方向批量检索（推荐用于全领域调研）**

```bash
python scripts/pipeline.py search --out <工作目录> --topics my_topics.json --years 2021-2026
```

`my_topics.json` 示例：

```json
{
  "脓毒症与脓毒性休克": "(\"sepsis\" OR \"septic shock\")",
  "ARDS与机械通气": "(\"acute respiratory distress syndrome\" OR \"mechanical ventilation\")",
  "骨盆骨折出血": "(\"pelvic fracture\" AND (hemorrhage OR bleeding))"
}
```

三条检索路径：
- **路径A**：主题 × 高被引（Europe PMC）
- **路径B**：近三年加厚（抵消高被引偏早年）
- **路径C**：指定期刊 × 主题约束（`--journals "刊名1;刊名2"`，可选）
- **路径D1（中文主通道）**：Europe PMC `LANG:"chi"` —— 命中**中华医学会系列 / CSCD / 北大核心**的中文文献（题录为英文翻译，附 PMID，部分附 PMCID）
- **路径D2（中文补充）**：OpenAlex 中文检索 + **核心期刊白名单**过滤

输出 `corpus_raw.json`（含 pmid/pmcid/doi/title/journal/year/cited/lang/source_db 等字段）。

### Step 2：下载全文

```bash
python scripts/pipeline.py download --out <工作目录> [--workers 3] [--limit 10]
```

通道优先级（前一通道失败自动降级）：

| # | 通道 | 说明 |
|---|------|------|
| 1 | Europe PMC render | `europepmc.org/articles/{PMCID}?pdf=render`，对 OA 文章有效 |
| 2 | Semantic Scholar | `openAccessPdf` 字段，常给出出版商 PDF 直链 |
| 3 | Unpaywall | 遍历**全部** `oa_locations`（不止 best） |
| 4 | OpenAlex | 遍历 `locations[].pdf_url` |
| 5 | **网页全文转 PDF** | DOI 落地页 → bs4 提取正文 → PyMuPDF 生成 PDF（对只有 HTML 版的 OA 文章有效） |
| 6 | Europe PMC fullTextUrlList | 兜底直链 |

校验：文件头 `%PDF` 且 > 15KB；网页通道要求正文 ≥ 8000 字符。
输出 `download_results.json`（含 `via` 字段记录获取通道）、`pdf/*.pdf`（文件名=论文标题）。

> 中文核心刊绝大多数为**订阅制**，下载不到属正常，会列入 Excel「待自行下载」表，供机构订阅 / 知网万方 / 文献传递获取。

### Step 3：按标题重命名

```bash
python scripts/pipeline.py rename --out <工作目录>
```

### Step 4：生成 Excel 清单

```bash
python scripts/pipeline.py excel --out <工作目录> [--years 2021-2026]
```

产出 `文献库清单.xlsx`，4 个工作表：
- **全部文献库**：序号 / 标题 / **语种** / 期刊 / 年份 / 类型 / 被引 / DOI / PMID / PMCID / 学科主题 / OA / **来源库** / **期刊等级（中文核心）** / 全文链接 / 下载状态 / 获取方式 / 本地文件
- **待自行下载**：未获取到开放全文的文献（多为订阅制），附 DOI 与链接
- **中文文献**：单独筛出中文语种记录
- **说明**：检索参数、统计、中文核心刊界定依据

### Step 5：中文核心文献补充（重要）

```bash
# 1) 生成中文库检索指引（含可直接粘贴的检索式与导出步骤）
python scripts/pipeline.py guide --out <工作目录> --topic "骨盆骨折出血"

# 2) 用户在知网/万方/SinoMed 检索并导出结果文件后，导入合并
python scripts/pipeline.py import --out <工作目录> --file <导出文件> --db "CNKI 知网"
```

支持的导出格式：**知网 TXT/Excel、RefWorks、EndNote RIS、纯 CSV**（需含标题列）。
`guide` 覆盖三个中文库：**CNKI 知网 / 万方数据 / SinoMed 中国生物医学文献服务系统**。

#### Step 5B：代理库直连下载（知网 / 中华医学会）—— 有账号时优先走这条

若用户已购买中文文献代理库账号（凭据放在 `~/.workbuddy/credentials/cn_proxy.json`），可**直接检索并下载中文全文**，不必再走 `guide`+`import` 半自动路线。

```bash
# 知网：检索并直接下载 PDF（已验证稳定）
python scripts/cn_lit.py dl "热射病 凝血功能" -n 3 -o <工作目录>/pdf_cn

# 知网：只检索（返回 标题/作者/期刊/年份/下载直链）
python scripts/cn_lit.py search "骨盆骨折 出血" -n 20 --src cnki --json cn_hits.json

# 中华医学会：检索并直接下载 PDF（点结果行右侧「下载PDF」按钮）
python scripts/cn_lit.py zh-dl "骨盆骨折 出血" -n 5 -o <工作目录>/pdf_zh

# 中华医学会：只检索
python scripts/cn_lit.py search "骨盆骨折" -n 20 --src zh

# 中华医学会：抓取单篇全文 HTML（需要正文 XML 时用）
python scripts/cn_lit.py zh-html <cmaid> -o <工作目录>/zh_html
```

**通道实测（2026-09 实测，均已出真实 PDF）**

| 库 | 检索 | 下载 | 说明 |
|---|---|---|---|
| **知网 CNKI** | ✅ | ✅ 直接出 PDF | 入口 1/2/3/146 自动切换 |
| **中华医学会**（中华医学期刊全文数据库） | ✅ | ✅ 直接出 PDF | 点结果行右侧的「**下载PDF**」按钮即触发下载；文件名由服务器给出，标题准确 |
| 维普 | ✅ 可访问 | 未验证 | — |
| 万方 | ❌ 入口1 报 500 | — | 可试入口 35 / 36 / 129 |
| PubMed / WoS / ScienceDirect / Springer | ✅ 可访问 | 未验证 | 英文库，一般有更省事的通道 |

**关键要点**

- **中华医学会的正确下载姿势**：搜索结果里**每篇论文右侧有「全文HTML / 下载PDF」两个按钮**（容器 `div.s_searchResult_li_button_r`）。**点「下载PDF」直接触发下载**；点标题只会新开标签页打开文章页（不是下载）。切勿只在标题上找下载入口。
- 下载接口形如 `/apiVue/file/down/<cmaid>/pdf/<uuid>`，由该按钮的 JS 构造并经 `/sf-webproxy/` 代理层取回——**必须由页面内真实点击触发**，不要用裸 HTTP 直接请求（会命中 webvpn 的「安全验证」验证码页）。
- 登录与跳转由 Playwright 驱动系统 Edge 完成。**SPA 的 hash 路由切换不会重挂载组件，必须在 `goto` 后 `reload` 才能触发 `Auth.php` 授权跳转**（`cn_lit.py` 已内置该修复）。
- 知网下载链路：结果行链接 → 代理中间页（标题「文献下载中」）→ 解析出 `docdown.cnki.net/docdown/fulltext/download?q=…` → 取回 `%PDF`。
- 上游 webvpn **偶发 `no_connect` 限流**（会把页面导到路由器页），脚本内置重试；连续失败请稍后重试或换时段。
- 代理库是第三方共享账号，**有并发限制**；请串行、低频下载，避免限流或封卡。
- 凭据只存本机 `~/.workbuddy/credentials/cn_proxy.json`，**不要打进对外分发的 skill 包**。

### Step 6：前沿报告与方向推荐

基于 `corpus_raw.json` 与 `stats` 统计，撰写两份交付：
1. **研究前沿报告** —— 总体范式转变 + 各子方向前沿结论（须引用库内具体文献）
2. **可行研究方向** —— **先询问用户条件**，再给 5–10 条方向，每条含：做什么 / 为何可行 / 优点 / 缺点 / 产出预期

| 条件 | 可推荐 | 避开 |
|---------|-------------|-----------|
| 无实验室、经费 <10 万 | 回顾性队列、区域病种特征、流程 QI、常规指标模型、护理研究 | 基础机制、组学、多中心 RCT |
| 有少量经费、有随访能力 | + PICU/ICU 远期随访、真实世界策略比较、表型聚类 | 大型平台试验 |
| 有特色场景（卫勤/军事/区域） | + 特色场景应急救治研究（差异化最高） | —— |
| 有实验室与团队 | + 机制研究、前瞻队列、外部验证 | —— |

---

## 检索源与通道实测结论（2026-09 实测）

**✅ 可用**

| 通道 | 覆盖 | 是否自动 |
|------|------|---------|
| Europe PMC（英文） | SCI / PubMed 全量 | ✅ 自动 |
| **Europe PMC `LANG:"chi"`** | **中文核心刊（中华系列/CSCD/北大核心）的英文题录** | ✅ 自动 |
| OpenAlex（英文） | 全球文献 | ✅ 自动 |
| OpenAlex（中文 + 白名单） | 中文核心刊覆盖有限，需白名单过滤 | ✅ 自动 |
| Unpaywall / Semantic Scholar | OA 全文直链 | ✅ 自动 |
| 出版商 HTML 全文页（Nature/Frontiers/BMC/BMJ 等） | 网页转 PDF | ✅ 自动 |

**❌ 不可用（已实测，不必再试）**

| 目标 | 结果 |
|------|------|
| NCBI PMC 直连 | Cloudflare 403 |
| MDPI | 403 |
| Europe PMC 文章页（抓正文） | JS 渲染，HTML 无正文 |
| **CNKI 知网** | 官方直连 403 + 强 JS 单页应用，无法自动检索 —— 但**可经代理库账号下载全文**（见 Step 5B） |
| **万方 / 维普 / 中华医学期刊网** | 官方直连为 Vue/Nuxt 单页应用 —— 代理库通道见 Step 5B |
| **SinoMed** | 文档检索需机构登录（重定向 SSO） |
| 百度学术 | 403 |
| 订阅制文献（无 OA、且无代理库权限） | 无合法自动获取途径 |

> **结论**：中文核心文献的**题录**靠「Europe PMC 中文语种通道」自动获取；**全文**有三条路——① **代理库直连下载**（Step 5B，有账号时首选；**知网、中华医学会均已实测下载到真实 PDF**）；② OA 通道（Step 2）；③ `guide` + `import` 半自动路线（无账号时的兜底）。

## 输出结构

```
<工作目录>/
├── corpus_raw.json             检索库（全部元数据）
├── download_results.json       下载结果
├── pdf/                        已下载全文（文件名=论文标题）
├── 文献库清单.xlsx
├── 文献库概览.md               （stats 输出整理）
├── 中文文献检索指引.md          （guide 输出）
└── <方向>研究前沿报告与可行方向.md
```

## 常见问题

| 问题 | 处理 |
|------|------|
| 中文轨道抓到 0 篇 | ① 是否给了 `--keywords` 英文关键词；② Europe PMC 偶发 503 限流，稍后重试；③ 用 `--cn-query` 直接指定英文检索式 |
| 下载成功率低 | ① 非 OA 文章本就下不到；② 确认 `bs4/lxml/pymupdf` 已安装；③ S2 报 429 时降低 `--workers` |
| 中文刊名显示为拼音 | 中文刊在 MEDLINE 中即为罗马化刊名（标准形式），Excel 中「期刊等级」列已标注"中文核心" |
| 想只要中文核心、不要水刊 | 默认已开启白名单过滤；反之加 `--cn-all` |
| 某期刊返回 0 条 | Europe PMC 期刊名需精确匹配，尝试去掉 "The" 或改用简称 |
| 库中混入无关文献 | 收紧 `--keywords`，或提高相关性过滤阈值 |
| 中文全文下不下来 | 有代理库账号 → Step 5B：知网 `cn_lit.py dl`、中华 `cn_lit.py zh-dl`（均可出 PDF）；无账号 → `guide`+`import`、机构订阅或文献传递 |
| 代理库报「打不开知网」 | 入口并发满，`cn_lit.py` 已自动依次切换入口 1/2/3/146；仍失败则稍后重试 / 换时段 |
| 中华医学会下不到 PDF | **要点结果行右侧的「下载PDF」按钮**（点标题只是打开文章页，不会下载）；用 `cn_lit.py zh-dl "<检索词>" -n N -o <目录>` |
| 中华医学会 `no_connect` | 上游 webvpn 限流（会跳到路由器页），脚本自动重试；持续失败请稍后重试 |
| Playwright 报找不到浏览器 | 脚本优先用系统 Edge（`channel="msedge"`）；无 Edge 时执行 `python -m playwright install chromium` |

## 扩展与迁移

- **换专业**：改 `--topic` / `--topics` 即可，无需改代码
- **补中文核心刊**：编辑 `references/cn_journals.json` 的 `journals` 列表（现有 269 本，含《中文核心期刊要目总览》2023 版医药卫生类 + 中华医学会系列）
- **换领域词典**：`TITLE_NOISE`（通用剔除词）在 `scripts/pipeline.py` 顶部
