package com.trailcoach.app

import com.trailcoach.app.data.healthconnect.HealthConnectHrvSample
import com.trailcoach.app.data.healthconnect.HealthConnectManager
import com.trailcoach.app.domain.model.*
import com.trailcoach.app.domain.usecase.AnalyzeAndAdaptPlanUseCase
import com.trailcoach.app.domain.usecase.GenerateTrainingPlanUseCase
import com.trailcoach.app.domain.usecase.HrvStatus
import java.time.Instant

class TestRunner {

    fun runAllTests() {
        println("=== DEBUT DES TESTS UNITAIRES (ETAPES 1, 2 & 3) ===")
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
            raceDate = System.currentTimeMillis() + (180L * 24 * 3600 * 1000), // Dans 6 mois
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

    private fun testGenerateTrainingPlanUseCase() {
        val user = User(
            id = "u1",
            name = "Julien",
            age = 30,
            weightKg = 70.0,
            vma = 17.0,
            fcMax = 190,
            trailLevel = TrailLevel.CONFIRME,
            weeklyAvailability = WeeklyAvailability(runningHours = 8.0, ppgHours = 2.0, mobilityHours = 1.0)
        )

        val now = System.currentTimeMillis()
        val raceDateIn24Weeks = now + (24L * 7 * 24 * 3600 * 1000)

        val goal = Goal(
            id = "g1",
            raceName = "UTMB - Ultra Trail du Mont Blanc",
            raceDate = raceDateIn24Weeks,
            distanceKm = 171.0,
            elevationGainDPlus = 9960,
            elevationLossDMinus = 9960,
            raceProfile = RaceProfile.TRES_TECHNIQUE_ALPIN,
            priority = GoalPriority.A
        )

        val useCase = GenerateTrainingPlanUseCase()
        val plan = useCase.execute(user, goal, startDateMillis = now)

        assert(plan.userId == user.id) { "UserId mismatch" }
        assert(plan.goalId == goal.id) { "GoalId mismatch" }
        assert(plan.cycles.size == 4) { "Le plan doit contenir 4 phases" }
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
            rpe = 9, // RPE très élevé
            sorenessFeedback = "Forte douleur quadriceps"
        )

        val lowHrvSample = listOf(HealthConnectHrvSample(38.0, Instant.now())) // Baseline 65.0, donc 38ms est anormalement bas

        val useCase = AnalyzeAndAdaptPlanUseCase()
        val report = useCase.execute(
            currentPlan = plan,
            completedActivity = hardActivity,
            userHrvSamples = lowHrvSample,
            baselineHrvRmssd = 65.0
        )

        assert(report.analysis.hrvBaselineStatus == HrvStatus.ANORMALEMENT_BAS) { "Le HRV doit être identifié comme anormalement bas" }
        assert(report.analysis.fatigueIndex >= 70) { "Score de fatigue doit être >= 70" }
        assert(report.isPlanAdapted) { "Le plan aurait dû être adapté en raison de la fatigue" }

        val firstUncompletedNextSession = report.updatedPlan.cycles[0].sessions.first { !it.isCompleted }
        assert(firstUncompletedNextSession.type == WorkoutType.MOBILITE_SOUPLESSE) { "La séance suivante aurait dû être reconvertie en Mobilité Douce" }
        println("[OK] Test AnalyzeAndAdaptPlanUseCase Fatigue & Low HRV Conversion")
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
            elevationGainDPlus = 100, // Cible côte était 400m D+ -> compliance < 60%
            elevationLossDMinus = 100,
            distanceKm = 5.0,
            durationMinutes = 40.0,
            paceMinPerKm = "8:00",
            rpe = 4 // RPE faible/normal
        )

        val normalHrvSample = listOf(HealthConnectHrvSample(66.0, Instant.now()))

        val useCase = AnalyzeAndAdaptPlanUseCase()
        val report = useCase.execute(
            currentPlan = plan,
            completedActivity = shortActivity,
            userHrvSamples = normalHrvSample,
            baselineHrvRmssd = 65.0
        )

        assert(report.analysis.hrvBaselineStatus == HrvStatus.NORMAL) { "HRV normal" }
        assert(report.isPlanAdapted) { "Le plan aurait dû être adapté pour sous-volume D+" }
        assert(report.adaptationReason?.contains("Rééquilibrage du volume") == true) { "Raison de rééquilibrage attendue" }
        println("[OK] Test AnalyzeAndAdaptPlanUseCase Under Volume Adjustment")
    }
}

fun main() {
    TestRunner().runAllTests()
}
