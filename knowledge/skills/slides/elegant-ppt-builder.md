---
name: elegant-ppt-builder
description: |
  This skill should be used when the user wants to create a beautiful,
  visually-rich PowerPoint deck. It generates .pptx files with complex
  visual elements (gradient backgrounds, soft glow blobs, glassmorphism
  cards, custom bar/donut charts) and rich color palettes across three
  built-in themes (aurora / neon / morandi). Use it whenever the user
  asks for slides, presentations, decks, or 演示文稿 / PPT, especially
  when they mention "精美" / "漂亮" / "好看" / "高级感" / "设计感".
  Triggers: "做一份PPT", "生成幻灯片", "write a deck", "make a pitch",
  "create slides about X". Do NOT use it for plain text documents,
  spreadsheets, or non-slide deliverables.
agent_created: true
---

# Elegant PPT Builder

Generate beautiful, visually-rich PowerPoint decks with complex visual
elements and rich color palettes. Three built-in themes, eleven pre-styled
page templates, custom-rendered charts — all driven from a small Python API.

## When to use

- The user asks for a slide deck / PPT / presentation
- The user asks for "精美的" / "好看的" / "高级的" / "有设计感的" slides
- The user provides content (text, bullets, metrics, etc.) and wants
  it laid out as a presentation
- The user wants themed slides (dark, light, neon, morandi, gradient, etc.)

## When NOT to use

- The user wants plain Markdown, Word, or PDF documents
- The user wants a spreadsheet
- The deliverable is a single image, not a multi-slide deck

## Quick start

```python
import sys
sys.path.insert(0, "~/.workbuddy/skills/elegant-ppt-builder/scripts")

from pptx_builder import Builder

b = Builder(theme="aurora")  # also: 'neon', 'morandi'

b.cover("Project Aurora", "2026 Strategy & Roadmap",
        eyebrow="Q2 2026 · Strategy",
        accent="designed with elegant-ppt-builder",
        bottom_left="Prepared by Strategy Team",
        bottom_right="2026.06.26")

b.section("01", "Executive Summary",
           "本季度核心成果与关键洞察")

b.bullets("Q2 Highlights", [
    "营收同比增长 38%，超预期完成目标",
    "新签客户 12 家，其中 3 家 Fortune 500",
    "产品 NPS 提升至 67，客户满意度创新高",
])

b.big_number("Key Metrics", [
    {"value": "¥ 1.24B", "label": "季度营收", "delta": "+38% YoY"},
    {"value": "12",       "label": "新签客户", "delta": "+5 vs Q1"},
    {"value": "67",       "label": "NPS 得分", "delta": "+12 pts"},
    {"value": "98%",      "label": "续约率",   "delta": "+3 pts"},
])

b.cards_grid("Focus Areas", [
    {"title": "产品创新", "icon": "✦", "metric": "3.2x",
     "body": "推出 4 项核心功能，用户活跃度提升 220%。"},
    {"title": "市场拓展", "icon": "◈", "metric": "5 城",
     "body": "新增华东 5 城渠道，区域营收占比突破 35%。"},
    {"title": "组织升级", "icon": "✧", "metric": "120 人",
     "body": "完成关键岗位招聘 120 人，人才密度提升。"},
], cols=3)

b.timeline("H2 Roadmap", [
    {"label": "Phase 1", "title": "Discovery", "body": "用户调研 & 需求分析"},
    {"label": "Phase 2", "title": "Design",    "body": "产品原型 & 用户测试"},
    {"label": "Phase 3", "title": "Build",     "body": "敏捷开发 & 持续交付"},
    {"label": "Phase 4", "title": "Launch",    "body": "灰度发布 & 增长迭代"},
])

b.bar_chart("Revenue by Region", ["华东", "华南", "华北", "西部"],
             [420, 310, 280, 150], unit="M", highlight_index=0)

b.donut_chart("Channel Mix", [
    {"label": "直销", "value": 45},
    {"label": "渠道", "value": 30},
    {"label": "电商", "value": 15},
    {"label": "其他", "value": 10},
], center_value="100%", center_label="Total")

b.quote("真正优秀的作品，是当所有人离开屏幕后，仍然在脑海里回响的旋律。",
         "— Jonathan Ive",
         "Chief Design Officer, Apple")

b.thanks("Thank You", "期待与您的下一次交流", "hello@company.com")

b.save("output.pptx")
```

## Available themes

| Name       | Description                                   | Best for                      |
|------------|-----------------------------------------------|-------------------------------|
| `aurora`   | 现代极简 + 强渐变（紫蓝粉极光）                | 通用商务、产品发布、战略汇报   |
| `neon`     | 深色赛博 + 霓虹（青/品红/紫）                 | 科技/AI/游戏主题、夜场发布     |
| `morandi`  | 柔和奶油 + 莫兰迪（米白/灰粉/雾蓝）            | 文化/品牌/时尚/教育/女性向主题 |

