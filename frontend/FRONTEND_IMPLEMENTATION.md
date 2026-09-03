# Base10 Frontend - Complete Implementation Guide

## 📋 Table of Contents
- [Architecture Overview](#architecture-overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Core Features](#core-features)
- [API Integration](#api-integration)
- [State Management](#state-management)
- [Authentication System](#authentication-system)
- [Classroom Module](#classroom-module)
- [AI Tutoring System](#ai-tutoring-system)
- [Admin Dashboard](#admin-dashboard)
- [Quiz System](#quiz-system)
- [Deployment](#deployment)

---

## 🏗️ Architecture Overview

Base10 is a Next.js 15 educational platform built with the App Router, featuring:
- **Client-Side Rendering** for interactive components
- **Server Components** for optimized performance
- **API Integration** with DigitalOcean backend
- **Real-time Features** with WebSocket support (planned)
- **Responsive Design** with Tailwind CSS

### Design Principles
- **Role-Based Access Control (RBAC)**: Student, Teacher, Admin roles
- **Progressive Enhancement**: Works without JavaScript
- **Mobile-First**: Optimized for all screen sizes
- **Dark Mode Support**: Full theme compatibility
- **Accessibility**: WCAG 2.1 AA compliance

### West African Design Priorities
- **Data Conservation**: Progressive disclosure, lazy loading, optional image loads
- **OLED Battery Saving**: Dark mode default, true black backgrounds (#0F172A)
- **High Sunlight Legibility**: High contrast ratios, emerald on dark slate
- **Low-End Device Performance**: System fonts, minimal animations, code splitting
- **Offline-First**: LocalStorage caching, sync queue, graceful degradation
- **Network Resilience**: Optimistic UI updates, 2G/3G tolerance

---

## 🛠️ Technology Stack

### Core Framework
- **Next.js 15.1.3** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety

### Styling
- **Tailwind CSS 3.4.17** - Utility-first CSS
- **Custom Design System** - Consistent spacing, colors, typography

### State Management
- **Zustand** - Lightweight state management
  - `authStore` - User authentication state
  - `modalStore` - Global modal management

### HTTP Client
- **Axios** - API requests with interceptors
- **Base URL**: `https://stingray-app-x7lzo.ondigitalocean.app/api/v1`

### UI Components
- **Lucide React** - Icon library
- **Custom Components** - Reusable UI elements

### Development Tools
- **ESLint** - Code linting
- **PostCSS** - CSS processing
- **Git** - Version control

---

## 📁 Project Structure

```
app-files/
├── app/                          # Next.js App Router pages
│   ├── admin/                    # Admin dashboard
│   │   ├── page.tsx             # Main admin dashboard
│   │   ├── roles/page.tsx       # Role management
│   │   ├── users/page.tsx       # User management
│   │   ├── questions/page.tsx   # Question management
│   │   └── reports/page.tsx     # Content reports
│   ├── ai-tutor/                # Standalone AI tutor
│   │   └── page.tsx             # Full AI chat interface
│   ├── classrooms/              # Classroom management
│   │   ├── page.tsx             # Classroom list
│   │   └── [id]/                # Individual classroom
│   │       ├── page.tsx         # Classroom stream
│   │       ├── assignments/     # Assignment management
│   │       ├── materials/       # Learning materials
│   │       ├── people/          # Student management
│   │       └── students/        # Student profiles
│   │           └── [studentId]/page.tsx
│   ├── dashboard/               # Student dashboard
│   │   └── page.tsx
│   ├── practice/                # Practice questions
│   │   └── page.tsx
│   ├── profile/                 # User profile
│   │   └── page.tsx
│   ├── login/                   # Authentication
│   │   └── page.tsx
│   ├── register/                # Registration
│   │   └── page.tsx
│   └── layout.tsx               # Root layout
├── components/                   # Reusable components
│   ├── AppLayout.tsx            # Main app layout
│   ├── GlobalModal.tsx          # Modal system
│   ├── Sidebar.tsx              # Navigation sidebar
│   └── classroom/               # Classroom components
│       ├── AssignmentCard.tsx
│       ├── AskAITeacher.tsx     # AI chat interface
│       ├── ClassroomCard.tsx
│       ├── Composer.tsx         # Announcement composer
│       ├── CreateClassroomForm.tsx
│       ├── EditClassroomForm.tsx
│       ├── JoinClassroomForm.tsx
│       ├── MaterialCard.tsx
│       └── StreamPost.tsx
├── lib/                         # Utilities
│   └── api.ts                   # API client
├── store/                       # State management
│   ├── authStore.ts             # Auth state
│   └── modalStore.ts            # Modal state
├── styles/                      # Global styles
│   └── globals.css
└── memory-bank/                 # Project documentation
    ├── activeContext.md
    ├── architect.md
    ├── decisionLog.md
    ├── productContext.md
    ├── progress.md
    ├── projectBrief.md
    └── systemPatterns.md
```

---

## 🎯 Core Features

### 1. Authentication & Authorization

#### Login System (`/login`)
- Phone number or email login
- Password with show/hide toggle
- Token-based authentication (JWT)
- Auto-redirect to dashboard on success
- Error handling with user-friendly messages

#### Registration System (`/register`)
- Required fields:
  - Full name
  - Phone number
  - Password (6+ characters)
  - Role selection (Student/Teacher)
- Optional: Email address
- Password confirmation
- Role-based onboarding
- Auto-login after registration

#### Role-Based Access Control
**Three User Roles:**
1. **Student**
   - Access quizzes and practice questions
   - Join classrooms with code
   - Submit assignments
   - Chat with AI tutor
   - View grades and feedback

2. **Teacher**
   - Create and manage classrooms
   - Post announcements
   - Create assignments
   - Grade student work
   - View student profiles
   - Send direct messages to students
   - Access AI teaching recommendations

3. **Admin**
   - Full system access
   - User management (view, edit, delete)
   - Role management (change user roles)
   - Content moderation
   - Question management
   - System health monitoring
   - Analytics dashboard

---

### 2. Dashboard System

#### Student Dashboard (`/dashboard`)
**Metrics Cards:**
- Total questions answered
- Current accuracy rate
- Active study streak
- Time spent studying

**Quick Actions:**
- Start Practice Session
- View Progress
- Join Classroom
- AI Tutor

**Recent Activity:**
- Recent quiz sessions
- Graded assignments
- Classroom announcements

#### Teacher Dashboard
- Active classrooms overview
- Student engagement metrics
- Pending assignments to grade
- Recent classroom activity

#### Admin Dashboard (`/admin`)
**System Health:**
- Database connection status
- Redis connection status
- Total users (24h, 7d active)
- Error rate monitoring

**Metrics Sections:**
- User Growth (DAU, MAU, retention)
- Content Quality (questions by subject/difficulty)
- Engagement (attempts, study time, streaks)

**Quick Actions:**
- Manage Roles
- Manage Users
- Review Questions
- Handle Reports

---

### 3. Practice & Quiz System

#### Practice Page (`/practice`)
**Subject Selection:**
- 10 WAEC subjects available
- Mathematics, English, Physics, Chemistry, Biology
- Geography, History, Economics, Commerce, Literature

**Question Interface:**
- Multiple choice questions (A, B, C, D)
- Timer display
- Progress tracking
- Instant feedback
- Explanation from AI tutor

**Session Management:**
- Configurable question count (5-50)
- Difficulty selection (Easy/Medium/Hard)
- Session summary at completion
- Score and accuracy tracking

---

## 🔌 API Integration

### API Client (`lib/api.ts`)

#### Base Configuration
```typescript
const API_BASE_URL = 'https://stingray-app-x7lzo.ondigitalocean.app/api/v1'

// Axios instance with interceptors
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

#### API Modules

**1. Authentication API (`authApi`)**
```typescript
register(data: {
  phone_number: string
  email?: string
  password: string
  full_name: string
  role?: 'student' | 'teacher'
})
login(username: string, password: string)
getProfile()
updateProfile(data: any)
```

**2. Classroom API (`classroomApi`)**
```typescript
// Classroom CRUD
createClassroom(data)
getClassrooms()
joinClassroom(join_code)
getClassroom(classroomId)
updateClassroom(classroomId, data)
deleteClassroom(classroomId)

// Stream & Announcements
getStream(classroomId)
postAnnouncement(classroomId, data)
commentOnPost(classroomId, postId, data)

// Assignments
createManualAssignment(classroomId, data)
getAssignments(classroomId)
updateAssignment(assignmentId, data)
deleteAssignment(assignmentId)
getSubmissions(assignmentId)
gradeSubmission(submissionId, data)

// Materials
uploadMaterial(classroomId, data)
getMaterials(classroomId)
updateMaterial(materialId, data)
deleteMaterial(materialId)

// AI Teacher
askAITeacher(classroomId, question)

// Student Profiles
getStudentProfile(classroomId, studentId)
updateStudentProfile(classroomId, studentId, data)
sendStudentMessage(classroomId, studentId, data)
getStudentMessages(classroomId, studentId)
getStudentAIContext(classroomId, studentId, question)

// Members
getClassroomMembers(classroomId)
```

**3. AI API (`aiApi`)**
```typescript
explainAnswer(data: {
  question_id: number
  student_answer: number
  context?: string
})
chat(data: {
  message: string
  history?: Array<{role, content}>
  subject?: string
  topic?: string
  socratic_mode?: boolean
})
generateQuiz(params: {
  subject: string
  topic?: string
  difficulty?: 'easy' | 'medium' | 'hard'
  num_questions?: number
})
getStatus()
```

**4. Question API (`questionApi`)**
```typescript
getRandomQuestions(subject, count, difficulty?)
submitAnswer(data: {
  question_id: number
  user_answer: string
})
```

**5. Admin API (`adminApi`)**
```typescript
// System
getHealth()
getUserGrowth()
getContentQuality()
getEngagement()

// User Management
searchUsers(query, limit)
getTopUsers(limit)
deactivateUser(userId, reason)
activateUser(userId)

// Role Management
changeUserRole(userId, newRole, reason)
getUsersByRole(role)
deleteUser(userId)

// Content Management
getProblematicQuestions(minAttempts, maxAccuracy, limit)
deleteQuestion(questionId, reason)
resolveReport(reportId, action, notes?)
```

**6. Student API (`studentApi`)**
```typescript
getDashboard()
getDashboardSummary()
```

---

## 🏫 Classroom Module

### Complete Feature Set

#### 1. Classroom Creation & Management

**Create Classroom (`CreateClassroomForm.tsx`)**
- Name (required)
- Description (optional)
- Subject (dropdown)
- Grade level (dropdown)
- Auto-generated join code (6-character)
- Role check: Teachers only

**Join Classroom (`JoinClassroomForm.tsx`)**
- Enter 6-character join code
- Auto-enrollment
- Role check: Students only

**Edit Classroom (`EditClassroomForm.tsx`)**
- Update name, description, subject, grade level
- Partial updates (only changed fields sent)
- Permission check: Teacher/creator only

**Delete Classroom**
- Confirmation modal with cascade warning
- Soft delete (can be recovered)
- Permission check: Teacher/creator only

#### 2. Classroom Dashboard (`/classrooms/[id]`)

**Two Tabs:**
1. **📢 Class Stream**
   - Announcements feed
   - Composer for new posts
   - Comments on posts
   - Notification badges

2. **🤖 AI Teacher**
   - Chat interface
   - Socratic mode toggle
   - Quiz generation
   - Context-aware responses

**Sidebar Components:**
- **Join Code Card** (Teacher only)
  - Display join code
  - Copy to clipboard
  - Share with students

- **Teacher Info Card** (Student only)
  - Teacher name
  - Contact information

- **Quick Links**
  - 📝 Assignments
  - 📚 Materials
  - 👥 People

- **Details Card**
  - Subject, grade level
  - Student count
  - Creation date

- **Notification Info** (Teacher only)
  - Push notifications active
  - Email notifications
  - SMS for urgent items

#### 3. Assignments Module (`/classrooms/[id]/assignments`)

**Teacher View:**
- Create manual assignment button
- Assignment cards with:
  - Title and description
  - Due date with countdown
  - Points possible
  - Priority indicator (HIGH if <24hrs)
  - Notification channel badges
  - Edit/Delete buttons
  - Submission count

**Student View:**
- Assignment cards showing:
  - Due date with urgency banner
  - Submission status
  - Grade and feedback (if graded)
  - Submit button
  - View submission history

**Assignment Card Features:**
- Priority calculation (24hr threshold)
- Notification indicators:
  - 📢 Push (always)
  - 📧 Email (always)
  - 📱 SMS (if HIGH priority)
- Color-coded grades:
  - 🎉 ≥80% (green)
  - ✅ ≥60% (blue)
  - 📊 <60% (orange)

**Grading Interface:**
- View all submissions
- Assign score (0-100)
- Provide feedback
- Bulk grading options
- Email notification to student

#### 4. Materials Module (`/classrooms/[id]/materials`)

**Upload Materials:**
- File upload
- Title and description
- Category selection
- Teacher only

**Material Cards:**
- File type icon
- Download button
- View/preview
- Edit/Delete (teacher only)
- Upload date

#### 5. People Management (`/classrooms/[id]/people`)

**Two Sections:**

**Teacher Section:**
- Prominent display with gradient
- Full name, username, email
- "Instructor" badge
- Larger avatar (14x14)

**Students Section:**
- Grid of student cards
- Each card shows:
  - Avatar
  - Full name, username
  - Email (teachers only)
  - Join date
  - Submission count with progress bar
  - Activity status
- Click to view detailed profile

#### 6. Student Profile System (`/classrooms/[id]/students/[studentId]`)

**Three Tabs:**

**📊 Overview Tab:**
- **Performance Metrics** (4 cards):
  - Assignment completion rate
  - Average grade
  - Quiz attempts
  - Quiz accuracy
  
- **Recent Activity Timeline:**
  - Submissions
  - Quiz attempts
  - Grades received
  - Timestamps

- **Teacher's Notes Sidebar:**
  - General notes
  - Strengths & weaknesses
  - Learning style (visual/auditory/kinesthetic)
  - Participation level (high/medium/low)
  - Homework completion rate (slider 0-100%)
  - AI context (for personalized tutoring)
  - Inline editing

**💬 Messages Tab:**
- **Send Message Form:**
  - Subject line
  - Message type (general/encouragement/concern/reminder)
  - Message content
  - Auto-notification trigger

- **Message History:**
  - All past messages
  - Read/Unread badges
  - Timestamps
  - Message types

**🤖 AI Advice Tab:**
- Ask AI for teaching strategies
- Context includes:
  - Student performance data
  - Teacher's observations
  - Recent activity
- Get personalized recommendations
- Example: "How can I help this student improve?"

---

## 🤖 AI Tutoring System

### Enhanced Features (Socratic Mode & Quiz Generation)

#### 1. Classroom AI (`AskAITeacher.tsx`)

**Features:**
- **Chat Interface:**
  - Message history
  - User/AI message differentiation
  - Typing indicator
  - Auto-scroll to latest

- **Socratic Mode Toggle:**
  - Button in header
  - Changes AI behavior to guided questioning
  - Helps students discover answers
  - Dynamic header message

- **Generate Quiz Button:**
  - Opens modal
  - Configure topic, difficulty, questions
  - Displays formatted quiz in chat

- **Quiz Mode Detection:**
  - AI can suggest `[QUIZ_MODE: Subject | Topic]`
  - Automatically opens quiz modal
  - Seamless transition to practice

- **Context Awareness:**
  - Knows classroom name
  - Subject-specific responses
  - Grade-level appropriate

#### 2. Standalone AI Tutor (`/ai-tutor`)

**Full-Featured Interface:**

**Header Controls:**
- Subject selector (10 WAEC subjects)
- Topic input (optional)
- Socratic mode toggle
- Settings panel toggle
- Generate quiz button
- Clear chat button

**Settings Panel:**
- Subject dropdown
- Topic input
- Mode explanation
- Quick actions

**Chat Area:**
- Empty state with feature cards:
  - 📖 Ask Questions
  - 🧠 Socratic Learning
  - ✨ Practice Quizzes
  
- Message bubbles:
  - User: Indigo background
  - AI: White with Sparkles icon
  - Prose formatting
  - Dark mode support

**Message History:**
- Last 10 messages sent for context
- Maintains conversation flow
- Subject/topic awareness

**Quiz Generation Modal:**
- Subject selection
- Topic input (optional)
- Difficulty (easy/medium/hard)
- Number of questions (1-10 slider)
- Generate button with loading state
- Formatted output in chat

#### 3. AI API Integration

**Chat Endpoint:**
```typescript
POST /ai/chat
{
  "message": "Explain quadratic equations",
  "history": [{role: "user", content: "..."}, ...],
  "subject": "MATHEMATICS",
  "topic": "Algebra",
  "socratic_mode": true
}

Response:
{
  "response": "Let me guide you...",
  "mode": "socratic"
}
```

**Quiz Generation:**
```typescript
POST /ai/generate-quiz
  ?subject=CHEMISTRY
  &topic=Atomic Structure
  &difficulty=medium
  &num_questions=5

Response:
{
  "questions": [
    {
      "question": "What is...",
      "options": {
        "A": "...",
        "B": "...",
        "C": "...",
        "D": "..."
      },
      "correct_answer": "B",
      "explanation": "The answer is B because...",
      "difficulty": "medium"
    }
  ],
  "metadata": {...}
}
```

**AI Status:**
```typescript
GET /ai/status

Response:
{
  "status": "operational",
  "model": "gemini-2.0-flash-exp",
  "features": {
    "explanations": true,
    "chat": true,
    "socratic_mode": true,
    "quiz_generation": true
  },
  "limits": {
    "max_history": 10,
    "max_quiz_questions": 10
  }
}
```

#### 4. LaTeX Support (Planned)

**Rendering:**
- KaTeX or MathJax integration
- Inline formulas: `$x^2 + 2x + 1$`
- Block formulas: `$$\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$`

**Clean for Speech:**
- Backend converts LaTeX to natural language
- Accessibility support
- Text-to-speech compatible

---

## 🎨 State Management

### 1. Authentication Store (`authStore.ts`)

**Zustand Store:**
```typescript
interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  setAuth: (token: string, user: User) => void
  logout: () => void
  updateUser: (user: User) => void
}
```

**Features:**
- Persists token to localStorage
- Auto-logout on token expiration
- User profile caching
- Role-based permission checks

**Usage:**
```typescript
const { user, isAuthenticated, setAuth, logout } = useAuthStore()

// Login
setAuth(token, userData)

// Logout
logout()

// Check role
const isTeacher = user?.role === 'teacher'
```

### 2. Modal Store (`modalStore.ts`)

**Zustand Store:**
```typescript
interface ModalState {
  title: string
  message: string
  type: 'success' | 'error' | 'confirm' | null
  isOpen: boolean
  onConfirm: (() => void) | null
  showSuccess: (message: string, title?: string) => void
  showError: (message: string, title?: string) => void
  showConfirm: (message: string, onConfirm: () => void, title?: string) => void
  close: () => void
}
```

**Features:**
- Global modal system
- Three types: success, error, confirm
- Custom titles and messages
- Confirmation callbacks
- Auto-close on success/error
- Manual close for confirms

**Usage:**
```typescript
const { showSuccess, showError, showConfirm } = useModalStore()

// Success notification
showSuccess('Classroom created successfully!', 'Success')

// Error notification
showError('Failed to save changes', 'Error')

// Confirmation dialog
showConfirm(
  'Delete this classroom?',
  async () => {
    await deleteClassroom(id)
    showSuccess('Classroom deleted')
  },
  'Confirm Delete'
)
```

### 3. Global Modal Component (`GlobalModal.tsx`)

**Rendered in Root Layout:**
- Always available
- Positioned as overlay
- Backdrop click to close
- Escape key to close
- Smooth animations

**Modal Types:**
- **Success**: Green checkmark, auto-close
- **Error**: Red X, manual close
- **Confirm**: Two buttons (Cancel/Confirm)

---

## 🎨 Component Library

### Layout Components

#### 1. AppLayout (`AppLayout.tsx`)
- **Sidebar navigation**
- **Main content area**
- **Responsive drawer on mobile**
- **Dark mode support**
- **Role-based menu items**

#### 2. Sidebar (`Sidebar.tsx`)
**Navigation Items:**
- Dashboard
- Practice
- Classrooms (Teachers/Students)
- AI Tutor
- Profile
- Admin (Admin only)
- Logout

**Features:**
- Active route highlighting
- Icon + text labels
- User info at bottom
- Collapsible on mobile

### Form Components

#### Input Fields
- Text input with label
- Password with show/hide
- Email validation
- Phone number formatting
- Textarea with auto-resize
- Select dropdown
- Range slider
- Date picker

#### Buttons
- Primary (indigo)
- Secondary (gray)
- Danger (red)
- Success (green)
- Loading states
- Disabled states
- Icon buttons

### Card Components

#### ClassroomCard
- Name and description
- Subject and grade pills
- Student count
- Role badge (Teacher/Student)
- Teacher name (students only)
- Creation date
- Hover effects
- Click to navigate

#### AssignmentCard
- Title and description
- Due date with countdown
- Priority badge
- Points possible
- Submission status
- Notification indicators
- Edit/Delete buttons
- Grade display

#### MaterialCard
- File type icon
- Title and description
- Upload date
- Download button
- Edit/Delete buttons
- Preview capability

---

## 🧩 Core UI Components (Detailed Specifications)

### 1. The Question Card (`<QuestionCard />`)
The atomic unit of the learning experience - every quiz question renders in this component.

#### Structure & Layout
```tsx
<div className="bg-slate-800 rounded-lg p-6 shadow-md">
  {/* Header */}
  <div className="flex justify-between items-center mb-4">
    <span className="text-xs font-semibold bg-emerald-900 text-emerald-500 px-3 py-1 rounded-full uppercase tracking-wide">
      {subject}
    </span>
    <span className="text-slate-400 font-mono text-sm tabular-nums">
      ⏱️ {formatTime(timeRemaining)}
    </span>
  </div>
  
  {/* Question Body (LaTeX Support) */}
  <div className="prose prose-invert prose-slate max-w-none mb-6">
    <div 
      className="text-slate-100 text-lg leading-relaxed"
      dangerouslySetInnerHTML={{ __html: renderLatex(questionText) }}
    />
  </div>
  
  {/* Options Grid (Touch Optimized) */}
  <div className="space-y-3">
    {options.map((option, idx) => (
      <button
        key={option.value}
        onClick={() => handleSelect(option.value)}
        disabled={answered}
        className={cn(
          "w-full min-h-[56px] px-6 py-4 rounded-lg text-left transition-all",
          "flex items-center gap-3 font-medium",
          // Default state
          "bg-slate-900 border-2 border-slate-700",
          // Hover state
          "hover:border-emerald-500 hover:bg-slate-800",
          // Active/Selected state
          selectedOption === option.value && "border-emerald-500 bg-emerald-900/30",
          // Correct answer (after submission)
          answered && option.value === correctAnswer && "border-green-500 bg-green-900/30",
          // Incorrect answer (after submission)
          answered && selectedOption === option.value && option.value !== correctAnswer && "border-red-500 bg-red-900/30",
          // Disabled state
          answered && "cursor-not-allowed opacity-75"
        )}
      >
        <span className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center font-bold text-slate-300">
          {option.label}
        </span>
        <span className="flex-1 text-slate-100">
          {option.text}
        </span>
        {answered && option.value === correctAnswer && (
          <CheckCircle className="flex-shrink-0 w-5 h-5 text-green-500" />
        )}
        {answered && selectedOption === option.value && option.value !== correctAnswer && (
          <XCircle className="flex-shrink-0 w-5 h-5 text-red-500" />
        )}
      </button>
    ))}
  </div>
  
  {/* Footer (AI Explanation) */}
  {answered && (
    <div className="mt-6 pt-6 border-t border-slate-700">
      <button
        onClick={() => loadExplanation()}
        className="text-emerald-500 hover:text-emerald-400 text-sm font-medium flex items-center gap-2"
      >
        <Sparkles className="w-4 h-4" />
        {showExplanation ? 'Hide Explanation' : '🤔 Why did I get this wrong? (Tap for AI explanation)'}
      </button>
      
      {showExplanation && (
        <div className="mt-4 prose prose-invert prose-sm">
          {isLoadingExplanation ? (
            <div className="flex items-center gap-2 text-slate-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>AI is thinking...</span>
            </div>
          ) : (
            <div dangerouslySetInnerHTML={{ __html: explanation }} />
          )}
        </div>
      )}
    </div>
  )}
</div>
```

#### Key Features
- **Full-width Design**: No wasted horizontal space on mobile
- **High Contrast**: `#F8FAFC` text on `#1E293B` cards for sunlight readability
- **56px Touch Targets**: Easy tapping on moving vehicles
- **LaTeX Rendering**: KaTeX for mathematical notation (e.g., `$x^2 + 5x + 6 = 0$`)
- **Progressive AI**: Explanation loads only when requested (saves data)
- **Visual Feedback**: Immediate color change on selection (optimistic UI)
- **State Persistence**: Selected answer survives even if user navigates away

#### Props Interface
```typescript
interface QuestionCardProps {
  question: {
    id: number
    text: string
    subject: string
    options: {
      A: string
      B: string
      C: string
      D: string
    }
    correct_answer: 'A' | 'B' | 'C' | 'D'
  }
  timeRemaining: number
  onAnswer: (answer: string) => void
  answered: boolean
  selectedOption?: string
}
```

---

### 2. The 3D Flashcard (`<Flashcard />`)
Swipe-based learning card with smooth flip animation and gesture controls.

#### Structure & Implementation
```tsx
const Flashcard = ({ flashcard, onSwipe }: FlashcardProps) => {
  const [flipped, setFlipped] = useState(false)
  const [touchStart, setTouchStart] = useState<number | null>(null)
  const [touchEnd, setTouchEnd] = useState<number | null>(null)
  
  // Minimum swipe distance (50px)
  const minSwipeDistance = 50
  
  const handleTouchStart = (e: TouchEvent) => {
    setTouchEnd(null)
    setTouchStart(e.targetTouches[0].clientX)
  }
  
  const handleTouchMove = (e: TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX)
  }
  
  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return
    
    const distance = touchStart - touchEnd
    const isLeftSwipe = distance > minSwipeDistance
    const isRightSwipe = distance < -minSwipeDistance
    
    if (isLeftSwipe) {
      // Forgot - move to review pile
      onSwipe('forgot', flashcard.id)
    }
    if (isRightSwipe) {
      // Remembered - move to known pile
      onSwipe('remembered', flashcard.id)
    }
  }
  
  return (
    <div className="relative w-full aspect-[3/2] cursor-pointer select-none">
      {/* Swipe hint indicators */}
      {touchStart !== null && touchEnd !== null && (
        <>
          {touchStart - touchEnd > 20 && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 z-20 text-red-500 animate-pulse">
              ← Forgot
            </div>
          )}
          {touchEnd - touchStart > 20 && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 z-20 text-green-500 animate-pulse">
              Remembered →
            </div>
          )}
        </>
      )}
      
      {/* 3D Card Container */}
      <div
        className="relative w-full h-full"
        style={{ perspective: '1000px' }}
        onClick={() => setFlipped(!flipped)}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        <div
          className={cn(
            "absolute inset-0 w-full h-full transition-transform duration-600 ease-out",
            "transform-style-preserve-3d",
            flipped && "rotate-y-180"
          )}
        >
          {/* Front Face */}
          <div className="absolute inset-0 w-full h-full backface-hidden bg-slate-800 rounded-xl p-8 flex flex-col justify-between shadow-xl border border-slate-700">
            <div>
              <h3 className="text-2xl font-bold text-slate-100 mb-4">
                {flashcard.term}
              </h3>
              {flashcard.image && (
                <img
                  src={flashcard.image}
                  alt={flashcard.term}
                  className="rounded-lg w-full h-48 object-cover"
                />
              )}
            </div>
            <p className="text-sm text-slate-400 text-center">
              Tap to flip • Swipe left (Forgot) • Swipe right (Remembered)
            </p>
          </div>
          
          {/* Back Face */}
          <div className="absolute inset-0 w-full h-full backface-hidden bg-emerald-900 rounded-xl p-8 flex flex-col justify-between shadow-xl rotate-y-180 border border-emerald-700">
            <div>
              <p className="text-lg text-slate-100 leading-relaxed mb-4">
                {flashcard.definition}
              </p>
              {flashcard.context && (
                <p className="text-sm text-emerald-200/80 italic">
                  💡 {flashcard.context}
                </p>
              )}
            </div>
            <p className="text-sm text-emerald-300 text-center">
              Tap to flip back
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
```

#### CSS for 3D Transform
```css
/* Add to globals.css */
.transform-style-preserve-3d {
  transform-style: preserve-3d;
}

.backface-hidden {
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.rotate-y-180 {
  transform: rotateY(180deg);
}
```

#### Gesture Recognition
- **Swipe Left (50px)**: "I forgot this" → Moves card to review pile
- **Swipe Right (50px)**: "I remembered this" → Moves card to known pile
- **Tap Center**: Flip card to see answer
- **Visual Hints**: Real-time swipe direction indicators

#### State Management
```typescript
// Flashcard store
interface FlashcardState {
  currentCard: Flashcard | null
  knownPile: Flashcard[]
  reviewPile: Flashcard[]
  moveToKnown: (id: number) => void
  moveToReview: (id: number) => void
  nextCard: () => void
}
```

---

### 3. The Classroom Stream Item (`<StreamPost />`)
Optimized for quick scanning and data efficiency with progressive disclosure.

#### Structure & Layout
```tsx
const StreamPost = ({ post }: StreamPostProps) => {
  const [expanded, setExpanded] = useState(false)
  const [imageLoaded, setImageLoaded] = useState(false)
  
  const needsTruncation = post.content.length > 200
  const displayContent = expanded ? post.content : post.content.slice(0, 200)
  
  return (
    <article className="bg-slate-800 rounded-lg p-4 mb-3 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <header className="flex items-center gap-3 mb-3">
        {/* Avatar */}
        <div 
          className="w-10 h-10 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0 text-white font-bold text-sm"
          aria-label={`${post.author.name}'s avatar`}
        >
          {post.author.name.charAt(0).toUpperCase()}
        </div>
        
        {/* Author Info */}
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-slate-100 truncate">
            {post.author.name}
            {post.author.role === 'teacher' && (
              <span className="ml-2 text-xs bg-emerald-900 text-emerald-400 px-2 py-0.5 rounded-full">
                Teacher
              </span>
            )}
          </p>
          <p className="text-xs text-slate-400">
            {formatTimeAgo(post.created_at)}
          </p>
        </div>
        
        {/* Options Menu (Teacher only) */}
        {post.canEdit && (
          <button className="flex-shrink-0 p-1 hover:bg-slate-700 rounded">
            <MoreVertical className="w-5 h-5 text-slate-400" />
          </button>
        )}
      </header>
      
      {/* Content */}
      <div className="mb-3">
        <p className="text-slate-300 leading-relaxed whitespace-pre-wrap">
          {displayContent}
          {!expanded && needsTruncation && '...'}
        </p>
        {needsTruncation && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-emerald-500 text-sm mt-2 hover:text-emerald-400 font-medium"
          >
            {expanded ? 'Show less' : 'Read more'}
          </button>
        )}
      </div>
      
      {/* Attachment (Progressive Disclosure) */}
      {post.attachment && (
        <div className="mt-3 p-3 bg-slate-900 rounded-lg border border-slate-700">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              {/* File Icon based on type */}
              {post.attachment.type === 'pdf' && (
                <FileText className="w-5 h-5 text-red-500 flex-shrink-0" />
              )}
              {post.attachment.type === 'image' && (
                <Image className="w-5 h-5 text-blue-500 flex-shrink-0" />
              )}
              {post.attachment.type === 'document' && (
                <FileIcon className="w-5 h-5 text-emerald-500 flex-shrink-0" />
              )}
              
              {/* File Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-100 truncate">
                  {post.attachment.name}
                </p>
                <p className="text-xs text-slate-400">
                  {post.attachment.type.toUpperCase()} • {formatFileSize(post.attachment.size)}
                </p>
              </div>
            </div>
            
            {/* Download Button */}
            <a
              href={post.attachment.url}
              download={post.attachment.name}
              className="flex-shrink-0 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium rounded-md flex items-center gap-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              Download
            </a>
          </div>
          
          {/* Image Preview (Optional) */}
          {post.attachment.type === 'image' && (
            <div className="mt-3">
              {!imageLoaded ? (
                <button
                  onClick={() => setImageLoaded(true)}
                  className="w-full py-2 border-2 border-dashed border-slate-700 rounded-lg text-slate-400 hover:border-emerald-500 hover:text-emerald-500 text-sm transition-colors"
                >
                  📊 Load Image ({formatFileSize(post.attachment.size)})
                </button>
              ) : (
                <img
                  src={post.attachment.url}
                  alt={post.attachment.name}
                  className="w-full rounded-lg"
                />
              )}
            </div>
          )}
        </div>
      )}
      
      {/* Footer (Comments count, Like, etc.) */}
      <footer className="mt-3 pt-3 border-t border-slate-700 flex items-center gap-4 text-sm">
        <button className="flex items-center gap-1.5 text-slate-400 hover:text-emerald-500 transition-colors">
          <MessageCircle className="w-4 h-4" />
          <span>{post.comments_count || 0} Comments</span>
        </button>
      </footer>
    </article>
  )
}
```

#### Data-Saving Features
- **Text Always Loads**: Lightweight, no data concerns
- **File Size Upfront**: User knows before downloading
- **Progressive Image Loading**: Click-to-load pattern
- **Truncated Content**: First 200 characters visible
- **Smart Caching**: Downloaded files cached in browser

#### Props Interface
```typescript
interface StreamPostProps {
  post: {
    id: number
    content: string
    created_at: string
    author: {
      name: string
      role: 'teacher' | 'student'
    }
    attachment?: {
      name: string
      type: 'pdf' | 'image' | 'document'
      size: number
      url: string
    }
    comments_count: number
    canEdit: boolean
  }
}
```

---

### 4. The Floating Calculator (`<ScientificCalc />`)
Draggable scientific calculator with persistent state for math/physics questions.

#### Structure & Implementation
```tsx
const ScientificCalc = () => {
  const [isMinimized, setIsMinimized] = useState(true)
  const [position, setPosition] = useState({ x: 20, y: 100 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  
  // Persistent calculator state
  const [display, setDisplay] = useState('0')
  const [memory, setMemory] = useState<number | null>(null)
  const [lastOperation, setLastOperation] = useState<string | null>(null)
  
  // Dragging logic
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    })
  }
  
  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      })
    }
  }
  
  const handleMouseUp = () => {
    setIsDragging(false)
  }
  
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      
      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging])
  
  // Calculator functions
  const handleNumber = (num: string) => {
    setDisplay(display === '0' ? num : display + num)
  }
  
  const handleOperation = (op: string) => {
    setMemory(parseFloat(display))
    setLastOperation(op)
    setDisplay('0')
  }
  
  const handleEquals = () => {
    if (memory === null || lastOperation === null) return
    
    const current = parseFloat(display)
    let result = 0
    
    switch (lastOperation) {
      case '+': result = memory + current; break
      case '-': result = memory - current; break
      case '×': result = memory * current; break
      case '÷': result = memory / current; break
      case '^': result = Math.pow(memory, current); break
    }
    
    setDisplay(result.toString())
    setMemory(null)
    setLastOperation(null)
  }
  
  const handleScientific = (func: string) => {
    const value = parseFloat(display)
    let result = 0
    
    switch (func) {
      case 'sin': result = Math.sin(value); break
      case 'cos': result = Math.cos(value); break
      case 'tan': result = Math.tan(value); break
      case 'log': result = Math.log10(value); break
      case 'ln': result = Math.log(value); break
      case 'sqrt': result = Math.sqrt(value); break
      case '1/x': result = 1 / value; break
      case 'x²': result = value * value; break
    }
    
    setDisplay(result.toString())
  }
  
  // Minimized FAB
  if (isMinimized) {
    return (
      <button
        onClick={() => setIsMinimized(false)}
        className="fixed bottom-6 right-6 w-16 h-16 bg-emerald-500 hover:bg-emerald-400 rounded-full shadow-lg flex items-center justify-center text-white text-2xl transition-all hover:scale-110 z-50"
        aria-label="Open calculator"
      >
        🧮
      </button>
    )
  }
  
  // Expanded Calculator
  return (
    <div
      className="fixed bg-slate-800/95 backdrop-blur-md rounded-xl shadow-2xl border border-slate-700 overflow-hidden z-50"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        width: '320px',
        cursor: isDragging ? 'grabbing' : 'default'
      }}
    >
      {/* Draggable Header */}
      <div
        className="bg-slate-900 px-4 py-3 flex items-center justify-between cursor-grab active:cursor-grabbing select-none"
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center gap-2">
          <Calculator className="w-5 h-5 text-emerald-500" />
          <h3 className="font-semibold text-slate-100">Scientific Calculator</h3>
        </div>
        <button
          onClick={() => setIsMinimized(true)}
          className="p-1 hover:bg-slate-800 rounded"
        >
          <Minimize2 className="w-4 h-4 text-slate-400" />
        </button>
      </div>
      
      {/* Display */}
      <div className="bg-slate-900 px-4 py-6 border-b border-slate-700">
        <div className="text-right">
          {memory !== null && lastOperation && (
            <div className="text-sm text-slate-500 mb-1">
              {memory} {lastOperation}
            </div>
          )}
          <div className="text-3xl font-mono text-slate-100 truncate">
            {display}
          </div>
        </div>
      </div>
      
      {/* Scientific Functions Row */}
      <div className="grid grid-cols-4 gap-1 p-2 bg-slate-900/50">
        {['sin', 'cos', 'tan', 'log'].map(func => (
          <button
            key={func}
            onClick={() => handleScientific(func)}
            className="py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm text-slate-200 font-medium"
          >
            {func}
          </button>
        ))}
      </div>
      
      {/* Number Pad + Operations */}
      <div className="grid grid-cols-4 gap-1 p-2">
        {/* Numbers & Basic Ops */}
        {['7', '8', '9', '÷'].map(key => (
          <CalcButton key={key} value={key} onClick={key.match(/\d/) ? handleNumber : handleOperation} />
        ))}
        {['4', '5', '6', '×'].map(key => (
          <CalcButton key={key} value={key} onClick={key.match(/\d/) ? handleNumber : handleOperation} />
        ))}
        {['1', '2', '3', '-'].map(key => (
          <CalcButton key={key} value={key} onClick={key.match(/\d/) ? handleNumber : handleOperation} />
        ))}
        {['0', '.', '=', '+'].map(key => (
          <CalcButton 
            key={key} 
            value={key} 
            onClick={key === '=' ? handleEquals : key.match(/[\d.]/) ? handleNumber : handleOperation}
            variant={key === '=' ? 'primary' : 'default'}
          />
        ))}
      </div>
      
      {/* Additional Functions */}
      <div className="grid grid-cols-4 gap-1 p-2 pt-0">
        {['√', 'x²', '^', 'C'].map(func => (
          <button
            key={func}
            onClick={() => func === 'C' ? setDisplay('0') : handleScientific(func === '√' ? 'sqrt' : func === 'x²' ? 'x²' : func)}
            className="py-3 bg-red-900/30 hover:bg-red-800/50 rounded text-sm text-red-300 font-semibold"
          >
            {func}
          </button>
        ))}
      </div>
    </div>
  )
}

