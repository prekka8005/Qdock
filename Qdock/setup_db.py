import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content.strip() + '\n')

def setup_db():
    base_pkg = 'app/src/main/java/com/qdock'
    
    # LessonEntity
    create_file(f'{base_pkg}/data/local/entity/LessonEntity.kt', """
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
""")

    # TopicEntity
    create_file(f'{base_pkg}/data/local/entity/TopicEntity.kt', """
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
""")

    # QuizLinkEntity
    create_file(f'{base_pkg}/data/local/entity/QuizLinkEntity.kt', """
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
""")

    # QuizSessionEntity
    create_file(f'{base_pkg}/data/local/entity/QuizSessionEntity.kt', """
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
""")

    # WrongAnswerEntity
    create_file(f'{base_pkg}/data/local/entity/WrongAnswerEntity.kt', """
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
""")

    # LessonDao
    create_file(f'{base_pkg}/data/local/dao/LessonDao.kt', """
package com.qdock.data.local.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.qdock.data.local.entity.LessonEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface LessonDao {
    @Query("SELECT * FROM lessons ORDER BY createdAt DESC")
    fun getAllLessons(): Flow<List<LessonEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertLesson(lesson: LessonEntity)

    @Update
    suspend fun updateLesson(lesson: LessonEntity)

    @Delete
    suspend fun deleteLesson(lesson: LessonEntity)
}
""")

    # TopicDao
    create_file(f'{base_pkg}/data/local/dao/TopicDao.kt', """
package com.qdock.data.local.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.qdock.data.local.entity.TopicEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface TopicDao {
    @Query("SELECT * FROM topics WHERE lessonId = :lessonId ORDER BY createdAt ASC")
    fun getTopicsByLesson(lessonId: Int): Flow<List<TopicEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTopic(topic: TopicEntity)

    @Delete
    suspend fun deleteTopic(topic: TopicEntity)
}
""")

    # QDockDatabase
    create_file(f'{base_pkg}/data/local/database/QDockDatabase.kt', """
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
""")

    # DatabaseModule
    create_file(f'{base_pkg}/di/DatabaseModule.kt', """
package com.qdock.di

import android.app.Application
import androidx.room.Room
import com.qdock.data.local.database.QDockDatabase
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideQDockDatabase(app: Application): QDockDatabase {
        return Room.databaseBuilder(
            app,
            QDockDatabase::class.java,
            "qdock_db"
        ).build()
    }

    @Provides
    @Singleton
    fun provideLessonDao(db: QDockDatabase) = db.lessonDao

    @Provides
    @Singleton
    fun provideTopicDao(db: QDockDatabase) = db.topicDao
}
""")

if __name__ == '__main__':
    setup_db()
    print("Database phase generated successfully.")
