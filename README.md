# dsh-research-suite

[![CI](https://github.com/xuzhecomeon/dsh-research-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/xuzhecomeon/dsh-research-suite/actions/workflows/ci.yml)
[![npm](https://img.shields.io/npm/v/dsh-research-suite.svg)](https://www.npmjs.com/package/dsh-research-suite)
[![license](https://img.shields.io/npm/l/dsh-research-suite.svg)](LICENSE)

A DeepSeek Harness (DSH) plugin for the full clinical-research workflow — manuscript writing, language polishing, figures, statistics, research ideation, peer review, slides, literature search and journal formatting. Install it and it **takes over research tasks automatically**: no UI, no manual skill picking.

> 中文完整说明见 **[README.zh-CN.md](README.zh-CN.md)**（内容更全，含配置项、目录结构、占位符清单）。

- Package: `dsh-research-suite` · Version: `3.2.0` · License: MIT · DSH tested: `0.2.1-rc.5`, `0.2.2-rc.1`
- Requires Node `^22.19.0 || >=24.0.0`, DSH `>=0.2.0-0 <0.3.0`
- **Self-contained: all 450 source skill documents plus their bundled `references/scripts/templates` assets ship inside the package; nothing is read from any external skill directory at runtime.**

## Why capability cards instead of a skill router

The hard part of research work is not a lack of skills — it is that three to eight skills can each do the same task well in different ways. A router hands the model one "primary skill" name; the model then reads that skill's manual and improvises, losing the other skills' strengths along the way.

Instead, each **capability card** takes every competing skill in its group, records `best_at` (what it is best at), `limits` (what it explicitly cannot do) and `take` (the concrete rules, thresholds and templates lifted from it), then fuses them into one executable **protocol**. Every protocol step says which skill it comes from and why. The acceptance rule is strict: *after reading one capability card you can finish the job without opening any original skill document.*

The 450 source documents (and the 954 asset files they bring along) remain bundled as a deep-reading layer — for checking details, not for improvising.

## How auto-takeover works

No UI, no buttons. Three pieces:

1. **A system-prompt section** — `lib/prompt.js` builds a policy named `research-suite/policy` at `order: 650` ("after team policy, before tool docs"); `lib/index.js` registers it through `systemPrompt.section({ name, order, text: () => buildPolicy(core) })`. The policy tells the model: recognise a research task → call `research_playbook` first → follow the capability protocol → deep-read if needed → run `research_gate` before delivering.
2. **11 skills** (`skills/`): one entry skill plus ten domain SOPs (writing / polish / figures / stats / ideation / review / slides / literature / format / data). Their `content` is inlined **at registration time** — passing a lazy `load()` hook fails DSH's runtime validation and silently drops every skill (the exact failure mode of v1).
3. **15 tools (7 query + 8 execution/verification/generation/memory)** for capability lookup, searching the 450-document catalog, deep reading (including skill-bundled assets), standards, and mechanical self-checks.

When `research_playbook` finds no match, the policy falls back to `research_catalog` + `research_kb_read` rather than refusing the task.

## Domains

| Domain | Source skills | Covers |
|---|---:|---|
| `writing` | 64 | paper types and sections (original / review / case report / grant) |
| `polish` | 12 | register, de-AI-flavour, reduction, proofreading, Word reports |
| `figures` | 33 | data plots, statistical charts, mechanism diagrams, layout |
| `stats` | 30 | descriptive, comparison, regression, survival, prediction, PSM, MR, Meta, missing data, sample size |
| `ideation` | 37 | topic selection, novelty search, hypotheses, grants, ethics |
| `review` | 20 | self-review, reviewer comments, revision, rebuttal, response letters |
| `slides` | 37 | conference, lecture, defence, lab meeting, poster |
| `literature` | 26 | search strings, screening, close reading, evidence tables, recall/precision |
| `format` | 51 | journal formatting, references, figure/table specs, submission package |
| `data` | 40 | databases and omics data: GEO / TCGA / dbGaP / genotype and variant databases, omics retrieval and curation |
| **Total** | **450** | **103** capability cards across the ten domains |

`toolbox` is an additional index-only bucket of 100 utility skills: it feeds `research_catalog` and `research_kb_read`, and deliberately has **no capability cards** — a tool is a means, not a task a user asks for.

Every one of the 450 source skills has a recorded verdict in `data/ledger/<domain>.json` (`fused` — and which cards it feeds / `index-only` / `deprecated` / `out-of-scope`), so the "all studied, best only" claim is auditable: `node scripts/verify-ledger.mjs all` re-checks coverage and that every `fused` skill is actually a member of the card it claims. Beyond the text, **skill-bundled assets ship too**: 186 skills contribute 954 files (~6.8 MB) of `references/`, `scripts/` and `templates/` under `knowledge/skills/<domain>/<slug>__assets/`; `research_kb_read(name, asset='scripts/plot.py')` reads them (omitting `asset` lists what the skill ships with). Nine reference standards live in `references/`.

## Tools

| Tool | Purpose |
|---|---|
| `research_playbook` | **The only entry point.** Pass the user's own words; returns the 1–3 best-matching capability cards with protocol, gates, deliverables and suggested deep reads |
| `research_capability` | Expand a full capability card (member comparison, protocol, decisions, gates, outputs, kb) by `id` or by `domain` |
| `research_catalog` | Search the 450-document catalog by name/description keywords (the 100 `toolbox` skills included), optionally filtered by domain; each hit reports how many bundled assets it carries |
| `research_kb_read` | Read one skill document or `INDEX.md`/`FUSION.md`; the `asset` parameter reads a skill-bundled file such as `scripts/plot.py` or `references/*.md` (omitting it lists the skill's assets); paging and path-escape rejection included |
| `research_standard` | List or read the nine reference standards in `references/` |
| `research_gate` | Gate and mechanical self-check: `section` = `all` / `data` / `selfcheck` / `mutex` / `forbidden` / `hard` / `handoffs`; `text` checks fullwidth punctuation, superscript citation numbers, AI-cliché phrases and absolute wording |
| `research_suite_status` | Load self-check: version, per-domain capability counts, 450-entry catalog completeness, asset statistics, references, package root |
| `research_run` | **actually executes** an R or Python script and returns stdout/stderr plus produced files; **off by default** — first calls return a preview only (see Security below) | `kind` (r/python) + `code`, optional `workdir` / `confirm` / `previewHash` / `timeoutMs` |
| `research_data_check` | **mechanical half of the six data gates**: rows/cols, missing rate, constant columns, duplicate IDs, impossible values, EPV<10 | `file`, optional `outcome` / `predictors` |
| `research_output_check` | **deliverable audit**: real PNG DPI, PDF pages and text layer, DOCX/XLSX structure, CSV rows, MD word count | `files` |
| `research_doi_check` | **reference authenticity**: resolves each DOI against Crossref and returns title/journal/year; degrades honestly offline | `dois` |
| `research_ref_audit` | **citation reconciliation**: `[n]` gaps/duplicates, mismatch with the reference list, missing DOIs, suspicious years, duplicate DOIs | `text` or `file` |
| `research_project` | **project memory**: read/write `.dsh-research/project.json` — target journal, glossary, finalized sections, decisions — surviving across sessions | `action` (get/set/diff/list) |
| `research_docx` | **produce and audit .docx**: build a Chinese-journal-formatted Word file (SimSun 12pt, 1.5 spacing, first-line indent, three-line tables, hanging reference indent, superscript citations) or audit an existing one | `action` (build/audit) |
| `research_litsearch` | **real search**: PubMed via esearch+esummary (PMID/journal/year/authors/DOI), or field-by-field DOI comparison against expected metadata | `action` (pubmed/compare-doi) |

## Install

Published on npm as [dsh-research-suite@3.2.0](https://www.npmjs.com/package/dsh-research-suite).

```powershell
# via plugin_manager (GUI) — recommended
plugin_manager(action="install_bundle", target="dsh-research-suite@3.2.0")

# via CLI (Windows)
dsh.cmd plugin --profile desktop add dsh-research-suite@3.2.0
# via CLI (POSIX)
dsh plugin --profile desktop add dsh-research-suite@3.2.0

# from a local checkout (plugin development)
plugin_manager(action="install_bundle", target="<absolute package path>")

# from GitHub, if npm is not reachable
dsh plugin --profile desktop add github:xuzhecomeon/dsh-research-suite
```

Fully quit and restart DSH Desktop afterwards (closing the window is not enough — the loader reads the bundle patch layer at startup). Verify with `research_suite_status`.

## Configuration

The plugin deliberately **does not export a `Config`**: in v2.0.0 that export (`toJSON()` returning JSON Schema) was hydrated by DSH's Host settings service as a schemastery envelope, crashed on `schema.meta`, and prevented DSH Desktop from starting. Configuration is now validated inside `apply()` by `validateConfig()`.

| Key | Default | Meaning |
|---|---|---|
| `autoTakeover` | `true` | Inject the auto-takeover prompt section; `false` degrades the plugin to "15 tools + 11 skills" without automatic routing |
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
node scripts/verify-ledger.mjs all # ledger coverage (11 domains, 450 skills) + fused check
npm run pack:check                # npm pack --dry-run (~38 MB unpacked in v3; knowledge/ included by design)
```

Measured on the current v3 tree (final numbers follow once every domain lands): **1,481 files / 38.62 MB** on disk (`scripts/verify-package.mjs` count, includes `.github/`); the bulk is `knowledge/` — 450 source documents plus 954 bundled asset files.

## Security and execution boundary

**Execution is off by default.** This plugin can genuinely run code (`research_run`), which is exactly why it ships a safety layer: scripts generated by the model are treated as untrusted input.

The flow is two-stage: **preview → explicit confirmation with a matching `previewHash` → three gates (enabled flag / hash / static policy) → run**.

- `data/exec-policy.json` ships with `run.enabled: false`. In that state `research_run` returns a preview only (first 60 lines, sha256 `previewHash`, policy summary, predicted violations) and **never writes a file or spawns a process**.
- Once enabled, scripts run **with your user privileges** inside `<cwd>/.dsh-research/run/<runId>/`. The static scanner enforces package allowlists (separate lists for R and Python), rejects the common network and subprocess APIs, confines writes to relative paths inside that directory, rejects PHI path keywords, and permanently blocks installers. **This is a guardrail, not a sandbox** — real isolation requires a container, a restricted account, or a VM.
- `research_doi_check` does make network requests: it sends each DOI to `https://api.crossref.org` and nothing else (no manuscript or local file content). No other tool performs network requests.
- The plugin is self-contained: 450 source skill documents and 954 bundled assets ship inside the package; at runtime it reads no external skill directory.
- The entry module never imports `@deepseek-ai/*`: those packages do not resolve from the profile's `node_modules`, and a single import would make the whole plugin fail to load (symptom: "installed, but zero skills"). `scripts/verify-package.mjs` enforces this.

| Tool | Reads files | Writes files | Network | Subprocess | Blast radius |
| --- | --- | --- | --- | --- | --- |
| `research_playbook` / `research_capability` | yes (capability cards) | no | no | no | in-process, read-only |
| `research_catalog` / `research_kb_read` / `research_standard` | yes (index, skill docs & assets, references) | no | no | no | in-process, read-only, paths confined to the package |
| `research_gate` / `research_ref_audit` | no (analyses supplied text) | no | no | no | in-process text checks |
| `research_data_check` / `research_output_check` | yes (caller-supplied data/deliverable) | no | no | no | in-process, read-only |
| `research_suite_status` | yes (index, stats, policy) | no | no | `where` / `which` probes only | in-process + PATH probe |
| `research_doi_check` | no | no | **yes** (Crossref, DOI only) | no | sends DOI strings |
| `research_run` | **yes** (whatever the interpreter can read as your user) | **yes** (inside the run dir; out-of-bounds writes rejected) | **no by default** | **yes** (Rscript / python) | run dir + whatever your user account can reach |

How to enable execution, the full policy schema, the three isolation layers, and the known bypass limits are documented in [docs/SECURITY.md](docs/SECURITY.md).

## Honest capability boundary

An external expert review pointed out that this plugin used to describe its abilities far better than it could verify them. This section states both sides plainly.

**What it actually does**

1. **Gated task routing** — on a 50-utterance golden set: takeover decision 50/50 correct, all 5 non-research cases rejected, capability-card top-3 100%; reproducible via `node scripts/eval-match.mjs --strict` (also run in CI).
2. **Real execution** — `research_run` actually spawns R (Rscript) or Python in a scratch directory and returns stdout/stderr; the model cannot pretend it ran something.
3. **Mechanical data gates** — `research_data_check`: missing rates, constant columns, duplicate IDs, impossible values, EPV < 10.
4. **Deliverable audit** — `research_output_check`: real PNG DPI, PDF page count and text layer, DOCX/XLSX structure.
5. **Reference authenticity** — `research_doi_check` resolves DOIs against Crossref; `research_ref_audit` reconciles in-text `[n]` against the reference list.

**What it does not do**

1. **No plagiarism or AI-text detection** — both require uploading full texts to paid external services. Not provided, and not faked.
2. **No final statistical judgement** — tools cover mechanical checks only; model choice, confounding control and sensitivity analysis still follow the capability protocol with human judgement.
3. **No full-text verification of claims** — a DOI proves existence, not that the cited conclusion was read correctly.
4. **No taste** — the suite gives verifiable numbers (DPI, font size, palette), not "what an editor will like".
5. **Limited golden set** — the 50 utterances are self-authored; the mechanism generalises but the sample is small.
6. **Host interface dependency** — if the host exposes no `tools` / `systemPrompt` service, the plugin degrades instead of dying (skills and policy still load); check with `research_suite_status` or the "装载自检" line in the policy section.

## License

MIT — see [LICENSE](LICENSE).

**Scope note**: MIT covers the plugin itself (`lib/`, `data/`, `skills/`, `references/`, `scripts/`, `docs/` and the index files). The 450 skill texts and 954 bundled assets under `knowledge/skills/` are third-party material vendored verbatim from the author's local skill collection; their licenses belong to their original authors and are **not** covered by MIT. Read [docs/ATTRIBUTION.md](docs/ATTRIBUTION.md) before redistributing.
