package com.trailcoach.app.domain.model

/**
 * Type de cycle d'entraînement en périodisation trail.
 */
enum class CycleType {
    DEVELOPPEMENT_GENERAL,
    SPECIFIQUE_TRAIL,
    AFFUTAGE,
    RECUPERATION
}

/**
 * Cycle d'entraînement (ex: mésocycle de 3 à 4 semaines).
 *
 * @property name Nom du cycle (ex: "Cycle 1 - Développement Foncier & Excentrique").
 * @property type Type de cycle d'entraînement.
 * @property startTimestamp Date de début du cycle (Epoch millis).
 * @property endTimestamp Date de fin du cycle (Epoch millis).
 * @property targetTrimp Target TRIMP for the cycle.
 * @property sessions Liste des séances planifiées dans ce cycle.
 */
data class TrainingCycle(
    val id: String,
    val name: String,
    val type: CycleType,
    val startTimestamp: Long,
    val endTimestamp: Long,
    val targetTrimp: Double,
    val sessions: List<WorkoutSession> = emptyList()
)

/**
 * Répartition de la charge globale et des composantes PPG / Mobilité / D+ / D-.
 *
 * @property totalDPlusMeters Volume global de dénivelé positif cible (mètres).
 * @property totalDMinusMeters Volume global de dénivelé négatif cible (mètres).
 * @property ppgRatioPourcent Pourcentage du temps ou volume alloué à la PPG (renforcement excentrique).
 * @property mobilityRatioPourcent Pourcentage du temps alloué à la mobilité/souplesse.
 */
data class VolumeDistribution(
    val totalDPlusMeters: Int = 0,
    val totalDMinusMeters: Int = 0,
    val ppgRatioPourcent: Double = 0.0,
    val mobilityRatioPourcent: Double = 0.0
)

/**
 * Plan d'entraînement global personnalisé (TrainingPlan).
 *
 * @property id Identifiant du plan d'entraînement.
 * @property userId Identifiant de l'utilisateur concerné.
 * @property goalId Identifiant de l'objectif principal lié (Goal A).
 * @property cycles Liste des découpages en cycles (mésocycles / microcycles).
 * @property trimpLoad Charge de travail calculée en TRIMP (Training Impulse).
 * @property tssLoad Charge de travail calculée en TSS (Training Stress Score).
 * @property volumeDistribution Répartition du D+/D- et de la PPG / Mobilité.
 */
data class TrainingPlan(
    val id: String,
    val userId: String,
    val goalId: String,
    val cycles: List<TrainingCycle> = emptyList(),
    val trimpLoad: Double = 0.0,
    val tssLoad: Double = 0.0,
    val volumeDistribution: VolumeDistribution = VolumeDistribution()
)
