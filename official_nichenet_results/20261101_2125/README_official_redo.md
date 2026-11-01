# 用官方 nichenetr 代码重做 7 亚型分析（20261101_2125）

## 1. 代码来源

- 包：`nichenetr 2.2.1.1`（已安装）
- 源码：`git clone https://github.com/saeyslab/nichenetr`（master，浅克隆 + sparse checkout 到 `tools/nichenetr`）
- 学习的官方文档：
  - `vignettes/seurat_wrapper.Rmd`（`nichenet_seuratobj_aggregate` 主教程）
  - `vignettes/seurat_steps.Rmd`（step-by-step）
  - `vignettes/seurat_steps_prioritization.Rmd`（表达量优先级 + circos + mushroom）
  - `vignettes/ligand_target_signaling_path.Rmd`（信号通路）
  - `R/prioritization.R`、`R/application_visualization.R`、`R/differential_nichenet_plotting.R`

## 2. 官方流程（wrapper）

```r
nichenet_seuratobj_aggregate(
  receiver = rcv, seurat_obj = obj,
  condition_colname = "group_use", condition_oi = "AD",
  condition_reference = "No Neuropathology",
  sender = "all",                       # 7 个亚群全部（含自分泌）
  ligand_target_matrix, lr_network, weighted_networks,
  expression_pct = 0.1, lfc_cutoff = 0.25,
  geneset = "DE", top_n_ligands = 30)
```

- 基因集：**该亚型全部 DE 基因**（padj ≤ 0.05 且 |log2FC| ≥ 0.25），不区分上下调
- 排序指标：**AUPR**（`aupr_corrected`），不是 Pearson
- 候选配体：配体在 sender 表达 **且** 其受体在 receiver 表达（sender-focused）
- 输出：配体活性表、配体-靶基因热图、配体 LFC 三色热图、配体-受体热图、配体表达 DotPlot、四联组合图

## 3. 结果（官方 wrapper，combined DE + AUPR）

| receiver | DE 基因数 | top1 | top5 |
|---|---|---|---|
| Homeos1 | 2,038 | TGFB1 | TGFB1, HMGB1, NLGN1, PSAP, TSPAN3 |
| Homeos2 | 1,023 | TGFB1 | TGFB1, PSAP, LIPC, ENG, GAS6 |
| Homeos3 | 197 | NLGN1 | NLGN1, TGFB1, JAM2, CXCL12, IL1B |
| Inflam.DAM | 2,866 | HMGB1 | HMGB1, PSAP, TGFB1, PTPRM, NLGN1 |
| Lipo.DAM | 1,393 | HMGB1 | HMGB1, PSAP, TGFB1, NLGN1, GAS6 |
| Ribo.DAM1 | 1,589 | TGFB1 | TGFB1, JAM2, HMGB1, PSAP, IL18 |
| Ribo.DAM2 | 642 | PSAP | PSAP, NRXN3, CALR, HMGB1, TSPAN3 |

## 4. 与之前（Pearson + 方向性 top200）的差异

| receiver | 官方 top5（AUPR，combined DE） | 之前 top5（Pearson，上调） |
|---|---|---|
| Homeos1 | TGFB1, HMGB1, NLGN1, PSAP, TSPAN3 | LY86, NLGN1, TF, NLGN4Y, JAM2 |
| Homeos2 | TGFB1, PSAP, LIPC, ENG, GAS6 | IL18, JAM2, SORL1, IL1B, NEGR1 |
| Inflam.DAM | HMGB1, PSAP, TGFB1, PTPRM, NLGN1 | NLGN1, LY86, CD9, NRXN1, NLGN4Y |
| Lipo.DAM | HMGB1, PSAP, TGFB1, NLGN1, GAS6 | LY86, NLGN1, NLGN4Y, LRP1B, NRXN1 |
| Ribo.DAM1 | TGFB1, JAM2, HMGB1, PSAP, IL18 | LY86, NLGN1, IL18, HLA-DMA, LRP1B |
| Ribo.DAM2 | PSAP, NRXN3, CALR, HMGB1, TSPAN3 | LY86, NLGN1, TF, NLGN4Y, NRXN1 |

三个原因：