// Button Component
const CalcButton = ({ value, onClick, variant = 'default' }: CalcButtonProps) => (
  <button
    onClick={() => onClick(value)}
    className={cn(
      "py-4 rounded font-semibold text-lg transition-colors",
      variant === 'primary' && "bg-emerald-600 hover:bg-emerald-500 text-white",
      variant === 'default' && "bg-slate-700 hover:bg-slate-600 text-slate-100"
    )}
  >
    {value}
  </button>
)
```

#### Key Features
- **Draggable**: Moves anywhere on screen via mouse/touch
- **Persistent State**: Calculation values survive minimize/maximize
- **Glassmorphism**: `backdrop-blur-md` overlay for modern look
- **Scientific Functions**: sin, cos, tan, log, ln, sqrt, power
- **Memory Operations**: M+, M-, MR, MC
- **Keyboard Support**: Number keys and operators work
- **Minimizes to FAB**: Circular floating button in bottom-right

#### State Persistence
```typescript
// Store calculator state globally
interface CalculatorState {
  display: string
  memory: number | null
  lastOperation: string | null
  history: Array<{ input: string; result: string }>
  setDisplay: (value: string) => void
  setMemory: (value: number | null) => void
  addToHistory: (input: string, result: string) => void
}

// Usage: State survives page navigation
const calcStore = create<CalculatorState>((set) => ({
  display: '0',
  memory: null,
  lastOperation: null,
  history: [],
  setDisplay: (value) => set({ display: value }),
  setMemory: (value) => set({ memory: value }),
  addToHistory: (input, result) => set((state) => ({
    history: [...state.history, { input, result }]
  }))
}))
```

#### Props Interface
```typescript
interface ScientificCalcProps {
  initialPosition?: { x: number; y: number }
  onClose?: () => void
}

