package com.qdock.data.local.entity

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.ForeignKey.Companion.CASCADE
import androidx.room.PrimaryKey

@Entity(
    tableName = "quiz_links",
    foreignKeys = [ForeignKey(
        entity = TopicEntity::class,
        parentColumns = ["id"],
        childColumns = ["topicId"],
        onDelete = CASCADE
    )]
)
data class QuizLinkEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val topicId: Int,
    val title: String,
    val url: String,             // Google Form URL
    val addedAt: Long
)
