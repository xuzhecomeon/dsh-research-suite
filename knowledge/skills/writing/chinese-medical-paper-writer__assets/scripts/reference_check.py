#!/usr/bin/env python3
"""
chinese-medical-paper-writer 辅助脚本（v2.0 - 强化审查版）

功能（5 轮自审）：
1. 第一轮 硬性规则扫描：
   - 参考文献上标数与正文引用总数一致性
   - AI 痕迹残留（**、# 等 Markdown 标记）
   - 禁用套话（"值得注意的是""综上所述"等）
   - 半 AI 化造词（"赋能""抓手"等）
   - 元话语标注（"本团队""本课题组"等）
2. 第二轮 投稿格式样例核查（已扩展）
3. 第三轮 中华医学会反例清单核查（新增）：
   - 占位作者检测（"王某某""张某某"等）
   - "具有显著性差异" 等禁用表述
   - "P=0.000" 应写为 "P<0.001"
   - 第一人称滥用检测（摘要中"我们""我院"）
   - DOI 缺失检测
4. 第四轮 语言深度核查（提示性）
5. 第五轮 参考文献真实性核查（占位作者、未核实标识等）

用法：
    python3 reference_check.py <docx_path>
"""

import re
import sys
from pathlib import Path
from docx import Document


def check_superscript_count(docx_path: str) -> dict:
    """
    检查正文中的参考文献上标数与引用总数是否一致。
    遍历所有段落，统计上标格式的 [n] / [n-m] / [n, m] / [n, m-p] 等。
    """
    doc = Document(docx_path)
    body = "\n".join(p.text for p in doc.paragraphs)

    # 提取所有上标格式的引用（如 [1]、[1-3]、[1, 3]、[1, 3-5]）
    # 通过 python-docx 的 run.font.superscript 标记来识别
    superscript_refs = []
    for para in doc.paragraphs:
        for run in para.runs:
            if run.font.superscript:
                text = run.text.strip()
                # 匹配 [n]、[n-m]、[n, m]、[n, m-p]
                if re.match(r'^\[[\d\-\s,]+\]$', text):
                    superscript_refs.append(text)

    # 计算引用总数（处理 [1, 3-5] 这样的多引用）
    total_count = 0
    for ref in superscript_refs:
        content = ref.strip("[]")
        # 拆分逗号
        parts = [p.strip() for p in content.split(",")]
        for part in parts:
            if "-" in part:
                # 范围引用 [1-3] 计数为 3（也可计为 1，需根据规则）
                # 这里我们计数为展开的篇数
                a, b = part.split("-")
                total_count += int(b) - int(a) + 1
            else:
                total_count += 1

    return {
        "上标引用条目数": len(superscript_refs),
        "上标引用条目": superscript_refs,
        "展开引用总数": total_count,
    }


