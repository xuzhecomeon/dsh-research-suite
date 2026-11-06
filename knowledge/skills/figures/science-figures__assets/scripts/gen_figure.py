#!/usr/bin/env python3
"""
science-figures: Publication-quality academic figure generator.
Powered by scienceplots + matplotlib.

Supports 15+ chart types with 8 journal styles, CJK auto-detection,
multi-panel subplots, and high-DPI output.

Usage:
  python gen_figure.py --type bar --data data.json --out figure.png --style nature
  python gen_figure.py --type heatmap --data data.csv --out figure.svg --style ieee
  python gen_figure.py --type surface --data data.json --out figure.png --style science
"""

# Fix Windows OpenBLAS threading conflict (must be set before numpy/matplotlib imports)
import os as _os
if _os.name == 'nt':  # Windows
    _os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
    _os.environ.setdefault('OMP_NUM_THREADS', '1')

import argparse, json, os, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import matplotlib.pyplot as plt

from data_loader import load_data
from style_manager import setup_style, list_styles
from fig_core import (
    load_cjk_font, needs_cjk, apply_base_style,
    set_axis_labels, set_title, finalize_and_save
)

# ── Import all generators ────────────────────────────────────────────────
from fig_bar import gen_bar
from fig_heatmap import gen_heatmap
from fig_scatter import gen_scatter
from fig_line import gen_line
from fig_box import gen_box, gen_violin
from fig_forest import gen_forest
from fig_distribution import gen_histogram, gen_density
from fig_pie import gen_pie
from fig_radar import gen_radar
from fig_3d import gen_surface, gen_contour, gen_scatter3d
from fig_subplots import gen_subplots

# ── Generator registry ────────────────────────────────────────────────────
GENERATORS = {
    "bar": gen_bar,
    "grouped_bar": gen_bar,
    "heatmap": gen_heatmap,
    "scatter": gen_scatter,
    "line": gen_line,
    "box": gen_box,
    "boxplot": gen_box,
    "violin": gen_violin,
    "forest": gen_forest,
    "histogram": gen_histogram,
    "density": gen_density,
    "pie": gen_pie,
    "donut": gen_pie,
    "radar": gen_radar,
    "surface": gen_surface,
    "contour": gen_contour,
    "scatter3d": gen_scatter3d,
}

# Chart types that need 3D axes
_3D_TYPES = {"surface", "scatter3d"}

# Chart types that need polar axes
_POLAR_TYPES = {"radar"}

# Chart types that need specific figure size
_SPECIAL_TYPES = {"subplots"}


