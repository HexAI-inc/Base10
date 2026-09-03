'use client'
import { useEffect, useState } from 'react'
import { Wifi, WifiOff, Loader2, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function SyncStatus() {
  const [status, setStatus] = useState<'online' | 'offline' | 'syncing' | 'error'>('online')

  useEffect(() => {
    const handleOnline = () => setStatus('online')
    const handleOffline = () => setStatus('offline')
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    // Simulate syncing for demo purposes if needed
    // In a real app, this would be tied to your sync queue
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-white dark:bg-slate-900/50 rounded-full border border-slate-100 dark:border-slate-800 shadow-sm">
      {status === 'online' && (
        <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400" title="Online & Synced">
          <div className="w-2 h-2 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
          <Wifi className="w-3.5 h-3.5" />
          <span className="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Synced</span>
        </div>
      )}
      {status === 'offline' && (
        <div className="flex items-center gap-2 text-orange-600 dark:text-orange-400" title="Offline Mode">
          <div className="w-2 h-2 bg-orange-500 rounded-full shadow-[0_0_8px_rgba(249,115,22,0.5)]" />
          <WifiOff className="w-3.5 h-3.5" />
          <span className="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Offline</span>
        </div>
      )}
      {status === 'syncing' && (
        <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400" title="Syncing...">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          <span className="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Syncing</span>
        </div>
      )}
      {status === 'error' && (
        <button 
          onClick={() => setStatus('syncing')}
          className="flex items-center gap-2 text-red-600 dark:text-red-400 hover:opacity-80 transition-all" 
          title="Sync Failed - Tap to retry"
        >
          <div className="w-2 h-2 bg-red-500 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
          <AlertCircle className="w-3.5 h-3.5" />
          <span className="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Sync Error</span>
        </button>
      )}
    </div>
  )
}

