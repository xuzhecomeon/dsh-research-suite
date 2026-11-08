# 识别层评测说明（v3.2.0）

本文说明 `data/golden/` 下三套数据的划分、防污染机制、指标定义与门槛，以及最近一次运行的结果。
所有数字都来自本机单次运行，命令与原始输出可复现；本文不构成第三方验证。

## 一、为什么要把「50 条金标准集」拆成两套

v3.1 发布时只有 `data/golden/cases.json`（50 条，负例 5 条），它有三个结构性问题：

1. **自证集**：题目与 `data/match-rules.json` 的 `cues` 是同一批人、同一轮写出来的，规则里的 `re` 往往直接照抄题面里出现的词。于是「跑一遍 golden 集」只是在检验规则能不能命中自己抄来的词，不检验识别层对新表述的泛化能力。
2. **没有负例规模**：50 条里只有 5 条非科研诉求，误接管率的分母太小（5），一条误判就是 20%，指标失去分辨力。
3. **没有调参/盲测的物理隔离**：改参数的人看得到全部题目，任何指标都可以「看着调上去」，发布时报出的数字没有预测意义。

v3.2.0 因此改为 **dev / test 双集 + 冻结哈希**，并明确一条纪律：**dev 用来调参，可以随时增删改；test 一经冻结不得修改，只在最后跑一次**。评审给出的真实失败样例（12 条）全部放进 dev，不进 test——它们已经被写规则的人看过，进 test 就等于泄题。

## 二、三集划分

| 集合 | 文件 | 条数 | 用途 | 是否可改 |
| --- | --- | --- | --- | --- |
| dev（调参集） | `data/golden/dev.json` | 150（负例 51） | 改 `lib/core.js` / `data/match-rules.json` 时看效果；含 12 条评审真实失败样例原话 | 可以随时增删改 |
| test（盲测集） | `data/golden/test.json` | 150（负例 82） | 只在收尾时跑；sha256 冻结在 `data/golden/.freeze.json` | **冻结后不可改**，改一个字符 `verify-eval.mjs` 即失败 |
| holdout（留出集） | 待建 | — | 由未参与写题的人按同一族谱另写一套，用于发布前的最终确认 | 未开始，见 §七 |

`data/golden/cases.json`（v3.1 的 50 条）保留作历史，只参与「重复检查」，不再作为发布指标。

两集的 category 覆盖与来源分布（`node scripts/verify-eval.mjs` 每次都会打印）：

- 正例覆盖 10 个科研域 + 多域混合；负例覆盖 11 类真实非科研意图（教育辅导、商务文案、家庭事务、临床问诊、情感写作、通用软件、生活事务、投资理财、行政事务、娱乐追剧、求职面试）。
- `source` 三个取值都必须出现且单类占比 ≤40%：`constructed`（直接构造）、`paraphrase`（改写旧集/规则表述）、`real-ish`（模拟真实对话日志口吻）。
- test 负例 ≥80 条、负例类 ≥10 类且每类 ≥5 条，由 `verify-eval.mjs` 硬断言。

> 关于 `source`：它是**作者声明的构造方式**，不是外部审计过的事实标签。它约束的是「别把同一句话换个说法算三个样本」，不能让一套自建的 150 条变成独立数据。真正的独立性只能来自 holdout 与第三方。

## 三、防污染机制（`scripts/verify-eval.mjs`）

CI 级断言，任一不过即 `exit 1`：

| 检查 | 阈值 | 目的 |
| --- | --- | --- |
| 句子级完全重复（集内 / dev↔test / 对旧 `cases.json`） | = 0 | 防止同题复用，也防止 test 抄 dev |
| 字符 3-gram 集合重叠率（test→dev、dev→test 双向） | < 5% | 完全重复抓不住「换两三个字的同一题」，3-gram 能抓 |
| test 与 `match-rules.json` 的 cue 长字面（≥6 汉字候选式） | 命中 = 0 | 防止题面直接抄规则表措辞（这就是 v3.1 自证集的根因） |
| test.json sha256 | 必须等于 `.freeze.json` 的 `sha256` | 改一个字符即失败，杜绝「跑完顺手修题」 |
| test 是否出现评审真实失败样例 | 必须为 0 | 泄题检查 |
| dev 是否含 12 条评审真实失败样例 | 必须 12/12 | 防止把专家给的原话弄丢 |
| 条数、id 唯一与 id 空间不相交、`expect.cap`/`alts` 在 `data/capabilities` 中真实存在 | 结构断言 | 防止指到不存在的卡 |

