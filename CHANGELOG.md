# 更新日志

本文件格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中

- 待定：随插件在 npm 上发布 format 1 索引源，便于在 DSH「发现 → 索引源」里直接添加。

## [3.1.0] - 2026-11-08

**按外部专家评审逐条整改。** 专家给了六条批评，这一版对每一条都给了可核验的改动，不再只有自述。

### 一、识别层：从「总分大于零就接管」改成有闸门的判定

- 旧实现：`lower.includes(trigger)` + 二元组重叠，任何微弱命中都会进候选，非科研任务也会被套上科研流程。
- 新实现（`lib/core.js` 的 `matchIn`）：
  - **触发词索引 + 特异性加权**：`spec = max(0, 10 - 3*(df-1))`，只被一张卡使用的词才拿满分，被多卡共享的泛词自动降权（治「参考文献」「审稿」这类共享词抢分）。
  - **切窗噪声过滤**：长触发词切出的片段若含「我你帮要想能怎么这那的了呢吧吗啊请就还也都」即丢弃——正是这些窗口让「购物清单/爬虫/工作总结」被误判成检索任务。
  - **口语线索表 52 条**：把「不够硬」「论证不足」「秒拒」「组会」「三线表」「样本量」「PSM」「孟德尔」「机制图」等真实说法直接绑到对应能力卡。
  - **否定闸门**：生活事务、投资理财、娱乐文艺、通用软件工程、行政事务五类模式命中时，除非同时满足「科研线索 ≥2 + 得分 ≥45 + 有线索命中」否则**强制不接管**。
  - **置信度分级**：high / medium / low，附带得分、与第二名的分差、命中词；`research_playbook` 直接把这些打给模型看。
- **可核验的评估**：新增 `data/golden/cases.json`（50 条真人原话，含 5 条「不该接管」）与 `scripts/eval-match.mjs`，CI 里用 `--strict` 卡门槛。

| 指标 | 旧版 | 3.1.0 |
|---|---:|---:|
| 接管判定正确率 | 30%（15/50） | **100%（50/50）** |
| 不该接管却被接管 | — | **0/5** |
| 域 top1 | 68.9% | **93.3%** |
| 能力卡 top1 | 20% | **91.1%** |
| 能力卡 top3 | 22.2% | **100%** |

诚实说明：这 50 条 golden 是本次自拟的，存在过拟合风险；机制（特异性加权 + 口语线索 + 否定闸门）是通用的，但样本量小，后续需要真实对话语料继续扩充。

### 二、门禁：误报清零，并给出三级口径

- 新增 `data/gate-whitelist.json`：约 35 条医学/统计白名单（完全缓解、完全切除、首次给药、首次确诊、最高值…）、复合词白名单（覆盖、涵盖、遮盖、掩盖、盖玻片、盖髓、亦然、亦可…）、以及「只有出现在结论句里才算绝对化」的极限词表。
- `checkText` 输出改为 **必改（error）/ 建议改（warn）/ 仅提示（info）** 三级；`total` 只统计 error+warn，info 不再被当成错误。
- 单字文言（盖/矣/焉/岂）只在句首或标点后判定；「所谓/亦/故/夫」降级为低置信提示。
- 绝对化措辞不再默认报错：只有同分句里出现 `P<|P>|显著|优于|提高|降低|改善|证实` 时才升为「建议改」。
- 实测：专家点名的正常医学表述 → 必改 0、建议改 0、仅提示 1；真有问题的句子 → 必改 2（半角标点/括号）+ 建议改 4（AI 套话×2、绝对化×2）。

### 三、从「只能查」到「能真跑」：工具 7 → 12

新增 `lib/verify.js`（981 行，纯 Node 零第三方依赖）与 5 个工具：

| 工具 | 做什么 | 边界 |
|---|---|---|
| `research_run` | 把 R/Python 脚本写进临时目录并真跑（Rscript / 本机 Python），返回 stdout/stderr 与产出文件 | 禁 `install`/`rm` 类命令；workdir 限 cwd 或临时目录；运行时缺失/被宿主拦截都如实返回，不伪造成功 |
| `research_data_check` | CSV/TSV 的行列、缺失率、常量列、ID 重复、不可能值、EPV | 只做机械项，变量含义仍需人工判 |
| `research_output_check` | PNG 实测 DPI、PDF 页数与文本层、DOCX/XLSX 结构、CSV 行数、MD 字数 | 不做审美判断 |
| `research_doi_check` | DOI 向 Crossref 核验存在性，返回标题/期刊/年份 | 网络不通时明确报 `network`，绝不编造 |
| `research_ref_audit` | 正文 `[n]` 与文献表对账：跳号、重复、条目缺 DOI、年份可疑 | 不替代人工核对原文 |

