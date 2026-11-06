---
name: slidep-pptx-notes
description: 为 slidep 生成的 PPTX 注入真实 PowerPoint 备注区讲稿（speaker notes）。解决 slidep notes 属性不生成 notesSlides part、zip 级 OOXML 注入后 python-pptx 读不到、descr 双重转义三大问题。触发词：PPT 备注、讲稿、speaker notes、notesSlide、slidep。
agent_created: true
---

# slidep PPTX 真实备注注入

适用场景：用 slidep（`slidep create` / `slidep upsert-dsl`）生成 PPTX 后，要求 PowerPoint 备注区逐页显示讲稿。

## 关键事实（先读，避免踩坑）

1. **slidep 的 `notes={...}` 属性不生成真备注**。转换器把讲稿文本塞进 slide 根元素的 `<p:cNvPr descr="notes={...}">`（alt 文本），包内 notesSlides 数为 0，PowerPoint 备注区为空。
2. **python-pptx 救不了原生缺陷**：slidep 的 notesMaster 没有任何 placeholder，`slide.notes_slide` 自动新建的空 part 中 `notes_text_frame` 为 `None`。
3. python-pptx 环境：`C:\Users\zy\.workbuddy\binaries\python\envs\default\Scripts\python.exe`（含 python-pptx 1.0.2 + lxml）。

## 推荐方案：python-pptx 原生注入（关系链自动正确）

```python
from pptx import Presentation
from pptx.oxml import parse_xml

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

def build_notes_sp(paragraphs):
    paras = "".join(
        f'<a:p><a:r><a:rPr lang="zh-CN" altLang="en-US" dirty="0"/>'
        f"<a:t>{p}</a:t></a:r></a:p>" for p in paragraphs  # p 需 XML 转义
    )
    sp_xml = (
        f'<p:sp xmlns:p="{P_NS}" xmlns:a="{A_NS}">'
        '<p:nvSpPr><p:cNvPr id="100" name="Notes Placeholder"/>'
        '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
        '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
        f'<p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody></p:sp>'
    )
    return parse_xml(sp_xml)  # 必须用 pptx.oxml.parse_xml 保证 CT_Shape 类

prs = Presentation(pptx_path)
for slide in prs.slides:
    ns = slide.notes_slide              # 自动建 part + rels + CT override
    ns.shapes._spTree.append(build_notes_sp(paras))
prs.save(pptx_path)
```

讲稿来源：读各 slide XML 用 `re.search(r"notes=\{\`(.+?)\`\}", xml, re.S)` 从 descr 提取。

## 备选方案：zip 级 OOXML 注入四件套

缺一不可：① `ppt/notesSlides/notesSlideN.xml`（含 sldImg + body ph）② `ppt/notesSlides/_rels/notesSlideN.xml.rels`（→notesMaster + →slide）③ `[Content_Types].xml` Override ④ `ppt/slides/_rels/slideN.xml.rels` 追加 `Type=".../relationships/notesSlide"` 关系。

### 坑 1：占位符漏插值 → 悬空关系

用字符串拼接构造 Relationship 时，`Target="../notesSlides/notesSlide{n}.xml"` 的 `{n}` 极易因 f-string 只包住第一段而漏插值。悬空 Target 使 python-pptx 找不到关系 → 新建空 part（blob ~576B），表现诡异。**每条替换必须断言生效**（替换后检查占位符不在结果中）。

### 坑 2：descr 双重转义

descr 属性值已被 XML 转义一次（`"` → `&quot;`）。正则取出的是转义形态，直接 esc() 再写入 notesSlide 会双重转义，备注区显示 `&quot;` 字面量。**取自 descr 的文本必须 `html.unescape` 一次再写入**（lxml 写入时自动单次转义）。

## 验证清单（全部通过才算完成）

1. python-pptx 读回：页数正确、每页 `has_notes_slide` 且 `notes_slide.notes_text_frame.text` 非空（打印每页字数+前 20 字）。
2. 无 `&quot;` / `&amp;` / `&lt;` 残留在备注文本中。
3. zip 级：notesSlide parts 数 = CT overrides 数 = 页数；`presentation.xml` 有 notesMasterIdLst；notesSlide rels 正确回链 slide 与 notesMaster。

## 注意

用 `slidep upsert-dsl` 单页更新后，该页备注会被还原成 descr 形态，需重跑注入。
