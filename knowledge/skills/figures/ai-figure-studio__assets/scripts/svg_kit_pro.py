# svg_kit_pro.py — 插画级 SVG 组件库（精细细胞/细胞器/蛋白/纳米材料/仪器）
import math

W, H = 1600, 1000
defs = []
gid = [0]
G = {}

def nid(p="e"):
    gid[0] += 1
    return f"{p}{gid[0]}"

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def put(grp, content):
    if content:
        G.setdefault(grp, []).append(content)

# ---------- 渐变 ----------
def rgrad(stops, cx=0.38, cy=0.34, r=0.78):
    i = nid("rg")
    s = "".join(f'<stop offset="{o}" stop-color="{c}"{f" stop-opacity=\"{a}\"" if a else ""}/>' for o, c, a in stops)
    defs.append(f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>')
    return f"url(#{i})"

def lgrad(stops, x1=0, y1=0, x2=0, y2=1):
    i = nid("lg")
    s = "".join(f'<stop offset="{o}" stop-color="{c}"{f" stop-opacity=\"{a}\"" if a else ""}/>' for o, c, a in stops)
    defs.append(f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')
    return f"url(#{i})"

def shadow(cx, cy, rx, ry, op=0.16):
    return f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="#54658A" opacity="{op}"/>'

# ---------- 基础 ----------
def circ(cx, cy, r, fill, stroke=None, sw=0, op=None):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o = f' opacity="{op}"' if op else ''
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"{st}{o}/>'

def ell(cx, cy, rx, ry, fill, stroke=None, sw=0, op=None, rot=None):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o = f' opacity="{op}"' if op else ''
    rotv = f' transform="rotate({rot} {cx:.1f} {cy:.1f})"' if rot is not None else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}"{st}{o}{rotv}/>'

def rrect(x, y, w, h, r, fill, stroke=None, sw=0, op=None):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o = f' opacity="{op}"' if op else ''
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:.1f}" fill="{fill}"{st}{o}/>'

def ln(x1, y1, x2, y2, col="#333", w=3, cap="round", dash=None, op=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    o = f' opacity="{op}"' if op else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="{cap}"{da}{o}/>'

def path(d, fill="none", stroke=None, sw=0, op=None, cap="round"):
    st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"' if stroke else ''
    o = f' opacity="{op}"' if op else ''
    return f'<path d="{d}" fill="{fill}"{st}{o}/>'

def smooth_blob(cx, cy, rx, ry, wob):
    n = len(wob)
    pts = []
    for i in range(n):
        a = 2*math.pi*i/n
        rr = 1 + wob[i]
        pts.append((cx + math.cos(a)*rx*rr, cy + math.sin(a)*ry*rr))
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f} "
    for i in range(n):
        p0=pts[(i-1)%n]; p1=pts[i]; p2=pts[(i+1)%n]; p3=pts[(i+2)%n]
        c1x=p1[0]+(p2[0]-p0[0])/6; c1y=p1[1]+(p2[1]-p0[1])/6
        c2x=p2[0]-(p3[0]-p1[0])/6; c2y=p2[1]-(p3[1]-p1[1])/6
        d += f"C{c1x:.1f} {c1y:.1f} {c2x:.1f} {c2y:.1f} {p2[0]:.1f} {p2[1]:.1f} "
    return d + "Z"

W8 = [0.05,-0.03,0.06,-0.02,0.04,-0.05,0.03,-0.02]

