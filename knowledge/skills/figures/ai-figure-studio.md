<!-- source: ai-figure-studio @ ai-figure-studio | domain: figures -->

---
name: ai-figure-studio
description: 论文插图 AI 绘制工作室 —— 从论文 PDF 提取机制图/流程图/实验示意图，逐张临摹为可编辑矢量（活字文字 + 语义分组 + 全英文），并通读全文后重绘原创机制图，最终在 Adobe Illustrator 中输出 .ai 文件。当用户提到「临摹论文图」「重绘机制图」「AI 绘图」「生成 .ai 插画」「画流程图/示意图/机制图/图形摘要」时使用。本 skill 承载用户在长期训练中确立的全部硬性标准与技术经验，每次迭代须回写更新。
version: 1.0.0
agent_created: true
keywords: Illustrator, AI绘图, 论文插图, 机制图, 流程图, 临摹, 重绘, 矢量, 活字, .ai, vtracer, OCR
---

# AI 绘图工作室（论文插图临摹 + 理解重绘）

本 skill 是用户与助手长期训练沉淀的成果：承载**全部硬性标准**、**实测技术坑**、**可复用脚本资产**与**训练迭代机制**。执行任何 AI 绘图任务前必读。

---

## 一、用户硬性标准（最高优先级 · 违反即返工）

| # | 标准 | 说明 |
|---|---|---|
| 1 | **全英文标注** | 图中任何文字严禁中文，一律英文（含面板标题、步骤、图例） |
| 2 | **文字必须活字** | 可编辑文本框（AI 中双击可改字），不是矢量轮廓。用 OCR 自动识别 + 重建 |
| 3 | **临摹要一模一样** | 视觉与原图无差别（分层高保真矢量化，不是手绘近似） |
| 4 | **产物必须是 .ai** | 在用户本机 Adobe Illustrator 中生成并保存 .ai；SVG 只是中间格式 |
| 5 | **语义分组** | 细胞/囊泡/箭头/文字/背景等按语义命名成组，便于用户单独调整 |
| 6 | **重绘必须插画级** | 不得简陋。多层细胞（膜/质/核/细胞器/高光/投影）、渐变、立体感 |
| 7 | **不留遗留问题** | 文字残影、乱码符号、元素越界等一律自查清零后再交付，不得让用户手工处理 |
| 8 | **脚本不污染 AI 菜单** | 脚本先写工作目录，用 Ctrl+F12「其他脚本...」运行；仅稳定批次入口放菜单 |
| 9 | **不偷懒** | 需要时主动调用图像生成辅助（路线 B）提升复杂仪器/质感 |
| 10 | **符号一律矢量绘制** | 对勾/叉号/化学下标等不得依赖 Unicode 字形，用 path 绘制 |

**工作方式**：端到端自主执行，先出成果再迭代；用户反馈即为新标准，须立即回写本 skill。

---

## 二、环境与硬约束（本机实测，2026-09-27）

- **AI 版本**：Adobe Illustrator 2025 (v29.5.0)，中文版
- **主程序**：`<APP_DIR>\adobe\AI\Adobe Illustrator 2025\Support Files\Contents\Windows\Illustrator.exe`
- **脚本菜节目录**：`<APP_DIR>\adobe\AI\Adobe Illustrator 2025\Presets\zh_CN\脚本\`（注意目录名是中文「脚本」）
- **COM 直连不可用**：flue/DoJavaScript 在此环境永久挂起；原因：AI 由用户桌面会话启动，助手进程在隔离上下文，Windows 禁止跨会话 COM 调用（`CO_E_SERVER_EXEC_FAILURE` / `MK_E_UNAVAILABLE`）。
  → **必须由用户运行一次脚本**（脚本内可批量处理所有文件，用户不必逐张操作）
- **AI 必须用户手动启动**：agent 启动的 Illustrator.exe 会在 1–2 分钟内静默退出（启动链路中 reg.exe 被安全策略拦截）
- **模态对话框会阻塞脚本引擎**：运行脚本前必须关闭 AI 中所有对话框，否则脚本静默挂起

**依赖（托管 venv：`<USER_HOME>\.workbuddy\binaries\python\envs\default`）**：
`pymupdf`（PDF/渲染）、`vtracer`（矢量化）、`rapidocr-onnxruntime`（OCR）、`opencv-python`、`numpy`

**SVG 渲染验证**：必须用 **Edge headless**（PyMuPDF 不支持 radialGradient 与负缩放）：
```bash
"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless --disable-gpu \
  --screenshot="out.png" --window-size=W,H --hide-scrollbars "file:///path.svg"