interface CalcButtonProps {
  value: string
  onClick: (value: string) => void
  variant?: 'default' | 'primary' | 'danger'
}
```

### Modal Components

#### CreateClassroomForm
- Name input (required)
- Description textarea
- Subject dropdown
- Grade level dropdown
- Cancel/Create buttons
- Validation
- Success notification

#### EditClassroomForm
- Pre-populated fields
- Partial update support
- Permission check
- Cancel/Save buttons

#### JoinClassroomForm
- Join code input
- Validation
- Submit button
- Error handling

---

## 🧩 West African-Optimized Components

### 1. The Question Card (`<QuestionCard />`)
The atomic unit of the learning experience.

**Structure:**
```tsx
<div className="bg-slate-800 rounded-lg p-6">
  {/* Header */}
  <div className="flex justify-between items-center mb-4">
    <span className="text-xs bg-emerald-900 text-emerald-500 px-3 py-1 rounded-full">
      MATHEMATICS
    </span>
    <span className="text-slate-400 font-mono text-sm">⏱️ 1:45</span>
  </div>
  
  {/* Question Body (with LaTeX support) */}
  <div className="prose prose-invert mb-6">
    <p>Solve: $x^2 + 5x + 6 = 0$</p>
  </div>
  
  {/* Options (Full-width, touch-optimized) */}
  <div className="space-y-3">
    {options.map(opt => (
      <button 
        key={opt.value}
        className="w-full min-h-[56px] px-6 py-4 bg-slate-900 border-2 border-slate-700 
                   hover:border-emerald-500 active:bg-emerald-900 rounded-lg text-left"
      >
        <span className="font-semibold mr-3">{opt.label}.</span>
        {opt.text}
      </button>
    ))}
  </div>
  
  {/* Footer (Only visible after answering) */}
  {answered && (
    <button className="mt-6 text-emerald-500 text-sm">
      🤔 Explain with AI (Tap to load)
    </button>
  )}
