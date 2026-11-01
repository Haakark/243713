## 用保存的 aggregate 结果重新导出组合图（官方 vignette 尺寸 16x10，避免标题裁切）
suppressPackageStartupMessages({ library(ggplot2); library(cowplot) })
setwd("C:/Users/lenovo/Desktop/nichenet_data")
base <- "official_nichenet_results/20261101_2125"
for (d in list.dirs(base, recursive = FALSE)) {
  f <- file.path(d, "aggregate_result.rds")
  if (!file.exists(f)) next
  res <- readRDS(f)
  p <- res$ligand_activity_target_heatmap
  if (is.null(p)) next
  ggsave(file.path(d, "01_ligand_activity_target_combined.png"), p,
         width = 16, height = 10, dpi = 300, limitsize = FALSE)
  cat("re-saved:", d, "\n")
}
