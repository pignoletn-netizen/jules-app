package com.trailcoach.app.data.local.entity

/**
 * Entité Room pour une séance d'entraînement.
 *
 * @property sessionCategory Category of session: "RUNNING", "PPG", or "MOBILITE"
 */
data class WorkoutSessionEntity(
    val id: String,
    val planId: String,
    val cycleName: String,
    val type: String, // VMA_COURTE, VMA_COTE, RANDO_COURSE, RENFORCEMENT_EXCENTRIQUE, MOBILITE_SOUPLESSE, REPOS, etc.
    val sessionCategory: String, // "RUNNING", "PPG", "MOBILITE"
    val title: String,
    val description: String,
    val coachNotes: String,
    val durationMinutes: Int,
    val targetFcPercentMin: Int? = null,
    val targetFcPercentMax: Int? = null,
    val targetDPlus: Int? = null,
    val targetPaceMinPerKm: String? = null,
    val isCompleted: Boolean = false
)
