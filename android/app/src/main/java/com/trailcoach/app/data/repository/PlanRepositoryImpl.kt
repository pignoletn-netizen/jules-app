package com.trailcoach.app.data.repository

import com.trailcoach.app.data.local.dao.PlanDao
import com.trailcoach.app.data.local.entity.GoalEntity
import com.trailcoach.app.data.local.entity.WorkoutSessionEntity
import com.trailcoach.app.domain.model.*
import com.trailcoach.app.domain.repository.PlanRepository

/**
 * Implémentation du PlanRepository interagissant avec la base Room (PlanDao).
 */
class PlanRepositoryImpl(
    private val planDao: PlanDao
) : PlanRepository {

    private var activePlanCache: TrainingPlan? = null

    override fun getActivePlan(userId: String): TrainingPlan? {
        return activePlanCache
    }

    override fun savePlan(plan: TrainingPlan) {
        activePlanCache = plan

        val sessionEntities = plan.cycles.flatMap { cycle ->
            cycle.sessions.map { session ->
                WorkoutSessionEntity(
                    id = session.id,
                    planId = plan.id,
                    cycleName = cycle.name,
                    type = session.type.name,
                    sessionCategory = when (session.type) {
                        WorkoutType.VMA_COURTE, WorkoutType.VMA_COTE, WorkoutType.ENDURANCE_FONDAMENTALE, WorkoutType.RANDO_COURSE, WorkoutType.TRAVAIL_DESCENTE -> "RUNNING"
                        WorkoutType.RENFORCEMENT_EXCENTRIQUE -> "PPG"
                        WorkoutType.MOBILITE_SOUPLESSE -> "MOBILITE"
                        WorkoutType.REPOS -> "REPOS"
                    },
                    title = session.title,
                    description = session.description,
                    coachNotes = session.coachNotes,
                    durationMinutes = session.targets.durationMinutes,
                    targetFcPercentMin = session.targets.targetFcPercentMax?.start,
                    targetFcPercentMax = session.targets.targetFcPercentMax?.endInclusive,
                    targetDPlus = session.targets.targetDPlus,
                    targetPaceMinPerKm = session.targets.targetPaceMinPerKm,
                    isCompleted = session.isCompleted
                )
            }
        }

        planDao.insertSessions(sessionEntities)
    }

    override fun updateWorkoutSession(session: WorkoutSession) {
        val currentPlan = activePlanCache
        if (currentPlan != null) {
            val updatedCycles = currentPlan.cycles.map { cycle ->
                val updatedSessions = cycle.sessions.map {
                    if (it.id == session.id) session else it
                }
                cycle.copy(sessions = updatedSessions)
            }
            activePlanCache = currentPlan.copy(cycles = updatedCycles)
        }
    }

    override fun saveGoal(goal: Goal, userId: String) {
        val entity = GoalEntity(
            id = goal.id,
            userId = userId,
            raceName = goal.raceName,
            raceDateTimestamp = goal.raceDate,
            distanceKm = goal.distanceKm,
            elevationGainDPlus = goal.elevationGainDPlus,
            elevationLossDMinus = goal.elevationLossDMinus,
            raceProfile = goal.raceProfile.name,
            priority = goal.priority.name
        )
        planDao.insertGoal(entity)
    }
}
