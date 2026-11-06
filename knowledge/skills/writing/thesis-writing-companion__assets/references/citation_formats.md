# 引用格式速查（Citation Formats）

不同学科/地区偏好不同格式。**先确认目标机构/期刊要求**，以下为通用主流规范要点。完整细则以官方手册为准。

## 六大格式一览
| 格式 | 常用地区/学科 | 文内标注 | 参考文献排序 |
|------|--------------|----------|--------------|
| **GB/T 7714-2015** | 中国大陆高校 | 顺序编码制 `[1]` 或著者-出版年 `(张三, 2020)` | 按出现顺序 / 著者拼音 |
| **APA 7th** | 英美心理/社科/教育 | 著者-年份 `(Smith, 2020)` | 著者字母序 |
| **MLA 9th** | 人文学科（英美） | 著者-页码 `(Smith 23)` | 著者字母序 |
| **IEEE** | 工程/计算机 | 方括号顺序 `[1]` | 出现顺序 |
| **Chicago** | 历史/出版 | 注释-书目 或 著者-年份 | 依体例 |
| **Vancouver** | 医学/生命科学 | 方括号顺序 `[1]` | 出现顺序 |

## 通用结构模板

### 期刊论文
- **GB/T 7714**：作者. 题名[J]. 刊名, 年, 卷(期): 起止页.
- **APA 7**：Author, A. A. (Year). Title of article. *Journal Name*, *Vol*(Issue), pp. https://doi.org/xx
- **IEEE**：A. Author, "Title," *Journal*, vol. x, no. y, pp. zz–ww, Year.

### 专著
- **GB/T 7714**：作者. 书名[M]. 出版地: 出版社, 年.
- **APA 7**：Author, A. A. (Year). *Title* (Ed.). Publisher.

### 会议论文
- **IEEE**：A. Author, "Title," in *Proc. Conf.*, Year, pp. xx–yy.
- **APA 7**：Author, A. A. (Year). Title. In *Proceedings* (pp. xx–yy).

### 学位论文
- **GB/T 7714**：作者. 题名[D]. 保存地: 保存单位, 年.

### 网页/报告
- 标注访问日期与 URL；机构报告注明报告号。

## 高频易错点
1. **et al. 用法**：APA 3 人以内全列，超 3 人首次列 1 人+et al.；GB/T 7714 常用"等"。
2. ** DOI 优先**：有 DOI 一律给 DOI，比 URL 稳定。
3. **中英文混排**：中文文献按拼音/笔画，英文按字母；GB/T 7714 常要求中文文献在前或分区。
4. **二次引用**：尽量避免"转引自"；确需时标注原始+转引来源。
5. **同一文献多次引用**：GB/T 顺序编码制同号；APA 同作者同年加 a/b。

## 工具建议
用 Zotero / EndNote / NoteExpress / Mendeley 管理，导出对应格式；Word 用"引文与书目"、LaTeX 用 BibTeX（见 `tools.md`）。**切忌手写参考文献后手动调格式——极易出错且难维护。**

## 各语言区常见偏好（锚定）
- 中文高校：GB/T 7714（顺序编码制最常见）
- 英美社科：APA 7；人文：MLA 9 / Chicago
- 工程/CS：IEEE
- 医学/生物：Vancouver（常称 ICMJE）
- 德语区：常自定义或 DIN；法语区：常自定义；详见 `locales/`
