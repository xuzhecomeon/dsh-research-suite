---
name: 论文汇报PPT制作
description: "当用户需要为学术论文（中文/英文、量化/质性均可）生成组会文献汇报PPT时使用此技能。触发词包括：文献汇报、组会PPT、学术PPT、论文汇报、生成PPT、毕业论文答辩PPT、开题报告PPT、make a presentation for this paper、create slides for my group meeting。该技能会生成一个17-20页的PPTX文件，采用专业学术蓝色系视觉风格，16pt正文、28pt标题、卡片式布局；若用户提供母版PPTX，则保留原始封面和结尾页。"
agent_created: true
---

# 论文汇报PPT制作 — 学术论文汇报PPT生成器

## 概述

本技能为研究生组会文献汇报生成专业的学术PPT。支持中英文论文、量化与质性研究。输入为论文PDF，输出为风格统一、内容结构清晰的PPTX文件，针对传播学/新闻学研究生研讨课优化。

## Workflow

### Step 0: Gather Requirements

Ask the user the following questions before starting (do NOT ask all at once — ask in batches of 2-4):

**Batch 1 — Essential:**
1. "汇报时长？听众是谁？（导师+同门/跨学科/其他）"
2. "你的母版PPT在哪里？（需要保留封面和结尾页的话，给我.pptx文件）"
3. "汇报人叫什么名字？汇报日期是哪天？"（封面页必须显示这两个信息）

**Batch 2 — If needed:**
4. "导师有没有格式/内容的偏好要求？"
5. "导师更看重讲清楚逻辑、批判性思考、还是研究方法细节？"
6. "你最想优先改进的是哪个方面？（美观/逻辑/内容深度/表达方式）"

**Key preferences to note:**
- Chinese communication/journalism graduate seminars
- Audience: supervisor + peer graduate students (传播学背景)
- 15-20 minute presentation, high information density, no animations
- Supervisor values: logical clarity + critical thinking + detailed methodology
- Font: 微软雅黑 (Chinese) + Arial (English)
- Body text: 16pt, Titles: 28pt

### Step 1: Extract Paper Content

Extract full text from the paper PDF using pymupdf (fitz):

```python
import fitz
doc = fitz.open("paper.pdf")
with open("paper.txt", "w", encoding="utf-8") as f:
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        f.write(f"--- Page {page_num+1} ---\n")
        f.write(text + "\n")
doc.close()
```

Read the extracted text and identify:
- Title, authors, journal, DOI, publication date, impact factor
- Research background, research gap, research questions/hypotheses
- Theoretical framework, key concepts
- Methodology (sample size, method type, data collection, analysis approach)
- Key findings (3-5 main results with specific data/Beta coefficients/quotes)
- Discussion, limitations, future directions
- Any figures or tables that need to be referenced

### Step 2: Build the PPTX

#### Loading Style Helpers

Use the bundled Python helper module at `scripts/ppt_helpers.py`. Copy it to the workspace and import:

```python
import sys
sys.path.insert(0, r'path/to/skill/scripts')
from ppt_helpers import *
```

#### Starting a Presentation

If the user provided a template PPTX (recommended):

```python
prs, LAYOUT = new_presentation(r"path/to/template.pptx")
# This preserves slide 0 (cover) and slide -1 (ending) from template
```

If no template provided:

```python
prs, LAYOUT = new_presentation()
# Build cover slide with COVER helper
cover = prs.slides.add_slide(LAYOUT)
COVER(cover, title="论文中文标题", presenters="汇报人姓名",
      date_str="2026年6月20日", en_title="English Title (optional)",
      journal="Journal Name", authors="Author Names")
# Build ending slide manually at the end
```

#### Building Content Slides

Use `prs.slides.add_slide(LAYOUT)` for each content slide. Apply the following helpers for every slide:

