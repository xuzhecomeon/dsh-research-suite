# 流水线：vtracer 矢量化 + 文字区域检测 + 活字替换 + 语义分组
import os, re, sys, json, math
import cv2, numpy as np
import vtracer

def process(img_path, out_svg, texts=None, out_dir=None):
    """img_path: 原图; texts: [(x, y, content, size, color, bold, italic)] 活字列表(可选)"""
    base = os.path.splitext(os.path.basename(img_path))[0]
    tmp_svg = os.path.join(out_dir or os.path.dirname(img_path), base + "_vtracer.svg")
    vtracer.convert_image_to_svg_py(
        img_path, tmp_svg,
        colormode="color", hierarchical="stacked", mode="spline",
        filter_speckle=2, color_precision=8, layer_difference=8,
        corner_threshold=45, length_threshold=3.5, path_precision=6)
    svg = open(tmp_svg, encoding="utf-8").read()
    mwh = re.search(r'width="(\d+)" height="(\d+)"', svg)
    W, H = int(mwh.group(1)), int(mwh.group(2))
    return tmp_svg, svg, W, H

def detect_text_boxes(img_path, dark_thresh=120, min_area=40):
    """检测深色文字区域（合并同行笔画 → 行 bbox）"""
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = (gray < dark_thresh).astype(np.uint8) * 255
    # 水平膨胀合并同行的字
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
    dil = cv2.dilate(mask, k, iterations=2)
    cnts, _ = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if w * h < min_area or h < 9 or w < 12:
            continue
        # 密实度过滤（排除实心色块）
        roi = mask[y:y+h, x:x+w]
        density = roi.mean() / 255.0
        if density > 0.62:
            continue
        boxes.append({"x": x, "y": y, "w": w, "h": h, "density": round(density, 2)})
    boxes.sort(key=lambda b: (b["y"] // 12, b["x"]))
    return boxes, (img.shape[1], img.shape[0])

if __name__ == "__main__":
    img = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(img)
    tmp, svg, W, H = process(img, None, None, outdir)
    boxes, (IW, IH) = detect_text_boxes(img)
    json.dump({"boxes": boxes, "W": IW, "H": IH},
              open(os.path.join(outdir, "textboxes.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"尺寸: {IW}x{IH} | 文字区域: {len(boxes)} 个")
    for b in boxes[:60]:
        print(f"  ({b['x']:4d},{b['y']:4d}) {b['w']:4d}x{b['h']:3d} d={b['density']}")
