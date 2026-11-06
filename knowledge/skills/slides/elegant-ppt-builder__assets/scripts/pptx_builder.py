"""
Elegant PPT Builder.

A high-level python-pptx based API for generating beautiful, visually
complex PowerPoint slides. Built around:

- Multi-theme design system (aurora / neon / morandi)
- Pre-rendered gradient backgrounds (Pillow)
- Pre-styled page templates (cover, section, content, chart, etc.)
- Decorative geometry (blobs, grids, dots, shadows)

Public entry points:

    from pptx_builder import Builder, THEMES

    b = Builder(theme="aurora")
    b.cover("Project Aurora", "2026 Mid-Year Strategy")
    b.section("01", "Executive Summary")
    b.bullets("Highlights", [...])
    ...
    b.save("output.pptx")
"""

from __future__ import annotations

import io
import os
import sys
import math
import tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# Ensure local imports work whether invoked as script or module
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree
from PIL import Image, ImageDraw, ImageFont

from visual import (
    CANVAS_W, CANVAS_H,
    hex_to_rgb, rgb_to_hex, lerp_color, soft_blobs,
    gradient_image, save_temp_png, make_background, load_font,
)

# Slide geometry: 13.333 x 7.5 inches (16:9 widescreen)
SLIDE_W_IN = 13.333
SLIDE_H_IN = 7.5


# -----------------------------------------------------------------------------
# Themes
# -----------------------------------------------------------------------------

