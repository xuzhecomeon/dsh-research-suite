# 过滤 + 生成每篇论文的缩略图网格（contact sheet）
import os, json, cv2, numpy as np

OUT = r"C:/Users/zy/WorkBuddy/2026-09-27-08-36-54/paper-figures"
manifest = json.load(open(os.path.join(OUT, "manifest.json"), encoding="utf-8"))

filtered = []
for m in manifest:
    tag = m["tag"]
    imgs = m["images"]
    # 去重（按 w x h 组合计数，tile 阵列只留第一张）+ 尺寸过滤
    seen = set()
    keep = []
    for im in sorted(imgs, key=lambda x: -(x["w"] * x["h"])):
        key = (im["w"], im["h"])
        if key in seen:
            continue
        seen.add(key)
        if im["w"] >= 480 and im["h"] >= 320:
            keep.append(im)
    keep = keep[:12]     # 每篇最多 12 张候选
    if keep:
        # 生成网格
        cols = 3
        rows = (len(keep) + cols - 1) // cols
        cw, ch = 460, 380
        sheet = np.full((rows * ch + 20, cols * cw, 3), 245, np.uint8)
        for i, im in enumerate(keep):
            fp = os.path.join(OUT, tag, im["file"])
            img = cv2.imread(fp)
            if img is None:
                continue
            h, w = img.shape[:2]
            scale = min((cw - 16) / w, (ch - 50) / h)
            rs = cv2.resize(img, (max(1, int(w * scale)), max(1, int(h * scale))))
            r, c = i // cols, i % cols
            y0, x0 = r * ch + 34, c * cw + 8
            sheet[y0:y0 + rs.shape[0], x0:x0 + rs.shape[1]] = rs
            cv2.putText(sheet, f"#{i+1} p{im['page']} {im['w']}x{im['h']}", (x0, y0 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 180), 1, cv2.LINE_AA)
        cv2.imwrite(os.path.join(OUT, f"sheet_{tag}.png"), sheet)
        filtered.append({"tag": tag, "paper": m["paper"], "candidates": keep})

json.dump(filtered, open(os.path.join(OUT, "filtered.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("网格生成完成：")
for f in filtered:
    print(f"  {f['tag']}: {len(f['candidates'])} 张候选 | {f['paper'][:50]}")
