# Life Sciences Literature Search

通用生命科学证据检索 Skill。它把口语化科研问题结构化为“场景 + 深度 + 类型化实体 + 约束 + 交付物”，按证据维度生成查询 lane，选择具备相应能力的公开来源，并把论文、临床试验、药物、靶点和数据集作为不同对象输出。

当前版本：`2.0.0`

输出协议：`life_sciences_evidence_bundle` / `2.0`

## 现在能解决什么

| 场景 | 结构化能力 | 典型交付 |
|---|---|---|
| 通用与基础科研 | 主题、机制、模型、物种、组织/细胞、通路、方法、accession | 文献地图、机制阅读清单 |
| 靶点调研 | 人类遗传学、疾病关联、机制、表达、实验验证、可药性、模态、临床转化、安全负担 | 多维靶点评估 |
| 药物管线 | 靶点 × 适应症 × 资产 × 申办方 × 模态 × 阶段/状态 | 带 NCT 与文献关系的竞争格局 |
| 药物安全 | 药物 × 不良事件 × 适应症/人群/合并用药 | 分证据层的安全性矩阵 |
| 临床循证 | PICO、RCT、系统综述/Meta、观察性证据、安全性、亚组、在研试验、指南 | 临床证据表与证据综述底稿 |
| 方法与 benchmark | 方法 × 任务 × 数据模态 × 数据集 × 指标 × 计算约束 | 可比性与方法选型矩阵 |
| 遗传与罕见病 | 基因–疾病、HPO/表型、独立变异、病例/队列、遗传方式、功能机制、冲突证据 | 遗传证据 landscape |

遗传与罕见病是七个同级场景之一；默认路由不再因为问题中出现一个基因符号就自动把整个任务变成遗传病检索。

## 核心设计

### 深度与预算分离

`quick`、`standard`、`deep` 控制 lane、来源、每源结果、最终论文数、网页搜索建议和引用扩展，而场景只控制证据框架。

| 深度 | Lane / 来源上限 | 最终论文 | 默认扩展 | 适用情况 |
|---|---:|---:|---|---|
| `quick` | 4 / 6 | 8 | 无 | 精确查证、快速定向、初步阅读 |
| `standard` | 14 / 12 | 20 | 仅弱结果时做一次 seed-based related fallback | 默认研究简报、证据表、常规调研 |
| `deep` | 32 / 21 | 40 | 一轮引用 + 相似文献 | landscape、负面/冲突证据、深度调研 |

每源记录总上限为 quick/standard/deep 的 8/15/30，单 lane 请求上限为 6/12/20，每源调用上限为 4/8/16；这些是整次执行额度，不会按 lane 重置。审计会同时写出计划 source operations、实际调用和因预算跳过的 lane。

### 能力感知的来源路由

四个常开核心索引是 Europe PMC、PubMed、Semantic Scholar 和 OpenAlex。场景按需加入 PubTator3、Open Targets、GWAS Catalog、ClinicalTrials.gov、Reactome、UniProt、LitVar2、ClinVar、ClinGen、CIViC、Crossref、DataCite、arXiv、DBLP、DOAJ、OpenAIRE、CORE 等适用来源。

每个 source 只执行被路由给它的 lane，不做全来源 × 全查询笛卡尔积。一个来源失败、限流或跳过时，其他来源结果仍会保留，并在审计中明确披露。

### 保守术语归一化

当前可使用 HGNC、OLS4（MONDO/HPO/ChEBI/GO/CL/UBERON）、ChEMBL、MeSH、NCBI Taxonomy 和受控研究设计词。只自动接受精确 ID、精确标签或唯一精确同义词；模糊、歧义、失败和超时都保留用户原词。ChEMBL 当前用于保守的分子身份解析，不会自动推导药物靶点、活性谱或治疗模态。

可通过 `--terminology-dir` 提供本地 `inn.json`、`meddra.json`、`cmesh.json`、`atc.json`、`edam.json`、`obi.json`、`therapeutic_modality.json` 和 `sponsor_aliases.json`。项目不捆绑 MedDRA 等授权词表。`--include-descendants` 最多加入 20 个经审计的 OLS 下位概念，不做无界树形扩展。`--mesh-heading` 必须与 `--mesh-subheading` 成对使用，生成明确的 PubMed 限定主题词 lane。

### 一等证据对象

输出不是一个混杂的“结果列表”：

