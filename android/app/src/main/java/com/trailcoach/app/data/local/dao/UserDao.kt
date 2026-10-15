package com.trailcoach.app.data.local.dao

import com.trailcoach.app.data.local.entity.UserEntity

/**
 * Interface DAO pour la gestion de l'utilisateur.
 * Utilise Kotlin `Flow` pour la réactivité avec l'UI (Jetpack Compose).
 */
interface UserDao {
    fun getUserById(userId: String): UserEntity?
    fun insertUser(user: UserEntity)
    fun updateUser(user: UserEntity)
}
