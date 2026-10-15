package com.trailcoach.app.domain.usecase

import com.trailcoach.app.domain.model.*
import java.util.UUID

/**
 * UseCase de génération automatique de plan d'entraînement Trail & Ultra-Trail sur-mesure.
 *
 * S'inspire de la méthodologie de coachs réputés (Mathieu Blanchard, Pascal Balducci, Guillaume Millet) :
 * 1. Périodisation en 4 phases distinctes :
 *    - Phase 1 : Foncière & Mobilité (Développement VMA, PPG de base, mobilité chevilles/hanches)
 *    - Phase 2 : Spécifique Trail (Côtes, renforcement excentrique pour la descente, Rando-Course avec bâtons)
 *    - Phase 3 : Affinage & Test Matériel (Sorties longues avec sac chargé / nutrition de course)
 *    - Phase 4 : Affûtage (Tapering) & Mobilité douce (Baisse du volume de 50%, maintien de l'intensité)
 *
 * 2. Structure hebdomadaire type :
 *    - 2 à 4 séances de Course / Trail (VMA, Seuil, Endurance, Rando-Course D+/D-)
 *    - 1 à 2 séances de Renforcement Musculaire Trail : Exercices excentriques (quadriceps/psoas), gainage dynamique 3D, mollets/proprioception.
 *    - 2 à 3 sessions de Mobilité & Souplesse (15 min) : Déverrouillage hanches/moyen fessier, mobilité chaîne postérieure, soulagement lombaires.
 */
class GenerateTrainingPlanUseCase {

