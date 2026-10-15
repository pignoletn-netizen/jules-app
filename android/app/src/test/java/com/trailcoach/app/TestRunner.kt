package com.trailcoach.app

import com.trailcoach.app.data.healthconnect.HealthConnectManager
import com.trailcoach.app.domain.model.*
import java.time.Instant

class TestRunner {

    fun runAllTests() {
        println("=== DEBUT DES TESTS UNITAIRES DE L'ETAPE 1 ===")
        testUserModel()
        testGoalModel()
        testWorkoutSessionModel()
        testActivityModel()
        testTrainingPlanModel()
        testHealthConnectManagerPermissions()
        testHealthConnectManager30DaysData()
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
            raceDate = 1729180800000L,
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

        val missingSome = setOf("android.permission.health.READ_EXERCISE")
        assert(!manager.hasAllPermissions(missingSome)) { "Permissions incomplètes doivent échouer" }
        println("[OK] Test HealthConnectManager Permissions")
    }

    private fun testHealthConnectManager30DaysData() {
        val manager = HealthConnectManager()
        val now = Instant.now()
        val data30Days = manager.readAggregatedHealthDataLast30Days(now)

        assert(data30Days.exerciseSessions.isEmpty()) { "Liste exercice initiale vide" }
        assert(data30Days.heartRateSamples.isEmpty()) { "Liste FC initiale vide" }
        assert(data30Days.sleepSessions.isEmpty()) { "Liste Sommeil initiale vide" }
        assert(data30Days.hrvSamples.isEmpty()) { "Liste HRV initiale vide" }
        println("[OK] Test HealthConnectManager 30 Days Aggregation")
    }
}

fun main() {
    TestRunner().runAllTests()
}
