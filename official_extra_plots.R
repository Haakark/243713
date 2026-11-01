## 在官方 aggregate 结果基础上补充 vignette 里的受体/靶基因表达图，并与之前的 Pearson 结果对比
suppressPackageStartupMessages({
  library(Seurat); library(SeuratObject); library(nichenetr)
  library(dplyr); library(ggplot2)
})
setwd("C:/Users/lenovo/Desktop/nichenet_data")

obj <- readRDS("official_data_slim.rds")
Idents(obj) <- "cell_type_use"

outdir <- sort(list.dirs("official_nichenet_results", recursive = FALSE), decreasing = TRUE)[1]
cat("outdir:", outdir, "\n")
receivers <- sub("^receiver_", "", list.dirs(outdir, recursive = FALSE, full.names = FALSE))

cmp <- list()
for (rcv in receivers) {
  rdir <- file.path(outdir, paste0("receiver_", rcv))
  f <- file.path(rdir, "aggregate_result.rds")
  if (!file.exists(f)) next
  res <- readRDS(f)
  cat("\n==", rcv, "==  top:", paste(head(res$top_ligands, 5), collapse = ", "), "\n")

  ## 靶基因表达（按条件拆分）
  if (length(res$top_targets) >= 5) {
    tg <- head(res$top_targets, 30)
    p <- tryCatch({
      DotPlot(subset(obj, idents = rcv), features = rev(tg), split.by = "group_use") +
        coord_flip() + labs(x = NULL, y = NULL, title = paste0(rcv, ": top target genes")) +
        theme(axis.text.y = element_text(size = 6))
    }, error = function(e) NULL)
    if (!is.null(p))
      ggsave(file.path(rdir, "06_target_expression_dotplot_split.png"), p,
             width = 9, height = 8, dpi = 300, limitsize = FALSE)
  }

  ## 受体表达（按条件拆分）
  if (length(res$top_receptors) >= 3) {
    rc <- head(res$top_receptors, 20)
    p2 <- tryCatch({
      DotPlot(subset(obj, idents = rcv), features = rev(rc), split.by = "group_use") +
        coord_flip() + labs(x = NULL, y = NULL, title = paste0(rcv, ": top receptors")) +
        theme(axis.text.y = element_text(size = 6))
    }, error = function(e) NULL)
    if (!is.null(p2))
      ggsave(file.path(rdir, "07_receptor_expression_dotplot_split.png"), p2,
             width = 9, height = 7, dpi = 300, limitsize = FALSE)
  }

  ## 与之前 Pearson 结果对比
  prev_dir <- "NicheNet_results_7subtypes/20261031_1842"
  prev <- NULL
  for (tag in c("up", "down")) {
    pf <- file.path(prev_dir, paste0("receiver_", rcv), paste0("ligand_activity_", tag, ".csv"))
    if (file.exists(pf)) {
      prev <- bind_rows(prev, read.csv(pf) %>% mutate(direction = tag))
    }
  }
  if (!is.null(prev)) {
    prev_top_up <- prev %>% filter(direction == "up") %>% arrange(rank) %>%
      head(5) %>% pull(test_ligand)
    prev_top_down <- prev %>% filter(direction == "down") %>% arrange(rank) %>%
      head(5) %>% pull(test_ligand)
    off_top <- head(res$top_ligands, 5)
    cmp[[rcv]] <- data.frame(
      receiver = rcv,
      official_top5_AUPR = paste(off_top, collapse = ","),
      previous_top5_up_Pearson = paste(prev_top_up, collapse = ","),
      previous_top5_down_Pearson = paste(prev_top_down, collapse = ","),
      overlap_official_vs_up = paste(intersect(off_top, prev_top_up), collapse = ","),
      n_geneset = length(res$geneset_oi))
  }
}
cmp_tbl <- bind_rows(cmp)
write.csv(cmp_tbl, file.path(outdir, "COMPARISON_official_vs_previous.csv"), row.names = FALSE)
print(cmp_tbl)