### 四、真实性核验（新增）

- DOI 核验与引用对账做成工具（见上），文献真实性从「口号」变成可执行步骤。
- 仍**不做**查重与 AIGC 检测：这两件事需要外部付费服务与全文上传，本插件明确不做，并在 README「能力边界」里写清。

### 五、知识层瘦身：40 MB → 16 MB，且逐条可审计

- 新增 `data/quality.json`：592 条源技能逐条判定 `core 245 / support 67 / peripheral 138 / excluded 142`（每条带 reason、语言、是否科研相关）。
- 被排除的 142 条（模型量化、语音合成、通用工程等）**完全不进包**；peripheral 只留正文不带资产。
- 结果：技能 592 → **450 条**（唯一目录 444）、资产 3,924 文件 29 MB → **954 文件 6.8 MB**、`knowledge/` 37.3 MB → **14.3 MB**、整包 **1,481 文件 / 16.20 MB**（原 4,586 文件 / 38.83 MB）。
- 同名技能消歧从「内置优先 + 字节大优先」改为 `dupRank`（描述信息量 > 资产 > 字节数 > 来源），并写进 `data/quality.json` 可复核。

### 六、宿主耦合与降级

- 0.2.2-rc.1 的「工具静默消失」已在 3.0.1 修好（`tools` 写进 `inject` + 延迟注入兜底 + 策略段装载自检行），本版保留并新增 selftest 断言。
- `dsh.testedWith` 记录实测过的宿主版本；README 增加「故障排查」一节，写清服务缺失时的表现与重启步骤。

### 其它

- 版本号、README 两份、`docs/ARCHITECTURE.md`、`docs/ATTRIBUTION.md`、`docs/CAPABILITY-SPEC.md`、`knowledge/FUSION.md`、`knowledge/INDEX.md`、入口技能全部按新数字与 12 个工具同步。
- `npm run check` 现在串起 selftest → 能力卡 → 判定账本 → 包校验；CI 另跑 `eval-match --strict`。

## [3.0.1] - 2026-11-06

**适配 DSH 0.2.2-rc.1。** 这一版只有一个实质修复，但它是致命的：升级到 0.2.2-rc.1 后，插件的 10 份技能与自动接管策略段都正常加载，**7 个 `research_*` 工具却静默消失了**。

### 修复

- **工具全部丢失（0.2.2-rc.1）**：入口原本只声明 `export const inject = ['skills']`，工具在 `apply()` 里用同步 `ctx.get('tools')` 现取。0.2.2-rc.1 的服务装配时序变了——apply 那一刻 `tools` 还没就绪，`ctx.get` 返回 `undefined`，七个工具就一个都没注册，而技能注册与 `systemPrompt.section()` 都成功，日志里也只有一条不显眼的 warn（默认不进日志文件），现象是「插件看着在工作，`research_playbook` 却不存在」。按官方 `cordis-plugin-development/references/host-plugin.md:61` 的写法，把 `tools` 提升为 `inject` 里的硬依赖，cordis 会等到服务就绪再 apply。
- **`systemPrompt` 保持可选但不再靠运气**：仍先同步取服务，取不到走 `ctx.inject(['systemPrompt'], cb)` 建子 fiber 延迟补装，避免在没有 agent 运行时的 profile 里把整个插件卡在 pending。
- 顺带把取服务统一收进 `readService(ctx, name)`（先试属性、再试 `ctx.get()`，两条路各自 try/catch），任何一次取服务失败都不再能掀翻已经成功的技能注册。

### 变更

- `package.json` 新增 `dsh.testedWith: ["0.2.1-rc.5", "0.2.2-rc.1"]`，`engines.dsh` 仍为 `>=0.2.0-0 <0.3.0`（两个版本都实测可用）。
- `scripts/selftest.mjs` 新增两条防线：`inject` 必须含 `tools`；以及「apply 时服务尚未就绪 → 延迟注入后工具仍为 7 个、策略段仍为 1 个」的时序用例。检查项 56 → 64 项。

