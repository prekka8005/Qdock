package com.qdock.data.local.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.qdock.data.local.dao.LessonDao
import com.qdock.data.local.dao.TopicDao
import com.qdock.data.local.entity.LessonEntity
import com.qdock.data.local.entity.QuizLinkEntity
import com.qdock.data.local.entity.QuizSessionEntity
import com.qdock.data.local.entity.TopicEntity
import com.qdock.data.local.entity.WrongAnswerEntity

@Database(
    entities = [
        LessonEntity::class,
        TopicEntity::class,
        QuizLinkEntity::class,
        QuizSessionEntity::class,
        WrongAnswerEntity::class
    ],
    version = 1,
    exportSchema = false
)
abstract class QDockDatabase : RoomDatabase() {
    abstract val lessonDao: LessonDao
    abstract val topicDao: TopicDao
}