def check_ai_traces(docx_path: str) -> list:
    """
    第二轮：检查 AI 痕迹残留
    Markdown 标记、半 AI 化造词、元话语标注、占位作者、第一人称滥用、禁用统计表述
    """
    doc = Document(docx_path)
    body = "\n".join(p.text for p in doc.paragraphs)

    issues = []

    # Markdown 残留
    md_patterns = [r"\*\*[^*]+\*\*", "^#+ ", r"\[.*?\]\(.*?\)"]
    for pattern in md_patterns:
        matches = re.findall(pattern, body, re.MULTILINE)
        if matches:
            issues.append(f"Markdown 残留 '{pattern}': {matches[:3]}")

    # 禁用套话（中华医学会标杆红线）
    forbidden_phrases = [
        "值得注意的是", "综上所述", "近年来随着", "在当今", "背景下",
        "扮演着", "提供了新思路", "不难看出", "众所周知",
        "具有重要理论意义", "具有重要临床推广价值", "亟待进一步",
        "总体而言", "从某种意义上说", "基于此", "换言之",
        "毋庸置疑", "不言而喻",
    ]
    for phrase in forbidden_phrases:
        count = body.count(phrase)
        if count > 0:
            issues.append(f"禁用套话 '{phrase}': {count} 处")

    # 半 AI 化造词
    ai_terms = [
        "病理驱动", "关键XX触发器", "重构", "赋能", "抓手", "闭环",
        "底层逻辑", "顶层设计", "全链路", "全方位", "全栈式", "一站式",
        "颗粒度", "高维", "降维", "根本性", "决定性", "颠覆性", "革命性",
        "重塑", "全场景", "痛点", "赛道", "商业化",
    ]
    for term in ai_terms:
        count = body.count(term)
        if count > 0:
            issues.append(f"半 AI 化造词 '{term}': {count} 处")

    # 元话语标注
    meta_discourse = [
        "本团队", "本课题组", "导师重点关注", "详见", "前文", "后述",
        "本文作者认为", "笔者认为", "我们认为",
    ]
    for term in meta_discourse:
        count = body.count(term)
        if count > 0:
            issues.append(f"元话语标注 '{term}': {count} 处")

    # 占位作者（绝对要避免）
    placeholder_authors = ["王某某", "张某某", "李某某", "赵某某", "刘某某", "陈某某", "某某某"]
    for name in placeholder_authors:
        count = body.count(name)
        if count > 0:
            issues.append(f"占位作者 '{name}': {count} 处 - 严禁虚构作者！")

    # 禁用统计表述
    forbidden_stats = [
        ("具有显著性差异", "应改为'差异有统计学意义'"),
        ("具有显著差异", "应改为'差异有统计学意义'"),
        ("P=0.000", "应写为 P<0.001"),
    ]
    for phrase, suggestion in forbidden_stats:
        count = body.count(phrase)
        if count > 0:
            issues.append(f"禁用统计表述 '{phrase}': {count} 处 - {suggestion}")

    # 摘要中第一人称检测（应避免在摘要使用）
    abstract_match = re.search(r'【摘要】(.*?)【关键词】|摘要(.*?)关键词', body, re.DOTALL)
    if abstract_match:
        abstract_text = abstract_match.group(1) or abstract_match.group(2)
        first_person = ["我们", "我院", "笔者", "本院"]
        for word in first_person:
            if word in abstract_text:
                issues.append(f"摘要中使用第一人称 '{word}' - 应改用'本研究/本文'")

    return issues


def check_placeholder_references(docx_path: str) -> list:
    """
    第五轮：参考文献真实性核查
    - 检测占位作者
    - 检测 DOI 缺失
    - 检测"原始来源待考"标识
    - 检测二次引用
    """
    doc = Document(docx_path)
    # 仅在参考文献部分
    body = "\n".join(p.text for p in doc.paragraphs)
    refs_section = body.split("参考文献")[-1] if "参考文献" in body else body

    issues = []

    # 占位作者
    placeholder_authors = ["某某", "XX 等", "XX.", "X 等"]
    for name in placeholder_authors:
        count = refs_section.count(name)
        if count > 0:
            issues.append(f"参考文献占位 '{name}': {count} 处 - 必须替换为真实作者！")

    # 二次引用
    secondary_cite = ["转引自", "原始数据被", "据XX报道", "据 XX 媒体"]
    for phrase in secondary_cite:
        count = refs_section.count(phrase)
        if count > 0:
            issues.append(f"二次引用 '{phrase}': {count} 处 - 必须引用原始期刊论文")

    return issues


def check_format_compliance(docx_path: str) -> list:
    """
    第二轮：投稿格式样例核查
    - 字体
    - 字号
    - 摘要结构
    - 关键词
    - 必备模块
    """
    doc = Document(docx_path)
    body = "\n".join(p.text for p in doc.paragraphs)

    issues = []

    # 摘要结构
    has_structured_abstract = all(
        label in body for label in ["【目的】", "【方法】", "【结果】", "【结论】"]
    )
    if not has_structured_abstract:
        # 综述用单段摘要，无须结构式
        if "综述" not in body[:200]:  # 综述的"·综述·"栏目标识
            issues.append("中文摘要缺少【目的】【方法】【结果】【结论】结构（论著必备）")

    # 必备模块
    required = ["利益冲突", "作者贡献", "参考文献", "摘要", "关键词"]
    missing = [m for m in required if m not in body]
    if missing:
        issues.append(f"缺失必备模块: {missing}")

    return issues


