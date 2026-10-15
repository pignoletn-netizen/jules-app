package com.trailcoach.app.ui.onboarding

import com.trailcoach.app.domain.model.Goal
import com.trailcoach.app.domain.model.GoalPriority
import com.trailcoach.app.domain.model.RaceProfile
import com.trailcoach.app.domain.model.User
import com.trailcoach.app.domain.model.WeeklyAvailability
import com.trailcoach.app.domain.usecase.GenerateTrainingPlanUseCase

data class OnboardingUiState(
    val raceName: String = "Diagonale des Fous",
    val distanceKm: String = "165",
    val elevationGainDPlus: String = "10200",
    val daysUntilRaceWeeks: String = "24",
    val runningDaysCount: Int = 4,
    val ppgDaysCount: Int = 2,
    val mobilityDaysCount: Int = 3,
    val isSubmitted: Boolean = false
)

/**
 * ViewModel Jetpack Compose gérant l'état UI pour l'Onboarding.
 */
class OnboardingViewModel(
    private val generatePlanUseCase: GenerateTrainingPlanUseCase = GenerateTrainingPlanUseCase()
) {
    var state: OnboardingUiState = OnboardingUiState()
        private set

    fun updateRaceName(name: String) { state = state.copy(raceName = name) }
    fun updateDistance(distance: String) { state = state.copy(distanceKm = distance) }
    fun updateElevation(elevation: String) { state = state.copy(elevationGainDPlus = elevation) }
    fun updateWeeks(weeks: String) { state = state.copy(daysUntilRaceWeeks = weeks) }

    fun submitGoal(user: User): Goal {
        val dist = state.distanceKm.toDoubleOrNull() ?: 100.0
        val dPlus = state.elevationGainDPlus.toIntOrNull() ?: 5000
        val weeks = state.daysUntilRaceWeeks.toLongOrNull() ?: 24L

        val goal = Goal(
            id = "goal_" + System.currentTimeMillis(),
            raceName = state.raceName,
            raceDate = System.currentTimeMillis() + (weeks * 7 * 24 * 3600 * 1000),
            distanceKm = dist,
            elevationGainDPlus = dPlus,
            elevationLossDMinus = dPlus,
            raceProfile = RaceProfile.TRES_TECHNIQUE_ALPIN,
            priority = GoalPriority.A
        )

        val updatedAvailability = WeeklyAvailability(
            runningHours = state.runningDaysCount * 2.0,
            ppgHours = state.ppgDaysCount * 1.0,
            mobilityHours = state.mobilityDaysCount * 0.5
        )

        val updatedUser = user.copy(weeklyAvailability = updatedAvailability)
        generatePlanUseCase.execute(updatedUser, goal)

        state = state.copy(isSubmitted = true)
        return goal
    }
}
