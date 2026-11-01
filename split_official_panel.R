## 把官方组合图拆开：单独导出「配体活性 AUPR 条形图」；
## 其余部分已有独立文件（02 LFC 热图、05 表达 DotPlot、03_top60 靶基因热图）。
suppressPackageStartupMessages({ library(ggplot2); library(dplyr) })
setwd("C:/Users/lenovo/Desktop/nichenet_data")
agg <- "official_nichenet_results/20261101_2125"

for (d in list.dirs(agg, recursive = FALSE)) {
  f <- file.path(d, "aggregate_result.rds")
  if (!file.exists(f)) next
  res <- readRDS(f)
  rcv <- sub("^receiver_", "", basename(d))
  la <- res$ligand_activities
  top <- head(la, 30)
  p <- ggplot(top, aes(x = aupr_corrected, y = reorder(test_ligand, aupr_corrected))) +
    geom_col(fill = "#E6550D", width = 0.72) +
    labs(x = "Ligand activity (AUPR, corrected)", y = NULL,
         title = paste0(rcv, ": prioritized ligands (top 30)")) +
    theme_bw(base_size = 11) +
    theme(axis.text.y = element_text(face = "italic", size = 9),
          plot.title = element_text(hjust = 0.5, face = "bold", size = 11),
          panel.grid.minor = element_blank())
  ggsave(file.path(d, "01a_ligand_activity_aupr_bar.png"), p,
         width = 7, height = 7, dpi = 300)
  cat("aupr bar:", rcv, "\n")
}