关于 cue 检查的口径（重要，且是刻意的）：只有 **≥6 汉字的候选式**（如「写一份正式的审稿意见」「参考文献格式」）算泄漏证据；3～5 字的专业名词（参考文献、样本量、机制图、生存曲线）在真实科研口语里必然出现，若也判违规，就会逼着出题人把句子改得不像人话，反而降低盲测的效度。这些短字面重合会在输出里以 `W-CUE-SHORT` 计数公示，不计入违规。

冻结记录（`data/golden/.freeze.json`）：

```json
{
  "frozenAt": "2026-11-08",
  "sha256": "81a1e83bbbd6ff83322e7900f883d67cfb1db2125f114b4088a43ae91d0e4961",
  "count": 150,
  "negatives": 82,
  "categories": ["..."]
}
```

重新冻结必须显式 `--force`，且应在 `CHANGELOG` 里说明理由——改 test 等于换测试集，旧数字全部作废。

## 四、指标定义与门槛

`scripts/eval-match.mjs` 逐条调用 `core.matchCapabilities()`，先判「该不该接管」，再判「接管到哪张卡」。

| 指标 | 定义 | 发布门槛（`--strict`，仅 test） |
| --- | --- | --- |
| 接管判定准确率 | (科研诉求被接管 + 非科研诉求未接管) / 全部 | ≥ 0.92 |
| 误接管率 | 非科研诉求被接管的条数 / 非科研诉求条数 | ≤ 0.03 |
| 科研诉求召回 | 科研诉求被接管的条数 / 科研诉求条数 | ≥ 0.90 |
| 卡 top1 | 候选第一位命中期望卡（cap 或 alts）/ 科研诉求条数 | ≥ 0.80 |
| 卡 top3 | 候选前三位含期望卡 / 科研诉求条数 | ≥ 0.95 |

两条口径说明：

1. **top1/top3 在 `candidates` 上算，不要求接管成功**。识别层的 `matches` 只在接管时非空，若只在 `matches` 上算 top-k，「漏接管」会同时打穿三个指标，掩盖「接对了但排错」这类独立问题。附加的 `top1WhenTaken`/`top3WhenTaken` 单独反映排序质量。
2. **`--set dev` 永不受 `--strict` 影响**。调参集一旦参与门禁，就会变成对着门槛调题，test 随之失效。`--strict` 打在 dev 上时脚本会打印提示并按设计忽略。

失败归因分四类：`漏接管`（该接管没接管）、`误接管`（不该接管却接管）、`域错`（接管了但域判错）、`卡错`（域对但卡不在前三位）。

## 五、怎么跑

```bash
# 1) 校验数据（结构、组成、去重、3-gram、cue 泄漏、冻结哈希）
node scripts/verify-eval.mjs
node scripts/verify-eval.mjs --json          # 机器可读
node scripts/verify-eval.mjs --freeze        # 生成冻结记录（已存在时需 --force）

# 2) 评估识别层
node scripts/eval-match.mjs --set dev                 # 调参集：只报数，exit 0
node scripts/eval-match.mjs --set test                # 盲测集：只报数
node scripts/eval-match.mjs --set test --strict       # CI 门禁：五项不达标 exit 1
node scripts/eval-match.mjs --set test --json         # 供 CI 解析
node scripts/eval-match.mjs --set test -v             # 逐条明细
```

`--strict` 失败时脚本会逐项打印「实际值 vs 门槛 vs 差多少」，**不调门槛、不挑数据**。

## 六、最近一次运行（2026-11-8 18:34:32）

运行环境：HEAD `7de62c4`，工作树有未提交改动（`lib/core.js`、`data/match-rules.json` 正被 Lead 换成「能力卡全文 BM25 + accept/ask/reject 三出口」）。**本节的数字是那一刻的现场快照**，重建期间指标会逐次变动（同一份数据相邻两次运行，失败条数从 37 变到 48），所以引用时必须连快照时间一起引用。

| 指标 | dev（150） | test（150） | 门槛（仅 test） |
| --- | --- | --- | --- |
| 接管判定准确率 | 93.3% | 86.7% | ≥92% |
| 误接管率 | 0.0% | 17.1% | ≤3% |
| 科研诉求召回 | 89.9% | 91.2% | ≥90% |
| 卡 top1 | 74.8% | 66.2% | ≥80% |
| 卡 top3 | 87.9% | 79.4% | ≥95% |
| 域正确率（辅助，无门槛） | 76.8% | 72.1% | — |
| 接管成功时 top1 / top3 | 78.6% / 89.9% | 69.3% / 80.7% | — |

失败结构：dev 19 条（漏接管 10 / 卡错 1 / 域错 8）；test 32 条（卡错 2 / 漏接管 6 / 域错 10 / 误接管 14）。