    /**
     * Génère un plan d'entraînement structuré et individualisé de [startDateMillis] jusqu'à la date de [goal].
     */
    fun execute(
        user: User,
        goal: Goal,
        startDateMillis: Long = System.currentTimeMillis()
    ): TrainingPlan {
        val totalDays = ((goal.raceDate - startDateMillis) / (1000 * 3600 * 24)).toInt().coerceAtLeast(14)
        val totalWeeks = (totalDays / 7).coerceAtLeast(2)

        // Découpage en 4 phases de périodisation
        val fonciereWeeks = (totalWeeks * 0.35).toInt().coerceAtLeast(1)
        val specifiqueWeeks = (totalWeeks * 0.40).toInt().coerceAtLeast(1)
        val affinageWeeks = (totalWeeks * 0.15).toInt().coerceAtLeast(1)
        val affutageWeeks = (totalWeeks - (fonciereWeeks + specifiqueWeeks + affinageWeeks)).coerceAtLeast(1)

        val cycles = mutableListOf<TrainingCycle>()

        var currentWeekStart = startDateMillis
        val millisInWeek = 7L * 24 * 3600 * 1000

        // Phase 1 : Foncière & Mobilité
        val cycle1Sessions = generatePhaseSessions(
            phase = CycleType.DEVELOPPEMENT_GENERAL,
            weeksCount = fonciereWeeks,
            user = user,
            goal = goal
        )
        val cycle1End = currentWeekStart + (fonciereWeeks * millisInWeek)
        cycles.add(
            TrainingCycle(
                id = UUID.randomUUID().toString(),
                name = "Phase 1 : Foncière & Mobilité ($fonciereWeeks semaines)",
                type = CycleType.DEVELOPPEMENT_GENERAL,
                startTimestamp = currentWeekStart,
                endTimestamp = cycle1End,
                targetTrimp = fonciereWeeks * 250.0,
                sessions = cycle1Sessions
            )
        )
        currentWeekStart = cycle1End

        // Phase 2 : Spécifique Trail (Côtes & Excentrique)
        val cycle2Sessions = generatePhaseSessions(
            phase = CycleType.SPECIFIQUE_TRAIL,
            weeksCount = specifiqueWeeks,
            user = user,
            goal = goal
        )
        val cycle2End = currentWeekStart + (specifiqueWeeks * millisInWeek)
        cycles.add(
            TrainingCycle(
                id = UUID.randomUUID().toString(),
                name = "Phase 2 : Spécifique Trail & Excentrique ($specifiqueWeeks semaines)",
                type = CycleType.SPECIFIQUE_TRAIL,
                startTimestamp = currentWeekStart,
                endTimestamp = cycle2End,
                targetTrimp = specifiqueWeeks * 380.0,
                sessions = cycle2Sessions
            )
        )
        currentWeekStart = cycle2End

        // Phase 3 : Affinage & Test Matériel
        val cycle3Sessions = generatePhaseSessions(
            phase = CycleType.AFFUTAGE, // Utilisation de la catégorie d'affinage / pré-course
            weeksCount = affinageWeeks,
            user = user,
            goal = goal
        )
        val cycle3End = currentWeekStart + (affinageWeeks * millisInWeek)
        cycles.add(
            TrainingCycle(
                id = UUID.randomUUID().toString(),
                name = "Phase 3 : Affinage & Test Matériel/Nutrition ($affinageWeeks semaines)",
                type = CycleType.AFFUTAGE,
                startTimestamp = currentWeekStart,
                endTimestamp = cycle3End,
                targetTrimp = affinageWeeks * 300.0,
                sessions = cycle3Sessions
            )
        )
        currentWeekStart = cycle3End

        // Phase 4 : Affûtage (Tapering) & Mobilité douce
        val cycle4Sessions = generatePhaseSessions(
            phase = CycleType.RECUPERATION,
            weeksCount = affutageWeeks,
            user = user,
            goal = goal
        )
        val cycle4End = currentWeekStart + (affutageWeeks * millisInWeek)
        cycles.add(
            TrainingCycle(
                id = UUID.randomUUID().toString(),
                name = "Phase 4 : Affûtage (Tapering) & Mobilité Douce ($affutageWeeks semaines)",
                type = CycleType.RECUPERATION,
                startTimestamp = currentWeekStart,
                endTimestamp = cycle4End,
                targetTrimp = affutageWeeks * 140.0,
                sessions = cycle4Sessions
            )
        )

        val totalDPlus = goal.elevationGainDPlus
        val totalDMinus = goal.elevationLossDMinus

        return TrainingPlan(
            id = UUID.randomUUID().toString(),
            userId = user.id,
            goalId = goal.id,
            cycles = cycles,
            trimpLoad = (totalWeeks * 280.0),
            tssLoad = (totalWeeks * 240.0),
            volumeDistribution = VolumeDistribution(
                totalDPlusMeters = totalDPlus,
                totalDMinusMeters = totalDMinus,
                ppgRatioPourcent = 25.0,
                mobilityRatioPourcent = 15.0
            )
        )
    }

