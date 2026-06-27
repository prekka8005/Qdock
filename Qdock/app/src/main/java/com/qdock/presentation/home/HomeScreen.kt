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