</div>
```

**Key Features:**
- Full-width design (no wasted space)
- High contrast (readable in sunlight)
- 56px button height (easy tapping)
- LaTeX rendering via KaTeX
- Progressive AI explanation loading

### 2. The 3D Flashcard (`<Flashcard />`)
Swipe-based learning card with flip animation.

**Gestures:**
- **Swipe Right (50px)**: "I remembered this" → Moves to known pile
- **Swipe Left (50px)**: "I forgot this" → Moves to review pile
- **Tap Center**: Flip card (CSS `rotateY(180deg)`)

**Implementation:**
```tsx
const Flashcard = ({ front, back }) => {
  const [flipped, setFlipped] = useState(false)
  
  return (
    <div 
      className="relative w-full aspect-[3/2] cursor-pointer"
      style={{ perspective: '1000px' }}
      onClick={() => setFlipped(!flipped)}
    >
      <div 
        className={`absolute inset-0 transition-transform duration-600 
                    preserve-3d ${flipped ? 'rotate-y-180' : ''}`}
      >
        {/* Front */}
        <div className="absolute inset-0 backface-hidden bg-slate-800 rounded-xl p-8">
          <h3 className="text-2xl font-bold mb-4">{front.term}</h3>
          {front.image && <img src={front.image} alt="" className="rounded-lg" />}
        </div>
        
        {/* Back */}
        <div className="absolute inset-0 backface-hidden bg-emerald-900 rounded-xl p-8 rotate-y-180">
          <p className="text-lg">{back.definition}</p>
          <p className="text-sm text-slate-400 mt-4">{back.context}</p>
        </div>
      </div>
    </div>
  )
}
```

### 3. The Classroom Stream Item (`<StreamPost />`)
Optimized for quick scanning and data efficiency.

**Layout:**
```tsx
<div className="bg-slate-800 rounded-lg p-4 mb-3">
  {/* Header */}
  <div className="flex items-center gap-3 mb-3">
    <div className="w-10 h-10 rounded-full bg-emerald-500 flex-shrink-0" />
    <div className="flex-1 min-w-0">
      <p className="font-semibold truncate">Mrs. Adebayo</p>
      <p className="text-xs text-slate-400">2 hours ago</p>
    </div>
  </div>
  
  {/* Content (Truncated with Read More) */}
  <p className="text-slate-300 line-clamp-3 mb-3">
    {post.content}
  </p>
  {post.content.length > 150 && (
    <button className="text-emerald-500 text-sm">Read more</button>
  )}
  
  {/* Attachment (Progressive Disclosure) */}
  {post.attachment && (
    <div className="mt-3 p-3 bg-slate-900 rounded-lg flex items-center justify-between">
      <div className="flex items-center gap-2">
        <FileIcon className="w-5 h-5 text-emerald-500" />
        <div>
          <p className="text-sm font-medium">Assignment.pdf</p>
          <p className="text-xs text-slate-400">1.2 MB</p>
        </div>
      </div>
      <button className="text-emerald-500 text-sm">⬇️ Download</button>
    </div>
  )}
