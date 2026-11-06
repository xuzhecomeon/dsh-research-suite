# 主题示例（跨专业，可编辑）

本文件给出**多个临床与基础医学方向**的检索主题写法，供参考与复制。
核心要求：**中文方向 + 英文关键词成对给出**（中文刊在 Europe PMC 的题录是英文翻译；SCI 检索也需英文）。

> 使用方法：把下面的 JSON 存为 `my_topics.json`，然后
> `python scripts/pipeline.py search --out ./lib --topics my_topics.json`

---

## 一、单方向快速检索（推荐起点）

```bash
# 骨科创伤 / 骨盆骨折出血
python scripts/pipeline.py search --out ./lib \
  --topic "骨盆骨折出血" \
  --keywords "pelvic fracture;hemorrhage;bleeding;hemodynamic instability;pelvic ring" \
  --years 2021-2026

# 急诊 / 心肺复苏
python scripts/pipeline.py search --out ./lib \
  --topic "心脏骤停复苏" \
  --keywords "cardiac arrest;cardiopulmonary resuscitation;targeted temperature management" \
  --years 2021-2026

# 肿瘤免疫
python scripts/pipeline.py search --out ./lib \
  --topic "肿瘤免疫治疗" \
  --keywords "immunotherapy;immune checkpoint inhibitor;PD-1;CAR-T" \
  --years 2021-2026

# 心血管
python scripts/pipeline.py search --out ./lib \
  --topic "急性心肌梗死" \
  --keywords "acute myocardial infarction;STEMI;primary PCI;reperfusion" \
  --years 2021-2026

# 护理
python scripts/pipeline.py search --out ./lib \
  --topic "ICU 谵妄护理" \
  --keywords "delirium;intensive care;nursing;ABCDEF bundle" \
  --years 2021-2026
```

---

## 二、多子方向批量检索（全领域调研）

```json
{
  "骨科创伤-骨盆骨折出血": "(\"pelvic fracture\" AND (hemorrhage OR bleeding OR \"hemodynamic instability\"))",
  "骨科创伤-脊柱脊髓损伤": "(\"spinal cord injury\" OR \"spinal fracture\" OR \"traumatic myelopathy\")",
  "急诊-心脏骤停与复苏": "(\"cardiac arrest\" OR \"cardiopulmonary resuscitation\")",
  "急诊-创伤救治": "(\"trauma\" AND (resuscitation OR \"damage control\"))",
  "重症-脓毒症": "(\"sepsis\" OR \"septic shock\")",
  "重症-ARDS与机械通气": "(\"acute respiratory distress syndrome\" OR \"mechanical ventilation\")",
  "内科-急性肾损伤": "(\"acute kidney injury\" AND (\"critical care\" OR \"intensive care\"))",
  "肿瘤-免疫治疗": "(\"immunotherapy\" OR \"immune checkpoint inhibitor\")",
  "心血管-急性冠脉综合征": "(\"acute coronary syndrome\" OR \"myocardial infarction\")",
  "神经-急性缺血性卒中": "(\"acute ischemic stroke\" AND (thrombolysis OR thrombectomy))",
  "基础-炎症小体与细胞死亡": "(\"NLRP3\" OR \"pyroptosis\" OR \"ferroptosis\")",
  "护理-重症护理集束化": "((\"delirium\" OR \"ventilator-associated pneumonia\") AND nursing)"
}
```

---

## 三、中文核心期刊白名单（`cn_journals.json`）

内置 **269 本**，来源：
- 《中文核心期刊要目总览》2023 年版 **医药卫生类**（R1–R9 全类目，252 本）
- **中华医学会系列期刊**一览表（2026-04）

覆盖学科：综合性医药卫生、预防医学/卫生学、中国医学、基础医学、临床医学、内科学、外科学、
妇产科学、儿科学、肿瘤学、神经病学与精神病学、皮肤病学与性病学、耳鼻咽喉科学、眼科学、
口腔科学、特种医学、药学。

按学科分类的完整清单在 `cn_journals.json` 的 `by_category` 字段。

**增补方式**：直接编辑 `journals` 数组，加入刊物中文名即可（罗马化别名与 ISSN 可留空，
`is_cn_core()` 会用「Zhonghua/Zhongguo/Chinese Journal of …」等通用规则兜底匹配）。

---

## 四、中文库检索式速查

| 库 | 入口 | 关键设置 | 导出格式 |
|----|------|---------|---------|
| **CNKI 知网** | kns.cnki.net → 高级检索 | 库选「学术期刊」；来源类别勾 北大核心/CSSCI/CSCD | 参考文献 TXT / Excel / RefWorks / EndNote |
| **万方数据** | s.wanfangdata.com.cn → 学术期刊 | 左侧「期刊收录」勾 北大核心/CSCD/统计源 | NoteExpress / EndNote / RefWorks / Excel |
| **SinoMed** | www.sinomed.ac.cn | 需机构 IP 或登录；支持主题词+副主题词 | 题录 / 参考文献 |

导出文件放进工作目录后：

```bash
python scripts/pipeline.py import --out ./lib --file 检索结果.ris --db "CNKI 知网"
```

---

## 五、方向推荐的条件适配（示例）

同一方向，**不同医院条件要推荐完全不同的做法**：

| 用户条件 | "脓毒症"方向的可行选题示例 |
|---------|--------------------------|
| 无实验室、经费 <10 万 | 本院脓毒症患者乳酸清除率与预后的回顾性队列；qSOFA 在真实世界的诊断效能 |
| 有少量经费、有随访 | 脓毒症生存者 1 年认知功能随访；不同血管活性药起始策略的真实世界比较 |
| 有特色场景（卫勤/区域） | 战现场/批量伤员脓毒症早期识别流程；高原/寒区脓毒症特征 |
| 有实验室与团队 | 脓毒症相关内皮糖萼损伤机制；外泌体 miRNA 诊断标志物前瞻验证 |

> 推荐时**必须同时说明优点与缺点**，不做只讲优点的"包装"。
