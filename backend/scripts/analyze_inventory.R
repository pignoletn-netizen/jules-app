suppressPackageStartupMessages({
  library(openxlsx)
  library(FactoMineR)
  library(factoextra)
  library(vegan)
  library(dplyr)
  library(ggplot2)
  library(readxl)
  library(jsonlite)
})

args <- commandArgs(trailingOnly = TRUE)
input_file <- ifelse(length(args) >= 1, args[1], "backend/data/sample_inventory.xlsx")
output_dir <- ifelse(length(args) >= 2, args[2], "backend/output")

if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

# Read Excel file
df <- read_excel(input_file)

# Normalize column names
col_names <- colnames(df)

find_col <- function(possible_names, default_val = NULL) {
  for (p in possible_names) {
    match_idx <- grep(paste0("^", p, "$"), col_names, ignore.case = TRUE)
    if (length(match_idx) > 0) return(col_names[match_idx[1]])
  }
  # Partial match fallback
  for (p in possible_names) {
    match_idx <- grep(p, col_names, ignore.case = TRUE)
    if (length(match_idx) > 0) return(col_names[match_idx[1]])
  }
  return(default_val)
}

sp_col      <- find_col(c("Genresp", "Espèce", "Espece", "Species", "Taxon"), "Genresp")
fam_col     <- find_col(c("Famille", "Family"), "Famille")
date_col    <- find_col(c("Date", "Dates"), "Date")
trap_col    <- find_col(c("Capture", "Piege", "Piège", "Trap"), "Capture")
males_col   <- find_col(c("Mâles", "Males", "Male", "M"), "Mâles")
fem_col     <- find_col(c("Fem", "Femelles", "Females", "F"), "Fem")
juv_col     <- find_col(c("Juv", "Juveniles", "Juvéniles", "J"), "Juv")
ad_col      <- find_col(c("Ad", "Adultes", "Adults"), "Ad")
tot_col     <- find_col(c("Tot ab", "Tot_ab", "Total", "Abondance", "Effectif"), "Tot ab")
station_col <- find_col(c("Station", "Habitat", "Site", "Lieu"), "Station")
mode_col    <- find_col(c("ModeCapt", "Mode_Capture", "Mode", "Méthode"), "ModeCapt")

# Ensure numeric conversion
df[[males_col]] <- suppressWarnings(as.numeric(ifelse(is.na(df[[males_col]]), 0, df[[males_col]])))
df[[fem_col]]   <- suppressWarnings(as.numeric(ifelse(is.na(df[[fem_col]]), 0, df[[fem_col]])))
df[[juv_col]]   <- suppressWarnings(as.numeric(ifelse(is.na(df[[juv_col]]), 0, df[[juv_col]])))

if (!is.null(ad_col) && ad_col %in% col_names) {
  df[[ad_col]] <- suppressWarnings(as.numeric(ifelse(is.na(df[[ad_col]]), df[[males_col]] + df[[fem_col]], df[[ad_col]])))
} else {
  df$Ad <- df[[males_col]] + df[[fem_col]]
  ad_col <- "Ad"
}

if (!is.null(tot_col) && tot_col %in% col_names) {
  df[[tot_col]] <- suppressWarnings(as.numeric(ifelse(is.na(df[[tot_col]]), df[[ad_col]] + df[[juv_col]], df[[tot_col]])))
} else {
  df$Tot_ab <- df[[ad_col]] + df[[juv_col]]
  tot_col <- "Tot_ab"
}

# 1. Summary Table by Station / Habitat
stations <- sort(unique(df[[station_col]]))

summary_list <- list()

