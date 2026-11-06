---
name: wos-search
display_name: Web of Science 检索
display_name_en: Web of Science Search
description: Build and execute a configuration-driven Web of Science advanced search and export Full Record metadata.
description_zh: 根据已确认的研究范围生成WoS高级检索式，执行检索并导出完整题录数据。
description_en: Generates a verified WoS advanced query, runs it in the user's authenticated browser, and exports Full Record metadata.
category: education
version: 1.0.0
author: Waylon
user-invocable: false
---

# WoS Search Skill

Use this Skill only after the Agent has confirmed the user's research scope and created a task work directory. Copy `templates/wos-config.yaml` into that work directory and edit only the user-approved query and filter values.

## Inputs

- A work directory.
- A user-approved `wos-config.yaml` with `database`, `query`, `logic`, `filters`, `sort`, and `export`.
- A browser in which the user has manually authenticated to Web of Science.

## Execution

1. Validate that every query and filter field is a supported WoS field tag. Reject `ALL`; it is not a WoS advanced-search field.
2. Build each query component as `FIELD=(value)` without adding synonyms, wildcards, fields, or filters. Join query components using the configured boolean operator and append all filters unchanged.
3. Record the configuration content hash and exact query in `search-log-<timestamp>.md` before opening the browser.
4. Check the authenticated WoS advanced-search page. If login is absent, expired, or a human verification is required, return `requires_user_action: wos_login` without attempting credentials.
5. Enter the complete query, execute the search, and record displayed hits and page count. If `expected_hits` exists and the difference exceeds 20%, log the discrepancy.
6. Export **Full Record** data. Use `All records on page` and page through batches; do not rely on the unreliable `Records from` numeric control. Respect WoS export limits and browser multi-download approval prompts.
7. Parse tab-delimited exports as UTF-8 with BOM support, deduplicate by `UT`, locally apply the approved sort if needed, and save `records.csv` and `records.json` in the configured output directory.
8. Append the final hit count, saved count, applied filters, deviations, and artifact paths to the search log. Return the paths and counts to the Agent.

## Waiting and safety

Never type, read, or store a username or password. Return a waiting result instead of failing when authentication, browser download permission, or a captcha requires user participation. Do not access sources other than WoS in this Skill.

## Outputs

- `records.csv` and `records.json` containing Full Record fields, including `UT`, `DI`, `TI`, `AU`, `SO`, and `PY` when available.
- `search-log-<timestamp>.md`.
- Structured result: `requires_user_action`, `page_hits`, `saved_records`, `output_dir`, and `deviations`.
