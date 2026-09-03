'use client'
import AppLayout from '@/components/AppLayout'
import { useEffect, useState, use } from 'react'
import { classroomApi } from '@/lib/api'
import { Loader2, ArrowLeft, Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import MaterialCard from '@/components/classroom/MaterialCard'
import { useModalStore } from '@/store/modalStore'

export default function ClassroomMaterialsPage({ params }: any) {
  const router = useRouter()
  const { id } = use(params) as any
  const classroomId = parseInt(id)
  const [materials, setMaterials] = useState<any[]>([])
  const [classroom, setClassroom] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const { showSuccess, showError, showConfirm } = useModalStore()

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const [materialsRes, classroomRes] = await Promise.all([
          classroomApi.getMaterials(classroomId),
          classroomApi.getClassroom(classroomId)
        ])
        setMaterials(materialsRes.data || [])
        setClassroom(classroomRes.data)
      } catch (err: any) {
        console.error(err)
        if (err.response?.status === 404) {
          setMaterials([])
        } else {
          setMaterials([])
        }
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [classroomId])

  const handleDelete = (materialId: number) => {
    showConfirm(
      'This will permanently delete this material. This action cannot be undone.',
      async () => {
        try {
          await classroomApi.deleteMaterial(materialId)
          setMaterials(prev => prev.filter(m => m.id !== materialId))
          showSuccess('Material deleted successfully.', 'Deleted')
        } catch (err: any) {
          console.error('Failed to delete material', err)
          if (err.response?.status === 403) {
            showError('You do not have permission to delete this material.', 'Permission Denied')
          } else {
            showError('Unable to delete material. Please try again.', 'Delete Failed')
          }
        }
      },
      'Delete Material'
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
              <div className="w-10 h-10 rounded-xl bg-purple-500 flex items-center justify-center shadow-lg shadow-purple-500/20">
                <span className="text-xl">📚</span>
              </div>
              <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Materials</h1>
            </div>
            <p className="text-slate-500 dark:text-slate-400 font-medium">
              {classroom?.is_teacher ? 'Upload and manage study resources' : 'Access your class study materials and resources'}
            </p>
          </div>

          {classroom?.is_teacher && (
            <button
              onClick={() => router.push(`/classrooms/${classroomId}/materials/upload`)}
              className="flex items-center justify-center gap-3 px-8 h-14 bg-purple-600 text-white rounded-2xl font-black uppercase tracking-widest text-sm hover:bg-purple-700 transition-all shadow-lg shadow-purple-600/20 hover:-translate-y-0.5 active:translate-y-0"
            >
              <span>Upload Material</span>
              <Plus className="w-5 h-5" />
            </button>
          )}
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center h-64 gap-4">
            <div className="relative">
              <div className="w-12 h-12 border-4 border-purple-500/20 border-t-purple-500 rounded-full animate-spin" />
              <span className="text-xl absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">📚</span>
            </div>
            <p className="text-xs font-black text-slate-400 uppercase tracking-widest animate-pulse">Loading Materials...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {materials.length === 0 ? (
              <div className="col-span-full bg-white dark:bg-slate-900 rounded-[2.5rem] p-16 text-center border-2 border-dashed border-slate-100 dark:border-slate-800">
                <div className="w-24 h-24 mx-auto mb-8 bg-slate-50 dark:bg-slate-800 rounded-[2rem] flex items-center justify-center">
                  <span className="text-4xl opacity-20">📚</span>
                </div>
                <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-3">No materials yet</h3>
                <p className="text-slate-500 dark:text-slate-400 max-w-md mx-auto font-medium">
                  {classroom?.is_teacher 
                    ? 'Upload your first study material to share resources, notes, or guides with your students.' 
                    : 'Your teacher hasnt uploaded any materials yet. Check back soon!'}
                </p>
              </div>
            ) : (
              materials.map(m => (
                <MaterialCard 
                  key={m.id} 
                  material={m} 
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