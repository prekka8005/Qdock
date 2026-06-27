package com.qdock.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "quiz_sessions")
data class QuizSessionEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val quizLinkId: Int,
    val topicId: Int,
    val lessonId: Int,
    val score: Float,            // 0.0 to 1.0
    val timeTakenSeconds: Int,
    val completedAt: Long
)