1. **基因集不同**：官方用全部 DE 基因（2,038 个），把上调、下调混在一起；下调基因数量多且信号强，因此 TGFB1/HMGB1/PSAP 这类"下调方向配体"占据榜首。之前把上调、下调分开做，才凸显出 LY86。
2. **排序指标不同**：AUPR 奖励"靶基因集中在基因集里"的配体，Pearson 奖励"靶基因权重与基因集标签整体相关"的配体，两者排序天然不同。
3. **候选配体不同**：官方要求受体也在 receiver 表达，滤掉了没有受体注释的配体（例如 LY86 的 TLR4 不在网络里，直接被排除）。

## 5. 重要发现：基因集太大时 AUPR 失效

Homeos1 的基因集 2,038 个，背景 3,475 个，**基因集占背景 53.4%**。AUPR 的随机基线就是 0.53，
所以 `aupr_corrected` 只有 −0.02 ~ +0.015，排序接近噪声——TGFB1 的 0.0153 与 HMGB1 的 0.0087 差距很小。

因此：**这批数据不适合用"全部 DE 基因 + AUPR"**。要么把基因集限制在 top 200（按方向分开），要么改用 Pearson。

## 6. 方向性 AUPR（官方函数 + top200 方向性基因集）

为验证上面的判断，用官方 `predict_ligand_activities`（AUPR）跑方向性基因集（`official_aupr_directional/`）：

| receiver | 上调 top5 | 下调 top5 |
|---|---|---|
| Homeos1 | NLGN4Y, NRXN1, NLGN1, ALCAM, ITGAL | TGFB1, HLA-DQA2, CALR, COPA, PLTP |
| Homeos2 | IL18, IL1B, TIMP1, LPL, NLGN4Y | TGFB1, IL1B, HMGB1, HLA-DQA2, PDGFB |
| Homeos3 | 基因不足（17 个，跳过） | TGFB1, HLA-DQA2, CXCL12, NLGN1, TIMP1 |
| Inflam.DAM | NLGN4Y, NLGN1, NRXN3, LRP1B, COL9A2 | TGFB1, ENG, HMGB1, GAS6, EDIL3 |
| Lipo.DAM | NLGN1, NLGN4Y, LRP1B, NRXN3, IL18 | ENG, TGFB1, APOE, HMGB1, GAS6 |
| Ribo.DAM1 | IL18, NLGN1, NLGN4Y, NRXN1, HLA-DMA | TGFB1, PTPRM, HMGB1, ENG, PSAP |
| Ribo.DAM2 | LRP1B, CALR, NRXN3, HLA-DMA, COL9A2 | PSAP, HMGB1, TGFB1, GAS6, CD99 |

- 下调方向：**TGFB1 在 6/7 个亚型进 top3**，与 Pearson 结果一致，结论稳健
- 上调方向：AUPR 更偏向 NLGN4Y/NLGN1/NRXN1 等神经元黏附分子（很可能环境 RNA），
  LY86 掉出前五——说明"LY86 第一"依赖于 Pearson 指标，需要谨慎表述

## 7. 结论与建议

1. 官方 wrapper 能跑通全部 7 个亚型（24.9 分钟，slim 对象 4,854 基因）。
2. 但这批数据 DE 比例过高，官方默认的"全部 DE + AUPR"排序不稳；建议**方向性基因集 + AUPR 或 Pearson**。
3. 稳健结论：**TGFB1 下调方向**（Pearson 与 AUPR 一致，6–7 个亚型）。
4. 条件性结论：**LY86 上调方向第一**只在 Pearson 下成立；AUPR 下是 NLGN4Y/NLGN1。
5. 下一步：用 `generate_info_tables()` + `generate_prioritization_tables()` 做表达量优先级，
   再用 `make_circos_lr()` / `make_mushroom_plot()` 可视化（R/prioritization.R）。

## 8. 文件

```
official_nichenet_results/20261101_2125/
  receiver_<X>/
    01_ligand_activity_target_combined.png   官方四联组合图
    02_ligand_lfc_sender_threecolor.png      配体在 sender 的 LFC 三色热图
    03_ligand_target_heatmap.png
    04_ligand_receptor_heatmap.png
    05_ligand_expression_dotplot.png
    06_target_expression_dotplot_split.png   靶基因表达（按 AD/对照拆分）
    07_receptor_expression_dotplot_split.png 受体表达（按 AD/对照拆分）
    ligand_activities.csv / ligand_target_df.csv / ligand_receptor_df.csv / geneset_DE.txt
  SUMMARY_official_aggregate.csv
  COMPARISON_official_vs_previous.csv
official_aupr_directional/                   方向性 AUPR 结果（官方 predict_ligand_activities）
```
