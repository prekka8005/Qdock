# QDock — Full Android Project Plan
### Quiz Practice App | Kotlin + Jetpack Compose + Room + Material 3

---

## 1. PROJECT OVERVIEW

| Field | Detail |
|---|---|
| App Name | QDock |
| Platform | Android (minSdk 26 / Android 8.0+) |
| Target SDK | 35 (Android 15) |
| Language | Kotlin 2.0 |
| UI Framework | Jetpack Compose (BOM 2024.09.00) |
| Architecture | MVVM + Clean Architecture |
| Theme | Material 3 — Purple seed (#6750A4) |
| Build Tool | Gradle (Kotlin DSL) |

---

## 2. ARCHITECTURE OVERVIEW

```
app/
├── data/
│   ├── local/
│   │   ├── database/        ← Room DB
│   │   ├── dao/             ← DAOs for each entity
│   │   └── entity/          ← Room entities
│   ├── repository/          ← Repository implementations
│   └── model/               ← Data models
│
├── domain/
│   ├── model/               ← Domain models (pure Kotlin)
│   ├── repository/          ← Repository interfaces
│   └── usecase/             ← Business logic use cases
│
├── presentation/
│   ├── home/                ← Home screen (Lessons list)
│   ├── lesson/              ← Add/Edit Lesson screen
│   ├── topic/               ← Topic list screen
│   ├── quiz/                ← Quiz WebView screen
│   ├── result/              ← Quiz result screen
│   ├── history/             ← History tab screen
│   └── components/          ← Shared Composables
│
├── ui/
│   ├── theme/               ← Color, Typography, Theme.kt
│   └── animation/           ← Custom animations
│
└── di/
    └── AppModule.kt         ← Hilt dependency injection
```

**Pattern:** MVVM (ViewModel → UseCase → Repository → Room DAO)

---

## 3. DATABASE DESIGN (Room)

### Entities

#### `LessonEntity`
```kotlin
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
```

#### `TopicEntity`
```kotlin
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
```

#### `QuizLinkEntity`
```kotlin
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
```

#### `QuizSessionEntity`
```kotlin
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
```

#### `WrongAnswerEntity`
```kotlin
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
```

---

## 4. SCREENS & NAVIGATION

### Navigation Graph
```
NavHost
├── HomeScreen          (route: "home")
│   └── BottomNav
│       ├── LessonsTab  (default)
│       └── HistoryTab
├── AddLessonScreen     (route: "add_lesson")
├── EditLessonScreen    (route: "edit_lesson/{lessonId}")
├── TopicListScreen     (route: "topics/{lessonId}")
├── AddTopicScreen      (route: "add_topic/{lessonId}")
├── QuizListScreen      (route: "quiz_list/{topicId}")
├── AddQuizScreen       (route: "add_quiz/{topicId}")
├── QuizScreen          (route: "quiz/{quizLinkId}")
├── QuizResultScreen    (route: "result/{sessionId}")
├── WrongAnswerDetail   (route: "wrong_detail/{sessionId}")
└── SettingsScreen      (route: "settings")
```

---

## 5. SCREEN-BY-SCREEN DESIGN

### 5.1 Home Screen — Lessons Tab
- Top bar: "QDock" logo + search icon
- Floating streak badge: 🔥 Day streak counter
- Lesson cards (LazyColumn):
  - Emoji icon + Lesson name
  - Progress bar (animated, colored by success rate)
  - Topic count badge
  - Swipe-to-delete with undo snackbar
- FAB: + Add Lesson (animated expand)

**Progress bar color logic:**
```kotlin
fun progressColor(rate: Float): Color = when {
    rate < 0.30f -> Color(0xFFE53935)  // Red
    rate < 0.70f -> Color(0xFFFDD835)  // Yellow
    else         -> Color(0xFF43A047)  // Green
}
```

---

### 5.2 History Tab
- Grouped list: Lesson → Topic → Date
- Each session card:
  - Score chip (colored)
  - Time taken
  - Wrong answer count
  - "Review Mistakes" button
- Empty state: animated illustration + "No quiz history yet"

---

### 5.3 Add Lesson Screen
- Text field: Lesson name
- Emoji picker grid (built-in, no library)
- Color accent picker (6 preset colors)
- Save button with ripple animation

---

### 5.4 Topic List Screen
- Lesson header card at top
- Topic list with quiz count per topic
- FAB: + Add Topic
- Tap topic → Quiz List Screen

---

### 5.5 Quiz List Screen
- Topic name header
- List of added Google Form quizzes
- Each quiz card: title + date added + "Start" button
- FAB: + Add Quiz (paste Google Form URL)
- URL validation: must contain `docs.google.com/forms`

---

### 5.6 Quiz Screen (Core)
```
┌──────────────────────────────┐
│  QDock        ⏱ Total: 12:30 │
│  Mathematics > Algebra       │
├──────────────────────────────┤
│  Question Timer: 1:30 ████░  │
│                              │
│  ┌────────────────────────┐  │
│  │   Google Form WebView  │  │
│  │                        │  │
│  │                        │  │
│  └────────────────────────┘  │
│                              │
│  [  Submit & Next  ]         │
└──────────────────────────────┘
```

**Timer logic:**
- Per-question timer: 90 seconds (1.5 min), resets each question
- Total timer: counts down from (num_questions × 90s)
- At 15 seconds remaining: timer turns red + haptic pulse
- Auto-advance when question timer hits 0

**WebView config:**
```kotlin
webView.settings.apply {
    javaScriptEnabled = true
    domStorageEnabled = true
    loadWithOverviewMode = true
    useWideViewPort = true
    mixedContentMode = MIXED_CONTENT_ALWAYS_ALLOW
}
```

---

### 5.7 Quiz Result Screen
```
┌──────────────────────────────┐
│         🎉 / 😢              │
│    Your Score: 85%           │
│  ████████████░░  85%         │
│                              │
│  ✅ Correct:    17           │
│  ❌ Wrong:       3           │
│  ⏱ Time:    18:42           │
│                              │
│  [Review Mistakes] [Home]    │
└──────────────────────────────┘
```
- 100% → confetti animation (Lottie)
- Score card slides up on entry
- Progress bar animates from 0 to score

---

### 5.8 Wrong Answer Review Screen
- Card per wrong answer:
  - Question text
  - ❌ Your answer (red)
  - ✅ Correct answer (green)
- "Back to History" button

---

## 6. GRADLE DEPENDENCIES (libs.versions.toml)

```toml
[versions]
kotlin = "2.0.21"
agp = "8.7.3"
compose-bom = "2024.09.00"
hilt = "2.52"
room = "2.6.1"
navigation = "2.8.3"
lifecycle = "2.8.6"
coroutines = "1.9.0"
lottie = "6.5.2"
splashscreen = "1.0.1"

[libraries]
# Compose
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
compose-animation = { group = "androidx.compose.animation", name = "animation" }
compose-ui-tooling = { group = "androidx.compose.ui", name = "ui-tooling-preview" }

# Navigation
navigation-compose = { group = "androidx.navigation", name = "navigation-compose", version.ref = "navigation" }

# Lifecycle
lifecycle-viewmodel = { group = "androidx.lifecycle", name = "lifecycle-viewmodel-compose", version.ref = "lifecycle" }
lifecycle-runtime = { group = "androidx.lifecycle", name = "lifecycle-runtime-compose", version.ref = "lifecycle" }

# Room
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }
room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }

# Hilt
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }
hilt-navigation = { group = "androidx.hilt", name = "hilt-navigation-compose", version = "1.2.0" }

# Coroutines
coroutines-android = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-android", version.ref = "coroutines" }

# Lottie
lottie-compose = { group = "com.airbnb.android", name = "lottie-compose", version.ref = "lottie" }

# Splash Screen
splashscreen = { group = "androidx.core", name = "core-splashscreen", version.ref = "splashscreen" }

# DataStore (for streak/settings)
datastore = { group = "androidx.datastore", name = "datastore-preferences", version = "1.1.1" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp = { id = "com.google.devtools.ksp", version = "2.0.21-1.0.28" }
room = { id = "androidx.room", version.ref = "room" }
```

---

## 7. THEME (Material 3 Purple)

```kotlin
// ui/theme/Color.kt
val QDockPurple = Color(0xFF6750A4)
val QDockPurpleContainer = Color(0xFFEADDFF)
val QDockOnPurple = Color(0xFFFFFFFF)
val QDockBackground = Color(0xFF1C1B1F)    // Dark
val QDockSurface = Color(0xFF2B2930)
val QDockSurfaceVariant = Color(0xFF332F3F)

// Progress colors
val ProgressRed = Color(0xFFE53935)
val ProgressYellow = Color(0xFFFDD835)
val ProgressGreen = Color(0xFF43A047)

// ui/theme/Type.kt
val QDockTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = FontFamily(Font(R.font.outfit_bold)),
        fontSize = 32.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = FontFamily(Font(R.font.outfit_regular)),
        fontSize = 14.sp
    )
    // ... complete scale
)
```

---

## 8. ANIMATIONS PLAN

| Location | Animation | Library |
|---|---|---|
| App launch | Animated QDock logo fade-in | Compose |
| Lesson cards | Slide-in staggered on load | Compose |
| Progress bar | Animated width from 0 to value | Compose |
| Quiz timer | Countdown ring animation | Compose Canvas |
| Timer < 15s | Red pulse + haptic | Compose + Vibrator |
| Result screen | Score card slide-up | Compose |
| 100% score | Confetti burst | Lottie |
| Wrong answer | Shake animation | Compose |
| FAB | Expand to form on click | Compose |
| Screen transitions | Shared element + fade | Navigation Compose |
| Streak badge | Bounce on new day | Compose |
| Empty states | Lottie loop illustration | Lottie |

---

## 9. PERMISSIONS (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.VIBRATE" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
```

---

## 10. NOTIFICATIONS

**Daily Study Reminder:**
- WorkManager task scheduled at user-set time
- Fires if no quiz session that day
- Channel: "QDock Reminders" (importance HIGH)
- Action button: "Open QDock"

---

## 11. BACKUP — EXPORT & IMPORT

### Overview
All app data (lessons, topics, quiz links, sessions, wrong answers, streak) is packaged into a single `.qdock` backup file (JSON inside, renamed extension). No internet needed — fully local.

---

### 11.1 Backup File Format

```json
{
  "version": 1,
  "exportedAt": 1719500000000,
  "appVersion": "1.0.0",
  "data": {
    "lessons": [...],
    "topics": [...],
    "quizLinks": [...],
    "quizSessions": [...],
    "wrongAnswers": [...],
    "streak": {
      "currentStreak": 5,
      "lastStudyDate": 1719500000000
    }
  }
}
```

**File extension:** `.qdock`
**MIME type:** `application/octet-stream`
**Filename format:** `QDock_Backup_2024-06-27.qdock`

---

### 11.2 Export Flow

```
User taps "Export Backup"
  → App serializes all Room tables to JSON (kotlinx.serialization)
  → Wraps in backup envelope with version + timestamp
  → Writes file to MediaStore Downloads (no permission needed API 29+)
  → Shows share sheet → user can save to Files, Google Drive, WhatsApp, etc.
  → Success snackbar: "Backup saved to Downloads"
```

**Code approach:**
```kotlin
// No WRITE_EXTERNAL_STORAGE needed on API 29+
val resolver = context.contentResolver
val contentValues = ContentValues().apply {
    put(MediaStore.Downloads.DISPLAY_NAME, "QDock_Backup_${date}.qdock")
    put(MediaStore.Downloads.MIME_TYPE, "application/octet-stream")
}
val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, contentValues)
resolver.openOutputStream(uri!!)?.use { it.write(jsonBytes) }
```

---

### 11.3 Import Flow

```
User taps "Import Backup"
  → Android file picker opens (ACTION_OPEN_DOCUMENT)
  → User selects .qdock file
  → App validates JSON structure + version
  → Shows confirmation dialog: "This will replace all current data. Continue?"
  → On confirm: clears DB → inserts all backup data → restores streak
  → Success: navigates to Home with snackbar "Backup restored!"
  → On error: shows error dialog with reason
