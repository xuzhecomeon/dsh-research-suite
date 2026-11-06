#!/usr/bin/env python3
"""
发表级多面板组图工具
将多张图表拼接为发表级多面板图 (Figure 1/2/3...)
用法: python compose_figure.py --images "a.png,b.png,c.png" --title "Figure 1" --output figure1.png
"""

import argparse
import json
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont


def _get_font(size: int = 14, bold: bool = True):
    candidates = []
    if sys.platform == "win32":
        candidates = ["arialbd.ttf", "arial.ttf", "segoeui.ttf", "calibri.ttf"]
    else:
        candidates = ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf", "LiberationSans-Bold.ttf", "LiberationSans.ttf"]

    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except (IOError, OSError):
            continue

    try:
        return ImageFont.load_default()
    except Exception:
        return None


def _auto_layout(n: int) -> tuple:
    if n <= 1:
        return 1, 1
    if n == 2:
        return 1, 2
    if n == 3:
        return 1, 3
    if n == 4:
        return 2, 2
    if n <= 6:
        return 2, 3
    cols = min(3, n)
    rows = math.ceil(n / cols)
    if rows * cols < n and rows == 2:
        rows = 3
    return rows, cols


def compose_figure(
    image_paths: list,
    output_path: str = "figure_combined.png",
    layout: str = None,
    labels: list = None,
    title: str = None,
    dpi: int = 300,
    font_size: int = 14,
    fmt: str = "png",
) -> str:
    n = len(image_paths)
    if n == 0:
        raise ValueError("至少需要一张图片")

    if layout:
        rows, cols = map(int, layout.split("x"))
    else:
        rows, cols = _auto_layout(n)

    if labels is None:
        labels = [chr(ord("A") + i) for i in range(n)]

    images = []
    for i, path in enumerate(image_paths):
        if not os.path.exists(path):
            raise FileNotFoundError(f"图片不存在: {path}")
        img = Image.open(path).convert("RGBA")
        images.append(img)
        print(f"  [{i + 1}/{n}] {os.path.basename(path)} ({img.size[0]}x{img.size[1]})", file=sys.stderr)

    min_w = min(img.size[0] for img in images)
    resized = []
    for img in images:
        if img.size[0] != min_w:
            ratio = min_w / img.size[0]
            new_h = int(img.size[1] * ratio)
            img = img.resize((min_w, new_h), Image.LANCZOS)
            print(f"  [resize] {img.size[0]}x{img.size[1]}", file=sys.stderr)
        resized.append(img)

    row_heights = []
    for r in range(rows):
        row_max_h = 0
        for c in range(cols):
            idx = r * cols + c
            if idx < n:
                row_max_h = max(row_max_h, resized[idx].size[1])
        row_heights.append(row_max_h)

    col_w = min_w

    label_font = _get_font(font_size, bold=True)
    title_font = _get_font(font_size + 4, bold=True) if title else None

    title_height = 0
    if title:
        temp_img = Image.new("RGBA", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), title, font=title_font)
        title_height = bbox[3] - bbox[1] + font_size

    canvas_w = cols * col_w
    canvas_h = sum(row_heights) + title_height
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (255, 255, 255, 255))

    if title and title_font:
        draw = ImageDraw.Draw(canvas)
        draw.text((font_size, font_size // 2), title, fill=(0, 0, 0), font=title_font)

    label_padding = 4
    for i, img in enumerate(resized):
        row = i // cols
        col = i % cols
        x = col * col_w
        y = sum(row_heights[:row]) + title_height

        paste_x = x + (col_w - img.size[0]) // 2
        paste_y = y + (row_heights[row] - img.size[1]) // 2

        canvas.paste(img, (paste_x, paste_y), img if img.mode == "RGBA" else None)

        draw = ImageDraw.Draw(canvas)
        label = labels[i] if i < len(labels) else ""
        if label:
            draw.text((x + label_padding, y + label_padding), label, fill=(0, 0, 0), font=label_font)

    if fmt.lower() == "pdf":
        canvas = canvas.convert("RGB")
        canvas.save(output_path, format="PDF", resolution=dpi)
    else:
        canvas = canvas.convert("RGB")
        canvas.save(output_path, format="PNG", dpi=(dpi, dpi))

    output_path = os.path.abspath(output_path)
    print(f"  [OK] 组图完成: {output_path} ({canvas_w}x{canvas_h})", file=sys.stderr)

    summary = {
        "output": output_path,
        "layout": f"{rows}x{cols}",
        "images": n,
        "uniform_width": min_w,
        "canvas": f"{canvas_w}x{canvas_h}",
        "labels": labels,
    }
    if title:
        summary["title"] = title
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    return output_path


def main():
    parser = argparse.ArgumentParser(description="发表级多面板组图工具")
    parser.add_argument("--images", required=True, help="图片路径，逗号分隔")
    parser.add_argument("--layout", default=None, help='行列布局，如 2x2 (默认自动推算)')
    parser.add_argument("--labels", default=None, help='面板标签，逗号分隔 (默认 A/B/C...)')
    parser.add_argument("--title", default=None, help="整体标题")
    parser.add_argument("--output", default="figure_combined.png", help="输出文件路径")
    parser.add_argument("--dpi", type=int, default=300, help="分辨率 (默认: 300)")
    parser.add_argument("--format", default="png", choices=["png", "pdf"], help="输出格式 (默认: png)")
    parser.add_argument("--font-size", type=int, default=14, help="标签字号 (默认: 14)")
    args = parser.parse_args()

    image_paths = [p.strip() for p in args.images.split(",") if p.strip()]
    labels = [l.strip() for l in args.labels.split(",")] if args.labels else None

    print(f"[compose] {len(image_paths)} 张图片 → {args.output}", file=sys.stderr)

    try:
        compose_figure(
            image_paths=image_paths,
            output_path=args.output,
            layout=args.layout,
            labels=labels,
            title=args.title,
            dpi=args.dpi,
            font_size=args.font_size,
            fmt=args.format,
        )
    except Exception as e:
        print(f"  [FAIL] 组图失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()