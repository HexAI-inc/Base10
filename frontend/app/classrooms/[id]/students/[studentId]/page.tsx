'use client'
import { useEffect, useState, use } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import { classroomApi } from '@/lib/api'
import { Loader2, ArrowLeft, User, MessageSquare, Brain, TrendingUp, BookOpen, Calendar, Send, X } from 'lucide-react'
import { useModalStore } from '@/store/modalStore'
import { cn } from '@/lib/utils'

export default function StudentProfilePage({ params }: any) {
  const router = useRouter()
  const { id, studentId } = use(params) as any
  const classroomId = parseInt(id)
  const studentIdNum = parseInt(studentId)
  
  const [profile, setProfile] = useState<any>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'messages' | 'ai'>('overview')
  const [isSending, setIsSending] = useState(false)
  
  // Message form
  const [messageSubject, setMessageSubject] = useState('')
  const [messageContent, setMessageContent] = useState('')
  const [messageType, setMessageType] = useState('general')
  
  // Profile editing
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState({
    notes: '',
    strengths: '',
    weaknesses: '',
    learning_style: '',
    participation_level: '',
    homework_completion_rate: 0,
    ai_context: '',
  })
  
  // AI question
  const [aiQuestion, setAiQuestion] = useState('')
  const [aiResponse, setAiResponse] = useState('')
  const [aiLoading, setAiLoading] = useState(false)
  
  const { showSuccess, showError } = useModalStore()

  useEffect(() => {
    loadData()
  }, [classroomId, studentIdNum])

  const loadData = async () => {
    try {
      setLoading(true)
      const [profileRes, messagesRes] = await Promise.allSettled([
        classroomApi.getStudentProfile(classroomId, studentIdNum),
        classroomApi.getStudentMessages(classroomId, studentIdNum),
      ])

      if (profileRes.status === 'fulfilled') {
        setProfile(profileRes.value.data)
        
        // Initialize edit form with existing data
        const p = profileRes.value.data.profile || {}
        setEditData({
          notes: p.notes || '',
          strengths: p.strengths || '',
          weaknesses: p.weaknesses || '',
          learning_style: p.learning_style || '',
          participation_level: p.participation_level || '',
          homework_completion_rate: p.homework_completion_rate || 0,
          ai_context: p.ai_context || '',
        })
      }

      if (messagesRes.status === 'fulfilled') {
        const msgData = messagesRes.value.data
        setMessages(Array.isArray(msgData) ? msgData : [])
      }
    } catch (err) {
      console.error('Failed to load student profile', err)
      showError('Failed to load student profile', 'Please try again')
    } finally {
      setLoading(false)
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!messageSubject.trim() || !messageContent.trim()) return

    try {
      setIsSending(true)
      await classroomApi.sendStudentMessage(classroomId, studentIdNum, {
        subject: messageSubject,
        message: messageContent,
        type: messageType,
      })
      
      showSuccess('Message sent successfully! Student will be notified.', 'Message Sent')
      setMessageSubject('')
      setMessageContent('')
      setMessageType('general')
      
      // Reload messages
      const res = await classroomApi.getStudentMessages(classroomId, studentIdNum)
      const msgData = res.data
      setMessages(Array.isArray(msgData) ? msgData : [])
    } catch (err: any) {
      showError(
        err.response?.data?.detail || 'Failed to send message',
        'Send Failed'
      )
    } finally {
      setIsSending(false)
    }
  }

  const handleSaveProfile = async () => {
    try {
      await classroomApi.updateStudentProfile(classroomId, studentIdNum, editData)
      showSuccess('Student profile updated successfully', 'Profile Saved')
      setIsEditing(false)
      await loadData()
    } catch (err: any) {
      showError(
        err.response?.data?.detail || 'Failed to update profile',
        'Save Failed'
      )
    }
  }

  const handleAskAI = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!aiQuestion.trim()) return

    try {
      setAiLoading(true)
      const res = await classroomApi.getStudentAIContext(classroomId, studentIdNum, aiQuestion)
      setAiResponse(res.data.advice || res.data.answer || 'No response')
      setAiQuestion('')
    } catch (err: any) {
      showError(
        err.response?.data?.detail || 'Failed to get AI advice',
        'AI Request Failed'
      )
    } finally {
      setAiLoading(false)
    }
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="max-w-7xl mx-auto p-6 sm:p-8">
          <div className="flex flex-col items-center justify-center h-96 gap-4">
            <div className="relative">
              <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
              <span className="text-xl absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">👤</span>
            </div>
            <p className="text-xs font-black text-slate-400 uppercase tracking-widest animate-pulse">Loading Profile...</p>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (!profile) {
    return (
      <AppLayout>
        <div className="max-w-7xl mx-auto p-6 sm:p-8">
          <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-16 text-center border-2 border-dashed border-slate-100 dark:border-slate-800">
            <div className="w-24 h-24 mx-auto mb-8 bg-slate-50 dark:bg-slate-800 rounded-[2rem] flex items-center justify-center">
              <User className="w-12 h-12 text-slate-300 dark:text-slate-600" />
            </div>
            <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-3">Profile not found</h3>
            <p className="text-slate-500 dark:text-slate-400 max-w-md mx-auto font-medium">
              We couldn't find the student profile you're looking for. It may have been removed or you may not have permission to view it.
            </p>
            <button
              onClick={() => router.push(`/classrooms/${classroomId}/people`)}
              className="mt-8 px-8 h-14 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl font-black uppercase tracking-widest text-xs hover:bg-emerald-600 dark:hover:bg-emerald-500 dark:hover:text-white transition-all"
            >
              Back to People
            </button>
          </div>
        </div>
      </AppLayout>
    )
  }

  const student = profile.student_info
  const performanceData = profile.performance || {}
  const profileData = profile.profile || {}
  const recentActivity = profile.recent_activity || []

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto p-6 sm:p-8 space-y-8">
        <button
          onClick={() => router.push(`/classrooms/${classroomId}/people`)}
          className="group flex items-center gap-3 text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all font-black uppercase tracking-widest text-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center group-hover:border-emerald-500/50 transition-colors shadow-sm">
            <ArrowLeft className="w-5 h-5" />
          </div>
          Back to People
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Sidebar - Profile Info */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 blur-3xl rounded-full -mr-16 -mt-16 group-hover:bg-emerald-500/10 transition-colors" />
              
              <div className="flex flex-col items-center text-center relative">
                <div className="w-32 h-32 rounded-[2.5rem] bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 flex items-center justify-center mb-6 shadow-inner group-hover:border-emerald-500/30 transition-colors">
                  {student?.avatar_url ? (
                    <img src={student.avatar_url} alt={student.full_name} className="w-full h-full rounded-[2.5rem] object-cover" />
                  ) : (
                    <User className="w-16 h-16 text-slate-300 group-hover:text-emerald-500 transition-colors" />
                  )}
                </div>
                
                <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-2">{student?.full_name}</h1>
                <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">@{student?.username}</p>
                
                <div className="w-full grid grid-cols-2 gap-3">
                  <div className="bg-slate-50 dark:bg-slate-950 rounded-2xl p-4 border border-slate-100 dark:border-slate-800">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Submissions</p>
                    <p className="text-xl font-outfit font-black text-emerald-600 dark:text-emerald-400">{profile?.submission_count || 0}</p>
                  </div>
                  <div className="bg-slate-50 dark:bg-slate-950 rounded-2xl p-4 border border-slate-100 dark:border-slate-800">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Avg. Grade</p>
                    <p className="text-xl font-outfit font-black text-blue-600 dark:text-blue-400">
                      {performanceData.average_grade ? `${Math.round(performanceData.average_grade)}%` : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="bg-white dark:bg-slate-900 rounded-[2rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm">
              <h3 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest mb-6">Performance</h3>
              <div className="space-y-6">
                <div className="space-y-2">
                  <div className="flex justify-between text-[10px] font-black uppercase tracking-widest">
                    <span className="text-slate-400">Participation</span>
                    <span className="text-emerald-500">{profileData.participation_level || 'Medium'}</span>
                  </div>
                  <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: '75%' }} />
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-[10px] font-black uppercase tracking-widest">
                    <span className="text-slate-400">Homework Rate</span>
                    <span className="text-blue-500">{Math.round((performanceData.submission_rate || 0) * 100)}%</span>
                  </div>
                  <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${(performanceData.submission_rate || 0) * 100}%` }} />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-8 space-y-8">
            {/* Tabs */}
            <div className="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 p-2 flex gap-2 shadow-sm">
              <button
                onClick={() => setActiveTab('overview')}
                className={cn(
                  "flex-1 flex items-center justify-center gap-3 px-6 h-14 rounded-[1.5rem] text-sm font-black uppercase tracking-widest transition-all",
                  activeTab === 'overview'
                    ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/20"
                    : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                )}
              >
                <TrendingUp className="w-5 h-5" />
                Overview
              </button>
              <button
                onClick={() => setActiveTab('messages')}
                className={cn(
                  "flex-1 flex items-center justify-center gap-3 px-6 h-14 rounded-[1.5rem] text-sm font-black uppercase tracking-widest transition-all",
                  activeTab === 'messages'
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                    : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                )}
              >
                <MessageSquare className="w-5 h-5" />
                Messages
              </button>
              <button
                onClick={() => setActiveTab('ai')}
                className={cn(
                  "flex-1 flex items-center justify-center gap-3 px-6 h-14 rounded-[1.5rem] text-sm font-black uppercase tracking-widest transition-all",
                  activeTab === 'ai'
                    ? "bg-purple-600 text-white shadow-lg shadow-purple-600/20"
                    : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                )}
              >
                <Brain className="w-5 h-5" />
                AI Insights
              </button>
            </div>

            {/* Tab Content */}
            <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
              {activeTab === 'overview' && (
                <div className="space-y-8">
                  {/* Performance Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-white dark:bg-slate-900 rounded-[2rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600">
                          <TrendingUp className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">Strengths</h3>
                      </div>
                      <p className="text-sm text-slate-600 dark:text-slate-400 font-medium leading-relaxed">
                        {profileData.strengths || 'No strengths recorded yet.'}
                      </p>
                    </div>
                    <div className="bg-white dark:bg-slate-900 rounded-[2rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-xl bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600">
                          <BookOpen className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">Areas for Growth</h3>
                      </div>
                      <p className="text-sm text-slate-600 dark:text-slate-400 font-medium leading-relaxed">
                        {profileData.weaknesses || 'No growth areas recorded yet.'}
                      </p>
                    </div>
                  </div>

                  {/* Recent Activity */}
                  <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm">
                    <div className="flex items-center justify-between mb-8">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600">
                          <Calendar className="w-5 h-5" />
                        </div>
                        <h3 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">Recent Activity</h3>
                      </div>
                      <button 
                        onClick={() => setIsEditing(true)}
                        className="px-6 h-10 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-slate-200 dark:hover:bg-slate-700 transition-all"
                      >
                        Edit Profile
                      </button>
                    </div>
                    
                    {recentActivity.length === 0 ? (
                      <p className="text-slate-500 dark:text-slate-400 font-medium text-center py-8">No recent activity recorded.</p>
                    ) : (
                      <div className="space-y-4">
                        {recentActivity.map((activity: any, idx: number) => (
                          <div key={idx} className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-950 rounded-2xl border border-slate-100 dark:border-slate-800">
                            <div className="w-10 h-10 rounded-xl bg-white dark:bg-slate-900 flex items-center justify-center text-lg shadow-sm">
                              {activity.type === 'submission' ? '📝' : activity.type === 'quiz' ? '🧠' : '📊'}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-black text-slate-900 dark:text-slate-100 truncate">{activity.description}</p>
                              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                {new Date(activity.timestamp).toLocaleString()}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'messages' && (
                <div className="space-y-8">
                  {/* Message Composer */}
                  <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm">
                    <h3 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest mb-8">Send Message</h3>
                    <form onSubmit={handleSendMessage} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Subject</label>
                          <input 
                            value={messageSubject}
                            onChange={(e) => setMessageSubject(e.target.value)}
                            placeholder="e.g. Homework Feedback"
                            className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-blue-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all"
                          />
                        </div>
                        <div className="space-y-2">
                          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Type</label>
                          <select 
                            value={messageType}
                            onChange={(e) => setMessageType(e.target.value)}
                            className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-blue-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all appearance-none"
                          >
                            <option value="general">General Update</option>
                            <option value="feedback">Academic Feedback</option>
                            <option value="warning">Performance Warning</option>
                            <option value="praise">Praise & Recognition</option>
                          </select>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Message Content</label>
                        <textarea 
                          value={messageContent}
                          onChange={(e) => setMessageContent(e.target.value)}
                          placeholder="Write your message here..."
                          className="w-full min-h-[160px] p-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-[2rem] focus:border-blue-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all resize-none"
                        />
                      </div>
                      <div className="flex justify-end">
                        <button 
                          disabled={isSending || !messageSubject.trim() || !messageContent.trim()}
                          className="flex items-center justify-center gap-3 px-10 h-14 bg-blue-600 text-white rounded-2xl font-black uppercase tracking-widest text-sm hover:bg-blue-700 transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isSending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                          <span>Send Message</span>
                        </button>
                      </div>
                    </form>
                  </div>

                  {/* Message History */}
                  <div className="space-y-6">
                    <div className="flex items-center gap-4">
                      <h3 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">Message History</h3>
                      <div className="h-px flex-1 bg-slate-100 dark:bg-slate-800" />
                    </div>
                    
                    {messages.length === 0 ? (
                      <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-16 text-center border-2 border-dashed border-slate-100 dark:border-slate-800">
                        <p className="text-slate-500 dark:text-slate-400 font-medium">No messages sent to this student yet.</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {messages.map((msg) => (
                          <div key={msg.id} className="bg-white dark:bg-slate-900 rounded-[2rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm">
                            <div className="flex justify-between items-start mb-4">
                              <div>
                                <h4 className="text-lg font-outfit font-black text-slate-900 dark:text-slate-100">{msg.subject}</h4>
                                <div className="flex items-center gap-2 mt-1">
                                  <span className={cn(
                                    "px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest",
                                    msg.message_type === 'praise' ? "bg-emerald-100 text-emerald-600" :
                                    msg.message_type === 'warning' ? "bg-red-100 text-red-600" :
                                    "bg-blue-100 text-blue-600"
                                  )}>
                                    {msg.message_type}
                                  </span>
                                  <span className="text-[10px] text-slate-400 font-medium">
                                    {new Date(msg.created_at).toLocaleDateString()}
                                  </span>
                                </div>
                              </div>
                            </div>
                            <p className="text-sm text-slate-600 dark:text-slate-400 font-medium leading-relaxed">
                              {msg.message}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'ai' && (
                <div className="space-y-8">
                  <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/5 blur-3xl rounded-full -mr-32 -mt-32" />
                    
                    <div className="flex items-center gap-4 mb-8 relative">
                      <div className="w-12 h-12 rounded-2xl bg-purple-600 flex items-center justify-center text-white shadow-lg shadow-purple-600/20">
                        <Brain className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="text-xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">AI Student Insights</h3>
                        <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Powered by Base10 Intelligence</p>
                      </div>
                    </div>

                    <div className="space-y-6 relative">
                      <div className="bg-slate-50 dark:bg-slate-950 rounded-[2rem] p-8 border border-slate-100 dark:border-slate-800">
                        <p className="text-sm text-slate-600 dark:text-slate-400 font-medium leading-relaxed italic">
                          "Based on recent submissions and participation, {student?.full_name} shows strong analytical skills but may benefit from more structured feedback on creative assignments. Their engagement has increased by 15% over the last two weeks."
                        </p>
                      </div>

                      <div className="space-y-4">
                        <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Ask AI about this student</h4>
                        <div className="flex gap-3">
                          <input 
                            value={aiQuestion}
                            onChange={(e) => setAiQuestion(e.target.value)}
                            placeholder="e.g. How can I help them improve in Algebra?"
                            className="flex-1 h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-purple-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all"
                          />
                          <button 
                            onClick={handleAskAI}
                            disabled={aiLoading || !aiQuestion.trim()}
                            className="w-14 h-14 flex items-center justify-center bg-purple-600 text-white rounded-2xl hover:bg-purple-700 transition-all shadow-lg shadow-purple-600/20 disabled:opacity-50"
                          >
                            {aiLoading ? <Loader2 className="w-6 h-6 animate-spin" /> : <Send className="w-6 h-6" />}
                          </button>
                        </div>
                      </div>

                      {aiResponse && (
                        <div className="bg-purple-50 dark:bg-purple-900/10 rounded-[2rem] p-8 border border-purple-100 dark:border-purple-900/30 animate-in fade-in zoom-in duration-300">
                          <div className="flex items-center gap-2 mb-4">
                            <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
                            <span className="text-[10px] font-black text-purple-600 dark:text-purple-400 uppercase tracking-widest">AI Response</span>
                          </div>
                          <p className="text-sm text-slate-700 dark:text-slate-300 font-medium leading-relaxed">
                            {aiResponse}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Edit Profile Modal */}
      {isEditing && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
          <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onClick={() => setIsEditing(false)} />
          <div className="relative bg-white dark:bg-slate-900 w-full max-w-2xl rounded-[2.5rem] overflow-hidden shadow-2xl border border-slate-100 dark:border-slate-800 animate-in fade-in zoom-in duration-300">
            <div className="p-8 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-950/50">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
                  <User className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Edit Student Profile</h3>
                  <p className="text-xs font-black text-slate-400 uppercase tracking-widest">Update academic records</p>
                </div>
              </div>
              <button 
                onClick={() => setIsEditing(false)}
                className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-8 max-h-[60vh] overflow-y-auto space-y-6 custom-scrollbar">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Participation Level</label>
                  <select 
                    value={editData.participation_level}
                    onChange={(e) => setEditData({...editData, participation_level: e.target.value})}
                    className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-emerald-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all appearance-none"
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Exceptional">Exceptional</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Homework Rate (%)</label>
                  <input 
                    type="number"
                    value={editData.homework_completion_rate}
                    onChange={(e) => setEditData({...editData, homework_completion_rate: parseInt(e.target.value)})}
                    className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-emerald-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Strengths</label>
                <textarea 
                  value={editData.strengths}
                  onChange={(e) => setEditData({...editData, strengths: e.target.value})}
                  className="w-full min-h-[100px] p-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-[1.5rem] focus:border-emerald-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all resize-none"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Areas for Growth</label>
                <textarea 
                  value={editData.weaknesses}
                  onChange={(e) => setEditData({...editData, weaknesses: e.target.value})}
                  className="w-full min-h-[100px] p-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-[1.5rem] focus:border-emerald-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all resize-none"
                />
              </div>
              
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Private Teacher Notes</label>
                <textarea 
                  value={editData.notes}
                  onChange={(e) => setEditData({...editData, notes: e.target.value})}
                  className="w-full min-h-[120px] p-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-[1.5rem] focus:border-emerald-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all resize-none"
                />
              </div>
            </div>
            
            <div className="p-8 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-4 bg-slate-50/50 dark:bg-slate-950/50">
              <button 
                onClick={() => setIsEditing(false)}
                className="px-8 h-14 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 rounded-2xl font-black uppercase tracking-widest text-xs hover:bg-slate-50 dark:hover:bg-slate-800 transition-all border border-slate-200 dark:border-slate-800"
              >
                Cancel
              </button>
              <button 
                onClick={handleSaveProfile}
                className="px-10 h-14 bg-emerald-600 text-white rounded-2xl font-black uppercase tracking-widest text-sm hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-600/20"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  )
}
