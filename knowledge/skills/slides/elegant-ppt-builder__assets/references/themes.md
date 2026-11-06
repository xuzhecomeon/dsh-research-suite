# Themes

Three pre-defined themes ship with the skill. Pick by content tone and audience.

## `aurora` (default)

**Feel:** 现代极简 + 强渐变（紫蓝粉极光）
**Use when:** Generic business / product launches / strategy reviews /
quarterly reports / anything that should feel modern and "premium".
**Avoid when:** Light/cultural/fashion contexts where neon would feel too techy.

### Color palette

| Token            | Hex       | Role                                   |
|------------------|-----------|----------------------------------------|
| `primary`        | `#6C5CE7` | Brand purple — titles, accents, dots   |
| `primary_2`      | `#5B6CFF` | Secondary blue — gradients             |
| `accent_pink`    | `#FF6B9D` | Warm accent — highlights, KPIs         |
| `accent_amber`   | `#FFB547` | Warm accent 2                          |
| `accent_cyan`    | `#22D3EE` | Cool accent — links, dividers          |
| `accent_lime`    | `#A3E635` | Success / positive deltas              |
| `text`           | `#0E1330` | Body text on light bg                  |
| `text_muted`     | `#5B5F77` | Sub-text, footers                      |
| `text_invert`    | `#FFFFFF` | Text on dark bg (cover, section)       |
| `text_soft`      | `#E8E9F2` | Muted text on dark bg                  |
| `surface`        | `#FFFFFF` | Card backgrounds                       |
| `line`           | `#E2E4F0` | Hairlines, dividers                    |

### Gradients

| Name    | Stops                                | Used for                |
|---------|--------------------------------------|-------------------------|
| primary | `#6C5CE7` → `#5B6CFF`                | Bar chart, hero elements |
| warm    | `#FF6B9D` → `#FFB547`                | Warm callouts            |
| cool    | `#22D3EE` → `#6C5CE7`                | Cool callouts            |
| sunset  | `#FF6B9D` → `#FFB547` → `#FFD86B`    | Multi-stop              |
| ocean   | `#22D3EE` → `#5B6CFF` → `#6C5CE7`    | Multi-stop cool         |

### Fonts

- Title (CN): `PingFang SC`
- Title (EN): `Inter`
- Body (CN): `PingFang SC`
- Body (EN): `Inter`
- Mono: `JetBrains Mono`

## `neon`

**Feel:** 深色赛博 + 霓虹（青/品红/紫）
**Use when:** Tech / AI / gaming / crypto / sci-fi / cyberpunk / "futuristic".
**Avoid when:** Conservative business, finance, healthcare — feels too aggressive.

### Color palette

| Token            | Hex       | Role                          |
|------------------|-----------|-------------------------------|
| `primary`        | `#22D3EE` | Cyan — main brand color       |
| `primary_2`      | `#A855F7` | Purple — gradients            |
| `accent_pink`    | `#F472B6` | Magenta — highlights          |
| `accent_amber`   | `#FBBF24` | Amber — warnings              |
| `accent_cyan`    | `#22D3EE` | Same as primary               |
| `accent_lime`    | `#A3E635` | Lime — success                |
| `text`           | `#F4F6FF` | Body text on dark bg          |
| `text_muted`     | `#9097B5` | Sub-text                      |
| `text_invert`    | `#0B0F1E` | Text on light cards           |
| `text_soft`      | `#1B2240` | Subtle dark surface           |
| `surface`        | `#0F1428` | Card on dark bg               |
| `line`           | `#2A3158` | Grid lines, dividers          |

### Gradients

| Name    | Stops                                |
|---------|--------------------------------------|
| primary | `#22D3EE` → `#A855F7`                |
| warm    | `#F472B6` → `#FBBF24`                |
| cool    | `#22D3EE` → `#3B82F6`                |
| sunset  | `#F472B6` → `#A855F7` → `#22D3EE`    |
| ocean   | `#22D3EE` → `#A855F7` → `#F472B6`    |

### Fonts

- Title (CN): `PingFang SC`
- Title (EN): `Orbitron` (fallback to Inter)
- Body (CN): `PingFang SC`
- Body (EN): `Inter`
- Mono: `JetBrains Mono`

