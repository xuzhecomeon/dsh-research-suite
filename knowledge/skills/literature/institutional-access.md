---
name: institutional-access
display_name: 机构权限访问
display_name_en: Institutional Access
description: Use a user-authorized publisher or library session to obtain subscription PDFs without handling credentials or bypassing access controls.
description_zh: 在用户完成图书馆或出版商认证后，使用授权会话下载订阅全文，不处理凭据也不绕过访问限制。
description_en: Uses the user's authorized library or publisher session to download subscribed PDFs without handling credentials or bypassing access controls.
category: education
version: 1.0.0
author: Waylon
user-invocable: false
---

# Institutional Access Skill

Use this Skill only for unresolved records after OA routes are exhausted and after the user explicitly confirms that an authorized browser session is ready.

Read @references/source-institutional-access.md for the retained source workflow and @references/bit-library-coverage.md only as a historical institution-specific example, never as a guarantee of the current user's access.

## Allowed workflow

1. Ask the user to manually authenticate through their institution or publisher. Return `requires_user_action: institutional_auth` for login, a captcha, or any final access decision.
2. After confirmation, open the DOI in the existing browser session and look for the actual institution-access signal.
3. For Springer, Elsevier/ScienceDirect, Wiley, IEEE, Taylor & Francis, and other supported publishers, use normal page controls to obtain only content made available by that session.
4. Inspect each download's first four bytes. Send valid files to the task `pdfs/` directory and record the publisher, DOI, source URL, access signal, and result.
5. If the page states that the institution does not subscribe or access is restricted, log the reason once and route the record to the user's final decision; do not retry indefinitely.

## Prohibitions

- Do not request, type, read, transmit, or store account credentials.
- Do not bypass a paid-access control, robot check, or captcha.
- Do not use illegal mirrors or unapproved full-text sources.
- Never assume an authentication session for one publisher grants access to another publisher.

## Outputs

- Downloaded PDFs that passed `%PDF` validation.
- An access log containing `doi`, `publisher`, `access_signal`, `outcome`, and `reason`.
- Remaining records for final user decision or library document-delivery request.
