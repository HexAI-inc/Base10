'use client'
import { useState, use } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import { classroomApi } from '@/lib/api'
import { useModalStore } from '@/store/modalStore'
import { ArrowLeft, Upload, FileText, Link as LinkIcon, Video, Loader2, Send } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function UploadMaterialPage({ params }: any) {
  const router = useRouter()
  const { id } = use(params) as any
  const classroomId = parseInt(id)
  
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    material_type: 'pdf',
    content_url: '',
  })
  
  const { showSuccess, showError } = useModalStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title || !formData.content_url) {
      showError('Please fill in all required fields', 'Missing Information')
      return
    }

    try {
      setLoading(true)
      await classroomApi.uploadMaterial(classroomId, formData)
      showSuccess('Material uploaded successfully!', 'Success')
      router.push(`/classrooms/${classroomId}/materials`)
    } catch (err: any) {
      console.error(err)
      showError(err.response?.data?.detail || 'Failed to upload material', 'Error')
    } finally {
      setLoading(false)
    }
  }

  const types = [
    { id: 'pdf', label: 'PDF Document', icon: FileText, color: 'text-red-500', bg: 'bg-red-50 dark:bg-red-900/20' },
    { id: 'link', label: 'Web Link', icon: LinkIcon, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-900/20' },
    { id: 'video', label: 'Video URL', icon: Video, color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-900/20' },
    { id: 'other', label: 'Other Resource', icon: Upload, color: 'text-slate-500', bg: 'bg-slate-50 dark:bg-slate-900/20' },
  ]

  return (
    <AppLayout>
      <div className="max-w-3xl mx-auto p-6 sm:p-8 space-y-8">
        <button
          onClick={() => router.back()}
          className="group flex items-center gap-3 text-slate-500 dark:text-slate-400 hover:text-purple-600 dark:hover:text-purple-400 transition-all font-black uppercase tracking-widest text-xs"
        >
          <div className="w-10 h-10 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-center group-hover:border-purple-500/50 transition-colors shadow-sm">
            <ArrowLeft className="w-5 h-5" />
          </div>
          Back
        </button>

        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-purple-600 flex items-center justify-center text-white shadow-lg shadow-purple-600/20">
              <Upload className="w-6 h-6" />
            </div>
            <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Upload Material</h1>
          </div>
          <p className="text-slate-500 dark:text-slate-400 font-medium ml-15">
            Share study resources, notes, or videos with your class.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 p-8 shadow-xl shadow-slate-200/50 dark:shadow-none space-y-8">
          <div className="space-y-8">
            {/* Material Type Selection */}
            <div className="space-y-3">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">Resource Type</label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {types.map((type) => (
                  <button
                    key={type.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, material_type: type.id })}
                    className={cn(
                      "flex flex-col items-center justify-center p-4 rounded-2xl border-2 transition-all gap-2",
                      formData.material_type === type.id
                        ? "border-purple-600 bg-purple-50 dark:bg-purple-900/10"
                        : "border-slate-100 dark:border-slate-800 hover:border-purple-200 dark:hover:border-purple-800/50"
                    )}
                  >
                    <div className={cn("p-2 rounded-xl", type.bg)}>
                      <type.icon className={cn("w-5 h-5", type.color)} />
                    </div>
                    <span className={cn(
                      "text-[10px] font-black uppercase tracking-wider",
                      formData.material_type === type.id ? "text-purple-600" : "text-slate-500"
                    )}>
                      {type.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Title */}
            <div className="space-y-2">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">Resource Title</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="e.g., Week 1: Introduction to Calculus Notes"
                className="w-full h-14 px-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-purple-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-bold transition-all placeholder:text-slate-400"
              />
            </div>

            {/* Content URL */}
            <div className="space-y-2">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">
                {formData.material_type === 'link' || formData.material_type === 'video' ? 'URL / Link' : 'File URL'}
              </label>
              <div className="relative">
                <LinkIcon className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="url"
                  required
                  value={formData.content_url}
                  onChange={(e) => setFormData({ ...formData, content_url: e.target.value })}
                  placeholder="https://..."
                  className="w-full h-14 pl-14 pr-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-2xl focus:border-purple-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-bold transition-all placeholder:text-slate-400"
                />
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-1">Description (Optional)</label>
              <textarea
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Briefly describe what this resource is about..."
                className="w-full p-6 bg-slate-50 dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-[2rem] focus:border-purple-500 focus:ring-0 text-slate-900 dark:text-slate-100 font-medium transition-all placeholder:text-slate-400 resize-none"
              />
            </div>
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full h-16 bg-purple-600 text-white rounded-2xl font-black uppercase tracking-widest text-sm hover:bg-purple-700 transition-all shadow-xl shadow-purple-600/20 flex items-center justify-center gap-3 disabled:opacity-50"
            >
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : (
                <>
                  <span>Upload Resource</span>
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