# ---------- 精细细胞（膜/质/核/细胞器/高光/影）----------
def cell_pro(cx, cy, rx, ry, c_out, c_in, nuc=True, organelles=True, name="cell", wob=None):
    wob = wob or W8
    s = []
    # 投影
    s.append(shadow(cx + rx*0.06, cy - ry*0.10, rx*1.02, ry*0.98, 0.10))
    # 细胞膜（外轮廓，淡色）+ 细胞质（内渐变）
    body = smooth_blob(cx, cy, rx, ry, wob)
    s.append(path(body, fill=c_out))
    inner = smooth_blob(cx, cy, rx*0.955, ry*0.955, wob)
    s.append(path(inner, fill=rgrad([("0", "#FFFFFF", "0.55"), ("0.45", c_in, None), ("1", c_in, None)])))
    if organelles:
        # 线粒体
        for (mx, my, ang) in [(-rx*0.45, ry*0.32, -18), (rx*0.42, -ry*0.30, 22), (rx*0.15, ry*0.55, 5)]:
            s.append(mitochondrion(cx+mx, cy+my, ang, rx*0.30, rx*0.11))
        # 内质网（波浪带）
        for k in range(3):
            yk = cy + ry*0.05 - k*ry*0.13
            d = "M" + " L".join(f"{cx - rx*0.62 + i*rx*1.24/14:.0f} {yk + math.sin(i*1.1+k)*ry*0.045:.0f}" for i in range(15))
            s.append(path(d, stroke="#B08CC8", sw=max(2, rx*0.035), op="0.75"))
        # 高尔基体
        for k in range(3):
            s.append(path(f"M{cx+rx*0.30:.0f} {cy-ry*0.10-k*ry*0.09:.0f} q{rx*0.16:.0f} {-ry*0.05:.0f} {rx*0.32:.0f} 0",
                          stroke="#7FB0D8", sw=max(2, rx*0.04), op="0.8"))
    if nuc:
        s.append(nucleus_pro(cx - rx*0.10, cy + ry*0.02, rx*0.40, ry*0.36))
    # 高光
    hl = smooth_blob(cx - rx*0.42, cy + ry*0.44, rx*0.26, ry*0.15, [0.2,-0.1,0.15,0.05,-0.15,0.1,-0.05,0.12])
    s.append(path(hl, fill="#FFFFFF", op="0.38"))
    return "\n".join(s)

def mitochondrion(cx, cy, ang, ln_, w):
    d = f'M{-ln_/2:.0f} 0 q{-ln_*0.28:.0f} {-w:.0f} 0 {-w*2:.0f} q{ln_*0.72:.0f} {-w*0.9:.0f} {ln_} 0 q{ln_*0.28:.0f} {w:.0f} 0 {w*2:.0f} Z'
    s = [f'<g transform="translate({cx:.0f},{cy:.0f}) rotate({ang})">']
    s.append(f'<path d="{d}" fill="#E88A6A" stroke="#C05A3A" stroke-width="1.6"/>')
    for k in range(4):
        xx = -ln_*0.36 + k*ln_*0.24
        s.append(f'<path d="M{xx:.0f} {-w*0.75:.0f} q{w*0.5:.0f} {w*0.75:.0f} 0 {w*1.5:.0f}" fill="none" stroke="#C05A3A" stroke-width="1.4" opacity="0.7"/>')
    s.append("</g>")
    return "".join(s)

def nucleus_pro(cx, cy, rx, ry):
    s = [ell(cx, cy, rx, ry, rgrad([("0", "#C9AEE0", None), ("0.7", "#9B7BC4", None), ("1", "#7A5CA8", None)]), stroke="#6A4C96", sw=2)]
    s.append(ell(cx, cy, rx*0.90, ry*0.90, "none", stroke="#8A6AB4", sw=1.2, op="0.7"))
    s.append(circ(cx + rx*0.22, cy - ry*0.10, rx*0.20, "#6A4C96", op="0.55"))
    for (dx, dy, rr) in [(-0.45, 0.30, 0.11), (0.10, 0.45, 0.09), (-0.15, -0.40, 0.10), (0.45, 0.25, 0.08)]:
        s.append(circ(cx + rx*dx, cy + ry*dy, rx*rr, "#5A3C86", op="0.28"))
    s.append(ell(cx - rx*0.35, cy + ry*0.40, rx*0.28, ry*0.16, "#FFFFFF", op="0.35"))
    return "\n".join(s)

# ---------- 结构域蛋白 ----------
def protein_domains(x, y, h, segs, name="prot"):
    """segs: [(w, color)] 横向结构域串"""
    s = []
    cx = x
    for (w, col) in segs:
        s.append(rrect(cx, y, w, h, h*0.5, col, stroke="#00000030", sw=1))
        cx += w
    return "\n".join(s)