```

---

## 三、五阶段工作流

### 阶段 0 · 提取与筛选
```python
# scripts/extract_all.py — 遍历论文 PDF，提取全部嵌入图（过滤 <260x200 小图）
# scripts/make_sheets.py — 生成缩略图网格（contact sheet），供视觉筛选目标图
```
- 目标图定义：**机制图 / 流程图 / 实验过程示意图 / 图形摘要**（排除纯数据图表、显微照片阵列、Western blot）
- 筛选方法：读网格图人工判断（每篇取最大 12 张候选）
- 注意：部分论文含大量重复小图（tile 阵列），需按 (w,h) 去重

### 阶段 1 · 临摹（高保真矢量化）
```python
import vtracer
vtracer.convert_image_to_svg_py(src_png, out_svg,
    colormode="color", hierarchical="stacked", mode="spline",
    filter_speckle=2, color_precision=8, layer_difference=8,
    corner_threshold=45, length_threshold=3.5, path_precision=6)
```
- 输出：数千条 `<path d="..." fill="#XXX" transform="translate(x,y)"/>`
- ❌ 禁用路线：AI 自带 Image Trace（文字缺损、涂抹感）；颜色分割轮廓重建（高光导致细胞变月牙形）

### 阶段 2 · 活字化（OCR）
```python
# scripts/live_text.py — 剔除文字轮廓路径 + 插入 <text> 活字
#   1) RapidOCR 识别：(bbox, text, conf)，按 (y, x) 排序
#   2) 采样文字颜色（bbox 内最暗 1/12 像素均值）
#   3) 剔除规则：path 中心落在 OCR bbox 内（pad 4~30）且尺寸匹配
#   4) 重建：font-size = bbox高 × 0.80；h≥19 用 bold；y_base = y2 - h×0.16
```
- 兜底规则：黑色系（亮度<90）小尺寸（w<340,h<90）路径 = 文字笔画，全局剔除
- 结果：`<g id="g01_graphics">` + `<g id="g02_text">`（活字层）

### 阶段 3 · 理解重绘（原创机制图）
1. 提取并精读全文（`page.get_text()`）→ 抓住核心机制链
2. 设计叙事结构（通常 5–6 面板：Problem → Design → Mechanism → Compatibility → Protocol → Outcome）
3. 用 `scripts/svg_kit_pro.py` 组件库生成 SVG（分组用 `put("NN_组名", ...)`）
4. **路线 B 辅助**（复杂仪器/质感）：
   ```
   ImageGen 生成白底插画 → 去水印（cv2 白覆盖）→ vtracer 矢量化
   → 以 <g transform="translate(TX,TY) scale(s,-s)"> 嵌入
   ```
   适用：显微镜、色谱、电镜、晶格、复杂器官

### 阶段 4 · AI 输出 .ai
```javascript
// scripts/ai_build.jsx — 在 AI 中批量执行
//   1) app.open(SVG/PNG)  2) 规范化文本字体为 ArialMT/Arial-BoldMT
//   3) saveAs(.ai, IllustratorSaveOptions + ILLUSTRATOR17)
//   4) imageCapture 导出 AI 内渲染预览（供核对）
```
- 用户运行一次即可处理整批文件（菜单或 Ctrl+F12）

---

## 四、技术坑清单（全部实测 · 逐条遵守）

### SVG 生成类
1. **y 轴方向**：SVG y 向下。按 y 向上设计时，全内容包裹 `<g transform="translate(0,H) scale(1,-1)">`；**文字必须局部反向**：`<text transform="translate(x,y) scale(1,-1)">`
2. **嵌入外部矢量组的坐标基准**：`translate(TX,TY) scale(s,-s)` 中 **TY = 图像在 y-up 系中的"顶部"**（写"底部"会整体下移一个图高）
3. **特殊 Unicode 符号会乱码**：`✓`(U+2713) `✕`(U+2715) `₄`(U+2084) 等字体缺字形 → **一律用 path 绘制**（对勾=两段线，叉号=交叉线），化学式下标写普通数字。安全：`→`(U+2192) `·`(U+00B7) `–`(U+2013)
4. **XML 转义**：文本与属性中的 `&` `<>` 必须转义为 `&amp;` `&lt;` `&gt;`（否则解析失败 → 页面全白）
5. **z-order**：按字典序输出组时，背景用 `00_` 前缀（最先画），标题用 `95_` 后缀（最上层）；否则背景覆盖全图
6. **圆润 blob**：控制点数少（6–8）+ 扰动小（±6%）才平滑；点数多/扰动大会变成花瓣形

### 环境类
7. **ExtendScript 是 ES3**：无 `JSON.stringify`、无 `Array.map/forEach`、无箭头函数
8. **空路径赋样式会崩溃**：`pathItems.add()` 后先 `setEntirePath()` 再设 fill/stroke（"Required value is missing"）
9. **脚本分段容错**：长脚本按阶段 try-catch + 进度写盘（`report()`），单段失败不拖垮全图
10. **中文 Windows GBK**：Python 读 `tasklist` 等命令输出需 `encoding="utf-8", errors="ignore"`

### 工艺类
11. **不要用轮廓分割重建细胞**：细胞内高光会被挖空 → 月牙形；改用 vtracer 分层描摹
12. **不要用 AI Image Trace**：文字笔画缺损（"T eg ce s"）、细节糊化
13. **光学字符检测需配合文字区**：文字区做过大会误删邻近图形（如细胞、蛋白 blob）——用颜色（黑/红系）+ 尺寸双重条件
14. **AI 启动脚本需重启生效**：新放入脚本目录的 .jsx 在 AI 重启后才出现在菜单（或用 Ctrl+F12 即时选择）

---

## 五、脚本与组件库（scripts/）

| 文件 | 用途 |
|---|---|
| `extract_all.py` | 批量提取论文 PDF 全部嵌入图 + manifest.json |
| `make_sheets.py` | 缩略图网格（供视觉筛选目标图） |
| `pipeline.py` | 单图 vtracer 矢量化 + 文字区域检测 |
| `live_text.py` | 活字化：剔除文字轮廓 + 插入 `<text>` |
| `svg_kit.py` | 基础 SVG 组件（cell/vesicle/membrane/arrow/txt/frame/emit） |
| `svg_kit_pro.py` | **插画级组件库**（26 组件）：`cell_pro`（膜/质/核/线粒体/ER/高尔基体/高光/投影）、`nucleus_pro`、`mitochondrion`、`protein_domains`、`receptor_pro`、`dna_3d`、`nanoparticle`、`dish`（3D 培养皿）、`microscope`、`pipette`、`vial`、`rgrad`/`lgrad`、`arrow`/`curve_arrow`、`shadow`、`txt`、`frame`、`emit` |
| `example_gen_figure.py` | 完整重绘脚本范例（P01 FLEXTAG 六面板） |
| `ai_build.jsx` | AI 批处理：打开 → 字体规范化 → 存 .ai → 导出预览 |

**组件库用法**：
```python
import sys; sys.path.insert(0, r"<skill>/scripts")
import svg_kit_pro as P
from svg_kit_pro import put, emit, cell_pro, dish, txt, frame
put("10_A", frame(30, 560, 420, 336, "#FEF6F5", "#E5B0A8"))
put("10_A", cell_pro(300, 700, 120, 90, "#CFE9DE", "#E8F6F0", nuc=True, organelles=True))
emit("out.svg", 1600, 1000, {"10_A": "Panel A"})   # 组名自动英文标签
```

---

## 五之二、素材库（Asset Library · 训练积累的核心资产）

**位置**：`assets/`（`catalog.md` 为索引，`manifest.json` 为结构化元数据，`_raw/` 存原始位图）

**分类目录**：`instruments/`（仪器）· `containers/`（容器）· `cells/`（细胞形态）· `organelles/`（细胞器）· `molecules/`（分子）· `organisms/`（生物体/器官）· `icons/`（图标）

**调用方法**（推荐路径——先查库，缺失才重绘）：
```python
from svg_kit_pro import asset
asset("instruments/microscope_fluorescence.svg", 100, 400, scale=0.8)
# tx,ty = 素材在 y-up 坐标系的【左下角】；函数自动处理 scale(s,-s) 的翻转基准与 id 冲突
```

**提取流程（每篇论文完成后必做）**：
1. 生成**坐标网格参照图**（每 100px 网格 + 每 200px 标注数字）——严禁凭缩略图目测坐标（会造成系统性偏移）
2. 必要时生成**局部放大网格图**（scale 1.6、50px 细分网格）精确定位
3. 裁切 → vtracer 矢量化（`filter_speckle=2, color_precision=8, layer_difference=9`）
4. 生成总览 contact sheet 验证裁切质量；裁偏的立即重做，低价值的立即删除
5. 登记 `catalog.md` 表格（名称/分类/尺寸/路径/描述/来源论文）

**命名规范**：`<类别>_<特征>` 全小写下划线（如 `cell_purple_nucleus_live`、`dish_culture_1`）

**素材库价值**：跨论文复用的**保真素材**（直接来自顶刊原图），风格统一、细节到位；配合组件库（`svg_kit_pro`）与路线 B（图像生成）形成三级资源体系：
1. 素材库（首选，最高保真）
2. 组件库（参数化重绘，可无限定制）
3. 路线 B（复杂仪器/质感，图像生成 → 矢量化）

---

## ⭐ 重大方法论修正（2026-09-27 用户明确指出）

### 用户的原话与要求
> "所有图形的临摹我不想用 AI 的临摹功能" · "箭头之类的也应该是你自己用 AI 画出来的" · "所有的图形重绘都应该在一笔一笔在 AI 的画布上画出来" · "你的很多线条都有涂抹感"

### 核心区分：**临摹 ≠ 自动描摹**

| ❌ 错误做法（禁止） | ✅ 正确做法（必须） |
|---|---|
| 位图 → vtracer 自动矢量化 | **逐元素识别 → 用 AI 原生对象重画** |
| 输出数千条碎路径（涂抹感） | 每个元素 = 1 个干净对象 |
| 箭头 = 色块拼出来 | **箭头 = AI 的箭头对象**（杆 + 三角头） |
| 文字 = 轮廓形状 | **文字 = AI 文本框（活字）** |
| 边框 = 碎路径 | **边框 = AI 圆角矩形对象** |

**「一模一样」的真正含义**：对着参考图，**用 AI 的工具把每个元素一笔一笔画出来**（如设计师用钢笔工具描图），而不是让软件自动转格式。

### 正确的临摹工作流（逐元素原生重绘）

```
1. 网格实测：生成坐标网格参照图（50px 网格 + 数字标注）→ 读出每个元素的精确坐标
2. 元素清点：分类列出所有元素
   - 圆角矩形（标签框/卡片）→ rrect()
   - 箭头（直线/曲线）→ ln() + polygon 三角头；虚线用 dash
   - 椭圆/圆点 → circ() / ell()
   - 线条/分割线 → ln()
   - 文字 → txt()（活字，字号按实测高度 ×0.8）
   - 复杂图标（分子结构/网格/散点）→ 用基础形状组合绘制（六边形=polygon，网格=多段 line）
