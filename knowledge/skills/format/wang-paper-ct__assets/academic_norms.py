# -*- coding: utf-8 -*-
"""
模块6：📋 学术规范检测
检测：抄袭/洗稿迹象、伦理合规性、参考文献完整性、基金/致谢披露
跨平台支持：Windows / Linux / macOS / HarmonyOS NEXT（鸿蒙）
"""
import sys, os, json, re

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass
# 鸿蒙(HarmonyOS)/Linux/macOS 终端默认UTF-8，无需特殊设置


def detect_academic_norms_issues(text, filepath=''):
    """执行学术规范检测"""
    issues = []
    score = 100
    details_parts = []
    
    lines = text.split('\n')
    
    # ========== 1. 引用完整性检测 ==========
    # 检查正文中的引用标记 [1][2] 等
    inline_citations = re.findall(r'\[\d+\]', text)
    ref_section_match = re.search(r'参考文献', text)
    
    details_parts.append(f"**引用标记统计**：")
    details_parts.append(f"- 正文引用标记数：{len(inline_citations)}")
    
    if len(inline_citations) > 0:
        max_cite_num = max(int(re.search(r'\d+', c).group()) for c in inline_citations)
        details_parts.append(f"- 最大引用序号：{max_cite_num}")
        
        # 检查引用是否集中在某些段落（堆砌嫌疑）
        cite_positions = [m.start() for m in re.finditer(r'\[\d+\]', text)]
        if len(cite_positions) >= 5:
            # 将文本分为4等份，检查分布
            chunk_size = len(text) // 4
            distribution = [0, 0, 0, 0]
            for pos in cite_positions:
                idx = min(int(pos / chunk_size), 3)
                distribution[idx] += 1
            
            max_chunk = max(distribution)
            total = sum(distribution)
            if max_chunk > total * 0.6 and total >= 5:
                issues.append({
                    "level": "warning",
                    "msg": f"引用标记分布不均，{max_chunk}/{total}集中在文本某一部分，可能存在引用堆砌",
                    "location": "全文"
                })
                score -= 8
    
    if not inline_citations and ref_section_match:
        issues.append({
            "level": "critical",
            "msg": "有参考文献列表但正文中无任何引用标记[1][2]...，文后引用必须与正文引用对应",
            "location": "全文"
        })
        score -= 20
    elif not inline_citations and not ref_section_match:
        issues.append({
            "level": "warning",
            "msg": "无任何引用和参考文献，学术论文通常需要文献支撑",
            "location": "全文"
        })
        score -= 15
    elif len(inline_citations) < 3 and len(text) > 3000:
        issues.append({
            "level": "info",
            "msg": f"仅{len(inline_citations)}处引用，对于长论文偏少",
            "location": "全文"
        })
    
    # ========== 2. 抄袭/洗稿迹象检测 ==========
    # 注意：这不是真正的查重，而是基于文本特征的初步筛查
    
    # 2.1 风格突变检测——如果不同段落风格差异极大
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
    if len(paragraphs) >= 8:
        # 简单的句长方差检测
        sentence_lengths = []
        for para in paragraphs:
            sentences = re.split(r'[。！？；]', para)
            sents = [len(s.strip()) for s in sentences if len(s.strip()) > 5]
            sentence_lengths.extend(sents)
        
        if len(sentence_lengths) >= 10:
            import statistics
            global_mean = statistics.mean(sentence_lengths)
            
            # 分段计算均值，看是否有段落偏离全局太多
            para_means = []
            for para in paragraphs[:min(len(paragraphs), 20)]:
                sentences = re.split(r'[。！？；]', para)
                sents = [len(s.strip()) for s in sentences if len(s.strip()) > 5]
                if sents:
                    para_means.append(statistics.mean(sents))
            
            if para_means:
                outliers = sum(1 for m in para_means if abs(m - global_mean) > global_mean * 1.5)
                outlier_ratio = outliers / len(para_means)
                
                if outlier_ratio > 0.3:
                    issues.append({
                        "level": "info",
                        "msg": f"{int(outlier_ratio*100)}%的段落句长明显偏离平均水平，可能存在拼接/复制痕迹",
                        "location": "全文"
                    })
    
    # 2.2 连续与原文高度相似的模式（超长连续相同词序列）
    # 这里用启发式：检查是否有异常长的连续无引用段落
    long_unreferenced = []
    current_para_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith('[['):  # 排除引用行
            if re.search(r'\[\d+\]', stripped):
                if i - current_para_start > 15:  # 超过15行无引用
                    long_unreferenced.append((current_para_start+1, i))
                current_para_start = i
    
    for start, end in long_unreferenced:
        span = end - start
        if span > 25:
            issues.append({
                "level": "warning",
                "msg": f"第{start}-{end}行（约{span}行）没有任何引用标记，大段无引用内容可能来自未标注来源",
                "location": f"第{start}-{end}行"
            })
            score -= 10
    
    # ========== 3. 基金/资助披露检测 ==========
    funding_patterns = [
        r'(?:基金|项目|课题)[^。]{0,30}(?:资助|支持|批准号|编号)',
        r'(?:National Natural Science|NSFC| humanities.*social.*science)',
        r'(?:项目编号|批准号|基金号)\s*[:：]\s*\w+',
    ]
    
    has_funding = any(re.search(p, text) for p in funding_patterns)
    
    details_parts.append(f"\n**基金/资助信息**：{'✅ 已找到' if has_funding else '⚠️ 未发现'}")
    
    if not has_funding:
        issues.append({
            "level": "info",
            "msg": "未发现基金项目信息。如有基金支持应注明（部分期刊要求）",
            "location": "首页/页脚/致谢"
        })
    
    # ========== 4. 致谢/作者信息检测 ==========
    has_acknowledgement = bool(re.search(r'(?:致谢|感谢|鸣谢|Acknowledg)', text, re.IGNORECASE))
    has_author_info = bool(re.search(r'(?:作者简介|作者单位|通讯作者|Email|e-mail)', text, re.IGNORECASE))
    
    details_parts.append(f"**致谢**：{'✅' if has_acknowledgement else '⚠️ 未发现'}")
    details_parts.append(f"**作者信息**：{'✅' if has_author_info else '⚠️ 未发现'}")
    
    # ========== 5. 利益冲突声明检测 ==========
    has_conflict_stmt = bool(re.search(
        r'(?:利益冲突|Conflict of Interest|无利益相关|作者声明.*无)',
        text, re.IGNORECASE
    ))
    
    if not has_conflict_stmt:
        details_parts.append("**利益冲突声明**：⚠️ 未发现（部分期刊要求）")
    else:
        details_parts.append("**利益冲突声明**：✅ 已找到")
    
    # ========== 6. 伦理审查声明检测（涉及人类受试者的研究） ==========
    human_subject_keywords = ['调查', '问卷', '访谈', '实验', '被试', '参与者', '学生', '教师']
    has_human_subjects = any(kw in text for kw in human_subject_keywords)
    has_ethics_stmt = bool(re.search(
        r'(?:伦理|Ethics|IRB|知情同意|informed consent|伦理委员会)',
        text, re.IGNORECASE
    ))
    
    if has_human_subjects and not has_ethics_stmt:
        issues.append({
            "level": "info",
            "msg": "研究涉及人类受试者但未发现伦理审查声明（部分期刊/学位论文要求）",
            "location": "方法部分或文末"
        })
    
    # ========== 7. 自引检测 ==========
    # 检查是否过度引用自己的文章
    author_name_match = re.search(r'作者[简介\s]*[：:]?\s*(\S{2,4})', text)
    # 这是一个简单版本，完整版需要知道作者姓名
    
    score = max(0, min(100, score))
    
    return {
        "error": None,
        "score": score,
        "issues": issues,
        "details": '\n'.join(details_parts),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='学术规范检测')
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
    
    result = detect_academic_norms_issues(text, args.input)
    
    out_path = os.path.join(args.output, 'academic_norms_result.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 学术规范检测完成：{result['score']}分，发现{len(result['issues'])}项问题")


if __name__ == '__main__':
    main()
