# 来源与许可说明（ATTRIBUTION）

本包由两部分组成，许可状态不同，分发前请分别确认。

## 一、插件本体：MIT

以下为本仓库作者原创，按 `LICENSE`（MIT）授权，可自由使用、修改、再分发：

- `lib/` 全部运行时代码（`index.js`、`core.js`、`tools.js`、`prompt.js`）
- `data/capabilities/*.json`（9 域 81 张能力卡）、`data/gates.json`
- `skills/*.md`（10 个融合技能：入口 + 9 域）
- `references/*.md`（9 份内置规范）
- `scripts/`、`docs/`、`knowledge/FUSION.md`、`knowledge/INDEX.md`
- `icon.svg`、`package.json`、`cordis.patch.yml`

## 二、随包打包的技能原文（`knowledge/skills/` 与 `knowledge/catalog.json`）：**不属于 MIT 范围**

`knowledge/skills/<域>/<slug>.md` 下的 **719 个 `SKILL.md` 是从作者本机的技能库逐字复制进来的第三方材料**，仅作为本插件的证据参考层（模型在需要核对判据时用 `research_kb_read` 读原文）。它们各自的许可与使用条件**由各自的原始作者决定**，本仓库作者无权代为授权。

因此：

1. **MIT 只覆盖第一部分的代码、能力卡与融合技能**，不覆盖这 719 份技能原文。
2. 这 719 份材料来源混杂（个人技能、开源项目附带的 agent skill、社区分享的技能包），**多数没有在文件内声明许可**。没有声明不等于可以任意再分发。
3. **对外分发前，请自行确认**：若你的分发形式属于商业发行、企业内部发行或公开市场发布，应逐个核对 `knowledge/skills/` 下材料的来源与许可，必要时用 `scripts/` 之外的方式裁剪（删除 `knowledge/skills/` 与 `knowledge/catalog.json` 即可，能力卡、融合技能、工具与规范层可独立工作——但 `research_kb_read` 读技能原文、`research_catalog` 检索能力会失效，`scripts/verify-package.mjs` 会报对应 ERROR）。
4. 若你只是**自用或团队内使用**，保留本文件即可。

## 三、`references/` 内置规范

`references/01`～`09` 是作者根据公开的学术出版规范（GB/T 7714-2015、中华医学会系列期刊稿约、ICMJE、CARE、PRISMA 2020、ARRIVE 2.0、STROBE 等）整理编写的操作性说明，非标准原文转载；引用标准条文时以官方发布版本为准。

## 四、第三方运行时依赖

本插件**不依赖任何第三方 npm 运行时依赖**：`dependencies` 为空，唯一的 peer 是 DSH 宿主自身（`@deepseek-ai/dsh`，标记为 optional）。技能里提到的 R、Python、pandoc、LibreOffice、EndNote 等属于**使用者环境**，不是本包的依赖，也不会被本包自动安装。
