# 发布手册（PUBLISH）v3.0.0

面向维护者：怎么把 `dsh-research-suite` 打包、发 npm、发 GitHub、装进 DSH、升级、回滚、排障。所有命令都在**包根目录**执行（`package.json` 所在目录）。

## 〇、发布前必须先知道的事实

| 项 | 值 |
|---|---|
| 包名 | `dsh-research-suite`（无 scope） |
| 当前版本 | `3.0.1`（v2.0.0 / v3.0.0 已发 GitHub / 市场 PR 待合并） |
| Node `engines` | `^22.19.0 \|\| >=24.0.0` |
| DSH `engines` | `>=0.2.0-0 <0.3.0`；`dsh.testedWith` = `0.2.1-rc.5`、`0.2.2-rc.1`（0.2.2-rc.1 是当前桌面版，工具注入时序已适配） |
| 许可证 | MIT |
| `files` 白名单 | `lib`、`data`、`skills`、`knowledge`、`references`、`scripts`、`docs`、`cordis.patch.yml`、`icon.svg`、`README.md`、`README.zh-CN.md`、`CHANGELOG.md`、`LICENSE` |
| 包体（实测口径） | v3 中间态：仓库目录 4577 files / 38.62 MB（能力卡与账本全部交付后以重跑 `verify-package.mjs` 为准）。其中 `knowledge/` 含 450 篇原文 + 186 个技能自带的 954 个资产文件（约 6.8 MB）——**这是设计如此，不要优化掉**；v2 的 773 files / 11.24 MB 只含 719 篇原文，无资产 |
| 入口 | `lib/index.js`（`"type": "module"`，`exports` 只暴露 `.`、`./cordis.patch.yml`、`./package.json`） |
| bundle patch | `cordis.patch.yml`，由 `package.json` 的 `dsh.bundle.patch` 指向 |
| 打包脚本 | `npm test`（selftest）、`npm run verify`（verify-package）、`npm run verify:caps`、`npm run pack:check`；账本校验无 npm script，直接 `node scripts/verify-ledger.mjs all` |

## 一、对外发布前要确认的元信息

仓库已是真实地址：`https://github.com/xuzhecomeon/dsh-research-suite`（`package.json` 的 `repository.url` / `homepage` / `bugs.url` 都已指向它，v2.0.0 已按此发过一次）。v3 复推前只需确认两处，**不需要再改仓库地址**：

| 位置 | v3 现状 | 是否要改 |
|---|---|---|
| `package.json` → `repository.url`（`bugs.url`、`homepage` 同步） | `git+https://github.com/xuzhecomeon/dsh-research-suite.git` | 不改；换账号/换仓库名时才改 |
| `package.json` → `author` | `{"name": "dsh-research-suite contributors"}` | 可选：想署个人名/邮箱时改 |
| `README.md`、`README.zh-CN.md` 顶部徽章链接 | 已指向 `xuzhecomeon/dsh-research-suite` | 不改；换仓库时同步 |

改完自查（应零命中）：

```powershell
Select-String -Path package.json,README.md,README.zh-CN.md -Pattern 'your-org|<owner>'
```

`dist/awesome-dsh-plugin-entry.yml` 里的 `<owner>` 是市场投稿用的，与仓库无关（见 §九）。

## 二、本地自检（全程不联网）

```powershell
node scripts/verify-capabilities.mjs all
node scripts/verify-ledger.mjs all
node scripts/verify-package.mjs
node scripts/selftest.mjs
```

四条都必须 `exit 0`（快捷方式：`npm run verify:caps`、`npm run verify`、`npm test`；账本无 npm script，直接 `node scripts/verify-ledger.mjs all`）。它们查的是**机械可判**的东西：