3. 坐标严格来自实测（禁止目测估算，会造成布局偏移）
4. 输出：SVG（验证用）+ ExtendScript（AI 原生对象，最终交付 .ai）
5. 渲染验证：Edge headless 截图 → 与原图并排比对 → 迭代
```

### 坐标系统注意
- 原生重绘脚本用 **y-down 坐标**（直接读原图坐标）→ 输出 SVG **不要**加 `scale(1,-1)` 翻转；文字也不要加局部翻转
- 与 `svg_kit_pro.emit()` 的 y-up 体系冲突 → 重绘脚本自建 y-down 输出函数



### 🔧 元素级重绘引擎（clean_engine2.py）能力边界（2026-09-27 全量实测 32 张）

**引擎流程**：OCR 检测文字 → 文字区填白 → 二值化区域分割 → 形状分类（ellipse/rect/path）→ 原生对象输出 + 活字层

**实测结论（32 张临摹图分类）**：
| 图类型 | 引擎效果 | 交付策略 |
|---|---|---|
| **几何型**（流程图/框图/机制示意图/网络图） | ✅ 优秀（文字活字 + 干净形状，零涂抹感） | **A 级：`_clean.svg`** |
| **插画型**（细胞/仪器/显微图/组织切片） | ❌ 差（渐变与细节丢失） | **B 级：`_live.svg`**（活字 + 高保真图形） |
| 淡色/低对比图 | ❌ 差（二值化检测不到） | B 级 |
| 暗底图 | ⚠️ 需反色预处理（引擎已支持 dark_bg 自动检测） | 视情况 |

**实测比例**：A 级 14 张 / B 级 18 张（共 32 张）

**经验**：
1. **文字必须先抠除**——否则文字笔画会被闭运算连成色块（早期失败原因）
2. **OCR 框需过滤**（高度 > 42px 或宽 > 55% 页宽 = 图形区误识别，会产出巨大文字）
3. 高方差区域（渐变/多色）应做局部二次分割（k=2~4），保持渐变结构
4. 自动引擎的极限是"几何型图"；**插画型图若要逐元素重绘，只能人工读取网格坐标逐张精绘**（每张约 1-2 小时工作量）

### ⚠️ 素材库 vs 临摹图：两种不同策略（2026-09-27 实测教训）

**关键区分**：
| 对象 | 性质 | 策略 |
|---|---|---|
| **临摹图**（用户指定的临摹任务） | 要交付的成品 | **逐元素原生重绘**（一笔一笔画）——见「重大方法论修正」 |
| **素材库**（可复用元件） | 拿来做新图的零件 | **保真优先**：高保真矢量化（vtracer）或位图，不做逐元素重绘 |

**失败教训（禁止重复）**：曾尝试用"颜色量化 + 轮廓平滑"重建素材库，结果**丢失大量渐变与内部细节**（细胞、仪器的插画质感全部消失，部分素材几近空白）。原因：插画型素材依赖渐变/阴影/纹理，色彩量化必然损失信息。

**素材库正确做法**：
1. 提取：从原图裁切 → vtracer 高保真矢量化（`filter_speckle=2, color_precision=8, layer_difference=9`）
2. 裁切必须精准（避免包含相邻元素/线条/文字）：用网格实测坐标 + autocrop 收紧
3. 裁切瑕疵（含斜线/虚线/文字截断）应重新裁切，而非重建
4. 素材作为"元件"使用时，其内部路径多并不影响最终图的观感（它是被拼装的零件，不是被审视的作品）

### 适用范围与效率
- **几何型示意图**（流程图/机制框图，如上例）→ 逐元素重绘效率高、效果好（126 个干净对象）
- **插画型示意图**（细胞/仪器/复杂生物结构）→ 主轮廓用少量控制点的平滑贝塞尔路径（非碎路径）+ 渐变填充；或调用**素材库**（已提取的原刊素材，最保真）
- 参考脚本：`gen_clean_P13.py`（P13 Fig.2a 逐元素重绘示范）

### 交付优先级
1. 素材库（原刊素材，最保真）
2. **逐元素原生重绘**（几何型图表，用户首选）
3. 组件库 `svg_kit_pro`（参数化插画）
4. 路线 B（图像生成辅助复杂仪器）
5. ❌ vtracer 自动描摹（仅可作为内部参考底稿，**不作为交付物**）

---


---

## 📚 用户科研素材库工程（2026-09-27 启动，长期进行）

### 素材来源
`C://Users//zy//Desktop//科研绘图素材//`（**1039 个文件**，83 个主题目录）
- 结构：`全套生物医学科研绘图素材33704/02.28万能模板/科研绘图矢量素材/CNS级科研绘图素材/`（CNS 级矢量素材，PPT 格式）+ `科研绘图素材/<主题>/`（按主题组织）
- 格式分布：PNG 747 · AI 98 · JPG 73 · EPS 52 · PPT 49 · 其他 20

