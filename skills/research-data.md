---
name: research-data
description: 科研数据获取、注释与取数留痕的融合 SOP。把「要一批数据」推到「拿到可核对、可复跑的本地数据集」：先定标识符与坐标体系，再按证据等级选库取数，随后做变异／表达／通路／结构的注释与标准化，最后落 manifest、版本号与本地处理声明。覆盖 NCBI（Gene／GEO／ClinVar）、Ensembl／UniProt／STRING／KEGG／Reactome、GWAS Catalog／gnomAD／ClinPGx／JASPAR、GTEx／cBioPortal／DepMap／Open Targets、PDB／AlphaFold／InterPro、PubChem／ChEMBL／BindingDB／ZINC、HMDB／Metabolomics Workbench、ENA 共 33 个可直连数据源。
whenToUse: 用户说要下载／检索／整合一批科研数据（公共数据库取数、GEO 数据集复用、变异注释、表达矩阵整理、批量 ID 转换、通路与互作网络取数、结构与化合物检索、代谢组数据合并、外部数据集对齐变量），或者要一份能复跑的取数记录与数据字典时使用。只做统计建模、只画图、只写文献综述时不要用本技能。
---

# research-data：科研数据获取、注释与取数留痕

本技能是 data 域的融合 SOP。v2 没有这个域，v3 从零建：源技能里 33 个是可直连的数据源（REST／FTP／GraphQL／官方 Python 包），7 个因为要付费账号、要人工登录或要上传个体级数据被降级，5 个与取数无关被划到别的域。判定记录在同目录的 `data/ledger/data.json`，能力卡在同目录的 `data/capabilities/data.json`。

## 一、本域边界

- **做取数，不做推断**。本域交付的是「数据集 + 数据字典 + 取数记录」，不是 p 值、不是通路富集结论、不是模型系数。拿到数据之后的检验交给 `research-stats`。
- **能直连的才进流程**。官方 REST／FTP／GraphQL／本地 pip 包可以直接写进 protocol；要注册账号、要人工登录浏览器、要把文件传到第三方平台的，一律不进主流程，只作替代方案说明。
- **字段名与版本号只能抄库文档**。不许凭印象写「GEO 有 survival 字段」这类字段。写作前在库正文或返回结果里核对字段名，核对不到就不写。
- **个体级数据只在本地**。变异、表达、临床、代谢组里的个体级记录，只在本机磁盘与本机进程之间流转；上传云实验室、云平台或在线接口前必须脱敏并停下确认。
- **凭据不进脚本**。token、邮箱密码、API key 走环境变量或 `~/.Renviron`，不写进 .py／.R／.md，不进仓库；在仓里发现明文凭据先轮换再继续。
- **与相邻域的交界**：文献检索式与引文管理交 `research-literature`；统计建模与数据闸门交 `research-stats`（DG1–DG6 在本域取数完成后接手）；组学数据的成图交 `research-figures`；取数结果写进论文的方法与数据可得性声明交 `research-writing`。

## 二、融合对比表

