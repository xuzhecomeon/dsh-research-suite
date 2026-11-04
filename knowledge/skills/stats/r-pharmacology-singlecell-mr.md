<!-- source: r-pharmacology-singlecell-mr @ r-pharmacology-singlecell-mr | domain: stats -->

---
name: r-pharmacology-singlecell-mr
description: 网络药理学与单细胞测序 R 语言实战技能。覆盖中药/药物成分-靶点网络构建与通路富集（KEGG/GO，clusterProfiler + org.Hs.eg.db + bitr 映射 + 气泡图/Facet 条形图 + 基因-通路表构建）、STRING 蛋白互作与交集、药靶孟德尔随机化（IL6 等炎症靶点 → 疾病结局）、单细胞 Seurat 标准流程（读入/merge/SCTransform/降维聚类/亚群提取/FindMarkers）、以及单细胞 eQTL 的 MR（variant_id → rsID 映射、EAF 计算、F 统计量、手写 Steiger 方向性检验）。触发场景：用户要做中药网络药理学、成分-靶点预测、KEGG/GO 富集、单细胞测序分析、细胞类型特异 eQTL 的因果推断，或给出相关 R 代码数据要求代为运行调试纠错。
agent_created: true
---

# 网络药理学与单细胞 · R 实战技能

## 三条铁律（先读）

1. **API token 绝不写进脚本。** 本仓发现 **4 个明文 token**（3 个 OpenGWAS JWT + 1 个 LDlink），
   分属至少 2 个真实用户账号，且**全部已过期** →
   ① 凭据泄露；② 直接运行必然失败；③ 分享代码即泄露凭据。
   **正确做法**：token 放 `~/.Renviron`（并加入 `.gitignore`），脚本内只写 `Sys.getenv("OPENGWAS_JWT")` 并启动时校验非空。
   **更优做法**：用**本地 PLINK + 本地 LD 参考面板 + `ieugwasr::ld_clump()`**，从根本上绕开 API。

2. **单细胞 eQTL 的 MR 必须做 Steiger 方向性检验。** 本域 `T.R` 提供了**完整手写实现**（可直接移植到任何 MR）：
   ```r
   harmdat$rsq.exposure <- (get_r_from_pn(p = harmdat$pval.exposure,
                                          n = harmdat$samplesize.exposure))^2
   harmdat$rsq.outcome  <- (get_r_from_lor(lor = harmdat$beta.outcome,
                                           af  = harmdat$eaf.outcome,
                                           ncase = harmdat$ncase, ncontrol = harmdat$ncontrol,
                                           prevalence = harmdat$ncase/harmdat$samplesize.outcome))^2
   st <- psych::r.test(n = harmdat$samplesize.exposure, n2 = harmdat$samplesize.outcome,
                       r12 = sqrt(harmdat$rsq.exposure), r34 = sqrt(harmdat$rsq.outcome))
   harmdat$steiger_dir  <- harmdat$rsq.exposure > harmdat$rsq.outcome
   harmdat$steiger_pval <- pnorm(-abs(st$z)) * 2      # ★ 双侧；若需单侧去掉 ×2
   ```

3. **`FindMarkers` 不要设 `min.pct=0, logfc.threshold=0`。** 这会返回**所有基因**（含完全不表达的），
   结果无意义且极大。通常 `min.pct = 0.1, logfc.threshold = 0.25`。

## 标准流程

### A. 网络药理学（成分 → 靶点 → 通路）
```
1. 成分-靶点预测（TCMSP/SwissTargetPrediction/BATMAN-TCM 等）→ 靶点基因列表
2. 疾病靶点（GeneCards/OMIM/DisGeNET）→ 与药物靶点取交集（VennDiagram）
3. ★ SYMBOL ↔ ENTREZID 映射：bitr(genes, fromType="SYMBOL", toType="ENTREZID", OrgDb=org.Hs.eg.db)
4. KEGG 富集：enrichKEGG(gene, organism="hsa", pAdjustMethod="BH")
   GO 富集：enrichGO(..., ont = "BP"|"CC"|"MF")
5. ★★ 必须先 as.data.frame() 再 filter（S4 对象不能直接 filter）
6. PPI：STRING + igraph/cytoHubba 找 hub 基因
7. ★★ 基因-通路一对一表（后续网络图的基础）：
   split geneID（"a/b/c" 斜杠分隔的 EntrezID）→ id2sym 映射 → bind_rows
8. 可视化：气泡图（按 KEGG level-1 category 循环出图）+ GO 三栏 Facet 条形图
```