    private fun generatePhaseSessions(
        phase: CycleType,
        weeksCount: Int,
        user: User,
        goal: Goal
    ): List<WorkoutSession> {
        val sessions = mutableListOf<WorkoutSession>()

        for (week in 1..weeksCount) {
            when (phase) {
                CycleType.DEVELOPPEMENT_GENERAL -> {
                    // Course VMA
                    sessions.add(
                        WorkoutSession(
                            id = UUID.randomUUID().toString(),
                            type = WorkoutType.VMA_COURTE,
                            title = "VMA Courte - Piste / Plat (Semaine $week)",
                            description = "Échauffement 20 min + 2 séries de (10x 30'' vite / 30'' lent) r=3' + Récupération 10 min",
                            coachNotes = "Consigne Coach : Cible VMA=${user.vma} km/h. Conserve une foulée dynamique au ras du sol.",
                            targets = WorkoutTargets(
                                targetFcPercentMax = 90..98,
                                targetPaceMinPerKm = "3:30 - 3:45",
                                durationMinutes = 50
                            )
                        )
                    )
                    // PPG de base
                    sessions.add(generateExcentricWorkout(week = week, isHardPhase = false))
                    // Endurance fondamentale
                    sessions.add(
                        WorkoutSession(
                            id = UUID.randomUUID().toString(),
                            type = WorkoutType.ENDURANCE_FONDAMENTALE,
                            title = "Endurance Fondamentale & Relâchement (Semaine $week)",
                            description = "Footing continu 1h15 à aisance respiratoire stricte.",
                            coachNotes = "Consigne Coach : Reste strictement sous 75% FCmax (${(user.fcMax * 0.75).toInt()} bpm).",
                            targets = WorkoutTargets(
                                targetFcPercentMax = 65..75,
                                durationMinutes = 75
                            )
                        )
                    )
                    // Session Mobilité
                    sessions.add(generateMobilityWorkout(week = week, soft = false))
                }

                CycleType.SPECIFIQUE_TRAIL -> {
                    // VMA Côte / D+
                    sessions.add(
                        WorkoutSession(
                            id = UUID.randomUUID().toString(),
                            type = WorkoutType.VMA_COTE,
                            title = "VMA Côte & Relance Sommet (Semaine $week)",
                            description = "Échauffement 20' + 8 à 10 répétitions de 1'30 en côte à 8-12% + descente trottoir + 30'' relance à plat.",
                            coachNotes = "Consigne Coach : Pousse fort sur les cuisses, monte le genou et relance immédiatement au sommet.",
                            targets = WorkoutTargets(
                                targetFcPercentMax = 88..95,
                                targetDPlus = 400,
                                durationMinutes = 65
                            )
                        )
                    )
                    // Renforcement Excentrique (Méthode Mathieu Blanchard / Casse musculaire)
                    sessions.add(generateExcentricWorkout(week = week, isHardPhase = true))
                    // Rando-Course bâtons
                    sessions.add(
                        WorkoutSession(
                            id = UUID.randomUUID().toString(),
                            type = WorkoutType.RANDO_COURSE,
                            title = "Rando-Course Bâtons D+ / D- (Semaine $week)",
                            description = "Sortie longue trail 2h30 à 3h30. Marche rapide avec bâtons dès que la pente dépasse 8%, course dynamique en descente.",
                            coachNotes = "Consigne Coach (Ultra-Trail) : Pratique le planté de bâtons synchronisé. Ne bloque pas la respiration dans les montées stiff.",
                            targets = WorkoutTargets(
                                targetFcPercentMax = 70..82,
                                targetDPlus = (goal.elevationGainDPlus / 5).coerceAtLeast(600),
                                durationMinutes = 180
                            )
                        )
                    )
                    // Travail spécifique descente
                    sessions.add(
                        WorkoutSession(
                            id = UUID.randomUUID().toString(),
                            type = WorkoutType.TRAVAIL_DESCENTE,
                            title = "Technique Descente & Casse Musculaire (Semaine $week)",
                            description = "5 répétitions de 300m D- en descente technique. Regard porté à 5 mètres devant, appuis légers et rapides.",
                            coachNotes = "Consigne Coach : Laisse courir le bassin, ne freine pas exagérément avec les talons pour épargner le dos.",
                            targets = WorkoutTargets(
                                durationMinutes = 45
                            )
                        )
                    )
                    // Session Mobilité
                    sessions.add(generateMobilityWorkout(week = week, soft = false))
                }

                CycleType.AFFUTAGE -> {
                    // Sortie Longue & Test Matériel
                    sessions.add(
                        WorkoutSession(
                            id = UUID.randomUUID().toString(),
                            type = WorkoutType.RANDO_COURSE,
                            title = "Sortie Longue Test Matériel & Nutrition (Semaine $week)",
                            description = "Sortie longue 3h avec sac de course chargé (matériel obligatoire ${goal.raceName}) + test des gels/poudres.",
                            coachNotes = "Consigne Coach : Bois 500ml/h minimum et ingère 40g à 60g de glucides par heure. Pas d'expérimentation le jour J !",
                            targets = WorkoutTargets(
                                targetFcPercentMax = 68..78,
                                targetDPlus = 800,
                                durationMinutes = 180
                            )
                        )
                    )
                    // Renforcement léger
                    sessions.add(generateExcentricWorkout(week = week, isHardPhase = false))
                    // Mobilité
                    sessions.add(generateMobilityWorkout(week = week, soft = true))
                }

                CycleType.RECUPERATION -> {
                    // Affûtage (Tapering)
                    sessions.add(
                        WorkoutSession(
                            id = UUID.randomUUID().toString(),
                            type = WorkoutType.ENDURANCE_FONDAMENTALE,
                            title = "Rappel d'Intensité Court (Tapering Semaine $week)",
                            description = "Footing 35 min comprenant 4x 30'' accélérations progressives à allure course.",
                            coachNotes = "Consigne Coach : Ne fatigue pas l'organisme, le travail est fait. Garde du jus et du peps.",
                            targets = WorkoutTargets(
                                targetFcPercentMax = 65..75,
                                durationMinutes = 35
                            )
                        )
                    )
                    // Mobilité douce
                    sessions.add(generateMobilityWorkout(week = week, soft = true))
                    // Repos
                    sessions.add(
                        WorkoutSession(
                            id = UUID.randomUUID().toString(),
                            type = WorkoutType.REPOS,
                            title = "Repos Complexe & Hydratation",
                            description = "Repos complet, massage au rouleau léger et sommeil réparateur.",
                            coachNotes = "Consigne Coach : Hydrate-toi abondamment et recharge tes stocks de glycogène.",
                            targets = WorkoutTargets(durationMinutes = 0)
                        )
                    )
                }
            }
        }

        return sessions
    }

