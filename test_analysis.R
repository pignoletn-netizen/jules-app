suppressPackageStartupMessages({
  library(openxlsx)
  library(FactoMineR)
  library(factoextra)
  library(vegan)
  library(dplyr)
  library(ggplot2)
  library(readxl)
})

args <- commandArgs(trailingOnly = TRUE)
input_file <- ifelse(length(args) >= 1, args[1], "sample_inventory.xlsx")
output_dir <- ifelse(length(args) >= 2, args[2], "output")

if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

# Read Excel file
df <- read_excel(input_file)

# Standardize column names
col_names <- colnames(df)

# Helper function to find column
find_col <- function(possible_names, default_val = NULL) {
  for (p in possible_names) {
    match_idx <- grep(paste0("^", p, "$"), col_names, ignore.case = TRUE)
    if (length(match_idx) > 0) return(col_names[match_idx[1]])
  }
  return(default_val)
}

sp_col <- find_col(c("Genresp", "Espèce", "Espece", "Species", "Taxon"), "Genresp")
fam_col <- find_col(c("Famille", "Family"), "Famille")
date_col <- find_col(c("Date", "Dates"), "Date")
trap_col <- find_col(c("Capture", "Piege", "Piège", "Trap"), "Capture")
males_col <- find_col(c("Mâles", "Males", "Male", "M"), "Mâles")
fem_col <- find_col(c("Fem", "Femelles", "Females", "F"), "Fem")
juv_col <- find_col(c("Juv", "Juveniles", "Juvéniles", "J"), "Juv")
ad_col <- find_col(c("Ad", "Adultes", "Adults"), "Ad")
tot_col <- find_col(c("Tot ab", "Tot_ab", "Total", "Abondance", "Effectif"), "Tot ab")
station_col <- find_col(c("Station", "Habitat", "Site", "Lieu"), "Station")
mode_col <- find_col(c("ModeCapt", "Mode_Capture", "Mode", "Méthode"), "ModeCapt")

# Ensure required numeric columns exist
df[[males_col]] <- as.numeric(ifelse(is.na(df[[males_col]]), 0, df[[males_col]]))
df[[fem_col]] <- as.numeric(ifelse(is.na(df[[fem_col]]), 0, df[[fem_col]]))
df[[juv_col]] <- as.numeric(ifelse(is.na(df[[juv_col]]), 0, df[[juv_col]]))

if (!is.null(ad_col) && ad_col %in% col_names) {
  df[[ad_col]] <- as.numeric(ifelse(is.na(df[[ad_col]]), df[[males_col]] + df[[fem_col]], df[[ad_col]]))
} else {
  df$Ad <- df[[males_col]] + df[[fem_col]]
  ad_col <- "Ad"
}

if (!is.null(tot_col) && tot_col %in% col_names) {
  df[[tot_col]] <- as.numeric(ifelse(is.na(df[[tot_col]]), df[[ad_col]] + df[[juv_col]], df[[tot_col]]))
} else {
  df$Tot_ab <- df[[ad_col]] + df[[juv_col]]
  tot_col <- "Tot_ab"
}

# 1. Summary Table by Station / Habitat
stations <- unique(df[[station_col]])

summary_list <- list()

for (st in stations) {
  sub_df <- df[df[[station_col]] == st, ]

  # Specific richness
  richness <- length(unique(sub_df[[sp_col]][!is.na(sub_df[[sp_col]]) & sub_df[[sp_col]] != ""]))

  # Adults sum
  ad_sum <- sum(sub_df[[ad_col]], na.rm = TRUE)

  # Juv sum
  juv_sum <- sum(sub_df[[juv_col]], na.rm = TRUE)

  # Total sum
  tot_sum <- sum(sub_df[[tot_col]], na.rm = TRUE)

  # Number of traps
  n_traps <- if (!is.null(trap_col) && trap_col %in% col_names) length(unique(sub_df[[trap_col]])) else 1
  if (n_traps == 0) n_traps <- 1

  # Duration in weeks
  dates <- as.Date(sub_df[[date_col]])
  dates <- dates[!is.na(dates)]
  if (length(dates) > 1) {
    duration_days <- as.numeric(max(dates) - min(dates))
    duration_weeks <- max(1, duration_days / 7)
  } else {
    duration_weeks <- 1
  }

  # Relative Abundance
  rel_abundance <- tot_sum / (n_traps * duration_weeks)

  summary_list[[as.character(st)]] <- c(
    "Richesse spécifique (S)" = richness,
    "Effectifs adultes (Ad)" = ad_sum,
    "Effectifs juvéniles (Juv)" = juv_sum,
    "Abondance relative (ind/piège/semaine)" = round(rel_abundance, 3)
  )
}

summary_df <- as.data.frame(do.call(cbind, summary_list))
summary_df <- cbind(Métrique = rownames(summary_df), summary_df)
rownames(summary_df) <- NULL

# 2. Diversity Indices (Shannon H' & Pielou J')
# Matrix Species x Station
mat_sp_st <- df %>%
  group_by(across(all_of(c(station_col, sp_col)))) %>%
  summarise(count = sum(.data[[tot_col]], na.rm = TRUE), .groups = 'drop') %>%
  tidyr::pivot_wider(names_from = all_of(sp_col), values_from = count, values_fill = 0)

station_names <- mat_sp_st[[station_col]]
comm_matrix <- as.matrix(mat_sp_st[, -1])
rownames(comm_matrix) <- station_names

# Shannon
shannon <- vegan::diversity(comm_matrix, index = "shannon")

# Pielou J' = H' / log(S)
spec_rich <- vegan::specnumber(comm_matrix)
pielou <- ifelse(spec_rich > 1, shannon / log(spec_rich), 0)

