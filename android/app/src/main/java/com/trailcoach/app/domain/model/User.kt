package com.trailcoach.app.domain.model

/**
 * Niveau de l'athlète en trail & ultra-trail.
 */
enum class TrailLevel {
    DEBUTANT,
    INTERMEDIAIRE,
    CONFIRME,
    EXPERT_ULTRA
}

/**
 * Disponibilités hebdomadaires en heures et jours de la semaine.
 *
 * @property runningHours Volume horaire hebdomadaire réservé à la course / trail (ex: 6.5h).
 * @property ppgHours Volume horaire réservé à la Préparation Physique Générale / renforcement (ex: 2.0h).
 * @property mobilityHours Volume horaire réservé à la mobilité et étirements (ex: 1.5h).
 * @property availableDays Jours de la semaine disponibles (ex: setOf("LUNDI", "MERCREDI", "SAMEDI", "DIMANCHE")).
 */
data class WeeklyAvailability(
    val runningHours: Double = 0.0,
    val ppgHours: Double = 0.0,
    val mobilityHours: Double = 0.0,
    val availableDays: Set<String> = emptySet()
)

/**
 * Profil de l'utilisateur / athlète.
 *
 * @property id Identifiant unique de l'utilisateur.
 * @property name Nom / Prénom de l'athlète.
 * @property age Âge de l'utilisateur en années.
 * @property weightKg Poids en kilogrammes.
 * @property vma Vitesse Maximale Aérobie en km/h.
 * @property fcMax Fréquence Cardiaque Maximale en bpm.
 * @property fcRepos Fréquence Cardiaque de Repos en bpm.
 * @property trailLevel Niveau de pratique du trail.
 * @property weeklyAvailability Disponibilités hebdomadaires détaillées (running, PPG, mobilité).
 */
data class User(
    val id: String,
    val name: String,
    val age: Int,
    val weightKg: Double,
    val vma: Double,
    val fcMax: Int,
    val fcRepos: Int = 50,
    val trailLevel: TrailLevel = TrailLevel.INTERMEDIAIRE,
    val weeklyAvailability: WeeklyAvailability = WeeklyAvailability()
)
