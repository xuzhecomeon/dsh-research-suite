#!/usr/bin/env python3
"""Heatmap generator with annotations."""
import numpy as np
import matplotlib.pyplot as plt


def gen_heatmap(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate annotated heatmap."""
    matrix = data.get("matrix")
    if matrix is None:
        series = data.get("series", {})
        if series:
            matrix = np.array(list(series.values()))
        else:
            matrix = np.array([])

    matrix = np.array(matrix, dtype=float)
    row_labels = data.get("row_labels", data.get("labels", []))
    col_labels = data.get("col_labels", [])
    if not col_labels and "series" in data:
        col_labels = data.get("labels", list(data["series"].keys()))

    cmap = kwargs.get("cmap", "RdBu_r")
    vmin = kwargs.get("vmin", None)
    vmax = kwargs.get("vmax", None)
    annot_fmt = kwargs.get("annot_format", "{:+.1f}")
    center = kwargs.get("center", None)

    if vmin is None or vmax is None:
        abs_max = max(abs(matrix.min()), abs(matrix.max()))
        vmin = vmin if vmin is not None else -abs_max
        vmax = vmax if vmax is not None else abs_max

    im = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')

    # Text annotations
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix[i, j]
            clim = abs(vmin) + abs(vmax) if vmin is not None and vmax is not None else 2
            color = 'white' if abs(v) > clim / 2 * 0.7 else 'black'
            ax.text(j, i, annot_fmt.format(v), ha='center', va='center',
                    fontsize=9, fontweight='bold', color=color)

    ax.set_xticks(range(len(col_labels)))
    ax.set_yticks(range(len(row_labels)))
    from fig_core import set_ticklabels
    set_ticklabels(ax, col_labels, 'x', cjk_fp)
    set_ticklabels(ax, row_labels, 'y', cjk_fp)

    return im  # for colorbar
