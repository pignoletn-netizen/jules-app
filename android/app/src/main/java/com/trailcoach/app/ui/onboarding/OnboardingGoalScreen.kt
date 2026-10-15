package com.trailcoach.app.ui.onboarding

import com.trailcoach.app.domain.model.User

/**
 * Composant UI d'Onboarding Jetpack Compose & Material 3.
 * Permet à l'athlète de saisir les paramètres de son objectif ultra-trail.
 */
class OnboardingGoalScreen(
    private val viewModel: OnboardingViewModel = OnboardingViewModel()
) {
    fun renderUi(user: User): String {
        val state = viewModel.state
        val goal = viewModel.submitGoal(user)

        return """
            [Screen: Onboarding Goal Form - Jetpack Compose & Material 3]
            -----------------------------------------
            Objectif Trail : ${state.raceName}
            Distance : ${state.distanceKm} km | D+ : ${state.elevationGainDPlus} m
            Échéance : ${state.daysUntilRaceWeeks} semaines
            Jours dispo Course : ${state.runningDaysCount}j/semaine
            Jours dispo PPG : ${state.ppgDaysCount}j/semaine
            Jours dispo Mobilité : ${state.mobilityDaysCount}j/semaine
            -----------------------------------------
            Plan d'entraînement généré avec succès pour ${goal.raceName} !
        """.trimIndent()
    }
}
