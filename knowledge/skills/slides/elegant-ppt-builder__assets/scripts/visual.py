"""
Visual engine for elegant-ppt-builder.

Provides low-level primitives for generating gradient backgrounds,
decorative blobs, glows, and other complex visual elements using
Pillow. These are rasterized to PNG and inserted into the PPTX.

This module is intentionally framework-light so it can be reused
outside the main builder.
"""

from __future__ import annotations

import math
import os
import random
import sys
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# -----------------------------------------------------------------------------
# Font handling
# -----------------------------------------------------------------------------

def _font_candidates() -> List[str]:
    """Return likely font paths in priority order. Best-effort."""
    candidates = []
    if sys.platform == "darwin":
        candidates += [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Songti.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/Avenir Next.ttc",
            "/System/Library/Fonts/Avenir.ttc",
            "/System/Library/Fonts/Optima.ttc",
        ]
    elif sys.platform.startswith("win"):
        candidates += [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
    else:
        candidates += [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
    return [c for c in candidates if os.path.exists(c)]


def load_font(size: int = 24, prefer_chinese: bool = True) -> ImageFont.FreeTypeFont:
    """Load a font with Chinese support if available, falling back gracefully."""
    paths = _font_candidates()
    for path in paths:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()

# Slide canvas defaults (16:9, 10 inches x 5.625 inches at 96 dpi for PIL)
# We render at 2x for crisp output: 1920 x 1080.
CANVAS_W = 1920
CANVAS_H = 1080


# -----------------------------------------------------------------------------
# Color utilities
# -----------------------------------------------------------------------------

Color = Tuple[int, int, int]
ColorRGBA = Tuple[int, int, int, int]


def hex_to_rgb(value: str) -> Color:
    """Convert "#RRGGBB" or "RRGGBB" to (r, g, b)."""
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6:
        raise ValueError(f"Invalid color: {value!r}")
    return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))


def rgb_to_hex(rgb: Color) -> str:
    return "#%02X%02X%02X" % tuple(int(c) for c in rgb)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(c1: Color, c2: Color, t: float) -> Color:
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )


# -----------------------------------------------------------------------------
# Gradients
# -----------------------------------------------------------------------------

def _vertical_gradient(size: Tuple[int, int], top: Color, bottom: Color) -> Image.Image:
    w, h = size
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        c = lerp_color(top, bottom, t)
        for x in range(w):
            px[x, y] = c
    return img


def _diagonal_gradient(size: Tuple[int, int], c1: Color, c2: Color,
                        angle_deg: float = 135.0) -> Image.Image:
    """Angle: 0 = left to right, 90 = top to bottom."""
    w, h = size
    rad = math.radians(angle_deg)
    # project (x, y) onto a unit vector along the gradient direction
    dx, dy = math.cos(rad), math.sin(rad)
    # distance from corner 0 along the direction
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    dists = [x * dx + y * dy for x, y in corners]
    lo, hi = min(dists), max(dists)
    rng = max(1e-6, hi - lo)

    img = Image.new("RGB", (w, h), c1)
    px = img.load()
    for y in range(h):
        for x in range(w):
            d = x * dx + y * dy
            t = (d - lo) / rng
            # ease curve for smoother appearance
            t = t * t * (3 - 2 * t)
            px[x, y] = lerp_color(c1, c2, t)
    return img


def _radial_gradient(size: Tuple[int, int], center: Tuple[float, float],
                      inner: Color, outer: Color, radius: float) -> Image.Image:
    w, h = size
    cx, cy = center
    img = Image.new("RGB", (w, h), outer)
    px = img.load()
    r2 = radius * radius
    for y in range(h):
        dy = y - cy
        for x in range(w):
            dx = x - cx
            d2 = dx * dx + dy * dy
            t = min(1.0, math.sqrt(d2) / radius)
            t = t ** 1.4
            px[x, y] = lerp_color(inner, outer, t)
    return img