- `papers`：论文/预印本及书目信息、摘要支持、排序和跨源 provenance；
- `trials`：ClinicalTrials.gov 注册号、阶段、状态、申办方、干预、入组、日期和国家；
- `drugs`：规范药物身份、别名、商品名/研发代号、模态；
- `targets`：规范靶点/基因/蛋白身份；
- `datasets`：GEO/SRA/ArrayExpress 规范 accession 或 DataCite 数据集；
- `relations`：有匹配 PMID 且论文已进入 bundle 时自动生成 trial–paper；试验干预名与规范药名精确一致时自动生成 `trial_tests_drug`。Schema 还可表达 drug/target/dataset–paper 等关系，但检索器不会凭实体共现自动生成它们。

Trial 不是 paper，数据库关联也不是论文结论。Open-access URL 只表示可访问，不表示全文已读取。

### 可追溯输出

默认 JSON 是完整 schema-v2 证据包，包括：原始请求、归一化、检索计划、source routes、每次调用状态、检索账本、失败/降级、对象、关系、result sets、synthesis 和校验计数。

另外支持：

- 中文、英文、中英双语 Markdown 表格；
- 只渲染已有证据 claims 的 Markdown review；
- BibTeX、RIS、CSL-JSON，仅导出符合引用资格的论文；
- Vancouver、Nature、AMA 参考文献显示样式；
- `--out` 保存主输出，`--audit-out` 同时保存 canonical JSON。

## 环境要求

- Python 3.10+；
- 可访问公开 API 的 HTTPS 网络；
- 检索运行时不要求第三方 Python 包；
- 所有 API key 都是可选增强，CORE 除外（没有 key 时自动跳过）。

可选环境变量：

```bash
export LITERATURE_CONTACT_EMAIL='research@example.org'
export OPENALEX_API_KEY='...'
export NCBI_API_KEY='...'
export SEMANTIC_SCHOLAR_API_KEY='...'
export CORE_API_KEY='...'
export OPENCITATIONS_ACCESS_TOKEN='...'
```

`LITERATURE_CONTACT_EMAIL` 用于 polite API pool，也是 Unpaywall 所需配置。密钥不会进入输出，错误信息会脱敏。

## CLI 概览

入口按场景使用子命令：

```text
search_literature.py
├── auto       自动识别主场景
├── general    通用/基础科研
├── target     靶点调研
├── pipeline   药物管线
├── safety     药物安全
├── clinical   临床循证
├── methods    方法与 benchmark
└── genetic    遗传与罕见病
```

查看接口：

```bash
python3 scripts/search_literature.py --help
python3 scripts/search_literature.py target --help
```

所有子命令共享：

- `--depth quick|standard|deep`；
- `--also <scenario>` 增加一个辅助场景；
- `--concept TYPE=VALUE` 增加任意类型化实体；
- 年份、文献类型、作者、venue、语言、物种、稳定 ID、OA、摘要、预印本和撤稿过滤；
- `--sort relevance|newest|citations`；
- `--expansion auto|none|related|citations|both`；
- `--format json|table|review|bibtex|ris|csl-json`；
- `--view papers|trials|drugs|targets|datasets`；
- `--output-language zh|en|bilingual`；
- `--dry-run`、`--out`、`--audit-out`。

每个场景另有更易读的专用实体参数，例如 `target --target/--indication`、`safety --drug/--adverse-event`、`clinical --population/--intervention/--outcome`。参数可重复。

## 快速开始

### 1. 自动路由与 dry run

先看将运行哪些 lane 和 source，不访问外部服务：

```bash
python3 scripts/search_literature.py auto \
  '比较空间转录组细胞分割方法及公开 benchmark' \
  --depth standard \
  --concept task='cell segmentation' \
  --concept data_modality='spatial transcriptomics' \
  --dry-run \
  --out /tmp/spatial-plan.json
```

### 2. 靶点多维调研

```bash
python3 scripts/search_literature.py target \
  '评估 PCSK9 在动脉粥样硬化性心血管病中的成药价值' \
  --target PCSK9 \
  --indication 'atherosclerotic cardiovascular disease' \
  --depth deep \
  --format table \
  --output-language zh \
  --out /tmp/pcsk9-target.md \
  --audit-out /tmp/pcsk9-target.json
```

### 3. 管线与试验对象

```bash
python3 scripts/search_literature.py pipeline \
  'PCSK9 靶点在高脂血症中的全球在研资产和试验' \
  --target PCSK9 \
  --indication hypercholesterolemia \
  --status RECRUITING \
  --depth standard \
  --format table \
  --view trials
```

### 4. 药物安全

```bash
python3 scripts/search_literature.py safety \
  'trastuzumab deruxtecan 相关间质性肺病的证据' \
  --drug 'trastuzumab deruxtecan' \
  --adverse-event 'interstitial lung disease' \
  --indication 'HER2-positive breast cancer' \
  --depth standard \
  --format table
```

