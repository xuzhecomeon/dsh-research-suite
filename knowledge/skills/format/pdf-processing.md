---
name: pdf-processing
display_name: PDF 整理与校验
display_name_en: PDF Processing
description: Verify PDFs, hash-deduplicate files recoverably, normalize filenames, and create a final processing report.
description_zh: 校验PDF文件、以哈希可恢复去重、规范化命名，并输出最终处理报告。
description_en: Verifies PDFs, recoverably deduplicates by hash, normalizes filenames, and writes a final processing report.
category: education
version: 1.0.0
author: Waylon
user-invocable: false
---

# PDF Processing Skill

Run this Skill after OA and any authorized institutional downloads. It adds the missing executable finalization seam while preserving the source pipeline's `%PDF`, hash-deduplication, naming, and reporting rules.

## Command

```bash
python3 <WORKBUDDY_EXPERT_ROOT>/skills/pdf_processing/scripts/process_pdfs.py \
  <work-output-dir>/pdfs --report-dir <work-output-dir>
```

## Behavior

- Reject files that do not start with `%PDF`; move them to `rejected/` with the reason in the report.
- Compute SHA-256 hashes of valid PDFs. Keep one canonical file for each identical hash and move additional copies to `duplicates/`; never silently delete user files.
- Normalize filenames using safe Unicode-preserving characters, retain the `.pdf` extension, and add a numeric suffix on collisions.
- Write a report listing valid, rejected, duplicate, renamed, and final file counts with all relative paths.

## Outputs

- `pdf_processing_report_<timestamp>.md` in the report directory.
- `duplicates/` and `rejected/` subdirectories when needed.
- A cleaned `pdfs/` library containing only unique, validated PDFs.