- `TITLE(slide, "标题", "副标题(可选)", cn=True)` — page title with blue underline
- `TB(slide, x, y, w, h, text, size, color, bold, align, cn)` — single text box
- `MTB(slide, x, y, w, h, lines, sizes, colors, bolds, aligns, cns)` — multi-line text box
- `BOX(slide, x, y, w, h, fill, border)` — rounded rectangle card
- `CIRCLE(slide, x, y, sz, fill)` — filled circle icon
- `DIVIDER(slide, num, text, cn)` — blue full-screen section divider
- `COVER(slide, title, presenters, date_str, en_title, journal, authors)` — cover page when no template
- `save(prs, output_path)` — save to a specific path
- `save_to_desktop(prs, filename)` — save directly to Desktop (default output)

After building all content slides, finalize:

```python
if USING_TEMPLATE:
    prs = finalize_ending(prs)  # Move original ending to last position
output_path = save_to_desktop(prs, "paper_report.pptx")  # Default: save to Desktop
```

#### Content Slide Order

Refer to `references/content_structure.md` for the recommended slide order and what each slide should contain. Key slides (17-20 total):

1. **Cover** — from template if provided; otherwise use `COVER()` with title/presenters/date
2. **Paper Info** — journal, IF, DOI, authors, affiliation, method summary
3. **Outline** — numbered circle navigation
4. **Background** — 4-card layout (phenomenon / gap / context / contribution)
5. **Theoretical Framework** — concept cards + original figure
6. **Research Questions/Hypotheses** — highlighted in colored box
7-8. **Methodology** — method overview + data collection + timeline
9. **Variables** (quantitative) — operationalization + controls + coding reliability
10-12. **Findings** — card-based results with data/quotations
13. **Discussion** — dialogue with prior research
14. **Critical Reflections** — theory/method/coder critique
15. **Implications** — 3-4 strategy cards tied to findings
16. **Limitations & Future** — 2-3 limitation cards + 4 future directions
17. **Personal Reflection** — China context + personal observations + advisor link
18. **Ending** — from template (DO NOT recreate)

#### Visual Design Rules

Refer to `references/style_guide.md` for exact color codes, font sizes, and card color mappings.

**Quick reference:**
- Titles: 28pt BLUE (#5A97D0) bold
- Body: 16pt DARK (#333333) regular
- Subtitle: 12pt GRAY (#666666)
- Card titles: 13-16pt accent color bold
- Card body: 10-13pt dark
- Footnotes: 9-10pt gray

**Card color scheme:**
| Purpose | Background | Border |
|---------|-----------|--------|
| Main info | #EBF3FA (light blue) | #5A97D0 (blue) |
| Contrast/case | #FEF3E8 (light orange) | #E87A00 (orange) |
| Positive/building | #E8F5E9 (light green) | #4A904A (green) |
| Negative/alert | #FFEBEE (light red) | #E53935 (red) |

### Step 3: Deliver the Result

1. Use `save_to_desktop(prs, "paper_report.pptx")` to save the PPTX directly to the user's Desktop (default output location)
2. Use `deliver_attachments` to present the file from the Desktop path
3. Provide a summary table of all slides and key improvements made

## Important Notes

- **ALWAYS preserve original cover and ending slides** when a template PPTX is provided. The `new_presentation()` and `finalize_ending()` functions handle this automatically. If the template cover lacks presenter/date info, remind the user to add them manually in PowerPoint.
- **ALWAYS include 汇报人 and 日期 on the cover page.** When no template, use `COVER()` which renders both. When using a template, confirm with the user that their cover includes them.
- **NEVER use animations** — the user explicitly prefers static displays.
- **High information density** is preferred — multiple sub-topics can coexist on one slide using card layouts.
- **For quantitative papers**: include Beta coefficients with significance stars (***/**/*), control variables, and compare superposition vs attenuation effects with dual-column cards.
- **For qualitative papers**: include at least one named ethnographic vignette (e.g., "Emma"), show theoretical framework evolution, and discuss platform challenges.
- **Always add critical reflection**: theory operationalization gaps, methodological limitations, coder positionality.
- **Always add China context**: connect findings to Chinese platform ecosystem (Douyin, Kuaishou, etc.) and local research opportunities.
