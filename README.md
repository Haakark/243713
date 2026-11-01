# NicheNet analysis of 7 microglial subtypes in Alzheimer's disease

基于人脑单细胞/单核转录组图谱，使用 [NicheNet](https://github.com/saeyslab/nichenetr) 分析 AD 与对照之间
小胶质细胞 7 个亚型的配体–靶基因–受体–信号通路通讯。

## 分析设计

- **数据**：`scRNA`（61,388 genes × 48,347 cells），剔除 DIMs / MAC 后保留 38,664 cells / 7 个亚群
  - Homeos1 / Homeos2 / Homeos3 / Inflam.DAM / Lipo.DAM / Ribo.DAM1 / Ribo.DAM2
- **分组**：`Group` = `AD` vs `No Neuropathology`
- **receiver**：7 个亚型轮流；**sender**：7 个亚群全部（含自分泌）
- **DE**：亚型内部 AD vs 对照（FindMarkers, Wilcoxon, padj < 0.05, |log2FC| ≥ 0.25, 检出率 ≥ 10%）
- **配体活性**：`predict_ligand_activities`（Pearson / AUPR）
- **下游**：配体–靶基因调控潜力、配体–受体（热图 / Circos / LFC）、ligand→受体→TF→靶基因 通路

## 目录结构

```
NicheNet_7subtypes_AD.R          主分析脚本（7 轮 receiver + 汇总）
make_nichenet_full_ppt.py        生成 24 页汇报 PPT
make_speech_docx.py              生成逐页讲解稿
NicheNet_7subtypes_AD_full_report.pptx   汇报 PPT
NicheNet_7subtypes_AD_analysis.docx      文字版分析报告
NicheNet_7subtypes_讲解稿.docx            讲解稿
NicheNet_results_7subtypes/<时间戳>/      结果（仅提交汇总图与汇总表）
```

## 如何运行

1. 准备数据与先验网络（**不入库，需自行下载**）：
   - `scRNA.RData`：分析用 Seurat 对象（对象名 `scRNA`）
   - `lr_network_human_21122021.rds`
   - `ligand_target_matrix_nsga2r_final.rds`
   - `weighted_networks_nsga2r_final.rds`
   - 网络文件可从 NicheNet 官方 Zenodo 获取：<https://doi.org/10.5281/zenodo.7074291>
2. 运行：
   ```bash
   Rscript NicheNet_7subtypes_AD.R
   ```
   - 环境：R 4.5.x + Seurat 5.x + nichenetr 2.2.x
   - 差异分析结果会缓存到 `NicheNet_cache/`，重跑可跳过 DE
   - 只跑部分亚型：`NICHENET_RECEIVERS="Homeos1,Lipo.DAM" Rscript NicheNet_7subtypes_AD.R`
   - 快速冒烟测试：`NICHENET_QUICK=1 Rscript NicheNet_7subtypes_AD.R`
3. 生成文档：
   ```bash
   python make_nichenet_full_ppt.py
   python make_speech_docx.py
   ```

## 主要结果

| receiver | 显著 DE | top 上调配体 | top 下调配体 |
|---|---|---|---|
| Homeos1 | 2,909 | LY86 | TGFB1 |
| Homeos2 | 1,091 | IL18 | IL1B |
| Homeos3 | 143 | —（基因不足） | TGFB1 |
| Inflam.DAM | 2,627 | NLGN1 | TGFB1 |
| Lipo.DAM | 1,127 | LY86 | TNFRSF14 |
| Ribo.DAM1 | 1,349 | LY86 | TGFB1 |
| Ribo.DAM2 | 492 | LY86 | CALM3 |

- **LY86（MD-2）** 在 4/7 亚型的上调方向排名第一，指向 TLR4 相关先天免疫激活
- **TGFB1** 在 4/7 亚型的下调方向排名第一，提示稳态 TGF-β 信号减弱
- 亚型特异：Homeos2 的 IL18/IL1B、Lipo.DAM 的 TNFRSF14 与 APOE–TREM2、Ribo 亚群的 GAS6–AXL/MERTK

## 注意事项

- 数据来自多个研究，AD/对照在研究间不平衡，DE 未校正研究来源
- NLGN1/NLGN4Y/NRXN1 等神经元黏附分子可能为环境 RNA
- 21122021 版 `lr_network` 未收录 LY86–TLR4
- NicheNet 结果为基于先验网络的相关性推断，需功能实验验证

## 官方 nichenetr 代码重做（2026-11-01）

用 `saeyslab/nichenetr` 的 `nichenet_seuratobj_aggregate()` 对 7 个亚型重跑了一遍：

- 结果：`official_nichenet_results/20261101_2125/`（每个亚型 7 张图 + 4 张表）
- 说明与对比：`official_nichenet_results/20261101_2125/README_official_redo.md`
- 方向性 AUPR：`official_aupr_directional/`

要点：官方默认用“全部 DE 基因 + AUPR”，本数据 DE 占表达基因 53%，AUPR 基线过高（`aupr_corrected` 仅 −0.02~0.015），
排序趋近噪声；改用方向性 top200 基因集后，**TGFB1 下调** 在 Pearson 与 AUPR 下都稳定，而 **LY86 上调第一** 仅在 Pearson 下成立。

## License

仅供学术研究使用。数据版权归原始研究作者所有，请遵循各数据集的使用条款。