- `verify-capabilities.mjs`：10 个域的能力卡是否合 `docs/CAPABILITY-SPEC.md` §3.1，包括技能名是否真在 `knowledge/catalog.json` 里（防编造）、`detail` 是否够 40 字、能力数是否落在域区间内。
- `verify-ledger.mjs`：`data/ledger/<domain>.json` 是否把该域 `knowledge/catalog.json` 里的每个源技能都判定了（一条不多一条不少）、`verdict` 是否四类之一、`fused` 的每条是否能在 `data/capabilities/<domain>.json` 的 `members[].skill` 里核到。源清单默认读包内 catalog，所以 CI 上可跑。
- `verify-package.mjs`：`package.json` 必填字段与 `files` 白名单实际存在性、`main` 文件、`cordis.patch.yml` 结构、入口是否 import 了 `@deepseek-ai/*`、`skills/*.md` 的 frontmatter 与编码、所有 `data/`+`knowledge/` 的 JSON 可解析性、catalog 里每个 `file` 是否真实存在、**资产目录与 catalog 的 `assets.files/bytes` 是否逐条一致**、**账本 JSON 结构**、**catalog 里有没有带引号的技能名**、版本一致（`package.json` / `CHANGELOG.md` / 能力卡）、`references/` 编号连续、`docs/` 无空文件、包体统计。
- `selftest.mjs`：不启动 DSH 的加载期 smoke test——用假 ctx 调 `apply()`，验入口契约、技能是否内联 `content`、12 个工具的形态与真实执行、策略段铁律、数据面完整性。

**不要**在校验脚本里调 `npm`——包体清单由 CI 单独跑 `npm pack --dry-run`，避免本地 npm 配置污染结果。

## 三、npm 发布

### 3.1 首次发布

```powershell
npm login                 # 确认登录的是目标账号
npm publish --dry-run     # 先看清单，确认 knowledge/ 与 references/ 都在
npm publish --access public
```

#### 3.1.1 2026-11 实测：发布已强制 2FA，且新包首发会被自动暂存

下面这套是 2026-11-07 在 `dsh-research-suite@3.0.1` 上逐条试出来的，照抄可复现：

**① 令牌必须是「Granular + Bypass 2FA」**

