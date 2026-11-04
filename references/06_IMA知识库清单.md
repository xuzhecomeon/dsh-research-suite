# IMA 知识库清单（28 个 · 默认检索范围）

> **来源**：2026-09-29 通过 IMA OpenAPI 实测全量抓取（`openapi/wiki/v1/search_knowledge_base`，`query=""` 返回全部）。
> **旧版**（2026-09-15 由 ima 永久记忆导出，仅 20 个）已废止 —— 与平台现状有 5 处实质性出入，详见文末「修订记录」。
> ⚠️ **kb_id 大小写敏感**，必须从本表原样复制使用，**禁止手抄或改写大小写**（本表 ID 全部由接口原样导出，可放心复制）。
> 实例：医学教材 kb_id 中 `Toi` 的 `T` 为大写；若误用小写 `toi`，写入类接口可能返回 code 0 但 `get_knowledge_list` 报 220004 invalid knowledge_base_id，极易误判为限流或 ID 失效。

---

## ★ 能力边界（先读这条，决定任务能不能做）

实测四个核心接口在两类库上的权限**不一样**：

| 接口 | 我创建的库 | 我加入的订阅库 | 共享库 |
|---|---|---|---|
| `search_knowledge_base` 列库 | ✅ | ✅ | ✅ |
| `get_knowledge_list` 浏览目录/拿标题 | ✅ | ✅ | ✅ |
| `search_knowledge` 库内检索 | ✅ | ✅ | ✅ |
| **`get_media_info` 读取原文** | ✅ | **❌ code 220030** | 待测 |

> 订阅库读原文报错原文：`没有权限通过skill获取订阅知识库的文件，请前往ima客户端尝试`。

**推论（写任务方案时必须考虑）**：
- 订阅库（统计学 / R语言包 / 一起学统计工具 / R语言及Python辅助科研 / tidy-R语言 / R机器学习）
  只能拿到**标题级线索**，可用于「资料地图 + 定位」，**不能取正文**；正文需用户在 ima 客户端阅读。
- 能取正文的库：参考文献-个人使用、医学教材、临床指南、共识、规培+系统教材、医学研究生教材、科研绘图素材、徐吉吉的知识库。

**其他实测特性**：
- `search_knowledge` **按标题匹配**，返回的 `highlight_content` 恒为空 → 全文检索不是标题检索，别指望子串命中。
- 结果上限每次 **100 条**（传 `limit` 无效，接口不认该参数）。
- 语言必须匹配标题语言：`统计学` 库标题为英文（物理/统计预印本），中文关键词恒 0 命中，换 `regression` 才有 100 条。
- 「自己的库」浏览时，根目录 `folder_id` = `knowledge_base_id`。

---

## 一、统计 / R 语言 / 绘图相关（★ 本技能主用，共 7 个）

| # | 知识库 | 条目数 | kb_id | 类型 |
|---|---|---:|---|---|
| 1 | 统计学 | 31,830 | `RDrNZMQf4WIej_w1zEGglq__AJeetXE25i1BuanVSAA=` | 我加入的订阅库 |
| 2 | R语言包 | 22,552 | `9kwPEw2idx_jrvcWf7yTV-N6ejNk8PaTA6RMfdIWsWU=` | 我加入的订阅库 |
| 3 | 一起学统计工具 | 20,496 | `0QH3c58mnGSQBvHXIatkIN4EHvXtSmxRn9NW2p8UqIk=` | 我加入的订阅库 |
| 4 | R语言及Python辅助科研 | 869 | `fkb9NIm08tPC0AOzM1sYi3UPe1cHICmwEdjTvFVdOfk=` | 我加入的订阅库 |
| 5 | tidy-R语言 | 55 | `nEKRz-2nFUV9DVlaVpfWnhXCLV8fWSzxGp_ykgKP-h8=` | 我加入的订阅库 |
| 6 | R机器学习 | 54 | `WhaGC6TR6_W3kJ2cZJ3CqJRr-9vpxnmIuTG-AR4ZIGI=` | 我加入的订阅库 |
| 7 | **科研绘图素材** | 1,646 | `70N2Zd1YZG-s6UHaOpWfrG2UlFu7KOvwQDkvki48eBs=` | **我创建的** ← 唯一可取正文 |

**各库内容画像（实测目录）**

