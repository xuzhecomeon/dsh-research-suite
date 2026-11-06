---
name: doi-validation
display_name: DOI 核验
display_name_en: DOI Validation
description: Validate DOI records against CrossRef, preserve four validation states, and generate an auditable report.
description_zh: 使用CrossRef核验DOI，保留有效、无效、为空和异常状态，并输出可追溯报告。
description_en: Validates DOI records with CrossRef, keeps valid, invalid, empty, and error states, and writes an auditable report.
category: education
version: 1.0.0
author: Waylon
user-invocable: false
---

# DOI Validation Skill

This Skill delegates the validation operation to the existing `scripts/validate_dois.py`, retained from the source WoS pipeline. It must run before any DOI-based download.

## Inputs

- CSV exported by `wos-search`, with a `DI` DOI column and optionally `TI`.
- A real contact email supplied by the user for CrossRef User-Agent identification. Do not persist it in task state; mask it in user-facing reports.

## Command

```bash
python3 <WORKBUDDY_EXPERT_ROOT>/skills/doi_validation/scripts/validate_dois.py \
  <records.csv> --output-dir <work-output-dir> --mail <user-contact-email>
```

The copied source script writes a timestamped CSV that adds `DOI_Status` and a Markdown validation report.

## Required handling

- `valid`: may proceed to `oa-download`.
- `invalid`: retain the DOI and report it; do not silently remove it.
- `empty`: retain as a normal no-DOI result.
- `error`: retain and report as retryable; do not treat a rate limit or network error as invalid.

The script retries CrossRef rate limits and confirms a CrossRef 404 through `doi.org` before classifying a DOI as invalid. It normalizes punctuation before comparing source and CrossRef titles.

## Outputs

- `*_validated_<timestamp>.csv` with `DOI_Status`.
- `doi_validation_report_<timestamp>.md`.
- Structured counts for `valid`, `invalid`, `empty`, and `error`.