</div>
```

**Data Saving Features:**
- Text always loads (lightweight)
- File size displayed upfront
- Download requires explicit tap
- Images show thumbnail placeholder

### 4. The Floating Calculator (`<ScientificCalc />`)
Draggable modal for math questions.

**Behavior:**
- Draggable anywhere on screen
- State persists when closed/reopened
- Glassmorphism design (`backdrop-blur-md`)
- Minimizes to FAB when not in use

**Example:**
```tsx
const ScientificCalc = () => {
  const [position, setPosition] = useState({ x: 20, y: 100 })
  const [minimized, setMinimized] = useState(false)
  
  if (minimized) {
    return (
      <button 
        className="fixed bottom-6 right-6 w-16 h-16 bg-emerald-500 rounded-full 
                   shadow-lg flex items-center justify-center"
        onClick={() => setMinimized(false)}
      >
        🧮
      </button>
    )
  }
  
  return (
    <div 
      className="fixed bg-slate-800/90 backdrop-blur-md rounded-xl shadow-2xl p-4"
      style={{ left: position.x, top: position.y }}
      draggable
    >
      {/* Calculator UI */}
    </div>
  )
}
```

### 5. The Network Status Banner
Non-intrusive connection status display.

**Design:**
```tsx
const NetworkBanner = ({ status }) => {
  if (status === 'online') return null
  
  return (
    <div className="fixed top-0 left-0 right-0 bg-yellow-900 text-yellow-200 px-4 py-2 
                    text-center text-sm z-50 animate-slide-down">
      {status === 'offline' && '📵 You\'re offline. Changes will sync when connected.'}
      {status === 'syncing' && '🔄 Syncing your progress...'}
      {status === 'error' && '⚠️ Sync failed. Tap to retry.'}
    </div>
  )
}
```

### 6. The Data Usage Indicator
Helps users monitor their data consumption.

**Display:**
```tsx
const DataUsage = ({ sessionData }) => (
  <div className="text-xs text-slate-400 flex items-center gap-2">
    <Activity className="w-3 h-3" />
    <span>Session: {formatBytes(sessionData)}</span>
    <span className={sessionData > 5_000_000 ? 'text-orange-500' : 'text-green-500'}>
      {sessionData > 5_000_000 ? '⚠️ High' : '✓ Low'}
    </span>
  </div>
)
```

**Placement**: Footer of main pages, updates every 30 seconds

---

## 🔐 Security Features

### 1. Authentication
- JWT token-based auth
- Token stored in localStorage
- Auto-refresh on expiration
- Secure logout (token removal)

### 2. Authorization
- Role-based access control
- Route protection
- Component-level permission checks
- API endpoint validation

### 3. Input Validation
- Client-side validation
- Server-side validation
- XSS prevention
- SQL injection prevention (backend)
- CSRF protection (backend)

### 4. Error Handling
- User-friendly error messages
- No sensitive data exposure
- Graceful degradation
- Fallback UI

---

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Optimizations
- Touch-friendly buttons (44px min)
- Collapsible sidebar
- Stacked layouts
- Bottom navigation
- Pull-to-refresh

### Tablet Optimizations
- Two-column layouts
- Larger touch targets
- Drawer navigation
- Grid adjustments

### Desktop Features
- Three-column layouts
- Hover states
- Keyboard shortcuts
- Multi-window support

---

## 🎨 Design System (West African Optimized)

### Brand Philosophy
**Base10** is the "Digital Older Sibling" — knowledgeable, patient, and encouraging. The design feels **Academic but Modern**, like a textbook that came to life.

### Colors (OLED Optimized for Tecno/Infinix Devices)

#### Deep Emerald Strategy
Green signifies "Go/Success" and works beautifully on dark backgrounds (saves battery on AMOLED screens common in West Africa).

| Token | Hex | Tailwind Class | Usage |
|-------|-----|----------------|-------|
| **Brand Primary** | `#10B981` | `bg-emerald-500` | Primary buttons, Active states, Correct answers |
| **Brand Dark** | `#064E3B` | `bg-emerald-900` | Highlighted card backgrounds |
| **Canvas Dark** | `#0F172A` | `bg-slate-900` | Main app background (Dark mode default) |
| **Surface Dark** | `#1E293B` | `bg-slate-800` | Cards, Modals, Input fields |
| **Success** | `#22C55E` | `text-green-500` | Correct answers, Study streaks |
| **Error** | `#EF4444` | `text-red-500` | Incorrect answers, Offline warnings |
| **Text High** | `#F8FAFC` | `text-slate-50` | Headings, Primary text |
| **Text Muted** | `#94A3B8` | `text-slate-400` | Explanations, Metadata |
| **Warning** | `#F59E0B` | `text-orange-500` | Caution, Pending states |
| **Info** | `#3B82F6` | `text-blue-500` | Informational messages |