判读（只陈述这次运行能支持的话）：

1. 本次失败的主项是「误接管」：test 32 条里 卡错 2 / 漏接管 6 / 域错 10 / 误接管 14。排序与决策的可分离性看两个数：全量 top1 66.2% / 接管成功时 top1 69.3%，全量 top3 79.4% / 接管成功时 top3 80.7%。接管成功时的排序分并不比全量高多少，说明这次掉分主要不在「没接管」，而在「接错了」——出口判定偏松、域判别也不稳。
2. 这次运行的 `--strict` 退出码是 **1**（1 = 有指标不达门槛），五项差值见 §五 的原始输出；门槛未调、数据未挑。
3. 识别层正在换装，本表不能当作新层成绩，只能当作「换装中途」的对照点；等新层落定必须整节重跑替换。

## 八、附录：最近一次 test 全部失败条目

快照：2026-11-8 18:34:32。共 32 条失败（卡错 2 / 漏接管 6 / 域错 10 / 误接管 14）。

| # | id | 类别 | 原话 | 期望 | 实际 | 候选前三 | 归因 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | t005 | 写作 | 结构化摘要的四个部分写不齐，帮我补齐 | writing / writing.abstract（含 alts） | writing / writing.evidence | writing.evidence > literature.close-read > format.typeset | 卡错 |
| 2 | t008 | 写作 | 全篇五章的逻辑顺序想重新排，怎么做 | writing / writing.blueprint（含 alts） | 不接管 | polish.en > writing.blueprint > writing.citation | 漏接管 |
| 3 | t011 | 润色 | 英文段落被说太啰嗦，能不能压掉三分之一字数 | polish / polish.en（含 alts） | review / review.selfcheck | review.selfcheck > review.referee > review.rebuttal | 域错 |
| 4 | t012 | 润色 | 两段内容高度相似，答辩时被问是不是凑字数 | polish / polish.rewrite（含 alts） | slides / slides.journal-club | slides.journal-club > slides.conference-defense > slides.auto-build | 域错 |
| 5 | t019 | 统计 | 十几篇队列研究，想把 HR 合起来 | stats / stats.meta（含 alts） | ideation / ideation.design | ideation.design > ideation.question > ideation.ethics | 域错 |
| 6 | t026 | 绘图 | 箱线图想按分组上色，图例放右侧 | figures / figures.statplot（含 alts） | 不接管 | stats.twogroup > figures.mechanism > stats.baseline | 漏接管 |
| 7 | t028 | 绘图 | 投稿要求线宽不小于一磅，帮我查一下 | figures / figures.audit（含 alts） | format / format.doc-audit | format.doc-audit > format.submission-package > format.final-delivery | 域错 |
| 8 | t030 | 文献 | 两个学生分别筛，分歧怎么处理 | literature / literature.screen-prisma（含 alts） | stats / stats.survival | stats.survival > stats.missing > stats.clean | 域错 |
| 9 | t033 | 文献 | 把十篇文献的结论做成矩阵表 | literature / literature.evidence-matrix（含 alts） | literature / literature.doi-validate | literature.doi-validate > literature.critique > writing.review | 卡错 |
| 10 | t034 | 文献 | 引文里有一篇撤稿了，怎么发现 | literature / literature.fact-check（含 alts） | 不接管 | format.intext-cite > ideation.topic > writing.citation | 漏接管 |
| 11 | t035 | 格式 | 参考文献的期刊缩写要统一成 ISO 格式 | format / format.ref-style（含 alts） | 不接管 | format.ref-style > writing.citation > format.intext-cite | 漏接管 |
| 12 | t038 | 格式 | 整篇要改成双栏排版，图表位置会乱 | format / format.typeset（含 alts） | 不接管 | format.figtable > writing.figure-table > format.typeset | 漏接管 |
| 13 | t039 | 格式 | 编辑部给了作者须知，帮我逐条对一遍 | format / format.journal-fit（含 alts） | review / review.report | review.report > figures.vector > format.ref-style | 域错 |
| 14 | t043 | 审稿 | 正文和补充材料里的样本量不一致，核一下 | review / review.audit（含 alts） | writing / writing.figure-table | writing.figure-table > format.figtable > format.submission-package | 域错 |
| 15 | t047 | 选题 | 科室没有方向，想找几个可以做的点 | ideation / ideation.topic（含 alts） | 不接管 | ideation.topic > data.gwas-eqtl > ideation.novelty | 漏接管 |
| 16 | t050 | 选题 | 单中心还是多中心，样本来源怎么定 | ideation / ideation.design（含 alts） | literature / literature.close-read | literature.close-read > stats.diagnostic > data.pathway-ppi | 域错 |
| 17 | t055 | 幻灯 | 周会要讲自己的结果，幻灯怎么组织 | slides / slides.journal-club（含 alts） | data / data.expression-reuse | data.expression-reuse > review.selfcheck > writing.zh-imrad | 域错 |
| 18 | t060 | 数据 | 同一基因在不同库里名字不一样，怎么统一 | data / data.gene-idmap（含 alts） | slides / slides.consistency | slides.consistency > data.expression-reuse > literature.federated-search | 域错 |
| 19 | t070 | 教育辅导 | 帮我把这段英语课文翻译成中文 | 不接管 | polish / polish.en | polish.en > stats.reportaudit > writing.zh-voice | 误接管 |
| 20 | t075 | 教育辅导 | 帮孩子改改演讲稿，学校比赛用 | 不接管 | writing / writing.zh-voice | writing.zh-voice > slides.speaker-notes > writing.en-sci | 误接管 |
| 21 | t078 | 商务文案 | 小红书笔记怎么写更容易被收藏 | 不接管 | slides / slides.journal-club | slides.journal-club > writing.zh-imrad > writing.discussion | 误接管 |
| 22 | t079 | 商务文案 | 产品说明书改得口语一点 | 不接管 | writing / writing.zh-voice | writing.zh-voice > polish.voice > polish.audit | 误接管 |
| 23 | t082 | 商务文案 | 客户投诉回复函怎么写显得专业 | 不接管 | writing / writing.case-report | writing.case-report > writing.thesis > review.rebuttal | 误接管 |
| 24 | t088 | 家庭事务 | 全家过年回谁家，怎么安排 | 不接管 | writing / writing.blueprint | writing.blueprint > stats.psm > stats.regression | 误接管 |
| 25 | t098 | 临床问诊 | 这个中药方子能不能长期吃 | 不接管 | data / data.provenance | data.provenance > ideation.feasibility > ideation.design | 误接管 |
| 26 | t102 | 情感写作 | 道歉短信怎么写才诚恳 | 不接管 | review / review.rebuttal | review.rebuttal > literature.federated-search > literature.search-plan | 误接管 |
| 27 | t110 | 通用软件 | 手机上照片怎么批量传到电脑 | 不接管 | literature / literature.library | literature.library > format.ref-bridge > figures.imaging | 误接管 |
| 28 | t111 | 通用软件 | 网站打不开提示证书错误 | 不接管 | literature / literature.fulltext-acquire | literature.fulltext-acquire > literature.doi-validate > format.doc-audit | 误接管 |
| 29 | t112 | 通用软件 | git 冲突怎么解决 | 不接管 | stats / stats.meta | stats.meta > stats.interpret > format.submission-package | 误接管 |
| 30 | t113 | 通用软件 | 打印机连不上无线网 | 不接管 | literature / literature.federated-search | literature.federated-search > figures.style > slides.speaker-notes | 误接管 |
| 31 | t117 | 生活事务 | 明天出门要不要带伞 | 不接管 | figures / figures.statplot | figures.statplot > literature.citation-chase > format.submission-package | 误接管 |
| 32 | t137 | 行政事务 | 会议通知怎么写 | 不接管 | slides / slides.conference-defense | slides.conference-defense > writing.zh-imrad > writing.discussion | 误接管 |

误接管（本该不接管却接管）的条目都在上表里，共 14 条；它们是最该先看的一类，因为它们的代价比漏接管高——一张错卡会让下游按错误的 SOP 干活。
## 七、局限（必须与数字一起引用）

1. **样本只有 150 条**，单次运行，类别内样本量 4～14 条；每一条错判就能让某类召回跳动 7～25 个百分点，95% 置信区间很宽。
2. **不是第三方验证**：题目、期望标签、失败归因都由本会话产出，存在系统性盲点（我看不到我看不到的东西）。
3. **负例来自构造**，不是从真实用户日志抽样；真实分布里「科研/非科研」的比例未知，误接管率不能直接外推到线上。
4. **dev 集可被反复调参**，所以 dev 数字只能看相对变化，不能当发布指标；发布指标只认 test。
5. **test 的冻结只防「跑完改题」**，防不住「出题时已知规则表」。这一条只能靠 holdout 消除——由未参与写题的人按同一族谱另写 150 条，且同样冻结后只跑一次。
6. 评测对象是**识别层**，不是下游执行质量。接管的卡对不对，与「按这张卡的 SOP 做完做得好不好」是两件事，后者目前没有评测。