```

**Validation checks:**
- Valid JSON structure ✅
- `version` field present ✅
- All required tables present ✅
- Foreign key integrity (lessonId exists before inserting topics) ✅

---

### 11.4 Backup Screen UI

**Location:** Settings screen (gear icon in top bar on Home)

```
┌──────────────────────────────┐
│  ⚙️ Settings                 │
├──────────────────────────────┤
│  🌙 Dark Mode          [  ●] │
│  🔐 App PIN Lock       [   ] │
│  🔔 Study Reminder   9:00 PM │
│                              │
│  ── Backup & Restore ──      │
│                              │
│  Last backup: Jun 27, 2024   │
│                              │
│  [ 📤 Export Backup ]        │
│  [ 📥 Import Backup ]        │
│                              │
│  ── Danger Zone ──           │
│  [ 🗑️ Clear All Data ]       │
└──────────────────────────────┘
```

---

### 11.5 Auto-Backup (Optional Enhancement)

- On every quiz session complete → silently save backup to Downloads/QDock/
- Keeps last 3 auto-backups, deletes older ones
- Toggle in Settings: "Auto-backup after each quiz" [ON/OFF]

---

### 11.6 Dependencies Needed

```toml
# kotlinx.serialization (JSON)
serialization-json = { group = "org.jetbrains.kotlinx", name = "kotlinx-serialization-json", version = "1.7.3" }
```

```toml
# Plugin in libs.versions.toml
kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
```

**No extra file permission needed** — uses MediaStore API (Android 10+) and `ACTION_OPEN_DOCUMENT` for import.

---

### 11.7 Permissions for Backup

```xml
<!-- Only needed for Android 9 and below (API 28-) -->
<uses-permission
    android:name="android.permission.WRITE_EXTERNAL_STORAGE"
    android:maxSdkVersion="28" />
