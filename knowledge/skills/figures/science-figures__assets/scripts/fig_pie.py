#!/usr/bin/env python3
"""Pie chart and donut chart generator."""
import numpy as np


def gen_pie(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate pie chart or donut chart."""
    labels = data.get("labels", [])
    values = data.get("values", [])

    if not values and data.get("series"):
        first_key = list(data["series"].keys())[0]
        values = data["series"][first_key]

    if not values:
        return

    donut = kwargs.get("donut", False)
    wedgeprops = {"width": 0.4, "edgecolor": "white", "linewidth": 1} if donut else \
                 {"edgecolor": "white", "linewidth": 1}

    show_pct = kwargs.get("show_pct", True)
    show_labels = kwargs.get("show_labels", True)
    pctdistance = 0.8 if donut else 0.6
    textprops = {"fontsize": 9}

    if cjk_fp:
        textprops["fontproperties"] = cjk_fp

    autopct = '%1.1f%%' if show_pct else None
    if autopct:
        wedges, texts, autotexts = ax.pie(
            values, labels=labels if show_labels else None,
            autopct=autopct, startangle=90,
            colors=colors[:len(values)],
            wedgeprops=wedgeprops,
            pctdistance=pctdistance,
            textprops=textprops
        )
        for t in autotexts:
            t.set_fontsize(8)
    else:
        wedges, texts = ax.pie(
            values, labels=labels if show_labels else None,
            startangle=90,
            colors=colors[:len(values)],
            wedgeprops=wedgeprops,
            textprops=textprops
        )[:2]

    # Equal aspect ratio
    ax.set_aspect('equal')
