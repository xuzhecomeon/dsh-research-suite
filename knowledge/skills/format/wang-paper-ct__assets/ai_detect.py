# -*- coding: utf-8 -*-
"""
模块5：🤖 AI生成痕迹检测（核心模块）
检测：段落均匀度、空洞语言、公式化过渡、虚构引用、术语不一致、表面华丽内容空泛
跨平台支持：Windows / Linux / macOS / HarmonyOS NEXT（鸿蒙）
"""
import sys, os, json, re
import statistics
from collections import Counter

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass
# 鸿蒙(HarmonyOS)/Linux/macOS 终端默认UTF-8，无需特殊设置


# ========== AI特征库 ==========

# AI高频"废话词"（出现频率显著高于人类写作）
AI_FILLER_WORDS = [
    "值得注意的是", "毋庸置疑", "综上所述", "不言而喻",
    "众所周知", "毫无疑问", "显而易见", "不可否认",
    "在一定程度上", "从某种意义上说", "可以说",
    "具有十分重要的意义", "发挥着重要作用", "提供了有力支撑",
    "值得关注的是", "需要指出的是", "应当看到",
    "不仅...而且...", "一方面...另一方面...",
    "首先...其次...最后...", "第一...第二...第三...",
    "综上所述", "总而言之", "由此可见",
]

# AI常见公式化结尾
AI_ENDINGS = [
    "具有重要意义", "值得进一步研究", "为后续研究提供参考",
    "具有一定的理论和实践价值", "有助于推动...的发展",
    "为...提供了新的视角和思路", "丰富了...的理论体系",
    "对于...具有重要的启示意义", "展现了广阔的应用前景",
]

# AI典型过渡句模板
AI_TRANSITIONS = [
    r'基于(?:上述|以上|前面)(?:分析|讨论|研究|论述)',
    r'(?:通过|经过)(?:上述|以上|前文)(?:分析|探讨|研究)',
    r'(?:具体)?(?:而言|来说|而论)',
    r'(?:在此基础上)?(?:进一步|进而|随后)',
    r'(?:此外|另外|同时)(?:，?值得?(?:一提|注意|强调)的是?)',
    r'(?:总之|综上|概括)(?:而言|来说)',
]


