"use client"
import { useState } from 'react'
import { classroomApi } from '@/lib/api'
import { useModalStore } from '@/store/modalStore'
import { Plus, X, Key, Loader2, Sparkles, ArrowRight } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function JoinClassroomForm({ onJoined }: { onJoined?: () => void }) {
  const [open, setOpen] = useState(false)
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const { showSuccess, showError } = useModalStore()

  const submit = async (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!code.trim()) return
    try {
      setLoading(true)
      await classroomApi.joinClassroom(code.trim())
      setCode('')
      setOpen(false)
      showSuccess('You have successfully joined the classroom!', 'Welcome Aboard')
      if (onJoined) onJoined()
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Failed to join classroom. Please check the code.', 'Error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button 
        onClick={() => setOpen(true)} 
        className="h-14 px-8 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] flex items-center gap-3 shadow-xl hover:scale-105 transition-all"
      >
        <Plus className="w-5 h-5" />
        Join Classroom
      </button>

      {open && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
          <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm animate-in fade-in duration-300" onClick={() => setOpen(false)} />
          
          <form 
            onSubmit={submit} 
            className="relative bg-white dark:bg-slate-950 w-full max-w-md rounded-[3rem] overflow-hidden shadow-2xl border-2 border-slate-50 dark:border-slate-900 animate-in zoom-in-95 duration-300"
          >
            <div className="p-10">
              <div className="flex items-center justify-between mb-10">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-blue-500 flex items-center justify-center text-white shadow-xl shadow-blue-500/20">
                    <Key className="w-7 h-7" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Join Class</h3>
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Enter your invite code</p>
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
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Classroom Code</label>
                  <input 
                    autoFocus
                    value={code} 
                    onChange={(e) => setCode(e.target.value.toUpperCase())} 
                    placeholder="e.g. MATH-123" 
                    className="w-full h-20 px-8 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-blue-500/50 rounded-2xl outline-none text-slate-900 dark:text-slate-100 font-outfit font-black text-3xl text-center tracking-[0.2em] transition-all placeholder:text-slate-200 dark:placeholder:text-slate-800 placeholder:tracking-normal placeholder:text-lg"
                    required
                  />
                </div>

                <p className="text-xs text-slate-500 dark:text-slate-400 text-center font-medium">
                  Ask your teacher for the unique classroom code to join their learning space.
                </p>

                <button 
                  type="submit" 
                  disabled={loading || !code.trim()}
                  className="w-full h-16 bg-blue-600 text-white rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] flex items-center justify-center gap-3 shadow-xl shadow-blue-600/20 hover:scale-105 transition-all disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <ArrowRight className="w-5 h-5" />}
                  Join Classroom
                </button>
              </div>
            </div>
          </form>
        </div>
      )}
    </>
  )
}
