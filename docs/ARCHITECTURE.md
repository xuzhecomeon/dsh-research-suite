# 架构（ARCHITECTURE）v2.0.0

本文件只写到**职责边界**层级：说明这个包由哪几块组成、每块的输入输出、以及用户诉求怎么一路走到交付物。具体函数名与内部实现可能随迭代调整，但下面这四条主线（入口装配、能力内核、工具面、自动接管文本）不变。

## 一、执行形态

`dsh-research-suite` 是一个 cordis 插件包，装进 DSH 的 profile 后由 loader 加载。它向 DSH 提供**三种东西**，没有第四种：

| 提供的对象 | 数量 | 作用 |
|---|---|---|
| 工具（`ctx.tool(...)`） | 7 个 | 模型可调用的查询/展开/自检接口 |
| 技能（`ctx.skills.register(...)`） | 10 个 | 模型可读的融合 SOP：1 个入口 + 9 个域 |
| 系统提示段（`systemPrompt.section(...)`） | 1 段 | 「科研任务自动接管」策略（`name: research-suite/policy`、`order: 650`），决定模型什么时候、按什么顺序用上面的东西 |

**没有 UI 页面，没有命令面板，没有侧边栏。** 自动触发的唯一机制是系统提示段：DSH 每次组系统提示时把它拼进去，模型据此判定"这是科研任务，先接管"，而不是等用户去点某个技能。

## 二、模块图

```
DSH loader
  │  cordis.patch.yml  →  - insert: { id: dsh-research-suite, name: dsh-research-suite }
  │  （缺这两行 → loader 永不 import 入口 → 技能一个都不注册）
  ▼
lib/index.js               入口与装配
  ├─ Config                插件配置项（autoTakeover / sectionOrder / verbose）
  ├─ skills 注册           ctx.skills.register(...) × 10，content 必须当场内联
  ├─ systemPrompt 注入     systemPrompt.section({ name: 'research-suite/policy', order: 650, text: () => buildPolicy(core) })
  └─ 工具注册              ctx.get('tools').register(...) × 7，处理器由 lib/tools.js 提供
        │
        ▼
lib/core.js                能力内核（不依赖 ctx，可单测）
  ├─ 目录加载    knowledge/catalog.json、data/capabilities/*.json、data/gates.json、references/
  ├─ 能力匹配    用户原话 → 打分 → 最匹配的 1～3 张能力卡
  ├─ 路径安全读取 研究原文 / 规范文件，越界路径拒绝
  └─ 文本机械检查 中文标点、引用上标、AI 套话、绝对化措辞
lib/tools.js               7 个工具：入参校验 + 调用 core + 统一返回格式
lib/prompt.js              「科研任务自动接管」段文本（静态策略 + 运行时域清单）
```

`lib/` 之外全是**数据**，代码只读不写：`data/`（能力卡与门禁）、`knowledge/`（719 篇技能原文 + 目录）、`references/`（9 份规范）、`skills/`（10 个域 SOP）。

## 三、七个关注点的职责边界

按关注点拆是七块，落地在四个源文件里；下表是"谁负责什么"，也是分诊问题时该看哪里。

| 关注点 | 落点 | 输入 | 输出 | 明确不做什么 |
|---|---|---|---|---|
| config | `lib/index.js` | DSH 传入的插件 config | 校验过的配置对象（`autoTakeover` / `sectionOrder` / `verbose`） | 不做业务逻辑；不读包外路径 |
| catalog | `lib/core.js` | `knowledge/catalog.json`（719 条） | 按域/关键词检索的条目（name/domain/bytes/file） | 不改写 catalog；不扫 `knowledge/skills/` 做二次索引 |
| capabilities | `lib/core.js` | `data/capabilities/*.json`（9 个域） | 能力卡（成员对比、protocol、decide、gates、outputs、kb） | 不替模型选技能；不把成员技能当可执行体 |
| playbooks | `lib/core.js` | 用户原话（task）+ 能力卡 triggers | 命中排序后的 1～3 张卡 + 协议摘要 | 不产出"推荐技能名清单"当终点（那是 v1 的路由器思路） |
| tools | `lib/tools.js` | 模型给的参数 | 稳定的文本/JSON 返回 | 不写用户文件；不执行外部程序（R/Python 由模型按协议在会话里跑） |
| prompt | `lib/prompt.js` | 域清单、工具清单、接管规则 | 一段中文策略文本 | 不写具体论文内容；不携带 719 篇原文（只带域级摘要） |
| skills | `lib/index.js`（注册装配）＋ `skills/*.md`（内容） | `skills/` 下的 md | DSH 技能目录里的 10 个条目 | 注册时**不传加载钩子**，只传 content 字符串 |

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
  │   research_kb_read(skill)      → knowledge/skills/<域>/<slug>.md 原文，分段读
  │   research_standard(file)      → references/ 下的格式、语体、统计报告规范
  │   research_catalog(keyword)    → 719 个原始技能里还有没有别的可用
  ▼
  ⑤ 模型执行协议，产出交付物（.docx / 图 / 表 / 回复信 …）
  ▼
  ⑥ research_gate(text = 交付正文)
      机械自检：中文语境半角标点、正文引用是否上标、AI 套话词、绝对化措辞
      命中 → 修 → 再交；不通过不交付
