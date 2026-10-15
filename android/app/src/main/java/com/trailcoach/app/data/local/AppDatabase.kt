package com.trailcoach.app.data.local

import com.trailcoach.app.data.local.dao.ActivityDao
import com.trailcoach.app.data.local.dao.PlanDao
import com.trailcoach.app.data.local.dao.UserDao
import com.trailcoach.app.data.local.entity.ActivityEntity
import com.trailcoach.app.data.local.entity.GoalEntity
import com.trailcoach.app.data.local.entity.UserEntity
import com.trailcoach.app.data.local.entity.WorkoutSessionEntity

/**
 * Interface d'abstraction de la base de données Room.
 */
abstract class AppDatabase {
    abstract fun userDao(): UserDao
    abstract fun planDao(): PlanDao
    abstract fun activityDao(): ActivityDao

    companion object {
        fun createInMemoryDatabase(): AppDatabase {
            val user = InMemoryUserDao()
            val plan = InMemoryPlanDao()
            val activity = InMemoryActivityDao()

            return object : AppDatabase() {
                override fun userDao(): UserDao = user
                override fun planDao(): PlanDao = plan
                override fun activityDao(): ActivityDao = activity
            }
        }
    }
}

class InMemoryUserDao : UserDao {
    private val users = mutableMapOf<String, UserEntity>()
    override fun getUserById(userId: String): UserEntity? = users[userId]
    override fun insertUser(user: UserEntity) { users[user.id] = user }
    override fun updateUser(user: UserEntity) { users[user.id] = user }
}

class InMemoryPlanDao : PlanDao {
    private val goals = mutableListOf<GoalEntity>()
    private val sessions = mutableListOf<WorkoutSessionEntity>()

    override fun getGoalsForUser(userId: String): List<GoalEntity> = goals.filter { it.userId == userId }
    override fun insertGoal(goal: GoalEntity) { goals.add(goal) }

    override fun getSessionsForPlan(planId: String): List<WorkoutSessionEntity> = sessions.filter { it.planId == planId }

    override fun getSessionsByCategory(planId: String, category: String): List<WorkoutSessionEntity> =
        sessions.filter { it.planId == planId && it.sessionCategory == category }

    override fun insertSessions(sessions: List<WorkoutSessionEntity>) { this.sessions.addAll(sessions) }
    override fun updateSession(session: WorkoutSessionEntity) {
        val index = sessions.indexOfFirst { it.id == session.id }
        if (index != -1) sessions[index] = session
    }
}

class InMemoryActivityDao : ActivityDao {
    private val activities = mutableListOf<ActivityEntity>()

    override fun getActivitiesForUser(userId: String): List<ActivityEntity> = activities.filter { it.userId == userId }
    override fun getActivityById(activityId: String): ActivityEntity? = activities.firstOrNull { it.id == activityId }
    override fun insertActivity(activity: ActivityEntity) { activities.add(activity) }
    override fun insertActivities(activities: List<ActivityEntity>) { this.activities.addAll(activities) }
}
