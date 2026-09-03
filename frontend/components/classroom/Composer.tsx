"use client"
import { useState, useRef, useEffect } from 'react'
import { useModalStore } from '@/store/modalStore'
import { Send, Bell, Image, Paperclip, Sparkles, X, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function Composer({ onPost, studentCount }: { onPost: (content: string) => Promise<void>, studentCount?: number }) {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { showError, showSuccess } = useModalStore()

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [content])

  const submit = async (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!content.trim()) return
    
    try {
      setLoading(true)
      await onPost(content.trim())
      setContent('')
      setIsExpanded(false)
      
      if (studentCount && studentCount > 0) {
        showSuccess(
          `Announcement posted and ${studentCount} student${studentCount !== 1 ? 's' : ''} will be notified.`,
          '📢 Notification Sent'
        )
      }
    } catch (err) {
      showError('Unable to post announcement. Please try again.', 'Post Failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative group">
      <div className={cn(
        "absolute -inset-1 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-[2.5rem] blur opacity-0 transition duration-500",
        isExpanded && "opacity-20"
      )} />
      
      <form 
        onSubmit={submit} 
        className={cn(
          "relative bg-white dark:bg-slate-950 rounded-[2.5rem] border-2 transition-all duration-500 ease-out overflow-hidden",
          isExpanded 
            ? "border-emerald-500/50 shadow-2xl shadow-emerald-500/10 p-8" 
            : "border-slate-100 dark:border-slate-900 p-4 hover:border-emerald-500/30"
        )}
      >
        <div className="flex items-start gap-6">
          <div className={cn(
            "w-14 h-14 rounded-2xl flex items-center justify-center transition-all duration-500",
            isExpanded 
              ? "bg-emerald-500 text-white shadow-2xl shadow-emerald-500/20" 
              : "bg-slate-50 dark:bg-slate-900 text-slate-400"
          )}>
            <Sparkles className={cn("w-7 h-7 transition-transform duration-500", isExpanded && "rotate-12")} />
          </div>
          
          <div className="flex-1 min-w-0">
            <textarea
              ref={textareaRef}
              value={content}
              onFocus={() => setIsExpanded(true)}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Share an update with your class..."
              className={cn(
                "w-full bg-transparent border-none focus:ring-0 text-slate-900 dark:text-white placeholder:text-slate-400 resize-none font-outfit font-medium transition-all duration-300",
                isExpanded ? "text-xl min-h-[120px] py-2" : "text-lg min-h-[56px] py-3"
              )}
            />
          </div>

          {isExpanded && (
            <button 
              type="button"
              onClick={() => {
                setIsExpanded(false)
                if (!content.trim()) setContent('')
              }}
              className="p-3 hover:bg-slate-100 dark:hover:bg-slate-900 rounded-full text-slate-400 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          )}
        </div>

        {isExpanded && (
          <div className="mt-8 pt-6 border-t-2 border-slate-50 dark:border-slate-900 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button type="button" className="p-3 text-slate-400 hover:text-emerald-500 hover:bg-emerald-500/10 rounded-xl transition-all">
                <Paperclip className="w-5 h-5" />
              </button>
              <button type="button" className="p-3 text-slate-400 hover:text-emerald-500 hover:bg-emerald-500/10 rounded-xl transition-all">
                <Image className="w-5 h-5" />
              </button>
              <button type="button" className="p-3 text-slate-400 hover:text-emerald-500 hover:bg-emerald-500/10 rounded-xl transition-all">
                <Bell className="w-5 h-5" />
              </button>
            </div>

            <button
              type="submit"
              disabled={loading || !content.trim()}
              className="h-14 px-10 bg-emerald-600 text-white rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] flex items-center gap-3 shadow-xl shadow-emerald-600/20 hover:scale-105 transition-all disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              Post Announcement
            </button>
          </div>
        )}
      </form>
    </div>
  )
}
