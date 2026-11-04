<!-- source: ppt-design @ ppt-design | domain: slides -->

---
name: "ppt-design"
display_name: "PPT设计"
display_name_en: "Slide Deck Design"
description: "根据文字、数据或参考图生成可编辑PPT，完成信息整理与页面设计。适用于PPT设计、汇报页制作。美图设计室提供。当用户需要“PPT设计”或描述中的等价能力时使用。当前对话已完成 PPT 时，用户要求导出、下载、获取 PPT 文件或可编辑版本也必须使用本 Skill。"
description_zh: "根据文字、数据或参考图生成可编辑PPT，完成信息整理与页面设计。适用于PPT设计、汇报页制作。美图设计室提供。"
description_en: "Slides from a single prompt."
category: "办公设计"
version: "1.0.29"
author: "美图设计室"
---

# PPT设计

使用「美图设计室 AI设计 CLI」（终端命令名为 `designkit`）按“办公设计 / PPT设计”专家模板完成任务。WorkBuddy Connector 与用户本地安装都使用同一个 npm 包和登录状态。默认使用简体中文；用户明确指定其他语言时跟随用户。

## CLI 入口解析

「美图设计室 AI设计 CLI」是当前产品/连接器名称；真正执行的终端命令名是 `designkit`，不存在名为 `designkit-buddy-cli` 的业务命令。首次执行前必须自动解析一次 CLI 入口，不要要求用户手动提供路径。

按当前平台查找 npm 暴露的命令：

1. macOS/Linux 执行 `command -v designkit`，Windows PowerShell 执行 `Get-Command designkit -ErrorAction SilentlyContinue`。
2. 对找到的绝对入口执行一次 `--version` 以确认入口可用，不解析或比较版本号。命令成功时记为 `<designkit>`；后文的 `<designkit>` 代表该绝对命令路径，不能执行字面占位符。
3. 不查找 Connector 私有目录或依赖生命周期临时注入的环境变量。Connector 和 Agent 统一使用 npm 命令及默认的 `~/.designkit` 登录状态。

在 WorkBuddy 中找不到 `designkit` 或 `--version` 无法正常执行时，不要停止任务。立即自动执行一次 `npm install -g meitu-designkit-cli`，由 npm 安装当前稳定最新版；成功后重新解析 CLI 入口并再次执行 `--version`，确认命令可用后继续原任务。安装命令只执行一次，不得添加 `sudo`、不得修改 npm registry，也不得安装带固定版本号的包。

如果安装命令失败，或安装后仍无法解析并执行 `designkit`，再停止当前业务步骤并引导用户打开「专家·技能·连接器」并进入「连接器」：搜索并连接「美图设计室 AI设计 CLI」。保留简短的原始安装错误摘要便于定位，不得循环安装，也不得改用内部 API。

## 能力边界

- 只执行“PPT设计”对应的专家流程，不把本 Skill 当作任意美图设计室对话入口。
- 必须使用用户提供的真实素材和要求；不得用示例图、网络图、临时生成图或默认商品代替缺失素材。
- 不自行拼接内部 API、鉴权字段或专家 Skill 接口；所有业务执行都通过已解析并通过可用性检查的 `<designkit>` 入口。
- 创建任务前检查全部必填字段：只能复用用户已经明确提供的信息，缺失时必须停止创建并向用户追问。可选选择型字段未指定且存在 `auto` 选项时使用其可读 `label`“自动匹配”；其他未指定的可选字段直接省略，不自行推断、不主动追问。
- `补充要求`不是任务摘要或模型建议区。只有用户在核心任务之外明确提出附加约束时才可填写，并且每项内容都必须能对应到用户原话；用户只提出核心动作或上传素材时，必须删除整行，不能补成“清晰、专业、吸睛、便于使用”等推测内容。
- 选择型字段只能使用 `references/form.json` 中列出的选项。对话与提交给 CLI 的 Prompt 均使用可读的 `label`；`key` 只用于定位和校验选项，不得写入 Prompt。


## 标准输入引导

