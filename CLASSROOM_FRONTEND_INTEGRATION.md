# Classroom System - Frontend Integration Guide

## Overview

The classroom system is a Google Classroom-style LMS with:
- **Stream**: Announcements, discussions, and threaded comments
- **Materials**: File/resource sharing with asset integration
- **People**: Member management (students & teacher)
- **Assignments**: Manual tasks, submissions, and AI-assisted grading
- **Grades**: Student gradebook with offline sync

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLASSROOM SYSTEM                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Stream  │  │ Materials│  │  People  │             │
│  │          │  │          │  │          │             │
│  │ • Posts  │  │ • Files  │  │ • List   │             │
│  │ • Reply  │  │ • Links  │  │ • Invite │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Assignments│ │Submissions│ │  Grades  │             │
│  │          │  │          │  │          │             │
│  │ • Create │  │ • Submit │  │ • View   │             │
│  │ • AI Gen │  │ • Photos │  │ • Sync   │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Key Models

### 1. Classroom
```typescript
interface Classroom {
  id: number;
  teacher_id: number;
  name: string;
  description: string;
  join_code: string;
  is_active: boolean;
  subject: string;        // "mathematics", "biology", etc.
  grade_level: string;    // "grade-7", "grade-12", etc.
  created_at: string;
  
  // Computed
  student_count?: number;
}
```

### 2. ClassroomPost (Stream)
```typescript
interface ClassroomPost {
  id: number;
  classroom_id: number;
  author_id: number;
  author_name: string;
  content: string;
  post_type: "announcement" | "discussion" | "assignment_alert";
  parent_post_id: number | null;  // null = top-level, else reply
  attachment_url: string | null;
  created_at: string;
  
  // For UI
  replies?: ClassroomPost[];     // Nested comments
}
```

### 3. ClassroomMaterial
```typescript
interface ClassroomMaterial {
  id: number;
  classroom_id: number;
  title: string;
  description: string;
  file_url: string;              // Link to Assets service
  file_type: "pdf" | "image" | "video" | "link";
  uploaded_by: number;
  uploader_name: string;
  created_at: string;
}
```

### 4. Assignment
```typescript
interface Assignment {
  id: number;
  classroom_id: number;
  title: string;
  description: string;
  assignment_type: "quiz" | "manual" | "essay";
  max_points: number;
  due_date: string;
  is_ai_generated: boolean;
  status: "draft" | "published" | "archived";
  created_at: string;
  
  // For teacher view
  submission_count?: number;
  graded_count?: number;
}
```

### 5. Submission
```typescript
interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  student_name: string;
  submission_type: "essay" | "photo";
  text_response: string | null;
  photo_url: string | null;
  
  // AI grading (teacher sees both)
  ai_suggested_score: number | null;
  ai_feedback_draft: string | null;
  
  // Final grade (teacher approves)
  final_score: number | null;
  final_feedback: string | null;
  is_graded: boolean;
  
  submitted_at: string;
  graded_at: string | null;
}
```

## API Endpoints

### Teacher Workflows

#### 1. Create Classroom
```typescript
POST /api/v1/classrooms
Authorization: Bearer {teacher_token}

Request:
{
  "name": "Form 3 Biology",
  "description": "Advanced biology concepts",
  "subject": "biology",
  "grade_level": "grade-10"
}

Response:
{
  "id": 15,
  "name": "Form 3 Biology",
  "join_code": "ABC123",  // Students use this to join
  "student_count": 0,
  "created_at": "2025-12-17T08:00:00Z"
}
```

**Frontend Implementation:**
```typescript
async function createClassroom(data: ClassroomCreate) {
  const response = await fetch(`${API_BASE}/api/v1/classrooms`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  return response.json();
}
```

#### 2. Post Announcement
```typescript
POST /api/v1/classrooms/{classroom_id}/announce
Authorization: Bearer {teacher_token}

Request:
{
  "content": "Quiz tomorrow on photosynthesis!",
  "post_type": "announcement",
  "attachment_url": null
}

Response:
{
  "id": 42,
  "author_name": "Mr. Jalloh",
  "content": "Quiz tomorrow on photosynthesis!",
  "created_at": "2025-12-17T08:30:00Z"
}
```

#### 3. Create Manual Assignment
```typescript
POST /api/v1/classrooms/{classroom_id}/assignments/manual
Authorization: Bearer {teacher_token}

Request:
{
  "title": "Essay: Climate Change",
  "description": "Write 500 words on causes of climate change",
  "assignment_type": "essay",
  "max_points": 20,
  "due_date": "2025-12-20T23:59:59Z"
}

Response:
{
  "id": 88,
  "title": "Essay: Climate Change",
  "status": "published",
  "created_at": "2025-12-17T09:00:00Z"
}
```