若有授权 MedDRA/本地药物映射：

```bash
python3 scripts/search_literature.py safety \
  'T-DXd pulmonary toxicity' \
  --drug T-DXd \
  --adverse-event pneumonitis \
  --terminology-dir /path/to/authorized-terminology \
  --audit-out /tmp/tdxd-safety.json
```

### 5. 临床循证

```bash
python3 scripts/search_literature.py clinical \
  'BRAF V600E 黑色素瘤靶向治疗的近五年临床证据' \
  --condition melanoma \
  --biomarker 'BRAF V600E' \
  --intervention 'BRAF inhibitor' \
  --outcome 'overall survival' \
  --study-design RCT \
  --year-from 2021 \
  --sort citations \
  --format table
```

### 6. 方法与数据集

```bash
python3 scripts/search_literature.py methods \
  '单细胞细胞类型注释方法 benchmark' \
  --task 'cell type annotation' \
  --data-modality 'single-cell RNA-seq' \
  --dataset GSE132044 \
  --metric F1 \
  --depth deep \
  --view datasets \
  --format table
```

DataCite 返回的 dataset/collection 会保留为 `dataset` 对象，不进入论文集合。

### 7. 遗传与罕见病

```bash
python3 scripts/search_literature.py genetic \
  'SCN1A c.5387G>A 与 Dravet 综合征的病例和功能证据' \
  --gene SCN1A \
  --disease 'Dravet syndrome' \
  --variant 'c.5387G>A' \
  --phenotype seizures \
  --inheritance 'de novo' \
  --depth standard \
  --format table
```

每个 variant/allele 默认独立。`variant + gene + disease` 严格 lane 只有在同一 source 成功且返回零条后，才允许该 source 执行 `variant + gene` 宽松回退。

## 过滤、MeSH 与层级扩展

常用过滤示例：

```bash
python3 scripts/search_literature.py clinical \
  'checkpoint inhibitor adjuvant melanoma' \
  --condition melanoma \
  --intervention 'immune checkpoint inhibitor' \
  --year-from 2020 \
  --publication-type 'Randomized Controlled Trial' \
  --language eng \
  --require-identifier pmid \
  --require-abstract \
  --exclude-preprints \
  --sort newest
```

同一字段的重复值按 OR，字段之间按 AND。部分来源原生执行过滤，其他来源只在有界候选集上复核；支持程度写入 route audit。

限定 MeSH 组合：

```bash
python3 scripts/search_literature.py clinical \
  'melanoma drug therapy evidence' \
  --mesh-heading Melanoma \
  --mesh-subheading 'drug therapy' \
  --dry-run
```

`--include-descendants` 只对已接受的 OLS 概念启用，最多 20 个下位词。不要为精确 ID 查询或高歧义概念默认开启。

## Agent 网页检索接入

Python CLI 不直接调用宿主 Agent 的浏览器。Agent 可以围绕所选场景执行少量、实质不同的查询，核对规范标题和 ID 后导入：

```bash
python3 scripts/search_literature.py target \
  'PCSK9 target assessment' \
  --target PCSK9 \
  --indication atherosclerosis \
  --web-results /tmp/pcsk9-web.json \
  --audit-out /tmp/pcsk9-bundle.json
```

输入合同见 [references/web-search-input.md](references/web-search-input.md)。网页 snippet 只是发现线索；只有显式 `abstract` 字段才能形成摘要支持，`metadata_verified` 也只表示书目信息已核对。

## 综述与引文导出

检索 CLI 不会从标题自动生成“关键发现”。`--format review` 在没有 synthesis 时会明确说明，并回退为事实结果。

Agent 完成摘要/全文证据阅读后，可单独准备符合 schema 的 `synthesis.json`，再附加、校验并渲染：

```bash
python3 scripts/render_evidence.py /tmp/pcsk9-bundle.json \
  --synthesis /tmp/pcsk9-synthesis.json \
  --save-bundle /tmp/pcsk9-reviewed.json \
  --format review \
  --language bilingual \
  --citation-style nature \
  --out /tmp/pcsk9-review.md
```

引文导出：

```bash
python3 scripts/render_evidence.py /tmp/pcsk9-reviewed.json \
  --format bibtex \
  --out /tmp/pcsk9.bib
```

BibTeX、RIS 和 CSL-JSON 只包含具备稳定 ID 且通过书目核验的 paper，不会把 trial、drug、target 或 dataset 伪装成参考文献。

