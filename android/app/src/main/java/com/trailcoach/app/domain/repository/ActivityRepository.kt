package com.trailcoach.app.domain.repository

import com.trailcoach.app.domain.model.Activity
import java.time.Instant

/**
 * Interface du Repository pour la gestion des activités.
 * Articule les données locales (Room) et la passerelle externe (Health Connect).
 */
interface ActivityRepository {
    fun getLocalActivities(userId: String): List<Activity>
    fun syncActivitiesFromHealthConnect(userId: String, startTime: Instant, endTime: Instant): List<Activity>
    fun saveActivity(userId: String, activity: Activity)
}
