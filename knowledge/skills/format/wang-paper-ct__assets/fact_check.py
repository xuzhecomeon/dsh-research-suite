# -*- coding: utf-8 -*-
"""
模块4：🧠 内容真伪检测
检测：事实交叉验证、统计合理性、逻辑谬误识别、过度陈述检测
跨平台支持：Windows / Linux / macOS / HarmonyOS NEXT（鸿蒙）
"""
import sys, os, json, re

if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass
# 鸿蒙(HarmonyOS)/Linux/macOS 终端默认UTF-8，无需特殊设置


# 常见事实知识库（体育/教育/学术领域）
FACT_BASE = {
    # 气排球相关
    "气排球起源": {
        "fact": "气排球起源于1984年中国内蒙古呼和浩特（集宁铁路系统），非意大利",
        "keywords": ["气排球.*起源", "气排球.*发源", "气排球.*历史", "气排球.*诞生"],
        "wrong_patterns": ["意大利", "美国", "日本", "欧洲"],
    },
    # 学术常识
    "P值含义": {
        "fact": "P<0.05 表示统计学显著，P<0.01 表示高度显著，不是'证明'",
        "keywords": ["P值", "显著性", "p<", "P<"],
        "wrong_patterns": ["证明了", "绝对正确", "完全有效"],
    },
    # 样本量常识
    "大样本定律": {
        "fact": "中心极限定理要求n≥30才能近似正态分布，小样本需用非参数检验",
        "keywords": ["样本量", "正态分布", "t检验"],
        "wrong_patterns": [],
    },
}


