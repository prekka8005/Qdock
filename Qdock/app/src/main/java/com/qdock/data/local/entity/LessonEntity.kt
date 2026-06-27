package com.qdock.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "lessons")
data class LessonEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val name: String,
    val iconEmoji: String,       // e.g. "📘"
    val colorHex: String,        // card accent color
    val createdAt: Long,
    val totalQuizzes: Int = 0,
    val completedQuizzes: Int = 0,
    val successRate: Float = 0f  // 0.0 to 1.0
)