diversity_df <- data.frame(
  Habitat_Station = station_names,
  Richesse_Specifique = spec_rich,
  Shannon_H = round(shannon, 3),
  Pielou_J = round(pielou, 3)
)

# 3. Similarity Indices (Jaccard similarity matrix)
jaccard_dist <- vegan::vegdist(comm_matrix, method = "jaccard", binary = TRUE)
jaccard_sim <- 1 - as.matrix(jaccard_dist)
jaccard_df <- as.data.frame(round(jaccard_sim, 3))
jaccard_df <- cbind(Habitat_Station = rownames(jaccard_df), jaccard_df)
rownames(jaccard_df) <- NULL

# 4. CA (AFC) & HCPC
# Species x Station contingency table
contingency_tab <- t(comm_matrix) # Rows = Species, Cols = Habitats

# Perform CA
res_ca <- FactoMineR::CA(contingency_tab, graph = FALSE)

# HCPC on Species (rows)
res_hcpc_sp <- FactoMineR::HCPC(res_ca, cluster.CA = "rows", graph = FALSE)
sp_clusters <- res_hcpc_sp$data.clust

# HCPC on Habitats (cols)
res_hcpc_hab <- FactoMineR::HCPC(res_ca, cluster.CA = "columns", graph = FALSE)
hab_clusters <- res_hcpc_hab$data.clust

# Save CA Plot
png(file.path(output_dir, "afc_biplot.png"), width = 800, height = 600)
p_ca <- factoextra::fviz_ca_biplot(res_ca, repel = TRUE, title = "Analyse Factorielle des Correspondances (AFC)")
print(p_ca)
dev.off()

# Save HCPC Species Plot
png(file.path(output_dir, "hcpc_species.png"), width = 800, height = 600)
p_hcpc_sp <- factoextra::fviz_dend(res_hcpc_sp, rect = TRUE, cex = 0.8, main = "Classification Hiérarchique sur Composantes Principales (Espèces)")
print(p_hcpc_sp)
dev.off()

# Save HCPC Habitats Plot
png(file.path(output_dir, "hcpc_habitats.png"), width = 800, height = 600)
p_hcpc_hab <- factoextra::fviz_dend(res_hcpc_hab, rect = TRUE, cex = 0.8, main = "Classification Hiérarchique sur Composantes Principales (Habitats)")
print(p_hcpc_hab)
dev.off()

# 5. Visualizations for Barber Traps
barber_df <- df[grep("barber", df[[mode_col]], ignore.case = TRUE), ]

if (nrow(barber_df) > 0) {
  fam_summary <- barber_df %>%
    group_by(across(all_of(c(fam_col, sp_col)))) %>%
    summarise(ind_count = sum(.data[[tot_col]], na.rm = TRUE), .groups = 'drop') %>%
    group_by(across(all_of(fam_col))) %>%
    summarise(
      nb_espèces = n_distinct(.data[[sp_col]]),
      nb_individus = sum(ind_count),
      .groups = 'drop'
    ) %>%
    mutate(
      pct_espèces = round(nb_espèces / sum(nb_espèces) * 100, 2),
      pct_individus = round(nb_individus / sum(nb_individus) * 100, 2)
    )

  # Plot 1: % Species by Family
  p_fam_sp <- ggplot(fam_summary, aes(x = reorder(.data[[fam_col]], pct_espèces), y = pct_espèces, fill = .data[[fam_col]])) +
    geom_col() +
    coord_flip() +
    labs(title = "Représentation des familles (% Nombre d'espèces - Pièges Barber)", x = "Famille", y = "% d'espèces") +
    theme_minimal() +
    theme(legend.position = "none")

  ggsave(file.path(output_dir, "barber_family_species_pct.png"), plot = p_fam_sp, width = 8, height = 6)

  # Plot 2: % Individuals by Family
  p_fam_ind <- ggplot(fam_summary, aes(x = reorder(.data[[fam_col]], pct_individus), y = pct_individus, fill = .data[[fam_col]])) +
    geom_col() +
    coord_flip() +
    labs(title = "Représentation des familles (% Nombre d'individus - Pièges Barber)", x = "Famille", y = "% d'individus") +
    theme_minimal() +
    theme(legend.position = "none")

  ggsave(file.path(output_dir, "barber_family_individuals_pct.png"), plot = p_fam_ind, width = 8, height = 6)
} else {
  fam_summary <- data.frame(Message = "Aucune donnée de piège Barber trouvée")
}

# Export Results to Excel workbook (compatible with Excel 2007 .xlsx)
wb <- createWorkbook()
addWorksheet(wb, "Synthèse Habitats")
writeData(wb, "Synthèse Habitats", summary_df)

addWorksheet(wb, "Indices Diversité")
writeData(wb, "Indices Diversité", diversity_df)

addWorksheet(wb, "Similarité Jaccard")
writeData(wb, "Similarité Jaccard", jaccard_df)

addWorksheet(wb, "Clusters Espèces (HCPC)")
writeData(wb, "Clusters Espèces (HCPC)", cbind(Espèce = rownames(sp_clusters), sp_clusters))

addWorksheet(wb, "Clusters Habitats (HCPC)")
writeData(wb, "Clusters Habitats (HCPC)", cbind(Habitat = rownames(hab_clusters), hab_clusters))

addWorksheet(wb, "Familles Barber")
writeData(wb, "Familles Barber", fam_summary)

saveWorkbook(wb, file.path(output_dir, "resultats_analyse.xlsx"), overwrite = TRUE)

cat("Analysis completed successfully.\n")
