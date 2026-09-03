'use client'
import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/AppLayout'
import { aiApi, authApi } from '@/lib/api'
import { Loader2, ArrowLeft, Sparkles, Brain, BookOpen, Send, MessageSquare, ListChecks, X, ChevronRight } from 'lucide-react'
import { useModalStore } from '@/store/modalStore'
import { useAuthStore } from '@/store/authStore'
import { cn } from '@/lib/utils'
import AIQuotaIndicator from '@/components/AIQuotaIndicator'
import 'katex/dist/katex.min.css'
import { InlineMath, BlockMath } from 'react-katex'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  suggestions?: string[]
  related_topics?: string[]
}

export default function AITutorPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [socraticMode, setSocraticMode] = useState(false)
  const [subject, setSubject] = useState('MATHEMATICS')
  const [topic, setTopic] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const [showQuizModal, setShowQuizModal] = useState(false)
  const [quizTopic, setQuizTopic] = useState('')
  const [quizDifficulty, setQuizDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium')
  const [numQuestions, setNumQuestions] = useState(5)
  const [generatingQuiz, setGeneratingQuiz] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { showError, showSuccess } = useModalStore()
  const { setUser } = useAuthStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const renderContent = (content: string) => {
    const parts = content.split(/(\$\$[\s\S]*?\$\$|\$.*?\$)/g)
    return parts.map((part, index) => {
      if (part.startsWith('$$') && part.endsWith('$$')) {
        return <BlockMath key={index}>{part.slice(2, -2)}</BlockMath>
      } else if (part.startsWith('$') && part.endsWith('$')) {
        return <InlineMath key={index}>{part.slice(1, -1)}</InlineMath>
      }
      return <span key={index} className="whitespace-pre-wrap">{part}</span>
    })
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const res = await aiApi.chat({
        message: input.trim(),
        history: messages.slice(-10).map(m => ({ role: m.role, content: m.content })),
        subject,
        topic: topic || undefined,
        socratic_mode: socraticMode
      })

      const aiMessage: Message = {
        role: 'assistant',
        content: res.data.response || res.data.answer,
        timestamp: new Date(),
        suggestions: res.data.suggestions,
        related_topics: res.data.related_topics
      }

      setMessages(prev => [...prev, aiMessage])

      // Refresh user profile to update quota
      const profileRes = await authApi.getProfile()
      setUser(profileRes.data)

      // Check for quiz mode trigger
      if (aiMessage.content.includes('[QUIZ_MODE:')) {
        const match = aiMessage.content.match(/\[QUIZ_MODE:\s*([^\|]+)\s*\|\s*([^\]]+)\]/)
        if (match) {
          setQuizTopic(match[2].trim())
          setTimeout(() => setShowQuizModal(true), 1000)
        }
      }
    } catch (error: any) {
      if (error.response?.status === 403) {
        showError(
          'You have reached your AI quota limit for today. Please wait for it to reset or upgrade your plan for more "Big Brain" power!',
          'Quota Exceeded'
        )
      } else {
        showError(
          error.response?.data?.detail || 'Failed to get response',
          'AI Error'
        )
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateQuiz = async () => {
    try {
      setGeneratingQuiz(true)
      const res = await aiApi.generateQuiz({
        subject,
        topic: quizTopic || undefined,
        difficulty: quizDifficulty,
        num_questions: numQuestions
      })

      const quizContent = `📝 **Generated Quiz: ${quizTopic || subject}**\n\n${formatQuiz(res.data.questions)}`
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: quizContent,
        timestamp: new Date()
      }])
      setShowQuizModal(false)
      showSuccess(`Generated ${numQuestions} questions!`, 'Quiz Created')

      // Refresh user profile to update quota
      const profileRes = await authApi.getProfile()
      setUser(profileRes.data)
    } catch (error: any) {
      if (error.response?.status === 403) {
        showError(
          'You have reached your AI quota limit for today. Please wait for it to reset or upgrade your plan for more "Big Brain" power!',
          'Quota Exceeded'
        )
      } else {
        showError(error.response?.data?.detail || 'Failed to generate quiz', 'Quiz Error')
      }
    } finally {
      setGeneratingQuiz(false)
    }
  }

  const formatQuiz = (questions: any[]) => {
    return questions.map((q, idx) => {
      const opts = Object.entries(q.options || {})
        .map(([key, val]) => `${key}) ${val}`)
        .join('\n')
      return `**Question ${idx + 1}:** ${q.question}\n\n${opts}\n\n*Answer: ${q.correct_answer}*\n*Explanation: ${q.explanation}*`
    }).join('\n\n---\n\n')
  }

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto h-[calc(100vh-6rem)] sm:h-[calc(100vh-8rem)] flex flex-col bg-white dark:bg-slate-950 rounded-2xl sm:rounded-3xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-2xl">
        {/* Header */}
        <div className="p-4 sm:p-6 border-b border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center justify-between">
          <div className="flex items-center gap-3 sm:gap-4">
            <button onClick={() => router.back()} className="p-1.5 sm:p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 transition-colors">
              <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-emerald-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg sm:text-xl font-outfit font-black text-slate-900 dark:text-slate-100">AI Tutor Pro</h1>
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-[8px] sm:text-[10px] font-black text-slate-500 uppercase tracking-widest">Pedagogical Mode</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2 sm:gap-4">
            <div className="hidden md:block">
              <AIQuotaIndicator variant="compact" />
            </div>
            <button
              onClick={() => setSocraticMode(!socraticMode)}
              className={cn(
                "flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl text-[10px] sm:text-xs font-bold transition-all duration-300",
                socraticMode 
                  ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/20" 
                  : "bg-slate-100 dark:bg-slate-800 text-slate-500"
              )}
            >
              <Brain className={cn("w-3.5 h-3.5 sm:w-4 sm:h-4", socraticMode && "animate-pulse")} />
              <span className="hidden xs:inline">{socraticMode ? 'Socratic ON' : 'Socratic Mode'}</span>
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 sm:space-y-8 scrollbar-hide">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center px-4">
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl sm:rounded-3xl bg-slate-50 dark:bg-slate-900 flex items-center justify-center mb-4 sm:mb-6">
                <MessageSquare className="w-8 h-8 sm:w-10 sm:h-10 text-slate-300" />
              </div>
              <h2 className="text-xl sm:text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-2 sm:mb-3">How can I help you today?</h2>
              <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 max-w-sm mb-8 sm:mb-10">
                I'm your AI tutor, optimized for WAEC preparation. Ask me to explain concepts, solve problems, or generate quizzes.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 w-full max-w-lg">
                {[
                  "Explain the laws of thermodynamics",
                  "Help me with quadratic equations",
                  "What are the themes in 'The Lion and the Jewel'?",
                  "Generate a biology practice quiz"
                ].map((tip, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(tip)}
                    className="text-left p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs sm:text-sm text-slate-600 dark:text-slate-400 hover:border-emerald-500 dark:hover:border-emerald-500 transition-all group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="flex-1 truncate">💡 {tip}</span>
                      <ChevronRight className="w-3 h-3 sm:w-4 sm:h-4 opacity-0 group-hover:opacity-100 transition-opacity text-emerald-500" />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, i) => (
            <div
              key={i}
              className={cn(
                "flex w-full animate-in fade-in slide-in-from-bottom-4 duration-500",
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={cn(
                  "max-w-[90%] sm:max-w-[85%] rounded-2xl sm:rounded-3xl px-4 sm:px-6 py-3 sm:py-4 shadow-sm",
                  message.role === 'user'
                    ? 'bg-emerald-600 text-white rounded-tr-none'
                    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100 rounded-tl-none'
                )}
              >
                <div className="text-xs sm:text-sm leading-relaxed prose dark:prose-invert max-w-none">
                  {renderContent(message.content)}
                </div>
                <div className={cn(
                  "text-[8px] sm:text-[10px] mt-2 sm:mt-3 font-bold opacity-50 uppercase tracking-widest",
                  message.role === 'user' ? 'text-white' : 'text-slate-500'
                )}>
                  {message.timestamp?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>

                {message.role === 'assistant' && (message.suggestions || message.related_topics) && (
                  <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 space-y-3">
                    {message.suggestions && message.suggestions.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {message.suggestions.map((suggestion, idx) => (
                          <button
                            key={idx}
                            onClick={() => setInput(suggestion)}
                            className="px-3 py-1.5 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 text-[10px] font-black uppercase tracking-widest rounded-lg border border-emerald-100 dark:border-emerald-900/30 hover:bg-emerald-100 transition-colors"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    )}
                    {message.related_topics && message.related_topics.length > 0 && (
                      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide">
                        <span className="text-[8px] font-black text-slate-400 uppercase tracking-widest whitespace-nowrap">Related:</span>
                        {message.related_topics.map((topic, idx) => (
                          <span key={idx} className="px-2 py-0.5 bg-slate-50 dark:bg-slate-800 text-slate-500 text-[8px] font-bold rounded-md whitespace-nowrap">
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start animate-in fade-in duration-300">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl sm:rounded-3xl rounded-tl-none px-4 sm:px-6 py-3 sm:py-4">
                <div className="flex gap-1 sm:gap-1.5">
                  <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 sm:p-6 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800">
          <form 
            onSubmit={handleSendMessage}
            className={cn(
              "relative flex items-center transition-all duration-500 ease-out",
              isFocused ? "scale-[1.01]" : "scale-100"
            )}
          >
            <div className="relative flex-1 group">
              <div className={cn(
                "absolute inset-y-0 left-4 sm:left-5 flex items-center transition-colors duration-300",
                isFocused ? "text-emerald-500" : "text-slate-400"
              )}>
                {isFocused ? <Sparkles className="w-5 h-5 sm:w-6 sm:h-6" /> : <MessageSquare className="w-5 h-5 sm:w-6 sm:h-6" />}
              </div>
              <input
                type="text"
                value={input}
                onFocus={() => setIsFocused(true)}
                onBlur={() => setIsFocused(false)}
                onChange={(e) => setInput(e.target.value)}
                placeholder={socraticMode ? "Ask for a hint..." : "Ask anything..."}
                disabled={isLoading}
                className={cn(
                  "w-full pl-12 sm:pl-14 pr-14 sm:pr-16 py-3.5 sm:py-5 bg-slate-50 dark:bg-slate-800 border-2 rounded-xl sm:rounded-2xl font-outfit text-sm sm:text-lg transition-all duration-300",
                  "text-slate-900 dark:text-slate-100 placeholder:text-slate-400",
                  "focus:outline-none focus:ring-0",
                  isFocused 
                    ? "border-emerald-500 bg-white dark:bg-slate-900 shadow-2xl shadow-emerald-500/10" 
                    : "border-transparent hover:bg-slate-100 dark:hover:bg-slate-700"
                )}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className={cn(
                  "absolute right-2 sm:right-3 top-1/2 -translate-y-1/2 w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl flex items-center justify-center transition-all duration-300",
                  input.trim() 
                    ? "bg-emerald-600 text-white shadow-lg hover:bg-emerald-700" 
                    : "bg-slate-200 dark:bg-slate-700 text-slate-400"
                )}
              >
                <Send className="w-5 h-5 sm:w-6 sm:h-6" />
              </button>
            </div>
          </form>
          <div className="flex items-center justify-between mt-3 sm:mt-4 px-1 sm:px-2">
            <div className="flex items-center gap-3 sm:gap-4">
              <div className="flex items-center gap-1.5 sm:gap-2">
                <div className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-emerald-500" />
                <span className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">AI Online</span>
              </div>
              <div className="h-2.5 sm:h-3 w-px bg-slate-200 dark:bg-slate-800" />
              <p className="text-[8px] sm:text-[10px] font-bold text-slate-400 uppercase tracking-widest truncate max-w-[100px] sm:max-w-none">
                {socraticMode ? "Socratic Mode" : "Direct Mode"}
              </p>
            </div>
            <button 
              onClick={() => setShowQuizModal(true)}
              className="text-[8px] sm:text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest hover:underline"
            >
              Generate Quiz
            </button>
          </div>
        </div>

        {/* Quiz Modal */}
        {showQuizModal && (
          <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-in fade-in duration-300">
            <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-200 dark:border-slate-800">
              <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <h3 className="text-xl font-outfit font-black text-slate-900 dark:text-slate-100">Generate Practice Quiz</h3>
                <button onClick={() => setShowQuizModal(false)} className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
                  <X className="w-5 h-5 text-slate-400" />
                </button>
              </div>
              
              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Topic</label>
                  <input
                    type="text"
                    value={quizTopic}
                    onChange={(e) => setQuizTopic(e.target.value)}
                    placeholder="e.g., Photosynthesis"
                    className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none transition-all"
                  />
                </div>

                <div className="grid grid-cols-3 gap-2">
                  {(['easy', 'medium', 'hard'] as const).map((d) => (
                    <button
                      key={d}
                      onClick={() => setQuizDifficulty(d)}
                      className={cn(
                        "py-3 rounded-xl text-xs font-black capitalize transition-all",
                        quizDifficulty === d 
                          ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/20" 
                          : "bg-slate-100 dark:bg-slate-800 text-slate-500"
                      )}
                    >
                      {d}
                    </button>
                  ))}
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Questions</label>
                    <span className="text-xs font-black text-emerald-600">{numQuestions}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={numQuestions}
                    onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                    className="w-full accent-emerald-600"
                  />
                </div>
              </div>

              <div className="p-6 bg-slate-50 dark:bg-slate-800/50 flex gap-3">
                <button
                  onClick={() => setShowQuizModal(false)}
                  className="flex-1 px-4 py-3 rounded-xl font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateQuiz}
                  disabled={generatingQuiz}
                  className="flex-1 px-4 py-3 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-700 disabled:bg-slate-400 shadow-lg shadow-emerald-600/20 transition-all"
                >
                  {generatingQuiz ? 'Generating...' : 'Start Quiz'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