def detect_ai_issues(text, filepath=''):
    """执行AI痕迹检测——这是最核心的检测维度"""
    issues = []
    score = 100  # 起始满分，发现AI痕迹扣分
    details_parts = []
    
    lines = text.split('\n')
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
    short_paras = [p for p in paragraphs if len(p) < 50]
    
    # 权重配置
    STRUCTURE_WEIGHT = 25   # 结构层面
    LANGUAGE_WEIGHT = 25    # 语言层面
    CONTENT_WEIGHT = 30     # 内容层面
    TERMINOLOGY_WEIGHT = 20 # 术语层面
    
    struct_score = 100
    lang_score = 100
    content_score = 100
    term_score = 100
    
    # ================================================================
    # 一、结构层面检测
    # ================================================================
    details_parts.append("## 一、结构层面分析\n")
    
    # 1.1 段落长度均匀性
    if len(paragraphs) >= 6:
        para_lengths = [len(re.sub(r'\s', '', p)) for p in paragraphs]
        mean_len = statistics.mean(para_lengths)
        std_len = statistics.stdev(para_lengths)
        cv = std_len / mean_len if mean_len > 0 else 0
        
        details_parts.append(f"**段落长度统计**：")
        details_parts.append(f"- 段落数：{len(paragraphs)}")
        details_parts.append(f"- 平均长度：{mean_len:.0f} 字符")
        details_parts.append(f"- 标准差：{std_len:.1f}")
        details_parts.append(f"- 变异系数(CV)：{cv:.3f}")
        
        if cv < 0.20:
            issues.append({
                "level": "critical",
                "msg": f"段落长度极度均匀（CV={cv:.2f}），人工写作CV通常在0.4-0.8之间。AI生成的文本段落往往过于整齐",
                "location": "全文"
            })
            struct_score -= 40
        elif cv < 0.35:
            issues.append({
                "level": "warning",
                "msg": f"段落长度较为均匀（CV={cv:.2f}），略显机械",
                "location": "全文"
            })
            struct_score -= 15
        else:
            details_parts.append(f"- ✅ 段落长度变化自然（CV={cv:.2f}）")
    else:
        details_parts.append(f"- 段落数不足（{len(paragraphs)}段），跳过均匀性检测")
    
    # 1.2 标题/小节结构模式化
    section_patterns = [
        (r'^[一二三四五六七八九十]+、', "中文数字标题"),
        (r'^\d+\.', "阿拉伯数字标题"),
        (r'^（[一二三四五六七八九十]+）', "括号中文标题"),
        (r'^\d+\s+', "空格数字标题"),
    ]
    
    section_types = []
    for line in lines:
        stripped = line.strip()
        for pattern, name in section_patterns:
            if re.match(pattern, stripped):
                section_types.append(name)
                break
    
    if len(section_types) >= 3:
        type_counts = Counter(section_types)
        dominant_type = type_counts.most_common(1)[0]
        ratio = dominant_type[1] / len(section_types)
        
        if ratio > 0.95 and len(section_types) >= 5:
            details_parts.append(f"\n**标题结构**：{dominant_type[0]} 占 {ratio*100:.0f}%（{len(section_types)}个标题全部同类型）")
            issues.append({
                "level": "info",
                "msg": f"所有{len(section_types)}个小节标题使用完全相同的格式，略显模板化",
                "location": "全文结构"
            })
            struct_score -= 5
    
    # 1.3 "首先...其次...最后..." 连续使用检测
    first_next_last = re.findall(r'(?:首先|第一)[^。]{0,30}(?:其次|第二)[^。]{0,30}(?:最后|第三)', text)
    if first_next_last:
        issues.append({
            "level": "warning",
            "msg": f"发现「首先→其次→最后」式枚举结构（共{len(first_next_last)}处），这是AI最常用的列举模式",
            "location": "全文"
        })
        struct_score -= 10
    
    # ================================================================
    # 二、语言层面检测
    # ================================================================
    details_parts.append("\n## 二、语言层面分析\n")
    
    filler_count = 0
    filler_examples = []
    
    for filler in AI_FILLER_WORDS:
        count = text.count(filler)
        if count > 0:
            filler_count += count
            if len(filler_examples) < 5:
                # 找到上下文
                pos = text.index(filler) if filler in text else -1
                if pos >= 0:
                    context = text[max(0,pos-15):pos+len(filler)+15].replace('\n', ' ')
                    filler_examples.append(f"「{context}」")
    
    total_chars = len(re.sub(r'\s', '', text))
    filler_rate = (filler_count * sum(len(f) for f in AI_FILLER_WORDS)) / max(total_chars, 1) * 100
    
    details_parts.append(f"**AI填充词统计**：")
    details_parts.append(f"- 命中次数：{filler_count} 次")
    details_parts.append(f"- 文本占比：{filler_rate:.2f}%")
    
    if filler_count >= 8:
        issues.append({
            "level": "critical",
            "msg": f"AI填充词出现{filler_count}次（过多），包括：{'; '.join(filler_examples[:4])}",
            "location": "全文"
        })
        lang_score -= 30
    elif filler_count >= 4:
        issues.append({
            "level": "warning",
            "msg": f"AI填充词出现{filler_count}次，建议替换为更具体的表述",
            "location": "全文"
        })
        lang_score -= 15
    elif filler_count > 0:
        details_parts.append(f"- ⚠️ 少量填充词（{filler_count}次），影响较小")
    
    # 形容词密度检测
    adj_pattern = re.compile(r'(?:的|地)\s*(?:重要|关键|核心|显著|明显|有效|积极|深刻|广泛|全面|深入|系统|充分|必要)')
    adj_matches = list(adj_pattern.finditer(text))
    adj_density = len(adj_matches) / max(total_chars // 100, 1)
    
    details_parts.append(f"\n**形容词密度**：每100字符约{adj_density:.2f}个高阶形容词")
    if adj_density > 1.5:
        issues.append({
            "level": "warning",
            "msg": f"形容词堆砌严重（密度={adj_density:.2f}），典型的AI「华丽但空泛」特征",
            "location": "全文"
        })
        lang_score -= 10
    
    # 公式化过渡句检测
    transition_count = 0
    for pattern in AI_TRANSITIONS:
        matches = list(re.finditer(pattern, text))
        transition_count += len(matches)
    
    if transition_count >= 5:
        issues.append({
            "level": "warning",
            "msg": f"发现{transition_count}处公式化过渡句，AI常用此类模板化衔接",
            "location": "全文"
        })
        lang_score -= 10
    elif transition_count > 0:
        details_parts.append(f"- 过渡句：{transition_count} 处（正常范围）")
    
    # ================================================================
    # 三、内容层面检测
    # ================================================================
    details_parts.append("\n## 三、内容层面分析\n")
    
    # 3.1 具体细节缺失检测
    # 人类写作通常包含：具体人名、地名、机构名、日期、具体数据点
    concrete_details = {
        '具体人名': len(re.findall(r'[\u4e00-\u9fff]{2,4}(?:教授|老师|研究员|学者|先生|女士)', text)),
        '具体地名': len(re.findall(r'[\u4e00-\u9fff]*(?:省|市|县|旗|区|镇|乡|村|学校|中学|小学|大学|学院)', text)),
        '具体日期': len(re.findall(r'(?:19|20)\d{2}[年\-/]\d{1,2}[月\-/]\d{1,2}', text)),
        '具体机构': len(re.findall(r'[\u4e00-\u9fff]*(?:大学|学院|中学|小学|研究院|研究所|中心|教研室)', text)),
        '具体数字+单位': len(re.findall(r'\d+\s*(?:人|名|例|份|所|校|组|班|课时|分钟|平方米|千米|公斤|万元)', text)),
    }
    
    total_concrete = sum(concrete_details.values())
    detail_ratio = total_concrete / max(total_chars // 200, 1)  # 每200字的具体细节数
    
    details_parts.append(f"**具体细节含量**：")
    for name, count in concrete_details.items():
        details_parts.append(f"- {name}: {count} 处")
    details_parts.append(f"- 合计：{total_concrete} 处 | 密度：{detail_ratio:.1f}/200字")
    
    if detail_ratio < 0.5 and total_chars > 1500:
        issues.append({
            "level": "critical",
            "msg": f"论文缺乏具体细节（仅{total_concrete}处具体信息）。AI生成文本的典型特征是「正确但空洞」——语法完美但缺少真实世界的具体信息",
            "location": "全文"
        })
        content_score -= 35
    elif detail_ratio < 1.0:
        issues.append({
            "level": "warning",
            "msg": f"具体细节偏少（{total_concrete}处），建议增加具体的人名、地名、时间、数据等",
            "location": "全文"
        })
        content_score -= 15
    
    # 3.2 公式化结尾检测
    ending_hits = []
    for ending in AI_ENDINGS:
        if ending in text:
            count = text.count(ending)
            ending_hits.append((ending, count))
    
    if ending_hits:
        details_parts.append(f"\n**公式化结尾**：")
        for ending, count in ending_hits:
            details_parts.append(f"- 「{ending}」×{count}次")
        
        total_endings = sum(c for _, c in ending_hits)
        if total_endings >= 3:
            issues.append({
                "level": "warning",
                "msg": f"结论部分使用了{total_endings}个公式化套话，建议改为具体的结论陈述",
                "location": "结论部分"
            })
            content_score -= 15
    
    # 3.3 数据精确度异常检测
    precise_data = re.findall(r'\d+\.\d{2,}%', text)
    if precise_data:
        details_parts.append(f"\n**高精度百分比**：{precise_data}")
        if len(precise_data) > 3:
            issues.append({
                "level": "warning",
                "msg": f"多个高精度百分比数据（如{precise_data[:3]}），AI常编造看似精确的虚假数据",
                "location": "数据分析部分"
            })
            content_score -= 10
    
    # ================================================================
    # 四、术语一致性检测
    # ================================================================
    details_parts.append("\n## 四、术语一致性分析\n")
    
    # 提取文中可能的核心概念（简单启发式：高频名词短语）
    # 这里用更实用的方法：检查已知领域术语的一致性
    term_groups = {}
    
    # 体育学常见近义词组
    synonym_groups = [
        ["气排球", "轻排球", "软式排球"],
        ["学生", "被试", "受试者", "研究对象", "参与者"],
        ["教师", "老师", "教练员", "指导者"],
        ["教学", "授课", "课堂教学", "课程教学"],
        ["训练", "练习", "体育锻炼", "体育活动"],
        ["学校", "院校", "办学机构"],
    ]
    
    inconsistent_terms = []
    for group in synonym_groups:
        found_in_group = [(term, text.count(term)) for term in group if text.count(term) > 0]
        if len(found_in_group) >= 2:
            term_groups[group[0]] = found_in_group
            inconsistent_terms.append(group[0])
    
    if inconsistent_terms:
        details_parts.append(f"**术语不一致警告**：")
        for key, terms in term_groups.items():
            term_str = '、'.join([f'{t}({c}次)' for t, c in terms])
            details_parts.append(f"- [{key}] 同一概念用了不同说法：{term_str}")
        
        issues.append({
            "level": "warning",
            "msg": f"术语使用不一致（{len(inconsistent_terms)}组概念混用），同一概念应统一术语",
            "location": "全文"
        })
        term_score -= 10 * min(len(inconsistent_terms), 3)
    
    # ================================================================
    # 综合评分
    # ================================================================
    weighted_ai_score = (
        struct_score * STRUCTURE_WEIGHT +
        lang_score * LANGUAGE_WEIGHT +
        content_score * CONTENT_WEIGHT +
        term_score * TERMINOLOGY_WEIGHT
    ) / 100
    
    # 转换为0-100分制（score越高=越像人类写作）
    final_score = round(weighted_ai_score, 1)
    final_score = max(0, min(100, final_score))
    
    details_parts.append(f"\n## AI检测结果汇总")
    details_parts.append(f"| 维度 | 得分 | 权重 | 加权得分 |")
    details_parts.append(f"|------|------|------|----------|")
    details_parts.append(f"| 结构层面 | {struct_score} | {STRUCTURE_WEIGHT}% | {struct_score*STRUCTURE_WEIGHT/100:.1f} |")
    details_parts.append(f"| 语言层面 | {lang_score} | {LANGUAGE_WEIGHT}% | {lang_score*LANGUAGE_WEIGHT/100:.1f} |")
    details_parts.append(f"| 内容层面 | {content_score} | {CONTENT_WEIGHT}% | {content_score*CONTENT_WEIGHT/100:.1f} |")
    details_parts.append(f"| 术语层面 | {term_score} | {TERMINOLOGY_WEIGHT}% | {term_score*TERMINOLOGY_WEIGHT/100:.1f} |")
    details_parts.append(f"| **综合** | **{final_score}** | 100% | **{final_score}** |")
    
    # 等级判断
    if final_score >= 80:
        ai_verdict = "✅ 低AI痕迹 —— 文本具有较强的人类写作特征"
    elif final_score >= 60:
        ai_verdict = "🟡 中等AI痕迹 —— 部分段落的表达方式较为模式化，建议重点改写"
    elif final_score >= 40:
        ai_verdict = "🔴 明显AI痕迹 —— 大量使用AI典型表达模式，强烈建议大幅改写"
    else:
        ai_verdict = "❌ 高度疑似AI生成 —— 几乎完全符合AI输出特征，需彻底重写"
    
    details_parts.append(f"\n> **判定：{ai_verdict}**")
    
    return {
        "error": None,
        "score": final_score,
        "issues": issues,
        "details": '\n'.join(details_parts),
        "sub_scores": {
            "structure": struct_score,
            "language": lang_score,
            "content": content_score,
            "terminology": term_score,
        },
        "verdict": ai_verdict,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='AI痕迹检测')
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
    
    result = detect_ai_issues(text, args.input)
    
    out_path = os.path.join(args.output, 'ai_detect_result.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ AI痕迹检测完成：{result['score']}分 | {result['verdict']}")


if __name__ == '__main__':
    main()
