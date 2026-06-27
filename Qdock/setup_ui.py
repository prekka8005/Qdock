import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content.strip() + '\n')

def setup_ui():
    base_pkg = 'app/src/main/java/com/qdock'

    # HomeViewModel
    create_file(f'{base_pkg}/presentation/home/HomeViewModel.kt', """
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
""")

    # HomeScreen
    create_file(f'{base_pkg}/presentation/home/HomeScreen.kt', """
package com.qdock.presentation.home

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToLesson: (Int) -> Unit,
    viewModel: HomeViewModel = hiltViewModel()
) {
    val lessons by viewModel.lessons.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("QDock") })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { viewModel.addLesson("New Lesson", "📘", "#6750A4") }) {
                Icon(Icons.Default.Add, contentDescription = "Add Lesson")
            }
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding).fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(lessons) { lesson ->
                Card(onClick = { onNavigateToLesson(lesson.id) }, modifier = Modifier.fillMaxWidth()) {
                    Row(modifier = Modifier.padding(16.dp)) {
                        Text(text = lesson.iconEmoji, style = MaterialTheme.typography.headlineSmall)
                        Spacer(modifier = Modifier.width(16.dp))
                        Text(text = lesson.name, style = MaterialTheme.typography.titleMedium)
                    }
                }
            }
        }
    }
}
""")

if __name__ == '__main__':
    setup_ui()
    print("UI Phase generated successfully.")
