"use client"
import { useEffect } from 'react'
import { X, CheckCircle2, AlertCircle, Info, HelpCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  message: string
  type?: 'success' | 'error' | 'info' | 'confirm'
  onConfirm?: () => void
  confirmText?: string
  cancelText?: string
}

export default function Modal({ isOpen, onClose, title, message, type = 'info', onConfirm, confirmText = 'OK', cancelText = 'Cancel' }: ModalProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  const icons = {
    success: { icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    error: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-500/10' },
    info: { icon: Info, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    confirm: { icon: HelpCircle, color: 'text-amber-500', bg: 'bg-amber-500/10' }
  }

  const { icon: Icon, color, bg } = icons[type]

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm animate-in fade-in duration-300" onClick={onClose} />
      
      {/* Modal Content */}
      <div className="relative bg-white dark:bg-slate-950 rounded-[2.5rem] max-w-md w-full shadow-2xl border-2 border-slate-50 dark:border-slate-900 overflow-hidden animate-in zoom-in-95 duration-300" onClick={(e) => e.stopPropagation()}>
        <div className="p-10">
          {/* Icon & Title */}
          <div className="flex flex-col items-center text-center mb-8">
            <div className={cn("w-20 h-20 rounded-[2rem] flex items-center justify-center mb-6", bg)}>
              <Icon className={cn("w-10 h-10", color)} />
            </div>
            <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">
              {title || (type === 'success' ? 'Success' : type === 'error' ? 'Error' : type === 'confirm' ? 'Confirm' : 'Info')}
            </h3>
          </div>

          {/* Message */}
          <p className="text-slate-500 dark:text-slate-400 text-center font-medium leading-relaxed mb-10">
            {message}
          </p>

          {/* Actions */}
          <div className="flex flex-col gap-3">
            {type === 'confirm' && onConfirm ? (
              <>
                <button
                  onClick={() => {
                    onConfirm()
                    onClose()
                  }}
                  className="w-full h-14 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] hover:scale-105 transition-all shadow-xl"
                >
                  {confirmText}
                </button>
                <button
                  onClick={onClose}
                  className="w-full h-14 bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] hover:bg-slate-200 dark:hover:bg-slate-800 transition-all"
                >
                  {cancelText}
                </button>
              </>
            ) : (
              <button
                onClick={onClose}
                className={cn(
                  "w-full h-14 text-white rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] hover:scale-105 transition-all shadow-xl",
                  type === 'success' ? 'bg-emerald-600 shadow-emerald-600/20' :
                  type === 'error' ? 'bg-red-600 shadow-red-600/20' :
                  'bg-blue-600 shadow-blue-600/20'
                )}
              >
                {confirmText}
              </button>
            )}
          </div>
        </div>
        
        {/* Close Button */}
        <button 
          onClick={onClose}
          className="absolute top-6 right-6 w-10 h-10 rounded-xl bg-slate-50 dark:bg-slate-900 flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}
