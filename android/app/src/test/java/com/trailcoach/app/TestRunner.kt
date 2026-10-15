package com.trailcoach.app

import com.trailcoach.app.data.healthconnect.HealthConnectManager
import com.trailcoach.app.domain.model.*
import com.trailcoach.app.domain.usecase.GenerateTrainingPlanUseCase
import java.time.Instant

class TestRunner {

    fun runAllTests() {
        println("=== DEBUT DES TESTS UNITAIRES (ETAPE 1 & ETAPE 2) ===")
        testUserModel()
        testGoalModel()
        testWorkoutSessionModel()
        testActivityModel()
        testTrainingPlanModel()
        testHealthConnectManagerPermissions()
        testHealthConnectManager30DaysData()
        testGenerateTrainingPlanUseCase()
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
        val raceDateIn24Weeks = now + (24L * 7 * 24 * 3600 * 1000) // 24 semaines

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
        assert(plan.cycles.size == 4) { "Le plan doit contenir exactement 4 phases de périodisation (obtenu: ${plan.cycles.size})" }

        val phase1 = plan.cycles[0]
        val phase2 = plan.cycles[1]
        val phase3 = plan.cycles[2]
        val phase4 = plan.cycles[3]

        assert(phase1.type == CycleType.DEVELOPPEMENT_GENERAL) { "Phase 1 doit être DEVELOPPEMENT_GENERAL" }
        assert(phase2.type == CycleType.SPECIFIQUE_TRAIL) { "Phase 2 doit être SPECIFIQUE_TRAIL" }
        assert(phase3.type == CycleType.AFFUTAGE) { "Phase 3 doit être AFFUTAGE/AFFINAGE" }
        assert(phase4.type == CycleType.RECUPERATION) { "Phase 4 doit être RECUPERATION/TAPER" }

        // Vérification présence séances clés : Renforcement Excentrique & Mobilité & Rando-Course
        val allSessions = plan.cycles.flatMap { it.sessions }
        val excentricSessions = allSessions.filter { it.type == WorkoutType.RENFORCEMENT_EXCENTRIQUE }
        val randoCourseSessions = allSessions.filter { it.type == WorkoutType.RANDO_COURSE }
        val mobilitySessions = allSessions.filter { it.type == WorkoutType.MOBILITE_SOUPLESSE }

        assert(excentricSessions.isNotEmpty()) { "Le plan doit inclure des séances de renforcement excentrique" }
        assert(randoCourseSessions.isNotEmpty()) { "Le plan doit inclure des séances de Rando-Course" }
        assert(mobilitySessions.isNotEmpty()) { "Le plan doit inclure des séances de mobilité" }

        // Vérification des consignes coach excentrique
        val excentricSample = excentricSessions.first()
        assert(excentricSample.description.contains("Squats Sautés Excentriques")) { "Manque d'exercices excentriques détaillés" }
        assert(excentricSample.coachNotes.contains("Ultra")) { "Consigne coach excentrique manquante" }

        println("[OK] Test GenerateTrainingPlanUseCase (Plan Ultra-Trail 24 semaines, 4 phases, Excentrique, Rando-Course & Mobilité)")
    }
}

fun main() {
    TestRunner().runAllTests()
}
