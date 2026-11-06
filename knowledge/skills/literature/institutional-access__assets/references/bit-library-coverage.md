# 北理工机构网关实战记录(2026-08-11)

67 个有效 DOI 的下载实战(篮球投篮生物力学检索),脚本 OA 下载 19 篇后,剩余经机构网关+浏览器路线补齐至 62 篇(93%)。以下为可复用的环境事实。

## 北理工订阅覆盖图谱(实测判定)

| 出版商 | 网关后状态 | 判定方式 |
|---|---|---|
| ScienceDirect(Elsevier) | ✅ 主流运动医学期刊可下 | 页面顶部 "Brought to you by: Beijing Institute of Technology" + 右上 "Institutional Access" 按钮 |
| Springer | ✅ 可下(NSTL 联合认证) | "Log in via an institution" → 机构搜索 → 经 "China Institute of Science & Technology acting through NSTL" 授权 |
| Taylor & Francis | ✅ 可下(网关/CARSI) | 页面顶部 "Access provided by Beijing Institute of Technology";Federation 下拉含 "China CERNET Federation (CARSI)" |
| Wiley | ✅ 可下(3 篇直接落盘 Downloads) | 文章页自动触发下载 |
| SAGE 期刊库 | ❌ 未订阅 | 页面明示 "Beijing Institute of Technology does not subscribe to Sage Journals content" |
| ACS | ❌ 机构库无北理工 | 机构搜索 "Beijing Institute of Technology" 零匹配;Federation 无可选项 |
| Human Kinetics | ❌ IP 未识别 | 文章页 "Restricted access" |
| Elsevier 书籍章节(pbr 系列) | ❌ 未订阅 | "does not subscribe to this content on ScienceDirect" |
| Elsevier Primary Care | ❌ 未订阅 | 同上 |

## 各库下载路径实测

- **ScienceDirect 稳定路径**:文章页 View PDF → viewer 加载(等 10-12s,cmd+S 过早会存 init.html)→ **cmd+P 打印为 PDF** → 保存对话框 save_enter。直接点工具条下载按钮保存对话框行为不稳定。`pdfft?isDTMRedir=true&download=true` 直链在代理下被 Cloudflare 拦(403),urllib 拉签名 URL 也 403(需浏览器环境)。
- **Springer**:机构认证后 Download PDF 按钮直接触发下载(文件名如 s00221-009-2040-x.pdf),无需保存对话框,最顺。
- **T&F**:PDF 阅读器(标题=文章名,页码工具条)的 Download 按钮坐标点击(1496,207)直接下载;AXPress 点击 Download 有时无效果。部分文章 Get Access 视图与 "You have Full Access" 标记并存,点 Full Article/Read this article 或强刷。
- **Cloudflare 验证**:代理出口 IP(66.90.98.106)触发 "Are you a robot?" 页;Turnstile 复选框 AX 可点即过;iframe 内 captcha 坐标点击右上(~1085,430)可过;验证通过后文章页才加载。

## 流程教训(对应"自动化优先"原则)

- 本次机构网关阶段每篇都手动交互(开页→等→找按钮→保存→收编),Chrome 崩溃 2 次、翻译气泡反复干扰、保存对话框 AX 读不到——大量步骤本可用 AppleScript 脚本化(打印流程、key-code 输入、坐标点击)。
- 正确编排:脚本全量(阶段1)→ MDPI 类直链批量(阶段2)→ agent 脚本化操作(阶段3)→ 用户登录网关后 agent 批量(阶段4)→ 用户兜底(阶段5)。
- 每篇下载后立即收编(移入 pdfs/ + 重命名 出版社_作者_年份_主题),避免 Downloads 堆积;最终 md5 查重清理 " (1)" 后缀副本。

## 收尾统计

- 62 篇 PDF 全部 %PDF 校验通过、无重复
- 命名规范示例:TnF_SportsBiomech2015_Okazaki_jump_shot_review.pdf、Elsevier_apunsm2021_100361_RTS_ACL_part2.pdf、Springer_Rein2010_EBR_phase_transition.pdf
- 未获取 5 篇(用户选择忽略):JMB 2025、ACS×2、SAGE ProcIMechE 2025 等
