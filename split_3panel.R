## 拆图：配体三联图（活性 AUPR + 表达 DotPlot + LFC 热图），共用同一配体行顺序
suppressPackageStartupMessages({
  library(ggplot2); library(cowplot); library(dplyr); library(Seurat)
})
setwd("C:/Users/lenovo/Desktop/nichenet_data")
agg <- "official_nichenet_results/20261101_2125"

obj <- readRDS("official_data_slim.rds")
Idents(obj) <- "cell_type_use"

for (d in list.dirs(agg, recursive = FALSE)) {
  f <- file.path(d, "aggregate_result.rds")
  if (!file.exists(f)) next
  res <- readRDS(f)
  rcv <- sub("^receiver_", "", basename(d))
  lig <- head(res$top_ligands, 20)
  lig_rev <- rev(lig)

  ## A. AUPR 条形图
  p_a <- res$ligand_activities %>%
    filter(test_ligand %in% lig) %>%
    mutate(test_ligand = factor(test_ligand, levels = lig_rev)) %>%
    ggplot(aes(aupr_corrected, test_ligand)) +
    geom_col(fill = "#E6550D", width = 0.7) +
    labs(x = "AUPR (corrected)", y = NULL, title = "Ligand activity") +
    theme_bw(base_size = 9) +
    theme(axis.text.y = element_text(face = "italic", size = 7.5),
          plot.title = element_text(hjust = 0.5, size = 10, face = "bold"),
          panel.grid.minor = element_blank())

  ## B. 配体表达 DotPlot（重建，保证顺序一致）
  p_b <- DotPlot(obj, features = lig_rev, group.by = "cell_type_use") +
    coord_flip() +
    scale_x_discrete(limits = lig_rev) +
    labs(x = NULL, y = NULL, title = "Expression in senders") +
    theme_bw(base_size = 9) +
    theme(axis.text.y = element_text(face = "italic", size = 7.5),
          axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
          plot.title = element_text(hjust = 0.5, size = 10, face = "bold"),
          legend.position = "right", legend.key.size = unit(0.35, "cm"))

  ## C. LFC 热图（官方对象，固定行顺序，去掉官方自带的重复标题）
  p_c <- res$ligand_differential_expression_heatmap +
    scale_y_discrete(limits = lig_rev) +
    labs(title = NULL) +
    theme(axis.text.y = element_text(face = "italic", size = 7.5),
          axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
          legend.position = "right", legend.key.size = unit(0.35, "cm"))

  p <- cowplot::plot_grid(p_a, p_b, p_c, nrow = 1, align = "h", axis = "tb",
                          rel_widths = c(0.85, 1.9, 1.45))
  ggsave(file.path(d, "01_ligand_summary_3panel.png"), p,
         width = 15, height = 7, dpi = 300, limitsize = FALSE)
  cat("3panel:", rcv, "\n")
}
