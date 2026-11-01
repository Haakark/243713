## 用官方 nichenetr::nichenet_seuratobj_aggregate() 重做 7 个亚型的分析
## 对象：official_data_slim.rds（4,854 个表达基因 × 38,664 cells，见 make_slim_object.R）
suppressPackageStartupMessages({
  library(Seurat); library(SeuratObject); library(nichenetr)
  library(dplyr); library(ggplot2); library(cowplot)
})
setwd("C:/Users/lenovo/Desktop/nichenet_data")
t_start <- Sys.time()

lr_network           <- readRDS("lr_network_human_21122021.rds")
ligand_target_matrix <- readRDS("ligand_target_matrix_nsga2r_final.rds")
weighted_networks    <- readRDS("weighted_networks_nsga2r_final.rds")

obj <- readRDS("official_data_slim.rds")
Idents(obj) <- "cell_type_use"
cat("object:", paste(dim(obj), collapse = " x "), "\n")

receivers <- c("Homeos1", "Homeos2", "Homeos3", "Inflam.DAM",
               "Lipo.DAM", "Ribo.DAM1", "Ribo.DAM2")
outdir <- file.path("official_nichenet_results", format(Sys.time(), "%Y%m%d_%H%M"))
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
cat("outdir:", outdir, "\n")

summ <- list()
for (rcv in receivers) {
  cat("\n==================================================\n")
  cat("receiver:", rcv, " start:", format(Sys.time()), "\n")
  rdir <- file.path(outdir, paste0("receiver_", rcv))
  dir.create(rdir, recursive = TRUE, showWarnings = FALSE)

  res <- tryCatch(
    nichenet_seuratobj_aggregate(
      receiver = rcv,
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
      top_n_ligands = 30,
      verbose = TRUE),
    error = function(e) { cat("FAIL:", conditionMessage(e), "\n"); NULL })

  if (is.null(res)) {
    summ[[rcv]] <- data.frame(receiver = rcv, n_geneset = NA, top_ligand = NA,
                              top5 = NA, note = "aggregate 失败")
    next
  }

  saveRDS(res, file.path(rdir, "aggregate_result.rds"))
  write.csv(res$ligand_activities, file.path(rdir, "ligand_activities.csv"), row.names = FALSE)
  writeLines(res$geneset_oi, file.path(rdir, "geneset_DE.txt"))
  if (!is.null(res$ligand_target_df))
    write.csv(res$ligand_target_df, file.path(rdir, "ligand_target_df.csv"), row.names = FALSE)
  if (!is.null(res$ligand_receptor_df))
    write.csv(res$ligand_receptor_df, file.path(rdir, "ligand_receptor_df.csv"), row.names = FALSE)

  save_plot <- function(p, file, w, h) {
    if (is.null(p)) return(invisible(NULL))
    tryCatch(ggsave(file.path(rdir, file), p, width = w, height = h, dpi = 300,
                    limitsize = FALSE),
             error = function(e) cat("plot fail:", file, conditionMessage(e), "\n"))
  }
  save_plot(res$ligand_activity_target_heatmap, "01_ligand_activity_target_combined.png", 18, 7)
  save_plot(res$ligand_differential_expression_heatmap, "02_ligand_lfc_sender_threecolor.png", 8, 7)
  save_plot(res$ligand_target_heatmap, "03_ligand_target_heatmap.png", 11, 7)
  save_plot(res$ligand_receptor_heatmap, "04_ligand_receptor_heatmap.png", 9, 7)
  save_plot(res$ligand_expression_dotplot, "05_ligand_expression_dotplot.png", 8, 8)

  summ[[rcv]] <- data.frame(
    receiver = rcv,
    n_geneset = length(res$geneset_oi),
    top_ligand = res$top_ligands[1],
    top5 = paste(head(res$top_ligands, 5), collapse = ","),
    note = "")

  cat("done:", rcv, " elapsed:", round(difftime(Sys.time(), t_start, units = "mins"), 1), "min\n")
  rm(res); gc()
}

summary_tbl <- bind_rows(summ)
write.csv(summary_tbl, file.path(outdir, "SUMMARY_official_aggregate.csv"), row.names = FALSE)
print(summary_tbl)
cat("\nALL DONE, total min:", round(difftime(Sys.time(), t_start, units = "mins"), 1), "\n")
