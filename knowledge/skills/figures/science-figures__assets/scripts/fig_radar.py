#!/usr/bin/env python3
"""Radar chart (spider/radar plot) generator."""
import numpy as np


def gen_radar(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate radar/spider chart."""
    labels = data.get("labels", [])
    series = data.get("series", {})

    if not labels or not series:
        return

    n_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, n_vars, endpoint=False).tolist()
    angles += angles[:1]  # close the loop

    # Convert to polar
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    for i, (name, values) in enumerate(series.items()):
        vals = list(values) + [values[0]]  # close the loop
        c = colors[i % len(colors)]
        ax.fill(angles, vals, alpha=0.15, color=c)
        ax.plot(angles, vals, 'o-', linewidth=1.5, color=c, label=name, markersize=4)
        ax.fill(angles, vals, alpha=0.05, color=c)

    ax.set_xticks(angles[:-1])
    from fig_core import set_ticklabels
    set_ticklabels(ax, labels, 'x', cjk_fp)
    ax.set_ylim(bottom=0)