### B. 药靶 MR
```
1. 靶点基因的工具变量（eQTL/pQTL 或功能变异）→ 阈值可放宽到 p<1e-5
2. extract_outcome_data → harmonise_data(action=2)
3. ★ 必须跑多种方法：c("mr_ivw","mr_egger_regression","mr_weighted_median","mr_weighted_mode","mr_simple_mode")
4. 敏感性分析：异质性 + Egger 截距 + MR-PRESSO(NbDistribution≥5000) + 留一法 + ★Steiger
5. ★ 药靶 MR 必须配 共定位分析（coloc 的 H4 后验概率 > 0.8）
```

### C. 单细胞 Seurat
```
1. 批量读入 → CreateSeuratObject → merge（多个样本）
2. ★ 设 set.seed()（FindClusters 含随机性）
3. SCTransform → RunPCA → RunUMAP → FindNeighbors → FindClusters
4. DimPlot / FeaturePlot 辨识细胞类型（CD3D/CD3E 标记 T 细胞）
5. ★ 提取目标亚群：subset(obj, seurat_clusters %in% c(...)) → 重新降维聚类
6. ★ SCTransform 后必须 PrepSCTFindMarkers() 才能跑 FindMarkers
7. FindMarkers(ident.1=, min.pct=0.1, logfc.threshold=0.25)
```

### D. 单细胞 eQTL → MR（前沿）
```
1. 上游 tensorQTL/cellregmap 输出 → 解析 variant_id 得 CHR/POS
2. ★★ chr:pos → rsID：SNPlocs.Hsapiens.dbSNP155.GRCh37 + snpsByOverlaps + GRanges
3. ★★ 计算 EAF：eaf = ifelse(A2 == maf, maf, 1 - maf)      # A2 = effect allele
4. format_data(effect_allele_col="A2", other_allele_col="A1")
5. 工具变量强度：F = beta^2 / se^2
6. 阈值放宽 p < 1e-05（eQTL 样本量小于 GWAS）
7. MR + Steiger（见铁律 2）
```

## 关键函数速查

| 需求 | 函数 | 要点 |
|---|---|---|
| ID 映射 | `clusterProfiler::bitr()` | SYMBOL↔ENTREZID |
| KEGG 富集 | `enrichKEGG(gene, organism="hsa", pAdjustMethod="BH")` | 需 ENTREZID |
| GO 富集 | `enrichGO(..., ont="BP"/"CC"/"MF")` | 需 ENTREZID |
| S4 转表 | `as.data.frame(enrichResult)` | ★ 不能直接 `%>% filter()` |
| 通路去冗余 | `clusterProfiler::simplify()` | 课程缺失，建议补 |
| 本地 LD clump | `ieugwasr::ld_clump(tibble(rsid, pval), plink_bin=get_plink_exe(), bfile=".../EUR", clump_r2=0.001)` | ★★ 绕开 API 的正解 |
| 单细胞读入 | `Seurat::CreateSeuratObject(counts=)` + `merge()` | 多样本 |
| 标准化 | `SCTransform()` | 后必须 `PrepSCTFindMarkers()` |
| 差异分析 | `FindMarkers(ident.1, min.pct=0.1, logfc.threshold=0.25)` | ★ 别设 0 |
| pos→rsID | `SNPlocs.Hsapiens.dbSNP155.GRCh37` + `snpsByOverlaps()` | 需 GRCh37 版本 |
| Steiger | `psych::r.test()` + `get_r_from_pn()` + `get_r_from_lor()` | ★ 手写实现（见铁律 2） |
| PPI | STRING db + `igraph` / `cytoHubba` | — |

## 高频陷阱（完整版见 `references/网络药理学和单细胞_精学笔记.md`）

**🔴 致命级**
- **4 个明文 API token**（3 OpenGWAS + 1 LDlink），全部过期 → 见铁律 1
- `disease1[i]` 变量未定义（单细胞.R）→ 报错
- `exposure_data` / `top_snps` / `ld_df` 三个变量未定义（LD check.R）→ 脚本无法运行（片段化摘录的半成品）
- `FindMarkers(min.pct=0, logfc.threshold=0)` → 返回全部基因

**🟠 严重级**
- 药靶 MR **只跑 IVW 一种方法** → 缺敏感性分析（MR 论文必须多方法对照）
- 缺 Steiger 方向性检验；缺共定位分析（药靶 MR 标配）
- `run_mr_presso(NbDistribution=1000)`（应 ≥5000）
- 硬编码文件索引 `file_list[c(23:26,...)]`
- `FindClusters` 前未设种子
- GO 结果未做通路去冗余（`simplify()`）

**🟡 工程级**
- `tiff("散点.tif")` 里画的却是留一法图（文件名与内容不符）
- `f <- beta^2/se^2` 算了未用（死代码）
- 硬编码他人桌面路径；`library()` 大量重复；`install_github` 写在 `library` 之后

## 相关技能

- 孟德尔随机化（本域 MR 部分的理论基础）→ `r-mendelian-randomization`
- 预测模型 / 生存分析 → `r-clinical-prediction-model`
- 本机 R 环境调用 → `local-r-clinical-stats`
