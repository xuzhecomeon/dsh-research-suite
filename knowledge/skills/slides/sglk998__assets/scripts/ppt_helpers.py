"""
学术论文汇报PPT生成器 — 通用辅助函数
配色: 科研蓝 #5A97D0 | 字体: 微软雅黑 + Arial | 风格: 学术会议风
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ======== 全局样式 ========
BLUE = RGBColor(0x5A, 0x97, 0xD0)
DARK_BLUE = RGBColor(0x2E, 0x5A, 0x8B)
LIGHT_BLUE_BG = RGBColor(0xEB, 0xF3, 0xFA)
DARK = RGBColor(0x33, 0x33, 0x33)
GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT_GRAY = RGBColor(0x99, 0x99, 0x99)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE = RGBColor(0xE8, 0x7A, 0x00)
GREEN = RGBColor(0x4A, 0x90, 0x4A)
RED = RGBColor(0xE5, 0x39, 0x35)
PURPLE = RGBColor(0x9C, 0x27, 0xB0)

FONT_CN = '微软雅黑'
FONT_EN = 'Arial'

# ======== 辅助函数 ========

def TB(slide, l, t, w, h, text, size=16, color=DARK, bold=False, align=PP_ALIGN.LEFT, cn=True):
    """Quick single-line textbox"""
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    f = p.font
    f.name = FONT_CN if cn else FONT_EN
    f.size = Pt(size)
    f.color.rgb = color
    f.bold = bold
    p.line_spacing = 1.15
    return tb


def MTB(slide, l, t, w, h, lines, sizes=None, colors=None, bolds=None, aligns=None, cns=None):
    """Multi-line textbox with per-line formatting"""
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.alignment = aligns[i] if (aligns and i < len(aligns)) else PP_ALIGN.LEFT
        sz = sizes[i] if (sizes and i < len(sizes)) else 16
        clr = colors[i] if (colors and i < len(colors)) else DARK
        bld = bolds[i] if (bolds and i < len(bolds)) else False
        cn = cns[i] if (cns and i < len(cns)) else True
        f = p.font
        f.name = FONT_CN if cn else FONT_EN
        f.size = Pt(sz)
        f.color.rgb = clr
        f.bold = bld
        p.line_spacing = 1.15
    return tb


def BOX(slide, l, t, w, h, fill_color, border_color=None):
    """Colored rounded rectangle card"""
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    box.fill.solid()
    box.fill.fore_color.rgb = fill_color
    if border_color:
        box.line.color.rgb = border_color
        box.line.width = Pt(0.5)
    else:
        box.line.fill.background()
    return box


def CIRCLE(slide, l, t, sz, fill_color):
    """Filled circle"""
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(l), Inches(t), Inches(sz), Inches(sz))
    c.fill.solid()
    c.fill.fore_color.rgb = fill_color
    c.line.fill.background()
    return c


def TITLE(slide, text, subtitle=None, cn=True):
    """Standard page title with blue underline"""
    TB(slide, 0.5, 0.35, 12.333, 0.6, text, 28, BLUE, True, cn=cn)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.05), Inches(2.5), Inches(0.025))
    line.fill.solid()
    line.fill.fore_color.rgb = BLUE
    line.line.fill.background()
    if subtitle:
        TB(slide, 0.5, 1.15, 9, 0.4, subtitle, 12, GRAY, cn=cn)


def DIVIDER(slide, num, text, cn=False):
    """Blue full-screen section divider"""
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = BLUE
    bg.line.fill.background()
    num_str = str(num) if num > 9 else '0' + str(num)
    TB(slide, 0.8, 2.3, 9, 1.2, num_str, 72, WHITE, True, cn=False)
    TB(slide, 0.8, 3.6, 9, 1, text, 32, WHITE, True, cn=cn)


def COVER(slide, title, presenters, date_str, en_title=None, journal=None, authors=None):
    """Build a cover slide when no template is provided.

    Args:
        slide: The slide object to build on
        title: Chinese paper title (string)
        presenters: name(s), e.g. "Zhang San" or "Zhang San, Li Si"
        date_str: Date string, e.g. "2026-06-20"
        en_title: English paper title (optional)
        journal: Journal name (optional)
        authors: Paper authors (optional)
    """
    # Top decorative bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()

    # Section label
    TB(slide, 0.8, 0.5, 4, 0.5, "文献汇报", 14, BLUE, True, PP_ALIGN.LEFT, cn=True)

    # Paper title (Chinese) - centered large
    TB(slide, 1.0, 1.6, 11.333, 1.6, title, 32, DARK, True, PP_ALIGN.CENTER, cn=True)

    # English title (if provided)
    if en_title:
        TB(slide, 1.0, 3.1, 11.333, 1.0, en_title, 16, GRAY, False, PP_ALIGN.CENTER, cn=False)

    # Separator line
    sep = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.167), Inches(3.9), Inches(5.0), Inches(0.02))
    sep.fill.solid()
    sep.fill.fore_color.rgb = BLUE
    sep.line.fill.background()

    y_start = 4.2

    # Authors line
    if authors:
        TB(slide, 1.0, y_start, 11.333, 0.5, f"作者：{authors}", 16, DARK, False, PP_ALIGN.CENTER, cn=True)
        y_start += 0.55

    # Journal line
    if journal:
        TB(slide, 1.0, y_start, 11.333, 0.5, f"来源：{journal}", 14, GRAY, False, PP_ALIGN.CENTER, cn=True)
        y_start += 0.55

    # 汇报人 line — always shown
    TB(slide, 1.0, y_start, 11.333, 0.5, f"汇报人：{presenters}", 18, DARK, False, PP_ALIGN.CENTER, cn=True)
    y_start += 0.6

    # 日期 line — always shown
    TB(slide, 1.0, y_start, 11.333, 0.5, f"日期：{date_str}", 16, GRAY, False, PP_ALIGN.CENTER, cn=True)

    # Bottom decorative bar
    bar2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.42), Inches(13.333), Inches(0.08))
    bar2.fill.solid()
    bar2.fill.fore_color.rgb = BLUE
    bar2.line.fill.background()


def new_presentation(original_pptx_path=None):
    """Create a new presentation.
    If original_pptx_path is given, preserve its cover (slide 0) and ending (slide -1).
    Returns (prs, LAYOUT).
    """
    if original_pptx_path:
        return _new_from_original(original_pptx_path)
    from pptx.util import Inches as _Inches
    prs = Presentation()
    prs.slide_width = _Inches(13.333)
    prs.slide_height = _Inches(7.5)
    return prs, prs.slide_layouts[6]


def _new_from_original(original_path):
    """Load original PPTX, keep only cover & ending, reopen for clean naming."""
    import os, tempfile
    prs = Presentation(original_path)

    # Remove all middle slides, keeping first and last
    while len(prs.slides) > 2:
        rId = prs.slides._sldIdLst[1].get(qn('r:id'))
        prs.part.drop_rel(rId)
        prs.slides._sldIdLst.remove(prs.slides._sldIdLst[1])

    # Save and reopen to reset internal naming counter
    tmp = os.path.join(tempfile.gettempdir(), '_workbuddy_academic_ppt_temp.pptx')
    prs.save(tmp)
    prs = Presentation(tmp)
    return prs, prs.slide_layouts[6]


def finalize_ending(prs):
    """Move the original ending slide (at index 1) to the very last position."""
    sld_lst = prs.slides._sldIdLst
    ending = sld_lst[1]   # original ending is now at index 1
    sld_lst.remove(ending)
    sld_lst.append(ending)
    return prs


def save(prs, output_path):
    """Save presentation to a specific path and print summary."""
    prs.save(output_path)
    print(f"Done! {len(prs.slides)} slides → {output_path}")


def save_to_desktop(prs, filename):
    """Save presentation to the user's Desktop (default output location).

    Args:
        prs: Presentation object
        filename: Output filename, e.g. "paper_report.pptx"
    Returns:
        str: Full path to the saved file on Desktop
    """
    import os
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    os.makedirs(desktop, exist_ok=True)
    output_path = os.path.join(desktop, filename)
    prs.save(output_path)
    print(f"Done! {len(prs.slides)} slides → {output_path} (Desktop)")
    return output_path