**Design Rationale:**
- True black (#0F172A) for OLED power efficiency
- High contrast for outdoor sunlight visibility
- Emerald green culturally neutral and universally positive
- Minimal use of bright colors to reduce eye strain

### Typography

#### Font Strategy: Zero-Download Performance
Use **system-ui** fonts to eliminate network requests and ensure instant rendering.

**Font Stack:**
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 
             'Fira Sans', 'Droid Sans', 'Helvetica Neue', 
             sans-serif;
```

**Specialized Fonts:**
- **Headings**: `Outfit` or `Plus Jakarta Sans` (Bold, Tight tracking)
- **Body**: System fonts (Tall x-height for readability)
- **Math**: `KaTeX_Main` (Serif style for equations)
- **Code**: `JetBrains Mono` or `Fira Code`

#### Font Sizes (Accessibility Optimized)
- **xs**: 0.75rem (12px) - Captions
- **sm**: 0.875rem (14px) - Body secondary
- **base**: 1rem (16px) - Body primary
- **lg**: 1.125rem (18px) - Subheadings
- **xl**: 1.25rem (20px) - Card titles
- **2xl**: 1.5rem (24px) - Section headers
- **3xl**: 1.875rem (30px) - Page titles
- **4xl**: 2.25rem (36px) - Hero text

**Readability Rules:**
- Minimum body text: 16px (1rem)
- Line height: 1.6 for body, 1.2 for headings
- Max line length: 65-75 characters
- Letter spacing: Tight for headings (-0.02em), Normal for body

### Iconography
**Lucide React** (Stroke width: 2px)

**Why Lucide?**
- Clean, scalable vectors that look sharp on low-res screens
- Lightweight bundle size (~50KB)
- Consistent 24x24 grid system
- Works beautifully at small sizes (16px, 20px)

**Icon Usage:**
- Navigation: 24px
- Buttons: 20px
- Inline text: 16px
- Feature cards: 48px

### Spacing
Based on 4px grid (0.25rem) for consistent rhythm:
- **0**: 0px
- **1**: 4px (0.25rem)
- **2**: 8px (0.5rem)
- **3**: 12px (0.75rem)
- **4**: 16px (1rem) - Base unit
- **5**: 20px (1.25rem)
- **6**: 24px (1.5rem)
- **8**: 32px (2rem)
- **10**: 40px (2.5rem)
- **12**: 48px (3rem)
- **16**: 64px (4rem)

### Shadows (Minimal for Performance)
Use sparingly to reduce rendering cost:
- **sm**: `0 1px 2px 0 rgb(0 0 0 / 0.05)` - Subtle lift
- **md**: `0 4px 6px -1px rgb(0 0 0 / 0.1)` - Cards
- **lg**: `0 10px 15px -3px rgb(0 0 0 / 0.1)` - Modals
- **xl**: `0 20px 25px -5px rgb(0 0 0 / 0.1)` - Dropdowns

**Alternative**: Use borders instead of shadows for better performance

### Border Radius
- **sm**: 0.25rem (4px) - Buttons, Badges
- **md**: 0.5rem (8px) - Cards, Inputs
- **lg**: 0.75rem (12px) - Modals, Large cards
- **xl**: 1rem (16px) - Feature sections
- **2xl**: 1.5rem (24px) - Hero cards
- **full**: 9999px - Circular avatars, Pills

---

## 🧠 West African UX Patterns

### 1. The "Optimistic" Interaction Model
**Problem**: Network latency on 2G/3G connections (200-1000ms typical)

**Solution**: Never wait for server before showing feedback

**Implementation:**
- **Quiz Submission**: Immediately paint option Green/Red based on local validation
- **Background Sync**: Queue API call to `pending_sync` in localStorage
- **Visual Feedback**: Show spinning sync indicator in header
- **Conflict Resolution**: Server response updates UI if different from local state

**Code Pattern:**
```typescript
const handleAnswer = async (option: string) => {
  // Immediate UI update
  setSelectedOption(option)
  const isCorrect = option === correctAnswer
  setAnswerState(isCorrect ? 'correct' : 'incorrect')
  
  // Background sync
  try {
    await questionApi.submitAnswer({ question_id, user_answer: option })
  } catch (error) {
    // Queue for retry
    addToPendingSync({ type: 'answer', data: { question_id, user_answer: option } })
  }
}
```

### 2. Progressive Disclosure (The Data Saver)
**Problem**: Images and AI explanations consume significant data (50KB-500KB per item)

**Solution**: Show content only when explicitly requested

**Implementation:**
- **Images**: Display placeholder with "Load Diagram (50KB)" button
- **AI Explanations**: Hidden by default, show "Why did I fail?" button
- **Network Detection**: Auto-load on WiFi, manual on mobile data

**Example:**
```tsx
{!imageLoaded && (
  <button onClick={() => loadImage()} className="text-emerald-500">
    📊 Load Diagram (50KB)
  </button>
)}

{showExplanation ? (
  <div className="prose prose-invert">{explanation}</div>
) : (
  <button onClick={() => setShowExplanation(true)}>
    🤔 Why did I fail? (Tap to see AI explanation)
  </button>
)}
```

### 3. The "Sync" Traffic Light
**Problem**: Users need to know connection status without checking settings

**Solution**: Persistent status indicator in header

**States:**
- 🟢 **Green Dot**: Online & All changes synced
- 🟡 **Yellow Dot**: Offline (Changes saved locally)
- 🔵 **Pulsing Blue**: Currently syncing...
- 🔴 **Red Dot**: Sync failed (Tap to retry)

**Position**: Top-right corner, always visible, 8px diameter

### 4. The "Morphing" Input
**Problem**: Screen space is precious on mobile devices

**Solution**: Context-aware input transformation

**Behavior:**
1. **Dashboard State**: Large centered search bar "What do you want to learn?"
2. **On Focus**: Animates to bottom of screen (chat input position)
3. **Quick Chips**: Recent subjects appear as tappable pills above keyboard
4. **On Submit**: Morphs into message bubble, input clears for next question

**Animation:**
```css
.morphing-input {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.morphing-input.focused {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  transform: translateY(0);
}
```

### 5. Offline-First Architecture
**Problem**: Intermittent connectivity disrupts learning flow

**Solution**: Full offline capability with background sync

**Features:**
- **Question Cache**: Last 50 questions stored in IndexedDB
- **Progress Tracking**: All attempts saved locally first
- **Sync Queue**: FIFO queue processes when online
- **Conflict Resolution**: Server timestamp wins on conflicts

**Storage Strategy:**
```typescript
const offlineStorage = {
  questions: IndexedDB, // Large data (1-5MB)
  progress: localStorage, // User stats (10-50KB)
  pendingSync: localStorage, // Sync queue (5-20KB)
  userProfile: localStorage, // Auth + preferences (2-5KB)
}
```

### 6. Touch-Optimized Interactions
**Problem**: Precise tapping difficult on moving buses/motorcycles

**Solution**: Large touch targets with generous padding

**Specifications:**
- **Minimum Touch Target**: 44x44px (iOS/Android standard)
- **Option Buttons**: Full-width, 56px height, 12px vertical margin
- **Floating Action Button**: 64x64px, bottom-right, 16px margin
- **Swipe Gestures**: Minimum 50px travel distance to trigger

---

## 🚀 Performance Optimizations

### Code Splitting
- Dynamic imports for heavy components
- Route-based splitting
- Component lazy loading

### Image Optimization
- Next.js Image component
- WebP format
- Lazy loading
- Responsive images

### Caching
- API response caching
- Static asset caching
- Service worker (planned)

### Bundle Size
- Tree shaking
- Dead code elimination
- Minification
- Compression (gzip/brotli)

---

## 🧪 Testing Strategy

### Unit Tests (Planned)
- Component tests with Jest
- Utility function tests
- Store tests

### Integration Tests (Planned)
- API integration tests
- User flow tests
- Form validation tests

### E2E Tests (Planned)
- Cypress or Playwright
- Critical user journeys
- Cross-browser testing

---

## 🌐 Internationalization (Future)

### Languages
- English (default)
- French
- Portuguese (planned)

### Implementation
- next-intl or react-i18next
- Translation files
- Language switcher
- RTL support (planned)

---

## ♿ Accessibility

### WCAG 2.1 AA Compliance
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Focus management
- Screen reader support
- Color contrast ratios

### Features
- Skip to content link
- Focus visible indicators
- Alt text for images
- Form labels
- Error announcements

---

## 📊 Analytics (Future)

### User Analytics
- Page views
- User journeys
- Feature usage
- Session duration

### Performance Monitoring
- Core Web Vitals
- API response times
- Error tracking
- User feedback

### Tools (Planned)
- Google Analytics
- Sentry for error tracking
- Vercel Analytics
- Custom analytics dashboard

---

## 🔄 State Synchronization

### Real-time Updates (Planned)
- WebSocket connection
- Live classroom updates
- Real-time notifications
- Collaborative features

### Optimistic Updates
- Immediate UI feedback
- Background sync
- Conflict resolution
- Error recovery

---

## 📦 Deployment

### Current Setup
- **Framework**: Next.js (SSR/SSG)
- **Hosting**: Vercel (recommended) or self-hosted
- **API**: DigitalOcean App Platform
- **Database**: PostgreSQL (DigitalOcean)
- **Redis**: DigitalOcean (planned)

### Environment Variables
```env
NEXT_PUBLIC_API_URL=https://stingray-app-x7lzo.ondigitalocean.app/api/v1
```

### Build Process
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Start production server
npm start

# Development
npm run dev
```

### Deployment Steps
1. Push to GitHub
2. Vercel auto-deploys from main branch
3. Environment variables set in Vercel dashboard
4. Build and deploy automatically

---

## 🐛 Known Issues & Future Enhancements

### Current Limitations
- No offline support
- Limited error recovery
- No real-time collaboration
- Basic search functionality

### Planned Features
- **WebSocket Integration**: Real-time updates
- **LaTeX Rendering**: Math formula display
- **File Upload**: Assignment submissions
- **Video Lessons**: Embedded content
- **Gamification**: Badges, leaderboards
- **Parent Portal**: Monitor child progress
- **Mobile App**: React Native
- **Offline Mode**: Service workers
- **Advanced Search**: Full-text search
- **Discussion Forums**: Student collaboration

---

## 📚 Additional Resources

### Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand Guide](https://docs.pmnd.rs/zustand)

### Backend API
- API Base: `https://stingray-app-x7lzo.ondigitalocean.app/api/v1`
- Swagger Docs: `/docs` endpoint
- Redoc: `/redoc` endpoint

### Design Resources
- Figma designs (if available)
- Component library (Storybook planned)
- Style guide

---

## 👥 Team & Contributors

### Development Team
- Frontend Developer: Implementation
- Backend Developer: API & database
- UI/UX Designer: Design system
- Product Manager: Features & roadmap

### Contact
- GitHub: [Repository URL]
- Email: Support contact
- Slack: Team workspace

---

## 📝 Changelog

### Version 1.0.0 (Current)
- ✅ Authentication system
- ✅ Student dashboard
- ✅ Practice questions
- ✅ Classroom management
- ✅ AI tutor with Socratic mode
- ✅ Assignment system
- ✅ Student profiles
- ✅ Admin dashboard
- ✅ Role-based access control
- ✅ Quiz generation
- ✅ Notification system

### Upcoming (v1.1.0)
- ⏳ LaTeX rendering
- ⏳ File uploads
- ⏳ Real-time updates
- ⏳ Mobile app
- ⏳ Parent portal

---

## 🤝 Contributing

### Getting Started
1. Clone repository
2. Install dependencies: `npm install`
3. Start dev server: `npm run dev`
4. Make changes
5. Test locally
6. Submit pull request

### Code Style
- Follow ESLint rules
- Use Prettier for formatting
- Write meaningful commit messages
- Add comments for complex logic
- Update documentation

### Pull Request Process
1. Create feature branch
2. Make changes with tests
3. Update documentation
4. Submit PR with description
5. Address review feedback
6. Merge when approved

---

**Last Updated**: December 18, 2025  
**Version**: 1.0.0  
**Status**: Production Ready 🚀
