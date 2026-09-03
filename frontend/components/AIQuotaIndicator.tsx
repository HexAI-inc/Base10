'use client'
import { useAuthStore } from '@/store/authStore'
import { Brain, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AIQuotaIndicatorProps {
  className?: string
  variant?: 'compact' | 'full'
}

export default function AIQuotaIndicator({ className, variant = 'full' }: AIQuotaIndicatorProps) {
  const { user } = useAuthStore()
  
  if (!user || user.ai_quota_limit === undefined || user.ai_quota_used === undefined) {
    return null
  }

  const limit = user.ai_quota_limit
  const used = user.ai_quota_used
  const remaining = Math.max(0, limit - used)
  const percentage = limit > 0 ? Math.min(100, (used / limit) * 100) : 0
  
  // Unlimited check
  if (limit === -1) {
    return (
      <div className={cn("flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full", className)}>
        <Zap className="w-3.5 h-3.5 text-emerald-500 fill-emerald-500" />
        <span className="text-[10px] font-black text-emerald-600 uppercase tracking-widest">Unlimited AI</span>
      </div>
    )
  }

  if (variant === 'compact') {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <div className="flex -space-x-1">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
        </div>
        <span className="text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-widest">
          {remaining} AI Credits
        </span>
      </div>
    )
  }

  return (
    <div className={cn("p-4 bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm", className)}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-lg shadow-emerald-600/20">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">AI Quota</p>
            <p className="text-xs font-bold text-slate-900 dark:text-slate-100">Big Brain Power</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm font-black text-emerald-600">{remaining}</p>
          <p className="text-[8px] font-black text-slate-400 uppercase tracking-widest">Left</p>
        </div>
      </div>

      <div className="space-y-2">
        <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
          <div 
            className={cn(
              "h-full transition-all duration-1000 ease-out rounded-full",
              percentage > 90 ? "bg-red-500" : percentage > 70 ? "bg-amber-500" : "bg-emerald-500"
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex justify-between items-center">
          <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest">
            {used} / {limit} Used
          </p>
          {percentage > 80 && (
            <p className="text-[9px] font-black text-amber-600 uppercase tracking-widest animate-pulse">
              Running Low
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