def gradient_image(colors: Sequence[str], angle: float = 135.0,
                    size: Tuple[int, int] = (CANVAS_W, CANVAS_H),
                    kind: str = "linear") -> Image.Image:
    """Generate a gradient image from 2+ hex colors.

    kind: 'linear' or 'radial' (radial uses the first color as center).
    """
    rgbs = [hex_to_rgb(c) for c in colors]
    if kind == "radial" and len(rgbs) >= 2:
        return _radial_gradient(
            size,
            (size[0] * 0.5, size[1] * 0.5),
            rgbs[0], rgbs[-1],
            max(size) * 0.9,
        )
    if len(rgbs) == 1:
        return Image.new("RGB", size, rgbs[0])
    if len(rgbs) == 2:
        return _diagonal_gradient(size, rgbs[0], rgbs[1], angle)
    # multi-stop: piecewise lerp
    w, h = size
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    dists = [x * dx + y * dy for x, y in corners]
    lo, hi = min(dists), max(dists)
    rng = max(1e-6, hi - lo)

    img = Image.new("RGB", (w, h), rgbs[0])
    px = img.load()
    n = len(rgbs) - 1
    for y in range(h):
        for x in range(w):
            d = x * dx + y * dy
            t = (d - lo) / rng
            t = max(0.0, min(0.999999, t))
            seg = int(t * n)
            local = (t * n) - seg
            px[x, y] = lerp_color(rgbs[seg], rgbs[seg + 1], local)
    return img


# -----------------------------------------------------------------------------
# Decorative elements
# -----------------------------------------------------------------------------

def soft_blob(size: Tuple[int, int], color: ColorRGBA,
               radius_factor: float = 0.6,
               softness: float = 0.4,
               cx: float = 0.5, cy: float = 0.5) -> Image.Image:
    """Render a soft fuzzy circle (for glow/blob effects)."""
    w, h = size
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    r = int(min(w, h) * radius_factor)
    x0 = int(w * cx - r)
    y0 = int(h * cy - r)
    x1 = int(w * cx + r)
    y1 = int(h * cy + r)
    d.ellipse((x0, y0, x1, y1), fill=color)
    base = base.filter(ImageFilter.GaussianBlur(radius=r * softness))
    return base


def soft_blobs(size: Tuple[int, int], blobs: Sequence[dict]) -> Image.Image:
    """Composite multiple soft blobs. Each blob dict can have:
        color: '#RRGGBB' or (r,g,b) or (r,g,b,a)
        alpha: 0-255 (used if color is rgb only)
        radius_factor, softness, cx, cy (0-1)
    """
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    for b in blobs:
        c = b["color"]
        if isinstance(c, str):
            rgb = hex_to_rgb(c)
            a = int(b.get("alpha", 200))
            color = (rgb[0], rgb[1], rgb[2], a)
        elif len(c) == 3:
            color = (c[0], c[1], c[2], int(b.get("alpha", 200)))
        else:
            color = c
        blob = soft_blob(
            size, color,
            radius_factor=b.get("radius_factor", 0.6),
            softness=b.get("softness", 0.4),
            cx=b.get("cx", 0.5),
            cy=b.get("cy", 0.5),
        )
        canvas.alpha_composite(blob)
    return canvas


def grid_lines(size: Tuple[int, int], color: ColorRGBA = (255, 255, 255, 24),
                step: int = 80, line_width: int = 1) -> Image.Image:
    """A faint grid pattern. Useful for tech/data themes."""
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x in range(0, w, step):
        d.line((x, 0, x, h), fill=color, width=line_width)
    for y in range(0, h, step):
        d.line((0, y, w, y), fill=color, width=line_width)
    return img


def dot_pattern(size: Tuple[int, int], color: ColorRGBA = (255, 255, 255, 40),
                 step: int = 60, radius: int = 2) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(0, h, step):
        for x in range(0, w, step):
            d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    return img


