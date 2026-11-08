# 架构（ARCHITECTURE）v3.0.0

本文件只写到**职责边界**层级：说明这个包由哪几块组成、每块的输入输出、以及用户诉求怎么一路走到交付物。具体函数名与内部实现可能随迭代调整，但下面这几条主线（入口装配、能力内核、工具面、自动接管文本、v3 知识层与判定账本）不变。

## 一、执行形态

`dsh-research-suite` 是一个 cordis 插件包，装进 DSH 的 profile 后由 loader 加载。它向 DSH 提供**三种东西**，没有第四种：

| 提供的对象 | 数量 | 作用 |
|---|---|---|
| 工具（`ctx.tool(...)`） | 7 个 | 模型可调用的查询/展开/深读/自检接口 |
| 技能（`ctx.skills.register(...)`） | 11 个 | 模型可读的融合 SOP：1 个入口 + 10 个能力域 |
| 系统提示段（`systemPrompt.section(...)`） | 1 段 | 「科研任务自动接管」策略（`name: research-suite/policy`、`order: 650`），决定模型什么时候、按什么顺序用上面的东西 |

**没有 UI 页面，没有命令面板，没有侧边栏。** 自动触发的唯一机制是系统提示段：DSH 每次组系统提示时把它拼进去，模型据此判定「这是科研任务，先接管」，而不是等用户去点某个技能。

能力域共 **10 个**：writing、polish、figures、stats、ideation、review、slides、literature、format、data。另有一个 **toolbox** 域——它是 100 个工具类技能的索引桶，只进 `research_catalog` 检索与 `research_kb_read` 原文读取，**没有能力卡**（工具不是「一件用户要办的事」）。

## 二、模块图

```
DSH loader
  │  cordis.patch.yml  →  - insert: { id: dsh-research-suite, name: dsh-research-suite }
  │  （缺这两行 → loader 永不 import 入口 → 技能一个都不注册）
  ▼
lib/index.js               入口与装配
  ├─ validateConfig()      配置兜底（autoTakeover / sectionOrder / verbose）——注意：不再导出 Config
  ├─ skills 注册           ctx.skills.register(...) × 11，content 必须当场内联
  ├─ systemPrompt 注入     systemPrompt.section({ name: 'research-suite/policy', order: 650, text: () => buildPolicy(core) })
  └─ 工具注册              ctx.get('tools').register(...) × 7，处理器由 lib/tools.js 提供
        │
        ▼
lib/core.js                能力内核（不依赖 ctx，可单测）
  ├─ 目录加载    knowledge/catalog.json（450 条）、data/capabilities/*.json、data/gates.json、data/ledger/*.json、references/
  ├─ 能力匹配    用户原话 → 打分 → 最匹配的 1～3 张能力卡
  ├─ 资产读取    技能自带的 references/scripts/templates（readAsset / listAssets）
  ├─ 路径安全读取 研究原文 / 规范文件，越界路径拒绝
  └─ 文本机械检查 中文标点、引用上标、AI 套话、绝对化措辞
lib/tools.js               12 个工具：入参校验 + 调用 core + 统一返回格式
lib/prompt.js              「科研任务自动接管」段文本（静态策略 + 运行时域清单）
```

`lib/` 之外全是**数据**，代码只读不写：`data/`（能力卡、门禁、判定账本）、`knowledge/`（450 篇技能原文 + 技能自带资产 + 目录）、`references/`（9 份规范）、`skills/`（11 个域 SOP）。

## 三、七个关注点的职责边界

按关注点拆是七块，落地在四个源文件里；下表是「谁负责什么」，也是分诊问题时该看哪里。