def detect_fact_issues(text, filepath=''):
    """执行内容真伪检测"""
    issues = []
    score = 100
    details_parts = []
    
    lines = text.split('\n')
    
    # ========== 1. 内置事实库核验 ==========
    details_parts.append("**内置事实核验**：")
    
    for fact_name, fact_info in FACT_BASE.items():
        for kw_pattern in fact_info["keywords"]:
            if re.search(kw_pattern, text):
                # 找到了相关内容，检查是否有错误表述
                has_error = False
                error_match = None
                for wrong in fact_info["wrong_patterns"]:
                    context_match = re.search(f'.{{0,50}}{re.escape(wrong)}.{{0,50}}', text)
                    if context_match:
                        has_error = True
                        error_match = context_match
                        break
                
                if has_error and error_match:
                    line_num = text[:error_match.start()].count('\n') + 1
                    issues.append({
                        "level": "critical",
                        "msg": f"「{fact_name}」事实可能有误——{fact_info['fact']}",
                        "location": f"第{line_num}行"
                    })
                    score -= 20
                    details_parts.append(f"- 🔴 [{fact_name}] 发现疑似错误表述")
                else:
                    details_parts.append(f"- ✅ [{fact_name}] 相关内容已检查，未发现明显错误")
                break
    
    # ========== 2. 统计数据合理性 ==========
    stats_patterns = [
        (r'相关系数\s*[rR=]\s*([+-]?\d+\.?\d*)', "相关系数", -1, 1),
        (r'(?:有效率|成功率|合格率|通过率|达标率)\s*(?:为|达|：)?\s*(\d+\.?\d*)%', "百分比数据", 0, 100),
        (r'提升[了之]?\s*(\d+\.?\d*)%(?!\s*[-—])', "提升幅度", 0, 500),
        (r'均值\s*(?:为|达|：)?\s*(\d+\.?\d*)(?:\s*[±±]\s*\d+\.?\d*)?', "均值", None, None),
        (r'标准差\s*(?:为|：)?\s*(\d+\.?\d*)', "标准差", 0, None),  # 标准差>=0
    ]
    
    details_parts.append("\n**统计数据合理性**：")
    stat_checks = 0
    
    for pattern, label, min_val, max_val in stats_patterns:
        matches = re.finditer(pattern, text)
        for m in matches:
            try:
                val = float(m.group(1))
                stat_checks += 1
                
                if min_val is not None and val < min_val:
                    line_num = text[:m.start()].count('\n') + 1
                    issues.append({
                        "level": "warning",
                        "msg": f"「{label}」值={val}，低于合理下限{min_val}",
                        "location": f"第{line_num}行"
                    })
                    score -= 5
                
                if max_val is not None and val > max_val:
                    line_num = text[:m.start()].count('\n') + 1
                    issues.append({
                        "level": "critical",
                        "msg": f"「{label}」值={val}，超出合理上限{max_val}（如相关系数应在[-1,1]）",
                        "location": f"第{line_num}行"
                    })
                    score -= 10
                
                # 特殊检查：百分比精度
                if '%' in m.group(0) and '.' in m.group(1):
                    decimal_places = len(m.group(1).split('.')[-1])
                    if decimal_places >= 2:
                        line_num = text[:m.start()].count('\n') + 1
                        issues.append({
                            "level": "info",
                            "msg": f"「{label}」精确到小数点后{decimal_places}位（{val}%），原始数据是否支持此精度？",
                            "location": f"第{line_num}行"
                        })
            except (ValueError, IndexError):
                continue
    
    if stat_checks == 0:
        details_parts.append("- 未发现明确的统计数据（如论文含数据分析请确认格式）")
    else:
        details_parts.append(f"- 共检查 {stat_checks} 组统计数据")
    
    # ========== 3. 逻辑谬误识别 ==========
    fallacy_patterns = [
        (r'因为.*?所以.*?因此.*?所以', "循环推理/重复论证"),
        (r'(?:显然|不言而喻|众所周知|毫无疑问|大家都清楚)', "诉诸常识（缺乏论证）"),
        (r'(?:A组|实验组).*?(?:优于|好于|胜过).*?(?:B|对照)', "结论先行（需看具体数据支撑）"),
        (r'.{0,30}(?:大幅|显著|急剧|飞速).{0,30}(?:提升|增长|改善).{0,5}$', "形容词堆砌无数据"),
    ]
    
    for pattern, fallacy_name in fallacy_patterns:
        matches = list(re.finditer(pattern, text))
        if matches:
            for m in matches[:2]:
                line_num = text[:m.start()].count('\n') + 1
                snippet = m.group()[:50]
                issues.append({
                    "level": "warning",
                    "msg": f"疑似{fallacy_name}：「{snippet}...」",
                    "location": f"第{line_num}行"
                })
                score -= 5
    
    # ========== 4. 因果关系滥用检测 ==========
    causation_abuse = re.findall(r'(?:.{10,50})(?:导致|引起|使得|造成|促使)(.{10,50})', text)
    if len(causation_abuse) > 3:
        details_parts.append(f"\n**因果声明**：发现{len(causation_abuse)}处因果关系表述")
        # 抽查前2个
        for ca in causation_abuse[:2]:
            if '相关' not in ca and '可能' not in ca and '或许' not in ca:
                line_num = text.index(ca) if ca in text else 0
                line_num = text[:max(0,line_num)].count('\n') + 1
                issues.append({
                    "level": "info",
                    "msg": f"因果关系断言「...导致...」——横断面研究通常只能说明相关，不能断言因果",
                    "location": f"第{line_num}行附近"
                })
    
    # ========== 5. 自相矛盾检测 ==========
    contradiction_patterns = [
        (r'(?:不|未|没有)(?:显著|明显|有效)', "否定性结果"),
        (r'(?:显著|明显|有效)(?:提升|改善|提高|促进)', "肯定性结果"),
    ]
    
    neg_found = bool(re.search(contradiction_patterns[0][0], text))
    pos_found = bool(re.search(contradiction_patterns[1][0], text))
    
    if neg_found and pos_found:
        # 进一步检查是否在同一语境下矛盾
        sections = re.split(r'[一二三四五六七八九十]、', text)
        contradictions_in_section = []
        for sec in sections:
            if re.search(contradiction_patterns[0][0], sec) and re.search(contradiction_patterns[1][0], sec):
                contradictions_in_section.append(sec[:60])
        
        if contradictions_in_section:
            issues.append({
                "level": "warning",
                "msg": "同一部分中同时出现否定性和肯定性结论，可能存在自相矛盾",
                "location": "结果/结论部分"
            })
            score -= 8
    
    score = max(0, min(100, score))
    
    return {
        "error": None,
        "score": score,
        "issues": issues,
        "details": '\n'.join(details_parts),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='内容真伪检测')
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
    
    result = detect_fact_issues(text, args.input)
    
    out_path = os.path.join(args.output, 'fact_check_result.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 内容真伪检测完成：{result['score']}分，发现{len(result['issues'])}项问题")


if __name__ == '__main__':
    main()