for (st in stations) {
  sub_df <- df[df[[station_col]] == st, ]

  # Specific richness
  richness <- length(unique(sub_df[[sp_col]][!is.na(sub_df[[sp_col]]) & sub_df[[sp_col]] != ""]))

  # Adult & Juvenile sum
  ad_sum <- sum(sub_df[[ad_col]], na.rm = TRUE)
  juv_sum <- sum(sub_df[[juv_col]], na.rm = TRUE)
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

  # Relative abundance (ind / trap / week)
  rel_abundance <- round(tot_sum / (n_traps * duration_weeks), 3)

  summary_list[[as.character(st)]] <- c(
    "Richesse spécifique (S)" = richness,
    "Effectifs adultes (Ad)" = ad_sum,
    "Effectifs juvéniles (Juv)" = juv_sum,
    "Abondance relative (ind/piège/semaine)" = rel_abundance
  )
}

summary_df <- as.data.frame(do.call(cbind, summary_list))
summary_df <- cbind(Métrique = rownames(summary_df), summary_df)
rownames(summary_df) <- NULL

# 2. Diversity Indices (Shannon H' & Pielou J')
mat_sp_st <- df %>%
  filter(!is.na(.data[[sp_col]]) & .data[[sp_col]] != "") %>%
  group_by(across(all_of(c(station_col, sp_col)))) %>%
  summarise(count = sum(.data[[tot_col]], na.rm = TRUE), .groups = 'drop') %>%
  tidyr::pivot_wider(names_from = all_of(sp_col), values_from = count, values_fill = 0)

station_names <- mat_sp_st[[station_col]]
comm_matrix <- as.matrix(mat_sp_st[, -1])
rownames(comm_matrix) <- station_names

shannon <- vegan::diversity(comm_matrix, index = "shannon")
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

# 4. CA (AFC) and HCPC
contingency_tab <- t(comm_matrix) # Rows = Species, Cols = Habitats

# Perform CA
res_ca <- FactoMineR::CA(contingency_tab, graph = FALSE)

# HCPC Species
res_hcpc_sp <- FactoMineR::HCPC(res_ca, cluster.CA = "rows", graph = FALSE)
sp_clusters <- res_hcpc_sp$data.clust
sp_coord <- as.data.frame(round(res_ca$row$coord, 3))
sp_results_df <- cbind(Espèce = rownames(sp_clusters), Cluster = sp_clusters$clust, sp_coord)

# HCPC Habitats
res_hcpc_hab <- FactoMineR::HCPC(res_ca, cluster.CA = "columns", graph = FALSE)
hab_clusters <- res_hcpc_hab$data.clust
hab_coord <- as.data.frame(round(res_ca$col$coord, 3))
hab_results_df <- cbind(Habitat = rownames(hab_clusters), Cluster = hab_clusters$clust, hab_coord)

# Export CA & HCPC Plots
png(file.path(output_dir, "afc_biplot.png"), width = 900, height = 650, res = 100)
p_ca <- factoextra::fviz_ca_biplot(res_ca, repel = TRUE, title = "Analyse Factorielle des Correspondances (AFC)") +
  theme_minimal(base_size = 12)
print(p_ca)
dev.off()

png(file.path(output_dir, "hcpc_species.png"), width = 900, height = 650, res = 100)
p_hcpc_sp <- factoextra::fviz_dend(res_hcpc_sp, rect = TRUE, cex = 0.8, main = "Dendrogramme HCPC - Espèces")
print(p_hcpc_sp)
dev.off()

png(file.path(output_dir, "hcpc_habitats.png"), width = 900, height = 650, res = 100)
p_hcpc_hab <- factoextra::fviz_dend(res_hcpc_hab, rect = TRUE, cex = 0.8, main = "Dendrogramme HCPC - Habitats")
print(p_hcpc_hab)
dev.off()

# 5. Visualizations for Barber Traps
barber_mask <- grep("barber|sol|piege", df[[mode_col]], ignore.case = TRUE)
barber_df <- if (length(barber_mask) > 0) df[barber_mask, ] else df

