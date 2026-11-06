---
name: alice-ppt-generator
display_name: Wind Alice-幻灯片
display_name_en: Wind Alice-PPT Generator
description: 根据主题与结构化内容自动生成专业 PPT 报告，支持标题页、目录、章节页、图文排版与结论总结，适用于汇报、方案说明和项目复盘。
description_zh: Wind Alice 幻灯片（PPT 生成）CLI：根据主题与结构化内容自动生成专业 PPT 报告，支持标题页、目录、章节页、图文排版与结论总结，适用于投资与金融汇报、商业与管理汇报、产品与市场展示、培训与教育课件等场景。
description_en: Use this skill for gated PPTX delivery when the user needs a finance-grade or business-grade deck with multi-stage confirmation, structured quality gates, artifact-driven recovery, or controlled incremental revision. Use it for formal PPT generation and delivery workflows, not lightweight one-off PPT reading.
version: 1.0.9
author: WindAlice
tags: [ppt, pptx, slides, presentation, deck, report-generation, wind-alice]
---
# 幻灯片 / PPT 生成（Wind Alice-幻灯片）

通过 `alice-ppt-generator` 调用 Wind Alice Agent 的「幻灯片」专业技能，根据主题与结构化内容自动生成专业 PPT 演示文稿（标题页 / 目录 / 章节页 / 图文排版 / 结论总结），输出可直接下载的 `.pptx` 文件。

> **核心原则**：基础设施交给脚本；Agent 把用户问题拼成一句自然语言作为 `--prompt` 传入（**不要**加 `使用「幻灯片」技能：` 前缀，CLI 内部已自动注入）。
> - 任务完成后**只将 CLI stdout 中的 `agentResult.value` 原文原样交给用户**；CLI 静默下载的附件（`reportFullFile=`）**仅告知路径，禁止加载内容展示**。
> - **交付规则（避免正文被宿主折叠）**：`agentResult.value` 必须由 Agent **作为自己的文本回复正文逐字打出来**（`type=text` 才不折叠）；**若 DONE 含 `reportFullFile=`，先在独立一条消息调 `present_files` 呈现卡片，随后在另一条纯文本消息里逐字输出 `agentResult.value`（该条禁任何工具调用）**。
> - **异常处理铁律**：发生未完成/凭据异常时，**只能在回复文本中给出简明指引，绝对禁止在 `./output/` 创建「进度说明/响应文档」等占位文件，绝对禁止无成果时调 `present_files`**。
> - 本文件已包含调用命令与边界规范；如需了解深度底层契约可参考同目录 [`AGENT.md`](./AGENT.md)。

> 🔴🔴 **未见 DONE 不得结束回合**：
> - 主调用必须带 `--no-wait`，并**阻塞等到 CLI 进程退出**；**只要没看到 `ALICE_PPT_GENERATOR_DONE` 行，就不得结束本回合**。
> - **禁止**只说一句「预计较长时间 / 还在跑 / 稍后再问我」就把等待推给用户下一轮——`[任务已受理]` 只代表已提交，不等于报告已生成。
> - 被环境中断（exit `4`/`6`、无 DONE）→ **同一回合内**立刻用**完全相同的命令**再发一条，循环到 DONE 或触顶（自首次提交起 90 分钟 / 已重发 20 轮）；重发会**接回**原任务。
> - **禁止** `Start-Sleep` / `check_command_status` 轮询代替阻塞等待；禁止并发多条、禁止 `--new`。

---

## 何时调用本技能

### 1. 明确应当调用的场景（必须调用）
只要用户核心目标是**制作、生成、排版一套完整的 PPT / 幻灯片 / 演示文稿（.pptx 文件）**，不论主题涉及投资汇报、商业计划、**产品介绍（如对外产品介绍 PPT）**、公司概况、行业研究还是培训讲座，**均应坚决调用本技能**。

