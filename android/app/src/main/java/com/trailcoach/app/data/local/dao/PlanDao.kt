package com.trailcoach.app.data.local.dao

import com.trailcoach.app.data.local.entity.GoalEntity
import com.trailcoach.app.data.local.entity.WorkoutSessionEntity

/**
 * Interface DAO pour la gestion du plan d'entraînement, des objectifs et des séances.
 */
interface PlanDao {
    fun getGoalsForUser(userId: String): List<GoalEntity>
    fun insertGoal(goal: GoalEntity)

    fun getSessionsForPlan(planId: String): List<WorkoutSessionEntity>
    fun getSessionsByCategory(planId: String, category: String): List<WorkoutSessionEntity>

    fun insertSessions(sessions: List<WorkoutSessionEntity>)
    fun updateSession(session: WorkoutSessionEntity)
}
