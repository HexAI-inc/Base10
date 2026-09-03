"use client"
import { useState, useEffect } from 'react'
import { classroomApi } from '@/lib/api'
import { useModalStore } from '@/store/modalStore'
import { X, Settings, Loader2, Save } from 'lucide-react'

interface EditClassroomFormProps {
  classroom: any
  onClose: () => void
  onSuccess: (updated: any) => void
}

export default function EditClassroomForm({ classroom, onClose, onSuccess }: EditClassroomFormProps) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [subject, setSubject] = useState('')
  const [gradeLevel, setGradeLevel] = useState('')
  const [loading, setLoading] = useState(false)
  const { showSuccess, showError } = useModalStore()

  useEffect(() => {
    if (classroom) {
      setName(classroom.name || '')
      setDescription(classroom.description || '')
      setSubject(classroom.subject || '')
      setGradeLevel(classroom.grade_level || '')
    }
  }, [classroom])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return

    try {
      setLoading(true)
      const updateData: any = {}
      
      if (name !== classroom.name) updateData.name = name.trim()
      if (description !== (classroom.description || '')) updateData.description = description.trim()
      if (subject !== (classroom.subject || '')) updateData.subject = subject.trim()
      if (gradeLevel !== (classroom.grade_level || '')) updateData.grade_level = gradeLevel.trim()

      if (Object.keys(updateData).length === 0) {
        onClose()
        return
      }

      const res = await classroomApi.updateClassroom(classroom.id, updateData)
      showSuccess('Classroom updated successfully!', 'Updated')
      onSuccess(res.data)
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Failed to update classroom', 'Update Failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
      <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-xl" onClick={onClose} />
      
      <div className="relative bg-white dark:bg-slate-950 w-full max-w-xl rounded-[3rem] overflow-hidden shadow-2xl border-2 border-slate-50 dark:border-slate-900 animate-in fade-in zoom-in duration-300">
        <div className="p-10 border-b-2 border-slate-50 dark:border-slate-900 flex items-center justify-between">
          <div className="flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-emerald-500 flex items-center justify-center text-white shadow-2xl shadow-emerald-500/20">
              <Settings className="w-7 h-7" />
            </div>
            <div>
              <h3 className="text-3xl font-outfit font-black text-slate-900 dark:text-white tracking-tight">Edit Class</h3>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Update classroom settings</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="w-12 h-12 flex items-center justify-center rounded-full hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-400 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-10 space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Class Name</label>
              <input 
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full h-16 px-6 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-emerald-500/50 rounded-2xl outline-none text-slate-900 dark:text-white font-bold transition-all"
                placeholder="e.g. Advanced Physics"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Subject</label>
              <input 
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full h-16 px-6 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-emerald-500/50 rounded-2xl outline-none text-slate-900 dark:text-white font-bold transition-all"
                placeholder="e.g. Science"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Grade Level</label>
              <input 
                type="text"
                value={gradeLevel}
                onChange={(e) => setGradeLevel(e.target.value)}
                className="w-full h-16 px-6 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-emerald-500/50 rounded-2xl outline-none text-slate-900 dark:text-white font-bold transition-all"
                placeholder="e.g. Grade 12"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Description</label>
              <input 
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full h-16 px-6 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-emerald-500/50 rounded-2xl outline-none text-slate-900 dark:text-white font-bold transition-all"
                placeholder="Brief description..."
              />
            </div>
          </div>

          <div className="pt-4 flex gap-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 h-16 bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] hover:bg-slate-200 dark:hover:bg-slate-800 transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim()}
              className="flex-[2] h-16 bg-emerald-600 text-white rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] flex items-center justify-center gap-3 shadow-xl shadow-emerald-600/20 hover:scale-105 transition-all disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
