package com.trailcoach.app.domain.model

/**
 * Activité enregistrée / réalisée par l'athlète (ex: issue des métriques Garmin/Health Connect).
 *
 * @property id Identifiant unique de l'activité.
 * @property timestamp Date/heure d'exécution en millisecondes (Epoch millis).
 * @property type Type d'activité (ex: "RUNNING", "TRAIL_RUNNING", "HIIT", "STRENGTH", "WALKING").
 * @property avgHeartRate Fréquence cardiaque moyenne durant la séance (bpm).
 * @property maxHeartRate Fréquence cardiaque maximale durant la séance (bpm).
 * @property elevationGainDPlus Dénivelé positif réalisé D+ (mètres).
 * @property elevationLossDMinus Dénivelé négatif réalisé D- (mètres).
 * @property distanceKm Distance parcourue en kilomètres.
 * @property durationMinutes Durée effective de l'activité en minutes.
 * @property paceMinPerKm Allure moyenne brute (min/km ou min/100m).
 * @property gapPaceMinPerKm Grade Adjusted Pace - Allure ajustée selon la pente (min/km).
 * @property rpe Rating of Perceived Exertion (RPE échelle de Foster de 1 à 10).
 * @property mobilityFeedback Feedback de la séance sur la mobilité / souplesse ressentie.
 * @property sorenessFeedback Feedback sur les courbatures (notamment quadriceps / travail excentrique).
 */
data class Activity(
    val id: String,
    val timestamp: Long,
    val type: String,
    val avgHeartRate: Int,
    val maxHeartRate: Int,
    val elevationGainDPlus: Int,
    val elevationLossDMinus: Int,
    val distanceKm: Double,
    val durationMinutes: Double,
    val paceMinPerKm: String,
    val gapPaceMinPerKm: String? = null,
    val rpe: Int? = null,
    val mobilityFeedback: String? = null,
    val sorenessFeedback: String? = null
)
