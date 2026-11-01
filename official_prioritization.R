## 官方表达量优先级流程：generate_info_tables + generate_prioritization_tables
## 再用官方 make_circos_lr / make_mushroom_plot 可视化（seurat_steps_prioritization.Rmd 的做法）
suppressPackageStartupMessages({
  library(Seurat); library(SeuratObject); library(nichenetr)
  library(dplyr); library(ggplot2); library(cowplot); library(patchwork)
})
setwd("C:/Users/lenovo/Desktop/nichenet_data")

lr_network           <- readRDS("lr_network_human_21122021.rds") %>% distinct(from, to)
ligand_target_matrix <- readRDS("ligand_target_matrix_nsga2r_final.rds")

obj <- readRDS("official_data_slim.rds")
Idents(obj) <- "cell_type_use"

receivers <- c("Homeos1","Homeos2","Homeos3","Inflam.DAM","Lipo.DAM","Ribo.DAM1","Ribo.DAM2")
subtype_colors <- c(Homeos1 = "#1B2A5B", Homeos2 = "#2C7FB8", Homeos3 = "#6BAED6",
                    Inflam.DAM = "#A50F15", Lipo.DAM = "#FC9272",
                    Ribo.DAM1 = "#006D2C", Ribo.DAM2 = "#A1D99B")

agg_dir <- "official_nichenet_results/20261101_2125"
outdir  <- "official_prioritization"
dir.create(outdir, showWarnings = FALSE)

targets <- c("Homeos1", "Insurance" )
targets <- c("Homeos1", "Inflam.DAM", "Lipo.DAM")

for (rcv in targets) {
  cat("\n==== ", rcv, " ====\n")
  rdir <- file.path(outdir, paste0("receiver_", rcv)); dir.create(rdir, showWarnings = FALSE)
  res <- readRDS(file.path(agg_dir, paste0("receiver_", rcv), "aggregate_result.rds"))
  la  <- res$ligand_activities

  lr_filtered <- lr_network %>%
    filter(from %in% la$test_ligand, to %in% res$background_expressed_genes)

  info <- generate_info_tables(
    obj, celltype_colname = "cell_type_use",
    senders_oi = receivers, receivers_oi = rcv,
    lr_network_filtered = lr_filtered,
    condition_colname = "group_use", condition_oi = "AD",
    condition_reference = "No Neuropathology",
    scenario = "case_control", assay_oi = "RNA")

  prior <- generate_prioritization_tables(
    info$sender_receiver_info, info$sender_receiver_de, la,
    info$lr_condition_de, scenario = "case_control")
  write.csv(prior, file.path(rdir, "prioritization_table.csv"), row.names = FALSE)
  cat("prior rows:", nrow(prior), " top score:",
      round(max(prior$prioritization_score, na.rm = TRUE), 3), "\n")

  ## Circos（官方 make_circos_lr）
  top_c <- prior %>% slice_max(prioritization_score, n = 50)
  p_circ <- tryCatch({
    make_circos_lr(top_c,
                   colors_sender   = subtype_colors[intersect(names(subtype_colors), unique(top_c$sender))],
                   colors_receiver = subtype_colors[rcv])
  }, error = function(e) { cat("circos fail:", conditionMessage(e), "\n"); NULL })
  if (!is.null(p_circ)) {
    ggsave(file.path(rdir, "01_circos_top50.png"), p_circ, width = 8, height = 8,
           dpi = 300, limitsize = FALSE)
  }

  ## Mushroom plot（官方 make_mushroom_plot）
  p_m <- tryCatch({
    make_mushroom_plot(prior %>% filter(receiver == rcv), top_n = 30,
                       true_color_range = TRUE, show_rankings = TRUE,
                       show_all_datapoints = FALSE)
  }, error = function(e) { cat("mushroom fail:", conditionMessage(e), "\n"); NULL })
  if (!is.null(p_m)) {
    ggsave(file.path(rdir, "02_mushroom_top30.png"), p_m, width = 8, height = 8,
           dpi = 300, limitsize = FALSE)
  }
  gc()
}
cat("\nDONE\n")
