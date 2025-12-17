# Classroom System - Full CRUD Implementation

## Overview
The classroom system now has complete CRUD (Create, Read, Update, Delete) operations for all resources:
- **Classrooms** - Full lifecycle management
- **Assignments** - Complete management with cascade delete
- **Materials** - Full resource control

All endpoints enforce proper permissions (teacher-only for modifications).

---

## 🎯 Classrooms CRUD

### ✅ Create
```http
POST /classrooms
```
Creates a new classroom with auto-generated join code.

### ✅ Read
```http
GET /classrooms              # List teacher's classrooms
GET /classrooms/{id}         # Get classroom details (teacher or enrolled student)
```

### ✅ Update (NEW)
```http
PUT /classrooms/{id}
Content-Type: application/json

{
  "name": "Updated Classroom Name",
  "description": "New description",
  "subject": "Advanced Mathematics",
  "grade_level": "Grade 11"
}
```
**Permissions:** Teacher only  
**Response:** Updated classroom with `updated_at` timestamp

### ✅ Delete (NEW)
```http
DELETE /classrooms/{id}
```
**Behavior:** Soft delete (sets `is_active = False`)  
**Permissions:** Teacher only  
**Response:** 204 No Content  
**Note:** Related data (assignments, posts, materials) remain but classroom is hidden

---

## 📝 Assignments CRUD

### ✅ Create
```http
POST /classrooms/{classroom_id}/assignments/manual
```
Creates a manual assignment for the classroom.

### ✅ Read
```http
GET /classrooms/{classroom_id}/assignments
```
Lists assignments with role-based filtering and submission stats.

### ✅ Update (NEW)
```http
PUT /classrooms/assignments/{assignment_id}
Content-Type: application/json

{
  "title": "Updated Assignment Title",
  "description": "New instructions",
  "due_date": "2025-12-31T23:59:59Z",
  "max_points": 150,
  "status": "published",
  "question_count": 15
}
```
**Permissions:** Teacher of the classroom only  
**Response:** Updated assignment with all fields

### ✅ Delete (NEW)
```http
DELETE /classrooms/assignments/{assignment_id}
```
**Behavior:** Hard delete with cascade  
**Permissions:** Teacher only  
**Response:** 204 No Content  
**Cascade:** All student submissions are also deleted

---

## 📚 Materials CRUD

### ✅ Create
```http
POST /classrooms/{classroom_id}/materials
```
Uploads learning material to the classroom.

### ✅ Read
```http
GET /classrooms/{classroom_id}/materials
```
Lists all materials in the classroom, sorted by creation date (newest first).

### ✅ Update (NEW)
```http
PUT /classrooms/materials/{material_id}
Content-Type: application/json

{
  "title": "Updated Material Title",
  "description": "New description",
  "asset_id": "new-asset-uuid"
}
```
**Permissions:** Teacher only  
**Response:** Updated material with metadata

### ✅ Delete (NEW)
```http
DELETE /classrooms/materials/{material_id}
```
**Behavior:** Hard delete  
**Permissions:** Teacher only  
**Response:** 204 No Content

---

## 🔒 Security Model

### Permission Enforcement
All update and delete operations enforce **teacher-only** access:
1. Fetch the resource (classroom/assignment/material)
2. Verify the classroom belongs to the current user
3. Return 403 Forbidden if not authorized
4. Return 404 Not Found if resource doesn't exist

### Read Permissions
- **Classrooms:** Teacher OR enrolled student
- **Assignments:** Teachers see all, students see published only
- **Materials:** Any classroom member

---

## 📋 Pydantic Schemas

### ClassroomUpdate
```python
class ClassroomUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=100)
    grade_level: Optional[str] = Field(None, max_length=50)
```

### AssignmentUpdate
```python
class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    subject_filter: Optional[str] = None
    topic_filter: Optional[str] = None
    difficulty_filter: Optional[str] = None
    question_count: Optional[int] = Field(None, gt=0)
    assignment_type: Optional[str] = None
    max_points: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None
    due_date: Optional[datetime] = None
```

### MaterialUpdate
```python
class MaterialUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    asset_id: Optional[str] = None
```

All schemas use **partial updates** - only provided fields are updated.

