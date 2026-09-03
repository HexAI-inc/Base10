'use client'
import { useEffect, useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/lib/api'
import { CheckCircle2, XCircle, Loader2, Mail, Sparkles, ArrowRight } from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

function VerifyEmailContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')
  const { user, setAuth, token: authToken } = useAuthStore()
  
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying')
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('No verification token provided')
      return
    }
    verifyEmail()
  }, [token])

  const verifyEmail = async () => {
    try {
      const response = await api.get(`/auth/verify-email?token=${token}`)
      setStatus('success')
      setMessage(response.data.message || 'Email verified successfully!')
      
      if (user && authToken) {
        setAuth(authToken, {
          ...user,
          is_verified: true,
          verified_at: new Date().toISOString()
        })
      }
      
      setTimeout(() => {
        router.push('/dashboard')
      }, 3000)
    } catch (err: any) {
      setStatus('error')
      setMessage(err.response?.data?.detail || 'Failed to verify email. The link may be invalid or expired.')
    }
  }

  return (
    <div className="min-h-screen bg-[#0F172A] flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-500/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px]" />

      <div className="max-w-md w-full relative z-10">
        <div className="bg-white dark:bg-slate-950 rounded-[3rem] border-2 border-slate-50 dark:border-slate-900 p-10 shadow-2xl text-center">
          {status === 'verifying' && (
            <div className="space-y-6">
              <div className="w-20 h-20 rounded-3xl bg-emerald-500/10 flex items-center justify-center mx-auto">
                <Loader2 className="w-10 h-10 text-emerald-500 animate-spin" />
              </div>
              <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-white tracking-tight">
                Verifying Email
              </h1>
              <p className="text-slate-500 font-medium">
                Please wait while we confirm your account credentials...
              </p>
            </div>
          )}

          {status === 'success' && (
            <div className="space-y-6">
              <div className="w-20 h-20 rounded-3xl bg-emerald-500 flex items-center justify-center mx-auto shadow-2xl shadow-emerald-500/20">
                <CheckCircle2 className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-white tracking-tight">
                Verified!
              </h1>
              <p className="text-slate-500 font-medium">
                {message}
              </p>
              <div className="bg-emerald-500/10 rounded-2xl p-4 border-2 border-emerald-500/20">
                <p className="text-emerald-600 dark:text-emerald-400 text-xs font-black uppercase tracking-widest">
                  Redirecting to dashboard...
                </p>
              </div>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 text-emerald-600 font-black uppercase tracking-widest text-xs hover:gap-4 transition-all"
              >
                Go to Dashboard <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}

          {status === 'error' && (
            <div className="space-y-6">
              <div className="w-20 h-20 rounded-3xl bg-red-500 flex items-center justify-center mx-auto shadow-2xl shadow-red-500/20">
                <XCircle className="w-10 h-10 text-white" />
              </div>
              <h1 className="text-3xl font-outfit font-black text-slate-900 dark:text-white tracking-tight">
                Verification Failed
              </h1>
              <p className="text-slate-500 font-medium">
                {message}
              </p>
              <div className="pt-4">
                <Link
                  href="/resend-verification"
                  className="w-full h-16 bg-slate-900 dark:bg-white dark:text-slate-900 text-white rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] flex items-center justify-center gap-3 shadow-xl hover:scale-105 transition-all"
                >
                  Resend Link
                </Link>
              </div>
              <Link
                href="/login"
                className="block text-slate-400 font-bold text-xs uppercase tracking-widest hover:text-slate-600 transition-colors"
              >
                Back to Login
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0F172A] flex items-center justify-center p-6">
        <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  )
}
