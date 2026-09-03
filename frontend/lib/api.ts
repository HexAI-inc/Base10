import axios from 'axios'

const API_BASE_URL = 'https://stingray-app-x7lzo.ondigitalocean.app/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth endpoints
export const authApi = {
  register: (data: { 
    phone_number: string; 
    email?: string; 
    password: string; 
    full_name: string;
    role?: 'student' | 'teacher';
  }) => api.post('/auth/register', data),
  login: (username: string, password: string) => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)
    return api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
  },
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data: any) => api.patch('/auth/profile', data),
}

// Recovery endpoints
export const recoveryApi = {
  forgotPassword: (identifier: string) => 
    api.post('/recovery/forgot-password', { identifier }),
  resetPassword: (data: { identifier: string; otp: string; new_password: string }) => 
    api.post('/recovery/reset-password', data),
  verifyOtp: (identifier: string, otp: string) => 
    api.post('/recovery/verify-otp', { identifier, otp }),
}

// Question endpoints
export const questionApi = {
  getRandomQuestions: (subject: string = 'Mathematics', count: number = 10, difficulty?: string) => {
    const params: any = { count }
    if (difficulty) {
      params.difficulty = difficulty
    }
    // Encode subject to handle spaces and special characters
    const encodedSubject = encodeURIComponent(subject)
    return api.get(`/questions/random/${encodedSubject}`, { params })
  },
  submitAnswer: (data: { question_id: number; user_answer: string }) =>
    api.post('/questions/submit', data),
}

// AI endpoints
export const aiApi = {
  explainAnswer: (data: { question_id: number; student_answer: number; context?: string }) =>
    api.post('/ai/explain', data, { timeout: 120000 }), // 120 second timeout
  chat: (data: { 
    message: string; 
    history?: Array<{ role: string; content: string }>; 
    subject?: string; 
    topic?: string;
    socratic_mode?: boolean;
  }) =>
    api.post('/ai/chat', data, { timeout: 120000 }), // 120 second timeout
  generateQuiz: (data: {
    subject: string;
    topic?: string;
    difficulty?: string;
    num_questions?: number;
  }) =>
    api.post('/ai/quiz', data, { timeout: 120000 }),
  getRecommendations: () => api.get('/ai/recommendations', { timeout: 30000 }), // 30s timeout for dashboard
  getStatus: () => api.get('/ai/status'),
}

// Student endpoints
export const studentApi = {
  getDashboard: () => api.get('/student/dashboard'),
  getDashboardSummary: () => api.get('/student/dashboard/summary'),
  getSubjects: () => api.get('/student/subjects'),
  getAnalytics: () => api.get('/student/dashboard/analytics'),
}

// Billing endpoints
export const billingApi = {
  getPlans: () => api.get('/billing/plans'),
  initializePayment: (plan_id: string) => api.post('/billing/initialize', { plan_id }),
}

