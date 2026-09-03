'use client'
import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import Composer from '@/components/classroom/Composer'
import StreamPost from '@/components/classroom/StreamPost'
import EditClassroomForm from '@/components/classroom/EditClassroomForm'
import AskAITeacher from '@/components/classroom/AskAITeacher'
import { classroomApi } from '@/lib/api'
import { Loader2, RefreshCw, Edit2, Trash2, Bell, ArrowLeft, Sparkles, Paperclip, User, Users, BookOpen, MessageSquare, Settings, Share2 } from 'lucide-react'
import { useModalStore } from '@/store/modalStore'
import { cn } from '@/lib/utils'

export default function ClassroomPage() {
  const router = useRouter()
  const params = useParams() as any
  const classroomId = parseInt(params.id)
  const [classroom, setClassroom] = useState<any>(null)
  const [stream, setStream] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'stream' | 'ai'>('stream')
  const { showSuccess, showError, showConfirm } = useModalStore()

  useEffect(() => {
    load()
  }, [classroomId])

  const load = async () => {
    try {
      setLoading(true)
      const [cRes, sRes] = await Promise.all([
        classroomApi.getClassroom(classroomId),
        classroomApi.getStream(classroomId),
      ])
      setClassroom(cRes.data)
      setStream(sRes.data || [])
    } catch (err) {
      console.error('Failed to load classroom', err)
    } finally {
      setLoading(false)
    }
  }

  const refresh = async () => {
    try {
      setRefreshing(true)
      const [cRes, sRes] = await Promise.all([
        classroomApi.getClassroom(classroomId),
        classroomApi.getStream(classroomId),
      ])
      setClassroom(cRes.data)
      setStream(sRes.data || [])
    } catch (err) {
      console.error('Failed to refresh classroom', err)
    } finally {
      setRefreshing(false)
    }
  }

  const handlePost = async (content: string) => {
    try {
      await classroomApi.postAnnouncement(classroomId, { content, post_type: 'announcement' })
      await load()
    } catch (err) {
      console.error('Failed to post announcement', err)
      showError('Unable to post announcement. Please try again.', 'Post Failed')
    }
  }

  const handleDelete = () => {
    showConfirm(
      'This will permanently delete the classroom and all its data. This action cannot be undone.',
      async () => {
        try {
          await classroomApi.deleteClassroom(classroomId)
          showSuccess('Classroom deleted successfully.', 'Deleted')
          router.push('/classrooms')
        } catch (err: any) {
          console.error('Failed to delete classroom', err)
          if (err.response?.status === 403) {
            showError('You do not have permission to delete this classroom.', 'Permission Denied')
          } else {
            showError('Unable to delete classroom. Please try again.', 'Delete Failed')
          }
        }
      },
      'Delete Classroom'
    )
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-full p-8 gap-4">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
            <RefreshCw className="w-6 h-6 text-emerald-500 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
          </div>
          <p className="text-slate-500 font-bold uppercase tracking-widest text-xs animate-pulse">Loading Classroom...</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto p-6 space-y-8">
        {/* Header Section */}
        <div className="relative overflow-hidden rounded-[2.5rem] bg-slate-900 dark:bg-slate-950 p-8 md:p-12 shadow-2xl">
          <div className="absolute top-0 right-0 w-1/2 h-full bg-gradient-to-l from-emerald-500/10 to-transparent" />
          <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl" />
          
          <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-8">
            <div className="space-y-4">
              <button 
                onClick={() => router.push('/classrooms')}
                className="flex items-center gap-2 text-emerald-500 font-black uppercase tracking-widest text-[10px] hover:gap-3 transition-all"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Classrooms
              </button>
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-2xl bg-emerald-500 flex items-center justify-center shadow-2xl shadow-emerald-500/20">
                  <BookOpen className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-4xl font-outfit font-black text-white tracking-tight">{classroom?.name}</h1>
                  <p className="text-slate-400 font-medium">{classroom?.subject} • {classroom?.grade_level}</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button 
                onClick={() => setEditOpen(true)}
                className="h-12 px-6 bg-white/10 hover:bg-white/20 text-white rounded-xl font-bold text-xs uppercase tracking-widest transition-all flex items-center gap-2 backdrop-blur-md"
              >
                <Settings className="w-4 h-4" /> Settings
              </button>
              <button 
                onClick={handleDelete}
                className="h-12 px-6 bg-red-500/10 hover:bg-red-500/20 text-red-500 rounded-xl font-bold text-xs uppercase tracking-widest transition-all flex items-center gap-2 backdrop-blur-md"
              >
                <Trash2 className="w-4 h-4" /> Delete
              </button>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="relative z-10 mt-12 grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Students', value: classroom?.student_count || 0, icon: Users },
              { label: 'Posts', value: stream.length, icon: MessageSquare },
              { label: 'Class Code', value: classroom?.code, icon: Share2, copy: true },
              { label: 'Teacher', value: classroom?.teacher?.full_name?.split(' ')[0] || 'You', icon: User },
            ].map((stat, i) => (
              <div key={i} className="bg-white/5 backdrop-blur-md rounded-2xl p-4 border border-white/10">
                <div className="flex items-center gap-3 mb-1">
                  <stat.icon className="w-4 h-4 text-emerald-500" />
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{stat.label}</span>
                </div>
                <p className="text-xl font-outfit font-black text-white">{stat.value}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Stream */}
          <div className="lg:col-span-2 space-y-6">
            {/* Tabs */}
            <div className="flex p-1 bg-slate-100 dark:bg-slate-900 rounded-2xl w-fit">
              <button
                onClick={() => setActiveTab('stream')}
                className={cn(
                  "px-8 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all",
                  activeTab === 'stream' ? "bg-white dark:bg-slate-800 text-emerald-600 shadow-lg" : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                )}
              >
                Class Stream
              </button>
              <button
                onClick={() => setActiveTab('ai')}
                className={cn(
                  "px-8 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all flex items-center gap-2",
                  activeTab === 'ai' ? "bg-white dark:bg-slate-800 text-emerald-600 shadow-lg" : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                )}
              >
                <Sparkles className="w-3 h-3" /> AI Teacher
              </button>
            </div>

            {activeTab === 'stream' ? (
              <div className="space-y-6">
                <Composer onPost={handlePost} />
                
                <div className="space-y-4">
                  {stream.length > 0 ? (
                    stream.map((post) => (
                      <StreamPost key={post.id} post={post} />
                    ))
                  ) : (
                    <div className="bg-white dark:bg-slate-900 rounded-[2rem] p-12 text-center border-2 border-dashed border-slate-200 dark:border-slate-800">
                      <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <MessageSquare className="w-8 h-8 text-slate-400" />
                      </div>
                      <h3 className="text-xl font-outfit font-black text-slate-900 dark:text-white mb-2">No posts yet</h3>
                      <p className="text-slate-500 font-medium">Be the first to share something with the class!</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <AskAITeacher classroomId={classroomId} />
            )}
          </div>

          {/* Right Column: Sidebar Info */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-900 rounded-[2rem] p-8 border-2 border-slate-50 dark:border-slate-800 shadow-xl">
              <h3 className="text-lg font-outfit font-black text-slate-900 dark:text-white mb-6 flex items-center gap-2">
                <Bell className="w-5 h-5 text-emerald-500" />
                Upcoming
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border-2 border-transparent hover:border-emerald-500/20 transition-all cursor-pointer group">
                  <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest mb-1">Due Tomorrow</p>
                  <p className="text-slate-900 dark:text-white font-bold group-hover:text-emerald-500 transition-colors">Mathematics Quiz #4</p>
                </div>
                <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border-2 border-transparent hover:border-emerald-500/20 transition-all cursor-pointer group">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">Friday, 2:00 PM</p>
                  <p className="text-slate-900 dark:text-white font-bold group-hover:text-emerald-500 transition-colors">Physics Lab Report</p>
                </div>
              </div>
              <button className="w-full mt-6 py-4 text-emerald-600 font-black uppercase tracking-widest text-[10px] hover:bg-emerald-50 dark:hover:bg-emerald-500/10 rounded-xl transition-all">
                View All Assignments
              </button>
            </div>

            <div className="bg-emerald-600 rounded-[2rem] p-8 text-white shadow-xl shadow-emerald-600/20 relative overflow-hidden group">
              <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-white/10 rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700" />
              <Sparkles className="w-8 h-8 mb-4" />
              <h3 className="text-xl font-outfit font-black mb-2">AI Study Assistant</h3>
              <p className="text-emerald-100 text-sm font-medium mb-6">Get instant help with your class materials and assignments.</p>
              <button 
                onClick={() => setActiveTab('ai')}
                className="w-full py-4 bg-white text-emerald-600 rounded-xl font-black uppercase tracking-widest text-[10px] shadow-lg hover:scale-105 transition-all"
              >
                Start Chatting
              </button>
            </div>
          </div>
        </div>
      </div>

      {editOpen && (
        <EditClassroomForm 
          classroom={classroom} 
          onClose={() => setEditOpen(false)} 
          onSuccess={() => {
            setEditOpen(false)
            load()
          }} 
        />
      )}
    </AppLayout>
  )
}
