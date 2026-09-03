'use client'
import AppLayout from '@/components/AppLayout'
import { useEffect, useState, use } from 'react'
import { classroomApi } from '@/lib/api'
import { Loader2, ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useModalStore } from '@/store/modalStore'

export default function SubmissionsPage({ params }: any) {
  const router = useRouter()
  const { assignmentId, id } = use(params) as any
  const assignmentId_num = parseInt(assignmentId)
  const classroomId = parseInt(id)
  const [submissions, setSubmissions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const { showError, showConfirm, showSuccess } = useModalStore()

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const res = await classroomApi.getSubmissions(assignmentId_num)
        setSubmissions(res.data || [])
      } catch (err: any) {
        console.error(err)
        if (err.response?.status === 404) {
          setSubmissions([])
        } else {
          setSubmissions([])
        }
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [assignmentId_num])

  const grade = async (submissionId: number, studentName?: string) => {
    const score = parseInt(prompt('Enter score') || '0')
    if (isNaN(score)) return
    try {
      setActionLoading(submissionId)
      await classroomApi.gradeSubmission(submissionId, { score })
      
      // Show notification feedback with emoji based on score
      const percentage = (score / 100) * 100 // Assuming max points, adjust as needed
      let emoji = '📊'
      if (percentage >= 80) emoji = '🎉'
      else if (percentage >= 60) emoji = '✅'
      
      showSuccess(
        `${studentName ? studentName + "'s" : 'Student'} work has been graded (${score} points). They will receive a notification via push notification and email.`,
        `${emoji} Grade Submitted`
      )
      
      const res = await classroomApi.getSubmissions(assignmentId_num)
      setSubmissions(res.data || [])
    } catch (err) {
      console.error(err)
      showError('Unable to grade submission. Please try again.', 'Grading Failed')
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto p-6 sm:p-8 space-y-8">
        <button
          onClick={() => router.push(`/classrooms/${classroomId}/assignments`)}
          className="group flex items-center gap-3 text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all font-black uppercase tracking-widest text-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center group-hover:border-emerald-500/50 transition-colors shadow-sm">
            <ArrowLeft className="w-5 h-5" />
          </div>
          Back to Assignments
        </button>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center text-white shadow-lg shadow-emerald-600/20">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Submissions</h1>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Assignment Review Hub</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3 bg-white dark:bg-slate-900 p-2 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm">
            <div className="px-4 py-2 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800">
              <p className="text-[8px] font-black text-slate-400 uppercase tracking-widest mb-0.5">Total</p>
              <p className="text-sm font-black text-slate-900 dark:text-slate-100">{submissions.length}</p>
            </div>
            <div className="px-4 py-2 bg-emerald-50 dark:bg-emerald-900/10 rounded-xl border border-emerald-100 dark:border-emerald-900/20">
              <p className="text-[8px] font-black text-emerald-600 uppercase tracking-widest mb-0.5">Graded</p>
              <p className="text-sm font-black text-emerald-600">{submissions.filter(s => s.is_graded).length}</p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 gap-4">
            <div className="relative">
              <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <FileText className="w-5 h-5 text-emerald-500" />
              </div>
            </div>
            <p className="text-xs font-black text-slate-400 uppercase tracking-widest animate-pulse">Loading Submissions...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {submissions.length === 0 ? (
              <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-16 text-center border-2 border-dashed border-slate-100 dark:border-slate-800">
                <div className="w-24 h-24 mx-auto mb-8 bg-slate-50 dark:bg-slate-800 rounded-[2rem] flex items-center justify-center">
                  <FileText className="w-10 h-10 text-slate-300" />
                </div>
                <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-3">No submissions yet</h3>
                <p className="text-slate-500 dark:text-slate-400 max-w-md mx-auto font-medium">
                  Students haven't submitted any work for this assignment yet. Check back later!
                </p>
              </div>
            ) : (
              submissions.map(s => (
                <SubmissionCard key={s.id} submission={s} onGrade={grade} />
              ))
            )}
          </div>
        )}
      </div>
    </AppLayout>
  )
}

import SubmissionCard from '@/components/classroom/SubmissionCard'
import { FileText } from 'lucide-react'
