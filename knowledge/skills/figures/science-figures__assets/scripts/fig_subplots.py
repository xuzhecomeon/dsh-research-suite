#!/usr/bin/env python3
"""Subplots / multi-panel figure generator."""
import os, sys
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from fig_core import apply_base_style, set_axis_labels, set_title, set_ticklabels
from fig_core import finalize_and_save, has_cjk


def gen_subplots(subplot_data, fig, axes, colors, cjk_fp=None, **kwargs):
    """
    Generate multi-panel subplot figure.

    subplot_data should be a list of dicts, each with:
      - "type": chart type
      - "data": data dict for that chart
      - "title" (optional): subplot title
      - "xlabel", "ylabel" (optional)
      - "position" (optional): (row, col) tuple, auto-layout if not provided
    """
    layout = kwargs.get("layout", "auto")  # "auto", (rows, cols), or "1x3"
    titles = kwargs.get("titles", [])
    sharex = kwargs.get("sharex", False)
    sharey = kwargs.get("sharey", False)

    if isinstance(subplot_data, list) and len(subplot_data) > 0:

        n = len(subplot_data)
        # Determine layout
        if isinstance(layout, tuple) and len(layout) == 2:
            rows, cols = layout
        elif layout == "auto":
            rows = int(n ** 0.5)
            cols = (n + rows - 1) // rows
        else:
            # Parse "RxC" format
            try:
                parts = layout.lower().replace("x", " ").split()
                rows, cols = int(parts[0]), int(parts[1])
            except Exception:
                rows, cols = 1, n

        fig2, axes2 = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
        if rows * cols == 1:
            axes_arr = [axes2]
        elif rows == 1 or cols == 1:
            axes_arr = list(axes2) if hasattr(axes2, '__iter__') else [axes2]
        else:
            axes_arr = [axes2[r, c] for r in range(rows) for c in range(cols)]

        # Import generators on demand
        from fig_bar import gen_bar
        from fig_heatmap import gen_heatmap
        from fig_scatter import gen_scatter
        from fig_line import gen_line
        from fig_box import gen_box, gen_violin
        from fig_forest import gen_forest
        from fig_distribution import gen_histogram, gen_density
        from fig_pie import gen_pie
        from fig_radar import gen_radar

        GEN_MAP = {
            "bar": gen_bar, "grouped_bar": gen_bar,
            "heatmap": gen_heatmap,
            "scatter": gen_scatter,
            "line": gen_line,
            "box": gen_box, "boxplot": gen_box,
            "violin": gen_violin,
            "forest": gen_forest,
            "histogram": gen_histogram, "density": gen_density,
            "pie": gen_pie, "donut": gen_pie,
            "radar": gen_radar,
        }

        for idx, item in enumerate(subplot_data):
            if idx >= len(axes_arr):
                break
            ax = axes_arr[idx]
            chart_type = item.get("type", "bar")
            chart_data = item.get("data", {})

            gen_func = GEN_MAP.get(chart_type)
            if gen_func:
                extra = gen_func(chart_data, ax, colors, cjk_fp)
            else:
                continue

            apply_base_style(ax)
            set_axis_labels(ax, item.get("xlabel", ""), item.get("ylabel", ""), cjk_fp)
            set_title(ax, item.get("title", ""), cjk_fp)

        # Hide unused axes
        for idx in range(n, len(axes_arr)):
            axes_arr[idx].set_visible(False)

        return fig2
    return None
