# dsh-research-suite（中文说明）

**一句话定位**：面向临床科研人员的 DeepSeek Harness（DSH）插件——论文写作、润色、绘图、统计、科研思路、审稿、PPT、文献、格式全流程，装进 DSH 后**自动接管**科研任务，没有界面、不需要手动挑技能。

- 包名：`dsh-research-suite`　版本：`2.0.0`　许可证：MIT
- 运行环境：Node `^22.19.0 || >=24.0.0`，DSH `>=0.2.0-0 <0.3.0`
- **本插件自包含：719 个原始技能全文随包分发，运行时不读取任何外部技能目录。**

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
2. **10 个技能**（`skills/`）：1 个入口技能 + 9 个域融合 SOP，注册时**当场内联 `content` 字符串**（不能传 `load()` 之类惰性钩子，否则 DSH 加载期校验不过、技能全丢——这是 v1 的原始故障）。
3. **7 个只读工具**：给模型查询能力卡、检索 719 个原始技能、读原文与规范、做机械自检的接口。

`research_playbook` 没命中时（任务超出覆盖范围），策略回退到 `research_catalog` 在 719 个原始技能里检索再直读原文——**不拒答**。

技术细节见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) §五。

## 9 个能力域

| 域 | 技能池 | 能力卡 | 覆盖什么 |
|---|---:|---:|---|
| `writing` | 51 | 11 | 按论文类型与章节切分（原创/综述/病例报告/标书…） |
| `polish` | 24 | 5 | 语体、去 AI 味、降重、审校、Word 精修报告 |
| `figures` | 76 | 9 | 数据图、统计图、机制图、示意图、组合排版 |
| `stats` | 180 | 16 | 描述、比较、回归、生存、预测模型、PSM、MR、Meta、缺失、样本量 |
| `ideation` | 33 | 7 | 选题、查新、假说、标书、伦理 |
| `review` | 39 | 8 | 自审、审稿意见、修回、rebuttal、回复信 |
| `slides` | 44 | 7 | 汇报型、讲课型、答辩型、组会型、海报 |
| `literature` | 152 | 11 | 检索式、筛选、精读、证据表、查全查准 |
| `format` | 32 | 7 | 投稿格式、参考文献、图表规范、投稿包 |
| **合计** | **631** | **81** | 9 域共 81 张能力卡（177 个技能被正式引用，其余 542 个仅编目待检索） |

9 域共 631 个技能，加上 `general` 88 个通用技能，合计 **719 个原始技能全文**（约 9.9 MB）随包分发。另有 9 份规范文档在 `references/`：中华医学会格式、中文语言风格与好句语料库、Elsevier 英文语言标准、论文类型风格档案、标书硬性规则与 AI 痕迹、IMA 知识库清单、IMA 知识库蒸馏任务书、科研技能索引、科研技能自动调用工作流。

## 7 个工具

| 工具 | 作用 | 调用方式 |
|---|---|---|
| `research_playbook` | **唯一入口**。传用户原话，返回最匹配的 1～3 张能力卡 + 融合协议 + 判据 + 交付物 + 建议深读 | 传 `task`（用户原话） |
| `research_capability` | 展开完整能力卡：成员对比表（best_at/limits/take）、protocol、decide、gates、outputs、kb | 按能力卡 `id` 或按 `domain` |
| `research_catalog` | 在 719 个原始技能里检索（名称/描述关键词，可加域过滤） | 传关键词，可选加域过滤 |
| `research_kb_read` | 读单个技能原文或 `INDEX.md`/`FUSION.md`，支持分段，越界路径拒绝 | 传技能名或索引文件名，可选 `offset`/`limit` |
| `research_standard` | 读 `references/` 下 9 份规范（列表或全文） | 传文件名；省略则列出 9 份 |
| `research_gate` | 门禁与机械自检：`section` 取 `all` / `data` / `selfcheck` / `mutex` / `forbidden` / `hard` / `handoffs`；`text` 检查标点、引用上标、AI 套话、绝对化措辞 | 传 `section` 或 `text` |
| `research_suite_status` | 装载自检：版本、9 域能力卡数量、719 索引完整性、references 齐备性、包根路径 | 无参数 |

## 安装

完整发布与排障看 [docs/PUBLISH.md](docs/PUBLISH.md)，这里只列最短路径。

**A. plugin_manager（GUI，推荐）**

```
plugin_manager(action="install_bundle", target="<包的绝对目录>")
```

也可以从 npm 装：`target` 传 `dsh-research-suite@2.0.0`。

**B. CLI**

```powershell
# Windows
dsh.cmd plugin --profile desktop add <包的绝对目录或包名>
# POSIX shell
dsh plugin --profile desktop add <包的绝对目录或包名>
```

装完**必须完全退出 DSH Desktop 再启动**（不是关窗口，是退出进程）——loader 只在启动时读补丁层 `cordis.patch.yml`。

验收：让模型调 `research_suite_status`，返回版本、9 域能力卡数量、719 索引完整性、`references/` 齐备性、包根路径。7 个工具都在、技能计数正确，才算装好。

## 配置项

