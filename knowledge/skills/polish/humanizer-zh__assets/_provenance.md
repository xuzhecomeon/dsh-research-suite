# 安装溯源记录

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/op7418/Humanizer-zh |
| 提交 | `f4518a8eab97b8bfebc66a89d34320a89bef6930`（2026-09-23） |
| 许可证 | MIT（Copyright (c) 2026 歸藏），已随包附 LICENSE |
| 安装日期 | 2026-10-23 |
| 版本关系 | 覆盖替换旧版 skillhub 包 `humanizer-zh__skillhub` v1.0.0（484 行，翻译自 blader/humanizer）。备份位于 `~/.workbuddy/skills_backup/humanizer-zh__skillhub-1.0.0-20261023/` |

## 与旧版的实质差异

- 由「模式黑名单式改写」转为「保留信息与确定程度优先」的四级约束优先级。
- 31 个检查点重写，每条补充适用条件与应保留表达的边界示例。
- 明确禁止润色凭空补充事实、数据、产品功能、人物经历。
- 文件模式下保护代码块、命令、路径、URL、YAML front matter、标题层级与锚点。
- 默认只交付最终稿，取消自评分与模式命中清单。

## 安全审计结论

- 仅 `SKILL.md`、`README.md`、`CHANGELOG.md`、`LICENSE` 及 `tests/`；无 hooks、无网络、无 shell 执行。
- `tests/check_structure.py` 为只读结构校验脚本，未在技能加载路径上被调用。
- `allowed-tools` 声明为 Read / Write / Edit / AskUserQuestion，无 Bash。

## 本地改动

`SKILL.md` frontmatter 的 `description` 末尾追加中文触发词（去 AI 味 / 去除 AI 痕迹 / 去 AI 化等）；正文未改。