#### 4. View Submissions & Grade
```typescript
// Get all submissions for an assignment
GET /api/v1/classrooms/assignments/{assignment_id}/submissions
Authorization: Bearer {teacher_token}

Response:
[
  {
    "id": 201,
    "student_name": "Fatima Kamara",
    "text_response": "Climate change is caused by...",
    "ai_suggested_score": 16,           // AI draft
    "ai_feedback_draft": "Good analysis, but missing...",
    "final_score": null,                // Teacher hasn't graded yet
    "is_graded": false,
    "submitted_at": "2025-12-18T14:30:00Z"
  }
]

// Grade a submission (approve AI suggestion or manual)
POST /api/v1/classrooms/submissions/{submission_id}/grade
Authorization: Bearer {teacher_token}

Request:
{
  "score": 18,                          // Teacher can adjust AI score
  "feedback": "Good work! Add more examples next time."
}

Response:
{
  "id": 201,
  "final_score": 18,
  "final_feedback": "Good work! Add more examples next time.",
  "is_graded": true,
  "graded_at": "2025-12-18T15:00:00Z"
}
```

#### 5. Upload Material
```typescript
POST /api/v1/classrooms/{classroom_id}/materials
Authorization: Bearer {teacher_token}

Request:
{
  "title": "Photosynthesis Diagram",
  "description": "Study this for the quiz",
  "file_url": "https://assets.base10.edu/diagrams/photo.png",
  "file_type": "image"
}

Response:
{
  "id": 55,
  "title": "Photosynthesis Diagram",
  "uploader_name": "Mr. Jalloh",
  "created_at": "2025-12-17T10:00:00Z"
}
```

### Student Workflows

#### 1. Join Classroom
```typescript
POST /api/v1/classrooms/join
Authorization: Bearer {student_token}

Request:
{
  "join_code": "ABC123"  // From teacher
}

Response:
{
  "message": "Successfully joined classroom",
  "classroom_name": "Form 3 Biology",
  "teacher": "Mr. Jalloh"
}
```

#### 2. View Stream
```typescript
GET /api/v1/classrooms/{classroom_id}/stream
Authorization: Bearer {student_token}

Response:
[
  {
    "id": 42,
    "author_name": "Mr. Jalloh",
    "content": "Quiz tomorrow on photosynthesis!",
    "post_type": "announcement",
    "parent_post_id": null,
    "created_at": "2025-12-17T08:30:00Z",
    "replies": [
      {
        "id": 43,
        "author_name": "Fatima Kamara",
        "content": "What chapters should we study?",
        "parent_post_id": 42,
        "created_at": "2025-12-17T09:00:00Z",
        "replies": []
      }
    ]
  }
]
```

#### 3. Comment on Post
```typescript
POST /api/v1/classrooms/{classroom_id}/stream/{post_id}/comment
Authorization: Bearer {student_token}

Request:
{
  "content": "What chapters should we study?"
}

Response:
{
  "id": 43,
  "parent_post_id": 42,
  "author_name": "Fatima Kamara",
  "content": "What chapters should we study?",
  "created_at": "2025-12-17T09:00:00Z"
}
```

#### 4. Submit Assignment
```typescript
POST /api/v1/classrooms/assignments/{assignment_id}/submit
Authorization: Bearer {student_token}

// Essay submission
Request:
{
  "submission_type": "essay",
  "text_response": "Climate change is primarily caused by..."
}

// Photo submission (homework problems)
Request:
{
  "submission_type": "photo",
  "photo_url": "https://assets.base10.edu/submissions/photo123.jpg"
}

Response:
{
  "id": 201,
  "message": "Submission recorded",
  "submitted_at": "2025-12-18T14:30:00Z"
}
```

#### 5. View Grades
```typescript
GET /api/v1/student/grades
Authorization: Bearer {student_token}

Response:
[
  {
    "assignment_title": "Essay: Climate Change",
    "classroom_name": "Form 3 Biology",
    "final_score": 18,
    "max_points": 20,
    "final_feedback": "Good work! Add more examples next time.",
    "graded_at": "2025-12-18T15:00:00Z"
  }
]
```

## AI Teacher Integration

