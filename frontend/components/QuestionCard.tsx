'use client'
import { useState, useMemo } from 'react'
import { CheckCircle, XCircle, Sparkles, Loader2, Timer } from 'lucide-react'
import { aiApi, authApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { useModalStore } from '@/store/modalStore'
import { cn } from '@/lib/utils'
import 'katex/dist/katex.min.css'
import { InlineMath } from 'react-katex'

interface QuestionCardProps {
  question: {
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
  timeRemaining?: number
  onSubmit: (selectedIndex: number) => void
}

export default function QuestionCard({ question, timeRemaining, onSubmit }: QuestionCardProps) {
  const [selected, setSelected] = useState<number | null>(null)
  const [submitted, setSubmitted] = useState(false)
  const [loadingExplanation, setLoadingExplanation] = useState(false)
  const [showExplanation, setShowExplanation] = useState(false)
  const [aiExplanation, setAiExplanation] = useState<string>('')
  const [keyConcepts, setKeyConcepts] = useState<string[]>([])
  const [aiDifficulty, setAiDifficulty] = useState<string>('')
  const { setUser } = useAuthStore()
  const { showError } = useModalStore()

  // Parse options from JSON string
  const options = useMemo(() => {
    try {
      return JSON.parse(question.options_json)
    } catch {
      return []
    }
  }, [question.options_json])

  const handleSelect = (index: number) => {
    if (submitted) return
    setSelected(index)
    setSubmitted(true)
    onSubmit(index)
  }

  const loadExplanation = async () => {
    if (showExplanation) {
      setShowExplanation(false)
      return
    }
    
    setShowExplanation(true)
    if (aiExplanation) return

    setLoadingExplanation(true)
    try {
      const response = await aiApi.explainAnswer({
        question_id: question.id,
        student_answer: selected ?? -1,
        context: `I chose "${selected !== null ? options[selected] : 'nothing'}" but the correct answer is "${options[question.correct_index]}"`
      })
      setAiExplanation(response.data.explanation)
      setKeyConcepts(response.data.key_concepts || [])
      setAiDifficulty(response.data.difficulty || '')

      // Refresh user profile to update quota
      const profileRes = await authApi.getProfile()
      setUser(profileRes.data)
    } catch (err: any) {
      if (err.response?.status === 403) {
        showError(
          'You have reached your AI quota limit for today. Please wait for it to reset or upgrade your plan for more "Big Brain" power!',
          'Quota Exceeded'
        )
        setAiExplanation('Quota exceeded. Please upgrade your plan.')
      } else {
        setAiExplanation(err.response?.data?.detail || 'Failed to get AI explanation. Please try again.')
      }
    } finally {
      setLoadingExplanation(false)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const renderContent = (text: string) => {
    // Simple LaTeX detection and rendering
    const parts = text.split(/(\$.*?\$)/g)
    return parts.map((part, i) => {
      if (part.startsWith('$') && part.endsWith('$')) {
        return <InlineMath key={i} math={part.slice(1, -1)} />
      }
      return <span key={i}>{part}</span>
    })
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl sm:rounded-3xl p-4 sm:p-8 shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-700 transition-all duration-500">
      {/* Header */}
      <div className="flex justify-between items-center mb-4 sm:mb-8">
        <div className="flex items-center gap-2 sm:gap-3">
          <span className="text-[8px] sm:text-xs font-black bg-emerald-100 dark:bg-emerald-900/50 text-emerald-600 dark:text-emerald-400 px-2 sm:px-4 py-1 sm:py-1.5 rounded-full uppercase tracking-widest">
            {question.subject}
          </span>
          <span className="text-[8px] sm:text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest truncate max-w-[100px] sm:max-w-none">
            {question.topic}
          </span>
        </div>
        {timeRemaining !== undefined && (
          <div className={cn(
            "px-2 sm:px-4 py-1 sm:py-2 rounded-xl sm:rounded-2xl font-mono text-[10px] sm:text-sm tabular-nums flex items-center gap-1.5 sm:gap-2 transition-colors",
            timeRemaining < 60 
              ? "bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400 animate-pulse" 
              : "bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-400"
          )}>
            <Timer className="w-3 h-3 sm:w-4 sm:h-4" />
            {formatTime(timeRemaining)}
          </div>
        )}
      </div>
      
      {/* Question Body */}
      <div className="mb-6 sm:mb-10">
        <div className="text-slate-900 dark:text-slate-100 text-lg sm:text-2xl font-outfit font-medium leading-relaxed">
          {renderContent(question.content)}
        </div>
      </div>
      
      {/* Options Grid */}
      <div className="space-y-3 sm:space-y-4">
        {options.map((option: string, idx: number) => {
          const isSelected = selected === idx
          const isCorrect = submitted && idx === question.correct_index
          const isWrong = submitted && isSelected && idx !== question.correct_index
          const label = String.fromCharCode(65 + idx) // A, B, C, D
          
          return (
            <button
              key={idx}
              onClick={() => handleSelect(idx)}
              disabled={submitted}
              className={cn(
                "w-full min-h-[56px] sm:min-h-[72px] px-4 sm:px-6 py-3 sm:py-5 rounded-xl sm:rounded-2xl text-left transition-all duration-300",
                "flex items-center gap-3 sm:gap-5 font-medium group relative overflow-hidden",
                // Default state
                "bg-slate-50 dark:bg-slate-900 border-2 border-slate-100 dark:border-slate-800",
                // Hover state
                !submitted && "hover:border-emerald-500 hover:bg-white dark:hover:bg-slate-800 hover:shadow-lg hover:shadow-emerald-500/10",
                // Selected state
                isSelected && !submitted && "border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20",
                // Correct answer (after submission)
                isCorrect && "border-green-500 bg-green-50 dark:bg-green-900/20",
                // Incorrect answer (after submission)
                isWrong && "border-red-500 bg-red-50 dark:bg-red-900/20",
                // Disabled state
                submitted && !isCorrect && !isWrong && "opacity-60 grayscale-[0.5]"
              )}
            >
              <span className={cn(
                "flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl flex items-center justify-center font-black text-sm sm:text-lg transition-all duration-300",
                isCorrect 
                  ? "bg-green-500 text-white shadow-lg shadow-green-500/30" 
                  : isWrong 
                    ? "bg-red-500 text-white shadow-lg shadow-red-500/30" 
                    : isSelected && !submitted
                      ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/30"
                      : "bg-white dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700 group-hover:border-emerald-500 group-hover:text-emerald-500"
              )}>
                {label}
              </span>
              <span className={cn(
                "flex-1 text-sm sm:text-lg transition-colors duration-300",
                isCorrect ? "text-green-700 dark:text-green-300 font-bold" : 
                isWrong ? "text-red-700 dark:text-red-300 font-bold" :
                "text-slate-700 dark:text-slate-200"
              )}>
                {renderContent(option)}
              </span>
              
              {isCorrect && (
                <div className="flex-shrink-0 bg-green-500 rounded-full p-0.5 sm:p-1 shadow-lg shadow-green-500/30">
                  <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
              )}
              {isWrong && (
                <div className="flex-shrink-0 bg-red-500 rounded-full p-0.5 sm:p-1 shadow-lg shadow-red-500/30">
                  <XCircle className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
              )}
            </button>
          )
        })}
      </div>
      
      {/* Footer Actions */}
      {submitted && (
        <div className="mt-6 sm:mt-10 pt-6 sm:pt-8 border-t border-slate-100 dark:border-slate-700 flex flex-col gap-4 sm:gap-6">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className={cn(
                "w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl flex items-center justify-center",
                selected === question.correct_index 
                  ? "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400" 
                  : "bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400"
              )}>
                {selected === question.correct_index ? <CheckCircle className="w-5 h-5 sm:w-6 sm:h-6" /> : <XCircle className="w-5 h-5 sm:w-6 sm:h-6" />}
              </div>
              <div>
                <p className="text-[10px] sm:text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Result</p>
                <p className={cn(
                  "text-sm sm:text-lg font-black font-outfit",
                  selected === question.correct_index ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
                )}>
                  {selected === question.correct_index ? 'Correct!' : 'Incorrect'}
                </p>
              </div>
            </div>

            <button
              onClick={loadExplanation}
              className={cn(
                "flex items-center gap-2 sm:gap-3 px-4 sm:px-6 py-2 sm:py-3 rounded-xl sm:rounded-2xl font-bold text-xs sm:text-sm transition-all duration-300",
                showExplanation 
                  ? "bg-purple-600 text-white shadow-lg shadow-purple-600/30" 
                  : "bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/40"
              )}
            >
              <Sparkles className={cn("w-4 h-4 sm:w-5 sm:h-5", loadingExplanation && "animate-spin")} />
              <span className="hidden sm:inline">{loadingExplanation ? 'Thinking...' : showExplanation ? 'Hide Explanation' : 'Explain with AI'}</span>
              <span className="sm:hidden">{loadingExplanation ? '...' : showExplanation ? 'Hide' : 'AI Help'}</span>
            </button>
          </div>

          {showExplanation && (
            <div className="bg-purple-50 dark:bg-purple-900/10 border border-purple-100 dark:border-purple-500/20 rounded-2xl sm:rounded-3xl p-4 sm:p-8 animate-in fade-in slide-in-from-top-4 duration-500">
              <div className="flex items-center gap-2 sm:gap-3 mb-3 sm:mb-4">
                <div className="w-6 h-6 sm:w-8 sm:h-8 bg-purple-600 rounded-lg sm:rounded-xl flex items-center justify-center">
                  <Sparkles className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                </div>
                <h4 className="font-outfit font-black text-purple-900 dark:text-purple-300 uppercase tracking-widest text-[10px] sm:text-sm">AI Tutor</h4>
              </div>
              
              {loadingExplanation ? (
                <div className="flex items-center gap-2 sm:gap-3 text-purple-600 dark:text-purple-400">
                  <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
                  <p className="text-xs sm:font-medium">Analyzing...</p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="prose prose-sm sm:prose-purple dark:prose-invert max-w-none">
                    <div className="text-slate-700 dark:text-slate-300 leading-relaxed text-sm sm:text-lg">
                      {renderContent(aiExplanation)}
                    </div>
                  </div>

                  {(keyConcepts.length > 0 || aiDifficulty) && (
                    <div className="flex flex-wrap items-center gap-3 pt-4 border-t border-purple-100 dark:border-purple-900/30">
                      {aiDifficulty && (
                        <div className="flex items-center gap-1.5 px-3 py-1 bg-purple-100 dark:bg-purple-900/40 rounded-full">
                          <span className="text-[8px] font-black text-purple-600 dark:text-purple-400 uppercase tracking-widest">Difficulty: {aiDifficulty}</span>
                        </div>
                      )}
                      {keyConcepts.map((concept, idx) => (
                        <div key={idx} className="flex items-center gap-1.5 px-3 py-1 bg-white dark:bg-slate-900 border border-purple-100 dark:border-purple-900/30 rounded-full">
                          <div className="w-1 h-1 rounded-full bg-purple-500" />
                          <span className="text-[8px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-widest">{concept}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

