# Components

Detailed API for every page template. All methods return the slide
object. Slide canvas: **13.333 × 7.5 inches** (16:9 widescreen).

## `cover(title, subtitle, **kwargs)`

Title slide. Use once at the start of a deck.

| Param         | Type | Required | Notes                                  |
|---------------|------|----------|----------------------------------------|
| `title`       | str  | yes      | Main title (CN/EN both work)           |
| `subtitle`    | str  | no       | Subtitle, single line                  |
| `eyebrow`     | str  | no       | Small uppercase tag above the title    |
| `accent`      | str  | no       | Italic accent line below subtitle      |
| `bottom_left` | str  | no       | Footer left (date, author)             |
| `bottom_right`| str  | no       | Footer right                           |

```python
b.cover("Project Aurora", "2026 Strategy & Roadmap",
        eyebrow="Q2 2026 · Strategy",
        accent="designed with elegant-ppt-builder",
        bottom_left="Prepared by Strategy Team",
        bottom_right="2026.06.26")
```

## `section(number, title, subtitle, **kwargs)`

Chapter divider. Use between major parts of the deck.

| Param      | Type | Required | Notes                            |
|------------|------|----------|----------------------------------|
| `number`   | str  | yes      | "01", "02", "PART I" — any string |
| `title`    | str  | yes      | Section title                    |
| `subtitle` | str  | no       | Short subtitle                   |
| `side`     | str  | no       | "left" (default) or "right" — which side the giant number sits on |

```python
b.section("01", "Executive Summary",
           "本季度核心成果与关键洞察", side="left")
```

## `bullets(title, items, **kwargs)`

Bulleted list. Each item is one bullet.

| Param            | Type             | Required | Notes                              |
|------------------|------------------|----------|------------------------------------|
| `title`          | str              | yes      | Slide title                        |
| `items`          | list[str]        | yes      | Each becomes one row               |
| `eyebrow`        | str              | no       | Small uppercase tag                |
| `icons`          | list[str]        | no       | Per-row icon character (else cycles through ◆ ● ▲ ■ ★ ◇) |
| `accent_colors`  | list[str]        | no       | Per-row icon disc color (else cycles through theme accents) |

```python
b.bullets("Q2 Highlights", [
    "营收同比增长 38%",
    "新签客户 12 家",
    "NPS 提升至 67",
], eyebrow="Highlights",
   icons=["◆", "●", "▲"])
```

## `cards_grid(title, cards, **kwargs)`

Grid of 1-3 column cards. Each card has an icon disc, optional big
metric, title, and body.

| Param    | Type       | Required | Notes                        |
|----------|------------|----------|------------------------------|
| `title`  | str        | yes      | Slide title                  |
| `cards`  | list[dict] | yes      | See schema below             |
| `eyebrow`| str        | no       |                              |
| `cols`   | int        | no       | Default 3                    |

### Card schema

```python
{
    "title":  "...",     # required, card title
    "body":   "...",     # required, body text
    "icon":   "✦",       # optional, default ✦ (cycles if multiple)
    "metric": "3.2x",    # optional, big number above title
    "accent": "primary", # optional, theme key OR "#RRGGBB"
}
```

If `metric` is provided, it renders as a large number in the accent color
above the card title.

```python
b.cards_grid("Focus Areas", [
    {"title": "产品创新", "icon": "✦", "metric": "3.2x",
     "body": "推出 4 项核心功能..."},
    {"title": "市场拓展", "icon": "◈", "metric": "5 城",
     "body": "新增华东 5 城渠道..."},
    {"title": "组织升级", "icon": "✧", "metric": "120 人",
     "body": "完成关键岗位招聘..."},
], cols=3)
```

## `big_number(title, metrics, **kwargs)`

KPI row of 3-6 large metrics. Use for "by the numbers" pages.

| Param     | Type       | Required | Notes                |
|-----------|------------|----------|----------------------|
| `title`   | str        | yes      | Slide title          |
| `metrics` | list[dict] | yes      | See schema below     |
| `eyebrow` | str        | no       |                      |

