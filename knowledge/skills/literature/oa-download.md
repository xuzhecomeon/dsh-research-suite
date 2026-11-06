---
name: oa-download
display_name: 开放获取全文下载
display_name_en: Open Access Download
description: Retrieve lawful open-access PDFs through Unpaywall and publisher-declared OA links, then route unresolved items.
description_zh: 通过Unpaywall与出版商明确开放获取链接下载合法全文，并为未获取文献生成后续分流清单。
description_en: Retrieves lawful open-access PDFs through Unpaywall and publisher-declared OA links, then routes unresolved items.
category: education
version: 1.0.0
author: Waylon
user-invocable: false
---

# Open Access Download Skill

This Skill delegates Stage 1 to the existing `scripts/download_fulltext.py` from the source pipeline. It must run after DOI validation and before an institution login is requested.

## Inputs

- The validated CSV from `doi-validation`; only `DOI_Status=valid` is eligible.
- A real Unpaywall contact email supplied by the user for this execution. Do not store it in task context and mask it in reports.
- An output directory.

## Command

```bash
python3 <WORKBUDDY_EXPERT_ROOT>/skills/oa_download/scripts/download_fulltext.py \
  <validated-records.csv> --output-dir <work-output-dir> --email <user-contact-email>
```

## Required order

1. Query Unpaywall and attempt all available `url_for_pdf` candidates.
2. Accept a download only when its first four bytes are `%PDF`.
3. Retain the script's filename sanitization, collision handling, report, and `next_stage.csv` output.
4. Before any institution-authentication request, process publisher-declared OA and browser-direct candidates that require no login.
5. Use `next_stage.csv` to route records: stage 3 for a browser-readable OA article, stage 4 for authorized institutional access, and stage 5 for a user decision. Do not use unauthorized mirrors or bypass a paywall.

## Outputs

- `pdfs/` with valid OA PDFs.
- `download_report_<timestamp>.md`.
- `next_stage.csv`, including unresolved DOI, reason, and recommended next stage.
