# P01 FLEXTAG — 插画级原创机制图（全英文）
import sys
sys.path.insert(0, r"C:/Users/zy/WorkBuddy/2026-09-27-08-36-54/paper-figures")
import svg_kit_pro as P
from svg_kit_pro import (put, emit, rgrad, lgrad, shadow, circ, ell, rrect, ln, path,
                         cell_pro, nucleus_pro, mitochondrion, protein_domains, receptor_pro,
                         dna_3d, nanoparticle, dish, microscope, pipette, vial, arrow,
                         curve_arrow, txt, frame, panel_title, smooth_blob)

W, H = 1600, 1000
NAVY, BLUE, TEAL, RED, PURPLE, GREEN, AMBER = "#1F4E79", "#2E75B6", "#1B8A7A", "#C0392B", "#7A5CA8", "#2E7D5B", "#D98C00"

# ===== 背景与标题 =====
put("00_BG", rrect(0, 0, W, H, 0, "#FBFDFF"))
put("00_BG", rrect(0, H-76, W, 76, 0, lgrad([("0", "#1F4E79", None), ("1", "#2E6CA5", None)])))
put("00_BG", txt(40, H-30, "FLEXTAG: Small, Self-Renewable Protein Tags for Anti-Fading Multi-Color Super-Resolution Imaging", 25, "#FFFFFF"))
put("00_BG", txt(40, H-56, "Three orthogonal 12\u201318 kDa exchangeable tags  \u00B7  protective-fixation protocol  \u00B7  one-for-all compatibility (SIM \u00B7 STED \u00B7 STORM \u00B7 PAINT)", 14, "#BFD7EE", bold=False))

# ===== Panel A: Challenges =====
put("10_A", frame(30, 560, 420, 336, "#FEF6F5", "#E5B0A8"))
put("10_A", panel_title(50, 866, "A | Limitations of existing tagging systems", RED, 19))
chal = [("Rapid photobleaching", "signal decays under prolonged laser illumination", "#D9534F"),
        ("Tag-induced artifacts", "large probes (\u2248150 kDa antibody, \u224833 kDa HaloTag)", "#C97B2E"),
        ("Low post-fixation labeling", "PFA/GA crosslinking blocks ligand accessibility", "#B85C8A"),
        ("Limited multiplexing", "no orthogonal tags across PLIM and SMLM", "#7A6CC4")]
for i, (t, sub, col) in enumerate(chal):
    y = 818 - i * 68
    put("10_A", rrect(48, y-30, 384, 58, 10, "#FFFFFF", col, 1.6))
    put("10_A", circ(76, y-1, 15, col, None, 0, 0.16))
    put("10_A", path(f"M{70},{y+5} L{82},{y-7} M{70},{y-7} L{82},{y+5}", stroke=col, sw=2.6))
    put("10_A", txt(102, y+9, t, 15, col))
    put("10_A", txt(102, y-11, sub, 11.5, "#8A7A76", bold=False))

# ===== Panel B: Design =====
put("20_B", frame(470, 560, 480, 336, "#F2F8FF", "#A8C8E8"))
put("20_B", panel_title(490, 866, "B | FLEXTAG design principle", BLUE, 19))
for i, (nm, col, kda) in enumerate([("FLEXTAG1", "#2E75B6", "12 kDa"), ("FLEXTAG2", "#7A5CA8", "15 kDa"), ("FLEXTAG3", "#1B8A7A", "18 kDa")]):
    cx = 540 + i * 130
    put("20_B", shadow(cx, 750, 40, 12, 0.12))
    put("20_B", circ(cx, 788, 38, rgrad([("0", "#FFFFFF", "0.9"), ("0.5", col, None), ("1", col, None)]), stroke=col, sw=2))
    put("20_B", ell(cx-14, 800, 12, 8, "#FFFFFF", op="0.5"))
    put("20_B", txt(cx-32, 722, nm, 13, col))
    put("20_B", txt(cx-22, 706, kda, 11, "#8A94A4", bold=False))
put("20_B", txt(490, 678, "Ligand = tag-binding moiety  +  PEG linker  +  nanoscopy dye", 15, "#3A4A5A"))
y0 = 632
put("20_B", f'<polygon points="502,{y0+13} 528,{y0+13} 515,{y0-11}" fill="#E8A33D" stroke="#B87A20" stroke-width="1.6"/>')
put("20_B", txt(492, y0+26, "moiety", 11, "#B87A20", bold=False))
for k in range(5):
    put("20_B", ln(534+k*12, y0, 541+k*12, y0, "#8A94A4", 3.4))