### 兼容性实测

- `dsh-skill` 的 `skills.register()` 契约两版完全一致（同一份 23721 字节）。
- `dsh-system-prompt` 只做了加法（新增 `TOOL_APPLY_PATCH: 1350`、`TOOL_SCHEDULE: 2500`），本插件用的 `order: 650` 未被占用。
- `dsh-tools` 内部拆包，但 `register()` 的校验语义逐条未变（`output.render` 必须是函数、`output.schema` 必须受支持、`timeoutMs` 正有限数、`run_code` 保留名）。
- `export const Config` 依旧不导出——0.2.2-rc.1 下它仍然是启动崩溃的引信。

### 发布

- **首次上架 npm**：`dsh-research-suite@3.0.1`（https://www.npmjs.com/package/dsh-research-suite）。registry 侧的 tarball 为 `12,671,464 B / 4584 files / unpacked 40.7 MB / MIT`，从 registry 拉回来解包后四件套（selftest 66 项 / 103 能力卡 / 586 条账本 / verify-package）全过。
- npm 现已强制「发布必须有 2FA，或带 Bypass 2FA 的 granular token」；本账号 2FA 是 security key，CLI 产生不了 TOTP，故 `--otp` 这条路的报错永远是同一个 `E403`。新包首次发布还会被 registry 自动暂存约 6 分钟（先出现 `0.0.0-stage` 占位版），期间 `npm stage list` 为空属正常。全过程与踩坑记录见 `docs/PUBLISH.md` §3.1.1。
- 两份 README 的安装段改成「npm 优先、本地目录次之、GitHub 兜底」，并补了 `dsh.cmd plugin --profile desktop add dsh-research-suite@3.0.1` 的等价写法。

## [3.0.0] - 2026-11-06

v3 不动运行架构，动的是**知识层**：把 719 篇「按关键词贴上域标签」的技能原文，换成 592 个**逐条判定过、带自带资产**的源技能，并为每一条判定留下可审计的账本。同时修掉一个会让 DSH Desktop 起不来的配置事故。

### 新增

- **592 个源技能的逐条判定账本**：`data/ledger/<domain>.json` 为每个源技能记一条判定（`fused` / `index-only` / `deprecated` / `out-of-scope` + 理由 + 融进哪些能力卡），对「每个技能都学过、择优录取」的要求给出可审计证据；`scripts/verify-ledger.mjs` 校验账本覆盖度（与 `knowledge/catalog.json` 的 `dir` 集合逐一对齐）与 `fused` 判定能否在能力卡 `members` 里核到。
- **第 10 个能力域 `data`（数据库与组学数据）**：覆盖 GEO / TCGA / dbGaP / UK Biobank / ClinVar 等数据库检索、组学数据获取与整理。
- **toolbox 索引桶**：233 个工具类技能归入 `toolbox` 域，只进 `research_catalog` 检索与 `research_kb_read` 深读，**不产能力卡**——工具是手段，不是「用户要办的一件事」。
- **技能自带资产随包分发**：除正文外，收录源技能的 `references/`、`scripts/`、`templates/`（文本/代码类白名单扩展名、单文件 ≤256KB、用户级整包 ≤260KB、内置技能 ≤5MB）。当前 451 个技能带资产、共 3924 个文件、约 29 MB。
- **`research_kb_read` 新增 `asset` 参数**：`research_kb_read(name, asset='scripts/plot.py')` 直接读技能自带的脚本/参考/模板；不给 `asset` 时列出该技能带了哪些资产。
- **知识库索引重建**：`knowledge/catalog.json` 592 条，字段扩展为 `name / dir / slug / domain / source / category / layer / bytes / file / description / whenToUse / assets`，并新增 `knowledge/stats.json` 的资产统计。

### 修复

