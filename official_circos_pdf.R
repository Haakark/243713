## 官方 make_circos_lr 在 png 上会因多页覆盖而只剩图例；改用 pdf 设备（第 1 页是 circos），
## 再用 LibreOffice 把第 1 页转成 png。
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
  out <- file.path(d, "01_circos_top50.pdf")
  pdf(out, width = 8, height = 8)
  make_circos_lr(top,
                 colors_sender   = subtype_colors[intersect(names(subtype_colors), unique(top$sender))],
                 colors_receiver = subtype_colors[rcv])
  dev.off()
  cat("pdf:", out, "\n")
}
