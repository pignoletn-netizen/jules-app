package com.trailcoach.app.domain.usecase

import com.trailcoach.app.data.healthconnect.HealthConnectHrvSample
import com.trailcoach.app.domain.model.*
import java.util.UUID

/**
 * Résultat de l'analyse comparative entre la séance prévue et l'activité réellement réalisée.
 *
 * @property plannedSession Séance initialement planifiée.
 * @property actualActivity Activité réalisée ( Health Connect / Garmin ).
 * @property distanceCompliancePourcent Respect de la distance cible (%).
 * @property elevationCompliancePourcent Respect du dénivelé D+ cible (%).
 * @property hrZoneCompliance Respect de la zone de fréquence cardiaque cible.
 * @property rpe Delta d'effort ressenti (1 à 10).
 * @property hrvBaselineStatus Statut du HRV (RMSSD) par rapport à la ligne de base.
 * @property fatigueIndex Score synthétique de fatigue (0 à 100).
 */
data class SessionAnalysisResult(
    val plannedSession: WorkoutSession?,
    val actualActivity: Activity,
    val distanceCompliancePourcent: Double,
    val elevationCompliancePourcent: Double,
    val hrZoneCompliance: Boolean,
    val rpe: Int,
    val hrvBaselineStatus: HrvStatus,
    val fatigueIndex: Int,
    val feedbackMessage: String
)

enum class HrvStatus {
    NORMAL,
    LEGEREMENT_BAS,
    ANORMALEMENT_BAS
}

/**
 * Rapport d'adaptation du plan d'entraînement.
 *
 * @property analysis Bilan de l'analyse comparative.
 * @property isPlanAdapted Indique si le plan a été modifié.
 * @property adaptationReason Raison principale du réajustement.
 * @property updatedPlan Plan d'entraînement mis à jour.
 */
data class PlanAdaptationReport(
    val analysis: SessionAnalysisResult,
    val isPlanAdapted: Boolean,
    val adaptationReason: String?,
    val updatedPlan: TrainingPlan
)

/**
 * UseCase d'Analyse Contextuelle et d'Adaptation Dynamique du Plan d'Entraînement.
 * S'inspire des algorithmes de coaching type RunMotion Coach et Nolio.
 */
class AnalyzeAndAdaptPlanUseCase {