- **DSH Desktop 启动失败（v2.0.0 上线当天）**：`lib/index.js` 曾对外 `export const Config`（Standard Schema + `toJSON()` 返回 JSON Schema）。Host 的 settings 服务会把 `toJSON()` 结果当 **schemastery 信封**用 `new Schema(json)` 水合，`schema.meta` 为 `undefined` → 读 `.volatile` 抛 `Cannot read properties of undefined (reading 'volatile')` → Desktop 起不来（`The application could not start`）。**现已删除 `Config`**，配置改由 `apply()` 内的 `validateConfig()` 兜底到 `DEFAULTS`；副作用是 settings 面板里暂时没有本插件的配置项，覆盖配置写在 profile 的 `cordis.patch.yml` entry `config:` 里。详见 `docs/ARCHITECTURE.md` §5.3。
- **源技能名带引号**（frontmatter 引号未剥离）导致能力卡成员匹配不到的问题，交由知识库构建侧修正（`scripts/verify-package.mjs` 现在会对带引号的 `name` 报错）。

### 变更

- **源技能 719 → 592**：v2 的 719 里包含 162 个噪声/错标技能（工程类、生活类、重复收录），v3 全部剔除或降为 `out-of-scope`，每条都留在账本里可查。
- **能力域 9 → 10**（新增 `data`），能力卡数量与域内聚类相应重做；能力卡总数以 `data/capabilities/*.json` 为准。
- **工具面**：仍是 7 个工具（`research_playbook` / `research_capability` / `research_catalog` / `research_kb_read` / `research_standard` / `research_gate` / `research_suite_status`），`research_catalog` 与 `research_kb_read` 增加资产维度，`research_suite_status` 装载自检改为读 592 条索引与资产统计。
- **技能面**：11 个技能（1 入口 + 10 域 SOP）。
- **包体**：592 篇原文 + 3924 个资产文件（约 29 MB）随包分发，仍保持「运行时不读取任何外部技能目录」的自包含约束；体量较 v2 明显增大，`npm pack` 体积以发布时实测为准。
- **文档与 CI**：`docs/ARCHITECTURE.md` 新增「v3 知识层与判定账本」与 Config 事故复盘；`docs/PUBLISH.md` 按 3.0.0 更新；`.github/workflows/ci.yml` 增加 `verify-ledger.mjs` 步骤；两份 README 更新为 10 域 / 592 技能 / 资产与 `asset` 参数。

### 移除

- 移除对外导出的 `Config`（崩溃根因，见上）。
- 移除 v2 的 719 条 catalog、`general` 域桶（改为 `toolbox` 索引桶）与旧的按标签自动聚类的域标注。

## [2.0.0] - 2026-11-04

v2 是一次**架构级重写**，不是 v1 的增量修复。三处硬伤决定了必须重写：机械单选"首选技能"没有真正融合、误用 DSH 技能注册 API 导致技能全部注册失败、完全没有自动触发机制。

### 新增

- **能力卡（capability）融合模型**：9 个域（writing / polish / figures / stats / ideation / review / slides / literature / format）各产出一份 `data/capabilities/<domain>.json`。每张能力卡把同功能的所有竞争技能拆成 `best_at` / `limits` / `take` 三元组，再合成为一条 3～8 步的**融合协议**（每步标注取自谁、为什么取它），并给出可机械检查的 `gates`、`outputs` 与深读 `kb`。取代 v1 的"首选技能 + 备选技能"路由。
- **`ctx.systemPrompt.section()` 自动接管段**：注入一段「科研任务自动接管」策略，插件安装后自动识别科研诉求并按「playbook → 能力卡协议 → 深读 → 自检」的顺序工作，**无需用户手动选择技能，也没有任何 UI 页面**。
- **门禁与机械自检层**：`data/gates.json` 提供 selfcheck / mutex / forbidden / hard 四类规则，配合 `research_gate` 工具对交付文本做中文标点、引用上标、AI 套话、绝对化措辞的机械检查。
- **规范深读层**：`references/` 补齐 9 份规范（中华医学会格式、中文语言风格与好句语料库、Elsevier 英文语言标准、论文类型风格档案、标书硬性规则与 AI 痕迹、IMA 知识库清单与蒸馏任务书、科研技能索引、科研技能自动调用工作流），由 `research_standard` 工具读取。
- **知识库索引层**：`knowledge/catalog.json`（719 条技能索引）、`knowledge/INDEX.md`、`knowledge/FUSION.md`、`knowledge/stats.json`，支撑 `research_catalog` 检索与能力卡的技能名对账。
- **发布工程**：`scripts/verify-capabilities.mjs`（能力卡契约校验）、`scripts/verify-package.mjs`（发布静态校验：patch 结构、入口依赖禁令、技能 frontmatter 与编码、JSON 可解析性、catalog 文件存在性、版本一致性、包体统计）、`.github/workflows/ci.yml`（verify + publish 两个 job，publish 走 `npm publish --provenance`）、`icon.svg`、`docs/PUBLISH.md`、`docs/ARCHITECTURE.md`。

