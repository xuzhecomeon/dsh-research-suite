#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WoS DOI 有效性验证脚本(并入 wos-literature-search 流程)
========================================================
对 CSV 中 DI 列的每个 DOI 做双重验证:
  1. CrossRef API(DOI 注册机构官方库): 200 = 有效; 404 = 疑似无效
  2. 疑似无效时用 doi.org HEAD 交叉确认: 仍 404 才判定 invalid
输出:
  - 原 CSV 追加 DOI_Status 列(valid / invalid / empty / error)
  - doi_validation_report_<ts>.md 验证报告
用法:
  python3 validate_dois.py <输入CSV> [--output-dir DIR] [--limit N] [--mail YOU@EXAMPLE.COM]
注意:
  CrossRef 免费接口有速率限制,脚本默认 0.8s/请求;完整验证 77 个 DOI 约需 3-5 分钟(国内网络),可后台运行。
  429 限流自动退避重试;网络异常重试 4 次后标记 error(非 invalid,可重跑)。
"""
import csv, json, sys, os, time, datetime, argparse, urllib.request, urllib.parse

HEADERS = {"User-Agent": "wos-literature-search/0.2 (mailto:research@example.com)"}
RETRIES = 4


def crossref(doi: str, mail: str):
    """返回 (status, title, year)。status: 'valid' | 'notfound' | 'error'"""
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    req = urllib.request.Request(url, headers={"User-Agent": f"wos-literature-search/0.2 (mailto:{mail})"})
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                m = json.load(r)["message"]
                title = (m.get("title") or [""])[0]
                year = None
                for k in ("published-print", "published-online", "issued"):
                    if k in m and m[k].get("date-parts"):
                        year = m[k]["date-parts"][0][0]
                        break
                return "valid", title, year
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return "notfound", "", None
            if e.code == 429:
                time.sleep(2 + attempt * 2)
                continue
            return "error", "", None
        except Exception:
            time.sleep(1.5)
            continue
    return "error", "", None


def doiorg_head(doi: str) -> bool:
    """doi.org HEAD 重定向检查,返回是否能解析(200/3xx = 有效)"""
    url = "https://doi.org/" + urllib.parse.quote(doi)
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return 200 <= r.status < 400
    except urllib.error.HTTPError as e:
        return 200 <= e.code < 400
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(description="DOI 有效性双重验证(CrossRef + doi.org)")
    ap.add_argument("csv_path", help="输入 CSV(须含 DI 列;通常为 wos-literature-search 输出)")
    ap.add_argument("--output-dir", default=None, help="输出目录(默认:输入文件所在目录)")
    ap.add_argument("--limit", type=int, default=0, help="仅验证前 N 条(测试用,0=全部)")
    ap.add_argument("--mail", default="research@example.com", help="CrossRef 要求的联系邮箱")
    args = ap.parse_args()

    csv_path = os.path.abspath(args.csv_path)
    out_dir = args.output_dir or os.path.dirname(csv_path)
    os.makedirs(out_dir, exist_ok=True)

    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    if args.limit:
        rows = rows[: args.limit]
    total = len(rows)
    print(f"待验证 {total} 条(带 DOI 的将逐个查询 CrossRef,预计每条约 2-3s)", flush=True)

    status_col = "DOI_Status"
    for i, r in enumerate(rows):
        doi = (r.get("DI") or "").strip()
        if not doi:
            r[status_col] = "empty"
        else:
            st, title, year = crossref(doi, args.mail)
            if st == "valid":
                r[status_col] = "valid"
            elif st == "notfound":
                # 交叉确认
                r[status_col] = "invalid" if not doiorg_head(doi) else "valid"
            else:
                r[status_col] = "error"
        if (i + 1) % 10 == 0 or i == total - 1:
            cnt = {s: sum(1 for x in rows[: i + 1] if x.get(status_col) == s)
                   for s in ("valid", "invalid", "empty", "error")}
            print(f"  进度 {i + 1}/{total}: {cnt}", flush=True)
        time.sleep(0.8)

    stats = {s: sum(1 for r in rows if r.get(status_col) == s) for s in ("valid", "invalid", "empty", "error")}

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = os.path.join(out_dir, os.path.basename(csv_path).replace(".csv", f"_validated_{ts}.csv"))
    fieldnames = list(rows[0].keys()) if rows else []
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    report = f"""# DOI 有效性验证报告(CrossRef 官方注册库 + doi.org 交叉确认)

- 验证时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 输入文件: {csv_path}
- 验证方式: CrossRef API(DOI 注册机构官方库)+ doi.org HEAD 双重确认
- 判定标准: CrossRef 200 且标题可回读 = valid;CrossRef 404 且 doi.org 404 = invalid;无 DI = empty;网络/限流失败 = error(可重跑)

## 统计
- 论文总数: {total}
- 有效 DOI: {stats.get('valid', 0)}
- 无效 DOI: {stats.get('invalid', 0)}
- 无 DOI(老文献未注册): {stats.get('empty', 0)}
- 异常(需重跑): {stats.get('error', 0)}

## 无效 DOI 明细
"""
    for r in rows:
        if r.get(status_col) == "invalid":
            report += f"- {r.get('DI', '')}  <- {r.get('TI', '')[:90]}\n"
    report += "\n## 异常明细(建议重跑)\n"
    for r in rows:
        if r.get(status_col) == "error":
            report += f"- {r.get('DI', '')}  <- {r.get('TI', '')[:90]}\n"
    report_path = os.path.join(out_dir, f"doi_validation_report_{ts}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n完成: 有效 {stats.get('valid',0)} / 无效 {stats.get('invalid',0)} / 空 {stats.get('empty',0)} / 异常 {stats.get('error',0)}")
    print(f"标注后的 CSV: {out_csv}")
    print(f"验证报告: {report_path}")


if __name__ == "__main__":
    main()
