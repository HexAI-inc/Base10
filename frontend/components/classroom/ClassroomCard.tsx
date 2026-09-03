import Link from 'next/link'
import { Users, GraduationCap, BookOpen, ChevronRight, Calendar, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function ClassroomCard({ classroom }: { classroom: any }) {
  // Format date safely
  const formatDate = (dateString: string) => {
    if (!dateString) return 'Recently'
    try {
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return 'Recently'
      return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    } catch {
      return 'Recently'
    }
  }

  const isTeacher = classroom.role === 'teacher'

  return (
    <Link 
      href={`/classrooms/${classroom.id}`} 
      className="group relative bg-white dark:bg-slate-950 rounded-[2.5rem] p-8 border-2 border-slate-50 dark:border-slate-900 hover:border-emerald-500/50 transition-all duration-500 shadow-sm hover:shadow-2xl hover:shadow-emerald-500/10 overflow-hidden flex flex-col h-full"
    >
      {/* Premium Gradient Background */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-emerald-500/5 rounded-full -mr-24 -mt-24 group-hover:scale-150 transition-transform duration-700 blur-3xl" />
      
      <div className="relative flex flex-col h-full">
        <div className="flex items-start justify-between mb-8">
          <div className="flex items-center gap-5">
            <div className={cn(
              "w-16 h-16 rounded-3xl flex items-center justify-center shadow-2xl transition-all duration-500 group-hover:scale-110 group-hover:rotate-3",
              isTeacher 
                ? "bg-emerald-600 text-white shadow-emerald-600/20" 
                : "bg-slate-900 dark:bg-emerald-500 text-white dark:text-slate-950 shadow-slate-900/20 dark:shadow-emerald-500/20"
            )}>
              {isTeacher ? <GraduationCap className="w-8 h-8" /> : <BookOpen className="w-8 h-8" />}
            </div>
            <div>
              <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 transition-colors tracking-tight">
                {classroom.name}
              </h3>
              <div className="flex items-center gap-2.5 mt-1.5">
                <span className={cn(
                  "text-[10px] font-black uppercase tracking-[0.2em] px-3 py-1 rounded-full",
                  isTeacher 
                    ? "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400" 
                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400"
                )}>
                  {isTeacher ? 'Teacher' : 'Student'}
                </span>
                {classroom.grade_level && (
                  <>
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/30" />
                    <span className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                      {classroom.grade_level}
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>
          
          {isTeacher && (
            <div className="w-10 h-10 rounded-2xl bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            </div>
          )}
        </div>

        <div className="flex-1">
          <div className="flex flex-wrap gap-2.5 mb-8">
            {classroom.subject && (
              <span className="px-4 py-1.5 bg-slate-50 dark:bg-slate-900 border-2 border-slate-100 dark:border-slate-800 text-slate-600 dark:text-slate-400 rounded-2xl text-[10px] font-black uppercase tracking-widest">
                {classroom.subject}
              </span>
            )}
            {!isTeacher && classroom.teacher_name && (
              <span className="px-4 py-1.5 bg-emerald-50 dark:bg-emerald-900/10 border-2 border-emerald-100 dark:border-emerald-900/20 text-emerald-700 dark:text-emerald-400 rounded-2xl text-[10px] font-black uppercase tracking-widest flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                {classroom.teacher_name}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between pt-8 border-t-2 border-slate-50 dark:border-slate-900">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
                <Users className="w-5 h-5 text-emerald-500" />
              </div>
              <div>
                <p className="text-sm font-black text-slate-900 dark:text-slate-100 leading-none">
                  {classroom.student_count ?? 0}
                </p>
                <p className="text-[10px] font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest mt-1">
                  Students
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3 text-slate-400 group-hover:text-emerald-500 transition-all duration-500">
            <span className="text-[10px] font-black uppercase tracking-[0.2em]">Enter Room</span>
            <div className="w-10 h-10 rounded-2xl bg-slate-50 dark:bg-slate-900 group-hover:bg-emerald-600 group-hover:text-white flex items-center justify-center transition-all duration-500">
              <ChevronRight className="w-6 h-6 transform group-hover:translate-x-0.5 transition-transform" />
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}
