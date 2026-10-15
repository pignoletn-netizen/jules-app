package com.trailcoach.app

import com.trailcoach.app.data.healthconnect.HealthConnectHrvSample
import com.trailcoach.app.data.healthconnect.HealthConnectManager
import com.trailcoach.app.data.local.AppDatabase
import com.trailcoach.app.data.repository.ActivityRepositoryImpl
import com.trailcoach.app.data.repository.PlanRepositoryImpl
import com.trailcoach.app.domain.model.*
import com.trailcoach.app.domain.usecase.AnalyzeAndAdaptPlanUseCase
import com.trailcoach.app.domain.usecase.GenerateTrainingPlanUseCase
import com.trailcoach.app.domain.usecase.HrvStatus
import java.time.Instant

class TestRunner {

    fun runAllTests() {
        println("=== DEBUT DES TESTS UNITAIRES (ETAPES 1 A 4) ===")
        testUserModel()
        testGoalModel()
        testWorkoutSessionModel()
        testActivityModel()
        testTrainingPlanModel()
        testHealthConnectManagerPermissions()
        testHealthConnectManager30DaysData()
        testGenerateTrainingPlanUseCase()
        testAnalyzeAndAdaptPlanUseCaseFatigue()
        testAnalyzeAndAdaptPlanUseCaseUnderVolume()
        testRoomDatabaseAndRepositories()
        println("=== TOUS LES TESTS PASSED AVEC SUCCES ===")
    }

    private fun testUserModel() {
        val user = User(
            id = "u123",
            name = "Mathieu",
            age = 34,
            weightKg = 68.5,
            vma = 18.5,
            fcMax = 192,
            fcRepos = 42,
            trailLevel = TrailLevel.EXPERT_ULTRA,
            weeklyAvailability = WeeklyAvailability(
                runningHours = 10.0,
                ppgHours = 3.0,
                mobilityHours = 2.0,
                availableDays = setOf("MARDI", "JEUDI", "SAMEDI", "DIMANCHE")
            )
        )

        assert(user.age == 34) { "Âge incorrect" }
        assert(user.weightKg == 68.5) { "Poids incorrect" }
        assert(user.vma == 18.5) { "VMA incorrecte" }
        assert(user.fcMax == 192) { "FCmax incorrecte" }
        assert(user.weeklyAvailability.runningHours == 10.0) { "Heures de course incorrectes" }
        println("[OK] Test User Model")
    }

    private fun testGoalModel() {
        val goal = Goal(
            id = "g001",
            raceName = "Diagonale des Fous",
            raceDate = System.currentTimeMillis() + (180L * 24 * 3600 * 1000),
            distanceKm = 165.0,
            elevationGainDPlus = 10200,
            elevationLossDMinus = 10200,
            raceProfile = RaceProfile.TRES_TECHNIQUE_ALPIN,
            priority = GoalPriority.A
        )

        assert(goal.raceName == "Diagonale des Fous") { "Nom de course incorrect" }
        assert(goal.distanceKm == 165.0) { "Distance incorrecte" }
        assert(goal.elevationGainDPlus == 10200) { "D+ incorrect" }
        assert(goal.priority == GoalPriority.A) { "Priorité incorrecte" }
        println("[OK] Test Goal Model")
    }

    private fun testWorkoutSessionModel() {
        val session = WorkoutSession(
            id = "ws001",
            type = WorkoutType.RENFORCEMENT_EXCENTRIQUE,
            title = "Excentrique Quadriceps & Mollets",
            description = "5 séries de 10 squats sautés contrôlés + chaise excentrique",
            coachNotes = "Focus freinement à la descente selon conseils Mathieu Blanchard",
            targets = WorkoutTargets(durationMinutes = 45)
        )

        assert(session.type == WorkoutType.RENFORCEMENT_EXCENTRIQUE) { "Type de séance incorrect" }
        assert(session.targets.durationMinutes == 45) { "Durée incorrecte" }
        println("[OK] Test WorkoutSession Model")
    }

