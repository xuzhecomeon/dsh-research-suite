# 学科导航索引（Discipline Index）

本文件把 36 个学科指南映射到文件名与常见关键词，便于快速路由。当用户说出学科/专业时，先在本表找到对应文件再读取 `references/disciplines/<文件>.md`。

> 若用户的学科未在表中，按"学科族"就近匹配（如"营养学"归入 public_health；"城市规划"归入 architecture/geography）；或以相近方法论学科 + 通用方法文件（`research_methods.md`、`qualitative_research.md`、`quantitative_research.md`）组合应对，并提示用户这属于近似建议。

## 一、理工与生命科学（STEM & Life Sciences）
| 学科（中 / EN） | 文件 | 典型关键词 |
|---|---|---|
| 计算机科学 / CS | `cs.md` | 算法、AI、软件、系统、数据科学 |
| 工程 / Engineering | `engineering.md` | 机械、电子、土木、化工、控制 |
| 自然科学 / Science | `science.md` | 物理、化学、生物、材料 |
| 数学 / Mathematics | `mathematics.md` | 纯数学、应用数学、建模 |
| 统计学 / Statistics | `statistics.md` | 推断、贝叶斯、因果、机器学习方法 |
| 农业 / Agriculture | `agriculture.md` | 作物、养殖、植保、土壤 |
| 医学 / Medicine | `medical.md` | 临床、基础、流行病、药学 |
| 护理学 / Nursing | `nursing.md` | 护理干预、慢病、循证、PICOT |
| 公共卫生 / Public Health | `public_health.md` | 流行病学、卫生政策、健康不平等 |
| 兽医学 / Veterinary | `veterinary.md` | 动物疫病、One Health、诊断 |
| 环境科学 / Environmental | `environmental.md` | 污染、生态、气候变化、可持续 |
| 地理学 / Geography | `geography.md` | GIS、遥感、城市、人地关系 |

## 二、人文与艺术（Humanities & Arts）
| 学科（中 / EN） | 文件 | 典型关键词 |
|---|---|---|
| 文学 / Literature | `literature.md` | 小说、诗歌、比较文学、批评 |
| 历史 / History | `history.md` | 古代、近代、史料、史学理论 |
| 哲学 / Philosophy | `philosophy.md` | 伦理、认识论、美学、分析哲学 |
| 宗教学 / Religious Studies | `theology.md` | 经典、仪式、比较宗教、田野 |
| 语言学 / Linguistics | `linguistics.md` | 句法、语义、语用、社会语言学 |
| 翻译学 / Translation | `translation.md` | 译论、机翻、口译、本地化 |
| 艺术 / Art | `art.md` | 美术史、绘画、雕塑、策展 |
| 音乐学 / Music | `music.md` | 乐理、民族音乐、表演、分析 |
| 设计学 / Design | `design.md` | 视觉、产品、UX、服务设计 |
| 建筑学 / Architecture | `architecture.md` | 城市设计、保护、参数化、性能 |
| 考古学 / Archaeology | `archaeology.md` | 遗址、器物、年代、田野 |

## 三、社会科学（Social Sciences）
| 学科（中 / EN） | 文件 | 典型关键词 |
|---|---|---|
| 心理学 / Psychology | `psychology.md` | 认知、发展、临床、实验 |
| 社会学 / Sociology | `sociology.md` | 阶层、组织、性别、网络 |
| 政治学 / Political Science | `political_science.md` | 比较政治、政党、国际关系 |
| 公共管理 / Public Administration | `public_administration.md` | 政策、治理、绩效、危机 |
| 传播学 / Communication | `communication.md` | 媒介、舆论、广告、新媒体 |
| 教育学 / Education | `education.md` | 课程、教学、测评、教育公平 |
| 经济学 / Economics | `economics.md` | 宏观、微观、发展、劳动 |
| 金融学 / Finance | `finance.md` | 资产定价、公司金融、风险 |
| 会计/商管 / Accounting & Business | `accounting.md` | 财务、审计、ESG、战略 |
| 管理学 / Management | `management.md` | 组织、营销、运营、创新 |
| 法学 / Law | `law.md` | 宪法、民法、刑法、国际法 |
| 图书馆情报 / Library & Info Science | `library_science.md` | 情报、知识组织、档案 |
| 体育学 / Sports Science | `sports_science.md` | 训练、生理、运动心理 |

## 路由规则
1. 优先精确匹配"学科族"；跨族时（如"健康经济学"）同时参考 finance/economics + public_health。
2. 方法论优先于学科细节：凡涉及"用什么方法"，先读 `research_methods.md` 及质/量深度文件。
3. 用户未说明学科时，在第 2 步追问中明确，再用通用方法文件作答。
