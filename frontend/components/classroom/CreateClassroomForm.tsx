"use client"
import { useState } from 'react'
import { classroomApi } from '@/lib/api'
import { useModalStore } from '@/store/modalStore'
import { Plus, X, GraduationCap, BookOpen, Layers, Loader2, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function CreateClassroomForm({ onCreated }: { onCreated?: (c: any) => void }) {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [subject, setSubject] = useState('')
  const [grade, setGrade] = useState('')
  const [loading, setLoading] = useState(false)
  const { showSuccess, showError } = useModalStore()

  const submit = async (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!name.trim()) return
    try {
      setLoading(true)
      const res = await classroomApi.createClassroom({ name: name.trim(), subject, grade_level: grade })
      setName('')
      setSubject('')
      setGrade('')
      setOpen(false)
      showSuccess(`Classroom "${res.data.name}" created successfully!`, 'Classroom Created')
      if (onCreated) onCreated(res.data)
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Failed to create classroom', 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button 
        onClick={() => setOpen(true)} 
        className="h-14 px-8 bg-emerald-600 text-white rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] flex items-center gap-3 shadow-xl shadow-emerald-600/20 hover:scale-105 transition-all"
      >
        <Plus className="w-5 h-5" />
        Create Classroom
      </button>

      {open && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
          <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm animate-in fade-in duration-300" onClick={() => setOpen(false)} />
          
          <form 
            onSubmit={submit} 
            className="relative bg-white dark:bg-slate-950 w-full max-w-lg rounded-[3rem] overflow-hidden shadow-2xl border-2 border-slate-50 dark:border-slate-900 animate-in zoom-in-95 duration-300"
          >
            <div className="p-10">
              <div className="flex items-center justify-between mb-10">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-emerald-500 flex items-center justify-center text-white shadow-xl shadow-emerald-500/20">
                    <GraduationCap className="w-7 h-7" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">New Classroom</h3>
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Set up your learning space</p>
                  </div>
                </div>
                <button 
                  type="button" 
                  onClick={() => setOpen(false)}
                  className="w-10 h-10 flex items-center justify-center rounded-xl bg-slate-50 dark:bg-slate-900 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-8">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Classroom Name</label>
                  <input 
                    autoFocus
                    value={name} 
                    onChange={(e) => setName(e.target.value)} 
                    placeholder="e.g. Advanced Mathematics" 
                    className="w-full h-16 px-8 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-emerald-500/50 rounded-2xl outline-none text-slate-900 dark:text-slate-100 font-bold transition-all"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Subject</label>
                    <input 
                      value={subject} 
                      onChange={(e) => setSubject(e.target.value)} 
                      placeholder="e.g. Math" 
                      className="w-full h-16 px-8 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-emerald-500/50 rounded-2xl outline-none text-slate-900 dark:text-slate-100 font-bold transition-all"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Grade Level</label>
                    <input 
                      value={grade} 
                      onChange={(e) => setGrade(e.target.value)} 
                      placeholder="e.g. SSS 3" 
                      className="w-full h-16 px-8 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-emerald-500/50 rounded-2xl outline-none text-slate-900 dark:text-slate-100 font-bold transition-all"
                    />
                  </div>
                </div>

                <button 
                  type="submit" 
                  disabled={loading || !name.trim()}
                  className="w-full h-16 bg-emerald-600 text-white rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] flex items-center justify-center gap-3 shadow-xl shadow-emerald-600/20 hover:scale-105 transition-all disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                  Create Classroom
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
    </>
  )
}
