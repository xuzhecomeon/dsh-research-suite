# Examples

End-to-end examples for common deck types.

## 1. Quarterly business review (QBR)

```python
from pptx_builder import Builder

b = Builder(theme="aurora")

b.cover("2026 Q2 业务回顾",
        "战略执行 · 经营成果 · 下阶段规划",
        eyebrow="2026 · Q2 · Quarterly Business Review",
        accent="Confidential · Internal Use Only",
        bottom_left="Strategy & Operations",
        bottom_right="2026.06.26")

b.section("01", "Executive Summary",
           "本季度核心成果与关键洞察")

b.bullets("Highlights", [
    "营业收入 ¥ 1.24B，同比增长 38%，超目标 12%",
    "毛利率提升至 47%，连续 4 个季度环比改善",
    "新签 12 家企业客户，其中 3 家 Fortune 500",
    "NPS 提升至 67，客户满意度创历史新高",
], eyebrow="Q2 2026 · At a glance")

b.big_number("By the Numbers", [
    {"value": "¥ 1.24B", "label": "季度营收", "delta": "+38% YoY"},
    {"value": "47%",     "label": "毛利率",   "delta": "+4.2 pts"},
    {"value": "12",      "label": "新签客户", "delta": "+5 vs Q1"},
    {"value": "67",      "label": "NPS",      "delta": "+12 pts"},
], eyebrow="Headline KPIs")

b.section("02", "业务表现", "各业务线增长与挑战")

b.cards_grid("业务线表现", [
    {"title": "企业服务",  "icon": "◆", "metric": "+52%",
     "body": "营收占比突破 60%，新签合同金额同比翻倍。"},
    {"title": "云服务",    "icon": "●", "metric": "+38%",
     "body": "续约率 98%，客户使用深度持续提升。"},
    {"title": "国际化",    "icon": "▲", "metric": "5 国",
     "body": "新增东南亚 3 国、中东 2 国市场。"},
    {"title": "开发者生态", "icon": "■", "metric": "120K",
     "body": "注册开发者突破 12 万，月活同比 +65%。"},
], eyebrow="What worked", cols=4)

b.bar_chart("营收分业务线", ["企业服务", "云服务", "开发者", "国际化"],
             [620, 380, 160, 80],
             eyebrow="Q2 2026", unit="M", highlight_index=0)

b.donut_chart("客户结构", [
    {"label": "世界 500 强", "value": 28},
    {"label": "上市公司",   "value": 35},
    {"label": "中型企业",   "value": 22},
    {"label": "其他",       "value": 15},
], center_value="230+", center_label="Total Accounts")

b.section("03", "下阶段规划", "聚焦 3 大战略主题")

b.timeline("H2 Roadmap", [
    {"label": "Q3 · 7-8 月", "title": "产品创新",
     "body": "发布 2.0 平台架构，开放 50+ API。", "color": "primary"},
    {"label": "Q3 · 8-9 月", "title": "市场扩张",
     "body": "进入欧洲市场，建立本地服务团队。", "color": "accent_pink"},
    {"label": "Q4 · 10-11月", "title": "组织升级",
     "body": "完成 200 人招聘，建立 AI Lab。",  "color": "accent_cyan"},
    {"label": "Q4 · 12 月",  "title": "年度复盘",
     "body": "总结与 2027 战略规划对齐。",      "color": "accent_amber"},
], orientation="horizontal")

b.quote("增长不是数字的堆叠，而是为客户持续创造独特价值的能力。",
         "— 创始人寄语",
         "Annual Address 2026")

b.thanks("Thank You", "期待与各位共同书写 2026 下半年的精彩",
          "strategy@company.com")

b.save("2026_Q2_Business_Review.pptx")
```

## 2. Product launch (Neon theme)

