# 安全与执行边界（SECURITY）

本文件说明 dsh-research-suite 的信任边界、工具能力矩阵、代码执行半径与隔离建议。按「实现是什么」写，不按「希望它是什么」写：凡是与实现相反的绝对表述（例如「不联网」「只读」），都不应该出现在本插件任何对外文档里。

## 一、威胁模型

**被执行的脚本 = 不可信输入。** `research_run` 接收的 R / Python 代码由模型生成，模型又受用户诉求、第三方技能原文与文件内容影响。因此脚本必须当作「可能是恶意的」处理，而不是当作「用户自己写的、一定安全」。

主要攻击面：

| 攻击面 | 具体表现 | 本插件的处置 |
| --- | --- | --- |
| 脚本外联 | `system()`、`download.file()`、`requests`、`socket` 把数据发出去或拉回载荷 | 默认 `allowNetwork:false` 静态拒绝；执行开关默认关 |
| 脚本越界写 | 写 `~/.ssh/authorized_keys`、改 `.Rprofile`、覆盖系统文件 | 写调用只允许执行目录内相对路径；绝对路径、`~`、`..` 一律拒绝 |
| 脚本读敏感文件 | 读患者名单、身份证表、PHI 目录 | `denyPathPatterns` 关键词拒绝；真正的隔离靠受限用户/容器（见第四节） |
| 装包与破坏系统 | `install.packages()`、`pip install`、`rm -rf` | 永久拒绝，与执行开关无关 |
| 提示注入 | 第三方技能原文/资产里夹带「忽略之前的指令」 | 原文按资料读，不按指令执行；工具不因文档内容扩大权限 |
| DOI 核验外联 | `research_doi_check` 向 Crossref 发请求 | 只发送 DOI 本身，不发送稿件正文；无 DOI 需求时不要调用 |

**明确不承诺的事**：本插件的静态扫描不是沙箱，不能保证拦住所有绕过手法（例如运行时拼接字符串、`get()` / `eval()` 动态求值、经白名单包间接触发的外部调用）。真正的隔离只有「受限用户 / 容器 / 虚拟机」能提供（第四节）。

## 二、工具能力矩阵

「作用半径」= 该工具能影响到的最大范围。所有工具都在插件进程内运行，只有 `research_run` 会起子进程、只有 `research_doi_check` 会主动联网。

| 工具 | 读文件 | 写文件 | 联网 | 子进程 | 作用半径 |
| --- | --- | --- | --- | --- | --- |
| `research_playbook` | 是（`data/capabilities/*.json`） | 否 | 否 | 否 | 进程内，只读能力卡 |
| `research_capability` | 是（能力卡） | 否 | 否 | 否 | 进程内，只读单张能力卡 |
| `research_catalog` | 是（`knowledge/` 索引与技能目录） | 否 | 否 | 否 | 进程内，只读索引 |
| `research_kb_read` | 是（`knowledge/skills/` 原文与 `<slug>__assets/` 内资产） | 否 | 否 | 否 | 进程内；路径被约束在知识库目录内 |
| `research_standard` | 是（`references/`） | 否 | 否 | 否 | 进程内，只读规范 |
| `research_gate` | 否（只分析传入文本） | 否 | 否 | 否 | 进程内，纯文本检查 |
| `research_suite_status` | 是（索引、统计、策略） | 否 | 否 | 是（仅 `where` / `which` 探测解释器） | 进程内 + PATH 探测 |
| `research_data_check` | 是（调用方指定的数据文件） | 否 | 否 | 否 | 进程内，只读该文件 |
| `research_output_check` | 是（调用方指定的图片/文档） | 否 | 否 | 否 | 进程内，只读该文件 |
| `research_doi_check` | 否 | 否 | **是**（`api.crossref.org`） | 否 | 外发 DOI 字符串；只读响应 |
| `research_ref_audit` | 否（只分析传入文本） | 否 | 否 | 否 | 进程内，纯文本检查 |
| `research_run` | **是**（解释器以当前用户身份可读的一切） | **是**（执行目录内；策略拦截越界写） | 默认 **否**（策略拒绝；开启后由脚本行为决定） | **是**（Rscript / python） | 执行目录 + 解释器在当前用户权限下能触达的一切 |

关键结论：

1. **默认情况下不会执行任何脚本。** `data/exec-policy.json` 的 `run.enabled` 出厂为 `false`，此时 `research_run` 只返回预览（脚本前 60 行 + `previewHash` + 策略摘要 + 预计拦截项），不落盘、不起子进程。
2. **开启执行后，脚本以你的用户权限运行**，不是以插件进程的受限身份运行。它能做你的账号能做的事，只是本插件会先做一轮静态拦截。
3. **`research_doi_check` 确实联网**，请求 `https://api.crossref.org/works/<doi>`，只发 DOI，不发本地文件内容。不使用 DOI 核验时不要调用它。

## 三、执行半径

开启执行后，每次运行的落点是：

```text
<当前工作目录>/.dsh-research/run/<runId>/
├── script-<runId>.R        # 或 .py，UTF-8 无 BOM
└── …                        # 脚本自己写出的相对路径产物
```

- `workdir` 参数只能是相对路径，且不能包含 `..`；解析后必须仍在本目录内，越界直接拒绝。
- 脚本写入的路径只允许相对路径：`write.csv("out/x.csv")` 可以，`write.csv("C:/x.csv")`、`write.csv("../x.csv")`、`write.csv("~/x.csv")` 会被拒绝。
- 运行产物清单（文件名、字节数、修改时间）会随结果返回，便于核对「脚本到底改了什么」。
- 超时与输出上限由策略控制：默认 120 秒、单次 stdout/stderr 1 MB，超过即终止。