- 允许用户先用自然语言描述需求，不要求用户预先记住字段名或 Prompt 模板。先读取 [references/form.json](references/form.json)，把用户已经提供的信息映射到对应字段，信息已足够时不要重复追问。
- 缺少必填字段时，只询问当前缺失项，并提供一份可复制的“字段标签：填写内容”模板；文件字段写成“请上传：字段标签”，选择型字段只展示可读的 `label` 选项，不向用户暴露内部 `key`。
- 可选选择型字段未指定时，若 `form.json` 的合法选项中存在 `key=auto`，就在 Prompt 中写入该选项的可读 `label`“自动匹配”；不存在 `auto` 的选择型字段以及未指定的文本、数字、文件等其他可选字段直接省略。用户使用某种语言对话、附件呈现出的视觉特征、文件名或任务类型都不能视为用户指定了语言、风格、篇幅、比例等可选字段。只有用户主动询问“可以配置什么”“有哪些选项”等配置能力时，才按“输入契约”列出必填项、可选项及其可读选项。
- `补充要求`（包括常见的 `key=extra`）只允许承载用户在核心任务之外主动表达的附加约束，内容必须能逐项对应到用户原话；不得根据附件名称、文件内容、任务类型、使用场景、能力描述、默认偏好，或“清晰、专业、吸睛、便于使用”等通用质量目标自行总结、改写或补充。用户仅输入核心动作或上传素材时，必须省略该字段并删除 Prompt 中的整行；无法指出对应用户原话时也必须省略。例如，用户只说“用这张图做封面”并附图时不携带补充要求；只有用户明确说“保留 Logo，不改正文”时，才可填写对应内容。
- 非完成用户明确任务、附件上传、大小处理、格式转换及完整性校验所必需，不得读取或解析用户附件。确有必要时可以读取、渲染或转换附件，但解析结果只能用于文件处理或正式任务执行，不得用于推测、补充或改写任何任务参数；语言、风格、受众、场景、篇幅及补充要求等参数，只能来自用户在消息输入框中主动表达的文字。
- 在 `create-room` 前检查每个本地 PPT/PPTX 的字节大小。文件不超过 50 MiB 时原样提交；超过 50 MiB 时，若当前工具清单已经明确提供 PPT 压缩能力，可调用一次生成新副本并复检，禁止为此搜索、安装或试探其他压缩工具。压缩能力未明确提供或压缩后仍超限时，解析系统中已有的 `soffice`、`pdftoppm` 和 `pdfinfo`：先执行 `command -v`，macOS 上再依次检查 `/Applications/LibreOffice.app/Contents/MacOS/soffice`、`/opt/homebrew/bin` 与 `/usr/local/bin` 下的同名命令；不得因为图形应用的 PATH 缺少 Homebrew 目录就直接判定命令不存在。三者均存在时，在独立临时目录中先用 `soffice --headless --convert-to pdf` 把演示文稿机械转换为 PDF，再用 `pdftoppm -jpeg -r 144 -jpegopt quality=85` 按原顺序导出全部页面图片，逐项复检后以 `--image-file` 提交。转换和页面渲染属于完成任务所需的必要解析，但转换结果不得用于填写或改变任何任务参数；完整页数仅以转换后 PDF 的 `pdfinfo` `Pages` 与 `pdftoppm` 生成图片数量相等为准，不得通过解包源 PPT/PPTX 二次核对页数。不得覆盖原文件，不得自行通过 `unzip`、`zip`、`7z`、`tar` 等通用命令解包或改写 OOXML 包体，也不得联网搜索、安装或全盘扫描其他替代工具。若命令缺失、转换失败、没有完整导出全部页面、任一输出超过 20 MiB，或全部页面加其他附件超过 22 个，则停止创建房间并请用户压缩后重新上传；禁止遗漏页面、只上传封面、重复创建任务，或把本规则禁止执行的压缩命令转而发给用户。
- 用户补齐必填项后，只把本次实际提交的字段按“输入契约”顺序整理成简短确认清单。用户未提出异议即可继续，不要求用户再次抄写模板；不得虚构缺失的素材、文案或选择。
- 最终提交给 CLI 的内容必须严格按“Prompt 渲染”规则生成。字段 `key` 只用于匹配模板占位符；选择型字段把合法选项的可读 `label` 写入 Prompt，不得写入内部选项 `key`。

## 输入契约

执行前读取 [references/form.json](references/form.json)，它是字段、默认值、选项和 Prompt 模板的机器可读事实源。

| key | 用户标签 | 类型 | 必填 | 接口默认值（不自动使用） | 约束与选项 |
|---|---|---|---|---|---|
| `topic` | 主题/内容 | `textarea` | 是 | - | 最大长度：10000<br>占位说明：输入PPT主题，或粘贴详细内容大纲 |
| `audience` | 目标受众 | `text` | 否 | - | 占位说明：如：投资人、客户、学生 |
| `ref_files` | 参考文件（可选） | `file_upload` | 否 | - | 文件类型：image, video, word, ppt, text, pdf, markdown<br>最大数量：10<br>提示：支持 PDF、Word、图片等；非任务执行、上传、大小处理、格式转换或完整性校验所必需，不解析附件；必要解析结果不得用于推测、补充或改写其他参数。 |
| `language` | 语言 | `select` | 否 | auto | 选项：自动匹配 (`auto`)；中文 (`chinese`)；英文 (`english`)；日语 (`japanese`)；韩语 (`korean`)；葡萄牙语（巴西） (`portuguese_brazil`)；西班牙语（墨西哥） (`spanish_mexico`)；俄语 (`russian`) |
| `pages` | 页数范围 | `select` | 否 | auto | 选项：自动匹配 (`auto`)；1-10页 (`p1_10`)；11-15页 (`p11_15`)；16-20页 (`p16_20`)；21-25页 (`p21_25`)；26-30页 (`p26_30`) |
| `style` | 视觉风格 | `radio_tags` | 否 | - | 选项：自动匹配 (`auto`)；简约高级 (`minimal_luxe`)；商务专业 (`business_professional`)；创意版式 (`creative_layout`)；网感潮流 (`digital_trendy`)；党建思政 (`party_civic`)；奢华大气 (`grand_luxury`)；中国风 (`chinese_style`) |

