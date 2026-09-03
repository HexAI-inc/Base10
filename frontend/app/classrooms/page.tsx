"use client"
import { useEffect, useState } from 'react'
import AppLayout from '@/components/AppLayout'
import ClassroomCard from '@/components/classroom/ClassroomCard'
import { classroomApi, authApi } from '@/lib/api'
import { Loader2, GraduationCap, Plus, Search, Sparkles, BookOpen, Users, ArrowRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import CreateClassroomForm from '@/components/classroom/CreateClassroomForm'
import JoinClassroomForm from '@/components/classroom/JoinClassroomForm'

export default function ClassroomsPage() {
  const [classrooms, setClassrooms] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [userProfile, setUserProfile] = useState<any>(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const [classroomsRes, profileRes] = await Promise.allSettled([
          classroomApi.getClassrooms(),
          authApi.getProfile()
        ])
        
        if (classroomsRes.status === 'fulfilled') {
          const rawClassrooms = classroomsRes.value.data || []
          const uniqueClassrooms = Array.from(
            new Map(rawClassrooms.map((c: any) => [c.id, c])).values()
          )
          setClassrooms(uniqueClassrooms)
        }
        
        if (profileRes.status === 'fulfilled') {
          setUserProfile(profileRes.value.data)
        }
      } catch (err) {
        console.error('Failed to load data', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const isTeacher = userProfile?.role === 'teacher' || userProfile?.is_teacher

  const filteredClassrooms = classrooms.filter(c => 
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.subject?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="relative mb-16">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-12">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                  <GraduationCap className="w-6 h-6 text-emerald-600" />
                </div>
                <span className="text-[10px] font-black text-emerald-600 uppercase tracking-[0.3em]">Academic Hub</span>
              </div>
              <h1 className="text-5xl md:text-6xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight mb-6">
                Your <span className="text-emerald-600">Classrooms</span>
              </h1>
              <p className="text-xl text-slate-500 dark:text-slate-400 font-medium max-w-2xl leading-relaxed">
                {isTeacher 
                  ? 'Empower your students with structured learning paths, collaborative discussions, and real-time feedback.' 
                  : 'Join your peers and teachers in a collaborative learning environment designed for WASSCE excellence.'}
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-4">
              {isTeacher ? (
                <CreateClassroomForm onCreated={(c: any) => setClassrooms(prev => [c, ...prev])} />
              ) : (
                <JoinClassroomForm onJoined={async () => {
                  const r = await classroomApi.getClassrooms()
                  setClassrooms(r.data || [])
                }} />
              )}
            </div>
          </div>

          {/* Stats Bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12">
            {[
              { label: 'Active Classes', value: classrooms.length, icon: BookOpen, color: 'text-blue-500' },
              { label: 'Total Students', value: classrooms.reduce((acc, c) => acc + (c.student_count || 0), 0), icon: Users, color: 'text-emerald-500' },
              { label: 'Assignments', value: '12', icon: Sparkles, color: 'text-amber-500' },
              { label: 'Completion', value: '84%', icon: ArrowRight, color: 'text-purple-500' },
            ].map((stat, i) => (
              <div key={i} className="bg-white dark:bg-slate-950 p-6 rounded-[2rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm">
                <div className="flex items-center gap-4">
                  <div className={cn("w-10 h-10 rounded-xl bg-slate-50 dark:bg-slate-900 flex items-center justify-center", stat.color)}>
                    <stat.icon className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{stat.label}</p>
                    <p className="text-xl font-outfit font-black text-slate-900 dark:text-slate-100">{stat.value}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Search & Filter */}
        <div className="mb-12">
          <div className="relative group">
            <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-6 h-6 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
            <input 
              type="text"
              placeholder="Search by class name or subject..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full h-20 pl-16 pr-8 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-900 rounded-[2rem] font-outfit font-bold text-lg focus:border-emerald-500/50 outline-none transition-all shadow-sm"
            />
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-6">
            <div className="relative w-20 h-20">
              <div className="absolute inset-0 border-4 border-emerald-500/10 rounded-[2rem] animate-pulse" />
              <div className="absolute inset-0 border-4 border-emerald-500 border-t-transparent rounded-[2rem] animate-spin" />
              <GraduationCap className="absolute inset-0 m-auto w-8 h-8 text-emerald-500" />
            </div>
            <p className="text-xs font-black text-slate-400 uppercase tracking-[0.3em]">Synchronizing Classrooms...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredClassrooms.length === 0 ? (
              <div className="col-span-full bg-white dark:bg-slate-950 rounded-[3rem] p-20 text-center border-2 border-dashed border-slate-100 dark:border-slate-900">
                <div className="w-24 h-24 mx-auto mb-8 bg-slate-50 dark:bg-slate-900 rounded-[2.5rem] flex items-center justify-center">
                  <GraduationCap className="w-12 h-12 text-slate-300 dark:text-slate-700" />
                </div>
                <h3 className="text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-4">
                  {searchQuery ? 'No matches found' : isTeacher ? 'No classrooms yet' : 'Not enrolled in any classes'}
                </h3>
                <p className="text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-12 font-medium text-lg">
                  {searchQuery 
                    ? `We couldn't find any classrooms matching "${searchQuery}". Try a different search term.`
                    : isTeacher 
                      ? 'Create your first classroom to start sharing materials and assignments with your students.' 
                      : 'Join a classroom using the unique code provided by your teacher to access study materials.'}
                </p>
                <div className="flex justify-center">
                  {isTeacher ? (
                    <CreateClassroomForm onCreated={(c: any) => setClassrooms(prev => [c, ...prev])} />
                  ) : (
                    <JoinClassroomForm onJoined={async () => {
                      const r = await classroomApi.getClassrooms()
                      setClassrooms(r.data || [])
                    }} />
                  )}
                </div>
              </div>
            ) : (
              filteredClassrooms.map(c => <ClassroomCard key={c.id} classroom={c} />)
            )}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
