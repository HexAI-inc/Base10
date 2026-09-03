'use client'
import AppLayout from '@/components/AppLayout'
import { useEffect, useState, use } from 'react'
import { classroomApi } from '@/lib/api'
import { Loader2, ArrowLeft, User } from 'lucide-react'
import { useRouter } from 'next/navigation'

export default function ClassroomPeoplePage({ params }: any) {
  const router = useRouter()
  const { id } = use(params) as any
  const classroomId = parseInt(id)
  const [teacher, setTeacher] = useState<any>(null)
  const [students, setStudents] = useState<any[]>([])
  const [classroom, setClassroom] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        
        // Try to get classroom and members from separate endpoints
        const [classroomRes, membersRes] = await Promise.allSettled([
          classroomApi.getClassroom(classroomId),
          classroomApi.getClassroomMembers(classroomId),
        ])

        // Set classroom data
        if (classroomRes.status === 'fulfilled') {
          setClassroom(classroomRes.value.data)
        }

        // Handle new members endpoint response format
        if (membersRes.status === 'fulfilled' && membersRes.value.data) {
          const data = membersRes.value.data
          
          // New format: { teacher: {...}, students: [...], total_students: N }
          if (data.teacher) {
            setTeacher(data.teacher)
          }
          if (data.students && Array.isArray(data.students)) {
            setStudents(data.students)
          }
        } else if (membersRes.status === 'rejected') {
          console.warn('Members endpoint not available or returned error:', membersRes.reason)
        }
        
      } catch (err: any) {
        console.error('Error loading people:', err)
        setStudents([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [classroomId])

  const totalMembers = (teacher ? 1 : 0) + students.length

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto p-6 sm:p-8 space-y-8">
        <button
          onClick={() => router.push(`/classrooms/${classroomId}`)}
          className="group flex items-center gap-3 text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all font-black uppercase tracking-widest text-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center group-hover:border-emerald-500/50 transition-colors shadow-sm">
            <ArrowLeft className="w-5 h-5" />
          </div>
          Back to Classroom
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-blue-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <span className="text-xl">👥</span>
              </div>
              <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Class Members</h1>
            </div>
            <p className="text-slate-500 dark:text-slate-400 font-medium">
              {classroom?.name} • {totalMembers} member{totalMembers !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 gap-4">
            <div className="relative">
              <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
              <span className="text-xl absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">👥</span>
            </div>
            <p className="text-xs font-black text-slate-400 uppercase tracking-widest animate-pulse">Loading Members...</p>
          </div>
        ) : (
          <div className="space-y-12">
            {/* Teacher Section */}
            {teacher && (
              <section>
                <div className="flex items-center gap-4 mb-6">
                  <h2 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">Teacher</h2>
                  <div className="h-px flex-1 bg-slate-100 dark:bg-slate-800" />
                </div>
                
                <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-100 dark:border-slate-800 shadow-sm relative overflow-hidden group">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 blur-3xl rounded-full -mr-16 -mt-16 group-hover:bg-emerald-500/10 transition-colors" />
                  
                  <div className="flex items-center gap-6 relative">
                    <div className="w-20 h-20 rounded-[1.5rem] bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center border-2 border-emerald-50 dark:border-emerald-800 shadow-inner">
                      {teacher.avatar_url ? (
                        <img src={teacher.avatar_url} alt={teacher.full_name} className="w-full h-full rounded-[1.5rem] object-cover" />
                      ) : (
                        <User className="w-10 h-10 text-emerald-600 dark:text-emerald-400" />
                      )}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-1">{teacher.full_name}</h3>
                      <div className="flex items-center gap-3">
                        <span className="px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 rounded-full text-[10px] font-black uppercase tracking-widest">Primary Instructor</span>
                        <span className="text-xs text-slate-400 font-medium">@{teacher.username}</span>
                        {teacher.email && <span className="text-xs text-slate-400 font-medium hidden sm:inline">• {teacher.email}</span>}
                      </div>
                    </div>
                  </div>
                </div>
              </section>
            )}

            {/* Students Section */}
            <section>
              <div className="flex items-center gap-4 mb-6">
                <h2 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">Students</h2>
                <div className="h-px flex-1 bg-slate-100 dark:bg-slate-800" />
                <span className="text-xs font-black text-slate-400 uppercase tracking-widest">{students.length} Enrolled</span>
              </div>

              {students.length === 0 ? (
                <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-16 text-center border-2 border-dashed border-slate-100 dark:border-slate-800">
                  <div className="w-24 h-24 mx-auto mb-8 bg-slate-50 dark:bg-slate-800 rounded-[2rem] flex items-center justify-center">
                    <User className="w-12 h-12 text-slate-300 dark:text-slate-600" />
                  </div>
                  <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-3">No students yet</h3>
                  <p className="text-slate-500 dark:text-slate-400 max-w-md mx-auto font-medium">
                    Share your class code with students so they can join this classroom.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {students.map((student) => (
                    <button
                      key={student.id}
                      onClick={() => router.push(`/classrooms/${classroomId}/students/${student.id}`)}
                      className="bg-white dark:bg-slate-900 rounded-3xl p-4 border border-slate-100 dark:border-slate-800 flex items-center gap-4 hover:border-blue-500/30 transition-all group text-left"
                    >
                      <div className="w-12 h-12 rounded-2xl bg-slate-50 dark:bg-slate-950 flex items-center justify-center border border-slate-100 dark:border-slate-800 group-hover:bg-blue-50 dark:group-hover:bg-blue-900/20 transition-colors">
                        {student.avatar_url ? (
                          <img src={student.avatar_url} alt={student.full_name} className="w-full h-full rounded-2xl object-cover" />
                        ) : (
                          <User className="w-6 h-6 text-slate-400 group-hover:text-blue-500 transition-colors" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-black text-slate-900 dark:text-slate-100 truncate">{student.full_name}</h4>
                        <div className="flex items-center gap-2">
                          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest truncate">@{student.username}</p>
                          {student.submission_count !== undefined && (
                            <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">• {student.submission_count} Submissions</span>
                          )}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
