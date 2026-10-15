package com.trailcoach.app.data.local.entity

/**
 * Entité Room pour l'objectif de course (Goal).
 */
data class GoalEntity(
    val id: String,
    val userId: String,
    val raceName: String,
    val raceDateTimestamp: Long,
    val distanceKm: Double,
    val elevationGainDPlus: Int,
    val elevationLossDMinus: Int,
    val raceProfile: String,
    val priority: String = "A"
)