// Admin endpoints
export const adminApi = {
  // Dashboard
  getHealth: () => api.get('/admin/health'),
  getUserGrowth: () => api.get('/admin/users/growth'),
  getContentQuality: () => api.get('/admin/content/quality'),
  getEngagement: () => api.get('/admin/engagement'),
  getStatsSummary: (timeRange: 'today' | 'week' | 'month' | 'all_time' = 'week') => 
    api.get('/admin/stats/summary', { params: { time_range: timeRange } }),
  
  // User Management
  getUsers: (skip: number = 0, limit: number = 20, role?: string) => 
    api.get('/admin/users', { params: { skip, limit, role } }),
  searchUsers: (query: string, limit: number = 10) => 
    api.get('/admin/users/search', { params: { query, limit } }),
  getTopUsers: (limit: number = 10) => 
    api.get('/admin/users/top', { params: { limit } }),
  updateUser: (userId: number, data: {
    full_name?: string;
    role?: string;
    total_points?: number;
    is_verified?: boolean;
    is_active?: boolean;
  }) => api.put(`/admin/users/${userId}`, data),
  deactivateUser: (userId: number, reason: string) => 
    api.put(`/admin/users/${userId}/deactivate`, null, { params: { reason } }),
  activateUser: (userId: number) => 
    api.put(`/admin/users/${userId}/activate`),
  
  // Content Management
  getProblematicQuestions: (minAttempts: number = 50, maxAccuracy: number = 0.4, limit: number = 20) => 
    api.get('/admin/questions/problematic', { params: { min_attempts: minAttempts, max_accuracy: maxAccuracy, limit } }),
  deleteQuestion: (questionId: number, reason: string) => 
    api.delete(`/admin/questions/${questionId}`, { params: { reason } }),
  resolveReport: (reportId: number, action: 'dismissed' | 'question_fixed' | 'question_deleted', notes?: string) => 
    api.put(`/admin/reports/${reportId}/resolve`, null, { params: { action, notes } }),
  
  // Role Management
  changeUserRole: (userId: number, newRole: 'student' | 'teacher' | 'admin', reason: string) =>
    api.post(`/admin/admin/users/${userId}/role`, { new_role: newRole, reason }),
  getUsersByRole: (role: 'student' | 'teacher' | 'admin') =>
    api.get(`/admin/admin/users/by-role/${role}`),
  deleteUser: (userId: number) =>
    api.delete(`/admin/admin/users/${userId}`),
}

// Classroom endpoints
export const classroomApi = {
  // Classrooms
  createClassroom: (data: { name: string; description?: string; subject?: string; grade_level?: string }) =>
    api.post('/classrooms', data),
  getClassrooms: () => api.get('/classrooms'),
  joinClassroom: (join_code: string) => api.post('/classrooms/join', { join_code }),
  getClassroom: (classroomId: number) => api.get(`/classrooms/${classroomId}`),
  getClassroomMembers: (classroomId: number) => api.get(`/classrooms/${classroomId}/members`),
  updateClassroom: (classroomId: number, data: { name?: string; description?: string; subject?: string; grade_level?: string }) =>
    api.put(`/classrooms/${classroomId}`, data),
  deleteClassroom: (classroomId: number) => api.delete(`/classrooms/${classroomId}`),

  // Stream / Posts
  getStream: (classroomId: number) => api.get(`/classrooms/${classroomId}/stream`),
  postAnnouncement: (classroomId: number, data: { content: string; post_type: string; attachment_url?: string }) =>
    api.post(`/classrooms/${classroomId}/announce`, data),
  commentOnPost: (classroomId: number, postId: number, data: { content: string }) =>
    api.post(`/classrooms/${classroomId}/stream/${postId}/comment`, data),

  // Assignments & submissions
  createManualAssignment: (classroomId: number, data: any) =>
    api.post(`/classrooms/${classroomId}/assignments/manual`, data),
  getAssignments: (classroomId: number) => api.get(`/classrooms/${classroomId}/assignments`),
  updateAssignment: (assignmentId: number, data: { title?: string; description?: string; due_date?: string; total_points?: number }) =>
    api.put(`/classrooms/assignments/${assignmentId}`, data),
  deleteAssignment: (assignmentId: number) => api.delete(`/classrooms/assignments/${assignmentId}`),
  getSubmissions: (assignmentId: number) => api.get(`/classrooms/assignments/${assignmentId}/submissions`),
  gradeSubmission: (submissionId: number, data: { score: number; feedback?: string }) =>
    api.post(`/classrooms/submissions/${submissionId}/grade`, data),

  // Materials
  uploadMaterial: (classroomId: number, data: any) => api.post(`/classrooms/${classroomId}/materials`, data),
  getMaterials: (classroomId: number) => api.get(`/classrooms/${classroomId}/materials`),
  updateMaterial: (materialId: number, data: { title?: string; description?: string; material_url?: string }) =>
    api.put(`/classrooms/materials/${materialId}`, data),
  deleteMaterial: (materialId: number) => api.delete(`/classrooms/materials/${materialId}`),

  // AI Teacher
  askAITeacher: (classroomId: number, question: string) =>
    api.post(`/classrooms/${classroomId}/ask-ai`, { question }),

  // Teacher insights
  getClassInsights: (classroomId: number) => api.get(`/ai/teacher/insights/${classroomId}`),

  // Student Profile Management
  getStudentProfile: (classroomId: number, studentId: number) =>
    api.get(`/classrooms/${classroomId}/students/${studentId}/profile`),
  updateStudentProfile: (classroomId: number, studentId: number, data: {
    notes?: string;
    strengths?: string;
    weaknesses?: string;
    learning_style?: string;
    participation_level?: string;
    homework_completion_rate?: number;
    ai_context?: string;
  }) => api.put(`/classrooms/${classroomId}/students/${studentId}/profile`, data),
  sendStudentMessage: (classroomId: number, studentId: number, data: {
    subject?: string;
    message: string;
    type: string;
  }) => api.post(`/classrooms/${classroomId}/students/${studentId}/message`, data),
  getStudentMessages: (classroomId: number, studentId: number) =>
    api.get(`/classrooms/${classroomId}/students/${studentId}/messages`),
  getStudentAIContext: (classroomId: number, studentId: number, question: string) =>
    api.post(`/classrooms/${classroomId}/students/${studentId}/ai-context`, { question }),
}