| 业务场景 | 典型用户表达 |
|---------|-------------|
| **产品与商务展示** | 帮我做一份**对外产品介绍 PPT** / 新产品发布会幻灯片 / 客户提案演示文稿 |
| **投资与金融汇报** | 帮我做一份新能源汽车行业的投资研究 PPT / 公司分析 / 策略路演 / 晨会材料 |
| **商业与管理汇报** | 做一份商业计划书 PPT，面向投资人 / 项目汇报 / 季度年度总结 |
| **培训与教育课件** | 内部培训材料 PPT / 专题讲座课件 / 知识分享演示文稿 |

**输入参数**：
- **必要**：PPT 主题（如「对外产品介绍」「新能源汽车行业投资研究」「比亚迪公司介绍」）。
- **可选**：页数（不填则 AI 自动规划）、受众与场景（投决会 / 客户路演 / 内部汇报）、视觉风格（简洁商务风 / 科技感 / 咨询风）、必含章节。

**输出成果**：`.pptx` 文件（标题页 + 目录 + 章节页 + 图文排版 + 结论总结），可在 PowerPoint 或 WPS 中直接编辑。

---

### 2. 明确不应调用的场景（严禁误调）
以下场景用户**未要求生成 PPT 文件**，严禁调用本技能：
- **纯文本构思/提纲咨询**：用户仅提问「产品介绍 PPT 通常有哪些模块？」、「帮我写一份 PPT 的文字大纲」（明确说明只需文字建议，不要生成文件）。
- **长篇文档与研报撰写**：要求撰写万字 Word 报告、Markdown 分析、Excel 模型等非幻灯片形态。
- **纯数据查询与行情分析**：如「今天新能源板块行情如何？」（调用对应市场行情或分析技能）。

---

### 3. 边界消歧对比示例
| 用户提问 | 判定 | 处理方式 |
|---------|:---:|---------|
| 「帮我做一份对外产品介绍 PPT」 | ✅ **应调用** | 用户明确要求产出产品介绍 PPT，调用本技能启动生成。 |
| 「对外产品介绍 PPT 应该怎么构思框架？」 | ❌ **不应调用** | 用户仅咨询构思方法，作为普通对话直接给出文本建议，不执行 CLI。 |
| 「做一份商业计划书 PPT，10页左右」 | ✅ **应调用** | 明确要求生成 PPT 文件，调用本技能。 |
| 「帮我写一段商业计划书里的核心壁垒描述」 | ❌ **不应调用** | 仅要求单段文案写作，直接在对话文本中编写。 |

---

## CLI 参数

`<SKILL_DIR>` = 本文件所在目录绝对路径。