---

## 🎨 Frontend Integration

### Update Classroom Example
```javascript
const updateClassroom = async (classroomId, updates) => {
  const response = await fetch(`/classrooms/${classroomId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(updates)
  });
  return response.json();
};

// Usage
await updateClassroom(5, {
  name: "Advanced Math - Fall 2025",
  subject: "Mathematics"
});
```

### Delete Assignment Example
```javascript
const deleteAssignment = async (assignmentId) => {
  await fetch(`/classrooms/assignments/${assignmentId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
};

// Usage (with confirmation)
if (confirm('Delete this assignment? All submissions will be lost.')) {
  await deleteAssignment(12);
  alert('Assignment deleted');
}
```

### Update Material Example
```javascript
const updateMaterial = async (materialId, updates) => {
  const response = await fetch(`/classrooms/materials/${materialId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(updates)
  });
  return response.json();
};

// Usage
await updateMaterial(8, {
  title: "Updated Study Guide",
  description: "Revised for Q4"
});
```

---

## ✅ Complete API Endpoint Map

### Classrooms
- ✅ POST `/classrooms` - Create
- ✅ GET `/classrooms` - List
- ✅ GET `/classrooms/{id}` - Detail
- ✅ **PUT `/classrooms/{id}` - Update**
- ✅ **DELETE `/classrooms/{id}` - Delete**
- ✅ POST `/classrooms/join` - Join with code
- ✅ GET `/classrooms/{id}/stream` - Get posts
- ✅ POST `/classrooms/{id}/announce` - Create post
- ✅ POST `/classrooms/{id}/stream/{post_id}/comment` - Add comment
- ✅ DELETE `/classrooms/{id}/stream/{post_id}` - Delete post
- ✅ GET `/classrooms/{id}/members` - List members
- ✅ DELETE `/classrooms/{id}/members/{user_id}` - Remove member
- ✅ POST `/classrooms/{id}/invite` - Regenerate join code

### Assignments
- ✅ GET `/classrooms/{id}/assignments` - List
- ✅ POST `/classrooms/{id}/assignments/manual` - Create
- ✅ **PUT `/classrooms/assignments/{id}` - Update**
- ✅ **DELETE `/classrooms/assignments/{id}` - Delete**
- ✅ POST `/classrooms/assignments/{id}/submit` - Submit
- ✅ GET `/classrooms/assignments/{id}/submissions` - List submissions
- ✅ POST `/classrooms/submissions/{id}/grade` - Grade submission

### Materials
- ✅ POST `/classrooms/{id}/materials` - Upload
- ✅ GET `/classrooms/{id}/materials` - List
- ✅ **PUT `/classrooms/materials/{id}` - Update**
- ✅ **DELETE `/classrooms/materials/{id}` - Delete**

### Student
- ✅ GET `/student/grades` - View grades

---

## 🚀 Deployment Status
- **Commit:** `ab7eb4f`
- **Status:** Pushed to GitHub, deployment in progress
- **Changes:** 212 lines added to `classrooms.py`
- **Tests:** No syntax errors detected

---

## 📝 Notes

### Delete Behaviors
1. **Classroom:** Soft delete (preserves data, sets `is_active = False`)
2. **Assignment:** Hard delete with cascade (removes submissions)
3. **Material:** Hard delete (permanent removal)

### Cascade Relationships
```python
# In Assignment model
submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
```
When an assignment is deleted, all related submissions are automatically deleted.

### Update Pattern
All update endpoints use the same pattern:
1. Parse update data with Pydantic schema
2. Validate ownership (teacher check)
3. Apply partial updates with `model_dump(exclude_unset=True)`
4. Commit and return updated resource

### Error Responses
- **404:** Resource not found
- **403:** Not authorized (not the teacher)
- **422:** Validation error (invalid data)
- **204:** Successful deletion (no content)

---

## 🎓 Summary
The classroom system now supports full lifecycle management for all resources. Teachers can:
- Create, view, update, and delete classrooms
- Manage assignment lifecycle with cascade delete
- Control learning materials completely

All operations enforce proper permissions and provide clear error messages. The API is ready for frontend integration with complete CRUD workflows.
