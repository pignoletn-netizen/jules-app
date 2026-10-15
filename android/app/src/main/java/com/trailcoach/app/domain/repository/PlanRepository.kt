package com.trailcoach.app.domain.repository

import com.trailcoach.app.domain.model.Goal
import com.trailcoach.app.domain.model.TrainingPlan
import com.trailcoach.app.domain.model.WorkoutSession

/**
 * Interface du Repository pour le plan d'entraînement.
 */
interface PlanRepository {
    fun getActivePlan(userId: String): TrainingPlan?
    fun savePlan(plan: TrainingPlan)
    fun updateWorkoutSession(session: WorkoutSession)
    fun saveGoal(goal: Goal, userId: String)
}