def main():
    parser = argparse.ArgumentParser(
        description="science-figures: Publication-quality academic figure generator (scienceplots-based)"
    )
    parser.add_argument("--type", "-t", choices=sorted(list(GENERATORS.keys()) + ["subplots"]),
                        help="Figure type")
    parser.add_argument("--data", "-d", help="Input data file (JSON or CSV)")
    parser.add_argument("--out", "-o", help="Output file path (.png/.svg/.pdf)")
    parser.add_argument("--title", default="", help="Figure title (use \\n for newline)")
    parser.add_argument("--xlabel", default="", help="X-axis label")
    parser.add_argument("--ylabel", default="", help="Y-axis label")
    parser.add_argument("--style", "-s", default="nature", choices=list_styles(),
                        help="Journal style (from scienceplots)")
    parser.add_argument("--cjk", action="store_true", help="Force enable CJK font")
    parser.add_argument("--cjk-font", default=None, help="Specific CJK font path")
    parser.add_argument("--width", type=float, default=None, help="Figure width (inches)")
    parser.add_argument("--height", type=float, default=None, help="Figure height (inches)")
    parser.add_argument("--legend", action="store_true", default=True, help="Show legend")
    parser.add_argument("--no-legend", action="store_true", help="Hide legend")

    # Bar-specific
    parser.add_argument("--show-values", action="store_true", help="Show value labels on bars")

    # Scatter-specific
    parser.add_argument("--trend", action="store_true", default=True, help="Show trend line (scatter)")
    parser.add_argument("--no-trend", action="store_true", help="Hide trend line")

    # Heatmap-specific
    parser.add_argument("--cmap", default=None, help="Colormap for heatmap/contour/surface")
    parser.add_argument("--vmin", type=float, default=None, help="Heatmap vmin")
    parser.add_argument("--vmax", type=float, default=None, help="Heatmap vmax")
    parser.add_argument("--center", type=float, default=None, help="Center value for divergence colormaps")

    # Distribution-specific
    parser.add_argument("--kde", action="store_true", default=True, help="Show KDE overlay (histogram)")
    parser.add_argument("--no-kde", action="store_true", help="Hide KDE overlay")
    parser.add_argument("--bins", default="auto", help="Histogram bins (int or 'auto')")
    parser.add_argument("--density", action="store_true", help="Normalize histogram to density")

    # Pie-specific
    parser.add_argument("--donut", action="store_true", help="Draw as donut chart (when --type pie)")
    parser.add_argument("--show-pct", action="store_true", default=True, help="Show percentages on pie")
    parser.add_argument("--no-pct", action="store_true", help="Hide percentages")

    # 3D-specific
    parser.add_argument("--contour-floor", action="store_true", help="Show contour project floor (surface)")
    parser.add_argument("--filled", action="store_true", default=True, help="Filled contour (contour)")
    parser.add_argument("--no-filled", action="store_true", help="Line-only contour")

    # Subplots
    parser.add_argument("--layout", default="auto", help="Subplot layout: auto, RxC, or rows,cols (e.g. 2x3)")

    parser.add_argument("--dpi", type=int, default=300, help="Output DPI (default: 300)")
    parser.add_argument("--list-styles", action="store_true", help="List available styles and exit")

    args = parser.parse_args()

    if args.list_styles:
        print("Available styles: " + ", ".join(list_styles()))
        return

    # ── Style setup ──────────────────────────────────────────────────────
    custom_rc = {}
    if args.width:
        custom_rc["figure.figsize"] = (args.width, args.height or args.width * 0.65)
    elif args.height:
        custom_rc["figure.figsize"] = (args.height * 1.5, args.height)
    if args.dpi:
        custom_rc["savefig.dpi"] = args.dpi

    style_info = setup_style(args.style, custom_rc)
    colors = style_info["colors"]

    # ── Load data ─────────────────────────────────────────────────────────
    if args.type == "subplots":
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = load_data(args.data, chart_type=args.type)

    if args.type == "subplots":
        if not data or not isinstance(data, list):
            print("ERROR: Subplots data must be a non-empty JSON array.", file=sys.stderr)
            sys.exit(1)
    else:
        if not data or not isinstance(data, dict):
            print("ERROR: Data file is empty or invalid.", file=sys.stderr)
            sys.exit(1)

        has_data = any(data.get(k) for k in ["series", "matrix", "x", "y", "estimates", "values"])
        if not has_data:
            print("ERROR: No data fields found.", file=sys.stderr)
            sys.exit(1)

    # ── CJK font ──────────────────────────────────────────────────────────
    cjk_fp = None
    if args.cjk or args.cjk_font or needs_cjk(data, args.title, args.xlabel, args.ylabel):
        cjk_fp, cjk_name = load_cjk_font(args.cjk_font)
        if cjk_name:
            plt.rcParams['font.sans-serif'] = [cjk_name, 'DejaVu Sans'] + \
                                               plt.rcParams.get('font.sans-serif', [])
        plt.rcParams['axes.unicode_minus'] = False
        if cjk_fp:
            print(f"CJK font loaded: {cjk_name}", file=sys.stderr)
        else:
            print("WARNING: No CJK font found, CJK characters may not render", file=sys.stderr)

    # ── Create figure ─────────────────────────────────────────────────────
    kw_width = args.width if args.width else plt.rcParams.get("figure.figsize", (8, 5))[0]
    kw_height = args.height if args.height else plt.rcParams.get("figure.figsize", (8, 5))[1]

    # Special axes types
    if args.type in _3D_TYPES:
        fig = plt.figure(figsize=(kw_width, kw_height))
        ax = fig.add_subplot(111, projection='3d')
    elif args.type in _POLAR_TYPES:
        fig = plt.figure(figsize=(kw_width, kw_height))
        ax = fig.add_subplot(111, polar=True)
    elif args.type == "subplots":
        fig, ax = plt.subplots(figsize=(kw_width, kw_height))
        new_fig = gen_subplots(data, fig, ax, colors, cjk_fp,
                               layout=args.layout)
        if new_fig is not None:
            fig = new_fig
        # For subplots, save directly
        out_ext = os.path.splitext(args.out)[1].lower()
        save_kwargs = {"bbox_inches": "tight", "facecolor": "white", "edgecolor": "none"}
        if out_ext == ".svg":
            save_kwargs["format"] = "svg"
        elif out_ext == ".pdf":
            save_kwargs["format"] = "pdf"
        fig.savefig(args.out, **save_kwargs)
        plt.close(fig)
        sz = os.path.getsize(args.out)
        print(f"Saved: {args.out} ({sz:,} bytes)", file=sys.stderr)
        return
    else:
        fig, ax = plt.subplots(figsize=(kw_width, kw_height))

    # ── Generate ──────────────────────────────────────────────────────────
    gen_func = GENERATORS[args.type]
    # Parse bins: convert to int if numeric string, otherwise keep as "auto"
    bins_val = args.bins
    if isinstance(bins_val, str) and bins_val.isdigit():
        bins_val = int(bins_val)

    gen_kwargs = {
        "show_values": args.show_values,
        "trend": args.trend and not args.no_trend,
        "cmap": args.cmap,
        "vmin": args.vmin,
        "vmax": args.vmax,
        "center": args.center,
        "kde": args.kde and not args.no_kde,
        "bins": bins_val,
        "density": args.density,
        "show_pct": args.show_pct and not args.no_pct,
        "donut": args.donut,
        "contour_floor": args.contour_floor,
        "filled": args.filled and not args.no_filled,
    }
    extra = gen_func(data, ax, colors, cjk_fp, **gen_kwargs)

    # ── Style & labels ────────────────────────────────────────────────────
    if args.type not in _3D_TYPES and args.type not in _POLAR_TYPES:
        apply_base_style(ax)
    elif args.type in _3D_TYPES:
        # 3D axes: make panes transparent
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor('white')
        ax.yaxis.pane.set_edgecolor('white')
        ax.zaxis.pane.set_edgecolor('white')

    set_title(ax, args.title, cjk_fp)
    if args.type not in _3D_TYPES:
        set_axis_labels(ax, args.xlabel, args.ylabel, cjk_fp)
    else:
        if args.xlabel:
            ax.set_xlabel(args.xlabel)
        if args.ylabel:
            ax.set_ylabel(args.ylabel)

    # ── Finalize ──────────────────────────────────────────────────────────
    legend = args.legend and not args.no_legend
    finalize_and_save(fig, ax, args.out, legend=legend,
                      colorbar_artist=extra, cbar_label=None, cjk_fp=cjk_fp)


if __name__ == "__main__":
    main()
