# -*- coding: utf-8 -*-
"""
模块7：🎯 期刊适配检测
检测：选题与期刊方向匹配度、字数合规、级别对等性
跨平台支持：Windows / Linux / macOS / HarmonyOS NEXT（鸿蒙）
"""
import sys, os, json, re

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass
# 鸿蒙(HarmonyOS)/Linux/macOS 终端默认UTF-8，无需特殊设置


# 常见中文期刊分类参考（部分）
JOURNAL_CATEGORIES = {
    "体育类": {
        "核心期刊": ["体育科学", "中国体育科技", "体育学刊", "体育与科学", "北京体育大学学报", "上海体育学院学报", "武汉体育学院学报", "天津体育学院学报", "西安体育学院学报", "成都体育学院学报"],
        "国家级/省级": ["体育教学", "体育师友", "当代体育科技", "体育文化导刊", "青少年体育"],
        "关键词": ['体育', '运动', '训练', '教学', '比赛', '竞技', '健身', '健康', '足球', '篮球', '排球', '气排球', '田径', '游泳'],
        "建议字数": (3000, 8000),
    },
    "教育类": {
        "核心期刊": ["教育研究", "课程·教材·教法", "中国教育学刊", "教育发展研究", "教育理论与实践"],
        "国家级/省级": ["中国教育报", "教育探索", "基础教育", "教学与管理", "班主任之友"],
        "关键词": ['教育', '教学', '课程', '学生', '教师', '学校', '课堂', '学习', '德育', '管理'],
        "建议字数": (3000, 8000),
    },
    "综合类": {
        "核心期刊": [],
        "国家级/省级": [],
        "关键词": [],
        "建议字数": (2000, 10000),
    }
}