| 关注点 | 落点 | 输入 | 输出 | 明确不做什么 |
|---|---|---|---|---|
| config | `lib/index.js` | DSH 传入的插件 config | 校验过的配置对象（`autoTakeover` / `sectionOrder` / `verbose`） | 不导出 `Config`（见 §5.3）；不读包外路径 |
| catalog | `lib/core.js` | `knowledge/catalog.json`（450 条） | 按域/关键词检索的条目（name/domain/source/file/assets） | 不改写 catalog；不扫 `knowledge/skills/` 做二次索引 |
| capabilities | `lib/core.js` | `data/capabilities/*.json`（10 个域） | 能力卡（成员对比、protocol、decide、gates、outputs、kb） | 不替模型选技能；不把成员技能当可执行体 |
| playbooks | `lib/core.js` | 用户原话（task）+ 能力卡 triggers | 命中排序后的 1～3 张卡 + 协议摘要 | 不产出「推荐技能名清单」当终点（那是 v1 的路由器思路） |
| tools | `lib/tools.js` | 模型给的参数 | 稳定的文本/JSON 返回 | 不写用户文件；不执行外部程序（R/Python 由模型按协议在会话里跑） |
| prompt | `lib/prompt.js` | 域清单、工具清单、接管规则 | 一段中文策略文本 | 不写具体论文内容；不携带 450 篇原文（只带域级摘要） |
| skills | `lib/index.js`（注册装配）＋ `skills/*.md`（内容） | `skills/` 下的 md | DSH 技能目录里的 11 个条目 | 注册时**不传加载钩子**，只传 content 字符串 |

## 四、数据流：从一句诉求到交付物

```
用户："帮我把这段讨论改得像人写的，字数别超"
  │
  ① DSH 组系统提示：内置段 + 本插件「科研任务自动接管」段
  │   该段的判定规则：识别为科研任务 → 先 research_playbook → 按能力卡协议执行 →
  │   交付前 research_gate 自检。不需要用户点名任何技能。
  ▼
  ② research_playbook(task = 用户原话)
  │   能力内核按 triggers 打分，返回 1～3 张最匹配的能力卡：
  │   id / label / summary / 协议步骤摘要 / gates / outputs / 建议深读技能
  ▼
  ③ research_capability(id 或 domain)
  │   展开完整能力卡：成员技能对比表（best_at / limits / take）、protocol 全文、
  │   decide、gates、outputs、kb
  ▼
  ④ 按需下钻（不是必走，卡里细节不够才走）
  │   research_kb_read(name)             → knowledge/skills/<域>/<slug>.md 原文
  │   research_kb_read(name, asset=...)  → 该技能自带的 references/scripts/templates
  │   research_standard(file)            → references/ 下的格式、语体、统计报告规范
  │   research_catalog(keyword)          → 450 个原始技能里还有没有别的可用
  ▼
  ⑤ 模型执行协议，产出交付物（.docx / 图 / 表 / 回复信 …）
  ▼
  ⑥ research_gate(text = 交付正文)
      机械自检：中文语境半角标点、正文引用是否上标、AI 套话词、绝对化措辞
      命中 → 修 → 再交；不通过不交付
```

**兜底分支**：`research_playbook` 没有达到阈值的命中时（例如用户提的是本插件不覆盖的任务），模型改用 `research_catalog` 在 450 个原始技能里检索，再 `research_kb_read` 直读原文——能力卡是加速层，不是唯一通路。这条分支保证了「插件没覆盖的科研任务也不会被拒答」。

## 五、自动接管的实现（最容易写错的四处）

「安装即自动触发」没有任何魔法，只有三条很具体的实现：**往系统提示里插一段策略**、**把技能内容在注册时定死**、**不要对外导出 `Config`**。这三处是翻车过的位置，所以单独写清楚。

### 5.1 策略段：`lib/prompt.js` + `lib/index.js`

`lib/prompt.js` 暴露三个东西：

```js
export const SECTION_NAME = 'research-suite/policy';
export const SECTION_ORDER = 650;
export function buildPolicy(core) { /* 返回策略段文本 */ }
```

`lib/index.js` 在 `apply()` 里把它挂到系统提示上：

```js
const systemPrompt = typeof ctx.get === 'function' ? ctx.get('systemPrompt') : ctx.systemPrompt;
if (systemPrompt && typeof systemPrompt.section === 'function') {
  systemPrompt.section({
    name: SECTION_NAME,            // 'research-suite/policy'
    order: settings.sectionOrder,  // 默认 SECTION_ORDER = 650
    text: () => buildPolicy(core), // 每次组系统提示时现算，不是一次性快照
  });
}
```

几个关键点：

