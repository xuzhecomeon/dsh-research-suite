#!/usr/bin/env python3
"""Forest plot generator for meta-analysis."""
import numpy as np


def gen_forest(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate forest plot (meta-analysis style)."""
    labels = data.get("labels", data.get("studies", []))
    estimates = data.get("estimates", [])
    ci_low = data.get("ci_low", [])
    ci_high = data.get("ci_high", [])
    overall = data.get("overall", None)
    ref_line = data.get("ref_line", 0)

    y_pos = list(range(len(labels)))

    # Draw CI lines and point estimates
    for i, (est, lo, hi) in enumerate(zip(estimates, ci_low, ci_high)):
        ax.plot([lo, hi], [i, i], '-', color=colors[0], linewidth=1.5, zorder=2)
        ax.scatter(est, i, c=colors[0], s=80, zorder=3, edgecolors='black', linewidth=0.5)

    # Reference line
    ax.axvline(x=ref_line, color='gray', linestyle='--', linewidth=1, alpha=0.6)

    # Overall diamond
    if overall:
        oy = len(labels)
        est_o, lo_o, hi_o = overall["estimate"], overall["ci_low"], overall["ci_high"]
        diamond_x = [lo_o, est_o, hi_o, est_o, lo_o]
        diamond_y = [oy, oy - 0.2, oy, oy + 0.2, oy]
        ax.fill(diamond_x, diamond_y, color=colors[1] if len(colors) > 1 else colors[0],
                alpha=0.7, zorder=4)

    # Set y-axis labels (study names)
    ax.set_yticks(list(y_pos) + ([len(labels)] if overall else []))
    all_labels = list(labels) + (["Overall"] if overall else [])
    from fig_core import set_ticklabels
    set_ticklabels(ax, all_labels, 'y', cjk_fp)
    ax.invert_yaxis()

    # Place value annotations in a fixed relative position (avoid tight_layout explosion)
    x_min, x_max = ax.get_xlim()
    x_range = x_max - x_min
    text_x = x_max + x_range * 0.05
    for i, (est, lo, hi) in enumerate(zip(estimates, ci_low, ci_high)):
        ax.text(text_x, i, f'{est:.2f} [{lo:.2f}, {hi:.2f}]',
                va='center', fontsize=8, clip_on=False)
    if overall:
        ax.text(text_x, oy, f'Overall: {est_o:.2f} [{lo_o:.2f}, {hi_o:.2f}]',
                va='center', fontsize=9, fontweight='bold', clip_on=False)
