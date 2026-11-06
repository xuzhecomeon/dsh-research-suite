# live_text.py — 把 vtracer SVG 转换为「活字增强版」：剔除文字轮廓，插入可编辑 <text>
import re, json, sys, os
import cv2, numpy as np

def path_bbox(d, tx=0, ty=0):
    nums = [float(v) for v in re.findall(r'-?\d+\.?\d*', d)]
    if len(nums) < 4:
        return None
    xs = nums[0::2]; ys = nums[1::2]
    return (min(xs)+tx, min(ys)+ty, max(xs)+tx, max(ys)+ty)

def hex_of(bgr):
    b, g, r = int(bgr[0]), int(bgr[1]), int(bgr[2])
    return f"#{r:02X}{g:02X}{b:02X}"

def build(src_svg, ocr_json, src_img, out_svg, H_img=None):
    svg = open(src_svg, encoding="utf-8").read()
    ocr = json.load(open(ocr_json, encoding="utf-8"))
    img = cv2.imread(src_img)
    IH, IW = img.shape[:2]
    mwh = re.search(r'width="(\d+)" height="(\d+)"', svg)
    SW, SH = int(mwh.group(1)), int(mwh.group(2))
    scale = IW / SW if SW else 1.0

    # OCR bbox 映射到 SVG 坐标
    boxes = []
    for it in ocr:
        x1, y1, x2, y2 = it["x1"]/scale, it["y1"]/scale, it["x2"]/scale, it["y2"]/scale
        # 采样文字颜色（bbox 内最暗 10% 像素均值）
        yy1, yy2 = int(it["y1"]), int(it["y2"])
        xx1, xx2 = int(it["x1"]), int(it["x2"])
        roi = img[max(0,yy1):yy2, max(0,xx1):xx2]
        col = "#1A1A1A"
        if roi.size:
            g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).ravel()
            idx = np.argsort(g)[:max(1, len(g)//12)]
            mean_bgr = roi.reshape(-1, 3)[idx].mean(axis=0)
            col = hex_of(mean_bgr)
        boxes.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "text": it["text"], "col": col,
                      "h": y2 - y1, "w": x2 - x1})
    def in_any_box(bx1, by1, bx2, by2):
        cx, cy = (bx1+bx2)/2, (by1+by2)/2
        for b in boxes:
            pad = 4
            if b["x1"]-pad <= cx <= b["x2"]+pad and b["y1"]-pad <= cy <= b["y2"]+pad:
                bw, bh = bx2-bx1, by2-by1
                if bw <= b["w"]*1.7 + 12 and bh <= b["h"]*1.9 + 10:
                    return True
        return False

    pat = re.compile(r'<path d="([^"]*)" fill="([^"]*)" transform="translate\(([-\d.]+),([-\d.]+)\)"\s*/>')
    kept, removed = [], 0
    for m in pat.finditer(svg):
        d, fill, tx, ty = m.group(1), m.group(2), float(m.group(3)), float(m.group(4))
        bb = path_bbox(d, tx, ty)
        if bb and in_any_box(*bb):
            removed += 1
            continue
        kept.append(m.group(0))

    texts = []
    for b in boxes:
        size = max(7, round(b["h"] * 0.80))
        bold = b["h"] >= 19
        ybase = b["y2"] - b["h"] * 0.16
        fw = ' font-weight="bold"' if bold else ''
        t = (b["text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        texts.append(f'<text x="{b["x1"]:.0f}" y="{ybase:.0f}" font-family="Arial, Helvetica, sans-serif" '
                     f'font-size="{size}"{fw} fill="{b["col"]}">{t}</text>')

    body = "\n".join(kept)
    text_layer = "\n".join(texts)
    out = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           f'width="{SW}" height="{SH}" viewBox="0 0 {SW} {SH}">\n'
           '<g id="g01_graphics" inkscape:label="Graphics">\n' + body + '\n</g>\n'
           '<g id="g02_text" inkscape:label="Text (editable)">\n' + text_layer + '\n</g>\n</svg>\n')
    open(out_svg, "w", encoding="utf-8").write(out)
    return removed, len(texts), SW, SH

if __name__ == "__main__":
    removed, ntext, W, H = build(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(f"剔除文字轮廓: {removed} 条 | 活字文本: {ntext} 个 | 画布 {W}x{H}")