- **`order: 650`** 的位置语义是「团队策略之后、工具说明之前」：前半段（身份与协作规则）先立，后半段（工具清单）后到，本段落在中间起「任务分发」作用。
- **`text` 是函数不是字符串**：DSH 每次组装系统提示都会重新求值，所以能力卡落盘多少、配置改成什么，下一轮对话就反映出来，不需要重启。
- **`buildPolicy(core)` 动态生成**：把 10 个域的能力卡数量、12 个工具名、接管顺序（`research_playbook` → 能力卡协议 → 深读 → `research_gate` 自检）拼进文本。域没落盘时自动省略该域，不会写出「有 10 个域」但实际只有 1 个卡的假话。
- **配置项**（`lib/index.js` 内的 `DEFAULTS` + `validateConfig()`，默认值 `{ autoTakeover: true, sectionOrder: 650, verbose: false }`）：
  - `autoTakeover: false` → 整段不注入，退化成「装了个工具包」，工具和技能仍可用，只是不再自动接管；
  - `sectionOrder` → 覆盖上表的 650，用于和其它插件的策略段抢位置；
  - `verbose: true` → 注册或注入失败时打 warn 日志，排查期必开。

### 5.2 技能：`ctx.skills.register()` 必须当场内联 `content`

```js
ctx.skills.register({
  name: skill.name,
  description: skill.description,
  whenToUse: skill.whenToUse,
  content: skill.text,   // ← 必须是字符串，注册那一刻就定死
  path: skill.file,
  source: 'runtime',
  provider: 'dsh-research-suite',
  invocation: { modelInvocable: true, userInvocable: true },
  resourceBase: { kind: 'directory', path: dirname(skill.file) },
  metadata: { suite: 'dsh-research-suite', version },
});
```

为什么不能传 `load()` 之类的惰性钩子：DSH 的 runtime provider 在解析技能时，`get(candidate)` 会**直接返回注册时传进去的那个对象**交给上层校验，校验要求 `typeof content === 'string'`。传函数进去，校验当场不通过（轻则技能被丢弃，重则加载期抛错，后面的工具与策略段注册全部不执行）。v1 就是这么挂的：现象是「插件装上了，但一个技能都没有」。

### 5.3 配置：不要导出 `Config`，用 `apply()` 内的 `validateConfig()`

v2.0.0 上线当天 DSH Desktop 起不来（`The application could not start`），根因就是 `lib/index.js` 曾对外 `export const Config`：

- 那个 `Config` 是 **Standard Schema**（带 `~standard` 属性）+ `toJSON()` 返回 **JSON Schema**；
- loader 自己的 `resolveConfig()` 确实接受 `~standard`，所以本地看起来一切正常；
- 但 **Host 的 settings 服务**（`settings/describe`）会把 `Config.toJSON()` 的结果当作 **schemastery 信封**，用 `new Schema(json)` 重新水合；
- 拿到的却是 JSON-Schema，`schema.meta` 为 `undefined`，随后读 `.volatile` 抛
  `Cannot read properties of undefined (reading 'volatile')`，启动链断裂。

本插件也无法静态 `import '@deepseek-ai/schemastery'` 来提供正确的信封（pnpm 下按真实路径解析不到，见 §七 第 1 条）。

**现在的做法**：不导出 `Config`；`apply(ctx, config)` 内部用 `validateConfig(config)` 兜底到 `DEFAULTS`，非法值忽略并记 warning。副作用是 **DSH 的 settings 面板里暂时看不到本插件的配置项**——这是刻意取舍，不是遗漏。要改配置，在 profile 的 `cordis.patch.yml` 里给这个 entry 写 `config:` 即可：

```yaml
# D:\nodehome\.dsh\profiles\desktop\cordis.patch.yml（示例，实际以你的 profile 路径为准）
- id: dsh-research-suite
  config:
    autoTakeover: true
    sectionOrder: 650
    verbose: false
```

配套的降级策略（让单点失败不毁掉整体）：

| 失败点 | 行为 |
|---|---|
| 某一份技能注册抛错 | 只 `warn` 该技能，其余技能继续注册 |
| `tools` 服务晚到或取不到 | 先 `warn`，再用 `ctx.inject(['tools'], cb)` 建子 fiber 延迟补装；技能与策略段不受影响 |
| `systemPrompt` 服务晚到或取不到 | 同样延迟补装；工具与技能不受影响 |
| `autoTakeover: false` | 主动不注入策略段（用户选择） |

这几条「部分可用」比「全有或全无」重要：DSH 插件加载期任何未捕获异常都会让整个包失效。

### 5.4 服务依赖：`tools` 必须写进 `inject`（0.2.2-rc.1 工具丢失事故）