### 修复

- **`ctx.skills.register()` 契约修复（v1 致命故障）**：v1 给注册接口传了 `load()` 之类的惰性钩子，DSH 加载期直接抛错，导致 10 个技能一个都没注册上。v2 改为**注册时当场内联 `content` 字符串**（技能内容在注册时即确定，不依赖运行时 IO）。该约束由 `scripts/verify-package.mjs` 长期看护。
- **入口依赖禁令**：入口与 `lib/**` 一律不 import `@deepseek-ai/*`（静态 `import`、动态 `import()`、`require()` 三种形式全禁）。原因：插件在自己的目录下解析依赖，profile 的 `node_modules` 里解析不到这些包，入口 import 一抛错，后面所有注册都不执行——现象是"装了但一个技能都没有"。校验脚本按 `file:line` 报命中位置。
- **bundle 补丁层结构**：`cordis.patch.yml` 必须含 `- insert:` 列表且有 `- id:` 与 `- name:` 两行，`package.json` 的 `dsh.bundle.patch` 必须指向它；缺任一条件 loader 永不 import 入口。

### 变更

- **工具面重构为 7 个工具**，职责收敛、入口唯一：
  - `research_playbook` —— 唯一入口，传用户原话返回 1～3 张最匹配能力卡 + 协议 + 判据 + 交付物 + 建议深读；
  - `research_capability` —— 按能力卡 id 或域展开完整卡（成员对比、协议、分歧点、门禁、交付物、深读清单）；
  - `research_catalog` —— 在 719 个原始技能目录里检索；
  - `research_kb_read` —— 读单个技能原文或索引文件，支持分段、越界路径拒绝；
  - `research_standard` —— 读 `references/` 下 9 份规范；
  - `research_gate` —— 门禁与交付文本机械自检；
  - `research_suite_status` —— 装载自检（版本、9 域能力卡数量、719 索引完整性、references 齐备性）。
- **技能面重组为 10 个技能**：1 个入口技能 + 9 个域融合 SOP（`skills/research-<domain>.md`，每份为七节固定结构，含模板、阈值与脚本片段）。
- **包体策略转为"自包含"**：719 篇原始技能全文（约 9.9 MB，连同 `knowledge/` 索引后整包 773 files / 11.24 MB（`npm pack`：771 files / 11.8 MB 解包、tarball 4.1 MB））随包分发，运行时不读取任何外部技能目录。`files` 白名单需完整覆盖 `lib`、`data`、`skills`、`knowledge`、`references`、`scripts`、`docs`、`cordis.patch.yml`、`icon.svg`、`README.md`、`README.zh-CN.md`、`CHANGELOG.md`、`LICENSE`。
- **双语文档**：`README.zh-CN.md` 为完整中文说明（定位、能力卡动机、9 域、7 工具、安装、配置项、占位符清单），`README.md` 为英文精简版并链接到中文版。
- **运行环境基线**：仅依赖 node 内置模块；`engines` 为 node `^22.19.0 || >=24.0.0`、dsh `>=0.2.0-0 <0.3.0`。开发与验证基准为 DSH 0.2.1-rc.5 桌面版（profile `desktop`）。

### 移除

- 移除 v1 的"首选技能 + 备选技能"路由数据结构，以及围绕它的技能选择逻辑。
- 移除任何 UI 页面、侧栏与命令面板（v2 的自动触发完全由系统提示段承担）。

### 迁移说明（v1 → v2）

v1 与 v2 **不兼容**，能力卡 JSON 结构与工具参数都是新的。升级方式：卸载 v1（`plugin_manager` 的 `remove_bundle`，target 传旧包名），安装 `dsh-research-suite@2.0.0`，然后**完全退出并重启 DSH Desktop**。详见 `docs/PUBLISH.md` §六。

<!-- 细节占位：各域最终能力数、719 条索引的生成命令、selftest 覆盖范围待主控定稿后回填。TODO(lead) -->