THEMES: Dict[str, dict] = {
    "aurora": {
        "name": "aurora",
        "description": "现代极简 + 强渐变（紫蓝粉极光）",
        "fonts": {
            "title": "PingFang SC",
            "title_en": "Inter",
            "body": "PingFang SC",
            "body_en": "Inter",
            "mono": "JetBrains Mono",
        },
        "colors": {
            "text":        "#0E1330",
            "text_muted":  "#5B5F77",
            "text_invert": "#FFFFFF",
            "text_soft":   "#E8E9F2",
            "primary":     "#6C5CE7",
            "primary_2":   "#5B6CFF",
            "accent_pink": "#FF6B9D",
            "accent_amber": "#FFB547",
            "accent_cyan": "#22D3EE",
            "accent_lime": "#A3E635",
            "surface":     "#FFFFFF",
            "surface_alt": "#F4F4FB",
            "line":        "#E2E4F0",
        },
        "gradients": {
            "primary":  ["#6C5CE7", "#5B6CFF"],
            "warm":     ["#FF6B9D", "#FFB547"],
            "cool":     ["#22D3EE", "#6C5CE7"],
            "sunset":   ["#FF6B9D", "#FFB547", "#FFD86B"],
            "ocean":    ["#22D3EE", "#5B6CFF", "#6C5CE7"],
        },
        "backgrounds": {
            "cover": {
                "base": "#0E1330",
                "gradient": ["#1A1F4A", "#0E1330"],
                "blobs": [
                    {"color": "#6C5CE7", "alpha": 200, "radius_factor": 0.55,
                     "softness": 0.45, "cx": 0.18, "cy": 0.28},
                    {"color": "#FF6B9D", "alpha": 170, "radius_factor": 0.45,
                     "softness": 0.5, "cx": 0.85, "cy": 0.75},
                    {"color": "#22D3EE", "alpha": 130, "radius_factor": 0.4,
                     "softness": 0.5, "cx": 0.72, "cy": 0.18},
                ],
                "grid": False,
                "dots": True,
            },
            "section": {
                "base": "#0E1330",
                "gradient": ["#1F1A4A", "#0E1330"],
                "blobs": [
                    {"color": "#5B6CFF", "alpha": 200, "radius_factor": 0.6,
                     "softness": 0.5, "cx": 0.5, "cy": 0.5},
                ],
                "dots": False,
                "grid": False,
            },
            "content": {
                "base": "#FFFFFF",
                "gradient": ["#FBFBFE", "#F1F1FA"],
                "blobs": [
                    {"color": "#6C5CE7", "alpha": 70, "radius_factor": 0.4,
                     "softness": 0.55, "cx": 0.05, "cy": 0.1},
                    {"color": "#FF6B9D", "alpha": 60, "radius_factor": 0.35,
                     "softness": 0.6, "cx": 0.95, "cy": 0.95},
                    {"color": "#22D3EE", "alpha": 50, "radius_factor": 0.3,
                     "softness": 0.6, "cx": 0.95, "cy": 0.1},
                ],
                "grid": False,
                "dots": False,
            },
            "closing": {
                "base": "#0E1330",
                "gradient": ["#1A1F4A", "#0E1330"],
                "blobs": [
                    {"color": "#6C5CE7", "alpha": 180, "radius_factor": 0.5,
                     "softness": 0.5, "cx": 0.2, "cy": 0.3},
                    {"color": "#22D3EE", "alpha": 150, "radius_factor": 0.4,
                     "softness": 0.5, "cx": 0.8, "cy": 0.7},
                ],
                "dots": True,
                "grid": False,
            },
            "quote": {
                "base": "#FFFFFF",
                "gradient": ["#FFFFFF", "#F4F2FB"],
                "blobs": [
                    {"color": "#FF6B9D", "alpha": 80, "radius_factor": 0.5,
                     "softness": 0.6, "cx": 0.5, "cy": 0.5},
                ],
            },
        },
    },

    "neon": {
        "name": "neon",
        "description": "深色赛博 + 霓虹（青/品红/紫）",
        "fonts": {
            "title": "PingFang SC",
            "title_en": "Orbitron",
            "body": "PingFang SC",
            "body_en": "Inter",
            "mono": "JetBrains Mono",
        },
        "colors": {
            "text":        "#F4F6FF",
            "text_muted":  "#9097B5",
            "text_invert": "#0B0F1E",
            "text_soft":   "#1B2240",
            "primary":     "#22D3EE",
            "primary_2":   "#A855F7",
            "accent_pink": "#F472B6",
            "accent_amber": "#FBBF24",
            "accent_cyan": "#22D3EE",
            "accent_lime": "#A3E635",
            "surface":     "#0F1428",
            "surface_alt": "#1A2040",
            "line":        "#2A3158",
        },
        "gradients": {
            "primary":  ["#22D3EE", "#A855F7"],
            "warm":     ["#F472B6", "#FBBF24"],
            "cool":     ["#22D3EE", "#3B82F6"],
            "sunset":   ["#F472B6", "#A855F7", "#22D3EE"],
            "ocean":    ["#22D3EE", "#A855F7", "#F472B6"],
        },
        "backgrounds": {
            "cover": {
                "base": "#070A18",
                "gradient": ["#0F1428", "#070A18"],
                "blobs": [
                    {"color": "#22D3EE", "alpha": 180, "radius_factor": 0.5,
                     "softness": 0.5, "cx": 0.2, "cy": 0.3},
                    {"color": "#A855F7", "alpha": 170, "radius_factor": 0.45,
                     "softness": 0.5, "cx": 0.85, "cy": 0.25},
                    {"color": "#F472B6", "alpha": 150, "radius_factor": 0.4,
                     "softness": 0.5, "cx": 0.7, "cy": 0.85},
                ],
                "dots": True,
                "grid": True,
            },
            "section": {
                "base": "#070A18",
                "gradient": ["#0F1428", "#070A18"],
                "blobs": [
                    {"color": "#22D3EE", "alpha": 160, "radius_factor": 0.5,
                     "softness": 0.5, "cx": 0.5, "cy": 0.5},
                ],
                "grid": True,
                "dots": False,
            },
            "content": {
                "base": "#0B0F1E",
                "gradient": ["#0F1428", "#0B0F1E"],
                "blobs": [
                    {"color": "#22D3EE", "alpha": 60, "radius_factor": 0.4,
                     "softness": 0.6, "cx": 0.05, "cy": 0.1},
                    {"color": "#A855F7", "alpha": 60, "radius_factor": 0.4,
                     "softness": 0.6, "cx": 0.95, "cy": 0.9},
                ],
                "grid": True,
                "dots": False,
            },
            "closing": {
                "base": "#070A18",
                "gradient": ["#0F1428", "#070A18"],
                "blobs": [
                    {"color": "#A855F7", "alpha": 180, "radius_factor": 0.5,
                     "softness": 0.5, "cx": 0.3, "cy": 0.4},
                    {"color": "#22D3EE", "alpha": 160, "radius_factor": 0.4,
                     "softness": 0.5, "cx": 0.8, "cy": 0.6},
                ],
                "dots": True,
                "grid": False,
            },
            "quote": {
                "base": "#0B0F1E",
                "gradient": ["#0F1428", "#0B0F1E"],
                "blobs": [
                    {"color": "#F472B6", "alpha": 100, "radius_factor": 0.5,
                     "softness": 0.6, "cx": 0.5, "cy": 0.5},
                ],
            },
        },
    },

    "morandi": {
        "name": "morandi",
        "description": "柔和奶油 + 莫兰迪（米白/灰粉/雾蓝）",
        "fonts": {
            "title": "Songti SC",
            "title_en": "Playfair Display",
            "body": "PingFang SC",
            "body_en": "Inter",
            "mono": "JetBrains Mono",
        },
        "colors": {
            "text":        "#2E2A26",
            "text_muted":  "#7A726A",
            "text_invert": "#FAF7F2",
            "text_soft":   "#D8D1C7",
            "primary":     "#B57E6B",
            "primary_2":   "#8A9A8B",
            "accent_pink": "#D4A5A5",
            "accent_amber": "#C9A66B",
            "accent_cyan": "#8AAFB7",
            "accent_lime": "#A8B07A",
            "surface":     "#FAF7F2",
            "surface_alt": "#F0EAE0",
            "line":        "#D8D1C7",
        },
        "gradients": {
            "primary":  ["#D4A5A5", "#B57E6B"],
            "warm":     ["#D4A5A5", "#C9A66B"],
            "cool":     ["#8AAFB7", "#8A9A8B"],
            "sunset":   ["#D4A5A5", "#C9A66B", "#A8B07A"],
            "ocean":    ["#8AAFB7", "#A8B07A", "#8A9A8B"],
        },
        "backgrounds": {
            "cover": {
                "base": "#F0EAE0",
                "gradient": ["#FAF7F2", "#E8DFD3"],
                "blobs": [
                    {"color": "#D4A5A5", "alpha": 140, "radius_factor": 0.5,
                     "softness": 0.5, "cx": 0.2, "cy": 0.3},
                    {"color": "#8AAFB7", "alpha": 130, "radius_factor": 0.45,
                     "softness": 0.5, "cx": 0.85, "cy": 0.75},
                    {"color": "#C9A66B", "alpha": 100, "radius_factor": 0.35,
                     "softness": 0.55, "cx": 0.7, "cy": 0.2},
                ],
                "dots": False,
                "grid": False,
            },
            "section": {
                "base": "#E8DFD3",
                "gradient": ["#F0EAE0", "#D8D1C7"],
                "blobs": [
                    {"color": "#B57E6B", "alpha": 140, "radius_factor": 0.5,
                     "softness": 0.5, "cx": 0.5, "cy": 0.5},
                ],
            },
            "content": {
                "base": "#FAF7F2",
                "gradient": ["#FAF7F2", "#F4EFE5"],
                "blobs": [
                    {"color": "#D4A5A5", "alpha": 70, "radius_factor": 0.4,
                     "softness": 0.6, "cx": 0.05, "cy": 0.1},
                    {"color": "#8AAFB7", "alpha": 60, "radius_factor": 0.35,
                     "softness": 0.6, "cx": 0.95, "cy": 0.9},
                ],
            },
            "closing": {
                "base": "#2E2A26",
                "gradient": ["#3D3833", "#2E2A26"],
                "blobs": [
                    {"color": "#B57E6B", "alpha": 130, "radius_factor": 0.5,
                     "softness": 0.5, "cx": 0.3, "cy": 0.4},
                    {"color": "#8AAFB7", "alpha": 110, "radius_factor": 0.4,
                     "softness": 0.5, "cx": 0.8, "cy": 0.6},
                ],
            },
            "quote": {
                "base": "#FAF7F2",
                "gradient": ["#FAF7F2", "#F0EAE0"],
                "blobs": [
                    {"color": "#D4A5A5", "alpha": 80, "radius_factor": 0.5,
                     "softness": 0.6, "cx": 0.5, "cy": 0.5},
                ],
            },
        },
    },
}


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def in2emu(inches: float) -> int:
    return Inches(inches)


