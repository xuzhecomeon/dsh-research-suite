# -*- coding: utf-8 -*-
"""
模块2：🔎 内容真实性检测
检测：数据出处支撑、引用文献存在性标记、事实主张可验证性、数据前后一致性
跨平台支持：Windows / Linux / macOS / HarmonyOS NEXT（鸿蒙）
"""
import sys, os, json, re
from collections import defaultdict

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass
# 鸿蒙(HarmonyOS)/Linux/macOS 终端默认UTF-8，无需特殊设置


def detect_authenticity_issues(text, filepath=''):
    """执行内容真实性检测"""
    issues = []
    score = 100
    details_parts = []
    
    lines = text.split('\n')
    
    # ========== 1. 数据索引与交叉验证 ==========
    # 提取所有带数字的数据声明
    data_patterns = [
        (r'样本[量数]?[为是]?\s*(\d+)\s*(人|名|例|份|个|所|校|组|班)?', "样本量"),
        (r'(\d+)\s*(人|名|例|份|个|所|校|组|班|人次)?(?:参与|参加|受访|调查|测试|实验)', "参与规模"),
        (r'有效率?\s*(?:为|达|：)?\s*(\d+\.?\d*)%', "有效率"),
        (r'提高[了之]?\s*(\d+\.?\d*)%(?!\s*[-—])', "提升幅度"),
        (r'增长[了之]?\s*(\d+\.?\d*)%', "增长率"),
        (r'(\d+\.?\d*)%?(?:的?(?:学生|教师|受访者|被试))', "比例数据"),
        (r'(?:历时|持续|经过)\s*(\d+)\s*(个月?|周|年|天|课时)', "时间跨度"),
        (r'(\d+)\s*(所|个)?(?:学校|单位|机构)', "机构数量"),
        (r'P?[＜<]\s*0\.0(\d)|P?[＞>]\s*0\.0(\d)|(?:显著)(?:相关|差异|影响)', "统计显著性"),
    ]
    
    data_index = defaultdict(list)  # {数据类型: [(值, 位置描述, 行号)]}
    
    for i, line in enumerate(lines, 1):
        for pattern, label in data_patterns:
            for m in re.finditer(pattern, line):
                val = m.group(1) if m else ''
                loc_desc = line.strip()[:40]
                data_index[label].append((val, loc_desc, i))
    
    details_parts.append(f"**数据索引（共提取{sum(len(v) for v in data_index.values())}条）**：")
    for dtype, entries in sorted(data_index.items()):
        if len(entries) <= 3:
            for val, loc, ln in entries:
                details_parts.append(f"- [{dtype}] {val} → 第{ln}行「{loc}」")
        else:
            details_parts.append(f"- [{dtype}] 共{len(entries)}处，值分布：{[e[0] for e in entries]}")
        
        # 同一类型数据在不同位置值不一致
        if len(entries) > 1:
            unique_vals = set(e[0] for e in entries)
            if len(unique_vals) > 1:
                issues.append({
                    "level": "critical",
                    "msg": f"「{dtype}」前后不一致：同一指标出现了不同值 {unique_vals}",
                    "location": f"第{entries[0][2]}-{entries[-1][2]}行"
                })
                score -= 20
    
    # ========== 2. 引用文献真实性核验 ==========
    ref_section_match = re.search(r'参考文献[\s\S]*$', text)
    refs_found = []
    fake_indicators = 0
    
    if ref_section_match:
        ref_text = ref_section_match.group()
        # 匹配 [序号] 作者.题名[类型].刊名,年份,卷(期):页码.
        ref_pattern = re.compile(
            r'\[(\d+)\]\s*'           # 序号
            r'([^\]]+?)\s*\.'          # 作者
            r'\s*([^.]+?)\s*'          # 题名
            r'\[([JMCDRPABNK])\]\s*'   # 文献类型标识
            r'.*?'                     # 刊名/出版社等
            r'(19\d{2}|20\d{2})',      # 年份
            re.DOTALL
        )
        
        for m in ref_pattern.finditer(ref_text):
            ref_info = {
                "index": int(m.group(1)),
                "author": m.group(2).strip()[:30],
                "title": m.group(3).strip()[:50],
                "type": m.group(4),
                "year": m.group(5),
            }
            refs_found.append(ref_info)
            
            # 虚构引用识别规则
            author = ref_info["author"]
            
            # 规则A：作者名看起来像拼音但非常见学者
            if re.match(r'^[A-Za-z]{2,15}$', author) and len(author) < 4:
                fake_indicators += 1
            
            # 规则B：年份异常（未来年份或太早）
            year = int(ref_info["year"])
            if year > 2026:
                issues.append({
                    "level": "critical",
                    "msg": f"参考文献[{ref_info['index']}] 年份为{year}年（未来年份），疑似错误",
                    "location": f"参考文献[{ref_info['index']}]"
                })
                score -= 10
            elif year < 1980 and ref_info["type"] == 'J':
                # 早期期刊论文较少，标记待核实
                pass
            
            # 规则C：题名过于泛化
            generic_titles = ['研究', '分析', '探讨', '思考', '对策', '建议']
            title = ref_info["title"]
            if any(title.endswith(gt) or title.endswith(gt+'。') for gt in generic_titles):
                if len(title) < 8:
                    fake_indicators += 0.5
    
    details_parts.append(f"\n**引用文献核验**：")
    details_parts.append(f"- 检测到 {len(refs_found)} 条格式化参考文献")
    if fake_indicators > 0:
        details_parts.append(f"- ⚠️ {fake_indicators:.1f} 个虚构嫌疑指标")
    
    # ========== 3. 数据来源标注检查 ==========
    has_data_source = bool(re.search(r'(数据来源|资料来源|据.*?统计|根据.*?调查|来自|来源于|出自)', text))
    has_quote_mark = text.count('[') > 3 and ']' in text  # 有上标引用标记
    
    if not has_data_source and len(data_index) > 5:
        issues.append({
            "level": "warning",
            "msg": "文中包含多组数据但未明确标注数据来源",
            "location": "全文"
        })
        score -= 8
    
    # ========== 4. 夸大/绝对化表述检测 ==========
    absolute_patterns = [
        (r'(?:完全|绝对|100%|毫无|从未|所有|全部)(?:都|一致|认同|肯定|有效)', "绝对化表述"),
        (r'(?:首次|首创|开创性|填补空白|国内外领先|世界一流)', "夸大原创性"),
        (r'(?:重大突破|革命性|颠覆性|里程碑式)', "过度夸张"),
    ]
    
    for pattern, label in absolute_patterns:
        matches = list(re.finditer(pattern, text))
        if matches:
            for m in matches[:3]:  # 最多报告3例
                line_num = text[:m.start()].count('\n') + 1
                issues.append({
                    "level": "warning",
                    "msg": f"发现{label}：「{m.group()}」——编辑部通常要求有充分证据支持此类表述",
                    "location": f"第{line_num}行"
                })
            score -= min(5, len(matches) * 2)
    
    score = max(0, min(100, score))
    
    return {
        "error": None,
        "score": score,
        "issues": issues,
        "details": '\n'.join(details_parts),
        "data_index": {k: v for k, v in data_index.items()},
        "ref_count": len(refs_found),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='内容真实性检测')
    parser.add_argument('--input', '-i', required=True)
    parser.add_argument('--output', '-o', required=True)
    args = parser.parse_args()
    
    cache_file = os.path.join(args.output, '_content_cache.txt')
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        ext = os.path.splitext(args.input)[1].lower()
        if ext == '.docx':
            from docx import Document
            doc = Document(args.input)
            text = '\n'.join([p.text for p in doc.paragraphs])
        elif ext == '.pdf':
            import pdfplumber
            with pdfplumber.open(args.input) as pdf:
                text = '\n'.join([p.extract_text() for p in pdf.pages if p.extract_text()])
        else:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
    
    result = detect_authenticity_issues(text, args.input)
    
    out_path = os.path.join(args.output, 'authenticity_check_result.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 内容真实性检测完成：{result['score']}分，发现{len(result['issues'])}项问题")


if __name__ == '__main__':
    main()