// Moderation endpoints (Admin only)
export const moderationApi = {
  // Questions
  createQuestion: (data: any) => api.post('/moderation/questions', data),
  updateQuestion: (id: number, data: any) => api.put(`/moderation/questions/${id}`, data),
  deleteQuestion: (id: number) => api.delete(`/moderation/questions/${id}`),
  
  // Assets
  uploadAsset: (formData: FormData) => api.post('/moderation/assets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  listAssets: () => api.get('/moderation/assets'),
  reviewAsset: (id: number, status: 'approved' | 'rejected', notes?: string) => 
    api.post(`/moderation/assets/${id}/review`, { status, notes }),
  updateAssetMetadata: (id: number, metadata: any) => 
    api.put(`/moderation/assets/${id}/metadata`, metadata),
  
  // Flashcards
  createDeck: (data: { title: string; subject: string; description?: string }) => 
    api.post('/moderation/flashcards/decks', data),
  addFlashcard: (data: { deck_id: number; front: string; back: string; asset_id?: number }) => 
    api.post('/moderation/flashcards', data),
}

// Asset & Image endpoints
export const assetApi = {
  getImageUrl: (filename: string, options?: { quality?: string; network?: string }) => {
    const params = new URLSearchParams(options as any)
    const queryString = params.toString()
    return `${API_BASE_URL}/assets/image/${filename}${queryString ? `?${queryString}` : ''}`
  },
  // For direct fetching if needed (though usually used in <img> tags)
  getImage: (filename: string, options?: { quality?: string; network?: string }) => 
    api.get(`/assets/image/${filename}`, { params: options, responseType: 'blob' }),
}

// Onboarding endpoints
export const onboardingApi = {
  getStatus: () => api.get('/onboarding/status'),
  completeStudent: (data: {
    education_level: string;
    preferred_subjects: string[];
    target_exam_date: string;
    learning_style: string;
    study_time_preference: string;
  }) => api.post('/onboarding/student', data),
  completeTeacher: (data: {
    bio: string;
    subjects_taught: string[];
    first_classroom_name: string;
    first_classroom_subject: string;
    first_classroom_grade: string;
  }) => api.post('/onboarding/teacher', data),
}

// Marketing endpoints
export const marketingApi = {
  joinWaitlist: (data: {
    full_name: string;
    phone: string;
    school_name: string;
    current_level: string;
    preparing_for: string;
    device_type: string;
  }) => api.post('/marketing/waitlist', data),
}

// System endpoints
export const systemApi = {
  getConfig: () => api.get('/system/config'),
}