升级到 **0.2.2-rc.1** 后出现过一个极隐蔽的故障：10 份技能正常、自动接管策略段正常、日志里也只有一条默认进不了日志文件的 `warn`，但 **7 个 `research_*` 工具一个都没注册**——模型这边看到的现象是「插件在工作，但 `research_playbook` 不存在」。

根因是**服务装配时序**：入口原本写 `export const inject = ['skills']`，工具在 `apply()` 里用同步 `ctx.get('tools')` 现取。0.2.2-rc.1 的 `tools` 服务在 apply 执行那一刻还没就绪，`ctx.get` 返回 `undefined`，于是工具全丢而其余部分照装。

两类写法的区别（cordis 语义）：

| 写法 | 语义 | 适用 |
|---|---|---|
| `export const inject = ['skills', 'tools']` | **必需依赖**：cordis 等到这些服务就绪才执行 `apply` | 缺了它就等于插件没意义的能力（技能、工具） |
| `ctx.get('name')` / `ctx.inject(['name'], cb)` | 可选依赖：现在没有就跳过，或建子 fiber 等它出现再补装 | 有更好、没有也能用的能力（`systemPrompt`） |

现行实现（`lib/index.js`）：

```js
export const inject = ['skills', 'tools'];          // 两个硬依赖

const tools = readService(ctx, 'tools');            // 先试 ctx.tools，再试 ctx.get('tools')，各自 try/catch
if (!installTools(tools, 'apply 同步阶段未拿到服务') && typeof ctx.inject === 'function') {
  ctx.inject(['tools'], (scope) => installTools(readService(scope, 'tools'), '延迟注入阶段'));
}
```

`readService(ctx, name)` 把「属性访问」与 `ctx.get()` 两条路各自包了 try/catch：某些 cordis 版本访问未就绪的服务**属性**会抛错，不能让一次取服务把已经成功的技能注册掀翻。

对应的回归防线写在 `scripts/selftest.mjs` 的 2b 节：构造一个 apply 时没有 `tools` / `systemPrompt` 的假 ctx，断言四件事——技能仍全部注册、申请了延迟注入且依赖里含 `tools` 与 `systemPrompt`、触发延迟回调后工具数回到 7、策略段数回到 1。

## 六、v3 知识层与判定账本

v3 的核心变化是**知识层从「719 篇原文 + 域标签」升级为「450 条逐条判定过的源技能 + 自带资产」**。为了让「择优录取」这件主观判断可审计，多了一个账本层。

### 6.1 catalog：450 条源技能索引

`knowledge/catalog.json` 是顶层数组，每条一个源技能：

| 字段 | 含义 |
|---|---|
| `name` | 调用名（能力卡 `members[].skill`、账本 `fused` 核对都用它） |
| `dir` | 源技能目录名（账本按 `dir` 逐条对账，是**唯一键**） |
| `slug` | 包内文件名（`knowledge/skills/<domain>/<slug>.md`；资产目录 `knowledge/skills/<domain>/<slug>__assets/`） |
| `domain` | 能力域（10 个 + `toolbox`） |
| `source` | `user`（用户级，563 条）或 `builtin`（插件内置，29 条） |
| `category` | 更细的主题分类（如「生物信息·组学·医药数据库」） |
| `layer` | 收录层级（如「A 索引收录（08/09 权威清单）」） |
| `bytes` | 技能正文 `SKILL.md` 字节数 |
| `file` | 正文路径，相对 `knowledge/`（`skills/<domain>/<slug>.md`） |
| `description` | 技能自述（截断到 260 字符） |
| `whenToUse` | 何时用（可能为空字符串） |
| `assets` | 自带资产：`{ included, files, bytes }`；未收录时是 `{ included: false, wouldBe }` |

### 6.2 资产目录约定：`<slug>__assets/`

源技能常自带 `references/`、`scripts/`、`templates/`——v2 只收了正文，这些用不上。v3 把可执行的与可引用的资产一起分发：

