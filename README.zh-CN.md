# dsh-research-suite（中文说明）

**一句话定位**：面向临床科研人员的 DeepSeek Harness（DSH）插件——论文写作、润色、绘图、统计、科研思路、审稿、PPT、文献、格式全流程，装进 DSH 后**自动接管**科研任务，没有界面、不需要手动挑技能。

- 包名：`dsh-research-suite`　版本：`3.2.0`　许可证：MIT　实测 DSH：`0.2.1-rc.5`、`0.2.2-rc.1`
- 运行环境：Node `^22.19.0 || >=24.0.0`，DSH `>=0.2.0-0 <0.3.0`
- **本插件自包含：450 个源技能全文 + 技能自带的 references/scripts/templates 资产随包分发，运行时不读取任何外部技能目录。**

## 它解决什么问题

科研任务的真实难点不是"缺技能"，而是"同一个任务有 3～8 个技能都能做，各有长处，到底用谁的哪一招"。

v1 的做法是认一个"首选技能"，然后让模型去读那份技能原文照做。三个问题：**机械单选丢掉别人的长处**（中文润色里"去文言腔"最强的、"字数守恒"最严的、"出 Word 精修报告"的往往不是同一个技能）；**选中不等于会用**（技能原文是给人读的说明书，动辄 8～25 KB，照读会漏判据、阈值、模板）；**责任又踢回模型**（给一串技能名，等于让模型自己想怎么组合）。

v2 的答案是**能力卡（capability）**：

> 一张能力卡 = 一件可独立验收的事（"给中文稿去 AI 味并保持字数"、"做倾向评分匹配并出 Love plot"）。
> 卡里把**所有**竞争技能拆成 `best_at`（最擅长的那一招）/ `limits`（明确不做什么）/ `take`（实际搬进协议的规则、阈值、模板），再合成为一条**融合协议**：每一步写清"取自谁、为什么取它、放弃了谁、为什么放弃"。

判据很硬：**读完一张能力卡，不打开任何原始技能原文，也能把这件事做完。** 原文保留在包内作为深读层，是"查细节"用的，不是"照做"用的。所以它**不是技能路由器**：返回的是已经组合好、带阈值和判据的协议，不是一份技能名清单。

## 自动接管是怎么实现的

没有 UI、没有按钮、不需要用户点技能。三件事拼起来：

1. **策略段注入**（`lib/prompt.js` + `lib/index.js`）：插件向 DSH 系统提示注入一段名为 `research-suite/policy`、`order: 650` 的策略（"团队策略之后、工具说明之前"），文本由 `buildPolicy(core)` 每次组装系统提示时现算。策略规定：识别到科研诉求 → **先调 `research_playbook`** → 按能力卡协议执行 → 需要细节再深读 → 交付前 `research_gate` 自检。
2. **11 个技能**（`skills/`）：1 个入口技能 + 10 个域融合 SOP（writing / polish / figures / stats / ideation / review / slides / literature / format / data），注册时**当场内联 `content` 字符串**（不能传 `load()` 之类惰性钩子，否则 DSH 加载期校验不过、技能全丢——这是 v1 的原始故障）。
3. **15 个工具（7 个查询 + 8 个执行/核验/生成/记忆）**：给模型查询能力卡、检索 450 个源技能、读原文与自带资产、读规范、做机械自检的接口。

`research_playbook` 没命中时（任务超出覆盖范围），策略回退到 `research_catalog` 在 450 个源技能里检索再直读原文——**不拒答**。

技术细节见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) §五、§六。

## 10 个能力域