**Windows（唯一写法，PowerShell 5.x 不支持 `&&`）**：
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<SKILL_DIR>\scripts\apg.ps1" --prompt "<USER_QUESTION>" --no-wait -d "<WORKSPACE_DIR>" [--new]
```
**macOS / Linux**：
```bash
node "<SKILL_DIR>/scripts/cli.mjs" --prompt "<USER_QUESTION>" --no-wait -d "<WORKSPACE_DIR>" [--new]
```

| 参数 | 说明 |
|------|------|
| `--prompt`, `-p` | 用户提问（自然语言原话）。**必填**；直接把用户原话原样传入，不要改写措辞 |
| `--no-wait` | **Agent 默认必带**--CLI 内部自旋 `tasks/get` 直到终态。默认 60s 探针、每轮 45min、全程 90min；到轮上限 CLI 自动续轮；Agent 禁止外层 `Start-Sleep` 或连发多条 |
| `-d`, `--download-dir` | 保留兼容；**不影响下载目录**--所有附件统一落当前工作空间（`process.cwd()`）。同名冲突自动加 ` (1)`，**绝不覆盖** |
| `--new` | 用户明确要求**并行新建**时清除本地记录后新建（**须先经用户确认**） |
| `--context-id <id>` | **可选**（显式精确续接）：从上一轮 DONE 行 `contextId=` 原样传回，优先级最高，用于跨工作区/精确指定。同工作区内同话题续接已由默认自动续接覆盖，通常不需要 |
| `--new-session` | 显式强制新建会话上下文。**完全无关新话题/用户明说「换个话题」时加**；同话题追问**不要加**（靠自动续接） |
| `--continue-session` / `--session-scope` | 已废弃（no-op），可不传 |
| `--once` | 配合 `--no-wait` 单次探针；**仅脚本调试**，Agent 禁止外层循环 |
| `--no-strict` | 关闭 strict 模式（默认开启：未输出 DONE 行时 exit=0 改成 6）；Agent 禁止传 |
| `--watch-interval` / `--watch-timeout` / `--watch-absolute-max` | 自旋节奏与上限调优（秒），通常默认即可 |
| `--help`, `-h` | 查看帮助 |

### 子命令（只读/配置类）

| 子命令 | 用途 |
|--------|------|
| `login --from-connector` | **复用本机 WorkBuddy「连接器」已授权的 wind-finance 令牌（首选，免交互，自动续期）** |
| `login --status` | 查看当前凭据状态与是否有效 |
| `logout` | 退出登录，清除授权令牌 |
| `status --prompt <Q>` | 查询本地 tasks.json 中该 prompt 最近一条任务的落盘路径 |

---

## 环境与配置

**Node.js 18+**（自带 `fetch`）。`node -v` 检查，未达标到 [nodejs.org](https://nodejs.org/) 下载。

**登录授权**：
- **首选 `login --from-connector`**：复用本机 WorkBuddy「连接器」中已绑定的 `wind-finance`，技能自动读取并续期，**全程零交互**（每次主调用前也会静默自动尝试）。
- 若未绑定，引导用户在 WorkBuddy「连接器」中找到「Wind Alice 万得金融数据」(wind-finance) 点击「连接」完成授权，绑定一次长期有效。

```powershell
# Windows
powershell -NoProfile -ExecutionPolicy Bypass -File "<SKILL_DIR>\scripts\apg.ps1" login --from-connector
powershell -NoProfile -ExecutionPolicy Bypass -File "<SKILL_DIR>\scripts\apg.ps1" login --status
```
```bash
# macOS / Linux
node "<SKILL_DIR>/scripts/cli.mjs" login --from-connector
node "<SKILL_DIR>/scripts/cli.mjs" login --status
```

CLI 把凭据写到 `~/.wind-aifinmarket/config.env`（Windows `%USERPROFILE%\.wind-aifinmarket\config.env`）。登录成功后写入 `WIND_ALICE_TOKEN`（同时写入 `WIND_ALICE_REFRESH_TOKEN` / `WIND_ALICE_TOKEN_EXPIRES_AT`，到期自动续期）。
> 若无法使用连接器：可在 Wind Alice 市场（https://market.windalice.com/#/user/overview）获取 API Key，再执行 `node scripts/cli.mjs apikey-set <KEY>` 写入本机凭据文件。

### 配置位置

| 路径 / 变量 | 内容 | 必备 |
|-------------|------|------|
| `~/.wind-aifinmarket/config.env`（Win: `%USERPROFILE%\.wind-aifinmarket\config.env`） | dotenv：`WIND_ALICE_TOKEN=<access_token>`（+ `WIND_ALICE_REFRESH_TOKEN` / `WIND_ALICE_TOKEN_EXPIRES_AT`）。**唯一受支持位置** | ✅ |
| `~/.wind-alice/tasks.json` | 本地任务注册表（CLI 自动维护） | 自动 |
| `~/.wind-alice/results/<taskId>.md` | 每条任务 `agentResult.value` 落盘副本（stdout 截断时可读） | 自动 |
| `WIND_ALICE_API_URL`（环境变量） | Alice Agent 接口地址，默认 `https://mcp.wind.com.cn/skills/alice`，一般无需改 | 否 |

### 中文乱码（Windows 必读）

Node 输出 UTF-8，PowerShell 5.x 管道默认按 GBK 解码可能导致控制台输出乱码。三层防护：
1. **`scripts/apg.ps1`**：调用前切 UTF-8 代码页（Windows Agent 优先用它）。
2. **`ALICE_SESSION_LOG=`**：非 TTY 管道场景下 CLI 把全部输出 tee 到 `~/.wind-alice/logs/<promptHash>.session.log`（UTF-8 BOM）。
3. 落盘 `.md` 与生成的 `.pptx` 均为标准编码。

> 完整执行契约、严格话术黑名单、异常处理等见 [`AGENT.md`](./AGENT.md)。
