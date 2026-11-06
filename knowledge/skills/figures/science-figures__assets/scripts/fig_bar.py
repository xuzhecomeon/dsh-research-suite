#!/usr/bin/env python3
"""Bar chart generator: grouped bar charts with error bars and significance markers."""
import numpy as np


def gen_bar(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate grouped bar chart."""
    labels = data.get("labels", [])
    series = data.get("series", {})
    error_data = data.get("errors", {})
    significance = data.get("significance", {})

    n_groups = len(labels)
    n_series = len(series)
    x = np.arange(n_groups)
    w = 0.8 / max(n_series, 1)

    for i, (name, values) in enumerate(series.items()):
        offset = (i - (n_series - 1) / 2) * w
        errs = error_data.get(name, None)
        if isinstance(errs, list):
            if len(errs) != len(values):
                errs = None
        elif isinstance(errs, (int, float)):
            errs = [errs] * len(values)

        bars = ax.bar(x + offset, values, w, yerr=errs,
                      color=colors[i % len(colors)], edgecolor='white', linewidth=0.5,
                      capsize=3, error_kw={'linewidth': 1}, label=name)

        if kwargs.get("show_values", False):
            for j, v in enumerate(values):
                err = errs[j] if errs and j < len(errs) else 0
                ax.text(x[j] + offset, v + err + np.nanmax(values) * 0.01,
                        f'{v:.1f}', ha='center', va='bottom', fontsize=7,
                        color=colors[i % len(colors)])

    # Significance brackets
    if significance:
        ylim = ax.get_ylim()
        for key, label in significance.items():
            parts = key.split(":")
            grp_idx = int(parts[0]) if len(parts) == 1 or not parts[1].isdigit() else int(parts[1])
            if grp_idx < n_groups:
                y_top = ylim[1] * 0.95
                fc = '#C0392B' if label not in ('NS', 'ns') else 'gray'
                fw = 'bold' if label not in ('NS', 'ns') else 'normal'
                ax.annotate(label, (x[grp_idx], y_top), ha='center', va='bottom',
                            fontsize=8, fontweight=fw, color=fc)

    ax.set_xticks(x)
    from fig_core import set_ticklabels
    set_ticklabels(ax, labels, 'x', cjk_fp)
