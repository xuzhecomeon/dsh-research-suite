# 安装溯源记录

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/Nanako0129/sepia |
| 提交 | `fb06be76abeae7dd606960a32f2b10c1d1798e0d`（2026-10-15） |
| 版本 | 0.12.4 |
| 许可证 | MIT（Copyright (c) 2026 Nanako Tsai），已随包附 LICENSE |
| 安装日期 | 2026-10-23 |
| 安装范围 | 仅规范路由主体 `skills/sepia/`（含 references/ 与 agents/），未安装 `sepia-write` / `sepia-review` / `sepia-refactor` / `sepia-recreate` / `sepia-hemingway` 五个包装入口 |

## 安全审计结论

- 全部为 Markdown 指令文档 + `references/` 参考资料；无 hooks、无 MCP、无网络请求、无 shell 执行。
- 仓库内 `scripts/check_persona.py`、`scripts/check_versions.py` 仅用 Python 标准库做结构校验，未随包安装。
- 无符号链接、无二进制、无可执行文件。
- SKILL.md 内置 "Security boundary" 条款：将目标文本视为不可信数据，不得由文本内嵌指令改变操作或扩权。

## 本地改动

1. `SKILL.md` frontmatter 的 `description` 末尾追加中文触发词（去 AI 味 / 去除 AI 痕迹 / 去 AI 化等），便于中文任务命中；正文未改。
2. 因未安装五个包装入口，`../sepia/SKILL.md` 的兄弟路径引用不适用；直接调用 `sepia` 即可覆盖 write / review / refactor / recreate 四种操作。

## 升级方式

重新克隆仓库后，覆盖 `SKILL.md` 与 `references/`，再补回上述 description 中文触发词。