```

Android 10+ (API 29+): **zero extra permissions needed** for Downloads folder access.

---

## 12. FEATURES CHECKLIST

### Core
- [x] Add / Edit / Delete Lessons
- [x] Add / Edit / Delete Topics per Lesson
- [x] Add Google Form quiz links per Topic
- [x] WebView quiz player
- [x] Per-question 1.5 min timer
- [x] Total session countdown timer
- [x] Score tracking + progress bar (colored)
- [x] Wrong answer save + review
- [x] History tab (grouped)

### Enhanced (Suggestions)
- [x] 🔥 Daily streak counter (DataStore)
- [x] 🔔 Daily push notification reminder (WorkManager)
- [x] 🌙 Dark mode (default) + Light mode toggle
- [x] 🔍 Search lessons/topics
- [x] 🎉 Confetti on 100% score (Lottie)
- [x] 📤 Export wrong answers as PDF (iText7 or PdfDocument API)
- [x] 📱 Haptic feedback on timer warning
- [x] 🔐 Optional app PIN lock (BiometricPrompt)
- [x] 📊 Quiz result summary card with animation
- [x] 💾 Room DB with cascade deletes (no orphan data)
- [x] 📤 Export full backup as `.qdock` file to Downloads (no permission needed API 29+)
- [x] 📥 Import backup via file picker with JSON validation
- [x] 🔁 Auto-backup after each quiz (keeps last 3 files)
- [x] ⚙️ Settings screen (dark mode, PIN, reminder time, backup controls)

---

## 12. MINIMUM SDK & COMPATIBILITY

| API | Android | Supported |
|---|---|---|
| 26 | Android 8.0 Oreo | ✅ minSdk |
| 28 | Android 9.0 Pie | ✅ |
| 30 | Android 11 | ✅ |
| 33 | Android 13 | ✅ |
| 34 | Android 14 | ✅ |
| 35 | Android 15 | ✅ targetSdk |

**Coverage: ~95% of active Android devices**

---

## 13. FOLDER & FILE COUNT ESTIMATE

| Layer | Files |
|---|---|
| Data (entities, DAOs, DB, repos) | ~18 files |
| Domain (models, interfaces, usecases) | ~12 files |
| Presentation (screens, viewmodels) | ~20 files |
| UI (theme, components, animations) | ~10 files |
| DI (Hilt modules) | ~3 files |
| Manifest + Gradle files | ~5 files |
| **Total** | **~68 files** |

---

## 14. DEVELOPMENT PHASES

| Phase | Tasks | Est. Time |
|---|---|---|
| 1 | Project setup, Gradle, theme, navigation skeleton | 1 day |
| 2 | Room DB, all entities + DAOs | 1 day |
| 3 | Lesson + Topic CRUD screens | 2 days |
| 4 | Quiz link management + WebView player | 2 days |
| 5 | Timer system + score tracking | 1 day |
| 6 | Progress bar + history tab | 1 day |
| 7 | Wrong answer save + review screen | 1 day |
| 8 | Animations + Lottie + haptics | 1 day |
| 9 | Streak, notifications, dark mode, search | 2 days |
| 10 | Backup export/import + Settings screen | 1 day |
| 11 | Testing, bug fixes, APK build | 1 day |
| **Total** | | **~14 days** |

---

## 15. BUILD COMMAND

```bash
# Debug APK
./gradlew assembleDebug

# Release APK (after keystore setup)
./gradlew assembleRelease

# Output location
app/build/outputs/apk/debug/app-debug.apk
```

---

*QDock — Study Smart. Track Progress. Dock Your Knowledge.*
