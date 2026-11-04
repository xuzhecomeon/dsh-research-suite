<!-- source: academic-reference-enhancer @ academic-reference-enhancer__skillhub | domain: literature -->

---
name: academic-reference-enhancer
description: Add, verify, format, and insert academic references for papers, thesis chapters, technical reports, stage reports, Markdown, Word, LaTeX, PDF-derived text, or Feishu documents. Use when Codex needs to find references from document content, verify candidate reference authenticity, format references such as GB/T 7714, check journal-paper ratios, plan citation insertion positions, or modify a formal document after user confirmation.
---

# Academic Reference Enhancer

Use this skill to turn a draft paper, thesis chapter, report, or candidate reference list into a citation-ready document. Verify before citing, plan before modifying, and never fabricate references.

## Core Rules

- Do not fabricate references, DOI values, page ranges, volume/issue numbers, authors, journal names, or publication status.
- Do not treat preprints as journal articles unless a formal journal version is verified.
- Do not treat conference papers, standards, regulations, datasets, blogs, or web pages as journal articles.
- Do not use blogs, repost sites, personal pages, ResearchGate, or random PDF mirrors as the only authenticity evidence.
- Do not keep suspicious references just to satisfy quantity or ratio requirements.
- Use each reference to support a specific claim in the document.
- Reuse one number for the same reference throughout the document.
- Number references by first appearance unless the user explicitly requests chapter-level numbering.
- Mark unverifiable or conflicting references clearly and suggest replacements.
- Do not modify the user's official source document before explicit confirmation. Draft reports, candidate lists, and verification tables may be created before confirmation.

## Mode Selection

Choose the smallest mode that satisfies the request.

- **Discovery Mode**: Use when the user has a document but no candidate references. Analyze the document, extract keywords, recommend source databases, and generate candidate references with `pending verification` status.
- **Verification Mode**: Use when the user provides candidate references or `reference/*.md` files. Verify metadata, grade references, replace unsuitable items, and format the proposed final list.
- **Insertion Planning Mode**: Use after references are verified or mostly verified. Match references to claims and produce a citation insertion plan.
- **Modification Mode**: Use only after the user confirms the insertion plan. Insert citation markers, update the final reference list, and run QA checks.

For long documents, process one chapter at a time and maintain a global reference registry so duplicates keep one citation number.

## Required Reference Files

Load these files only when needed:

- `references/source-policy.md`: Read before web/database search, source recommendation, or authenticity judgment.
- `references/verification.md`: Read before verifying candidate references, assigning grades, or replacing problematic references.
- `references/gb7714.md`: Read before formatting GB/T 7714 references.
- `references/citation-placement.md`: Read before planning citation insertion positions.
- `references/output-templates.md`: Read before producing the first-stage plan, insertion plan, or final report.

## Workflow

1. Identify the target document format, citation style, numbering requirement, allowed source types, per-chapter reference counts, journal ratio target, and whether modification is requested.
2. Read the main document or relevant chapter. Extract title, abstract, keywords, headings, key claims, existing citations, existing reference list, tables, figures, and appendices when relevant.
3. If no candidate references exist, enter Discovery Mode and produce candidate references with explicit `pending verification` status.
4. If candidate references exist, enter Verification Mode. Do not assume suggestions are correct.
5. Verify each reference using reliable evidence. Record source name, source URL or DOI resolver URL, matched metadata, access date, and mismatch notes.
6. Grade each reference. Use only Grade A/B directly; ask before using Grade C; replace or remove Grade D/E.
7. Check chapter-level requirements: total references, journal article count, journal ratio, source-type allowances, and unresolved risks.
8. Format the proposed final reference list in the required style. Default to GB/T 7714 for Chinese academic reports unless the user asks otherwise.
9. Enter Insertion Planning Mode. Match each citation to a specific claim and produce an execution plan.
10. Ask for confirmation before modifying the official document. Accept confirmations such as `同意执行`, `可以修改`, `开始执行`, or `按这个方案修改`.
11. After confirmation, modify the document using the safest format-appropriate tool: direct Markdown edits, LaTeX/BibTeX edits, Word/document tooling, or Feishu CLI when available.
12. Run final QA: citation/reference consistency, continuous numbering, duplicate detection, uncited references, missing references, journal ratio, style consistency, and document-structure preservation.

## Deterministic Checks

Use scripts for plain-text or Markdown QA when applicable:

```bash
python scripts/check_reference_numbering.py path/to/document.md
python scripts/detect_uncited_references.py path/to/document.md
python scripts/check_journal_ratio.py path/to/references.tsv --min-ratio 0.8
```

The scripts are helpers only. They do not verify authenticity and do not replace expert judgment or source checking.

## Failure Handling

- If a reference cannot be verified, mark it as unverified, explain the failure, and suggest a replacement when possible.
- If reliable sources cannot satisfy the required quantity or journal ratio, report the shortage and suggest relaxing constraints or expanding the search scope.
- If automatic document modification is unsafe or unavailable, provide a manual insertion plan, final reference list, and exact snippets for manual editing.
- If citation style is ambiguous, ask the user to choose a style. For Chinese academic reports, default to GB/T 7714.
