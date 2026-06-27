package com.qdock.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.qdock.data.local.dao.LessonDao
import com.qdock.data.local.entity.LessonEntity
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val lessonDao: LessonDao
) : ViewModel() {
    val lessons = lessonDao.getAllLessons()
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun addLesson(name: String, emoji: String, color: String) {
        viewModelScope.launch {
            lessonDao.insertLesson(
                LessonEntity(
                    name = name,
                    iconEmoji = emoji,
                    colorHex = color,
                    createdAt = System.currentTimeMillis()
                )
            )
        }
    }
}
