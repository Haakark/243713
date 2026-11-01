## 第三轮：组合图加大画布；全量配体-靶基因热图改名（保留 top60 展示版）
suppressPackageStartupMessages({ library(ggplot2); library(cowplot) })
setwd("C:/Users/lenovo/Desktop/nichenet_data")
agg <- "official_nichenet_results/20261101_2125"

for (d in list.dirs(agg, recursive = FALSE)) {
  f <- file.path(d, "aggregate_result.rds")
  if (!file.exists(f)) next
  res <- readRDS(f)
  p <- res$ligand_activity_target_heatmap
  if (!is.null(p)) {
    ggsave(file.path(d, "01_ligand_activity_target_combined.png"), p,
           width = 26, height = 13, dpi = 300, limitsize = FALSE)
  }
  full <- file.path(d, "03_ligand_target_heatmap.png")
  if (file.exists(full)) file.rename(full, file.path(d, "03_ligand_target_heatmap_full.png"))
}
cat("done\n")
