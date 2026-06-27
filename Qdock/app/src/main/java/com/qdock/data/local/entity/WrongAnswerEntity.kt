package com.qdock.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "wrong_answers")
data class WrongAnswerEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val sessionId: Int,
    val lessonId: Int,
    val topicId: Int,
    val question: String,
    val userAnswer: String,
    val correctAnswer: String,
    val savedAt: Long
)
