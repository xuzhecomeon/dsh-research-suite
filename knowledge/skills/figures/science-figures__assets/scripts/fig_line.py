#!/usr/bin/env python3
"""Line chart generator with error bands and markers."""
import numpy as np


def gen_line(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate line chart with optional error bands."""
    labels = data.get("labels", [])
    series = data.get("series", {})
    error_data = data.get("errors", {})
    markers = ['o', 's', 'D', '^', 'v', 'p', '*', 'h', '+', 'x']

    # Determine x: use labels if numeric, otherwise use index
    numeric_labels = all(isinstance(l, (int, float)) or (isinstance(l, str) and l.replace('.', '', 1).replace('-', '', 1).isdigit())
                         for l in labels)
    if numeric_labels and labels:
        x = np.array([float(l) for l in labels])
    else:
        x = np.arange(len(labels)) if labels else np.arange(max(len(v) for v in series.values()))

    for i, (name, values) in enumerate(series.items()):
        c = colors[i % len(colors)]
        mk = markers[i % len(markers)]
        lw = kwargs.get("linewidth", 2)
        ax.plot(x[:len(values)], values, c=c, marker=mk, markersize=6,
                linewidth=lw, label=name, zorder=3)

        # Error band
        if name in error_data and error_data[name]:
            errs = error_data[name]
            if isinstance(errs, list) and len(errs) == len(values):
                lower = [v - e for v, e in zip(values, errs)]
                upper = [v + e for v, e in zip(values, errs)]
                ax.fill_between(x[:len(values)], lower, upper, color=c, alpha=0.15, zorder=2)

    if not numeric_labels and labels:
        ax.set_xticks(x)
        from fig_core import set_ticklabels
        set_ticklabels(ax, labels, 'x', cjk_fp)
