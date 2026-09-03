import { CheckCircle, Clock, ChevronRight, User, FileText, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function SubmissionCard({ 
  submission, 
  onGrade 
}: { 
  submission: any, 
  onGrade?: (id: number, studentName?: string) => void 
}) {
  const submittedAt = new Date(submission.submitted_at)
  
  return (
    <div className="group bg-white dark:bg-slate-900 rounded-[2rem] p-6 border border-slate-100 dark:border-slate-800 hover:border-emerald-500/50 transition-all duration-300 shadow-sm hover:shadow-xl hover:shadow-emerald-500/5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 flex items-center justify-center text-slate-400 group-hover:border-emerald-500/30 group-hover:text-emerald-600 transition-all shadow-inner">
            {submission.student_avatar ? (
              <img src={submission.student_avatar} alt="" className="w-full h-full rounded-2xl object-cover" />
            ) : (
              <User className="w-7 h-7" />
            )}
          </div>
          <div>
            <h3 className="text-lg font-outfit font-black text-slate-900 dark:text-slate-100 group-hover:text-emerald-600 transition-colors">
              {submission.student_name}
            </h3>
            <div className="flex items-center gap-3 mt-1">
              <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
                  {submittedAt.toLocaleDateString()} • {submittedAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              {submission.file_url && (
                <>
                  <span className="w-1 h-1 rounded-full bg-slate-300 dark:bg-slate-700" />
                  <a 
                    href={submission.file_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-[10px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest hover:underline"
                  >
                    <FileText className="w-3 h-3" />
                    View Work
                  </a>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {submission.is_graded ? (
            <div className="flex flex-col items-end">
              <div className="flex items-center gap-2 px-4 h-10 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-900/30 rounded-xl">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span className="text-[10px] font-black text-emerald-600 uppercase tracking-widest">Graded</span>
              </div>
              <p className="mt-2 text-xl font-outfit font-black text-slate-900 dark:text-slate-100">
                {submission.score}<span className="text-xs text-slate-400 ml-1">pts</span>
              </p>
            </div>
          ) : (
            <button 
              onClick={() => onGrade && onGrade(submission.id, submission.student_name)} 
              className="flex items-center gap-3 px-8 h-14 bg-emerald-600 text-white rounded-2xl text-sm font-black uppercase tracking-widest hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-600/20 hover:-translate-y-0.5 active:translate-y-0"
            >
              <span>Grade Now</span>
              <ChevronRight className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>
      
      {submission.content && (
        <div className="mt-6 p-6 bg-slate-50 dark:bg-slate-950 rounded-2xl border border-slate-100 dark:border-slate-800">
          <p className="text-sm text-slate-600 dark:text-slate-400 font-medium leading-relaxed">
            {submission.content}
          </p>
        </div>
      )}
    </div>
  )
}