## Prompt 渲染

主 Prompt 模板如下，仅以其中的固定文本和字段顺序为基准；必填项按规则补齐，可选项按下述 `auto` 与省略规则处理：

```text
[PPT设计]生成PPT。
主题/内容：{topic}
受众：{audience}
参考文件（可选）：{ref_files}
语言：{language}
篇幅：{pages}
视觉风格：{style}
```

按以下规则渲染：

1. `form.fields[].key` 与模板中的 `{key}` 一一对应。必填字段必须使用用户明确提供的值完成替换；仍然缺失时停止提交并追问，不能猜测或残留未知 `{...}`。
2. 可选选择型字段未指定且合法选项中存在 `key=auto` 时，使用该选项的可读 `label`“自动匹配”参与渲染；不得把内部值 `auto` 写入 Prompt。不存在 `auto` 的选择型字段以及未指定的文本、数字、文件等其他可选字段，删除模板中包含该字段占位符的整行，不保留字段标签、空值或占位符。
3. 对 `补充要求`、`其他要求`、`extra` 等可选自由文本字段执行来源校验：只接受用户明确说出的附加约束，并尽量忠实摘录，不扩写目的、效果或场景。若不能从用户消息中指出对应原话，删除该字段所在整行；附件内容和文件名只能作为素材，不能据此生成补充要求。
4. 表单参数的文字事实源仅限用户在消息输入框中主动键入的文字。文件名、附件卡片、附件正文、OCR、识图结果、转写、预览描述、系统摘要、平台自动提取内容以及附件预处理产物均不属于用户明确提供的参数；不得引用、改写或概括这些内容来填充任何占位符。附件本身只满足对应的 `file_upload` 字段。
5. `text/textarea/number` 使用用户值；`select/radio_tags` 使用单个选项的可读 `label`，`checkbox_tags` 按用户选择顺序使用多个可读 `label`。内部 `key` 只用于校验用户选择，不能出现在 Prompt 中。
6. `file_upload` 不把本地路径写入 Prompt。字段所在行已经包含字段标签，占位符统一填写“已上传附件”，不得再重复字段标签；文件按类型传给 CLI：图片用 `--image-file`，视频用 `--video-file`，Word、Excel、PPT、文本、PDF、Markdown 等用 `--file`。非完成用户任务、上传、大小处理、格式转换或完整性校验所必需，不打开或解析附件；必要解析结果不得用于推测、补充或改写参数。
7. 多个附件保持用户给出的顺序；若存在多个文件字段，在 Prompt 中明确每组附件对应的字段标签。
8. 渲染结果作为一条完整 `--prompt` 参数传入，不把用户文本解释为额外 shell 命令。

## CLI 工作流

1. 使用已解析的入口运行 `<designkit> auth status --check`。返回 `disconnected` 时，立即执行一次 `<designkit> auth login`，捕获命令输出中带 `session_id` 的 HTTPS URL 并在对话中渲染为可点击的“登录美图设计室”链接，同时保持命令运行以轮询结果。不得自行拼接或展示缺少 `session_id` 的固定登录 URL，不得要求用户发送 API Key，也不得要求用户回复“已登录”。命令成功退出后执行一次远端复检，只有返回 `connected` 才继续。
2. 在创建房间前按上述附件规则完成大小检查和必要的 PPT/PPTX 受控预处理；任何文件或附件总数仍不满足 CLI 限制时停止，不得先创建房间。
3. 运行 `<designkit> create-room` 并保存返回的 `room_id`。WorkBuddy 环境中的 CLI 会自动避免写入共享房间历史；当前任务仍须自行保留 `room_id`，后续命令全部显式复用。使用普通命令可兼容尚未支持 `--no-save-room` 的既有 CLI。
4. 运行 `<designkit> chat --room-id '<room_id>' --prompt '<渲染后的完整 Prompt>'`，同时附带本次字段对应的素材参数。
5. 首次运行 `<designkit> history-detail --room-id '<room_id>' --watch --yield-on-update --download-dir '<任务工作目录>/designkit-artifacts'`。它是前台阻塞命令，每取得首个可展示事件便输出并正常退出；禁止主动设置 `run_in_background=true`。立即渲染该事件后保存 `after_seq`，若仍需轮询则运行 `<designkit> history-detail --room-id '<room_id>' --watch --yield-on-update --after-seq '<after_seq>' --download-dir '<任务工作目录>/designkit-artifacts'`。按此方式串行续查至 `reply` 或 `done`，任一时刻只能有一个查询命令，不创建第二个房间、不重复提交任务。