### 处理策略（按用户要求）
| 格式 | 处理 |
|---|---|
| **矢量格式**（.ai / .eps / .ppt） | **直接取用**，不做临摹 |
| **位图格式**（.png / .jpg 等） | **矢量化/重绘入库** |

### 执行管线
```
1. .ai / .eps  → 直接复制入库  → asset_lib/vector/<topic>/
2. .ppt        → PowerPoint COM 导出 PNG(2400x1800) → vtracer 矢量化 → asset_lib/raster/
3. .png / .jpg → 透明背景填白 + 尺寸限制 → vtracer 矢量化 → asset_lib/raster/<topic>/
```


### 🎨 素材脚本库（assets_lib.jsx）—— 在 AI 中直接调用素材作图

**文件**：`scripts/assets_lib.jsx`（3.8 MB，27 个素材函数；由 `build_assets_jsx.py` 从素材 SVG 自动生成）

**用法**（在任意 AI 脚本中）：
```javascript
$.evalFile(new File("<USER_HOME>/.workbuddy/skills/ai-figure-studio/scripts/assets_lib.jsx"));
var doc = app.documents.add(DocumentColorSpace.RGB, 1200, 800);
draw_cell_purple_nucleus_live(doc, 100, 700, 1.5);   // (doc, x, y, scale)
draw_microscope_fluorescence(doc, 400, 700, 1.0);
```
- 每个素材 = 一个函数 `draw_<素材名>(doc, x, y, scale)`
- 素材为**AI 原生路径对象**（贝塞尔控制柄完整），可在 AI 中自由编辑
- 坐标：AI 画布坐标（y 向上）；函数内部自动处理 SVG→AI 的 y 轴翻转与组级缩放定位
- 索引：`assets/jsx_index.json`（列出全部函数名/尺寸/形状数）