| 知识库 | 顶层结构 |
|---|---|
| 一起学统计工具 | 01公共统计 / 02生物医药 / 03经济统计 / 04统计物理 / 05工业质量 / 06论文科研 |
| R语言及Python辅助科研 | 代码·R语言统计代码实操 / 代码·R语言科研绘图代码实操 / 绘图·60套R语言SCI绘图模板 / 模仿·高分机器学习文献汇总 / 配色·高颜值插图和配色模仿 / 工具·AI辅助科研绘图 / 书籍·医学统计课件和书籍 ＋ 约 50 篇公众号长文 |
| tidy-R语言 | 张敬信系：R数学建模 / Tidyverse优雅编程系列 / R实验 / R书第二版新内容 ＋《R for Data Science 2e》《Advanced R 2e》等原书 |
| R机器学习 | R机器学习培训班课件 / R机器学习新书节选 / R机器学习实战 ＋《统计学习方法(李航)》《机器学习(周志华)》《ESL统计学习基础》《Tidy Modeling with R》《mlr3book》等 |
| R语言包 | CRAN 官方包帮助文档（`survival`→29 条、`ggplot2`→4 条、`dplyr`→3 条，按包名检索） |
| 统计学 | 英文预印本库（回归/方差分析/因果推断/生存），**必须用英文关键词** |
| 科研绘图素材 | 医学插图、通路图、器官图、CNS级科研绘图素材、矢量插画、配色模板 |

**检索词策略**：库内检索是标题匹配 → 中文库用中文词、英文库用英文词；查某 R 包直接输包名。

---

## 二、临床与科研写作

| # | 知识库 | 条目数 | kb_id | 类型 |
|---|---|---:|---|---|
| 8 | 临床指南 | 1,676 | `yJCFo9zzQnsia5SMPrY4hPvupeFPPG5XmiMaB34OOOI=` | 共享库（仅 2 名成员，他人无法自助加入） |
| 9 | 临床指南、共识 | 3,749 | `_fSmSpAj4AfenS767qEKobULDjYtnS80ElPaHgbeI-E=` | 我创建的 |
| 10 | 医学教材 | 261 | `DQx_-trfu--NxLbHKSSLToiEgcc4-SY2IzRcoNtA0rQ=` | 我创建的 ← 注意 `Toi` 大写 T |
| 11 | 医学研究生教材 | 102 | `N6j6YRY0D-0dQs-Ei5QMyLIvPcHizajZYsQ7vQmZRKc=` | 我创建的 |
| 12 | 规培+系统教材 | 217 | `Mat0a0tAIhijcgdfDHFdN6qw8mNqhiAtEMOtY18p40g=` | 我创建的 |
| 13 | 参考文献-个人使用 | 3,363 | `pJOAzKlATUvmT3TEUnaOfe64p6VqZwaFQPdfx9GID6k=` | 我创建的｜原「骨盆骨折-血流动力学不稳定」，2026-09 前后更名 |
| 14 | SCI论文与国自然课题科研写作 | 818 | `umUnw_qZJYDY4Ei0gp4F2xVkymmVyz3QE4yrsoJSSIQ=` | 我加入的订阅库 |
| 15 | 科普语料库 | 230 | `JI2M0_zRsJmOVhaTH5l2L4hxr9PjfN_mkb0WKQeCKAQ=` | 共享库 |

## 三、急危重症 / 卫勤

| # | 知识库 | 条目数 | kb_id | 类型 |
|---|---|---:|---|---|
| 16 | 漫学急危重症 | 159,435 | `UFkuWe9h78_ZWkr5t5PcUW2_hyQq_WR2kEBfei5ZVP8=` | 我加入的订阅库（572 人） |
| 17 | 青禾重症 | 5,280 | `ewyEbJHAOHd1J0tsBQ_gMTiFDUh9qYiwspTIVhO5ckQ=` | 我加入的订阅库（1,573 人） |
| 18 | 卫勤elite | 1,631 | `GUOsxMGt4tfddWSj5EeCXiqdQnAjMJIkyISvtZFoppi=` | 我加入的订阅库 |
| 19 | 默沙东诊疗手册-专业版 | 2,784 | `4UMMFlhkeKaZNuSk0dIOmkcyJ9UKYWH3ignyrDLAXWM=` | 我加入的订阅库 |