## 事件续跑

- `event=user_input_required`：存在选项预览时，先读取 `interaction.questions[].options[].artifacts`（兼容 `interaction.options[].artifacts`），把本事件实际返回的预览视为完整集合；预览总数允许为 0～4 张，必须逐项精确计数，禁止假设固定 4 张、等待不存在的第 4 张或继续轮询补齐。收到 `next_action=reply` 后，必须在当前模型轮次立即调用 `AskUserQuestion` 或等效原生选择器，禁止先结束为一条普通 assistant 消息、等待不会自动发生的下一模型轮次。有风格预览时，先在普通 assistant 正文中按选项顺序输出选项文字和 `![<title>](<media_url>)`。标题使用完整选项文字，`media_url` 必须逐字符使用该选项 artifact 的原始值，禁止改写、缩短、补全或丢失查询参数。禁止使用 HTML、`widget_guidelines` 或 `show_widget` 展示风格预览；禁止只在推理或工具参数中写 Markdown。不得为了打开卡片省略已有预览；预览不加入正式产物区，选择仍由 `AskUserQuestion` 完成。预览展示后，在当前模型轮次立即调用 `AskUserQuestion`，不结束当前轮次或等待下一轮。实际没有预览时直接询问，不补造图片。每个选项必须保留原始文字和 `option_id`。选项预览只用于辅助选择，不是正式产物；禁止把这些预览 `local_file` 传给 `present_files`，禁止打开文件卡、右侧产物区或浏览器标签。禁止使用 `show_widget` 的本地绝对路径渲染这些预览，WorkBuddy 无法把该路径转换为可访问图片。不要把完整产物 JSON 塞进选择弹窗，避免 WorkBuddy 长 JSON 截断。不存在预览时直接展示文字选项。禁止自动代选，原生交互能力不可用时才降级为编号列表。以下回答校验用于需要回复服务端的标准问询；`action_type=export_pptx` 且 `requires_server_reply=false` 的本地导出卡遵守其独立路由，关闭后不导出、不重新追问，不能发给reply。调用 `AskUserQuestion` 时只传 `questions`，禁止在工具调用参数中传入或预填顶层 `answers`；`answers` 只能来自用户实际提交后的工具结果，推荐项、历史偏好、模型判断和服务端默认值都不能代替用户选择。问题文字使用事件原始 `question`，每个可展示选项的 `label` 必须逐字符使用事件原始 `content`，禁止增加“推荐”、缩写、改写或重新排序。若服务端选项多于原生选择器上限，只展示选择器允许的原始选项，并在问题中说明可通过“其他”提交剩余选项的完整原文；禁止为了适配上限删除后自动代选。只有工具结果明确包含用户实际提交的选项文字或非空自由文本时才能继续；结果为空、关闭、取消、`[已跳过]` 或仍是预填/默认值时，都必须停留在当前交互并重新询问，禁止执行 `<designkit> reply`。先将用户结果与本题原始选项逐字符匹配；唯一匹配时使用该项自己的 `option_id` 和完整 `content`；禁止按序号猜测、使用第一个选项兜底或沿用上一次回答。未匹配选项时，若本题 `allow_user_input=true` 或本题没有选项，应视为用户自定义输入：原文通过 `--prompt` 回复，不传该题的 `--select-option-ids`；合并多题回复时，该题对应的选项 ID 数组为空。合法自定义输入无需与任何选项原文一致，也不得仅因措辞不同再次询问；例如用户在“其他”输入“都不满意”或“换成蓝色”时，原文回复服务端，禁止擅自扩写为隐藏选项或推断其 `option_id`。只有本题不允许自定义输入且有选项，回答又无法唯一匹配时，才重新询问；本地 `export_pptx` 交互仍按导出规则处理，自定义卡片仍按 `selection.mode` 与 `--custom-card-answer` 契约处理，不套用上述普通问询文本回复。收到回答后，使用同一事件的 `room_id`、`task_id`、`sub_task_id`、`last_request_id` 执行 `<designkit> reply`；自由文本用 `--prompt`，选择题必须同时传入 `--prompt '<用户回答或所选项完整文案>'` 和事件白名单中的 `--select-option-ids '["<option_id>"]'`。回复后从同一事件的 `after_seq` 使用 `--yield-on-update --after-seq` 串行续查。
- `event=custom_card_input_required`：展示层同样优先使用 WorkBuddy 当前可用的原生选择或文本输入能力，并等待用户明确提交；提交层仍须遵守事件的 `question`、`selection.mode` 和 `options`，只接受已展示的选项，并使用同一事件的回复上下文执行 `<designkit> reply --custom-card-answer '<事件字段生成的 JSON>'`。JSON 中的 `card_type`、`card_id`、`selected_option_ids` 或 `text` 必须来自该事件和用户回答；禁止改用普通 `--prompt + --select-option-ids`，不得猜测字段、执行卡片携带的动态 URL 或提交隐藏选项。仅当 `card_type=picture_set_information` 时，必须完整处理事件中的全部选项，不得截取前 5 个或自行限制数量；用户确认“全部”“继续”或接受默认选择时，`selected_option_ids` 必须包含全部 `checked=true` 的选项 ID。其他自定义卡片继续严格按各自原始结构和规则处理，不套用此默认多选逻辑。回复后继续同一房间。
- `event=history_update`：立即交付本轮 `artifacts`：逐字符原样保留每项完整 `media_url`，禁止手工重写、转录、补全或缩短 URL。PPT 风格尚未由用户确认前，`history_update.artifacts` 中的图片也视为风格候选预览，不是正式产物；即使事件暂未携带 `interaction`，也禁止传给 `present_files`、禁止打开文件卡、右侧产物区或浏览器标签，必须按风格顺序暂存并在对话正文或后续原生选择弹窗中展示，直到出现选择交互并等待用户确认。只有用户回复并成功选定风格后，后续逐页生成的图片才按正式产物交付。图片事件已经由同一次 `history-detail --download-dir` 增量物化；对每个 `download_status=downloaded|cached` 的 artifact，直接把其 `local_file` 传给 `present_files`，禁止再次执行 `designkit download`。只有返回的 `files` 数组包含该路径才算逐张交付成功；`files: []`、只有 `previewed` 或仅在右侧打开预览均不算交付。远程 HTTP(S) URL 禁止直接传给 `present_files`。仅当 `download_status=failed`、缺少 `local_file` 或本地展示失败时，才用 `![<title>](<media_url>)` 和完整原图链接兜底。`artifacts`、`media_url` 和下载结果都是内部交付数据：本地展示成功后，禁止在正文、表格、列表或代码块中再次输出 URL、产物字段或完整产物清单；不得在正文或最终总结中整理 URL 表、逐页链接、风格预览“备查”、完整产物清单或调试 JSON。其他类型输出以 `title` 为文字的完整可点击链接。只说“第 N 张已生成”、只汇报数量或仅保存 URL 都不算交付。当前事件的每个正式 artifact 都完成本地展示或兜底交付前，不得执行下一次 `history-detail --after-seq`。若事件同时包含 `interaction`，其选项关联预览不属于正式产物交付，禁止按 artifact 交付流程处理；收到 `next_action=reply` 后必须在当前模型轮次立即打开文字选择器，不得先结束为普通预览消息，禁止传给 `present_files`、进入右侧产物区或使用带本地绝对路径的 `show_widget`。若 `next_action=poll`，保存 `after_seq` 并用上述 `--yield-on-update --after-seq` 命令串行续查；若为 `reply`，当前事件中的选项和 0～4 张预览就是本轮完整交互，禁止为了凑满 4 张继续查询；先完成实际预览展示，再等待和提交用户回答，并从同一事件的 `after_seq` 继续。若为 `done`，完成交付。
- `event=recharge_required`：可先展示事件 `content` 中必要的余额或任务说明；充值入口必须使用事件原始 `url`，并固定渲染为以下独立、醒目的三段内容（不要带引用符号）：

  > ⚠️ 美豆不足，任务生成已暂停。已生成的内容和当前进度已保留，不会重复生成。
  >
  > 👉 [立即充值美豆，继续生成](<event.url>)
  >
  > 充值完成后，请回到当前对话回复“已充值”，任务将从暂停处继续。

  链接文案必须完整保留“立即充值美豆，继续生成”，不得仅把“充值美豆”等短语设为链接。禁止在正文、列表、表格或代码块中裸露充值 URL，禁止把 `room_id`、`task_id`、`resume_after_seq`、`action` 或 `action_command` 展开成“事件关键信息”，也不要在同一回复中重复给出第二套充值说明或多个恢复口令。“好了”或“继续任务”仍可在后台兼容识别，但面向用户只引导回复“已充值”；仅当当前任务仍有待处理的充值事件时才能触发恢复。随后依据结构化 `action` 校验目标，把事件的 `action_command`（即 `<designkit> resume`）作为前台首事件命令原样执行，禁止主动设置 `run_in_background=true`，并等待其退出，不得新建房间、重新执行普通 `chat` 或重复原 Prompt。没有待恢复事件时，“好了”等模糊表达不能触发恢复。
