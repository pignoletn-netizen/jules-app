package com.trailcoach.app.ui.session

import com.trailcoach.app.domain.model.WorkoutSession

/**
 * Composant UI SessionDetailScreen Jetpack Compose & Material 3.
 * Fiche détaillée de la séance pour Course / Trail ou PPG / Mobilité.
 */
class SessionDetailScreen(
    private val viewModel: SessionDetailViewModel = SessionDetailViewModel()
) {
    fun renderUi(session: WorkoutSession): String {
        viewModel.setSession(session)
        val state = viewModel.state

        val isRunning = session.type.name.contains("VMA") || session.type.name.contains("ENDURANCE") || session.type.name.contains("RANDO")

        return if (isRunning) {
            """
                [Screen: SessionDetailScreen - Course / Trail (Jetpack Compose / Material 3)]
                =================================================
                Titre : ${session.title}
                Type : ${session.type.name} | Durée : ${session.targets.durationMinutes} min
                -------------------------------------------------
                🔥 ÉCHAUFFEMENT :
                ${state.warmupNotes}

                🎯 CORPS DE SÉANCE :
                Description : ${session.description}
                Cible FC : ${session.targets.targetFcPercentMax ?: "Aisance respiratoire"}
                Cible D+ : ${session.targets.targetDPlus ?: 0} m D+

                🧊 RETOUR AU CALME :
                ${state.cooldownNotes}

                💡 CONSEIL DU COACH :
                ${session.coachNotes}
                =================================================
            """.trimIndent()
        } else {
            """
                [Screen: SessionDetailScreen - PPG / Renforcement / Mobilité (Jetpack Compose / Material 3)]
                =================================================
                Titre : ${session.title}
                Type : ${session.type.name} | Durée : ${session.targets.durationMinutes} min
                -------------------------------------------------
                🏋️ LISTE DES EXERCICES & SÉRIES :
                ${session.description}

                💡 CONSEILS D'EXÉCUTION DU COACH :
                ${session.coachNotes}
                =================================================
            """.trimIndent()
        }
    }
}
