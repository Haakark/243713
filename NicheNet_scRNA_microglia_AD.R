###############################################################################
# NicheNet 分析：小胶质细胞亚群间通讯  ——  AD vs 对照
# 数据：scRNA.RData  (scRNA 对象: 61,388 genes × 48,347 cells)
#       小胶质细胞 9 个亚群：Homeos1/2/3, Inflam.DAM, Lipo.DAM,
#                            Ribo.DAM1/2, DIMs, MAC
#       分组：Group = "AD"  vs  "No Neuropathology"
#
# 分析设计（可在下面 cfg 里随意改）：
#   receiver（接收细胞）= 稳态小胶质细胞 Homeos1/2/3
#   sender （发送细胞）= 各 DAM / MAC 亚群
#   差异基因：在 receiver 内部做 AD vs 对照，取上调/下调 top 200 基因
#   核心问题：哪些由 DAM 等亚群分泌的配体，能解释稳态小胶质细胞在 AD 中的
#             转录变化（NicheNet 配体活性 → 靶基因 → 配体-受体）
#
# 参考：NicheNet 官方 vignette (Bonaventura et al., 2024, nichenetr 2.x)
# 运行：Rscript NicheNet_scRNA_microglia_AD.R
###############################################################################

## ========================= 0. 全局参数 =========================
cfg <- list(
  rdata_file      = "scRNA.RData",          # 数据文件
  object_name     = "scRNA",                # RData 里的对象名（NULL = 自动找 Seurat 对象）
  assay           = "RNA",                  # 用 RNA assay（counts/data），不要用 SCT/integrated
  celltype_col    = "cell_type",            # 亚群列
  group_col       = "Group",                # 分组列
  case_group      = "AD",                   # 病例组
  ref_group       = "No Neuropathology",    # 对照组

  receiver_celltypes = c("Homeos1", "Homeos2", "Homeos3"),
  sender_celltypes   = c("Inflam.DAM", "Lipo.DAM", "Ribo.DAM1",
                         "Ribo.DAM2", "DIMs", "MAC"),

  n_top_genes     = 200,     # 上/下调各取多少个 DE 基因（NicheNet 建议 100–500）
  padj_cutoff     = 0.05,
  lfc_cutoff      = 0.25,
  min_pct         = 0.10,    # 表达基因的检出率阈值
  rank_de_by      = "logfc", # DE 基因排序："logfc"（|logFC|）或 "pval"（显著性）
  exclude_regex   = "^MT-",  # 从基因集中剔除的基因（正则），"" 表示不剔除
  n_top_ligands   = 30,      # 优先展示的配体数
  lt_n            = 250,     # 每个配体取 top n 靶基因算权重
  lt_cutoff       = 0.25,    # 配体-靶基因热图的 regulatory potential 过滤分位数
  # TRUE = 每组只抽 2000 细胞，快速跑通流程（命令行可用 NICHENET_QUICK=1 开启）
  quick_test      = identical(Sys.getenv("NICHENET_QUICK"), "1"),
  force_recompute_de = FALSE,  # TRUE = 忽略 DE 缓存重新做差异分析
  outdir          = file.path("NicheNet_results", format(Sys.time(), "%Y%m%d_%H%M"))
)

## ---------- 自动定位数据目录 ----------
## 报错 “无法打开压缩文件 lr_network_human_21122021.rds … No such file or directory”
## 几乎都是因为 R 的工作目录不是数据文件夹。这里自动把工作目录切到脚本所在目录：
##   - Rscript 运行：用 --file= 参数
##   - RStudio 里 source()：用 rstudioapi 取当前编辑脚本的路径
##   - 也可以用环境变量 NICHENET_DATA_DIR 或这里手动指定 data_dir 覆盖
find_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  f <- grep("^--file=", args, value = TRUE)
  if (length(f) > 0) {
    return(dirname(normalizePath(sub("^--file=", "", f[1]), mustWork = FALSE)))
  }
  if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
    p <- tryCatch(rstudioapi::getSourceEditorContext()$path, error = function(e) "")
    if (!is.null(p) && nzchar(p)) return(dirname(normalizePath(p, mustWork = FALSE)))
  }
  getwd()
}