- `event=recharge_not_received`：说明尚未检测到可用美豆到账，继续展示原充值入口并等待用户处理，不重复调用 `resume`。
- `event=recharge_resumed`：这是续跑请求已被服务端受理的唯一凭据。只有收到该事件才能告知用户续跑已受理；先处理同一条 `resume` 命令随后返回的首个 `history_update`，按其 `artifacts`、`interaction`、`after_seq` 和 `next_action` 正常交付。若该命令只返回 `recharge_resumed` 而没有 `history_update`，才立即从事件的 `after_seq` 按上面的 `history-detail --watch --yield-on-update --after-seq` 流程继续增量查询。PPT 任务续查时保留 `--download-dir`，逐事件交付直至 `reply` 或 `done`，不得停在“正在执行中”、转成后台任务或要求用户再次回复。单独收到 `history_update/next_action=done` 不得描述为续跑已受理。
- `is_complete=true` 或 `next_action.action=done`：仅当没有仍有效的 `recharge_required` 时停止轮询，按“结果直接交付”整理 `artifacts`。订阅或充值引导优先于完成态；服务端 `card_detail.type=guide_purchase` 与 `type=self_define/sub_type=guide_purchase` 均由 CLI 归一为 `recharge_required`，不得忽略，也不得重复处理 `after_seq` 之前或已回复/已续跑的旧引导。仅当 `next_action=done`、事件不含 `terminal_notice` 且 `available_actions` 包含 `open_room` 时才展示房间入口：若同一事件还包含 `export_pptx`，在最终回复末尾逐字追加且只追加 `也可点击进入 [美图设计室](<room_url>)，对版式和文字进行精细调整。`；否则逐字追加且只追加 `本次结果已同步至 [美图设计室](<room_url>)，可在线查看或继续编辑。`。其中 `<room_url>` 必须原样使用同一事件字段；禁止改写、扩写、混用两套文案、替换为“右侧预览/下载”等说明，也禁止在面向用户的完成总结中展示本地绝对路径。异常终态继续展示审核、失败或客服信息，不得使用成功完成文案。`next_action=poll` 和 `next_action=reply` 均不得展示房间入口，也不得根据 `room_id` 自行拼接链接。


