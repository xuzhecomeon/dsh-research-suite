# dsh-research-suite

[![CI](https://github.com/xuzhecomeon/dsh-research-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/xuzhecomeon/dsh-research-suite/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/dsh-research-suite.svg)](https://www.npmjs.com/package/dsh-research-suite)
[![license](https://img.shields.io/npm/l/dsh-research-suite.svg)](LICENSE)

A DeepSeek Harness (DSH) plugin for the full clinical-research workflow — manuscript writing, language polishing, figures, statistics, research ideation, peer review, slides, literature search and journal formatting. Install it and it **takes over research tasks automatically**: no UI, no manual skill picking.

> 中文完整说明见 **[README.zh-CN.md](README.zh-CN.md)**（内容更全，含配置项、目录结构、占位符清单）。

- Package: `dsh-research-suite` · Version: `2.0.0` · License: MIT
- Requires Node `^22.19.0 || >=24.0.0`, DSH `>=0.2.0-0 <0.3.0`
- **Self-contained: all 719 original skill documents ship inside the package; nothing is read from any external skill directory at runtime.**

## Why capability cards instead of a skill router

The hard part of research work is not a lack of skills — it is that three to eight skills can each do the same task well in different ways. A router hands the model one "primary skill" name; the model then reads that skill's manual and improvises, losing the other skills' strengths along the way.

Instead, each **capability card** takes every competing skill in its group, records `best_at` (what it is best at), `limits` (what it explicitly cannot do) and `take` (the concrete rules, thresholds and templates lifted from it), then fuses them into one executable **protocol**. Every protocol step says which skill it comes from and why. The acceptance rule is strict: *after reading one capability card you can finish the job without opening any original skill document.*

The 719 original documents remain bundled as a deep-reading layer — for checking details, not for improvising.

## How auto-takeover works

No UI, no buttons. Three pieces:

1. **A system-prompt section** — `lib/prompt.js` builds a policy named `research-suite/policy` at `order: 650` ("after team policy, before tool docs"); `lib/index.js` registers it through `systemPrompt.section({ name, order, text: () => buildPolicy(core) })`. The policy tells the model: recognise a research task → call `research_playbook` first → follow the capability protocol → deep-read if needed → run `research_gate` before delivering.
2. **10 skills** (`skills/`): one entry skill plus nine domain SOPs. Their `content` is inlined **at registration time** — passing a lazy `load()` hook fails DSH's runtime validation and silently drops every skill (the exact failure mode of v1).
3. **7 read-only tools** for capability lookup, searching the 719-document catalog, deep reading, standards, and mechanical self-checks.

When `research_playbook` finds no match, the policy falls back to `research_catalog` + `research_kb_read` rather than refusing the task.

## Domains

| Domain | Skills | Capabilities | Covers |
|---|---:|---:|---|
| `writing` | 51 | 11 | paper types and sections (original / review / case report / grant) |
| `polish` | 24 | 5 | register, de-AI-flavour, reduction, proofreading, Word reports |
| `figures` | 76 | 9 | data plots, statistical charts, mechanism diagrams, layout |
| `stats` | 180 | 16 | descriptive, comparison, regression, survival, prediction, PSM, MR, Meta, missing data, sample size |
| `ideation` | 33 | 7 | topic selection, novelty search, hypotheses, grants, ethics |
| `review` | 39 | 8 | self-review, reviewer comments, revision, rebuttal, response letters |
| `slides` | 44 | 7 | conference, lecture, defence, lab meeting, poster |
| `literature` | 152 | 11 | search strings, screening, close reading, evidence tables, recall/precision |
| `format` | 32 | 7 | journal formatting, references, figure/table specs, submission package |
| **Total** | **631** | **81** | 81 capability cards across the nine domains (177 skills formally referenced, 542 catalogued for on-demand reading) |

631 skills across the nine domains plus 88 general skills = **719 bundled skill documents** (~9.9 MB). Nine reference standards (Chinese Medical Association format, GB/T citation, statistical reporting, figure specs, grant rules, etc.) live in `references/`.

## Tools

| Tool | Purpose |
|---|---|
| `research_playbook` | **The only entry point.** Pass the user's own words; returns the 1–3 best-matching capability cards with protocol, gates, deliverables and suggested deep reads |
| `research_capability` | Expand a full capability card (member comparison, protocol, decisions, gates, outputs, kb) by `id` or by `domain` |
| `research_catalog` | Search the 719-document catalog by name/description keywords, optionally filtered by domain |
| `research_kb_read` | Read one skill document or `INDEX.md`/`FUSION.md`, with paging and path-escape rejection |
| `research_standard` | List or read the nine reference standards in `references/` |
| `research_gate` | Gate and mechanical self-check: `section` = `all` / `data` / `selfcheck` / `mutex` / `forbidden` / `hard` / `handoffs`; `text` checks fullwidth punctuation, superscript citation numbers, AI-cliché phrases and absolute wording |
| `research_suite_status` | Load self-check: version, per-domain capability counts, catalog completeness, references, package root |

## Install

```powershell
# via plugin_manager (GUI)
plugin_manager(action="install_bundle", target="<absolute package path or dsh-research-suite@2.0.0>")

# via CLI (Windows)
dsh.cmd plugin --profile desktop add <absolute package path or package name>
# via CLI (POSIX)
dsh plugin --profile desktop add <absolute package path or package name>
```

Fully quit and restart DSH Desktop afterwards (closing the window is not enough — the loader reads the bundle patch layer at startup). Verify with `research_suite_status`.

## Configuration

| Key | Default | Meaning |
|---|---|---|
| `autoTakeover` | `true` | Inject the auto-takeover prompt section; `false` degrades the plugin to "7 tools + 10 skills" without automatic routing |
| `sectionOrder` | `650` | Order of the prompt section (after team policy, before tool docs) |
| `verbose` | `false` | Log warnings when skill/tool/prompt registration fails |

## Documentation

- [docs/CAPABILITY-SPEC.md](docs/CAPABILITY-SPEC.md) — capability-card content contract
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — modules, data flow, how auto-takeover is implemented
- [docs/PUBLISH.md](docs/PUBLISH.md) — npm release, DSH install paths, upgrade/rollback, troubleshooting table
- [CHANGELOG.md](CHANGELOG.md) — what changed in 2.0.0

## Self-checks

```powershell
npm test           # scripts/selftest.mjs — fake-ctx load smoke test
npm run verify     # scripts/verify-package.mjs — static release checks
npm run verify:caps# scripts/verify-capabilities.mjs all
npm run pack:check # npm pack --dry-run (~11-12 MB unpacked / ~4 MB tarball; knowledge/ included by design)
```

Measured on the 2.0.0 release candidate: **773 files / 11.24 MB** on disk (`scripts/verify-package.mjs` count, includes `.github/`); `npm pack` ships **771 files, 11.8 MB unpacked, 4.1 MB tarball**.

## License

MIT — see [LICENSE](LICENSE).

**Scope note**: MIT covers the plugin itself (`lib/`, `data/capabilities/`, `skills/`, `references/`, `scripts/`, `docs/` and the index files). The 719 skill texts under `knowledge/skills/` are third-party material vendored verbatim from the author's local skill collection; their licenses belong to their original authors and are **not** covered by MIT. Read [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md) before redistributing.
