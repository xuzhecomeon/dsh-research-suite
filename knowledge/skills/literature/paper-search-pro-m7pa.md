---

name: 论文搜索专业版
slug: paper-search-pro
version: 1.0.0
displayName: 论文搜索专业版
description: >
  Find academic papers across up to 7 sources (OpenAlex / Semantic Scholar / CrossRef / PubMed / arXiv for English, plus native-Chinese retrieval via NSSD 国家哲社文献中心 + yiigle 中华医学期刊) with adjustable depth — Quick scan (5 min) to Audit prep (3 hr). Use when the user wants to find papers, run a literature search, gather references, scope a research topic, search Chinese-language / 中文原生 literature (中文文献/中文核心/CSSCI/C刊/国内研究/国内文献/中华××期刊/心理学报/经济研究), or filter results by journal tier (中科院分区/一区/几区, Q1, JCR/S
summary: "Find academic papers across up to 7 sources (OpenAlex / Semantic Scholar / CrossRef / PubMed / arXiv for English, plus native-Chinese retrieval via NSSD 国家哲社文献中心 + yiigle 中华医学期刊) with adjustable depth"
license: Apache-2.0
category: 学术研究
framework:
  - Claude Code
  - Codex
  - Hermes Agent
  - OpenClaw
  - QClaw
  - WorkBuddy
platform: multi-platform
homepage: "https://github.com/1991513ccie-png"
repository: "https://github.com/1991513ccie-png"

---




# paper-search-pro

Multi-source literature search with adjustable depth. Four tiers, five data sources orchestrated by you (the main agent). Python helpers handle deterministic work; LLM classification is delegated to parallel Inline SubAgents — no external API key required.

## When to use this skill

- User wants to find academic papers / 找文献 / 论文搜索
- User is preparing a literature review, systematic review (SR), scoping review, or meta-analysis
- User wants to scope research on a topic for a thesis / proposal / coursework / news story
- User asks "what research exists on X" / "find me papers about Y"
- User uploads a query that suggests literature gathering (PICO, SPIDER, MeSH, RCT, etc.)

## When NOT to use

- User wants to **read** a specific paper (use PDF reader / download tool)
- User wants to **summarize** a single known paper (use a summarizer)
- User wants to **download** PDFs given DOIs (use `paper-downloader-portable`)
- User already has a literature set and wants to write a review (use `literature-set-review` / `factor-outcome-review`)
- User wants concept explanation, not papers ("what is prospect theory" → just answer)

