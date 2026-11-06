#!/usr/bin/env python3
"""
batch_doi_verify.py
批量 DOI 验证脚本 — 通过 CrossRef API 核验文献 DOI 真实性

用法:
    python3 batch_doi_verify.py --doi-list dois.txt
    python3 batch_doi_verify.py --doi "10.1109/TPAMI.2023.XXXXXX"

依赖: requests (pip install requests)
"""

import argparse
import json
import time
import sys

try:
    import requests
except ImportError:
    print("请先安装 requests: pip install requests")
    sys.exit(1)


CROSSREF_API = "https://api.crossref.org/works/{doi}"
REQUEST_DELAY = 0.5  # 请求间隔（秒），避免 API 限流


def verify_doi(doi: str) -> dict:
    """通过 CrossRef API 核验单个 DOI"""
    doi = doi.strip()
    url = CROSSREF_API.format(doi=doi)
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "DOI-Verifier/1.0"})
        if resp.status_code == 200:
            data = resp.json().get("message", {})
            title = data.get("title", ["N/A"])[0] if data.get("title") else "N/A"
            authors = []
            for a in data.get("author", []):
                name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                if name:
                    authors.append(name)
            journal = (data.get("container-title") or ["N/A"])[0]
            year = None
            for date_field in ["published-print", "published-online", "issued"]:
                date_parts = data.get(date_field, {}).get("date-parts", [[]])
                if date_parts and date_parts[0]:
                    year = date_parts[0][0]
                    break
            volume = data.get("volume", "N/A")
            issue = data.get("issue", "N/A")
            page = data.get("page", "N/A")
            return {
                "doi": doi,
                "status": "VALID",
                "title": title,
                "authors": ", ".join(authors) or "N/A",
                "journal": journal,
                "year": str(year) if year else "N/A",
                "volume": volume,
                "issue": issue,
                "page": page,
                "url": f"https://doi.org/{doi}"
            }
        elif resp.status_code == 404:
            return {"doi": doi, "status": "NOT_FOUND", "error": "DOI 在 CrossRef 中不存在"}
        else:
            return {"doi": doi, "status": "ERROR", "error": f"HTTP {resp.status_code}"}
    except requests.Timeout:
        return {"doi": doi, "status": "TIMEOUT", "error": "请求超时"}
    except Exception as e:
        return {"doi": doi, "status": "ERROR", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="批量 DOI 验证工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--doi", help="单个 DOI（如 10.1109/xxx）")
    group.add_argument("--doi-list", help="DOI 列表文件（每行一个 DOI）")
    parser.add_argument("--output", help="输出 JSON 结果文件路径", default=None)
    args = parser.parse_args()

    dois = []
    if args.doi:
        dois = [args.doi]
    else:
        with open(args.doi_list, "r", encoding="utf-8") as f:
            dois = [line.strip() for line in f if line.strip()]

    print(f"共需核验 {len(dois)} 个 DOI...\n")
    results = []
    for i, doi in enumerate(dois, 1):
        print(f"[{i}/{len(dois)}] 正在核验: {doi}", end=" ... ")
        result = verify_doi(doi)
        results.append(result)
        status_icon = {"VALID": "✅", "NOT_FOUND": "❌", "ERROR": "⚠️", "TIMEOUT": "⏱️"}.get(result["status"], "❓")
        print(f"{status_icon} {result['status']}")
        if result["status"] == "VALID":
            print(f"    题名: {result['title']}")
            print(f"    作者: {result['authors']}")
            print(f"    来源: {result['journal']} ({result['year']})")
        time.sleep(REQUEST_DELAY)

    # 统计
    valid = sum(1 for r in results if r["status"] == "VALID")
    not_found = sum(1 for r in results if r["status"] == "NOT_FOUND")
    error = sum(1 for r in results if r["status"] not in ("VALID", "NOT_FOUND"))

    print(f"\n{'='*50}")
    print(f"核验完成 | ✅ 有效: {valid} | ❌ 不存在: {not_found} | ⚠️ 异常: {error}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"结果已保存至: {args.output}")


if __name__ == "__main__":
    main()