data_dir <- Sys.getenv("NICHENET_DATA_DIR", unset = find_script_dir())
if (!dir.exists(data_dir)) {
  stop("数据目录不存在：", data_dir,
       "\n请把 data_dir 改成 scRNA.RData 所在文件夹，或在 R 里先 setwd('C:/Users/lenovo/Desktop/nichenet_data')")
}
setwd(data_dir)
cat("工作目录：", getwd(), "\n")

## 必需文件检查（缺文件时给出明确提示，而不是 readRDS 报 gzfile 错）
required_files <- c(cfg$rdata_file,
                    "lr_network_human_21122021.rds",
                    "ligand_target_matrix_nsga2r_final.rds",
                    "weighted_networks_nsga2r_final.rds")
missing_files <- required_files[!file.exists(required_files)]
if (length(missing_files) > 0) {
  stop("以下文件不在工作目录 ", getwd(), " 中：\n  ",
       paste(missing_files, collapse = "\n  "),
       "\n请确认 data_dir / setwd() 指向 nichenet_data 文件夹。")
}

dir.create(cfg$outdir, recursive = TRUE, showWarnings = FALSE)

## ========================= 1. 加载包 =========================
suppressPackageStartupMessages({
  library(Seurat)
  library(SeuratObject)
  library(nichenetr)
  library(dplyr)
  library(tidyr)
  library(tibble)
  library(ggplot2)
  library(pheatmap)
})
set.seed(123)
options(future.globals.maxSize = 8 * 1024^3)
future::plan("sequential")   # 避免 FindMarkers 多进程吃爆内存

log_file <- file.path(cfg$outdir, "run_log.txt")
sink(log_file, split = TRUE)
cat("==== NicheNet 分析开始：", format(Sys.time()), "====\n\n")

## ========================= 2. NicheNet 先验网络 =========================
lr_network           <- readRDS("lr_network_human_21122021.rds")
ligand_target_matrix <- readRDS("ligand_target_matrix_nsga2r_final.rds")
weighted_networks    <- readRDS("weighted_networks_nsga2r_final.rds")

cat("lr_network:", nrow(lr_network), "条配体-受体对\n")
cat("ligand_target_matrix:", nrow(ligand_target_matrix), "genes ×",
    ncol(ligand_target_matrix), "ligands\n\n")

## ========================= 3. 读取单细胞数据 =========================
if (is.null(cfg$object_name)) {
  e <- new.env(); objs <- load(cfg$rdata_file, envir = e)
  hit <- objs[sapply(objs, function(o) inherits(get(o, envir = e), "Seurat"))]
  if (length(hit) == 0) stop("RData 中没有 Seurat 对象")
  obj <- get(hit[1], envir = e)
  cat("自动读取到 Seurat 对象：", hit[1], "\n")
} else {
  e <- new.env(); load(cfg$rdata_file, envir = e)
  obj <- get(cfg$object_name, envir = e)
}
rm(e); gc()

cat("原始对象：", paste(dim(obj), collapse = " x "), "\n")
cat("Assays:", paste(Assays(obj), collapse = ", "), "\n")

## 只保留 RNA assay，丢掉 SCT / integrated，节省大量内存
obj <- DietSeurat(obj, assays = cfg$assay, dimreducs = NULL, graphs = NULL)
DefaultAssay(obj) <- cfg$assay
gc()
cat("精简后对象：", paste(dim(obj), collapse = " x "),
    " | layers:", paste(Layers(obj[[cfg$assay]]), collapse = ", "), "\n\n")

## 若没有归一化 data 层，补一个
if (!"data" %in% Layers(obj[[cfg$assay]])) {
  obj <- NormalizeData(obj, verbose = FALSE)
  cat("已补做 NormalizeData\n")
}

## 统一列名 & 设 Idents
stopifnot(cfg$celltype_col %in% colnames(obj@meta.data))
stopifnot(cfg$group_col    %in% colnames(obj@meta.data))
obj$cell_type_use <- obj@meta.data[[cfg$celltype_col]]
obj$group_use     <- obj@meta.data[[cfg$group_col]]
Idents(obj) <- "cell_type_use"

