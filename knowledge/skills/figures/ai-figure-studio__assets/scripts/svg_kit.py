# svg_kit.py — SVG 绘图函数库（供各论文重绘脚本复用）
import math

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

W, H = 1600, 1000
defs = []
gid = [0]
def nid(p="e"):
    gid[0] += 1
    return f"{p}{gid[0]}"

def grad(c1, c2, cx=0.40, cy=0.36, r=0.75):
    i = nid("g")
    defs.append(f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}">'
                f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></radialGradient>')
    return f"url(#{i})"

def lin(c1, c2):
    i = nid("lg")
    defs.append(f'<linearGradient id="{i}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')
    return f"url(#{i})"

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
W6 = [0.05,-0.04,0.06,-0.03,0.05,-0.02]

def cell(cx, cy, r, c1, c2, name="cell", rx=None, ry=None):
    rx = rx or r; ry = ry or r
    g = grad(c1, c2)
    d = smooth_blob(cx, cy, rx, ry, W8)
    s = [f'<path id="{name}" d="{d}" fill="{g}" stroke="{c2}" stroke-width="2.2"/>']
    hl = smooth_blob(cx-rx*0.36, cy-ry*0.40, rx*0.30, ry*0.20, W6)
    s.append(f'<path d="{hl}" fill="#FFFFFF" opacity="0.42"/>')
    return "\n".join(s)

def circle(cx, cy, r, fill, stroke=None, sw=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{st}/>'

def rect(x, y, w, h, fill, stroke=None, sw=0, rx=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}/>'

def ell(cx, cy, rx, ry, fill, stroke=None, sw=0):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}"{st}/>'

def line(x1, y1, x2, y2, col="#333", w=3, cap="round", dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="{cap}"{da}/>'

def arrow(x1, y1, x2, y2, w=4, col="#333333", dash=None, hl=14, hw=11):
    dx, dy = x2-x1, y2-y1
    L = math.hypot(dx, dy)
    ux, uy = dx/L, dy/L
    bx, by = x2-ux*hl, y2-uy*hl
    da = f' stroke-dasharray="{dash}"' if dash else ''
    px, py = -uy, ux
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{da}/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {bx+px*hw/2:.1f},{by+py*hw/2:.1f} {bx-px*hw/2:.1f},{by-py*hw/2:.1f}" fill="{col}"/>')

def curve_arrow(x1, y1, x2, y2, bend, w=4, col="#333", dash=None, hl=14, hw=11):
    mx, my = (x1+x2)/2, (y1+y2)/2
    dx, dy = x2-x1, y2-y1
    L = math.hypot(dx, dy)
    px, py = -dy/L, dx/L
    cx, cy = mx+px*bend, my+py*bend
    tx, ty = x2-cx, y2-cy
    tL = math.hypot(tx, ty)
    tx, ty = tx/tL, ty/tL
    bx, by = x2-tx*hl, y2-ty*hl
    da = f' stroke-dasharray="{dash}"' if dash else ''
    qx, qy = -ty, tx
    return (f'<path d="M{x1:.1f} {y1:.1f} Q{cx:.1f} {cy:.1f} {bx:.1f} {by:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{da}/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {bx+qx*hw/2:.1f},{by+qy*hw/2:.1f} {bx-qx*hw/2:.1f},{by-qy*hw/2:.1f}" fill="{col}"/>')

def block_arrow(x, ytop, ybot, w, col):
    hh, hw = w*1.1, w*2.2
    yb = ybot+hh
    pts = [(x-w/2,ytop),(x+w/2,ytop),(x+w/2,yb),(x+hw/2,yb),(x,ybot),(x-hw/2,yb),(x-w/2,yb)]
    return f'<polygon points="{" ".join(f"{p[0]:.0f},{p[1]:.0f}" for p in pts)}" fill="{col}"/>'

def txt(x, y, s, size=22, col="#1A1A1A", bold=True, italic=False, anchor="start"):
    fw = ' font-weight="bold"' if bold else ''
    fs = ' font-style="italic"' if italic else ''
    return (f'<text x="0" y="0" transform="translate({x},{y}) scale(1,-1)" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="{size}"'
            f'{fw}{fs} fill="{col}" text-anchor="{anchor}">{esc(s)}</text>')

def frame(x, y, w, h, fill="#F2F7FC", stroke="#9CB8D4", rx=14, sw=2, fillurl=False):
    f = fill
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" stroke="{stroke}" stroke-width="{sw}"/>'

def dna(x1, x2, y, h, col="#4A76C8", sw=3.6):
    a, b = [], []
    n = 60
    for i in range(n+1):
        px = x1 + (x2-x1)*i/n
        a.append(f"{px:.1f} {y - math.sin(i/n*math.pi*6)*h/2:.1f}")
        b.append(f"{px:.1f} {y + math.sin(i/n*math.pi*6)*h/2:.1f}")
    s = [f'<path d="M{" L".join(a)}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>',
         f'<path d="M{" L".join(b)}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"/>']
    for k in range(1, 12):
        px = x1 + (x2-x1)*k/12
        off = math.sin(k/12*math.pi*6)*h/2
        s.append(line(px, y-off, px, y+off, col, sw*0.55))
    return "\n".join(s)

G = {}
def put(grp, content):
    G.setdefault(grp, []).append(content)

def emit(path, W_, H_, names=None):
    body = []
    for k in sorted(G.keys()):
        body.append(f'  <g id="{k}" inkscape:label="{esc((names or {}).get(k, k))}">')
        for item in G[k]:
            if item:
                body.append("    " + item.replace("\n", "\n    "))
        body.append("  </g>")
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           f'width="{W_}" height="{H_}" viewBox="0 0 {W_} {H_}">\n'
           f'<g transform="translate(0,{H_}) scale(1,-1)">\n'
           '<defs>' + "".join(defs) + '</defs>\n' + "\n".join(body) + "\n  </g>\n</svg>\n")
    open(path, "w", encoding="utf-8").write(svg)
    return svg