| 能力 | 主用技能 | 关键长处 | 明确短板 | 融合取舍 |
|---|---|---|---|---|
| 基因与蛋白标识符对齐 | `gene-database` | 符号／Entrez／GO／染色体定位检索齐全，Datasets API 一次给全套 | 只管 NCBI 自己的命名体系，跨库映射要另找 | 以 NCBI 为枢纽取 Entrez，再用 `uniprot-database` 的 ID mapping 换蛋白号 |
| 变异注释与分级核对 | `clinvar-database` | 分级与审核星级齐全，E-utilities 与 FTP 双通道 | VCF 不含大于 10kb 与复杂结构变异；VUS 占比高 | 频率核对固定交 `gnomad-database`，药物基因组注释交 `clinpgx-database` |
| GWAS 汇总统计与工具变量 | `gwas-database` | 研究／关联／汇总统计三层接口加 FTP 批次目录 | 汇总统计列名与 build 各研究不一致，需要逐批核对 | 取数用 REST，clump 与 F 值计算本地做，不碰在线 API token |
| 组学数据下载与整理 | `geo-database` | GSE 层级、GEOparse 本地缓存、矩阵透视都讲得细 | 原始读段在 GEO 侧信息不全，补充文件格式各异 | 表达矩阵走 GEO，原始读段走 `ena-database` 的直链 |
| 外部表达与依赖性数据集复用 | `gtex-database` | 组织层中位表达与样本数可批量取，口径清楚 | 只覆盖有限组织与人群，个体级数据受限 | 人群参考交 GTEx，肿瘤队列交 `cbioportal-database`，细胞系交 `depmap` |
| 通路与互作网络取数 | `string-database` | 标识映射与网络脚本齐备，版本化 URL 保证可复现 | 互作是预测与证据合并，不是实测物理结合 | 互作走 STRING，反应级细节交 `reactome-database`，通路图交 `kegg-database` |
| 蛋白结构与结构域 | `pdb-database` | 实验结构按物种与方法可筛，字段可编程查询 | 覆盖偏向可结晶蛋白，膜蛋白与无序区缺失 | 实验结构走 PDB，缺失区交 `alphafold-database` 的预测模型，域注释交 `interpro-database` |
| 小分子与靶点亲和力 | `pubchem-database` | 名称／CID／SMILES 三向检索，性质与活性注释齐全 | 活性数据来自多来源汇总，测定条件不统一 | 化学本体走 PubChem，活性质量交 `chembl-database` 与 `bindingdb-database` |
| 代谢组数据与命名标准化 | `hmdb-database` | 理化性质、谱图、通路关联成体系 | 以人源代谢物为主，跨物种覆盖弱 | 注释走 HMDB，研究级原始数据走 Metabolomics Workbench 的 RefMet 标准化 |
| 取数留痕与可复现记录 | `geo-database` | 本地缓存目录天然形成可复跑锚点 | 只解决文件落盘，不解决版本与许可记录 | 统一由本技能的 manifest 规范收口，所有卡都走同一套记录格式 |

## 三、融合协议

下面每一节对应一张能力卡。步骤名后的括号是协作技能，箭头后是可机械判定的完成标志。

### 3.1 基因与蛋白标识符对齐（`gene-database` + `uniprot-database` + `ensembl-database`）

**先定体系再取数** → 在动手前写下三件事：物种（`taxonomy_id`，人用 9606）、主键类型（symbol／Entrez GeneID／Ensembl／UniProt accession）、坐标版本（GRCh37 还是 GRCh38）。同一张表里不允许混用两套主键，混用必然在合并时丢行。⇒ 工作笔记里有一行「物种｜主键｜坐标版本」。

**NCBI 侧取主记录** → E-utilities 走 `esearch` 到 `esummary` 到 `efetch`，检索式用字段标签限定：`BRCA1[gene name] AND human[organism]`、`GO:0006915[biological process]`、`17q21[chromosome]`。要一次拿全（序列、注释、同源）时用 Datasets API，别用 E-utilities 逐条拼。⇒ 拿到 GeneID 列表与每条记录的 symbol、summary、定位。

**限速与退避按库正文执行** → 无 key 的 E-utilities 按 3 req/s、Datasets 按 5 req/s 排队，有 key 提到 10 req/s；遇到 429 做指数退避而不是立刻重试，遇到 400 先回头查检索式语法，遇到 404 说明 ID 不存在而不是网络问题。批量任务必须走批处理脚本，不要在主流程里循环单查。⇒ 日志里能看到每次请求的时间戳与状态码。

**蛋白侧换号** → UniProt REST 用 `gene:BRCA1 AND reviewed:true`（reviewed 即 Swiss-Prot，人工审校过）、`accession:P12345`、`taxonomy_id:9606`、`length:[100 TO 500]`、`go:0005515`，支持 `NOT` 与括号布尔。要用 UniProt 的 ID mapping 把 Entrez／Ensembl 批量换成 accession，一次提交一批而不是一条一条换。⇒ 映射表两列：原 ID、目标 accession，附 unmapped 清单。

**坐标与转录本核对** → Ensembl REST 的主端点是 `https://rest.ensembl.org`，旧项目要 GRCh37 时换镜像 `https://grch37.rest.ensembl.org`，两个端点返回的坐标不能在同一张表里混。要 VEP 预测、orthologs、assembly mapping 时也从这里取，别自己按外显子拼。⇒ 表里每条记录带 assembly 标识。

**人源符号映射兜底** → R 侧 `bitr()` 做 SYMBOL 与 ENTREZID 互换，只覆盖人源基因；富集结果要先 `as.data.frame()` 再 `filter`，否则 dplyr 的 filter 会作用在 list 列上报错。⇒ 映射后统计未匹配比例，超过两成停下查主键是否选错。

### 3.2 变异注释与分级核对（`clinvar-database` + `gnomad-database` + `clinpgx-database` + `jaspar-database`）