## 四、其他（与科研任务基本无关，仅登记备查）

| # | 知识库 | 条目数 | kb_id |
|---|---|---:|---|
| 20 | 徐吉吉的知识库 | 6 | `iTQlfj9A7WqAFGWLoNleeqS7G6Y5gfc1-Mh8_wqbgE8=` |
| 21 | 中医资料（可下载） | 1,458 | `2ORDHpUimCZDaSX7kIhg4XMEo4S7JADZ0Ffl177SPPw=` |
| 22 | 倪海厦知识库 | 1,150 | `U17TpA_MlAZieHK8EGqJrj5iR3OgRuLG5Z4mMx7oGC8=` |
| 23 | 倪海厦天人地 | 88 | `VCJVgthDtIR0_KVuwQw95vu0h0ZXDX333xikfn7oJc0=` |
| 24 | 古诗词 | 1,500 | `akCC1XoCZLIcEN8J3J9b4sPm05XA8F7Qo8MHK65plg4=` |
| 25 | 禄命文化★星命子平 | 492 | `jeZ5Ihip31Nm9--ptwPXEStVqH-uTMfeo5JSKi2FN5c=` |
| 26 | 紫微斗数知识汇集 | 102 | `OriWeXq8n9JMvMH6JGaycy5T57IIm4UdPoH1mBoGfSc=` |
| 27 | 梁湘润命理 | 176 | `OVrhy64irUoMbvjxsyP4VmjqHRW5g3k33Cf6Te__J-M=` |
| 28 | 邵雍术数★皇极铁板 | 269 | `afvS4gJo6cO3iGZoOp12s6DBsqh7kwkBej3KLE-nIeI=` |

---

## 五、默认检索规则

1. 统计 / R / 绘图类任务 → 优先检索上表 **第一节 7 个库**；其中「统计学」用英文词、「一起学统计工具」用中文词。
2. 临床方法学 / 指南依据 → 第 8–12 个库（临床指南、临床指南共识、医学教材、医学研究生教材、规培+系统教材）。
3. 本课题自有文献 → `参考文献-个人使用`（可取正文，3363 条）。
4. 出图素材与配色 → `科研绘图素材`（可取正文）。
5. 急危重症背景知识 → 青禾重症 / 漫学急危重症。
6. **凡涉及统计方法描述/勘误、样本量估算、多重比较校正、重复测量 ANOVA 球对称、判别分析、ROC** 等 → 必须优先参考「统计学」与「一起学统计工具」两库。
7. 所有检索均先 `search_knowledge`（标题级）→ 命中后判断库类型 → 自建库再走 `get_media_info` 取正文；订阅库提示用户去 ima 客户端打开。

---

## 六、修订记录

### 2026-09-29（本次实测重写）
| 变化 | 内容 |
|---|---|
| 库总数 | 20 → **28** |
| 新增（12 个） | 科研绘图素材、R机器学习、徐吉吉的知识库、中医资料（可下载）、倪海厦知识库、倪海厦天人地、古诗词、禄命文化★星命子平、紫微斗数知识汇集、梁湘润命理、邵雍术数★皇极铁板、默沙东诊疗手册-专业版 |
| **更正硬错误** | 旧版备注「R语言及Python辅助科研 = 2026-09-13 由『一起学统计工具』更名」**有误**。实测两库**并存**：一起学统计工具 20,496 条、R语言及Python辅助科研 869 条，kb_id 不同、内容不同 |
| 更名 | 「骨盆骨折-血流动力学不稳定」→ **参考文献-个人使用**（kb_id `pJOAzKlA...` 未变，条目数 3363） |
| **已从账号消失（4 个）** | 卫勤相关 `bkrPT4Ij...`、个人参考文献 `X0ErjWCr...`、热射病 `4q-eujOU...`、高质量论文知识库 `GlPXmheQ...`。⚠️ **待用户确认**：是自行退出/删除，还是接口不返回；在确认前，涉及「热射病」类任务不要假设该库存在 |
| 新增能力边界表 | 订阅库 `get_media_info` 报 220030，不可读原文（见文首） |
| 条目数更新 | 青禾重症 5280（旧记录未载）、医学教材 261 |

> **后续维护**：用户新增/退出知识库时主动告知，届时应更新本表，并同步 `~/.workbuddy/MEMORY.md` 与新建技能中的库引用。
