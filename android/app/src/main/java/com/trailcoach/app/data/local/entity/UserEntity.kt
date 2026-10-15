package com.trailcoach.app.data.local.entity

/**
 * Entité Room représentant l'utilisateur / athlète.
 */
data class UserEntity(
    val id: String,
    val name: String,
    val age: Int,
    val weightKg: Double,
    val vma: Double,
    val fcMax: Int,
    val fcRepos: Int = 50,
    val trailLevel: String = "INTERMEDIAIRE",
    val runningHoursWeekly: Double = 0.0,
    val ppgHoursWeekly: Double = 0.0,
    val mobilityHoursWeekly: Double = 0.0,
    val availableDaysCsv: String = "LUNDI,MERCREDI,SAMEDI,DIMANCHE"
)
