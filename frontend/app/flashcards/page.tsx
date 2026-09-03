'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { questionApi } from '@/lib/api'
import Flashcard from '@/components/Flashcard'
import AppLayout from '@/components/AppLayout'
import { 
  BookOpen, Loader2, RefreshCw, Brain, Sparkles, 
  ChevronLeft, ChevronRight, Zap, Star, Shield
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface Question {
  id: number
  question_text: string
  correct_answer: string
  subject?: string
}

export default function FlashcardsPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }
    loadFlashcards()
  }, [user, router])

  const loadFlashcards = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await questionApi.getRandomQuestions(undefined, 20)
      setQuestions(response.data)
      setCurrentIndex(0)
    } catch (err: any) {
      const errorMessage = typeof err.response?.data?.detail === 'string' 
        ? err.response.data.detail 
        : 'Failed to load flashcards'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1)
    }
  }

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1)
    }
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="min-h-[80vh] flex flex-col items-center justify-center">
          <div className="relative w-24 h-24 mb-8">
            <div className="absolute inset-0 border-4 border-emerald-500/10 rounded-[2rem] animate-pulse" />
            <div className="absolute inset-0 border-4 border-emerald-500 border-t-transparent rounded-[2rem] animate-spin" />
            <Brain className="absolute inset-0 m-auto w-10 h-10 text-emerald-500" />
          </div>
          <p className="text-slate-900 dark:text-slate-100 font-outfit font-black text-xl tracking-tight">Preparing Deck</p>
          <p className="text-slate-400 dark:text-slate-600 font-bold text-xs uppercase tracking-[0.3em] mt-2">Shuffling cards...</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-12">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 sm:gap-8 mb-8 sm:mb-12">
          <div className="flex items-center gap-4 sm:gap-6">
            <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-xl sm:rounded-2xl bg-emerald-600 flex items-center justify-center shadow-2xl shadow-emerald-600/20">
              <Zap className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2 sm:gap-3 mb-0.5 sm:mb-1">
                <h1 className="text-2xl sm:text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Flashcards</h1>
                <div className="px-2 sm:px-3 py-0.5 sm:py-1 bg-emerald-500/10 border-2 border-emerald-500/20 rounded-full">
                  <span className="text-[8px] sm:text-[10px] font-black text-emerald-700 dark:text-emerald-400 uppercase tracking-widest">Active</span>
                </div>
              </div>
              <p className="text-[10px] sm:text-sm font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest">
                Card {currentIndex + 1} of {questions.length}
              </p>
            </div>
          </div>

          <button 
            onClick={loadFlashcards}
            className="h-12 sm:h-14 px-4 sm:px-6 bg-white dark:bg-slate-950 border-2 border-slate-50 dark:border-slate-900 rounded-xl sm:rounded-2xl font-outfit font-black text-[10px] sm:text-xs uppercase tracking-[0.2em] shadow-sm hover:border-emerald-500/50 transition-all flex items-center justify-center gap-2 sm:gap-3 group"
          >
            <RefreshCw className="w-4 h-4 sm:w-5 sm:h-5 group-hover:rotate-180 transition-transform duration-500" />
            New Deck
          </button>
        </header>

        {/* Progress Bar */}
        <div className="mb-8 sm:mb-12">
          <div className="h-3 sm:h-4 w-full bg-slate-100 dark:bg-slate-900 rounded-full overflow-hidden p-0.5 sm:p-1 border-2 border-slate-50 dark:border-slate-800">
            <div 
              className="h-full bg-emerald-500 rounded-full transition-all duration-1000 ease-out shadow-[0_0_12px_rgba(16,185,129,0.4)]"
              style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Card Area */}
        <div className="relative mb-8 sm:mb-12">
          {questions[currentIndex] && (
            <Flashcard 
              front={questions[currentIndex].question_text}
              back={questions[currentIndex].correct_answer}
              context={questions[currentIndex].subject}
              onNext={handleNext}
              onPrevious={handlePrevious}
              currentIndex={currentIndex}
              total={questions.length}
            />
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center justify-center gap-4 sm:gap-6">
          <button
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            className="w-16 h-16 sm:w-20 sm:h-20 rounded-[1.5rem] sm:rounded-[2rem] bg-white dark:bg-slate-950 border-2 border-slate-50 dark:border-slate-900 flex items-center justify-center text-slate-400 hover:text-emerald-500 hover:border-emerald-500/50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            <ChevronLeft className="w-8 h-8 sm:w-10 sm:h-10" />
          </button>
          
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-xl sm:rounded-2xl bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center mb-1 sm:mb-2">
              <Star className="w-6 h-6 sm:w-8 sm:h-8 text-emerald-600 dark:text-emerald-400" />
            </div>
            <span className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">Mastery</span>
          </div>

          <button
            onClick={handleNext}
            disabled={currentIndex === questions.length - 1}
            className="w-16 h-16 sm:w-20 sm:h-20 rounded-[1.5rem] sm:rounded-[2rem] bg-slate-900 dark:bg-emerald-600 text-white flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-2xl shadow-emerald-600/20"
          >
            <ChevronRight className="w-8 h-8 sm:w-10 sm:h-10" />
          </button>
        </div>

        {/* Footer Info */}
        <div className="mt-12 sm:mt-16 flex items-center justify-center gap-6 sm:gap-8">
          <div className="flex items-center gap-2 sm:gap-3">
            <Shield className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-500" />
            <span className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">Verified</span>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-amber-500" />
            <span className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">AI Powered</span>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