def set_run(run, text: str, *, font: str = None, size: int = None,
            color: str = None, bold: bool = None, italic: bool = None):
    run.text = text
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color.lstrip("#"))
    if font is not None:
        run.font.name = font
        # Set East Asian font as well for Chinese rendering
        rPr = run._r.get_or_add_rPr()
        # Remove any existing eastAsia child
        for ea in rPr.findall(qn("a:ea")):
            rPr.remove(ea)
        ea = etree.SubElement(rPr, qn("a:ea"))
        ea.set("typeface", font)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic


def add_textbox(slide, x: float, y: float, w: float, h: float,
                text: str = "", *, font: str = None, size: int = 18,
                color: str = None, bold: bool = False, italic: bool = False,
                align: str = "left", anchor: str = "top",
                auto_size: bool = False) -> "pptx.shapes.autoshape.Shape":
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)

    if anchor == "middle":
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    elif anchor == "bottom":
        tf.vertical_anchor = MSO_ANCHOR.BOTTOM
    else:
        tf.vertical_anchor = MSO_ANCHOR.TOP

    p = tf.paragraphs[0]
    if align == "center":
        p.alignment = PP_ALIGN.CENTER
    elif align == "right":
        p.alignment = PP_ALIGN.RIGHT
    else:
        p.alignment = PP_ALIGN.LEFT

    if text:
        run = p.add_run()
        set_run(run, text, font=font, size=size, color=color, bold=bold, italic=italic)
    return tb


def add_paragraph(text_frame, text: str, *, font: str = None, size: int = 18,
                  color: str = None, bold: bool = False, italic: bool = False,
                  align: str = "left", space_after: int = 6):
    p = text_frame.add_paragraph()
    if align == "center":
        p.alignment = PP_ALIGN.CENTER
    elif align == "right":
        p.alignment = PP_ALIGN.RIGHT
    else:
        p.alignment = PP_ALIGN.LEFT
    p.space_after = Pt(space_after)
    run = p.add_run()
    set_run(run, text, font=font, size=size, color=color, bold=bold, italic=italic)
    return p


def set_solid_fill(shape, color_hex: str, alpha: float = 1.0):
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(color_hex.lstrip("#"))
    if alpha < 1.0:
        # Set transparency in the fill XML
        sp = shape.fill.fore_color._xFill
        # Need to add alpha attribute
        solidFill = sp
        for srgb in solidFill.findall(qn("a:srgbClr")):
            srgb.set("val", color_hex.lstrip("#"))
            # alpha child
            for child in list(srgb):
                if child.tag.endswith("}alpha"):
                    srgb.remove(child)
            alpha_el = etree.SubElement(srgb, qn("a:alpha"))
            alpha_el.set("val", str(int(alpha * 100000)))


def set_line(shape, color_hex: str, width_pt: float = 0.75,
             transparency: float = 0.0):
    shape.line.color.rgb = RGBColor.from_string(color_hex.lstrip("#"))
    shape.line.width = Pt(width_pt)
    if transparency > 0:
        ln = shape.line._get_or_add_ln()
        for child in list(ln):
            if child.tag.endswith("}solidFill"):
                for srgb in child.findall(qn("a:srgbClr")):
                    srgb.set("val", color_hex.lstrip("#"))
                    for c2 in list(srgb):
                        if c2.tag.endswith("}alpha"):
                            srgb.remove(c2)
                    a = etree.SubElement(srgb, qn("a:alpha"))
                    a.set("val", str(int((1 - transparency) * 100000)))


def no_line(shape):
    shape.line.fill.background()


def rounded_rect(slide, x, y, w, h, *, fill: str = None, line: str = None,
                 line_width: float = 0.75, line_transparency: float = 0.0,
                 corner: float = 0.12):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                    Inches(x), Inches(y), Inches(w), Inches(h))
    # python-pptx default corner radius is ~10% — adjust via XML
    if fill is not None:
        set_solid_fill(shape, fill)
    else:
        shape.fill.background()
    if line is None:
        no_line(shape)
    else:
        set_line(shape, line, line_width, line_transparency)
    # adjust corner radius
    try:
        adj = shape.adjustments
        adj[0] = corner
    except Exception:
        pass
    return shape


def ellipse(slide, x, y, w, h, *, fill: str = None, line: str = None):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is not None:
        set_solid_fill(s, fill)
    else:
        s.fill.background()
    if line is None:
        no_line(s)
    else:
        set_line(s, line, 0.75)
    return s


def line_shape(slide, x1, y1, x2, y2, *, color: str = "#000000", width_pt: float = 1.0):
    s = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    s.line.color.rgb = RGBColor.from_string(color.lstrip("#"))
    s.line.width = Pt(width_pt)
    return s


# -----------------------------------------------------------------------------
# Builder
# -----------------------------------------------------------------------------