**锁定坐标版本** → 先确认下游分析用的是 GRCh37 还是 GRCh38，再去取对应版本的 ClinVar VCF（`vcf_GRCh37`／`vcf_GRCh38`）。跨版本时不要拿 rsID 硬凑，走 lift 或重新注释。⇒ 注释表里有一列写 build。

**取 ClinVar 分级** → 单条查询用 E-utilities：`db=clinvar&term=BRCA1[gene]+AND+pathogenic[CLNSIG]`；批量注释用 FTP 的 `clinvar.vcf.gz`，INFO 里看 `CLNSIG` 与 `GENEINFO`，用 `bcftools view -i 'INFO/CLNSIG~"Pathogenic"'` 先筛再 `bcftools annotate -a clinvar.vcf.gz -c INFO` 贴回自己的 VCF。走 tab 表时 `variant_summary.txt.gz` 里基因列叫 `GeneSymbol`。⇒ 每个变异有一行 CLNSIG。

**分级必须带星级一起报** → ACMG 五级是 Pathogenic（外显率估计约 99%）、Likely pathogenic（约 90%）、VUS、Likely benign、Benign；审核状态按星标：4★ 实践指南、3★ 专家小组、2★ 多提交者无冲突、1★ 单提交者、无星为无断言。只报字母不报星标，等于把 1★ 的孤立提交和 4★ 的指南同级对待。⇒ 注释表两列并排：CLNSIG、review status。

**频率核对交 gnomAD** → 用 GraphQL 端点 `https://gnomad.broadinstitute.org/api` 按基因或坐标取群体频率，顺带取约束指标 pLI 与 LOEUF（判断该基因是否耐受功能缺失）。需要整批时从 downloads 页取 VCF／Hail 表／constraint tables，别在 GraphQL 里拉几万条。⇒ 每个变异有 popmax AF 及其人群标签。

**药物基因组注释补一层** → ClinPGx 基础接口 `https://api.clinpgx.org/v1/` 不需要认证，能给基因-药物对、CPIC 指南、allele function、临床注释与药物标签；超量会返 429，按退避处理；数据许可 CC BY-SA 4.0，引用与再分发要照此标注。⇒ 有用药相关变异时，表里多一列 CPIC 推荐等级。

**调控区变异看结合影响** → JASPAR 接口 `https://jaspar.elixir.no/api/v1` 的 search 支持 `collection=CORE`、`tf_name`、`species`、`tf_class`，可取 PFM／PWM 矩阵做双链扫描，再评估变异对转录因子结合位点的影响；仅当变异落在启动子或增强子区时才需要这一步。⇒ 有矩阵 ID 与扫描窗口参数。

**边界提醒** → ClinVar 的 VCF 不收大于 10kb 与复杂结构变异，涉及大片段时改查 tab 表或原始提交；VUS 不能当阳性用，报结果时写清「证据不足」而不是折中措辞。⇒ 注释表对 VUS 单独标记，不参与阳性集。

### 3.3 GWAS 汇总统计与工具变量（`gwas-database` + `r-pharmacology-singlecell-mr` + `gnomad-database`）

**先摸研究清单** → GWAS Catalog 的 `https://www.ebi.ac.uk/gwas/rest/api` 取 studies（如 `GCST001795`）拿研究描述与样本量，`singleNucleotidePolymorphisms/rs7903146/associations` 看该位点在各研究里的关联，`efoTraits/EFO_0001360` 查表型词表。表型一定要落到 EFO 号上，只写疾病名会在不同研究之间串味。⇒ 研究表带 GCST 号、EFO 号、样本量与人群。

**汇总统计走两道路** → 单研究汇总统计从 `https://www.ebi.ac.uk/gwas/summary-statistics/api` 取，整批从 `http://ftp.ebi.ac.uk/pub/databases/gwas/summary_statistics/` 按 GCST 号下载。两道路的列名与 build 各研究不一致，下载后先打印列名对比再合并；库正文有数据更新与局限专节，新版本发布时会调整字段。⇒ 每个研究一份列名快照与行数。

**工具变量本地筛** → 阈值先定 `p < 1e-5`，再按 F 统计量 `F = beta^2 / se^2` 剔弱工具；等位基因对齐时用 `eaf = ifelse(A2 == maf, maf, 1 - maf)` 校正效应等位基因频率，方向反了会让整条 MR 结论翻转。⇒ 工具变量表含 rsID、chr:pos、EA、OA、EAF、beta、se、p、F。