fam_summary <- barber_df %>%
  filter(!is.na(.data[[fam_col]]) & .data[[fam_col]] != "") %>%
  group_by(across(all_of(c(fam_col, sp_col)))) %>%
  summarise(ind_count = sum(.data[[tot_col]], na.rm = TRUE), .groups = 'drop') %>%
  group_by(across(all_of(fam_col))) %>%
  summarise(
    nb_especes = n_distinct(.data[[sp_col]]),
    nb_individus = sum(ind_count),
    .groups = 'drop'
  ) %>%
  mutate(
    pct_especes = round(nb_especes / sum(nb_especes) * 100, 2),
    pct_individus = round(nb_individus / sum(nb_individus) * 100, 2)
  )

# Plot % Species by Family
p_fam_sp <- ggplot(fam_summary, aes(x = reorder(.data[[fam_col]], pct_especes), y = pct_especes, fill = .data[[fam_col]])) +
  geom_col(show.legend = FALSE, fill = "#2563eb") +
  geom_text(aes(label = paste0(pct_especes, "%")), hjust = -0.1, size = 3.5) +
  coord_flip() +
  scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
  labs(title = "Répartition des familles (% en nombre d'espèces - Pièges Barber)", x = "Famille", y = "% d'espèces") +
  theme_minimal(base_size = 12)

ggsave(file.path(output_dir, "barber_family_species_pct.png"), plot = p_fam_sp, width = 8, height = 5, dpi = 120)

# Plot % Individuals by Family
p_fam_ind <- ggplot(fam_summary, aes(x = reorder(.data[[fam_col]], pct_individus), y = pct_individus, fill = .data[[fam_col]])) +
  geom_col(show.legend = FALSE, fill = "#059669") +
  geom_text(aes(label = paste0(pct_individus, "%")), hjust = -0.1, size = 3.5) +
  coord_flip() +
  scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
  labs(title = "Répartition des familles (% en nombre d'individus - Pièges Barber)", x = "Famille", y = "% d'individus") +
  theme_minimal(base_size = 12)

ggsave(file.path(output_dir, "barber_family_individuals_pct.png"), plot = p_fam_ind, width = 8, height = 5, dpi = 120)

# Export Workbook Excel (.xlsx) compatible Excel 2007
wb <- createWorkbook()

addWorksheet(wb, "Synthèse Habitats")
writeData(wb, "Synthèse Habitats", summary_df)

addWorksheet(wb, "Indices Diversité")
writeData(wb, "Indices Diversité", diversity_df)

addWorksheet(wb, "Similarité Jaccard")
writeData(wb, "Similarité Jaccard", jaccard_df)

addWorksheet(wb, "Clusters Espèces (HCPC)")
writeData(wb, "Clusters Espèces (HCPC)", sp_results_df)

addWorksheet(wb, "Clusters Habitats (HCPC)")
writeData(wb, "Clusters Habitats (HCPC)", hab_results_df)

addWorksheet(wb, "Familles Barber")
writeData(wb, "Familles Barber", fam_summary)

excel_output_path <- file.path(output_dir, "resultats_analyse.xlsx")
saveWorkbook(wb, excel_output_path, overwrite = TRUE)

# Export JSON summary for FastAPI API response
json_out <- list(
  summary_table = summary_df,
  diversity_table = diversity_df,
  jaccard_matrix = jaccard_df,
  species_clusters = sp_results_df,
  habitat_clusters = hab_results_df,
  barber_family_summary = fam_summary,
  excel_file = "resultats_analyse.xlsx",
  plots = list(
    afc_biplot = "afc_biplot.png",
    hcpc_species = "hcpc_species.png",
    hcpc_habitats = "hcpc_habitats.png",
    barber_species_pct = "barber_family_species_pct.png",
    barber_individuals_pct = "barber_family_individuals_pct.png"
  )
)

write(toJSON(json_out, auto_unbox = TRUE, pretty = TRUE), file.path(output_dir, "analysis_results.json"))
cat("Analysis executed and output written successfully.\n")