### 1. Generate Quiz (Teacher)
```typescript
POST /api/v1/ai/teacher/generate-quiz
Authorization: Bearer {teacher_token}

Request:
{
  "topic": "Photosynthesis",
  "count": 10,
  "level": "grade-10",
  "source_text": "Plants use sunlight to..."  // Optional
}

Response:
{
  "questions": [
    {
      "question_text": "What is the primary pigment in photosynthesis?",
      "correct_answer": "Chlorophyll",
      "wrong_answer_1": "Carotene",
      "wrong_answer_2": "Xanthophyll",
      "wrong_answer_3": "Melanin",
      "explanation": "Chlorophyll absorbs light energy...",
      "subject": "biology",
      "difficulty": "easy"
    }
    // ... 9 more questions
  ]
}
```

**Save to DB:** Teacher reviews, then saves approved questions via `/api/v1/teacher/assignments` (existing quiz creation endpoint).

### 2. Auto-Grade Submission (Teacher)
```typescript
// Single submission
POST /api/v1/ai/teacher/grade-submission/{submission_id}
Authorization: Bearer {teacher_token}

Response:
{
  "submission_id": 201,
  "ai_suggested_score": 16,
  "ai_feedback_draft": "Your essay covers the main causes well. Consider adding more specific examples and data to support your points. The structure is clear but the conclusion could be stronger.",
  "message": "AI grading complete. Review and approve."
}

// Batch grade all submissions for an assignment
POST /api/v1/ai/teacher/grade-batch
Authorization: Bearer {teacher_token}

Request:
{
  "assignment_id": 88
}

Response:
{
  "graded_count": 25,
  "message": "AI grading complete for 25 submissions. Review in submissions tab."
}
```

### 3. Class Insights (Teacher)
```typescript
GET /api/v1/ai/teacher/insights/{classroom_id}
Authorization: Bearer {teacher_token}

Response:
{
  "summary": "Overall Performance: Your class is performing well with an average accuracy of 72%. Top performers include Fatima Kamara and Ibrahim Sesay. Students struggling with cellular respiration concepts may need review sessions.",
  
  "struggling_students": [
    "Mohamed Conteh - 45% accuracy, slow response times",
    "Aminata Bangura - 52% accuracy, high guessing rate"
  ],
  
  "recommendations": [
    "Schedule review session on cellular respiration",
    "Provide additional practice problems for photosynthesis",
    "Consider one-on-one support for Mohamed and Aminata"
  ]
}
```

## Offline Sync Integration

### Pull Grades (for offline notifications)
```typescript
POST /api/v1/sync/pull
Authorization: Bearer {student_token}

Request:
{
  "last_sync": "2025-12-17T00:00:00Z"  // Last time app synced
}

Response:
{
  "new_questions": [...],
  "user_progress": {...},
  
  // NEW: Grade notifications
  "new_grades": [
    {
      "assignment_title": "Essay: Climate Change",
      "classroom_name": "Form 3 Biology",
      "score": 18,
      "max_points": 20,
      "feedback": "Good work! Add more examples next time.",
      "graded_at": "2025-12-18T15:00:00Z"
    }
  ],
  
  "leaderboard": {...},
  "server_timestamp": "2025-12-18T16:00:00Z"
}
```

**Frontend:** Show notification when `new_grades.length > 0`

## React Component Examples