- **目录**：`knowledge/skills/<domain>/<slug>__assets/`，内部保留源技能里的相对路径（如 `scripts/plot.py`、`references/faq.md`）；
- **只收白名单扩展名**（`.md .py .r .sh .mjs .js .json .csv .txt .yml .yaml .tex .bib .ipynb .html .css .Rmd .qmd` 等文本/代码类），二进制、模型权重、数据转储一律不收；
- **单文件 ≤ 256 KB**，超过的跳过（多为数据转储/日志）；
- **用户级技能整包 ≤ 260 KB 才完整收录**，**插件内置技能 ≤ 5 MB**；超预算的整包丢弃，记 `included: false` + `wouldBe`（当前 46 个源技能因此未收录资产；另有 95 个本来就没有资产）；
- 当前实测：**186 个技能带资产、共 954 个文件、约 6.8 MB**，目录/文件数/字节与 catalog 逐条一致（`scripts/verify-package.mjs` 会校验这一点）。

模型侧通过 `research_kb_read(name, asset='scripts/plot.py')` 读单个资产；不给 `asset` 时列出该技能带了哪些资产。

### 6.3 判定账本：`data/ledger/<domain>.json`

450 个源技能**每一个**都必须在账本里有一条判定，四类语义：

| verdict | 语义 | 对能力卡的要求 |
|---|---|---|
| `fused` | 长处被拆进能力卡协议（成员/O 步骤的来源） | `cards` 必填，且每张卡 `members[].skill` 必须含该技能 |
| `index-only` | 只编目、供 `research_catalog` + `research_kb_read` 检索；不进任何卡 | `cards` 必须为空 |
| `deprecated` | 有明确缺陷/与发布边界冲突，登记在册并写明为什么不用 | `cards` 必须为空 |
| `out-of-scope` | 不属于科研场景（工程/生活类），排除在融合之外 | `cards` 必须为空 |

条目契约：`{ dir, name?, verdict, why, cards? }`——`dir` 对应 catalog 的 `dir`，`why` 是判定理由（至少 4 字）。账本只做**判定记录**，不参与运行时检索：运行时仍以能力卡为第一入口。

### 6.4 账本怎么被校验

`scripts/verify-ledger.mjs <domain|all>`（CI 必跑）：

1. **覆盖度**：源清单默认取包内 `knowledge/catalog.json`（该域 `dir` 集合，共 450 条），账本必须一条不多一条不少；缺一条即 ERROR 并列出前 6 个。`--src=<本地分析目录>` 只是本地核对构建输入的可选覆盖，**CI 不传**（保证可在 GitHub Actions 上跑）。
2. **判定合法性**：`verdict` ∈ 四类；`why` 非空且 ≥4 字；非 `fused` 却写了 `cards` 只警告。
3. **fused 可核**：`cards` 里每张卡必须真实存在于 `data/capabilities/<domain>.json`，且该卡 `members[].skill` 含该技能 `name`——防止「账本说融进去了，卡里却没有」。

## 七、数据面

| 路径 | 内容 | 谁写 | 运行时怎么用 |
|---|---|---|---|
| `data/capabilities/<domain>.json` | 10 个域的能力卡（机器可读契约） | 内容作者，受 `docs/CAPABILITY-SPEC.md` 约束 | `research_playbook` / `research_capability` 加载 |
| `data/ledger/<domain>.json` | 450 条源技能的判定账本（可审计证据） | 内容作者 | 不参与运行时；`verify-ledger.mjs` 与审计用 |
| `data/gates.json` | 门禁、自检、互斥、禁用、硬规则 | 主控维护 | `research_gate` 的 `section` 参数 |
| `knowledge/catalog.json` | 450 条技能索引（name/dir/slug/domain/source/file/assets） | 构建期生成 | `research_catalog`、能力卡的技能名对账、账本源清单 |
| `knowledge/skills/<域>/<slug>.md` | 450 篇原始技能全文 | 随包分发 | `research_kb_read` 深读 |
| `knowledge/skills/<域>/<slug>__assets/` | 技能自带 references/scripts/templates（954 个文件） | 随包分发 | `research_kb_read(name, asset=...)` |
| `knowledge/INDEX.md`、`knowledge/FUSION.md` | 总索引与融合说明 | 随包分发 | `research_kb_read` 可读 |
| `references/01–09` | 格式、语体、统计、图件、标书、知识库等规范 | 随包分发 | `research_standard` |
| `skills/*.md` | 11 个域 SOP（1 入口 + 10 域） | 内容作者 | 装进 DSH 技能目录，模型按需读 |

## 八、四条不可退让的契约

这四条各自都能让插件「装上但完全不工作」，所以写死进静态校验（`scripts/verify-package.mjs`）：