**clump 只在本地做** → 用 PLINK 加本地 LD 参考面板跑 `ieugwasr::ld_clump()`，r2 与窗口参数写进记录。绝不要为省事把 token 写进脚本调在线 clump 接口——项目里曾发现三个 OpenGWAS JWT 与一个 LDlink token 明文躺在代码里且已过期，凭据应当放 `~/.Renviron` 或环境变量。⇒ clump 参数、面板版本、r2 阈值三件都在记录里。

**方向性检验不能省** → 单细胞 eQTL 做 MR 必须做 Steiger：`get_r_from_pn`／`get_r_from_lor` 先估 r，再 `psych::r.test` 比较，`steiger_pval <- pnorm(-abs(st$z)) * 2`。不做的后果是把「表达影响性状」和「性状影响表达」写成同一个方向。⇒ 输出表含 steiger_pval 与方向判定列。

**敏感性分析与共定位** → 五种方法并跑：`mr_ivw`、`mr_egger_regression`、`mr_weighted_median`、`mr_weighted_mode`、`mr_simple_mode`；异质性与多效性看 MR-PRESSO，`NbDistribution` 不低于 5000；共定位看 H4，通常以 H4 大于 0.8 作为共享因果信号的支持。⇒ 结论段落引用的是方法间一致性，不是单方法 p 值。

**频率与约束复核** → 工具变量的群体频率交 gnomAD 核对，落在常见变异区间的位点要说明是否会被 LD 牵连；顺带看 pLI 与 LOEUF 判断基因剂量敏感性。⇒ 位点表多两列：gnomAD AF、基因约束指标。

### 3.4 组学数据下载与整理（`geo-database` + `ena-database`）

**读懂 GSE 层级** → GEO 的五层是 GSE（系列）、GSM（样本）、GPL（平台）、GDS（整理过的数据集）、Profiles（按基因整理的表达谱）。要复现分析必须同时拿 GSE 与 GPL：只拿矩阵不知道探针怎么映射到基因，只拿 GPL 没有表达值。⇒ 记录里三件齐全：GSE 号、GPL 号、样本数。

**用检索语法找数据集** → `Bio.Entrez` 查 `db="gds"`（数据集）与 `db="geoprofiles"`（表达谱），必须设 `Entrez.email`（NCBI 的礼貌要求），大结果集用 `usehistory="y"` 保存历史再分页取。检索式字段标签照库正文：`breast cancer[MeSH] AND Homo sapiens[Organism]`、`GPL570[Accession]`、`expression profiling by array[DataSet Type]`、`2024[Publication Date]`。⇒ 候选数据集表带命中数与筛选理由。

**下载走 GEOparse 并留本地缓存** → `uv pip install GEOparse` 之后 `GEOparse.get_GEO(geo="GSE123456", destdir=...)`，`destdir` 里会留下 SOFT 文件，同批数据第二次跑直接命中缓存，这是可复跑的关键。取表达矩阵用 `gse.pivot_samples('VALUE')`，补充文件用 `gse.download_supplementary_files(directory=..., download_sra=False)`——`download_sra=False` 是有意的默认值：原始读段体积大且走 SRA 通道慢。⇒ `destdir` 有文件清单、字节数与 md5。

**元数据要按固定键取** → GEO 的 metadata 键是 `title`、`summary`、`overall_design`、`source_name_ch1`、`characteristics_ch1`。分组变量几乎都藏在 `characteristics_ch1` 里（如 `disease state: tumor`），要按冒号切开再映射，不要直接拿 `source_name_ch1` 当分组。⇒ 样本表每行有分组列与原始字段值。

**原始读段转 ENA** → ENA 的检索能拿到 run 记录与文件直链，支持批量与续传下载，GEO 侧缺原始数据的项目从这里补。下载前先核对 read 长度、配对方式与参考基因组版本。⇒ run 表含 SRR/ERR 号、文件大小、md5、测序平台。

**整理成三件套** → 交付表达矩阵（行基因、列样本）、样本表（分组与协变量）、平台注释表（探针到基因）。矩阵里的探针映射不确定时保留多对多关系，不要硬取平均后当唯一值。⇒ 三件套齐备，行列数一致且能对上。

### 3.5 外部表达与依赖性数据集复用（`gtex-database` + `cbioportal-database` + `depmap` + `opentargets-database`）

