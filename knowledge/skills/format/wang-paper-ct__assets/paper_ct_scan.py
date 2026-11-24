# -*- coding: utf-8 -*-
"""
论文CT — 全方位漏洞检测系统（主控脚本）v2.0
核心理念：CT三步法 —— 穿透→诊断→处方
作者：QClaw | 版本：2.0 | 日期：2026-06-02
用法：python paper_ct_scan.py --input <路径> --output <输出目录>

跨平台支持：Windows / Linux / macOS / HarmonyOS NEXT（鸿蒙）
异常处理原则：绝不静默跳过，所有异常记录到全景报告中。
"""
import sys, os, json, re, time, traceback
from datetime import datetime

# 跨平台控制台编码适配
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
# 鸿蒙(HarmonyOS)/Linux/macOS 终端默认UTF-8，无需特殊设置

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = ''

# ============================================================
# 异常全景报告收集器（全局）
# ============================================================
EXCEPTION_REPORT = {
    "skipped_files": [],      # 跳过的文件及原因
    "failed_modules": [],     # 执行失败的模块
    "missing_dependencies": [], # 缺失的依赖
    "warnings": [],           # 非致命警告
    "operation_log": [],       # 操作日志
}


def log_operation(action, detail, status="ok"):
    """记录操作日志"""
    EXCEPTION_REPORT["operation_log"].append({
        "time": datetime.now().isoformat(),
        "action": action,
        "detail": detail,
        "status": status
    })

# ============================================================
# 工具函数
# ============================================================

def read_file_content(filepath):
    """根据扩展名读取文件内容，返回纯文本。异常不静默，全部记录。"""
    ext = os.path.splitext(filepath)[1].lower()
    content = ''
    
    if ext == '.docx':
        try:
            from docx import Document
            doc = Document(filepath)
            paragraphs = [p.text for p in doc.paragraphs]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        paragraphs.append(cell.text)
            content = '\n'.join(paragraphs)
            log_operation("读取文件", f"{filepath} (.docx) 成功")
        except ImportError:
            msg = f"缺少依赖 python-docx，无法读取 .docx 文件。安装命令：pip install python-docx"
            print(f"[错误] {msg}")
            EXCEPTION_REPORT["missing_dependencies"].append({"package": "python-docx", "file": filepath, "reason": msg})
            log_operation("读取文件", f"{filepath} 失败: 缺少python-docx", "error")
            return None
        except Exception as e:
            msg = f"读取 .docx 文件失败 ({type(e).__name__}: {e})"
            print(f"[错误] {msg}")
            EXCEPTION_REPORT["warnings"].append({"file": filepath, "reason": msg})
            log_operation("读取文件", f"{filepath} 失败: {e}", "error")
            return None
    elif ext == '.pdf':
        try:
            import pdfplumber
            with pdfplumber.open(filepath) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                content = '\n\n'.join(pages)
            log_operation("读取文件", f"{filepath} (.pdf) 成功，共{len(pages)}页")
        except ImportError:
            msg = f"缺少依赖 pdfplumber，无法读取 PDF 文件。安装命令：pip install pdfplumber"
            print(f"[错误] {msg}")
            EXCEPTION_REPORT["missing_dependencies"].append({"package": "pdfplumber", "file": filepath, "reason": msg})
            log_operation("读取文件", f"{filepath} 失败: 缺少pdfplumber", "error")
            return None
        except Exception as e:
            msg = f"读取 PDF 文件失败 ({type(e).__name__}: {e})"
            print(f"[错误] {msg}")
            EXCEPTION_REPORT["warnings"].append({"file": filepath, "reason": msg})
            log_operation("读取文件", f"{filepath} 失败: {e}", "error")
            return None
    elif ext in ('.txt', '.md'):
        encodings = ['utf-8', 'gbk', 'gb18030', 'latin-1']
        last_err = None
        for enc in encodings:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    content = f.read()
                log_operation("读取文件", f"{filepath} 成功 (编码:{enc})")
                break
            except (UnicodeDecodeError, UnicodeError) as e:
                last_err = e
                continue
        else:
            msg = f"无法解码文件（已尝试 UTF-8/GBK/GB18030/Latin-1）：{filepath}"
            print(f"[错误] {msg}")
            EXCEPTION_REPORT["skipped_files"].append({"path": filepath, "reason": f"编码问题: {last_err}"})
            log_operation("读取文件", f"{filepath} 失败: 编码不支持", "error")
            return None
    else:
        msg = f"不支持的文件格式: {ext}"
        print(f"[警告] {msg}，将尝试以文本方式读取")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            log_operation("读取文件", f"{filepath} (非标准格式{ext}) 尝试成功")
        except Exception as e:
            EXCEPTION_REPORT["skipped_files"].append({"path": filepath, "reason": f"格式不支持且读取失败: {e}"})
            log_operation("读取文件", f"{filepath} 失败: {e}", "error")
            return None
    
    return content


