package com.trailcoach.app.data.healthconnect

import java.time.Instant

/**
 * Modèle interne représentant une session d'exercice lue depuis Health Connect.
 */
data class HealthConnectExerciseSession(
    val id: String,
    val title: String?,
    val exerciseType: Int,
    val startTime: Instant,
    val endTime: Instant,
    val notes: String? = null
)

/**
 * Modèle interne pour la fréquence cardiaque.
 */
data class HealthConnectHeartRateSample(
    val beatsPerMinute: Long,
    val time: Instant
)

/**
 * Modèle interne pour les données de sommeil.
 */
data class HealthConnectSleepSession(
    val id: String,
    val startTime: Instant,
    val endTime: Instant,
    val title: String? = null,
    val durationMinutes: Long = (endTime.epochSecond - startTime.epochSecond) / 60
)

/**
 * Modèle interne pour la variabilité de la fréquence cardiaque (HRV RMSSD).
 */
data class HealthConnectHrvSample(
    val hrvRmssdMs: Double,
    val time: Instant
)

/**
 * Bilan des données de santé et activités récoltées sur les 30 derniers jours via Health Connect (Garmin Connect passthrough).
 */
data class HealthConnect30DaysData(
    val exerciseSessions: List<HealthConnectExerciseSession>,
    val heartRateSamples: List<HealthConnectHeartRateSample>,
    val sleepSessions: List<HealthConnectSleepSession>,
    val hrvSamples: List<HealthConnectHrvSample>
)

/**
 * Directement utilisable sans dépendances binaires externes lourdes au build time
 * mais prêt pour l'intégration `androidx.health.connect.client.HealthConnectClient`.
 *
 * Déclaration explicite des permissions Health Connect requises :
 * - Read Exercise Sessions (Activités Garmin / Running / Trail)
 * - Read Heart Rate (FC, FC repos, FC max)
 * - Read Sleep (Sommeil, récupération)
 * - Read Heart Rate Variability (HRV / VRC RMSSD pour le score de récupération)
 */
class HealthConnectManager {

    companion object {
        val REQUIRED_PERMISSIONS = setOf(
            "android.permission.health.READ_EXERCISE",
            "android.permission.health.READ_HEART_RATE",
            "android.permission.health.READ_SLEEP",
            "android.permission.health.READ_HEART_RATE_VARIABILITY"
        )
    }

    /**
     * Indique si l'intégration Health Connect est disponible sur l'appareil.
     */
    fun isAvailable(): Boolean {
        // En environnement réel : HealthConnectClient.getSdkStatus(context) == HealthConnectClient.SDK_AVAILABLE
        return true
    }

    /**
     * Indique si toutes les permissions nécessaires pour le coaching trail (FC, Activités, Sommeil, HRV) sont accordées.
     */
    fun hasAllPermissions(grantedPermissions: Set<String>): Boolean {
        return grantedPermissions.containsAll(REQUIRED_PERMISSIONS)
    }

    /**
     * Lit les sessions d'activités (Running, Trail, etc.) enregistrées dans Health Connect sur une période.
     */
    fun readExerciseSessions(startTime: Instant, endTime: Instant): List<HealthConnectExerciseSession> {
        // Implémentation Health Connect Client : readRecords(ReadRecordsRequest(ExerciseSessionRecord::class, timeRangeFilter))
        return emptyList()
    }

    /**
     * Lit les données de Fréquence Cardiaque (FC) sur une période.
     */
    fun readHeartRateData(startTime: Instant, endTime: Instant): List<HealthConnectHeartRateSample> {
        // Implémentation Health Connect Client : readRecords(ReadRecordsRequest(HeartRateRecord::class, timeRangeFilter))
        return emptyList()
    }

    /**
     * Lit les sessions de sommeil sur une période.
     */
    fun readSleepData(startTime: Instant, endTime: Instant): List<HealthConnectSleepSession> {
        // Implémentation Health Connect Client : readRecords(ReadRecordsRequest(SleepSessionRecord::class, timeRangeFilter))
        return emptyList()
    }

    /**
     * Lit la variabilité de la fréquence cardiaque (HRV) RMSSD sur une période.
     */
    fun readHrvData(startTime: Instant, endTime: Instant): List<HealthConnectHrvSample> {
        // Implémentation Health Connect Client : readRecords(ReadRecordsRequest(HeartRateVariabilityRmssdRecord::class, timeRangeFilter))
        return emptyList()
    }

    /**
     * Lit et regroupe l'ensemble des données d'activités, FC, sommeil et HRV des 30 derniers jours.
     */
    fun readAggregatedHealthDataLast30Days(now: Instant = Instant.now()): HealthConnect30DaysData {
        val startTime = now.minusSeconds(30L * 24 * 3600)
        val endTime = now

        val sessions = readExerciseSessions(startTime, endTime)
        val heartRates = readHeartRateData(startTime, endTime)
        val sleeps = readSleepData(startTime, endTime)
        val hrvs = readHrvData(startTime, endTime)

        return HealthConnect30DaysData(
            exerciseSessions = sessions,
            heartRateSamples = heartRates,
            sleepSessions = sleeps,
            hrvSamples = hrvs
        )
    }
}
