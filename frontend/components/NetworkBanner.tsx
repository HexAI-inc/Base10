'use client'
import { useEffect, useState } from 'react'
import { WifiOff, RefreshCw, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function NetworkBanner() {
  const [status, setStatus] = useState<'online' | 'offline' | 'syncing' | 'error'>('online')

  useEffect(() => {
    const handleOnline = () => setStatus('online')
    const handleOffline = () => setStatus('offline')
    
    if (!navigator.onLine) setStatus('offline')
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  if (status === 'online') return null
  
  return (
    <div className={cn(
      "fixed top-0 left-0 right-0 px-4 py-2 text-center text-xs font-bold z-[100] animate-in slide-in-from-top duration-300",
      status === 'offline' && "bg-orange-900 text-orange-200 border-b border-orange-800",
      status === 'syncing' && "bg-blue-900 text-blue-200 border-b border-blue-800",
      status === 'error' && "bg-red-900 text-red-200 border-b border-red-800"
    )}>
      <div className="flex items-center justify-center gap-2">
        {status === 'offline' && (
          <>
            <WifiOff className="w-3.5 h-3.5" />
            <span>📵 You're offline. Changes will sync when connected.</span>
          </>
        )}
        {status === 'syncing' && (
          <>
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>🔄 Syncing your progress...</span>
          </>
        )}
        {status === 'error' && (
          <>
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>⚠️ Sync failed. <button onClick={() => setStatus('syncing')} className="underline font-black">Tap to retry</button></span>
          </>
        )}
      </div>
    </div>
  )
}
