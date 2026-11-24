# -*- coding: utf-8 -*-
"""
模块3：⚙️ 可行性检测
检测：研究方法合理性、样本量充足性、时间线现实性、人力/资源匹配度
跨平台支持：Windows / Linux / macOS / HarmonyOS NEXT（鸿蒙）
"""
import sys, os, json, re

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass
# 鸿蒙(HarmonyOS)/Linux/macOS 终端默认UTF-8，无需特殊设置


def detect_feasibility_issues(text, filepath=''):
    """执行可行性检测"""
    issues = []
    score = 100
    details_parts = []
    
    # ========== 1. 研究方法识别与评估 ==========
    method_keywords = {
        '文献研究法': ['文献', '资料收集', '综述', '梳理'],
        '问卷调查法': ['问卷', '调查', '量表', '李克特'],
        '实验研究法': ['实验组', '对照组', '前测', '后测', '干预'],
        '行动研究法': ['行动研究', '计划-行动-观察-反思', '循环'],
        '案例研究法': ['案例', '个案', '深度访谈'],
        '数理统计法': ['SPSS', '相关分析', '回归分析', 't检验', '方差分析', '显著性'],
        '比较研究法': ['对比', '比较', '差异分析'],
        '观察法': ['观察', '记录表', '行为观察'],
    }
    
    methods_found = {}
    for method, keywords in method_keywords.items():
        count = sum(len(re.findall(kw, text)) for kw in keywords)
        if count > 0:
            methods_found[method] = count
    
    details_parts.append(f"**研究方法识别**：")
    if methods_found:
        for method, count in sorted(methods_found.items(), key=lambda x: -x[1]):
            details_parts.append(f"- ✅ {method}（提及{count}次）")
    else:
        issues.append({
            "level": "warning",
            "msg": "未明确识别到具体的研究方法，学术论文应明确说明研究方法",
            "location": "全文"
        })
        score -= 10
    
    # 方法数量合理性
    method_count = len(methods_found)
    if method_count == 1:
        details_parts.append("- ℹ️ 仅使用一种方法，确认是否足够支撑研究结论")
    elif method_count >= 5:
        issues.append({
            "level": "warning",
            "msg": f"同时使用{method_count}种研究方法，需确认每种都有实质性运用（非罗列凑数）",
            "location": "方法论部分"
        })
        score -= 5
    
    # ========== 2. 样本量评估 ==========
    sample_matches = re.findall(r'(?:样本|被试|调查对象|研究对象|参与)(?:量|数|为是)?[：:]\s*(\d+)', text)
    if not sample_matches:
        sample_matches = re.findall(r'(\d+)\s*(?:名?学生|名?教师|名?人|个?样本|例?被试)\b', text)
    
    if sample_matches:
        sample_size = max(int(s) for s in sample_matches)  # 取最大声明的样本量
        details_parts.append(f"\n**样本量评估**：声明最大样本量 = {sample_size}")
        
        # 基于方法的最低样本量建议
        if '问卷调查法' in methods_found or '数理统计法' in methods_found:
            if sample_size < 30:
                issues.append({
                    "level": "critical",
                    "msg": f"样本量仅{sample_size}，使用统计分析通常要求n≥30（大样本定律）",
                    "location": "研究设计部分"
                })
                score -= 15
            elif sample_size < 100:
                issues.append({
                    "level": "info",
                    "msg": f"样本量为{sample_size}，如做推广性结论建议扩大到100+",
                    "location": "研究设计部分"
                })
        
        if '实验研究法' in methods_found:
            if sample_size < 20:
                issues.append({
                    "level": "warning",
                    "msg": f"实验研究样本量{sample_size}偏小，每组至少10-15人才能保证统计效力",
                    "location": "实验设计部分"
                })
                score -= 8
    else:
        if any(m in methods_found for m in ['问卷调查法', '实验研究法', '数理统计法']):
            issues.append({
                "level": "warning",
                "msg": "使用了需要样本的研究方法但未明确声明样本量",
                "location": "研究方法部分"
            })
            score -= 10
    
    # ========== 3. 时间线评估 ==========
    time_patterns = [
        (r'(?:历时|持续|历时|研究周期|项目周期)[为：:]?\s*(\d+)\s*(个月?|周|年)', "总时长"),
        (r'(\d{4})\s*年?\s*(\d{1,2})?\s*月?\s*(?:至|—|-|~|～)\s*(\d{4})\s*年?\s*(\d{1,2})?\s*月?', "起止时间"),
        (r'(?:第[一二三四]阶段|阶段[一二三四]|Phase\s*\d)[^。\n]{0,50}(\d+)\s*(个月?|周)', "阶段时长"),
    ]
    
    timeline_info = []
    for pattern, label in time_patterns:
        matches = re.finditer(pattern, text)
        for m in matches:
            timeline_info.append((label, m.group(), m.start()))
    
    if timeline_info:
        details_parts.append(f"\n**时间线信息**（共{len(timeline_info)}条）：")
        for label, val, _ in timeline_info[:8]:
            details_parts.append(f"- [{label}] {val}")
        
        # 检查时间合理性
        for label, val, pos in timeline_info:
            month_match = re.search(r'(\d+)\s*(个月?)', val)
            if month_match:
                months = int(month_match.group(1))
                if months > 36 and '年' not in val:
                    issues.append({
                        "level": "warning",
                        "msg": f"声明周期{months}个月（{months//12}年有余），确认是否有足够资源支撑",
                        "location": f"时间线部分"
                    })
                    score -= 5
                elif months < 2 and '课题' in text:
                    issues.append({
                        "level": "warning",
                        "msg": f"周期仅{months}个月，对于课题研究可能过短",
                        "location": f"时间线部分"
                    })
                    score -= 5
    else:
        if '课题' in text or '研究计划' in text:
            issues.append({
                "level": "info",
                "msg": "未找到明确的时间规划/研究周期说明",
                "location": "全文"
            })
    
    # ========== 4. 资源匹配度粗检 ==========
    resource_indicators = {
        '经费': bool(re.search(r'(经费|预算|资金|资助|基金|项目经费)[^。]{0,30}', text)),
        '人员': bool(re.search(r'(课题组|团队|成员|分工|负责人)[^。]{0,30}', text)),
        '设备/场地': bool(re.search(r'(场地|实验室|器材|设备|仪器|教室|场馆)[^。]{0,30}', text)),
        '理论支持': bool(re.search(r'(理论依据|理论基础|理论框架|文献基础)[^。]{0,30}', text)),
    }
    
    has_resources = sum(resource_indicators.values())
    details_parts.append(f"\n**资源保障检查**：")
    for name, present in resource_indicators.items():
        status = "✅" if present else "⚠️ 未提及"
        details_parts.append(f"- {name}: {status}")
    
    if has_resources <= 1 and len(text) > 2000:
        issues.append({
            "level": "info",
            "msg": "资源保障条件描述不足，审稿人通常会关注研究的可行性支撑",
            "location": "保障条件/可行性分析部分"
        })
    
    # ========== 5. 逻辑链完整性 ==========
    # 检查是否有：问题→方法→数据→结果→结论 的基本链条
    chain_keywords = {
        '问题提出': ['问题', '背景', '现状', '不足', '亟待'],
        '研究目的': ['目的', '目标', '旨在', '为了'],
        '研究方法': list(set(kw for kws in method_keywords.values() for kw in kws)),
        '研究结果': ['结果', '表明', '发现', '显示', '数据'],
        '结论': ['结论', '启示', '建议', '对策', '展望'],
    }
    
    missing_links = []
    for link_name, kwds in chain_keywords.items():
        if not any(re.search(kw, text) for kw in kwds):
            missing_links.append(link_name)
    
    if missing_links:
        issues.append({
            "level": "warning",
            "msg": f"论文逻辑链可能不完整，缺少：{'、'.join(missing_links)}",
            "location": "全文结构"
        })
        score -= 5 * len(missing_links)
    
    score = max(0, min(100, score))
    
    return {
        "error": None,
        "score": score,
        "issues": issues,
        "details": '\n'.join(details_parts),
        "methods_found": methods_found,
        "resource_check": resource_indicators,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='可行性检测')
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
    
    result = detect_feasibility_issues(text, args.input)
    
    out_path = os.path.join(args.output, 'feasibility_check_result.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 可行性检测完成：{result['score']}分，发现{len(result['issues'])}项问题")


if __name__ == '__main__':
    main()
