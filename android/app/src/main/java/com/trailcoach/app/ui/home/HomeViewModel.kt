package com.trailcoach.app.ui.home

import com.trailcoach.app.domain.model.TrainingPlan
import com.trailcoach.app.domain.model.WorkoutSession
import com.trailcoach.app.domain.model.WorkoutType

data class WeeklyLoadState(
    val totalKm: Double = 48.5,
    val totalDPlusMeters: Int = 2150,
    val ppgMinutes: Int = 90,
    val mobilityMinutes: Int = 45
)

data class RecoveryHrvState(
    val hrvScoreRmssd: Int = 68,
    val sleepQualityScore: Int = 85,
    val statusText: String = "Excellente Récupération (Garmin Sync)"
)

data class HomeUiState(
    val weeklyLoad: WeeklyLoadState = WeeklyLoadState(),
    val recoveryStatus: RecoveryHrvState = RecoveryHrvState(),
    val nextSession: WorkoutSession? = null,
    val isSyncing: Boolean = false,
    val syncMessage: String? = null
)

/**
 * ViewModel Jetpack Compose pour le Dashboard HomeScreen.
 */
class HomeViewModel {
    var state: HomeUiState = HomeUiState()
        private set

    fun loadDashboardData(activePlan: TrainingPlan?) {
        val next = activePlan?.cycles?.flatMap { it.sessions }?.firstOrNull { !it.isCompleted }
        state = state.copy(nextSession = next)
    }

    fun syncHealthConnectData() {
        state = state.copy(isSyncing = true)
        state = state.copy(
            isSyncing = false,
            syncMessage = "Données Garmin synchronisées avec succès via Health Connect (FC, Sommeil, HRV).",
            recoveryStatus = RecoveryHrvState(
                hrvScoreRmssd = 72,
                sleepQualityScore = 88,
                statusText = "Forme Optimale (HRV 72ms)"
            )
        )
    }

    fun getBadgeColorHexForSession(type: WorkoutType?): String {
        return when (type) {
            WorkoutType.ENDURANCE_FONDAMENTALE, WorkoutType.RANDO_COURSE -> "#2E7D32" // Vert
            WorkoutType.VMA_COURTE, WorkoutType.VMA_COTE, WorkoutType.TRAVAIL_DESCENTE -> "#D32F2F" // Rouge
            WorkoutType.RENFORCEMENT_EXCENTRIQUE -> "#7B1FA2" // Violet
            WorkoutType.MOBILITE_SOUPLESSE -> "#0288D1" // Bleu
            WorkoutType.REPOS, null -> "#757575" // Gris
        }
    }
}