def receptor_pro(x, y, w, h, col="#C44E6E", label=None, lx=0, ly=0):
    """穿膜受体：膜外域(圆角)+跨膜柄"""
    s = [rrect(x - w/2, y + h*0.15, w, h*0.75, w*0.32, rgrad([("0", "#F2B8CC", None), ("1", col, None)]), stroke=col, sw=1.6)]
    s.append(rrect(x - w*0.13, y - h*0.35, w*0.26, h*0.55, w*0.1, col))
    return "\n".join(s)

# ---------- 立体 DNA ----------
def dna_3d(x1, x2, y, h, col_a="#3E6FC4", col_b="#7BA3E0"):
    n = 64
    s = []
    for strand, col, sign in [(0, col_a, 1), (1, col_b, -1)]:
        pts = []
        for i in range(n+1):
            px = x1 + (x2-x1)*i/n
            py = y + sign*math.sin(i/n*math.pi*6)*h/2
            pts.append(f"{px:.1f} {py:.1f}")
        s.append(path("M" + " L".join(pts), stroke=col, sw=max(3, h*0.10)))
    for k in range(14):
        px = x1 + (x2-x1)*k/14
        off = math.sin(k/14*math.pi*6)*h/2
        s.append(ln(px, y-off, px, y+off, "#9DB8E8", max(2, h*0.055)))
    return "\n".join(s)

# ---------- 纳米颗粒（核壳 + 配体）----------
def nanoparticle(cx, cy, r, core, shell, ligands=10, lig_col="#F0A030"):
    s = [circ(cx, cy, r*1.12, rgrad([("0", shell, "0.9"), ("1", shell, None)]), op="0.55")]
    s.append(circ(cx, cy, r, rgrad([("0", "#FFFFFF", "0.65"), ("0.4", core, None), ("1", core, None)]), stroke="#00000022", sw=1.2))
    for k in range(ligands):
        a = 2*math.pi*k/ligands + 0.25
        x1, y1 = cx + math.cos(a)*r*1.05, cy + math.sin(a)*r*1.05
        x2, y2 = cx + math.cos(a)*r*1.42, cy + math.sin(a)*r*1.42
        s.append(ln(x1, y1, x2, y2, lig_col, max(2, r*0.10)))
        s.append(circ(x2, y2, max(2, r*0.13), lig_col))
    return "\n".join(s)

# ---------- 3D 培养皿 ----------
def dish(cx, cy, r, liquid=None, cells=None, lid=True):
    s = []
    s.append(shadow(cx, cy - r*0.30, r*1.05, r*0.38, 0.13))
    s.append(ell(cx, cy, r, r*0.36, rgrad([("0", "#FFFFFF", "0.9"), ("1", "#C9DCEC", None)]), stroke="#8FB4D4", sw=2.4))
    if liquid:
        s.append(ell(cx, cy - r*0.04, r*0.86, r*0.30, liquid, op="0.85"))
    if cells:
        for (dx, dy, rr, col) in cells:
            s.append(ell(cx + dx*r, cy + dy*r*0.36 - r*0.04, rr*r, rr*r*0.5, col, stroke="#00000022", sw=1))
    if lid:
        s.append(ell(cx, cy + r*0.10, r*1.02, r*0.36, "none", stroke="#A8C8E0", sw=1.6, op="0.8"))
    return "\n".join(s)