def find_paper_files(input_path):
    """查找输入路径下的所有论文文件"""
    files = []
    
    if os.path.isfile(input_path):
        ext = os.path.splitext(input_path)[1].lower()
        if ext in ('.docx', '.pdf', '.txt', '.md'):
            files.append(input_path)
    elif os.path.isdir(input_path):
        for root, dirs, filenames in os.walk(input_path):
            # 跳过隐藏目录和输出目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'output']
            for fn in filenames:
                ext = os.path.splitext(fn)[1].lower()
                if ext in ('.docx', '.pdf', '.txt', '.md'):
                    files.append(os.path.join(root, fn))
    
    return sorted(files)


def run_module(module_name, input_path, output_dir):
    """运行单个检测模块，返回结果字典。异常全部记录，不静默跳过。"""
    module_path = os.path.join(SCRIPT_DIR, module_name)
    result_file = os.path.join(output_dir, module_name.replace('.py', '_result.json'))
    mod_display = module_name.replace('.py', '')
    
    if not os.path.exists(module_path):
        msg = f"模块文件不存在: {module_path}"
        print(f"[错误] {msg}")
        EXCEPTION_REPORT["failed_modules"].append({"module": mod_display, "reason": msg})
        log_operation("模块执行", f"{mod_display} 失败: 模块文件缺失", "error")
        return {"error": msg, "score": 0, "issues": [{"level": "critical", "msg": f"⚠️ 模块缺失: {mod_display}"}]}
    
    try:
        import subprocess
        log_operation("模块执行", f"{mod_display} 开始运行...")
        ret = subprocess.run(
            [sys.executable, module_path, '--input', input_path, '--output', output_dir],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=60  # 单模块超时保护60秒
        )
        
        if ret.returncode != 0:
            stderr_msg = ret.stderr.strip()[:300] if ret.stderr else "未知错误"
            msg = f"模块退出码={ret.returncode}: {stderr_msg}"
            print(f"[警告] {mod_display} 执行异常: {msg}")
            EXCEPTION_REPORT["failed_modules"].append({"module": mod_display, "reason": msg, "stderr": stderr_msg})
            log_operation("模块执行", f"{mod_display} 异常退出(code={ret.returncode})", "warning")
            # 返回降级结果而不是空结果
            return {"error": msg, "score": 0, "issues": [{"level": "critical", "msg": f"⚠️ {mod_display}执行异常: {stderr_msg[:100]}"}]}
        
        # 尝试读取模块输出的结果JSON
        if os.path.exists(result_file):
            with open(result_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            log_operation("模块执行", f"{mod_display} 完成 (得分:{result.get('score','?')}, 问题:{len(result.get('issues',[]))}项)")
            return result
        else:
            stdout_snip = ret.stdout.strip()[:200] if ret.stdout else "(无输出)"
            msg = f"模块未生成结果文件，stdout: {stdout_snip}"
            print(f"[注意] {mod_display}: {msg}")
            EXCEPTION_REPORT["warnings"].append({"module": mod_display, "reason": msg})
            log_operation("模块执行", f"{mod_display} 完成但无结果文件", "warning")
            return {
                "error": None,
                "score": 50,
                "issues": [{"level": "warning", "msg": f"⚠️ {mod_display}完成但未输出结构化结果: {stdout_snip}"}],
                "details": ret.stdout[:500] if ret.stdout else ""
            }
    except subprocess.TimeoutExpired:
        msg = f"模块执行超时(>60秒): {mod_display}"
        print(f"[错误] {msg}")
        EXCEPTION_REPORT["failed_modules"].append({"module": mod_display, "reason": "执行超时60秒"})
        log_operation("模块执行", f"{mod_display} 超时", "error")
        return {"error": "执行超时", "score": 0, "issues": [{"level": "critical", "msg": f"⚠️ {mod_display}执行超时"}]}
    except Exception as e:
        tb = traceback.format_exc()[-500:]
        msg = f"{type(e).__name__}: {e}"
        print(f"[错误] {mod_display} 异常: {msg}")
        EXCEPTION_REPORT["failed_modules"].append({"module": mod_display, "reason": msg, "traceback": tb})
        log_operation("模块执行", f"{mod_display} 异常: {e}", "error")
        return {"error": msg, "score": 0, "issues": [{"level": "critical", "msg": f"⚠️ {mod_display}异常: {msg}"}]}


def generate_report(all_results, paper_title, output_dir):
    """生成综合检测报告（Markdown格式）"""
    report_lines = []
    total_score = 0
    weight_sum = 0
    
    # 维度配置
    dimensions = [
        ("format_check",      "📐 排版规范检测",     0.10),
        ("authenticity_check", "🔎 内容真实性检测",   0.25),
        ("feasibility_check",  "⚙️ 可行性检测",       0.15),
        ("fact_check",         "🧠 内容真伪检测",     0.15),
        ("ai_detect",          "🤖 AI痕迹检测",       0.15),
        ("academic_norms",     "📋 学术规范检测",     0.10),
        ("journal_fit",        "🎯 期刊适配检测",     0.10),
    ]
    
    # 计算总分
    weighted_scores = []
    for mod_key, dim_name, weight in dimensions:
        result = all_results.get(mod_key, {})
        score = result.get('score', 0)
        weighted_scores.append((dim_name, score, weight, result))
        total_score += score * weight
        weight_sum += weight
    
    final_score = round(total_score / weight_sum, 1) if weight_sum > 0 else 0
    
    # 等级判定
    if final_score >= 90: grade = "🏆 优秀"
    elif final_score >= 75: grade = "✅ 良好"
    elif final_score >= 60: grade = "🟡 合格"
    elif final_score >= 40: grade = "⚠️ 需改进"
    else: grade = "❌ 不合格"
    
    # 报告头部
    report_lines.append(f"# 📋 论文CT检测报告\n")
    report_lines.append(f"> 论文：《{paper_title}》| 检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} | 总评分：**{final_score}/100**\n")
    report_lines.append(f"## 🏆 总评等级：{grade}\n")
    report_lines.append("---\n")
    
    # 各维度详情
    all_critical = []
    all_warning = []
    
    for item in dimensions:
        mod_key = item[0]
        dim_name = item[1]
        weight = item[2]
        result = all_results.get(mod_key, {})
        score = result.get('score', 0)
        issues = result.get('issues', [])
        details = result.get('details', '')
        error = result.get('error')
        
        # 分数等级图标
        if score >= 85: s_icon = "🟢"
        elif score >= 60: s_icon = "🟡"
        else: s_icon = "🔴"
        
        report_lines.append(f"## {dim_name} — **{score}/100** 分 {s_icon}\n")
        
        if error and len(issues) == 0:
            report_lines.append(f"> ⚠️ 模块执行异常：{error}\n")
        elif len(issues) == 0:
            report_lines.append("### ✅ 未发现明显问题\n")
        else:
            report_lines.append(f"### 发现问题（{len(issues)}项）\n")
            for i, issue in enumerate(issues, 1):
                level = issue.get('level', 'info')
                msg = issue.get('msg', '')
                loc = issue.get('location', '')
                
                icon = {"critical": "🔴", "warning": "🟡", "info": "🟢", "pass": "🟢"}.get(level, "⚪")
                label = {"critical": "[严重]", "warning": "[注意]", "info": "[提示]", "pass": "[合格]"}.get(level, "")
                
                loc_str = f" → {loc}" if loc else ""
                report_lines.append(f"- {icon} {label} {msg}{loc_str}")
                
                # 收集到优先修复清单
                if level == "critical":
                    all_critical.append(f"{icon} [{dim_name}] {msg}{loc_str}")
                elif level == "warning":
                    all_warning.append(f"{icon} [{dim_name}] {msg}{loc_str}")
        
        if details:
            report_lines.append(f"\n### 详细分析\n{details}\n")
        
        report_lines.append("---\n")
    
    # 综合诊断
    report_lines.append("## 📊 综合诊断结论\n")
    
    ai_score = all_results.get("ai_detect", {}).get("score", 100)
    auth_score = all_results.get("authenticity_check", {}).get("score", 100)
    
    conclusions = []
    if ai_score < 60:
        conclusions.append("⚠️ **AI生成痕迹明显**——编辑部越来越重视此问题，建议大幅改写增加个人特色细节。")
    if auth_score < 70:
        conclusions.append("🔴 **内容真实性存疑**——数据或引用存在问题，这是最致命的问题，必须逐项核实。")
    if final_score < 60:
        conclusions.append("❌ **整体质量未达发表标准**——建议按下方修复清单逐项修改后重新检测。")
    elif final_score < 75:
        conclusions.append("🟡 **基本达标但有改进空间**——重点修复「严重」级别问题即可显著提升。")
    else:
        conclusions.append("✅ **整体质量良好**——检查「注意」级问题可进一步提升发表概率。")
    
    for c in conclusions:
        report_lines.append(f"{c}\n")
    
    # 优先修复清单
    report_lines.append("## ⚡ 优先修复清单（按严重程度排序）\n")
    all_items = all_critical + all_warning
    if all_items:
        for i, item in enumerate(all_items, 1):
            report_lines.append(f"{i}. {item}")
    else:
        report_lines.append("🎉 未发现需要紧急修复的问题！")
    
    report_lines.append("\n---\n")
    
    # ====== 异常全景报告 ======
    report_lines.append("## 🔍 运行状态与异常报告\n")
    has_exceptions = any([
        EXCEPTION_REPORT["skipped_files"],
        EXCEPTION_REPORT["failed_modules"],
        EXCEPTION_REPORT["missing_dependencies"],
        EXCEPTION_REPORT["warnings"]
    ])
    
    if has_exceptions:
        if EXCEPTION_REPORT["missing_dependencies"]:
            report_lines.append("### ⚠️ 缺失依赖\n")
            for dep in EXCEPTION_REPORT["missing_dependencies"]:
                report_lines.append(f"- ❌ **{dep['package']}** — {dep['reason']}\n")
        
        if EXCEPTION_REPORT["failed_modules"]:
            report_lines.append("### ❌ 执行失败模块\n")
            for mod in EXCEPTION_REPORT["failed_modules"]:
                reason = mod.get('reason', '未知原因')
                report_lines.append(f"- ❌ **{mod['module']}** — {reason}\n")
        
        if EXCEPTION_REPORT["skipped_files"]:
            report_lines.append("### ⏭️ 跳过的文件\n")
            for sf in EXCEPTION_REPORT["skipped_files"]:
                report_lines.append(f"- ⏭️ `{sf['path']}` — {sf['reason']}\n")
        
        if EXCEPTION_REPORT["warnings"]:
            report_lines.append("### 💡 非致命警告\n")
            for w in EXCEPTION_REPORT["warnings"][:5]:  # 最多显示5条
                mod = w.get('module', '系统')
                report_lines.append(f"- 💡 [{mod}] {w.get('reason', '')}\n")
    else:
        report_lines.append("✅ 所有模块正常运行，无异常。\n")
    
    # ====== 操作日志 ======
    report_lines.append("### 📋 操作日志\n")
    for entry in EXCEPTION_REPORT["operation_log"]:
        status_icon = {"ok": "✅", "warning": "⚠️", "error": "❌"}.get(entry["status"], "📌")
        report_lines.append(f"- {status_icon} `{entry['time']}` {entry['action']} — {entry['detail']}\n")
    
    report_lines.append("\n---\n")
    report_lines.append(f"*报告由 论文CT v2.0 自动生成 | CT三步法：穿透→诊断→处方 | 检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # 写入文件
    report_text = '\n'.join(report_lines)
    report_path = os.path.join(output_dir, 'report_summary.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    # 同时保存结构化数据
    scores_data = {
        "paper_title": paper_title,
        "scan_time": datetime.now().isoformat(),
        "final_score": final_score,
        "grade": grade,
        "dimensions": {
            d[0]: {"name": d[1], "score": all_results.get(d[0], {}).get('score', 0), "weight": d[2], "issue_count": len(all_results.get(d[0], {}).get('issues', []))}
            for d in dimensions
        },
        "critical_count": len(all_critical),
        "warning_count": len(all_warning),
    }
    scores_path = os.path.join(output_dir, 'scores.json')
    with open(scores_path, 'w', encoding='utf-8') as f:
        json.dump(scores_data, f, ensure_ascii=False, indent=2)
    
    # 输出异常摘要
    exc_count = len(EXCEPTION_REPORT["failed_modules"]) + len(EXCEPTION_REPORT["skipped_files"])
    dep_count = len(EXCEPTION_REPORT["missing_dependencies"])
    
    print(f"\n{'='*60}")
    print(f"  📋 论文CT v2.0 检测完成！（CT三步法：穿透→诊断→处方）")
    print(f"  📄 论文：《{paper_title}》")
    print(f"  🏆 总评分：{final_score}/100 （{grade}）")
    print(f"  🔴 严重问题：{len(all_critical)} 项")
    print(f"  🟡 注意事项：{len(all_warning)} 项")
    if exc_count > 0:
        print(f"  ⚠️  异常/跳过：{exc_count} 项（详见报告「运行状态」章节）")
    if dep_count > 0:
        print(f"  📦  缺失依赖：{dep_count} 项（详见报告）")
    print(f"  📁 报告位置：{report_path}")
    print(f"{'='*60}")
    
    return final_score, grade


# ============================================================
# 主入口
# ============================================================

def main():
    global OUTPUT_DIR
    
    import argparse
    parser = argparse.ArgumentParser(description='论文CT — 学术论文全方位漏洞检测系统')
    parser.add_argument('--input', '-i', required=True, help='论文文件或文件夹路径')
    parser.add_argument('--output', '-o', default=None, help='输出目录（默认为脚本同目录下的output/）')
    args = parser.parse_args()
    
    # 输出目录
    if args.output:
        OUTPUT_DIR = args.output
    else:
        OUTPUT_DIR = os.path.join(SKILL_DIR, 'output')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 查找论文文件
    print("=" * 60)
    print("  🔬 论文CT v1.0 — 学术论文全方位漏洞检测系统")
    print("=" * 60)
    print(f"\n📂 扫描路径：{args.input}")
    
    paper_files = find_paper_files(args.input)
    
    if not paper_files:
        print(f"\n❌ 未找到任何论文文件（支持 .docx / .pdf / .txt / .md）")
        print(f"   请确认路径是否正确，或文件扩展名是否支持。")
        return
    
    print(f"📄 发现 {len(paper_files)} 个文件待检测：")
    for pf in paper_files:
        print(f"   - {os.path.basename(pf)}")
    
    # 对每个文件执行全量检测
    for filepath in paper_files:
        print(f"\n{'━'*60}")
        print(f"🔍 正在检测：{os.path.basename(filepath)}")
        print(f"{'━'*60}")
        
        content = read_file_content(filepath)
        if content is None or len(content.strip()) < 50:
            print(f"⚠️ 文件内容过短或读取失败，跳过：{os.path.basename(filepath)}")
            continue
        
        # 提取标题（取第一行非空内容作为标题候选）
        title = os.path.basename(filepath)
        for line in content.split('\n')[:10]:
            line = line.strip()
            if len(line) > 5 and len(line) < 80:
                title = line
                break
        
        # 将内容暂存供子模块使用
        content_cache = os.path.join(OUTPUT_DIR, '_content_cache.txt')
        with open(content_cache, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 运行7个检测模块
        modules = [
            "format_check.py",
            "authenticity_check.py",
            "feasibility_check.py",
            "fact_check.py",
            "ai_detect.py",
            "academic_norms.py",
            "journal_fit.py",
        ]
        
        all_results = {}
        for mod in modules:
            mod_name = mod.replace('.py', '')
            print(f"\n  ▶ 运行模块：{mod_name}...", end='')
            result = run_module(mod, filepath, OUTPUT_DIR)
            all_results[mod_name] = result
            sc = result.get('score', '?')
            issues_n = len(result.get('issues', []))
            print(f" 完成 ({sc}分, {issues_n}项发现)")
        
        # 生成综合报告
        generate_report(all_results, title, OUTPUT_DIR)
    
    # 清理缓存
    cache_file = os.path.join(OUTPUT_DIR, '_content_cache.txt')
    if os.path.exists(cache_file):
        os.remove(cache_file)
    
    print(f"\n✅ 所有检测完成！报告已保存至：{OUTPUT_DIR}")


if __name__ == '__main__':
    main()
