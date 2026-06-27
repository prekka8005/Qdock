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
