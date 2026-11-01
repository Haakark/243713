library(nichenetr)
library(Seurat)
library(tidyverse)

# ========== 加载数据库（你的文件） ==========
lr_network <- readRDS("lr_network_human_21122021.rds")
ligand_target_matrix <- readRDS("ligand_target_matrix_nsga2r_final.rds")

# ========== 定义sender、receiver ==========
Idents(seurat_obj) <- seurat_obj$cluster
sender_clusters  <- c("MG1", "MG2", "MG3")
receiver_clusters <- c("EX1","EX2","EX3","EX4","EX5","INH1","INH2","INH3","INH4")

# 校验cluster名称
all_clusters <- unique(Idents(seurat_obj))
check_vec <- c(sender_clusters, receiver_clusters)
if(!all(check_vec %in% all_clusters)){
  stop(paste("不存在的cluster：", setdiff(check_vec, all_clusters)))
}

# ---------------------- 步骤1：筛选sender（小胶质）表达基因 ----------------------
expressed_genes_sender <- get_expressed_genes(
  sender_clusters,
  seurat_obj,
  pct = 0.1,
  assay = "RNA"
)

# ---------------------- 步骤2：筛选receiver（神经元）表达基因 ----------------------
expressed_genes_receiver <- get_expressed_genes(
  receiver_clusters,
  seurat_obj,
  pct = 0.1,
  assay = "RNA"
)

# ---------------------- 步骤3：找receiver的DE靶基因（神经元特异性上调基因） ----------------------
receiver_de <- FindMarkers(
  seurat_obj,
  ident.1 = receiver_clusters,
  ident.2 = setdiff(all_clusters, receiver_clusters),
  min.pct = 0.1,
  assay = "RNA"
)
receiver_targets <- receiver_de %>%
  filter(p_val_adj < 0.05, avg_log2FC > 0.25) %>%
  rownames()

# ---------------------- 步骤4：背景基因集 ----------------------
background_expressed_genes <- union(expressed_genes_sender, expressed_genes_receiver) %>%
  intersect(rownames(ligand_target_matrix))

# ---------------------- 步骤5：筛选潜在配体（小胶质表达、数据库存在的配体） ----------------------
potential_ligands <- lr_network %>%
  pull(from) %>%
  unique() %>%
  intersect(expressed_genes_sender)

# ---------------------- 步骤6：NicheNet核心预测 ----------------------
ligand_activities <- predict_ligand_activities(
  geneset = receiver_targets,
  background_expressed_genes = background_expressed_genes,
  ligand_target_matrix = ligand_target_matrix,
  potential_ligands = potential_ligands
)

# 按Pearson相关排序
ligand_activities <- ligand_activities %>% arrange(-pearson)
top_ligands <- ligand_activities$test_ligand

# ---------------------- 步骤7：提取配体-靶基因、配体-受体关系 ----------------------
# top30配体对应的靶基因矩阵
ligand_target_top30 <- ligand_target_matrix[receiver_targets, top_ligands[1:30]]
# 配体受体互作对
lr_top30 <- lr_network %>%
  filter(from %in% top_ligands[1:30], to %in% expressed_genes_receiver) %>%
  distinct(from, to)

# ---------------------- 输出csv，和你文件夹命名对齐 ----------------------
write.csv(ligand_activities, "ligand_activities_all.csv", row.names = F)
write.csv(ligand_target_top30, "ligand_target_top30.csv", row.names = T)
write.csv(lr_top30, "lr_pairs_top30.csv", row.names = F)

# 查看top配体
head(ligand_activities, 20)
# 1. 配体活性条形图
plot_ligand_activity_bar(ligand_activities, top_n = 20)

# 2. 配体-靶基因热图
ligand_target_heatmap(ligand_target_matrix, ligand_activities, receiver_targets, top_n_ligands = 20, top_n_target = 40)

# 3. LR网络图
lr_network_top <- lr_network %>% filter(from %in% top_ligands[1:15], to %in% expressed_genes_receiver)
plot_ligand_receptor_network(lr_network_top)

