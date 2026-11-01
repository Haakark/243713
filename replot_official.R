## 重新导出官方图：统一放大画布、旋转/缩小坐标标签，避免重叠
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

  ## 05 配体表达 DotPlot：x 轴斜排 + 缩小字号
  p <- res$ligand_expression_dotplot
  if (!is.null(p)) {
    p <- p + theme(axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1, size = 9),
                   axis.text.y = element_text(size = 8),
                   axis.title = element_text(size = 10))
    ggsave(file.path(d, "05_ligand_expression_dotplot.png"), p,
           width = 9, height = 7, dpi = 300, limitsize = FALSE)
  }

  ## 03 配体-靶基因热图：加宽 + 缩小 x 标签
  p <- res$ligand_target_heatmap
  if (!is.null(p)) {
    p <- p + theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.5, size = 3.5),
                   axis.text.y = element_text(size = 7))
    ggsave(file.path(d, "03_ligand_target_heatmap.png"), p,
           width = 24, height = 9, dpi = 300, limitsize = FALSE)
  }

  ## 04 配体-受体热图
  p <- res$ligand_receptor_heatmap
  if (!is.null(p)) {
    p <- p + theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
                   axis.text.y = element_text(size = 8))
    ggsave(file.path(d, "04_ligand_receptor_heatmap.png"), p,
           width = 10, height = 8, dpi = 300, limitsize = FALSE)
  }

  ## 02 配体 LFC 三色热图
  p <- res$ligand_differential_expression_heatmap
  if (!is.null(p)) {
    p <- p + theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 9),
                   axis.text.y = element_text(size = 7))
    ggsave(file.path(d, "02_ligand_lfc_sender_threecolor.png"), p,
           width = 8, height = 9, dpi = 300, limitsize = FALSE)
  }

  ## 01 官方四联组合图：加大画布
  p <- res$ligand_activity_target_heatmap
  if (!is.null(p)) {
    ggsave(file.path(d, "01_ligand_activity_target_combined.png"), p,
           width = 22, height = 11, dpi = 300, limitsize = FALSE)
  }
  cat("re-exported:", rcv, "\n")
}