    private fun testActivityModel() {
        val activity = Activity(
            id = "act001",
            timestamp = System.currentTimeMillis(),
            type = "TRAIL_RUNNING",
            avgHeartRate = 145,
            maxHeartRate = 172,
            elevationGainDPlus = 850,
            elevationLossDMinus = 850,
            distanceKm = 18.5,
            durationMinutes = 135.0,
            paceMinPerKm = "7:18",
            gapPaceMinPerKm = "5:45",
            rpe = 7,
            mobilityFeedback = "Légère raideur ischios",
            sorenessFeedback = "Courbatures modérées quadriceps D-"
        )

        assert(activity.avgHeartRate == 145) { "FC moyenne incorrecte" }
        assert(activity.elevationGainDPlus == 850) { "D+ incorrect" }
        assert(activity.gapPaceMinPerKm == "5:45") { "GAP Pace incorrect" }
        assert(activity.rpe == 7) { "RPE incorrect" }
        println("[OK] Test Activity Model")
    }

    private fun testTrainingPlanModel() {
        val plan = TrainingPlan(
            id = "plan_001",
            userId = "u123",
            goalId = "g001",
            trimpLoad = 450.0,
            tssLoad = 380.0,
            volumeDistribution = VolumeDistribution(
                totalDPlusMeters = 3500,
                totalDMinusMeters = 3500,
                ppgRatioPourcent = 20.0,
                mobilityRatioPourcent = 10.0
            )
        )

        assert(plan.trimpLoad == 450.0) { "TRIMP incorrect" }
        assert(plan.volumeDistribution.totalDPlusMeters == 3500) { "Volume D+ incorrect" }
        println("[OK] Test TrainingPlan Model")
    }

    private fun testHealthConnectManagerPermissions() {
        val manager = HealthConnectManager()
        assert(manager.isAvailable()) { "HealthConnect doit être disponible" }

        val allGranted = setOf(
            "android.permission.health.READ_EXERCISE",
            "android.permission.health.READ_HEART_RATE",
            "android.permission.health.READ_SLEEP",
            "android.permission.health.READ_HEART_RATE_VARIABILITY"
        )
        assert(manager.hasAllPermissions(allGranted)) { "Toutes les permissions doivent être validées" }
        println("[OK] Test HealthConnectManager Permissions")
    }

    private fun testHealthConnectManager30DaysData() {
        val manager = HealthConnectManager()
        val now = Instant.now()
        val data30Days = manager.readAggregatedHealthDataLast30Days(now)

        assert(data30Days.exerciseSessions.isEmpty()) { "Liste exercice initiale vide" }
        println("[OK] Test HealthConnectManager 30 Days Aggregation")
    }

    private fun testGenerateTrainingPlanUseCase() {
        val user = User("u1", "Julien", 30, 70.0, 17.0, 190)
        val goal = Goal("g1", "UTMB", System.currentTimeMillis() + (100L * 24 * 3600 * 1000), 171.0, 9960)
        val plan = GenerateTrainingPlanUseCase().execute(user, goal)

        assert(plan.cycles.size == 4) { "4 phases attendues" }
        println("[OK] Test GenerateTrainingPlanUseCase")
    }

    private fun testAnalyzeAndAdaptPlanUseCaseFatigue() {
        val user = User("u1", "Julien", 30, 70.0, 17.0, 190)
        val goal = Goal("g1", "Diagonale des Fous", System.currentTimeMillis() + (100L * 24 * 3600 * 1000), 165.0, 10000)
        val plan = GenerateTrainingPlanUseCase().execute(user, goal)

        val hardActivity = Activity(
            id = "act_hard",
            timestamp = System.currentTimeMillis(),
            type = "TRAIL_RUNNING",
            avgHeartRate = 175,
            maxHeartRate = 188,
            elevationGainDPlus = 600,
            elevationLossDMinus = 600,
            distanceKm = 12.0,
            durationMinutes = 90.0,
            paceMinPerKm = "7:30",
            rpe = 9,
            sorenessFeedback = "Forte douleur quadriceps"
        )

        val lowHrvSample = listOf(HealthConnectHrvSample(38.0, Instant.now()))

        val report = AnalyzeAndAdaptPlanUseCase().execute(plan, hardActivity, userHrvSamples = lowHrvSample)
        assert(report.isPlanAdapted) { "Le plan aurait dû être adapté" }
        println("[OK] Test AnalyzeAndAdaptPlanUseCase Fatigue")
    }