    /**
     * Génère une séance de Renforcement Musculaire Trail axée sur le travail excentrique et le gainage 3D.
     */
    private fun generateExcentricWorkout(week: Int, isHardPhase: Boolean): WorkoutSession {
        val series = if (isHardPhase) 4 else 3
        val reps = if (isHardPhase) 12 else 8

        return WorkoutSession(
            id = UUID.randomUUID().toString(),
            type = WorkoutType.RENFORCEMENT_EXCENTRIQUE,
            title = "Renforcement Excentrique Quadris & Gainage 3D (S$week)",
            description = """
                Exercices obligatoires Trail :
                1. Squats Sautés Excentriques : $series séries x $reps réps (Descente contrôlée sur 4 secondes, saut explosif).
                2. Fentes Arrière Pliométriques : $series séries x 10 réps par jambe.
                3. Chaise Excentrique à 1 Jambe : $series séries x 30 secondes par jambe.
                4. Mollets sur Marche (Soleaires/Gastrocnémiens) : $series séries x 15 réps (Freinement 5s à la descente).
                5. Gainage Dynamique 3D (Planche avec élévation alternative bras/jambe) : $series séries x 45 secondes.
            """.trimIndent(),
            coachNotes = "Consigne Coach : L'excentrique prépare vos quadriceps aux contraintes des 5000m+ de D- de l'Ultra. Contrôlez toujours la phase de descente !",
            targets = WorkoutTargets(durationMinutes = 45)
        )
    }

    /**
     * Génère une session de Mobilité & Souplesse (15 min) pour le déverrouillage des hanches, chevilles et lombaires.
     */
    private fun generateMobilityWorkout(week: Int, soft: Boolean): WorkoutSession {
        return WorkoutSession(
            id = UUID.randomUUID().toString(),
            type = WorkoutType.MOBILITE_SOUPLESSE,
            title = "Routine Mobilité Hanches, Chevilles & Lombaires 15min (S$week)",
            description = """
                Routine 15 minutes :
                1. Déverrouillage des hanches en 90/90 : 2 x 1 minute de chaque côté.
                2. Mobilité de cheville contre mur (Dorsiflexion pour la montée) : 2 x 10 balayages lent.
                3. Étirement de la chaîne postérieure (Chiens tête en bas & Psoas chevalier) : 3 x 45 secondes.
                4. Décompression des lombaires (Posture de l'enfant) : 3 minutes en respiration profonde.
            """.trimIndent(),
            coachNotes = if (soft) "Consigne Coach : Routine très douce. Relâchement total des tensions." else "Consigne Coach : Augmente la mobilité de vos hanches pour fluidifier le pas en montée.",
            targets = WorkoutTargets(durationMinutes = 15)
        )
    }
}
