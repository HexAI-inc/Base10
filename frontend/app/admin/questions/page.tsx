'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { adminApi } from '@/lib/api'
import AppLayout from '@/components/AppLayout'
import { 
  AlertCircle, 
  Trash2, 
  Loader2, 
  BookOpen,
  TrendingDown,
  Flag,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

interface ProblematicQuestion {
  question_id: number
  subject: string
  topic: string
  difficulty: string
  accuracy_rate: number
  total_attempts: number
  report_count: number
  reasons: string[]
}

export default function AdminQuestionsPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [questions, setQuestions] = useState<ProblematicQuestion[]>([])
  const [loading, setLoading] = useState(true)
  const [deleteLoading, setDeleteLoading] = useState<number | null>(null)
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null)
  const [filters, setFilters] = useState({
    minAttempts: 50,
    maxAccuracy: 0.4,
    limit: 20
  })

  useEffect(() => {
    const adminEmails = ['cjalloh25@gmail.com', 'esjallow03@gmail.com', 'esjallow@gmail.com']
    const isAdmin = user?.role === 'admin' || (user?.email && adminEmails.includes(user.email))
    
    if (!user || !isAdmin) {
      router.push('/dashboard')
      return
    }
    loadQuestions()
  }, [user, router])

  const loadQuestions = async () => {
    setLoading(true)
    try {
      const response = await adminApi.getProblematicQuestions(
        filters.minAttempts,
        filters.maxAccuracy,
        filters.limit
      )
      setQuestions(response.data)
    } catch (err) {
      console.error('Failed to load questions:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (questionId: number) => {
    const reason = prompt('Reason for deleting this question:')
    if (!reason) return

    if (!confirm('Are you sure you want to permanently delete this question?')) return

    setDeleteLoading(questionId)
    try {
      await adminApi.deleteQuestion(questionId, reason)
      setQuestions(questions.filter(q => q.question_id !== questionId))
      alert('Question deleted successfully')
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete question')
    } finally {
      setDeleteLoading(null)
    }
  }

  const handleApplyFilters = () => {
    loadQuestions()
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30 dark:text-emerald-400'
      case 'medium': return 'text-amber-600 bg-amber-100 dark:bg-amber-900/30 dark:text-amber-400'
      case 'hard': return 'text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-400'
      default: return 'text-slate-600 bg-slate-100 dark:bg-slate-900/30 dark:text-slate-400'
    }
  }

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy < 30) return 'text-red-600 dark:text-red-400'
    if (accuracy < 40) return 'text-amber-600 dark:text-amber-400'
    return 'text-slate-600 dark:text-slate-400'
  }

  return (
    <AppLayout>
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-outfit font-bold text-slate-900 dark:text-slate-100">
            Problematic Questions
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            Review and manage questions with low accuracy or multiple reports
          </p>
        </div>
        {/* Filters */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 mb-8">
          <h2 className="text-lg font-outfit font-bold text-slate-900 dark:text-slate-100 mb-4">
            Filters
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Min Attempts
              </label>
              <input
                type="number"
                value={filters.minAttempts}
                onChange={(e) => setFilters({ ...filters, minAttempts: parseInt(e.target.value) || 0 })}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Max Accuracy (0-1)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={filters.maxAccuracy}
                onChange={(e) => setFilters({ ...filters, maxAccuracy: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Limit
              </label>
              <input
                type="number"
                value={filters.limit}
                onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) || 20 })}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-900 dark:text-slate-100"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={handleApplyFilters}
                disabled={loading}
                className="w-full px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Apply Filters'}
              </button>
            </div>
          </div>
        </div>

        {/* Questions List */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
          </div>
        ) : questions.length > 0 ? (
          <div className="space-y-4">
            {questions.map(question => (
              <div 
                key={question.question_id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm font-mono text-slate-500 dark:text-slate-400">
                          ID: {question.question_id}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getDifficultyColor(question.difficulty)}`}>
                          {question.difficulty}
                        </span>
                        {question.report_count > 0 && (
                          <span className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
                            <Flag className="w-3 h-3" />
                            {question.report_count} reports
                          </span>
                        )}
                      </div>
                      <h3 className="text-lg font-outfit font-bold text-slate-900 dark:text-slate-100">
                        {question.subject} - {question.topic}
                      </h3>
                    </div>

                    <button
                      onClick={() => handleDelete(question.question_id)}
                      disabled={deleteLoading === question.question_id}
                      className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition disabled:opacity-50"
                      title="Delete question"
                    >
                      {deleteLoading === question.question_id ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <Trash2 className="w-5 h-5" />
                      )}
                    </button>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
                    <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
                      <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Accuracy Rate</p>
                      <p className={`text-2xl font-bold ${getAccuracyColor(question.accuracy_rate)}`}>
                        {question.accuracy_rate.toFixed(1)}%
                      </p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
                      <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Total Attempts</p>
                      <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                        {question.total_attempts}
                      </p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
                      <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Reports</p>
                      <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                        {question.report_count}
                      </p>
                    </div>
                  </div>

                  {question.reasons.length > 0 && (
                    <div>
                      <button
                        onClick={() => setExpandedQuestion(
                          expandedQuestion === question.question_id ? null : question.question_id
                        )}
                        className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition mb-2"
                      >
                        {expandedQuestion === question.question_id ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                        View report reasons ({question.reasons.length})
                      </button>

                      {expandedQuestion === question.question_id && (
                        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
                          <p className="text-sm font-medium text-amber-900 dark:text-amber-100 mb-2">
                            Report Reasons:
                          </p>
                          <ul className="space-y-1">
                            {question.reasons.map((reason, index) => (
                              <li key={index} className="text-sm text-amber-800 dark:text-amber-300 flex items-center gap-2">
                                <AlertCircle className="w-3 h-3" />
                                {reason}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  {question.accuracy_rate < 30 && (
                    <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                      <div className="flex items-start gap-2">
                        <TrendingDown className="w-4 h-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                        <p className="text-sm text-red-800 dark:text-red-300">
                          <strong>Critical:</strong> Accuracy below 30%. This question may have an incorrect answer or unclear wording.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
            <p className="text-slate-600 dark:text-slate-400">
              No problematic questions found with current filters
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-500 mt-2">
              Try adjusting the minimum attempts or maximum accuracy
            </p>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
