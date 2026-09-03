'use client'
import { useState, use } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import { classroomApi } from '@/lib/api'
import { useModalStore } from '@/store/modalStore'
import { ArrowLeft, Send, Calendar, Award, FileText, Loader2 } from 'lucide-react'

export default function CreateAssignmentPage({ params }: any) {
  const router = useRouter()
  const { id } = use(params) as any
  const classroomId = parseInt(id)
  
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_date: '',
    points: 100,
  })
  
  const { showSuccess, showError } = useModalStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title || !formData.due_date) {
      showError('Please fill in all required fields', 'Missing Information')
      return
    }

    try {
      setLoading(true)
      await classroomApi.createManualAssignment(classroomId, {
        ...formData,
        due_date: new Date(formData.due_date).toISOString()
      })
      showSuccess('Assignment created successfully!', 'Success')
      router.push(`/classrooms/${classroomId}/assignments`)
    } catch (err: any) {
      console.error(err)
      showError(err.response?.data?.detail || 'Failed to create assignment', 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto p-6 sm:p-8 space-y-8">
        <button
          onClick={() => router.back()}
          className="group flex items-center gap-3 text-slate-500 dark:text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all font-black uppercase tracking-widest text-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center group-hover:border-emerald-500/50 transition-colors shadow-sm">
            <ArrowLeft className="w-5 h-5" />
          </div>
          Back
        </button>

        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center text-white shadow-lg shadow-emerald-600/20">
              <FileText className="w-6 h-6" />
            </div>
            <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Create Assignment</h1>
          </div>
          <p className="text-slate-500 dark:text-slate-400 font-medium ml-15">
            Set up a new task for your students to complete.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 p-8 shadow-xl shadow-slate-200/50 dark:shadow-none space-y-8">
          <div className="space-y-6">
            {/* Title */}
            <div className="space-y-2">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">Assignment Title</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g., Introduction to Algebra Quiz"
                className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-emerald-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-bold transition-all placeholder:text-slate-400"
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">Instructions</label>
              <textarea
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Provide detailed instructions for your students..."
                className="w-full p-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-[2rem] focus:border-emerald-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all placeholder:text-slate-400 resize-none"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Due Date */}
              <div className="space-y-2">
                <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">Due Date</label>
                <div className="relative">
                  <Calendar className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="datetime-local"
                    required
                    value={formData.due_date}
                    onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                    className="w-full h-14 pl-14 pr-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-emerald-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-bold transition-all"
                  />
                </div>
              </div>

              {/* Points */}
              <div className="space-y-2">
                <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">Total Points</label>
                <div className="relative">
                  <Award className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="number"
                    required
                    min="0"
                    value={formData.points}
                    onChange={(e) => setFormData({ ...formData, points: parseInt(e.target.value) })}
                    className="w-full h-14 pl-14 pr-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-emerald-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-bold transition-all"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full h-16 bg-emerald-600 text-white rounded-2xl font-black uppercase tracking-widest text-sm hover:bg-emerald-700 transition-all shadow-xl shadow-emerald-600/20 flex items-center justify-center gap-3 disabled:opacity-50"
            >
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <>
                  <span>Create Assignment</span>
                  <Send className="w-5 h-5" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </AppLayout>
  )
}