## 四、三层隔离建议

| 层级 | 做法 | 能挡住什么 |
| --- | --- | --- |
| 第一层：本机开关（默认已开） | 保持 `run.enabled:false`，只在需要真跑统计时临时打开 | 绝大多数「顺手跑一下」的场景，完全不起子进程 |
| 第二层：策略与目录约束（默认已开） | 包白名单、网络禁令、写半径、PHI 关键词、超时与输出上限 | 常见的越权写、外联、装包；防不住精心构造的绕过 |
| 第三层：真正的隔离（建议自建） | 在容器、受限用户或虚拟机里跑 DSH；把工作目录挂载成可丢弃卷 | 进程级逃逸、读取宿主敏感文件、持久化后门 |

对处理患者数据的机器，**第三层是必须项**：本插件是科研写作工具，不是数据处理合规系统。

## 五、PHI 与敏感目录

- 默认拒绝关键词：`patient`、`患者`、`病历`、`phi`、`idcard`、`身份证`（`data/exec-policy.json` 的 `denyPathPatterns`，大小写不敏感）。脚本文本里出现即拒绝运行。
- **不要把患者数据目录放在执行工作目录内**。静态关键词只能拦「脚本里写出来的路径关键词」，拦不住「脚本遍历某个目录再挑文件」。处理 PHI 的正确做法是：数据放在受限用户/容器之外，执行环境只挂载脱敏后的副本。
- 需要更严时可以往 `denyPathPatterns` 里加自己机构的目录名与字段名；加得越多，误伤正常脚本的概率也越高，建议只加真正致命的词。

## 六、执行策略文件

`data/exec-policy.json` 是唯一的策略入口（缺失或损坏时按「全关」处理，不会因为读不到配置就放开执行）。

| 字段 | 默认值 | 含义 |
| --- | --- | --- |
| `run.enabled` | `false` | 是否允许真正执行；`false` 时只预览 |
| `run.requireConsent` | `true` | 是否要求预览后显式确认（保留位，当前由 `confirm` 参数强制） |
| `run.allowNetwork` | `false` | 是否允许脚本调用网络/子进程类 API |
| `run.workdir` | `.dsh-research/run` | 相对执行目录 |
| `run.timeoutMs` | `120000` | 单次执行超时上限 |
| `run.maxOutputBytes` | `1048576` | 单次 stdout/stderr 上限 |
| `runtimes.r` / `runtimes.python` | `null` | 解释器绝对路径；留空则按环境变量与 PATH 探测 |
| `allowedPackages.r` / `allowedPackages.python` | 见文件 | 唯一允许导入的包白名单 |
| `denyPathPatterns` | 见文件 | 出现即拒绝的敏感路径关键词 |

开启执行的最小步骤：

```json
{ "run": { "enabled": true } }
```

保存后不需要重启插件（每次调用都会重新读策略）。**开启意味着脚本以你的用户权限运行**，确认自己接受这个半径再开。

解释器探测顺序（`detectRuntimes()`，`research_suite_status` 会展示结果）：

1. `data/exec-policy.json` 的 `runtimes.r` / `runtimes.python`；
2. 环境变量 `R_HOME`（R）、`PYTHON` / `CONDA_PREFIX`（Python）；
3. PATH 探测（Windows 用 `where`，其它平台用 `which`）。

三者都找不到时返回 `runtime_missing` 与三条可执行建议，不抛异常。

## 七、返回字段与审计线索

一次执行会回传这些可用于事后核对的字段：

| 字段 | 含义 |
| --- | --- |
| `previewHash` | 预览时脚本的 sha256；执行时必须与当前代码一致 |
| `runId` | 本次运行标识，执行目录名同源 |
| `script` / `workdir` | 脚本绝对路径与执行目录绝对路径 |
| `command` | 可直接粘贴复现的完整命令 |
| `exitCode` / `signal` / `timedOut` | 退出状态与超时标记 |
| `stdout` / `stderr` | 截断后的输出 |
| `files` | 执行期间新增或修改的文件（路径、字节数、修改时间） |
| `violations` | 静态扫描命中的策略项（`kind` / `detail` / `line`） |

当前版本**不写持久化审计日志**：字段随工具结果返回，是否留档由使用方决定（例如把 `runId` 与 `previewHash` 记进实验记录）。这一点不要按「已有审计日志」宣传。

## 八、已知限制

1. 静态扫描是启发式规则，不是沙箱；绕过手法（字符串拼接、动态求值、白名单包内部外联）无法静态穷尽。
2. `allowNetwork:false` 只拦常见网络 API，不拦经白名单包间接发起的请求；需要强保证时用容器断网。
3. 包白名单按「导入名」判定：`library(pkg)`、`pkg::fn()`、`import pkg`、`from pkg import`；别名与动态 `library()` 参数可能绕过。
4. 不校验脚本计算结果是否正确——`research_data_check` 等工具只做机械项，统计方法判断仍要人工。
5. `research_doi_check` 依赖 Crossref 可用性；网络不通时返回降级结果，不给「假通过」。

## 九、报告安全问题

发现绕过手法或策略缺陷，请开 issue 并附最小复现代码与 `runId`（如果没有真正执行，附 `previewHash` 与 `violations` 输出即可）。仓库：<https://github.com/xuzhecomeon/dsh-research-suite>。