```python
b = Builder(theme="neon")

b.cover("PHANTOM X1", "下一代神经渲染引擎",
        eyebrow="2026 · Product Launch",
        accent="The future of rendering is here.",
        bottom_left="Product Team",
        bottom_right="Reveal Event · 2026.07.15")

b.section("01", "Vision",
           "重新定义视觉生成的边界")

b.bullets("Why PHANTOM X1", [
    "10x faster than competitors on diffusion workloads",
    "Native support for 4K + HDR real-time generation",
    "Half the power consumption of leading alternatives",
    "Open ecosystem with 200+ pre-trained models",
], eyebrow="Differentiation",
   icons=["▶", "◆", "▲", "■"],
   accent_colors=["primary", "accent_pink", "accent_amber", "accent_lime"])

b.cards_grid("Core Capabilities", [
    {"title": "Neural Render",   "icon": "◆", "metric": "120 fps",
     "body": "Real-time photorealistic rendering at 4K resolution."},
    {"title": "Adaptive Cache",  "icon": "●", "metric": "60% less",
     "body": "Predictive caching cuts redundant compute by 60%."},
    {"title": "Open SDK",        "icon": "▲", "metric": "200+ models",
     "body": "Drop-in compatible with PyTorch, JAX, and TF."},
], eyebrow="Under the hood", cols=3)

b.timeline("Launch Plan", [
    {"label": "T-30d", "title": "Teaser",   "body": "Influencer seeding"},
    {"label": "T-7d",  "title": "Preview",  "body": "Press & analysts"},
    {"label": "T-0",   "title": "Reveal",   "body": "Live event"},
    {"label": "T+30d", "title": "GA",       "body": "Public release"},
], orientation="horizontal")

b.bar_chart("Performance vs Competition",
             ["Ours", "Comp A", "Comp B", "Comp C"],
             [120, 65, 42, 38],
             eyebrow="4K HDR · fps",
             highlight_index=0, unit=" fps")

b.thanks("PHANTOM X1", "Coming July 15, 2026", "phantom-x1.company.com")

b.save("PHANTOM_X1_Launch.pptx")
```

## 3. Brand / culture deck (Morandi theme)

```python
b = Builder(theme="morandi")

b.cover("Maison Lumière", "2026 春夏新品发布",
        eyebrow="Spring · Summer · 2026",
        accent="An ode to light, form, and quiet luxury.",
        bottom_left="Creative Direction",
        bottom_right="Paris · 2026.03.10")

b.section("01", "The Story",
           "从地中海晨光到工作室午后的灵感之旅")

b.two_column("Concept",
    {"eyebrow": "Inspiration",
     "title": "晨光乍现",
     "body": "白色亚麻披拂而过\n瓷器与玻璃器皿的微光\n旧木地板上散落的光斑\n米色羊绒的柔软弧度",
     "accent": "accent_pink"},
    {"eyebrow": "Manifesto",
     "title": "慢，是一种姿态",
     "body": "不追逐喧嚣的时尚\n不制造焦虑的稀缺\n只为那些愿意慢下来的人\n做一件值得穿十年的衣服",
     "accent": "primary_2"})

b.cards_grid("Collection Highlights", [
    {"title": "The Linen Series", "icon": "❀", "metric": "12 件",
     "body": "意大利手织亚麻，自然染色，亲肤透气。"},
    {"title": "The Ceramic Edit", "icon": "✦", "metric": "8 件",
     "body": "釉色灵感，单品限量，附工匠签名。"},
    {"title": "The Atelier Set",  "icon": "❖", "metric": "5 件",
     "body": "工作室联名，工坊手作，绝版发行。"},
], eyebrow="This season", cols=3)

b.donut_chart("Material Mix", [
    {"label": "亚麻",     "value": 40, "color": "accent_pink"},
    {"label": "羊绒",     "value": 25, "color": "primary_2"},
    {"label": "有机棉",   "value": 20, "color": "accent_amber"},
    {"label": "再生纤维", "value": 15, "color": "accent_cyan"},
], center_value="100%", center_label="Sustainable")

b.quote("真正奢侈的，是时间。",
         "— Hélène Dubois",
         "Creative Director, Maison Lumière")

b.thanks("Merci", "欢迎预约 2026 春夏预览", "atelier@maison-lumiere.fr")

b.save("Maison_Lumiere_SS2026.pptx")
```

## 4. Minimal data report (no theme override)

