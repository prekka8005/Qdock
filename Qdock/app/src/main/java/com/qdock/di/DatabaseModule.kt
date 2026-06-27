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
