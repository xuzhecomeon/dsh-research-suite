#!/usr/bin/env python3
"""
下载 MCP 结果图到本地
用法: python download_results.py --urls "url1,url2" --output-dir ./output
"""

import argparse
import json
import os
import sys
import time
from urllib.parse import urlparse

import requests

CONNECT_TIMEOUT = 5
DOWNLOAD_TIMEOUT = 60
ALLOWED_DOMAIN_SUFFIXES = {
    ".dazd.cn",
    ".obs.cn-east-3.myhuaweicloud.com",
    ".obs.cn-north-4.myhuaweicloud.com",
    ".obs.cn-south-1.myhuaweicloud.com",
}


def download_file(url: str, output_dir: str) -> dict:
    domain = urlparse(url).hostname or urlparse(url).netloc
    if not any(domain.endswith(s) or domain == s.lstrip(".") for s in ALLOWED_DOMAIN_SUFFIXES):
        return {"url": url, "error": "DOMAIN_NOT_ALLOWED", "message": f"不允许下载外部域名: {domain}"}

    try:
        resp = requests.get(url, timeout=(CONNECT_TIMEOUT, DOWNLOAD_TIMEOUT))
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"url": url, "error": "DOWNLOAD_FAILED", "message": str(e)}

    timestamp = int(time.time() * 1000)
    ext = ".png"
    content_type = resp.headers.get("Content-Type", "")
    if "jpeg" in content_type or "jpg" in content_type:
        ext = ".jpg"
    elif "svg" in content_type:
        ext = ".svg"
    elif "pdf" in content_type:
        ext = ".pdf"

    filename = f"result_{timestamp}{ext}"
    out_path = os.path.join(output_dir, filename)

    os.makedirs(output_dir, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(resp.content)

    size_kb = len(resp.content) // 1024
    print(f"  [OK] {filename} ({size_kb} KB)", file=sys.stderr)
    return {"url": url, "path": out_path, "size_kb": size_kb}


def main():
    parser = argparse.ArgumentParser(description="下载 MCP 结果图到本地")
    parser.add_argument("--urls", required=True, help="图片 URL，逗号分隔")
    parser.add_argument("--output-dir", default="./output", help="输出目录 (默认: ./output)")
    args = parser.parse_args()

    urls = [u.strip() for u in args.urls.split(",") if u.strip()]
    if not urls:
        print(json.dumps({"error": "NO_URLS"}, ensure_ascii=False))
        sys.exit(1)

    output_dir = os.path.abspath(args.output_dir)
    print(f"[download] {len(urls)} 张图片 → {output_dir}", file=sys.stderr)

    downloaded = []
    errors = []
    for i, url in enumerate(urls):
        print(f"  [{i + 1}/{len(urls)}] {url[:80]}...", file=sys.stderr)
        r = download_file(url, output_dir)
        if "error" in r:
            errors.append(r)
        else:
            downloaded.append(r["path"])

    result = {"downloaded": downloaded, "output_dir": output_dir}
    if errors:
        result["errors"] = errors

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()