def detect_journal_fit_issues(text, filepath=''):
    """执行期刊适配检测"""
    issues = []
    score = 80  # 起始80分（因为不知道目标期刊，给基础分）
    details_parts = []
    
    total_chars = len(re.sub(r'\s', '', text))
    
    # ========== 1. 领域识别 ==========
    detected_fields = []
    field_scores = {}
    
    for category, info in JOURNAL_CATEGORIES.items():
        if not info["关键词"]:
            continue
        hits = sum(text.count(kw) for kw in info["关键词"])
        if hits > 0:
            field_scores[category] = hits
            detected_fields.append((category, hits))
    
    detected_fields.sort(key=lambda x: -x[1])
    
    details_parts.append(f"**领域识别**：")
    if detected_fields:
        for field, hits in detected_fields[:3]:
            bar = "█" * min(hits // 2, 20)
            details_parts.append(f"- {field}：{hits}次匹配 {bar}")
        
        primary_field = detected_fields[0][0]
        secondary = detected_fields[1][0] if len(detected_fields) > 1 else None
        
        details_parts.append(f"\n> 📌 主要领域：**{primary_field}**" + (f" | 次要领域：{secondary}" if secondary else ""))
    else:
        details_parts.append("- ⚠️ 未匹配到已知领域，可能是跨学科或冷门方向")
        primary_field = "未知"
    
    # ========== 2. 字数适配 ==========
    details_parts.append(f"\n**字数统计**：")
    details_parts.append(f"- 纯文字数：约 **{total_chars}** 字")
    
    if primary_field in JOURNAL_CATEGORIES and JOURNAL_CATEGORIES[primary_field]["建议字数"]:
        min_w, max_w = JOURNAL_CATEGORIES[primary_field]["建议字数"]
        details_parts.append(f"- {primary_field}类期刊建议字数：{min_w}-{max_w} 字")
        
        if total_chars < min_w:
            issues.append({
                "level": "warning",
                "msg": f"字数（{total_chars}）低于{primary_field}类期刊建议下限（{min_w}字），可能因篇幅不足被退稿",
                "location": "全文"
            })
            score -= 10
        elif total_chars > max_w:
            issues.append({
                "level": "info",
                "msg": f"字数（{total_chars}）超过{primary_field}类期刊建议上限（{max_w}字），确认目标期刊是否接受长文",
                "location": "全文"
            })
        else:
            details_parts.append(f"- ✅ 字数在合理范围内")
    else:
        if total_chars < 2000:
            issues.append({
                "level": "warning",
                "msg": f"字数仅{total_chars}，大多数正规期刊要求至少3000字",
                "location": "全文"
            })
            score -= 10
        elif total_chars > 15000:
            issues.append({
                "level": "info",
                "msg": f"字数达{total_chars}，可能需要拆分或确认目标期刊类型",
                "location": "全文"
            })
    
    # ========== 3. 论文类型识别 ==========
    type_indicators = {
        "综述/述评": ['综述', '述评', '进展', '现状', '回顾', '展望'],
        "实证研究": ['实验', '调查', '数据', '样本', '统计', '分析', '测量', '问卷'],
        "理论研究": ['理论', '框架', '模型', '机制', '原理', '建构'],
        "经验总结": ['实践', '经验', '做法', '体会', '探索', '尝试', '案例'],
        "方法学研究": ['方法', '工具', '量表', '信度', '效度', '开发'],
    }
    
    paper_type_scores = {}
    for ptype, keywords in type_indicators.items():
        score_hits = sum(text.count(kw) for kw in keywords)
        if score_hits > 0:
            paper_type_scores[ptype] = score_hits
    
    paper_type_scores = dict(sorted(paper_type_scores.items(), key=lambda x: -x[1]))
    
    details_parts.append(f"\n**论文类型识别**：")
    if paper_type_scores:
        for ptype, sc in list(paper_type_scores.items())[:3]:
            details_parts.append(f"- {ptype}（匹配度：{sc}）")
        primary_type = list(paper_type_scores.keys())[0]
    else:
        primary_type = "未明确"
        details_parts.append("- ⚠️ 论文类型不明确")
    
    # ========== 4. 级别适配建议 ==========
    details_parts.append(f"\n**级别适配建议**：")
    
    # 根据引用数量、方法论复杂度、创新性表述等粗略判断
    ref_count = len(re.findall(r'\[\d+\]', text))
    has_statistics = bool(re.search(r'(?:SPSS|t检验|方差|回归|相关|显著性|P<|p<)', text))
    has_innovation = bool(re.search(r'(?:创新|首创|首次|新(?:的?)(?:模式|方法|视角|框架|路径))', text))
    
    level_indicators = {
        "核心期刊候选": 0,
        "国家级期刊适合": 0,
        "省级期刊适合": 0,
    }
    
    if ref_count >= 15 and has_statistics:
        level_indicators["核心期刊候选"] += 2
    elif ref_count >= 8:
        level_indicators["国家级期刊适合"] += 2
    
    if has_innovation:
        level_indicators["核心期刊候选"] += 1
    
    if total_chars >= 5000:
        level_indicators["国家级期刊适合"] += 1
    elif total_chars >= 3000:
        level_indicators["省级期刊适合"] += 1
    
    best_level = max(level_indicators.items(), key=lambda x: x[1])
    
    if best_level[1] >= 2:
        details_parts.append(f"- 📌 建议投递级别：**{best_level[0]}**")
    else:
        details_parts.append(f"- 📌 当前特征不明显，建议根据目标期刊具体要求调整")
    
    # ========== 5. 结构完整性（针对期刊投稿） ==========
    journal_structure_items = {
        "标题": bool(text.split('\n')[0].strip() and 5 <= len(text.split('\n')[0].strip()) <= 50),
        "摘要": bool(re.search(r'摘要', text)),
        "关键词": bool(re.search(r'关键词', text)),
        "引言/前言": bool(re.search(r'(?:引言|前言|问题的提出|研究背景)', text)),
        "正文主体": len([l for l in text.split('\n') if len(l.strip()) > 30]) > 10,
        "结论": bool(re.search(r'(?:结论|小结|结语|讨论)', text)),
        "参考文献": bool(re.search(r'参考文献', text)),
    }
    
    missing_items = [k for k, v in journal_structure_items.items() if not v]
    
    details_parts.append(f"\n**期刊论文结构检查**：")
    for item, present in journal_structure_items.items():
        status = "✅" if present else "❌ 缺失"
        details_parts.append(f"- {item}: {status}")
    
    if missing_items:
        missing_str = "、".join(missing_items)
        issues.append({
            "level": "warning",
            "msg": f"期刊论文结构不完整，缺少：{missing_str}",
            "location": "全文结构"
        })
        score -= 5 * len(missing_items)
    
    # ========== 6. 中英文摘要配对检查 ==========
    has_cn_abstract = bool(re.search(r'摘要', text))
    has_en_abstract = bool(re.search(r'(?:Abstract|ABSTRACT)', text, re.IGNORECASE))
    
    details_parts.append(f"\n**中英文摘要**：中文{'✅' if has_cn_abstract else '❌'} | 英文{'✅' if has_en_abstract else '❌'}")
    
    if has_cn_abstract and not has_en_abstract:
        issues.append({
            "level": "info",
            "msg": "有中文摘要但无英文摘要，部分期刊要求中英文双语摘要",
            "location": "摘要部分"
        })
    
    score = max(0, min(100, score))
    
    return {
        "error": None,
        "score": score,
        "issues": issues,
        "details": '\n'.join(details_parts),
        "detected_field": primary_field,
        "paper_type": primary_type,
        "word_count": total_chars,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='期刊适配检测')
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
    
    result = detect_journal_fit_issues(text, args.input)
    
    out_path = os.path.join(args.output, 'journal_fit_result.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 期刊适配检测完成：{result['score']}分，发现{len(result['issues'])}项问题")


if __name__ == '__main__':
    main()