**GTEx 表达必须用带版本 GENCODE ID** → 端点 `https://gtexportal.org/api/v2`，`/expression/medianGeneExpression?gencodeId=&datasetId=gtex_v10&itemsPerPage=100`，返回列是 `tissueSiteDetailId`、`tissueSiteDetail`、`median`、`unit`。基因 ID 要带版本后缀（如 `ENSG00000130203.10`），不带版本会匹配不上；组织用 `tissueSiteDetailId` 而不是组织全名。⇒ 表达表保留单位列与样本数列。

**肿瘤队列走 cBioPortal** → 接口基址 `https://www.cbioportal.org/api`，Swagger 在 `/api/swagger-ui/index.html`，覆盖 TCGA、GENIE、MSK-IMPACT 的突变、拷贝数、表达、甲基化、临床与生存。要整包离线复现就下 datahub 的打包文件（如 `wget https://cbioportal-datahub.s3.amazonaws.com/brca_tcga.tar.gz`），本地脚本解析比逐次调 API 稳。按突变状态分生存这类分析库正文给了 workflow，可以直接照做。⇒ 队列表带 studyId、样本数、数据层级（mRNA／CNA／mutation）。

**细胞系依赖性走 DepMap** → 基址 `https://depmap.org/portal/api`，`/gene?gene_id=&dataset=` 拿基因元信息，`/data/gene_dependency?gene_name=&dataset_name=` 拿 CRISPR 依赖性打分，默认数据集是 `CRISPRGeneEffect`（底层 `Chronos_Combined`）。版本按季度命名（如 DepMap 24Q4），记录里必须写清季度号，否则跨季度比较会漂。⇒ 依赖性表带细胞系谱系列与版本号。

**靶点证据分层走 Open Targets** → `scripts/query_opentargets.py` 的 `search_entities(name, entity_types=["target"|"disease"])` 一次拿 ENSG 与 EFO 号（如 `ENSG00000012048`、`EFO_0000249`），再用这些号去查证据分层汇总。库正文有数据更新与版本说明，引用时标版本。⇒ 靶点-疾病表带 ENSG、EFO、证据类型与得分。

**跨库合并前先对齐主键** → GTEx 用带版本 Ensembl、cBioPortal 用 Hugo Symbol、DepMap 用 Entrez 或 Symbol。合并前统一到一套主键，丢失率超过两成说明主键选错。⇒ 合并表有一列原主键来源。

### 3.6 通路与互作网络取数（`string-database` + `reactome-database` + `kegg-database`）

**先映射标识符再取网络** → STRING 的 `scripts/string_api.py` 里 `string_map_ids(query, species=9606, limit=)` 先把基因名换成 STRING 内部 ID，再 `string_network(ids, required_score=700|400, add_nodes=10, network_type='physical')` 取边。不先映射直接喂 symbol，返回的边会漏。`required_score=700` 是高置信，`400` 是中等，报告里要写明用哪一档。⇒ 映射表加边表（node1、node2、score、证据通道）。

**限速一秒一次** → STRING 明确要求每次调用间隔 1 秒，批量循环里加 sleep，别并发打满。库正文建议用带版本号的 URL 调接口，配合 `string_version()` 记录当前版本，同一分析复跑时版本号能对上。⇒ 记录里有 STRING 版本号。

**Reactome 直调 REST** → 基址 `https://reactome.org/ContentService/...`，先 `GET /data/database/version` 拿版本再取通路。旧的 reactome2py v3.0.0（2021-01）已不活跃，不要再依赖它，脚本 `scripts/reactome_query.py` 里 `version` 子命令就是查版本的入口。⇒ 通路表带 Reactome 版本与通路稳定号。

**KEGG 换标识符** → `scripts/kegg_api.py` 里 `kegg_list('pathway','hsa')` 取人源通路清单，`kegg_list('hsa:10458+hsa:10459')` 批量取条目（单次最多 10 个，超了会截断），`kegg_conv` 支持 `ncbi-geneid`、`ncbi-proteinid`、`uniprot`、`pubchem`、`chebi` 之间换号。KEGG 仅限学术用途，取数阶段就要在记录里声明用途，商业项目不要用。⇒ conv 表两列对照，转换失败条目单列。

**富集结果的表要先拆** → R 侧 `enrichKEGG(organism="hsa", pAdjustMethod="BH")` 与 `enrichGO(ont="BP"|"CC"|"MF")` 返回的 `geneID` 是用 `/` 拼起来的字符串，做基因-通路一对一表要 `split` 再展开，否则一张图里每个通路只能挂一个基因。⇒ 一对一表行数等于原始「通路-基因」对的数量。