**扩展方式**：新增素材 SVG 后运行 `build_assets_jsx.py` 即可重新生成整个脚本库。

**演示脚本**：工作目录 `assets_demo.jsx`（调用 14 个素材组成演示图，输出 `assets_demo.ai` + PNG）

### ⭐ 关键技术要点（实测）
1. **PowerPoint COM 可用**（v16.0）：`app.Presentations.Open()` + `pres.Export(dir, "PNG", W, H)` 成功
   - ❌ `Export(..., "SVG")` 失败（"支持该类文件的转换器未安装"）
   - ✅ `Export(..., "EMF")` 成功（矢量图元，6MB/页，可在 AI 中直接打开）
2. **导出目标必须在工作区内**（如 `C://Users//zy//WorkBuddy//<session>//ppt_out//`）
   - 写入 `~/.workbuddy/skills/` 等目录会被拒绝 → 先导出到工作区，再复制入库
3. **中文路径必须用 imdecode/imencode**（`cv2.imread` 对中文路径静默失败）：
   ```python
   img = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_UNCHANGED)
   cv2.imencode(ext, img)[1].tofile(path)
   ```
4. 透明背景 PNG 需 alpha 合成白底后再矢量化
5. 大批量任务应**后台运行** + 进度写日志 + 断点续传（已存在文件跳过）

