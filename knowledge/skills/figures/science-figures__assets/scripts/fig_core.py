#!/usr/bin/env python3
"""Core engine: unified figure creation, style application, and saving."""
import os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from style_manager import setup_style, list_styles
from font_detector import detect_cjk_font


def has_cjk(text):
    """Check if text contains CJK characters."""
    if not text:
        return False
    return any('\u4e00' <= ch <= '\u9fff' or '\u3400' <= ch <= '\u4dbf' for ch in str(text))


def load_cjk_font(font_path=None):
    """Load CJK font. Returns (FontProperties, font_name) or (None, None)."""
    if font_path:
        if os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
            fp = fm.FontProperties(fname=font_path)
            return fp, fp.get_name()
    else:
        detected = detect_cjk_font()
        if detected and os.path.exists(detected):
            fm.fontManager.addfont(detected)
            fp = fm.FontProperties(fname=detected)
            return fp, fp.get_name()
    return None, None


def needs_cjk(data, title="", xlabel="", ylabel=""):
    """Auto-detect if any display text contains CJK characters."""
    for t in [title, xlabel, ylabel]:
        if t and has_cjk(t):
            return True
    if not isinstance(data, dict):
        # Could be list (subplots) — scan dict items inside
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and needs_cjk(item):
                    return True
        return False
    for field in ["labels", "row_labels", "col_labels"]:
        for v in data.get(field, []) or []:
            if isinstance(v, str) and has_cjk(v):
                return True
    series = data.get("series", {})
    if isinstance(series, dict):
        for k in series.keys():
            if isinstance(k, str) and has_cjk(k):
                return True
    for v in (data.get("groups") or []):
        if isinstance(v, str) and has_cjk(v):
            return True
    return False


def apply_base_style(ax, grid=True):
    """Apply common styling to axes."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid:
        ax.yaxis.grid(True, alpha=0.3, linestyle='--')


def set_axis_labels(ax, xlabel, ylabel, cjk_fp=None):
    """Set axis labels with optional CJK font."""
    if xlabel:
        ax.set_xlabel(xlabel, fontproperties=cjk_fp if cjk_fp and has_cjk(xlabel) else None)
    if ylabel:
        ax.set_ylabel(ylabel, fontproperties=cjk_fp if cjk_fp and has_cjk(ylabel) else None)


def set_title(ax, title, cjk_fp=None):
    """Set figure title with optional CJK font."""
    if title:
        title_text = title.replace('\\n', '\n')
        ax.set_title(title_text, fontweight='bold', pad=12,
                     fontproperties=cjk_fp if cjk_fp and has_cjk(title_text) else None)


def set_ticklabels(ax, labels, axis='x', cjk_fp=None, rotation=0):
    """Set tick labels with optional CJK font and rotation."""
    use_cjk = cjk_fp and any(has_cjk(str(l)) for l in labels)
    if axis == 'x':
        ax.set_xticklabels(labels, fontproperties=cjk_fp if use_cjk else None, rotation=rotation)
    else:
        ax.set_yticklabels(labels, fontproperties=cjk_fp if use_cjk else None)


def finalize_and_save(fig, ax, out_path, legend=True, colorbar_artist=None, cbar_label=None,
                      cjk_fp=None, tight=True):
    """Finalize figure: legend, colorbar, layout, save."""
    if legend and ax.get_legend_handles_labels()[1]:
        ax.legend(loc='best', framealpha=0.9, prop=cjk_fp if cjk_fp else None)

    if colorbar_artist is not None and hasattr(colorbar_artist, 'get_cmap'):
        cbar = fig.colorbar(colorbar_artist, ax=ax, shrink=0.8)
        if cbar_label:
            cbar.set_label(cbar_label)

    if tight:
        try:
            plt.tight_layout()
        except Exception:
            # scienceplots may produce very large bboxes in edge cases (e.g. forest),
            # or MemoryError if elements fall outside axes bounds
            plt.subplots_adjust(left=0.15, right=0.85)

    out_ext = os.path.splitext(out_path)[1].lower()
    save_kwargs = {"bbox_inches": "tight", "facecolor": "white", "edgecolor": "none"}
    if out_ext == ".svg":
        save_kwargs["format"] = "svg"
    elif out_ext == ".pdf":
        save_kwargs["format"] = "pdf"

    fig.savefig(out_path, **save_kwargs)
    plt.close(fig)

    sz = os.path.getsize(out_path)
    print(f"Saved: {out_path} ({sz:,} bytes)", file=sys.stderr)
