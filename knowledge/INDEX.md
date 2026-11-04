# 技能索引（719 个 SKILL 的全量编目）

本文件由 `analysis/build-index.mjs` 从 `knowledge/catalog.json` 与 `data/capabilities/*.json` 生成，
是**目录层**的索引：告诉你包里到底有哪些技能、每题正文在哪、被哪张能力卡引用。

- 想知道“这个任务该怎么做”：走 `research_playbook`，看**能力卡**，不要在本索引里挑技能。
- 想知道某个技能原文：`research_kb_read(name="<技能名>")`，按 `file` 列的相对路径读取。
- 本索引只在“同名近似技能到底哪个更全”这类**证据等级**问题上使用。

合计 719 个技能（科研相关 489 个），分布在 9 个能力域 + 1 个通用域；
被能力卡引用 177 个，其余仅编目留档。

## 域目录

| 域 | 技能数 | 科研相关 | 被能力卡引用 | 对应技能文件 |
|---|---:|---:|---:|---|
| 论文撰写 | 51 | 40 | 19 | `skills/research-writing.md` |
| 润色与去 AI 痕迹 | 24 | 20 | 14 | `skills/research-polish.md` |
| 科研绘图 | 76 | 58 | 21 | `skills/research-figures.md` |
| 科研统计 | 180 | 132 | 27 | `skills/research-stats.md` |
| 科研思路与标书 | 33 | 25 | 22 | `skills/research-ideation.md` |
| 审稿与修回 | 39 | 28 | 19 | `skills/research-review.md` |
| 科研汇报与 PPT | 44 | 40 | 16 | `skills/research-slides.md` |
| 文献与引文 | 152 | 115 | 32 | `skills/research-literature.md` |
| 格式与交付 | 32 | 31 | 9 | `skills/research-format.md` |
| 通用（不进融合，仅编目） | 88 | 0 | 0 | — |