### Metric schema

```python
{
    "value":  "¥ 1.24B",  # required, big number
    "label":  "季度营收",   # required, label below
    "delta":  "+38% YoY", # optional, small text below label
    "accent": "primary",  # optional, theme key OR hex
}
```

```python
b.big_number("Key Metrics", [
    {"value": "¥ 1.24B", "label": "季度营收", "delta": "+38% YoY"},
    {"value": "12",      "label": "新签客户", "delta": "+5 vs Q1"},
    {"value": "67",      "label": "NPS 得分", "delta": "+12 pts"},
    {"value": "98%",     "label": "续约率",   "delta": "+3 pts"},
])
```

## `two_column(title, left, right, **kwargs)`

Side-by-side compare/contrast.

| Param   | Type | Required | Notes                |
|---------|------|----------|----------------------|
| `title` | str  | yes      |                      |
| `left`  | dict | yes      | See schema below     |
| `right` | dict | yes      | Same schema as left  |
| `eyebrow` | str | no      |                      |

### Block schema

```python
{
    "eyebrow": "PROS",     # small uppercase tag (optional)
    "title":   "...",      # block title (required)
    "body":    "line 1\nline 2\nline 3",  # required, newline-separated
    "accent":  "primary",  # optional, theme key OR hex
}
```

```python
b.two_column("Approach Comparison",
    {"eyebrow": "Option A",
     "title": "In-house build",
     "body":  "Full control\nCustom fit\nLonger time-to-market",
     "accent": "primary"},
    {"eyebrow": "Option B",
     "title": "Vendor solution",
     "body":  "Faster launch\nLower upfront cost\nLess differentiation",
     "accent": "accent_pink"})
```

## `timeline(title, events, **kwargs)`

Process / roadmap / phase timeline. Horizontal or vertical.

| Param         | Type       | Required | Notes                              |
|---------------|------------|----------|------------------------------------|
| `title`       | str        | yes      |                                    |
| `events`      | list[dict] | yes      | See schema below                   |
| `eyebrow`     | str        | no       |                                    |
| `orientation` | str        | no       | "horizontal" (default) or "vertical" |

### Event schema

```python
{
    "label": "Phase 1",   # required, small uppercase tag
    "title": "Discovery", # required, event title
    "body":  "...",       # required, description
    "color": "primary",   # optional, theme key OR hex
}
```

```python
b.timeline("H2 Roadmap", [
    {"label": "Phase 1", "title": "Discovery", "body": "用户调研"},
    {"label": "Phase 2", "title": "Design",    "body": "产品原型"},
    {"label": "Phase 3", "title": "Build",     "body": "敏捷开发"},
    {"label": "Phase 4", "title": "Launch",    "body": "灰度发布"},
], orientation="horizontal")
```

## `bar_chart(title, labels, values, **kwargs)`

Custom-rendered gradient bar chart (NOT the default ugly python-pptx chart).

| Param             | Type        | Required | Notes                              |
|-------------------|-------------|----------|------------------------------------|
| `title`           | str         | yes      |                                    |
| `labels`          | list[str]   | yes      | Category labels (X axis)           |
| `values`          | list[float] | yes      | Numeric values                     |
| `eyebrow`         | str         | no       |                                    |
| `highlight_index` | int         | no       | Index of bar to highlight (default -1) |
| `value_format`   | str         | no       | Format string, default "{:.0f}"    |
| `unit`            | str         | no       | Unit suffix (e.g. "M", "%")        |

```python
b.bar_chart("Revenue by Region", ["华东", "华南", "华北", "西部"],
             [420, 310, 280, 150],
             eyebrow="Q2 2026", unit="M", highlight_index=0)
```

## `donut_chart(title, segments, **kwargs)`

Custom-rendered donut/ring chart with center label.

| Param          | Type       | Required | Notes                            |
|----------------|------------|----------|----------------------------------|
| `title`        | str        | yes      |                                  |
| `segments`     | list[dict] | yes      | See schema below                 |
| `eyebrow`      | str        | no       |                                  |
| `center_label` | str        | no       | Small text under center value    |
| `center_value` | str        | no       | Big text in donut hole           |

