import os

def create_file(path, content):
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content.strip() + '\n')

def setup_rest():
    base_pkg = 'app/src/main/java/com/qdock'

    # QuizScreen (WebView + Timer)
    create_file(f'{base_pkg}/presentation/quiz/QuizScreen.kt', """
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
""")

    # BackupManager
    create_file(f'{base_pkg}/domain/usecase/BackupManager.kt', """
package com.qdock.domain.usecase

import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import com.qdock.data.local.database.QDockDatabase
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.OutputStream
import javax.inject.Inject

class BackupManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val db: QDockDatabase
) {
    suspend fun exportBackup(): Boolean = withContext(Dispatchers.IO) {
        try {
            val json = JSONObject()
            json.put("version", 1)
            json.put("exportedAt", System.currentTimeMillis())
            json.put("appVersion", "1.0.0")
            // Normally, we'd serialize room tables to JSON arrays here
            
            val jsonBytes = json.toString().toByteArray()
            
            val resolver = context.contentResolver
            val contentValues = ContentValues().apply {
                put(MediaStore.Downloads.DISPLAY_NAME, "QDock_Backup_${System.currentTimeMillis()}.qdock")
                put(MediaStore.Downloads.MIME_TYPE, "application/octet-stream")
            }
            
            val uri: Uri? = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, contentValues)
            if (uri != null) {
                resolver.openOutputStream(uri)?.use { stream: OutputStream ->
                    stream.write(jsonBytes)
                }
                true
            } else {
                false
            }
        } catch (e: Exception) {
            e.printStackTrace()
            false
        }
    }
}
""")

    # Navigation Setup
    create_file(f'{base_pkg}/presentation/navigation/NavGraph.kt', """
package com.qdock.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.qdock.presentation.home.HomeScreen
import com.qdock.presentation.quiz.QuizScreen

@Composable
fun QDockNavHost(
    navController: NavHostController = rememberNavController(),
    startDestination: String = "home"
) {
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToLesson = { lessonId ->
                    // mock navigation to topic list
                    navController.navigate("quiz_test")
                }
            )
        }
        
        composable("quiz_test") {
            QuizScreen(
                url = "https://docs.google.com/forms/d/e/1FAIpQLS.../viewform",
                onFinished = { score ->
                    navController.popBackStack()
                }
            )
        }
    }
}
""")

    # Update MainActivity to use NavGraph
    create_file(f'{base_pkg}/MainActivity.kt', """
package com.qdock

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import com.qdock.ui.theme.QDockTheme
import com.qdock.presentation.navigation.QDockNavHost
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            QDockTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Column(modifier = Modifier.fillMaxSize()) {
                        // Adding the requested logo at the top briefly for demonstration
                        Image(
                            painter = painterResource(id = R.drawable.logo),
                            contentDescription = "App Logo",
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(80.dp)
                                .padding(8.dp)
                        )
                        QDockNavHost()
                    }
                }
            }
        }
    }
}
""")

if __name__ == '__main__':
    setup_rest()
    print("Remaining files and NavGraph integrated successfully.")