**网络与通路的取舍** → STRING 给的是互作证据合并分，不是物理结合的直接证据，写结果时用「互作证据」而不是「结合」；Reactome 给反应级顺序与区室信息，做机制叙述时用它而不是 KEGG 的静态图。⇒ 机制段落引用的是反应与区室，互作段落标注置信档。

### 3.7 蛋白结构与结构域（`pdb-database` + `alphafold-database` + `interpro-database`）

**结构检索用 rcsbapi** → `rcsbapi.search` 的 `TextQuery` 与 `AttributeQuery` 两组构造查询，按物种筛时属性名是 `rcsb_entity_source_organism.scientific_name`，运算符用 `exact_match`。旧的 rcsb 老接口已经弃用，代码里若还引用旧接口要换掉，别在弃用接口上排错。⇒ 结构表带 PDB ID、方法（X-ray／cryo-EM／NMR）、分辨率、覆盖链。

**预测结构补缺失区** → AlphaFold DB 端点 `https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}` 拿条目元信息，文件在 `https://alphafold.ebi.ac.uk/files/{entryId}-model_v4.cif`、同目录 `-confidence_v4.json` 与 `-predicted_aligned_error_v4.json`。Biopython 的 `Bio.PDB.alphafold_db` 有 `get_predictions()`、`download_cif_for()`、`get_structural_models_for()` 三个入口，批量时用它比自己拼 URL 稳。⇒ 结构文件与置信度文件成对落盘，文件名带 entryId 与 v4。

**置信度要按区间报 pLDDT** → 预测结构看两个指标：pLDDT 是残基级置信度，PAE 是域间相对位置置信度。整条链的均值没有信息量，要按结构域分段报，低置信段在结果里标出来而不是当结构用。⇒ 结构域表带残基区间、平均 pLDDT、PAE 摘要。

**批量与备选通道** → 一次要几百条预测结构时走 Google Cloud 的批量通道，别在 API 上循环；需要跨库聚合结构时用 3D-Beacons API 作备选。⇒ 批量任务有清单与失败重试记录。

**域注释用 InterPro** → 基址 `https://www.ebi.ac.uk/interpro/api`，`protein/UniProt/{acc}/entry/InterPro/` 返回条目里的 `metadata.accession`、`metadata.type`、`metadata.name`（如 `IPR011615` 为 domain 型），支持 GO term 映射与按分类学检索。批量时 `time.sleep(0.3)` 控速。⇒ 域表带 IPR 号、类型、起止残基、来源库（Pfam／SMART／PROSITE 等）。

**三源交叉** → 实验结构给实测坐标，预测结构给覆盖，域注释给功能边界。三者对同一段残基的结论不一致时，以实验结构坐标为准，预测与注释作为补充说明。⇒ 结论表里三列并排，冲突行有标注。

### 3.8 小分子与靶点亲和力（`pubchem-database` + `chembl-database` + `bindingdb-database` + `zinc-database`）

**从 PubChem 进化学品本体** → 名称、CID、SMILES 三向检索都能起手，相似性与子结构检索也支持。PUG-REST 的常用路径是 `/rest/pug/compound/cid/{cid}/PNG`（结构图）、`/assaysummary/JSON`（生物活性汇总）、pug_view 的 `/data/compound/{cid}/JSON`（详细注释）。Python 侧用 PubChemPy 包住这些调用。⇒ 化合物表带 CID、分子式、分子量、SMILES、InChIKey。

**活性质量交 ChEMBL** → `chembl_webresource_client` 的 `new_client.molecule`、`target`、`activity`、`drug` 覆盖化合物、靶点、活性与药物四个维度。过滤语法支持链式条件：`molecule_properties__mw_freebase__lte=500`、`__range=[300,500]`。库正文有 rate limiting 节，按它排队。⇒ 活性表带 assay 类型、靶点 ChEMBL ID、pChEMBL 值。

**亲和力实测值查 BindingDB** → 服务地址 `https://www.bindingdb.org/axis2/services/BDBService/{method}`，常用参数是 `uniprot_id`、`affinity_type`（Ki／Kd／IC50／EC50 四种）、`affinity_cutoff`（单位 nM）、`response=json`。条目多时下载全量再本地筛，接口按条查不适合批量。许可 CC-BY-3.0，引用与再分发照此标注。⇒ 亲和力表带单位 nM、类型、来源文献与测定条件。

