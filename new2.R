# ==================== NICHE NET 完整标准流水线：AD VS Control｜其他细胞调控小胶质细胞mic【上调+下调双通路完整版】 ====================
setwd("C:/Users/lenovo/Desktop/nichenet_data")
library(Seurat)
library(tidyverse)
library(nichenetr)
library(pheatmap)
library(patchwork)

# ========== 补上缺失的 make_heatmap_ggplot 函数 ==========
make_heatmap_ggplot <- function(mat, xlab, ylab, legend_title, color = "purple"){
  df <- as.data.frame(mat) %>%
    rownames_to_column("y") %>%
    pivot_longer(-y, names_to = "x", values_to = "value")
  p <- ggplot(df, aes(x = x, y = y, fill = value)) +
    geom_tile() +
    scale_fill_viridis_c(option = color) +
    labs(x = xlab, y = ylab, fill = legend_title)+
    theme_bw()+
    theme(axis.text.x = element_blank(), axis.ticks.x = element_blank())
  return(p)
}

# ==================== 2. 加载NicheNet网络 ====================
lr_network           <- readRDS("lr_network_human_21122021.rds")
ligand_target_matrix <- readRDS("ligand_target_matrix_nsga2r_final.rds")
weighted_networks    <- readRDS("weighted_networks_nsga2r_final.rds")

# ==================== 3. 从RData加载内置Seurat对象 ====================
rdata_path <- "C:/Users/lenovo/Desktop/nichenet_data/YaqiaoLi_data.RData"
loaded_objs <- load(rdata_path)
cat("RData中包含的对象：", paste(loaded_objs, collapse = ", "), "\n")
seurat_obj <- NULL
for (obj_name in loaded_objs) {
  obj <- get(obj_name)
  if (inherits(obj, "Seurat")) {
    seurat_obj <- obj
    cat("✅ 自动检测到Seurat对象：", obj_name, "\n")
    break
  }
}
if (is.null(seurat_obj)) {
  common_names <- c("seurat_obj", "obj", "sce", "seurat", "srat", "sc_obj")
  for (nm in common_names) {
    if (nm %in% loaded_objs && inherits(get(nm), "Seurat")) {
      seurat_obj <- get(nm)
      cat("✅ 通过常见名匹配到Seurat对象：", nm, "\n")
      break
    }
  }
}
if (is.null(seurat_obj) && length(loaded_objs) == 1) {
  seurat_obj <- get(loaded_objs[1])
}
if (is.null(seurat_obj)) stop("❌ 未能在RData中找到Seurat对象！")

# 自动检测细胞类型列
celltype_col <- NULL
for (col in c("Cell.Type", "cell_type", "CellType", "celltype", "CellType_label", "cell_type_label")) {
  if (col %in% colnames(seurat_obj@meta.data)) { celltype_col <- col; break }
}
if (is.null(celltype_col)) {
  seurat_obj$Cell.Type <- as.character(Idents(seurat_obj))
  celltype_col <- "Cell.Type"
}
if (celltype_col != "Cell.Type") seurat_obj$Cell.Type <- seurat_obj@meta.data[[celltype_col]]
cat("使用的细胞类型列：", celltype_col, "\n")
print(table(seurat_obj$Cell.Type))

# ---------- 自动检测病例分组列（Diagnosis / diagnosis / Group / group）----------
group_col <- NULL
for (col in c("Diagnosis", "diagnosis", "Group", "group", "Condition", "condition")) {
  if (col %in% colnames(seurat_obj@meta.data)) {
    group_col <- col
    break
  }
}
if (is.null(group_col)) stop("❌ 未找到病例分组列！请检查 meta.data 列名：", paste(colnames(seurat_obj@meta.data), collapse=", "))
seurat_obj$Diagnosis <- seurat_obj@meta.data[[group_col]]
cat("使用的病例分组列：", group_col, "（已统一为 Diagnosis）\n")
print(table(seurat_obj$Diagnosis))

# 不再重新NormalizeData（已有data层）
if (!"data" %in% names(seurat_obj@assays$RNA)) {
  seurat_obj@assays$RNA$data <- seurat_obj@assays$RNA@counts
}
cat("ℹ️ 对象已存在归一化data层，跳过NormalizeData\n")