Pick the theme based on the user's content and tone. If unsure, default
to `aurora` (most flexible). For dark/tech/science, use `neon`. For soft
fashion/beauty/education, use `morandi`.

## Page templates

All page methods return the slide object. Methods marked with ★ are
high-impact cover/divider/closing pages — use them at the start of
each major section.

| Method              | Purpose                          | Key params                        |
|---------------------|----------------------------------|-----------------------------------|
| `cover`         ★   | Title slide                      | title, subtitle, eyebrow, accent  |
| `section`       ★   | Chapter divider                  | number, title, subtitle, side     |
| `bullets`           | Bulleted list                    | title, items, icons, accents      |
| `cards_grid`        | 1-3 col cards with icon+metric  | title, cards, cols                |
| `big_number`        | KPI row (3-6 metrics)            | title, metrics                    |
| `two_column`        | Side-by-side compare             | title, left, right                |
| `timeline`          | Horizontal/vertical process      | title, events, orientation        |
| `bar_chart`         | Custom gradient bar chart        | title, labels, values, unit       |
| `donut_chart`       | Custom donut/ring chart          | title, segments, center_value     |
| `quote`             | Big quote with attribution       | quote_text, author, role          |
| `thanks`        ★   | Closing/thank-you                | message, subtitle, contact        |
| `custom`            | Escape hatch (full control)      | build_fn(slide, builder)          |

For complete details on every parameter and the visual contract, see
`references/components.md`.

For theme color palettes, gradient sets, and font choices, see
`references/themes.md`.

For more worked examples, see `references/examples.md`.

## Design system at a glance

The skill produces slides that follow these visual rules:

- **Background:** Every slide gets a pre-rendered gradient + soft-blob
  background (Pillow), giving a much richer look than python-pptx's
  default flat fills. Variant cycling keeps consecutive content slides
  visually distinct without being chaotic.
- **Cards:** All content containers are rounded-rectangle white cards
  with a top accent bar and an icon disc, sitting on top of the colored
  background. This creates a glassmorphism-like depth.
- **Typography:** Chinese text uses PingFang/Songti (theme-dependent);
  numeric and English text uses theme-specific display fonts. Each page
  uses 3 distinct sizes (eyebrow / title / body) to maintain hierarchy.
- **Color:** Themes define a primary + 5 accent colors. Pages cycle
  through accents so multi-card layouts look intentional, not random.
- **Charts:** `bar_chart` and `donut_chart` are NOT the default ugly
  python-pptx charts. They are rendered as PNGs with gradient fills
  and re-imported as images, giving full control over style.

## Adding new themes

Themes live in `scripts/pptx_builder.py` in the `THEMES` dict. Each
theme needs:

- `fonts` — title, body, mono font names (will fall back gracefully)
- `colors` — primary, accents, surface, text colors (hex)
- `gradients` — named gradient pairs/triples used by charts
- `backgrounds` — for each `kind` in
  `{cover, section, content, closing, quote}`:
  base color, gradient stops, blob list (color/alpha/radius/cx/cy),
  optional grid/dots overlay.

Use an existing theme as a starting template.

## Adding new page templates

The cleanest way to add a new page is to write a method on `Builder`
that:

1. Calls `self.add_blank_slide()` and `self._add_background(slide, "content")`
2. Calls `self._page_header(slide, title, eyebrow)` for a consistent header
3. Builds content using the shape helpers:
   - `rounded_rect(slide, x, y, w, h, fill=..., corner=...)`
   - `ellipse(slide, x, y, w, h, fill=...)`
   - `line_shape(slide, x1, y1, x2, y2, color=..., width_pt=...)`
   - `add_textbox(slide, x, y, w, h, text, font=..., size=..., color=..., bold=...)`
4. Optionally calls `self._add_footer(slide, page_number)`

Slide canvas is **13.333 × 7.5 inches** (16:9). Keep content within
`(0.6, 0.5) → (12.7, 7.0)` for safe margins.

## Dependencies

- `python-pptx` — PowerPoint generation
- `Pillow` — image generation for backgrounds, blobs, charts
- `lxml` — XML manipulation for advanced shape adjustments
- Chinese fonts (macOS: PingFang/Songti/STHeiti; Linux: WQY MicroHei
  or Noto CJK) — if missing, the donut center text may render in a
  default font, but everything else will still work.

## Files

```
elegant-ppt-builder/
├── SKILL.md                 # this file
├── scripts/
│   ├── pptx_builder.py      # main Builder class + page templates + themes
│   └── visual.py            # Pillow-based visual primitives
├── references/
│   ├── themes.md            # theme palettes, gradients, fonts
│   ├── components.md        # detailed page template API
│   └── examples.md          # more worked examples
└── assets/                  # (empty by default; place fonts here if needed)
```

## Quick demo

```bash
~/.workbuddy/binaries/python/envs/default/bin/python3 \
  ~/.workbuddy/skills/elegant-ppt-builder/scripts/pptx_builder.py \
  demo ./demo.pptx aurora
```

This produces a 10-slide demo deck showcasing every page template.
