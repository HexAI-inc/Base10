'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { adminApi } from '@/lib/api'
import AppLayout from '@/components/AppLayout'
import { 
  AlertCircle, 
  CheckCircle, 
  Loader2, 
  Flag,
  XCircle,
  Clock,
  User,
  BookOpen
} from 'lucide-react'

interface Report {
  id: number
  question_id: number
  user_id: number
  reason: string
  description?: string
  status: 'pending' | 'resolved' | 'dismissed'
  created_at: string
  resolved_at?: string
  resolved_by?: number
  question_text?: string
  subject?: string
  topic?: string
}

export default function AdminReportsPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [filter, setFilter] = useState<'all' | 'pending' | 'resolved'>('pending')

  useEffect(() => {
    const adminEmails = ['cjalloh25@gmail.com', 'esjallow03@gmail.com', 'esjallow@gmail.com']
    const isAdmin = user?.role === 'admin' || (user?.email && adminEmails.includes(user.email))
    
    if (!user || !isAdmin) {
      router.push('/dashboard')
      return
    }
    loadReports()
  }, [user, router])

  const loadReports = async () => {
    try {
      setLoading(true)
      // Note: This endpoint needs to be added to the backend
      // For now, we'll show a placeholder
      setReports([])
    } catch (error) {
      console.error('Error loading reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleResolveReport = async (reportId: number) => {
    try {
      setActionLoading(reportId)
      await adminApi.resolveReport(reportId, 'dismissed')
      await loadReports()
    } catch (error) {
      console.error('Error resolving report:', error)
      alert('Failed to resolve report')
    } finally {
      setActionLoading(null)
    }
  }

  const filteredReports = reports.filter(report => {
    if (filter === 'all') return true
    if (filter === 'pending') return report.status === 'pending'
    if (filter === 'resolved') return report.status === 'resolved'
    return true
  })

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-outfit font-bold text-slate-900 dark:text-slate-100">
            Reports Management
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Review and resolve user-reported issues
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 mb-8">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Filter:
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  filter === 'all'
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                }`}
              >
                All Reports
              </button>
              <button
                onClick={() => setFilter('pending')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  filter === 'pending'
                    ? 'bg-amber-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                }`}
              >
                Pending ({reports.filter(r => r.status === 'pending').length})
              </button>
              <button
                onClick={() => setFilter('resolved')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  filter === 'resolved'
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                }`}
              >
                Resolved ({reports.filter(r => r.status === 'resolved').length})
              </button>
            </div>
          </div>
        </div>

        {/* Reports List */}
        {filteredReports.length === 0 ? (
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-12 text-center">
            <Flag className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-outfit font-bold text-slate-900 dark:text-slate-100 mb-2">
              No Reports Found
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              {filter === 'pending' 
                ? 'There are no pending reports at the moment.'
                : filter === 'resolved'
                ? 'No resolved reports to display.'
                : 'No reports have been submitted yet.'}
            </p>
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg max-w-2xl mx-auto">
              <p className="text-sm text-blue-800 dark:text-blue-300">
                <strong>Note:</strong> The reports endpoint needs to be implemented in the backend. 
                Once available, reports will appear here for review.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredReports.map((report) => (
              <div
                key={report.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      report.status === 'pending'
                        ? 'bg-amber-100 dark:bg-amber-900/20'
                        : report.status === 'resolved'
                        ? 'bg-emerald-100 dark:bg-emerald-900/20'
                        : 'bg-slate-100 dark:bg-slate-700'
                    }`}>
                      {report.status === 'pending' ? (
                        <Clock className="w-5 h-5 text-amber-600 dark:text-amber-500" />
                      ) : report.status === 'resolved' ? (
                        <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-500" />
                      ) : (
                        <XCircle className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                      )}
                    </div>
                    <div>
                      <h3 className="text-lg font-outfit font-bold text-slate-900 dark:text-slate-100">
                        Report #{report.id}
                      </h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {new Date(report.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    report.status === 'pending'
                      ? 'bg-amber-100 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400'
                      : report.status === 'resolved'
                      ? 'bg-emerald-100 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400'
                      : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
                  }`}>
                    {report.status}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center gap-2 text-sm">
                    <User className="w-4 h-4 text-slate-400" />
                    <span className="text-slate-600 dark:text-slate-400">
                      User ID: {report.user_id}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <BookOpen className="w-4 h-4 text-slate-400" />
                    <span className="text-slate-600 dark:text-slate-400">
                      Question ID: {report.question_id}
                    </span>
                  </div>
                </div>

                {report.subject && report.topic && (
                  <div className="flex items-center gap-2 mb-4">
                    <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400 rounded text-xs font-medium">
                      {report.subject}
                    </span>
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded text-xs font-medium">
                      {report.topic}
                    </span>
                  </div>
                )}

                <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4 mb-4">
                  <p className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                    Reason: <span className="text-amber-600 dark:text-amber-500">{report.reason}</span>
                  </p>
                  {report.description && (
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      {report.description}
                    </p>
                  )}
                </div>

                {report.status === 'pending' && (
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleResolveReport(report.id)}
                      disabled={actionLoading === report.id}
                      className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {actionLoading === report.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <CheckCircle className="w-4 h-4" />
                      )}
                      Resolve Report
                    </button>
                    <button
                      onClick={() => router.push(`/admin/questions`)}
                      className="px-4 py-2 bg-slate-200 dark:bg-slate-700 text-slate-900 dark:text-slate-100 rounded-lg hover:bg-slate-300 dark:hover:bg-slate-600 transition"
                    >
                      View Question
                    </button>
                  </div>
                )}

                {report.status === 'resolved' && report.resolved_at && (
                  <div className="text-sm text-slate-600 dark:text-slate-400">
                    Resolved on {new Date(report.resolved_at).toLocaleString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  )
}
