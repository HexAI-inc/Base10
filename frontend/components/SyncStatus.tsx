'use client'
import { useEffect, useState } from 'react'
import { Wifi, WifiOff, Loader2, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useSyncStore } from '@/store/syncStore'
import { flushPendingAttempts } from '@/lib/offline'

export default function SyncStatus() {
  const [online, setOnline] = useState(true)
  const { status, pendingCount } = useSyncStore()

  useEffect(() => {
    setOnline(navigator.onLine)
    const handleOnline = () => setOnline(true)
    const handleOffline = () => setOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Real state, driven by lib/offline.ts's queue rather than a browser
  // event alone: offline (network down) > syncing (flush in progress) >
  // error (last flush failed, pending attempts remain) > synced.
  const display: 'offline' | 'syncing' | 'error' | 'synced' =
    !online ? 'offline'
    : status === 'syncing' ? 'syncing'
    : status === 'error' && pendingCount > 0 ? 'error'
    : 'synced'

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-white dark:bg-slate-900/50 rounded-full border border-slate-100 dark:border-slate-800 shadow-sm">
      {display === 'synced' && (
        <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400" title="Online & Synced">
          <div className="w-2 h-2 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
          <Wifi className="w-3.5 h-3.5" />
          <span className="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Synced</span>
        </div>
      )}
      {display === 'offline' && (
        <div className="flex items-center gap-2 text-orange-600 dark:text-orange-400" title={pendingCount > 0 ? `Offline - ${pendingCount} pending` : 'Offline Mode'}>
          <div className="w-2 h-2 bg-orange-500 rounded-full shadow-[0_0_8px_rgba(249,115,22,0.5)]" />
          <WifiOff className="w-3.5 h-3.5" />
          <span className="text-[10px] font-black uppercase tracking-widest hidden sm:inline">
            {pendingCount > 0 ? `Offline (${pendingCount})` : 'Offline'}
          </span>
        </div>
      )}
      {display === 'syncing' && (
        <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400" title="Syncing...">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(59,130,246,0.5)]" />
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          <span className="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Syncing</span>
        </div>
      )}
      {display === 'error' && (
        <button
          onClick={() => flushPendingAttempts()}
          className="flex items-center gap-2 text-red-600 dark:text-red-400 hover:opacity-80 transition-all"
          title={`Sync failed - ${pendingCount} pending. Tap to retry`}
        >
          <div className="w-2 h-2 bg-red-500 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
          <AlertCircle className="w-3.5 h-3.5" />
          <span className="text-[10px] font-black uppercase tracking-widest hidden sm:inline">Sync Error</span>
        </button>
      )}
    </div>
  )
}
