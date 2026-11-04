# 更新日志

本文件格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中

- 待定：各域能力卡的最终数量与融合细节以 `data/capabilities/*.json` 为准，本节的域级统计待主控在内容定稿后回填。TODO(lead)
- 待定：`scripts/selftest.mjs` 的加载期 smoke test 用例清单。TODO(lead)

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