# ---------- 3D 超分辨显微镜 ----------
def microscope(cx, cy, s_=1.0):
    s = [f'<g transform="translate({cx:.0f},{cy:.0f}) scale({s_})">']
    s.append(shadow(0, -64, 62, 12, 0.16))
    # 底座
    s.append(rrect(-56, -58, 112, 16, 7, lgrad([("0","#5A6A80",None),("1","#3A4A60",None)])))
    s.append(rrect(-26, -112, 52, 58, 8, lgrad([("0","#7A8CA0",None),("1","#4A5A70",None)])))
    # 载物台
    s.append(rrect(-64, -40, 128, 10, 5, "#8A9CB0"))
    # 物镜（倒置）
    s.append(rrect(-13, -96, 26, 40, 8, lgrad([("0","#9AAEC2",None),("1","#6A7E92",None)])))
    s.append(rrect(-17, -60, 34, 12, 5, "#B0C0D0"))
    # 荧光光路（激发/发射）
    s.append(path("M0 -96 L0 -140", stroke="#3ACA9A", sw=4, op="0.9"))
    s.append(path("M-34 -142 L34 -142", stroke="#3ACA9A", sw=5, op="0.9"))
    s.append(circ(0, -146, 9, "#3ACA9A", op="0.35"))
    # 探测器
    s.append(rrect(-40, -168, 30, 22, 6, "#4A5A70"))
    s.append(circ(-25, -157, 7, "#2E9E7A"))
    s.append(circ(26, -150, 10, "#C9DAEA", stroke="#7A8CA0", sw=1.5, op="0.9"))
    s.append("</g>")
    return "".join(s)

# ---------- 移液器 ----------
def pipette(cx, cy, ang, ln_=90, w=13):
    s = [f'<g transform="translate({cx:.0f},{cy:.0f}) rotate({ang})">']
    s.append(rrect(-w/2, -ln_*0.55, w, ln_*1.1, w*0.32, lgrad([("0","#F0F4F8",None),("1","#C2CEDC",None)]), stroke="#98A8BC", sw=1.4))
    s.append(rrect(-w*0.34, -ln_*0.62, w*0.68, w*0.5, w*0.14, "#5A8AC0"))
    s.append(f'<polygon points="{-w*0.16:.0f},{ln_*0.55:.0f} {w*0.16:.0f},{ln_*0.55:.0f} {w*0.05:.0f},{ln_*0.86:.0f} {-w*0.05:.0f},{ln_*0.86:.0f}" fill="#A8B8CC"/>')
    s.append(circ(0, ln_*0.94, w*0.13, "#6AAEE0", op="0.9"))
    s.append("</g>")
    return "".join(s)

# ---------- 试剂瓶 ----------
def vial(cx, cy, w=46, h=86, liquid="#F2D06B", label=""):
    s = [shadow(cx, cy - h*0.6, w*0.72, 7, 0.14)]
    s.append(rrect(cx - w/2, cy - h*0.55, w, h, w*0.18, lgrad([("0","#FFFFFF","0.85"),("1","#DCE8F2",None)]), stroke="#98B0C8", sw=1.8))
    s.append(rrect(cx - w/2 + 4, cy - h*0.42, w - 8, h*0.42, w*0.14, liquid, op="0.9"))
    s.append(rrect(cx - w*0.30, cy + h*0.42, w*0.60, h*0.13, 4, "#6A7E92"))
    s.append(rrect(cx - w*0.22, cy + h*0.53, w*0.44, h*0.05, 3, "#4A5A70"))
    return "\n".join(s)

# ---------- 箭头 / 文本 ----------
def arrow(x1, y1, x2, y2, w=4, col="#3A4A5A", dash=None, hl=14, hw=11):
    dx, dy = x2-x1, y2-y1
    L = math.hypot(dx, dy)
    ux, uy = dx/L, dy/L
    bx, by = x2-ux*hl, y2-uy*hl
    px, py = -uy, ux
    s = [ln(x1, y1, bx, by, col, w, dash=dash)]
    s.append(f'<polygon points="{x2:.1f},{y2:.1f} {bx+px*hw/2:.1f},{by+py*hw/2:.1f} {bx-px*hw/2:.1f},{by-py*hw/2:.1f}" fill="{col}"/>')
    return "\n".join(s)

