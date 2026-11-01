## 修复官方 make_circos_lr 在 png 设备上只输出图例的问题：
## 用 separate_legend = TRUE 拿到 recordPlot，再在干净 png 设备上 replay。
suppressPackageStartupMessages({
  library(nichenetr); library(dplyr); library(ggplot2); library(cowplot)
})
setwd("C:/Users/lenovo/Desktop/nichenet_data")

subtype_colors <- c(Homeos1 = "#1B2A5B", Homeos2 = "#2C7FB8", Homeos3 = "#6BAED6",
                    Inflam.DAM = "#A50F15", Lipo.DAM = "#FC9272",
                    Ribo.DAM1 = "#006D2C", Ribo.DAM2 = "#A1D99B")

dirs <- list.dirs("official_prioritization", recursive = FALSE)
for (d in dirs) {
  rcv <- sub("^receiver_", "", basename(d))
  f <- file.path(d, "prioritization_table.csv")
  if (!file.exists(f)) next
  prior <- read.csv(f)
  top <- prior %>% slice_max(prioritization_score, n = 50)

  ## 在空设备里跑，避免污染输出文件
  pdf(NULL)
  p <- make_circos_lr(top,
                      colors_sender   = subtype_colors[intersect(names(subtype_colors), unique(top$sender))],
                      colors_receiver = subtype_colors[rcv],
                      separate_legend = TRUE)
  dev.off()

  out <- file.path(d, "01_circos_top50.png")
  png(out, width = 2400, height = 2400, res = 300)
  replayPlot(p$p_circos)
  dev.off()
  cat("circos:", out, "\n")
}