1. **入口不得 import `@deepseek-ai/*`**。静态 `import ... from '@deepseek-ai/...'`、动态 `import('@deepseek-ai/...')`、`require('@deepseek-ai/...')` 一律禁止。原因：插件在自己的目录下解析依赖，profile 的 `node_modules` 里解析不到这些包，入口 import 一抛错，后面的技能注册全部不执行——现象是「装了，但一个技能都没有」。
2. **`ctx.skills.register()` 必须当场传 `content` 字符串**（展开见 §5.2）。原因：runtime provider 的 `get(candidate)` 直接返回注册对象，校验要求 `typeof content === 'string'`；传惰性钩子会在加载期抛错，后面的注册全部不执行（v1 的原始故障）。
3. **不要对外 `export const Config`**（展开见 §5.3）。Host 的 settings 服务会把 `toJSON()` 结果当 schemastery 信封水合，JSON-Schema 会在 `.meta` 上崩掉整个 Desktop 启动；配置改用 `apply()` 内的 `validateConfig()` 兜底。
4. **`cordis.patch.yml` 必须有 `- insert:` 列表，且列表里有 `- id:` 与 `- name:` 两行**（值都是 `dsh-research-suite`），`package.json` 的 `dsh.bundle.patch` 必须指向该文件。缺任一条件，loader 永不 import 入口。

另有两条「发布前必须全绿」的机械门：`scripts/verify-capabilities.mjs`（能力卡契约）、`scripts/verify-ledger.mjs`（账本覆盖与 fused 可核）。

## 九、明确不做的事

- **不做技能路由器**：不返回「推荐技能名」作为终点。能力卡里成员技能名只出现在「账本」（谁的长处被搬进哪一步）里。
- **不做 UI**：不注册页面、侧栏、命令面板；settings 面板里也刻意没有配置项（§5.3）。
- **不联网**：运行时只依赖 node 内置模块；不请求任何远程服务。
- **不读外部技能目录**：450 篇原文与 954 个资产随包分发，不读用户机器的 `skills-library` 或别的插件目录。
- **不写用户文件**：12 个工具当前都是只读查询/展开/深读/自检；若后续引入写盘工具，需同步回改本文与 `docs/PUBLISH.md` 的安全说明。

---

相关文档：内容契约见 `docs/CAPABILITY-SPEC.md`，发布与排障见 `docs/PUBLISH.md`，对外介绍见 `README.md`。

## 七、执行与核验层（v3.1 新增）

`lib/verify.js`（981 行，纯 Node、零第三方依赖、不 import 任何 `@deepseek-ai/*`）由 `createVerify(core, options)` 工厂返回五个 async 方法，`lib/tools.js` 只是把它们包成 ToolDefinition：

| 方法 | 底层动作 | 失败时怎么返回 |
|---|---|---|
| `runScript({kind:'r'|'python', code, workdir, timeoutMs})` | `spawnSync` 调 `Rscript.exe` 或本机 `python.exe`，写脚本到 workdir，清 `LC_ALL/LANG/LANGUAGE` | `runtime_missing` / `spawn_blocked`（宿主沙箱 EPERM）/ `dangerous_code` / `workdir_outside` / `bad_kind`，**从不抛异常** |
| `checkData({file, outcome, predictors})` | 自实现 CSV/TSV 解析 + 六道闸门的机械项 | 读不到文件返回 `error`，不猜数据 |
| `checkOutputs({files})` | PNG IHDR+pHYs 读实测 DPI；PDF 页数/文本层；DOCX/XLSX 最小 zip 结构 | 逐文件报 `ok/level/message` |
| `checkDois({dois})` | Crossref `api.crossref.org/works/<doi>`，5 秒超时 | `network` / `not_found` / `http_<code>` 降级返回 |
| `auditRefs({text})` | 先切掉文献表，再统计正文 `[n]` 与文献条目对账 | 跳号/重复/缺 DOI/年份可疑 |

设计要点：

1. **工具层不伪造执行**：`research_run` 的返回值里有 `command`、`exitCode`、`stdout`、`stderr`、`files`，模型无法把「没跑」说成「跑了」。
2. **不做破坏性动作**：脚本内容命中 `install`/`rm` 类模式直接拒绝；workdir 必须在 cwd 或系统临时目录内。
3. **网络失败必须诚实**：DOI 核验失败时返回 `ok:false, error:'network'`，绝不编造「核验通过」。