def noise_texture(size: Tuple[int, int], intensity: int = 6) -> Image.Image:
    """A subtle noise overlay to break up flat gradients."""
    w, h = size
    img = Image.new("L", (w, h), 128)
    px = img.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = 128 + random.randint(-intensity, intensity)
    return img.convert("RGBA")


def rounded_rect_shadow(size: Tuple[int, int], rect: Tuple[int, int, int, int],
                         radius: int = 24, shadow_offset: int = 8,
                         shadow_blur: int = 24, alpha: int = 90) -> Image.Image:
    """Returns an RGBA image with a soft drop shadow under the rect."""
    w, h = size
    base = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    x0, y0, x1, y1 = rect
    sx0, sy0, sx1, sy1 = x0, y0 + shadow_offset, x1, y1 + shadow_offset
    d.rounded_rectangle((sx0, sy0, sx1, sy1), radius=radius, fill=(0, 0, 0, alpha))
    base = base.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
    return base


# -----------------------------------------------------------------------------
# Composite helpers
# -----------------------------------------------------------------------------

@dataclass
class BackgroundSpec:
    """Specification for a slide background.

    layers is rendered bottom-to-top, each entry being a PIL Image in the
    slide canvas size.
    """
    base: Image.Image
    layers: List[Image.Image]

    def composite(self) -> Image.Image:
        canvas = self.base.convert("RGBA").copy()
        for layer in self.layers:
            if layer.mode != "RGBA":
                layer = layer.convert("RGBA")
            canvas.alpha_composite(layer)
        return canvas


def make_background(theme: dict, kind: str = "content",
                     size: Tuple[int, int] = (CANVAS_W, CANVAS_H),
                     variant: int = 0) -> Image.Image:
    """Build a background image for a given theme + page kind.

    kind: 'cover', 'section', 'content', 'closing', 'quote'
    """
    bg = theme["backgrounds"][kind]
    base_color = hex_to_rgb(bg["base"])
    base = Image.new("RGB", size, base_color)

    # Build gradient overlay
    angle = bg.get("angle", 135)
    grad_colors = bg.get("gradient", [bg["base"], bg["base"]])
    if len(grad_colors) >= 2:
        grad = gradient_image(grad_colors, angle=angle, size=size, kind="linear")
        base = grad

    canvas = base.convert("RGBA")

    # Add decorative blobs
    for blob in bg.get("blobs", []):
        cfg = dict(blob)
        # Vary blob position slightly by variant for visual rhythm
        if "cx_variants" in cfg:
            cfg["cx"] = cfg["cx_variants"][variant % len(cfg["cx_variants"])]
        if "cy_variants" in cfg:
            cfg["cy"] = cfg["cy_variants"][variant % len(cfg["cy_variants"])]
        cfg.pop("cx_variants", None)
        cfg.pop("cy_variants", None)
        b = soft_blobs(size, [cfg])
        canvas.alpha_composite(b)

    # Optional grid / dots
    if bg.get("grid"):
        canvas.alpha_composite(grid_lines(size, color=(255, 255, 255, 18)))
    if bg.get("dots"):
        canvas.alpha_composite(dot_pattern(size, color=(255, 255, 255, 30)))

    return canvas.convert("RGB")


def save_temp_png(img: Image.Image, cache_dir: str, name: str) -> str:
    """Save a PIL image to cache_dir/name.png and return the path."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"{name}.png")
    img.save(path, "PNG", optimize=True)
    return path


# -----------------------------------------------------------------------------
# Number / progress visuals
# -----------------------------------------------------------------------------

def ring_progress(size: int, value: float, color: Color, bg_color: Color,
                   thickness: int = 10, max_value: float = 100.0) -> Image.Image:
    """Render a circular progress ring (0-1 value)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.arc((thickness, thickness, size - thickness, size - thickness),
          start=0, end=360, fill=bg_color, width=thickness)
    end = -90 + 360 * (value / max_value)
    d.arc((thickness, thickness, size - thickness, size - thickness),
          start=-90, end=end, fill=color, width=thickness)
    return img
