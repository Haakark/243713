## 用官方 predict_ligand_activities（AUPR 排序）+ 方向性基因集（top200 up / down）重跑配体活性
## 与官方 wrapper（全部 DE 基因）对比：后者基因集占背景 53%，AUPR 基线过高、排序不稳。
suppressPackageStartupMessages({
  library(Seurat); library(SeuratObject); library(nichenetr); library(dplyr)
})
setwd("C:/Users/lenovo/Desktop/nichenet_data")

lr_network           <- readRDS("lr_network_human_21122021.rds")
ligand_target_matrix <- readRDS("ligand_target_matrix_nsga2r_final.rds")

obj <- readRDS("official_data_slim.rds")
Idents(obj) <- "cell_type_use"
receivers <- c("Homeos1","Homeos2","Homeos3","Inflam.DAM","Lipo.DAM","Ribo.DAM1","Ribo.DAM2")
senders   <- receivers

prev_dir <- "NicheNet_results_7subtypes/20261031_1842"
outdir <- "official_aupr_directional"
dir.create(outdir, showWarnings = FALSE)

expressed <- lapply(c(receivers, senders), function(ct) get_expressed_genes(ct, obj, pct = 0.1))
names(expressed) <- c(receivers, senders)
sender_expr <- unique(unlist(expressed[senders]))

summ <- list()
for (rcv in receivers) {
  rdir <- file.path(outdir, paste0("receiver_", rcv)); dir.create(rdir, showWarnings = FALSE)
  recv_expr <- expressed[[rcv]]
  background <- intersect(recv_expr, rownames(ligand_target_matrix))
  expressed_ligands  <- intersect(unique(lr_network$from), sender_expr)
  expressed_receptors <- intersect(unique(lr_network$to), recv_expr)
  potential_ligands <- lr_network %>%
    filter(from %in% expressed_ligands, to %in% expressed_receptors) %>%
    pull(from) %>% unique()

  for (tag in c("up", "down")) {
    f <- file.path(prev_dir, paste0("receiver_", rcv), paste0("geneset_", tag, ".txt"))
    if (!file.exists(f)) next
    gs <- readLines(f)
    gs <- intersect(gs, rownames(ligand_target_matrix))
    if (length(gs) < 20) { cat(rcv, tag, "geneset too small, skip\n"); next }
    la <- predict_ligand_activities(geneset = gs, background_expressed_genes = background,
                                    ligand_target_matrix = ligand_target_matrix,
                                    potential_ligands = potential_ligands) %>%
      arrange(desc(aupr_corrected)) %>% mutate(rank = row_number())
    write.csv(la, file.path(rdir, paste0("ligand_activity_aupr_", tag, ".csv")), row.names = FALSE)
    cat(sprintf("%-11s %-4s n=%4d top: %s\n", rcv, tag, length(gs),
                paste(head(la$test_ligand, 5), collapse = ", ")))
    summ[[paste(rcv, tag)]] <- data.frame(receiver = rcv, direction = tag,
                                          n_geneset = length(gs),
                                          top5 = paste(head(la$test_ligand, 5), collapse = ","))
  }
}
write.csv(bind_rows(summ), file.path(outdir, "SUMMARY_aupr_directional.csv"), row.names = FALSE)
cat("done\n")