| 域 | 源技能 | 覆盖什么 |
|---|---:|---|
| `writing` | 64 | 按论文类型与章节切分（原创/综述/病例报告/标书…） |
| `polish` | 12 | 语体、去 AI 味、降重、审校、Word 精修报告 |
| `figures` | 33 | 数据图、统计图、机制图、示意图、组合排版 |
| `stats` | 30 | 描述、比较、回归、生存、预测模型、PSM、MR、Meta、缺失、样本量 |
| `ideation` | 37 | 选题、查新、假说、标书、伦理 |
| `review` | 20 | 自审、审稿意见、修回、rebuttal、回复信 |
| `slides` | 37 | 汇报型、讲课型、答辩型、组会型、海报 |
| `literature` | 26 | 检索式、筛选、精读、证据表、查全查准 |
| `format` | 51 | 投稿格式、参考文献、图表规范、投稿包 |
| `data` | 40 | 数据库与组学数据：GEO / TCGA / dbGaP / 基因型与变异库检索、组学数据获取与整理 |
| **合计** | **450** | 10 个能力域共 **103** 张能力卡 |

另有 `toolbox` 域（100 个工具类技能的索引桶）：**只进 `research_catalog` 检索与 `research_kb_read` 深读，不产能力卡**——工具是手段，不是"用户要办的一件事"。

450 个源技能**全部逐条判定过**：每一条都在 `data/ledger/<domain>.json` 里留了判定（`fused` 融进哪张卡的哪一步 / `index-only` 仅编目 / `deprecated` 明确不用 / `out-of-scope` 不属于科研），理由可查，`node scripts/verify-ledger.mjs all` 机械核对覆盖度与"融进去了却不在卡里"。

除正文外，**技能自带资产随包**：186 个技能带来 954 个文件（约 6.8 MB）的 `references/`、`scripts/`、`templates/`，放在 `knowledge/skills/<域>/<slug>__assets/`。模型可用 `research_kb_read(name, asset='scripts/plot.py')` 直接读这些资产（不给 `asset` 时列出该技能带了哪些资产）。

另有 9 份规范文档在 `references/`：中华医学会格式、中文语言风格与好句语料库、Elsevier 英文语言标准、论文类型风格档案、标书硬性规则与 AI 痕迹、IMA 知识库清单、IMA 知识库蒸馏任务书、科研技能索引、科研技能自动调用工作流。

## 15 个工具

| 工具 | 作用 | 调用方式 |
|---|---|---|
| `research_playbook` | **唯一入口**。传用户原话，返回最匹配的 1～3 张能力卡 + 融合协议 + 判据 + 交付物 + 建议深读 | 传 `task`（用户原话） |
| `research_capability` | 展开完整能力卡：成员对比表（best_at/limits/take）、protocol、decide、gates、outputs、kb | 按能力卡 `id` 或按 `domain` |
| `research_catalog` | 在 450 个源技能里检索（名称/描述关键词，可加域过滤；`toolbox` 的 100 个工具类技能也在内），每条附带它收了几个资产 | 传关键词，可选加域过滤 |
| `research_kb_read` | 读单个技能原文或 `INDEX.md`/`FUSION.md`；新增 `asset` 参数可读技能自带的 `scripts/plot.py`、`references/*.md` 等资产，不给 `asset` 时列出该技能附带哪些资产；支持分段，越界路径拒绝 | 传技能名，可选 `asset` / `offset` / `limit` |
| `research_standard` | 读 `references/` 下 9 份规范（列表或全文） | 传文件名；省略则列出 9 份 |
| `research_gate` | 门禁与机械自检：`section` 取 `all` / `data` / `selfcheck` / `mutex` / `forbidden` / `hard` / `handoffs`；`text` 检查标点、引用上标、AI 套话、绝对化措辞 | 传 `section` 或 `text` |
| `research_suite_status` | 装载自检：版本、10 域能力卡数量、450 索引完整性、资产收录统计、references 齐备性、包根路径 | 无参数 |
| `research_run` | **真执行**：把 R 或 Python 脚本写进临时目录并真的跑（Rscript / 本机 Python），返回 stdout/stderr 与产出文件清单；禁 install/rm 类破坏性命令，工作目录限 cwd 或临时目录 | 传 `kind`(r/python) + `code`，可选 `workdir` / `timeoutMs` |
| `research_data_check` | **数据六道闸门的机械部分**：读 CSV/TSV，报行列、缺失率、常量列、ID 重复、不可能值（年龄越界/负数/百分比>100）、EPV<10 | 传 `file`，可选 `outcome` / `predictors` |
| `research_output_check` | **交付物核验**：PNG 实测 DPI（<300 提醒）、PDF 页数与文本层、DOCX/XLSX 结构、CSV 行数、MD 字数 | 传 `files` |
| `research_doi_check` | **文献真实性**：按 DOI 向 Crossref 核验是否存在，返回标题/期刊/年份；网络失败如实降级，不编造 | 传 `dois`（数组或逗号串） |
| `research_ref_audit` | **引用对账**：正文 `[n]` 跳号/重复、与文献表条目数不符、条目缺 DOI、年份可疑、DOI 重复 | 传 `text` 或 `file` |
| `research_project` | **项目记忆**：读写工作区 `.dsh-research/project.json`，记住目标期刊、术语表、已定稿段落、已定决策，跨会话不丢 | 传 `action`（get/set/diff/list） |
| `research_docx` | **产出与审计 docx**：按中文期刊体例生成 .docx（宋体小四、1.5 倍行距、首行缩进、三线表、参考文献悬挂缩进、引用编号上标），或反向审计既有 docx 的排版硬指标 | 传 `action`（build/audit） |
| `research_litsearch` | **真检索**：直接查 PubMed（esearch+esummary，返回 PMID/期刊/年份/作者/DOI），或把 DOI 与作者/卷/期/页逐字段比对 | 传 `action`（pubmed/compare-doi） |