**可购化合物库走 ZINC** → `https://cartblanche22.docking.org/substances.txt:zinc_id=...&output_fields=smiles,zinc_id,tranche` 按编号或 SMILES 取，`tranche` 列标明可购层级（价格与供货档）。当前版本是 ZINC22（两亿三千万级），ZINC15 是前代，版本要写进记录。取三维结构用于对接时确认是 3D-ready 版本。⇒ 化合物库表带 ZINC ID、SMILES、tranche。

**四种亲和力类型不能混算** → Ki 与 Kd 是平衡常数，IC50 与 EC50 依赖实验条件，把它们放进同一个统计里会把条件差当成活性差。汇总时按类型分层，报告里写明各类型各多少条。⇒ 汇总表按 affinity_type 分组计数。

### 3.9 代谢组数据与命名标准化（`hmdb-database` + `metabolomics-workbench-database`）

**注释先落 HMDB** → HMDB v5.0（2023-07-01）提供代谢物理化性质、生物标志物关联、NMR 与 MS 谱、通路关联；数据集可下载，也有 programmatic API。许可是学术免费非商业，商用要另授权，取数阶段就把用途写清。⇒ 注释表带 HMDB ID、名称、分子式、KEGG／PubChem 交叉号。

**研究级数据走 Metabolomics Workbench** → REST 基址 `https://www.metabolomicsworkbench.org/rest/`。常用路径：`compound/pubchem_cid/5281365/all/json` 按 PubChem CID 查化合物、`compound/regno/11/png` 取结构图、`study/study_id/ST/available/json` 列可用研究、`study/study_id/ST000001/summary/json` 取研究摘要、`study/study_id/ST000001/data/json` 取数据、`study/refmet_name/Tyrosine/summary/json` 按 RefMet 名反查研究。⇒ 研究表带 ST 号、平台、样本数、单位。

**命名标准化用 RefMet** → 四个库对同一代谢物的写法不一致（大写缩写、带电荷、带异构体后缀），跨研究合并前先映射到 RefMet 名，再按 RefMet 名对齐。只按原名合并会出现同名不同物或同物不同名两类错误。⇒ 合并表保留两列：原始名、RefMet 名，未映射的单独列出。

**单位与平台要进表** → 代谢组数据的浓度单位（μM、peak area、log2）与检测平台（LC-MS／GC-MS／NMR）决定能不能跨研究比较。不同单位的表不要直接取均值合并，先做标准化并记录方法。⇒ 数据字典里有单位列与平台列。

### 3.10 取数留痕与可复现记录（`geo-database` + `gwas-database` + `string-database` + `clinvar-database`）

**每个数据集一份 manifest** → 固定五要素：库名与版本或抓取日期、端点 URL 或检索参数、抓取时间、文件 sha256 与字节数、行数与列名清单。缺任何一项，半年后同一批数据复不出来。⇒ `manifest.json` 存在数据目录根部。

**版本号要能从接口读到** → STRING 用 `string_version()` 与版本化 URL；Reactome 用 `GET /data/database/version`；DepMap 记季度号（如 24Q4）；GTEx 记 `datasetId`（如 `gtex_v10`）；ClinVar 记 FTP 目录日期或 VCF 头里的版本行。接口给不出精确版本时，退一步记抓取日期并在记录里注明「版本未由接口暴露」。⇒ 版本字段非空且不是「latest」。

**一条命令能重跑** → 记录里写清从零复跑的入口命令（含参数与工作目录），而不是只写「用脚本下的」。脚本自己也要能读环境变量拿凭据，不硬编码。⇒ 复跑命令在空目录里能跑通。

**隐私硬门** → 变异、表达、临床、代谢组里的个体级记录只在本机处理，不上传云实验室、云平台或在线分析接口；需要外部服务时先本地脱敏（去直接标识符、日期泛化、地名到省级）并停下向用户确认，确认后在记录里写脱敏方式与残留风险。⇒ 记录里有「本地处理」声明与脱敏步骤说明。

**凭据硬门** → token、邮箱密码、API key 只从环境变量或 `~/.Renviron` 读，不写进脚本、不写进文档、不进版本库；在仓库里发现明文凭据时先轮换再继续，并在改动记录里写清楚。⇒ 交付前 `grep` 一遍常见凭据关键词，命中数为零。