### 素材库位置
- `asset_lib/vector/`（矢量原件，按主题组织）
- `asset_lib/raster/`（位图矢量化产物，按主题组织）
- 索引：`vector_index.json` / `raster_log.json`

## 六、训练与迭代机制（本 skill 的核心价值）

每次任务须执行以下闭环，**不得只在对话中答复**：

1. **执行前**：读本 skill，按「硬性标准」与「坑清单」自检
2. **执行中**：遇到新坑 / 用户新要求 → 当场记录
3. **交付后**：把新增内容回写本 skill：
   - 新标准 → 写入 §一（硬性标准表）
   - 新坑 → 写入 §四（技术坑清单，编号续接）
   - 新组件 → 追加到 `scripts/svg_kit_pro.py` 并在 §五 表格登记
   - 新流程 → 更新 §三 对应阶段
4. **状态汇报**：更新 §七 任务进度表

**当前工作目录**：`<USER_HOME>\WorkBuddy\2026-09-27-08-36-54\paper-figures\`
（每篇论文一个 `Pxx/` 文件夹：`original_FigN.png` / `Pxx_replica_live.svg` / `Pxx_redraw_pro.svg` / OCR json / 预览 PNG）

---

## 七、任务进度追踪

**任务**：19 篇顶刊论文（P01–P19）——每篇所有机制图/流程图/实验示意图逐一临摹 + 每篇一张理解重绘，全英文，输出 .ai。

> **状态（2026-09-27 完成）**：18 篇已交付（P18 与 P10 为同一论文，跳过）；共 **约 27 张临摹图 + 17 张重绘机制图**；素材库 **27 个**；统一入口 `ai_build.jsx`（约 50 个 JOBS）一键产出全部 .ai。

| 论文 | 主题 | 临摹 | 重绘 | 备注 |
|---|---|---|---|---|
| P01 | FLEXTAG 蛋白标签系统（Nat Commun 2026） | ✅ Fig.1 活字版 | ✅ 六面板插画级（含路线 B 仪器） | 示范篇；**已提取 18 个素材入库** |
| P02 | 太阳能循环脱盐农业（amyloid fibril bioevaporators, Nature Water） | ✅ 3 张（Fig.1/2a/5c 活字版） | ✅ 六面板（含素材库调用） | 新增 9 素材入库；库总 27 |
| P03 | 亚磷酸盐废水+CO₂ 生物合成 | ✅ 3 张（Fig.1/5d/5i） | ✅ 六面板 | Fig.5 需按面板拆切 |
| P04 | OD-Cu 电化学 CO₂ 还原（·OH 再氧化） | ✅ 1 张（Fig.6） | ✅ 六面板 | |
| P05 | 柔性亚纳米铁电催化剂 | ✅ 1 张（p33 彩色区检测） | ✅ 六面板 | 48 页长文，图在 p33 |
| P06 | 单粒小麦基因组学 | ✅ 2 张（Fig.2/5） | ✅ 六面板 | |
| P07 | 自噬×代谢×适应性免疫（综述） | ✅ 1 张（Fig.1 p8） | ✅ 六面板 | 综述核心机制图 |
| P08 | 手性配位聚合物纳米线 | ✅ 2 张（Fig.1/4） | ✅ 六面板 | |
| P09 | 适体可穿戴电化学传感器 | ✅ 2 张（Fig.1/3）+1 张 Fig.5 | ✅ 六面板 | |
| P10 | 双自由基协同电催化 | ✅ 1 张（Fig.1） | ✅ 六面板 | ⚠️ P18 为同一论文（跳过） |
| P11 | 原位焦亡体疫苗（个性化癌症免疫治疗） | ⬜ | ⬜ | |
| P12 | polyBERT 化学语言模型 | ⬜ | ⬜ | |
| P13 | 复杂分子反应体系放大（机理建模+深度迁移学习） | ⬜ | ⬜ | |
| P14 | 小分子–RNA 相互作用预测（无需三级结构） | ⬜ | ⬜ | |
| P11 | 原位焦亡体疫苗（pyroptosome） | ✅ 1 张（p3） | ✅ 六面板 | 无彩色，灰度密度检测 |
| P12 | polyBERT 化学语言模型 | ✅ 1 张（p7 表格/网络） | ✅ 六面板 | 计算类论文图少 |
| P13 | 复杂反应放大（机理+迁移学习） | ✅ 2 张（模型/流程图） | ✅ 六面板 | |
| P14 | 小分子–RNA 相互作用预测（Nat Biotechnol） | ✅ 1 张（p6） | ✅ 六面板 | |
| P15 | 伪装纳米机器人 | ✅ 2 张（Fig.1/2） | ✅ 六面板 | |
| P16 | 工程化外泌体纳米囊泡 | ✅ 1 张（Fig.1） | ✅ 六面板 | |
| P17 | 细菌膜纳米囊泡 | ✅ 2 张（p3/p8） | ✅ 六面板 | |
| P18 | Biradical-mediated electrocatalysis | — | — | **与 P10 同一论文，跳过** |
| P19 | P-SELEX 适配体筛选 | ✅ 2 张（Fig.1/2） | ✅ 六面板 | 与 P09 同期刊不同文 |

**节奏建议**：每 3–5 篇交付一次供用户抽查；用户反馈即标准更新。

### 批量处理流水线（P02–P10 实战沉淀）

```
batch_render.py     批量渲染页面（1.6x）+ 页面缩略图网格
batch_extract.py    彩色区域自动检测裁切 + autocrop + vtracer 矢量化
batch_livetext.py   分块 OCR（防扁图/大图失败）+ 活字化
gen_batch_redraw.py 批量六面板重绘（内容字典驱动）
ai_build.jsx        统一批处理入口 → .ai（JOBS 累积所有已完成图）
```

**关键经验**：
1. 判图顺序：页面渲染 → 候选页网格 → **坐标网格定位**（100px/50px 网格 + 数字标注）→ 精确裁切
2. **彩色区域检测**（HSV 饱和度 > 35）可自动定位彩色示意图，但对黑白/淡色图失效，需退回人工网格定位
3. 长论文（P05 前 14 页无图）需扩大渲染页数
4. 一张多面板大图（如 P03 Fig.5）应按**面板级**拆切（d 机制模块 / i 系统集成），而非整图
5. 重绘版模板化：标题条 + 2×3 六面板（Challenge/Strategy/Mechanism/Process/Outcome/Impact）