missing_ct <- setdiff(c(cfg$receiver_celltypes, cfg$sender_celltypes),
                      unique(obj$cell_type_use))
if (length(missing_ct) > 0) stop("对象中不存在的细胞类型: ", paste(missing_ct, collapse = ", "))
cat("receiver:", paste(cfg$receiver_celltypes, collapse = ", "), "\n")
cat("sender  :", paste(cfg$sender_celltypes,   collapse = ", "), "\n")
print(table(obj$cell_type_use, obj$group_use))

## 快速测试模式：每组下采样，仅用于验证代码能跑通
if (isTRUE(cfg$quick_test)) {
  cells_keep <- unlist(lapply(split(rownames(obj@meta.data), obj$group_use), function(cs)
    sample(cs, min(2000, length(cs)))))
  obj <- subset(obj, cells = cells_keep)
  cat("\n[quick_test] 下采样后细胞数：", ncol(obj), "\n")
}

## ========================= 4. 工具函数 =========================
## 4.1 稀疏矩阵快速计算每类细胞的“表达比例”（返回命名向量）
expressed_fraction <- function(object, celltypes, assay = "RNA", col = "cell_type_use") {
  md    <- object@meta.data
  cells <- rownames(md)[md[[col]] %in% celltypes]
  if (length(cells) == 0) return(setNames(numeric(0), character(0)))
  x <- GetAssayData(object, assay = assay, layer = "data")[, cells, drop = FALSE]
  frac <- Matrix::rowSums(x > 0) / length(cells)
  setNames(as.numeric(frac), rownames(x))
}

## 4.2 每个亚群分别算表达比例，再取并集（NicheNet 官方做法：
##     亚群特异基因不应因“在全 sender 中比例低”而被丢掉）
genes_from_fracs <- function(fracs, pct = 0.1) {
  unique(unlist(lapply(fracs, function(f) names(f)[f >= pct])))
}

## 4.3 多个细胞类型的表达比例取最大值（用于汇总表）
max_expression_fraction <- function(fracs) {
  fracs <- fracs[vapply(fracs, length, integer(1)) > 0]
  if (length(fracs) == 0) return(numeric(0))
  genes <- unique(unlist(lapply(fracs, names)))
  m <- sapply(fracs, function(f) f[genes])
  m[is.na(m)] <- 0
  setNames(apply(m, 1, max), genes)
}

## 4.4 按方向挑 top N 差异基因
##     过滤：padj、两组都表达（pct.1/pct.2 ≥ min_pct）、剔除线粒体基因，
##     再按 |logFC|（或 p 值）排序 —— 避免低表达 lncRNA 因 |logFC| 巨大而霸榜
pick_de_genes <- function(de, direction = c("up", "down"),
                          n = 200, padj = 0.05, lfc = 0.25, min_pct = 0.1) {
  direction <- match.arg(direction)
  d <- de[!is.na(de$p_val_adj) & de$p_val_adj < padj, , drop = FALSE]
  d <- d[d$pct.1 >= min_pct & d$pct.2 >= min_pct, , drop = FALSE]
  if (nzchar(cfg$exclude_regex)) {
    d <- d[!grepl(cfg$exclude_regex, rownames(d)), , drop = FALSE]
  }
  d <- if (direction == "up") d[d$avg_log2FC >=  lfc, , drop = FALSE]
       else                   d[d$avg_log2FC <= -lfc, , drop = FALSE]
  ord <- if (identical(cfg$rank_de_by, "pval")) order(d$p_val_adj)
         else order(-abs(d$avg_log2FC))
  head(rownames(d)[ord], n)
}

## 4.5 配体活性条形图
plot_ligand_bar <- function(lig_act, top_ligands, title_txt, fill_hi = "#E65100") {
  df <- lig_act %>%
    filter(test_ligand %in% top_ligands) %>%
    arrange(pearson) %>%
    mutate(test_ligand = factor(test_ligand, levels = test_ligand))
  ggplot(df, aes(x = pearson, y = test_ligand, fill = pearson)) +
    geom_col(width = 0.75) +
    scale_fill_gradient(low = "#FFE0B2", high = fill_hi, name = "Pearson\ncorrelation") +
    labs(x = "Ligand activity (Pearson correlation)", y = NULL, title = title_txt) +
    theme_bw(base_size = 11) +
    theme(panel.grid.minor = element_blank(),
          plot.title = element_text(hjust = 0.5, face = "bold"))
}

