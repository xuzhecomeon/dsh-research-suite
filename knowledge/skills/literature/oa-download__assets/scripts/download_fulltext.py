#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合法 OA 全文下载脚本(literature-search-download skill)
====================================================
输入含 DI 列的 CSV(推荐本 skill 流水线输出,含 DOI_Status 列),
经 Unpaywall API(开放获取聚合,免费)查找 OA 全文并下载 PDF。
只走合法 OA 渠道,不做任何绕过付费墙/未授权站点的操作。

用法:
  python3 download_fulltext.py <输入CSV> [--output-dir DIR] [--limit N] [--email YOU@EXAMPLE.COM]

注意:--email 必须传你自己的真实邮箱(Unpaywall 要求;example.com 域名会被 422 拒绝)。

输出:
  - pdfs/ 目录下的 PDF(命名:第一作者_年份_标题前50字.pdf)
  - download_report_<时间戳>.md 下载报告(含每篇"下一阶段建议")
  - next_stage.csv 未获取清单(带 stage 列:2=浏览器直链可下,3=agent半自动,4=机构网关,5=用户决策)
    —— 该 CSV 是"分层下载路径"中阶段 2/3/4/5 的输入,自动化优先、手动兜底
"""
import csv, json, sys, os, time, re, datetime, argparse, urllib.request, urllib.parse

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def unpaywall(doi: str, email: str):
    """查 Unpaywall,返回 (status, url_for_pdf, page_url)。
    status: 'oa' | 'not_oa' | 'notfound' | 'error'"""
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={urllib.parse.quote(email)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            m = json.load(r)
        if not m.get("is_oa"):
            return "not_oa", [], None
        # 收集所有可用 PDF 来源(主来源 + 备用,如 PMC),下载时逐个尝试
        pdfs = []
        loc = m.get("best_oa_location") or {}
        if loc.get("url_for_pdf"):
            pdfs.append(loc["url_for_pdf"])
        for loc2 in m.get("oa_locations", []):
            if loc2.get("url_for_pdf") and loc2["url_for_pdf"] not in pdfs:
                pdfs.append(loc2["url_for_pdf"])
        page = loc.get("url") or (pdfs[0] if pdfs else None)
        return "oa", pdfs, page
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "notfound", None, None  # DOI 在 Unpaywall 无记录
        # 422(邮箱被拒)/429/5xx 等:请求本身失败,不能误判为"未开放获取"
        return "error", None, None
    except Exception:
        return "error", None, None


def clean_url(url: str) -> str:
    """清洗 URL:去掉控制字符与首尾空白;空格编码为 %20(Python urllib 视空格为非法字符,实测报 'URL can't contain control characters')"""
    url = re.sub(r"[\x00-\x1f\x7f]+", "", url or "").strip()
    return url.replace(" ", "%20")


def download_pdf(url: str, dest: str, retries=2):
    """下载并校验 %PDF 头,返回 (ok, reason)。url 可为候选列表,逐个尝试(一个失败换下一个来源)。"""
    urls = url if isinstance(url, (list, tuple)) else [url]
    last_reason = "无可用链接"
    for u in urls:
        u = clean_url(u)
        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(u, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=45) as r:
                    ctype = r.headers.get("Content-Type", "")
                    data = r.read()
                if data[:4] == b"%PDF":
                    with open(dest, "wb") as f:
                        f.write(data)
                    return True, f"OK ({len(data)} bytes)"
                last_reason = f"非PDF内容(Content-Type={ctype}, 前4字节={data[:4]!r})"
                break  # 该来源内容不对,试下一个候选
            except urllib.error.HTTPError as e:
                if e.code in (403, 401):
                    last_reason = f"HTTP {e.code}(订阅墙/反爬,需机构访问或文献传递)"
                    break  # 反爬,换下一个候选来源
                last_reason = f"HTTP {e.code}"
                if attempt < retries:
                    time.sleep(2)
                    continue
            except Exception as e:
                last_reason = str(e)[:80]
                if attempt < retries:
                    time.sleep(2)
                    continue
    return False, last_reason


def safe_name(s: str, maxlen=50):
    s = re.sub(r"[\\/:*?\"<>|\r\n\t]+", "_", s).strip(" _")
    return s[:maxlen] if s else "untitled"


def suggest_stage(cat: str, reason: str) -> str:
    """根据失败类别给出"下一阶段"建议(分层下载路径的阶段号)。
    2=浏览器直链可批量下;3=agent 半自动(打印/验证/输入);4=机构网关;5=用户决策。"""
    if cat == "failed":
        if "403" in reason or "401" in reason:
            return "4"   # 反爬/订阅墙 → 机构网关优先(阶段4)
        if "非PDF" in reason:
            return "3"   # 内容拦截 → agent 浏览器处理
        return "4"       # 其他下载失败 → 机构网关/浏览器
    if cat == "not_oa":
        return "4"       # 未开放获取 → 机构网关
    if cat == "no_pdf":
        return "3"       # OA 仅 HTML → agent 浏览器找 PDF 按钮/打印
    if cat == "notfound":
        return "5"       # Unpaywall 无记录 → 用户核对/放弃
    return "5"           # error → 检查邮箱/网络重跑


def main():
    ap = argparse.ArgumentParser(description="Unpaywall 合法 OA 全文下载(分层下载路径·阶段1)")
    ap.add_argument("csv_path", help="输入 CSV(须含 DI 列;推荐本流水线输出)")
    ap.add_argument("--output-dir", default=None, help="输出目录(默认:输入 CSV 同目录)")
    ap.add_argument("--limit", type=int, default=0, help="仅处理前 N 条(测试用,0=全部)")
    ap.add_argument("--email", default="research@example.org", help="Unpaywall 要求联系邮箱(不能用 example.com 域名,会被 422 拒绝;请传你自己的真实邮箱)")
    args = ap.parse_args()

    csv_path = os.path.abspath(args.csv_path)
    out_root = args.output_dir or os.path.dirname(csv_path)
    pdf_dir = os.path.join(out_root, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)

    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    if args.limit:
        rows = rows[: args.limit]

    # 筛选有效 DOI
    has_status = "DOI_Status" in (rows[0].keys() if rows else {})
    todo = []
    for r in rows:
        doi = (r.get("DI") or "").strip()
        status = r.get("DOI_Status", "valid")
        if not doi:
            continue
        if has_status and status != "valid":
            continue
        todo.append((doi, r.get("TI", ""), r.get("AU", ""), r.get("PY", "")))
    print(f"待下载 {len(todo)} 篇(输入 {len(rows)} 条,筛除无DOI/非valid)", flush=True)

    results = {"ok": [], "not_oa": [], "no_pdf": [], "failed": [], "notfound": [], "error": []}
    used_names = set()

    for i, (doi, ti, au, py) in enumerate(todo):
        status, pdf, page = unpaywall(doi, args.email)
        if status == "notfound":
            results["notfound"].append((doi, ti, "Unpaywall 无此 DOI 记录"))
        elif status == "error":
            results["error"].append((doi, ti, "Unpaywall 请求失败(检查邮箱/网络,可重跑)"))
        elif status == "not_oa":
            results["not_oa"].append((doi, ti, "未开放获取(需机构订阅或文献传递)"))
        elif not pdf:
            results["no_pdf"].append((doi, ti, "OA 但无 PDF 直链(仅 HTML)"))
        else:
            first_au = (au.split(";")[0].strip() if au else "")
            base = f"{safe_name(first_au)}_{py or 'xxxx'}_{safe_name(ti)}"
            dest = os.path.join(pdf_dir, base + ".pdf")
            n = 1
            while dest in used_names or os.path.exists(dest):
                dest = os.path.join(pdf_dir, f"{base}_{n}.pdf")
                n += 1
            used_names.add(dest)
            ok, reason = download_pdf(pdf, dest)
            if ok:
                results["ok"].append((doi, ti, os.path.basename(dest)))
                print(f"  [{i+1}/{len(todo)}] 下载成功 {os.path.basename(dest)[:60]}", flush=True)
            else:
                src_desc = (pdf[0] if pdf else "")[:90]
                results["failed"].append((doi, ti, f"{reason} (来源: {src_desc})"))
                print(f"  [{i+1}/{len(todo)}] 失败 {reason[:50]}", flush=True)
        time.sleep(1.0)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    email_masked = re.sub(r"(?<=.).(?=.*@)", "*", args.email)

    # ---- 下一阶段清单(next_stage.csv):阶段 2/3/4/5 的输入 ----
    stage_rows = []
    for cat, items in [("failed", results["failed"]), ("not_oa", results["not_oa"]),
                       ("no_pdf", results["no_pdf"]), ("notfound", results["notfound"]),
                       ("error", results["error"])]:
        for doi, ti, why in items:
            stage = suggest_stage(cat, why)
            stage_rows.append({"DOI": doi, "TI": ti, "类别": cat, "原因": why, "下一阶段": stage})
    next_csv = os.path.join(out_root, "next_stage.csv")
    if stage_rows:
        with open(next_csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["DOI", "TI", "类别", "原因", "下一阶段"])
            w.writeheader()
            w.writerows(stage_rows)
        print(f"\n下一阶段清单(阶段2-5输入): {next_csv} ({len(stage_rows)} 条)")
    else:
        print("\n全部下载成功,无需下一阶段清单")

    # ---- 报告 ----
    stage_desc = {"2": "浏览器直链批量下", "3": "agent 半自动(打印/验证/输入)", "4": "机构网关", "5": "用户决策/核对"}
    report = f"""# OA 全文下载报告(Unpaywall 合法渠道)

- 执行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 输入文件: {csv_path}
- 渠道: Unpaywall API(开放获取聚合,仅下载出版商授权 OA 内容)
- 邮箱: {email_masked}
- 分层下载: 本报告为阶段1(全自动脚本)输出;未获取条目见 next_stage.csv,按"下一阶段"列继续处理

## 统计
- 待处理(有效 DOI): {len(todo)}
- 成功下载: {len(results['ok'])}
- 未开放获取(→阶段4机构网关): {len(results['not_oa'])}
- OA 无 PDF 直链(→阶段3 agent): {len(results['no_pdf'])}
- 下载失败(→阶段4/3): {len(results['failed'])}
- Unpaywall 无记录(→阶段5): {len(results['notfound'])}
- Unpaywall 请求失败(重跑): {len(results['error'])}
- 输出目录: {pdf_dir}

## 成功清单
"""
    for doi, ti, fn in results["ok"]:
        report += f"- {doi} | {fn} | {ti[:80]}\n"
    report += "\n## 未获取清单(含下一阶段建议)\n"
    for cat, items in [("not_oa", "未开放获取"), ("no_pdf", "OA无直链"), ("failed", "下载失败"),
                       ("notfound", "无记录"), ("error", "请求失败")]:
        if not results[cat]:
            continue
        report += f"\n### {items}({len(results[cat])})\n"
        for doi, ti, why in results[cat]:
            st = suggest_stage(cat, why)
            report += f"- {doi} | 建议阶段{st}({stage_desc[st]}) | {why[:60]} | {ti[:60]}\n"

    report_path = os.path.join(out_root, f"download_report_{ts}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n完成: 成功 {len(results['ok'])} / 未OA {len(results['not_oa'])} / 无PDF直链 {len(results['no_pdf'])} / 失败 {len(results['failed'])} / 无记录 {len(results['notfound'])} / 请求失败 {len(results['error'])}")
    print(f"PDF 目录: {pdf_dir}")
    print(f"报告: {report_path}")


if __name__ == "__main__":
    main()
