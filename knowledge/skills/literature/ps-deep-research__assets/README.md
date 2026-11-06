# deep-research

**English** · [简体中文](README.zh-CN.md)

> A "deep research" skill for Claude Code: works like a senior consultant — understand the question → produce a research plan → verify iteratively across multiple sources (with built-in dissent and cross-checking) → deliver a report with a judgment, evidence, and traceable sources.

A plain Q&A easily hands you an answer that *sounds* right. Deep research is different: it forms hypotheses, dispatches several independent researchers to verify in parallel, actively hunts for counter-evidence, checks recency, and ends with a judgment that carries a confidence level and "under what conditions this conclusion would be wrong." Good for selection, due diligence, comparison, and investment/purchase decisions — anything you can't afford to wing.

## Three-step workflow

1. **Research plan** — restate your question + a tentative take + 3-5 angles + expected depth, shown to you first.
   - **Clear-direction questions with nothing for you to steer** (diagnostic / verification / status, e.g. "why does X do Y") **→ no plan, no prompt, it just starts.**
   - When direction is open (survey / selection / scope is yours to set), it shows the plan and **auto-starts 60 seconds later**; during that window you can change the plan, or reply "start now" to go immediately.
   - Put "立即开始 / start now" in the command from the outset to skip the wait entirely.
2. **Autonomous research** — dispatches sub-agents to search, extract, cross-verify and find dissent in parallel; decides whether to run another round based on saturation. No interruptions once started.
3. **Deliver report** — consultant-grade analysis (central thesis, judgment, actionable next steps), not a dump of search results.

## Install

```bash
# 1) Drop it into the Claude Code skills directory
cp -r deep-research ~/.claude/skills/deep-research

# 2) (Optional) install the /deep-research command alias: put the command file into ~/.claude/commands/
```

Then in Claude Code just say "deep research \<topic\>" or `/deep-research \<topic\>`.

## Quality tiers

| Tier | Time | researchers | Words | For |
|---|---|---|---|---|
| **fast** | 5-10 min | 0 (main agent) | 1000-2500 | single-point deepening / decision memo |
| **standard** (default) | 15-30 min | ≥2 | 2500-5000 | medium research / selection |
| **deep** | 40-60 min | ≥4 | 5000-12000 | systematic research / major decisions |

If any hard constraint isn't met, the report **honestly flags** `degraded` up front — it never pretends to have done the full job.

## Five golden rules

1. **No fabrication** — every number has a traceable source; if unsure, say so.
2. **Find the other side** — actively search counter-views and failure cases; one-sided = not done.
3. **Mark the gaps** — "I don't know X, so confidence in Y is only Z."
4. **Give a judgment** — central thesis, confidence, actionable next step.
5. **Be falsifiable** — every core conclusion ships with "under what conditions it's wrong."

## Self-check

After changing the skill itself, run the built-in harness:

```bash
bash hooks/verify.sh all   # fixture self-tests + cross-file consistency + skill integrity
```

## File layout

| File | Purpose |
|---|---|
| `SKILL.md` | workflow + hard constraints + golden rules (single source of truth) |
| `PLAYBOOK.md` | per-phase execution detail, researcher prompts, saturation criteria |
| `REPORT_TEMPLATES.md` | survey / compare / decide / howto report skeletons |
| `RUBRIC.md` | Devil's Advocate + self-scoring |
| `WRITING_STYLE.md` | consultant-grade writing standard |
| `experts/` | per-domain quality-dimension templates |
| `hooks/` | output-validation scripts + self-check harness |

## Methodological basis

An engineering combination of several published research methods (understand the spirit, apply as needed, no name-dropping): ReAct, Reflexion, Self-Ask, CRAG, Step-Back, the Toulmin argument model, plus targeted re-checking for "later sections hallucinate more."

## License

[MIT](LICENSE)
