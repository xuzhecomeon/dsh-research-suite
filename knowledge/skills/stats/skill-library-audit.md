<!-- source: skill-library-audit @ skill-library-audit | domain: stats -->

---
name: skill-library-audit
description: 技能库健康体检工具。检测完全重复的技能目录、frontmatter 与目录名不一致、功能重叠竞争，并统计技能库规模与体积分布。当用户刚批量安装过技能、怀疑有重复、技能太多想整理，或说"技能重复了""检查技能库""整理技能库"时使用。
agent_created: true
---

# 技能库体检

## 何时用

- 从多个来源批量装过技能后（同领域技能容易撞车）
- 技能目录数超过 100 个，怀疑有重复
- 某些技能触发异常、或名称与预期不符

## 三类问题与判据

### 1. 完全重复（真重复，可安全删除）

**判据**：两个技能目录的**全部文件 md5 逐一相同**，或 A 的所有文件是 B 的子集。

⚠️ **只比 `SKILL.md` 远远不够。** 实测案例：两个技能 `SKILL.md` 的 md5 完全一致，但 A 有 10 个文件、B 有 11 个——B 多一个 `skill-card.md`，两者 `_icon.png` 尺寸与 SkillHub 元数据也不同。只看 SKILL.md 就删，会漏判。

**删除前置流程（缺一不可）**：

1. 逐文件比对两个目录的全部 md5，列出「仅 A 有」「仅 B 有」「同名不同内容」
2. 确认待删版本**没有独有文件**
3. 备份到工作区 `.backup/<技能名>/`
4. 再执行删除
5. 删后验证：目录消失 + 保留版文件数不变 + 技能总数减 1

### 2. 功能重叠（不是重复，是竞争）

**判据**：多个技能的 `description` 覆盖同一个动作。例如"去 AI 味"散落在 4 个技能里（`humanizer-zh` / `paper-deweight-fd` / `wb-academic-polish` / `paper-polisherskill`）。

**处置**：**不要删**。应明确指定主选技能并写入路由表，否则每次相关请求都会有多個技能争抢匹配，反而降低准确度。

### 3. 名称不一致

**判据**：目录名 ≠ frontmatter 的 `name:`。

⚠️ **先排除安装器后缀**：SkillHub 安装的技能，目录名会被追加 `__skillhub`（防重名冲突）。这是**安装器约定，不是作者设计**——比较时必须先剥离，否则会把几十个正常技能误报为不一致。脚本已内置该处理。

⚠️ **再查证是否作者有意**：若作者在 `manifest.yaml` 里写明「有意不同」（实例：`nature-proposal-writer/` 的 name 是 `researchwrite`），或该名称在技能目录内被引用 3 处以上，则**保持原样**——改名会破坏内部路径引用。

**判据的边界（实测教训）**："被引用 3 处以上"这条只对**非安装器后缀**场景有效。因为技能正文里提到自己的名字是常态，若拿它判断 `__skillhub` 系列技能，会全部误判为"作者有意设计"。

## 用法

```bash
"<USER_HOME>/.workbuddy/binaries/python/versions/3.13.12/python.exe" \
  "<USER_HOME>/.workbuddy/skills/skill-library-audit/scripts/audit_skills.py"
```

参数：
- （无）→ 全量体检
- `--duplicates` → 只查完全重复
- `--names` → 只查名称一致性
- `--top 20` → 列出体积最大的 N 个技能

## 删除操作的本机注意事项

- **不要用 `shutil.rmtree`**：沙箱会把删除重定向到回收站，失败时报 `SHFileOperationW 失败: 0x78`
- 改用 PowerShell 的 `[System.IO.Directory]::Delete($path, $true)`，实测稳定
- 大目录（>5000 文件）删除需后台执行