# ==================== 4. 仅对小胶质细胞mic做病例-对照差异分析 ====================
mic_seurat <- subset(seurat_obj, Cell.Type == "mic")
Idents(mic_seurat) <- mic_seurat$Diagnosis
cat("mic细胞 ident 分组：\n")
print(table(Idents(mic_seurat)))

# 自动识别 AD 组和对照组
all_groups <- unique(seurat_obj$Diagnosis)
ad_group  <- all_groups[grepl("AD|Alzheimer|case", all_groups, ignore.case = TRUE)][1]
ctl_group <- all_groups[!all_groups %in% ad_group][1]
if (is.na(ad_group) || is.na(ctl_group)) stop("❌ 无法自动识别 AD/对照组，请手动指定 ident.1 和 ident.2")
cat("自动识别 → AD组：", ad_group, " 对照组：", ctl_group, "\n")

deg_mg <- FindMarkers(mic_seurat, ident.1 = ad_group, ident.2 = ctl_group,
                      min.pct = 0.1, logfc.threshold = 0)
deg_mg <- deg_mg[deg_mg$p_val_adj < 0.05, ]
cat("\n===== mic：AD-ctl显著差异基因总数：",nrow(deg_mg),"=====\n")

# ==================== 5. 自动寻找最优logFC：上调&下调基因严格控制在200-300之间 ====================
# 上调（mic：AD > ctl）
fc_candidate_up <- seq(0.05, 1.2, by = 0.02)
fc_up_count <- sapply(fc_candidate_up, function(fc){sum(deg_mg$avg_log2FC > fc)})
df_up_search <- data.frame(logFC = fc_candidate_up, gene_num = fc_up_count)
target_range_up <- df_up_search %>% filter(gene_num >=200 & gene_num <=300)
if(nrow(target_range_up)>0){
  chosen_up <- min(target_range_up$logFC)
}else{
  chosen_up <- df_up_search$logFC[which.min(abs(df_up_search$gene_num-250))]
}
total_up <- sum(deg_mg$avg_log2FC > chosen_up)

# 下调（mic：AD < ctl）
fc_candidate_down <- seq(0.05, 1.2, by = 0.02)
fc_down_count <- sapply(fc_candidate_down, function(fc){sum(deg_mg$avg_log2FC < -fc)})
df_down_search <- data.frame(logFC = fc_candidate_down, gene_num = fc_down_count)
target_range_down <- df_down_search %>% filter(gene_num >=200 & gene_num <=300)
if(nrow(target_range_down)>0){
  chosen_down <- min(target_range_down$logFC)
}else{
  chosen_down <- df_down_search$logFC[which.min(abs(df_down_search$gene_num-250))]
}
total_down <- sum(deg_mg$avg_log2FC < -chosen_down)
if(total_down < 150){
  chosen_down <- 0.05
  total_down <- sum(deg_mg$avg_log2FC < -chosen_down)
  cat("⚠️ 下调基因不足，自动放宽阈值兜底，下调基因数：",total_down,"\n")
}
cat("✅ 上调logFC阈值：",round(chosen_up,4)," 上调基因数total_up =",total_up,"(200-300)\n")
cat("✅ 下调logFC阈值：",round(chosen_down,4)," 下调基因数total_down =",total_down,"(200-300)\n")
genes_up   <- rownames(deg_mg)[deg_mg$avg_log2FC > chosen_up]
genes_down <- rownames(deg_mg)[deg_mg$avg_log2FC < -chosen_down]

# ==================== 6. 定义发送/接收细胞，剔除mic自分泌 ====================
background_genes  <- rownames(seurat_obj)
receiver_celltype <- "mic"
sender_celltypes  <- setdiff(unique(seurat_obj$Cell.Type), receiver_celltype)
avg_expr <- AverageExpression(seurat_obj, assays = "RNA", group.by = "Cell.Type")$RNA
sender_expressed <- lapply(sender_celltypes, function(ct) rownames(avg_expr)[avg_expr[, ct] > 0.1])
all_sender_genes  <- unique(unlist(sender_expressed))
potential_ligands <- intersect(lr_network$from, all_sender_genes)

# ==================== 7. NicheNet配体活性预测(Pearson) ====================
# ========== 释放内存：删除不再需要的大对象 ==========
rm(mic_seurat, deg_mg, 
   fc_candidate_up, fc_candidate_down,
   fc_up_count, fc_down_count,
   df_up_search, df_down_search,
   target_range_up, target_range_down,
   avg_expr, sender_expressed, all_sender_genes)