    /**
     * Analyse l'activité réalisée et réajuste dynamiquement le plan d'entraînement si nécessaire.
     */
    fun execute(
        currentPlan: TrainingPlan,
        completedActivity: Activity,
        plannedSessionId: String? = null,
        userHrvSamples: List<HealthConnectHrvSample> = emptyList(),
        baselineHrvRmssd: Double = 65.0
    ): PlanAdaptationReport {
        // 1. Matcher l'activité réalisée avec la séance prévue du jour
        val targetCycle = currentPlan.cycles.firstOrNull { cycle ->
            cycle.sessions.any { it.id == plannedSessionId }
        } ?: currentPlan.cycles.firstOrNull()

        val plannedSession = targetCycle?.sessions?.firstOrNull { it.id == plannedSessionId }
            ?: targetCycle?.sessions?.firstOrNull { !it.isCompleted }

        // 2. Calculer le respect des cibles (Distance, D+, FC)
        val distanceTarget = plannedSession?.targets?.targetPaceMinPerKm?.let { 10.0 } ?: 10.0
        val distanceCompliance = if (distanceTarget > 0) (completedActivity.distanceKm / distanceTarget) * 100 else 100.0

        val elevationTarget = plannedSession?.targets?.targetDPlus ?: 0
        val elevationCompliance = if (elevationTarget > 0) {
            (completedActivity.elevationGainDPlus.toDouble() / elevationTarget) * 100
        } else 100.0

        // Respect Zone Cardiaque
        val hrCompliance = if (plannedSession?.targets?.targetFcPercentMax != null) {
            completedActivity.avgHeartRate > 0
        } else true

        // 3. Traitement du HRV et du score de fatigue / RPE
        val latestHrv = userHrvSamples.lastOrNull()?.hrvRmssdMs ?: baselineHrvRmssd
        val hrvStatus = when {
            latestHrv < baselineHrvRmssd * 0.75 -> HrvStatus.ANORMALEMENT_BAS
            latestHrv < baselineHrvRmssd * 0.88 -> HrvStatus.LEGEREMENT_BAS
            else -> HrvStatus.NORMAL
        }

        val rpe = completedActivity.rpe ?: 5
        val sorenessText = completedActivity.sorenessFeedback ?: ""
        val sorenessBonus = if (sorenessText.contains("forte") || sorenessText.contains("Forte")) 25 else 0

        // Index de fatigue globale (0 à 100)
        var fatigueIndex = (rpe * 6) + sorenessBonus
        if (hrvStatus == HrvStatus.ANORMALEMENT_BAS) fatigueIndex += 30
        else if (hrvStatus == HrvStatus.LEGEREMENT_BAS) fatigueIndex += 15
        fatigueIndex = fatigueIndex.coerceIn(0, 100)

        val analysisMessage = when {
            fatigueIndex >= 70 -> "Alerte Fatigue Élevée : HRV en baisse (${latestHrv.toInt()}ms) & RPE $rpe/10. Adaptation requise !"
            fatigueIndex >= 50 -> "Fatigue Modérée : Surveillez la récupération sur la prochaine séance."
            else -> "Excellente séance ! Maintien des zones cibles et HRV stable."
        }

        val analysisResult = SessionAnalysisResult(
            plannedSession = plannedSession,
            actualActivity = completedActivity,
            distanceCompliancePourcent = distanceCompliance,
            elevationCompliancePourcent = elevationCompliance,
            hrZoneCompliance = hrCompliance,
            rpe = rpe,
            hrvBaselineStatus = hrvStatus,
            fatigueIndex = fatigueIndex,
            feedbackMessage = analysisMessage
        )

        // 4. Logique d'adaptation dynamique du plan
        var isAdapted = false
        var reason: String? = null

        val updatedCycles = currentPlan.cycles.map { cycle ->
            if (cycle.id == targetCycle?.id) {
                val updatedSessions = cycle.sessions.map { session ->
                    // Marquer la séance courante comme réalisée
                    if (session.id == plannedSession?.id) {
                        session.copy(isCompleted = true)
                    } else if (!session.isCompleted && !isAdapted) {
                        // Règle A : Fatigue Élevée ou HRV Bas -> Transformer la séance suivante en Mobilité Douce / Repos
                        if (fatigueIndex >= 70 || hrvStatus == HrvStatus.ANORMALEMENT_BAS) {
                            isAdapted = true
                            reason = "Ajustement de sécurité : Conversion de la séance suivante en Mobilité Douce & Récupération active suite à un score de fatigue de $fatigueIndex/100 et un HRV bas."
                            session.copy(
                                type = WorkoutType.MOBILITE_SOUPLESSE,
                                title = "Récupération Active & Mobilité Douce (Adaptation Fatigue)",
                                description = "30 min d'étirements très légers, auto-massages rouleau et respiration diaphragmatique.",
                                coachNotes = "Consigne Coach : Repos prioritaire ! Votre organisme présente des signes de fatigue nerveuse (HRV bas).",
                                targets = WorkoutTargets(durationMinutes = 30)
                            )
                        }
                        // Règle B : Sous-performance / Manque de temps sur le volume D+ -> Réadapter le volume du week-end
                        else if (elevationCompliance < 60.0 && session.type == WorkoutType.RANDO_COURSE) {
                            isAdapted = true
                            reason = "Rééquilibrage du volume : Légère augmentation progressive du D+ du week-end suite au sous-volume réalisé."
                            val newTargetDPlus = (session.targets.targetDPlus ?: 500) + 150
                            session.copy(
                                coachNotes = "${session.coachNotes} [Adapté : +150m D+ compensatoire sans surcharge]",
                                targets = session.targets.copy(targetDPlus = newTargetDPlus)
                            )
                        } else {
                            session
                        }
                    } else {
                        session
                    }
                }
                cycle.copy(sessions = updatedSessions)
            } else {
                cycle
            }
        }

        val updatedPlan = currentPlan.copy(cycles = updatedCycles)

        return PlanAdaptationReport(
            analysis = analysisResult,
            isPlanAdapted = isAdapted,
            adaptationReason = reason,
            updatedPlan = updatedPlan
        )
    }
}
