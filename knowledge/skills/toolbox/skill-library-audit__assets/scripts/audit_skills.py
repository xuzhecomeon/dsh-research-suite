"""技能库健康体检。

用法：
    python audit_skills.py                 # 全量体检
    python audit_skills.py --duplicates    # 只查完全重复
    python audit_skills.py --names         # 只查名称一致性
    python audit_skills.py --top 20        # 列出体积最大的 N 个技能
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".workbuddy", "skills")
SKIP_DIRS = {"__pycache__", ".git"}
META_FILES = {"_meta.json", "_skillhub_meta.json", "_icon.png", "skill-card.md"}


def md5(path: str) -> str:
    try:
        with open(path, "rb") as fh:
            return hashlib.md5(fh.read()).hexdigest()
    except OSError:
        return "READ_ERROR"


def scan(base: str) -> dict[str, dict[str, tuple[int, str]]]:
    """返回 {技能名: {相对路径: (大小, md5)}}"""
    out: dict[str, dict[str, tuple[int, str]]] = {}
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not os.path.isdir(d):
            continue
        files: dict[str, tuple[int, str]] = {}
        for r, dirs, fs in os.walk(d):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for f in fs:
                p = os.path.join(r, f)
                rel = os.path.relpath(p, d).replace("\\", "/")
                try:
                    files[rel] = (os.path.getsize(p), md5(p))
                except OSError:
                    files[rel] = (-1, "ERROR")
        out[name] = files
    return out


def fm_name(skill_dir: str):
    p = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(p):
        return None
    try:
        t = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    if not t.startswith("---"):
        return None
    fm = t[3:].split("\n---", 1)[0]
    m = re.search(r"^name\s*:\s*(.+)$", fm, flags=re.M)
    return m.group(1).strip().strip("\"'") if m else None


def report_duplicates(data):
    print("=" * 70)
    print("① 完全重复检测（逐文件 md5 比对）")
    print("=" * 70)
    names = list(data)
    groups = []
    seen = set()
    for i, a in enumerate(names):
        if a in seen:
            continue
        for b in names[i + 1 :]:
            if b in seen:
                continue
            fa, fb = data[a], data[b]
            if not fa or not fb:
                continue
            # 排除元数据文件后比较功能文件
            ka = {k for k in fa if k not in META_FILES}
            kb = {k for k in fb if k not in META_FILES}
            if not ka or ka != kb:
                continue
            if all(fa[k][1] == fb[k][1] for k in ka):
                groups.append((a, b, sorted(ka)))
                seen.add(a)
                seen.add(b)
                break
    if not groups:
        print("  未发现完全重复的技能。\n")
        return
    for a, b, files in groups:
        print(f"  ⚠ {a}")
        print(f"    与 {b} 的功能文件完全相同（{len(files)} 个）")
        only_a = sorted({k for k in data[a] if k not in META_FILES} - {k for k in data[b] if k not in META_FILES})
        only_b = sorted({k for k in data[b] if k not in META_FILES} - {k for k in data[a] if k not in META_FILES})
        print(f"    仅 {a} 独有: {only_a or '（无 → 删除安全）'}")
        print(f"    仅 {b} 独有: {only_b or '（无）'}")
    print()


def strip_installer_suffix(d: str) -> str:
    """SkillHub 安装器会给目录名追加 __skillhub 后缀以避免重名冲突。
    这是安装器约定，不是作者的设计——比较名称时应先剥离，
    否则会把几十个正常技能误报为「名称不一致」。"""
    for suf in ("__skillhub",):
        if d.endswith(suf):
            return d[: -len(suf)]
    return d


def report_names(base, data):
    print("=" * 70)
    print("② 目录名 vs frontmatter name（已剥离 __skillhub 安装器后缀）")
    print("=" * 70)
    bad = []
    for name in data:
        n = fm_name(os.path.join(base, name))
        if n and n != strip_installer_suffix(name):
            bad.append((name, n))
    if not bad:
        print("  全部一致。\n")
        return
    for d, n in bad:
        # 判断是否为作者有意设计
        hits = 0
        for r, dirs, fs in os.walk(os.path.join(base, d)):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for f in fs:
                if os.path.splitext(f)[1].lower() not in {
                    ".md", ".py", ".yaml", ".yml", ".json", ".sh", ".toml", ".txt"
                }:
                    continue
                try:
                    t = open(os.path.join(r, f), encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                hits += len(re.findall(re.escape(n), t))
        verdict = "作者有意设计，保持原样" if hits >= 3 else "疑似疏漏，可统一"
        print(f"  目录 {d}")
        print(f"       frontmatter name = {n}   （被引用 {hits} 处 → {verdict}）")
    print()


def report_size(data):
    print("=" * 70)
    print("③ 规模统计")
    print("=" * 70)
    sizes = []
    for name, files in data.items():
        total = sum(s for s, _ in files.values() if s > 0)
        sizes.append((total, len(files), name))
    sizes.sort(reverse=True)
    grand = sum(s for s, _, _ in sizes)
    print(f"  技能总数 : {len(data)}")
    print(f"  文件总数 : {sum(n for _, n, _ in sizes):,}")
    print(f"  占用空间 : {grand:,} 字节 ({grand/1048576:.1f} MB)")
    print()
    print("  体积最大的 10 个：")
    for s, n, name in sizes[:10]:
        print(f"    {s:>12,} B  {n:>5} 文件  {name}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=DEFAULT_DIR)
    ap.add_argument("--duplicates", action="store_true")
    ap.add_argument("--names", action="store_true")
    ap.add_argument("--top", type=int)
    args = ap.parse_args()

    if not os.path.isdir(args.dir):
        print("目录不存在:", args.dir)
        return 1

    data = scan(args.dir)
    if args.top:
        sizes = sorted(
            ((sum(s for s, _ in f.values() if s > 0), len(f), n) for n, f in data.items()),
            reverse=True,
        )
        for s, n, name in sizes[: args.top]:
            print(f"{s:>12,} B  {n:>5} 文件  {name}")
        return 0

    if args.duplicates:
        report_duplicates(data)
    elif args.names:
        report_names(args.dir, data)
    else:
        report_duplicates(data)
        report_names(args.dir, data)
        report_size(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
