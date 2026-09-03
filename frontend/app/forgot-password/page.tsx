'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { recoveryApi } from '@/lib/api'
import { 
  Brain, ArrowRight, Mail, Phone, Lock, 
  ShieldCheck, Sparkles, Loader2, ChevronLeft,
  CheckCircle2, AlertCircle
} from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

export default function ForgotPasswordPage() {
  const router = useRouter()
  const [step, setStep] = useState<'request' | 'verify' | 'success'>('request')
  const [identifier, setIdentifier] = useState('')
  const [otp, setOtp] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [devOtp, setDevOtp] = useState('')

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = await recoveryApi.forgotPassword(identifier)
      if (response.data.dev_otp) {
        setDevOtp(response.data.dev_otp)
      }
      setStep('verify')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to request reset. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await recoveryApi.resetPassword({
        identifier,
        otp,
        new_password: newPassword
      })
      setStep('success')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid OTP or reset failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0F172A] flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Premium Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-600/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 rounded-full blur-[120px] animate-pulse delay-700" />
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="flex flex-col items-center mb-12">
          <div className="w-20 h-20 rounded-[2.5rem] bg-emerald-600 flex items-center justify-center shadow-2xl shadow-emerald-600/20 mb-6 group hover:scale-110 transition-transform duration-500">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-outfit font-black text-white tracking-tighter mb-2">
            Base10 <span className="text-emerald-500">Recovery</span>
          </h1>
          <p className="text-slate-400 font-medium text-center">
            {step === 'request' && "Enter your details to receive a recovery code."}
            {step === 'verify' && "Enter the 4-digit code sent to your device."}
            {step === 'success' && "Your password has been successfully reset."}
          </p>
        </div>

        <div className="bg-slate-900/50 backdrop-blur-3xl p-10 rounded-[3rem] border-2 border-slate-800 shadow-2xl relative overflow-hidden group">
          {/* Error Message */}
          {error && (
            <div className="mb-8 p-4 bg-red-500/10 border-2 border-red-500/20 rounded-2xl flex items-center gap-3 animate-shake">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <p className="text-xs font-bold text-red-500 uppercase tracking-wider">{error}</p>
            </div>
          )}

          {step === 'request' && (
            <form onSubmit={handleRequestReset} className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-4">Phone or Email</label>
                <div className="relative group/input">
                  <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
                    <UserIcon className="w-5 h-5 text-slate-500 group-focus-within/input:text-emerald-500 transition-colors" />
                  </div>
                  <input
                    type="text"
                    required
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    className="w-full h-16 pl-14 pr-6 bg-slate-950 border-2 border-slate-800 rounded-2xl text-white font-medium focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 transition-all outline-none placeholder:text-slate-700"
                    placeholder="e.g. +220 1234567"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full h-16 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-2xl font-outfit font-black text-sm uppercase tracking-[0.2em] shadow-2xl shadow-emerald-600/20 transition-all duration-500 flex items-center justify-center gap-3 group"
              >
                {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : (
                  <>
                    Send Recovery Code
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>
          )}

          {step === 'verify' && (
            <form onSubmit={handleResetPassword} className="space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-4">4-Digit Code</label>
                <div className="relative group/input">
                  <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
                    <ShieldCheck className="w-5 h-5 text-slate-500 group-focus-within/input:text-emerald-500 transition-colors" />
                  </div>
                  <input
                    type="text"
                    required
                    maxLength={4}
                    value={otp}
                    onChange={(e) => setOtp(e.target.value)}
                    className="w-full h-16 pl-14 pr-6 bg-slate-950 border-2 border-slate-800 rounded-2xl text-white font-mono text-2xl tracking-[1em] text-center focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 transition-all outline-none placeholder:text-slate-700"
                    placeholder="0000"
                  />
                </div>
                {devOtp && (
                  <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest text-center mt-2">
                    Dev Mode OTP: {devOtp}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-4">New Password</label>
                <div className="relative group/input">
                  <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
                    <Lock className="w-5 h-5 text-slate-500 group-focus-within/input:text-emerald-500 transition-colors" />
                  </div>
                  <input
                    type="password"
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full h-16 pl-14 pr-6 bg-slate-950 border-2 border-slate-800 rounded-2xl text-white font-medium focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10 transition-all outline-none placeholder:text-slate-700"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full h-16 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded-2xl font-outfit font-black text-sm uppercase tracking-[0.2em] shadow-2xl shadow-emerald-600/20 transition-all duration-500 flex items-center justify-center gap-3 group"
              >
                {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : (
                  <>
                    Reset Password
                    <CheckCircle2 className="w-5 h-5 group-hover:scale-110 transition-transform" />
                  </>
                )}
              </button>

              <button 
                type="button"
                onClick={() => setStep('request')}
                className="w-full text-[10px] font-black text-slate-500 hover:text-white uppercase tracking-[0.2em] transition-colors"
              >
                Back to Request
              </button>
            </form>
          )}

          {step === 'success' && (
            <div className="text-center space-y-8 py-4">
              <div className="w-20 h-20 rounded-[2.5rem] bg-emerald-500/10 border-2 border-emerald-500/20 flex items-center justify-center mx-auto animate-bounce">
                <CheckCircle2 className="w-10 h-10 text-emerald-500" />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-outfit font-black text-white tracking-tight">Success!</h3>
                <p className="text-slate-400 font-medium">Your password has been updated. You can now log in with your new credentials.</p>
              </div>
              <Link
                href="/login"
                className="w-full h-16 bg-white text-slate-900 rounded-2xl font-outfit font-black text-sm uppercase tracking-[0.2em] hover:bg-emerald-50 transition-all duration-500 flex items-center justify-center gap-3 group"
              >
                Go to Login
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          )}
        </div>

        {/* Footer Links */}
        <div className="mt-12 flex items-center justify-center gap-8">
          <Link href="/login" className="flex items-center gap-2 text-[10px] font-black text-slate-500 hover:text-white uppercase tracking-[0.2em] transition-colors group">
            <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Back to Login
          </Link>
          <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
          <Link href="/register" className="text-[10px] font-black text-slate-500 hover:text-white uppercase tracking-[0.2em] transition-colors">
            Create Account
          </Link>
        </div>
      </div>
    </div>
  )
}

function UserIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  )
}
