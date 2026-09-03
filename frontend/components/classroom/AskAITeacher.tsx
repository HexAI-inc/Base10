"use client"

import { useState, useRef, useEffect } from 'react'
import { classroomApi, aiApi, authApi } from '@/lib/api'
import { useModalStore } from '@/store/modalStore'
import { useAuthStore } from '@/store/authStore'
import { cn } from '@/lib/utils'
import { Send, Sparkles, Brain, ListChecks, X, MessageSquare, Search, Loader2, User, Bot } from 'lucide-react'
import 'katex/dist/katex.min.css'
import { InlineMath, BlockMath } from 'react-katex'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
}

interface AskAITeacherProps {
  classroomId: number
}

export default function AskAITeacher({ classroomId }: AskAITeacherProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { showError } = useModalStore()
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

  const handleAskQuestion = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: question.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setQuestion('')
    setIsLoading(true)

    try {
      const res = await classroomApi.askAITeacher(classroomId, question.trim())
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: res.data.answer,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])

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
        showError('Failed to get AI response', 'Please try again later')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[600px] bg-white dark:bg-slate-950 rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b-2 border-slate-50 dark:border-slate-900 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/50">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500 flex items-center justify-center text-white shadow-2xl shadow-emerald-500/20">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-outfit font-black text-slate-900 dark:text-white tracking-tight">AI Teacher</h3>
            <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Always Online</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="px-4 py-2 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
            <p className="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest flex items-center gap-2">
              <Sparkles className="w-3 h-3" /> Socratic Mode
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-premium">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-6">
            <div className="w-20 h-20 rounded-3xl bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
              <Brain className="w-10 h-10 text-slate-300" />
            </div>
            <div>
              <h4 className="text-xl font-outfit font-black text-slate-900 dark:text-white mb-2">Ask anything about the class</h4>
              <p className="text-slate-500 font-medium max-w-xs mx-auto">I can help you understand complex topics, solve problems, or prepare for exams.</p>
            </div>
            <div className="grid grid-cols-1 gap-3 w-full max-w-sm">
              {['Explain the last lesson', 'Help me with my homework', 'Create a practice quiz'].map((hint, i) => (
                <button 
                  key={i}
                  onClick={() => setQuestion(hint)}
                  className="p-4 bg-slate-50 dark:bg-slate-900 hover:bg-emerald-50 dark:hover:bg-emerald-500/10 rounded-2xl border-2 border-transparent hover:border-emerald-500/20 text-slate-600 dark:text-slate-400 font-bold text-sm transition-all text-left"
                >
                  {hint}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={cn("flex gap-4", msg.type === 'user' ? "flex-row-reverse" : "flex-row")}>
              <div className={cn(
                "w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg",
                msg.type === 'user' ? "bg-slate-900 text-white" : "bg-emerald-500 text-white"
              )}>
                {msg.type === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>
              <div className={cn(
                "max-w-[80%] p-6 rounded-[2rem] font-medium text-lg leading-relaxed",
                msg.type === 'user' 
                  ? "bg-slate-900 text-white rounded-tr-none" 
                  : "bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100 rounded-tl-none border-2 border-slate-100 dark:border-slate-800"
              )}>
                {renderContent(msg.content)}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex gap-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-500 text-white flex items-center justify-center animate-pulse">
              <Bot className="w-5 h-5" />
            </div>
            <div className="bg-slate-50 dark:bg-slate-900 p-6 rounded-[2rem] rounded-tl-none border-2 border-slate-100 dark:border-slate-800">
              <div className="flex gap-2">
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
      <div className="p-6 bg-slate-50/50 dark:bg-slate-900/50 border-t-2 border-slate-50 dark:border-slate-900">
        <form onSubmit={handleAskQuestion} className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500 to-blue-500 rounded-2xl blur opacity-0 group-focus-within:opacity-20 transition duration-500" />
          <div className="relative flex items-center gap-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask your teacher a question..."
              className="w-full h-16 pl-6 pr-20 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-800 focus:border-emerald-500/50 rounded-2xl outline-none text-slate-900 dark:text-white font-bold transition-all"
            />
            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="absolute right-2 w-12 h-12 bg-emerald-600 text-white rounded-xl flex items-center justify-center shadow-lg shadow-emerald-600/20 hover:scale-110 transition-all disabled:opacity-50"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