    private fun testAnalyzeAndAdaptPlanUseCaseUnderVolume() {
        val user = User("u1", "Julien", 30, 70.0, 17.0, 190)
        val goal = Goal("g1", "Trail Local", System.currentTimeMillis() + (60L * 24 * 3600 * 1000), 50.0, 2500)
        val plan = GenerateTrainingPlanUseCase().execute(user, goal)

        val shortActivity = Activity(
            id = "act_short",
            timestamp = System.currentTimeMillis(),
            type = "TRAIL_RUNNING",
            avgHeartRate = 140,
            maxHeartRate = 155,
            elevationGainDPlus = 100,
            elevationLossDMinus = 100,
            distanceKm = 5.0,
            durationMinutes = 40.0,
            paceMinPerKm = "8:00",
            rpe = 4
        )

        val report = AnalyzeAndAdaptPlanUseCase().execute(plan, shortActivity)
        assert(report.isPlanAdapted) { "Plan adapté pour sous-volume" }
        println("[OK] Test AnalyzeAndAdaptPlanUseCase Under Volume")
    }

    private fun testRoomDatabaseAndRepositories() {
        val db = AppDatabase()
        val healthConnectManager = HealthConnectManager()

        val planRepo = PlanRepositoryImpl(db.planDao)
        val activityRepo = ActivityRepositoryImpl(db.activityDao, healthConnectManager)

        val user = User("u_room", "Alex", 28, 65.0, 19.0, 195)
        val goal = Goal("g_room", "UTMB 100M", System.currentTimeMillis() + (120L * 24 * 3600 * 1000), 170.0, 10000)
        val plan = GenerateTrainingPlanUseCase().execute(user, goal)

        planRepo.saveGoal(goal, user.id)
        planRepo.savePlan(plan)

        val storedGoals = db.planDao.getGoalsForUser(user.id)
        assert(storedGoals.size == 1) { "Goal Room attendu 1, obtenu ${storedGoals.size}" }
        assert(storedGoals[0].raceName == "UTMB 100M") { "Nom de course incorrect" }

        val runningSessions = db.planDao.getSessionsByCategory(plan.id, "RUNNING")
        val ppgSessions = db.planDao.getSessionsByCategory(plan.id, "PPG")
        val mobilitySessions = db.planDao.getSessionsByCategory(plan.id, "MOBILITE")

        assert(runningSessions.isNotEmpty()) { "Sessions Running attendues" }
        assert(ppgSessions.isNotEmpty()) { "Sessions PPG attendues" }
        assert(mobilitySessions.isNotEmpty()) { "Sessions Mobilité attendues" }

        val newActivity = Activity(
            id = "act_room_01",
            timestamp = System.currentTimeMillis(),
            type = "TRAIL_RUNNING",
            avgHeartRate = 150,
            maxHeartRate = 170,
            elevationGainDPlus = 500,
            elevationLossDMinus = 500,
            distanceKm = 15.0,
            durationMinutes = 110.0,
            paceMinPerKm = "7:20"
        )

        activityRepo.saveActivity(user.id, newActivity)
        val localActivities = activityRepo.getLocalActivities(user.id)
        assert(localActivities.size == 1) { "Activité sauvegardée attendue 1" }
        assert(localActivities[0].id == "act_room_01") { "Activity ID mismatch" }

        println("[OK] Test Room Database & Repositories (Entities, DAOs, Category Filtering & Health Connect Link)")
    }
}

fun main() {
    TestRunner().runAllTests()
}
