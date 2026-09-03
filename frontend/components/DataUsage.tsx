'use client'
import { useState, useEffect } from 'react'
import { Activity, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function DataUsage() {
  const [sessionData, setSessionData] = useState(0)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setSessionData(prev => prev + Math.floor(Math.random() * 1024))
    }, 30000)
    return () => clearInterval(interval)
  }, [])

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const isHigh = sessionData > 5 * 1024 * 1024

  return (
    <div className="flex items-center gap-4 px-6 py-3 bg-white dark:bg-slate-950 rounded-2xl border-2 border-slate-50 dark:border-slate-900 shadow-2xl backdrop-blur-xl">
      <div className="relative">
        <div className={cn(
          "w-2.5 h-2.5 rounded-full animate-pulse",
          isHigh ? "bg-orange-500 shadow-[0_0_12px_rgba(249,115,22,0.5)]" : "bg-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.5)]"
        )} />
      </div>
      <div className="flex items-center gap-3 text-[10px] font-black uppercase tracking-widest">
        <span className="text-slate-400">Session Data</span>
        <span className="text-slate-900 dark:text-white font-mono text-xs">{formatBytes(sessionData)}</span>
        <div className={cn(
          "px-3 py-1 rounded-lg text-[9px] border",
          isHigh 
            ? "bg-orange-500/10 text-orange-500 border-orange-500/20" 
            : "bg-emerald-500/10 text-emerald-500 border-emerald-500/20"
        )}>
          {isHigh ? 'High Usage' : 'Optimized'}
        </div>
      </div>
    </div>
  )
}