def curve_arrow(x1, y1, x2, y2, bend, w=4, col="#3A4A5A", dash=None, hl=14, hw=11):
    mx, my = (x1+x2)/2, (y1+y2)/2
    dx, dy = x2-x1, y2-y1
    L = math.hypot(dx, dy)
    px, py = -dy/L, dx/L
    cx, cy = mx+px*bend, my+py*bend
    tx, ty = x2-cx, y2-cy
    tL = math.hypot(tx, ty)
    tx, ty = tx/tL, ty/tL
    bx, by = x2-tx*hl, y2-ty*hl
    qx, qy = -ty, tx
    da = f' stroke-dasharray="{dash}"' if dash else ''
    s = [f'<path d="M{x1:.1f} {y1:.1f} Q{cx:.1f} {cy:.1f} {bx:.1f} {by:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{da}/>']
    s.append(f'<polygon points="{x2:.1f},{y2:.1f} {bx+qx*hw/2:.1f},{by+qy*hw/2:.1f} {bx-qx*hw/2:.1f},{by-qy*hw/2:.1f}" fill="{col}"/>')
    return "\n".join(s)

def txt(x, y, s, size=22, col="#1A1A1A", bold=True, italic=False, anchor="start"):
    fw = ' font-weight="bold"' if bold else ''
    fs = ' font-style="italic"' if italic else ''
    return (f'<text x="0" y="0" transform="translate({x},{y}) scale(1,-1)" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="{size}"{fw}{fs} '
            f'fill="{col}" text-anchor="{anchor}">{esc(s)}</text>')

def frame(x, y, w, h, fill="#F7FBFF", stroke="#A8C4DE", rx=16, sw=2, op=None):
    return rrect(x, y, w, h, rx, fill, stroke, sw, op)

def panel_title(x, y, s, col="#1F4E79", size=20):
    return txt(x, y, s, size, col)

def emit(path_out, W_, H_, names=None):
    body = []
    for k in sorted(G.keys()):
        body.append(f'  <g id="{k}" inkscape:label="{esc((names or {}).get(k, k))}">')
        for item in G[k]:
            body.append("    " + item.replace("\n", "\n    "))
        body.append("  </g>")
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           f'width="{W_}" height="{H_}" viewBox="0 0 {W_} {H_}">\n'
           f'<g transform="translate(0,{H_}) scale(1,-1)">\n'
           '<defs>' + "".join(defs) + '</defs>\n' + "\n".join(body) + "\n  </g>\n</svg>\n")
    open(path_out, "w", encoding="utf-8").write(svg)
    return svg

# ================= 素材库调用（跨论文复用）=================
import os as _os, re as _re
ASSET_LIB = r"C:/Users/zy/.workbuddy/skills/ai-figure-studio/assets"

def asset(rel_path, tx, ty, scale=1.0, group="40_Assets"):
    """把素材库 SVG 嵌入主图。
    rel_path: 如 "instruments/microscope_fluorescence.svg"
    tx, ty  : 素材在 y-up 坐标系中的【左下角】位置（函数内部自动处理 scale 翻转基准）
    scale   : 缩放（保持纵横比）
    返回    : (宽, 高) 实际占位尺寸（便于排版）
    """
    p = _os.path.join(ASSET_LIB, rel_path)
    svg = open(p, encoding="utf-8").read()
    mw = _re.search(r'width="(\d+)"', svg); mh = _re.search(r'height="(\d+)"', svg)
    w = int(mw.group(1)); h = int(mh.group(1))
    prefix = f"as{gid[0]}_"
    # 重命名内部 id 防冲突
    svg = _re.sub(r'id="([^"]+)"', lambda m: f'id="{prefix}{m.group(1)}"', svg)
    svg = _re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{prefix}{m.group(1)})', svg)
    d = _re.search(r"<defs>(.*?)</defs>", svg, _re.S)
    if d and d.group(1).strip():
        defs.append(d.group(1))
    paths = _re.findall(r"<path[^>]*/>", svg)
    inner = "".join(paths)
    _ty_top = ty + h * scale   # scale(s,-s) 下，translate 的 y 基准是素材【顶部】
    put(group, f'<g transform="translate({tx},{_ty_top}) scale({scale},{-scale})">{inner}</g>')
    return w * scale, h * scale