**许可要跟随数据走** → 各库许可不同：BindingDB 是 CC-BY-3.0，ClinPGx 是 CC BY-SA 4.0，JASPAR 与 InterPro 是 CC0-1.0，KEGG 仅限学术用途，HMDB 学术免费商用另议，DrugBank 与 COSMIC 有各自的商用限制。manifest 里记许可，论文的数据可得性声明照此写。⇒ 每个数据集的许可字段非空。

## 四、常见错误

- **拿 rsID 当跨版本主键**：GRCh37 与 GRCh38 的坐标不同，只按 rsID 合并会漏掉未标注位点，也会把重复区段错配。改成先固定 build，再按 chrom:pos:ref:alt 合并。
- **把 ClinVar 的 VUS 当阴性或阳性**：VUS 是证据不足，不是「倾向于良性」。报结果时单列，不参与阳性集，也不用于训练标签。
- **只报 CLNSIG 不报星级**：1★ 单提交者的致病判定与 4★ 实践指南的分级证据强度差两个量级，合并统计前必须分层。
- **用在线 clump 接口并硬编码 token**：既不可复现又泄凭据。改成本地 PLINK 加参考面板。
- **GEO 只下矩阵不下平台文件**：探针无法映射到基因，后续分析全部悬空；下载时 GSE 与 GPL 一起拿。
- **用 `source_name_ch1` 当分组变量**：分组信息通常在 `characteristics_ch1`，按冒号切分后映射。
- **跨库直接拿 symbol 合并**：GTEx 要带版本的 Ensembl、cBioPortal 用 Hugo Symbol、DepMap 用 Entrez，先统一主键再合并。
- **把 pLDDT 全链均值当质量指标**：均值会掩盖局部无序区，要按结构域分段报。
- **把 Ki 与 IC50 放进同一个均值**：实验条件不同，分开统计。
- **记录里写 `latest` 当版本**：半年后无法复现。接口给不出版本就记抓取日期并注明。

## 五、自检清单

- [ ] 物种、主键类型、坐标版本三项在笔记里写定，全流程未混用。
- [ ] 每张表的基因或变异主键与库的官方标识符一致，丢失率已统计。
- [ ] 分级类结论带审核星级；频率类结论带人群标签。
- [ ] 组学矩阵有配套样本表与平台注释表，行列数能对上。
- [ ] 表达数据的基因 ID 带版本，组织或队列命名与库口径一致。
- [ ] 网络与通路的取数带了库版本号与置信档。
- [ ] 结构文件与置信度文件成对，文件名含模型版本；域注释带 IPR 号。
- [ ] 化合物表的亲和力按类型分层，单位统一为 nM 或明确标注。
- [ ] 代谢物跨研究合并前已映射到 RefMet 名，单位与平台进表。
- [ ] `manifest.json` 五要素齐全，复跑命令在空目录能跑通。
- [ ] 个体级数据未上传任何第三方，或已脱敏并留下确认记录。
- [ ] 凭据未出现在脚本、文档与仓库里；许可字段已记入 manifest。

## 六、能力卡索引

| 能力卡 | 主用技能 | 典型触发 |
|---|---|---|
| `data.gene-idmap` | `gene-database` | 基因符号换 ID、批量 ID 转换、跨库对号 |
| `data.variant-annot` | `clinvar-database` | 变异注释、致病性分级、频率核对、药物基因组 |
| `data.gwas-eqtl` | `gwas-database` | 汇总统计下载、工具变量、clump、MR 数据准备 |
| `data.omics-download` | `geo-database` | GEO 数据集下载、表达矩阵、原始读段 |
| `data.expression-reuse` | `gtex-database` | 组织表达、肿瘤队列、细胞系依赖性、靶点证据 |
| `data.pathway-ppi` | `string-database` | 互作网络、通路成员、富集背景 |
| `data.protein-structure` | `pdb-database` | 实验结构、预测结构、结构域注释 |
| `data.chem-target` | `pubchem-database` | 化合物检索、靶点活性、可购库 |
| `data.metab-omics` | `hmdb-database` | 代谢物注释、研究级代谢组合并 |
| `data.provenance` | `geo-database` | 取数记录、版本锁定、许可与隐私声明 |

取数完成后，数据闸门（DG1 列类型核对、DG2 不可能值、DG3 缺失模式、DG4 事件数与 EPV、DG5 参数合理性、DG6 方向与编码）交给 `research-stats` 接手；本域只保证「数据是真的、来源可查、能重跑」。
