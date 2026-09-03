'use client'
import { useState, useEffect } from 'react'
import { assetApi } from '@/lib/api'
import { ImageIcon, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SmartImageProps {
  filename: string
  alt: string
  className?: string
  quality?: 'low' | 'medium' | 'high' | 'auto'
}

export function SmartImage({ filename, alt, className, quality = 'auto' }: SmartImageProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [networkType, setNetworkType] = useState<string>('wifi')

  useEffect(() => {
    // Detect network type if available (Chrome/Edge/Android)
    const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection
    if (connection) {
      setNetworkType(connection.effectiveType || 'wifi')
      
      const updateConnection = () => {
        setNetworkType(connection.effectiveType || 'wifi')
      }
      connection.addEventListener('change', updateConnection)
      return () => connection.removeEventListener('change', updateConnection)
    }
  }, [])

  const imageUrl = assetApi.getImageUrl(filename, { 
    quality: quality === 'auto' ? undefined : quality,
    network: networkType 
  })

  return (
    <div className={cn("relative overflow-hidden bg-slate-100 dark:bg-slate-800 rounded-2xl", className)}>
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-100 dark:bg-slate-800 z-10">
          <Loader2 className="w-6 h-6 text-emerald-500 animate-spin" />
        </div>
      )}
      
      {error ? (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-400">
          <ImageIcon className="w-8 h-8 mb-2 opacity-20" />
          <span className="text-[10px] font-black uppercase tracking-widest">Failed to load</span>
        </div>
      ) : (
        <img
          src={imageUrl}
          alt={alt}
          className={cn(
            "w-full h-full object-cover transition-opacity duration-500",
            loading ? "opacity-0" : "opacity-100"
          )}
          onLoad={() => setLoading(false)}
          onError={() => {
            setLoading(false)
            setError(true)
          }}
        />
      )}
    </div>
  )
}
