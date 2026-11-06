#!/usr/bin/env python3
"""
文件格式转换工具：将 Excel / TSV 等格式转换为 CSV
满足科研云服务端 CSV 格式要求
用法: python convert_to_csv.py <input_file> [output_file] [--sheet 0]
"""

import argparse
import csv
import os
import sys


def convert_xlsx(input_path: str, output_path: str, sheet: int = 0):
    try:
        import openpyxl
    except ImportError:
        print("错误: 需要安装 openpyxl，请运行 pip install openpyxl", file=sys.stderr)
        sys.exit(1)

    wb = openpyxl.load_workbook(input_path)
    if sheet >= len(wb.sheetnames):
        print(f"错误: Sheet 索引 {sheet} 超出范围 (共 {len(wb.sheetnames)} 个 Sheet)", file=sys.stderr)
        sys.exit(1)

    ws = wb.worksheets[sheet]
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        for row in ws.iter_rows(values_only=True):
            writer.writerow([str(c) if c is not None else "" for c in row])

    return output_path


def convert_xls(input_path: str, output_path: str):
    try:
        import xlrd
    except ImportError:
        print("错误: 需要安装 xlrd，请运行 pip install xlrd", file=sys.stderr)
        sys.exit(1)

    wb = xlrd.open_workbook(input_path)
    ws = wb.sheet_by_index(0)
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        for row_idx in range(ws.nrows):
            writer.writerow([str(ws.cell_value(row_idx, col_idx)) for col_idx in range(ws.ncols)])

    return output_path


def convert_txt(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8-sig") as fi:
        sample = fi.read(4096)
        fi.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="\t,;|")
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = "\t"

        fi.seek(0)
        reader = csv.reader(fi, delimiter=delimiter)
        rows = list(reader)

    print(f"  [detect] 检测到分隔符: {repr(delimiter)}", file=sys.stderr)

    with open(output_path, "w", encoding="utf-8-sig", newline="") as fo:
        writer = csv.writer(fo)
        for row in rows:
            writer.writerow(row)

    return output_path


def convert_csv(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8-sig") as fi:
        with open(output_path, "w", encoding="utf-8-sig", newline="") as fo:
            reader = csv.reader(fi)
            writer = csv.writer(fo)
            for row in reader:
                writer.writerow(row)

    return output_path


def _preview_csv(output_path: str):
    with open(output_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)

    total = len(rows)
    cols = len(rows[0]) if rows else 0
    print(f"\n[preview] 共 {total} 行 × {cols} 列，前 5 行:", file=sys.stderr)
    for i, row in enumerate(rows[:5]):
        print(f"  [{i}] {row}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="文件格式转换：Excel/TSV → CSV")
    parser.add_argument("input", help="输入文件路径")
    parser.add_argument("output", nargs="?", default="", help="输出 CSV 文件路径 (默认: 同目录同名 .csv)")
    parser.add_argument("--sheet", type=int, default=0, help="Excel 工作表索引 (默认: 0)")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"错误: 文件不存在 - {input_path}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(input_path)[1].lower()
    output_path = args.output or os.path.splitext(input_path)[0] + ".csv"

    print(f"[convert] {input_path} → {output_path}", file=sys.stderr)

    try:
        if ext in (".xlsx",):
            convert_xlsx(input_path, output_path, sheet=args.sheet)
        elif ext in (".xls",):
            convert_xls(input_path, output_path)
        elif ext in (".tsv", ".tab", ".txt"):
            convert_txt(input_path, output_path)
        elif ext in (".csv",):
            if input_path == output_path:
                print(f"  [OK] 已是 CSV 格式，无需转换", file=sys.stderr)
            else:
                convert_csv(input_path, output_path)
        else:
            print(f"错误: 不支持的格式 {ext}，支持: .xlsx .xls .tsv .txt .csv", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"错误: 转换失败 - {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  [OK] 转换完成: {output_path}", file=sys.stderr)
    _preview_csv(output_path)
    print(output_path)


if __name__ == "__main__":
    main()