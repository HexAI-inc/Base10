import { Trash2, FileText, ExternalLink, Download } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function MaterialCard({ 
  material, 
  isTeacher, 
  onDelete 
}: { 
  material: any
  isTeacher?: boolean
  onDelete?: (id: number) => void
}) {
  return (
    <div className="group bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-100 dark:border-slate-800 hover:border-purple-500/30 transition-all duration-500 shadow-sm hover:shadow-2xl hover:shadow-purple-500/5 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 blur-3xl rounded-full -mr-16 -mt-16 group-hover:bg-purple-500/10 transition-colors" />
      
      <div className="flex items-start justify-between mb-6 relative">
        <div className="flex items-center gap-4 flex-1">
          <div className="w-14 h-14 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 flex items-center justify-center text-slate-400 group-hover:bg-purple-50 dark:group-hover:bg-purple-900/20 group-hover:text-purple-500 transition-all duration-500">
            <FileText className="w-7 h-7" />
          </div>
          <div>
            <h3 className="text-xl font-outfit font-black text-slate-900 dark:text-slate-100 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
              {material.title}
            </h3>
            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
              Study Resource
            </span>
          </div>
        </div>
        
        {isTeacher && onDelete && (
          <button
            onClick={() => onDelete(material.id)}
            className="w-12 h-12 flex items-center justify-center text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-2xl transition-all border border-transparent hover:border-red-100 dark:hover:border-red-900/50"
            title="Delete material"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        )}
      </div>

      <p className="text-sm text-slate-500 dark:text-slate-400 mb-8 font-medium leading-relaxed line-clamp-2 relative">
        {material.description || 'No description provided for this resource.'}
      </p>

      <div className="flex items-center gap-3 relative">
        <a 
          href={material.material_url || material.file_url} 
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 flex items-center justify-center gap-3 h-14 bg-purple-600 text-white rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-purple-700 transition-all shadow-lg shadow-purple-600/20"
        >
          <ExternalLink className="w-4 h-4" />
          Open Resource
        </a>
        
        <button className="w-14 h-14 flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded-2xl hover:bg-purple-100 dark:hover:bg-purple-900/20 hover:text-purple-600 transition-all">
          <Download className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}
