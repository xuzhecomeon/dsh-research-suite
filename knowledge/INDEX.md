# 技能索引（全量编目）

本文件由 `scripts/build-index.mjs` 从 `knowledge/catalog.json` 与 `data/capabilities/*.json` 生成，
是**目录层**的索引：告诉你包里到底有哪些技能、每题正文在哪、被哪张能力卡引用。

- 想知道“这个任务该怎么做”：走 `research_playbook`，看**能力卡**，不要在本索引里挑技能。
- 想知道某个技能原文：`research_kb_read(name="<技能名>")`，按 `file` 列的相对路径读取。
- 本索引只在“同名近似技能到底哪个更全”这类**证据等级**问题上使用。

合计 450 条源记录（去重后 444 个技能目录：6 组同目录重复记录各计一条），科研相关 450 条，分布在 10 个能力域 + 1 个工具箱索引桶；
被能力卡引用 237 个，其余仅编目留档。

## 域目录

| 域 | 技能数 | 科研相关 | 被能力卡引用 | 对应技能文件 |
|---|---:|---:|---:|---|
| 论文撰写 | 64 | 64 | 34 | `skills/research-writing.md` |
| 润色与去 AI 痕迹 | 12 | 12 | 12 | `skills/research-polish.md` |
| 科研绘图 | 33 | 33 | 22 | `skills/research-figures.md` |
| 科研统计 | 30 | 30 | 22 | `skills/research-stats.md` |
| 科研思路与标书 | 37 | 37 | 21 | `skills/research-ideation.md` |
| 审稿与修回 | 20 | 20 | 18 | `skills/research-review.md` |
| 科研汇报与 PPT | 37 | 37 | 19 | `skills/research-slides.md` |
| 文献与引文 | 26 | 26 | 20 | `skills/research-literature.md` |
| 格式与交付 | 51 | 51 | 41 | `skills/research-format.md` |
| 数据获取与组学 | 40 | 40 | 29 | `skills/research-data.md` |
| 工具箱（索引桶，不建能力卡） | 100 | 100 | 7 | — |

