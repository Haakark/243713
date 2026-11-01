## 用官方 nichenetr 的 nichenet_seuratobj_aggregate() 跑一个 receiver 做冒烟测试
suppressPackageStartupMessages({
  library(Seurat); library(SeuratObject); library(nichenetr); library(dplyr); library(ggplot2)
})
setwd("C:/Users/lenovo/Desktop/nichenet_data")
t0 <- Sys.time()

lr_network           <- readRDS("lr_network_human_21122021.rds")
ligand_target_matrix <- readRDS("ligand_target_matrix_nsga2r_final.rds")
weighted_networks    <- readRDS("weighted_networks_nsga2r_final.rds")

e <- new.env(); load("scRNA.RData", envir = e); obj <- e$scRNA; rm(e); gc()
obj <- DietSeurat(obj, assays = "RNA", dimreducs = NULL, graphs = NULL)
obj$cell_type_use <- obj@meta.data[["cell_type"]]
obj$group_use     <- obj@meta.data[["Group"]]
keep <- c("Homeos1","Homeos2","Homeos3","Inflam.DAM","Lipo.DAM","Ribo.DAM1","Ribo.DAM2")
obj <- subset(obj, cells = rownames(obj@meta.data)[obj$cell_type_use %in% keep])
Idents(obj) <- "cell_type_use"
cat("cells:", ncol(obj), " time:", round(difftime(Sys.time(), t0, units = "mins"), 1), "min\n")

dir.create("official_test", showWarnings = FALSE)
cat("start aggregate:", format(Sys.time()), "\n")
res <- nichenet_seuratobj_aggregate(
  receiver = "Homeos1",
  seurat_obj = obj,
  condition_colname = "group_use",
  condition_oi = "AD",
  condition_reference = "No Neuropathology",
  sender = "all",
  ligand_target_matrix = ligand_target_matrix,
  lr_network = lr_network,
  weighted_networks = weighted_networks,
  assay_oi = "RNA",
  expression_pct = 0.1,
  lfc_cutoff = 0.25,
  geneset = "DE",
  top_n_ligands = 30
)
cat("done aggregate:", format(Sys.time()), " elapsed:",
    round(difftime(Sys.time(), t0, units = "mins"), 1), "min\n")

saveRDS(res, "official_test/aggregate_Homeos1.rds")
print(head(res$ligand_activities, 10))
cat("n geneset:", length(res$geneset_oi), "\n")

ggsave("official_test/ligand_activity_target_heatmap.png", res$ligand_activity_target_heatmap,
       width = 18, height = 7, dpi = 300, limitsize = FALSE)
ggsave("official_test/ligand_differential_expression_heatmap.png",
       res$ligand_differential_expression_heatmap, width = 8, height = 7, dpi = 300)
ggsave("official_test/ligand_target_heatmap.png", res$ligand_target_heatmap,
       width = 10, height = 7, dpi = 300)
ggsave("official_test/ligand_receptor_heatmap.png", res$ligand_receptor_heatmap,
       width = 8, height = 7, dpi = 300)
cat("plots saved\n")