### Segment schema

```python
{
    "label": "直销",     # required, legend label
    "value": 45,         # required, numeric value
    "color": "primary",  # optional, theme key OR hex
}
```

```python
b.donut_chart("Channel Mix", [
    {"label": "直销", "value": 45},
    {"label": "渠道", "value": 30},
    {"label": "电商", "value": 15},
    {"label": "其他", "value": 10},
], center_value="100%", center_label="Total")
```

## `quote(quote_text, author, role)`

Big quote slide. Use sparingly — 1 per deck max.

| Param        | Type | Required | Notes                |
|--------------|------|----------|----------------------|
| `quote_text` | str  | yes      | The quote            |
| `author`     | str  | no       | Attribution          |
| `role`       | str  | no       | Author's role/title  |

```python
b.quote("真正优秀的作品，是当所有人离开屏幕后，仍然在脑海里回响的旋律。",
         "— Jonathan Ive",
         "Chief Design Officer, Apple")
```

## `thanks(message, subtitle, contact)`

Closing slide. Use once at the end.

| Param      | Type | Required | Notes                |
|------------|------|----------|----------------------|
| `message`  | str  | yes      | "Thank You" or similar |
| `subtitle` | str  | no       |                      |
| `contact`  | str  | no       | Email/URL/handle     |

```python
b.thanks("Thank You", "期待与您的下一次交流", "hello@company.com")
```

## `custom(build_fn)`

Escape hatch. `build_fn(slide, builder)` is called with a blank slide
that already has the content background, and the builder instance (for
theme/colors/fonts access).

Use this when none of the pre-built templates fit. Inspect the source
of any page method for a worked example of how to compose shapes
inside `build_fn`.

```python
def my_slide(slide, b):
    c = b.theme["colors"]
    f = b.theme["fonts"]
    # Build whatever you need:
    rounded_rect(slide, 1, 2, 11.3, 3, fill="#FFFFFF", corner=0.05)
    add_textbox(slide, 1.4, 2.3, 10.5, 0.6,
                "Custom Heading", font=f["title"], size=32,
                color=c["primary"], bold=True)
    # ... add more shapes

b.custom(my_slide)
```

## Shape helpers (advanced)

These are the low-level building blocks used by the page templates.
You can call them directly inside `custom()`.

### `rounded_rect(slide, x, y, w, h, *, fill=None, line=None, line_width=0.75, line_transparency=0, corner=0.12)`

Add a rounded rectangle. `fill` and `line` are hex colors; pass `None`
to make them transparent.

### `ellipse(slide, x, y, w, h, *, fill=None, line=None)`

Add an ellipse (oval / circle if w==h).

### `line_shape(slide, x1, y1, x2, y2, *, color, width_pt=1.0)`

Add a straight line. Coordinates are absolute (inches).

### `add_textbox(slide, x, y, w, h, text, *, font=None, size=18, color=None, bold=False, italic=False, align="left", anchor="top", auto_size=False)`

Add a text box. `align`: "left" / "center" / "right". `anchor`: "top" /
"middle" / "bottom". For multi-line content, pass empty `text=""` and
manipulate `tb.text_frame` directly:

```python
tb = add_textbox(slide, 1, 2, 10, 3, "")
tf = tb.text_frame
for line in ["first", "second", "third"]:
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    set_run(run, line, font="PingFang SC", size=14, color="#333333")
```

### `set_run(run, text, *, font=None, size=None, color=None, bold=None, italic=None)`

Set a run's properties. `color` is hex without `#`. Setting `font`
also sets the East-Asian font, which is required for proper Chinese
rendering in PowerPoint.

## Coordinate system

All coordinates are in **inches**. Slide is 13.333 × 7.5.

Recommended safe area:

- left margin: 0.6
- right margin: 0.6
- top margin: 0.5
- bottom margin: 0.5 (footer takes the last 0.5)

So content lives in `(0.6, 0.5) → (12.7, 7.0)`.