```python
b = Builder(theme="aurora")  # default works for almost any data

b.cover("Q2 2026 数据洞察",
        "User Growth · Engagement · Revenue",
        eyebrow="Product Analytics",
        accent="Data through 2026-06-25",
        bottom_left="Data Team",
        bottom_right="Weekly Report")

b.big_number("This Week", [
    {"value": "1.24M",  "label": "DAU",          "delta": "+5.2% WoW"},
    {"value": "8.4",    "label": "Avg Session",  "delta": "+0.3 min"},
    {"value": "32.1%",  "label": "Conversion",   "delta": "+1.2 pts"},
    {"value": "$ 4.2",  "label": "ARPU",         "delta": "+0.18"},
])

b.bar_chart("DAU by Channel", ["Search", "Social", "Direct", "Referral", "Email"],
             [420, 310, 280, 150, 80],
             highlight_index=0, unit="K")

b.timeline("Experiment Results", [
    {"label": "Week 1", "title": "Onboarding v3",
     "body": "+8% activation", "color": "primary"},
    {"label": "Week 2", "title": "Push notification",
     "body": "+12% retention", "color": "accent_pink"},
    {"label": "Week 3", "title": "Pricing page",
     "body": "+3% conversion", "color": "accent_cyan"},
])

b.thanks("Q2 W11 Wrap-up", "See you next Friday", "#data-weekly")

b.save("data_weekly_w11.pptx")
```

## 5. Adding a custom page

```python
def agenda_slide(slide, b):
    c = b.theme["colors"]
    f = b.theme["fonts"]
    rounded_rect(slide, 0.8, 0.8, 11.7, 5.9,
                  fill="#FFFFFF", corner=0.04)
    add_textbox(slide, 1.2, 1.2, 10.5, 0.6, "Agenda",
                font=f["title"], size=36, color=c["text"], bold=True)
    items = [
        ("01", "Executive Summary",       "10 min"),
        ("02", "Q2 Performance Review",   "20 min"),
        ("03", "Product Roadmap",         "15 min"),
        ("04", "Q&A and Discussion",      "15 min"),
    ]
    for i, (num, title, dur) in enumerate(items):
        y = 2.2 + i * 1.0
        ellipse(slide, 1.2, y, 0.7, 0.7, fill=c["primary"])
        add_textbox(slide, 1.2, y, 0.7, 0.7, num,
                    font=f["title_en"], size=18, color="#FFFFFF",
                    bold=True, align="center", anchor="middle")
        add_textbox(slide, 2.2, y, 8.0, 0.7, title,
                    font=f["title"], size=22, color=c["text"], bold=True)
        add_textbox(slide, 2.2, y + 0.45, 8.0, 0.4, dur,
                    font=f["body_en"], size=13, color=c["text_muted"])

b = Builder(theme="aurora")
b.cover("Board Meeting", "Q2 2026 Review", eyebrow="Board of Directors")
b.custom(agenda_slide)
b.section("01", "Executive Summary")
# ...
b.save("board_meeting.pptx")
```

## Best practices

1. **One cover, one closing.** The deck should open with `cover()` and
   close with `thanks()`. Section dividers (`section()`) sit between
   major parts — typically 3-7 per deck, not 1 per content slide.

2. **Alternate content density.** Don't put 3 cards_grid slides back
   to back. Mix in bullets, big_number, or charts for visual variety.

3. **Use `eyebrow` for scannability.** Most content pages should have
   a small uppercase tag above the title. It gives readers a "you are
   here" cue as they flip through.

4. **Pick a theme that matches the tone.** The user said "premium" →
   aurora. The user said "tech" → neon. The user said "elegant /
   beauty / fashion" → morandi. When in doubt, aurora.

5. **Keep `bullets` lists short.** 3-5 items per slide. If you have
   more, split across multiple slides or switch to `cards_grid`.

6. **Use `highlight_index` to draw attention.** In a bar chart, set
   `highlight_index` to the bar you want the audience to focus on.
   The other bars stay in the standard gradient; the highlighted bar
   gets a warm pink→amber gradient.

7. **Customize per slide, not per theme.** If the user wants one slide
   to look different (e.g., a black closing slide in a light deck),
   use `b.custom(build_fn)` for that one slide rather than swapping
   themes mid-deck.
