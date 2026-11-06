# 素材库索引（Asset Library）

**位置**：`~/.workbuddy/skills/ai-figure-studio/assets/`
**格式**：vtracer 高保真矢量化 SVG（原始位图存 `_raw/`）；**用途 = 可复用元件库**
**重要**：素材库保真优先（作为零件被拼装）；而**临摹交付物**须用「逐元素原生重绘」（见 SKILL.md 重大方法论修正章节）

## 调用方法
```python
from svg_kit_pro import asset
asset("cells/cell_purple_nucleus_live.svg", tx, ty, scale=1.0)   # tx,ty = 左下角
```

| # | 分类 | 名称 | 尺寸 | 路径数 | 描述 | 来源 |
|---|------|------|------|--------|------|------|
| 1 | instruments | `microscope_fluorescence` | 191×188 | 143 | Fluorescence super-resolution microscope, 3D isometric | P01 Fig.1 |
| 2 | cells | `cell_multicolor_organelles` | 305×190 | 506 | Cell with multicolor organelle labeling network | P01 Fig.1 |
| 3 | cells | `cytoskeleton_network` | 210×190 | 423 | Cytoskeleton / mitochondria dense network field | P01 Fig.1 |
| 4 | molecules | `membrane_receptor_scheme` | 172×188 | 231 | Plasma membrane with receptors and ligands | P01 Fig.1 |
| 5 | icons | `tag_renewal_cycle` | 392×210 | 248 | Self-renewable tag cycle (fading / photobleach / self-renew) | P01 Fig.1 |
| 6 | containers | `dish_culture_1` | 255×155 | 121 | 3D culture dish with medium and cells | P01 Fig.1 |
| 7 | containers | `dish_culture_2` | 255×155 | 148 | 3D culture dish with medium and cells (variant) | P01 Fig.1 |
| 8 | containers | `dish_culture_3` | 255×155 | 120 | 3D culture dish with medium and cells (variant) | P01 Fig.1 |
| 9 | instruments | `pipette_micropipette` | 124×86 | 40 | Micropipette with droplet (angled) | P01 Fig.1 |
| 10 | containers | `vial_reagent_powder` | 88×148 | 55 | Reagent vial with powder (NaBH4) | P01 Fig.1 |
| 11 | cells | `cell_purple_nucleus_live` | 156×95 | 9 | Irregular cell, purple nucleus (live-cell) | P01 Fig.1 |
| 12 | cells | `cell_purple_nucleus_fixed` | 164×114 | 5 | Irregular cell, purple nucleus (fixed-cell) | P01 Fig.1 |
| 13 | cells | `cell_surface_modified` | 198×118 | 27 | Beige cell with surface-modified proteins | P01 Fig.1 |
| 14 | cells | `cell_nonspecific_binding` | 207×138 | 81 | Pink cell after non-specific binding | P01 Fig.1 |
| 15 | molecules | `protein_pink_pocket` | 56×50 | 6 | Protein cartoon with binding pocket (pink, unbound) | P01 Fig.1 |
| 16 | molecules | `protein_bound_state` | 62×60 | 13 | Protein cartoon (bound state, ligand fitted) | P01 Fig.1 |
| 17 | molecules | `protein_beige_hydrophobic` | 100×101 | 30 | Beige protein with chemical structure | P01 Fig.1 |
| 18 | icons | `blocking_agents_icons` | 48×48 | 4 | Blocking agent small molecules (3 dots) | P01 Fig.1 |
| 19 | containers | `greenhouse_soilless_array` | 210×120 | 616 | Greenhouse array with soilless cultivation trays (solar desalination) | P02 Fig.1 |
| 20 | materials | `bioevaporator_block` | 90×60 | 64 | Porous bioevaporator block (red, 3D) | P02 Fig.1 |
| 21 | molecules | `fibril_bundle` | 45×65 | 12 | Amyloid fibril bundle (wavy filaments) | P02 Fig.1 |
| 22 | icons | `building_cluster` | 100×90 | 60 | Residential building cluster (isometric) | P02 Fig.1 |
| 23 | organisms | `soybean_pods` | 55×130 | 43 | Soybean pods (two) | P02 Fig.1 |
| 24 | icons | `fertilizer_icon` | 60×50 | 34 | Fertilizer icon (turtle-shaped, granular) | P02 Fig.1 |
| 25 | containers | `food_products_bag` | 60×65 | 44 | Food and high-value products (bag with grains) | P02 Fig.1 |
| 26 | materials | `soybean_meal_block` | 65×50 | 16 | Soybean meal block (granular) | P02 Fig.1 |
| 27 | icons | `sun_icon` | 51×55 | 5 | Sun icon (yellow, radial glow) | P02 Fig.1 |

**共 27 个素材** | 分类：instruments / containers / cells / molecules / materials / organisms / icons / organelles