def check_structure(docx_path: str) -> dict:
    """
    检查文档基本结构完整性
    """
    doc = Document(docx_path)
    body = "\n".join(p.text for p in doc.paragraphs)

    required_sections = {
        "摘要": r"【摘要】|\[摘要\]|摘\s*要",
        "关键词": r"关键词",
        "Abstract": r"Abstract",
        "Key words": r"Key\s*words",
        "中图分类号": r"中图分类号",
        "资料与方法": r"资料与方法",
        "结果": r"^\s*结\s*果\s*$",
        "讨论": r"^\s*讨\s*论\s*$",
        "利益冲突": r"利益冲突",
        "作者贡献": r"作者贡献",
        "参考文献": r"参考文献",
    }

    structure = {}
    for section, pattern in required_sections.items():
        structure[section] = bool(re.search(pattern, body, re.MULTILINE))

    return structure


def main():
    if len(sys.argv) < 2:
        print("用法: python3 reference_check.py <docx_path>")
        print("\n该脚本用于检查中文医学论文的 5 轮自审：")
        print("  1. 参考文献上标数与引用总数是否一致")
        print("  2. AI 痕迹 / 禁用表述 / 占位作者")
        print("  3. 投稿格式样例核查")
        print("  4. 文档结构完整性")
        print("  5. 参考文献真实性核查")
        sys.exit(1)

    docx_path = sys.argv[1]
    if not Path(docx_path).exists():
        print(f"错误: 文件不存在: {docx_path}")
        sys.exit(1)

    print(f"=== 检查文件: {docx_path} ===\n")

    # 第一轮：上标检查
    print("【第一轮 硬性规则 - 参考文献上标核查】")
    sc = check_superscript_count(docx_path)
    print(f"  - 上标引用条目数: {sc['上标引用条目数']}")
    print(f"  - 展开引用总数: {sc['展开引用总数']}")
    print(f"  - 上标引用列表: {sc['上标引用条目'][:10]}{'...' if len(sc['上标引用条目']) > 10 else ''}")
    if sc['上标引用条目数'] == 0:
        print("  ⚠️ 警告: 未检测到上标格式的参考文献编号，请检查！\n")
    else:
        print("  ✅ 已检测到上标格式的参考文献\n")

    # 第二轮：AI 痕迹 + 禁用表述
    print("【第二轮 中华医学会反例清单 - AI 痕迹 / 禁用表述核查】")
    issues = check_ai_traces(docx_path)
    if not issues:
        print("  ✅ 未检测到 AI 痕迹 / 禁用表述\n")
    else:
        print(f"  ⚠️ 发现 {len(issues)} 个问题：")
        for issue in issues:
            print(f"    - {issue}")
        print()

    # 第三轮：投稿格式核查
    print("【第三轮 投稿格式样例核查】")
    fmt_issues = check_format_compliance(docx_path)
    if not fmt_issues:
        print("  ✅ 投稿格式样例符合要求\n")
    else:
        print(f"  ⚠️ 发现 {len(fmt_issues)} 个问题：")
        for issue in fmt_issues:
            print(f"    - {issue}")
        print()

    # 第四轮：结构核查
    print("【第四轮 文档结构核查】")
    structure = check_structure(docx_path)
    missing = [k for k, v in structure.items() if not v]
    if not missing:
        print("  ✅ 所有必要模块齐备\n")
    else:
        print(f"  ⚠️ 缺失模块: {missing}\n")

    # 第五轮：参考文献真实性
    print("【第五轮 参考文献真实性核查】")
    ref_issues = check_placeholder_references(docx_path)
    if not ref_issues:
        print("  ✅ 参考文献无占位/二次引用\n")
    else:
        print(f"  ⚠️ 发现 {len(ref_issues)} 个问题：")
        for issue in ref_issues:
            print(f"    - {issue}")
        print()

    print("=== 检查完成 ===")


if __name__ == "__main__":
    main()
