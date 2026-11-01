## 构建“精简对象”：只保留在任一亚型中检出率 >= 10% 的基因
## 目的：官方 nichenet_seuratobj_aggregate() 的 receiver DE 会用全部基因跑 Wilcoxon，
##       在 6 万基因 x 1 万多细胞上非常慢；未表达基因本来也进不了 DE/背景，删掉不改变结论。
suppressPackageStartupMessages({ library(Seurat); library(SeuratObject) })
setwd("C:/Users/lenovo/Desktop/nichenet_data")
t0 <- Sys.time()

e <- new.env(); load("scRNA.RData", envir = e); obj <- e$scRNA; rm(e); gc()
obj <- DietSeurat(obj, assays = "RNA", dimreducs = NULL, graphs = NULL)
obj$cell_type_use <- obj@meta.data[["cell_type"]]
obj$group_use     <- obj@meta.data[["Group"]]
keep <- c("Homeos1","Homeos2","Homeos3","Inflam.DAM","Lipo.DAM","Ribo.DAM1","Ribo.DAM2")
obj <- subset(obj, cells = rownames(obj@meta.data)[obj$cell_type_use %in% keep])
Idents(obj) <- "cell_type_use"
cat("cells:", ncol(obj), "\n")

x <- GetAssayData(obj, assay = "RNA", layer = "data")
genes_keep <- unique(unlist(lapply(keep, function(ct) {
  cells <- rownames(obj@meta.data)[obj$cell_type_use == ct]
  frac <- Matrix::rowSums(x[, cells, drop = FALSE] > 0) / length(cells)
  names(frac)[frac >= 0.10]
})))
cat("expressed genes (union, >=10%):", length(genes_keep), "\n")

obj_slim <- subset(obj, features = genes_keep)
cat("slim object:", paste(dim(obj_slim), collapse = " x "), "\n")
saveRDS(obj_slim, "official_data_slim.rds")
cat("saved, size MB:", round(file.size("official_data_slim.rds") / 1024^2, 1),
    " elapsed min:", round(difftime(Sys.time(), t0, units = "mins"), 1), "\n")