## 4.6 配体活性直方图
plot_ligand_hist <- function(lig_act, title_txt) {
  thr <- quantile(lig_act$pearson, 0.85, na.rm = TRUE)
  ggplot(lig_act, aes(x = pearson)) +
    geom_histogram(bins = 30, fill = "darkorange", colour = "black", linewidth = 0.2) +
    geom_vline(xintercept = thr, colour = "red", linetype = "dashed", linewidth = 0.6) +
    labs(x = "Ligand activity (Pearson correlation)", y = "# ligands",
         title = title_txt,
         subtitle = paste0("dashed line = 85th percentile (", round(thr, 3), ")")) +
    theme_classic(base_size = 11)
}

## ========================= 5. 表达基因 / 背景基因 / 候选配体 =========================
cat("\n---- 计算各类细胞表达基因 ----\n")
sender_frac_list   <- lapply(cfg$sender_celltypes,   function(ct) expressed_fraction(obj, ct))
receiver_frac_list <- lapply(cfg$receiver_celltypes, function(ct) expressed_fraction(obj, ct))
sender_expr   <- genes_from_fracs(sender_frac_list,   cfg$min_pct)
receiver_expr <- genes_from_fracs(receiver_frac_list, cfg$min_pct)
sender_max_frac <- max_expression_fraction(sender_frac_list)
cat("sender 表达基因:", length(sender_expr),
    "| receiver 表达基因:", length(receiver_expr), "\n")

background_expressed_genes <- intersect(receiver_expr, rownames(ligand_target_matrix))

potential_ligands <- lr_network %>%
  pull(from) %>% unique() %>%
  intersect(sender_expr) %>%
  intersect(colnames(ligand_target_matrix))
cat("候选配体（sender 表达 且 在先验网络中）:", length(potential_ligands), "\n")

## ========================= 6. receiver 内 AD vs 对照差异分析 =========================
cat("\n---- receiver 内差异分析：", cfg$case_group, " vs ", cfg$ref_group, " ----\n")
recv_cells <- rownames(obj@meta.data)[obj$cell_type_use %in% cfg$receiver_celltypes]
recv_obj   <- subset(obj, cells = recv_cells)
Idents(recv_obj) <- recv_obj$group_use
print(table(Idents(recv_obj)))

## 差异分析结果缓存：DE 很慢，改下游参数重跑时可直接复用（换 receiver 请先删缓存）
dir.create("NicheNet_cache", showWarnings = FALSE)
de_cache <- file.path("NicheNet_cache", sprintf("DE_%s_vs_%s_receiver%d.rds",
                                                gsub("\\s+", "", cfg$case_group),
                                                gsub("\\s+", "", cfg$ref_group),
                                                length(recv_cells)))
if (file.exists(de_cache) && !isTRUE(cfg$force_recompute_de)) {
  de <- readRDS(de_cache)
  cat("已读取差异分析缓存：", de_cache, "\n")
} else {
  de <- FindMarkers(recv_obj,
                    features  = receiver_expr,
                    ident.1    = cfg$case_group, ident.2 = cfg$ref_group,
                    min.pct    = cfg$min_pct, logfc.threshold = 0,
                    test.use   = "wilcox", verbose = FALSE)
  saveRDS(de, de_cache)
}
de$gene <- rownames(de)
write.csv(de, file.path(cfg$outdir, "DE_receiver_AD_vs_Control.csv"), row.names = FALSE)
cat("显著差异基因 (padj<", cfg$padj_cutoff, "):",
    sum(de$p_val_adj < cfg$padj_cutoff), "\n")

genes_up   <- pick_de_genes(de, "up",   cfg$n_top_genes, cfg$padj_cutoff,
                             cfg$lfc_cutoff, cfg$min_pct)
genes_down <- pick_de_genes(de, "down", cfg$n_top_genes, cfg$padj_cutoff,
                            cfg$lfc_cutoff, cfg$min_pct)
cat("用于 NicheNet 的上调基因:", length(genes_up),
    "| 下调基因:", length(genes_down), "\n")