## PPT 逐页交付

- `history_update.artifacts` 是本次游标之后的新产物，不在 WorkBuddy 内累计或转存整段历史 JSON。每处理一个事件就立即逐项展示，然后仅保留 `room_id` 和 `after_seq` 供下一次查询。
- 风格未确认前，服务端可能把 0～4 张候选风格预览作为普通 `history_update.artifacts` 分批返回；只在 `next_action=poll` 时按 `after_seq` 继续收集。出现 `next_action=reply` 后，以该事件选项实际关联和此前累计的预览为本轮完整集合，禁止假设固定 4 张、等待不存在的图片或继续轮询补齐。收到 `next_action=reply` 后必须在当前模型轮次立即展示文字选择器；有风格预览时，先在普通 assistant 正文中按选项顺序输出选项文字和 `![<title>](<media_url>)`。标题使用完整选项文字，`media_url` 必须逐字符使用该选项 artifact 的原始值，禁止改写、缩短、补全或丢失查询参数。禁止使用 HTML、`widget_guidelines` 或 `show_widget` 展示风格预览；禁止只在推理或工具参数中写 Markdown。不得为了打开卡片省略已有预览；预览不加入正式产物区，选择仍由 `AskUserQuestion` 完成。预览展示后，在当前模型轮次立即调用 `AskUserQuestion`，不结束当前轮次或等待下一轮。实际没有预览时直接询问，不补造图片。这些图片一律不是正式产物，禁止使用带本地绝对路径的 `show_widget`，禁止传给 `present_files`，禁止打开文件卡、右侧产物区或浏览器标签。只有用户回复并成功选定风格后，后续逐页生成图片才进入正式产物交付。
- 每个正式新增图片事件返回后，直接读取该事件由 `--download-dir` 生成的 `local_file` 并传给 `present_files`；禁止再次执行 `designkit download`。成功展示后才能续查，不得等全部 PPT 页面完成后再批量展示。
- `media_url` 必须从事件逐字符原样复制，禁止模型手工重写或转录。远程 HTTP(S) URL 禁止传给 `present_files`；`previewed` 不等于聊天内产物。本地展示失败时用 `![<title>](<media_url>)` 和完整原图链接兜底。
- `artifacts` 和 `media_url` 只用于内部匹配与交付。图片已通过 `present_files` 成功展示后，不得在对话正文、表格、列表、代码块或最终总结中再次打印 URL、逐页链接、风格预览链接或完整产物清单；只有对应图片本地交付失败时才单项使用 Markdown 兜底，不得汇总成 URL 表。
- `interaction.questions[].options[].artifacts` 以及风格确认前累计到的 `history_update.artifacts` 都是风格选择预览，不是最终产物。收到 `next_action=reply` 后，必须在当前模型轮次直接调用 `AskUserQuestion`；有风格预览时，先在普通 assistant 正文中按选项顺序输出选项文字和 `![<title>](<media_url>)`。标题使用完整选项文字，`media_url` 必须逐字符使用该选项 artifact 的原始值，禁止改写、缩短、补全或丢失查询参数。禁止使用 HTML、`widget_guidelines` 或 `show_widget` 展示风格预览；禁止只在推理或工具参数中写 Markdown。不得为了打开卡片省略已有预览；预览不加入正式产物区，选择仍由 `AskUserQuestion` 完成。预览展示后，在当前模型轮次立即调用 `AskUserQuestion`，不结束当前轮次或等待下一轮。实际没有预览时直接询问，不补造图片。禁止只在推理或工具参数中写 Markdown，禁止使用带本地绝对路径的 `show_widget`，禁止传给 `present_files`，禁止打开文件卡、右侧产物区或浏览器标签。
- CLI 会依据 `after_seq` 过滤已经交付过的 URL。最终 `agent_artifact` 再次列出已展示页面时不得重复渲染；其中出现新 URL 时仍须逐张补交。


