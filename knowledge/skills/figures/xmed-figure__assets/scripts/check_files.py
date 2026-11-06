#!/usr/bin/env python3
"""
检查图表所需的输入文件要求
用法: python check_files.py <chartType> --server-data '{"inputFiles":[...],"uploadKey":"...","uploadExpire":300}'
"""

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REFERENCES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "references")


def read_reference_file_requirements(chart_type: str) -> str:
    ref_path = os.path.join(REFERENCES_DIR, f"{chart_type}.md")
    if not os.path.exists(ref_path):
        return ""

    try:
        with open(ref_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (IOError, UnicodeDecodeError) as e:
        print(f"[check_files] 读取 reference 文件失败: {e}", file=sys.stderr)
        return ""

    m = re.search(r"## 文件要求\n+(.+?)(?=\n## |\Z)", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def main():
    parser = argparse.ArgumentParser(description="检查图表文件要求")
    parser.add_argument("chartType", help="图表类型代号 (如 volcano, pca)")
    parser.add_argument("--server-data", default="{}", help="get_chart_input_files MCP 返回的 JSON 字符串")
    args = parser.parse_args()

    chart_type = args.chartType

    if not re.match(r'^[a-z0-9_]+$', chart_type):
        print(json.dumps({"error": "INVALID_CHART_TYPE", "message": "chartType 包含非法字符"}))
        sys.exit(1)

    ref_path = os.path.join(REFERENCES_DIR, f"{chart_type}.md")
    if not os.path.exists(ref_path):
        print(json.dumps({"error": "INVALID_CHART_TYPE", "message": f"'{chart_type}' 不在支持的图表类型中"}))
        sys.exit(1)

    try:
        server_result = json.loads(args.server_data)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": "INVALID_SERVER_DATA", "message": str(e)}, ensure_ascii=False))
        sys.exit(1)

    ref_req = read_reference_file_requirements(chart_type)

    print(f"[check_files] chartType={chart_type}", file=sys.stderr)
    if ref_req:
        print(f"[check_files] reference 文件要求: {ref_req[:100]}...", file=sys.stderr)

    server_files = server_result.get("inputFiles", []) if isinstance(server_result, dict) else []

    output = {
        "chartType": chart_type,
        "referenceRequirements": ref_req,
        "serverFiles": server_files,
        "uploadKey": server_result.get("uploadKey", "") if isinstance(server_result, dict) else "",
        "uploadExpire": server_result.get("uploadExpire", 0) if isinstance(server_result, dict) else 0,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()