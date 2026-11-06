#!/usr/bin/env python3
"""
上传文件到科研云服务器
用法: python upload_files.py <file1.csv> [file2.csv ...] --data-names <name1>[,name2...]
"""

import argparse
import json
import os
import sys

import requests

UPLOAD_URL = os.environ.get("XM_UPLOAD_URL", "https://x-med-kyy-mcp.dazd.cn/kyy_visualization_mcp/upload_files")
CONNECT_TIMEOUT = 5
UPLOAD_READ_TIMEOUT = 60


def upload_file(filepath: str, upload_key: str) -> dict:
    filename = os.path.basename(filepath)
    print(f"  [upload] {filename} ...", file=sys.stderr)

    try:
        with open(filepath, "rb") as f:
            resp = requests.post(
                UPLOAD_URL,
                files={"file": (filename, f)},
                data={"uploadKey": upload_key},
                timeout=(CONNECT_TIMEOUT, UPLOAD_READ_TIMEOUT),
            )
    except FileNotFoundError:
        return {"error": "FILE_NOT_FOUND"}
    except PermissionError:
        return {"error": "PERMISSION_DENIED"}
    except requests.exceptions.RequestException as e:
        return {"error": "NETWORK_ERROR", "message": str(e)}

    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code}", "detail": resp.text[:500]}

    try:
        data = resp.json()
    except (json.JSONDecodeError, ValueError):
        return {"error": "INVALID_RESPONSE", "raw": resp.text[:500]}

    return {"fileId": data.get("fileId", "")}


def main():
    parser = argparse.ArgumentParser(description="上传文件到科研云服务器")
    parser.add_argument("files", nargs="+", help="要上传的文件路径")
    parser.add_argument("--data-names", required=True, help="dataFileName 映射，逗号分隔，与文件顺序一一对应")
    parser.add_argument("--upload-key", default="", help="文件上传临时令牌，也可通过环境变量 XM_UPLOAD_KEY 传入")
    args = parser.parse_args()

    upload_key = args.upload_key or os.environ.get("XM_UPLOAD_KEY", "")
    if not upload_key:
        print("错误: 需要提供 --upload-key 参数或设置 XM_UPLOAD_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    data_names = [n.strip() for n in args.data_names.split(",")]

    if len(data_names) != len(args.files):
        print(f"错误: --data-names 数量 ({len(data_names)}) 与文件数量 ({len(args.files)}) 不一致", file=sys.stderr)
        sys.exit(1)

    print(f"[upload_files] 上传 {len(args.files)} 个文件 ...", file=sys.stderr)

    result = {}
    for i, fp in enumerate(args.files):
        data_name = data_names[i]

        if not os.path.exists(fp):
            result[data_name] = "FILE_NOT_FOUND"
            print(f"  [FAIL] {fp} 不存在", file=sys.stderr)
            continue

        r = upload_file(fp, upload_key=upload_key)
        if isinstance(r, dict) and "fileId" in r and "error" not in r:
            result[data_name] = r["fileId"]
            print(f"  [OK] {os.path.basename(fp)} → {data_name}={r['fileId']}", file=sys.stderr)
        else:
            err = r.get("error", "UNKNOWN") if isinstance(r, dict) else "UNKNOWN"
            result[data_name] = err
            print(f"  [FAIL] {os.path.basename(fp)}: {err}", file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()