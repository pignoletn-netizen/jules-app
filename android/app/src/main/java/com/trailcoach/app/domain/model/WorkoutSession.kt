package com.trailcoach.app.domain.model

/**
 * Types de séances d'entraînement selon la méthodologie Trail & Ultra-Trail.
 */
enum class WorkoutType {
    VMA_COURTE,
    VMA_COTE,
    ENDURANCE_FONDAMENTALE,
    RANDO_COURSE,
    RENFORCEMENT_EXCENTRIQUE,
    MOBILITE_SOUPLESSE,
    TRAVAIL_DESCENTE,
    REPOS
}

/**
 * Cibles de la séance prescrite par le coach.
 *
 * @property targetFcMin Fréquence cardiaque minimale cible (bpm).
 * @property targetFcMax Fréquence cardiaque maximale cible (bpm).
 * @property targetFcPercentMax Pourcentage de FCmax cible (ex: 70..80).
 * @property targetPaceMinPerKm Allure cible estimée (min/km).
 * @property targetDPlus Dénivelé positif cible en mètres.
 * @property durationMinutes Durée cible de la séance en minutes.
 */
data class WorkoutTargets(
    val targetFcMin: Int? = null,
    val targetFcMax: Int? = null,
    val targetFcPercentMax: IntRange? = null,
    val targetPaceMinPerKm: String? = null,
    val targetDPlus: Int? = null,
    val durationMinutes: Int = 0
)

/**
 * Séance d'entraînement planifiée (WorkoutSession).
 *
 * @property id Identifiant unique de la séance.
 * @property type Type de séance (ex: RANDO_COURSE, RENFORCEMENT_EXCENTRIQUE, etc.).
 * @property title Titre évocateur de la séance (ex: "Rando-Course en Bloc WE").
 * @property description Detailed description of the workout structure (warmup, main sets, cooldown).
 * @property coachNotes Consignes spécifiques du coach (ex: "Focus travail excentrique quadris, pente 15%").
 * @property targets Cibles de la séance (FC, Allure, D+, Durée).
 * @property isCompleted Statut de réalisation de la séance.
 */
data class WorkoutSession(
    val id: String,
    val type: WorkoutType,
    val title: String,
    val description: String,
    val coachNotes: String,
    val targets: WorkoutTargets = WorkoutTargets(),
    val isCompleted: Boolean = false
)
