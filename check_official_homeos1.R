r <- readRDS("official_nichenet_results/20261101_2125/receiver_Homeos1/aggregate_result.rds")
g <- r$geneset_oi; b <- r$background_expressed_genes
cat("geneset:", length(g), " background:", length(b),
    " frac:", round(length(intersect(g, b)) / length(b), 3), "\n")
la <- r$ligand_activities
cat("aupr_corrected range:", paste(round(range(la$aupr_corrected), 4), collapse = " ~ "),
    " | pearson range:", paste(round(range(la$pearson), 4), collapse = " ~ "), "\n")
cat("top10 by AUPR:", paste(head(la$test_ligand[order(-la$aupr_corrected)], 10), collapse = ", "), "\n")
cat("top10 by Pearson:", paste(head(la$test_ligand[order(-la$pearson)], 10), collapse = ", "), "\n")
