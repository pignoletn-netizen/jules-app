package com.trailcoach.app.ui.session

import com.trailcoach.app.domain.model.WorkoutSession

data class SessionDetailUiState(
    val session: WorkoutSession? = null,
    val warmupNotes: String = "20 minutes en endurance fondamentale progressive + éducatifs de foulée (montées de genoux, griffés sol).",
    val cooldownNotes: String = "10 minutes footing très lent de retour au calme + réhydratation.",
    val exercisesList: List<String> = emptyList()
)

/**
 * ViewModel Jetpack Compose pour la fiche détaillée de séance.
 */
class SessionDetailViewModel {
    var state: SessionDetailUiState = SessionDetailUiState()
        private set

    fun setSession(session: WorkoutSession) {
        val exercises = if (session.type.name.contains("RENFORCEMENT") || session.type.name.contains("MOBILITE")) {
            session.description.split("\n")
        } else {
            emptyList()
        }

        state = state.copy(
            session = session,
            exercisesList = exercises
        )
    }
}
