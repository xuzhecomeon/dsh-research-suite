#!/usr/bin/env python3
"""Box plot and violin plot generator."""
import numpy as np


def gen_box(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate box plot with jitter points."""
    labels = data.get("labels", [])
    series = data.get("series", {})

    positions = list(range(len(series)))
    bp = ax.boxplot(list(series.values()), positions=positions, widths=0.5,
                    patch_artist=True, showfliers=True, flierprops={'marker': 'o', 'alpha': 0.5})

    for i, (patch, name) in enumerate(zip(bp['boxes'], series.keys())):
        patch.set_facecolor(colors[i % len(colors)])
        patch.set_alpha(0.6)

    # Jitter points
    rng = np.random.default_rng(42)
    for i, (name, values) in enumerate(series.items()):
        vals = np.array(values, dtype=float)
        jitter_x = positions[i] + rng.normal(0, 0.06, len(vals))
        ax.scatter(jitter_x, vals, s=18, c=colors[i % len(colors)], alpha=0.5,
                   zorder=3, edgecolors='none')

    ax.set_xticks(positions)
    box_labels = labels if labels and len(labels) == len(series) else list(series.keys())
    from fig_core import set_ticklabels
    set_ticklabels(ax, box_labels, 'x', cjk_fp)


def gen_violin(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate violin plot with inner box."""
    labels = data.get("labels", [])
    series = data.get("series", {})

    positions = list(range(len(series)))
    values_list = list(series.values())

    vp = ax.violinplot(values_list, positions=positions, widths=0.6,
                       showmeans=kwargs.get("show_means", True),
                       showmedians=kwargs.get("show_medians", True),
                       showextrema=kwargs.get("show_extrema", True))

    for i, body in enumerate(vp['bodies']):
        body.set_facecolor(colors[i % len(colors)])
        body.set_alpha(0.6)
        body.set_edgecolor(colors[i % len(colors)])
        body.set_linewidth(1)

    for part in ['cmeans', 'cmedians', 'cmins', 'cmaxes', 'cbars']:
        if part in vp:
            vp[part].set_color('#333333')
            vp[part].set_linewidth(1)

    ax.set_xticks(positions)
    violin_labels = labels if labels and len(labels) == len(series) else list(series.keys())
    from fig_core import set_ticklabels
    set_ticklabels(ax, violin_labels, 'x', cjk_fp)