完成事件的 `available_actions` 包含 `export_pptx` 且 `interaction.action_type=export_pptx` 时，必须在同一轮完成 PPT 专属房间引导后立即调用 WorkBuddy 当前可用的 `AskUserQuestion` 或等效原生单选工具，禁止把选项改写成普通 assistant 文字列表、只提示用户手动回复或直接结束任务。`next_action=done` 只表示服务端生成结束，不得据此忽略这个本地导出交互。卡片只包含一个问题：`header` 使用“PPTX导出”，`multiSelect=false`；问题使用 `interaction.question`，选项严格按 `interaction.options` 原顺序映射，并保留对应 `option_id`。每个卡片选项的 `label` 必须逐字符使用完整的 `options[].content`，包括括号内的推荐标识、耗时、可编辑性和排版风险，禁止提炼、缩写、删除括号或只取“导出展示型 PPTX”“导出可编辑 PPTX”等短标题；`description` 仍逐字符使用 `options[].description` 作为可选副说明，但宿主不展示副说明时，主 `label` 也必须独立表达完整差异。当前三项应显示为 `导出展示型 PPTX（推荐，约 30 秒，还原度高，不可编辑）`、`导出可编辑 PPTX（约 1～5 分钟，文字/排版可编辑，可能少量错位）`、`暂不导出（在线查看即可）`。不得自动选择推荐项，必须等待用户明确提交；展示卡片本身不算导出请求，用户选择展示型或可编辑型才算明确请求。用户选择 `display` 时复用完成事件的 `room_id` 执行 `<designkit> export-pptx --room-id '<room_id>' --mode display --output-dir '<目标目录>'`；选择 `editable` 时执行同一命令的 `--mode editable`；选择 `none`、关闭卡片或选择“暂不导出”时不执行导出且不再追问。这个交互的 `requires_server_reply=false`，禁止把选择提交给 `reply`、`chat` 或 `--select-option-ids`，不得创建新房间或重新生成 PPT。原生单选工具确实不可用，或旧 CLI 只有 `available_actions=export_pptx` 而没有上述 `interaction` 时，才降级为文字提示并引导用户直接回复“导出展示型 PPTX”或“导出可编辑 PPTX”。用户后续自由文本明确要求导出时仍按相同模式复用原房间；当前上下文没有可确认的已完成 PPT 房间时，只询问用户需要导出哪个任务，不得擅自选择其他房间。

## 结果直接交付

