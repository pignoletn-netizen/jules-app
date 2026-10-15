package com.trailcoach.app.data.local.dao

import com.trailcoach.app.data.local.entity.ActivityEntity

/**
 * Interface DAO pour les activités de l'utilisateur.
 */
interface ActivityDao {
    fun getActivitiesForUser(userId: String): List<ActivityEntity>
    fun getActivityById(activityId: String): ActivityEntity?
    fun insertActivity(activity: ActivityEntity)
    fun insertActivities(activities: List<ActivityEntity>)
}
