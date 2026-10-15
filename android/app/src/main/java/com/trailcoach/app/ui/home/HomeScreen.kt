package com.trailcoach.app.ui.home

import com.trailcoach.app.domain.model.TrainingPlan

/**
 * Composant UI HomeScreen (Dashboard principal) Jetpack Compose & Material 3.
 */
class HomeScreen(
    private val viewModel: HomeViewModel = HomeViewModel()
) {
    fun renderUi(activePlan: TrainingPlan?): String {
        viewModel.loadDashboardData(activePlan)
        val state = viewModel.state
        val session = state.nextSession
        val badgeColorHex = viewModel.getBadgeColorHexForSession(session?.type)

        return """
            [Screen: HomeScreen - Dashboard Trail Coach (Jetpack Compose / Material 3)]
            =================================================
            📊 CHARGE HEBDOMADAIRE :
            - Distance : ${state.weeklyLoad.totalKm} km
            - Dénivelé : ${state.weeklyLoad.totalDPlusMeters} m D+
            - PPG / Renforcement : ${state.weeklyLoad.ppgMinutes} min
            - Mobilité & Souplesse : ${state.weeklyLoad.mobilityMinutes} min
            -------------------------------------------------
            🏃 PROCHAINE SÉANCE :
            - Titre : ${session?.title ?: "Repos ou Récupération"}
            - Type : ${session?.type?.name ?: "REPOS"} [Badge Couleur: $badgeColorHex]
            - Consigne Coach : ${session?.coachNotes ?: "Conservez votre énergie."}
            - Durée : ${session?.targets?.durationMinutes ?: 0} min
            -------------------------------------------------
            ❤️ FORME & RÉCUPÉRATION (Garmin / Health Connect) :
            - HRV RMSSD : ${state.recoveryStatus.hrvScoreRmssd} ms
            - Qualité du Sommeil : ${state.recoveryStatus.sleepQualityScore}/100
            - Statut : ${state.recoveryStatus.statusText}
            -------------------------------------------------
            [Bouton Action: Sync Health Connect] -> Données à jour
            =================================================
        """.trimIndent()
    }
}
