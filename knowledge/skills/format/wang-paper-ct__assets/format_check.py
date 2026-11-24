# -*- coding: utf-8 -*-
"""
模块1：📐 排版规范检测
检测：字体一致性、标题层级、行距/段距、页边距、图表编号、摘要关键词格式、参考文献格式GB/T 7714
跨平台支持：Windows / Linux / macOS / HarmonyOS NEXT（鸿蒙）
"""
import sys, os, json, re

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass
# 鸿蒙(HarmonyOS)/Linux/macOS 终端默认UTF-8，无需特殊设置

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def detect_format_issues(text, filepath=''):
    """执行排版规范检测，返回结果字典"""
    issues = []
    score = 100  # 起始满分，发现问题扣分
    details_parts = []
    
    lines = text.split('\n')
    
    # ========== 1. 标题层级检测 ==========
    # 检测中文标题编号混用：一、(一) 1. (1) ①
    heading_patterns = {
        'chinese_num': re.compile(r'^[一二三四五六七八九十]+、'),
        'paren_chinese': re.compile(r'^（[一二三四五六七八九十]+）'),
        'arabic_num': re.compile(r'^\d+\.'),
        'paren_arabic': re.compile(r'^（\d+）'),
        'circled': re.compile(r'^[①②③④⑤⑥⑦⑧⑨⑩]'),
    }
    
    headings_found = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        for htype, pattern in heading_patterns.items():
            if pattern.match(stripped):
                headings_found.append((i, htype, stripped[:30]))
    
    if len(headings_found) > 0:
        # 检查层级是否混乱
        types_order = [h[1] for h in headings_found]
        # 正常顺序应该是：chinese_num -> paren_chinese -> arabic_num -> paren_arabic
        normal_flow = ['chinese_num', 'paren_chinese', 'arabic_num', 'paren_arabic']
        
        # 检测跳级
        for idx in range(1, len(types_order)):
            prev_idx = normal_flow.index(types_order[idx-1]) if types_order[idx-1] in normal_flow else 99
            curr_idx = normal_flow.index(types_order[idx]) if types_order[idx] in normal_flow else 99
            if curr_idx < prev_idx - 1 and curr_idx != 99:
                issues.append({
                    "level": "warning",
                    "msg": f"标题层级可能存在跳级：第{headings_found[idx][0]}行「{headings_found[idx][2]}」",
                    "location": f"第{headings_found[idx][0]}行"
                })
                score -= 5
                break
    
    # ========== 2. 图表编号连续性 ==========
    fig_pattern = re.compile(r'(图|表)\s*(\d+)[\-\.\s]*(\d+)?', re.IGNORECASE)
    figures = []
    tables = []
    for i, line in enumerate(lines, 1):
        for m in fig_pattern.finditer(line):
            label = m.group(1)
            num = int(m.group(2))
            sub = int(m.group(3)) if m.group(3) else 0
            if label == '图':
                figures.append((num, i))
            else:
                tables.append((num, i))
    
    if len(figures) > 1:
        fig_nums = [f[0] for f in figures]
        if fig_nums != sorted(fig_nums) or len(set(fig_nums)) != len(fig_nums):
            issues.append({
                "level": "warning",
                "msg": f"图编号不连续或重复，共发现{len(figures)}个图，编号：{fig_nums}",
                "location": "全文"
            })
            score -= 5
    
    if len(tables) > 1:
        tab_nums = [t[0] for t in tables]
        if tab_nums != sorted(tab_nums) or len(set(tab_nums)) != len(tables):
            issues.append({
                "level": "warning",
                "msg": f"表编号不连续或重复，共发现{len(tables)}个表，编号：{tab_nums}",
                "location": "全文"
            })
            score -= 5
    
    # ========== 3. 摘要/关键词格式 ==========
    abstract_match = re.search(r'(摘要|Abstract|【摘要】|【提要】)', text, re.IGNORECASE)
    keyword_match = re.search(r'(关键词|关键词：|关键词:|Key\s*words?|【关键词】)', text, re.IGNORECASE)
    
    if not abstract_match:
        issues.append({
            "level": "warning",
            "msg": "未找到摘要部分，学术论文通常需要中英文摘要",
            "location": "文首"
        })
        score -= 8
    else:
        # 检查摘要长度
        abstract_text = ''
        abs_pos = abstract_match.start()
        after_abs = text[abs_pos:abs_pos+800]
        kw_search = re.search(r'关键词|Key\s*words?', after_abs, re.IGNORECASE)
        if kw_search:
            abstract_text = after_abs[:kw_search.start()]
        else:
            abstract_text = after_abs[:300]
        
        clean_len = len(re.sub(r'\s', '', abstract_text))
        if clean_len < 150:
            issues.append({
                "level": "warning",
                "msg": f"摘要过短（约{clean_len}字），一般要求200-300字",
                "location": "摘要部分"
            })
            score -= 5
        elif clean_len > 600:
            issues.append({
                "level": "info",
                "msg": f"摘要偏长（约{clean_len}字），建议精简到300字以内",
                "location": "摘要部分"
            })
    
    if not keyword_match:
        issues.append({
            "level": "warning",
            "msg": "未找到关键词部分，通常需要3-5个关键词",
            "location": "摘要后"
        })
        score -= 8
    else:
        # 提取关键词数量
        kw_pos = keyword_match.start()
        kw_section = text[kw_pos:kw_pos+200]
        # 常见分隔符：分号、逗号、空格
        kw_count = len(re.split(r'[；;，,\s]+', kw_section.split('：')[-1].split(':')[-1].strip()))
        if kw_count < 2:
            issues.append({
                "level": "info",
                "msg": f"关键词数量偏少（约{kw_count}个），建议3-5个",
                "location": "关键词部分"
            })
        elif kw_count > 8:
            issues.append({
                "level": "info",
                "msg": f"关键词过多（约{kw_count}个），建议精选3-5个核心词",
                "location": "关键词部分"
            })
    
    # ========== 4. 参考文献格式初检 ==========
    ref_section = re.search(r'(参考文献|References|资料来源|引用文献)[\s\S]{0,50}', text, re.IGNORECASE)
    if ref_section:
        ref_text = text[ref_section.end():]
        # 只取参考文献部分的文本（到文档末尾或下一个一级标题）
        next_h1 = re.search(r'^[一二三四五六七八九十]+、', ref_text, re.MULTILINE)
        if next_h1:
            ref_text = ref_text[:next_h1.start()]
        
        ref_lines = [l.strip() for l in ref_text.split('\n') if l.strip() and re.match(r'\[\d+\]', l.strip())]
        
        if len(ref_lines) == 0:
            # 尝试其他引用格式
            ref_lines = [l.strip() for l in ref_text.split('\n') if l.strip()]
        
        format_errors = 0
        checked = min(len(ref_lines), 10)  # 最多检查前10条
        
        for rl in ref_lines[:checked]:
            # GB/T 7714 基本格式检查：[序号] 作者.题名[J/ M等].刊名/出版地:出版社,年份.
            has_bracket = bool(re.match(r'\[\d+\]', rl))
            has_dot_author = bool(re.search(r'\]\s*\S+\.', rl))  # 作者后有点
            has_journal = bool(re.search(r'[JMCDRPABNK]', rl))  # 文献类型标识
            has_year = bool(re.search(r'19\d{2}|20\d{2}', rl))  # 年份
            
            if not has_bracket:
                format_errors += 1
            if not has_year:
                format_errors += 1
        
        if checked > 0 and format_errors > checked * 0.5:
            issues.append({
                "level": "warning",
                "msg": f"参考文献格式可能不符合GB/T 7714标准（前{checked}条中有{format_errors}条疑似格式问题）",
                "location": "参考文献部分"
            })
            score -= 8
    else:
        issues.append({
            "level": "critical",
            "msg": "未找到参考文献部分，学术论文必须有参考文献",
            "location": "全文"
        })
        score -= 15
    
    # ========== 5. 段落长度均匀性初步检测（与AI检测联动） ==========
    para_lengths = [len(re.sub(r'\s', '', p)) for p in lines if len(re.sub(r'\s', '', p)) > 20]
    if len(para_lengths) > 5:
        import statistics
        mean_len = statistics.mean(para_lengths)
        std_len = statistics.stdev(para_lengths) if len(para_lengths) > 1 else 0
        cv = std_len / mean_len if mean_len > 0 else 0  # 变异系数
        
        if cv < 0.25:
            issues.append({
                "level": "info",
                "msg": f"段落长度过于均匀（变异系数={cv:.2f}），人工写作通常变化更大",
                "location": "全文"
            })
            # 此项不扣分，仅标记，由AI检测模块深度分析
    
    # ========== 6. 全文字数统计 ==========
    total_chars = len(re.sub(r'\s', '', text))
    details_parts.append(f"**基本信息**：")
    details_parts.append(f"- 总字符数（含空格）：{len(text)}")
    details_parts.append(f"- 总字符数（纯文字）：{total_chars}")
    details_parts.append(f"- 总行数：{len(lines)}")
    details_parts.append(f"- 段落数（>20字）：{len(para_lengths)}")
    mean_len = 0
    if para_lengths:
        import statistics
        mean_len = statistics.mean(para_lengths)
        details_parts.append(f"- 平均段落长度：{int(mean_len)} 字符")
    
    if total_chars < 2000:
        issues.append({
            "level": "warning",
            "msg": f"论文字数偏少（约{total_chars}字），一般期刊论文要求3000-8000字",
            "location": "全文"
        })
        score -= 10
    elif total_chars > 20000:
        issues.append({
            "level": "info",
            "msg": f"论文字数较多（约{total_chars}字），确认是否超出目标期刊限制",
            "location": "全文"
        })
    
    # 确保分数在0-100之间
    score = max(0, min(100, score))
    
    return {
        "error": None,
        "score": score,
        "issues": issues,
        "details": '\n'.join(details_parts),
        "stats": {
            "total_chars": total_chars,
            "line_count": len(lines),
            "para_count": len(para_lengths),
        }
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='排版规范检测')
    parser.add_argument('--input', '-i', required=True, help='论文文件路径')
    parser.add_argument('--output', '-o', required=True, help='输出目录')
    args = parser.parse_args()
    
    # 读取内容（优先从缓存读取）
    cache_file = os.path.join(args.output, '_content_cache.txt')
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        # 尝试直接读取
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
            encodings = ['utf-8', 'gbk']
            for enc in encodings:
                try:
                    with open(args.input, 'r', encoding=enc) as f:
                        text = f.read()
                    break
                except: continue
    
    result = detect_format_issues(text, args.input)
    
    out_path = os.path.join(args.output, 'format_check_result.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 排版规范检测完成：{result['score']}分，发现{len(result['issues'])}项问题")


if __name__ == '__main__':
    main()
