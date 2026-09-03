'use client'
import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { questionApi } from '@/lib/api'
import QuestionCard from '@/components/QuestionCard'
import SyncStatus from '@/components/SyncStatus'
import AppLayout from '@/components/AppLayout'
import ScientificCalc from '@/components/ScientificCalc'
import { 
  Trophy, Target, Loader2, BookOpen, Brain, ArrowLeft, 
  ChevronRight, Sparkles, Timer, Shield, Star, LayoutGrid,
  ChevronLeft, Calculator
} from 'lucide-react'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import { Suspense } from 'react'

interface Question {
  id: number
  subject: string
  topic: string
  content: string
  options_json: string
  correct_index: number
  explanation?: string
  exam_year?: string
  difficulty: string
}

function PracticeContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { user } = useAuthStore()
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [score, setScore] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [subject, setSubject] = useState<string>(searchParams.get('subject') || 'Mathematics')
  const [difficulty, setDifficulty] = useState<string>('Medium')
  const [showSubjectSelector, setShowSubjectSelector] = useState(true)
  const [showCalculator, setShowCalculator] = useState(false)

  const subjects = ['Mathematics', 'English Language', 'Physics', 'Chemistry', 'Biology', 'Geography', 'Government', 'Civic Education', 'Financial Accounting']
  const difficulties = ['Easy', 'Medium', 'Hard']

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }
    // Only load if we have a subject and selector is closed
    if (!showSubjectSelector) {
      loadQuestions()
    }
  }, [user, router, subject, difficulty, showSubjectSelector])

  const loadQuestions = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await questionApi.getRandomQuestions(subject, 10, difficulty.toLowerCase())
      const data = typeof response.data === 'string' ? JSON.parse(response.data) : response.data
      
      if (!data || !Array.isArray(data) || data.length === 0) {
        throw new Error('No questions available')
      }
      
      setQuestions(data)
      setCurrentIndex(0)
      setScore(0)
    } catch (err: any) {
      if (err.response?.status === 422) {
        setError(`No questions available for ${subject} yet. Try Mathematics, Physics, or Biology.`)
      } else {
        const errorMessage = typeof err.response?.data?.detail === 'string' 
          ? err.response.data.detail 
          : `Failed to load questions for ${subject}. Please try another subject.`
        setError(errorMessage)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleAnswerSubmit = (selectedIndex: number) => {
    const currentQuestion = questions[currentIndex]
    const isCorrect = selectedIndex === currentQuestion.correct_index

    if (isCorrect) {
      setScore(score + 1)
    }
  }

  const nextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  const prevQuestion = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
    }
  }

  if (loading && !showSubjectSelector) {
    return (
      <AppLayout>
        <div className="min-h-[80vh] flex flex-col items-center justify-center">
          <div className="relative w-24 h-24 mb-8">
            <div className="absolute inset-0 border-4 border-emerald-500/10 rounded-[2rem] animate-pulse" />
            <div className="absolute inset-0 border-4 border-emerald-500 border-t-transparent rounded-[2rem] animate-spin" />
            <Brain className="absolute inset-0 m-auto w-10 h-10 text-emerald-500" />
          </div>
          <p className="text-slate-900 dark:text-slate-100 font-outfit font-black text-xl tracking-tight">Generating Session</p>
          <p className="text-slate-400 dark:text-slate-600 font-bold text-xs uppercase tracking-[0.3em] mt-2">Curating {subject} questions...</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 sm:py-12">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8 sm:mb-12">
          <div className="flex items-center gap-4 sm:gap-6">
            <Link 
              href="/dashboard"
              className="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-white dark:bg-slate-950 border-2 border-slate-50 dark:border-slate-900 flex items-center justify-center text-slate-400 hover:text-emerald-500 hover:border-emerald-500/50 transition-all duration-500 shadow-sm"
            >
              <ArrowLeft className="w-5 h-5 sm:w-6 sm:h-6" />
            </Link>
            <div>
              <div className="flex items-center gap-2 sm:gap-3 mb-1">
                <h1 className="text-xl sm:text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight truncate max-w-[150px] sm:max-w-none">
                  {subject}
                </h1>
                <div className="px-2 sm:px-3 py-0.5 sm:py-1 bg-emerald-500/10 border-2 border-emerald-500/20 rounded-full">
                  <span className="text-[8px] sm:text-[10px] font-black text-emerald-700 dark:text-emerald-400 uppercase tracking-widest">Active</span>
                </div>
              </div>
              <p className="text-[10px] sm:text-sm font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest">
                Q{currentIndex + 1} of {questions.length}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 sm:gap-4">
            <div className="flex-1 sm:flex-none bg-white dark:bg-slate-950 px-4 sm:px-6 py-2 sm:py-3 rounded-2xl border-2 border-slate-50 dark:border-slate-900 shadow-sm flex items-center gap-3 sm:gap-4">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
                <Trophy className="w-4 h-4 sm:w-5 sm:h-5 text-amber-500" />
              </div>
              <div>
                <p className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">Score</p>
                <p className="text-lg sm:text-xl font-outfit font-black text-slate-900 dark:text-slate-100 leading-none">{score}</p>
              </div>
            </div>
            
            <button 
              onClick={() => setShowCalculator(true)}
              className="w-12 h-12 sm:w-14 sm:h-14 bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 rounded-2xl flex items-center justify-center hover:bg-emerald-500 hover:text-white transition-all"
            >
              <Calculator className="w-5 h-5 sm:w-6 sm:h-6" />
            </button>

            <button 
              onClick={() => setShowSubjectSelector(true)}
              className="h-12 sm:h-14 px-4 sm:px-6 bg-slate-900 dark:bg-emerald-600 text-white rounded-2xl font-outfit font-black text-[10px] sm:text-xs uppercase tracking-[0.2em] shadow-xl shadow-emerald-600/20 transition-all hover:scale-105 flex items-center gap-2 sm:gap-3"
            >
              <LayoutGrid className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="hidden sm:inline">Switch</span>
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-8 sm:mb-12">
          <div className="h-3 sm:h-4 w-full bg-slate-100 dark:bg-slate-900 rounded-full overflow-hidden p-0.5 sm:p-1 border-2 border-slate-50 dark:border-slate-800">
            <div 
              className="h-full bg-emerald-500 rounded-full transition-all duration-1000 ease-out shadow-[0_0_12px_rgba(16,185,129,0.4)]"
              style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Error State */}
        {error ? (
          <div className="bg-red-50 dark:bg-red-900/10 border-2 border-red-100 dark:border-red-900/20 p-8 sm:p-12 rounded-[2rem] sm:rounded-[2.5rem] text-center">
            <div className="w-16 h-16 sm:w-20 h-20 bg-red-100 dark:bg-red-900/20 rounded-2xl sm:rounded-3xl flex items-center justify-center mx-auto mb-6">
              <Target className="w-8 h-8 sm:w-10 sm:h-10 text-red-500" />
            </div>
            <h2 className="text-xl sm:text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-4">Content Unavailable</h2>
            <p className="text-sm sm:text-slate-500 dark:text-slate-400 mb-8 max-w-md mx-auto font-medium">{error}</p>
            <button 
              onClick={() => setShowSubjectSelector(true)}
              className="h-12 sm:h-14 px-6 sm:px-8 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl font-outfit font-black text-[10px] sm:text-xs uppercase tracking-[0.2em] transition-all hover:scale-105"
            >
              Try Another Subject
            </button>
          </div>
        ) : (
          <div className="space-y-6 sm:space-y-8">
            {questions[currentIndex] && (
              <QuestionCard 
                question={questions[currentIndex]} 
                onSubmit={handleAnswerSubmit}
              />
            )}
            
            {/* Navigation Controls */}
            <div className="flex items-center justify-between gap-4">
              <button
                onClick={prevQuestion}
                disabled={currentIndex === 0}
                className="flex-1 h-14 sm:h-16 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-900 rounded-2xl font-outfit font-black text-[10px] sm:text-xs uppercase tracking-[0.2em] text-slate-600 dark:text-slate-400 disabled:opacity-30 flex items-center justify-center gap-2 hover:border-emerald-500/50 transition-all"
              >
                <ChevronLeft className="w-4 h-4 sm:w-5 sm:h-5" />
                Previous
              </button>
              <button
                onClick={nextQuestion}
                disabled={currentIndex === questions.length - 1}
                className="flex-1 h-14 sm:h-16 bg-emerald-600 text-white rounded-2xl font-outfit font-black text-[10px] sm:text-xs uppercase tracking-[0.2em] shadow-xl shadow-emerald-600/20 disabled:opacity-30 flex items-center justify-center gap-2 hover:bg-emerald-500 transition-all"
              >
                Next
                <ChevronRight className="w-4 h-4 sm:w-5 sm:h-5" />
              </button>
            </div>

            <div className="flex items-center justify-between px-2 sm:px-4">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center">
                  <Shield className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <p className="text-[8px] sm:text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-[0.2em]">Verified Content</p>
              </div>
              
              <div className="flex items-center gap-1.5 sm:gap-2">
                <Star className="w-3 h-3 sm:w-4 sm:h-4 text-amber-500 fill-amber-500" />
                <span className="text-[8px] sm:text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-widest">Premium</span>
              </div>
            </div>
          </div>
        )}

        {/* Subject & Difficulty Selector Modal */}
        {showSubjectSelector && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
            <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-xl" />
            <div className="relative bg-white dark:bg-slate-950 w-full max-w-2xl rounded-[2.5rem] sm:rounded-[3rem] border-2 border-slate-100 dark:border-slate-900 p-8 sm:p-12 shadow-2xl overflow-y-auto max-h-[90vh] scrollbar-hide">
              <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full -mr-32 -mt-32 blur-3xl" />
              
              <div className="relative z-10">
                <h2 className="text-2xl sm:text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-8 tracking-tight">Practice Settings</h2>
                
                <div className="space-y-8">
                  {/* Difficulty Selector */}
                  <div className="space-y-4">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] ml-2">Select Difficulty</p>
                    <div className="grid grid-cols-3 gap-3">
                      {difficulties.map((d) => (
                        <button
                          key={d}
                          onClick={() => setDifficulty(d)}
                          className={cn(
                            "h-12 rounded-xl font-outfit font-black text-[10px] uppercase tracking-widest transition-all",
                            difficulty === d 
                              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/20" 
                              : "bg-slate-50 dark:bg-slate-900 text-slate-500 border-2 border-transparent hover:border-emerald-500/30"
                          )}
                        >
                          {d}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Subject Selector */}
                  <div className="space-y-4">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] ml-2">Select Subject</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {subjects.map((s) => (
                        <button
                          key={s}
                          onClick={() => setSubject(s)}
                          className={cn(
                            "h-14 px-6 rounded-xl font-outfit font-black text-[10px] uppercase tracking-widest transition-all flex items-center justify-between group",
                            subject === s 
                              ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/20" 
                              : "bg-slate-50 dark:bg-slate-900 text-slate-500 border-2 border-transparent hover:border-emerald-500/30"
                          )}
                        >
                          {s}
                          <ChevronRight className={cn(
                            "w-4 h-4 transition-transform group-hover:translate-x-1",
                            subject === s ? "text-white" : "text-slate-400"
                          )} />
                        </button>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={() => setShowSubjectSelector(false)}
                    className="w-full h-16 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] shadow-2xl transition-all hover:scale-[1.02] active:scale-[0.98] mt-4"
                  >
                    Start Practice Session
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Calculator Modal */}
        {showCalculator && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-slate-950/40 backdrop-blur-sm" onClick={() => setShowCalculator(false)} />
            <div className="relative w-full max-w-md">
              <ScientificCalc isStatic onClose={() => setShowCalculator(false)} />
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}

export default function PracticePage() {
  return (
    <Suspense fallback={
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-full p-8 gap-4">
          <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
          <p className="text-slate-500 font-bold uppercase tracking-widest text-xs animate-pulse">Loading Practice...</p>
        </div>
      </AppLayout>
    }>
      <PracticeContent />
    </Suspense>
  )
}