gc()  # 强制垃圾回收
cat("✅ 内存已清理，开始配体活性预测\n")

lig_act_up <- predict_ligand_activities(
  geneset = genes_up, background_expressed_genes = background_genes,
  ligand_target_matrix = ligand_target_matrix, potential_ligands = potential_ligands)
lig_act_down <- predict_ligand_activities(
  geneset = genes_down, background_expressed_genes = background_genes,
  ligand_target_matrix = ligand_target_matrix, potential_ligands = potential_ligands)
write.csv(lig_act_up,"NicheNet_mic_up_ligands_Pearson.csv",row.names=F)
write.csv(lig_act_down,"NicheNet_mic_down_ligands_Pearson.csv",row.names=F)

# ==================== 8. Pearson配体活性直方图+85%分位数筛选 ====================
p_hist_up <- lig_act_up %>%
  ggplot(aes(x = pearson)) +
  geom_histogram(bins = 30, fill = "darkorange", color = "black") +
  geom_vline(xintercept = quantile(lig_act_up$pearson, 0.85), color = "red", linetype = "dashed", size = 1) +
  labs(x = "ligand activity (PCC)", y = "# ligands", title = "Ligand activity distribution (mic up-genes)") +
  theme_classic()
print(p_hist_up)
ggsave("NicheNet_上调_配体活性直方图.png", p_hist_up, width=6, height=4, dpi=300)
threshold_up <- quantile(lig_act_up$pearson, 0.85)
best_up_ligands <- lig_act_up %>% filter(pearson >= threshold_up) %>% arrange(-pearson) %>% pull(test_ligand)

p_hist_down <- lig_act_down %>%
  ggplot(aes(x = pearson)) +
  geom_histogram(bins = 30, fill = "darkorange", color = "black") +
  geom_vline(xintercept = quantile(lig_act_down$pearson, 0.85), color = "red", linetype = "dashed", size = 1) +
  labs(x = "ligand activity (PCC)", y = "# ligands", title = "Ligand activity distribution (mic down-genes)") +
  theme_classic()
print(p_hist_down)
ggsave("NicheNet_下调_配体活性直方图.png", p_hist_down, width=6, height=4, dpi=300)
threshold_down <- quantile(lig_act_down$pearson, 0.85)
best_down_ligands <- lig_act_down %>% filter(pearson >= threshold_down) %>% arrange(-pearson) %>% pull(test_ligand)

# ==================== 9. 配体活性条形图（按Pearson降序排列，最高在最上面）====================
#----------上调通路----------
ligand_bar_up <- lig_act_up %>%
  filter(test_ligand %in% best_up_ligands) %>%
  arrange(desc(pearson)) %>%
  mutate(test_ligand = factor(test_ligand, levels = rev(test_ligand)))

p_bar_up <- ggplot(ligand_bar_up, aes(x = pearson, y = test_ligand, fill = pearson)) +
  geom_col() +
  scale_fill_gradient(low = "#FFE0B2", high = "#E65100", name = "Pearson correlation") +
  labs(x = "Pearson correlation", y = "Prioritized ligands",
       title = "Prioritized ligands for mic up-regulation") +
  theme_bw() +
  theme(axis.text.y = element_text(size = 8),
        plot.title = element_text(hjust = 0.5))
print(p_bar_up)
ggsave("NicheNet_上调_配体活性条形图.png", p_bar_up, width=6, height=8, dpi=300)

#----------下调通路----------
ligand_bar_down <- lig_act_down %>%
  filter(test_ligand %in% best_down_ligands) %>%
  arrange(desc(pearson)) %>%
  mutate(test_ligand = factor(test_ligand, levels = rev(test_ligand)))

p_bar_down <- ggplot(ligand_bar_down, aes(x = pearson, y = test_ligand, fill = pearson)) +
  geom_col() +
  scale_fill_gradient(low = "#FFE0B2", high = "#E65100", name = "Pearson correlation") +
  labs(x = "Pearson correlation", y = "Prioritized ligands",
       title = "Prioritized ligands for mic down-regulation") +
  theme_bw() +
  theme(axis.text.y = element_text(size = 8),
        plot.title = element_text(hjust = 0.5))