```

**兜底分支**：`research_playbook` 没有达到阈值的命中时（例如用户提的是本插件不覆盖的任务），模型改用 `research_catalog` 在 719 个原始技能里检索，再 `research_kb_read` 直读原文——能力卡是加速层，不是唯一通路。这条分支保证了"插件没覆盖的科研任务也不会被拒答"。

## 五、自动接管的实现（最容易写错的两处）

"安装即自动触发"没有任何魔法，只有两条很具体的实现：**往系统提示里插一段策略**，以及**把技能内容在注册时定死**。这两处是 v1 翻车的地方，所以单独写清楚。

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

- **`order: 650`** 的位置语义是"团队策略之后、工具说明之前"：前半段（身份与协作规则）先立，后半段（工具清单）后到，本段落在中间起"任务分发"作用。
- **`text` 是函数不是字符串**：DSH 每次组装系统提示都会重新求值，所以能力卡落盘多少、配置改成什么，下一轮对话就反映出来，不需要重启。
- **`buildPolicy(core)` 动态生成**：把 9 个域的能力卡数量、7 个工具名、接管顺序（`research_playbook` → 能力卡协议 → 深读 → `research_gate` 自检）拼进文本。域没落盘时自动省略该域，不会写出"有 9 个域"但实际只有 1 个卡的假话。
- **配置项**（`lib/index.js` 的 Config schema，默认值 `{ autoTakeover: true, sectionOrder: 650, verbose: false }`）：
  - `autoTakeover: false` → 整段不注入，退化成"装了个工具包"，工具和技能仍可用，只是不再自动接管；
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

为什么不能传 `load()` 之类的惰性钩子：DSH 的 runtime provider 在解析技能时，`get(candidate)` 会**直接返回注册时传进去的那个对象**交给上层校验，校验要求 `typeof content === 'string'`。传函数进去，校验当场不通过（轻则技能被丢弃，重则加载期抛错，后面的工具与策略段注册全部不执行）。v1 就是这么挂的：现象是"插件装上了，但一个技能都没有"。

配套的降级策略（让单点失败不毁掉整体）：

| 失败点 | 行为 |
|---|---|
| 某一份技能注册抛错 | 只 `warn` 该技能，其余技能继续注册 |
| `tools` 服务不存在 | 只跳过 7 个工具注册，技能与策略段仍生效 |
| `systemPrompt` 服务不存在 | 只跳过策略段注入，工具与技能仍可用 |
| `autoTakeover: false` | 主动不注入策略段（用户选择） |

这三条"部分可用"比"全有或全无"重要：DSH 插件加载期任何未捕获异常都会让整个包失效。

## 六、数据面

| 路径 | 内容 | 谁写 | 运行时怎么用 |
|---|---|---|---|
| `data/capabilities/<domain>.json` | 9 个域的能力卡（机器可读契约） | 内容作者，受 `docs/CAPABILITY-SPEC.md` 约束 | `research_playbook` / `research_capability` 加载 |
| `data/gates.json` | 门禁、自检、互斥、禁用、硬规则 | 主控维护 | `research_gate` 的 `section` 参数 |
| `knowledge/catalog.json` | 719 条技能索引（name/domain/bytes/file） | 构建期生成 | `research_catalog`、能力卡的技能名对账 |
| `knowledge/skills/<域>/*.md` | 719 篇原始技能全文（约 10 MB） | 随包分发 | `research_kb_read` 深读 |
| `knowledge/INDEX.md`、`knowledge/FUSION.md` | 总索引与融合说明 | 随包分发 | `research_kb_read` 可读 |
| `references/01–09` | 格式、语体、统计、图件、标书、知识库等规范 | 随包分发 | `research_standard` |
| `skills/*.md` | 10 个域 SOP（1 入口 + 9 域） | 内容作者 | 装进 DSH 技能目录，模型按需读 |

## 七、三条不可退让的契约

这三条各自都能让插件"装上但完全不工作"，所以写死进静态校验（`scripts/verify-package.mjs`）：

1. **入口不得 import `@deepseek-ai/*`**。静态 `import ... from '@deepseek-ai/...'`、动态 `import('@deepseek-ai/...')`、`require('@deepseek-ai/...')` 一律禁止。原因：插件在自己的目录下解析依赖，profile 的 `node_modules` 里解析不到这些包，入口 import 一抛错，后面的技能注册全部不执行——现象是"装了，但一个技能都没有"。
2. **`ctx.skills.register()` 必须当场传 `content` 字符串**（展开见 §5.2）。原因：runtime provider 的 `get(candidate)` 直接返回注册对象，校验要求 `typeof content === 'string'`；传惰性钩子会在加载期抛错，后面的注册全部不执行（v1 的原始故障）。
3. **`cordis.patch.yml` 必须有 `- insert:` 列表，且列表里有 `- id:` 与 `- name:` 两行**（值都是 `dsh-research-suite`），`package.json` 的 `dsh.bundle.patch` 必须指向该文件。缺任一条件，loader 永不 import 入口。

## 八、明确不做的事

- **不做技能路由器**：不返回"推荐技能名"作为终点。能力卡里成员技能名只出现在"账本"（谁的长处被搬进哪一步）里。
- **不做 UI**：不注册页面、侧栏、命令面板。
- **不联网**：运行时只依赖 node 内置模块；不请求任何远程服务。
- **不读外部技能目录**：719 篇原文随包分发，不读用户机器的 `skills-library` 或别的插件目录。
- **不写用户文件**：7 个工具当前都是只读查询/展开/自检；若后续引入写盘工具，需同步回改本文与 `docs/PUBLISH.md` 的安全说明。

---

相关文档：内容契约见 `docs/CAPABILITY-SPEC.md`，发布与排障见 `docs/PUBLISH.md`，对外介绍见 `README.md`。
