#!/usr/bin/env python3
"""Scatter plot generator with trend line and grouping."""
import numpy as np


def gen_scatter(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate scatter plot with optional trend line and grouping."""
    x_data = np.array(data.get("x", []), dtype=float)
    y_data = np.array(data.get("y", []), dtype=float)
    groups = data.get("groups", None)

    if groups is None:
        ax.scatter(x_data, y_data, s=60, color=colors[0],
                   edgecolors='white', linewidth=0.5, alpha=0.7, zorder=3)
    else:
        from collections import OrderedDict
        # Preserve insertion order of group labels
        seen = {}
        unique_groups = []
        for g in groups:
            if g not in seen:
                seen[g] = True
                unique_groups.append(g)

        for i, g in enumerate(unique_groups):
            mask = np.array([j for j in range(len(groups)) if groups[j] == g])
            c = colors[i % len(colors)]
            ax.scatter(x_data[mask], y_data[mask], s=60, c=c,
                       edgecolors='white', linewidth=0.5, alpha=0.7,
                       label=g, zorder=3)

    # Trend line
    if kwargs.get("trend", True) and len(x_data) >= 3:
        z = np.polyfit(x_data, y_data, 1)
        p = np.poly1d(z)
        x_line = np.linspace(x_data.min(), x_data.max(), 100)
        ax.plot(x_line, p(x_line), '--', color='gray', alpha=0.6, linewidth=1.2, zorder=2)
        r = np.corrcoef(x_data, y_data)[0, 1]
        ax.text(0.95, 0.05, f'r = {r:.3f}', transform=ax.transAxes,
                ha='right', va='bottom', fontsize=9, fontstyle='italic', color='gray',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8,
                          edgecolor='lightgray'))

    ax.xaxis.grid(True, alpha=0.3, linestyle='--')