writeLines(genes_up,   file.path(cfg$outdir, "geneset_up.txt"))
writeLines(genes_down, file.path(cfg$outdir, "geneset_down.txt"))

## ========================= 7. 配体活性预测 + 下游图 =========================
run_one_direction <- function(geneset, tag) {
  cat("\n==== NicheNet:", tag, "====\n")
  if (length(geneset) < 20) {
    cat("基因数太少，跳过\n"); return(invisible(NULL))
  }

  ## 7.1 配体活性
  lig_act <- predict_ligand_activities(
    geneset                  = geneset,
    background_expressed_genes = background_expressed_genes,
    ligand_target_matrix     = ligand_target_matrix,
    potential_ligands        = potential_ligands)
  lig_act <- lig_act %>%
    arrange(desc(pearson)) %>%
    mutate(rank = row_number()) %>%
    relocate(rank)
  write.csv(lig_act, file.path(cfg$outdir, paste0("ligand_activity_", tag, ".csv")),
            row.names = FALSE)

  top_ligands <- head(lig_act$test_ligand, cfg$n_top_ligands)
  cat("Top 10 配体:", paste(head(top_ligands, 10), collapse = ", "), "\n")

  ## 7.2 直方图 + 条形图
  p_hist <- plot_ligand_hist(lig_act, paste0("Ligand activity distribution (", tag, ")"))
  ggsave(file.path(cfg$outdir, paste0("01_ligand_activity_hist_", tag, ".png")),
         p_hist, width = 6, height = 4, dpi = 300)

  p_bar <- plot_ligand_bar(lig_act, top_ligands, paste0("Prioritized ligands (", tag, ")"))
  ggsave(file.path(cfg$outdir, paste0("02_ligand_activity_bar_", tag, ".png")),
         p_bar, width = 6.5, height = 8, dpi = 300)

  ## 7.3 配体-靶基因调控潜力热图
  lig_tar_df <- lapply(top_ligands, function(l)
    get_weighted_ligand_target_links(ligand = l, geneset = geneset,
                                     ligand_target_matrix = ligand_target_matrix,
                                     n = cfg$lt_n)) %>%
    bind_rows() %>%
    filter(!is.na(target)) %>%
    distinct()
  write.csv(lig_tar_df, file.path(cfg$outdir, paste0("ligand_target_links_", tag, ".csv")),
            row.names = FALSE)

  targets_keep <- character(0)
  if (nrow(lig_tar_df) > 0) {
    vis_lt <- prepare_ligand_target_visualization(
      ligand_target_df = lig_tar_df,
      ligand_target_matrix = ligand_target_matrix,
      cutoff = cfg$lt_cutoff)
    targets_keep <- rownames(vis_lt)
    ## vis_lt: 行 = 靶基因, 列 = 配体 → 转置成 配体 × 靶基因 便于阅读
    if (is.matrix(vis_lt) && nrow(vis_lt) >= 2 && ncol(vis_lt) >= 2) {
      vis_lt_t <- t(vis_lt)
      p_lt <- make_heatmap_ggplot(as.matrix(vis_lt_t),
                                  y_name = "Prioritized ligands",
                                  x_name = "Predicted target genes",
                                  color = "purple",
                                  legend_title = "Regulatory potential",
                                  x_axis_position = "bottom") +
        theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.5, size = 7),
              axis.text.y = element_text(size = 8),
              plot.title = element_text(hjust = 0.5, face = "bold")) +
        ggtitle(paste0("Ligand → target regulatory potential (", tag, ")"))
      ggsave(file.path(cfg$outdir, paste0("03_ligand_target_heatmap_", tag, ".png")),
             p_lt, width = max(8, ncol(vis_lt_t) * 0.22), height = max(6, nrow(vis_lt_t) * 0.3),
             dpi = 300, limitsize = FALSE)
    }
  }

  ## 7.4 配体-受体网络（仅保留 receiver 表达的受体）
  lr_top <- lr_network %>%
    filter(from %in% top_ligands, to %in% receiver_expr) %>%
    distinct(from, to) %>%
    mutate(weight = 1)
  write.csv(lr_top, file.path(cfg$outdir, paste0("ligand_receptor_pairs_", tag, ".csv")),
            row.names = FALSE)

  if (nrow(lr_top) > 0) {
    lr_mat <- prepare_ligand_receptor_visualization(
      lr_network_top_df_long = as.data.frame(lr_top),
      best_upstream_ligands   = top_ligands,
      order_hclust = "none")
    p_lr <- make_heatmap_ggplot(as.matrix(lr_mat),
                                y_name = "Receptors (receiver)",
                                x_name = "Prioritized ligands",
                                color = "darkgreen",
                                legend_title = "Ligand–receptor\npair",
                                x_axis_position = "bottom") +
      theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0.5, size = 7),
            axis.text.y = element_text(size = 8),
            plot.title = element_text(hjust = 0.5, face = "bold")) +
      ggtitle(paste0("Prioritized ligand–receptor pairs (", tag, ")"))
    ggsave(file.path(cfg$outdir, paste0("04_ligand_receptor_heatmap_", tag, ".png")),
           p_lr, width = max(7, ncol(lr_mat) * 0.3), height = max(5, nrow(lr_mat) * 0.28),
           dpi = 300, limitsize = FALSE)
  }

  ## 7.5 配体在各细胞类型中的表达（确认 sender 特异性）
  lig_show <- head(top_ligands, 20)
  p_dot <- DotPlot(obj, features = lig_show, group.by = "cell_type_use",
                   assay = cfg$assay) +
    RotatedAxis() +
    labs(x = NULL, y = NULL, title = paste0("Prioritized ligands expression (", tag, ")")) +
    theme(plot.title = element_text(hjust = 0.5, face = "bold"),
          axis.text.x = element_text(size = 8))
  ggsave(file.path(cfg$outdir, paste0("05_ligand_expression_dotplot_", tag, ".png")),
         p_dot, width = 9, height = 4.5, dpi = 300)

  ## 7.6 靶基因在 receiver 中 AD vs 对照的平均表达热图
  top_targets <- lig_tar_df %>%
    count(target, sort = TRUE) %>% head(40) %>% pull(target)
  top_targets <- intersect(top_targets, targets_keep)  # 仅保留进入热图的
  if (length(top_targets) >= 2) {
    avg <- AverageExpression(recv_obj, assays = cfg$assay, group.by = "group_use",
                             layer = "data")[[cfg$assay]]
    avg <- avg[, intersect(c(cfg$case_group, cfg$ref_group), colnames(avg)), drop = FALSE]
    avg <- avg[top_targets, , drop = FALSE]
    z <- t(scale(t(as.matrix(avg))))
    z[is.na(z)] <- 0
    pheatmap(z,
             cluster_cols = FALSE, cluster_rows = TRUE,
             color = colorRampPalette(c("#2166AC", "white", "#B2182B"))(100),
             border_color = NA,
             fontsize_row = 7, fontsize_col = 10,
             main = paste0("Top target genes in receiver (", tag, ")"),
             filename = file.path(cfg$outdir, paste0("06_target_expr_heatmap_", tag, ".png")),
             width = 5, height = 8)
  }

  ## 7.7 汇总表：配体 + 活性 + 表达比例 + 受体
  summary_tbl <- lig_act %>%
    filter(test_ligand %in% head(top_ligands, 20)) %>%
    mutate(max_sender_expr_pct = round(sender_max_frac[test_ligand] * 100, 1),
           receptors = sapply(test_ligand, function(l)
             paste(lr_top$to[lr_top$from == l], collapse = "/")))
  write.csv(summary_tbl, file.path(cfg$outdir, paste0("summary_top_ligands_", tag, ".csv")),
            row.names = FALSE)
  invisible(list(lig_act = lig_act, top_ligands = top_ligands, lr = lr_top))
}

res_up   <- run_one_direction(genes_up,   "up")
res_down <- run_one_direction(genes_down, "down")

## ========================= 8. 会话信息 & 结束 =========================
writeLines(capture.output(sessionInfo()),
           file.path(cfg$outdir, "sessionInfo.txt"))
cat("\n==== 全部分析完成，结果保存在：", normalizePath(cfg$outdir), "====\n")
sink()