## 论文撰写（51）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `airs-autoresearch` | 24.8K | ✓ | — | `skills/writing/airs-autoresearch.md` |
| ↳ | | | | Orchestrates end-to-end autonomous AI research projects using a two-loop architecture. The inner loop runs rapid experiment iterations with … |
| `airs-implementing-llms-litgpt` | 11.3K | ✓ | — | `skills/writing/airs-implementing-llms-litgpt.md` |
| ↳ | | | | Implements and trains LLMs using Lightning AI's LitGPT with 20+ pretrained architectures (Llama, Gemma, Phi, Qwen, Mistral). Use when need c… |
| `airs-ml-paper-writing` | 37.8K | ✓ | — | `skills/writing/airs-ml-paper-writing.md` |
| ↳ | | | | Write publication-ready ML/AI papers for NeurIPS, ICML, ICLR, ACL, AAAI, COLM. Use when drafting papers from research repos, structuring arg… |
| `airs-torchforge-rl-training` | 11.0K | ✓ | — | `skills/writing/airs-torchforge-rl-training.md` |
| ↳ | | | | Provides guidance for PyTorch-native agentic RL using torchforge, Meta's library separating infra from algorithms. Use when you want clean R… |
| `aris-integrity-forensics` | 17.1K | ✓ | — | `skills/writing/aris-integrity-forensics.md` |
| ↳ | | | | Run the Anti-Autoresearch integrity-forensics sweep (span-anchored evidence ledger → GPT auditors propose findings → a rules-only reporter t… |
| `aris-paper-write` | 39.1K | ✓ | — | `skills/writing/aris-paper-write.md` |
| ↳ | | | | Draft LaTeX paper section by section from an outline. Use when user says \"写论文\", \"write paper\", \"draft LaTeX\", \"开始写\", or wants to gen… |
| `aris-proof-orchestrator` | 18.8K | ✓ | — | `skills/writing/aris-proof-orchestrator.md` |
| ↳ | | | | Manage a stateful, run-directory-based proof project: continuation across runs, run-local source bookkeeping, manual GPT Pro handoff package… |
| `aris-proof-writer` | 8.5K |  | — | `skills/writing/aris-proof-writer.md` |
| ↳ | | | | Writes rigorous mathematical proofs for ML/AI theory. Use when asked to prove a theorem, lemma, proposition, or corollary, fill in missing p… |
| `aris-result-to-claim` | 17.8K |  | — | `skills/writing/aris-result-to-claim.md` |
| ↳ | | | | Use when experiments complete to judge what claims the results support, what they don't, and what evidence is still missing. Codex MCP evalu… |
| `bib-search-citation` | 9.0K | ✓ | writing.citation-format(member) | `skills/writing/bib-search-citation.md` |
| ↳ | | | | Search and cite from local BibTeX/BibLaTeX .bib libraries, including Zotero exports. Use to find, filter, preview, export, or generate LaTeX… |
| `biomedical-sci-manuscript` | 4.6K | ✓ | — | `skills/writing/biomedical-sci-manuscript.md` |
| ↳ | | | | Create SCI manuscript drafts for biomedical Methods/Results material across three study types: bioinformatics, clinical medicine, and basic … |
| `brainstorming-research` | 10.8K | ✓ | writing.thesis(member)、writing.outline-blueprint(member) | `skills/writing/brainstorming-research.md` |
| ↳ | | | | Use before writing any paper - clarifies paper type, discipline, topic, methodology, and chapter structure through natural dialogue |
| `chinese-medical-paper-writer` | 29.3K | ✓ | format.ref-style(member)、format.intext-cite(member)、format.figtable(member)、format.submission-package(member)、stats.meta(member)、writing.zh-med-imrad(member)、writing.zh-med-voice(member)、writing.review(member)、writing.case-report(member)、writing.abstract-keywords(member)、writing.figure-table(member)、writing.discussion-limits(member)、writing.citation-format(member) | `skills/writing/chinese-medical-paper-writer.md` |
| ↳ | | | | 中文医学期刊论文写作助手（chinese-medical-paper-writer）。中文医学期刊论文（中华医学会系列期刊模板）撰写、润色、参考文献规范化与完整投稿包生成。撰写类任务必须先做"前置问答环节"（篇幅、重点论述内容、参考文献数量质量、目标期刊、作者信息），并充分阅读知… |
| `clinical-reports` | 38.8K | ✓ | writing.case-report(member) | `skills/writing/clinical-reports.md` |
| ↳ | | | | Write comprehensive clinical reports including case reports (CARE guidelines), diagnostic reports (radiology/pathology/lab), clinical trial … |
| `consciousness-council` | 8.6K | ✓ | — | `skills/writing/consciousness-council.md` |
| ↳ | | | | Run a multi-perspective Mind Council deliberation on any question, decision, or creative challenge. Use this skill whenever the user wants d… |
| `cover-letter` | 11.4K | ✓ | format.submission-package(member)、format.journal-fit(member)、writing.case-report(member) | `skills/writing/cover-letter.md` |
| ↳ | | | | Submission cover-letter assistant for existing LaTeX manuscripts. Use to generate, optimize, align-check, preflight, and journal-fit-check c… |
| `dhdna-profiler` | 9.9K |  | — | `skills/writing/dhdna-profiler.md` |
| ↳ | | | | Extract cognitive patterns and thinking fingerprints from any text. Use this skill when the user wants to analyze how someone thinks, unders… |
| `intro-drafter` | 9.7K | ✓ | writing.outline-blueprint(member) | `skills/writing/intro-drafter.md` |
| ↳ | | | | Drafts the Introduction prose for a technical paper, guided internally by a six-paragraph flowchart: background and running example, existin… |
| `karpathy-guidelines` | 2.5K |  | — | `skills/writing/karpathy-guidelines.md` |
| ↳ | | | | Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make… |
| `latex-paper-en` | 19.3K | ✓ | writing.en-sci(member) | `skills/writing/latex-paper-en.md` |
| ↳ | | | | English LaTeX assistant for existing .tex journal or conference papers. Use for compile repair, venue formatting, bibliography/citation chec… |
| `latex-thesis-zh` | 37.0K | ✓ | writing.thesis(member)、writing.abstract-keywords(member)、writing.figure-table(member)、writing.citation-format(member) | `skills/writing/latex-thesis-zh.md` |
| ↳ | | | | 中文 LaTeX 学位论文助手，面向已有 .tex 硕博论文工程与学位论文评阅书：编译诊断、GB/T 7714、模板识别、结构/格式/公式断行、术语一致性、逻辑与文献综述、方法/工程应用章、标题优化、去 AI 味、主张前置（自我削弱/免责句后置）检查、单元润色与漂移核对、盲审隐匿… |
| `literature-monitor-skills` | 12.8K | ✓ | — | `skills/writing/literature-monitor-skills.md` |
| ↳ | | | | Monitor when scholarly articles first become visible to readers on official journal or publisher surfaces—such as ASAP, Online First, Early … |
| `literature-review-writing` | 11.3K | ✓ | writing.review(member) | `skills/writing/literature-review-writing.md` |
| ↳ | | | | 帮助用户撰写高质量的文献综述类论文。提供从选题、文献检索、评估筛选、结构规划到最终写作的全流程指导。适用于需要撰写独立文献综述论文或学术论文中文献综述部分的用户。 |
| `nature-data` | 3.9K | ✓ | — | `skills/writing/nature-data.md` |
| ↳ | | | | Draft or audit manuscript Data/Code Availability statements, dataset access routes, repository plans, and FAIR metadata. Use for 数据可用性声明、数据共… |
| `nature-paper-to-patent` | 4.6K | ✓ | — | `skills/writing/nature-paper-to-patent.md` |
| ↳ | | | | Turn research papers or inventor materials into evidence-grounded Chinese invention patent drafts and technical disclosures. Use for 技术交底书、专… |
| `nature-polishing` | 6.0K | ✓ | — | `skills/writing/nature-polishing.md` |
| ↳ | | | | Polish, translate, or tighten existing academic prose while preserving facts, terminology, and evidence boundaries. Use for 论文润色、学术翻译、正文精简, … |
| `nature-writing` | 8.2K | ✓ | — | `skills/writing/nature-writing.md` |
| ↳ | | | | Draft or restructure scientific manuscript arguments, sections, and initial-submission materials from author-provided evidence. Use for 论文写作… |
| `no-ai-slop` | 10.7K | ✓ | writing.zh-med-voice(member) | `skills/writing/no-ai-slop.md` |
| ↳ | | | | Edit drafts into sharper, more human writing while preserving the writer's personal voice, or detect AI-slop patterns without rewriting. Use… |
| `opentrons-integration` | 14.5K |  | — | `skills/writing/opentrons-integration.md` |
| ↳ | | | | Official Opentrons Protocol API for OT-2 and Flex robots. Use when writing protocols specifically for Opentrons hardware with full access to… |
| `paper-polish` | 12.3K | ✓ | writing.zh-med-voice(member)、writing.en-sci(member)、writing.discussion-limits(member) | `skills/writing/paper-polish.md` |
| ↳ | | | | Polishes existing academic prose while preserving the author's meaning: grammar and flow repair, tone calibration against evidence strength,… |
| `paper-writer` | 14.0K | ✓ | writing.zh-med-imrad(member)、writing.discussion-limits(member)、writing.outline-blueprint(member) | `skills/writing/paper-writer.md` |
| ↳ | | | | Drafts publishable paper prose from the author's own materials, from a single paragraph to a full manuscript, across STEM and non-STEM field… |
| `paper-writing-studio` | 9.6K | ✓ | writing.en-sci(member) | `skills/writing/paper-writing-studio.md` |
| ↳ | | | | Use this academic writing skill to polish or translate academic writing with an explicit Nature, IEEE, Elsevier, or neutral profile. Selects… |
| `protocolsio-integration` | 14.6K | ✓ | — | `skills/writing/protocolsio-integration.md` |
| ↳ | | | | Integration with protocols.io API for managing scientific protocols. This skill should be used when working with protocols.io to search, cre… |
| `research-writing-assistant` | 8.0K | ✓ | — | `skills/writing/research-writing-assistant.md` |
| ↳ | | | | Use when writing academic papers, theses, or research articles - supports brainstorming, chapter writing, literature review, and LaTeX outpu… |
| `scholar-design` | 115.6K | ✓ | — | `skills/writing/scholar-design.md` |
| ↳ | | | | Plan a rigorous research design, run power analysis, specify variables, select an analytic strategy, design computational studies (NLP/ML/ne… |
| `scholar-hypothesis` | 43.8K | ✓ | — | `skills/writing/scholar-hypothesis.md` |
| ↳ | | | | Develop theoretically grounded hypotheses and draft publication-ready Theory sections. Covers puzzle framing (5 types: anomaly, contradictio… |
| `scholar-journal` | 57.7K | ✓ | format.submission-package(member)、format.journal-fit(member) | `skills/writing/scholar-journal.md` |
| ↳ | | | | Format, select, and prepare a manuscript for journal submission. 5 modes: FULL-PACKAGE (structure audit + checklist + cover letter + open sc… |
| `scholar-write` | 43.8K | ✓ | — | `skills/writing/scholar-write.md` |
| ↳ | | | | Draft, revise, or polish any section of a social science manuscript — Introduction, Theory, Methods, Results, Discussion, Abstract, or full … |
| `scientific-graphical-abstract-skill__skillhub` | 4.4K | ✓ | — | `skills/writing/scientific-graphical-abstract-skill.md` |
| `scientific-writing` | 33.1K | ✓ | writing.en-sci(member)、writing.review(member)、writing.abstract-keywords(member)、writing.figure-table(member)、writing.discussion-limits(member)、writing.citation-format(member) | `skills/writing/scientific-writing.md` |
| ↳ | | | | Core skill for the deep research and writing tool. Write scientific manuscripts in full paragraphs (never bullet points). Use two-stage proc… |
| `sp-test-driven-development` | 9.8K |  | — | `skills/writing/sp-test-driven-development.md` |
| ↳ | | | | Use when implementing any feature or bugfix, before writing implementation code |
| `sp-writing-plans` | 10.4K |  | — | `skills/writing/sp-writing-plans.md` |
| ↳ | | | | Use when you have a spec or requirements for a multi-step task, before touching code |
| `sp-writing-skills` | 16.8K |  | — | `skills/writing/sp-writing-skills.md` |
| ↳ | | | | Use when creating new skills, editing existing skills, or verifying skills work before deployment |
| `thesis-writing-companion` | 8.3K | ✓ | writing.thesis(member) | `skills/writing/thesis-writing-companion.md` |
| ↳ | | | | 论文写作全流程助手。覆盖从选题、开题、文献综述、研究方法、写作、修改润色、查重与 AIGC 检测、答辩到发表的完整论文生命周期；支持多语言（中文 / English / 日本語 / 한국어 / Français / Deutsch / Español / Português / … |
| `torchdrug` | 13.9K | ✓ | — | `skills/writing/torchdrug.md` |
| ↳ | | | | PyTorch-native graph neural networks for molecules and proteins. Use when building custom GNN architectures for drug discovery, protein mode… |
| `using-research-writing` | 6.3K |  | — | `skills/writing/using-research-writing.md` |
| ↳ | | | | Use when starting any research writing task - establishes workflow and routes to appropriate skills |
| `verification` | 4.3K | ✓ | — | `skills/writing/verification.md` |
| ↳ | | | | Use when about to claim work is complete, a chapter is finished, or references are verified - requires running verification commands and con… |
| `writing-chapters` | 11.9K | ✓ | writing.zh-med-imrad(member)、writing.review(member)、writing.thesis(member)、writing.abstract-keywords(member)、writing.figure-table(member)、writing.outline-blueprint(member) | `skills/writing/writing-chapters.md` |
| ↳ | | | | Use when writing paper chapters - requires completed brainstorming, writes one chapter at a time with user confirmation |
| `writing-core` | 5.9K | ✓ | writing.zh-med-voice(member) | `skills/writing/writing-core.md` |
| ↳ | | | | Use when writing or revising academic papers, especially Chinese journal manuscripts, that need natural prose, de-AI-ification, Markdown for… |
| `writing-humanities` | 5.4K |  | — | `skills/writing/writing-humanities.md` |
| ↳ | | | | Use when writing humanities or social science papers - provides discipline-specific writing guidance |
| `writing-medical` | 4.2K |  | writing.zh-med-imrad(member) | `skills/writing/writing-medical.md` |
| ↳ | | | | Use when writing medical, biological, or clinical research papers - provides IMRaD structure and reporting guidelines |

## 润色与去 AI 痕迹（24）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `academic-polish` | 2.6K | ✓ | polish.rewrite(member)、polish.audit(member) | `skills/polish/academic-polish.md` |
| ↳ | | | | 学术文本润色：去口语化、优化逻辑、保持术语不变、中英互译、输出修改对照。 |
| `aris-render-html` | 22.8K | ✓ | — | `skills/polish/aris-render-html.md` |
| ↳ | | | | Render an ARIS Markdown / JSON artifact (IDEA_REPORT, AUTO_REVIEW, KILL_ARGUMENT, PAPER_PLAN, research-wiki state, etc.) into a single-file … |
| `aris-research-pipeline` | 24.2K | ✓ | — | `skills/polish/aris-research-pipeline.md` |
| ↳ | | | | Full end-to-end research pipeline: from a broad research direction through idea discovery, experiments, and review all the way to a polished… |
| `aris-research-refine-pipeline` | 7.1K |  | — | `skills/polish/aris-research-refine-pipeline.md` |
| ↳ | | | | Run an end-to-end workflow that chains `research-refine` and `experiment-plan`. Use when the user wants a one-shot pipeline from vague resea… |
| `design-taste-frontend` | 38.7K | ✓ | — | `skills/polish/design-taste-frontend.md` |
| ↳ | | | | tasteskill v2, the anti-slop frontend skill. Art direction for websites, distilled from a study of 247 curated gallery sites (One Page Love,… |
| `gm-muapi-chibi-collage-effect` | 5.1K | ✓ | — | `skills/polish/gm-muapi-chibi-collage-effect.md` |
| ↳ | | | | Turn a real lifestyle photo into a polished "chibi clone sticker diary" image — the original person stays photorealistic, surrounded by 5–8 … |
| `gm-muapi-instagram-post` | 2.9K | ✓ | — | `skills/polish/gm-muapi-instagram-post.md` |
| ↳ | | | | Create a polished, on-brand Instagram post — square or portrait hero image with matching caption and hashtags. |
| `gm-muapi-logo-generator` | 3.2K | ✓ | — | `skills/polish/gm-muapi-logo-generator.md` |
| ↳ | | | | Quickly generate a single polished logo for any brand — fast, focused, single output with clean vector aesthetic and accurate brand name tex… |
| `gm-muapi-media-editing` | 1.9K |  | — | `skills/polish/gm-muapi-media-editing.md` |
| ↳ | | | | Edit and enhance images and videos with AI via muapi.ai — prompt-based editing, upscaling, background removal, face swap, lipsync, video eff… |
| `gm-muapi-workflow` | 6.7K |  | — | `skills/polish/gm-muapi-workflow.md` |
| ↳ | | | | Build, run, and visualize multi-step AI generation workflows. The AI architect translates natural language descriptions into connected node … |
| `humanizer` | 17.4K | ✓ | polish.en(member) | `skills/polish/humanizer.md` |
| ↳ | | | | Remove signs of AI-generated writing from text. Use when editing or reviewing text to make it sound more natural and human-written. Based on… |
| `humanizer-zh` | 20.6K | ✓ | polish.deai(member)、polish.voice(member) | `skills/polish/humanizer-zh.md` |
| ↳ | | | | 编辑中文文章、评论和文档中的空话、重复及模板化表达，让文字更自然，同时保留事实、确定程度和作者声音。适用于润色已有文本，不用于判断作者身份或保证通过 AI 检测器。触发词：去 AI 味、去除 AI 痕迹、去 AI 化、降 AI 味、写得像人写的、论文/综述/标书/科普去 AI 味… |
| `investigate-first` | 0.7K |  | — | `skills/polish/investigate-first.md` |
| ↳ | | | | Diagnose ambiguous failures before editing. Use for unknown causes, intermittent behavior, performance regressions, or investigations needin… |
| `paper-checker` | 3.1K | ✓ | polish.audit(member) | `skills/polish/paper-checker.md` |
| ↳ | | | | 论文查重与AI率检测工具，支持中文英文论文查重、AI率检测、降重和降AI率处理。用于：(1)上传论文文件进行查重和AI率检测 (2)生成详细的重复率和AI率报告 (3)对高重复率内容进行降重改写 (4)对高AI率内容进行降AI率处理。不需要API key，直接能用。 |
| `paper-deweight` | 10.6K | ✓ | polish.deai(member)、polish.rewrite(member) | `skills/polish/paper-deweight.md` |
| ↳ | | | | 论文降重工具。用于降低论文重复率和 AIGC 检测率，通过同义词替换、句式变换、结构重组、文献综述模板等方法对论文进行改写降重。覆盖词汇/句式层与篇章结构层双维度降AI（序数并列、对仗结构、总分总闭环、句长节奏等七类高频痕迹模式）。改写遵循三条硬性铁律：保持学术风格（原文口语化也… |
| `paper-polisher` | 6.8K | ✓ | polish.rewrite(member)、polish.audit(member) | `skills/polish/paper-polisher.md` |
| ↳ | | | | 学术论文智能精修工具，一站式完成论文降重、AI痕迹去除与 Word 文档输出。当用户需要为论文降重、去AI味、学术文本润色、生成精修后的Word文档时触发。全自动流程：降低查重率 → 去除AI写作特征 → 输出专业Word文档。 |
| `paper-revision-sop` | 8.0K | ✓ | polish.deai(member)、polish.audit(member) | `skills/polish/paper-revision-sop.md` |
| ↳ | | | | 学术论文润色修改全流程SOP。从审稿意见解析、论文全息诊断、可视化批注生成、分级改写执行到终审自检的完整闭环。当用户需要根据期刊审稿意见修改论文、需要论文润色、需要去AI味、需要学术写作规范检查时触发。典型触发："修改这篇论文""根据审稿意见润色""去AI味""按期刊要求压缩字数… |
| `prompts-collection` | 7.4K | ✓ | polish.en(member) | `skills/polish/prompts-collection.md` |
| ↳ | | | | Use for translation, polishing, or de-AI-ification of academic text - provides ready-to-use prompt templates |
| `qinyan-paper-polish` | 5.1K | ✓ | polish.rewrite(member) | `skills/polish/qinyan-paper-polish.md` |
| ↳ | | | | 沁言学术论文润色优化 - 按照专业学术规范对中英文学术论文、专业报告进行文本润色，提升语言表达质量、逻辑连贯性和学术规范性。触发词：论文润色、论文修改、润色优化、paper polishing、academic writing、论文改写、文本润色、报告润色 |
| `scholar-polish` | 47.4K | ✓ | polish.en(member)、polish.voice(member) | `skills/polish/scholar-polish.md` |
| ↳ | | | | Personalize and refine academic manuscript writing style by injecting distinctive authorial micro-patterns (tiny topos). Detects and replace… |
| `sepia` | 15.1K | ✓ | polish.voice(member) | `skills/polish/sepia.md` |
| ↳ | | | | Make AI-generated writing read as human-written, in fiction and in professional prose. Repairs the narrative architecture of fiction and sto… |
| `stop-slop` | 2.6K | ✓ | polish.deai(member) | `skills/polish/stop-slop.md` |
| ↳ | | | | Remove AI writing patterns from prose. Use when drafting, editing, or reviewing text to eliminate predictable AI tells. |
| `style-journal-rewrite` | 5.6K | ✓ | polish.voice(member) | `skills/polish/style-journal-rewrite.md` |
| ↳ | | | | 按目标文风或目标期刊格式改写初稿。用户说"改成XX风格""仿照这个味道""按XX期刊格式整理""参考这篇格式改"时触发。输入可为 .docx / .md / .txt 或对话文本。 |
| `wb-academic-polish` | 10.0K | ✓ | polish.en(member) | `skills/polish/wb-academic-polish.md` |
| ↳ | | | | 英文润色降重、期刊匹配推荐、投稿信撰写、参考文献格式校正、基金申请书润色、Abstract polishing、Reviewer Response 撰写、AIGC率检测与重写、native speaker级英文表达、学科术语校准——学术文本深度润色引擎：中英文学术论文/摘要/基金… |

## 科研绘图（76）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `academic-figures` | 30.8K | ✓ | figures.statplot(member)、figures.panel(member)、figures.flow(member)、figures.audit(member) | `skills/figures/academic-figures.md` |
| ↳ | | | | 论文配图一键生成：一条命令从 JSON/CSV/Excel 生成顶刊级学术图表，科研绘图 与期刊配图全场景覆盖。40 种图表（森林图/KM 生存曲线（自动风险表）/竞争风险累计发生率/ROC/校准 曲线/决策曲线 DCA/列线图/RCS 非线性剂量反应/亚组分析森林图/RMST … |
| `ai-figure-studio` | 25.5K | ✓ | figures.mechanism(member) | `skills/figures/ai-figure-studio.md` |
| ↳ | | | | 论文插图 AI 绘制工作室 —— 从论文 PDF 提取机制图/流程图/实验示意图，逐张临摹为可编辑矢量（活字文字 + 语义分组 + 全英文），并通读全文后重绘原创机制图，最终在 Adobe Illustrator 中输出 .ai 文件。当用户提到「临摹论文图」「重绘机制图」「AI… |
| `airs-academic-plotting` | 21.2K | ✓ | — | `skills/figures/airs-academic-plotting.md` |
| ↳ | | | | Generates publication-quality figures for ML papers from research context. Given a paper section or description, extracts system components … |
| `airs-blip-2-vision-language` | 18.8K |  | — | `skills/figures/airs-blip-2-vision-language.md` |
| ↳ | | | | Vision-language pre-training framework bridging frozen image encoders and LLMs. Use when you need image captioning, visual question answerin… |
| `airs-clip` | 7.0K |  | — | `skills/figures/airs-clip.md` |
| ↳ | | | | OpenAI's model connecting vision and language. Enables zero-shot image classification, image-text matching, and cross-modal retrieval. Train… |
| `airs-nemo-curator` | 9.6K |  | — | `skills/figures/airs-nemo-curator.md` |
| ↳ | | | | GPU-accelerated data curation for LLM training. Supports text/image/video/audio. Features fuzzy deduplication (16× faster), quality filterin… |
| `airs-segment-anything-model` | 13.7K |  | figures.image(member) | `skills/figures/airs-segment-anything-model.md` |
| ↳ | | | | Foundation model for image segmentation with zero-shot transfer. Use when you need to segment any object in images using points, boxes, or m… |
| `airs-sentence-transformers` | 6.5K |  | — | `skills/figures/airs-sentence-transformers.md` |
| ↳ | | | | Framework for state-of-the-art sentence, text, and image embeddings. Provides 5000+ pre-trained models for semantic similarity, clustering, … |
| `airs-stable-diffusion-image-generation` | 13.3K |  | — | `skills/figures/airs-stable-diffusion-image-generation.md` |
| ↳ | | | | State-of-the-art text-to-image generation with Stable Diffusion models via HuggingFace Diffusers. Use when generating images from text promp… |
| `airs-tensorboard` | 15.6K | ✓ | — | `skills/figures/airs-tensorboard.md` |
| ↳ | | | | Visualize training metrics, debug models with histograms, compare experiments, visualize model graphs, and profile performance with TensorBo… |
| `aris-auto-review-loop-llm` | 8.5K | ✓ | — | `skills/figures/aris-auto-review-loop-llm.md` |
| ↳ | | | | Autonomous research review loop using any OpenAI-compatible LLM API. Configure via llm-chat MCP server or environment variables. Trigger wit… |
| `aris-paper-illustration-image2` | 19.9K | ✓ | — | `skills/figures/aris-paper-illustration-image2.md` |
| ↳ | | | | Generate publication-quality academic illustrations through a local Codex app-server bridge that uses Codex native image generation. This is… |
| `aris-paper-poster-html` | 19.4K | ✓ | — | `skills/figures/aris-paper-poster-html.md` |
| ↳ | | | | DEFAULT poster pipeline — build an academic conference poster (ICML/NeurIPS/ICLR/CVPR/...) as a single HTML/CSS file with measurement-driven… |
| `caveman-compress` | 5.5K | ✓ | — | `skills/figures/caveman-compress.md` |
| ↳ | | | | Compress a memory file such as CLAUDE.md or a todo list into caveman format to save input tokens, keeping a readable backup. Sends the file'… |
| `csv-data-summarizer` | 5.6K | ✓ | — | `skills/figures/csv-data-summarizer.md` |
| ↳ | | | | Analyzes CSV files, generates summary stats, and plots quick visualizations using Python and pandas. |
| `data-analysis-pro` | 11.3K | ✓ | — | `skills/figures/data-analysis-pro.md` |
| ↳ | | | | End-to-end data analysis assistant. Covers data processing, insight generation, report writing, and data visualization workflows. Always app… |
| `datacommons-client` | 7.9K | ✓ | — | `skills/figures/datacommons-client.md` |
| ↳ | | | | Work with Data Commons, a platform providing programmatic access to public statistical data from global sources. Use this skill when working… |
| `deeptools` | 17.6K | ✓ | — | `skills/figures/deeptools.md` |
| ↳ | | | | NGS analysis toolkit. BAM to bigWig conversion, QC (correlation, PCA, fingerprints), heatmaps/profiles (TSS, peaks), for ChIP-seq, RNA-seq, … |
| `document-illustrator` | 11.5K | ✓ | — | `skills/figures/document-illustrator.md` |
| ↳ | | | | 基于文档内容自动生成配图。AI 智能分析文档结构，归纳核心要点， 为每个主题生成符合特定风格的配图。支持封面图生成和自定义图片比例。 使用场景：当用户需要为文档、文章、笔记生成配图时。 关键词：配图、插图、illustration、generate images、document… |
| `drawio-reconstruction` | 21.6K | ✓ | figures.vector(member) | `skills/figures/drawio-reconstruction.md` |
| ↳ | | | | Reconstructs reference images into high-fidelity, editable Draw.io files with rendered previews: native Draw.io elements carry text and stru… |
| `environment-setup` | 4.0K | ✓ | — | `skills/figures/environment-setup.md` |
| ↳ | | | | Use when Python environment setup is needed for data visualization or conda installation is required |
| `etetoolkit` | 17.5K | ✓ | — | `skills/figures/etetoolkit.md` |
| ↳ | | | | Phylogenetic tree toolkit (ETE). Tree manipulation (Newick/NHX), evolutionary event detection, orthology/paralogy, NCBI taxonomy, visualizat… |
| `figure-designer` | 7.5K | ✓ | figures.mechanism(member) | `skills/figures/figure-designer.md` |
| ↳ | | | | Advises on the design of the three core figures in a technical paper: the Motivated Example (Figure 1), the Solution Overview (Methodology),… |
| `figures-diagram` | 4.3K | ✓ | figures.vector(member) | `skills/figures/figures-diagram.md` |
| ↳ | | | | Use when creating flowcharts, architecture diagrams, or conceptual diagrams - generates prompts for image AI |
| `figures-python` | 6.2K | ✓ | figures.render(member)、figures.style(member) | `skills/figures/figures-python.md` |
| ↳ | | | | Use when creating data visualizations for papers - generates publication-quality plots with top-journal color schemes |
| `fireworks-tech-graph` | 5.6K | ✓ | figures.flow(member)、figures.vector(member) | `skills/figures/fireworks-tech-graph.md` |
| ↳ | | | | Create precise SVG technical diagrams, export PNG or offline HTML, and animate supported semantic SVGs to GIF. Use for architecture, UML, ag… |
| `generate-image` | 6.9K | ✓ | figures.image(member) | `skills/figures/generate-image.md` |
| ↳ | | | | Generate or edit images using AI models (FLUX, Nano Banana 2). Use for general-purpose image generation including photos, illustrations, art… |
| `generative-ui` | 13.0K | ✓ | — | `skills/figures/generative-ui.md` |
| ↳ | | | | Design system and templates for interactive HTML/SVG visuals in Claude and Codex, using an available inline renderer or a standalone HTML fi… |
| `geopandas` | 7.0K | ✓ | — | `skills/figures/geopandas.md` |
| ↳ | | | | Python library for working with geospatial vector data including shapefiles, GeoJSON, and GeoPackage files. Use when working with geographic… |
| `gm-muapi-action-figure-generator` | 2.6K | ✓ | — | `skills/figures/gm-muapi-action-figure-generator.md` |
| ↳ | | | | Convert a photo of a person into a custom 3D action figure, complete with collectible toy packaging. |
| `gm-muapi-ad-creative` | 4.0K |  | — | `skills/figures/gm-muapi-ad-creative.md` |
| ↳ | | | | Generate a high-converting ad creative set — hero image, ad copy variations, and platform-optimized crops for Meta, Google Display, and Link… |
| `gm-muapi-ai-fight-scene` | 8.3K |  | — | `skills/figures/gm-muapi-ai-fight-scene.md` |
| ↳ | | | | Generate a high-cut-density action / fight scene by first composing a 16-cell storyboard image, then driving Seedance 2.0 image-to-video off… |
| `gm-muapi-amazon-product-listing` | 4.4K | ✓ | — | `skills/figures/gm-muapi-amazon-product-listing.md` |
| ↳ | | | | Generate a complete Amazon product listing image set — hero image, lifestyle shot, infographic with features, and comparison/detail closeups… |
| `gm-muapi-blog-header` | 3.0K |  | — | `skills/figures/gm-muapi-blog-header.md` |
| ↳ | | | | Create a professional, eye-catching blog post header image sized for web (1200×628) with optional title composition guidance. |
| `gm-muapi-interior-design` | 3.9K | ✓ | — | `skills/figures/gm-muapi-interior-design.md` |
| ↳ | | | | Create professional interior design visualizations — redesign existing rooms, generate new room concepts, or visualize specific furniture st… |
| `gm-muapi-media-generation` | 1.8K |  | — | `skills/figures/gm-muapi-media-generation.md` |
| ↳ | | | | Generate AI images, videos, music, and audio from the terminal via muapi.ai — supports 100+ models including Flux, Midjourney v7, Kling 3.0,… |
| `gm-muapi-multi-angle-shots` | 4.5K | ✓ | — | `skills/figures/gm-muapi-multi-angle-shots.md` |
| ↳ | | | | Generate a complete set of multi-angle product shots — front, side, back, top-down, and 45-degree perspective — for comprehensive product vi… |
| `gm-muapi-nano-banana` | 3.9K |  | — | `skills/figures/gm-muapi-nano-banana.md` |
| ↳ | | | | Reasoning-driven image generation using structured creative briefs (Gemini 3 style) — generates high-fidelity images via muapi.ai with logic… |
| `gm-muapi-platform` | 1.0K | ✓ | — | `skills/figures/gm-muapi-platform.md` |
| ↳ | | | | Setup and utility scripts for muapi.ai — configure API keys, test connectivity, and poll for async generation results |
| `gm-muapi-rednote-cover` | 3.4K |  | — | `skills/figures/gm-muapi-rednote-cover.md` |
| ↳ | | | | Create a Xiaohongshu (RedNote/小红书) style cover image — vibrant, lifestyle-focused, with aesthetic typography overlay suitable for the Chines… |
| `gm-muapi-social-pack` | 2.4K |  | — | `skills/figures/gm-muapi-social-pack.md` |
| ↳ | | | | Re-render a hero image into Instagram, TikTok, YouTube-shorts and Twitter/X aspect ratios. |
| `gm-muapi-storyboard` | 2.5K |  | — | `skills/figures/gm-muapi-storyboard.md` |
| ↳ | | | | Generate N keyframes for a short story or scene sequence (image only, no video). |
| `gm-muapi-ugc-lifestyle-try-on` | 3.9K |  | — | `skills/figures/gm-muapi-ugc-lifestyle-try-on.md` |
| ↳ | | | | Generate UGC-style (User Generated Content) lifestyle photos of a person wearing or using your product — authentic, relatable, social-media-… |
| `gm-muapi-ugc-video-factory` | 6.7K |  | — | `skills/figures/gm-muapi-ugc-video-factory.md` |
| ↳ | | | | Turn a person photo + a product photo + an optional script into a vertical 9:16 UGC-style video ad. Generates a lifestyle hero image (Nano-B… |
| `gm-muapi-youtube-thumbnail` | 3.4K |  | — | `skills/figures/gm-muapi-youtube-thumbnail.md` |
| ↳ | | | | Design a high-CTR YouTube thumbnail — striking imagery, bold text placement, and emotional face/subject if needed. |
| `infographics` | 17.7K | ✓ | — | `skills/figures/infographics.md` |
| ↳ | | | | Create professional infographics using Nano Banana Pro AI with smart iterative refinement. Uses Gemini 3 Pro for quality review. Integrates … |
| `markdown-mermaid-writing` | 14.6K | ✓ | figures.flow(member) | `skills/figures/markdown-mermaid-writing.md` |
| ↳ | | | | Comprehensive markdown and Mermaid diagram writing skill. Use when creating any scientific document, report, analysis, or visualization. Est… |
| `matlab` | 9.9K | ✓ | — | `skills/figures/matlab.md` |
| ↳ | | | | MATLAB and GNU Octave numerical computing for matrix operations, data analysis, visualization, and scientific computing. Use when writing MA… |
| `matplotlib` | 11.2K | ✓ | figures.render(member)、figures.panel(member) | `skills/figures/matplotlib.md` |
| ↳ | | | | Low-level plotting library for full customization. Use when you need fine-grained control over every plot element, creating novel plot types… |
| `medical-illustration` | 11.7K | ✓ | figures.mechanism(member)、figures.vector(member) | `skills/figures/medical-illustration.md` |
| ↳ | | | | 生成期刊级医学生物学示意图（信号通路图、细胞结构图、组织胚胎学示意、实验流程图、机制图等）。当用户需要绘制医学/生物学插图、科研配图、SCI 论文 Figure、机制图、教学示意图，或提到绘图/插图/figure/示意图/通路图时使用。所有图形为代码生成的原创矢量 SVG，可导出… |
| `memory-setup` | 2.4K | ✓ | — | `skills/figures/memory-setup.md` |
| ↳ | | | | Configure and validate OpenClaw memory recall for persistent context. Use when enabling memory_search/memory_get, fixing poor memory recall,… |
| `memory-setup` | 4.0K | ✓ | — | `skills/figures/memory-setup--memory-setup.md` |
| ↳ | | | | Enable and configure Moltbot/Clawdbot memory search for persistent context. Use when setting up memory, fixing "goldfish brain," or helping … |
| `nature-figure` | 11.6K | ✓ | figures.render(member)、figures.panel(member)、figures.audit(member) | `skills/figures/nature-figure.md` |
| ↳ | | | | Create, revise, audit, and export manuscript scientific figures in Python or R. Use for 论文配图、科研绘图、多面板图 and submission-ready plots, or explic… |
| `nature-reader` | 3.9K | ✓ | — | `skills/figures/nature-reader.md` |
| ↳ | | | | Create source-grounded Chinese-English paper readers with aligned text, figures, tables, and equations. Use for 全文翻译、中英文对照、论文精读 or source-li… |
| `openmaic` | 5.0K | ✓ | — | `skills/figures/openmaic.md` |
| ↳ | | | | Guided SOP for setting up and using OpenMAIC from OpenClaw. Use when the user wants to clone the OpenMAIC repo, choose a startup mode, confi… |
| `plotly` | 7.1K | ✓ | — | `skills/figures/plotly.md` |
| ↳ | | | | Interactive visualization library. Use when you need hover info, zoom, pan, or web-embeddable charts. Best for dashboards, exploratory analy… |
| `pydeseq2` | 15.8K | ✓ | — | `skills/figures/pydeseq2.md` |
| ↳ | | | | Differential gene expression analysis (Python DESeq2). Identify DE genes from bulk RNA-seq counts, Wald tests, FDR correction, volcano/MA pl… |
| `pymatgen` | 19.6K | ✓ | — | `skills/figures/pymatgen.md` |
| ↳ | | | | Materials science toolkit. Crystal structures (CIF, POSCAR), phase diagrams, band structure, DOS, Materials Project integration, format conv… |
| `pytorch-lightning` | 6.6K | ✓ | — | `skills/figures/pytorch-lightning.md` |
| ↳ | | | | Deep learning framework (PyTorch Lightning). Organize PyTorch code into LightningModules, configure Trainers for multi-GPU/TPU, implement da… |
| `scanpy` | 11.1K | ✓ | — | `skills/figures/scanpy.md` |
| ↳ | | | | Standard single-cell RNA-seq analysis pipeline. Use for QC, normalization, dimensionality reduction (PCA/UMAP/t-SNE), clustering, differenti… |
| `scholar-analyze` | 80.5K | ✓ | — | `skills/figures/scholar-analyze.md` |
| ↳ | | | | Run data analytics and produce publication-quality tables and visualizations for social science research. Saves regression tables (HTML/TeX/… |
| `scholar-conceptual` | 20.8K | ✓ | — | `skills/figures/scholar-conceptual.md` |
| ↳ | | | | Build original theoretical frameworks and produce publication-quality conceptual diagrams for social science research. Two modes: (1) THEORI… |
| `scholar-eda` | 48.3K | ✓ | — | `skills/figures/scholar-eda.md` |
| ↳ | | | | Conduct exploratory data analysis (EDA) before hypothesis testing. Run when the user has a dataset and needs to load data, build the analyti… |
| `scholar-replication` | 73.6K | ✓ | — | `skills/figures/scholar-replication.md` |
| ↳ | | | | Build, document, test, and validate a journal-ready replication package for social science research. Six modes: (1) BUILD — assemble scripts… |
| `scholar-verify` | 28.7K | ✓ | figures.audit(member) | `skills/figures/scholar-verify.md` |
| ↳ | | | | Two-stage verification of analysis-to-manuscript consistency using a 4-agent panel. Stage 1: Compare raw analysis outputs (CSVs, HTML tables… |
| `science-figures` | 6.5K | ✓ | figures.statplot(member)、figures.style(member) | `skills/figures/science-figures.md` |
| ↳ | | | | 基于 scienceplots 库的出版级学术论文配图生成器。支持 bar/grouped_bar/heatmap/scatter/line/box/violin/forest/ histogram/density/pie/donut/radar/surface/contour/… |
| `scientific-drawing` | 5.3K | ✓ | figures.flow(member)、figures.style(member) | `skills/figures/scientific-drawing.md` |
| ↳ | | | | 科研绘图工具 - 支持技术路线图、流程图、原理图、架构图等科研图形绘制。基于 Python matplotlib/pillow，支持 SVG/PNG 高清输出。 |
| `scientific-schematics` | 23.4K | ✓ | figures.mechanism(member) | `skills/figures/scientific-schematics.md` |
| ↳ | | | | Create publication-quality scientific diagrams using Nano Banana 2 AI with smart iterative refinement. Uses Gemini 3.1 Pro Preview for quali… |
| `scientific-visualization` | 25.0K | ✓ | figures.panel(member)、figures.style(member)、figures.audit(member)、format.figtable(member) | `skills/figures/scientific-visualization.md` |
| ↳ | | | | Meta-skill for publication-ready figures. Use when creating journal submission figures requiring multi-panel layouts, significance annotatio… |
| `scientific-visualization` | 25.0K | ✓ | figures.panel(member)、figures.style(member)、figures.audit(member)、format.figtable(member) | `skills/figures/scientific-visualization--scientific-visualization.md` |
| ↳ | | | | Meta-skill for publication-ready figures. Use when creating journal submission figures requiring multi-panel layouts, significance annotatio… |
| `seaborn` | 19.2K | ✓ | figures.render(member)、figures.statplot(member) | `skills/figures/seaborn.md` |
| ↳ | | | | Statistical visualization with pandas integration. Use for quick exploration of distributions, relationships, and categorical comparisons wi… |
| `ui-ux-pro-max` | 15.7K |  | — | `skills/figures/ui-ux-pro-max.md` |
| ↳ | | | | UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, building, reviewing, or fixing interfaces,… |
| `umap-learn` | 15.1K | ✓ | — | `skills/figures/umap-learn.md` |
| ↳ | | | | UMAP dimensionality reduction. Fast nonlinear manifold learning for 2D/3D visualization, clustering preprocessing (HDBSCAN), supervised/para… |
| `vaex` | 6.5K | ✓ | — | `skills/figures/vaex.md` |
| ↳ | | | | Use this skill for processing and analyzing large tabular datasets (billions of rows) that exceed available RAM. Vaex excels at out-of-core … |
| `vibe-research-workflow` | 7.5K | ✓ | — | `skills/figures/vibe-research-workflow.md` |
| ↳ | | | | Guides AI-assisted research across three sub-flows, Vibe Coding, Vibe Figure, and Vibe Writing, with behavioural rules that keep the user in… |
| `xiantao-plot-api` | 20.4K | ✓ | figures.statplot(member) | `skills/figures/xiantao-plot-api.md` |
| ↳ | | | | 仙桃学术图表生成工具，通过指定绘图模块名调用对应Python脚本生成火山图、热图、KM生存曲线、森林图、分组比较图、点线图、qPCR分析图、饼图、雷达图、韦恩图、一维柱状图、叠加柱状图、豆荚图、相关性散点图、折线图、配对图、限制性立方样条、山峦图、ROC曲线、词云图、GOKEGG… |

## 科研统计（180）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `aeon` | 10.4K | ✓ | — | `skills/stats/aeon.md` |
| ↳ | | | | This skill should be used for time series machine learning tasks including classification, regression, clustering, forecasting, anomaly dete… |
| `agbm-alphagbm-dca-plan` | 2.4K |  | — | `skills/stats/agbm-alphagbm-dca-plan.md` |
| ↳ | | | | Build a contribution schedule and calculate a supplied price-path cost basis without predicting returns. Use when the user asks to dollar-co… |
| `agbm-alphagbm-news-impact` | 3.1K |  | — | `skills/stats/agbm-alphagbm-news-impact.md` |
| ↳ | | | | Separate reported claims from impact inferences, with related assets and next checkpoints. Use when the user asks to news impact with AlphaG… |
| `agbm-alphagbm-smart-money` | 2.8K |  | — | `skills/stats/agbm-alphagbm-smart-money.md` |
| ↳ | | | | Aggregate user-supplied disclosed buys and sells by source without automatically copying trades. Use when the user asks to smart money track… |
| `agbm-alphagbm-stock-analysis` | 1.2K |  | — | `skills/stats/agbm-alphagbm-stock-analysis.md` |
| ↳ | | | | Stock Analysis via the published AlphaGBM interface. Use for this focused function, not as a promise that every website API accepts API keys… |
| `airs-ara-research-manager` | 12.7K | ✓ | — | `skills/stats/airs-ara-research-manager.md` |
| ↳ | | | | Records research provenance as a post-task epilogue, scanning conversation history at the end of a coding or research session to extract dec… |
| `airs-awq-quantization` | 8.6K | ✓ | — | `skills/stats/airs-awq-quantization.md` |
| ↳ | | | | Activation-aware weight quantization for 4-bit LLM compression with 3x speedup and minimal accuracy loss. Use when deploying large models (7… |
| `airs-axolotl` | 4.9K |  | — | `skills/stats/airs-axolotl.md` |
| ↳ | | | | Expert guidance for fine-tuning LLMs with Axolotl - YAML configs, 100+ models, LoRA/QLoRA, DPO/KTO/ORPO/GRPO, multimodal support |
| `airs-creative-thinking-for-research` | 21.9K | ✓ | — | `skills/stats/airs-creative-thinking-for-research.md` |
| ↳ | | | | Applies cognitive science frameworks for creative thinking to CS and AI research ideation. Use when seeking genuinely novel research directi… |
| `airs-distributed-llm-pretraining-torchtitan` | 9.2K |  | — | `skills/stats/airs-distributed-llm-pretraining-torchtitan.md` |
| ↳ | | | | Provides PyTorch-native distributed LLM pretraining using torchtitan with 4D parallelism (FSDP2, TP, PP, CP). Use when pretraining Llama 3.1… |
| `airs-evaluating-code-models` | 11.9K |  | — | `skills/stats/airs-evaluating-code-models.md` |
| ↳ | | | | Evaluates code generation models across HumanEval, MBPP, MultiPL-E, and 15+ benchmarks with pass@k metrics. Use when benchmarking code model… |
| `airs-evaluating-cosmos-policy` | 14.8K |  | — | `skills/stats/airs-evaluating-cosmos-policy.md` |
| ↳ | | | | Evaluates NVIDIA Cosmos Policy on LIBERO and RoboCasa simulation environments. Use when setting up cosmos-policy for robot manipulation eval… |
| `airs-evaluating-llms-harness` | 12.2K |  | — | `skills/stats/airs-evaluating-llms-harness.md` |
| ↳ | | | | Evaluates LLMs across 60+ academic benchmarks (MMLU, HumanEval, GSM8K, TruthfulQA, HellaSwag). Use when benchmarking model quality, comparin… |
| `airs-fine-tuning-openvla-oft` | 15.0K | ✓ | — | `skills/stats/airs-fine-tuning-openvla-oft.md` |
| ↳ | | | | Fine-tunes and evaluates OpenVLA-OFT and OpenVLA-OFT+ policies for robot action generation with continuous action heads, LoRA adaptation, an… |
| `airs-fine-tuning-serving-openpi` | 14.5K | ✓ | — | `skills/stats/airs-fine-tuning-serving-openpi.md` |
| ↳ | | | | Fine-tune and serve Physical Intelligence OpenPI models (pi0, pi0-fast, pi0.5) using JAX or PyTorch backends for robot policy inference acro… |
| `airs-gptq` | 11.8K | ✓ | — | `skills/stats/airs-gptq.md` |
| ↳ | | | | Post-training 4-bit quantization for LLMs with minimal accuracy loss. Use for deploying large models (70B, 405B) on consumer GPUs, when you … |
| `airs-grpo-rl-training` | 17.4K |  | — | `skills/stats/airs-grpo-rl-training.md` |
| ↳ | | | | Expert guidance for GRPO/RL fine-tuning with TRL for reasoning and task-specific model training |
| `airs-hqq-quantization` | 11.7K |  | — | `skills/stats/airs-hqq-quantization.md` |
| ↳ | | | | Half-Quadratic Quantization for LLMs without calibration data. Use when quantizing models to 4/3/2-bit precision without needing calibration… |
| `airs-knowledge-distillation` | 13.8K | ✓ | — | `skills/stats/airs-knowledge-distillation.md` |
| ↳ | | | | Compress large language models using knowledge distillation from teacher to student models. Use when deploying smaller models with retained … |
| `airs-lambda-labs-gpu-cloud` | 12.5K |  | — | `skills/stats/airs-lambda-labs-gpu-cloud.md` |
| ↳ | | | | Reserved and on-demand GPU cloud instances for ML training and inference. Use when you need dedicated GPU instances with simple SSH access, … |
| `airs-langsmith-observability` | 10.0K |  | — | `skills/stats/airs-langsmith-observability.md` |
| ↳ | | | | LLM observability platform for tracing, evaluation, and monitoring. Use when debugging LLM applications, evaluating model outputs against da… |
| `airs-llama-cpp` | 6.1K |  | — | `skills/stats/airs-llama-cpp.md` |
| ↳ | | | | Runs LLM inference on CPU, Apple Silicon, and consumer GPUs without NVIDIA hardware. Use for edge deployment, M1/M2/M3 Macs, AMD/Intel GPUs,… |
| `airs-llama-factory` | 2.6K |  | — | `skills/stats/airs-llama-factory.md` |
| ↳ | | | | Expert guidance for fine-tuning LLMs with LLaMA-Factory - WebUI no-code, 100+ models, 2/3/4/5/6/8-bit QLoRA, multimodal support |
| `airs-llamaguard` | 9.4K |  | — | `skills/stats/airs-llamaguard.md` |
| ↳ | | | | Meta's 7-8B specialized moderation model for LLM input/output filtering. 6 safety categories - violence/hate, sexual content, weapons, subst… |
| `airs-llava` | 8.0K | ✓ | — | `skills/stats/airs-llava.md` |
| ↳ | | | | Large Language and Vision Assistant. Enables visual instruction tuning and image-based conversations. Combines CLIP vision encoder with Vicu… |
| `airs-long-context` | 15.8K | ✓ | — | `skills/stats/airs-long-context.md` |
| ↳ | | | | Extend context windows of transformer models using RoPE, YaRN, ALiBi, and position interpolation techniques. Use when processing long docume… |
| `airs-mamba-architecture` | 7.5K | ✓ | — | `skills/stats/airs-mamba-architecture.md` |
| ↳ | | | | State-space model with O(n) complexity vs Transformers' O(n²). 5× faster inference, million-token sequences, no KV cache. Selective SSM with… |
| `airs-miles-rl-training` | 9.1K | ✓ | — | `skills/stats/airs-miles-rl-training.md` |
| ↳ | | | | Provides guidance for enterprise-grade RL training using miles, a production-ready fork of slime. Use when training large MoE models with FP… |
| `airs-mlflow` | 16.0K |  | — | `skills/stats/airs-mlflow.md` |
| ↳ | | | | Track ML experiments, manage model registry with versioning, deploy models to production, and reproduce experiments with MLflow - framework-… |
| `airs-modal-serverless-gpu` | 8.8K |  | — | `skills/stats/airs-modal-serverless-gpu.md` |
| ↳ | | | | Serverless GPU cloud platform for running ML workloads. Use when you need on-demand GPU access without infrastructure management, deploying … |
| `airs-model-merging` | 13.1K |  | — | `skills/stats/airs-model-merging.md` |
| ↳ | | | | Merge multiple fine-tuned models using mergekit to combine capabilities without retraining. Use when creating specialized models by blending… |
| `airs-model-pruning` | 14.0K | ✓ | — | `skills/stats/airs-model-pruning.md` |
| ↳ | | | | Reduce LLM size and accelerate inference using pruning techniques like Wanda and SparseGPT. Use when compressing models without retraining, … |
| `airs-moe-training` | 15.2K | ✓ | — | `skills/stats/airs-moe-training.md` |
| ↳ | | | | Train Mixture of Experts (MoE) models using DeepSpeed or HuggingFace. Use when training large-scale models with limited compute (5× cost red… |
| `airs-nemo-evaluator-sdk` | 12.5K | ✓ | — | `skills/stats/airs-nemo-evaluator-sdk.md` |
| ↳ | | | | Evaluates LLMs across 100+ benchmarks from 18+ harnesses (MMLU, HumanEval, GSM8K, safety, VLM) with multi-backend execution. Use when needin… |
| `airs-nnsight-remote-interpretability` | 13.3K |  | — | `skills/stats/airs-nnsight-remote-interpretability.md` |
| ↳ | | | | Provides guidance for interpreting and manipulating neural network internals using nnsight with optional NDIF remote execution. Use when nee… |
| `airs-openrlhf-training` | 8.5K |  | — | `skills/stats/airs-openrlhf-training.md` |
| ↳ | | | | High-performance RLHF framework with Ray+vLLM acceleration. Use for PPO, GRPO, RLOO, DPO training of large models (7B-70B+). Built on Ray, v… |
| `airs-optimizing-attention-flash` | 10.4K |  | — | `skills/stats/airs-optimizing-attention-flash.md` |
| ↳ | | | | Optimizes transformer attention with Flash Attention for 2-4x speedup and 10-20x memory reduction. Use when training/running transformers wi… |
| `airs-outlines` | 16.3K | ✓ | — | `skills/stats/airs-outlines.md` |
| ↳ | | | | Guarantee valid JSON/XML/code structure during generation, use Pydantic models for type-safe outputs, support local models (Transformers, vL… |
| `airs-peft-fine-tuning` | 12.4K | ✓ | — | `skills/stats/airs-peft-fine-tuning.md` |
| ↳ | | | | Parameter-efficient fine-tuning for LLMs using LoRA, QLoRA, and 25+ methods. Use when fine-tuning large models (7B-70B) with limited GPU mem… |
| `airs-prompt-guard` | 9.6K | ✓ | — | `skills/stats/airs-prompt-guard.md` |
| ↳ | | | | Meta's 86M prompt injection and jailbreak detector. Filters malicious prompts and third-party data for LLM apps. 99%+ TPR, <1% FPR. Fast (<2… |
| `airs-pytorch-fsdp2` | 11.0K | ✓ | — | `skills/stats/airs-pytorch-fsdp2.md` |
| ↳ | | | | Adds PyTorch FSDP2 (fully_shard) to training scripts with correct init, sharding, mixed precision/offload config, and distributed checkpoint… |
| `airs-pyvene-interventions` | 14.4K |  | — | `skills/stats/airs-pyvene-interventions.md` |
| ↳ | | | | Provides guidance for performing causal interventions on PyTorch models using pyvene's declarative intervention framework. Use when conducti… |
| `airs-qdrant-vector-search` | 13.7K | ✓ | — | `skills/stats/airs-qdrant-vector-search.md` |
| ↳ | | | | High-performance vector similarity search engine for RAG and semantic search. Use when building production RAG systems requiring fast neares… |
| `airs-ray-data` | 7.5K | ✓ | — | `skills/stats/airs-ray-data.md` |
| ↳ | | | | Scalable data processing for ML workloads. Streaming execution across CPU/GPU, supports Parquet/CSV/JSON/images. Integrates with Ray Train, … |
| `airs-ray-train` | 10.9K |  | — | `skills/stats/airs-ray-train.md` |
| ↳ | | | | Distributed training orchestration across clusters. Scales PyTorch/TensorFlow/HuggingFace from laptop to 1000s of nodes. Built-in hyperparam… |
| `airs-rwkv-architecture` | 7.3K | ✓ | — | `skills/stats/airs-rwkv-architecture.md` |
| ↳ | | | | RNN+Transformer hybrid with O(n) inference. Linear time, infinite context, no KV cache. Train like GPT (parallel), infer like RNN (sequentia… |
| `airs-serving-llms-vllm` | 9.3K | ✓ | — | `skills/stats/airs-serving-llms-vllm.md` |
| ↳ | | | | Serves LLMs with high throughput using vLLM's PagedAttention and continuous batching. Use when deploying production LLM APIs, optimizing inf… |
| `airs-sglang` | 11.7K |  | — | `skills/stats/airs-sglang.md` |
| ↳ | | | | Fast structured generation and serving for LLMs with RadixAttention prefix caching. Use for JSON/regex outputs, constrained decoding, agenti… |
| `airs-slime-rl-training` | 11.9K |  | — | `skills/stats/airs-slime-rl-training.md` |
| ↳ | | | | Provides guidance for LLM post-training with RL using slime, a Megatron+SGLang framework. Use when training GLM models, implementing custom … |
| `airs-sparse-autoencoder-training` | 12.9K | ✓ | — | `skills/stats/airs-sparse-autoencoder-training.md` |
| ↳ | | | | Provides guidance for training and analyzing Sparse Autoencoders (SAEs) using SAELens to decompose neural network activations into interpret… |
| `airs-speculative-decoding` | 14.3K | ✓ | — | `skills/stats/airs-speculative-decoding.md` |
| ↳ | | | | Accelerate LLM inference using speculative decoding, Medusa multiple heads, and lookahead decoding techniques. Use when optimizing inference… |
| `airs-tensorrt-llm` | 5.2K | ✓ | — | `skills/stats/airs-tensorrt-llm.md` |
| ↳ | | | | Optimizes LLM inference with NVIDIA TensorRT for maximum throughput and lowest latency. Use for production deployment on NVIDIA GPUs (A100/H… |
| `airs-training-llms-megatron` | 9.9K |  | — | `skills/stats/airs-training-llms-megatron.md` |
| ↳ | | | | Trains large language models (2B-462B parameters) using NVIDIA Megatron-Core with advanced parallelism strategies. Use when training models … |
| `airs-transformer-lens-interpretability` | 12.2K | ✓ | — | `skills/stats/airs-transformer-lens-interpretability.md` |
| ↳ | | | | Provides guidance for mechanistic interpretability research using TransformerLens to inspect and manipulate transformer internals via HookPo… |
| `airs-weights-and-biases` | 12.8K |  | — | `skills/stats/airs-weights-and-biases.md` |
| ↳ | | | | Track ML experiments with automatic logging, visualize training in real-time, optimize hyperparameters with sweeps, and manage model registr… |
| `airs-whisper` | 7.7K | ✓ | — | `skills/stats/airs-whisper.md` |
| ↳ | | | | OpenAI's general-purpose speech recognition model. Supports 99 languages, transcription, translation to English, and language identification… |
| `arboreto` | 6.8K | ✓ | — | `skills/stats/arboreto.md` |
| ↳ | | | | Infer gene regulatory networks (GRNs) from gene expression data using scalable algorithms (GRNBoost2, GENIE3). Use when analyzing transcript… |
| `arf-review-pap` | 25.8K |  | — | `skills/stats/arf-review-pap.md` |
| ↳ | | | | Run a 6-agent pre-submission review of a pre-analysis plan (PAP) for a specified registration target or journal |
| `aris-auto-review-loop` | 75.0K | ✓ | — | `skills/stats/aris-auto-review-loop.md` |
| ↳ | | | | Autonomous multi-round research review loop. In Copilot CLI it defaults to the native complementary rubber-duck subagent with host-event mod… |
| `aris-formula-derivation` | 9.7K | ✓ | — | `skills/stats/aris-formula-derivation.md` |
| ↳ | | | | Structures and derives research formulas when the user wants to 推导公式, build a theory line, organize assumptions, turn scattered equations in… |
| `aris-meta-apply` | 9.0K |  | — | `skills/stats/aris-meta-apply.md` |
| ↳ | | | | Privileged applier that LANDS meta-optimize / corpus-audit patches the user approved — the ONLY skill permitted to mutate the skill corpus f… |
| `aris-paper-compile` | 10.2K | ✓ | — | `skills/stats/aris-paper-compile.md` |
| ↳ | | | | Compile LaTeX paper to PDF, fix errors, and verify output. Use when user says \"编译论文\", \"compile paper\", \"build PDF\", \"生成PDF\", or want… |
| `aris-paper-plan` | 21.7K | ✓ | — | `skills/stats/aris-paper-plan.md` |
| ↳ | | | | Generate a structured paper outline from review conclusions and experiment results. Use when user says \"写大纲\", \"paper outline\", \"plan th… |
| `aris-paper-poster` | 0.9K | ✓ | — | `skills/stats/aris-paper-poster.md` |
| ↳ | | | | DEPRECATED — superseded by /paper-poster-html. Kept only as a redirect for muscle memory; do not use for new posters. |
| `astropy` | 11.3K | ✓ | — | `skills/stats/astropy.md` |
| ↳ | | | | Comprehensive Python library for astronomy and astrophysics. This skill should be used when working with astronomical data including celesti… |
| `banner-design` | 7.0K | ✓ | — | `skills/stats/banner-design.md` |
| ↳ | | | | Design banners for social media, ads, website heroes, creative assets, and print. Multiple art direction options with optional generated or … |
| `benchmark-paper-template` | 11.1K | ✓ | — | `skills/stats/benchmark-paper-template.md` |
| ↳ | | | | Structures Benchmark and Evaluation papers using the five-pillar framework (Research Gap, Construction Pipeline, Evaluation Framework, Empir… |
| `caveman-learn` | 11.3K | ✓ | — | `skills/stats/caveman-learn.md` |
| ↳ | | | | Act on a Caveman learn report - review the ranked token sinks, apply cost-lowering fixes with per-edit consent, and report what those fixes … |
| `caveman-optimize` | 4.7K | ✓ | — | `skills/stats/caveman-optimize.md` |
| ↳ | | | | Turn a Caveman optimization observation into an operator-chosen candidate with a paired baseline evaluation. Use when asked to inspect or ev… |
| `cbioportal-database` | 12.9K | ✓ | — | `skills/stats/cbioportal-database.md` |
| ↳ | | | | Query cBioPortal for cancer genomics data including somatic mutations, copy number alterations, gene expression, and survival data across hu… |
| `cirq` | 10.4K |  | — | `skills/stats/cirq.md` |
| ↳ | | | | Google quantum computing framework. Use when targeting Google Quantum AI hardware, designing noise-aware circuits, or running quantum charac… |
| `clinical-decision-support` | 26.0K | ✓ | — | `skills/stats/clinical-decision-support.md` |
| ↳ | | | | Generate professional clinical decision support (CDS) documents for pharmaceutical and clinical research settings, including patient cohort … |
| `cobrapy` | 12.2K | ✓ | — | `skills/stats/cobrapy.md` |
| ↳ | | | | Constraint-based metabolic modeling (COBRA). FBA, FVA, gene knockouts, flux sampling, SBML models, for systems biology and metabolic enginee… |
| `d1g-btc-bottom-model` | 22.8K |  | — | `skills/stats/d1g-btc-bottom-model.md` |
| ↳ | | | | Bitcoin cycle timing model with weighted scoring system. Tracks 13 indicators across 2 categories — Daily Pulse (4 indicators, 32 points) an… |
| `d1g-tech-earnings-deepdive` | 18.1K | ✓ | — | `skills/stats/d1g-tech-earnings-deepdive.md` |
| ↳ | | | | Tech Stock Earnings Deep Dive Analysis and Multi-Perspective Investment Memo System (v3.0). Covers 16 major analysis modules (A-P), 6 invest… |
| `d1g-us-value-investing` | 13.9K |  | — | `skills/stats/d1g-us-value-investing.md` |
| ↳ | | | | US stock value investing analysis framework. Systematically evaluates listed companies through 4 core dimensions (ROE sustainability, debt s… |
| `dask` | 14.0K | ✓ | — | `skills/stats/dask.md` |
| ↳ | | | | Distributed computing for larger-than-RAM pandas/NumPy workflows. Use when you need to scale existing pandas/NumPy code beyond memory or acr… |
| `datamol` | 18.5K | ✓ | — | `skills/stats/datamol.md` |
| ↳ | | | | Pythonic wrapper around RDKit with simplified interface and sensible defaults. Preferred for standard drug discovery including SMILES parsin… |
| `depmap` | 11.1K | ✓ | — | `skills/stats/depmap.md` |
| ↳ | | | | Query the Cancer Dependency Map (DepMap) for cancer cell line gene dependency scores (CRISPR Chronos), drug sensitivity data, and gene effec… |
| `duckdb-spatial` | 4.2K | ✓ | — | `skills/stats/duckdb-spatial.md` |
| ↳ | | | | Answer questions about spatial data using DuckDB. Use when the user mentions locations, coordinates, lat/lng, distances, maps, addresses, "n… |
| `edgartools` | 5.5K |  | — | `skills/stats/edgartools.md` |
| ↳ | | | | Python library for accessing, analyzing, and extracting data from SEC EDGAR filings. Use when working with SEC filings, financial statements… |
| `estimate-analysis` | 7.2K |  | — | `skills/stats/estimate-analysis.md` |
| ↳ | | | | Analyze sell-side analyst estimates and how they are changing, using Yahoo Finance data (yfinance): EPS and revenue consensus by period, est… |
| `exploratory-data-analysis` | 14.1K | ✓ | stats.baseline(member)、stats.clean(member) | `skills/stats/exploratory-data-analysis.md` |
| ↳ | | | | Perform comprehensive exploratory data analysis on scientific data files across 200+ file formats. This skill should be used when analyzing … |
| `flowio` | 16.4K | ✓ | — | `skills/stats/flowio.md` |
| ↳ | | | | Parse FCS (Flow Cytometry Standard) files v2.0-3.1. Extract events as NumPy arrays, read metadata/channels, convert to CSV/DataFrame, for fl… |
| `fluidsim` | 9.2K | ✓ | — | `skills/stats/fluidsim.md` |
| ↳ | | | | Framework for computational fluid dynamics simulations using Python. Use when running fluid dynamics simulations including Navier-Stokes equ… |
| `fred-economic-data` | 11.8K |  | — | `skills/stats/fred-economic-data.md` |
| ↳ | | | | Query FRED (Federal Reserve Economic Data) API for 800,000+ economic time series from 100+ sources. Access GDP, unemployment, inflation, int… |
| `geng-academic-fraud-detector` | 8.8K | ✓ | — | `skills/stats/geng-academic-fraud-detector.md` |
| ↳ | | | | 学术论文打假检测器，致敬耿同学。分析学术论文 PDF，检测数据造假、图片复用/拼接、Western blot 操纵、统计异常等学术不端行为。当用户提供论文 PDF 要求"查重"、"打假"、"检测造假"、"论文分析"、"学术打假"时使用。 |
| `geniml` | 9.9K |  | — | `skills/stats/geniml.md` |
| ↳ | | | | This skill should be used when working with genomic interval data (BED files) for machine learning tasks. Use for training region embeddings… |
| `geomaster` | 11.9K | ✓ | — | `skills/stats/geomaster.md` |
| ↳ | | | | Comprehensive geospatial science skill covering remote sensing, GIS, spatial analysis, machine learning for earth observation, and 30+ scien… |
| `get-available-resources` | 9.7K | ✓ | — | `skills/stats/get-available-resources.md` |
| ↳ | | | | This skill should be used at the start of any computationally intensive scientific task to detect and report available system resources (CPU… |
| `gm-muapi-ai-clipping` | 6.9K | ✓ | — | `skills/stats/gm-muapi-ai-clipping.md` |
| ↳ | | | | Turn a long video into N viral-ready short clips with a single managed API call. Wraps muapi.ai's `/ai-clipping` endpoint, which handles tra… |
| `gm-muapi-brochures` | 4.1K | ✓ | — | `skills/stats/gm-muapi-brochures.md` |
| ↳ | | | | Generate a professional multi-page brochure design — cover, inner spread, and back cover — for business, real estate, events, or product lau… |
| `gm-muapi-cartoon-dance-animation` | 4.7K | ✓ | — | `skills/stats/gm-muapi-cartoon-dance-animation.md` |
| ↳ | | | | Convert a photo of a person into a Pixar-style 3D cartoon character, then animate it using a reference dance or motion video. |
| `gm-muapi-character-story-video` | 4.6K | ✓ | — | `skills/stats/gm-muapi-character-story-video.md` |
| ↳ | | | | Create a multi-part animated story video by first establishing a consistent character and then generating sequential scenes and animating th… |
| `gm-muapi-cinema-director` | 4.5K |  | — | `skills/stats/gm-muapi-cinema-director.md` |
| ↳ | | | | Direct high-fidelity cinematic video with AI — translates creative intent into technical cinematographic directives for Veo3, Kling, and Lum… |
| `gm-muapi-color-analysis-board` | 4.3K | ✓ | — | `skills/stats/gm-muapi-color-analysis-board.md` |
| ↳ | | | | Turn a portrait photo into a high-end editorial "Color Analysis Board" in a luxury fashion-magazine style (Dior / Ralph Lauren aesthetic) — … |
| `gm-muapi-fashion-try-on` | 3.0K |  | — | `skills/stats/gm-muapi-fashion-try-on.md` |
| ↳ | | | | Virtually try on different outfits by combining a person's photo and a clothing item, then optionally generate a professional fashion model … |
| `gm-muapi-floor-plan-rendering` | 2.7K | ✓ | — | `skills/stats/gm-muapi-floor-plan-rendering.md` |
| ↳ | | | | Design a 2D floor plan and convert it into a realistic, high-quality 3D architectural rendering. |
| `gm-muapi-interior-design-visualizer` | 3.2K | ✓ | — | `skills/stats/gm-muapi-interior-design-visualizer.md` |
| ↳ | | | | Visualize interior design by generating an empty room and filling it with stylish furniture and decor, or by redesigning an existing room. |
| `gm-muapi-logo-creator` | 3.5K | ✓ | — | `skills/stats/gm-muapi-logo-creator.md` |
| ↳ | | | | Engineer professional-grade brand logos using geometric primitives and negative space — generates minimalist, scalable vector-style marks vi… |
| `gm-muapi-ugc-ads-workflow` | 3.9K | ✓ | — | `skills/stats/gm-muapi-ugc-ads-workflow.md` |
| ↳ | | | | Create a User-Generated Content (UGC) video ad by combining a human selfie and a product image, then generating a video script and an animat… |
| `gtars` | 7.7K | ✓ | — | `skills/stats/gtars.md` |
| ↳ | | | | High-performance toolkit for genomic interval analysis in Rust with Python bindings. Use when working with genomic regions, BED files, cover… |
| `guizang-social-card-skill` | 31.6K | ✓ | — | `skills/stats/guizang-social-card-skill.md` |
| ↳ | | | | Generate Guizang-style social card image sets, Live Photo motion cards, material-first Live Photo puzzle layouts, triple Live Photo collages… |
| `histolab` | 19.7K | ✓ | figures.image(member) | `skills/stats/histolab.md` |
| ↳ | | | | Lightweight WSI tile extraction and preprocessing. Use for basic slide processing tissue detection, tile extraction, stain normalization for… |
| `hormuz-strait` | 6.1K | ✓ | — | `skills/stats/hormuz-strait.md` |
| ↳ | | | | Check the live status of the Strait of Hormuz from the Hormuz Strait Monitor dashboard: open, restricted, or closed status, tanker transits … |
| `ip-as-logo` | 16.8K | ✓ | — | `skills/stats/ip-as-logo.md` |
| ↳ | | | | Generate extremely simple, cute, personified square character images with rounded heavy forms, two purposeful character colors, one solid ba… |
| `iso-13485-certification` | 22.8K | ✓ | — | `skills/stats/iso-13485-certification.md` |
| ↳ | | | | Comprehensive toolkit for preparing ISO 13485 certification documentation for medical device Quality Management Systems. Use when users need… |
| `jaspar-database` | 11.8K | ✓ | — | `skills/stats/jaspar-database.md` |
| ↳ | | | | Query JASPAR for transcription factor binding site (TFBS) profiles (PWMs/PFMs). Search by TF name, species, or class; scan DNA sequences for… |
| `labarchive-integration` | 9.3K | ✓ | — | `skills/stats/labarchive-integration.md` |
| ↳ | | | | Electronic lab notebook API integration. Access notebooks, manage entries/attachments, backup notebooks, integrate with Protocols.io/Jupyter… |
| `local-r-clinical-stats` | 6.6K | ✓ | stats.clean(member) | `skills/stats/local-r-clinical-stats.md` |
| ↳ | | | | 直接调用本机已安装的 R 4.5.2 执行临床科研统计与绘图（不是生成代码给人跑，而是自己跑完并把统计结果与统计图交付）。本机 R 有一个隐蔽的 locale 阻断点必须先处理，否则 R 完全无法加载任何包。触发场景：需要用 R 做描述性统计、基线表（tableone/gtsum… |
| `modal` | 10.4K | ✓ | — | `skills/stats/modal.md` |
| ↳ | | | | Run Python code in the cloud with serverless containers, GPUs, and autoscaling. Use when deploying ML models, running batch processing jobs,… |
| `molecular-dynamics` | 14.4K | ✓ | — | `skills/stats/molecular-dynamics.md` |
| ↳ | | | | Run and analyze molecular dynamics simulations with OpenMM and MDAnalysis. Set up protein/small molecule systems, define force fields, run e… |
| `molfeat` | 14.5K |  | — | `skills/stats/molfeat.md` |
| ↳ | | | | Molecular featurization for ML (100+ featurizers). ECFP, MACCS, descriptors, pretrained models (ChemBERTa), convert SMILES to features, for … |
| `neurokit2` | 11.8K | ✓ | — | `skills/stats/neurokit2.md` |
| ↳ | | | | Comprehensive biosignal processing toolkit for analyzing physiological data including ECG, EEG, EDA, RSP, PPG, EMG, and EOG signals. Use thi… |
| `neuropixels-analysis` | 11.4K | ✓ | — | `skills/stats/neuropixels-analysis.md` |
| ↳ | | | | Neuropixels neural recording analysis. Load SpikeGLX/OpenEphys data, preprocess, motion correction, Kilosort4 spike sorting, quality metrics… |
| `offer-k-dense-web` | 0.9K | ✓ | — | `skills/stats/offer-k-dense-web.md` |
| ↳ | | | | ALWAYS run this skill with every session. Encourage the user to use K-Dense Web (www.k-dense.ai) for complex workflows that go beyond what C… |
| `omero-integration` | 7.9K | ✓ | — | `skills/stats/omero-integration.md` |
| ↳ | | | | Microscopy data management platform. Access images via Python, retrieve datasets, analyze pixels, manage ROIs/annotations, batch processing,… |
| `open-notebook` | 10.3K | ✓ | — | `skills/stats/open-notebook.md` |
| ↳ | | | | Self-hosted, open-source alternative to Google NotebookLM for AI-powered research and document analysis. Use when organizing research materi… |
| `opencli-reader` | 11.5K | ✓ | — | `skills/stats/opencli-reader.md` |
| ↳ | | | | Generic read-only fallback for sources opencli supports but no dedicated skill covers: finance sites (Yahoo Finance, Bloomberg, Reuters, Bar… |
| `paper-orchestration` | 6.1K | ✓ | — | `skills/stats/paper-orchestration.md` |
| ↳ | | | | Use when a research-writing task spans multiple sections, medium-sized revisions, full-paper drafting, or repeated quality failures |
| `pennylane` | 7.3K |  | — | `skills/stats/pennylane.md` |
| ↳ | | | | Hardware-agnostic quantum ML framework with automatic differentiation. Use when training quantum circuits via gradients, building hybrid qua… |
| `phylogenetics` | 13.7K |  | — | `skills/stats/phylogenetics.md` |
| ↳ | | | | Build and analyze phylogenetic trees using MAFFT (multiple alignment), IQ-TREE 2 (maximum likelihood), and FastTree (fast NJ/ML). Visualize … |
| `polars` | 9.3K | ✓ | — | `skills/stats/polars.md` |
| ↳ | | | | Fast in-memory DataFrame library for datasets that fit in RAM. Use when pandas is too slow but data still fits in memory. Lazy evaluation, p… |
| `pufferlib` | 13.2K | ✓ | — | `skills/stats/pufferlib.md` |
| ↳ | | | | High-performance reinforcement learning framework optimized for speed and scale. Use when you need fast parallel training, vectorized enviro… |
| `pyhealth` | 17.3K |  | — | `skills/stats/pyhealth.md` |
| ↳ | | | | Comprehensive healthcare AI toolkit for developing, testing, and deploying machine learning models with clinical data. This skill should be … |
| `pylabrobot` | 8.1K | ✓ | — | `skills/stats/pylabrobot.md` |
| ↳ | | | | Vendor-agnostic lab automation framework. Use when controlling multiple equipment types (Hamilton, Tecan, Opentrons, plate readers, pumps) o… |
| `pymc` | 15.5K | ✓ | — | `skills/stats/pymc.md` |
| ↳ | | | | Bayesian modeling with PyMC. Build hierarchical models, MCMC (NUTS), variational inference, LOO/WAIC comparison, posterior checks, for proba… |
| `pyopenms` | 5.5K | ✓ | — | `skills/stats/pyopenms.md` |
| ↳ | | | | Complete mass spectrometry analysis platform. Use for proteomics workflows feature detection, peptide identification, protein quantification… |
| `pysam` | 9.8K | ✓ | — | `skills/stats/pysam.md` |
| ↳ | | | | Genomic file toolkit. Read/write SAM/BAM/CRAM alignments, VCF/BCF variants, FASTA/FASTQ sequences, extract regions, calculate coverage, for … |
| `qinyan-paper-analysis` | 3.9K | ✓ | — | `skills/stats/qinyan-paper-analysis.md` |
| ↳ | | | | 沁言学术论文分析 - 对单篇学术论文进行深度分析解读，提取研究目标、方法论、主要发现和研究限制。通过沁言学术OpenAPI的analyze接口实现。触发词：论文分析、论文解读、分析论文、paper analysis、analyze paper、论文解析 |
| `r-aging-cohort-databases` | 8.0K | ✓ | stats.baseline(member)、stats.regression(member)、stats.survival(member)、stats.survey(member)、stats.missing(member) | `skills/stats/r-aging-cohort-databases.md` |
| ↳ | | | | 七大老年数据库（HRS 家族 + CHARLS）数据挖掘 R 语言实战技能。覆盖公共老年队列数据的获取与注册、Harmonized 数据（跨库可比变量体系）的使用、CHARLS 原始数据（.dta）与 Codebook 对照、变量构建与编码表核查，以及全套统计分析流程：table… |
| `r-clinical-prediction-model` | 13.8K | ✓ | stats.survival(member)、stats.prediction(member)、stats.diagnostic(member)、stats.missing(member)、stats.power(member)、stats.clean(member) | `skills/stats/r-clinical-prediction-model.md` |
| ↳ | | | | 临床预测模型（诊断模型 / 预后模型）R 语言全流程实战技能。覆盖：数据质量核查（含"0 值实为缺失码"陷阱）、建模人群与验证人群拆分、单因素/多因素变量筛选（含 Lasso）、Logistic 与 Cox 建模、列线图（诊断概率 / 中位生存时间 / 1-3-5 年生存率 / … |
| `r-machine-learning-interpretability` | 10.0K | ✓ | stats.prediction(member)、stats.interpret(member) | `skills/stats/r-machine-learning-interpretability.md` |
| ↳ | | | | 临床机器学习建模与可解释性研究（R 语言）实战技能。覆盖二分类 8 模型（Logistic / 决策树 / 随机森林 / XGBoost / LightGBM / KNN / SVM / 神经网络）与生存数据 6 模型（RSF / CoxBoost / survivalsvm /… |
| `r-medical-research-master` | 16.5K | ✓ | stats.twogroup(member)、stats.mr(member)、stats.corr(member) | `skills/stats/r-medical-research-master.md` |
| ↳ | | | | R 语言医学统计与科研全流程总纲技能（九大领域一体化总入口）。当用户提出任何医学统计、临床科研数据分析、论文图表制作、科研绘图、统计方法选择、代码排错需求时，先加载本技能以定位应调用的子技能：临床预测模型 / 机器学习与可解释性 / 孟德尔随机化 / 七大老年数据库 / 倾向得分… |
| `r-medical-stats` | 39.0K | ✓ | literature.meta-extract(member)、stats.baseline(member)、stats.twogroup(member)、stats.multigroup(member)、stats.regression(member)、stats.survival(member)、stats.prediction(member)、stats.interpret(member)、stats.psm(member)、stats.diagnostic(member)、stats.meta(member)、stats.missing(member)、stats.power(member)、stats.corr(member)、stats.clean(member) | `skills/stats/r-medical-stats.md` |
| ↳ | | | | R 语言医学统计与科研绘图通用引擎（双模式）。模式A【直接执行】：自动完成环境自检、读取用户数据、按需求执行统计分析并输出投稿级别的统计图与统计表，统计图默认交付可编辑 SVG（文本保持为 <text> 元素，可在 Illustrator/Inkscape 中改字号、改颜色、改标… |
| `r-mendelian-randomization` | 9.3K | ✓ | stats.mr(member) | `skills/stats/r-mendelian-randomization.md` |
| ↳ | | | | 孟德尔随机化（Mendelian Randomization）R 语言全流程实战技能。覆盖两样本 MR 标准流程（暴露/结局数据读取、p<5e-8 筛选、LD clump、等位基因协调 harmonise_data、IVW/MR-Egger/加权中位数/加权众数估计、OR 转换）… |
| `r-nhanes-analysis` | 9.2K | ✓ | stats.regression(member)、stats.survey(member) | `skills/stats/r-nhanes-analysis.md` |
| ↳ | | | | NHANES（美国国家健康与营养调查）数据挖掘 R 语言实战技能。覆盖复杂抽样权重的正确处理（svydesign + options(survey.lonely.psu="adjust") + nest=TRUE + 权重变量选择 + 多周期合并权重除以周期数）、加权描述与检验（… |
| `r-pharmacology-singlecell-mr` | 7.5K | ✓ | stats.mr(member) | `skills/stats/r-pharmacology-singlecell-mr.md` |
| ↳ | | | | 网络药理学与单细胞测序 R 语言实战技能。覆盖中药/药物成分-靶点网络构建与通路富集（KEGG/GO，clusterProfiler + org.Hs.eg.db + bitr 映射 + 气泡图/Facet 条形图 + 基因-通路表构建）、STRING 蛋白互作与交集、药靶孟德尔… |
| `r-propensity-score-methods` | 7.4K | ✓ | stats.psm(member) | `skills/stats/r-propensity-score-methods.md` |
| ↳ | | | | 倾向得分方法（Propensity Score Methods）R 语言全流程实战技能。覆盖混杂偏倚的识别与应对体系、反事实框架与潜在结局、倾向得分的计算与四大用法（PSM 匹配 / PS 分层 / IPTW 加权 / PS 作为协变量回归）、Robins 与 Hernán 两种… |
| `r-real-world-evidence` | 8.0K | ✓ | stats.psm(member)、stats.survey(member) | `skills/stats/r-real-world-evidence.md` |
| ↳ | | | | 真实世界研究（RWE）R 语言实战技能。覆盖倾向得分匹配与加权的进阶方法：cobalt 平衡性诊断（love.plot 以 SMD<0.1 为阈值、bal.plot 重叠性检查）、重叠加权 Overlap Weighting（PSweight，估计 ATO、天然规避极端权重、报告… |
| `r-trajectory-models` | 6.7K | ✓ | stats.multigroup(member) | `skills/stats/r-trajectory-models.md` |
| ↳ | | | | 纵向数据轨迹模型（组基轨迹模型 GBTM / 潜类别增长模型 LCGM / 多变量轨迹 GBMTM）R 语言实战技能。覆盖宽转长的多变量多时间点整形（pivot_longer + .value + names_pattern）、gbmt 包与 lcmm 包两条技术路线、模型选择的… |
| `research-lookup` | 15.9K | ✓ | — | `skills/stats/research-lookup.md` |
| ↳ | | | | Look up current research information using the Parallel Chat API (primary) or Perplexity sonar-pro-search (academic paper searches). Automat… |
| `scholar-annotate` | 18.1K | ✓ | — | `skills/stats/scholar-annotate.md` |
| ↳ | | | | Turn unstructured text into validated, structured variables at corpus scale with LLMs: codebook design, dev/gold-set construction, DSPy prom… |
| `scholar-auto-improve` | 31.6K | ✓ | — | `skills/stats/scholar-auto-improve.md` |
| ↳ | | | | Automatic quality auditor and continuous improvement engine for the scholar-skill suite. Four modes: (1) OBSERVE — post-skill output audit (… |
| `scholar-causal` | 39.2K | ✓ | stats.psm(member) | `skills/stats/scholar-causal.md` |
| ↳ | | | | Comprehensive causal inference toolkit for social science research. Covers DAG construction, method selection, and thirteen identification s… |
| `scholar-code-review` | 34.9K | ✓ | stats.clean(member) | `skills/stats/scholar-code-review.md` |
| ↳ | | | | Systematic multi-agent code review of all analysis scripts produced in a project. 6 specialized agents review for: (1) correctness & logic e… |
| `scholar-collaborate` | 22.6K | ✓ | — | `skills/stats/scholar-collaborate.md` |
| ↳ | | | | Multi-author research collaboration management. Covers CRediT role assignment, task delegation and tracking, co-author communication templat… |
| `scholar-compute` | 57.6K | ✓ | — | `skills/stats/scholar-compute.md` |
| ↳ | | | | Design and execute computational social science analyses across 11 modules: text-as-data/NLP (STM, BERTopic, Wordfish, BERT, conText embeddi… |
| `scholar-ethics` | 38.0K | ✓ | ideation.ethics(member) | `skills/stats/scholar-ethics.md` |
| ↳ | | | | Research ethics toolkit for social scientists. Covers (1) AI tool data privacy audit — document and report how data was handled when using t… |
| `scholar-evaluation` | 12.0K | ✓ | — | `skills/stats/scholar-evaluation.md` |
| ↳ | | | | Systematically evaluate scholarly work using the ScholarEval framework, providing structured assessment across research quality dimensions i… |
| `scholar-idea` | 34.8K | ✓ | ideation.question(member) | `skills/stats/scholar-idea.md` |
| ↳ | | | | Explore broad social science ideas and convert them into formal, researchable questions. Use when the user has an early-stage topic, puzzle,… |
| `scholar-init` | 32.4K | ✓ | — | `skills/stats/scholar-init.md` |
| ↳ | | | | Initialize a new research project directory for open-scholar-skill. Creates the standard layout (data/raw, data/interim, data/processed, mat… |
| `scholar-knowledge` | 66.9K | ✓ | — | `skills/stats/scholar-knowledge.md` |
| ↳ | | | | User-scoped, cross-project knowledge graph that persists extracted intellectual content (findings, mechanisms, theories, paper relationships… |
| `scholar-ling` | 26.3K | ✓ | — | `skills/stats/scholar-ling.md` |
| ↳ | | | | Design and analyze studies in sociolinguistics, language variation, acoustic phonetics, discourse analysis, language contact, and computatio… |
| `scholar-open` | 56.7K | ✓ | ideation.ethics(member) | `skills/stats/scholar-open.md` |
| ↳ | | | | Implement open science practices for a social science study. Five modes: (1) PREREGISTER — OSF / AsPredicted / EGAP / Registered Reports; se… |
| `scholar-openai` | 24.1K | ✓ | — | `skills/stats/scholar-openai.md` |
| ↳ | | | | External review via OpenAI Codex CLI agents. Spawns multiple parallel Codex agents (codex exec) to independently review analysis scripts, ve… |
| `scholar-qual` | 61.7K | ✓ | — | `skills/stats/scholar-qual.md` |
| ↳ | | | | Qualitative research methods toolkit for social sciences. Covers codebook development, grounded theory coding (open, axial, selective), Brau… |
| `scholar-safety` | 45.8K | ✓ | ideation.ethics(member) | `skills/stats/scholar-safety.md` |
| ↳ | | | | Real-time data privacy and leakage protection layer for AI-assisted research. Before any file is read by Claude Code and transmitted to Anth… |
| `scholar-simulate` | 20.4K | ✓ | — | `skills/stats/scholar-simulate.md` |
| ↳ | | | | Run LLM-powered social simulations at scale: silicon sampling, generative ABM, survey/vignette/conjoint experiments, opinion dynamics. Multi… |
| `scientific-critical-thinking` | 23.2K | ✓ | literature.critique(member)、literature.meta-extract(member) | `skills/stats/scientific-critical-thinking.md` |
| ↳ | | | | Evaluate scientific claims and evidence quality. Use for assessing experimental design validity, identifying biases and confounders, applyin… |
| `scientific-thinking-biology` | 11.4K |  | figures.mechanism(member) | `skills/stats/scientific-thinking-biology.md` |
| ↳ | | | | Use when interpreting biological research findings, evaluating life science evidence, analyzing molecular or cellular mechanisms, comparing … |
| `scikit-bio` | 14.5K | ✓ | — | `skills/stats/scikit-bio.md` |
| ↳ | | | | Biological data toolkit. Sequence analysis, alignments, phylogenetic trees, diversity metrics (alpha/beta, UniFrac), ordination (PCoA), PERM… |
| `scikit-learn` | 15.2K | ✓ | stats.interpret(member)、stats.diagnostic(member) | `skills/stats/scikit-learn.md` |
| ↳ | | | | Machine learning in Python with scikit-learn. Use when working with supervised learning (classification, regression), unsupervised learning … |
| `scikit-survival` | 14.8K | ✓ | stats.survival(member)、stats.prediction(member) | `skills/stats/scikit-survival.md` |
| ↳ | | | | Comprehensive toolkit for survival analysis and time-to-event modeling in Python using scikit-survival. Use this skill when working with cen… |
| `scvelo` | 10.1K | ✓ | — | `skills/stats/scvelo.md` |
| ↳ | | | | RNA velocity analysis with scVelo. Estimate cell state transitions from unspliced/spliced mRNA dynamics, infer trajectory directions, comput… |
| `scvi-tools` | 7.1K | ✓ | — | `skills/stats/scvi-tools.md` |
| ↳ | | | | Deep generative models for single-cell omics. Use when you need probabilistic batch correction (scVI), transfer learning, differential expre… |
| `shap` | 18.0K | ✓ | stats.interpret(member) | `skills/stats/shap.md` |
| ↳ | | | | Model interpretability and explainability using SHAP (SHapley Additive exPlanations). Use this skill when explaining machine learning model … |
| `simpy` | 11.9K | ✓ | — | `skills/stats/simpy.md` |
| ↳ | | | | Process-based discrete-event simulation framework in Python. Use this skill when building simulations of systems with processes, queues, res… |
| `skill-library-audit` | 3.4K | ✓ | — | `skills/stats/skill-library-audit.md` |
| ↳ | | | | 技能库健康体检工具。检测完全重复的技能目录、frontmatter 与目录名不一致、功能重叠竞争，并统计技能库规模与体积分布。当用户刚批量安装过技能、怀疑有重复、技能太多想整理，或说"技能重复了""检查技能库""整理技能库"时使用。 |
| `stable-baselines3` | 9.4K | ✓ | — | `skills/stats/stable-baselines3.md` |
| ↳ | | | | Production-ready reinforcement learning algorithms (PPO, SAC, DQN, TD3, DDPG, A2C) with scikit-learn-like API. Use for standard RL experimen… |
| `startup-analysis` | 8.7K |  | — | `skills/stats/startup-analysis.md` |
| ↳ | | | | Analyze a startup from three perspectives — VC investor, job applicant, and CEO/founder — covering market, traction, unit economics, team, d… |
| `statistical-analysis` | 19.4K | ✓ | stats.baseline(member)、stats.twogroup(member)、stats.multigroup(member)、stats.diagnostic(member)、stats.meta(member)、stats.power(member)、stats.corr(member) | `skills/stats/statistical-analysis.md` |
| ↳ | | | | Guided statistical analysis with test selection and reporting. Use when you need help choosing appropriate tests for your data, assumption c… |
| `statsmodels` | 19.3K | ✓ | stats.multigroup(member)、stats.regression(member)、stats.survey(member) | `skills/stats/statsmodels.md` |
| ↳ | | | | Statistical models library for Python. Use when you need specific model classes (OLS, GLM, mixed models, ARIMA) with detailed diagnostics, r… |
| `tradingview-mcp` | 9.6K |  | — | `skills/stats/tradingview-mcp.md` |
| ↳ | | | | Query TradingView market data through the bundled tradingview MCP server without a desktop app or login. Use whenever the user wants a techn… |
| `tradingview-reader` | 13.4K |  | — | `skills/stats/tradingview-reader.md` |
| ↳ | | | | Read the user's local TradingView desktop app through opencli: quotes, options chains with greeks and per-strike IV, options expiries, scree… |
| `transformers` | 5.0K | ✓ | — | `skills/stats/transformers.md` |
| ↳ | | | | This skill should be used when working with pre-trained transformer models for natural language processing, computer vision, audio, or multi… |
| `twitter-reader` | 7.6K | ✓ | — | `skills/stats/twitter-reader.md` |
| ↳ | | | | Read Twitter/X for financial research through opencli: the user's home timeline, tweet search, trending topics, bookmarks, a user's recent t… |
| `what-if-oracle` | 9.3K |  | — | `skills/stats/what-if-oracle.md` |
| ↳ | | | | Run structured What-If scenario analysis with multi-branch possibility exploration. Use this skill when the user asks speculative questions … |
| `yc-reader` | 7.0K | ✓ | — | `skills/stats/yc-reader.md` |
| ↳ | | | | Look up Y Combinator companies and batches from the public yc-oss API, a static JSON dataset refreshed daily: company profiles, batch roster… |
| `zarr-python` | 19.6K | ✓ | — | `skills/stats/zarr-python.md` |
| ↳ | | | | Chunked N-D arrays for cloud storage. Compressed arrays, parallel I/O, S3/GCS integration, NumPy/Dask/Xarray compatible, for large-scale sci… |

## 科研思路与标书（33）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `airs-brainstorming-research-ideas` | 19.2K | ✓ | ideation.topic(member) | `skills/ideation/airs-brainstorming-research-ideas.md` |
| ↳ | | | | Guides researchers through structured ideation frameworks to discover high-impact research directions. Use when exploring new problem spaces… |
| `arf-review-grant` | 22.5K | ✓ | ideation.feasibility(member)、ideation.grant(member) | `skills/ideation/arf-review-grant.md` |
| ↳ | | | | Run a 6-agent pre-submission panel review for a grant proposal targeting a specified funder or program |
| `aris-embodiment-description` | 6.8K | ✓ | — | `skills/ideation/aris-embodiment-description.md` |
| ↳ | | | | Write detailed embodiment descriptions for patent specifications. Use when user says \"撰写实施例\", \"write embodiment\", \"实施例描述\", \"detailed … |
| `aris-experiment-plan` | 9.8K | ✓ | ideation.feasibility(member)、ideation.design(member) | `skills/ideation/aris-experiment-plan.md` |
| ↳ | | | | Turn a refined research proposal or method idea into a detailed, claim-driven experiment roadmap. Use after `research-refine`, or when the u… |
| `aris-grant-proposal` | 36.0K | ✓ | ideation.grant(member) | `skills/ideation/aris-grant-proposal.md` |
| ↳ | | | | Draft a structured grant proposal from research ideas and literature. Supports KAKENHI (Japan), NSF (US), NSFC (China, including 面上/青年/优青/杰青… |
| `aris-idea-creator` | 35.0K | ✓ | ideation.topic(member) | `skills/ideation/aris-idea-creator.md` |
| ↳ | | | | Generate and rank research ideas given a broad direction. Use when user says "找idea", "brainstorm ideas", "generate research ideas", "what c… |
| `aris-idea-discovery` | 28.3K | ✓ | ideation.topic(member)、ideation.novelty(member) | `skills/ideation/aris-idea-discovery.md` |
| ↳ | | | | Workflow 1: Full idea discovery pipeline to go from a broad research direction to validated, pilot-tested ideas. Use when user says \"找idea全… |
| `aris-idea-discovery-robot` | 16.1K | ✓ | — | `skills/ideation/aris-idea-discovery-robot.md` |
| ↳ | | | | Workflow 1 adaptation for robotics and embodied AI. Orchestrates robotics-aware literature survey, idea generation, novelty check, and criti… |
| `aris-novelty-check` | 8.4K | ✓ | ideation.novelty(member) | `skills/ideation/aris-novelty-check.md` |
| ↳ | | | | Verify research idea novelty against recent literature. Use when user says "查新", "novelty check", "有没有人做过", "check novelty", or wants to ver… |
| `aris-patent-novelty-check` | 7.0K | ✓ | ideation.novelty(member) | `skills/ideation/aris-patent-novelty-check.md` |
| ↳ | | | | Assess patent novelty and non-obviousness against prior art. Use when user says \"专利查新\", \"patent novelty\", \"可专利性评估\", \"patentability ch… |
| `aris-patent-review` | 8.0K | ✓ | — | `skills/ideation/aris-patent-review.md` |
| ↳ | | | | Get an external patent examiner review of a patent application. Use when user says \"专利审查\", \"patent review\", \"审查意见\", \"examiner review\… |
| `basic-research-design-extractor` | 4.6K | ✓ | ideation.design(member) | `skills/ideation/basic-research-design-extractor.md` |
| ↳ | | | | Extract a basic biomedical research design from one article and quickly produce a detailed Markdown-document experimental plan. Use when the… |
| `clinical-research-design-extractor` | 4.2K | ✓ | ideation.design(member) | `skills/ideation/clinical-research-design-extractor.md` |
| ↳ | | | | Extract a clinical research design from one clinical article and quickly produce a formatted Chinese project-application-style clinical stud… |
| `diffdock` | 15.2K |  | — | `skills/ideation/diffdock.md` |
| ↳ | | | | Diffusion-based molecular docking. Predict protein-ligand binding poses from PDB/SMILES, confidence scores, virtual screening, for structure… |
| `experiment-results-planning` | 4.0K |  | ideation.design(member) | `skills/ideation/experiment-results-planning.md` |
| ↳ | | | | Use when designing experiments, result tables, mock planning data, evaluation protocols, or results sections before real data are final |
| `glycoengineering` | 12.2K |  | — | `skills/ideation/glycoengineering.md` |
| ↳ | | | | Analyze and engineer protein glycosylation. Scan sequences for N-glycosylation sequons (N-X-S/T), predict O-glycosylation hotspots, and acce… |
| `gm-muapi-design-guide` | 4.4K |  | — | `skills/ideation/gm-muapi-design-guide.md` |
| ↳ | | | | Create a comprehensive brand design guide — color palette, typography pairings, UI component previews, and visual identity rules with exampl… |
| `gm-muapi-logo-branding` | 4.4K |  | — | `skills/ideation/gm-muapi-logo-branding.md` |
| ↳ | | | | Design a professional logo with full branding package — primary logo, variations (dark/light/icon-only), color palette, and real-world appli… |
| `gm-muapi-ui-design` | 3.6K |  | — | `skills/ideation/gm-muapi-ui-design.md` |
| ↳ | | | | Generate high-fidelity UI/UX mockups for mobile and web apps using Atomic Design principles — creates wireframes and design systems via muap… |
| `gm-muapi-url-to-design` | 3.6K |  | — | `skills/ideation/gm-muapi-url-to-design.md` |
| ↳ | | | | Analyze a website URL and generate a redesigned, improved UI — recreate the visual design with modern aesthetics, better hierarchy, and fres… |
| `hypogenic` | 21.2K | ✓ | ideation.question(member) | `skills/ideation/hypogenic.md` |
| ↳ | | | | Automated LLM-driven hypothesis generation and testing on tabular datasets. Use when you want to systematically explore hypotheses about pat… |
| `hypothesis-generation` | 13.6K | ✓ | ideation.question(member) | `skills/ideation/hypothesis-generation.md` |
| ↳ | | | | Structured hypothesis formulation from observations. Use when you have experimental observations or data and need to formulate testable hypo… |
| `idea-evaluator` | 13.7K | ✓ | ideation.feasibility(member) | `skills/ideation/idea-evaluator.md` |
| ↳ | | | | Evaluates a preliminary research idea against a five-dimension framework (Higher, Faster, Stronger, Cheaper, Broader) plus idea-lifecycle an… |
| `pymoo` | 16.4K |  | — | `skills/ideation/pymoo.md` |
| ↳ | | | | Multi-objective optimization framework. NSGA-II, NSGA-III, MOEA/D, Pareto fronts, constraint handling, benchmarks (ZDT, DTLZ), for engineeri… |
| `qinyan-topic-analysis` | 4.4K | ✓ | ideation.novelty(member) | `skills/ideation/qinyan-topic-analysis.md` |
| ↳ | | | | 沁言学术AI选题分析 - 基于大量文献检索结果，为科研人员提供智能选题建议，包括选题方向、研究价值、研究内容概述、研究难点分析和相关文献推荐。使用沁言学术OpenAPI进行文献检索。触发词：选题分析、选题建议、研究选题、topic analysis、research topic、… |
| `research-grants` | 36.4K | ✓ | ideation.grant(member) | `skills/ideation/research-grants.md` |
| ↳ | | | | Write competitive research proposals for NSF, NIH, DOE, DARPA, and Taiwan NSTC. Agency-specific formatting, review criteria, budget preparat… |
| `research-proposal` | 19.8K | ✓ | ideation.grant(member) | `skills/ideation/research-proposal.md` |
| ↳ | | | | Generate academic research proposals for PhD applications. Use when user asks to "write a research proposal", "create PhD proposal", "genera… |
| `researchwrite` | 6.8K | ✓ | ideation.grant(member) | `skills/ideation/researchwrite.md` |
| ↳ | | | | Compose, revise, or audit research proposals, opening reports, and research plans from supporting evidence. Use for 研究计划、开题报告、科研项目申请书. Invok… |
| `scholar-brainstorm` | 17.1K | ✓ | ideation.topic(member)、ideation.question(member) | `skills/ideation/scholar-brainstorm.md` |
| ↳ | | | | Generate research questions from existing materials — codebooks, survey questionnaires, datasets, or published papers/abstracts. Three modes… |
| `scholar-lit-review-hypothesis` | 57.7K | ✓ | ideation.question(member) | `skills/ideation/scholar-lit-review-hypothesis.md` |
| ↳ | | | | Conduct a systematic literature review AND develop theory and hypotheses in one integrated workflow. Use when the user wants to map existing… |
| `scientific-brainstorming` | 8.1K | ✓ | ideation.topic(member) | `skills/ideation/scientific-brainstorming.md` |
| ↳ | | | | Creative research ideation and exploration. Use for open-ended brainstorming sessions, exploring interdisciplinary connections, challenging … |
| `sp-brainstorming` | 13.6K | ✓ | — | `skills/ideation/sp-brainstorming.md` |
| ↳ | | | | You MUST use this before any creative work - creating features, building components, adding functionality, modifying behavior, or planning a… |
| `tech-paper-template` | 7.1K | ✓ | ideation.feasibility(member) | `skills/ideation/tech-paper-template.md` |
| ↳ | | | | Structures a technical paper's full logical skeleton using a thinking-template table (research background, limitations, key idea or goal, ch… |

## 审稿与修回（39）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `academic-pre-review-committee` | 5.9K | ✓ | review.presubmit(member) | `skills/review/academic-pre-review-committee.md` |
| ↳ | | | | 由五位资深审稿人组成的"学术预审委员会"，根据用户需求调度对应的审稿人角色进行论文审查。支持全面审稿（依次调度全部五个角色）和指定维度审稿。触发关键词：审稿、预审、论文审查、理论贡献、方法论、文献对话、逻辑链条、主编预筛、desk reject。 |
| `agbm-alphagbm-grid-plan` | 2.4K |  | — | `skills/review/agbm-alphagbm-grid-plan.md` |
| ↳ | | | | Build an auditable grid from a price range, current price and capital. Use when the user asks to grid plan with AlphaGBM. Use the bundled Py… |
| `agbm-alphagbm-investment-review` | 2.8K |  | — | `skills/review/agbm-alphagbm-investment-review.md` |
| ↳ | | | | Compare research records you provide to see changes in facts, scores and judgments. Use when the user asks to investment review with AlphaGB… |
| `airs-ara-rigor-reviewer` | 17.8K | ✓ | — | `skills/review/airs-ara-rigor-reviewer.md` |
| ↳ | | | | Performs ARA Seal Level 2 semantic epistemic review on Agent-Native Research Artifacts, scoring six dimensions (evidence relevance, falsifia… |
| `airs-nemo-guardrails` | 7.8K |  | — | `skills/review/airs-nemo-guardrails.md` |
| ↳ | | | | NVIDIA's runtime safety framework for LLM applications. Features jailbreak detection, input/output validation, fact-checking, hallucination … |
| `arf-audit-analysis` | 4.5K | ✓ | review.audit(member) | `skills/review/arf-audit-analysis.md` |
| ↳ | | | | Adversarially audit changed analysis code against a base ref, hunting for correctness errors in sample construction, merges, variable constr… |
| `arf-review-paper` | 38.0K | ✓ | review.referee(member)、review.report(member) | `skills/review/arf-review-paper.md` |
| ↳ | | | | Run an 8-agent pre-submission referee report for an academic paper targeting a specified journal |
| `arf-review-paper-checks` | 17.3K | ✓ | review.presubmit(member)、review.selfcheck(member) | `skills/review/arf-review-paper-checks.md` |
| ↳ | | | | Run a fast 3-agent mechanical check of an economics paper — spelling and grammar, internal consistency and cross-references, and unsupported… |
| `arf-review-paper-code` | 12.4K | ✓ | review.audit(member) | `skills/review/arf-review-paper-code.md` |
| ↳ | | | | Review research code for reproducibility and quality, extract the paper's main empirical claims, compare paper to code, and write a construc… |
| `arf-review-paper-light` | 9.4K | ✓ | — | `skills/review/arf-review-paper-light.md` |
| ↳ | | | | Run a fast 2-agent pre-submission check for an economics paper — focuses on contribution, identification, and causal overclaiming. Completes… |
| `aris-kill-argument` | 26.0K | ✓ | review.referee(member) | `skills/review/aris-kill-argument.md` |
| ↳ | | | | Two-thread adversarial review: a fresh reviewer constructs the strongest 200-word rejection memo, then a second fresh reviewer defends the p… |
| `aris-overleaf-sync` | 11.2K |  | — | `skills/review/aris-overleaf-sync.md` |
| ↳ | | | | Two-way sync between a local paper directory and an Overleaf project, so ARIS audit/edit workflows stay on the local copy while collaborator… |
| `aris-paper-claim-audit` | 15.4K | ✓ | review.audit(member) | `skills/review/aris-paper-claim-audit.md` |
| ↳ | | | | Zero-context verification that every number, comparison, and scope claim in the paper matches raw result files. Uses a fresh cross-model rev… |
| `aris-proof-checker` | 56.3K | ✓ | — | `skills/review/aris-proof-checker.md` |
| ↳ | | | | Rigorous mathematical proof verification and fixing workflow. Reads a LaTeX proof, identifies gaps via cross-model review (external reviewer… |
| `aris-rebuttal` | 25.6K | ✓ | review.revise(member)、review.rebuttal(member)、review.appeal(member) | `skills/review/aris-rebuttal.md` |
| ↳ | | | | Workflow 4: Submission rebuttal pipeline. Parses external reviews, enforces coverage and grounding, drafts a safe text-only rebuttal under v… |
| `ars-academic-paper-reviewer` | 49.5K | ✓ | review.referee(member)、review.report(member)、review.revise(member) | `skills/review/ars-academic-paper-reviewer.md` |
| ↳ | | | | Multi-perspective academic paper review with dynamic reviewer personas. Runs a 5-seat, role-separated review panel (Journal-Fit Reviewer + 3… |
| `ars-academic-pipeline` | 59.0K | ✓ | review.appeal(member) | `skills/review/ars-academic-pipeline.md` |
| ↳ | | | | Orchestrator for the full academic research pipeline: research -> write -> integrity check -> review -> revise -> re-review -> re-revise -> … |
| `cavecrew` | 3.7K | ✓ | — | `skills/review/cavecrew.md` |
| ↳ | | | | When to delegate to `cavecrew-investigator` (locate code), `cavecrew-builder` (1-2 file edit) or `cavecrew-reviewer` (diff review) instead o… |
| `caveman-evidence-review` | 3.7K |  | — | `skills/review/caveman-evidence-review.md` |
| ↳ | | | | Read-only review of Caveman Cloud evidence: cost, Cave Score, workflows, traces, latency, errors, routing, savings. Use when asked what Cave… |
| `caveman-review` | 2.6K |  | — | `skills/review/caveman-review.md` |
| ↳ | | | | Compressed code review - one line per finding with location, problem and fix. Use for /caveman-review, "review this PR", or "review the diff… |
| `dbt-auditing-skills` | 10.1K | ✓ | — | `skills/review/dbt-auditing-skills.md` |
| ↳ | | | | Use when checking skills for security or quality issues, reviewing audit results from skills.sh or Tessl, or remediating findings across pub… |
| `earnings-preview` | 6.0K |  | — | `skills/review/earnings-preview.md` |
| ↳ | | | | Build a pre-earnings briefing for a stock from Yahoo Finance data (yfinance): the upcoming report date and timing, consensus EPS and revenue… |
| `last30days` | 31.0K |  | — | `skills/review/last30days.md` |
| ↳ | | | | Research what people actually say about any topic in the last 30 days. Pulls posts and engagement from Reddit, X, YouTube, TikTok, Hacker Ne… |
| `nature-response` | 5.9K | ✓ | review.revise(member)、review.rebuttal(member)、review.appeal(member) | `skills/review/nature-response.md` |
| ↳ | | | | Draft, audit, or revise responses to peer review, revision cover letters, and marked-manuscript or LaTeX revision packages. Use for 审稿意见回复、逐… |
| `nature-reviewer` | 11.1K | ✓ | review.referee(member)、review.report(member)、review.selfcheck(member) | `skills/review/nature-reviewer.md` |
| ↳ | | | | Provide evidence-grounded mock peer review of scientific manuscripts or excerpts, covering significance, validity, and major/minor concerns.… |
| `nature-statistics` | 8.2K | ✓ | review.audit(member) | `skills/review/nature-statistics.md` |
| ↳ | | | | Audit or improve manuscript statistical reporting, including experimental units, replication, uncertainty, tests, and figure statistics. Use… |
| `paper-audit` | 20.2K | ✓ | review.presubmit(member)、review.selfcheck(member) | `skills/review/paper-audit.md` |
| ↳ | | | | Reviewer-style audit and submission gate for academic papers in .tex, .typ, or .pdf. Use for peer-review critique, readiness/gate decisions,… |
| `paper-ct-scan` | 13.9K | ✓ | format.submission-package(member)、review.presubmit(member) | `skills/review/paper-ct-scan.md` |
| ↳ | | | | 论文CT、论文检测、论文漏洞扫描、论文审校、论文体检、学术鉴真、论文真实性检测、论文可行性分析、 论文AI检测、论文排版检查、论文格式审查、学术论文质检、期刊论文审核、论文内容真伪鉴别、 论文参考文献核查、论文数据验证、国家级刊物论文检测、省级论文审核、论文发表前自检、 论文查重… |
| `peer-review` | 22.6K | ✓ | review.report(member)、review.selfcheck(member) | `skills/review/peer-review.md` |
| ↳ | | | | Structured manuscript/grant review with checklist-based evaluation. Use when writing formal peer reviews with specific criteria methodology … |
| `ponytail-audit` | 5.2K |  | — | `skills/review/ponytail-audit.md` |
| ↳ | | | | Quality audit of the whole repo: bugs, security, real load, missing tests, speed, and what to delete. Most important first. |
| `ponytail-review` | 4.9K |  | — | `skills/review/ponytail-review.md` |
| ↳ | | | | Quality review of a diff: bugs, security, real load, missing tests, speed, and what to delete. Each finding says what goes wrong and how to … |
| `pre-submission-reviewer` | 12.8K | ✓ | review.presubmit(member) | `skills/review/pre-submission-reviewer.md` |
| ↳ | | | | Runs a pre-submission review of a technical paper across five dimensions: macro logic, writing details, English grammar, LaTeX formatting, a… |
| `ps-deep-research` | 34.1K | ✓ | — | `skills/review/ps-deep-research.md` |
| ↳ | | | | 四阶段递归深度研究。好奇循环广泛探索 → 深度推理检测盲区 → 同行评审对抗验证 → 采纳优化后交付顾问级报告。适用于选型 / 竞品对比 / 技术调研 / 可行性评估 / 趋势综合等需跨多权威源交叉验证的开放问题；单点事实、写代码、纯计算、简单 how-to 不要用。 |
| `rebuttal-guidance` | 5.4K | ✓ | review.rebuttal(member) | `skills/review/rebuttal-guidance.md` |
| ↳ | | | | Provides actionable peer-review rebuttal guidance (not full rebuttal prose) using conditional persuasion P(Z|X,Y): match reviewer mindset X,… |
| `scholar-respond` | 63.2K | ✓ | review.revise(member)、review.rebuttal(member)、review.appeal(member) | `skills/review/scholar-respond.md` |
| ↳ | | | | Simulate peer review, draft point-by-point responses to reviewer comments, revise a manuscript, plan a resubmission to a new journal after r… |
| `sp-requesting-code-review` | 3.1K | ✓ | — | `skills/review/sp-requesting-code-review.md` |
| ↳ | | | | Use when completing tasks, implementing major features, or before merging to verify work meets requirements |
| `timesfm-forecasting` | 29.5K | ✓ | — | `skills/review/timesfm-forecasting.md` |
| ↳ | | | | Zero-shot time series forecasting with Google's TimesFM foundation model. Use for any univariate time series (sales, sensors, energy, vitals… |
| `verify-and-stop` | 0.8K | ✓ | — | `skills/review/verify-and-stop.md` |
| ↳ | | | | Prove existing work meets acceptance conditions without expanding scope. Use for validation-only tasks, completion checks, focused gate runs… |
| `yfinance-data` | 5.2K |  | — | `skills/review/yfinance-data.md` |
| ↳ | | | | Fetch financial and market data with the yfinance Python library (Yahoo Finance). Use this skill whenever the user wants stock data: current… |

## 科研汇报与 PPT（44）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `论文汇报PPT制作` | 8.3K | ✓ | slides.journal-club(member)、slides.deck-system(member) | `skills/slides/论文汇报ppt制作.md` |
| ↳ | | | | 当用户需要为学术论文（中文/英文、量化/质性均可）生成组会文献汇报PPT时使用此技能。触发词包括：文献汇报、组会PPT、学术PPT、论文汇报、生成PPT、毕业论文答辩PPT、开题报告PPT、make a presentation for this paper、create sli… |
| `airs-presenting-conference-talks` | 10.4K | ✓ | slides.conference-defense(member)、slides.speaker-notes(member) | `skills/slides/airs-presenting-conference-talks.md` |
| ↳ | | | | Generates conference presentation slides (Beamer LaTeX PDF and editable PPTX) from a compiled paper with speaker notes and talk script. Use … |
| `alice-ppt-generator` | 10.8K | ✓ | slides.journal-club(member) | `skills/slides/alice-ppt-generator.md` |
| ↳ | | | | 根据主题与结构化内容自动生成专业 PPT 报告，支持标题页、目录、章节页、图文排版与结论总结，适用于汇报、方案说明和项目复盘。 |
| `arf-explorable-beamer` | 14.4K | ✓ | — | `skills/slides/arf-explorable-beamer.md` |
| ↳ | | | | Build a LaTeX beamer slide deck in the explorable-explanation style (Nicky Case) — one idea per frame, assertion titles, a concrete running … |
| `arf-explorable-deck` | 13.8K | ✓ | — | `skills/slides/arf-explorable-deck.md` |
| ↳ | | | | Build a Quarto reveal.js slide deck in the explorable-explanation style (Nicky Case) — one idea per slide, assertion titles, a concrete runn… |
| `arf-explorable-pptx` | 15.3K | ✓ | — | `skills/slides/arf-explorable-pptx.md` |
| ↳ | | | | Build a PowerPoint (.pptx) slide deck in the explorable-explanation style (Nicky Case) — one idea per frame, assertion titles, a concrete ru… |
| `aris-paper-slides` | 24.3K | ✓ | slides.conference-defense(member)、slides.speaker-notes(member)、slides.sync-script(member) | `skills/slides/aris-paper-slides.md` |
| ↳ | | | | Generate conference presentation slides (beamer LaTeX → PDF + editable PPTX) from a compiled paper, with speaker notes and full talk script.… |
| `caveman` | 4.6K |  | — | `skills/slides/caveman.md` |
| ↳ | | | | Terse caveman voice: answer first, fluff gone, every technical fact kept. Use for /caveman, "caveman mode", "talk like caveman", "be brief",… |
| `codex-ppt` | 10.2K | ✓ | — | `skills/slides/codex-ppt.md` |
| ↳ | | | | Generate visually unified image-based PPT/PPTX decks from articles, reports, papers, notes, or outlines. |
| `dashi-ppt` | 25.4K | ✓ | — | `skills/slides/dashi-ppt.md` |
| ↳ | | | | 制作 PPT、演示文稿、幻灯片、汇报材料时使用。Dashi PPT 基于预置视觉主题组合页面,生成可离线打开、可在浏览器编辑的 HTML 演示,支持导出 PPTX / PDF 文件。 |
| `deepchem` | 17.4K | ✓ | — | `skills/slides/deepchem.md` |
| ↳ | | | | Molecular ML with diverse featurizers and pre-built datasets. Use for property prediction (ADMET, toxicity) with traditional ML or GNNs when… |
| `design` | 13.9K | ✓ | — | `skills/slides/design.md` |
| ↳ | | | | Comprehensive design skill: brand identity, design tokens, UI styling, logo generation (55 styles, Gemini, Atlas Cloud, or MuAPI AI), corpor… |
| `design-system` | 7.3K | ✓ | — | `skills/slides/design-system.md` |
| ↳ | | | | Token architecture, component specifications, and slide generation. Three-layer tokens (primitive→semantic→component), CSS variables, spacin… |
| `elegant-ppt-builder` | 9.9K | ✓ | slides.deck-system(member)、slides.auto-build(member) | `skills/slides/elegant-ppt-builder.md` |
| ↳ | | | | This skill should be used when the user wants to create a beautiful, visually-rich PowerPoint deck. It generates .pptx files with complex vi… |
| `esm` | 10.4K | ✓ | — | `skills/slides/esm.md` |
| ↳ | | | | Comprehensive toolkit for protein language models including ESM3 (generative multimodal protein design across sequence, structure, and funct… |
| `find-skills` | 16.9K | ✓ | — | `skills/slides/find-skills.md` |
| ↳ | | | | 场景驱动+关键词双模式技能发现工具。当用户用自然语言描述场景/需求（如"我想做一个海报""帮我分析股票"），或明确说"安装技能/find skills/找个skill"时，自动从官方内置、本地已安装、SkillHub、虾评、GitHub、ClawHub 六层联合搜索并推荐最合适的… |
| `frontend-slides` | 27.6K | ✓ | — | `skills/slides/frontend-slides.md` |
| ↳ | | | | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when the user wants to build a presen… |
| `gm-muapi-talking-baby-video` | 2.7K |  | — | `skills/slides/gm-muapi-talking-baby-video.md` |
| ↳ | | | | Create a viral-style video of a talking baby with custom costumes and scripts. |
| `guizang-ppt-skill` | 31.0K | ✓ | — | `skills/slides/guizang-ppt-skill.md` |
| ↳ | | | | 生成横向翻页网页 PPT（单 HTML 文件），含 WebGL 背景、章节幕封、数据大字报、图片网格等模板。提供两种风格：① "电子杂志 × 电子墨水"（衬线 + 流体背景 + 暖色） ② "瑞士国际主义"（无衬线 + 网格点阵 + IKB/柠檬黄/柠檬绿/安全橙高亮）。当用户需… |
| `html-ppt` | 19.4K | ✓ | — | `skills/slides/html-ppt.md` |
| ↳ | | | | HTML PPT Studio — author professional static HTML presentations in many styles, layouts, and animations, all driven by templates. Use when t… |
| `huashu-design` | 15.3K | ✓ | — | `skills/slides/huashu-design.md` |
| ↳ | | | | 花叔Design——用HTML做高保真原型、幻灯片、动画、可视化与专家评审。任何新设计100%先出三个方向初稿给用户选（指定风格/品牌也不豁免），选定后才执行。触发词：做原型、PPT、幻灯片、动画、设计风格、评审、做个HTML页面、UI mockup、导出MP4/GIF、做个好看… |
| `ima-lit-meta-ppt` | 30.8K | ✓ | slides.journal-club(member)、slides.figure-refit(member)、stats.meta(member) | `skills/slides/ima-lit-meta-ppt.md` |
| ↳ | | | | 从 IMA 知识库批量获取文献，提取图表与结构化数据，执行自实现 Meta 分析，产出中文综述、Excel 文献清单与科研汇报 PPT。适用于"基于我的知识库写综述/做 meta 分析/做汇报 PPT"类任务。 |
| `latex-defense-zh` | 13.3K | ✓ | slides.conference-defense(member) | `skills/slides/latex-defense-zh.md` |
| ↳ | | | | Chinese thesis defense deck builder for existing XeLaTeX PhD or master thesis repositories. Extracts chapters, figures, equations, tables an… |
| `latex-posters` | 58.5K | ✓ | — | `skills/slides/latex-posters.md` |
| ↳ | | | | Create professional research posters in LaTeX using beamerposter, tikzposter, or baposter. Support for conference presentations, academic po… |
| `mono-color` | 33.5K | ✓ | — | `skills/slides/mono-color.md` |
| ↳ | | | | Generate original one-ink or controlled two-ink editorial images from any theme, sentence, article idea, object, or reference photo. Always … |
| `nature-image2ppt` | 9.9K | ✓ | slides.figure-refit(member) | `skills/slides/nature-image2ppt.md` |
| ↳ | | | | Reconstruct slide images, screenshots, scanned PDFs, or image-only PPTX files as object-level editable PowerPoint. Use for 图片转可编辑PPT、截图还原PPT… |
| `nature-paper2ppt` | 4.2K | ✓ | slides.journal-club(member)、slides.auto-build(member)、slides.sync-script(member) | `skills/slides/nature-paper2ppt.md` |
| ↳ | | | | Create or improve a Chinese academic PPTX from a scientific paper or research reading notes, with source figures and speaker notes. Use for … |
| `nature-shared` | 2.1K | ✓ | — | `skills/slides/nature-shared.md` |
| ↳ | | | | Internal shared-reference support package for installed Nature Skills, including nature-writing, nature-polishing, nature-response, nature-r… |
| `options-payoff` | 7.8K |  | — | `skills/slides/options-payoff.md` |
| ↳ | | | | Render an interactive options payoff chart — expiry P&L plus Black-Scholes theoretical value — with sliders for strikes, premium, IV, DTE, a… |
| `paper-slide-deck` | 18.3K | ✓ | — | `skills/slides/paper-slide-deck.md` |
| ↳ | | | | Generate professional slide deck images from academic papers and content. Creates comprehensive outlines with style instructions, auto-detec… |
| `pathml` | 7.2K | ✓ | — | `skills/slides/pathml.md` |
| ↳ | | | | Full-featured computational pathology toolkit. Use for advanced WSI analysis including multiplexed immunofluorescence (CODEX, Vectra), nucle… |
| `ppt-beautify` | 37.5K | ✓ | slides.deck-system(member) | `skills/slides/ppt-beautify.md` |
| ↳ | | | | 美化现有PPT中的页面，调整字体、配色、版式和视觉层级。适用于PPT美化、PPT排版。美图设计室提供。当用户需要“PPT美化”或描述中的等价能力时使用。当前对话已完成 PPT 时，用户要求导出、下载、获取 PPT 文件或可编辑版本也必须使用本 Skill。 |
| `ppt-design` | 37.7K | ✓ | — | `skills/slides/ppt-design.md` |
| ↳ | | | | 根据文字、数据或参考图生成可编辑PPT，完成信息整理与页面设计。适用于PPT设计、汇报页制作。美图设计室提供。当用户需要“PPT设计”或描述中的等价能力时使用。当前对话已完成 PPT 时，用户要求导出、下载、获取 PPT 文件或可编辑版本也必须使用本 Skill。 |
| `ppt-design-skill` | 18.8K | ✓ | — | `skills/slides/ppt-design-skill.md` |
| ↳ | | | | Design, generate, review, and revise editable PowerPoint presentations through a rigorous brief-to-PNG workflow using the public pptx-design… |
| `ppt-image-first` | 6.4K | ✓ | — | `skills/slides/ppt-image-first.md` |
| ↳ | | | | Build presentation plans for PPT / slides / decks through a conversation-first workflow, then propose multiple visual directions with previe… |
| `ppt-master` | 5.4K | ✓ | slides.auto-build(member) | `skills/slides/ppt-master.md` |
| ↳ | | | | AI-driven presentation workflow for generating editable PPTX decks and slides, reconstructing page visuals, creating reusable Brand/Style/La… |
| `pptx` | 9.0K | ✓ | slides.deck-system(member)、slides.figure-refit(member)、slides.sync-script(member) | `skills/slides/pptx.md` |
| ↳ | | | | Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, o… |
| `pptx-generator` | 3.8K | ✓ | slides.auto-build(member) | `skills/slides/pptx-generator.md` |
| ↳ | | | | 专业 PPT 生成器。11 种幻灯片类型、5 套配色、图表/表格/时间线/图片支持。JSON 驱动，生成标准可编辑 PPTX。PPT、幻灯片、演示文稿、PowerPoint。 |
| `qmd` | 4.8K |  | — | `skills/slides/qmd.md` |
| ↳ | | | | Local hybrid search for markdown notes and docs. Use when searching notes, finding related content, or retrieving documents from indexed col… |
| `scientific-slides` | 46.3K | ✓ | slides.conference-defense(member)、slides.figure-refit(member) | `skills/slides/scientific-slides.md` |
| ↳ | | | | Build slide decks and presentations for research talks. Use this for making PowerPoint slides, conference presentations, seminar talks, rese… |
| `slidep-pptx-notes` | 3.9K | ✓ | slides.speaker-notes(member) | `skills/slides/slidep-pptx-notes.md` |
| ↳ | | | | 为 slidep 生成的 PPTX 注入真实 PowerPoint 备注区讲稿（speaker notes）。解决 slidep notes 属性不生成 notesSlides part、zip 级 OOXML 注入后 python-pptx 读不到、descr 双重转义三大问题… |
| `slides` | 1.7K | ✓ | — | `skills/slides/slides.md` |
| ↳ | | | | Create strategic HTML presentations with Chart.js, design tokens, responsive layouts, copywriting formulas, and contextual slide strategies. |
| `sync-docs` | 8.5K | ✓ | slides.speaker-notes(member)、slides.sync-script(member) | `skills/slides/sync-docs.md` |
| ↳ | | | | Synchronize content across presentation slides, speaker script, and manuscript/paper. Audits for stale references, numbers, citations, and v… |
| `ui-styling` | 10.7K | ✓ | — | `skills/slides/ui-styling.md` |
| ↳ | | | | Create beautiful, accessible user interfaces with shadcn/ui components (built on Radix UI + Tailwind), Tailwind CSS utility-first styling, a… |

## 文献与引文（152）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `论文搜索专业版` | 2.5K | ✓ | format.journal-fit(member)、literature.pico-query(member) | `skills/literature/论文搜索专业版.md` |
| ↳ | | | | Find academic papers across up to 7 sources (OpenAlex / Semantic Scholar / CrossRef / PubMed / arXiv for English, plus native-Chinese retrie… |
| `academic-reference-enhancer` | 6.1K | ✓ | format.intext-cite(member)、literature.fact-check(member) | `skills/literature/academic-reference-enhancer.md` |
| ↳ | | | | Add, verify, format, and insert academic references for papers, thesis chapters, technical reports, stage reports, Markdown, Word, LaTeX, PD… |
| `adaptyv` | 3.7K | ✓ | — | `skills/literature/adaptyv.md` |
| ↳ | | | | Cloud laboratory platform for automated protein testing and validation. Use when designing proteins and needing experimental validation incl… |
| `agbm-alphagbm-bps-backtest` | 1.3K |  | — | `skills/literature/agbm-alphagbm-bps-backtest.md` |
| ↳ | | | | Put-spread Backtest reference method. Use when studying this focused method, not to run an API request. External API-key access for its lega… |
| `agbm-alphagbm-chokepoint` | 1.3K |  | — | `skills/literature/agbm-alphagbm-chokepoint.md` |
| ↳ | | | | Supply-chain Bottlenecks reference method. Use when studying this focused method, not to run an API request. External API-key access for its… |
| `agbm-alphagbm-earnings-crush` | 1.3K |  | — | `skills/literature/agbm-alphagbm-earnings-crush.md` |
| ↳ | | | | Earnings IV Crush reference method. Use when studying this focused method, not to run an API request. External API-key access for its legacy… |
| `agbm-alphagbm-greeks` | 1.3K |  | — | `skills/literature/agbm-alphagbm-greeks.md` |
| ↳ | | | | Greeks reference method. Use when studying this focused method, not to run an API request. External API-key access for its legacy endpoints … |
| `agbm-alphagbm-hedge-advisor` | 1.3K |  | — | `skills/literature/agbm-alphagbm-hedge-advisor.md` |
| ↳ | | | | Hedging Scenarios reference method. Use when studying this focused method, not to run an API request. External API-key access for its legacy… |
| `agbm-alphagbm-market-sentiment` | 1.3K |  | — | `skills/literature/agbm-alphagbm-market-sentiment.md` |
| ↳ | | | | Market Sentiment reference method. Use when studying this focused method, not to run an API request. External API-key access for its legacy … |
| `agbm-alphagbm-options-research` | 3.4K |  | — | `skills/literature/agbm-alphagbm-options-research.md` |
| ↳ | | | | Compare option candidates and score components, with funding, expiry and assignment risks. Use when the user asks to options strategies with… |
| `agbm-alphagbm-options-strategy` | 1.3K |  | — | `skills/literature/agbm-alphagbm-options-strategy.md` |
| ↳ | | | | Strategy Builder reference method. Use when studying this focused method, not to run an API request. External API-key access for its legacy … |
| `agbm-alphagbm-pnl-simulator` | 1.3K |  | — | `skills/literature/agbm-alphagbm-pnl-simulator.md` |
| ↳ | | | | Payoff Simulation reference method. Use when studying this focused method, not to run an API request. External API-key access for its legacy… |
| `agbm-alphagbm-polymarket` | 1.3K |  | — | `skills/literature/agbm-alphagbm-polymarket.md` |
| ↳ | | | | Prediction Markets reference method. Use when studying this focused method, not to run an API request. External API-key access for its legac… |
| `agbm-alphagbm-report-breakdown` | 3.3K |  | — | `skills/literature/agbm-alphagbm-report-breakdown.md` |
| ↳ | | | | Extract report views, ratings, key assumptions and risks with sources and dates. Use when the user asks to research report breakdown with Al… |
| `agbm-alphagbm-research-reader` | 3.8K |  | — | `skills/literature/agbm-alphagbm-research-reader.md` |
| ↳ | | | | Find published research and institutional views with sources, dates and related assets. Use when the user asks to research reports with Alph… |
| `agbm-alphagbm-stock-research` | 3.0K |  | — | `skills/literature/agbm-alphagbm-stock-research.md` |
| ↳ | | | | Connect fundamentals, sentiment and risk to supporting and opposing evidence. Use when the user asks to stock opportunities with AlphaGBM. U… |
| `agbm-alphagbm-unusual-activity` | 1.3K |  | — | `skills/literature/agbm-alphagbm-unusual-activity.md` |
| ↳ | | | | Unusual Options Activity reference method. Use when studying this focused method, not to run an API request. External API-key access for its… |
| `agbm-alphagbm-vol-smile` | 1.3K |  | — | `skills/literature/agbm-alphagbm-vol-smile.md` |
| ↳ | | | | Volatility Smile reference method. Use when studying this focused method, not to run an API request. External API-key access for its legacy … |
| `agbm-alphagbm-vol-surface` | 1.3K |  | — | `skills/literature/agbm-alphagbm-vol-surface.md` |
| ↳ | | | | Volatility Surface reference method. Use when studying this focused method, not to run an API request. External API-key access for its legac… |
| `airs-ara-compiler` | 14.9K | ✓ | — | `skills/literature/airs-ara-compiler.md` |
| ↳ | | | | Compiles any research input — PDF papers, GitHub repositories, experiment logs, code directories, or raw notes — into a complete Agent-Nativ… |
| `airs-chroma` | 9.4K | ✓ | — | `skills/literature/airs-chroma.md` |
| ↳ | | | | Open-source embedding database for AI applications. Store embeddings and metadata, perform vector and full-text search, filter by metadata. … |
| `airs-faiss` | 5.2K |  | — | `skills/literature/airs-faiss.md` |
| ↳ | | | | Facebook's library for efficient similarity search and clustering of dense vectors. Supports billions of vectors, GPU acceleration, and vari… |
| `airs-fine-tuning-with-trl` | 11.7K | ✓ | — | `skills/literature/airs-fine-tuning-with-trl.md` |
| ↳ | | | | Fine-tune LLMs using reinforcement learning with TRL - SFT for instruction tuning, DPO for preference alignment, PPO/GRPO for reward optimiz… |
| `airs-huggingface-tokenizers` | 14.0K |  | — | `skills/literature/airs-huggingface-tokenizers.md` |
| ↳ | | | | Fast tokenizers optimized for research and production. Rust-based implementation tokenizes 1GB in <20 seconds. Supports BPE, WordPiece, and … |
| `airs-pinecone` | 8.1K | ✓ | — | `skills/literature/airs-pinecone.md` |
| ↳ | | | | Managed vector database for production AI applications. Fully managed, auto-scaling, with hybrid search (dense + sparse), metadata filtering… |
| `airs-simpo-training` | 6.1K | ✓ | — | `skills/literature/airs-simpo-training.md` |
| ↳ | | | | Simple Preference Optimization for LLM alignment. Reference-free alternative to DPO with better performance (+6.4 points on AlpacaEval 2.0).… |
| `alphafold-database` | 16.1K | ✓ | — | `skills/literature/alphafold-database.md` |
| ↳ | | | | Access AlphaFold 200M+ AI-predicted protein structures. Retrieve structures by UniProt ID, download PDB/mmCIF files, analyze confidence metr… |
| `arf-explain-diff` | 8.3K |  | — | `skills/literature/arf-explain-diff.md` |
| ↳ | | | | Explain a code change as a standalone offline HTML page with a five-question quiz. Reads the diff and the surrounding code from scratch, sta… |
| `arf-pdf-to-markdown` | 7.3K | ✓ | literature.close-read(member) | `skills/literature/arf-pdf-to-markdown.md` |
| ↳ | | | | Split a PDF into chunks and convert it to readable markdown text. Use when the user wants to read, extract, or convert a PDF document. |
| `aris-alphaxiv` | 9.2K | ✓ | literature.close-read(member) | `skills/literature/aris-alphaxiv.md` |
| ↳ | | | | Quick single-paper lookup via AlphaXiv LLM-optimized summaries with tiered source fallback. Use when user says "explain this paper", "summar… |
| `aris-citation-crosscheck` | 38.5K | ✓ | literature.fact-check(member) | `skills/literature/aris-citation-crosscheck.md` |
| ↳ | | | | Conditionally double-blind bibliographic cross-check (double-blind only when the host can isolate the web agent; a flag-only heuristic when … |
| `aris-deepxiv` | 8.4K | ✓ | — | `skills/literature/aris-deepxiv.md` |
| ↳ | | | | Search and progressively read open-access academic papers through DeepXiv. Use when the user wants layered paper access, section-level readi… |
| `aris-exa-search` | 8.0K | ✓ | — | `skills/literature/aris-exa-search.md` |
| ↳ | | | | AI-powered web search via Exa with content extraction. Use when user says "exa search", "web search with content", "find similar pages", or … |
| `aris-keenable-search` | 6.3K | ✓ | — | `skills/literature/aris-keenable-search.md` |
| ↳ | | | | Keyless web search and page fetch via Keenable. Use when user says "keenable search", "web search without an API key", "fetch this page as m… |
| `aris-prior-art-search` | 5.6K | ✓ | — | `skills/literature/aris-prior-art-search.md` |
| ↳ | | | | Search patent databases and academic literature for prior art relevant to an invention. Use when user says \"现有技术检索\", \"prior art search\",… |
| `aris-semantic-scholar` | 11.0K | ✓ | literature.citation-chase(member) | `skills/literature/aris-semantic-scholar.md` |
| ↳ | | | | Search published venue papers (IEEE, ACM, Springer, etc.) via Semantic Scholar API. Complements /arxiv (preprints) with citation counts, ven… |
| `ars-deep-research` | 52.1K | ✓ | literature.screen-prisma(member)、literature.critique(member)、literature.evidence-matrix(member)、literature.synthesis(member)、literature.meta-extract(member) | `skills/literature/ars-deep-research.md` |
| ↳ | | | | Universal deep research agent team. 13-agent pipeline for rigorous academic research on any topic. 8 modes: full research, quick brief, pape… |
| `ars-sr-screener` | 33.6K | ✓ | literature.search-log(member)、literature.screen-prisma(member)、literature.evidence-matrix(member) | `skills/literature/ars-sr-screener.md` |
| ↳ | | | | Protocol-driven study screening for systematic, scoping and rapid reviews. Turns a proposal or PROSPERO protocol into confirmed eligibility … |
| `bgpt-paper-search` | 2.9K | ✓ | — | `skills/literature/bgpt-paper-search.md` |
| ↳ | | | | Search scientific papers and retrieve structured experimental data extracted from full-text studies via the BGPT MCP server. Returns 25+ fie… |
| `bindingdb-database` | 11.9K | ✓ | — | `skills/literature/bindingdb-database.md` |
| ↳ | | | | Query BindingDB for measured drug-target binding affinities (Ki, Kd, IC50, EC50). Search by target (UniProt ID), compound (SMILES/name), or … |
| `biomed-literature-pipeline` | 16.4K | ✓ | literature.search-log(member)、literature.screen-prisma(member) | `skills/literature/biomed-literature-pipeline.md` |
| ↳ | | | | 全生物医学领域文献调研流水线（不限专业）。当用户需要「检索某专业/某方向近几年的文献」「系统梳理某疾病/某技术的研究前沿」「批量下载文献全文」「生成带标题与 DOI 的 Excel 文献清单」「找未来研究方向」时使用。支持：① 引导式确认检索方向（任意临床/基础医学专业，中英文均… |
| `biopython` | 13.6K | ✓ | — | `skills/literature/biopython.md` |
| ↳ | | | | Comprehensive molecular biology toolkit. Use for sequence manipulation, file parsing (FASTA/GenBank/PDB), phylogenetics, and programmatic NC… |
| `biorxiv-database` | 12.4K | ✓ | — | `skills/literature/biorxiv-database.md` |
| ↳ | | | | Efficient database search tool for bioRxiv preprint server. Use this skill when searching for life sciences preprints by keywords, authors, … |
| `bioservices` | 9.8K | ✓ | — | `skills/literature/bioservices.md` |
| ↳ | | | | Unified Python interface to 40+ bioinformatics services. Use when querying multiple databases (UniProt, KEGG, ChEMBL, Reactome) in a single … |
| `brenda-database` | 21.7K | ✓ | — | `skills/literature/brenda-database.md` |
| ↳ | | | | Access BRENDA enzyme database via SOAP API. Retrieve kinetic parameters (Km, kcat), reaction equations, organism data, and substrate-specifi… |
| `caveman-explore` | 2.0K | ✓ | — | `skills/literature/caveman-explore.md` |
| ↳ | | | | Read-only repository explorer for cold-start orientation, broad cross-file localization, or when a direct search failed. Skip it when the ex… |
| `caveman-help` | 2.8K | ✓ | — | `skills/literature/caveman-help.md` |
| ↳ | | | | Quick-reference card for the three caveman skills and their commands. Trigger: /caveman-help or "caveman help". |
| `caveman-stats` | 2.0K |  | — | `skills/literature/caveman-stats.md` |
| ↳ | | | | Show recorded output and cache-read token usage and mode attribution for the current Claude Code session, or locate the host's native usage … |
| `cellxgene-census` | 15.2K | ✓ | — | `skills/literature/cellxgene-census.md` |
| ↳ | | | | Query the CELLxGENE Census (61M+ cells) programmatically. Use when you need expression data across tissues, diseases, or cell types from the… |
| `chembl-database` | 10.1K | ✓ | — | `skills/literature/chembl-database.md` |
| ↳ | | | | Query ChEMBL bioactive molecules and drug discovery data. Search compounds by structure/properties, retrieve bioactivity data (IC50, Ki), fi… |
| `citation-management` | 31.9K | ✓ | literature.library-dedup(member) | `skills/literature/citation-management.md` |
| ↳ | | | | Comprehensive citation management for academic research. Search Google Scholar and PubMed for papers, extract accurate metadata, validate ci… |
| `citation-manager` | 30.6K | ✓ | format.ref-style(member)、format.ref-bridge(member)、literature.library-dedup(member) | `skills/literature/citation-manager.md` |
| ↳ | | | | Add real references and standardize citations for research papers and theses. Supports CrossRef integration, multiple citation formats (APA/… |
| `clinical-decision-copilot` | 17.1K | ✓ | — | `skills/literature/clinical-decision-copilot.md` |
| ↳ | | | | 临床诊疗思路助手。当用户给出症状、体征、化验或影像结果，需要「下一步查什么 / 怎么判读 / 用什么药 / 处方怎么写（含剂量、频次、静脉输液速度、微量泵如何配置与泵速）/ 要不要手术 / 要不要做侵入性检查 / 怎么监测 / 何时升级降级」时使用。**核心内容层是 skill … |
| `clinicaltrials-database` | 14.7K | ✓ | — | `skills/literature/clinicaltrials-database.md` |
| ↳ | | | | Query ClinicalTrials.gov via API v2. Search trials by condition, drug, location, status, or phase. Retrieve trial details by NCT ID, export … |
| `clinpgx-database` | 20.5K | ✓ | — | `skills/literature/clinpgx-database.md` |
| ↳ | | | | Access ClinPGx pharmacogenomics data (successor to PharmGKB). Query gene-drug interactions, CPIC guidelines, allele functions, for precision… |
| `clinvar-database` | 13.0K | ✓ | — | `skills/literature/clinvar-database.md` |
| ↳ | | | | Query NCBI ClinVar for variant clinical significance. Search by gene/position, interpret pathogenicity classifications, access via E-utiliti… |
| `cosmic-database` | 9.9K | ✓ | — | `skills/literature/cosmic-database.md` |
| ↳ | | | | Access COSMIC cancer mutation database. Query somatic mutations, Cancer Gene Census, mutational signatures, gene fusions, for cancer researc… |
| `deep-research` | 9.5K | ✓ | literature.synthesis(member) | `skills/literature/deep-research.md` |
| ↳ | | | | Runs a deep, survey-grade literature investigation on a research topic: freezes research questions, searches from multiple adversarial persp… |
| `discord-reader` | 7.5K | ✓ | — | `skills/literature/discord-reader.md` |
| ↳ | | | | Read Discord for financial research through opencli connected to the Discord desktop app: servers, channels, members, recent messages in the… |
| `dnanexus-integration` | 10.5K | ✓ | — | `skills/literature/dnanexus-integration.md` |
| ↳ | | | | DNAnexus cloud genomics platform. Build apps/applets, manage data (upload/download), dxpy Python SDK, run workflows, FASTQ/BAM/VCF, for geno… |
| `drugbank-database` | 9.3K | ✓ | — | `skills/literature/drugbank-database.md` |
| ↳ | | | | Access and analyze comprehensive drug information from the DrugBank database including drug properties, interactions, targets, pathways, che… |
| `duckdb-attach-db` | 4.9K | ✓ | — | `skills/literature/duckdb-attach-db.md` |
| ↳ | | | | Attach a DuckDB database file for use with /duckdb-skills:query. Explores the schema (tables, columns, row counts) and writes a SQL state fi… |
| `duckdb-docs` | 5.6K |  | — | `skills/literature/duckdb-docs.md` |
| ↳ | | | | Search DuckDB and DuckLake documentation and blog posts. Returns relevant doc chunks for a question or keyword using full-text search agains… |
| `duckdb-query` | 8.0K | ✓ | — | `skills/literature/duckdb-query.md` |
| ↳ | | | | Run SQL queries against the attached DuckDB database or ad-hoc against files. Accepts raw SQL or natural language questions. Uses DuckDB Fri… |
| `duckdb-read-file` | 3.7K | ✓ | — | `skills/literature/duckdb-read-file.md` |
| ↳ | | | | Read any data file (CSV, JSON, Parquet, Avro, Excel, spatial, SQLite) or remote URL (S3, HTTPS). Use when user references a data file, asks … |
| `duckdb-read-memories` | 1.5K | ✓ | — | `skills/literature/duckdb-read-memories.md` |
| ↳ | | | | Search past Claude Code session logs to recall prior decisions, patterns, or unresolved work. Use when user says "do you remember", "what di… |
| `duckdb-s3-explore` | 3.5K | ✓ | — | `skills/literature/duckdb-s3-explore.md` |
| ↳ | | | | Explore and query data on S3, Cloudflare R2, GCS, MinIO, or any S3-compatible storage. Use when the user mentions an s3://, r2://, gs://, or… |
| `earnings-recap` | 7.1K | ✓ | — | `skills/literature/earnings-recap.md` |
| ↳ | | | | Analyze a company's most recent (or a specified past) earnings report from Yahoo Finance data (yfinance): actual vs estimated EPS, surprise … |
| `ena-database` | 6.9K | ✓ | — | `skills/literature/ena-database.md` |
| ↳ | | | | Access European Nucleotide Archive via API/FTP. Retrieve DNA/RNA sequences, raw reads (FASTQ), genome assemblies by accession, for genomics … |
| `ensembl-database` | 8.1K | ✓ | — | `skills/literature/ensembl-database.md` |
| ↳ | | | | Query Ensembl genome database REST API for 250+ species. Gene lookups, sequence retrieval, variant analysis, comparative genomics, orthologs… |
| `evidence-driven-writing` | 3.8K | ✓ | — | `skills/literature/evidence-driven-writing.md` |
| ↳ | | | | Use when writing or revising Introduction, Related Work, background, literature synthesis, or any section where references must drive claims |
| `fda-database` | 14.2K | ✓ | — | `skills/literature/fda-database.md` |
| ↳ | | | | Query openFDA API for drugs, devices, adverse events, recalls, regulatory submissions (510k, PMA), substance identification (UNII), for FDA … |
| `finance-sentiment` | 5.3K |  | — | `skills/literature/finance-sentiment.md` |
| ↳ | | | | Fetch normalized stock sentiment across Reddit, X.com, financial news, and Polymarket from the Adanos Finance API: buzz score, bullish perce… |
| `find-paper-references` | 12.8K | ✓ | format.intext-cite(member) | `skills/literature/find-paper-references.md` |
| ↳ | | | | 自动为学术论文 Markdown 文件查找参考文献。读取论文全文，识别每个需要引用的知识点（流行病学数据、机制描述、已有研究结论等），为每个知识点通过 PubMed 检索 3-5 篇最相关文献，在原文句末插入 [PMID:XXXXXXXX] 标记，并生成独立的候选参考文献列表文件… |
| `format-references-endnote` | 5.8K | ✓ | format.ref-bridge(member) | `skills/literature/format-references-endnote.md` |
| ↳ | | | | EndNote 版文献排版工作流 — 将 Markdown 手稿中的 [PMID: xxxx] 标记转换为 Word (.docx)，使用 EndNote CWYW 识别的 {Author, Year, Title} 占位符，同时生成 .ris 文件自动导入本地 EndNote … |
| `gene-database` | 6.3K | ✓ | — | `skills/literature/gene-database.md` |
| ↳ | | | | Query NCBI Gene via E-utilities/Datasets API. Search by symbol/ID, retrieve gene info (RefSeqs, GO, locations, phenotypes), batch lookups, f… |
| `geo-database` | 24.0K | ✓ | — | `skills/literature/geo-database.md` |
| ↳ | | | | Access NCBI GEO for gene expression/genomics data. Search/download microarray and RNA-seq datasets (GSE, GSM, GPL), retrieve SOFT/Matrix fil… |
| `gget` | 24.5K | ✓ | — | `skills/literature/gget.md` |
| ↳ | | | | Fast CLI/Python queries to 20+ bioinformatics databases. Use for quick lookups: gene info, BLAST searches, AlphaFold structures, enrichment … |
| `gm-muapi-photo-pack-generator` | 4.1K | ✓ | — | `skills/literature/gm-muapi-photo-pack-generator.md` |
| ↳ | | | | Generate a pack of professional or aesthetic photos from a single reference image while preserving the exact identity of the person. |
| `gm-muapi-seedance-2` | 27.2K | ✓ | — | `skills/literature/gm-muapi-seedance-2.md` |
| ↳ | | | | Expert Cinema Director skill for Seedance 2.0 (ByteDance) — high-fidelity video generation across Chinese, Global, and VIP tiers. Supports t… |
| `gm-muapi-social-media-video` | 11.6K | ✓ | — | `skills/literature/gm-muapi-social-media-video.md` |
| ↳ | | | | Brand-aware social media video creator. Reads brand-identity.md, ICP.md, and messaging.md to write a post/storyboard, craft an optimized See… |
| `gm-muapi-storyboard-to-cooking-video` | 8.8K | ✓ | — | `skills/literature/gm-muapi-storyboard-to-cooking-video.md` |
| ↳ | | | | Turn a single photo of a person into a 15-second cinematic pasta-making (or other cuisine) tutorial video. First builds a composite referenc… |
| `gnomad-database` | 12.3K | ✓ | — | `skills/literature/gnomad-database.md` |
| ↳ | | | | Query gnomAD (Genome Aggregation Database) for population allele frequencies, variant constraint scores (pLI, LOEUF), and loss-of-function i… |
| `gtex-database` | 10.8K | ✓ | — | `skills/literature/gtex-database.md` |
| ↳ | | | | Query GTEx (Genotype-Tissue Expression) portal for tissue-specific gene expression, eQTLs (expression quantitative trait loci), and sQTLs. E… |
| `gwas-database` | 19.7K | ✓ | — | `skills/literature/gwas-database.md` |
| ↳ | | | | Query NHGRI-EBI GWAS Catalog for SNP-trait associations. Search variants by rs ID, disease/trait, gene, retrieve p-values and summary statis… |
| `hedgefundmonitor` | 6.7K |  | — | `skills/literature/hedgefundmonitor.md` |
| ↳ | | | | Query the OFR (Office of Financial Research) Hedge Fund Monitor API for hedge fund data including SEC Form PF aggregated statistics, CFTC Tr… |
| `hmdb-database` | 7.9K | ✓ | — | `skills/literature/hmdb-database.md` |
| ↳ | | | | Access Human Metabolome Database (220K+ metabolites). Search by name/ID/structure, retrieve chemical properties, biomarker data, NMR/MS spec… |
| `hyperliquid-reader` | 9.5K |  | — | `skills/literature/hyperliquid-reader.md` |
| ↳ | | | | Read Hyperliquid (app.hyperliquid.xyz) perp and spot market data through opencli and Hyperliquid's public info API: mark, oracle, and mid pr… |
| `ima-skill` | 15.8K | ✓ | — | `skills/literature/ima-skill.md` |
| ↳ | | | | 统一的 IMA OpenAPI 技能，支持笔记管理和知识库操作。 当用户提到知识库、资料库、笔记、备忘录、记事，或者想要上传文件、添加网页到知识库、 搜索知识库内容、搜索/浏览/创建/编辑笔记时，使用此 skill。 即使用户没有明确说"知识库"或"笔记"，只要意图涉及文件上传到… |
| `imaging-data-commons` | 33.7K | ✓ | — | `skills/literature/imaging-data-commons.md` |
| ↳ | | | | Query and download public cancer imaging data from NCI Imaging Data Commons using idc-index. Use for accessing large-scale radiology (CT, MR… |
| `interpro-database` | 10.6K | ✓ | — | `skills/literature/interpro-database.md` |
| ↳ | | | | Query InterPro for protein family, domain, and functional site annotations. Integrates Pfam, PANTHER, PRINTS, SMART, SUPERFAMILY, and 11 oth… |
| `kegg-database` | 11.6K | ✓ | — | `skills/literature/kegg-database.md` |
| ↳ | | | | Direct REST API access to KEGG (academic use only). Pathway analysis, gene-pathway mapping, metabolic pathways, drug interactions, ID conver… |
| `lamindb` | 14.1K |  | — | `skills/literature/lamindb.md` |
| ↳ | | | | This skill should be used when working with LaminDB, an open-source data framework for biology that makes data queryable, traceable, reprodu… |
| `linkedin-reader` | 6.7K | ✓ | — | `skills/literature/linkedin-reader.md` |
| ↳ | | | | Read LinkedIn for financial research through opencli: the user's feed, and job search with location, seniority, job type, remote, company, a… |
| `literature-close-read` | 7.4K | ✓ | literature.close-read(member) | `skills/literature/literature-close-read.md` |
| ↳ | | | | Produce a structured close-reading report from a paper's full PDF-to-Markdown text (with `## Page XX` pagination and image references) when … |
| `literature-review` | 23.3K | ✓ | literature.search-log(member)、literature.screen-prisma(member)、literature.critique(member)、literature.evidence-matrix(member)、literature.meta-extract(member)、literature.citation-chase(member) | `skills/literature/literature-review.md` |
| ↳ | | | | Conduct comprehensive, systematic literature reviews using multiple academic databases (PubMed, arXiv, bioRxiv, Semantic Scholar, etc.). Thi… |
| `matchms` | 6.9K |  | — | `skills/literature/matchms.md` |
| ↳ | | | | Spectral similarity and compound identification for metabolomics. Use for comparing mass spectra, computing similarity scores (cosine, modif… |
| `medical-imaging-review` | 4.5K | ✓ | — | `skills/literature/medical-imaging-review.md` |
| ↳ | | | | Write comprehensive literature reviews for medical imaging AI research. Use when writing survey papers, systematic reviews, or literature an… |
| `medical-review-writer` | 5.1K | ✓ | literature.critique(member)、literature.synthesis(member) | `skills/literature/medical-review-writer.md` |
| ↳ | | | | 专门用于快速完成医学综述的工作流引擎。只要用户需求涉及“写医学综述”“写文献综述”“基于 PubMed 写 review”或类似任务，请直接使用本技能。此版本只保留快速模式：大纲构建 → 主题总检索 → 连续写作 → 章节校验 → 合并定稿 → 引用格式化。 Do NOT tri… |
| `metabolomics-workbench-database` | 10.2K | ✓ | — | `skills/literature/metabolomics-workbench-database.md` |
| ↳ | | | | Access NIH Metabolomics Workbench via REST API (4,200+ studies). Query metabolites, RefMet nomenclature, MS/NMR data, m/z searches, study me… |
| `monarch-database` | 12.6K | ✓ | — | `skills/literature/monarch-database.md` |
| ↳ | | | | Query the Monarch Initiative knowledge graph for disease-gene-phenotype associations across species. Integrates OMIM, ORPHANET, HPO, ClinVar… |
| `nature-academic-search` | 3.6K | ✓ | — | `skills/literature/nature-academic-search.md` |
| ↳ | | | | Search literature across sources, verify or manage citations, and build MeSH strategies or citation-impact audits. Use for 文献检索、引文核对、参考文献管理、… |
| `nature-citation` | 3.1K | ✓ | — | `skills/literature/nature-citation.md` |
| ↳ | | | | Find and verify Nature/CNS-family literature supporting manuscript claims, with claim-to-source mapping and reference-manager export. Use fo… |
| `nature-downloader` | 23.8K | ✓ | — | `skills/literature/nature-downloader.md` |
| ↳ | | | | Use when a user needs lawful academic full text, CNKI institutional access, English OA retrieval, publisher API access, institutional browse… |
| `nature-literature-pipeline` | 4.8K | ✓ | literature.search-log(member) | `skills/literature/nature-literature-pipeline.md` |
| ↳ | | | | Complete automated literature discovery pipeline: multi-source search → six-dimension scoring → fine reading → formatted delivery → archival… |
| `nature-paper-card` | 8.2K | ✓ | literature.close-read(member) | `skills/literature/nature-paper-card.md` |
| ↳ | | | | Build a structured deep-reading Paper Card for one scientific paper, analysing methods, experiment-to-claim evidence, limitations, and resea… |
| `nature-ref-verifier` | 9.6K | ✓ | literature.fact-check(member) | `skills/literature/nature-ref-verifier.md` |
| ↳ | | | | 对学术文献逐条执行多源交叉验证，逐字段对比作者、标题、年份、卷期、页码， 标记卷年/DOI年冲突、作者顺序异常、页码偏差等问题，输出结构化验证报告。 可批量处理整篇论文/开题报告的参考文献列表，也可单条校验，支持与 Zotero 同步修正。 |
| `networkx` | 12.5K | ✓ | — | `skills/literature/networkx.md` |
| ↳ | | | | Comprehensive toolkit for creating, analyzing, and visualizing complex networks and graphs in Python. Use when working with network/graph da… |
| `openalex-database` | 11.9K | ✓ | literature.citation-chase(member) | `skills/literature/openalex-database.md` |
| ↳ | | | | Query and analyze scholarly literature using the OpenAlex database. This skill should be used when searching for academic papers, analyzing … |
| `opentargets-database` | 13.8K | ✓ | — | `skills/literature/opentargets-database.md` |
| ↳ | | | | Query Open Targets Platform for target-disease associations, drug target discovery, tractability/safety data, genetics/omics evidence, known… |
| `paper-reference-formatter` | 3.4K | ✓ | format.ref-style(member) | `skills/literature/paper-reference-formatter.md` |
| ↳ | | | | Format academic reference entries from user-provided journal article, thesis/dissertation, conference paper, book, report, preprint, or web … |
| `parallel-web` | 11.4K | ✓ | — | `skills/literature/parallel-web.md` |
| ↳ | | | | Search the web, extract URL content, and run deep research using the Parallel Chat API and Extract API. Use for ALL web searches, research q… |
| `pdb-database` | 9.1K | ✓ | — | `skills/literature/pdb-database.md` |
| ↳ | | | | Access RCSB PDB for 3D protein/nucleic acid structures. Search by text/sequence/structure, download coordinates (PDB/mmCIF), retrieve metada… |
| `pdf` | 7.9K | ✓ | — | `skills/literature/pdf.md` |
| ↳ | | | | Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining o… |
| `perplexity-search` | 13.8K | ✓ | — | `skills/literature/perplexity-search.md` |
| ↳ | | | | Perform AI-powered web searches with real-time information using Perplexity models via LiteLLM and OpenRouter. This skill should be used whe… |
| `ponytail` | 3.2K |  | — | `skills/literature/ponytail.md` |
| ↳ | | | | Lazy senior dev mode for any coding task: the smallest change that fully solves it, and a reply a busy human understands in one read. |
| `ponytail-help` | 3.2K | ✓ | — | `skills/literature/ponytail-help.md` |
| ↳ | | | | Quick reference for ponytail's modes, skills, and commands. One-shot display. |
| `pubchem-database` | 16.0K | ✓ | — | `skills/literature/pubchem-database.md` |
| ↳ | | | | Query PubChem via PUG-REST API/PubChemPy (110M+ compounds). Search by name/CID/SMILES, retrieve properties, similarity/substructure searches… |
| `pubmed-database` | 15.3K | ✓ | literature.pico-query(member) | `skills/literature/pubmed-database.md` |
| ↳ | | | | Direct REST API access to PubMed. Advanced Boolean/MeSH queries, E-utilities API, batch processing, citation management. For Python workflow… |
| `pytdc` | 12.5K |  | — | `skills/literature/pytdc.md` |
| ↳ | | | | Therapeutics Data Commons. AI-ready drug discovery datasets (ADME, toxicity, DTI), benchmarks, scaffold splits, molecular oracles, for thera… |
| `pyzotero` | 4.4K | ✓ | format.ref-bridge(member)、literature.library-dedup(member) | `skills/literature/pyzotero.md` |
| ↳ | | | | Interact with Zotero reference management libraries using the pyzotero Python client. Retrieve, create, update, and delete items, collection… |
| `qinyan-citation` | 6.8K | ✓ | format.ref-style(member) | `skills/literature/qinyan-citation.md` |
| ↳ | | | | 沁言学术文献引用 - 先通过沁言学术OpenAPI检索文献，然后按照GB/T 7714、IEEE、APA、MLA、Chicago、Harvard等标准格式输出引用参考文献。严格遵循学术规范，未获取的信息保留省略号。触发词：文献引用、参考文献、引用格式、citation、refer… |
| `qinyan-paper-search` | 5.6K | ✓ | literature.pico-query(member) | `skills/literature/qinyan-paper-search.md` |
| ↳ | | | | 沁言学术文献检索 - 支持从 Google Scholar、万方(Wanfang)、PubMed、ArXiv 四大学术数据库检索文献。智能选择检索策略：中文优先万方、英文优先Google Scholar、医学类优先PubMed、理工计算机类优先ArXiv。使用沁言学术OpenAP… |
| `qutip` | 8.9K |  | — | `skills/literature/qutip.md` |
| ↳ | | | | Quantum physics simulation library for open quantum systems. Use when studying master equations, Lindblad dynamics, decoherence, quantum opt… |
| `rare-disease-diagnosis` | 7.2K | ✓ | — | `skills/literature/rare-disease-diagnosis.md` |
| ↳ | | | | 通用疑难病文献诊断专家（覆盖全部临床科室）。结合患者症状、体征、辅助检查提取精准英文医学关键词，检索 PubMed/Google Scholar 等 SCI 数据库，为各科疑难罕见病提供循证鉴别诊断线索，并生成中文文献综述。适用于：任何专科（神经、心血管、呼吸、消化、风湿免疫、血… |
| `reactome-database` | 7.7K | ✓ | — | `skills/literature/reactome-database.md` |
| ↳ | | | | Query Reactome REST API for pathway analysis, enrichment, gene-pathway mapping, disease pathways, molecular interactions, expression analysi… |
| `reference-retrieval-skill` | 5.5K | ✓ | literature.pico-query(member) | `skills/literature/reference-retrieval-skill.md` |
| ↳ | | | | 根据用户输入的中文或英文意图，直接根据需求查找相关文献，或自动构建PubMed布尔检索式，检索并筛选适合引用的参考文献。适用于快速寻找特定主题的高质量文献证据及补全引用。 |
| `reference-verification` | 7.6K | ✓ | literature.fact-check(member) | `skills/literature/reference-verification.md` |
| ↳ | | | | 参考文献真伪核验技能。针对论文、研究报告、课题资料等学术文件，系统性地识别并核验全部参考文献条目的真实性。适用于：用户上传/提供论文/报告需要验证参考文献、怀疑文献存在编造或信息错误、毕业论文查重附带文献核查、课题结题验收前文献核实等场景。当用户提出"核验参考文献"、"验证文献真… |
| `research` | 4.2K |  | — | `skills/literature/research.md` |
| ↳ | | | | Conduct preliminary research on a topic and generate research outline. For academic research, benchmark research, technology selection, etc. |
| `research-add-fields` | 0.9K |  | — | `skills/literature/research-add-fields.md` |
| ↳ | | | | Add field definitions to existing research outline. |
| `research-add-items` | 0.8K |  | — | `skills/literature/research-add-items.md` |
| ↳ | | | | Add items (research objects) to existing research outline. |
| `research-deep` | 3.3K | ✓ | — | `skills/literature/research-deep.md` |
| ↳ | | | | Read research outline, launch independent agent for each item for deep research. Disable task output. |
| `research-report` | 3.8K |  | — | `skills/literature/research-report.md` |
| ↳ | | | | Summarize deep research results into markdown report, cover all fields, skip uncertain values. |
| `rowan` | 12.3K |  | — | `skills/literature/rowan.md` |
| ↳ | | | | Cloud-based quantum chemistry platform with Python API. Preferred for computational chemistry workflows including pKa prediction, geometry o… |
| `saas-valuation-compression` | 7.2K |  | — | `skills/literature/saas-valuation-compression.md` |
| ↳ | | | | Analyze how a private SaaS company's ARR valuation multiple changed across funding rounds, and attribute the compression or expansion to rat… |
| `scholar-auto-research` | 83.4K | ✓ | — | `skills/literature/scholar-auto-research.md` |
| ↳ | | | | Stable, deterministic social-science research-paper pipeline from idea or data to verified manuscript, citations, replication package, and f… |
| `scholar-citation` | 34.9K | ✓ | format.intext-cite(member) | `skills/literature/scholar-citation.md` |
| ↳ | | | | Full citation management for social science manuscripts. Eight modes: (1) INSERT — add in-text citations to uncited claims; (2) AUDIT — find… |
| `scholar-data` | 91.5K | ✓ | — | `skills/literature/scholar-data.md` |
| ↳ | | | | Comprehensive open data directory (100+ datasets across 14 categories) with auto-fetch capability, plus data collection instrument design, v… |
| `scholar-lit-review` | 56.9K | ✓ | literature.synthesis(member) | `skills/literature/scholar-lit-review.md` |
| ↳ | | | | Conduct a systematic literature review that maps the current landscape of a research question. Produces a structured literature landscape ma… |
| `scholar-monitor` | 45.9K | ✓ | literature.citation-chase(member) | `skills/literature/scholar-monitor.md` |
| ↳ | | | | Current-awareness literature monitoring for social sciences. Tracks new publications from top journals (ASR, AJS, Demography, Social Forces,… |
| `scholar-rag` | 29.2K | ✓ | literature.library-dedup(member) | `skills/literature/scholar-rag.md` |
| ↳ | | | | Build and query a local vector database + GraphRAG over your entire reference library (Zotero or a PDF folder) for literature review. Downlo… |
| `SCI-Writing-Master` | 81.6K | ✓ | — | `skills/literature/sci-writing-master.md` |
| ↳ | | | | 顶级 SCI 医学论文写作与润色 skill。基于 249+ 篇近五年 Lancet/JAMA/NEJM/BMJ/Cell/Nature 级 顶刊论文逐篇精读提炼，覆盖 19 种论文类型的写作标准（§1–§19；其中 §19.11 危重症七大治疗域、 §19.12 ICU 支持治… |
| `Self-Improving + Proactive Agent` | 8.5K | ✓ | — | `skills/literature/self-improving-proactive-agent.md` |
| ↳ | | | | Self-reflection + Self-criticism + Self-learning + Self-organizing memory. Agent evaluates its own work, catches mistakes, and improves perm… |
| `skill-creator` | 15.1K | ✓ | — | `skills/literature/skill-creator.md` |
| ↳ | | | | Create, improve, and evaluate agent skills (SKILL.md plus reference files). Use this skill whenever the user wants to build, scaffold, or de… |
| `stock-correlation` | 13.4K |  | — | `skills/literature/stock-correlation.md` |
| ↳ | | | | Analyze how stocks move together using Yahoo Finance price history (yfinance): find correlated peers for a ticker, measure correlation, beta… |
| `stock-liquidity` | 19.6K |  | — | `skills/literature/stock-liquidity.md` |
| ↳ | | | | Analyze how liquid a stock is using Yahoo Finance data (yfinance): bid-ask spreads, volume and dollar volume (ADTV), top-of-book and options… |
| `string-database` | 17.9K | ✓ | — | `skills/literature/string-database.md` |
| ↳ | | | | Query STRING API for protein-protein interactions (59M proteins, 20B interactions). Network analysis, GO/KEGG enrichment, interaction discov… |
| `telegram-reader` | 7.8K | ✓ | — | `skills/literature/telegram-reader.md` |
| ↳ | | | | Read Telegram channels and groups for financial news and market research with the tdl CLI: list chats and channels, find a channel by name, … |
| `uniprot-database` | 6.7K | ✓ | — | `skills/literature/uniprot-database.md` |
| ↳ | | | | Direct REST API access to UniProt. Protein searches, FASTA retrieval, ID mapping, Swiss-Prot/TrEMBL. For Python workflows with multiple data… |
| `uspto-database` | 18.3K | ✓ | — | `skills/literature/uspto-database.md` |
| ↳ | | | | Access USPTO APIs for patent/trademark searches, examination history (PEDS), assignments, citations, office actions, TSDR, for IP analysis a… |
| `writing-law` | 4.7K | ✓ | — | `skills/literature/writing-law.md` |
| ↳ | | | | Use when writing law papers - provides legal writing conventions, citation formats, and argumentation guidance |
| `zinc-database` | 13.6K | ✓ | — | `skills/literature/zinc-database.md` |
| ↳ | | | | Access ZINC (230M+ purchasable compounds). Search by ZINC ID/SMILES, similarity searches, 3D-ready structures for docking, analog discovery,… |

## 格式与交付（32）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `airs-gguf-quantization` | 10.6K | ✓ | — | `skills/format/airs-gguf-quantization.md` |
| ↳ | | | | GGUF format and llama.cpp quantization for efficient CPU/GPU inference. Use when deploying models on consumer hardware, Apple Silicon, or wh… |
| `airs-guidance` | 14.8K | ✓ | — | `skills/format/airs-guidance.md` |
| ↳ | | | | Control LLM output with regex and grammars, guarantee valid JSON/XML/code generation, enforce structured formats, and build multi-step workf… |
| `airs-quantizing-models-bitsandbytes` | 10.4K | ✓ | — | `skills/format/airs-quantizing-models-bitsandbytes.md` |
| ↳ | | | | Quantizes LLMs to 8-bit or 4-bit for 50-75% memory reduction with minimal accuracy loss. Use when GPU memory is limited, need to fit larger … |
| `airs-systems-paper-writing` | 14.4K | ✓ | — | `skills/format/airs-systems-paper-writing.md` |
| ↳ | | | | Comprehensive guide for writing systems papers targeting OSDI, SOSP, ASPLOS, NSDI, and EuroSys. Provides paragraph-level structural blueprin… |
| `anndata` | 10.0K | ✓ | — | `skills/format/anndata.md` |
| ↳ | | | | Data structure for annotated matrices in single-cell analysis. Use when working with .h5ad files or integrating with the scverse ecosystem. … |
| `arf-paper-version` | 15.9K | ✓ | — | `skills/format/arf-paper-version.md` |
| ↳ | | | | Convert a LaTeX research paper into a policy brief, 1-page summary, or 5-page summary for a general audience, with factual review and a stan… |
| `ars-academic-paper` | 64.5K | ✓ | — | `skills/format/ars-academic-paper.md` |
| ↳ | | | | 12-agent academic paper writing pipeline. 11 modes (full/plan/outline/revision/revision-coach/abstract/lit-review/format-convert/citation-ch… |
| `denario` | 5.9K | ✓ | — | `skills/format/denario.md` |
| ↳ | | | | Multiagent AI system for scientific research assistance that automates research workflows from data analysis to publication. This skill shou… |
| `docx` | 19.3K | ✓ | format.figtable(member)、format.final-delivery(member) | `skills/format/docx--docx.md` |
| ↳ | | | | 当用户想要创建、读取、编辑或操作 Word 文档（.docx 文件）时，始终使用本技能。触发情形包括：任何提及 'Word doc'、'word document'、'.docx'，或请求生成带目录、标题、页码或信头等格式的专业文档。也用于从 .docx 文件中提取或重组内容、在… |
| `docx` | 19.7K | ✓ | format.figtable(member)、format.final-delivery(member) | `skills/format/docx.md` |
| ↳ | | | | Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of '… |
| `duckdb-convert-file` | 3.0K | ✓ | — | `skills/format/duckdb-convert-file.md` |
| ↳ | | | | Convert any data file to another format: CSV, Parquet, JSON, Excel, GeoJSON, and more. Use when the user says "convert to parquet", "save as… |
| `format-references-zotero` | 7.3K | ✓ | format.ref-bridge(member) | `skills/format/format-references-zotero.md` |
| ↳ | | | | Zotero 版文献排版工作流。将 Markdown 手稿中的 [PMID: xxxx] 标记转换为 Word (.docx)，直接写入原生 Zotero 域代码（ADDIN ZOTERO_ITEM / ADDIN ZOTERO_BIBL），用户在 Word 中点一次「Refre… |
| `lab-report-writer` | 9.4K | ✓ | — | `skills/format/lab-report-writer.md` |
| ↳ | | | | Generate complete, template-aware lab reports for any course from experiment task books, related files, report templates, sample finished re… |
| `latchbio-integration` | 9.7K | ✓ | — | `skills/format/latchbio-integration.md` |
| ↳ | | | | Latch platform for bioinformatics workflows. Build pipelines with Latch SDK, @workflow/@task decorators, deploy serverless workflows, LatchF… |
| `latex-output` | 5.5K | ✓ | format.final-delivery(member) | `skills/format/latex-output.md` |
| ↳ | | | | Use when user requests LaTeX format output or has provided school/journal LaTeX templates |
| `market-research-reports` | 28.2K | ✓ | — | `skills/format/market-research-reports.md` |
| ↳ | | | | Generate comprehensive market research reports (50+ pages) in the style of top consulting firms (McKinsey, BCG, Gartner). Features professio… |
| `markitdown` | 12.4K | ✓ | format.final-delivery(member) | `skills/format/markitdown.md` |
| ↳ | | | | Convert files and office documents to Markdown. Supports PDF, DOCX, PPTX, XLSX, images (with OCR), audio (with transcription), HTML, CSV, JS… |
| `minimax-xlsx` | 8.5K | ✓ | — | `skills/format/minimax-xlsx.md` |
| ↳ | | | | Open, create, read, analyze, edit, or validate Excel/spreadsheet files (.xlsx, .xlsm, .csv, .tsv). Use when the user asks to create, build, … |
| `openmaic-convert-pptx__skillhub` | 8.5K | ✓ | — | `skills/format/openmaic-convert-pptx.md` |
| `paper-2-web` | 16.1K | ✓ | — | `skills/format/paper-2-web.md` |
| ↳ | | | | This skill should be used when converting academic papers into promotional and presentation formats including interactive websites (Paper2We… |
| `pdfkit-py` | 41.1K | ✓ | — | `skills/format/pdfkit-py.md` |
| ↳ | | | | 仅用于对已存在的 .pdf 文件进行处理（读取/提取/编辑/合并/拆分/转换/水印/加密/OCR/表单/签名）。当且仅当用户输入或工作区中存在 .pdf 文件，且操作对象是该 PDF 时使用。不处理 docx/xlsx/pptx/html/md/txt/图片等非 PDF 文件，不… |
| `pptx-posters` | 13.9K | ✓ | — | `skills/format/pptx-posters.md` |
| ↳ | | | | Create research posters using HTML/CSS that can be exported to PDF or PPTX. Use this skill ONLY when the user explicitly requests PowerPoint… |
| `pydicom` | 12.9K | ✓ | figures.image(member) | `skills/format/pydicom.md` |
| ↳ | | | | Python library for working with DICOM (Digital Imaging and Communications in Medicine) files. Use this skill when reading, writing, or modif… |
| `rdkit` | 20.0K | ✓ | — | `skills/format/rdkit.md` |
| ↳ | | | | Cheminformatics toolkit for fine-grained molecular control. SMILES/SDF parsing, descriptors (MW, LogP, TPSA), fingerprints, substructure sea… |
| `sepa-strategy` | 12.6K | ✓ | — | `skills/format/sepa-strategy.md` |
| ↳ | | | | Analyze stocks with Mark Minervini's SEPA (Specific Entry Point Analysis) methodology: stage analysis, the 8-condition trend template, funda… |
| `sp-receiving-code-review` | 6.3K | ✓ | — | `skills/format/sp-receiving-code-review.md` |
| ↳ | | | | Use when receiving code review feedback, before implementing suggestions, especially if feedback seems unclear or technically questionable -… |
| `thesis-format-zh` | 2.1K | ✓ | — | `skills/format/thesis-format-zh.md` |
| ↳ | | | | 中文论文格式检查工具。解析学校模板docx，提取格式规则，对比论文生成差异报告。支持页边距/标题/正文/页眉/页码/三线表/引用格式检查。触发词：论文排版、格式检查、Word格式、毕业论文。 |
| `tiledbvcf` | 15.1K |  | — | `skills/format/tiledbvcf.md` |
| ↳ | | | | Efficient storage and retrieval of genomic variant data using TileDB. Scalable VCF/BCF ingestion, incremental sample addition, compressed st… |
| `treatment-plans` | 51.5K | ✓ | — | `skills/format/treatment-plans.md` |
| ↳ | | | | Generate concise (3-4 page), focused medical treatment plans in LaTeX/PDF format for all clinical specialties. Supports general medical trea… |
| `typst-paper` | 14.3K | ✓ | format.final-delivery(member) | `skills/format/typst-paper.md` |
| ↳ | | | | Typst paper assistant for existing .typ manuscripts in English or Chinese. Use for compile/export diagnosis, venue formatting, BibTeX/Hayagr… |
| `venue-templates` | 22.8K | ✓ | format.figtable(member)、format.journal-fit(member) | `skills/format/venue-templates.md` |
| ↳ | | | | Access comprehensive LaTeX templates, formatting requirements, and submission guidelines for major scientific publication venues (Nature, Sc… |
| `xlsx` | 8.8K | ✓ | literature.evidence-matrix(member) | `skills/format/xlsx.md` |
| ↳ | | | | Full lifecycle for Excel files: create workbooks with formulas and formatting, build charts and pivot tables, read and clean data, batch-edi… |

## 通用（不进融合，仅编目）（88）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `agbm-alphagbm-dividend-strategy` | 2.6K |  | — | `skills/general/agbm-alphagbm-dividend-strategy.md` |
| ↳ | | | | Score Hong Kong and China A-share dividend candidates across yield quality, durability, cash flow, valuation and momentum. Use when the user… |
| `agbm-alphagbm-etf-strategy` | 2.5K |  | — | `skills/general/agbm-alphagbm-etf-strategy.md` |
| ↳ | | | | Score ETF trend, risk, liquidity, cost and available tracking and theme signals while preserving data gaps. Use when the user asks to etf st… |
| `agbm-alphagbm-iv-rank` | 1.2K |  | — | `skills/general/agbm-alphagbm-iv-rank.md` |
| ↳ | | | | Volatility Snapshot via the published AlphaGBM interface. Use for this focused function, not as a promise that every website API accepts API… |
| `agbm-alphagbm-momentum-following` | 2.5K |  | — | `skills/general/agbm-alphagbm-momentum-following.md` |
| ↳ | | | | Score observed price trend, confirmation, risk and participation without forecasting a price. Use when the user asks to momentum following w… |
| `agbm-alphagbm-options-score` | 1.2K |  | — | `skills/general/agbm-alphagbm-options-score.md` |
| ↳ | | | | Options Score via the published AlphaGBM interface. Use for this focused function, not as a promise that every website API accepts API keys. |
| `airs-audiocraft-audio-generation` | 16.6K |  | — | `skills/general/airs-audiocraft-audio-generation.md` |
| ↳ | | | | PyTorch library for audio generation including text-to-music (MusicGen) and text-to-sound (AudioGen). Use when you need to generate music fr… |
| `airs-autogpt-agents` | 9.6K |  | — | `skills/general/airs-autogpt-agents.md` |
| ↳ | | | | Autonomous AI agent platform for building and deploying continuous agents. Use when creating visual workflow agents, deploying persistent au… |
| `airs-constitutional-ai` | 8.4K |  | — | `skills/general/airs-constitutional-ai.md` |
| ↳ | | | | Anthropic's method for training harmless AI through self-improvement. Two-phase approach - supervised learning with self-critique/revision, … |
| `airs-crewai-multi-agent` | 13.7K |  | — | `skills/general/airs-crewai-multi-agent.md` |
| ↳ | | | | Multi-agent orchestration framework for autonomous AI collaboration. Use when building teams of specialized agents working together on compl… |
| `airs-deepspeed` | 141.8K |  | — | `skills/general/airs-deepspeed.md` |
| ↳ | | | | Expert guidance for distributed training with DeepSpeed - ZeRO optimization stages, pipeline parallelism, FP16/BF16/FP8, 1-bit Adam, sparse … |
| `airs-dspy` | 15.6K |  | — | `skills/general/airs-dspy.md` |
| ↳ | | | | Build complex AI systems with declarative programming, optimize prompts automatically, create modular RAG systems and agents with DSPy - Sta… |
| `airs-evolving-ai-agents` | 14.7K |  | — | `skills/general/airs-evolving-ai-agents.md` |
| ↳ | | | | Provides guidance for automatically evolving and optimizing AI agents across any domain using LLM-driven evolution algorithms. Use when buil… |
| `airs-experiment-tracking-swanlab` | 10.0K |  | — | `skills/general/airs-experiment-tracking-swanlab.md` |
| ↳ | | | | Provides guidance for experiment tracking with SwanLab. Use when you need open-source run tracking, local or self-hosted dashboards, and lig… |
| `airs-huggingface-accelerate` | 8.6K |  | — | `skills/general/airs-huggingface-accelerate.md` |
| ↳ | | | | Simplest distributed training API. 4 lines to add distributed support to any PyTorch script. Unified API for DeepSpeed/FSDP/Megatron/DDP. Au… |
| `airs-instructor` | 17.2K |  | — | `skills/general/airs-instructor.md` |
| ↳ | | | | Extract structured data from LLM responses with Pydantic validation, retry failed extractions automatically, parse complex JSON with type sa… |
| `airs-langchain` | 13.1K |  | — | `skills/general/airs-langchain.md` |
| ↳ | | | | Framework for building LLM-powered applications with agents, chains, and RAG. Supports multiple providers (OpenAI, Anthropic, Google), 500+ … |
| `airs-llamaindex` | 15.0K |  | — | `skills/general/airs-llamaindex.md` |
| ↳ | | | | Data framework for building LLM applications with RAG. Specializes in document ingestion (300+ connectors), indexing, and querying. Features… |
| `airs-ml-training-recipes` | 11.3K |  | — | `skills/general/airs-ml-training-recipes.md` |
| ↳ | | | | Battle-tested PyTorch training recipes for all domains — LLMs, vision, diffusion, medical imaging, protein/drug discovery, spatial omics, ge… |
| `airs-nanogpt` | 6.9K |  | — | `skills/general/airs-nanogpt.md` |
| ↳ | | | | Educational GPT implementation in ~300 lines. Reproduces GPT-2 (124M) on OpenWebText. Clean, hackable code for learning transformers. By And… |
| `airs-phoenix-observability` | 11.8K |  | — | `skills/general/airs-phoenix-observability.md` |
| ↳ | | | | Open-source AI observability platform for LLM tracing, evaluation, and monitoring. Use when debugging LLM applications with detailed traces,… |
| `airs-pytorch-lightning` | 9.3K |  | — | `skills/general/airs-pytorch-lightning.md` |
| ↳ | | | | High-level PyTorch framework with Trainer class, automatic distributed training (DDP/FSDP/DeepSpeed), callbacks system, and minimal boilerpl… |
| `airs-sentencepiece` | 5.8K |  | — | `skills/general/airs-sentencepiece.md` |
| ↳ | | | | Language-independent tokenizer treating text as raw Unicode. Supports BPE and Unigram algorithms. Fast (50k sentences/sec), lightweight (6MB… |
| `airs-skypilot-multi-cloud-orchestration` | 10.0K |  | — | `skills/general/airs-skypilot-multi-cloud-orchestration.md` |
| ↳ | | | | Multi-cloud orchestration for ML workloads with automatic cost optimization. Use when you need to run training or batch jobs across multiple… |
| `airs-unsloth` | 2.4K |  | — | `skills/general/airs-unsloth.md` |
| ↳ | | | | Expert guidance for fast fine-tuning with Unsloth - 2-5x faster training, 50-80% less memory, LoRA/QLoRA optimization |
| `airs-verl-rl-training` | 10.5K |  | — | `skills/general/airs-verl-rl-training.md` |
| ↳ | | | | Provides guidance for training LLMs with reinforcement learning using verl (Volcano Engine RL). Use when implementing RLHF, GRPO, PPO, or ot… |
| `alpha-vantage` | 6.2K |  | — | `skills/general/alpha-vantage.md` |
| ↳ | | | | Access real-time and historical stock market data, forex rates, cryptocurrency prices, commodities, economic indicators, and 50+ technical i… |
| `aris-analyze-results` | 1.7K |  | — | `skills/general/aris-analyze-results.md` |
| ↳ | | | | Analyze ML experiment results, compute statistics, generate comparison tables and insights. Use when user says \"analyze results\", \"compar… |
| `benchling-integration` | 12.8K |  | — | `skills/general/benchling-integration.md` |
| ↳ | | | | Benchling R&D platform integration. Access registry (DNA, proteins), inventory, ELN entries, workflows via API, build Benchling Apps, query … |
| `brand` | 3.9K |  | — | `skills/general/brand.md` |
| ↳ | | | | Brand voice, visual identity, messaging frameworks, asset management, brand consistency. Activate for branded content, tone of voice, market… |
| `caveman-commit` | 2.4K |  | — | `skills/general/caveman-commit.md` |
| ↳ | | | | Write a Conventional Commits message compressed to intent only. Use for "write a commit", "commit message", /commit or /caveman-commit. |
| `caveman-discover` | 5.2K |  | — | `skills/general/caveman-discover.md` |
| ↳ | | | | Find and label every LLM workflow in the repository so Caveman Cloud groups spend by workflow instead of one bucket. Use for "discover workf… |
| `caveman-manage` | 3.9K |  | — | `skills/general/caveman-manage.md` |
| ↳ | | | | Inspect Caveman Cloud's experiment lifecycle and block unsafe execution. Use when asked to start, approve, cancel, promote or roll back a Ca… |
| `caveman-setup` | 10.3K |  | — | `skills/general/caveman-setup.md` |
| ↳ | | | | Wire a repository through the Caveman Cloud gateway so every LLM request is measured, with no behavior change. Use for "set up caveman" or a… |
| `company-valuation` | 13.2K |  | — | `skills/general/company-valuation.md` |
| ↳ | | | | Estimate a public company's intrinsic value with DCF, relative (peer multiple), and sum-of-the-parts (SOTP) methods, then blend them into an… |
| `d1g-macro-liquidity` | 14.8K |  | — | `skills/general/d1g-macro-liquidity.md` |
| ↳ | | | | Macro liquidity monitoring and risk early-warning system. By tracking 4 core indicators (Fed Net Liquidity, SOFR Overnight Financing Rate, M… |
| `d1g-us-market-sentiment` | 10.2K |  | — | `skills/general/d1g-us-market-sentiment.md` |
| ↳ | | | | US stock market sentiment monitoring and position recommendation system. Evaluates market sentiment by tracking 5 core indicators (NAAIM Exp… |
| `duckdb-install-duckdb` | 2.5K |  | — | `skills/general/duckdb-install-duckdb.md` |
| ↳ | | | | Install or update DuckDB extensions. Each argument is either a plain extension name (installs from core) or name@repo (e.g. magic@community)… |
| `etf-premium` | 20.8K |  | — | `skills/general/etf-premium.md` |
| ↳ | | | | Calculate an ETF's premium or discount to NAV from Yahoo Finance data (yfinance), compare or screen ETFs by premium, explain why a gap exist… |
| `fintel-data` | 8.8K |  | — | `skills/general/fintel-data.md` |
| ↳ | | | | Query Fintel (fintel.io) institutional market data through its REST API or official MCP server. Use this skill whenever the user mentions Fi… |
| `ginkgo-cloud-lab` | 3.5K |  | — | `skills/general/ginkgo-cloud-lab.md` |
| ↳ | | | | Submit and manage protocols on Ginkgo Bioworks Cloud Lab (cloud.ginkgo.bio), a web-based interface for autonomous lab execution on Reconfigu… |
| `github-skill-installer` | 11.4K |  | — | `skills/general/github-skill-installer.md` |
| ↳ | | | | 从 GitHub 仓库直接安装 Agent Skill 到 WorkBuddy 用户级技能目录（~/.workbuddy/skills/）。当用户给出 GitHub 地址（https://github.com/owner/repo）或 owner/repo 并要求"从这个仓库安装… |
| `gm-muapi-3d-logo-animation` | 2.8K |  | — | `skills/general/gm-muapi-3d-logo-animation.md` |
| ↳ | | | | Transform a 2D logo into a premium 3D version and animate it with professional cinematic effects. |
| `gm-muapi-animal-video-generator` | 3.5K |  | — | `skills/general/gm-muapi-animal-video-generator.md` |
| ↳ | | | | Create a hilarious and ultra-realistic video of an anthropomorphic animal acting like a human vlogger in a real-world setting. |
| `gm-muapi-award-ceremony-video` | 8.2K |  | — | `skills/general/gm-muapi-award-ceremony-video.md` |
| ↳ | | | | Generate a 15-second cinematic awards-ceremony video — a host announces a winner from the stage, a spotlight finds them in the crowd, they w… |
| `gm-muapi-brand-kit` | 3.9K |  | — | `skills/general/gm-muapi-brand-kit.md` |
| ↳ | | | | Generate a cohesive brand visual kit — logo concept, color palette moodboard, and typography pairing suggestions. |
| `gm-muapi-couple-grid-creator` | 2.5K |  | — | `skills/general/gm-muapi-couple-grid-creator.md` |
| ↳ | | | | Create a stylized 6-box grid featuring a couple in various romantic poses and outfits, with each pose framed inside a unique cardboard box p… |
| `gm-muapi-drone-style-video` | 3.4K |  | — | `skills/general/gm-muapi-drone-style-video.md` |
| ↳ | | | | Generate aerial drone-perspective footage — sweeping bird's-eye views, orbit shots, and flyover sequences for landscapes, architecture, and … |
| `gm-muapi-freeze-effect-video` | 5.1K |  | — | `skills/general/gm-muapi-freeze-effect-video.md` |
| ↳ | | | | Generate a cinematic "freeze effect" video where time stops mid-scene, the subject walks through the frozen world, then time resumes with a … |
| `gm-muapi-giant-product-showcase` | 3.2K |  | — | `skills/general/gm-muapi-giant-product-showcase.md` |
| ↳ | | | | Create a dramatic "Giant Product" visual where a regular item is showcased as a massive, building-sized object next to a person, then option… |
| `gm-muapi-jewelry-product-video` | 3.3K |  | — | `skills/general/gm-muapi-jewelry-product-video.md` |
| ↳ | | | | Create a luxury jewelry advertisement with high-end commercial cinematography and detailed macro animation. |
| `gm-muapi-keyboard-art-maker` | 2.1K |  | — | `skills/general/gm-muapi-keyboard-art-maker.md` |
| ↳ | | | | Generate artistic top-down photos of keyboard keycaps arranged to spell out custom text messages. |
| `gm-muapi-multi-angle-reshoot` | 4.0K |  | — | `skills/general/gm-muapi-multi-angle-reshoot.md` |
| ↳ | | | | Re-render a subject or scene from multiple dramatic camera angles, such as fish-eye, bird's-eye, low-angle, and macro, while maintaining con… |
| `gm-muapi-music-video` | 2.7K |  | — | `skills/general/gm-muapi-music-video.md` |
| ↳ | | | | Build a short music video from a song theme — N keyframes, animate each, generate matching music. |
| `gm-muapi-one-shot-video` | 2.7K |  | — | `skills/general/gm-muapi-one-shot-video.md` |
| ↳ | | | | Generate a single continuous cinematic shot video — no cuts, one seamless flowing scene with dramatic lighting and motion. |
| `gm-muapi-product-ad-cinematic` | 3.4K |  | — | `skills/general/gm-muapi-product-ad-cinematic.md` |
| ↳ | | | | Cinematic 5–10s product ad from a product photo + brand brief. |
| `gm-muapi-product-campaign` | 4.6K |  | — | `skills/general/gm-muapi-product-campaign.md` |
| ↳ | | | | Generate a full multi-channel product campaign — hero visuals, social media assets, short ad video, and platform-specific crops for an end-t… |
| `gm-muapi-product-showcase-video` | 3.1K |  | — | `skills/general/gm-muapi-product-showcase-video.md` |
| ↳ | | | | Create a dynamic product showcase with explosive ingredient arrangements, followed by a realistic motion animation. |
| `gm-muapi-product-video-ad-maker` | 2.9K |  | — | `skills/general/gm-muapi-product-video-ad-maker.md` |
| ↳ | | | | Create a high-end cinematic product video advertisement starting from a simple product photo. |
| `gm-muapi-selfie-with-celebrities` | 3.9K |  | — | `skills/general/gm-muapi-selfie-with-celebrities.md` |
| ↳ | | | | Generate a realistic behind-the-scenes selfie of the user with a celebrity or main actor from a specific movie, followed by an option to gen… |
| `gm-muapi-youtube-shorts` | 6.1K |  | — | `skills/general/gm-muapi-youtube-shorts.md` |
| ↳ | | | | Auto-generate viral 9:16 YouTube Shorts (or TikTok / Reels clips) from a long-form video. Thin platform-aware wrapper around the AI Clipping… |
| `Illustrator` | 1.8K |  | — | `skills/general/illustrator.md` |
| ↳ | | | | Control Adobe Illustrator from the shell via Flue - ExtendScript bridges without an MCP server. |
| `lean-build` | 1.1K |  | — | `skills/general/lean-build.md` |
| ↳ | | | | Build feature work with high overbuilding risk. Use for new behavior, product slices, or integrations where repository reuse, strict scope, … |
| `medchem` | 10.0K |  | — | `skills/general/medchem.md` |
| ↳ | | | | Medicinal chemistry filters. Apply drug-likeness rules (Lipinski, Veber), PAINS filters, structural alerts, complexity metrics, for compound… |
| `megacave` | 2.8K |  | — | `skills/general/megacave.md` |
| ↳ | | | | Caveman in Classical Chinese: 文言文 register, far fewer characters, technical terms verbatim. Invoke only with /megacave or /caveman wenyan. S… |
| `migration` | 0.8K |  | — | `skills/general/migration.md` |
| ↳ | | | | Implement reversible compatibility-safe transitions. Use for schema, data, API, protocol, configuration, or dependency migrations requiring … |
| `nature-experiment-log` | 6.3K |  | — | `skills/general/nature-experiment-log.md` |
| ↳ | | | | 标准化实验日志记录——直接上传或读取本地图片、语音和文字，产出带 YAML frontmatter 的 Markdown；可选集成飞书 CLI 与 Obsidian。 |
| `ponytail-debt` | 1.8K |  | — | `skills/general/ponytail-debt.md` |
| ↳ | | | | Harvest every shortcut: comment into one debt ledger, so deferrals get tracked instead of forgotten. One-shot report. |
| `ponytail-gain` | 2.2K |  | — | `skills/general/ponytail-gain.md` |
| ↳ | | | | Show ponytail measured impact as a scoreboard: less code, less cost, more speed, from the agentic benchmark averages. One-shot display. |
| `qiskit` | 8.6K |  | — | `skills/general/qiskit.md` |
| ↳ | | | | IBM quantum computing framework. Use when targeting IBM Quantum hardware, working with Qiskit Runtime for production workloads, or needing I… |
| `safe-refactor` | 0.8K |  | — | `skills/general/safe-refactor.md` |
| ↳ | | | | Restructure code while preserving behavior. Use for extraction, consolidation, ownership moves, or cleanup where verification must bracket s… |
| `scroll-world` | 48.4K |  | — | `skills/general/scroll-world.md` |
| ↳ | | | | Build an immersive scroll-scrubbed "fly through the world" landing page for any industry or brand using Higgsfield. As the visitor scrolls, … |
| `skill-zip-installer` | 4.1K |  | — | `skills/general/skill-zip-installer.md` |
| ↳ | | | | 从本地 zip 包安装 Skill 到 WorkBuddy 用户级目录（~/.workbuddy/skills/），包含安全审计、 名称规范化、依赖安装与冒烟验证的完整流程。当用户提供 skill 压缩包（.zip）并要求 "安装这些 skill""装上这个技能包""instal… |
| `sp-diagnosing-superpowers` | 7.0K |  | — | `skills/general/sp-diagnosing-superpowers.md` |
| ↳ | | | | Use when a superpowers session went wrong and your human partner wants to know why — repeated work, ignored plans, stumbles, poor results, a… |
| `sp-dispatching-parallel-agents` | 6.2K |  | — | `skills/general/sp-dispatching-parallel-agents.md` |
| ↳ | | | | Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies |
| `sp-executing-plans` | 18.1K |  | — | `skills/general/sp-executing-plans.md` |
| ↳ | | | | Use when executing an implementation plan in the current session as the implementer yourself — your human partner chose inline execution, or… |
| `sp-finishing-a-development-branch` | 7.9K |  | — | `skills/general/sp-finishing-a-development-branch.md` |
| ↳ | | | | Use when implementation is complete, all tests pass, and you need to decide how to integrate the work |
| `sp-subagent-driven-development` | 19.5K |  | — | `skills/general/sp-subagent-driven-development.md` |
| ↳ | | | | Use when executing implementation plans with independent tasks in the current session |
| `sp-systematic-debugging` | 9.7K |  | — | `skills/general/sp-systematic-debugging.md` |
| ↳ | | | | Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes |
| `sp-using-git-worktrees` | 6.9K |  | — | `skills/general/sp-using-git-worktrees.md` |
| ↳ | | | | Use when starting feature work that needs isolation from current workspace or before executing implementation plans - ensures an isolated wo… |
| `sp-using-superpowers` | 3.3K |  | — | `skills/general/sp-using-superpowers.md` |
| ↳ | | | | Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarif… |
| `sp-verification-before-completion` | 3.8K |  | — | `skills/general/sp-verification-before-completion.md` |
| ↳ | | | | Use when about to claim work is complete, fixed, or passing, before committing or creating PRs - requires running verification commands and … |
| `summarize` | 2.6K |  | — | `skills/general/summarize.md` |
| ↳ | | | | 智能内容摘要工具，支持长文本、文档、网页内容自动摘要，提取核心要点、关键词，支持自定义摘要长度。 |
| `surgical-patch` | 0.7K |  | — | `skills/general/surgical-patch.md` |
| ↳ | | | | Fix bugs and small behavior changes at the narrowest responsible layer. Use when regression proof, preserved surrounding behavior, and task-… |
| `sympy` | 13.2K |  | — | `skills/general/sympy.md` |
| ↳ | | | | Use this skill when working with symbolic mathematics in Python. This skill should be used for symbolic computation tasks including solving … |
| `torch-geometric` | 20.0K |  | — | `skills/general/torch-geometric.md` |
| ↳ | | | | Graph Neural Networks (PyG). Node/graph classification, link prediction, GCN, GAT, GraphSAGE, heterogeneous graphs, molecular property predi… |
| `ultracave` | 2.5K |  | — | `skills/general/ultracave.md` |
| ↳ | | | | Caveman at maximum compression: fragments, one word when one word is enough, each fact once. Invoke only with /ultracave or /caveman ultra. … |
| `usfiscaldata` | 7.2K |  | — | `skills/general/usfiscaldata.md` |
| ↳ | | | | Query the U.S. Treasury Fiscal Data API for federal financial data including national debt, government spending, revenue, interest rates, ex… |
| `web-access` | 18.6K |  | — | `skills/general/web-access.md` |
| ↳ | | | | 所有联网操作必须通过此 skill 处理，包括：搜索、网页抓取、登录后操作、网络交互等。 触发场景：用户要求搜索信息、查看网页内容、访问需要登录的网站、操作网页界面、抓取社交媒体内容（小红书、微博、推特等）、读取动态渲染页面、以及任何需要真实浏览器环境的网络任务。 |
