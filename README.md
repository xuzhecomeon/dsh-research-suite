# dsh-research-suite

[![CI](https://github.com/xuzhecomeon/dsh-research-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/xuzhecomeon/dsh-research-suite/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/dsh-research-suite.svg)](https://www.npmjs.com/package/dsh-research-suite)
[![license](https://img.shields.io/npm/l/dsh-research-suite.svg)](LICENSE)

A DeepSeek Harness (DSH) plugin for the full clinical-research workflow — manuscript writing, language polishing, figures, statistics, research ideation, peer review, slides, literature search and journal formatting. Install it and it **takes over research tasks automatically**: no UI, no manual skill picking.

> 中文完整说明见 **[README.zh-CN.md](README.zh-CN.md)**（内容更全，含配置项、目录结构、占位符清单）。

- Package: `dsh-research-suite` · Version: `3.0.1` · License: MIT · DSH tested: `0.2.1-rc.5`, `0.2.2-rc.1`
- Requires Node `^22.19.0 || >=24.0.0`, DSH `>=0.2.0-0 <0.3.0`
- **Self-contained: all 592 source skill documents plus their bundled `references/scripts/templates` assets ship inside the package; nothing is read from any external skill directory at runtime.**

## Why capability cards instead of a skill router

The hard part of research work is not a lack of skills — it is that three to eight skills can each do the same task well in different ways. A router hands the model one "primary skill" name; the model then reads that skill's manual and improvises, losing the other skills' strengths along the way.

Instead, each **capability card** takes every competing skill in its group, records `best_at` (what it is best at), `limits` (what it explicitly cannot do) and `take` (the concrete rules, thresholds and templates lifted from it), then fuses them into one executable **protocol**. Every protocol step says which skill it comes from and why. The acceptance rule is strict: *after reading one capability card you can finish the job without opening any original skill document.*

The 592 source documents (and the 3,924 asset files they bring along) remain bundled as a deep-reading layer — for checking details, not for improvising.

## How auto-takeover works

No UI, no buttons. Three pieces:

1. **A system-prompt section** — `lib/prompt.js` builds a policy named `research-suite/policy` at `order: 650` ("after team policy, before tool docs"); `lib/index.js` registers it through `systemPrompt.section({ name, order, text: () => buildPolicy(core) })`. The policy tells the model: recognise a research task → call `research_playbook` first → follow the capability protocol → deep-read if needed → run `research_gate` before delivering.
2. **11 skills** (`skills/`): one entry skill plus ten domain SOPs (writing / polish / figures / stats / ideation / review / slides / literature / format / data). Their `content` is inlined **at registration time** — passing a lazy `load()` hook fails DSH's runtime validation and silently drops every skill (the exact failure mode of v1).
3. **7 read-only tools** for capability lookup, searching the 592-document catalog, deep reading (including skill-bundled assets), standards, and mechanical self-checks.

When `research_playbook` finds no match, the policy falls back to `research_catalog` + `research_kb_read` rather than refusing the task.

## Domains

| Domain | Source skills | Covers |
|---|---:|---|
| `writing` | 66 | paper types and sections (original / review / case report / grant) |
| `polish` | 12 | register, de-AI-flavour, reduction, proofreading, Word reports |
| `figures` | 36 | data plots, statistical charts, mechanism diagrams, layout |
| `stats` | 31 | descriptive, comparison, regression, survival, prediction, PSM, MR, Meta, missing data, sample size |
| `ideation` | 39 | topic selection, novelty search, hypotheses, grants, ethics |
| `review` | 21 | self-review, reviewer comments, revision, rebuttal, response letters |
| `slides` | 37 | conference, lecture, defence, lab meeting, poster |
| `literature` | 26 | search strings, screening, close reading, evidence tables, recall/precision |
| `format` | 51 | journal formatting, references, figure/table specs, submission package |
| `data` | 40 | databases and omics data: GEO / TCGA / dbGaP / genotype and variant databases, omics retrieval and curation |
| **Total** | **592** | **103** capability cards across the ten domains |

`toolbox` is an additional index-only bucket of 233 utility skills: it feeds `research_catalog` and `research_kb_read`, and deliberately has **no capability cards** — a tool is a means, not a task a user asks for.

Every one of the 592 source skills has a recorded verdict in `data/ledger/<domain>.json` (`fused` — and which cards it feeds / `index-only` / `deprecated` / `out-of-scope`), so the "all studied, best only" claim is auditable: `node scripts/verify-ledger.mjs all` re-checks coverage and that every `fused` skill is actually a member of the card it claims. Beyond the text, **skill-bundled assets ship too**: 451 skills contribute 3,924 files (~29 MB) of `references/`, `scripts/` and `templates/` under `knowledge/skills/<domain>/<slug>__assets/`; `research_kb_read(name, asset='scripts/plot.py')` reads them (omitting `asset` lists what the skill ships with). Nine reference standards live in `references/`.

## Tools

| Tool | Purpose |
|---|---|
| `research_playbook` | **The only entry point.** Pass the user's own words; returns the 1–3 best-matching capability cards with protocol, gates, deliverables and suggested deep reads |
| `research_capability` | Expand a full capability card (member comparison, protocol, decisions, gates, outputs, kb) by `id` or by `domain` |
| `research_catalog` | Search the 592-document catalog by name/description keywords (the 233 `toolbox` skills included), optionally filtered by domain; each hit reports how many bundled assets it carries |
| `research_kb_read` | Read one skill document or `INDEX.md`/`FUSION.md`; the `asset` parameter reads a skill-bundled file such as `scripts/plot.py` or `references/*.md` (omitting it lists the skill's assets); paging and path-escape rejection included |
| `research_standard` | List or read the nine reference standards in `references/` |
| `research_gate` | Gate and mechanical self-check: `section` = `all` / `data` / `selfcheck` / `mutex` / `forbidden` / `hard` / `handoffs`; `text` checks fullwidth punctuation, superscript citation numbers, AI-cliché phrases and absolute wording |
| `research_suite_status` | Load self-check: version, per-domain capability counts, 592-entry catalog completeness, asset statistics, references, package root |

## Install

```powershell
# via plugin_manager (GUI)
plugin_manager(action="install_bundle", target="<absolute package path or dsh-research-suite@3.0.0>")

# via CLI (Windows)
dsh.cmd plugin --profile desktop add <absolute package path or package name>
# via CLI (POSIX)
dsh plugin --profile desktop add <absolute package path or package name>
```

Fully quit and restart DSH Desktop afterwards (closing the window is not enough — the loader reads the bundle patch layer at startup). Verify with `research_suite_status`.

## Configuration

The plugin deliberately **does not export a `Config`**: in v2.0.0 that export (`toJSON()` returning JSON Schema) was hydrated by DSH's Host settings service as a schemastery envelope, crashed on `schema.meta`, and prevented DSH Desktop from starting. Configuration is now validated inside `apply()` by `validateConfig()`.

| Key | Default | Meaning |
|---|---|---|
| `autoTakeover` | `true` | Inject the auto-takeover prompt section; `false` degrades the plugin to "7 tools + 11 skills" without automatic routing |
| `sectionOrder` | `650` | Order of the prompt section (after team policy, before tool docs) |
| `verbose` | `false` | Log warnings when skill/tool/prompt registration fails |

Because there is no exported `Config`, **the DSH settings panel shows no entries for this plugin** (a deliberate trade-off). Override values in the profile's `cordis.patch.yml` entry instead:

```yaml
- id: dsh-research-suite
  config:
    autoTakeover: true
    sectionOrder: 650
    verbose: false
```

## Documentation

- [docs/CAPABILITY-SPEC.md](docs/CAPABILITY-SPEC.md) — capability-card content contract
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — modules, data flow, how auto-takeover is implemented, and the v3 knowledge layer & ledger
- [docs/PUBLISH.md](docs/PUBLISH.md) — npm release, DSH install paths, upgrade/rollback, troubleshooting table
- [CHANGELOG.md](CHANGELOG.md) — what changed in 3.0.0

## Self-checks

```powershell
npm test                          # scripts/selftest.mjs — fake-ctx load smoke test
npm run verify                    # scripts/verify-package.mjs — static release checks
npm run verify:caps               # scripts/verify-capabilities.mjs all
node scripts/verify-ledger.mjs all # ledger coverage (11 domains, 592 skills) + fused check
npm run pack:check                # npm pack --dry-run (~38 MB unpacked in v3; knowledge/ included by design)
```

Measured on the current v3 tree (final numbers follow once every domain lands): **4,577 files / 38.62 MB** on disk (`scripts/verify-package.mjs` count, includes `.github/`); the bulk is `knowledge/` — 592 source documents plus 3,924 bundled asset files.

## License

MIT — see [LICENSE](LICENSE).

**Scope note**: MIT covers the plugin itself (`lib/`, `data/`, `skills/`, `references/`, `scripts/`, `docs/` and the index files). The 592 skill texts and 3,924 bundled assets under `knowledge/skills/` are third-party material vendored verbatim from the author's local skill collection; their licenses belong to their original authors and are **not** covered by MIT. Read [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md) before redistributing.
