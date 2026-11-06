#!/usr/bin/env python3
"""3D chart generator: surface, contour, 3D scatter, wireframe."""
import numpy as np
import matplotlib.pyplot as plt


def gen_surface(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate 3D surface plot."""
    matrix = data.get("matrix")
    x = data.get("x")
    y = data.get("y")

    if matrix is not None:
        matrix = np.array(matrix, dtype=float)
        if x is not None and y is not None:
            X, Y = np.meshgrid(np.array(x, dtype=float), np.array(y, dtype=float))
        else:
            X, Y = np.meshgrid(range(matrix.shape[1]), range(matrix.shape[0]))
        Z = matrix
    elif data.get("z") is not None and data.get("x") is not None and data.get("y") is not None:
        X = np.array(data["x"], dtype=float)
        Y = np.array(data["y"], dtype=float)
        Z = np.array(data["z"], dtype=float)
        if X.ndim == 1:
            X, Y = np.meshgrid(np.unique(X), np.unique(Y))
            Z = Z.reshape(X.shape) if len(Z) == X.size else Z
    else:
        # 3D scatter fallback — x, y, z vectors
        return gen_scatter3d(data, ax, colors, cjk_fp, **kwargs)

    cmap = kwargs.get("cmap", "viridis")
    surf = ax.plot_surface(X, Y, Z, cmap=cmap, alpha=0.9, linewidth=0, antialiased=True,
                           edgecolor='none')

    # Contour projection on the floor
    if kwargs.get("contour_floor", False):
        ax.contour(X, Y, Z, zdir='z', offset=Z.min(), cmap=cmap, alpha=0.5, linewidths=0.5)

    return surf


def gen_contour(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate 2D contour plot."""
    matrix = data.get("matrix")
    if matrix is None:
        return None
    matrix = np.array(matrix, dtype=float)

    x = data.get("x")
    y = data.get("y")
    if x is not None and y is not None:
        X, Y = np.meshgrid(np.array(x, dtype=float), np.array(y, dtype=float))
    else:
        X, Y = np.meshgrid(range(matrix.shape[1]), range(matrix.shape[0]))

    cmap = kwargs.get("cmap", "viridis")
    levels = kwargs.get("contour_levels", 10)
    filled = kwargs.get("filled", True)

    if filled:
        cf = ax.contourf(X, Y, matrix, levels=levels, cmap=cmap, alpha=0.9)
        ax.contour(X, Y, matrix, levels=levels, colors='black', linewidths=0.3, alpha=0.4)
    else:
        cf = ax.contour(X, Y, matrix, levels=levels, cmap=cmap, linewidths=1.2)

    ax.clabel(cf, inline=True, fontsize=8)
    ax.set_aspect('equal')
    return cf


def gen_scatter3d(data, ax, colors, cjk_fp=None, **kwargs):
    """Generate 3D scatter plot."""
    x = np.array(data.get("x", []), dtype=float)
    y = np.array(data.get("y", []), dtype=float)
    z = np.array(data.get("z", []), dtype=float)
    groups = data.get("groups", None)

    if groups is None:
        ax.scatter(x, y, z, s=40, c=colors[0], alpha=0.7)
    else:
        unique_groups = sorted(set(groups), key=list(groups).index)
        for i, g in enumerate(unique_groups):
            mask = np.array([j for j in range(len(groups)) if groups[j] == g])
            ax.scatter(x[mask], y[mask], z[mask], s=40,
                       c=colors[i % len(colors)], alpha=0.7, label=g)