- 对 PPT 流式任务执行严格的“逐张本地展示后续查”门禁：每个新增正式图片 artifact 返回后直接使用同一事件中的 `local_file`，并只把该事件对应的本地绝对路径传给 `present_files`；成功后才能读取下一事件。远程 URL 禁止传给 `present_files`，因为 `previewed` 不等于产物；本地物化或展示失败时才用原样 Markdown 图片和完整链接兜底。选项风格预览不属于正式产物，必须作为选项预览进入选择弹窗，禁止传给 `present_files` 或加入右侧产物区。
- `artifacts`、`media_url`、下载结果和本地路径都是内部交付数据，不是面向用户的报告内容。确保每一项存在可用地址的正式产物都通过文件卡、图片预览或单项兜底完成交付；选项风格预览只在选择弹窗或对话正文辅助选择，禁止进入右侧产物区，也禁止整理为表格、链接列表、逐页清单、风格预览“备查”或调试 JSON。
- 每张图片通过 `present_files` 成功进入 WorkBuddy 产物后即视为已交付，最终回复不得再次输出该图片的 Markdown、远程 URL 或本地路径，也不得再次按页罗列全部产物。
- 只有某一图片无法完成本地交付时，才对该图片单独使用 `![<title>](<media_url>)` 及完整原图链接兜底并说明失败；不得把正常产物一并降级为 URL 表。用户明确索要原始链接时除外。
- 最终回复只做简短结果说明，并按可用操作追加规定的房间入口与 PPTX 提示；文件卡和图片预览本身就是产物入口，不再用文字重复。
- 按 `media_type` 选择入口：图片需可查看原图，视频和音频需可播放或下载，文档、压缩包及其他文件需可打开或下载。`media_cover_url` 只能作为封面或图片地址兜底，不能代替视频、音频或文件本体的 `media_url`。
- `present_files` 只接收下载成功的本地绝对路径，不接收远程 URL。只有工具结果的 `files` 数组包含预期本地文件才算加入 WorkBuddy 产物；`previewed` 数组不算附件或产物。
- 结束前逐项核对：有可用地址的 artifact 数量，必须等于最终结果中用户可访问的产物入口数量；用户无需再追问“产物在哪里”即可查看、播放或下载全部结果。URL 查询参数不得截断或删除；没有可用地址时明确说明暂未取得可交付产物，不得虚构完成。
- 风格未确认前的 `history_update` 图片一律按候选预览处理，禁止把这些 `local_file` 传给 `present_files`，禁止打开文件卡、右侧产物区或浏览器标签；必须等用户确认风格后，才把后续逐页生成图片作为正式产物交付。对正式产物阶段每个含新增图片的 `history_update`，直接把该事件中 `download_status=downloaded|cached` 的 `local_file` 立即传给 `present_files`，禁止再次执行 `designkit download`；只有返回的 `files` 数组包含这些路径才算进入 WorkBuddy 产物。`files: []`、只有 `previewed` 或 `Successfully opened ... preview(s)` 均表示交付失败，必须纠正后再结束或等待用户。当前事件正式产物交付成功前不得续查下一游标。若同一事件含选项预览，必须先随选项在原生选择弹窗中展示预览，禁止把预览传给 `present_files`；不得积攒到交互或终态后批量展示。不得绕过 CLI 使用 `curl` 下载。`download_status=failed`、缺少 `local_file` 或入产物失败时仍须保留原样内联图片和完整 URL，并明确报告失败项。当前对话最近一次完成事件的 `available_actions` 包含 `export_pptx`，且用户明确要求把当前 PPT 下载、导出或保存为 PPTX 时才执行导出。用户明确说“可编辑”“文字可编辑”“源文件”或“分层 PPT”时执行 `<designkit> export-pptx --room-id '<room_id>' --mode editable --output-dir '<目标目录>'`；用户说“展示型”“一比一”“保真”，或只说“导出 PPTX”“下载 PPT”“导出文件”等未指定模式的意图时，执行 `<designkit> export-pptx --room-id '<room_id>' --mode display --output-dir '<目标目录>'`。此续轮导出必须复用该完成事件的 `room_id`，跳过表单读取、字段追问、`create-room` 和 `chat`，不得重新生成 PPT。如果当前上下文没有可确认的已完成 PPT 房间，只询问用户需要导出哪个任务，不得擅自选择其他房间。命令成功后必须把 JSON 中 `file` 指向的唯一 `.pptx` 文件作为可操作附件交付，只输出本地路径不算完成交付。展示型交付时说明它一比一还原但不可逐元素编辑；可编辑型交付时说明可能存在字体替换、文字错乱或轻微排版偏差。可编辑结果的 `fallback_page_count` 大于 0 时，必须原样告知 `warning` 和兜底页数；导出失败时不得擅自切换为另一模式。导出失败只重试导出，不重新生成 PPT；不得绕过 CLI 下载页面或自行拼装 PPTX。
- 面向用户隐藏 `room_id`、`task_id`、`sub_task_id`、`last_request_id`、原始调试 JSON以及 Token、Cookie、API Key 和认证相关签名参数。PPT 流式任务按本节规则隐藏已成功本地交付的产物 URL；其他任务仍原样展示交付 URL。

## 失败与安全

- 必填字段、附件或合法选项缺失时停止提交，只询问当前最关键的缺失信息。
- 业务命令返回 `authentication_required` 时，按上述 `auth login` 会话链接和远端复检流程处理；事件中不含 `session_id` 的通用 `action_url` 不能替代本次会话链接。最多恢复并重试原命令一次。
- 网络失败或轮询超时只恢复查询，不重复创建可能消耗额度的任务。
- 不输出或保存 Token、Cookie、API Key、认证相关签名参数和内部调试信息；产物地址按“结果直接交付”的任务类型规则处理。