npm 现在的策略是（[官方文档](https://docs.npmjs.com/requiring-2fa-for-package-publishing-and-settings-modification)）：**所有包发布都需要 2FA，或一个勾了 Bypass 2FA 的 granular token**。踩到的三种失败形态：

| 令牌形态 | 结果 |
|---|---|
| 什么都没有 | `E401 Unauthorized` |
| Classic `Publish` 令牌 | `E403 Two-factor authentication or granular access token with bypass 2fa enabled is required to publish packages` |
| 同上 + `--otp=<码>` | **还是同一个 E403**。该 403 响应不带 `www-authenticate` 挑战头，所以 `--otp` 永远不生效，填假码和填真码报错一模一样 |
| 浏览器 `npm login --auth-type=web` 的会话令牌 | 能 `whoami`，发布仍是同一个 E403 |
| **Granular Access Token + 勾 Bypass 2FA** | ✅ 通过 |

生成路径：npmjs.com → 右上角头像 → **Access Tokens** → Generate New Token → **Granular Access Token** → Permissions 选 **Read and write (publish and stage)**（不是 stage only）→ 勾 **Bypass two-factor authentication (2FA)** → Generate。

> 如果账号的 2FA 是 **security key / passkey**（`Account` 页显示「1 security key」），CLI 永远拿不到 6 位 TOTP，`--otp` 这条路直接不存在，只能走 granular bypass 令牌。**这类令牌从 2027-01 起不能再直接发布**，届时应改用 Trusted Publishing（见 §3.2）。

**② 新包首发会被 registry 自动暂存（约 6 分钟）**

`npm publish` 返回 `+ dsh-research-suite@3.0.1`、exit 0，但 registry 上先只出现一个占位版本：

```
versions: 0.0.0-stage      # stub:true，只有 package.json + README（340 B）
description: Temporary package placeholder for staged publishing
```

此阶段再发同版本会得到 `E409 Cannot publish over previously staged version "3.0.1"`，而 `npm stage list` 是**空的**——**这不是需要你去 Approve 的暂存**（`maintainer approve` 只属于显式 `npm stage publish` 的流程），而是 npm 对新包的自动处理队列，等就行。实测时间线：

```
04:05:07Z  placeholder 0.0.0-stage 出现
04:11:21Z  3.0.1 上线（6 分 14 秒），dist-tags.latest 自动指向 3.0.1
```

**③ 上线后把占位版标为废弃**，避免别人 `npm i <包名>` 装到空壳：

```powershell
npm deprecate dsh-research-suite@0.0.0-stage "placeholder version created by npm staged publishing, do not install"
```

**④ 回读验证（不要只看 CLI 的 `+ name@version`）**

```powershell
npm view dsh-research-suite versions --prefer-online   # 必须看到 3.0.1
npm pack dsh-research-suite@3.0.1                      # 从 registry 拉真包
tar -xzf dsh-research-suite-3.0.1.tgz -C <空目录>      # 解包后跑四件套，必须全过
```

2026-11-07 实测：registry 上的 tarball `12,671,464 B / 4584 files / unpacked 16.2 MB / MIT`；解包后 `selftest 66 项`、`103 capabilities`、`444 entries`、`verify-package 0 errors` 全部通过。

无 scope 的包默认就是 public。当前 `package.json` **没有** `publishConfig` 字段；如果希望把发布策略显式写进包（也避免以后误加 scope 后行为变化），可以补一段：

```json
"publishConfig": {
  "access": "public"
}
```

### 3.2 用 CI 发（推荐，带 provenance）

`.github/workflows/ci.yml` 的 `publish` job **默认只支持一种触发条件**：

- 在 GitHub Actions 页面手动 `workflow_dispatch`。

> **为什么不是打 tag 就发**：本仓库尚未配置 secret `NPM_TOKEN`。若保留「打 tag 自动发布」，任何一次 `git push origin v*` 都会因 401 失败，把 Actions 整片刷红，反而掩盖真正的错误。因此 `publish` job 的 `if` 被改成只认 `workflow_dispatch`。
>
> **要恢复 tag 触发**：先在仓库 Settings → Secrets and variables → Actions 里加 `NPM_TOKEN`，再把 `ci.yml` 中 `publish` job 的 `if` 改回
> ```yaml
> if: startsWith(github.ref, 'refs/tags/v') || github.event_name == 'workflow_dispatch'
> ```
> 提醒：**打 tag 本身不会发 npm**，它只是给提交打版本标记、生成 Release；发 npm 是另一件事。

该 job 走 `npm publish --provenance`，需要仓库 secret `NPM_TOKEN`（Automation 类型 token），并且 `permissions` 里有 `id-token: write`。**不要在 workflow 文件里写 token 明文**——只引用 `${{ secrets.NPM_TOKEN }}`。

provenance 要求构建产物与源码可追溯：公开发布时确保 tag 与 `package.json` 的 `version` 完全一致（v3 就是 tag `v3.0.0` ↔ `3.0.0`）。发 npm 时若走 tag 触发，CI 的 publish job 里有一步硬校验 tag 与 `package.json.version`，不一致直接拒绝发布。

### 3.3 发完之后确认

```powershell
npm view dsh-research-suite version dist.tarball
```

## 四、GitHub 仓库与 CI 徽章

1. 建仓库 → 推 `main` → 确认 Actions 的 `verify` job 绿。
2. `Settings → Secrets and variables → Actions` 加 `NPM_TOKEN`（同名 secret，仅 `publish` job 用）。
3. 保护 `main`：要求 PR + `verify` 通过才能合（CI 里已有 `pull_request` 触发，可直接作为必需检查）。
4. README 顶部徽章（`<your-org>` 替换成真实组织）：

```markdown
[![CI](https://github.com/<your-org>/dsh-research-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/<your-org>/dsh-research-suite/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/dsh-research-suite.svg)](https://www.npmjs.com/package/dsh-research-suite)
[![license](https://img.shields.io/npm/l/dsh-research-suite.svg)](LICENSE)
```

徽章只在仓库公开且有 CI 运行记录后才显示正常；仓库私有或从未跑过 Actions 时徽章会显示 "no status"。

## 五、装进 DSH 的两条路径

装完**必须完全退出 DSH Desktop（不是关窗口，是退出进程）再启动**，loader 只在启动时读 patch。

### 5.1 plugin_manager（推荐，GUI）

`plugin_manager` 工具，`action: "install_bundle"`，`target` 传**绝对包目录**：

```
D:\workbuddy\2026-11-04-20-37-51\2026-11-04_2229\dsh-research-suite
```

也可以从 npm 装（`install_bundle` 的 target 传包名/安装 spec，例如 `dsh-research-suite@3.0.0`）。装完按提示重启。

### 5.2 CLI

```powershell
dsh.cmd plugin --profile desktop add <绝对包目录或包名>
```

装完完全退出并重启 DSH Desktop。

### 5.3 装完怎么确认真的生效

```powershell
# ① 插件是否进了 profile 的依赖
Select-String -Path "$env:DSH_HOME\profiles\desktop\package.json" -Pattern 'dsh-research-suite'

# ② 是否真的装进 node_modules
Test-Path "$env:DSH_HOME\profiles\desktop\node_modules\dsh-research-suite\package.json"

# ③ profile 的 patch 里有没有 insert 行
Select-String -Path "$env:DSH_HOME\profiles\desktop\cordis.patch.yml" -Pattern 'dsh-research-suite'
```

三条都命中，再去会话里让模型调 `research_suite_status` —— 它返回版本、10 个域的能力卡数量、450 条技能索引与资产收录统计（`knowledge/stats.json`）、references 是否齐全、包根路径。这是最终验收口径。

`$env:DSH_HOME` 默认是 `~/.dsh`；本机被重定向到 `D:\nodehome\.dsh`，命令里统一用环境变量，不要写死路径。

## 六、升级与回滚

### 6.1 升级（发新版本）

版本号必须**四处同步**，`verify-package.mjs` 会拦不一致：

1. `package.json` → `version`
2. `CHANGELOG.md` → 最新 `## x.y.z` 标题
3. `data/capabilities/*.json` → 每个文件的 `version`
4. git tag `vx.y.z`（与 `version` 一致）

```powershell
node scripts/verify-capabilities.mjs all    # 能力卡契约
node scripts/verify-ledger.mjs all          # 450 条判定账本覆盖与 fused 可核
node scripts/verify-package.mjs             # 版本一致性必须 0 error
npm pack --dry-run                          # 看清单与体积（v3 约 38 MB 解包量级）
git tag v3.0.0
git push origin v3.0.0                      # 打版本标记 / 生成 Release；发 npm 见 §3.2
```

语义化版本约定：

- 修 bug / 排版 / 文案 → patch（`3.0.1`）；
- 新增能力卡、新增工具、协议不兼容增强 → minor（`3.1.0`）；
- 能力卡 JSON 结构、工具参数、**知识层契约**（catalog 字段 / 资产目录约定 / 账本 schema）破坏性变更 → major，同时改 `docs/CAPABILITY-SPEC.md` 的版本号。

v2 → v3 就是一次 major：知识层重建（719 → 450）、域从 9 变 10、新增账本与资产层、移除对外 `Config`。这类改动**不要**用 minor 混过去——账本与能力卡成员对不上时 `verify-ledger` 会红。

插件 `engines.dsh` 在 DSH 进入 0.3.x 之前不会放开；DSH 大版本升级时先改 `engines` + 重装验证，再发版。

### 6.2 回滚（发出去的版本有问题）

**优先**：发一个修复版，而不是删版本。npm 的版本号一旦被消费方锁进 lockfile，删掉会让他们的 `npm install` 直接失败。

```powershell
# ① 把 latest 回指到上一个可用版本（消费方重新 install 会拿到旧版）
npm dist-tag add dsh-research-suite@2.0.0 latest

# ② 标记坏版本弃用（保留可安装性，给出升级提示）
npm deprecate dsh-research-suite@3.0.0 "3.0.0 存在 XXX 问题，请升级到 3.0.1"
```

`npm unpublish` 只在发布后极短时间内、且没有其它包依赖它时才可用，属于最后手段；用之前先确认 `npm view dsh-research-suite dependents` 为空。

**本地回滚到旧版**：先卸载当前版本（`plugin_manager` 的 `remove_bundle`，target 传包名），再装指定版本 `dsh-research-suite@2.0.0`，然后**完全退出并重启** DSH Desktop。不要手动改 profile 的 `node_modules`——那会和 profile 的 `pnpm-lock.yaml` 打架。

## 七、常见失败模式排查表

| # | 现象 | 最可能原因 | 判断命令 | 修复 |
|---|---|---|---|---|
| 1 | 装完重启，一个技能都没多出来 | 入口没被 import（patch 里缺该插件，或 `dsh.bundle.patch` 指错） | `Select-String -Path "$env:DSH_HOME\profiles\desktop\cordis.patch.yml" -Pattern 'dsh-research-suite'`；`Test-Path "$env:DSH_HOME\profiles\desktop\node_modules\dsh-research-suite\package.json"` | 重装；确认包内 `cordis.patch.yml` 有 `- insert:` 且有 `- id:`/`- name:` 两行；确认 `package.json` 的 `dsh.bundle.patch` 指向它 |
| 2 | 技能注册期抛错，后面的工具也没了 | 注册时传了 `load()` 之类惰性钩子，而不是当场传 `content` 字符串 | 看 DSH 日志：`Get-ChildItem "$env:DSH_HOME\logs" -Recurse -File \| Sort-Object LastWriteTime -Descending \| Select-Object -First 5 FullName`，再 `Select-String -Path <日志文件> -Pattern 'skills.register\|dsh-research-suite'` | 改为注册时内联 `content`；`node scripts/verify-package.mjs` 会扫这类问题 |
| 3 | 插件装了但加载期报"找不到模块" | 入口静态/动态 import 了 `@deepseek-ai/*` | `node scripts/verify-package.mjs`（它会扫 `lib/**` 与根 `index.js`，报 `file:line`） | 入口只依赖 node 内置模块；`@deepseek-ai/*` 一律不 import |
| 4 | `install_bundle` 装不上 / 被跳过 | `engines` 不匹配（node 或 DSH 版本超出区间），或包目录里没有可读的 `package.json` | `node -v`；桌面版看 About 的版本；`Get-Content "$env:DSH_HOME\profiles\desktop\node_modules\dsh-research-suite\package.json" -TotalCount 20` | 满足 `node ^22.19.0 \|\| >=24.0.0`、DSH `>=0.2.0-0 <0.3.0`；版本不对就装对应 DSH 或改 `engines` 后重发 |
| 5 | npm 包体异常小 / 解包后没有 450 篇原文或资产目录 | `files` 白名单漏了 `knowledge`/`references`，或资产目录没被构建进包 | `npm pack --dry-run`（看文件数总量）；`node scripts/verify-package.mjs` 的资产一致性与包体统计行 | 补 `files` 白名单；资产要让 `knowledge/skills/<域>/<slug>__assets/` 真实落盘，catalog 的 `assets.files/bytes` 必须与之一致 |
| 6 | 工具在、技能不在（或反之） | 注册代码被条件包裹（配置缺省时跳过），或 `skills/*.md` 缺 frontmatter `name` | `node scripts/verify-package.mjs`；会话里调 `research_suite_status` 看技能/工具计数 | 补齐 frontmatter；确认注册不依赖可选配置 |
| 7 | 改完代码没生效 | 只重启了窗口，没退出进程；或装的是 npm 旧版而不是本地目录 | `(Get-Content "$env:DSH_HOME\profiles\desktop\node_modules\dsh-research-suite\package.json" -Raw \| ConvertFrom-Json).version` | 完全退出 DSH Desktop 再启动；本地验证时 `install_bundle` 传本地绝对目录 |
| 8 | CI 的 `npm pack --dry-run` 报错但本地正常 | CI 检出的是干净 clone，若本地有未提交文件（如新落盘的 `skills/*.md`）本地会多出来；或 `.npmignore` 覆盖了 `files` | 本地删 `node_modules` 后重跑：`npm pack --dry-run` | 以 `files` 白名单为准，删掉冲突的 `.npmignore` 条目 |
| 9 | **DSH Desktop 启动即失败**（`The application could not start`），连主界面都进不去 | 入口对外 `export const Config`，其 `toJSON()` 返回 JSON Schema，被 Host settings 服务当 **schemastery 信封** `new Schema(json)` 水合 → `schema.meta` 为 `undefined` → 读 `.volatile` 抛 `Cannot read properties of undefined (reading 'volatile')`（v2.0.0 上线当天真实事故） | `Select-String -Path lib/index.js -Pattern 'export const Config'`（应零命中）；日志里搜：`Get-ChildItem "$env:DSH_HOME\logs" -Recurse -File \| Sort-Object LastWriteTime -Descending \| Select-Object -First 5`，再 `Select-String -Path <日志> -Pattern 'volatile\|schemastery'` | 删除 `export const Config`；配置改由 `apply()` 内 `validateConfig()` 兜底（`DEFAULTS + validateConfig`）。详见 `docs/ARCHITECTURE.md` §5.3 |
| 10 | 能力卡里写的技能在 `knowledge/catalog.json` 里找不到 / 账本红一片 | 技能名对不上：catalog 重建后 `name` 变了，或 frontmatter 引号没剥离（`name` 带引号），或账本引用了不存在的卡 | `node scripts/verify-capabilities.mjs all`；`node scripts/verify-ledger.mjs all`；`Select-String -Path knowledge/catalog.json -Pattern '"name": "\\"'` | 让知识库构建侧修 `name`（去引号/去重）；能力卡 `members[].skill`、账本 `cards` 与 catalog `name`/`dir` 三者对齐后再复跑 |

> 说明：本机的 `dsh.cmd --version`（CLI）与桌面版 DSH 是两份安装，实测可能不一致（CLI `0.2.0-rc.2` / 桌面 `0.2.1-rc.5`）。**判断插件能否装，以桌面版 About 的版本为准**，不要拿 CLI 版本做依据。

## 八、发布检查清单

- [ ] 元信息确认过（`repository` 已指 `xuzhecomeon/dsh-research-suite`；`author` 如要署名已改）
- [ ] `node scripts/verify-capabilities.mjs all` → exit 0
- [ ] `node scripts/verify-ledger.mjs all` → exit 0（11 个域、450 条判定齐全，fused 全部可核）
- [ ] `node scripts/verify-package.mjs` → exit 0
- [ ] `node scripts/selftest.mjs` → exit 0
- [ ] `npm pack --dry-run` 里 `knowledge/`（450 篇 + `__assets/`）、`references/`、`skills/`、`lib/`、两个 README 都在；解包体积约 38 MB 量级、`scripts/` 含三份校验脚本
- [ ] 两份 README 里的能力卡总数已从占位符替换成真实数字（`grep -rn 'CAP_TOTAL' README*.md` 零命中）
- [ ] 版本四处一致（`package.json` = `3.0.1` / `CHANGELOG.md` 最新 `## 3.0.1` / 能力卡 `version` / git tag `v3.0.1`）
- [ ] `CHANGELOG.md` 的 `3.0.0` 段已写清本次变更（知识层重建、10 域、账本、资产、Config 移除）
- [ ] 本地 `install_bundle` 装一遍，重启后 `research_suite_status` 通过，12 个工具都在、11 个技能都在
- [ ] 发完 `npm view dsh-research-suite version` 是新版本
- [ ] 上架社区市场前：GitHub 仓库公开、创建满 1 天、已加 topic `dsh-plugin`、仓库根有 `package.json` + `cordis.patch.yml`（见 §九）
- [ ] 市场条目：v2 时已提 PR #12199（`data/plugins/xuzhecomeon__dsh-research-suite.yml`），**插件名没变，不重提**；合并后条目描述里的数字如需更新，另开一个改一个文件的 PR（450 技能 / `data/capabilities/*.json` 合计能力卡数 / 11 技能 / 7 工具）

## 九、上架社区插件市场（awesome-dsh-plugin → dshmarket 与官方 Discover）

事实链先讲清楚：`dshmarket.com` 和 dshmarket 插件里的列表**不是它自己维护的**，数据来自仓库 `github.com/awesome-dsh-plugin/awesome-dsh-plugin` 的 `data/plugins/*.yml`（一个插件一个文件）。所以「发布到插件市场」的真实动作是：**在那个仓库提一个只加一个文件的 PR**。合并后站点与市场自动收录，仓库 README 说通常一天内生效。dsh-market 仓库自己也写明了：它是市场应用本身，不要往那里提插件条目。

### 9.1 前置条件（官方 contributing.md 逐条对齐）

| # | 要求 | 本包现状 |
| --- | --- | --- |
| 1 | GitHub 公开仓库，包在仓库根（`package.json` 与 `cordis.patch.yml` 同级） | 满足（包根即仓库根） |
| 2 | `package.json` 声明 `dsh.bundle`，形如 `"dsh": { "bundle": { "patch": "./cordis.patch.yml" } }` | 满足 |
| 3 | 只声明 `dsh.client` 会**被拒** | 本包不需要前端，未声明 |
| 4 | 仓库创建满 1 天（CI 自动查） | 建仓时注意 |
| 5 | 仓库加 topic `dsh-plugin` | 需手动加 |
| 6 | 真实可跑代码，非占位/纯 README | 满足（`lib/` 4 个模块 + `scripts/` 4 个校验脚本：capabilities / ledger / package / selftest） |
| 7 | 描述只说功能、不带营销词，且**与代码一致**（写数字就要数得出来） | 条目里可写的可验证数字：450 个源技能 / `data/capabilities/*.json` 的能力卡数 / 11 个注册技能 / 12 个工具 |
| 8 | 一个 PR 最多 3 个条目 | 本次 1 条 |
| 9 | 可选 `icon:` 必须是 **GitHub 托管的位图**（png/jpg/webp，卡片约 96px 显示），**SVG 会被拒** | 本包 `icon.svg` 不能直接用作条目图标；不写则回退成作者 GitHub 头像 |
| 10 | 可选：自身仓库根放 `screenshots.json`（1~8 张，相对路径） | 暂无截图 |
| 11 | 可选：发 npm 不影响收录；但若发，`repository` 字段必须指回被收录的那个仓库 | 见 §一 占位符替换 |

### 9.2 投稿五步

1. 把本包推到 GitHub 公开仓库，并替换 3 处占位符（见 §一）。
2. `git tag v3.0.0` 并推送 tag（v2.0.0 的 tag 已存在；v3 是同一仓库的新 major，不重开仓库、不重提市场 PR #12199）。
3. Fork `awesome-dsh-plugin/awesome-dsh-plugin`。
4. 把 `dist/awesome-dsh-plugin-entry.yml` 里的 `<owner>` 全替换成你的 GitHub 账号，另存为 `data/plugins/<owner>__dsh-research-suite.yml` 提交 PR（**不要**手工改两个 README，它们由脚本生成）。
5. PR 描述用 `dist/PR-提交说明.md`。

### 9.3 CI 检查顺序与常见被打回原因

CI 依次查：条目数 ≤3 → 从仓库读 `dsh.bundle` → 仓库年龄 ≥1 天 → `awesome-lint` 与站点构建（双语一致性、分隔符、日期、截图）。失败会明确指出要改什么，**往同一分支推即可，不必重开 PR**。

关于年龄门槛：`scripts/check-submission.mjs` 里 `MIN_AGE_DAYS = 1`，但 contributing 明确写了 gate 结论是**快照且过期会自动重跑**——被「仓库 0.5 天」挡住的投稿几小时后自己就达标，**不需要推空提交**。

> 本包的实际投稿记录（2026-11-05）：仓库 `xuzhecomeon/dsh-research-suite` 上线后已按上面五步提过一次 PR —— `awesome-dsh-plugin/awesome-dsh-plugin` **#12199**，改动仅 `data/plugins/xuzhecomeon__dsh-research-suite.yml` 一个文件。提 PR 时仓库创建未满 1 天，故 gate 会在满 1 天后自动重新判定。

最常见的两种被打回：① 只声明 `dsh.client`（不可安装）；② 描述夸大（写了「46 个工具、六个领域」就得真有）。v2 条目里的四个数字当时是「719 篇 / 81 卡 / 10 技能 / 7 工具」，v3 已变为「450 篇源技能 / `data/capabilities/*.json` 合计张能力卡 / 11 个注册技能 / 12 个工具」，都能用 `node scripts/verify-package.mjs` 与 `data/capabilities/*.json` 数出来。**插件名与仓库没变，市场 PR #12199 不重提**；若合并后要改条目描述里的数字，另提一个只改 `data/plugins/xuzhecomeon__dsh-research-suite.yml` 的 PR。

## 十、不经过市场，直接把插件发给别人（四条路）

### 路线 A：发 tgz（最快，已实测）

- v3 打包：包根执行 `npm pack` → `dsh-research-suite-3.0.0.tgz`（解包约 38 MB 量级，含 450 篇原文 + 954 个资产文件）；v2 是 `dist/dsh-research-suite-2.0.0.tgz`（4.1 MB，解包 11.8 MB / 771 文件）。
- 对方执行：`dsh plugin --profile <profile名> add <tgz 绝对路径>`，然后**完全退出并重启 DSH Desktop（含托盘）**。
- 实测记录（2026-11-04，v2 tgz）：在全新 profile 上执行上述命令 → **exit 0**，profile 依赖记为 `file:<tgz 路径>`；装出来的目录是**实体拷贝而非符号链接**，771 文件、`skills/` 10 个 md、`knowledge/skills/` 10 个域、`cordis.patch.yml` 齐全 ⇒ tarball 自足，对方无需任何本机技能目录。v3 的 tgz 尚未实测，首次发出前按本清单 §八 走一遍。
- 注意：对方 DSH 需 ≥0.2.0；装的是拷贝，**升级必须发新 tgz 并改版本号**（同名同版本会被判 `Already up to date` 而跳过）。

### 路线 B：发 GitHub 仓库（适合同行复现）

- 对方执行：`dsh plugin --profile <profile名> add github:<owner>/<repo>#<commit>`。`dsh plugin` 把参数原样转给 pnpm，支持 pnpm 的 `github:` 协议；本包无构建步骤，装上即可用。
- **实测记录（2026-11-05，v2）**：在全新 profile 上执行 `dsh plugin --profile ghverify add github:xuzhecomeon/dsh-research-suite` → pnpm 从 `codeload.github.com` 拉 tar.gz，输出 `+ dsh-research-suite 2.0.0`，`Done in 2m 22.5s`，exit 0；该 profile 的 `dsh.profile.bundles` 自动出现 `dsh-research-suite`。⇒ 同行拿到仓库地址就能一条命令装上。v3 同一仓库、同一包名，装 `#v3.0.0` 这个 tag（或 `#<commit>` 锁提交）即可，不需要换仓库地址。
- 好处：可锁 commit 复现。缺点：国内直连 GitHub 不稳，拉不下来就退回路线 A。

### 路线 C：发到 npm（公开包，一次发布长期可用）

- 你：按 §三 发布；对方：`dsh plugin --profile <profile名> add dsh-research-suite`。
- 包名可用性：2026-11-04 实测 `npm view dsh-research-suite version` → `E404`，即 **npm 上这个名字还空着**。
- 注意：公开 npm 包＝公开再分发。`knowledge/skills/` 下 450 篇源技能与 954 个自带资产是第三方材料，许可见 `docs/ATTRIBUTION.md`，发之前请自行判断授权风险。

### 路线 D（可选）：让对方加「索引源」

dsh 0.2.1 起「插件 → 发现（Discover）→ 索引源」支持 format 1 的 `index.json`（官方示例是放在 npm 上分发的 `https://cdn.jsdelivr.net/npm/dsh-plugin-catalog/index.json`）。适合你以后有多个插件要一起分发；只发一个插件时用 A/B/C 更省事。

### 部署现状提醒（很重要）

你本机 desktop profile 里的 `dsh-research-suite` 现在是 **junction 指向任务文件夹** `D:\workbuddy\2026-11-04-20-37-51\2026-11-04_2229\dsh-research-suite`。**删掉或挪走这个文件夹，插件立即失效**。想让它稳定，二选一：

1. 把包复制到固定位置（例如 `D:\workbuddy\dsh-plugins\dsh-research-suite`），再用 `plugin_manager` 的 `install_bundle` 指新位置；
2. 改成从 tgz 安装（需先把版本号提升，例如提到 `3.0.1` 再打包，否则同版本会被 pnpm 判为已满足）。
