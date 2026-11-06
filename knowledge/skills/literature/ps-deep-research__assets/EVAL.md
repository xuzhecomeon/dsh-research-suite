# EVAL Harness (v5.0)

> 本文只描述当前仓库中真实存在、可运行的评测资产。

## 实际状态

| 层 | 数据 | 当前状态 |
|---|---|---|
| **Dev-time Hook Tests** | `hook-tests/fixtures/*.md` + `hooks/verify.sh hook-tests` | ✅ **可运行**。7 个 fixture 覆盖 clean / hedge / vague / weak title / confab numbers / preflight fail / preflight pass |
| **Doc Drift Check** | `hooks/verify.sh drift` | ✅ **可运行**。检查 tier 硬约束在核心文档中的一致性 |
| **Report Audit** | `hooks/verify.sh scan/preflight/frontmatter <report.md>` | ✅ **可运行**。用于单份报告的 Phase 6 审计 |
| **L1 Regression** | 12 题问题集（4 模板 × 3 难度）| ✅ **已建成**（12 题，见 `eval/questions/INDEX.md`）；pass criteria 已定稿，baseline 待运行 |
| **L2 Benchmark** | BrowseComp / GAIA 子集 | ❌ **未运行** |
| **L3 Production Sampling** | 真实调用周抽样 | ❌ **未启用** |
| **L4 Quality Trend** | `~/.claude/research/.quality_registry.jsonl` | ⚠️ **未由本仓库验证** |

结论: 当前可验证闭环是 **dev-time hook + doc drift**。L1 regression 问题集已建成（12 题，见 `eval/questions/INDEX.md`），但 baseline 尚未运行。在 baseline 跑通前，不要宣称"通过 L1 regression"或"v1.0 stable"。

## 可运行命令

Windows / Git Bash:

```bash
~/.claude/skills/deep-research/hooks/verify.sh hook-tests
~/.claude/skills/deep-research/hooks/verify.sh drift
~/.claude/skills/deep-research/hooks/verify.sh all
```

PowerShell 里如果 `bash` 不在 PATH,用 Git for Windows 的 bash 全路径:

```powershell
& "C:\Program Files\Git\bin\bash.exe" -lc "~/.claude/skills/deep-research/hooks/verify.sh all"
```

单份报告:

```bash
~/.claude/skills/deep-research/hooks/verify.sh scan <report.md> --json
~/.claude/skills/deep-research/hooks/verify.sh preflight <report.md>
~/.claude/skills/deep-research/hooks/verify.sh frontmatter <report.md>
```

## L1 Regression（问题集已建成，baseline 待运行）

已建成 12 题（4 模板 × 3 难度），每题固定 pass criteria，见 `eval/questions/INDEX.md`。baseline **尚未运行** —— 跑通前不要宣称已通过 L1。

### 基线运行流程

```bash
# 运行全部 12 题（deep tier + eval mode）
# for q in S1 S2 S3 C1 C2 C3 D1 D2 D3 H1 H2 H3; do
#   /deep-research "$(eval/questions/$q-*.md)" --quality=deep --eval
# done
```

每题输出：`report.md` / `judge.json` / `diff.md` / `summary.json` → `eval/results/<run-id>/`

### Pass criteria（固定，不回调）

- ≥10/12 题 overall ≥0.75
- 0 题 overall <0.55
- 平均 factual_accuracy ≥0.80
- citation 造假 = block
- 模板额外维度（survey/compare/decide/howto）≥ 0.70

## 失败处理

- Hook tests fail → 不提交 skill/hook 修改
- Drift fail → 先修文档一致性
- 单份报告 frontmatter fail → 报告必须 `degraded: true` 并在 TL;DR 前显式告知
- 未来 L1 fail → block release,除非人工 override 并写明原因

## Anti-patterns

| 反模式 | 为什么 |
|---|---|
| reference 由同 agent 写 | self-eval bias |
| pass criteria 跟随结果调 | 必须固定 |
| 只跑 hook-tests 就宣称 regression pass | hook 只测扫描器,不测研究质量 |
| 只看 overall 不看分维度 | 漏诊断信号 |
