package com.trailcoach.app.ui.calendar

import com.trailcoach.app.domain.model.TrainingPlan

/**
 * Composant UI CalendarPlanScreen Jetpack Compose & Material 3.
 * Affiche le mix entre Séances de Course, Renforcement Trail et Sessions de Mobilité.
 */
class CalendarPlanScreen(
    private val viewModel: CalendarViewModel = CalendarViewModel()
) {
    fun renderUi(activePlan: TrainingPlan?, currentFilter: String = "TOUT"): String {
        viewModel.filterSessions(currentFilter, activePlan)
        val state = viewModel.state

        val sessionsFormatted = state.sessions.take(6).joinToString("\n") { s ->
            "   * [${s.type.name}] ${s.title} (${s.targets.durationMinutes} min)"
        }

        return """
            [Screen: CalendarPlanScreen - Planning des Séances (Jetpack Compose / Material 3)]
            Filtre actif : ${state.selectedFilter} (Options: TOUT | COURSE | PPG | MOBILITE)
            -------------------------------------------------
            Séances planifiées (${state.sessions.size} séances) :
            $sessionsFormatted
            -------------------------------------------------
        """.trimIndent()
    }
}
