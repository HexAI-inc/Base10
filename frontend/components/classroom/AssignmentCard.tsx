import Link from 'next/link'
import { Calendar, CheckCircle, Clock, Trash2, Bell, AlertCircle, ChevronRight, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function AssignmentCard({ 
  assignment, 
  classroomId, 
  isTeacher,
  onDelete 
}: { 
  assignment: any
  classroomId: number
  isTeacher?: boolean
  onDelete?: (id: number) => void
}) {
  const dueDate = new Date(assignment.due_date)
  const isOverdue = dueDate < new Date()
  const hasSubmitted = assignment.has_submitted
  
  // Calculate priority based on due date (within 24 hours = HIGH)
  const hoursUntilDue = (dueDate.getTime() - Date.now()) / (1000 * 60 * 60)
  const isUrgent = hoursUntilDue > 0 && hoursUntilDue <= 24
  const priority = isUrgent ? 'HIGH' : 'MEDIUM'
  
  return (
    <div className="group bg-white dark:bg-slate-900 rounded-3xl p-6 border border-slate-200 dark:border-slate-800 hover:border-emerald-500/50 transition-all duration-300 shadow-sm hover:shadow-xl hover:shadow-emerald-500/5">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center",
              isUrgent && !isOverdue ? "bg-red-100 dark:bg-red-900/20 text-red-600" : "bg-emerald-100 dark:bg-emerald-900/20 text-emerald-600"
            )}>
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-outfit font-black text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 transition-colors">
                {assignment.title}
              </h3>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                  {assignment.assignment_type}
                </span>
                <span className="w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-700" />
                <span className="text-[10px] font-black text-emerald-600 uppercase tracking-widest">
                  {assignment.max_points} Points
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col items-end gap-2">
          {/* Status badge for students */}
          {!isTeacher && hasSubmitted && (
            <span className="px-3 py-1 bg-emerald-500 text-white rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-1 shadow-lg shadow-emerald-500/20">
              <CheckCircle className="w-3 h-3" />
              Submitted
            </span>
          )}
          
          {/* Status badge for overdue */}
          {!isTeacher && !hasSubmitted && isOverdue && (
            <span className="px-3 py-1 bg-red-500 text-white rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg shadow-red-500/20">
              Overdue
            </span>
          )}

          {isUrgent && !isOverdue && !hasSubmitted && (
            <span className="px-3 py-1 bg-amber-500 text-white rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-1 shadow-lg shadow-amber-500/20 animate-pulse">
              <AlertCircle className="w-3 h-3" />
              Urgent
            </span>
          )}
        </div>
      </div>

      <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2 mb-6 font-medium leading-relaxed">
        {assignment.description}
      </p>

      <div className="flex items-center justify-between pt-6 border-t border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
            <Calendar className="w-4 h-4 text-emerald-500" />
            <span className="text-xs font-black uppercase tracking-widest">Due {dueDate.toLocaleDateString()}</span>
          </div>
          
          {isTeacher && (
            <div className="flex items-center gap-3">
              <div className="h-4 w-px bg-slate-200 dark:bg-slate-800" />
              <span className="text-xs font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">
                {assignment.submission_count || 0} Submissions
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3">
          {isTeacher ? (
            <>
              {onDelete && (
                <button
                  onClick={() => onDelete(assignment.id)}
                  className="w-12 h-12 flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-2xl transition-all border border-transparent hover:border-red-100 dark:hover:border-red-900/50"
                  title="Delete assignment"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              )}
              <Link 
                href={`/classrooms/${classroomId}/assignments/${assignment.id}/submissions`}
                className="flex items-center gap-2 px-6 h-12 bg-emerald-600 text-white rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-600/20"
              >
                Submissions
                <ChevronRight className="w-4 h-4" />
              </Link>
            </>
          ) : (
            <>
              <Link 
                href={`/classrooms/${classroomId}/assignments/${assignment.id}`}
                className="flex items-center gap-2 px-6 h-12 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-slate-200 dark:hover:bg-slate-700 transition-all"
              >
                Details
              </Link>
              {!hasSubmitted && (
                <Link 
                  href={`/classrooms/${classroomId}/assignments/${assignment.id}/submit`}
                  className="flex items-center gap-2 px-6 h-12 bg-emerald-600 text-white rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-600/20"
                >
                  Submit
                  <ChevronRight className="w-4 h-4" />
                </Link>
              )}
            </>
          )}
        </div>
      </div>

      {/* Teacher view priority info */}
      {isTeacher && (
        <div className="mt-4 flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-[10px] font-black text-slate-400 uppercase tracking-widest">
            <Bell className="w-3 h-3" />
            <span>{priority === 'HIGH' ? 'Push + Email + SMS' : 'Push + Email'}</span>
          </div>
        </div>
      )}

      {/* Student view grade */}
      {!isTeacher && assignment.is_graded && (
        <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-black text-slate-500 uppercase tracking-widest">Your Grade</span>
            <span className="text-xl font-outfit font-black text-emerald-600 dark:text-emerald-400">
              {assignment.final_score}/{assignment.max_points}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