put("20_B", ell(604, y0, 5, 5, "#B0B8C4"))
put("20_B", txt(568, y0+26, "PEG linker", 11, "#8A94A4", bold=False))
put("20_B", f'<polygon points="656,{y0+10} 676,{y0-1} 656,{y0-12} 636,{y0-1}" fill="#D94A6A"/>')
put("20_B", circ(670, y0+9, 3.4, "#FFD9E2"))
put("20_B", txt(634, y0+26, "fluorophore", 11, "#D94A6A", bold=False))
put("20_B", txt(490, 588, "Dye choice is independent of tag recognition \u2192 flexible spectral palette", 13, BLUE, bold=False))

# ===== Panel C: Mechanism (illustration-grade cell) =====
put("30_C", frame(970, 560, 600, 336, "#F0FAF6", "#96CCB8"))
put("30_C", panel_title(990, 866, "C | Continuous ligand exchange \u2192 self-renewal", TEAL, 19))
put("30_C", cell_pro(1330, 706, 158, 88, "#CFE9DE", "#E8F6F0", nuc=True, organelles=True, name="c1"))
# 标签蛋白 + 配体交换
put("30_C", ln(1250, 676, 1250, 730, "#5A6A7A", 4))
put("30_C", f'<polygon points="1228,732 1272,732 1250,704" fill="#7A8A9A"/>')
put("30_C", txt(1180, 660, "genetically encoded tag", 11, "#6A7A8A", bold=False))
put("30_C", f'<polygon points="{1300},782 {1318},770 {1300},758 {1282},770" fill="#D94A6A"/>')
put("30_C", circ(1308, 766, 4, "#FFD9E2"))
put("30_C", txt(1248, 806, "bound fluorescent ligand", 11, "#C0392B", bold=False))
put("30_C", curve_arrow(1334, 784, 1440, 810, 40, 4, "#D94A6A", None, 13, 11))
put("30_C", txt(1330, 840, "photobleached dye dissociates", 11, "#C0392B", bold=False))
put("30_C", f'<polygon points="{1216},830 {1198},842 {1216},854 {1234},842" fill="#B9A0D0"/>')
put("30_C", curve_arrow(1194, 826, 1148, 790, -20, 4, TEAL, None, 12, 10))
put("30_C", txt(1146, 776, "fresh ligand binds", 11, TEAL, bold=False))
put("30_C", txt(1160, 616, "Tag stays anchored while fluorophores are continuously exchanged", 11.5, "#3A8A70", bold=False))
put("30_C", txt(1160, 600, "\u2192 anti-fading imaging over extended durations", 11.5, "#3A8A70", bold=False))


# ===== 路线 B：AI 生成的显微镜仪器插画（矢量化叠加）=====
try:
    _micro = open(r"C://Users//zy//WorkBuddy//2026-09-27-08-36-54//paper-figures//assets//microscope_group.svg", encoding="utf-8").read()
    _s = 0.148
    _iw, _ih = 1024, 1008
    _tx, _ty = 992, 792          # y 向上坐标系：图像左边界与底部
    put("35_C_Instrument", f'<ellipse cx="{_tx + _iw*_s/2:.0f}" cy="{_ty - _ih*_s/2:.0f}" rx="{_iw*_s*0.62:.0f}" ry="{_ih*_s*0.58:.0f}" fill="#DCEAF6" opacity="0.55"/>')
    put("35_C_Instrument", f'<g transform="translate({_tx},{_ty}) scale({_s},{-_s})">' + _micro + '</g>')
    put("35_C_Instrument", txt(998, 806, "super-resolution nanoscopy", 11, "#5A7A9A", bold=False))
    put("35_C_Instrument", txt(1004, 792, "SIM / STED / STORM / PAINT", 10, "#8AA0B4", bold=False))
except Exception as _e:
    print("microscope embed failed:", _e)

# ===== Panel D: Compatibility =====
put("40_D", frame(30, 300, 420, 240, "#F6F3FC", "#C0B0E0"))
put("30_C", "")  # 保持组序
put("40_D", panel_title(50, 518, "D | One-for-all compatibility", PURPLE, 19))
put("40_D", rrect(48, 424, 180, 76, 10, "#FFFFFF", "#A8C0E0", 1.6))
put("40_D", txt(60, 480, "PLIM", 15, BLUE))
put("40_D", txt(60, 458, "SIM \u00B7 STED", 13, "#4A5A6A", bold=False))
put("40_D", rrect(240, 424, 192, 76, 10, "#FFFFFF", "#96CCB8", 1.6))
put("40_D", txt(252, 480, "SMLM", 15, TEAL))
put("40_D", txt(252, 458, "STORM \u00B7 PAINT", 13, "#4A5A6A", bold=False))
for i, (nm, col, y) in enumerate([("Mitochondria\u2013FLEXTAG1", "#2E75B6", 392),
                                  ("Microtubule\u2013FLEXTAG2", "#7A5CA8", 362),
                                  ("ER\u2013FLEXTAG3", "#1B8A7A", 332)]):
    put("40_D", ell(62, y, 15, 8, col, stroke="#00000022", sw=1))
    put("40_D", txt(86, y+5, nm, 13, col))