### Teacher Dashboard
```typescript
function TeacherClassroomDashboard() {
  const [classrooms, setClassrooms] = useState<Classroom[]>([]);
  
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/classrooms`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setClassrooms(data));
  }, []);
  
  return (
    <div>
      <h1>My Classrooms</h1>
      <button onClick={() => setShowCreateModal(true)}>
        + Create Classroom
      </button>
      
      {classrooms.map(classroom => (
        <ClassroomCard 
          key={classroom.id}
          classroom={classroom}
          onClick={() => navigate(`/classroom/${classroom.id}`)}
        />
      ))}
    </div>
  );
}
```

### Classroom Stream View
```typescript
function ClassroomStream({ classroomId }: { classroomId: number }) {
  const [posts, setPosts] = useState<ClassroomPost[]>([]);
  const [newPost, setNewPost] = useState("");
  
  const loadStream = async () => {
    const response = await fetch(
      `${API_BASE}/api/v1/classrooms/${classroomId}/stream`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    setPosts(await response.json());
  };
  
  const postAnnouncement = async () => {
    await fetch(
      `${API_BASE}/api/v1/classrooms/${classroomId}/announce`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content: newPost,
          post_type: "announcement"
        })
      }
    );
    
    setNewPost("");
    loadStream();  // Refresh
  };
  
  return (
    <div className="stream">
      {/* Post composer (teacher only) */}
      {isTeacher && (
        <div className="composer">
          <textarea 
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder="Announce something to your class"
          />
          <button onClick={postAnnouncement}>Post</button>
        </div>
      )}
      
      {/* Stream feed */}
      {posts.map(post => (
        <StreamPost 
          key={post.id}
          post={post}
          onReply={(content) => replyToPost(post.id, content)}
        />
      ))}
    </div>
  );
}
```

### Student Grades View
```typescript
function StudentGrades() {
  const [grades, setGrades] = useState<Grade[]>([]);
  
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/student/grades`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.json())
    .then(data => setGrades(data));
  }, []);
  
  return (
    <div className="gradebook">
      <h2>My Grades</h2>
      
      {grades.map(grade => (
        <div key={grade.assignment_id} className="grade-card">
          <div className="grade-header">
            <h3>{grade.assignment_title}</h3>
            <span className="classroom">{grade.classroom_name}</span>
          </div>
          
          <div className="grade-score">
            <span className="score">{grade.final_score}</span>
            <span className="max">/ {grade.max_points}</span>
            <span className="percentage">
              {Math.round((grade.final_score / grade.max_points) * 100)}%
            </span>
          </div>
          
          {grade.final_feedback && (
            <div className="feedback">
              <strong>Teacher Feedback:</strong>
              <p>{grade.final_feedback}</p>
            </div>
          )}
          
          <span className="date">
            Graded {new Date(grade.graded_at).toLocaleDateString()}
          </span>
        </div>
      ))}
    </div>
  );
}
```

## Permission Model

| Action | Student | Teacher | Admin |
|--------|---------|---------|-------|
| View classroom stream | ✅ (if member) | ✅ (own) | ✅ |
| Post announcement | ❌ | ✅ | ✅ |
| Comment on posts | ✅ | ✅ | ✅ |
| Upload materials | ❌ | ✅ | ✅ |
| Create assignment | ❌ | ✅ | ✅ |
| Submit assignment | ✅ | ❌ | ❌ |
| View all submissions | ❌ | ✅ | ✅ |
| Grade submissions | ❌ | ✅ | ✅ |
| View own grades | ✅ | ❌ | ✅ |
| Remove student | ❌ | ✅ | ✅ |

## Offline-First Considerations

### 1. Text-First Design
- Stream posts are text-first (lightweight)
- Attachments load lazily
- Materials use progressive enhancement

### 2. Photo Compression
- Compress photos before upload (reduce from 3MB to 300KB)
- Use `image/jpeg` with quality 0.7
- Generate thumbnail previews

```typescript
async function compressPhoto(file: File): Promise<Blob> {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const MAX_WIDTH = 1200;
        const scale = MAX_WIDTH / img.width;
        
        canvas.width = MAX_WIDTH;
        canvas.height = img.height * scale;
        
        const ctx = canvas.getContext('2d')!;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob((blob) => resolve(blob!), 'image/jpeg', 0.7);
      };
      img.src = e.target!.result as string;
    };
    reader.readAsDataURL(file);
  });
}
```

### 3. Sync Strategy
- Pull new grades during regular sync
- Show badge/notification when grades available
- Cache stream posts locally (IndexedDB)
- Queue submissions when offline

## Testing Checklist

### Teacher Flow
- [ ] Create classroom
- [ ] Copy join code
- [ ] Post announcement
- [ ] Upload material (PDF/image)
- [ ] Create manual assignment
- [ ] View submissions
- [ ] Run AI auto-grading
- [ ] Review and approve grades
- [ ] View class insights

### Student Flow
- [ ] Join classroom with code
- [ ] View stream
- [ ] Comment on announcement
- [ ] Download material
- [ ] Submit essay assignment
- [ ] Submit photo assignment
- [ ] View grades
- [ ] Receive grade notification (offline sync)

### Edge Cases
- [ ] Invalid join code
- [ ] Submit after due date
- [ ] Resubmit assignment
- [ ] Large photo upload (>5MB)
- [ ] No internet (queue submission)
- [ ] Student removed from classroom

## Next Steps

1. **Build UI Components**
   - Classroom cards
   - Stream feed with nested replies
   - Assignment submission form
   - Gradebook table

2. **Integrate Assets Service**
   - Connect materials to file upload
   - Handle photo submissions
   - Generate thumbnails

3. **Add Notifications**
   - Push notifications for new posts
   - Email digest of weekly grades
   - SMS alerts for due dates

4. **Mobile Optimization**
   - Infinite scroll for stream
   - Swipe actions (delete, archive)
   - Camera integration for photo submissions
   - Offline queue management

5. **Analytics**
   - Track classroom engagement
   - Monitor AI grading accuracy
   - Measure student submission rates

---

**Backend Status:** ✅ All endpoints deployed and ready
**Documentation:** `/docs` for interactive API testing
**Support:** GitHub issues or team@base10.education