## 安装

完整发布与排障看 [docs/PUBLISH.md](docs/PUBLISH.md)，这里只列最短路径。

**A. 从 npm 装（最省事，已发布 [dsh-research-suite@3.2.0](https://www.npmjs.com/package/dsh-research-suite)）**

```
plugin_manager(action="install_bundle", target="dsh-research-suite@3.2.0")
```

等价 CLI：

```powershell
dsh.cmd plugin --profile desktop add dsh-research-suite@3.2.0
```

**B. 从本地目录装（改源码调试时用）**

```
plugin_manager(action="install_bundle", target="<包的绝对目录>")
```

**C. 从 GitHub 装（npm 上还没发包时）**

```powershell
dsh.cmd plugin --profile desktop add github:xuzhecomeon/dsh-research-suite
```

装完**必须完全退出 DSH Desktop 再启动**（不是关窗口，是退出进程）——loader 只在启动时读补丁层 `cordis.patch.yml`。

验收：让模型调 `research_suite_status`，返回版本、10 域能力卡数量、450 索引完整性、资产收录统计、`references/` 齐备性、包根路径。15 个工具都在、技能计数正确，才算装好。

## 配置项

本插件**不对外导出 Config**：v2.0.0 上线当天就是因为导出了一个 `toJSON()` 返回 JSON Schema 的 Config，被 Host 的 settings 服务当作 schemastery 信封水合，`schema.meta` 为 `undefined`，读 `.volatile` 抛错，DSH Desktop 直接起不来。现在配置由 `apply()` 内的 `validateConfig()` 兜底校验，共 3 个键：

| 键 | 默认 | 作用 |
|---|---|---|
| `autoTakeover` | `true` | 是否注入「科研任务自动接管」策略段。设 `false` 后插件退化为"装了 15 个工具 + 11 个技能"，不再自动接管 |
| `sectionOrder` | `650` | 策略段在系统提示里的排序值。默认落在"团队策略之后、工具说明之前"；需要与其它插件抢位置时改它（合法区间 100–5000，非整数或越界会被配置校验拒绝） |
| `verbose` | `false` | `true` 时把注册/注入失败（技能注册失败、tools 服务缺失、systemPrompt 缺失）写成 warn 日志，排查期必开 |

因此 **DSH 的设置面板里暂时看不到本插件的配置项**（这是刻意取舍，不是遗漏）。要改配置，在 profile 的 `cordis.patch.yml` 里给这个 entry 写 `config:`：

```yaml
- id: dsh-research-suite
  config:
    autoTakeover: true
    sectionOrder: 650
    verbose: false
```

## 能力卡长什么样（节选，完整契约见 [docs/CAPABILITY-SPEC.md](docs/CAPABILITY-SPEC.md)）

```json
{
  "id": "polish.deai",
  "label": "中文去 AI 味与学术润色",
  "summary": "输入中文稿与目标期刊，输出保持字数的学术书面语版本 + 修改说明",
  "triggers": ["润色", "去AI味", "降AI率", "学术化改写", "改得像人写的"],
  "members": [
    {
      "skill": "paper-deweight",
      "verdict": "主用",
      "best_at": ["文言/半文半白腔调识别与还原", "字数守恒（±5%）"],
      "limits": ["只改语言不改结构", "对英文稿无意义"],
      "take": ["第三人称学术书面语替换规则", "文言虚词黑名单", "字数守恒校验流程"]
    }
  ],
  "protocol": [
    {
      "step": "1 立标杆（不立标杆不动笔）",
      "from": "paper-deweight#以标杆为参照 + wb-academic-polish#选刊定位",
      "do": "取 2～3 篇目标期刊近三年同型范文，抽取句长分布、连接词密度、段落首句句式。",
      "detail": "语体指纹至少含：平均句长、每段句数、第一人称出现次数、动词偏好、被动句比例。没有指纹就改稿＝凭感觉改，必然来回拉锯。"
    }
  ],
  "gates": ["字数变动 ≤ ±5%", "未改动任何专业术语/剂量/数值", "文言虚词命中数为 0", "全角标点校验通过"],
  "outputs": [".docx 修改稿", "修改说明表（原句/改句/理由/依据）"],
  "kb": ["paper-deweight", "paper-polisher", "humanizer-zh"]
}
```

字段级硬约束（`id` 全局唯一、`members` 2～6 个、`triggers` 3～10 条、每条 `detail` ≥40 字、`gates` 必须可机械检查等）由 `scripts/verify-capabilities.mjs` 机械校验；技能名必须真在 `knowledge/catalog.json` 里，编造即报错。

## 目录结构

```
dsh-research-suite/
├── package.json            # name/main/type/exports/engines/files + dsh.bundle.patch
├── cordis.patch.yml        # bundle 补丁层：- insert: id/name 两行
├── lib/                    # 运行时（只依赖 node 内置模块）
│   ├── index.js            #   入口：validateConfig、技能注册、systemPrompt 注入、工具注册
│   ├── core.js             #   能力内核：目录加载、能力匹配、资产读取、路径安全读取、文本机械检查
│   ├── tools.js            #   15 个工具
│   └── prompt.js           #   「科研任务自动接管」段文本（buildPolicy）
├── data/
│   ├── capabilities/*.json # 10 个域的能力卡（机器可读契约）
│   ├── capabilities/*.notes.md  # 可选：挖掘记录
│   ├── ledger/*.json       # 450 个源技能的逐条判定账本（fused/index-only/deprecated/out-of-scope）
│   └── gates.json          # 门禁、自检、互斥、禁用、硬规则、交接
├── skills/                 # 11 个技能：1 个入口（research-suite）+ 10 个域 SOP
│   └── research-<domain>.md
├── knowledge/              # 450 个源技能：catalog.json + INDEX.md + FUSION.md + stats.json + skills/<域>/*.md
│   └── skills/<域>/<slug>.md
│       └── <slug>__assets/ # 技能自带的 references/scripts/templates（186 个技能、954 个文件）
├── references/             # 9 份规范（01–09）
├── scripts/
│   ├── verify-capabilities.mjs   # 能力卡契约校验
│   ├── verify-ledger.mjs         # 判定账本校验（覆盖度 + fused 可核）
│   ├── verify-package.mjs        # 发布静态校验（含资产一致性、占位符、知识层一致性）
│   └── selftest.mjs              # 加载期 smoke test（假 ctx 调 apply）
├── docs/
│   ├── CAPABILITY-SPEC.md  # 能力卡内容契约
│   ├── ARCHITECTURE.md     # 模块图、数据流、自动接管实现、v3 知识层与账本
│   ├── PUBLISH.md          # 发布、安装、升级回滚、排障
│   └── ATTRIBUTION.md      # 第三方技能来源与许可
├── icon.svg
├── README.md               # 英文精简版
├── README.zh-CN.md         # 本文件
├── CHANGELOG.md
└── LICENSE
```

## 开发与自检

```powershell
npm test                          # node scripts/selftest.mjs（假 ctx 加载期 smoke test）
npm run verify                    # node scripts/verify-package.mjs（发布静态校验）
npm run verify:caps               # node scripts/verify-capabilities.mjs all（能力卡契约）
node scripts/verify-ledger.mjs all  # 判定账本（11 域 450 条覆盖 + fused 可核）
npm run pack:check                # npm pack --dry-run（看真实发布清单：v3 解包约 38 MB 量级）
```

四条校验都必须 exit 0；CI（`.github/workflows/ci.yml`）在 ubuntu-latest + Node 24 上跑同一套（verify-package → verify-capabilities → verify-ledger → selftest），并额外跑 `npm pack --dry-run`。`publish` job 默认**只能手动触发**（`workflow_dispatch`）：仓库还没配 secret `NPM_TOKEN` 时，打 tag 自动发布会以 401 失败并刷红 Actions，所以 tag 不会触发发布。要恢复「打 `v*` tag 即发 npm」，先在仓库 Settings → Secrets 配好 `NPM_TOKEN`，再把 `publish` job 的 `if` 改回 `startsWith(github.ref, 'refs/tags/v') || github.event_name == 'workflow_dispatch'`（需 `id-token: write`，不写任何明文）。

当前包体（v3 中间态实测，全部域交付后以重跑为准）：**1481 个文件、16.20 MB**（`scripts/verify-package.mjs` 口径，含 `.github/` 等仓库文件），其中 `knowledge/` 的 450 篇原文 + 954 个资产文件占绝大部分——**这是设计如此，不要"优化"掉**。

## 仓库地址

仓库地址已填为 `https://github.com/xuzhecomeon/dsh-research-suite`（`package.json` 的 `repository.url` / `homepage` / `bugs.url` 与两个 README 的徽章同步）。

以后换账号时，改 `package.json` 的 `repository`/`homepage`/`bugs` 与两个 README 的徽章后自查：`Select-String -Path package.json,README.md,README.zh-CN.md -Pattern "your-org"`，零命中才算干净。

## 安全与边界

**执行默认关闭。** 本插件里有真正执行代码的能力（`research_run`），正因为如此它自带一层安全策略：模型生成的脚本按「不可信输入」处理，而不是按「用户自己写的、一定安全」处理。

执行链路是两段式：**预览 → 显式确认（哈希一致）→ 三道闸（开关 / 哈希 / 静态策略）→ 执行**。

- `data/exec-policy.json` 出厂 `run.enabled: false`。此时 `research_run` 只返回预览（脚本前 60 行 + `previewHash` + 策略摘要 + 预计拦截项），**不写文件、不起子进程**。
- 开启执行后，脚本以**你的用户权限**运行在 `<当前工作目录>/.dsh-research/run/<runId>/` 内。静态扫描负责：包白名单（R / Python 各有清单）、拒绝常见联网与子进程 API、写入只允许该目录内相对路径、拒绝 PHI 路径关键词、永久拒绝安装类命令。**这是护栏，不是沙箱**——真正的隔离要靠容器、受限用户或虚拟机。
- `research_doi_check` 确实会联网：只把 DOI 发到 `https://api.crossref.org`，不发送稿件或本地文件内容；其余工具不发网络请求。
- 本插件自包含：450 篇源技能原文与 954 个自带资产随包分发，运行时不读取任何外部技能目录。
- 入口不 import `@deepseek-ai/*`：profile 的 `node_modules` 里解析不到这类包，入口一旦 import 就会整个加载失败（现象是"装了但一个技能都没有"）。这条由 `scripts/verify-package.mjs` 强制拦截。

| 工具 | 读文件 | 写文件 | 联网 | 子进程 | 作用半径 |
| --- | --- | --- | --- | --- | --- |
| `research_playbook` / `research_capability` | 是（能力卡） | 否 | 否 | 否 | 进程内只读 |
| `research_catalog` / `research_kb_read` / `research_standard` | 是（索引、技能原文与资产、规范） | 否 | 否 | 否 | 进程内只读，路径约束在包内 |
| `research_gate` / `research_ref_audit` | 否（只分析传入文本） | 否 | 否 | 否 | 进程内纯文本检查 |
| `research_data_check` / `research_output_check` | 是（调用方指定的数据/交付文件） | 否 | 否 | 否 | 进程内只读 |
| `research_suite_status` | 是（索引、统计、策略） | 否 | 否 | 仅 `where` / `which` 探测解释器 | 进程内 + PATH 探测 |
| `research_doi_check` | 否 | 否 | **是**（Crossref，仅 DOI） | 否 | 外发 DOI 字符串 |
| `research_run` | **是**（解释器以当前用户权限可读的一切） | **是**（执行目录内；越界写被策略拒绝） | 默认 **否** | **是**（Rscript / python） | 执行目录 + 当前用户权限能触达的范围 |

开启执行的最小步骤、完整策略字段、三层隔离建议与已知绕过边界，见 [docs/SECURITY.md](docs/SECURITY.md)。

## 能力边界（诚实版）

外部专家评审指出过「自述能力强、可验证能力弱」，这一节把能做什么、不能做什么写清。

**能做的**

1. **任务识别有闸门**：50 条真人原话的 golden set 上，接管判定 50/50、不该接管的 5 条全部拒绝、能力卡 top3 100%；`node scripts/eval-match.mjs --strict` 可复跑（CI 里也跑）。
2. **真执行（默认关闭）**：`research_run` 会在策略约束下真跑 R（Rscript）或 Python（本机解释器）并回传 stdout/stderr；执行开关默认关，开启要先预览、再带哈希确认，见「安全与边界」。不是让模型「假装跑过」。
3. **数据机械核验**：`research_data_check` 能查缺失率、常量列、ID 重复、不可能值、EPV<10。
4. **交付物核验**：`research_output_check` 读 PNG 真实 DPI（不达标会提醒）、PDF 页数与文本层、DOCX/XLSX 结构。
5. **文献真实性**：`research_doi_check` 向 Crossref 核验 DOI 是否存在；`research_ref_audit` 对账正文 `[n]` 与文献表。

**不能做的（说清比含糊更强）**

1. **不做查重、不做 AIGC 检测**：需要全文上传到外部付费服务，本插件明确不做，也不假装有这能力。
2. **不做统计学的最终判断**：工具只做机械项（缺失、越界、EPV），方法选择、混杂控制、敏感性分析仍要按能力卡协议人工判。
3. **不做文献全文核真**：DOI 能核验「存在」，但论文结论是否被正确引用，必须读原文。
4. **图像审美与期刊偏好**：给的是可核验的数值（DPI、字号、配色），不是「编辑会不会喜欢」。
5. **golden set 规模有限**：50 条为自拟，存在过拟合风险；机制是通用的，但真实语料仍不够多。
6. **依赖宿主接口**：宿主不提供 `tools` / `systemPrompt` 服务时会自动降级（技能仍在、策略段仍在），可用 `research_suite_status` 与策略段里的「装载自检」行确认装载情况。

## 许可

MIT，见 [LICENSE](LICENSE)。

**注意**：MIT 只覆盖插件本体（`lib/`、`data/`、`skills/`、`references/`、`scripts/`、`docs/` 与索引文件）。`knowledge/skills/` 下 450 篇源技能全文与 954 个自带资产是从作者本机技能库逐字打包的第三方材料，各自许可由其原始作者决定，不在 MIT 范围内——对外分发前请先看 [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md)。
