# 批量提取 19 篇论文的所有嵌入图片 + 生成缩略图网格
import os, json, pymupdf

SRC_DIR = r"C:/Users/zy/Desktop/急诊、重症课题/论文训练库"
OUT = r"C:/Users/zy/WorkBuddy/2026-09-27-08-36-54/paper-figures"

papers = [
    "s41467-026-69658-9.pdf",
    "Solar-powered circular desalination agriculture enabled by amyloid fibril-based bioevaporators.pdf",
    "Solar-driven biosynthesis of chemicals from phosphite-rich wastewater and carbon dioxide.pdf",
    "Hydroxyl radicals dominate reoxidation of oxide-derived Cu in electrochemical CO2 reduction.pdf",
    "Constructing flexible sub-nanometer ferroelectric catalyst to overcome heterocatalytic kinetic barriers for enhanced catalytic and immuno-therapy.pdf",
    "Einkorn genomics sheds light on history of the oldest domesticated wheat.pdf",
    "Adaptive immunity at the crossroads of autophagy and metabolism.pdf",
    "Chiral coordination polymer nanowires boost radiation-induced in situ tumor vaccination.pdf",
    "Aptamers-based wearable electrochemical sensors for continuous monitoring of biomarkers in vivo.pdf",
    "Biradical-mediated synergistic electrocatalysis using metal-free redox molecular catalysts.pdf",
    "In situ-generated vaccine-like pyroptosome for personalized cancer immunotherapy.pdf",
    "polyBERT a chemical language model to enable fully machine-driven ultrafast polymer informatics.pdf",
    "Scale-up of complex molecular reaction system by hybrid mechanistic modeling and deep transfer learning.pdf",
    "Predicting small molecule–RNA interactions without RNA tertiary structures.pdf",
    "s41467-026-68636-5.pdf",
    "s41467-026-69382-4.pdf",
    "s41467-025-60570-2.pdf",
    "s41467-025-66495-0.pdf",
    "s41378-025-00993-5.pdf",
]

manifest = []
for idx, name in enumerate(papers, 1):
    path = os.path.join(SRC_DIR, name)
    if not os.path.exists(path):
        print(f"[{idx}] MISSING: {name}")
        continue
    tag = f"P{idx:02d}"
    pdir = os.path.join(OUT, tag)
    os.makedirs(pdir, exist_ok=True)
    try:
        doc = pymupdf.open(path)
        npages = len(doc)
        imgs = []
        for pno in range(npages):
            page = doc[pno]
            for im in page.get_images(full=True):
                xref = im[0]
                try:
                    info = doc.extract_image(xref)
                except Exception:
                    continue
                w, h = info["width"], info["height"]
                if w < 260 or h < 200:      # 过滤图标/小碎图
                    continue
                fn = f"{tag}_p{pno+1:02d}_x{xref}_{w}x{h}.{info['ext']}"
                fp = os.path.join(pdir, fn)
                if not os.path.exists(fp):
                    with open(fp, "wb") as f:
                        f.write(info["image"])
                imgs.append({"file": fn, "page": pno + 1, "w": w, "h": h,
                             "kb": len(info["image"]) // 1024})
        manifest.append({"tag": tag, "paper": name, "pages": npages, "images": imgs})
        print(f"[{tag}] {name[:60]} | {npages}p | {len(imgs)} imgs")
        doc.close()
    except Exception as e:
        print(f"[{tag}] ERROR: {e}")

with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)
tot = sum(len(m["images"]) for m in manifest)
print(f"\n总计: {len(manifest)} 篇 | {tot} 张候选图")
