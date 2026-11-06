#!/usr/bin/env python3
"""Distribution chart generator: histogram and density/KDE plots."""
import numpy as np
from scipy import stats


def gen_histogram(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate histogram with optional KDE overlay."""
    series = data.get("series", {})
    values = data.get("values", [])

    if not values and series:
        # Take first series
        values = list(series.values())[0] if series else []

    if not values:
        return

    values = np.array(values, dtype=float)
    bins = kwargs.get("bins", "auto")
    density = kwargs.get("density", False)
    alpha = kwargs.get("alpha", 0.7)

    ax.hist(values, bins=bins, density=density, alpha=alpha, color=colors[0],
            edgecolor='white', linewidth=0.5, label=data.get("name", ""))

    # KDE overlay
    if kwargs.get("kde", True) and len(values) >= 3:
        kde_x = np.linspace(values.min(), values.max(), 200)
        try:
            kde = stats.gaussian_kde(values)
            ax2 = ax.twinx()
            ax2.plot(kde_x, kde(kde_x), color=colors[1] if len(colors) > 1 else '#333333',
                     linewidth=2, alpha=0.8)
            ax2.set_ylabel('Density', fontsize=8)
            ax2.yaxis.label.set_color(colors[1] if len(colors) > 1 else '#333333')
        except Exception:
            pass


def gen_density(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate density/KDE plot for one or more series."""
    series = data.get("series", {})
    values_list = data.get("values", [])

    if values_list and not series:
        series = {"Data": values_list}

    for i, (name, values) in enumerate(series.items()):
        vals = np.array(values, dtype=float)
        xs = np.linspace(vals.min() - (vals.std() or 1), vals.max() + (vals.std() or 1), 200)
        try:
            kde = stats.gaussian_kde(vals)
            ax.plot(xs, kde(xs), color=colors[i % len(colors)], linewidth=2, label=name)
            ax.fill_between(xs, kde(xs), color=colors[i % len(colors)], alpha=0.15)
        except Exception:
            pass