print(p_bar_down)
ggsave("NicheNet_下调_配体活性条形图.png", p_bar_down, width=6, height=8, dpi=300)

# ==================== 10. 官方原版配体靶基因热图｜上调+下调（RP阈值0.1过滤） ====================
max_target_show <- 40

#----------上调通路----------
common_targets_up <- intersect(genes_up, rownames(ligand_target_matrix))
common_ligands_up <- intersect(best_up_ligands, colnames(ligand_target_matrix))
raw_lt_up <- ligand_target_matrix[common_targets_up, common_ligands_up]
# 过滤 Regulatory potential > 0.1
raw_lt_up[raw_lt_up < 0.1] <- 0
# 去除全0靶基因
raw_lt_up <- raw_lt_up[rowSums(raw_lt_up) > 0, ]
raw_lt_up <- raw_lt_up[,order(colSums(raw_lt_up),decreasing = TRUE)]
# 最多展示前15个配体，防止过密
if(ncol(raw_lt_up)>15) raw_lt_up <- raw_lt_up[,1:15]
# 靶基因过多时最多取前40个
if(nrow(raw_lt_up) > max_target_show) raw_lt_up <- raw_lt_up[1:max_target_show, ]
vis_mat_up <- t(raw_lt_up)
heat_df_up <- as.data.frame(vis_mat_up) %>%
  rownames_to_column("Ligand") %>%
  pivot_longer(-Ligand, names_to = "Target_gene", values_to = "Regulatory_potential")
p_heat_up <- ggplot(heat_df_up, aes(x = Target_gene, y = Ligand, fill = Regulatory_potential)) +
  geom_tile() +
  scale_fill_gradient(low = "whitesmoke", high = "purple", name = "Regulatory potential") +
  labs(x = "Predicted target genes", y = "Prioritized ligands") +
  theme_bw() +
  theme(
    axis.text.x = element_text(angle = 90, hjust = 1, size=6),
    axis.text.y = element_text(size=7),
    legend.position = "top",
    panel.border = element_blank(),
    panel.grid = element_blank()
  )
print(p_heat_up)
plot_w_up <- max(8, nrow(raw_lt_up)*0.35)
ggsave("NicheNet_上调_官方原版配体靶基因热图.png", p_heat_up, width=plot_w_up, height=8, dpi=300)

#----------下调通路----------
common_targets_down <- intersect(genes_down, rownames(ligand_target_matrix))
common_ligands_down <- intersect(best_down_ligands, colnames(ligand_target_matrix))
raw_lt_down <- ligand_target_matrix[common_targets_down, common_ligands_down]
raw_lt_down[raw_lt_down < 0.1] <- 0
raw_lt_down <- raw_lt_down[rowSums(raw_lt_down) > 0, ]
raw_lt_down <- raw_lt_down[,order(colSums(raw_lt_down),decreasing = TRUE)]
if(ncol(raw_lt_down)>15) raw_lt_down <- raw_lt_down[,1:15]
if(nrow(raw_lt_down) > max_target_show) raw_lt_down <- raw_lt_down[1:max_target_show, ]
vis_mat_down <- t(raw_lt_down)
heat_df_down <- as.data.frame(vis_mat_down) %>%
  rownames_to_column("Ligand") %>%
  pivot_longer(-Ligand, names_to = "Target_gene", values_to = "Regulatory_potential")
p_heat_down <- ggplot(heat_df_down, aes(x = Target_gene, y = Ligand, fill = Regulatory_potential)) +
  geom_tile() +
  scale_fill_gradient(low = "whitesmoke", high = "purple", name = "Regulatory potential") +
  labs(x = "Predicted target genes", y = "Prioritized ligands") +
  theme_bw() +
  theme(
    axis.text.x = element_text(angle = 90, hjust = 1, size=6),
    axis.text.y = element_text(size=7),
    legend.position = "top",
    panel.border = element_blank(),
    panel.grid = element_blank()
  )
print(p_heat_down)
plot_w_down <- max(8, nrow(raw_lt_down)*0.35)
ggsave("NicheNet_下调_官方原版配体靶基因热图.png", p_heat_down, width=plot_w_down, height=8, dpi=300)

# ==================== 分析全部完成 ====================
cat("\n===== NicheNet完整双通路(上调+下调)分析全部完成！AD-ctl对比，RP阈值0.1过滤 =====")