## 论文撰写（64）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `aris-deepxiv` | 8.3K | ✓ | — | `skills/writing/aris-deepxiv.md` |
| ↳ | | | | Search and progressively read open-access academic papers through DeepXiv. Use when the user wants layered paper access, section-level readi… |
| `aris-paper-plan` | 21.6K | ✓ | — | `skills/writing/aris-paper-plan.md` |
| ↳ | | | | "Generate a structured paper outline from review conclusions and experiment results. Use when user says \"写大纲\", \"paper outline\", \"plan t… |
| `aris-paper-write` | 39.0K | ✓ | — | `skills/writing/aris-paper-write.md` |
| ↳ | | | | "Draft LaTeX paper section by section from an outline. Use when user says \"写论文\", \"write paper\", \"draft LaTeX\", \"开始写\", or wants to ge… |
| `aris-proof-orchestrator` | 18.8K | ✓ | — | `skills/writing/aris-proof-orchestrator.md` |
| ↳ | | | | "Manage a stateful, run-directory-based proof project: continuation across runs, run-local source bookkeeping, manual GPT Pro handoff packag… |
| `aris-proof-writer` | 8.4K | ✓ | — | `skills/writing/aris-proof-writer.md` |
| ↳ | | | | Writes rigorous mathematical proofs for ML/AI theory. Use when asked to prove a theorem, lemma, proposition, or corollary, fill in missing p… |
| `aris-render-html` | 22.7K | ✓ | — | `skills/writing/aris-render-html.md` |
| ↳ | | | | "Render an ARIS Markdown / JSON artifact (IDEA_REPORT, AUTO_REVIEW, KILL_ARGUMENT, PAPER_PLAN, research-wiki state, etc.) into a single-file… |
| `aris-result-to-claim` | 17.8K | ✓ | — | `skills/writing/aris-result-to-claim.md` |
| ↳ | | | | Use when experiments complete to judge what claims the results support, what they don't, and what evidence is still missing. Codex MCP evalu… |
| `ars-academic-paper` | 64.5K | ✓ | writing.blueprint(member) | `skills/writing/ars-academic-paper.md` |
| ↳ | | | | "12-agent academic paper writing pipeline. 11 modes (full/plan/outline/revision/revision-coach/abstract/lit-review/format-convert/citation-c… |
| `benchmark-paper-template` | 11.1K | ✓ | writing.blueprint(member) | `skills/writing/benchmark-paper-template.md` |
| ↳ | | | | Structures Benchmark and Evaluation papers using the five-pillar framework (Research Gap, Construction Pipeline, Evaluation Framework, Empir… |
| `bgpt-paper-search` | 2.8K | ✓ | — | `skills/writing/bgpt-paper-search.md` |
| ↳ | | | | Search scientific papers and retrieve structured experimental data extracted from full-text studies via the BGPT MCP server. Returns 25+ fie… |
| `biomedical-sci-manuscript` | 4.5K | ✓ | — | `skills/writing/biomedical-sci-manuscript.md` |
| ↳ | | | | Create SCI manuscript drafts for biomedical Methods/Results material across three study types: bioinformatics, clinical medicine, and basic … |
| `brainstorming-research` | 10.7K | ✓ | writing.thesis(member) | `skills/writing/brainstorming-research.md` |
| ↳ | | | | Use before writing any paper - clarifies paper type, discipline, topic, methodology, and chapter structure through natural dialogue |
| `chinese-medical-paper-writer` | 29.2K | ✓ | format.intext-cite(member)、format.figtable(member)、format.submission-package(member)、writing.zh-imrad(member)、writing.zh-voice(member)、writing.review(member)、writing.case-report(member)、writing.abstract(member)、writing.figure-table(member)、writing.discussion(member)、writing.citation(member) | `skills/writing/chinese-medical-paper-writer.md` |
| ↳ | | | | 中文医学期刊论文写作助手（chinese-medical-paper-writer）。中文医学期刊论文（中华医学会系列期刊模板）撰写、润色、参考文献规范化与完整投稿包生成。撰写类任务必须先做"前置问答环节"（篇幅、重点论述内容、参考文献数量质量、目标期刊、作者信息），并充分阅读知… |
| `clinical-reports` | 38.8K | ✓ | writing.case-report(member)、writing.submission(member) | `skills/writing/clinical-reports.md` |
| ↳ | | | | Write comprehensive clinical reports including case reports (CARE guidelines), diagnostic reports (radiology/pathology/lab), clinical trial … |
| `clinicaltrials-database` | 14.6K | ✓ | — | `skills/writing/clinicaltrials-database.md` |
| ↳ | | | | Query ClinicalTrials.gov via API v2. Search trials by condition, drug, location, status, or phase. Retrieve trial details by NCT ID, export … |
| `cover-letter` | 11.3K | ✓ | format.submission-package(member)、format.journal-fit(member)、writing.submission(member) | `skills/writing/cover-letter.md` |
| ↳ | | | | Submission cover-letter assistant for existing LaTeX manuscripts. Use to generate, optimize, align-check, preflight, and journal-fit-check c… |
| `evidence-driven-writing` | 3.7K | ✓ | writing.evidence(member) | `skills/writing/evidence-driven-writing.md` |
| ↳ | | | | Use when writing or revising Introduction, Related Work, background, literature synthesis, or any section where references must drive claims |
| `intro-drafter` | 9.7K | ✓ | writing.evidence(member) | `skills/writing/intro-drafter.md` |
| ↳ | | | | >- Drafts the Introduction prose for a technical paper, guided internally by a six-paragraph flowchart: background and running example, exis… |
| `lab-report-writer` | 9.3K | ✓ | — | `skills/writing/lab-report-writer.md` |
| ↳ | | | | Generate complete, template-aware lab reports for any course from experiment task books, related files, report templates, sample finished re… |
| `latex-paper-en` | 19.3K | ✓ | — | `skills/writing/latex-paper-en.md` |
| ↳ | | | | English LaTeX assistant for existing .tex journal or conference papers. Use for compile repair, venue formatting, bibliography/citation chec… |
| `latex-thesis-zh` | 36.9K | ✓ | writing.thesis(member) | `skills/writing/latex-thesis-zh.md` |
| ↳ | | | | 中文 LaTeX 学位论文助手，面向已有 .tex 硕博论文工程与学位论文评阅书：编译诊断、GB/T 7714、模板识别、结构/格式/公式断行、术语一致性、逻辑与文献综述、方法/工程应用章、标题优化、去 AI 味、主张前置（自我削弱/免责句后置）检查、单元润色与漂移核对、盲审隐匿… |
| `library` | 19.0K | ✓ | literature.library(member) | `skills/writing/library.md` |
| ↳ | | | | Route here (资料库/知识库/网盘/空间) when users create, generate, beautify, upload, edit, share, organize (整理/归档/理一理), publish, download, export (导出/下… |
| `literature-monitor-skills` | 12.7K | ✓ | — | `skills/writing/literature-monitor-skills.md` |
| ↳ | | | | Monitor when scholarly articles first become visible to readers on official journal or publisher surfaces—such as ASAP, Online First, Early … |
| `literature-review` | 23.2K | ✓ | literature.screen-prisma(member)、writing.review(member)、writing.citation(member) | `skills/writing/literature-review.md` |
| ↳ | | | | Conduct comprehensive, systematic literature reviews using multiple academic databases (PubMed, arXiv, bioRxiv, Semantic Scholar, etc.). Thi… |
| `literature-review` | 23.2K | ✓ | literature.screen-prisma(member)、writing.review(member)、writing.citation(member) | `skills/writing/literature-review-2.md` |
| ↳ | | | | Conduct comprehensive, systematic literature reviews using multiple academic databases (PubMed, arXiv, bioRxiv, Semantic Scholar, etc.). Thi… |
| `medical-review-writer` | 5.1K | ✓ | writing.review(member) | `skills/writing/medical-review-writer.md` |
| ↳ | | | | 专门用于快速完成医学综述的工作流引擎。只要用户需求涉及“写医学综述”“写文献综述”“基于 PubMed 写 review”或类似任务，请直接使用本技能。此版本只保留快速模式：大纲构建 → 主题总检索 → 连续写作 → 章节校验 → 合并定稿 → 引用格式化。 Do NOT tri… |
| `nature-academic-search` | 3.5K | ✓ | — | `skills/writing/nature-academic-search.md` |
| ↳ | | | | Search literature across sources, verify or manage citations, and build MeSH strategies or citation-impact audits. Use for 文献检索、引文核对、参考文献管理、… |
| `nature-data` | 3.8K | ✓ | writing.submission(member) | `skills/writing/nature-data.md` |
| ↳ | | | | Draft or audit manuscript Data/Code Availability statements, dataset access routes, repository plans, and FAIR metadata. Use for 数据可用性声明、数据共… |
| `nature-paper-to-patent` | 4.5K | ✓ | — | `skills/writing/nature-paper-to-patent.md` |
| ↳ | | | | Turn research papers or inventor materials into evidence-grounded Chinese invention patent drafts and technical disclosures. Use for 技术交底书、专… |
| `nature-shared` | 2.1K | ✓ | — | `skills/writing/nature-shared.md` |
| ↳ | | | | Internal shared-reference support package for installed Nature Skills, including nature-writing, nature-polishing, nature-response, nature-r… |
| `nature-writing` | 8.1K | ✓ | writing.en-sci(member)、writing.journal-profile(member)、writing.discussion(member) | `skills/writing/nature-writing.md` |
| ↳ | | | | Draft or restructure scientific manuscript arguments, sections, and initial-submission materials from author-provided evidence. Use for 论文写作… |
| `paper-2-web` | 16.1K | ✓ | — | `skills/writing/paper-2-web.md` |
| ↳ | | | | This skill should be used when converting academic papers into promotional and presentation formats including interactive websites (Paper2We… |
| `paper-checker` | 3.0K | ✓ | polish.audit(member) | `skills/writing/paper-checker.md` |
| ↳ | | | | 论文查重与AI率检测工具，支持中文英文论文查重、AI率检测、降重和降AI率处理。用于：(1)上传论文文件进行查重和AI率检测 (2)生成详细的重复率和AI率报告 (3)对高重复率内容进行降重改写 (4)对高AI率内容进行降AI率处理。不需要API key，直接能用。 |
| `paper-orchestration` | 6.1K | ✓ | writing.blueprint(member) | `skills/writing/paper-orchestration.md` |
| ↳ | | | | Use when a research-writing task spans multiple sections, medium-sized revisions, full-paper drafting, or repeated quality failures |
| `paper-revision-sop` | 8.0K | ✓ | polish.audit(member)、writing.zh-voice(member) | `skills/writing/paper-revision-sop.md` |
| ↳ | | | | 学术论文润色修改全流程SOP。从审稿意见解析、论文全息诊断、可视化批注生成、分级改写执行到终审自检的完整闭环。当用户需要根据期刊审稿意见修改论文、需要论文润色、需要去AI味、需要学术写作规范检查时触发。典型触发："修改这篇论文""根据审稿意见润色""去AI味""按期刊要求压缩字数… |
| `paper-writer` | 14.0K | ✓ | writing.zh-imrad(member)、writing.en-sci(member)、writing.evidence(member)、writing.blueprint(member) | `skills/writing/paper-writer.md` |
| ↳ | | | | >- Drafts publishable paper prose from the author's own materials, from a single paragraph to a full manuscript, across STEM and non-STEM fi… |
| `paper-writing-studio` | 9.5K | ✓ | writing.journal-profile(member)、writing.figure-table(member) | `skills/writing/paper-writing-studio.md` |
| ↳ | | | | Use this academic writing skill to polish or translate academic writing with an explicit Nature, IEEE, Elsevier, or neutral profile. Selects… |
| `prompts-collection` | 7.4K | ✓ | writing.zh-voice(member)、writing.abstract(member)、writing.figure-table(member) | `skills/writing/prompts-collection.md` |
| ↳ | | | | Use for translation, polishing, or de-AI-ification of academic text - provides ready-to-use prompt templates |
| `qinyan-paper-analysis` | 3.8K | ✓ | — | `skills/writing/qinyan-paper-analysis.md` |
| ↳ | | | | 沁言学术论文分析 - 对单篇学术论文进行深度分析解读，提取研究目标、方法论、主要发现和研究限制。通过沁言学术OpenAPI的analyze接口实现。触发词：论文分析、论文解读、分析论文、paper analysis、analyze paper、论文解析 |
| `research-lookup` | 15.9K | ✓ | — | `skills/writing/research-lookup.md` |
| ↳ | | | | Look up current research information using the Parallel Chat API (primary) or Perplexity sonar-pro-search (academic paper searches). Automat… |
| `research-writing-assistant` | 7.9K | ✓ | — | `skills/writing/research-writing-assistant.md` |
| ↳ | | | | Use when writing academic papers, theses, or research articles - supports brainstorming, chapter writing, literature review, and LaTeX outpu… |
| `scholar-evaluation` | 12.0K | ✓ | — | `skills/writing/scholar-evaluation.md` |
| ↳ | | | | Systematically evaluate scholarly work using the ScholarEval framework, providing structured assessment across research quality dimensions i… |
| `scholar-hypothesis` | 43.7K | ✓ | — | `skills/writing/scholar-hypothesis.md` |
| ↳ | | | | Develop theoretically grounded hypotheses and draft publication-ready Theory sections. Covers puzzle framing (5 types: anomaly, contradictio… |
| `scholar-journal` | 57.7K | ✓ | format.submission-package(member)、format.journal-fit(member)、writing.journal-profile(member)、writing.submission(member) | `skills/writing/scholar-journal.md` |
| ↳ | | | | Format, select, and prepare a manuscript for journal submission. 5 modes: FULL-PACKAGE (structure audit + checklist + cover letter + open sc… |
| `scholar-openai` | 24.0K | ✓ | — | `skills/writing/scholar-openai.md` |
| ↳ | | | | External review via OpenAI Codex CLI agents. Spawns multiple parallel Codex agents (codex exec) to independently review analysis scripts, ve… |
| `scholar-respond` | 63.2K | ✓ | review.revise(member)、review.rebuttal(member)、review.appeal(member) | `skills/writing/scholar-respond.md` |
| ↳ | | | | Simulate peer review, draft point-by-point responses to reviewer comments, revise a manuscript, plan a resubmission to a new journal after r… |
| `scholar-verify` | 28.6K | ✓ | writing.evidence(member) | `skills/writing/scholar-verify.md` |
| ↳ | | | | Two-stage verification of analysis-to-manuscript consistency using a 4-agent panel. Stage 1: Compare raw analysis outputs (CSVs, HTML tables… |
| `scholar-write` | 43.7K | ✓ | — | `skills/writing/scholar-write.md` |
| ↳ | | | | Draft, revise, or polish any section of a social science manuscript — Introduction, Theory, Methods, Results, Discussion, Abstract, or full … |
| `SCI-Writing-Master` | 81.5K | ✓ | writing.en-sci(member)、writing.review(member)、writing.case-report(member)、writing.abstract(member)、writing.discussion(member)、writing.citation(member) | `skills/writing/sci-writing-master.md` |
| ↳ | | | | 顶级 SCI 医学论文写作与润色 skill。基于 249+ 篇近五年 Lancet/JAMA/NEJM/BMJ/Cell/Nature 级 顶刊论文逐篇精读提炼，覆盖 19 种论文类型的写作标准（§1–§19；其中 §19.11 危重症七大治疗域、 §19.12 ICU 支持治… |
| `scientific-graphical-abstract-skill__skillhub` | 4.3K | ✓ | — | `skills/writing/scientific-graphical-abstract-skill.md` |
| `scientific-writing` | 33.0K | ✓ | writing.en-sci(member)、writing.abstract(member)、writing.figure-table(member)、writing.discussion(member) | `skills/writing/scientific-writing.md` |
| ↳ | | | | Core skill for the deep research and writing tool. Write scientific manuscripts in full paragraphs (never bullet points). Use two-stage proc… |
| `scientific-writing` | 33.0K | ✓ | writing.en-sci(member)、writing.abstract(member)、writing.figure-table(member)、writing.discussion(member) | `skills/writing/scientific-writing-2.md` |
| ↳ | | | | Core skill for the deep research and writing tool. Write scientific manuscripts in full paragraphs (never bullet points). Use two-stage proc… |
| `sepia` | 15.0K | ✓ | polish.voice(member) | `skills/writing/sepia.md` |
| ↳ | | | | Make AI-generated writing read as human-written, in fiction and in professional prose. Repairs the narrative architecture of fiction and sto… |
| `style-journal-rewrite` | 5.5K | ✓ | writing.journal-profile(member) | `skills/writing/style-journal-rewrite.md` |
| ↳ | | | | 按目标文风或目标期刊格式改写初稿。用户说"改成XX风格""仿照这个味道""按XX期刊格式整理""参考这篇格式改"时触发。输入可为 .docx / .md / .txt 或对话文本。 |
| `tdoc-orchestrator` | 19.9K | ✓ | — | `skills/writing/tdoc-orchestrator.md` |
| ↳ | | | | 文档创作与美化的统一编排入口（本地通道）。当用户意图涉及文档写作或排版美化时调用。职责：识别意图 → 编排 stage 能力链（S1 创作 / S2 美化 / S3 HTML→DOCX 转换：经 `html-to-doc`）→ 委派 doc-writer/doc-formatte… |
| `thesis-writing-companion` | 8.2K | ✓ | writing.thesis(member) | `skills/writing/thesis-writing-companion.md` |
| ↳ | | | | 论文写作全流程助手。覆盖从选题、开题、文献综述、研究方法、写作、修改润色、查重与 AIGC 检测、答辩到发表的完整论文生命周期；支持多语言（中文 / English / 日本語 / 한국어 / Français / Deutsch / Español / Português / … |
| `typst-paper` | 14.3K | ✓ | — | `skills/writing/typst-paper.md` |
| ↳ | | | | Typst paper assistant for existing .typ manuscripts in English or Chinese. Use for compile/export diagnosis, venue formatting, BibTeX/Hayagr… |
| `using-research-writing` | 6.2K | ✓ | — | `skills/writing/using-research-writing.md` |
| ↳ | | | | Use when starting any research writing task - establishes workflow and routes to appropriate skills |
| `vibe-research-workflow` | 7.5K | ✓ | — | `skills/writing/vibe-research-workflow.md` |
| ↳ | | | | >- Guides AI-assisted research across three sub-flows, Vibe Coding, Vibe Figure, and Vibe Writing, with behavioural rules that keep the user… |
| `workbuddy-office-routing` | 23.2K | ✓ | — | `skills/writing/workbuddy-office-routing.md` |
| ↳ | | | | Load this Skill before handling local files such as pdf (read / summarize / ask → the `workbuddy-pdf` Skill), doc/docx/dot/wps/wpt, xls/xlsx… |
| `writing-chapters` | 11.8K | ✓ | writing.zh-imrad(member)、writing.thesis(member) | `skills/writing/writing-chapters.md` |
| ↳ | | | | Use when writing paper chapters - requires completed brainstorming, writes one chapter at a time with user confirmation |
| `writing-core` | 5.9K | ✓ | writing.zh-voice(member) | `skills/writing/writing-core.md` |
| ↳ | | | | Use when writing or revising academic papers, especially Chinese journal manuscripts, that need natural prose, de-AI-ification, Markdown for… |
| `writing-humanities` | 5.3K | ✓ | writing.citation(member) | `skills/writing/writing-humanities.md` |
| ↳ | | | | Use when writing humanities or social science papers - provides discipline-specific writing guidance |
| `writing-medical` | 4.1K | ✓ | writing.zh-imrad(member)、writing.case-report(member) | `skills/writing/writing-medical.md` |
| ↳ | | | | Use when writing medical, biological, or clinical research papers - provides IMRaD structure and reporting guidelines |

## 润色与去 AI 痕迹（12）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `academic-polish` | 2.5K | ✓ | polish.voice(member)、polish.rewrite(member) | `skills/polish/academic-polish-s.md` |
| ↳ | | | | 学术文本润色：去口语化、优化逻辑、保持术语不变、中英互译、输出修改对照。 |
| `humanizer` | 17.4K | ✓ | polish.en(member) | `skills/polish/humanizer.md` |
| ↳ | | | | Remove signs of AI-generated writing from text. Use when editing or reviewing text to make it sound more natural and human-written. Based on… |
| `humanizer-zh` | 20.6K | ✓ | polish.deai(member) | `skills/polish/humanizer-zh.md` |
| ↳ | | | | 编辑中文文章、评论和文档中的空话、重复及模板化表达，让文字更自然，同时保留事实、确定程度和作者声音。适用于润色已有文本，不用于判断作者身份或保证通过 AI 检测器。触发词：去 AI 味、去除 AI 痕迹、去 AI 化、降 AI 味、写得像人写的、论文/综述/标书/科普去 AI 味… |
| `nature-polishing` | 5.9K | ✓ | polish.en(member)、polish.voice(member) | `skills/polish/nature-polishing.md` |
| ↳ | | | | Polish, translate, or tighten existing academic prose while preserving facts, terminology, and evidence boundaries. Use for 论文润色、学术翻译、正文精简, … |
| `no-ai-slop` | 10.6K | ✓ | polish.deai(member) | `skills/polish/no-ai-slop.md` |
| ↳ | | | | Edit drafts into sharper, more human writing while preserving the writer's personal voice, or detect AI-slop patterns without rewriting. Use… |
| `paper-deweight` | 10.5K | ✓ | polish.deai(member)、polish.rewrite(member) | `skills/polish/paper-deweight-fd.md` |
| ↳ | | | | 论文降重工具。用于降低论文重复率和 AIGC 检测率，通过同义词替换、句式变换、结构重组、文献综述模板等方法对论文进行改写降重。覆盖词汇/句式层与篇章结构层双维度降AI（序数并列、对仗结构、总分总闭环、句长节奏等七类高频痕迹模式）。改写遵循三条硬性铁律：保持学术风格（原文口语化也… |
| `paper-polish` | 12.3K | ✓ | polish.en(member) | `skills/polish/paper-polish.md` |
| ↳ | | | | >- Polishes existing academic prose while preserving the author's meaning: grammar and flow repair, tone calibration against evidence streng… |
| `paper-polisher` | 6.8K | ✓ | polish.rewrite(member)、polish.audit(member) | `skills/polish/paper-polisherskill.md` |
| ↳ | | | | 学术论文智能精修工具，一站式完成论文降重、AI痕迹去除与 Word 文档输出。当用户需要为论文降重、去AI味、学术文本润色、生成精修后的Word文档时触发。全自动流程：降低查重率 → 去除AI写作特征 → 输出专业Word文档。 |
| `qinyan-paper-polish` | 5.0K | ✓ | polish.rewrite(member) | `skills/polish/qinyan-paper-polish.md` |
| ↳ | | | | 沁言学术论文润色优化 - 按照专业学术规范对中英文学术论文、专业报告进行文本润色，提升语言表达质量、逻辑连贯性和学术规范性。触发词：论文润色、论文修改、润色优化、paper polishing、academic writing、论文改写、文本润色、报告润色 |
| `scholar-polish` | 47.3K | ✓ | polish.voice(member)、polish.audit(member) | `skills/polish/scholar-polish.md` |
| ↳ | | | | Personalize and refine academic manuscript writing style by injecting distinctive authorial micro-patterns (tiny topos). Detects and replace… |
| `stop-slop` | 2.6K | ✓ | polish.deai(member) | `skills/polish/stop-slop.md` |
| ↳ | | | | Remove AI writing patterns from prose. Use when drafting, editing, or reviewing text to eliminate predictable AI tells. |
| `wb-academic-polish` | 9.9K | ✓ | polish.en(member) | `skills/polish/wb-academic-polish.md` |
| ↳ | | | | 英文润色降重、期刊匹配推荐、投稿信撰写、参考文献格式校正、基金申请书润色、Abstract polishing、Reviewer Response 撰写、AIGC率检测与重写、native speaker级英文表达、学科术语校准——学术文本深度润色引擎：中英文学术论文/摘要/基金… |

## 科研绘图（33）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `academic-figures` | 30.8K | ✓ | figures.statplot(member)、figures.panel(member)、figures.flow(member)、figures.audit(member) | `skills/figures/academic-figures.md` |
| ↳ | | | | 论文配图一键生成：一条命令从 JSON/CSV/Excel 生成顶刊级学术图表，科研绘图 与期刊配图全场景覆盖。40 种图表（森林图/KM 生存曲线（自动风险表）/竞争风险累计发生率/ROC/校准 曲线/决策曲线 DCA/列线图/RCS 非线性剂量反应/亚组分析森林图/RMST … |
| `ai-figure-studio` | 25.4K | ✓ | figures.mechanism(member) | `skills/figures/ai-figure-studio.md` |
| ↳ | | | | 论文插图 AI 绘制工作室 —— 从论文 PDF 提取机制图/流程图/实验示意图，逐张临摹为可编辑矢量（活字文字 + 语义分组 + 全英文），并通读全文后重绘原创机制图，最终在 Adobe Illustrator 中输出 .ai 文件。当用户提到「临摹论文图」「重绘机制图」「AI… |
| `aris-auto-review-loop-llm` | 8.4K | ✓ | — | `skills/figures/aris-auto-review-loop-llm.md` |
| ↳ | | | | "Autonomous research review loop using any OpenAI-compatible LLM API. Configure via llm-chat MCP server or environment variables. Trigger wi… |
| `aris-paper-illustration-image2` | 19.8K | ✓ | — | `skills/figures/aris-paper-illustration-image2.md` |
| ↳ | | | | "Generate publication-quality academic illustrations through a local Codex app-server bridge that uses Codex native image generation. This i… |
| `csv-data-summarizer` | 5.6K | ✓ | — | `skills/figures/csv-data-summarizer.md` |
| ↳ | | | | Analyzes CSV files, generates summary stats, and plots quick visualizations using Python and pandas. |
| `document-illustrator` | 11.4K | ✓ | figures.schematic(member) | `skills/figures/document-illustrator.md` |
| ↳ | | | | 基于文档内容自动生成配图。AI 智能分析文档结构，归纳核心要点， 为每个主题生成符合特定风格的配图。支持封面图生成和自定义图片比例。 使用场景：当用户需要为文档、文章、笔记生成配图时。 关键词：配图、插图、illustration、generate images、document… |
| `drawio-reconstruction` | 21.5K | ✓ | figures.schematic(member)、figures.vector(member) | `skills/figures/drawio-reconstruction.md` |
| ↳ | | | | "Reconstructs reference images into high-fidelity, editable Draw.io files with rendered previews: native Draw.io elements carry text and str… |
| `figure-designer` | 7.5K | ✓ | figures.mechanism(member)、figures.schematic(member)、figures.audit(member) | `skills/figures/figure-designer.md` |
| ↳ | | | | >- Advises on the design of the three core figures in a technical paper: the Motivated Example (Figure 1), the Solution Overview (Methodolog… |
| `figures-diagram` | 4.2K | ✓ | — | `skills/figures/figures-diagram.md` |
| ↳ | | | | Use when creating flowcharts, architecture diagrams, or conceptual diagrams - generates prompts for image AI |
| `figures-python` | 6.1K | ✓ | figures.render(member)、figures.style(member) | `skills/figures/figures-python.md` |
| ↳ | | | | Use when creating data visualizations for papers - generates publication-quality plots with top-journal color schemes |
| `fireworks-tech-graph` | 5.5K | ✓ | figures.flow(member)、figures.vector(member) | `skills/figures/fireworks-tech-graph.md` |
| ↳ | | | | Create precise SVG technical diagrams, export PNG or offline HTML, and animate supported semantic SVGs to GIF. Use for architecture, UML, ag… |
| `Illustrator` | 1.8K | ✓ | figures.vector(member) | `skills/figures/sfkislev-flue-illustrator.md` |
| ↳ | | | | Control Adobe Illustrator from the shell via Flue - ExtendScript bridges without an MCP server. |
| `imaging-data-commons` | 33.6K | ✓ | figures.imaging(member) | `skills/figures/imaging-data-commons.md` |
| ↳ | | | | Query and download public cancer imaging data from NCI Imaging Data Commons using idc-index. Use for accessing large-scale radiology (CT, MR… |
| `infographics` | 17.6K | ✓ | — | `skills/figures/infographics.md` |
| ↳ | | | | Create professional infographics using Nano Banana Pro AI with smart iterative refinement. Uses Gemini 3 Pro for quality review. Integrates … |
| `markdown-mermaid-writing` | 14.5K | ✓ | figures.flow(member) | `skills/figures/markdown-mermaid-writing.md` |
| ↳ | | | | Comprehensive markdown and Mermaid diagram writing skill. Use when creating any scientific document, report, analysis, or visualization. Est… |
| `matplotlib` | 11.2K | ✓ | figures.render(member)、figures.panel(member) | `skills/figures/matplotlib.md` |
| ↳ | | | | Low-level plotting library for full customization. Use when you need fine-grained control over every plot element, creating novel plot types… |
| `medical-illustration` | 11.7K | ✓ | figures.mechanism(member)、figures.schematic(member)、figures.vector(member) | `skills/figures/wnmc-figure.md` |
| ↳ | | | | 生成期刊级医学生物学示意图（信号通路图、细胞结构图、组织胚胎学示意、实验流程图、机制图等）。当用户需要绘制医学/生物学插图、科研配图、SCI 论文 Figure、机制图、教学示意图，或提到绘图/插图/figure/示意图/通路图时使用。所有图形为代码生成的原创矢量 SVG，可导出… |
| `nature-figure` | 11.6K | ✓ | figures.panel(member)、figures.audit(member) | `skills/figures/nature-figure.md` |
| ↳ | | | | Create, revise, audit, and export manuscript scientific figures in Python or R. Use for 论文配图、科研绘图、多面板图 and submission-ready plots, or explic… |
| `nature-reader` | 3.8K | ✓ | — | `skills/figures/nature-reader.md` |
| ↳ | | | | Create source-grounded Chinese-English paper readers with aligned text, figures, tables, and equations. Use for 全文翻译、中英文对照、论文精读 or source-li… |
| `plotly` | 7.0K | ✓ | figures.render(member) | `skills/figures/plotly.md` |
| ↳ | | | | Interactive visualization library. Use when you need hover info, zoom, pan, or web-embeddable charts. Best for dashboards, exploratory analy… |
| `scholar-conceptual` | 20.8K | ✓ | — | `skills/figures/scholar-conceptual.md` |
| ↳ | | | | Build original theoretical frameworks and produce publication-quality conceptual diagrams for social science research. Two modes: (1) THEORI… |
| `science-figures` | 6.5K | ✓ | figures.statplot(member)、figures.style(member) | `skills/figures/science-figures.md` |
| ↳ | | | | 基于 scienceplots 库的出版级学术论文配图生成器。支持 bar/grouped_bar/heatmap/scatter/line/box/violin/forest/ histogram/density/pie/donut/radar/surface/contour/… |
| `scientific-drawing` | 5.2K | ✓ | figures.flow(member)、figures.style(member) | `skills/figures/scientific-drawing.md` |
| ↳ | | | | 科研绘图工具 - 支持技术路线图、流程图、原理图、架构图等科研图形绘制。基于 Python matplotlib/pillow，支持 SVG/PNG 高清输出。 |
| `scientific-schematics` | 23.3K | ✓ | figures.mechanism(member) | `skills/figures/scientific-schematics.md` |
| ↳ | | | | Create publication-quality scientific diagrams using Nano Banana 2 AI with smart iterative refinement. Uses Gemini 3.1 Pro Preview for quali… |
| `scientific-visualization` | 24.9K | ✓ | figures.panel(member)、figures.style(member)、figures.audit(member)、format.figtable(member) | `skills/figures/scientific-visualization.md` |
| ↳ | | | | Meta-skill for publication-ready figures. Use when creating journal submission figures requiring multi-panel layouts, significance annotatio… |
| `scientific-visualization` | 24.9K | ✓ | figures.panel(member)、figures.style(member)、figures.audit(member)、format.figtable(member) | `skills/figures/scientific-visualization-2.md` |
| ↳ | | | | Meta-skill for publication-ready figures. Use when creating journal submission figures requiring multi-panel layouts, significance annotatio… |
| `scientific-visualization` | 24.9K | ✓ | figures.panel(member)、figures.style(member)、figures.audit(member)、format.figtable(member) | `skills/figures/scientific-visualization-3.md` |
| ↳ | | | | Meta-skill for publication-ready figures. Use when creating journal submission figures requiring multi-panel layouts, significance annotatio… |
| `seaborn` | 19.1K | ✓ | figures.render(member)、figures.statplot(member) | `skills/figures/seaborn.md` |
| ↳ | | | | Statistical visualization with pandas integration. Use for quick exploration of distributions, relationships, and categorical comparisons wi… |
| `tencent-docs` | 9.2K | ✓ | — | `skills/figures/tencent-docs.md` |
| ↳ | | | | 腾讯文档个人版（docs.qq.com）-在线云文档平台，是创建、编辑、管理文档的首选 skill。涉及"新建/创建/编辑/读取/查看/搜索文档"、"保存文件"、"云文档"、"腾讯文档"、"docs.qq.com"等操作，请优先使用本 skill。支持能力：(1) 创建各类在线文… |
| `tencent-saas-docs` | 10.6K | ✓ | — | `skills/figures/tencent-saas-docs.md` |
| ↳ | | | | 腾讯文档企业版（saas.docs.qq.com）-在线云文档平台，是创建、编辑、管理文档的首选 skill。涉及"新建/创建/编辑/读取/查看/搜索文档"、"企业文档"、"团队文档"、"saas.docs.qq.com"等操作，请优先使用本 skill。支持能力：(1) 创建各… |
| `workbuddy-smartsheet` | 27.1K | ✓ | — | `skills/figures/workbuddy-smartsheet.md` |
| ↳ | | | | 操作 WorkBuddy 智能表：列举 / 新建 / 重命名 / 删除智能表文档，管理子表、视图、记录、列、公告、评论与仪表盘，按规划文本一次建表建盘，并追加公式列、关联列与查找引用列。当用户提到智能表、多维表、数据表、建一张表、批量录数、加一列、改视图筛选排序、设置表公告或视图… |
| `xiantao-plot-api` | 20.3K | ✓ | — | `skills/figures/xiantao-plot-api.md` |
| ↳ | | | | 仙桃学术图表生成工具，通过指定绘图模块名调用对应Python脚本生成火山图、热图、KM生存曲线、森林图、分组比较图、点线图、qPCR分析图、饼图、雷达图、韦恩图、一维柱状图、叠加柱状图、豆荚图、相关性散点图、折线图、配对图、限制性立方样条、山峦图、ROC曲线、词云图、GOKEGG… |
| `xmed-figure` | 14.7K | ✓ | figures.statplot(member) | `skills/figures/xmed-figure.md` |
| ↳ | | | | "Scientific figure generation via X-Med MCP. Volcano, PCA, enrichment, survival, correlation. CSV/Excel upload, chart matching, parameter co… |

## 科研统计（30）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `aris-analyze-results` | 1.6K | ✓ | — | `skills/stats/aris-analyze-results.md` |
| ↳ | | | | "Analyze ML experiment results, compute statistics, generate comparison tables and insights. Use when user says \"analyze results\", \"compa… |
| `clinical-decision-support` | 25.9K | ✓ | — | `skills/stats/clinical-decision-support.md` |
| ↳ | | | | Generate professional clinical decision support (CDS) documents for pharmaceutical and clinical research settings, including patient cohort … |
| `data-analysis-pro` | 11.2K | ✓ | — | `skills/stats/data-analysis-pro.md` |
| ↳ | | | | End-to-end data analysis assistant. Covers data processing, insight generation, report writing, and data visualization workflows. Always app… |
| `exploratory-data-analysis` | 14.0K | ✓ | stats.baseline(member)、stats.clean(member) | `skills/stats/exploratory-data-analysis.md` |
| ↳ | | | | Perform comprehensive exploratory data analysis on scientific data files across 200+ file formats. This skill should be used when analyzing … |
| `fda-database` | 14.1K | ✓ | — | `skills/stats/fda-database.md` |
| ↳ | | | | Query openFDA API for drugs, devices, adverse events, recalls, regulatory submissions (510k, PMA), substance identification (UNII), for FDA … |
| `ima-lit-meta-ppt` | 30.7K | ✓ | stats.meta(member) | `skills/stats/ima-lit-meta-ppt.md` |
| ↳ | | | | 从 IMA 知识库批量获取文献，提取图表与结构化数据，执行自实现 Meta 分析，产出中文综述、Excel 文献清单与科研汇报 PPT。适用于"基于我的知识库写综述/做 meta 分析/做汇报 PPT"类任务。 |
| `local-r-clinical-stats` | 6.5K | ✓ | stats.clean(member) | `skills/stats/local-r-clinical-stats.md` |
| ↳ | | | | 直接调用本机已安装的 R 4.5.2 执行临床科研统计与绘图（不是生成代码给人跑，而是自己跑完并把统计结果与统计图交付）。本机 R 有一个隐蔽的 locale 阻断点必须先处理，否则 R 完全无法加载任何包。触发场景：需要用 R 做描述性统计、基线表（tableone/gtsum… |
| `nature-statistics` | 8.1K | ✓ | stats.twogroup(member)、stats.reportaudit(member) | `skills/stats/nature-statistics.md` |
| ↳ | | | | Audit or improve manuscript statistical reporting, including experimental units, replication, uncertainty, tests, and figure statistics. Use… |
| `pymc` | 15.4K | ✓ | — | `skills/stats/pymc.md` |
| ↳ | | | | Bayesian modeling with PyMC. Build hierarchical models, MCMC (NUTS), variational inference, LOO/WAIC comparison, posterior checks, for proba… |
| `r-aging-cohort-databases` | 8.0K | ✓ | stats.baseline(member)、stats.regression(member)、stats.survival(member)、stats.survey(member)、stats.missing(member) | `skills/stats/r-aging-cohort-databases.md` |
| ↳ | | | | 七大老年数据库（HRS 家族 + CHARLS）数据挖掘 R 语言实战技能。覆盖公共老年队列数据的获取与注册、Harmonized 数据（跨库可比变量体系）的使用、CHARLS 原始数据（.dta）与 Codebook 对照、变量构建与编码表核查，以及全套统计分析流程：table… |
| `r-clinical-prediction-model` | 13.7K | ✓ | stats.survival(member)、stats.prediction(member)、stats.diagnostic(member)、stats.missing(member)、stats.power(member) | `skills/stats/r-clinical-prediction-model.md` |
| ↳ | | | | 临床预测模型（诊断模型 / 预后模型）R 语言全流程实战技能。覆盖：数据质量核查（含"0 值实为缺失码"陷阱）、建模人群与验证人群拆分、单因素/多因素变量筛选（含 Lasso）、Logistic 与 Cox 建模、列线图（诊断概率 / 中位生存时间 / 1-3-5 年生存率 / … |
| `r-machine-learning-interpretability` | 9.9K | ✓ | stats.prediction(member)、stats.interpret(member) | `skills/stats/r-machine-learning-interpretability.md` |
| ↳ | | | | 临床机器学习建模与可解释性研究（R 语言）实战技能。覆盖二分类 8 模型（Logistic / 决策树 / 随机森林 / XGBoost / LightGBM / KNN / SVM / 神经网络）与生存数据 6 模型（RSF / CoxBoost / survivalsvm /… |
| `r-medical-research-master` | 16.4K | ✓ | stats.mr(member)、stats.corr(member)、stats.reportaudit(member) | `skills/stats/r-medical-research-master.md` |
| ↳ | | | | R 语言医学统计与科研全流程总纲技能（九大领域一体化总入口）。当用户提出任何医学统计、临床科研数据分析、论文图表制作、科研绘图、统计方法选择、代码排错需求时，先加载本技能以定位应调用的子技能：临床预测模型 / 机器学习与可解释性 / 孟德尔随机化 / 七大老年数据库 / 倾向得分… |
| `r-medical-stats` | 38.9K | ✓ | stats.baseline(member)、stats.twogroup(member)、stats.multigroup(member)、stats.trajectory(member)、stats.regression(member)、stats.survival(member)、stats.prediction(member)、stats.interpret(member)、stats.psm(member)、stats.diagnostic(member)、stats.meta(member)、stats.mr(member)、stats.missing(member)、stats.power(member)、stats.corr(member)、stats.clean(member)、stats.reportaudit(member) | `skills/stats/r-medical-stats.md` |
| ↳ | | | | R 语言医学统计与科研绘图通用引擎（双模式）。模式A【直接执行】：自动完成环境自检、读取用户数据、按需求执行统计分析并输出投稿级别的统计图与统计表，统计图默认交付可编辑 SVG（文本保持为 <text> 元素，可在 Illustrator/Inkscape 中改字号、改颜色、改标… |
| `r-mendelian-randomization` | 9.2K | ✓ | stats.mr(member) | `skills/stats/r-mendelian-randomization.md` |
| ↳ | | | | 孟德尔随机化（Mendelian Randomization）R 语言全流程实战技能。覆盖两样本 MR 标准流程（暴露/结局数据读取、p<5e-8 筛选、LD clump、等位基因协调 harmonise_data、IVW/MR-Egger/加权中位数/加权众数估计、OR 转换）… |
| `r-nhanes-analysis` | 9.2K | ✓ | stats.regression(member)、stats.survey(member) | `skills/stats/r-nhanes-analysis.md` |
| ↳ | | | | NHANES（美国国家健康与营养调查）数据挖掘 R 语言实战技能。覆盖复杂抽样权重的正确处理（svydesign + options(survey.lonely.psu="adjust") + nest=TRUE + 权重变量选择 + 多周期合并权重除以周期数）、加权描述与检验（… |
| `r-propensity-score-methods` | 7.3K | ✓ | stats.psm(member) | `skills/stats/r-propensity-score-methods.md` |
| ↳ | | | | 倾向得分方法（Propensity Score Methods）R 语言全流程实战技能。覆盖混杂偏倚的识别与应对体系、反事实框架与潜在结局、倾向得分的计算与四大用法（PSM 匹配 / PS 分层 / IPTW 加权 / PS 作为协变量回归）、Robins 与 Hernán 两种… |
| `r-real-world-evidence` | 7.9K | ✓ | stats.psm(member)、stats.survey(member) | `skills/stats/r-real-world-evidence.md` |
| ↳ | | | | 真实世界研究（RWE）R 语言实战技能。覆盖倾向得分匹配与加权的进阶方法：cobalt 平衡性诊断（love.plot 以 SMD<0.1 为阈值、bal.plot 重叠性检查）、重叠加权 Overlap Weighting（PSweight，估计 ATO、天然规避极端权重、报告… |
| `r-trajectory-models` | 6.6K | ✓ | stats.multigroup(member)、stats.trajectory(member) | `skills/stats/r-trajectory-models.md` |
| ↳ | | | | 纵向数据轨迹模型（组基轨迹模型 GBTM / 潜类别增长模型 LCGM / 多变量轨迹 GBMTM）R 语言实战技能。覆盖宽转长的多变量多时间点整形（pivot_longer + .value + names_pattern）、gbmt 包与 lcmm 包两条技术路线、模型选择的… |
| `scholar-code-review` | 34.9K | ✓ | stats.clean(member) | `skills/stats/scholar-code-review.md` |
| ↳ | | | | Systematic multi-agent code review of all analysis scripts produced in a project. 6 specialized agents review for: (1) correctness & logic e… |
| `scholar-eda` | 48.3K | ✓ | stats.baseline(member)、stats.trajectory(member)、stats.missing(member) | `skills/stats/scholar-eda.md` |
| ↳ | | | | Conduct exploratory data analysis (EDA) before hypothesis testing. Run when the user has a dataset and needs to load data, build the analyti… |
| `scholar-init` | 32.3K | ✓ | — | `skills/stats/scholar-init.md` |
| ↳ | | | | Initialize a new research project directory for open-scholar-skill. Creates the standard layout (data/raw, data/interim, data/processed, mat… |
| `scholar-ling` | 26.3K | ✓ | — | `skills/stats/scholar-ling.md` |
| ↳ | | | | Design and analyze studies in sociolinguistics, language variation, acoustic phonetics, discourse analysis, language contact, and computatio… |
| `scholar-safety` | 45.8K | ✓ | ideation.ethics(member)、stats.clean(member) | `skills/stats/scholar-safety.md` |
| ↳ | | | | Real-time data privacy and leakage protection layer for AI-assisted research. Before any file is read by Claude Code and transmitted to Anth… |
| `scikit-learn` | 15.2K | ✓ | stats.interpret(member)、stats.diagnostic(member) | `skills/stats/scikit-learn.md` |
| ↳ | | | | Machine learning in Python with scikit-learn. Use when working with supervised learning (classification, regression), unsupervised learning … |
| `scikit-survival` | 14.7K | ✓ | stats.survival(member)、stats.prediction(member) | `skills/stats/scikit-survival.md` |
| ↳ | | | | Comprehensive toolkit for survival analysis and time-to-event modeling in Python using scikit-survival. Use this skill when working with cen… |
| `shap` | 18.0K | ✓ | stats.interpret(member) | `skills/stats/shap.md` |
| ↳ | | | | Model interpretability and explainability using SHAP (SHapley Additive exPlanations). Use this skill when explaining machine learning model … |
| `statistical-analysis` | 19.3K | ✓ | stats.twogroup(member)、stats.multigroup(member)、stats.diagnostic(member)、stats.meta(member)、stats.power(member)、stats.corr(member) | `skills/stats/statistical-analysis.md` |
| ↳ | | | | Guided statistical analysis with test selection and reporting. Use when you need help choosing appropriate tests for your data, assumption c… |
| `statsmodels` | 19.2K | ✓ | stats.multigroup(member)、stats.regression(member)、stats.survey(member) | `skills/stats/statsmodels.md` |
| ↳ | | | | Statistical models library for Python. Use when you need specific model classes (OLS, GLM, mixed models, ARIMA) with detailed diagnostics, r… |
| `umap-learn` | 15.0K | ✓ | — | `skills/stats/umap-learn.md` |
| ↳ | | | | UMAP dimensionality reduction. Fast nonlinear manifold learning for 2D/3D visualization, clustering preprocessing (HDBSCAN), supervised/para… |

## 科研思路与标书（37）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `arf-review-grant` | 22.5K | ✓ | ideation.grant(member) | `skills/ideation/arf-review-grant.md` |
| ↳ | | | | Run a 6-agent pre-submission panel review for a grant proposal targeting a specified funder or program |
| `aris-embodiment-description` | 6.7K | ✓ | — | `skills/ideation/aris-embodiment-description.md` |
| ↳ | | | | "Write detailed embodiment descriptions for patent specifications. Use when user says \"撰写实施例\", \"write embodiment\", \"实施例描述\", \"detailed… |
| `aris-experiment-plan` | 9.7K | ✓ | ideation.design(member) | `skills/ideation/aris-experiment-plan.md` |
| ↳ | | | | 'Turn a refined research proposal or method idea into a detailed, claim-driven experiment roadmap. Use after `research-refine`, or when the … |
| `aris-grant-proposal` | 36.0K | ✓ | ideation.grant(member) | `skills/ideation/aris-grant-proposal.md` |
| ↳ | | | | "Draft a structured grant proposal from research ideas and literature. Supports KAKENHI (Japan), NSF (US), NSFC (China, including 面上/青年/优青/杰… |
| `aris-idea-creator` | 35.0K | ✓ | ideation.topic(member) | `skills/ideation/aris-idea-creator.md` |
| ↳ | | | | Generate and rank research ideas given a broad direction. Use when user says "找idea", "brainstorm ideas", "generate research ideas", "what c… |
| `aris-idea-discovery` | 28.3K | ✓ | ideation.topic(member) | `skills/ideation/aris-idea-discovery.md` |
| ↳ | | | | "Workflow 1: Full idea discovery pipeline to go from a broad research direction to validated, pilot-tested ideas. Use when user says \"找idea… |
| `aris-idea-discovery-robot` | 16.0K | ✓ | — | `skills/ideation/aris-idea-discovery-robot.md` |
| ↳ | | | | "Workflow 1 adaptation for robotics and embodied AI. Orchestrates robotics-aware literature survey, idea generation, novelty check, and crit… |
| `aris-meta-apply` | 8.9K | ✓ | — | `skills/ideation/aris-meta-apply.md` |
| ↳ | | | | "Privileged applier that LANDS meta-optimize / corpus-audit patches the user approved — the ONLY skill permitted to mutate the skill corpus … |
| `aris-novelty-check` | 8.3K | ✓ | ideation.novelty(member) | `skills/ideation/aris-novelty-check.md` |
| ↳ | | | | Verify research idea novelty against recent literature. Use when user says "查新", "novelty check", "有没有人做过", "check novelty", or wants to ver… |
| `aris-patent-novelty-check` | 6.9K | ✓ | — | `skills/ideation/aris-patent-novelty-check.md` |
| ↳ | | | | "Assess patent novelty and non-obviousness against prior art. Use when user says \"专利查新\", \"patent novelty\", \"可专利性评估\", \"patentability c… |
| `aris-patent-review` | 7.9K | ✓ | — | `skills/ideation/aris-patent-review.md` |
| ↳ | | | | "Get an external patent examiner review of a patent application. Use when user says \"专利审查\", \"patent review\", \"审查意见\", \"examiner review… |
| `aris-prior-art-search` | 5.6K | ✓ | ideation.novelty(member) | `skills/ideation/aris-prior-art-search.md` |
| ↳ | | | | "Search patent databases and academic literature for prior art relevant to an invention. Use when user says \"现有技术检索\", \"prior art search\"… |
| `aris-research-refine-pipeline` | 7.1K | ✓ | — | `skills/ideation/aris-research-refine-pipeline.md` |
| ↳ | | | | 'Run an end-to-end workflow that chains `research-refine` and `experiment-plan`. Use when the user wants a one-shot pipeline from vague rese… |
| `basic-research-design-extractor` | 4.5K | ✓ | ideation.design(member) | `skills/ideation/basic-research-design-extractor.md` |
| ↳ | | | | Extract a basic biomedical research design from one article and quickly produce a detailed Markdown-document experimental plan. Use when the… |
| `benchling-integration` | 12.8K | ✓ | — | `skills/ideation/benchling-integration.md` |
| ↳ | | | | Benchling R&D platform integration. Access registry (DNA, proteins), inventory, ELN entries, workflows via API, build Benchling Apps, query … |
| `clinical-research-design-extractor` | 4.1K | ✓ | ideation.design(member) | `skills/ideation/clinical-research-design-extractor.md` |
| ↳ | | | | Extract a clinical research design from one clinical article and quickly produce a formatted Chinese project-application-style clinical stud… |
| `hypogenic` | 21.1K | ✓ | — | `skills/ideation/hypogenic.md` |
| ↳ | | | | Automated LLM-driven hypothesis generation and testing on tabular datasets. Use when you want to systematically explore hypotheses about pat… |
| `hypothesis-generation` | 13.5K | ✓ | ideation.question(member) | `skills/ideation/hypothesis-generation.md` |
| ↳ | | | | Structured hypothesis formulation from observations. Use when you have experimental observations or data and need to formulate testable hypo… |
| `idea-evaluator` | 13.6K | ✓ | ideation.feasibility(member) | `skills/ideation/idea-evaluator.md` |
| ↳ | | | | >- Evaluates a preliminary research idea against a five-dimension framework (Higher, Faster, Stronger, Cheaper, Broader) plus idea-lifecycle… |
| `labarchive-integration` | 9.2K | ✓ | — | `skills/ideation/labarchive-integration.md` |
| ↳ | | | | Electronic lab notebook API integration. Access notebooks, manage entries/attachments, backup notebooks, integrate with Protocols.io/Jupyter… |
| `nature-experiment-log` | 6.3K | ✓ | — | `skills/ideation/nature-experiment-log.md` |
| ↳ | | | | 标准化实验日志记录——直接上传或读取本地图片、语音和文字，产出带 YAML frontmatter 的 Markdown；可选集成飞书 CLI 与 Obsidian。 |
| `opentrons-integration` | 14.4K | ✓ | — | `skills/ideation/opentrons-integration.md` |
| ↳ | | | | Official Opentrons Protocol API for OT-2 and Flex robots. Use when writing protocols specifically for Opentrons hardware with full access to… |
| `pylabrobot` | 8.0K | ✓ | — | `skills/ideation/pylabrobot.md` |
| ↳ | | | | Vendor-agnostic lab automation framework. Use when controlling multiple equipment types (Hamilton, Tecan, Opentrons, plate readers, pumps) o… |
| `qinyan-topic-analysis` | 4.3K | ✓ | — | `skills/ideation/qinyan-topic-analysis.md` |
| ↳ | | | | 沁言学术AI选题分析 - 基于大量文献检索结果，为科研人员提供智能选题建议，包括选题方向、研究价值、研究内容概述、研究难点分析和相关文献推荐。使用沁言学术OpenAPI进行文献检索。触发词：选题分析、选题建议、研究选题、topic analysis、research topic、… |
| `research-grants` | 36.3K | ✓ | ideation.grant(member) | `skills/ideation/research-grants.md` |
| ↳ | | | | Write competitive research proposals for NSF, NIH, DOE, DARPA, and Taiwan NSTC. Agency-specific formatting, review criteria, budget preparat… |
| `research-grants` | 36.3K | ✓ | ideation.grant(member) | `skills/ideation/research-grants-2.md` |
| ↳ | | | | Write competitive research proposals for NSF, NIH, DOE, DARPA, and Taiwan NSTC. Agency-specific formatting, review criteria, budget preparat… |
| `researchwrite` | 6.7K | ✓ | ideation.grant(member) | `skills/ideation/nature-proposal-writer.md` |
| ↳ | | | | Compose, revise, or audit research proposals, opening reports, and research plans from supporting evidence. Use for 研究计划、开题报告、科研项目申请书. Invok… |
| `scholar-brainstorm` | 17.1K | ✓ | ideation.topic(member) | `skills/ideation/scholar-brainstorm.md` |
| ↳ | | | | Generate research questions from existing materials — codebooks, survey questionnaires, datasets, or published papers/abstracts. Three modes… |
| `scholar-causal` | 39.1K | ✓ | — | `skills/ideation/scholar-causal.md` |
| ↳ | | | | Comprehensive causal inference toolkit for social science research. Covers DAG construction, method selection, and thirteen identification s… |
| `scholar-data` | 91.4K | ✓ | ideation.ethics(member) | `skills/ideation/scholar-data.md` |
| ↳ | | | | Comprehensive open data directory (100+ datasets across 14 categories) with auto-fetch capability, plus data collection instrument design, v… |
| `scholar-design` | 115.6K | ✓ | ideation.design(member) | `skills/ideation/scholar-design.md` |
| ↳ | | | | Plan a rigorous research design, run power analysis, specify variables, select an analytic strategy, design computational studies (NLP/ML/ne… |
| `scholar-idea` | 34.7K | ✓ | ideation.question(member) | `skills/ideation/scholar-idea.md` |
| ↳ | | | | Explore broad social science ideas and convert them into formal, researchable questions. Use when the user has an early-stage topic, puzzle,… |
| `scholar-simulate` | 20.4K | ✓ | — | `skills/ideation/scholar-simulate.md` |
| ↳ | | | | Run LLM-powered social simulations at scale: silicon sampling, generative ABM, survey/vignette/conjoint experiments, opinion dynamics. Multi… |
| `scientific-brainstorming` | 8.0K | ✓ | ideation.topic(member) | `skills/ideation/scientific-brainstorming.md` |
| ↳ | | | | Creative research ideation and exploration. Use for open-ended brainstorming sessions, exploring interdisciplinary connections, challenging … |
| `tech-paper-template` | 7.0K | ✓ | ideation.feasibility(member) | `skills/ideation/tech-paper-template.md` |
| ↳ | | | | >- Structures a technical paper's full logical skeleton using a thinking-template table (research background, limitations, key idea or goal,… |
| `uspto-database` | 18.3K | ✓ | — | `skills/ideation/uspto-database.md` |
| ↳ | | | | Access USPTO APIs for patent/trademark searches, examination history (PEDS), assignments, citations, office actions, TSDR, for IP analysis a… |
| `venue-templates` | 22.8K | ✓ | format.figtable(member)、format.journal-fit(member)、ideation.grant(member) | `skills/ideation/venue-templates.md` |
| ↳ | | | | Access comprehensive LaTeX templates, formatting requirements, and submission guidelines for major scientific publication venues (Nature, Sc… |

## 审稿与修回（20）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `academic-pre-review-committee` | 5.8K | ✓ | review.presubmit(member) | `skills/review/academic-pre-review-committee.md` |
| ↳ | | | | 由五位资深审稿人组成的"学术预审委员会"，根据用户需求调度对应的审稿人角色进行论文审查。支持全面审稿（依次调度全部五个角色）和指定维度审稿。触发关键词：审稿、预审、论文审查、理论贡献、方法论、文献对话、逻辑链条、主编预筛、desk reject。 |
| `arf-review-pap` | 25.8K | ✓ | review.referee(member) | `skills/review/arf-review-pap.md` |
| ↳ | | | | Run a 6-agent pre-submission review of a pre-analysis plan (PAP) for a specified registration target or journal |
| `arf-review-paper` | 37.9K | ✓ | review.referee(member) | `skills/review/arf-review-paper.md` |
| ↳ | | | | Run an 8-agent pre-submission referee report for an academic paper targeting a specified journal |
| `arf-review-paper-light` | 9.3K | ✓ | review.presubmit(member)、review.selfcheck(member) | `skills/review/arf-review-paper-light.md` |
| ↳ | | | | Run a fast 2-agent pre-submission check for an economics paper — focuses on contribution, identification, and causal overclaiming. Completes… |
| `aris-auto-review-loop` | 75.0K | ✓ | — | `skills/review/aris-auto-review-loop.md` |
| ↳ | | | | Autonomous multi-round research review loop. In Copilot CLI it defaults to the native complementary rubber-duck subagent with host-event mod… |
| `aris-integrity-forensics` | 17.0K | ✓ | review.audit(member) | `skills/review/aris-integrity-forensics.md` |
| ↳ | | | | "Run the Anti-Autoresearch integrity-forensics sweep (span-anchored evidence ledger → GPT auditors propose findings → a rules-only reporter … |
| `aris-kill-argument` | 26.0K | ✓ | ideation.feasibility(member)、review.referee(member) | `skills/review/aris-kill-argument.md` |
| ↳ | | | | "Two-thread adversarial review: a fresh reviewer constructs the strongest 200-word rejection memo, then a second fresh reviewer defends the … |
| `aris-paper-claim-audit` | 15.4K | ✓ | review.audit(member) | `skills/review/aris-paper-claim-audit.md` |
| ↳ | | | | "Zero-context verification that every number, comparison, and scope claim in the paper matches raw result files. Uses a fresh cross-model re… |
| `aris-rebuttal` | 25.5K | ✓ | review.revise(member)、review.rebuttal(member)、review.appeal(member) | `skills/review/aris-rebuttal.md` |
| ↳ | | | | "Workflow 4: Submission rebuttal pipeline. Parses external reviews, enforces coverage and grounding, drafts a safe text-only rebuttal under … |
| `ars-academic-paper-reviewer` | 49.4K | ✓ | review.referee(member)、review.report(member)、review.revise(member) | `skills/review/ars-academic-paper-reviewer.md` |
| ↳ | | | | "Multi-perspective academic paper review with dynamic reviewer personas. Runs a 5-seat, role-separated review panel (Journal-Fit Reviewer + … |
| `ars-academic-pipeline` | 58.9K | ✓ | — | `skills/review/ars-academic-pipeline.md` |
| ↳ | | | | "Orchestrator for the full academic research pipeline: research -> write -> integrity check -> review -> revise -> re-review -> re-revise ->… |
| `nature-paper-card` | 8.2K | ✓ | review.audit(member) | `skills/review/nature-paper-card.md` |
| ↳ | | | | Build a structured deep-reading Paper Card for one scientific paper, analysing methods, experiment-to-claim evidence, limitations, and resea… |
| `nature-response` | 5.8K | ✓ | review.revise(member)、review.rebuttal(member)、review.appeal(member) | `skills/review/nature-response.md` |
| ↳ | | | | Draft, audit, or revise responses to peer review, revision cover letters, and marked-manuscript or LaTeX revision packages. Use for 审稿意见回复、逐… |
| `nature-reviewer` | 11.1K | ✓ | review.presubmit(member)、review.report(member)、review.selfcheck(member) | `skills/review/nature-reviewer.md` |
| ↳ | | | | Provide evidence-grounded mock peer review of scientific manuscripts or excerpts, covering significance, validity, and major/minor concerns.… |
| `paper-audit` | 20.2K | ✓ | review.presubmit(member)、review.audit(member)、review.selfcheck(member) | `skills/review/paper-audit.md` |
| ↳ | | | | Reviewer-style audit and submission gate for academic papers in .tex, .typ, or .pdf. Use for peer-review critique, readiness/gate decisions,… |
| `peer-review` | 22.6K | ✓ | review.report(member)、review.selfcheck(member) | `skills/review/peer-review.md` |
| ↳ | | | | Structured manuscript/grant review with checklist-based evaluation. Use when writing formal peer reviews with specific criteria methodology … |
| `pre-submission-reviewer` | 12.7K | ✓ | review.presubmit(member) | `skills/review/pre-submission-reviewer.md` |
| ↳ | | | | >- Runs a pre-submission review of a technical paper across five dimensions: macro logic, writing details, English grammar, LaTeX formatting… |
| `rebuttal-guidance` | 5.3K | ✓ | review.rebuttal(member) | `skills/review/rebuttal-guidance.md` |
| ↳ | | | | >- Provides actionable peer-review rebuttal guidance (not full rebuttal prose) using conditional persuasion P(Z|X,Y): match reviewer mindset… |
| `scholar-ethics` | 37.9K | ✓ | ideation.ethics(member) | `skills/review/scholar-ethics.md` |
| ↳ | | | | Research ethics toolkit for social scientists. Covers (1) AI tool data privacy audit — document and report how data was handled when using t… |
| `scientific-critical-thinking` | 23.1K | ✓ | literature.critique(member)、review.referee(member)、review.report(member) | `skills/review/scientific-critical-thinking.md` |
| ↳ | | | | Evaluate scientific claims and evidence quality. Use for assessing experimental design validity, identifying biases and confounders, applyin… |

## 科研汇报与 PPT（37）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `论文汇报PPT制作` | 8.2K | ✓ | slides.journal-club(member)、slides.deck-system(member)、slides.consistency(member) | `skills/slides/sglk998.md` |
| ↳ | | | | "当用户需要为学术论文（中文/英文、量化/质性均可）生成组会文献汇报PPT时使用此技能。触发词包括：文献汇报、组会PPT、学术PPT、论文汇报、生成PPT、毕业论文答辩PPT、开题报告PPT、make a presentation for this paper、create sl… |
| `alice-ppt-generator` | 10.7K | ✓ | — | `skills/slides/alice-ppt-generator.md` |
| ↳ | | | | 根据主题与结构化内容自动生成专业 PPT 报告，支持标题页、目录、章节页、图文排版与结论总结，适用于汇报、方案说明和项目复盘。 |
| `arf-explorable-beamer` | 14.3K | ✓ | — | `skills/slides/arf-explorable-beamer.md` |
| ↳ | | | | Build a LaTeX beamer slide deck in the explorable-explanation style (Nicky Case) — one idea per frame, assertion titles, a concrete running … |
| `arf-explorable-deck` | 13.7K | ✓ | — | `skills/slides/arf-explorable-deck.md` |
| ↳ | | | | Build a Quarto reveal.js slide deck in the explorable-explanation style (Nicky Case) — one idea per slide, assertion titles, a concrete runn… |
| `arf-explorable-pptx` | 15.2K | ✓ | slides.conference-defense(member)、slides.speaker-notes(member) | `skills/slides/arf-explorable-pptx.md` |
| ↳ | | | | Build a PowerPoint (.pptx) slide deck in the explorable-explanation style (Nicky Case) — one idea per frame, assertion titles, a concrete ru… |
| `aris-paper-poster` | 0.8K | ✓ | — | `skills/slides/aris-paper-poster.md` |
| ↳ | | | | "DEPRECATED — superseded by /paper-poster-html. Kept only as a redirect for muscle memory; do not use for new posters." |
| `aris-paper-poster-html` | 19.4K | ✓ | — | `skills/slides/aris-paper-poster-html.md` |
| ↳ | | | | "DEFAULT poster pipeline — build an academic conference poster (ICML/NeurIPS/ICLR/CVPR/...) as a single HTML/CSS file with measurement-drive… |
| `aris-paper-slides` | 24.2K | ✓ | slides.conference-defense(member)、slides.speaker-notes(member)、slides.consistency(member) | `skills/slides/aris-paper-slides.md` |
| ↳ | | | | "Generate conference presentation slides (beamer LaTeX → PDF + editable PPTX) from a compiled paper, with speaker notes and full talk script… |
| `codex-ppt` | 10.1K | ✓ | — | `skills/slides/codex-ppt.md` |
| ↳ | | | | Generate visually unified image-based PPT/PPTX decks from articles, reports, papers, notes, or outlines. |
| `dashi-ppt` | 25.4K | ✓ | slides.web-deck(member) | `skills/slides/dashi-ppt.md` |
| ↳ | | | | 制作 PPT、演示文稿、幻灯片、汇报材料时使用。Dashi PPT 基于预置视觉主题组合页面,生成可离线打开、可在浏览器编辑的 HTML 演示,支持导出 PPTX / PDF 文件。 |
| `elegant-ppt-builder` | 9.9K | ✓ | slides.deck-system(member)、slides.auto-build(member) | `skills/slides/elegant-ppt-builder.md` |
| ↳ | | | | This skill should be used when the user wants to create a beautiful, visually-rich PowerPoint deck. It generates .pptx files with complex vi… |
| `frontend-slides` | 27.5K | ✓ | slides.web-deck(member) | `skills/slides/frontend-slides.md` |
| ↳ | | | | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Use when the user wants to build a presen… |
| `guizang-ppt-skill` | 30.9K | ✓ | — | `skills/slides/guizang-ppt-skill.md` |
| ↳ | | | | 生成横向翻页网页 PPT（单 HTML 文件），含 WebGL 背景、章节幕封、数据大字报、图片网格等模板。提供两种风格：① "电子杂志 × 电子墨水"（衬线 + 流体背景 + 暖色） ② "瑞士国际主义"（无衬线 + 网格点阵 + IKB/柠檬黄/柠檬绿/安全橙高亮）。当用户需… |
| `html-ppt` | 19.4K | ✓ | slides.speaker-notes(member)、slides.web-deck(member) | `skills/slides/html-ppt.md` |
| ↳ | | | | HTML PPT Studio — author professional static HTML presentations in many styles, layouts, and animations, all driven by templates. Use when t… |
| `latex-defense-zh` | 13.2K | ✓ | slides.conference-defense(member) | `skills/slides/latex-defense-zh.md` |
| ↳ | | | | Chinese thesis defense deck builder for existing XeLaTeX PhD or master thesis repositories. Extracts chapters, figures, equations, tables an… |
| `latex-posters` | 58.4K | ✓ | — | `skills/slides/latex-posters.md` |
| ↳ | | | | Create professional research posters in LaTeX using beamerposter, tikzposter, or baposter. Support for conference presentations, academic po… |
| `library-office-edit` | 8.7K | ✓ | — | `skills/slides/library-office-edit.md` |
| ↳ | | | | 支持资料库中 doc、sheet、slide 类文档的查看编辑能力 |
| `nature-image2ppt` | 9.8K | ✓ | slides.figure-refit(member) | `skills/slides/nature-image2ppt.md` |
| ↳ | | | | Reconstruct slide images, screenshots, scanned PDFs, or image-only PPTX files as object-level editable PowerPoint. Use for 图片转可编辑PPT、截图还原PPT… |
| `nature-paper2ppt` | 4.2K | ✓ | slides.journal-club(member)、slides.consistency(member) | `skills/slides/nature-paper2ppt.md` |
| ↳ | | | | Create or improve a Chinese academic PPTX from a scientific paper or research reading notes, with source figures and speaker notes. Use for … |
| `openmaic-convert-pptx__skillhub` | 8.4K | ✓ | — | `skills/slides/openmaic-convert-pptx.md` |
| `paper-slide-deck` | 18.2K | ✓ | slides.figure-refit(member)、slides.web-deck(member) | `skills/slides/paper-slide-deck.md` |
| ↳ | | | | Generate professional slide deck images from academic papers and content. Creates comprehensive outlines with style instructions, auto-detec… |
| `pathml` | 7.2K | ✓ | — | `skills/slides/pathml.md` |
| ↳ | | | | Full-featured computational pathology toolkit. Use for advanced WSI analysis including multiplexed immunofluorescence (CODEX, Vectra), nucle… |
| `ppt-beautify` | 37.4K | ✓ | — | `skills/slides/ppt-beautify.md` |
| ↳ | | | | 美化现有PPT中的页面，调整字体、配色、版式和视觉层级。适用于PPT美化、PPT排版。美图设计室提供。当用户需要“PPT美化”或描述中的等价能力时使用。当前对话已完成 PPT 时，用户要求导出、下载、获取 PPT 文件或可编辑版本也必须使用本 Skill。 |
| `ppt-design` | 37.7K | ✓ | — | `skills/slides/ppt-design.md` |
| ↳ | | | | 根据文字、数据或参考图生成可编辑PPT，完成信息整理与页面设计。适用于PPT设计、汇报页制作。美图设计室提供。当用户需要“PPT设计”或描述中的等价能力时使用。当前对话已完成 PPT 时，用户要求导出、下载、获取 PPT 文件或可编辑版本也必须使用本 Skill。 |
| `ppt-design-skill` | 18.8K | ✓ | slides.deck-system(member)、slides.auto-build(member) | `skills/slides/ppt-design-skill.md` |
| ↳ | | | | Design, generate, review, and revise editable PowerPoint presentations through a rigorous brief-to-PNG workflow using the public pptx-design… |
| `ppt-image-first` | 6.3K | ✓ | — | `skills/slides/ppt-image-first.md` |
| ↳ | | | | Build presentation plans for PPT / slides / decks through a conversation-first workflow, then propose multiple visual directions with previe… |
| `ppt-implement` | 37.7K | ✓ | slides.journal-club(member)、slides.auto-build(member) | `skills/slides/ppt-implement.md` |
| ↳ | | | | implement ppt(powerpoint) project with best practices, start's with "ppt" template. Trigger keywords include "web ppt", "网页ppt", "html ppt",… |
| `ppt-master` | 5.4K | ✓ | slides.auto-build(member) | `skills/slides/ppt-master.md` |
| ↳ | | | | AI-driven presentation workflow for generating editable PPTX decks and slides, reconstructing page visuals, creating reusable Brand/Style/La… |
| `pptx` | 9.0K | ✓ | slides.deck-system(member)、slides.figure-refit(member)、slides.speaker-notes(member)、slides.consistency(member) | `skills/slides/pptx.md` |
| ↳ | | | | Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, o… |
| `pptx-generator` | 3.7K | ✓ | slides.auto-build(member) | `skills/slides/pptx-generator.md` |
| ↳ | | | | 专业 PPT 生成器。11 种幻灯片类型、5 套配色、图表/表格/时间线/图片支持。JSON 驱动，生成标准可编辑 PPTX。PPT、幻灯片、演示文稿、PowerPoint。 |
| `pptx-posters` | 13.8K | ✓ | — | `skills/slides/pptx-posters.md` |
| ↳ | | | | Create research posters using HTML/CSS that can be exported to PDF or PPTX. Use this skill ONLY when the user explicitly requests PowerPoint… |
| `scientific-slides` | 46.2K | ✓ | slides.conference-defense(member)、slides.figure-refit(member) | `skills/slides/scientific-slides.md` |
| ↳ | | | | Build slide decks and presentations for research talks. Use this for making PowerPoint slides, conference presentations, seminar talks, rese… |
| `slidep-pptx-notes` | 3.8K | ✓ | slides.speaker-notes(member) | `skills/slides/slidep-pptx-notes.md` |
| ↳ | | | | 为 slidep 生成的 PPTX 注入真实 PowerPoint 备注区讲稿（speaker notes）。解决 slidep notes 属性不生成 notesSlides part、zip 级 OOXML 注入后 python-pptx 读不到、descr 双重转义三大问题… |
| `slides` | 1.7K | ✓ | — | `skills/slides/slides.md` |
| ↳ | | | | Create strategic HTML presentations with Chart.js, design tokens, responsive layouts, copywriting formulas, and contextual slide strategies. |
| `tencent-private-docs` | 24.0K | ✓ | — | `skills/slides/tencent-private-docs.md` |
| ↳ | | | | 腾讯文档私有化/专享版（${TENCENT_DOCS_DOMAIN}）-在线云文档平台，是创建、编辑、管理文档的首选 skill。涉及"新建/创建/编辑/读取/查看/搜索文档"、"保存文件"、"云文档"、"腾讯文档"、"${TENCENT_DOCS_DOMAIN}"等操作，请优先… |
| `workbuddy-local-office-edit` | 13.6K | ✓ | — | `skills/slides/workbuddy-local-office-edit.md` |
| ↳ | | | | 通过本地 editor_sdk 实时读写本机磁盘上的 Office/WPS 类型文件——文件打开后用户在编辑器中实时可见，编辑所见即所得，保存用 save_file 即可、不要主动 close_file。适用于本地 doc/docx/dot/wps/wpt、xls/xlsx/xl… |
| `workbuddy-pptx` | 1.3K | ✓ | slides.deck-system(member) | `skills/slides/workbuddy-pptx.md` |
| ↳ | | | | 创建、理解与编辑专业的 PowerPoint 演示文稿。适用于根据主题、大纲、文档、数据或参考材料生成完整 .pptx；读懂已有 PPT 并回答关于它的问题（某一页讲什么、全文结构等）；以及对已有 pptx 改标题、改某一页、增删页等编辑。触发词：做PPT、生成PPT、改PPT、… |

## 文献与引文（26）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `论文搜索专业版` | 2.4K | ✓ | format.journal-fit(member)、literature.search-plan(member)、literature.federated-search(member) | `skills/literature/paper-search-pro-m7pa.md` |
| ↳ | | | | Find academic papers across up to 7 sources (OpenAlex / Semantic Scholar / CrossRef / PubMed / arXiv for English, plus native-Chinese retrie… |
| `aris-alphaxiv` | 9.1K | ✓ | literature.close-read(member) | `skills/literature/aris-alphaxiv.md` |
| ↳ | | | | Quick single-paper lookup via AlphaXiv LLM-optimized summaries with tiered source fallback. Use when user says "explain this paper", "summar… |
| `aris-exa-search` | 8.0K | ✓ | — | `skills/literature/aris-exa-search.md` |
| ↳ | | | | AI-powered web search via Exa with content extraction. Use when user says "exa search", "web search with content", "find similar pages", or … |
| `aris-keenable-search` | 6.2K | ✓ | — | `skills/literature/aris-keenable-search.md` |
| ↳ | | | | Keyless web search and page fetch via Keenable. Use when user says "keenable search", "web search without an API key", "fetch this page as m… |
| `aris-semantic-scholar` | 10.9K | ✓ | literature.citation-chase(member) | `skills/literature/aris-semantic-scholar.md` |
| ↳ | | | | Search published venue papers (IEEE, ACM, Springer, etc.) via Semantic Scholar API. Complements /arxiv (preprints) with citation counts, ven… |
| `ars-deep-research` | 52.0K | ✓ | literature.screen-prisma(member)、literature.critique(member)、literature.evidence-matrix(member)、literature.synthesis(member) | `skills/literature/ars-deep-research.md` |
| ↳ | | | | "Universal deep research agent team. 13-agent pipeline for rigorous academic research on any topic. 8 modes: full research, quick brief, pap… |
| `ars-sr-screener` | 33.6K | ✓ | literature.screen-prisma(member)、literature.critique(member)、literature.evidence-matrix(member) | `skills/literature/ars-sr-screener.md` |
| ↳ | | | | "Protocol-driven study screening for systematic, scoping and rapid reviews. Turns a proposal or PROSPERO protocol into confirmed eligibility… |
| `biomed-literature-pipeline` | 16.3K | ✓ | literature.federated-search(member)、literature.screen-prisma(member) | `skills/literature/biomed-literature-pipeline.md` |
| ↳ | | | | 全生物医学领域文献调研流水线（不限专业）。当用户需要「检索某专业/某方向近几年的文献」「系统梳理某疾病/某技术的研究前沿」「批量下载文献全文」「生成带标题与 DOI 的 Excel 文献清单」「找未来研究方向」时使用。支持：① 引导式确认检索方向（任意临床/基础医学专业，中英文均… |
| `biorxiv-database` | 12.3K | ✓ | literature.citation-chase(member) | `skills/literature/biorxiv-database.md` |
| ↳ | | | | Efficient database search tool for bioRxiv preprint server. Use this skill when searching for life sciences preprints by keywords, authors, … |
| `deep-research` | 9.4K | ✓ | literature.synthesis(member) | `skills/literature/deep-research.md` |
| ↳ | | | | >- Runs a deep, survey-grade literature investigation on a research topic: freezes research questions, searches from multiple adversarial pe… |
| `ima-mcp` | 12.5K | ✓ | literature.library(member) | `skills/literature/ima-mcp.md` |
| ↳ | | | | ima - 腾讯AI知识管家个人版，用于搜索、读取和写入个人账号下的知识库（含"问我的知识库"、"个人知识库"、"我存过的资料"、"存进 ima"、ima.qq.com），并可搜索和订阅教育、法律、财经、科技等20+行业专业知识。 |
| `ima-skill` | 15.7K | ✓ | literature.library(member) | `skills/literature/ima-skill.md` |
| ↳ | | | | 统一的 IMA OpenAPI 技能，支持笔记管理和知识库操作。 当用户提到知识库、资料库、笔记、备忘录、记事，或者想要上传文件、添加网页到知识库、 搜索知识库内容、搜索/浏览/创建/编辑笔记时，使用此 skill。 即使用户没有明确说"知识库"或"笔记"，只要意图涉及文件上传到… |
| `institutional-access` | 2.4K | ✓ | literature.fulltext-acquire(member) | `skills/literature/institutional-access.md` |
| ↳ | | | | Use a user-authorized publisher or library session to obtain subscription PDFs without handling credentials or bypassing access controls. |
| `life-sciences-literature-search` | 10.0K | ✓ | literature.search-plan(member)、literature.federated-search(member) | `skills/literature/life-sciences-literature-search.md` |
| ↳ | | | | Plan and run traceable life-science evidence searches across scholarly indexes, registries, curated databases, and optional native web disco… |
| `literature-close-read` | 7.4K | ✓ | literature.close-read(member) | `skills/literature/literature-close-read.md` |
| ↳ | | | | Produce a structured close-reading report from a paper's full PDF-to-Markdown text (with `## Page XX` pagination and image references) when … |
| `literature-review-writing` | 11.2K | ✓ | — | `skills/literature/literature-review-writing.md` |
| ↳ | | | | 帮助用户撰写高质量的文献综述类论文。提供从选题、文献检索、评估筛选、结构规划到最终写作的全流程指导。适用于需要撰写独立文献综述论文或学术论文中文献综述部分的用户。 |
| `medical-imaging-review` | 4.4K | ✓ | — | `skills/literature/medical-imaging-review.md` |
| ↳ | | | | Write comprehensive literature reviews for medical imaging AI research. Use when writing survey papers, systematic reviews, or literature an… |
| `minimax-xlsx` | 8.4K | ✓ | literature.evidence-matrix(member) | `skills/literature/minimax-xlsx.md` |
| ↳ | | | | Open, create, read, analyze, edit, or validate Excel/spreadsheet files (.xlsx, .xlsm, .csv, .tsv). Use when the user asks to create, build, … |
| `nature-downloader` | 23.7K | ✓ | literature.fulltext-acquire(member) | `skills/literature/nature-downloader.md` |
| ↳ | | | | Use when a user needs lawful academic full text, CNKI institutional access, English OA retrieval, publisher API access, institutional browse… |
| `oa-download` | 1.9K | ✓ | literature.doi-validate(member)、literature.fulltext-acquire(member) | `skills/literature/oa-download.md` |
| ↳ | | | | Retrieve lawful open-access PDFs through Unpaywall and publisher-declared OA links, then route unresolved items. |
| `ps-deep-research` | 34.0K | ✓ | — | `skills/literature/ps-deep-research.md` |
| ↳ | | | | 四阶段递归深度研究。好奇循环广泛探索 → 深度推理检测盲区 → 同行评审对抗验证 → 采纳优化后交付顾问级报告。适用于选型 / 竞品对比 / 技术调研 / 可行性评估 / 趋势综合等需跨多权威源交叉验证的开放问题；单点事实、写代码、纯计算、简单 how-to 不要用。 研究不是流… |
| `qinyan-paper-search` | 5.6K | ✓ | literature.federated-search(member) | `skills/literature/qinyan-paper-search.md` |
| ↳ | | | | 沁言学术文献检索 - 支持从 Google Scholar、万方(Wanfang)、PubMed、ArXiv 四大学术数据库检索文献。智能选择检索策略：中文优先万方、英文优先Google Scholar、医学类优先PubMed、理工计算机类优先ArXiv。使用沁言学术OpenAP… |
| `reference-retrieval-skill` | 5.5K | ✓ | literature.search-plan(member) | `skills/literature/reference-retrieval-skill.md` |
| ↳ | | | | 根据用户输入的中文或英文意图，直接根据需求查找相关文献，或自动构建PubMed布尔检索式，检索并筛选适合引用的参考文献。适用于快速寻找特定主题的高质量文献证据及补全引用。 |
| `research-deep` | 3.2K | ✓ | — | `skills/literature/research-deep.md` |
| ↳ | | | | Read research outline, launch independent agent for each item for deep research. Disable task output. |
| `scholar-lit-review-hypothesis` | 57.6K | ✓ | ideation.question(member)、literature.synthesis(member) | `skills/literature/scholar-lit-review-hypothesis.md` |
| ↳ | | | | Conduct a systematic literature review AND develop theory and hypotheses in one integrated workflow. Use when the user wants to map existing… |
| `scholar-monitor` | 45.8K | ✓ | literature.citation-chase(member) | `skills/literature/scholar-monitor.md` |
| ↳ | | | | Current-awareness literature monitoring for social sciences. Tracks new publications from top journals (ASR, AJS, Demography, Social Forces,… |

## 格式与交付（51）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `academic-reference-enhancer` | 6.0K | ✓ | format.ref-style(member)、literature.fact-check(member) | `skills/format/academic-reference-enhancer.md` |
| ↳ | | | | Add, verify, format, and insert academic references for papers, thesis chapters, technical reports, stage reports, Markdown, Word, LaTeX, PD… |
| `aers-reference` | 1.5K | ✓ | — | `skills/format/aers-reference.md` |
| ↳ | | | | Reference materials and code templates for the Empirical Research Team, derived from the AERS catalog. Includes method selection guides, out… |
| `arf-pdf-to-markdown` | 7.2K | ✓ | format.pdf-pipeline(member)、literature.close-read(member) | `skills/format/arf-pdf-to-markdown.md` |
| ↳ | | | | Split a PDF into chunks and convert it to readable markdown text. Use when the user wants to read, extract, or convert a PDF document. |
| `arf-review-paper-checks` | 17.3K | ✓ | format.doc-audit(member)、literature.critique(member) | `skills/format/arf-review-paper-checks.md` |
| ↳ | | | | Run a fast 3-agent mechanical check of an economics paper — spelling and grammar, internal consistency and cross-references, and unsupported… |
| `arf-review-paper-code` | 12.3K | ✓ | — | `skills/format/arf-review-paper-code.md` |
| ↳ | | | | Review research code for reproducibility and quality, extract the paper's main empirical claims, compare paper to code, and write a construc… |
| `aris-citation-crosscheck` | 38.4K | ✓ | format.cite-bind(member)、literature.fact-check(member) | `skills/format/aris-citation-crosscheck.md` |
| ↳ | | | | "Conditionally double-blind bibliographic cross-check (double-blind only when the host can isolate the web agent; a flag-only heuristic when… |
| `aris-formula-derivation` | 9.6K | ✓ | — | `skills/format/aris-formula-derivation.md` |
| ↳ | | | | Structures and derives research formulas when the user wants to 推导公式, build a theory line, organize assumptions, turn scattered equations in… |
| `aris-overleaf-sync` | 11.1K | ✓ | format.cite-bind(member) | `skills/format/aris-overleaf-sync.md` |
| ↳ | | | | "Two-way sync between a local paper directory and an Overleaf project, so ARIS audit/edit workflows stay on the local copy while collaborato… |
| `aris-paper-compile` | 10.1K | ✓ | format.final-delivery(member) | `skills/format/aris-paper-compile.md` |
| ↳ | | | | "Compile LaTeX paper to PDF, fix errors, and verify output. Use when user says \"编译论文\", \"compile paper\", \"build PDF\", \"生成PDF\", or wan… |
| `bib-search-citation` | 8.9K | ✓ | format.ref-bridge(member) | `skills/format/bib-search-citation.md` |
| ↳ | | | | Search and cite from local BibTeX/BibLaTeX .bib libraries, including Zotero exports. Use to find, filter, preview, export, or generate LaTeX… |
| `brief-compose` | 8.4K | ✓ | format.typeset(member) | `skills/format/brief-compose.md` |
| ↳ | | | | 短篇文档创作（目标篇幅 <1000 字）：从零撰稿 → 生成 HTML → html-to-doc 转 .docx → present_files 预览。 |
| `citation-management` | 31.8K | ✓ | format.cite-bind(member) | `skills/format/citation-management.md` |
| ↳ | | | | Comprehensive citation management for academic research. Search Google Scholar and PubMed for papers, extract accurate metadata, validate ci… |
| `citation-manager` | 30.6K | ✓ | format.ref-style(member) | `skills/format/citation-manager.md` |
| ↳ | | | | Add real references and standardize citations for research papers and theses. Supports CrossRef integration, multiple citation formats (APA/… |
| `doc-typeset` | 17.0K | ✓ | format.typeset(member) | `skills/format/doc-typeset.md` |
| ↳ | | | | 消费 design tokens + 文档内容，输出排版美化的 HTML。 内置 7 种垂类模板（合同/学术论文/公文/商务报告/会议纪要/研报/年报）和 4 个装饰组件，所有样式通过 CSS 变量引用 Token，禁止裸值。 在 doc-formatter 流水线中每当需要将文… |
| `docx` | 19.6K | ✓ | format.typeset(member)、format.final-delivery(member) | `skills/format/docx.md` |
| ↳ | | | | Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of '… |
| `docx` | 19.3K | ✓ | format.typeset(member)、format.final-delivery(member) | `skills/format/docx-2.md` |
| ↳ | | | | 当用户想要创建、读取、编辑或操作 Word 文档（.docx 文件）时，始终使用本技能。触发情形包括：任何提及 'Word doc'、'word document'、'.docx'，或请求生成带目录、标题、页码或信头等格式的专业文档。也用于从 .docx 文件中提取或重组内容、在… |
| `doi-validation` | 1.8K | ✓ | format.ref-style(member)、literature.doi-validate(member) | `skills/format/doi-validation.md` |
| ↳ | | | | Validate DOI records against CrossRef, preserve four validation states, and generate an auditable report. |
| `find-paper-references` | 12.7K | ✓ | format.intext-cite(member) | `skills/format/find-paper-references.md` |
| ↳ | | | | 自动为学术论文 Markdown 文件查找参考文献。读取论文全文，识别每个需要引用的知识点（流行病学数据、机制描述、已有研究结论等），为每个知识点通过 PubMed 检索 3-5 篇最相关文献，在原文句末插入 [PMID:XXXXXXXX] 标记，并生成独立的候选参考文献列表文件… |
| `format-extract` | 9.9K | ✓ | format.doc-audit(member) | `skills/format/format-extract.md` |
| ↳ | | | | 把 .docx 文档转为语义化 HTML + 提取内嵌图片（标题层级、表格样式、段落缩进、字体颜色等结构信息），供调用方做后续格式分析；也可独立评估 HTML 转换质量。适用场景（**技术性底层调用**）："docx 转 HTML"、"提取 docx 结构为 HTML"、"HTM… |
| `format-references-endnote` | 5.7K | ✓ | format.ref-bridge(member) | `skills/format/format-references-endnote.md` |
| ↳ | | | | EndNote 版文献排版工作流 — 将 Markdown 手稿中的 [PMID: xxxx] 标记转换为 Word (.docx)，使用 EndNote CWYW 识别的 {Author, Year, Title} 占位符，同时生成 .ris 文件自动导入本地 EndNote … |
| `format-references-zotero` | 7.2K | ✓ | format.ref-bridge(member) | `skills/format/format-references-zotero.md` |
| ↳ | | | | Zotero 版文献排版工作流。将 Markdown 手稿中的 [PMID: xxxx] 标记转换为 Word (.docx)，直接写入原生 Zotero 域代码（ADDIN ZOTERO_ITEM / ADDIN ZOTERO_BIBL），用户在 Word 中点一次「Refre… |
| `geng-academic-fraud-detector` | 8.7K | ✓ | format.doc-audit(member) | `skills/format/geng-academic-fraud-detector.md` |
| ↳ | | | | 学术论文打假检测器，致敬耿同学。分析学术论文 PDF，检测数据造假、图片复用/拼接、Western blot 操纵、统计异常等学术不端行为。当用户提供论文 PDF 要求"查重"、"打假"、"检测造假"、"论文分析"、"学术打假"时使用。 |
| `html-review` | 6.4K | ✓ | format.typeset(member) | `skills/format/html-review.md` |
| ↳ | | | | HTML 质量门禁 skill（路线 A + 路线 B 共享）。对 doc-typeset（路线 A）或 doc-edit（路线 B）输出的 HTML 进行 5 维度质量检测（design-token 合规性、结构完整性、排版合理性、文体契合度、装饰使用合理性），输出结构化检测报… |
| `html-to-doc` | 11.7K | ✓ | format.typeset(member)、format.final-delivery(member) | `skills/format/html-to-doc.md` |
| ↳ | | | | 将 HTML 整份转换为 .docx——一键脚本 scripts/convert_doc.py 自包含全流程：预检 → create → open → insert_html_content → save 直接写交付路径（产物即位，无中间拷贝）→ verify，结果 JSON 在… |
| `latex-output` | 5.4K | ✓ | format.final-delivery(member) | `skills/format/latex-output.md` |
| ↳ | | | | Use when user requests LaTeX format output or has provided school/journal LaTeX templates |
| `markitdown` | 12.3K | ✓ | format.doc-audit(member) | `skills/format/markitdown.md` |
| ↳ | | | | Convert files and office documents to Markdown. Supports PDF, DOCX, PPTX, XLSX, images (with OCR), audio (with transcription), HTML, CSV, JS… |
| `nature-citation` | 3.0K | ✓ | format.intext-cite(member) | `skills/format/nature-citation.md` |
| ↳ | | | | Find and verify Nature/CNS-family literature supporting manuscript claims, with claim-to-source mapping and reference-manager export. Use fo… |
| `nature-literature-pipeline` | 4.7K | ✓ | — | `skills/format/nature-literature-pipeline.md` |
| ↳ | | | | Complete automated literature discovery pipeline: multi-source search → six-dimension scoring → fine reading → formatted delivery → archival… |
| `nature-ref-verifier` | 9.5K | ✓ | format.ref-style(member)、literature.doi-validate(member)、literature.fact-check(member) | `skills/format/nature-ref-verifier.md` |
| ↳ | | | | 对学术文献逐条执行多源交叉验证，逐字段对比作者、标题、年份、卷期、页码， 标记卷年/DOI年冲突、作者顺序异常、页码偏差等问题，输出结构化验证报告。 可批量处理整篇论文/开题报告的参考文献列表，也可单条校验，支持与 Zotero 同步修正。 |
| `openalex-database` | 11.8K | ✓ | literature.doi-validate(member)、literature.citation-chase(member) | `skills/format/openalex-database.md` |
| ↳ | | | | Query and analyze scholarly literature using the OpenAlex database. This skill should be used when searching for academic papers, analyzing … |
| `paper-ct-scan` | 13.8K | ✓ | format.doc-audit(member)、format.submission-package(member) | `skills/format/wang-paper-ct.md` |
| ↳ | | | | 论文CT、论文检测、论文漏洞扫描、论文审校、论文体检、学术鉴真、论文真实性检测、论文可行性分析、 论文AI检测、论文排版检查、论文格式审查、学术论文质检、期刊论文审核、论文内容真伪鉴别、 论文参考文献核查、论文数据验证、国家级刊物论文检测、省级论文审核、论文发表前自检、 论文查重… |
| `paper-reference-formatter` | 3.3K | ✓ | format.ref-style(member) | `skills/format/paper-reference-formatter.md` |
| ↳ | | | | Format academic reference entries from user-provided journal article, thesis/dissertation, conference paper, book, report, preprint, or web … |
| `pdf` | 7.9K | ✓ | format.pdf-pipeline(member) | `skills/format/pdf.md` |
| ↳ | | | | Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining o… |
| `pdf` | 7.9K | ✓ | format.pdf-pipeline(member) | `skills/format/pdf-2.md` |
| ↳ | | | | Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining o… |
| `pdf-processing` | 1.6K | ✓ | format.pdf-pipeline(member) | `skills/format/pdf-processing.md` |
| ↳ | | | | Verify PDFs, hash-deduplicate files recoverably, normalize filenames, and create a final processing report. |
| `pdfkit-py` | 41.0K | ✓ | format.pdf-pipeline(member) | `skills/format/pdfkit-py.md` |
| ↳ | | | | 仅用于对已存在的 .pdf 文件进行处理（读取/提取/编辑/合并/拆分/转换/水印/加密/OCR/表单/签名）。当且仅当用户输入或工作区中存在 .pdf 文件，且操作对象是该 PDF 时使用。不处理 docx/xlsx/pptx/html/md/txt/图片等非 PDF 文件，不… |
| `pdfkit-py` | 41.0K | ✓ | format.pdf-pipeline(member) | `skills/format/pdfkit-py-2.md` |
| ↳ | | | | 仅用于对已存在的 .pdf 文件进行处理（读取/提取/编辑/合并/拆分/转换/水印/加密/OCR/表单/签名）。当且仅当用户输入或工作区中存在 .pdf 文件，且操作对象是该 PDF 时使用。不处理 docx/xlsx/pptx/html/md/txt/图片等非 PDF 文件，不… |
| `pubmed-database` | 15.2K | ✓ | format.cite-bind(member)、literature.search-plan(member) | `skills/format/pubmed-database.md` |
| ↳ | | | | Direct REST API access to PubMed. Advanced Boolean/MeSH queries, E-utilities API, batch processing, citation management. For Python workflow… |
| `pyzotero` | 4.3K | ✓ | format.ref-bridge(member)、literature.library(member) | `skills/format/pyzotero.md` |
| ↳ | | | | Interact with Zotero reference management libraries using the pyzotero Python client. Retrieve, create, update, and delete items, collection… |
| `qinyan-citation` | 6.8K | ✓ | format.ref-style(member) | `skills/format/qinyan-citation.md` |
| ↳ | | | | 沁言学术文献引用 - 先通过沁言学术OpenAPI检索文献，然后按照GB/T 7714、IEEE、APA、MLA、Chicago、Harvard等标准格式输出引用参考文献。严格遵循学术规范，未获取的信息保留省略号。触发词：文献引用、参考文献、引用格式、citation、refer… |
| `reference-verification` | 7.5K | ✓ | format.doc-audit(member)、literature.fact-check(member) | `skills/format/reference-verification.md` |
| ↳ | | | | 参考文献真伪核验技能。针对论文、研究报告、课题资料等学术文件，系统性地识别并核验全部参考文献条目的真实性。适用于：用户上传/提供论文/报告需要验证参考文献、怀疑文献存在编造或信息错误、毕业论文查重附带文献核查、课题结题验收前文献核实等场景。当用户提出"核验参考文献"、"验证文献真… |
| `scholar-analyze` | 80.4K | ✓ | — | `skills/format/scholar-analyze.md` |
| ↳ | | | | Run data analytics and produce publication-quality tables and visualizations for social science research. Saves regression tables (HTML/TeX/… |
| `scholar-auto-research` | 83.3K | ✓ | — | `skills/format/scholar-auto-research.md` |
| ↳ | | | | Stable, deterministic social-science research-paper pipeline from idea or data to verified manuscript, citations, replication package, and f… |
| `scholar-citation` | 34.8K | ✓ | format.intext-cite(member) | `skills/format/scholar-citation.md` |
| ↳ | | | | Full citation management for social science manuscripts. Eight modes: (1) INSERT — add in-text citations to uncited claims; (2) AUDIT — find… |
| `scholar-lit-review` | 56.8K | ✓ | literature.synthesis(member) | `skills/format/scholar-lit-review.md` |
| ↳ | | | | Conduct a systematic literature review that maps the current landscape of a research question. Produces a structured literature landscape ma… |
| `thesis-format-zh` | 2.0K | ✓ | — | `skills/format/thesis-format-zh.md` |
| ↳ | | | | 中文论文格式检查工具。解析学校模板docx，提取格式规则，对比论文生成差异报告。支持页边距/标题/正文/页眉/页码/三线表/引用格式检查。触发词：论文排版、格式检查、Word格式、毕业论文。 |
| `wecom-wedrive-reference` | 6.5K | ✓ | — | `skills/format/wecom-wedrive-reference.md` |
| ↳ | | | | Fetch the WeCom WeDrive files a user attached as references. Load this Skill whenever the host injects a `<wecom_wedrive_references>` block,… |
| `workbuddy-pdf` | 5.6K | ✓ | format.pdf-pipeline(member)、literature.fulltext-acquire(member)、literature.close-read(member) | `skills/format/workbuddy-pdf.md` |
| ↳ | | | | Read, summarize, search, and understand PDFs with the local workbuddy-pdf CLI. Use for PDF questions, text/table/image extraction, and check… |
| `workbuddy-sheet-generation` | 16.7K | ✓ | — | `skills/format/workbuddy-sheet-generation.md` |
| ↳ | | | | 生成一份全新的 Excel/xlsx 工作簿。触发条件是**意图为"生成新表"**——用户明确请求 "创建/生成/新建/做一份/整理成一份新表/汇总成新表/from scratch" 一个 XLSX 文件。 支持三类输入：① 纯文字需求；② 以 pdf/docx/pptx 附件作… |
| `workbuddy-sheetagent` | 1.7K | ✓ | — | `skills/format/workbuddy-sheetagent.md` |
| ↳ | | | | 编辑、查询、分析、清洗、透视、排序、筛选、格式化既有 Excel/xlsx/xls/csv 表格文件， 构造公式、生成图表、增删行列、合并单元格。 当用户上传、引用或指向一份**既有**表格文件、并对其做上述行为时使用。 当用户意图是从零产出一份新工作簿时改走 workbuddy… |
| `xlsx` | 8.7K | ✓ | format.figtable(member)、literature.evidence-matrix(member) | `skills/format/xlsx.md` |
| ↳ | | | | Full lifecycle for Excel files: create workbooks with formulas and formatting, build charts and pivot tables, read and clean data, batch-edi… |

## 数据获取与组学（40）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `adaptyv` | 3.7K | ✓ | — | `skills/data/adaptyv.md` |
| ↳ | | | | Cloud laboratory platform for automated protein testing and validation. Use when designing proteins and needing experimental validation incl… |
| `alphafold-database` | 16.0K | ✓ | data.protein-structure(member) | `skills/data/alphafold-database.md` |
| ↳ | | | | Access AlphaFold 200M+ AI-predicted protein structures. Retrieve structures by UniProt ID, download PDB/mmCIF files, analyze confidence metr… |
| `arf-explain-diff` | 8.2K | ✓ | — | `skills/data/arf-explain-diff.md` |
| ↳ | | | | Explain a code change as a standalone offline HTML page with a five-question quiz. Reads the diff and the surrounding code from scratch, sta… |
| `arf-paper-version` | 15.9K | ✓ | — | `skills/data/arf-paper-version.md` |
| ↳ | | | | Convert a LaTeX research paper into a policy brief, 1-page summary, or 5-page summary for a general audience, with factual review and a stan… |
| `bindingdb-database` | 11.8K | ✓ | data.chem-target(member) | `skills/data/bindingdb-database.md` |
| ↳ | | | | Query BindingDB for measured drug-target binding affinities (Ki, Kd, IC50, EC50). Search by target (UniProt ID), compound (SMILES/name), or … |
| `brenda-database` | 21.6K | ✓ | — | `skills/data/brenda-database.md` |
| ↳ | | | | Access BRENDA enzyme database via SOAP API. Retrieve kinetic parameters (Km, kcat), reaction equations, organism data, and substrate-specifi… |
| `cbioportal-database` | 12.8K | ✓ | data.expression-reuse(member) | `skills/data/cbioportal-database.md` |
| ↳ | | | | Query cBioPortal for cancer genomics data including somatic mutations, copy number alterations, gene expression, and survival data across hu… |
| `chembl-database` | 10.0K | ✓ | data.chem-target(member) | `skills/data/chembl-database.md` |
| ↳ | | | | Query ChEMBL bioactive molecules and drug discovery data. Search compounds by structure/properties, retrieve bioactivity data (IC50, Ki), fi… |
| `clinpgx-database` | 20.5K | ✓ | data.variant-annot(member) | `skills/data/clinpgx-database.md` |
| ↳ | | | | Access ClinPGx pharmacogenomics data (successor to PharmGKB). Query gene-drug interactions, CPIC guidelines, allele functions, for precision… |
| `clinvar-database` | 13.0K | ✓ | data.variant-annot(member)、data.provenance(member) | `skills/data/clinvar-database.md` |
| ↳ | | | | Query NCBI ClinVar for variant clinical significance. Search by gene/position, interpret pathogenicity classifications, access via E-utiliti… |
| `cobrapy` | 12.2K | ✓ | — | `skills/data/cobrapy.md` |
| ↳ | | | | Constraint-based metabolic modeling (COBRA). FBA, FVA, gene knockouts, flux sampling, SBML models, for systems biology and metabolic enginee… |
| `cosmic-database` | 9.8K | ✓ | — | `skills/data/cosmic-database.md` |
| ↳ | | | | Access COSMIC cancer mutation database. Query somatic mutations, Cancer Gene Census, mutational signatures, gene fusions, for cancer researc… |
| `depmap` | 11.0K | ✓ | data.expression-reuse(member) | `skills/data/depmap.md` |
| ↳ | | | | Query the Cancer Dependency Map (DepMap) for cancer cell line gene dependency scores (CRISPR Chronos), drug sensitivity data, and gene effec… |
| `dnanexus-integration` | 10.4K | ✓ | — | `skills/data/dnanexus-integration.md` |
| ↳ | | | | DNAnexus cloud genomics platform. Build apps/applets, manage data (upload/download), dxpy Python SDK, run workflows, FASTQ/BAM/VCF, for geno… |
| `drugbank-database` | 9.2K | ✓ | — | `skills/data/drugbank-database.md` |
| ↳ | | | | Access and analyze comprehensive drug information from the DrugBank database including drug properties, interactions, targets, pathways, che… |
| `ena-database` | 6.9K | ✓ | data.omics-download(member) | `skills/data/ena-database.md` |
| ↳ | | | | Access European Nucleotide Archive via API/FTP. Retrieve DNA/RNA sequences, raw reads (FASTQ), genome assemblies by accession, for genomics … |
| `ensembl-database` | 8.1K | ✓ | data.gene-idmap(member) | `skills/data/ensembl-database.md` |
| ↳ | | | | Query Ensembl genome database REST API for 250+ species. Gene lookups, sequence retrieval, variant analysis, comparative genomics, orthologs… |
| `gene-database` | 6.2K | ✓ | data.gene-idmap(member) | `skills/data/gene-database.md` |
| ↳ | | | | Query NCBI Gene via E-utilities/Datasets API. Search by symbol/ID, retrieve gene info (RefSeqs, GO, locations, phenotypes), batch lookups, f… |
| `geo-database` | 24.0K | ✓ | data.omics-download(member)、data.provenance(member) | `skills/data/geo-database.md` |
| ↳ | | | | Access NCBI GEO for gene expression/genomics data. Search/download microarray and RNA-seq datasets (GSE, GSM, GPL), retrieve SOFT/Matrix fil… |
| `ginkgo-cloud-lab` | 3.4K | ✓ | — | `skills/data/ginkgo-cloud-lab.md` |
| ↳ | | | | Submit and manage protocols on Ginkgo Bioworks Cloud Lab (cloud.ginkgo.bio), a web-based interface for autonomous lab execution on Reconfigu… |
| `glycoengineering` | 12.2K | ✓ | — | `skills/data/glycoengineering.md` |
| ↳ | | | | Analyze and engineer protein glycosylation. Scan sequences for N-glycosylation sequons (N-X-S/T), predict O-glycosylation hotspots, and acce… |
| `gnomad-database` | 12.2K | ✓ | data.variant-annot(member)、data.gwas-eqtl(member) | `skills/data/gnomad-database.md` |
| ↳ | | | | Query gnomAD (Genome Aggregation Database) for population allele frequencies, variant constraint scores (pLI, LOEUF), and loss-of-function i… |
| `gtex-database` | 10.8K | ✓ | data.expression-reuse(member) | `skills/data/gtex-database.md` |
| ↳ | | | | Query GTEx (Genotype-Tissue Expression) portal for tissue-specific gene expression, eQTLs (expression quantitative trait loci), and sQTLs. E… |
| `gwas-database` | 19.6K | ✓ | data.gwas-eqtl(member)、data.provenance(member) | `skills/data/gwas-database.md` |
| ↳ | | | | Query NHGRI-EBI GWAS Catalog for SNP-trait associations. Search variants by rs ID, disease/trait, gene, retrieve p-values and summary statis… |
| `hmdb-database` | 7.8K | ✓ | data.metab-omics(member) | `skills/data/hmdb-database.md` |
| ↳ | | | | Access Human Metabolome Database (220K+ metabolites). Search by name/ID/structure, retrieve chemical properties, biomarker data, NMR/MS spec… |
| `interpro-database` | 10.5K | ✓ | data.protein-structure(member) | `skills/data/interpro-database.md` |
| ↳ | | | | Query InterPro for protein family, domain, and functional site annotations. Integrates Pfam, PANTHER, PRINTS, SMART, SUPERFAMILY, and 11 oth… |
| `jaspar-database` | 11.7K | ✓ | data.variant-annot(member) | `skills/data/jaspar-database.md` |
| ↳ | | | | Query JASPAR for transcription factor binding site (TFBS) profiles (PWMs/PFMs). Search by TF name, species, or class; scan DNA sequences for… |
| `kegg-database` | 11.5K | ✓ | data.pathway-ppi(member) | `skills/data/kegg-database.md` |
| ↳ | | | | Direct REST API access to KEGG (academic use only). Pathway analysis, gene-pathway mapping, metabolic pathways, drug interactions, ID conver… |
| `latchbio-integration` | 9.6K | ✓ | — | `skills/data/latchbio-integration.md` |
| ↳ | | | | Latch platform for bioinformatics workflows. Build pipelines with Latch SDK, @workflow/@task decorators, deploy serverless workflows, LatchF… |
| `metabolomics-workbench-database` | 10.1K | ✓ | data.metab-omics(member) | `skills/data/metabolomics-workbench-database.md` |
| ↳ | | | | Access NIH Metabolomics Workbench via REST API (4,200+ studies). Query metabolites, RefMet nomenclature, MS/NMR data, m/z searches, study me… |
| `opentargets-database` | 13.7K | ✓ | data.expression-reuse(member) | `skills/data/opentargets-database.md` |
| ↳ | | | | Query Open Targets Platform for target-disease associations, drug target discovery, tractability/safety data, genetics/omics evidence, known… |
| `pdb-database` | 9.0K | ✓ | data.protein-structure(member) | `skills/data/pdb-database.md` |
| ↳ | | | | Access RCSB PDB for 3D protein/nucleic acid structures. Search by text/sequence/structure, download coordinates (PDB/mmCIF), retrieve metada… |
| `pubchem-database` | 15.9K | ✓ | data.chem-target(member) | `skills/data/pubchem-database.md` |
| ↳ | | | | Query PubChem via PUG-REST API/PubChemPy (110M+ compounds). Search by name/CID/SMILES, retrieve properties, similarity/substructure searches… |
| `r-pharmacology-singlecell-mr` | 7.4K | ✓ | data.gene-idmap(member)、data.gwas-eqtl(member) | `skills/data/r-pharmacology-singlecell-mr.md` |
| ↳ | | | | 网络药理学与单细胞测序 R 语言实战技能。覆盖中药/药物成分-靶点网络构建与通路富集（KEGG/GO，clusterProfiler + org.Hs.eg.db + bitr 映射 + 气泡图/Facet 条形图 + 基因-通路表构建）、STRING 蛋白互作与交集、药靶孟德尔… |
| `reactome-database` | 7.7K | ✓ | data.pathway-ppi(member) | `skills/data/reactome-database.md` |
| ↳ | | | | Query Reactome REST API for pathway analysis, enrichment, gene-pathway mapping, disease pathways, molecular interactions, expression analysi… |
| `scientific-thinking-biology` | 11.3K | ✓ | figures.mechanism(member) | `skills/data/scientific-thinking-biology.md` |
| ↳ | | | | Use when interpreting biological research findings, evaluating life science evidence, analyzing molecular or cellular mechanisms, comparing … |
| `string-database` | 17.8K | ✓ | data.pathway-ppi(member)、data.provenance(member) | `skills/data/string-database.md` |
| ↳ | | | | Query STRING API for protein-protein interactions (59M proteins, 20B interactions). Network analysis, GO/KEGG enrichment, interaction discov… |
| `uniprot-database` | 6.6K | ✓ | data.gene-idmap(member) | `skills/data/uniprot-database.md` |
| ↳ | | | | Direct REST API access to UniProt. Protein searches, FASTA retrieval, ID mapping, Swiss-Prot/TrEMBL. For Python workflows with multiple data… |
| `wos-search` | 2.9K | ✓ | ideation.novelty(member)、literature.search-plan(member)、literature.federated-search(member) | `skills/data/wos-search.md` |
| ↳ | | | | Build and execute a configuration-driven Web of Science advanced search and export Full Record metadata. |
| `zinc-database` | 13.6K | ✓ | data.chem-target(member) | `skills/data/zinc-database.md` |
| ↳ | | | | Access ZINC (230M+ purchasable compounds). Search by ZINC ID/SMILES, similarity searches, 3D-ready structures for docking, analog discovery,… |

## 工具箱（索引桶，不建能力卡）（100）

| 技能名 | 体积 | 科研 | 被能力卡引用 | 文件 |
|---|---:|:--:|---|---|
| `airs-academic-plotting` | 21.1K | ✓ | — | `skills/toolbox/airs-academic-plotting.md` |
| ↳ | | | | Generates publication-quality figures for ML papers from research context. Given a paper section or description, extracts system components … |
| `airs-ara-compiler` | 14.8K | ✓ | — | `skills/toolbox/airs-ara-compiler.md` |
| ↳ | | | | Compiles any research input — PDF papers, GitHub repositories, experiment logs, code directories, or raw notes — into a complete Agent-Nativ… |
| `airs-ara-research-manager` | 12.7K | ✓ | — | `skills/toolbox/airs-ara-research-manager.md` |
| ↳ | | | | Records research provenance as a post-task epilogue, scanning conversation history at the end of a coding or research session to extract dec… |
| `airs-ara-rigor-reviewer` | 17.7K | ✓ | — | `skills/toolbox/airs-ara-rigor-reviewer.md` |
| ↳ | | | | Performs ARA Seal Level 2 semantic epistemic review on Agent-Native Research Artifacts, scoring six dimensions (evidence relevance, falsifia… |
| `airs-brainstorming-research-ideas` | 19.1K | ✓ | ideation.topic(member) | `skills/toolbox/airs-brainstorming-research-ideas.md` |
| ↳ | | | | Guides researchers through structured ideation frameworks to discover high-impact research directions. Use when exploring new problem spaces… |
| `airs-creative-thinking-for-research` | 21.8K | ✓ | — | `skills/toolbox/airs-creative-thinking-for-research.md` |
| ↳ | | | | Applies cognitive science frameworks for creative thinking to CS and AI research ideation. Use when seeking genuinely novel research directi… |
| `airs-ml-paper-writing` | 37.7K | ✓ | — | `skills/toolbox/airs-ml-paper-writing.md` |
| ↳ | | | | Write publication-ready ML/AI papers for NeurIPS, ICML, ICLR, ACL, AAAI, COLM. Use when drafting papers from research repos, structuring arg… |
| `airs-presenting-conference-talks` | 10.3K | ✓ | — | `skills/toolbox/airs-presenting-conference-talks.md` |
| ↳ | | | | Generates conference presentation slides (Beamer LaTeX PDF and editable PPTX) from a compiled paper with speaker notes and talk script. Use … |
| `airs-segment-anything-model` | 13.6K | ✓ | figures.imaging(member) | `skills/toolbox/airs-segment-anything-model.md` |
| ↳ | | | | Foundation model for image segmentation with zero-shot transfer. Use when you need to segment any object in images using points, boxes, or m… |
| `airs-systems-paper-writing` | 14.3K | ✓ | — | `skills/toolbox/airs-systems-paper-writing.md` |
| ↳ | | | | Comprehensive guide for writing systems papers targeting OSDI, SOSP, ASPLOS, NSDI, and EuroSys. Provides paragraph-level structural blueprin… |
| `anndata` | 10.0K | ✓ | — | `skills/toolbox/anndata.md` |
| ↳ | | | | Data structure for annotated matrices in single-cell analysis. Use when working with .h5ad files or integrating with the scverse ecosystem. … |
| `arboreto` | 6.8K | ✓ | — | `skills/toolbox/arboreto.md` |
| ↳ | | | | Infer gene regulatory networks (GRNs) from gene expression data using scalable algorithms (GRNBoost2, GENIE3). Use when analyzing transcript… |
| `arf-audit-analysis` | 4.4K | ✓ | — | `skills/toolbox/arf-audit-analysis.md` |
| ↳ | | | | Adversarially audit changed analysis code against a base ref, hunting for correctness errors in sample construction, merges, variable constr… |
| `aris-proof-checker` | 56.2K | ✓ | — | `skills/toolbox/aris-proof-checker.md` |
| ↳ | | | | Rigorous mathematical proof verification and fixing workflow. Reads a LaTeX proof, identifies gaps via cross-model review (external reviewer… |
| `aris-research-pipeline` | 24.1K | ✓ | — | `skills/toolbox/aris-research-pipeline.md` |
| ↳ | | | | "Full end-to-end research pipeline: from a broad research direction through idea discovery, experiments, and review all the way to a polishe… |
| `biopython` | 13.5K | ✓ | — | `skills/toolbox/biopython.md` |
| ↳ | | | | Comprehensive molecular biology toolkit. Use for sequence manipulation, file parsing (FASTA/GenBank/PDB), phylogenetics, and programmatic NC… |
| `bioservices` | 9.7K | ✓ | — | `skills/toolbox/bioservices.md` |
| ↳ | | | | Unified Python interface to 40+ bioinformatics services. Use when querying multiple databases (UniProt, KEGG, ChEMBL, Reactome) in a single … |
| `cellxgene-census` | 15.1K | ✓ | — | `skills/toolbox/cellxgene-census.md` |
| ↳ | | | | Query the CELLxGENE Census (61M+ cells) programmatically. Use when you need expression data across tissues, diseases, or cell types from the… |
| `clinical-decision-copilot` | 17.0K | ✓ | — | `skills/toolbox/clinical-decision-copilot.md` |
| ↳ | | | | 临床诊疗思路助手。当用户给出症状、体征、化验或影像结果，需要「下一步查什么 / 怎么判读 / 用什么药 / 处方怎么写（含剂量、频次、静脉输液速度、微量泵如何配置与泵速）/ 要不要手术 / 要不要做侵入性检查 / 怎么监测 / 何时升级降级」时使用。**核心内容层是 skill … |
| `consciousness-council` | 8.5K | ✓ | — | `skills/toolbox/consciousness-council.md` |
| ↳ | | | | Run a multi-perspective Mind Council deliberation on any question, decision, or creative challenge. Use this skill whenever the user wants d… |
| `dask` | 14.0K | ✓ | — | `skills/toolbox/dask.md` |
| ↳ | | | | Distributed computing for larger-than-RAM pandas/NumPy workflows. Use when you need to scale existing pandas/NumPy code beyond memory or acr… |
| `datamol` | 18.4K | ✓ | — | `skills/toolbox/datamol.md` |
| ↳ | | | | Pythonic wrapper around RDKit with simplified interface and sensible defaults. Preferred for standard drug discovery including SMILES parsin… |
| `deepchem` | 17.4K | ✓ | — | `skills/toolbox/deepchem.md` |
| ↳ | | | | Molecular ML with diverse featurizers and pre-built datasets. Use for property prediction (ADMET, toxicity) with traditional ML or GNNs when… |
| `deeptools` | 17.6K | ✓ | — | `skills/toolbox/deeptools.md` |
| ↳ | | | | NGS analysis toolkit. BAM to bigWig conversion, QC (correlation, PCA, fingerprints), heatmaps/profiles (TSS, peaks), for ChIP-seq, RNA-seq, … |
| `denario` | 5.9K | ✓ | — | `skills/toolbox/denario.md` |
| ↳ | | | | Multiagent AI system for scientific research assistance that automates research workflows from data analysis to publication. This skill shou… |
| `diffdock` | 15.1K | ✓ | — | `skills/toolbox/diffdock.md` |
| ↳ | | | | Diffusion-based molecular docking. Predict protein-ligand binding poses from PDB/SMILES, confidence scores, virtual screening, for structure… |
| `duckdb-attach-db` | 4.9K | ✓ | — | `skills/toolbox/duckdb-attach-db.md` |
| ↳ | | | | > Attach a DuckDB database file for use with /duckdb-skills:query. Explores the schema (tables, columns, row counts) and writes a SQL state … |
| `duckdb-convert-file` | 2.9K | ✓ | — | `skills/toolbox/duckdb-convert-file.md` |
| ↳ | | | | > Convert any data file to another format: CSV, Parquet, JSON, Excel, GeoJSON, and more. Use when the user says "convert to parquet", "save … |
| `duckdb-docs` | 5.6K | ✓ | — | `skills/toolbox/duckdb-duckdb-docs.md` |
| ↳ | | | | Search DuckDB and DuckLake documentation and blog posts. Returns relevant doc chunks for a question or keyword using full-text search agains… |
| `duckdb-install-duckdb` | 2.4K | ✓ | — | `skills/toolbox/duckdb-install-duckdb.md` |
| ↳ | | | | > Install or update DuckDB extensions. Each argument is either a plain extension name (installs from core) or name@repo (e.g. magic@communit… |
| `duckdb-query` | 8.0K | ✓ | — | `skills/toolbox/duckdb-query.md` |
| ↳ | | | | > Run SQL queries against the attached DuckDB database or ad-hoc against files. Accepts raw SQL or natural language questions. Uses DuckDB F… |
| `duckdb-read-file` | 3.7K | ✓ | — | `skills/toolbox/duckdb-read-file.md` |
| ↳ | | | | > Read any data file (CSV, JSON, Parquet, Avro, Excel, spatial, SQLite) or remote URL (S3, HTTPS). Use when user references a data file, ask… |
| `duckdb-s3-explore` | 3.4K | ✓ | — | `skills/toolbox/duckdb-s3-explore.md` |
| ↳ | | | | > Explore and query data on S3, Cloudflare R2, GCS, MinIO, or any S3-compatible storage. Use when the user mentions an s3://, r2://, gs://, … |
| `duckdb-spatial` | 4.1K | ✓ | — | `skills/toolbox/duckdb-spatial.md` |
| ↳ | | | | > Answer questions about spatial data using DuckDB. Use when the user mentions locations, coordinates, lat/lng, distances, maps, addresses, … |
| `environment-setup` | 3.9K | ✓ | — | `skills/toolbox/environment-setup.md` |
| ↳ | | | | Use when Python environment setup is needed for data visualization or conda installation is required |
| `esm` | 10.3K | ✓ | — | `skills/toolbox/esm.md` |
| ↳ | | | | Comprehensive toolkit for protein language models including ESM3 (generative multimodal protein design across sequence, structure, and funct… |
| `etetoolkit` | 17.5K | ✓ | — | `skills/toolbox/etetoolkit.md` |
| ↳ | | | | Phylogenetic tree toolkit (ETE). Tree manipulation (Newick/NHX), evolutionary event detection, orthology/paralogy, NCBI taxonomy, visualizat… |
| `experiment-results-planning` | 3.9K | ✓ | ideation.design(member) | `skills/toolbox/experiment-results-planning.md` |
| ↳ | | | | Use when designing experiments, result tables, mock planning data, evaluation protocols, or results sections before real data are final |
| `flowio` | 16.4K | ✓ | — | `skills/toolbox/flowio.md` |
| ↳ | | | | Parse FCS (Flow Cytometry Standard) files v2.0-3.1. Extract events as NumPy arrays, read metadata/channels, convert to CSV/DataFrame, for fl… |
| `geniml` | 9.9K | ✓ | — | `skills/toolbox/geniml.md` |
| ↳ | | | | This skill should be used when working with genomic interval data (BED files) for machine learning tasks. Use for training region embeddings… |
| `get-available-resources` | 9.6K | ✓ | — | `skills/toolbox/get-available-resources.md` |
| ↳ | | | | This skill should be used at the start of any computationally intensive scientific task to detect and report available system resources (CPU… |
| `gget` | 24.5K | ✓ | — | `skills/toolbox/gget.md` |
| ↳ | | | | Fast CLI/Python queries to 20+ bioinformatics databases. Use for quick lookups: gene info, BLAST searches, AlphaFold structures, enrichment … |
| `gtars` | 7.6K | ✓ | — | `skills/toolbox/gtars.md` |
| ↳ | | | | High-performance toolkit for genomic interval analysis in Rust with Python bindings. Use when working with genomic regions, BED files, cover… |
| `histolab` | 19.7K | ✓ | figures.imaging(member) | `skills/toolbox/histolab.md` |
| ↳ | | | | Lightweight WSI tile extraction and preprocessing. Use for basic slide processing tissue detection, tile extraction, stain normalization for… |
| `iso-13485-certification` | 22.7K | ✓ | — | `skills/toolbox/iso-13485-certification.md` |
| ↳ | | | | Comprehensive toolkit for preparing ISO 13485 certification documentation for medical device Quality Management Systems. Use when users need… |
| `lamindb` | 14.0K | ✓ | — | `skills/toolbox/lamindb.md` |
| ↳ | | | | This skill should be used when working with LaminDB, an open-source data framework for biology that makes data queryable, traceable, reprodu… |
| `matchms` | 6.8K | ✓ | — | `skills/toolbox/matchms.md` |
| ↳ | | | | Spectral similarity and compound identification for metabolomics. Use for comparing mass spectra, computing similarity scores (cosine, modif… |
| `medchem` | 9.9K | ✓ | — | `skills/toolbox/medchem.md` |
| ↳ | | | | Medicinal chemistry filters. Apply drug-likeness rules (Lipinski, Veber), PAINS filters, structural alerts, complexity metrics, for compound… |
| `molecular-dynamics` | 14.4K | ✓ | — | `skills/toolbox/molecular-dynamics.md` |
| ↳ | | | | Run and analyze molecular dynamics simulations with OpenMM and MDAnalysis. Set up protein/small molecule systems, define force fields, run e… |
| `molfeat` | 14.5K | ✓ | — | `skills/toolbox/molfeat.md` |
| ↳ | | | | Molecular featurization for ML (100+ featurizers). ECFP, MACCS, descriptors, pretrained models (ChemBERTa), convert SMILES to features, for … |
| `monarch-database` | 12.5K | ✓ | — | `skills/toolbox/monarch-database.md` |
| ↳ | | | | Query the Monarch Initiative knowledge graph for disease-gene-phenotype associations across species. Integrates OMIM, ORPHANET, HPO, ClinVar… |
| `networkx` | 12.4K | ✓ | — | `skills/toolbox/networkx.md` |
| ↳ | | | | Comprehensive toolkit for creating, analyzing, and visualizing complex networks and graphs in Python. Use when working with network/graph da… |
| `neurokit2` | 11.7K | ✓ | — | `skills/toolbox/neurokit2.md` |
| ↳ | | | | Comprehensive biosignal processing toolkit for analyzing physiological data including ECG, EEG, EDA, RSP, PPG, EMG, and EOG signals. Use thi… |
| `neuropixels-analysis` | 11.3K | ✓ | — | `skills/toolbox/neuropixels-analysis.md` |
| ↳ | | | | Neuropixels neural recording analysis. Load SpikeGLX/OpenEphys data, preprocess, motion correction, Kilosort4 spike sorting, quality metrics… |
| `omero-integration` | 7.9K | ✓ | — | `skills/toolbox/omero-integration.md` |
| ↳ | | | | Microscopy data management platform. Access images via Python, retrieve datasets, analyze pixels, manage ROIs/annotations, batch processing,… |
| `parallel-web` | 11.4K | ✓ | — | `skills/toolbox/parallel-web.md` |
| ↳ | | | | Search the web, extract URL content, and run deep research using the Parallel Chat API and Extract API. Use for ALL web searches, research q… |
| `perplexity-search` | 13.8K | ✓ | — | `skills/toolbox/perplexity-search.md` |
| ↳ | | | | Perform AI-powered web searches with real-time information using Perplexity models via LiteLLM and OpenRouter. This skill should be used whe… |
| `phylogenetics` | 13.6K | ✓ | — | `skills/toolbox/phylogenetics.md` |
| ↳ | | | | Build and analyze phylogenetic trees using MAFFT (multiple alignment), IQ-TREE 2 (maximum likelihood), and FastTree (fast NJ/ML). Visualize … |
| `polars` | 9.2K | ✓ | — | `skills/toolbox/polars.md` |
| ↳ | | | | Fast in-memory DataFrame library for datasets that fit in RAM. Use when pandas is too slow but data still fits in memory. Lazy evaluation, p… |
| `protocolsio-integration` | 14.6K | ✓ | — | `skills/toolbox/protocolsio-integration.md` |
| ↳ | | | | Integration with protocols.io API for managing scientific protocols. This skill should be used when working with protocols.io to search, cre… |
| `pydeseq2` | 15.8K | ✓ | — | `skills/toolbox/pydeseq2.md` |
| ↳ | | | | Differential gene expression analysis (Python DESeq2). Identify DE genes from bulk RNA-seq counts, Wald tests, FDR correction, volcano/MA pl… |
| `pydicom` | 12.9K | ✓ | figures.imaging(member) | `skills/toolbox/pydicom.md` |
| ↳ | | | | Python library for working with DICOM (Digital Imaging and Communications in Medicine) files. Use this skill when reading, writing, or modif… |
| `pyhealth` | 17.2K | ✓ | — | `skills/toolbox/pyhealth.md` |
| ↳ | | | | Comprehensive healthcare AI toolkit for developing, testing, and deploying machine learning models with clinical data. This skill should be … |
| `pymoo` | 16.4K | ✓ | — | `skills/toolbox/pymoo.md` |
| ↳ | | | | Multi-objective optimization framework. NSGA-II, NSGA-III, MOEA/D, Pareto fronts, constraint handling, benchmarks (ZDT, DTLZ), for engineeri… |
| `pyopenms` | 5.5K | ✓ | — | `skills/toolbox/pyopenms.md` |
| ↳ | | | | Complete mass spectrometry analysis platform. Use for proteomics workflows feature detection, peptide identification, protein quantification… |
| `pysam` | 9.8K | ✓ | — | `skills/toolbox/pysam.md` |
| ↳ | | | | Genomic file toolkit. Read/write SAM/BAM/CRAM alignments, VCF/BCF variants, FASTA/FASTQ sequences, extract regions, calculate coverage, for … |
| `pytdc` | 12.4K | ✓ | — | `skills/toolbox/pytdc.md` |
| ↳ | | | | Therapeutics Data Commons. AI-ready drug discovery datasets (ADME, toxicity, DTI), benchmarks, scaffold splits, molecular oracles, for thera… |
| `pytorch-lightning` | 6.5K | ✓ | — | `skills/toolbox/pytorch-lightning.md` |
| ↳ | | | | Deep learning framework (PyTorch Lightning). Organize PyTorch code into LightningModules, configure Trainers for multi-GPU/TPU, implement da… |
| `rare-disease-diagnosis` | 7.1K | ✓ | — | `skills/toolbox/rare-disease-diagnosis.md` |
| ↳ | | | | 通用疑难病文献诊断专家（覆盖全部临床科室）。结合患者症状、体征、辅助检查提取精准英文医学关键词，检索 PubMed/Google Scholar 等 SCI 数据库，为各科疑难罕见病提供循证鉴别诊断线索，并生成中文文献综述。适用于：任何专科（神经、心血管、呼吸、消化、风湿免疫、血… |
| `rdkit` | 19.9K | ✓ | — | `skills/toolbox/rdkit.md` |
| ↳ | | | | Cheminformatics toolkit for fine-grained molecular control. SMILES/SDF parsing, descriptors (MW, LogP, TPSA), fingerprints, substructure sea… |
| `research` | 4.2K | ✓ | — | `skills/toolbox/research.md` |
| ↳ | | | | Conduct preliminary research on a topic and generate research outline. For academic research, benchmark research, technology selection, etc. |
| `research-add-fields` | 0.8K | ✓ | — | `skills/toolbox/research-add-fields.md` |
| ↳ | | | | Add field definitions to existing research outline. |
| `research-add-items` | 0.7K | ✓ | — | `skills/toolbox/research-add-items.md` |
| ↳ | | | | Add items (research objects) to existing research outline. |
| `research-proposal` | 19.7K | ✓ | ideation.grant(member) | `skills/toolbox/research-proposal.md` |
| ↳ | | | | Generate academic research proposals for PhD applications. Use when user asks to "write a research proposal", "create PhD proposal", "genera… |
| `research-report` | 3.7K | ✓ | — | `skills/toolbox/research-report.md` |
| ↳ | | | | Summarize deep research results into markdown report, cover all fields, skip uncertain values. |
| `scanpy` | 11.1K | ✓ | — | `skills/toolbox/scanpy.md` |
| ↳ | | | | Standard single-cell RNA-seq analysis pipeline. Use for QC, normalization, dimensionality reduction (PCA/UMAP/t-SNE), clustering, differenti… |
| `scholar-annotate` | 18.0K | ✓ | — | `skills/toolbox/scholar-annotate.md` |
| ↳ | | | | Turn unstructured text into validated, structured variables at corpus scale with LLMs: codebook design, dev/gold-set construction, DSPy prom… |
| `scholar-auto-improve` | 31.5K | ✓ | — | `skills/toolbox/scholar-auto-improve.md` |
| ↳ | | | | Automatic quality auditor and continuous improvement engine for the scholar-skill suite. Four modes: (1) OBSERVE — post-skill output audit (… |
| `scholar-collaborate` | 22.5K | ✓ | — | `skills/toolbox/scholar-collaborate.md` |
| ↳ | | | | Multi-author research collaboration management. Covers CRediT role assignment, task delegation and tracking, co-author communication templat… |
| `scholar-compute` | 57.6K | ✓ | — | `skills/toolbox/scholar-compute.md` |
| ↳ | | | | Design and execute computational social science analyses across 11 modules: text-as-data/NLP (STM, BERTopic, Wordfish, BERT, conText embeddi… |
| `scholar-knowledge` | 66.8K | ✓ | — | `skills/toolbox/scholar-knowledge.md` |
| ↳ | | | | User-scoped, cross-project knowledge graph that persists extracted intellectual content (findings, mechanisms, theories, paper relationships… |
| `scholar-open` | 56.6K | ✓ | ideation.ethics(member) | `skills/toolbox/scholar-open.md` |
| ↳ | | | | Implement open science practices for a social science study. Five modes: (1) PREREGISTER — OSF / AsPredicted / EGAP / Registered Reports; se… |
| `scholar-qual` | 61.6K | ✓ | — | `skills/toolbox/scholar-qual.md` |
| ↳ | | | | Qualitative research methods toolkit for social sciences. Covers codebook development, grounded theory coding (open, axial, selective), Brau… |
| `scholar-rag` | 29.2K | ✓ | — | `skills/toolbox/scholar-rag.md` |
| ↳ | | | | Build and query a local vector database + GraphRAG over your entire reference library (Zotero or a PDF folder) for literature review. Downlo… |
| `scholar-replication` | 73.5K | ✓ | — | `skills/toolbox/scholar-replication.md` |
| ↳ | | | | Build, document, test, and validate a journal-ready replication package for social science research. Six modes: (1) BUILD — assemble scripts… |
| `scikit-bio` | 14.4K | ✓ | — | `skills/toolbox/scikit-bio.md` |
| ↳ | | | | Biological data toolkit. Sequence analysis, alignments, phylogenetic trees, diversity metrics (alpha/beta, UniFrac), ordination (PCoA), PERM… |
| `scvelo` | 10.0K | ✓ | — | `skills/toolbox/scvelo.md` |
| ↳ | | | | RNA velocity analysis with scVelo. Estimate cell state transitions from unspliced/spliced mRNA dynamics, infer trajectory directions, comput… |
| `scvi-tools` | 7.1K | ✓ | — | `skills/toolbox/scvi-tools.md` |
| ↳ | | | | Deep generative models for single-cell omics. Use when you need probabilistic batch correction (scVI), transfer learning, differential expre… |
| `simpy` | 11.9K | ✓ | — | `skills/toolbox/simpy.md` |
| ↳ | | | | Process-based discrete-event simulation framework in Python. Use this skill when building simulations of systems with processes, queues, res… |
| `summarize` | 2.5K | ✓ | — | `skills/toolbox/summarize.md` |
| ↳ | | | | 智能内容摘要工具，支持长文本、文档、网页内容自动摘要，提取核心要点、关键词，支持自定义摘要长度。 |
| `sympy` | 13.2K | ✓ | — | `skills/toolbox/sympy.md` |
| ↳ | | | | Use this skill when working with symbolic mathematics in Python. This skill should be used for symbolic computation tasks including solving … |
| `sync-docs` | 8.4K | ✓ | — | `skills/toolbox/sync-docs.md` |
| ↳ | | | | Synchronize content across presentation slides, speaker script, and manuscript/paper. Audits for stale references, numbers, citations, and v… |
| `tiledbvcf` | 15.0K | ✓ | — | `skills/toolbox/tiledbvcf.md` |
| ↳ | | | | Efficient storage and retrieval of genomic variant data using TileDB. Scalable VCF/BCF ingestion, incremental sample addition, compressed st… |
| `torch-geometric` | 19.9K | ✓ | — | `skills/toolbox/torch-geometric.md` |
| ↳ | | | | Graph Neural Networks (PyG). Node/graph classification, link prediction, GCN, GAT, GraphSAGE, heterogeneous graphs, molecular property predi… |
| `torchdrug` | 13.8K | ✓ | — | `skills/toolbox/torchdrug.md` |
| ↳ | | | | PyTorch-native graph neural networks for molecules and proteins. Use when building custom GNN architectures for drug discovery, protein mode… |
| `treatment-plans` | 51.5K | ✓ | — | `skills/toolbox/treatment-plans.md` |
| ↳ | | | | Generate concise (3-4 page), focused medical treatment plans in LaTeX/PDF format for all clinical specialties. Supports general medical trea… |
| `vaex` | 6.4K | ✓ | — | `skills/toolbox/vaex.md` |
| ↳ | | | | Use this skill for processing and analyzing large tabular datasets (billions of rows) that exceed available RAM. Vaex excels at out-of-core … |
| `web-access` | 18.5K | ✓ | — | `skills/toolbox/web-access.md` |
| ↳ | | | | 所有联网操作必须通过此 skill 处理，包括：搜索、网页抓取、登录后操作、网络交互等。 触发场景：用户要求搜索信息、查看网页内容、访问需要登录的网站、操作网页界面、抓取社交媒体内容（小红书、微博、推特等）、读取动态渲染页面、以及任何需要真实浏览器环境的网络任务。 |
| `what-if-oracle` | 9.3K | ✓ | — | `skills/toolbox/what-if-oracle.md` |
| ↳ | | | | Run structured What-If scenario analysis with multi-branch possibility exploration. Use this skill when the user asks speculative questions … |
| `zarr-python` | 19.6K | ✓ | — | `skills/toolbox/zarr-python.md` |
| ↳ | | | | Chunked N-D arrays for cloud storage. Compressed arrays, parallel I/O, S3/GCS integration, NumPy/Dask/Xarray compatible, for large-scale sci… |
