'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { Mail, CheckCircle2, AlertCircle, Loader2, ArrowLeft, Sparkles, Send } from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

export default function ResendVerificationPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!user) {
      router.push('/login')
    }
  }, [user, router])

  const handleResend = async () => {
    setLoading(true)
    setStatus('idle')
    setMessage('')

    try {
      const response = await api.post('/auth/resend-verification')
      setStatus('success')
      setMessage(response.data.message || 'Verification email sent successfully!')
    } catch (err: any) {
      setStatus('error')
      if (err.response?.data?.detail === 'Email already verified') {
        setMessage('Your email is already verified! Redirecting to dashboard...')
        setTimeout(() => router.push('/dashboard'), 2000)
      } else {
        setMessage(err.response?.data?.detail || 'Failed to send verification email. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-[#0F172A] flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-500/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px]" />

      <div className="max-w-md w-full relative z-10">
        <div className="text-center mb-12">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500 flex items-center justify-center shadow-2xl shadow-emerald-500/20 mx-auto mb-6">
            <Mail className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-outfit font-black text-white tracking-tight mb-3">Verify Email</h1>
          <p className="text-slate-400 font-medium">Secure your account to access all features</p>
        </div>

        <div className="bg-white dark:bg-slate-950 rounded-[3rem] border-2 border-slate-50 dark:border-slate-900 p-10 shadow-2xl">
          <div className="space-y-8">
            <div className="text-center">
              <p className="text-slate-500 font-medium mb-6">
                We need to verify your email address. If you didn't receive the link, we can send it again.
              </p>
              
              <div className="bg-slate-50 dark:bg-slate-900 rounded-2xl p-6 border-2 border-transparent group-hover:border-emerald-500/20 transition-all">
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Sending to</p>
                <p className="text-slate-900 dark:text-white font-bold text-lg">{user.email}</p>
              </div>
            </div>

            {status === 'success' && (
              <div className="bg-emerald-500/10 border-2 border-emerald-500/20 rounded-2xl p-4 flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                <p className="text-emerald-600 dark:text-emerald-400 text-xs font-bold uppercase tracking-widest">{message}</p>
              </div>
            )}

            {status === 'error' && (
              <div className="bg-red-500/10 border-2 border-red-500/20 rounded-2xl p-4 flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-500" />
                <p className="text-red-600 dark:text-red-400 text-xs font-bold uppercase tracking-widest">{message}</p>
              </div>
            )}

            <button
              onClick={handleResend}
              disabled={loading}
              className="w-full h-16 bg-emerald-600 text-white rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] flex items-center justify-center gap-3 shadow-xl shadow-emerald-600/20 hover:scale-105 transition-all disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              Resend Verification Link
            </button>

            <div className="text-center">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 text-slate-500 font-black uppercase tracking-widest text-xs hover:text-slate-900 dark:hover:text-white transition-all"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
