package com.trailcoach.app.ui.calendar

import com.trailcoach.app.domain.model.TrainingPlan
import com.trailcoach.app.domain.model.WorkoutSession

data class CalendarUiState(
    val selectedFilter: String = "TOUT", // "TOUT", "COURSE", "PPG", "MOBILITE"
    val sessions: List<WorkoutSession> = emptyList()
)

/**
 * ViewModel Jetpack Compose pour le planning/calendrier.
 */
class CalendarViewModel {
    var state: CalendarUiState = CalendarUiState()
        private set

    fun loadSessions(plan: TrainingPlan?) {
        val allSessions = plan?.cycles?.flatMap { it.sessions } ?: emptyList()
        state = state.copy(sessions = allSessions)
    }

    fun filterSessions(filter: String, plan: TrainingPlan?) {
        val allSessions = plan?.cycles?.flatMap { it.sessions } ?: emptyList()
        val filtered = when (filter) {
            "COURSE" -> allSessions.filter { it.type.name.contains("VMA") || it.type.name.contains("ENDURANCE") || it.type.name.contains("RANDO") }
            "PPG" -> allSessions.filter { it.type.name.contains("RENFORCEMENT") }
            "MOBILITE" -> allSessions.filter { it.type.name.contains("MOBILITE") }
            else -> allSessions
        }
        state = state.copy(selectedFilter = filter, sessions = filtered)
    }
}