插件 Config schema 提供 3 个键（默认值见下）：

| 键 | 默认 | 作用 |
|---|---|---|
| `autoTakeover` | `true` | 是否注入「科研任务自动接管」策略段。设 `false` 后插件退化为"装了 7 个工具 + 10 个技能"，不再自动接管 |
| `sectionOrder` | `650` | 策略段在系统提示里的排序值。默认落在"团队策略之后、工具说明之前"；需要与其它插件抢位置时改它（合法区间 100–5000，非整数或越界会被配置校验拒绝） |
| `verbose` | `false` | `true` 时把注册/注入失败（技能注册失败、tools 服务缺失、systemPrompt 缺失）写成 warn 日志，排查期必开 |

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
│   ├── index.js            #   入口：Config、技能注册、systemPrompt 注入、工具注册
│   ├── core.js             #   能力内核：目录加载、能力匹配、路径安全读取、文本机械检查
│   ├── tools.js            #   7 个工具
│   └── prompt.js           #   「科研任务自动接管」段文本（buildPolicy）
├── data/
│   ├── capabilities/*.json # 9 个域的能力卡（机器可读契约）
│   ├── capabilities/*.notes.md  # 可选：挖掘记录
│   └── gates.json          # 门禁、自检、互斥、禁用、硬规则、交接
├── skills/                 # 10 个技能：1 个入口（research-suite）+ 9 个域 SOP
│   └── research-<domain>.md
├── knowledge/              # 719 篇原始技能全文 + catalog.json + INDEX.md + FUSION.md + stats.json
│   └── skills/<域>/*.md
├── references/             # 9 份规范（01–09）
├── scripts/
│   ├── verify-capabilities.mjs   # 能力卡契约校验
│   ├── verify-package.mjs        # 发布静态校验
│   └── selftest.mjs              # 加载期 smoke test（假 ctx 调 apply）
├── docs/
│   ├── CAPABILITY-SPEC.md  # 能力卡内容契约
│   ├── ARCHITECTURE.md     # 模块图、数据流、自动接管实现
│   └── PUBLISH.md          # 发布、安装、升级回滚、排障
├── icon.svg
├── README.md               # 英文精简版
├── README.zh-CN.md         # 本文件
├── CHANGELOG.md
└── LICENSE
```

## 开发与自检

```powershell
npm test                 # node scripts/selftest.mjs（假 ctx 加载期 smoke test）
npm run verify           # node scripts/verify-package.mjs（发布静态校验）
npm run verify:caps      # node scripts/verify-capabilities.mjs all（能力卡契约）
npm run pack:check       # npm pack --dry-run（看真实发布清单：约 11–12 MB 解包、tarball 约 4 MB，属预期）
```

三条脚本都必须 exit 0；CI（`.github/workflows/ci.yml`）在 ubuntu-latest + Node 24 上跑同一套，并额外跑 `npm pack --dry-run`。`publish` job 默认**只能手动触发**（`workflow_dispatch`）：仓库还没配 secret `NPM_TOKEN` 时，打 tag 自动发布会以 401 失败并刷红 Actions，所以 tag 不会触发发布。要恢复「打 `v*` tag 即发 npm」，先在仓库 Settings → Secrets 配好 `NPM_TOKEN`，再把 `publish` job 的 `if` 改回 `startsWith(github.ref, 'refs/tags/v') || github.event_name == 'workflow_dispatch'`（需 `id-token: write`，不写任何明文）。

当前包实测（2.0.0 发布候选）：**773 个文件、11.24 MB**（`scripts/verify-package.mjs` 口径，含 `.github/` 等仓库文件；其中 `knowledge/` 占绝大部分），`npm pack --dry-run` 实际打包 **771 个文件、解包 11.8 MB、tarball 4.1 MB**。

## 仓库地址

仓库地址已填为 `https://github.com/xuzhecomeon/dsh-research-suite`（`package.json` 的 `repository.url` / `homepage` / `bugs.url` 与两个 README 的徽章同步）。

以后换账号时，改这 3 处后自查：`Select-String -Path package.json,README.md,README.zh-CN.md -Pattern "your-org"`，零命中才算干净。
## 安全与边界

- **不联网**：运行时只依赖 node 内置模块，不请求任何远程服务。
- **不读外部技能目录**：719 篇原文随包分发，不碰用户机器的其它技能库。
- **不写用户文件**：7 个工具都是只读查询、展开与机械自检。
- **入口不 import `@deepseek-ai/*`**：profile 的 `node_modules` 里解析不到这类包，入口一旦 import 就会整个加载失败（现象是"装了但一个技能都没有"）。这条由 `scripts/verify-package.mjs` 强制拦截。

## 许可

MIT，见 [LICENSE](LICENSE)。

**注意**：MIT 只覆盖插件本体（`lib/`、`data/capabilities/`、`skills/`、`references/`、`scripts/`、`docs/` 与索引文件）。`knowledge/skills/` 下 719 篇技能原文是从作者本机技能库逐字打包的第三方材料，各自许可由其原始作者决定，不在 MIT 范围内——对外分发前请先看 [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md)。
