'use client'
import AppLayout from '@/components/AppLayout'
import { useEffect, useState, use } from 'react'
import { classroomApi } from '@/lib/api'
import { Loader2, ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'
import AssignmentCard from '@/components/classroom/AssignmentCard'
import { useModalStore } from '@/store/modalStore'

export default function ClassroomAssignmentsPage({ params }: any) {
  const router = useRouter()
  const { id } = use(params) as any
  const classroomId = parseInt(id)
  const [assignments, setAssignments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [classroom, setClassroom] = useState<any>(null)
  const { showSuccess, showError, showConfirm } = useModalStore()

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const [assignmentsRes, classroomRes] = await Promise.allSettled([
          classroomApi.getAssignments(classroomId),
          classroomApi.getClassroom(classroomId)
        ])
        
        // Handle assignments response
        if (assignmentsRes.status === 'fulfilled') {
          setAssignments(assignmentsRes.value.data || [])
        } else {
          console.warn('Failed to load assignments:', assignmentsRes.reason)
          setAssignments([])
        }
        
        // Handle classroom response
        if (classroomRes.status === 'fulfilled') {
          setClassroom(classroomRes.value.data)
        } else {
          console.warn('Failed to load classroom:', classroomRes.reason)
        }
      } catch (err: any) {
        console.error('Unexpected error loading data:', err)
        setAssignments([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [classroomId])

  const handleDelete = (assignmentId: number) => {
    showConfirm(
      'This will permanently delete the assignment and all student submissions. This action cannot be undone.',
      async () => {
        try {
          await classroomApi.deleteAssignment(assignmentId)
          setAssignments(prev => prev.filter(a => a.id !== assignmentId))
          showSuccess('Assignment deleted successfully.', 'Deleted')
        } catch (err: any) {
          console.error('Failed to delete assignment', err)
          if (err.response?.status === 403) {
            showError('You do not have permission to delete this assignment.', 'Permission Denied')
          } else {
            showError('Unable to delete assignment. Please try again.', 'Delete Failed')
          }
        }
      },
      'Delete Assignment'
    )
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto p-6 sm:p-8 space-y-8">
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
              <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <span className="text-xl">📝</span>
              </div>
              <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Assignments</h1>
            </div>
            <p className="text-slate-500 dark:text-slate-400 font-medium">
              {classroom?.is_teacher ? 'Manage and grade student submissions' : 'View and submit your class assignments'}
            </p>
          </div>

          {classroom?.is_teacher && (
            <button
              onClick={() => router.push(`/classrooms/${classroomId}/assignments/create`)}
              className="flex items-center justify-center gap-3 px-8 h-14 bg-emerald-600 text-white rounded-2xl font-black uppercase tracking-widest text-sm hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-600/20 hover:-translate-y-0.5 active:translate-y-0"
            >
              <span>Create Assignment</span>
              <Plus className="w-5 h-5" />
            </button>
          )}
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 gap-4">
            <div className="relative">
              <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
              <span className="text-xl absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">📝</span>
            </div>
            <p className="text-xs font-black text-slate-400 uppercase tracking-widest animate-pulse">Loading Assignments...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {assignments.length === 0 ? (
              <div className="col-span-full bg-white dark:bg-slate-900 rounded-[2.5rem] p-16 text-center border-2 border-dashed border-slate-100 dark:border-slate-800">
                <div className="w-24 h-24 mx-auto mb-8 bg-slate-50 dark:bg-slate-800 rounded-[2rem] flex items-center justify-center">
                  <span className="text-4xl opacity-20">📝</span>
                </div>
                <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-3">No assignments yet</h3>
                <p className="text-slate-500 dark:text-slate-400 max-w-md mx-auto font-medium">
                  {classroom?.is_teacher 
                    ? 'Create your first assignment to start tracking student progress and providing feedback.' 
                    : 'Your teacher hasn\'t posted any assignments yet. Enjoy the break!'}
                </p>
              </div>
            ) : (
              assignments.map(a => (
                <AssignmentCard 
                  key={a.id} 
                  assignment={a} 
                  classroomId={classroomId} 
                  isTeacher={classroom?.is_teacher}
                  onDelete={classroom?.is_teacher ? handleDelete : undefined}
                />
              ))
            )}
          </div>
        )}
      </div>
    </AppLayout>
  )
}

import { Plus } from 'lucide-react'
