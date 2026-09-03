'use client'
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { Mail, X, Loader2, CheckCircle } from 'lucide-react'
import { api } from '@/lib/api'
import Link from 'next/link'

export default function EmailVerificationBanner() {
  const { user } = useAuthStore()
  const [dismissed, setDismissed] = useState(false)
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)

  const handleResend = async () => {
    setSending(true)
    try {
      await api.post('/auth/resend-verification')
      setSent(true)
      setTimeout(() => setSent(false), 5000)
    } catch (err) {
      console.error('Failed to resend verification:', err)
    } finally {
      setSending(false)
    }
  }

  // Don't show if user is verified, has no email, or banner was dismissed
  if (!user || user.is_verified || !user.email || dismissed) {
    return null
  }

  return (
    <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 flex-1">
            <Mail className="w-5 h-5 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-medium">
                Please verify your email address
              </p>
              <p className="text-sm text-amber-50">
                Check your inbox for the verification link we sent to <strong>{user.email}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {sent ? (
              <div className="flex items-center gap-2 bg-white/20 px-4 py-2 rounded-lg">
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Email sent!</span>
              </div>
            ) : (
              <button
                onClick={handleResend}
                disabled={sending}
                className="bg-white text-amber-600 px-4 py-2 rounded-lg text-sm font-outfit font-bold hover:bg-amber-50 transition disabled:opacity-50 flex items-center gap-2"
              >
                {sending ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  'Resend Email'
                )}
              </button>
            )}

            <button
              onClick={() => setDismissed(true)}
              className="text-white hover:text-amber-100 transition p-1"
              aria-label="Dismiss"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
