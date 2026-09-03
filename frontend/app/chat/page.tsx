'use client'
import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { aiApi } from '@/lib/api'
import AppLayout from '@/components/AppLayout'
import { 
  Send, Brain, Loader2, Sparkles, User, Bot, 
  ChevronRight, LayoutGrid, Shield, Star, Clock,
  MessageSquare, Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  suggestions?: string[]
  related_topics?: string[]
}

export default function ChatPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your AI tutor. I can help explain WAEC topics, clarify concepts, and answer your study questions. What would you like to learn about?",
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentSubject, setCurrentSubject] = useState<string>('')
  const [aiStatus, setAiStatus] = useState<{ 
    available: boolean; 
    quota_remaining?: number;
    features?: {
      gpt_5_1_codex_max_enabled?: boolean;
    };
    model_name?: string;
  } | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const subjects = [
    'Mathematics', 'Physics', 'Chemistry', 'Biology', 
    'English', 'Geography', 'Government', 'Financial Accounting', 'Civic Education'
  ]

  useEffect(() => {
    if (!user) {
      router.push('/login')
    }
  }, [user, router])

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await aiApi.getStatus()
        setAiStatus(response.data)
      } catch (err) {
        console.error('Failed to fetch AI status:', err)
      }
    }
    fetchStatus()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = input
    setInput('')
    setLoading(true)

    try {
      const recentMessages = messages.slice(-10)
      const history = recentMessages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      const response = await aiApi.chat({
        message: currentInput,
        history,
        subject: currentSubject || undefined
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        suggestions: response.data.suggestions,
        related_topics: response.data.related_topics
      }
      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      console.error('Chat failed:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto h-[calc(100vh-120px)] flex flex-col px-6 py-8">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-2xl shadow-emerald-600/20">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h1 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">AI Tutor</h1>
                <div className="px-3 py-1 bg-emerald-500/10 border-2 border-emerald-500/20 rounded-full flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-[10px] font-black text-emerald-700 dark:text-emerald-400 uppercase tracking-widest">Online</span>
                </div>
                {aiStatus?.features?.gpt_5_1_codex_max_enabled && (
                  <div className="px-3 py-1 bg-purple-500/10 border-2 border-purple-500/20 rounded-full flex items-center gap-2">
                    <Sparkles className="w-3 h-3 text-purple-500" />
                    <span className="text-[10px] font-black text-purple-700 dark:text-purple-400 uppercase tracking-widest">GPT-5.1 Codex Max</span>
                  </div>
                )}
              </div>
              <p className="text-xs font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest">Powered by Base10 Intelligence</p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-4">
            <div className="bg-white dark:bg-slate-950 px-6 py-3 rounded-2xl border-2 border-slate-50 dark:border-slate-900 shadow-sm flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                <Zap className="w-5 h-5 text-emerald-500" />
              </div>
              <div>
                <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none mb-1">Quota</p>
                <p className="text-xl font-outfit font-black text-slate-900 dark:text-slate-100 leading-none">
                  {aiStatus?.quota_remaining ?? '∞'}
                </p>
              </div>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 bg-white dark:bg-slate-950 rounded-[3rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm overflow-hidden flex flex-col relative">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-hide">
            {messages.map((msg) => (
              <div 
                key={msg.id}
                className={cn(
                  "flex gap-4 max-w-[85%]",
                  msg.role === 'user' ? "ml-auto flex-row-reverse" : ""
                )}
              >
                <div className={cn(
                  "w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-xl",
                  msg.role === 'user' 
                    ? "bg-slate-900 dark:bg-emerald-600 text-white" 
                    : "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400"
                )}>
                  {msg.role === 'user' ? <User className="w-6 h-6" /> : <Bot className="w-6 h-6" />}
                </div>
                
                <div className="space-y-3">
                  <div className={cn(
                    "p-6 rounded-[2rem] text-lg leading-relaxed font-medium",
                    msg.role === 'user' 
                      ? "bg-slate-900 dark:bg-emerald-600 text-white rounded-tr-none" 
                      : "bg-slate-50 dark:bg-slate-900 text-slate-700 dark:text-slate-300 rounded-tl-none"
                  )}>
                    {msg.content}
                  </div>
                  
                  {msg.suggestions && msg.suggestions.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {msg.suggestions.map((s, i) => (
                        <button
                          key={i}
                          onClick={() => setInput(s)}
                          className="px-4 py-2 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-xl text-xs font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest hover:border-emerald-500/50 transition-all"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-2xl bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center">
                  <Loader2 className="w-6 h-6 text-emerald-600 animate-spin" />
                </div>
                <div className="bg-slate-50 dark:bg-slate-900 p-6 rounded-[2rem] rounded-tl-none">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-8 bg-slate-50/50 dark:bg-slate-900/50 border-t-2 border-slate-50 dark:border-slate-900">
            <form onSubmit={handleSubmit} className="relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask anything about WAEC topics..."
                className="w-full h-20 pl-8 pr-24 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 rounded-[2rem] text-lg font-medium focus:outline-none focus:border-emerald-500/50 transition-all dark:text-white"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className="absolute right-3 top-3 w-14 h-14 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-200 dark:disabled:bg-slate-800 text-white rounded-2xl shadow-xl shadow-emerald-600/20 transition-all flex items-center justify-center group"
              >
                <Send className="w-6 h-6 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </button>
            </form>
            <div className="mt-4 flex items-center justify-center gap-6">
              <div className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-500" />
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Secure Session</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4 text-amber-500" />
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Premium AI</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
