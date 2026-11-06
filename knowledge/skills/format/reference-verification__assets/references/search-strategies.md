# 检索策略与掠夺性期刊识别指南

## 一、精准检索策略

### 1. 题名精确匹配（首选）

```
搜索格式："完整英文题名" 加引号精确匹配
示例：搜索 "Attention Is All You Need"
平台：Google Scholar, Semantic Scholar, Bing Academic
```

**注意事项**：
- 英文题名去掉所有格式符号（如冒号、问号），只保留核心词组
- 副标题可以省略后再次搜索
- 含特殊字符（数学符号、希腊字母）时改用关键词搜索

### 2. 作者+年份组合搜索

```
搜索格式：[FirstAuthorLastName] [Year] "[关键词组]"
示例：Vaswani 2017 "attention mechanism transformer"
```

适用场景：题名过长或含特殊字符时

### 3. DOI 直接验证（最可靠）

```
直接访问：https://doi.org/{DOI}
API验证：https://api.crossref.org/works/{DOI}
示例：https://doi.org/10.1109/TPAMI.2023.3264658
```

CrossRef API 返回 JSON，重点核查字段：
- `title` — 实际题名
- `author` — 作者列表
- `published-print` / `published-online` — 发表年份
- `container-title` — 期刊名
- `volume`, `issue`, `page` — 卷期页

### 4. 中文文献专项检索

| 平台 | 检索入口 | 适合类型 |
|------|---------|---------|
| CNKI知网 | https://www.cnki.net | 期刊、学位、会议、报纸 |
| 万方数据 | https://www.wanfangdata.com.cn | 期刊、学位、科技报告 |
| 维普资讯 | https://www.cqvip.com | 中文科技期刊 |
| 超星学术 | https://book.chaoxing.com | 中文图书/学位论文 |

**中文期刊核验重点**：
- 核查该刊是否为核心期刊（北大核心/CSSCI/CSCD）
- 核查期刊CN号是否真实：`https://www.national-library.cn/` 国家图书馆刊物数据库

### 5. 预印本与灰色文献

| 来源 | 检索平台 | 注意事项 |
|------|---------|---------|
| arXiv | https://arxiv.org/search/ | 未经同行评审，注意版本号 |
| bioRxiv/medRxiv | https://www.biorxiv.org | 生物医学预印本 |
| SSRN | https://www.ssrn.com | 社会科学预印本 |
| 技术报告 | 机构官网 / Google | 需标注为非正式发表 |

---

## 二、期刊/会议真实性核验

### 权威期刊认定标准

**SCI/SSCI/EI 认定**：
- SCI收录：通过 Web of Science Master Journal List 查询
- EI收录：通过 Elsevier EI Village 查询
- 中科院分区：https://www.fenqubiao.com/

**核心期刊标准（中文）**：
- 北大核心（PKU Core）：北京大学图书馆发布
- CSSCI（南大核心）：南京大学中国社会科学研究评价中心
- CSCD：中国科学引文数据库

### 掠夺性期刊（Predatory Journal）识别

**高风险特征（符合3项以上高度警惕）**：
- 刊名与知名期刊高度相似（如 "International Journal of Advanced Science" 等泛化命名）
- 投稿即被接受，审稿时间极短（<48小时）
- 高昂的版面费（APC）但无学术背书
- 期刊官网设计粗糙，联系方式为免费邮箱（Gmail/Yahoo）
- 编委会成员姓名查不到对应学者真实信息
- 出版商不在 COPE 成员目录中

**核查资源**：
- Beall's List 更新版（掠夺性出版商名单）：https://beallslist.net/
- COPE 成员目录：https://publicationethics.org/members
- DOAJ（真实开放获取期刊目录）：https://doaj.org/
- Think.Check.Submit.（期刊核查工具）：https://thinkchecksubmit.org/

### 掠夺性会议识别

**高风险特征**：
- 会议名称与顶会雷同（如 "International IEEE Conference on..."）
- 会议官网无真实举办地信息或历届记录
- 无同行评审，交钱即可发表/出席
- 出版的 Proceedings 无 ISBN/ISSN 或无法在任何数据库检索到

**核查资源**：
- DBLP（CS会议/期刊收录）：https://dblp.org/
- Core Rankings（CS会议等级）：https://www.core.edu.au/conference-portal
- ACM/IEEE 官方会议列表

---

## 三、撤稿文献核查

**撤稿文献数据库（必查）**：
- Retraction Watch 数据库：https://www.retractionwatch.com/retraction-watch-database-user-guide/
- PubMed 撤稿标记：搜索时注意 `[Retracted]` 标签
- CrossRef Metadata：JSON中查找 `update-to` 字段（含撤稿通知）

**处理建议**：
- 已撤稿文献一律标记 `E-RETRACT`，在报告中单独列出
- 引用者可能不知情，建议在报告备注中提示撤稿时间及原因

---

## 四、批量核验效率技巧

### 优先级排序（先核验高风险条目）

1. **格式异常条目**：缺少多个必填字段的
2. **孤僻来源**：来自不知名期刊/会议的
3. **近年文献**：2022年后的（AI生成文献风险最高）
4. **境外开放期刊**：MDPI系列、Hindawi系列需重点核查
5. **无DOI的英文期刊**：2010年后正规英文期刊通常有DOI

### 批量 DOI 验证脚本提示

若有大量文献含 DOI，可使用脚本批量调用 CrossRef API 验证，
详见 `scripts/batch_doi_verify.py`。
