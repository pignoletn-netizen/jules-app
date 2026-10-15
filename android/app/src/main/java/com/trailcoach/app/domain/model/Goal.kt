package com.trailcoach.app.domain.model

/**
 * Priorité d'un objectif de course (méthodologie classique trail).
 * A : Objectif principal de la saison (ex: UTMB, Diagonale des Fous)
 * B : Course de préparation avec affûtage partiel
 * C : Course d'entraînement grand grandeur nature / Test
 */
enum class GoalPriority {
    A,
    B,
    C
}

/**
 * Profil topographique de la course.
 */
enum class RaceProfile {
    ROULANT,
    TECHNIQUE,
    TRES_TECHNIQUE_ALPIN,
    MUD_AND_FOREST,
    GRAND_DENIVELE
}

/**
 * Objectif de course (Goal) pour la planification d'entraînement.
 *
 * @property id Identifiant unique de l'objectif.
 * @property raceName Nom de la course (ex: "Diagonale des Fous", "UTMB", "Trail des Luys").
 * @property raceDate Timestamp en millisecondes ou date ISO (ex: Epoch millis) de la course.
 * @property distanceKm Distance totale en kilomètres.
 * @property elevationGainDPlus Dénivelé positif cumulé D+ en mètres.
 * @property elevationLossDMinus Dénivelé négatif cumulé D- en mètres.
 * @property raceProfile Profil topographique et technique du parcours.
 * @property priority Priorité de la course (A, B ou C).
 * @property targetTimeMinutes Temps cible estimé en minutes (optionnel).
 */
data class Goal(
    val id: String,
    val raceName: String,
    val raceDate: Long,
    val distanceKm: Double,
    val elevationGainDPlus: Int,
    val elevationLossDMinus: Int = elevationGainDPlus,
    val raceProfile: RaceProfile = RaceProfile.TECHNIQUE,
    val priority: GoalPriority = GoalPriority.A,
    val targetTimeMinutes: Int? = null
)