class Builder:
    """Top-level builder. Add slides via typed methods, then save()."""

    def __init__(self, theme: str = "aurora",
                 aspect: str = "16:9",
                 cache_dir: Optional[str] = None):
        if theme not in THEMES:
            raise ValueError(f"Unknown theme: {theme!r}. "
                             f"Choose from {list(THEMES)}")
        self.theme = THEMES[theme]
        self.theme_name = theme
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_W_IN)
        self.prs.slide_height = Inches(SLIDE_H_IN)
        # blank layout
        self._blank = self.prs.slide_layouts[6]
        self._variant = 0
        self._cache_dir = cache_dir or tempfile.mkdtemp(prefix="elegant_ppt_")
        self._temp_pngs: List[str] = []

    # -- Background -----------------------------------------------------------

    def _add_background(self, slide, kind: str = "content",
                         override: Optional[dict] = None):
        """Render and add a background image for the given page kind."""
        spec = make_background(self.theme, kind=kind,
                                size=(CANVAS_W, CANVAS_H),
                                variant=self._variant)
        self._variant += 1
        # Save to a temp file, then add_picture, then we leave the file
        # (python-pptx needs a path; we don't delete while the prs is open)
        out_path = save_temp_png(spec, self._cache_dir,
                                  f"bg_{kind}_{self._variant}.png")
        self._temp_pngs.append(out_path)
        # Place as full-bleed image
        slide.shapes.add_picture(out_path, 0, 0,
                                  width=Inches(SLIDE_W_IN),
                                  height=Inches(SLIDE_H_IN))

    def add_blank_slide(self) -> "pptx.slide.Slide":
        slide = self.prs.slides.add_slide(self._blank)
        return slide

    # -- Footer / header decoration -------------------------------------------

    def _add_footer(self, slide, page_label: str = None):
        c = self.theme["colors"]
        if page_label is not None:
            add_textbox(slide, SLIDE_W_IN - 1.6, SLIDE_H_IN - 0.45,
                        1.4, 0.3, page_label, font=self.theme["fonts"]["body_en"],
                        size=10, color=c["text_muted"], align="right")
        add_textbox(slide, 0.6, SLIDE_H_IN - 0.45, 6.0, 0.3,
                    "· elegant-ppt-builder ·", font=self.theme["fonts"]["body_en"],
                    size=10, color=c["text_muted"], align="left")

    def _add_corner_marks(self, slide, color: str = None):
        """Small decorative marks in the top-right and bottom-left."""
        c = color or self.theme["colors"]["primary"]
        # Top-left thin bar
        line_shape(slide, 0.5, 0.5, 1.4, 0.5, color=c, width_pt=2.0)
        ellipse(slide, 1.5, 0.42, 0.16, 0.16, fill=c)
        # Bottom-right thin bar
        line_shape(slide, SLIDE_W_IN - 1.4, SLIDE_H_IN - 0.5,
                    SLIDE_W_IN - 0.5, SLIDE_H_IN - 0.5, color=c, width_pt=2.0)
        ellipse(slide, SLIDE_W_IN - 1.58, SLIDE_H_IN - 0.58,
                0.16, 0.16, fill=c)

    # -- Page: Cover ----------------------------------------------------------

    def cover(self, title: str, subtitle: str = "", *,
              eyebrow: str = None, accent: str = None,
              bottom_left: str = None, bottom_right: str = None):
        slide = self.add_blank_slide()
        self._add_background(slide, "cover")
        c = self.theme["colors"]
        f = self.theme["fonts"]

        if eyebrow:
            add_textbox(slide, 0.8, 2.1, 8.0, 0.45,
                        eyebrow.upper(), font=f["body_en"],
                        size=14, color=c["text_soft"], bold=True)

        # Title
        add_textbox(slide, 0.8, 2.55, 11.5, 2.0, title,
                    font=f["title"], size=66, color=c["text_invert"], bold=True)

        if subtitle:
            add_textbox(slide, 0.8, 4.6, 10.0, 0.6, subtitle,
                        font=f["body"], size=22,
                        color=c["text_soft"])

        if accent:
            add_textbox(slide, 0.8, 5.4, 11.5, 0.5, accent,
                        font=f["body_en"], size=16, color=c["accent_cyan"],
                        bold=True, italic=True)

        # Footer
        if bottom_left:
            add_textbox(slide, 0.8, SLIDE_H_IN - 0.7, 6.0, 0.3,
                        bottom_left, font=f["body_en"], size=11,
                        color=c["text_soft"])
        if bottom_right:
            add_textbox(slide, SLIDE_W_IN - 4.0, SLIDE_H_IN - 0.7, 3.2, 0.3,
                        bottom_right, font=f["body_en"], size=11,
                        color=c["text_soft"], align="right")
        return slide

    # -- Page: Section Divider ------------------------------------------------

    def section(self, number: str, title: str, subtitle: str = "",
                 *, side: str = "left"):
        slide = self.add_blank_slide()
        self._add_background(slide, "section")
        c = self.theme["colors"]
        f = self.theme["fonts"]

        # Giant number
        if side == "left":
            nx = 0.8
            ax = "left"
        else:
            nx = SLIDE_W_IN - 5.0
            ax = "right"
        add_textbox(slide, nx, 1.8, 4.5, 3.0, number,
                    font=f["title_en"], size=180, color=c["primary"],
                    bold=True, align=ax)

        # Vertical accent line
        if side == "left":
            line_shape(slide, 5.4, 2.6, 5.4, SLIDE_H_IN - 2.6,
                        color=c["accent_cyan"], width_pt=2.0)
            tx = 5.9
        else:
            line_shape(slide, SLIDE_W_IN - 5.9, 2.6,
                        SLIDE_W_IN - 5.9, SLIDE_H_IN - 2.6,
                        color=c["accent_cyan"], width_pt=2.0)
            tx = 0.8
            ax = "right"

        add_textbox(slide, tx, 3.0, 6.6, 1.2, title,
                    font=f["title"], size=54, color=c["text_invert"],
                    bold=True, align=ax)
        if subtitle:
            add_textbox(slide, tx, 4.3, 6.6, 0.6, subtitle,
                        font=f["body"], size=18, color=c["text_soft"],
                        align=ax)
        return slide

    # -- Page: Title + Bullets ------------------------------------------------

    def _page_header(self, slide, title: str, eyebrow: str = None):
        c = self.theme["colors"]
        f = self.theme["fonts"]
        if eyebrow:
            add_textbox(slide, 0.8, 0.6, 6.0, 0.4, eyebrow.upper(),
                        font=f["body_en"], size=12,
                        color=c["primary"], bold=True)
            ty = 1.05
        else:
            ty = 0.85
        add_textbox(slide, 0.8, ty, 11.5, 0.9, title,
                    font=f["title"], size=40,
                    color=c["text"], bold=True)
        # underline accent
        line_shape(slide, 0.8, ty + 0.95, 1.6, ty + 0.95,
                    color=c["primary"], width_pt=3.0)

    def bullets(self, title: str, items: Sequence[str], *,
                eyebrow: str = None,
                icons: Sequence[str] = None,
                accent_colors: Sequence[str] = None):
        slide = self.add_blank_slide()
        self._add_background(slide, "content")
        c = self.theme["colors"]
        f = self.theme["fonts"]
        self._page_header(slide, title, eyebrow)

        y0 = 2.3
        row_h = 0.85
        default_icons = ["◆", "●", "▲", "■", "★", "◇"]
        default_accents = [c["primary"], c["accent_pink"], c["accent_cyan"],
                            c["accent_amber"], c["accent_lime"], c["primary_2"]]

        for i, item in enumerate(items):
            yy = y0 + i * row_h
            icon = (icons[i] if icons and i < len(icons)
                    else default_icons[i % len(default_icons)])
            accent = (accent_colors[i] if accent_colors and i < len(accent_colors)
                      else default_accents[i % len(default_accents)])
            # icon disc
            ellipse(slide, 0.95, yy + 0.18, 0.5, 0.5, fill=accent)
            add_textbox(slide, 0.95, yy + 0.18, 0.5, 0.5, icon,
                        font=f["body_en"], size=18, color="#FFFFFF",
                        bold=True, align="center", anchor="middle")
            add_textbox(slide, 1.7, yy + 0.1, 10.8, 0.7, item,
                        font=f["body"], size=20, color=c["text"])
        self._add_footer(slide, str(len(self.prs.slides)))
        return slide

    # -- Page: Cards grid -----------------------------------------------------

    def cards_grid(self, title: str, cards: Sequence[dict], *,
                   eyebrow: str = None, cols: int = 3):
        """Each card dict:
            {title, body, icon (str), accent (color hex or theme key),
             metric (str, optional)}
        """
        slide = self.add_blank_slide()
        self._add_background(slide, "content")
        c = self.theme["colors"]
        f = self.theme["fonts"]
        self._page_header(slide, title, eyebrow)

        n = len(cards)
        cols = max(1, min(cols, n))
        rows = math.ceil(n / cols)
        grid_x0 = 0.8
        grid_y0 = 2.4
        grid_w = SLIDE_W_IN - 1.6
        grid_h = 4.5
        gap_x = 0.25
        gap_y = 0.25
        card_w = (grid_w - gap_x * (cols - 1)) / cols
        card_h = (grid_h - gap_y * (rows - 1)) / rows

        accent_keys = ["primary", "accent_pink", "accent_cyan",
                        "accent_amber", "accent_lime", "primary_2"]
        for i, card in enumerate(cards):
            r = i // cols
            col = i % cols
            x = grid_x0 + col * (card_w + gap_x)
            y = grid_y0 + r * (card_h + gap_y)
            accent_hex = card.get("accent") or c[accent_keys[i % len(accent_keys)]]
            accent_hex = accent_hex.lstrip("#") if "#" in accent_hex else accent_hex
            if accent_hex in c:
                accent_hex = c[accent_hex].lstrip("#")

            # Card body
            rounded_rect(slide, x, y, card_w, card_h,
                          fill="#FFFFFF", corner=0.08)
            # Top accent bar
            line_shape(slide, x, y, x + card_w, y,
                        color="#" + accent_hex, width_pt=6.0)
            # Icon disc
            disc_r = 0.55
            ellipse(slide, x + 0.35, y + 0.45, disc_r, disc_r,
                    fill="#" + accent_hex)
            icon_char = card.get("icon", "✦")
            add_textbox(slide, x + 0.35, y + 0.45, disc_r, disc_r,
                        icon_char, font=f["body_en"], size=22,
                        color="#FFFFFF", bold=True,
                        align="center", anchor="middle")

            if card.get("metric"):
                add_textbox(slide, x + 0.35, y + 1.15, card_w - 0.7, 0.7,
                            card["metric"], font=f["title_en"], size=32,
                            color="#" + accent_hex, bold=True)
                ty = 1.95
            else:
                ty = 1.2

            add_textbox(slide, x + 0.35, y + ty, card_w - 0.7, 0.5,
                        card["title"], font=f["title"], size=18,
                        color=c["text"], bold=True)
            add_textbox(slide, x + 0.35, y + ty + 0.55, card_w - 0.7,
                        card_h - ty - 0.7, card["body"],
                        font=f["body"], size=13, color=c["text_muted"])
        self._add_footer(slide, str(len(self.prs.slides)))
        return slide

    # -- Page: Big Number KPI -------------------------------------------------

    def big_number(self, title: str, metrics: Sequence[dict], *,
                   eyebrow: str = None):
        """Each metric dict: {value (str), label (str), delta (str, optional),
        accent (color, optional)}"""
        slide = self.add_blank_slide()
        self._add_background(slide, "content")
        c = self.theme["colors"]
        f = self.theme["fonts"]
        self._page_header(slide, title, eyebrow)

        n = len(metrics)
        margin = 0.8
        gap = 0.4
        total_w = SLIDE_W_IN - 2 * margin
        item_w = (total_w - gap * (n - 1)) / n
        y0 = 2.5
        h = 3.2

        accent_keys = ["primary", "accent_pink", "accent_cyan",
                        "accent_amber", "accent_lime", "primary_2"]

        for i, m in enumerate(metrics):
            x = margin + i * (item_w + gap)
            accent_hex = m.get("accent") or c[accent_keys[i % len(accent_keys)]]
            accent_hex = accent_hex.lstrip("#") if "#" in accent_hex else accent_hex
            if accent_hex in c:
                accent_hex = c[accent_hex].lstrip("#")

            # Card
            rounded_rect(slide, x, y0, item_w, h, fill="#FFFFFF", corner=0.06)
            # Vertical accent line on the left
            line_shape(slide, x + 0.3, y0 + 0.4, x + 0.3, y0 + h - 0.4,
                        color="#" + accent_hex, width_pt=4.0)
            # Value
            add_textbox(slide, x + 0.5, y0 + 0.5, item_w - 0.7, 1.4,
                        m["value"], font=f["title_en"], size=68,
                        color="#" + accent_hex, bold=True)
            # Label
            add_textbox(slide, x + 0.5, y0 + 1.9, item_w - 0.7, 0.5,
                        m["label"], font=f["body"], size=15,
                        color=c["text"], bold=True)
            # Delta
            if m.get("delta"):
                add_textbox(slide, x + 0.5, y0 + 2.5, item_w - 0.7, 0.5,
                            m["delta"], font=f["body_en"], size=13,
                            color=c["text_muted"])
        self._add_footer(slide, str(len(self.prs.slides)))
        return slide

    # -- Page: Two column ----------------------------------------------------

    def two_column(self, title: str, left: dict, right: dict, *,
                   eyebrow: str = None):
        slide = self.add_blank_slide()
        self._add_background(slide, "content")
        c = self.theme["colors"]
        f = self.theme["fonts"]
        self._page_header(slide, title, eyebrow)

        margin = 0.8
        gap = 0.4
        col_w = (SLIDE_W_IN - 2 * margin - gap) / 2
        y0 = 2.4
        h = 4.4

        for i, block in enumerate([left, right]):
            x = margin + i * (col_w + gap)
            accent_hex = block.get("accent", c["primary"]).lstrip("#")
            if accent_hex in c:
                accent_hex = c[accent_hex].lstrip("#")
            rounded_rect(slide, x, y0, col_w, h, fill="#FFFFFF", corner=0.05)
            # accent top
            line_shape(slide, x, y0, x + col_w, y0,
                        color="#" + accent_hex, width_pt=5.0)
            add_textbox(slide, x + 0.4, y0 + 0.35, col_w - 0.8, 0.5,
                        block.get("eyebrow", "").upper(),
                        font=f["body_en"], size=12,
                        color="#" + accent_hex, bold=True)
            add_textbox(slide, x + 0.4, y0 + 0.85, col_w - 0.8, 0.7,
                        block.get("title", ""), font=f["title"], size=24,
                        color=c["text"], bold=True)
            body = block.get("body", "")
            tb = add_textbox(slide, x + 0.4, y0 + 1.7, col_w - 0.8,
                              h - 2.0, "", font=f["body"], size=14,
                              color=c["text_muted"])
            for j, line_ in enumerate(body.split("\n")):
                if j == 0:
                    p = tb.text_frame.paragraphs[0]
                else:
                    p = tb.text_frame.add_paragraph()
                p.alignment = PP_ALIGN.LEFT
                p.space_after = Pt(6)
                run = p.add_run()
                set_run(run, line_, font=f["body"], size=14,
                        color=c["text_muted"])
        self._add_footer(slide, str(len(self.prs.slides)))
        return slide

    # -- Page: Timeline / Process --------------------------------------------

    def timeline(self, title: str, events: Sequence[dict], *,
                  eyebrow: str = None, orientation: str = "horizontal"):
        """events: [{label, title, body, color (optional)}]"""
        slide = self.add_blank_slide()
        self._add_background(slide, "content")
        c = self.theme["colors"]
        f = self.theme["fonts"]
        self._page_header(slide, title, eyebrow)

        n = len(events)
        accent_keys = ["primary", "accent_pink", "accent_cyan",
                        "accent_amber", "accent_lime", "primary_2"]

        if orientation == "horizontal":
            y_line = 4.0
            margin = 1.0
            gap = 0.2
            item_w = (SLIDE_W_IN - 2 * margin) / n
            # main line
            line_shape(slide, margin + 0.4, y_line,
                        SLIDE_W_IN - margin - 0.4, y_line,
                        color=c["line"], width_pt=2.0)
            for i, e in enumerate(events):
                cx = margin + item_w * (i + 0.5)
                accent_hex = e.get("color") or c[accent_keys[i % len(accent_keys)]]
                accent_hex = accent_hex.lstrip("#") if "#" in accent_hex else accent_hex
                if accent_hex in c:
                    accent_hex = c[accent_hex].lstrip("#")
                # dot
                ellipse(slide, cx - 0.18, y_line - 0.18, 0.36, 0.36,
                        fill="#" + accent_hex)
                # label above
                add_textbox(slide, cx - item_w / 2 + 0.2, y_line - 1.4,
                            item_w - 0.4, 0.5, e.get("label", "").upper(),
                            font=f["body_en"], size=12,
                            color="#" + accent_hex, bold=True, align="center")
                add_textbox(slide, cx - item_w / 2 + 0.2, y_line - 0.95,
                            item_w - 0.4, 0.5, e.get("title", ""),
                            font=f["title"], size=18, color=c["text"],
                            bold=True, align="center")
                # body below
                add_textbox(slide, cx - item_w / 2 + 0.2, y_line + 0.4,
                            item_w - 0.4, 1.8, e.get("body", ""),
                            font=f["body"], size=12, color=c["text_muted"],
                            align="center")
        else:
            # vertical
            margin = 1.2
            x_line = 2.5
            gap = 0.4
            item_h = (SLIDE_H_IN - 2.4 - 0.5 - gap * (n - 1)) / n
            line_shape(slide, x_line, 2.4, x_line, SLIDE_H_IN - 0.5,
                        color=c["line"], width_pt=2.0)
            for i, e in enumerate(events):
                cy = 2.4 + item_h * (i + 0.5) + gap * i - gap / 2
                accent_hex = e.get("color") or c[accent_keys[i % len(accent_keys)]]
                accent_hex = accent_hex.lstrip("#") if "#" in accent_hex else accent_hex
                if accent_hex in c:
                    accent_hex = c[accent_hex].lstrip("#")
                ellipse(slide, x_line - 0.18, cy - 0.18, 0.36, 0.36,
                        fill="#" + accent_hex)
                add_textbox(slide, x_line + 0.4, cy - 0.4, SLIDE_W_IN - x_line - 1.5,
                            0.5, e.get("label", "").upper(),
                            font=f["body_en"], size=12,
                            color="#" + accent_hex, bold=True)
                add_textbox(slide, x_line + 0.4, cy + 0.0, SLIDE_W_IN - x_line - 1.5,
                            0.5, e.get("title", ""),
                            font=f["title"], size=20, color=c["text"], bold=True)
                add_textbox(slide, x_line + 0.4, cy + 0.55, SLIDE_W_IN - x_line - 1.5,
                            0.8, e.get("body", ""),
                            font=f["body"], size=13, color=c["text_muted"])
        self._add_footer(slide, str(len(self.prs.slides)))
        return slide

    # -- Page: Bar chart (custom rendered) -----------------------------------

    def bar_chart(self, title: str, labels: Sequence[str],
                   values: Sequence[float], *,
                   eyebrow: str = None,
                   highlight_index: int = -1,
                   value_format: str = "{:.0f}",
                   unit: str = ""):
        slide = self.add_blank_slide()
        self._add_background(slide, "content")
        c = self.theme["colors"]
        f = self.theme["fonts"]
        self._page_header(slide, title, eyebrow)

        margin = 0.8
        chart_x = margin
        chart_y = 2.5
        chart_w = SLIDE_W_IN - 2 * margin
        chart_h = 3.6
        max_v = max(values) if values else 1
        max_v = max_v * 1.15 if max_v > 0 else 1
        n = len(labels)
        bar_gap = 0.25
        bar_w = (chart_w - bar_gap * (n + 1)) / n
        grad_palette = [
            ("#5B6CFF", "#6C5CE7"),
            ("#22D3EE", "#5B6CFF"),
            ("#FF6B9D", "#FFB547"),
            ("#A855F7", "#F472B6"),
        ]
        for i, v in enumerate(values):
            x = chart_x + bar_gap + i * (bar_w + bar_gap)
            bar_h = (v / max_v) * (chart_h - 0.6)
            y = chart_y + chart_h - bar_h - 0.3
            top, bot = grad_palette[i % len(grad_palette)]
            if highlight_index == i:
                top, bot = ("#FF6B9D", "#FFB547")
            # Render gradient bar as image
            bar_img = gradient_image([top, bot], angle=90.0,
                                        size=(int(bar_w * 200),
                                              max(2, int(bar_h * 200))),
                                        kind="linear")
            bar_path = save_temp_png(bar_img, self._cache_dir,
                                       f"bar_{self._variant}_{i}.png")
            self._temp_pngs.append(bar_path)
            pic = slide.shapes.add_picture(bar_path, Inches(x), Inches(y),
                                            width=Inches(bar_w),
                                            height=Inches(bar_h))
            # add corner-radius approximation by setting shape adjustments
            # (pictures can't be rounded, so we overlay a rounded rect mask
            # would require an SVG image; for now we accept square bars)

            # value label
            val_txt = value_format.format(v) + unit
            add_textbox(slide, x, y - 0.55, bar_w, 0.4, val_txt,
                        font=f["title_en"], size=14,
                        color=c["text"], bold=True, align="center")
            # category label
            add_textbox(slide, x, chart_y + chart_h - 0.25,
                        bar_w, 0.4, labels[i],
                        font=f["body"], size=12,
                        color=c["text_muted"], align="center")
        self._add_footer(slide, str(len(self.prs.slides)))
        return slide

    # -- Page: Donut (ring) chart -------------------------------------------

    def donut_chart(self, title: str, segments: Sequence[dict], *,
                    eyebrow: str = None,
                    center_label: str = "", center_value: str = ""):
        """segments: [{label, value, color (optional)}]"""
        slide = self.add_blank_slide()
        self._add_background(slide, "content")
        c = self.theme["colors"]
        f = self.theme["fonts"]
        self._page_header(slide, title, eyebrow)

        from PIL import ImageDraw
        from visual import ring_progress
        import math

        # Donut image (left side)
        donut_size = 600
        img = Image.new("RGBA", (donut_size, donut_size), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cx = cy = donut_size / 2
        r_out = donut_size / 2 - 20
        r_in = r_out - 70
        total = sum(s["value"] for s in segments) or 1
        start = -90
        accent_keys = ["primary", "accent_pink", "accent_cyan",
                        "accent_amber", "accent_lime", "primary_2"]
        for i, s in enumerate(segments):
            hex_ = s.get("color") or c[accent_keys[i % len(accent_keys)]]
            if hex_.startswith("#"):
                pass
            else:
                hex_ = c.get(hex_, "#6C5CE7")
            rgb = hex_to_rgb(hex_)
            sweep = 360 * s["value"] / total
            # outer arc
            d.pieslice((cx - r_out, cy - r_out, cx + r_out, cy + r_out),
                        start=start, end=start + sweep,
                        fill=rgb + (255,))
            start += sweep
        # inner cut
        d.ellipse((cx - r_in, cy - r_in, cx + r_in, cy + r_in),
                   fill=(255, 255, 255, 0))
        # center text — render with a real font
        if center_value:
            big_font = load_font(64, prefer_chinese=False)
            d.text((cx, cy - 16), center_value,
                    fill=hex_to_rgb(c["text"]) + (255,),
                    anchor="mm", font=big_font)
        if center_label:
            small_font = load_font(20, prefer_chinese=True)
            d.text((cx, cy + 30), center_label,
                    fill=hex_to_rgb(c["text_muted"]) + (255,),
                    anchor="mm", font=small_font)

        donut_path = save_temp_png(img, self._cache_dir,
                                    f"donut_{self._variant}.png")
        self._temp_pngs.append(donut_path)
        slide.shapes.add_picture(donut_path, Inches(0.8), Inches(2.4),
                                  width=Inches(4.5), height=Inches(4.5))

        # Legend (right side)
        legend_x = 6.0
        legend_y = 2.6
        for i, s in enumerate(segments):
            hex_ = s.get("color") or c[accent_keys[i % len(accent_keys)]]
            if not hex_.startswith("#"):
                hex_ = c.get(hex_, "#6C5CE7")
            yy = legend_y + i * 0.7
            ellipse(slide, legend_x, yy + 0.08, 0.32, 0.32, fill=hex_)
            pct = s["value"] / total * 100
            add_textbox(slide, legend_x + 0.5, yy, 4.0, 0.4, s["label"],
                        font=f["body"], size=15, color=c["text"], bold=True)
            add_textbox(slide, legend_x + 0.5, yy + 0.35, 4.0, 0.4,
                        f"{pct:.1f}%", font=f["body_en"], size=13,
                        color=c["text_muted"])
        self._add_footer(slide, str(len(self.prs.slides)))
        return slide

    # -- Page: Quote ---------------------------------------------------------

    def quote(self, quote_text: str, author: str = "", role: str = ""):
        slide = self.add_blank_slide()
        self._add_background(slide, "quote")
        c = self.theme["colors"]
        f = self.theme["fonts"]

        # Big quote mark
        add_textbox(slide, 0.8, 0.6, 2.0, 2.0, "“",
                    font=f["title_en"], size=180, color=c["primary"],
                    bold=True)
        # Quote text
        add_textbox(slide, 1.2, 2.4, SLIDE_W_IN - 2.4, 2.6, quote_text,
                    font=f["title"], size=32, color=c["text"],
                    italic=True, align="center")
        # Divider
        line_shape(slide, SLIDE_W_IN / 2 - 0.4, 5.3,
                    SLIDE_W_IN / 2 + 0.4, 5.3,
                    color=c["primary"], width_pt=2.0)
        # Author
        if author:
            add_textbox(slide, 1.2, 5.5, SLIDE_W_IN - 2.4, 0.5, author,
                        font=f["body"], size=18, color=c["text"],
                        bold=True, align="center")
        if role:
            add_textbox(slide, 1.2, 6.0, SLIDE_W_IN - 2.4, 0.5, role,
                        font=f["body_en"], size=13, color=c["text_muted"],
                        align="center")
        return slide

    # -- Page: Closing / Thanks ----------------------------------------------

    def thanks(self, message: str = "Thank You",
                subtitle: str = "期待与您的下一次交流",
                contact: str = ""):
        slide = self.add_blank_slide()
        self._add_background(slide, "closing")
        c = self.theme["colors"]
        f = self.theme["fonts"]

        add_textbox(slide, 0.8, 2.6, SLIDE_W_IN - 1.6, 1.6, message,
                    font=f["title"], size=80, color=c["text_invert"],
                    bold=True, align="center")
        if subtitle:
            add_textbox(slide, 0.8, 4.3, SLIDE_W_IN - 1.6, 0.5, subtitle,
                        font=f["body"], size=20, color=c["text_soft"],
                        align="center")
        if contact:
            add_textbox(slide, 0.8, 5.5, SLIDE_W_IN - 1.6, 0.4, contact,
                        font=f["body_en"], size=14, color=c["text_soft"],
                        align="center")
        return slide

    # -- Page: Custom content (escape hatch) ---------------------------------

    def custom(self, build_fn):
        """Add a custom slide. build_fn(slide, builder) is called with the
        blank slide and the builder (for theme/colors/fonts access)."""
        slide = self.add_blank_slide()
        self._add_background(slide, "content")
        build_fn(slide, self)
        return slide

    # -- Save ----------------------------------------------------------------

    def save(self, path: str):
        self.prs.save(path)
        return path


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main(argv: List[str]) -> int:
    """Minimal CLI: python pptx_builder.py demo <out.pptx> [theme]"""
    if len(argv) < 3 or argv[1] != "demo":
        print("Usage: python pptx_builder.py demo <out.pptx> [theme]")
        return 1
    out = argv[2]
    theme = argv[3] if len(argv) > 3 else "aurora"
    b = Builder(theme=theme)
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
    ], eyebrow="Highlights")
    b.big_number("Key Metrics", [
        {"value": "¥ 1.24B", "label": "季度营收", "delta": "+38% YoY",
         "accent": "primary"},
        {"value": "12", "label": "新签客户", "delta": "+5 vs Q1",
         "accent": "accent_pink"},
        {"value": "67", "label": "NPS 得分", "delta": "+12 pts",
         "accent": "accent_cyan"},
        {"value": "98%", "label": "续约率", "delta": "+3 pts",
         "accent": "accent_amber"},
    ], eyebrow="By the numbers")
    b.cards_grid("Focus Areas", [
        {"title": "产品创新", "icon": "✦", "metric": "3.2x",
         "body": "推出 4 项核心功能，用户活跃度提升 220%。"},
        {"title": "市场拓展", "icon": "◈", "metric": "5 城",
         "body": "新增华东 5 城渠道，区域营收占比突破 35%。"},
        {"title": "组织升级", "icon": "✧", "metric": "120 人",
         "body": "完成关键岗位招聘 120 人，人才密度提升。"},
    ], eyebrow="What worked", cols=3)
    b.timeline("H2 Roadmap", [
        {"label": "Phase 1", "title": "Discovery",
         "body": "用户调研 & 需求分析", "color": "primary"},
        {"label": "Phase 2", "title": "Design",
         "body": "产品原型 & 用户测试", "color": "accent_pink"},
        {"label": "Phase 3", "title": "Build",
         "body": "敏捷开发 & 持续交付", "color": "accent_cyan"},
        {"label": "Phase 4", "title": "Launch",
         "body": "灰度发布 & 增长迭代", "color": "accent_amber"},
    ], eyebrow="Path forward", orientation="horizontal")
    b.bar_chart("Revenue by Region", ["华东", "华南", "华北", "西部"],
                 [420, 310, 280, 150],
                 eyebrow="Q2 2026", unit="M",
                 highlight_index=0)
    b.donut_chart("Channel Mix", [
        {"label": "直销", "value": 45, "color": "primary"},
        {"label": "渠道", "value": 30, "color": "accent_pink"},
        {"label": "电商", "value": 15, "color": "accent_cyan"},
        {"label": "其他", "value": 10, "color": "accent_amber"},
    ], eyebrow="Q2 2026", center_value="100%", center_label="Total")
    b.quote("真正优秀的作品，是当所有人离开屏幕后，仍然在脑海里回响的旋律。",
             "— Jonathan Ive",
             "Chief Design Officer, Apple")
    b.thanks("Thank You", "期待与您的下一次交流", "hello@company.com")
    b.save(out)
    print(f"Saved demo deck to: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
