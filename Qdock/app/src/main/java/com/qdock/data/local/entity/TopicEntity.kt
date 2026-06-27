package com.qdock.data.local.entity

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.ForeignKey.Companion.CASCADE
import androidx.room.PrimaryKey

@Entity(
    tableName = "topics",
    foreignKeys = [ForeignKey(
        entity = LessonEntity::class,
        parentColumns = ["id"],
        childColumns = ["lessonId"],
        onDelete = CASCADE
    )]
)
data class TopicEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val lessonId: Int,
    val name: String,
    val createdAt: Long
)