## `morandi`

**Feel:** 柔和奶油 + 莫兰迪（米白/灰粉/雾蓝）
**Use when:** Fashion / beauty / culture / art / education / lifestyle / wedding
/ slow-paced brands. When you want the slides to feel warm, soft, and
"considered" rather than energetic.
**Avoid when:** Tech / data-heavy reports / anything that needs to feel
"punchy".

### Color palette

| Token            | Hex       | Role                          |
|------------------|-----------|-------------------------------|
| `primary`        | `#B57E6B` | Warm clay — brand             |
| `primary_2`      | `#8A9A8B` | Sage green — gradients        |
| `accent_pink`    | `#D4A5A5` | Dusty rose                    |
| `accent_amber`   | `#C9A66B` | Muted gold                    |
| `accent_cyan`    | `#8AAFB7` | Foggy blue                    |
| `accent_lime`    | `#A8B07A` | Sage lime                     |
| `text`           | `#2E2A26` | Body text (warm dark)         |
| `text_muted`     | `#7A726A` | Sub-text                      |
| `text_invert`    | `#FAF7F2` | Text on dark cover (closing)  |
| `text_soft`      | `#D8D1C7` | Muted light                   |
| `surface`        | `#FAF7F2` | Cream surface                 |
| `line`           | `#D8D1C7` | Hairlines                     |

### Gradients

| Name    | Stops                                |
|---------|--------------------------------------|
| primary | `#D4A5A5` → `#B57E6B`                |
| warm    | `#D4A5A5` → `#C9A66B`                |
| cool    | `#8AAFB7` → `#8A9A8B`                |
| sunset  | `#D4A5A5` → `#C9A66B` → `#A8B07A`    |
| ocean   | `#8AAFB7` → `#A8B07A` → `#8A9A8B`    |

### Fonts

- Title (CN): `Songti SC` (more elegant than PingFang for serif feel)
- Title (EN): `Playfair Display` (fallback to Inter)
- Body (CN): `PingFang SC`
- Body (EN): `Inter`
- Mono: `JetBrains Mono`

## Background recipes

Each theme defines 5 background kinds: `cover`, `section`, `content`,
`closing`, `quote`. Each background is a base color + linear gradient +
a set of soft fuzzy "blobs" (large semi-transparent circles with Gaussian
blur) + optional grid/dot overlays.

The blob list per background controls the "shape" of the background.
For example, the aurora cover uses 3 blobs (purple top-left, pink
bottom-right, cyan top-right) to create an aurora-like glow.

**To customize:** Edit the `backgrounds` section of a theme. Each blob
is a dict with:

```python
{
    "color":         "#RRGGBB",   # hex
    "alpha":         200,         # 0-255, lower = more transparent
    "radius_factor": 0.5,         # blob size as fraction of min(w, h)
    "softness":      0.5,         # gaussian blur strength
    "cx":            0.2,         # blob center X as fraction of width
    "cy":            0.3,         # blob center Y as fraction of height
}
```

Variant cycling: backgrounds rotate subtly between consecutive content
slides (variant 0, 1, 2, ...). To control this per slide, place
`"cx_variants": [0.1, 0.3, 0.5]` instead of `"cx"` and the builder
will pick the right one.

## Custom theme

```python
from pptx_builder import THEMES, Builder

THEMES["brand"] = {
    "name": "brand",
    "description": "My custom brand theme",
    "fonts": {
        "title": "PingFang SC",
        "title_en": "Inter",
        "body": "PingFang SC",
        "body_en": "Inter",
        "mono": "JetBrains Mono",
    },
    "colors": {
        "text":        "#1A1A2E",
        "text_muted":  "#6B6B7E",
        "text_invert": "#FFFFFF",
        "text_soft":   "#E5E5F0",
        "primary":     "#E94560",
        "primary_2":   "#0F3460",
        "accent_pink": "#E94560",
        "accent_amber": "#FFC857",
        "accent_cyan": "#16C79A",
        "accent_lime": "#A8E6CF",
        "surface":     "#FFFFFF",
        "surface_alt": "#F8F8FC",
        "line":        "#E5E5F0",
    },
    "gradients": { ... },
    "backgrounds": { ... },
}

b = Builder(theme="brand")
```
