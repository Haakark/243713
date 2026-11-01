## 第二轮：靶基因太多导致标签不可读 → 只显示 top60 靶基因（展示用，不改变分析结果）；
## mushroom 的 x 轴标签旋转，避免重叠。
suppressPackageStartupMessages({
  library(ggplot2); library(cowplot); library(dplyr); library(nichenetr)
})
setwd("C:/Users/lenovo/Desktop/nichenet_data")
agg <- "official_nichenet_results/20261101_2125"

for (d in list.dirs(agg, recursive = FALSE)) {
  f <- file.path(d, "aggregate_result.rds")
  if (!file.exists(f)) next
  res <- readRDS(f)
  rcv <- sub("^receiver_", "", basename(d))
  m <- res$ligand_target_matrix
  if (is.null(m)) next
  ## m: ligands × targets
  ord <- order(apply(m, 2, max), decreasing = TRUE)
  keep <- colnames(m)[ord][seq_len(min(60, ncol(m)))]
  m2 <- m[, keep, drop = FALSE]
  p <- make_heatmap_ggplot(as.matrix(m2), "Prioritized ligands", "Predicted target genes",
                           color = "purple", legend_title = "Regulatory potential",
                           x_axis_position = "bottom") +
    theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.5, size = 7),
          axis.text.y = element_text(size = 8, face = "italic"),
          legend.position = "top")
  ggsave(file.path(d, "03_ligand_target_heatmap_top60.png"), p,
         width = 13, height = 8, dpi = 300, limitsize = FALSE)
  cat("top60 saved:", rcv, "\n")
}

## mushroom：x 轴标签旋转
pri <- "official_prioritization"
for (d in list.dirs(pri, recursive = FALSE)) {
  f <- file.path(d, "prioritization_table.csv")
  if (!file.exists(f)) next
  rcv <- sub("^receiver_", "", basename(d))
  prior <- read.csv(f)
  p <- make_mushroom_plot(prior %>% filter(receiver == rcv), top_n = 30,
                          true_color_range = TRUE, show_rankings = TRUE,
                          show_all_datapoints = FALSE) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1, size = 9))
  ggsave(file.path(d, "02_mushroom_top30.png"), p, width = 10, height = 10,
         dpi = 300, limitsize = FALSE)
  cat("mushroom saved:", rcv, "\n")
}