# ===== Panel E: Protective fixation protocol =====
put("50_E", frame(470, 90, 1100, 450, "#FFFCF4", "#E0C898"))
put("50_E", panel_title(490, 516, "E | Protective-fixation protocol preserves ligand accessibility", "#B8860B", 19))
steps = [("1. Ligand protection", "+ Protective agent", "#E893B0"),
         ("2. Protective fixation", "PFA + GA + agent", "#8FB8E8"),
         ("3. Reduction", "+ NaBH4", "#E8C860"),
         ("4. Blocking", "BSA + Tween20 + KSCN", "#E893B0")]
for i, (t, sub, col) in enumerate(steps):
    x = 500 + i * 268
    put("50_E", rrect(x, 300, 244, 190, 12, "#FFFFFF", col, 2.2))
    put("50_E", txt(x+14, 470, t, 16, "#3A4A5A"))
    put("50_E", txt(x+14, 448, sub, 12, "#7A8A9A", bold=False))
    cells = [(k*0.26-0.52, 0.35, 0.10, col) for k in range(4)]
    put("50_E", dish(x+122, 356, 100, "#EAF4FB", cells, lid=True))
    if i < 3:
        put("50_E", arrow(x+250, 396, x+262, 396, 4.5, "#B0B8C4", None, 12, 10))
put("50_E", rrect(500, 112, 500, 164, 10, "#FEF6F7", "#E8B8C0", 1.6))
put("50_E", txt(516, 252, "Previous work: non-protective fixation", 14, RED))
put("50_E", cell_pro(586, 184, 58, 44, "#EFD5DA", "#F8ECEE", nuc=True, organelles=False, name="pc"))
put("50_E", txt(654, 206, "crosslinked \u2192 aldehyde-accessible", 12, "#8A6A6E", bold=False))
put("50_E", txt(654, 184, "\u2192 weaker ligand binding", 12, RED, bold=False))
put("50_E", txt(654, 162, "\u2192 low labeling efficiency", 12, RED, bold=False))
put("50_E", rrect(1020, 112, 500, 164, 10, "#F2FBF7", "#96CCB8", 1.6))
put("50_E", txt(1036, 252, "This work: protective fixation", 14, GREEN))
put("50_E", cell_pro(1106, 184, 58, 44, "#CDE8DB", "#E6F5EE", nuc=True, organelles=False, name="nc"))
put("50_E", txt(1174, 206, "binding site shielded by protective agent", 12, "#3A7A62", bold=False))
put("50_E", txt(1174, 184, "\u2192 stronger ligand binding", 12, GREEN, bold=False))
put("50_E", txt(1174, 162, "\u2192 preserved labeling + low background", 12, GREEN, bold=False))

# ===== Panel F: Outcomes =====
put("60_F", frame(30, 90, 420, 190, "#F2F8FF", "#A8C8E8"))
put("60_F", panel_title(50, 258, "F | Capabilities achieved", BLUE, 19))
for i, t in enumerate(["Anti-fading long-duration nanoscopy",
                       "High post-fixation labeling efficiency",
                       "Minimal non-specific background",
                       "3+ color imaging across SIM / STED / STORM / PAINT"]):
    y = 224 - i * 34
    put("60_F", circ(68, y, 11, "#D6E8F7", BLUE, 1.4))
    put("60_F", path(f"M62.5,{y} L66.5,{y-4.5} L74,{y+4.5}", stroke=BLUE, sw=2.6))
    put("60_F", txt(90, y+6, t, 13.5, "#3A4A5A", bold=False))

names = {"00_BG": "Background & Title", "10_A": "Panel A - Challenges", "20_B": "Panel B - Design Principle",
         "30_C": "Panel C - Ligand Exchange Mechanism", "40_D": "Panel D - Compatibility",
         "50_E": "Panel E - Protective Fixation Protocol", "60_F": "Panel F - Capabilities", "35_C_Instrument": "Panel C - Instrument (route B)"}
emit(r"C:/Users/zy/WorkBuddy/2026-09-27-08-36-54/paper-figures/P01/P01_redraw_pro.svg", W, H, names)
print("插画级重绘完成")
