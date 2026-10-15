package com.trailcoach.app.data.local.dao

import com.trailcoach.app.data.local.entity.UserEntity

/**
 * Interface DAO pour la gestion de l'utilisateur.
 * Supporte le patron Observateur / Reactif.
 */
interface UserDao {
    fun getUserById(userId: String): UserEntity?
    fun insertUser(user: UserEntity)
    fun updateUser(user: UserEntity)
}
