package com.trailcoach.app.data.local.entity

/**
 * Entité Room pour une activité enregistrée.
 */
data class ActivityEntity(
    val id: String,
    val userId: String,
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
