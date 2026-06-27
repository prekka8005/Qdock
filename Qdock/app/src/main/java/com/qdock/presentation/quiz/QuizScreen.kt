package com.qdock.presentation.quiz

import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import kotlinx.coroutines.delay
import kotlin.time.Duration.Companion.seconds

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QuizScreen(url: String, onFinished: (Float) -> Unit) {
    var timeLeft by remember { mutableStateOf(90) }
    var isWarning by remember { mutableStateOf(false) }

    LaunchedEffect(timeLeft) {
        if (timeLeft > 0) {
            delay(1.seconds)
            timeLeft--
            if (timeLeft <= 15) isWarning = true
        } else {
            // auto-advance or finish
            onFinished(0.85f)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Quiz Time") },
                actions = {
                    Text(
                        text = "⏱ 0:$timeLeft",
                        color = if (isWarning) Color.Red else MaterialTheme.colorScheme.onSurface,
                        modifier = Modifier.padding(end = 16.dp),
                        style = MaterialTheme.typography.titleLarge
                    )
                }
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding).fillMaxSize()) {
            LinearProgressIndicator(
                progress = timeLeft / 90f,
                modifier = Modifier.fillMaxWidth(),
                color = if (isWarning) Color.Red else MaterialTheme.colorScheme.primary
            )
            AndroidView(
                modifier = Modifier.weight(1f).fillMaxWidth(),
                factory = { context ->
                    WebView(context).apply {
                        settings.apply {
                            javaScriptEnabled = true
                            domStorageEnabled = true
                            loadWithOverviewMode = true
                            useWideViewPort = true
                            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                        }
                        webViewClient = WebViewClient()
                        loadUrl(url)
                    }
                }
            )
            Button(
                onClick = { onFinished(1.0f) },
                modifier = Modifier.fillMaxWidth().padding(16.dp)
            ) {
                Text("Submit & Next")
            }
        }
    }
}