## 工程结构

旧的单文件实现已拆成薄入口与职责明确的包：

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── search_literature.py          # 薄 CLI 入口
│   ├── render_evidence.py            # 证据包校验、synthesis 附加和渲染
│   └── literature_search/
│       ├── cli.py                    # v2 参数与请求构造
│       ├── models.py                 # 请求、概念、预算、lane、route 合同
│       ├── budgets.py                # quick / standard / deep
│       ├── normalizers.py            # 通用术语归一化
│       ├── source_packs.py           # 场景来源能力包
│       ├── planner.py                # 检测、规划、路由和校验
│       ├── scenarios/                # 七个独立场景 planner
│       ├── registries/               # ClinicalTrials.gov、Open Targets、DataCite 一等对象
│       ├── adapter_contracts.py       # adapter 输入、结果与失败契约
│       ├── backend.py                # HTTP transport、论文源 adapters、多 lane source runner
│       ├── reconciliation.py         # 论文身份归并、过滤、验证与 RRF
│       ├── audit.py                  # source status 与检索账本
│       ├── execution.py              # 执行编排与 bundle 构造
│       ├── evidence.py               # 类型化证据对象与 relations
│       ├── schema.py                 # schema-v2 不变量校验
│       └── renderers/                # Markdown / BibTeX / RIS / CSL-JSON
├── references/
│   ├── intent-and-depth.md
│   ├── query-planning.md
│   ├── evidence-and-output.md
│   ├── sources.md
│   ├── output-schema.md
│   ├── web-search-input.md
│   └── lanes/                        # 七场景说明
└── tests/                            # 仅源码仓库；Release 归档不包含
```

原 6500 多行单文件不再承担 CLI、遗传专项 planner、归一化、去重、审计和 Markdown 输出。高变更率的场景、术语、规划、执行、Schema、证据对象和渲染均已独立；新增方向通常只需要增加 scenario planner、source pack、reference 和相应测试。`backend.py` 仍集中保存 20 多个共享论文源 adapter，这是下一步可按 biomedical / scholarly / specialist / expansion 家族继续拆分的明确技术债，但它已不再决定任何场景或输出合同。

## 开发与验证

以下命令用于完整源码仓库。标准 Git archive 通过 `export-ignore` 排除测试与 Git 开发元数据；工蜂 Release 标签另指向一个以源码提交为父节点的精简 distribution tree，只保留运行 Skill 所需的 README、SKILL、agents、references 和 scripts。源码分支仍完整保留测试与开发配置。

```bash
ruff check scripts tests
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts
```

专项测试覆盖七场景检测与 lane 合同、深度预算、来源路由、非人 species、遗传严格/宽松回退、术语归一化、ClinicalTrials/DataCite 一等对象、schema-v2 边界、引用资格、中英双语 Markdown 与 BibTeX/RIS/CSL-JSON。

退出码：`0` 表示 dry run 或至少一条 route 成功；`2` 表示参数、校验或输入错误；`3` 表示正式运行中没有任何 route 成功。

## 明确边界

- 这是有界证据发现，不是穷尽性系统综述，也不承诺 recall 完整。
- 当前自动读取的内容以元数据和 API 返回摘要为主；不会自动抓取、解析和评审全文。
- 检索排序不是证据等级；引用数不是研究质量；自动化不会替代风险偏倚评估。
- review renderer 只渲染已有 synthesis，不会从标题或 snippet 编造研究结论。
- Trial status、管线状态、监管信息会变化，必须携带检索时间并对重要事实核对 canonical source。
- 药物警戒检索可以由宿主自动化定期调用，但本项目自身没有调度器、监控服务或常驻进程。
- 不接入 Sci-Hub，不绕过付费墙、登录、robots、限流、地区限制或受控访问治理。
- 不捆绑 MedDRA、WHO INN/CMeSH 等授权或本地词表；未配置时明确降级。
- 不把药名自动推导成靶点、活性或模态关系；这些关系需要权威对象、显式 relation 或人工核验。
- bioRxiv/medRxiv 预印本通过 Europe PMC、广域索引或定向网页搜索发现，当前没有独立关键词 adapter。
- 不进行临床诊断、医疗建议、ACMG/AMP 变异分类或自动 benefit–risk 决策。
- 不管理本地全文库，也不依赖 GenDiaMcp、GenDiaRag 或其他私有服务。

Agent 行为入口见 [SKILL.md](SKILL.md)，完整来源能力见 [references/sources.md](references/sources.md)，字段级输出合同见 [references/output-schema.md](references/output-schema.md)。
