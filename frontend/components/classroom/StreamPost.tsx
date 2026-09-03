'use client'
import { useState } from 'react'
import { 
  MessageCircle, 
  Download, 
  FileText, 
  Image as ImageIcon, 
  File as FileIcon, 
  MoreVertical,
  Clock,
  User,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Share2,
  Heart
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface StreamPostProps {
  post: {
    id: number
    content: string
    created_at: string
    author_name: string
    author_role?: 'teacher' | 'student'
    attachment?: {
      name: string
      type: 'pdf' | 'image' | 'document'
      size: number
      url: string
    }
    replies?: any[]
    canEdit?: boolean
  }
}

export default function StreamPost({ post }: StreamPostProps) {
  const [expanded, setExpanded] = useState(false)
  const [liked, setLiked] = useState(false)
  
  const needsTruncation = post.content.length > 300
  const displayContent = expanded ? post.content : post.content.slice(0, 300)

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-GB', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
  
  return (
    <article className="bg-white dark:bg-slate-950 rounded-[2.5rem] p-8 shadow-sm hover:shadow-2xl hover:shadow-emerald-500/10 transition-all duration-500 border-2 border-slate-50 dark:border-slate-900 group relative overflow-hidden">
      {/* Premium Accent */}
      <div className="absolute top-0 left-0 w-2 h-full bg-emerald-500/20 group-hover:bg-emerald-500 transition-colors duration-500" />
      
      {/* Header */}
      <header className="flex items-center gap-5 mb-8">
        <div 
          className={cn(
            "w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 text-white font-black text-xl shadow-2xl transition-all duration-500 group-hover:scale-110 group-hover:rotate-3",
            post.author_role === 'teacher' 
              ? "bg-emerald-600 shadow-emerald-600/20" 
              : "bg-slate-900 dark:bg-emerald-500 shadow-slate-900/20 dark:shadow-emerald-500/20 dark:text-slate-950"
          )}
        >
          {post.author_name?.[0]?.toUpperCase() ?? <User className="w-7 h-7" />}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1">
            <p className="font-outfit font-black text-slate-900 dark:text-white truncate text-xl tracking-tight">
              {post.author_name}
            </p>
            {post.author_role === 'teacher' && (
              <span className="text-[10px] bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 px-3 py-1 rounded-full font-black uppercase tracking-[0.2em] border-2 border-emerald-200/50 dark:border-emerald-800/50">
                Teacher
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 text-slate-400">
            <Clock className="w-4 h-4" />
            <p className="text-xs font-black uppercase tracking-widest">
              {formatTimeAgo(post.created_at)}
            </p>
          </div>
        </div>

        <button className="p-3 text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-900 rounded-xl transition-all">
          <MoreVertical className="w-5 h-5" />
        </button>
      </header>

      {/* Content */}
      <div className="space-y-6">
        <div className="prose dark:prose-invert max-w-none">
          <p className="text-slate-600 dark:text-slate-300 text-lg leading-relaxed font-medium whitespace-pre-wrap">
            {displayContent}
            {!expanded && needsTruncation && '...'}
          </p>
          {needsTruncation && (
            <button 
              onClick={() => setExpanded(!expanded)}
              className="mt-4 flex items-center gap-2 text-emerald-600 font-black uppercase tracking-widest text-[10px] hover:gap-3 transition-all"
            >
              {expanded ? (
                <>Show Less <ChevronUp className="w-4 h-4" /></>
              ) : (
                <>Read More <ChevronDown className="w-4 h-4" /></>
              )}
            </button>
          )}
        </div>

        {/* Attachment */}
        {post.attachment && (
          <div className="bg-slate-50 dark:bg-slate-900 rounded-3xl p-6 border-2 border-transparent hover:border-emerald-500/20 transition-all group/file cursor-pointer">
            <div className="flex items-center gap-5">
              <div className="w-14 h-14 rounded-2xl bg-white dark:bg-slate-800 flex items-center justify-center shadow-xl group-hover/file:scale-110 transition-transform">
                {post.attachment.type === 'pdf' ? (
                  <FileText className="w-7 h-7 text-red-500" />
                ) : post.attachment.type === 'image' ? (
                  <ImageIcon className="w-7 h-7 text-blue-500" />
                ) : (
                  <FileIcon className="w-7 h-7 text-emerald-500" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-slate-900 dark:text-white font-bold truncate text-lg">{post.attachment.name}</p>
                <p className="text-slate-400 text-xs font-black uppercase tracking-widest">{formatFileSize(post.attachment.size)}</p>
              </div>
              <button className="w-12 h-12 rounded-xl bg-emerald-500 text-white flex items-center justify-center shadow-lg shadow-emerald-500/20 hover:scale-110 transition-all">
                <Download className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Footer Actions */}
        <div className="pt-8 border-t-2 border-slate-50 dark:border-slate-900 flex items-center gap-6">
          <button 
            onClick={() => setLiked(!liked)}
            className={cn(
              "flex items-center gap-2 font-black uppercase tracking-widest text-[10px] transition-all",
              liked ? "text-red-500" : "text-slate-400 hover:text-red-500"
            )}
          >
            <Heart className={cn("w-5 h-5", liked && "fill-current")} />
            {liked ? 'Liked' : 'Like'}
          </button>
          <button className="flex items-center gap-2 text-slate-400 hover:text-emerald-500 font-black uppercase tracking-widest text-[10px] transition-all">
            <MessageCircle className="w-5 h-5" />
            {post.replies?.length || 0} Comments
          </button>
          <button className="flex items-center gap-2 text-slate-400 hover:text-blue-500 font-black uppercase tracking-widest text-[10px] transition-all ml-auto">
            <Share2 className="w-5 h-5" />
            Share
          </button>
        </div>
      </div>
    </article>
  )
}
