'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { studentApi, aiApi } from '@/lib/api'
import { 
  Brain, BookOpen, MessageCircle, Zap, Calculator, Trophy, 
  Target, TrendingUp, Loader2, Search, Sparkles, ArrowRight, 
  ChevronRight, Star, Clock, Shield, ZapOff
} from 'lucide-react'
import AppLayout from '@/components/AppLayout'
import RadarChart from '@/components/RadarChart'
import Link from 'next/link'
import { cn } from '@/lib/utils'

interface SubjectStat {
  subject_name: string
  total_attempts: number
  accuracy: number
  mastery_level: string
  top_topics: string[]
}

interface DashboardData {
  total_attempts: number
  overall_accuracy: number
  streak_days: number
  study_time_hours: number
  due_reviews: number
  today_attempts: number
  has_target_exam: boolean
  subject_performance?: Array<{
    subject_name: string
    accuracy: number
  }>
  recommendations?: Array<{
    priority: string
    type: string
    title: string
    message: string
    action: string
    data?: any
  }>
  exam_readiness?: {
    readiness_score: number
    readiness_level: string
    message: string
  }
}

export default function DashboardPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [subjectStats, setSubjectStats] = useState<SubjectStat[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }

    // Redirect admins to admin dashboard
    const adminEmails = ['cjalloh25@gmail.com', 'esjallow03@gmail.com', 'esjallow@gmail.com']
    if (user.role === 'admin' || (user.email && adminEmails.includes(user.email))) {
      router.push('/admin')
      return
    }

    const fetchDashboard = async () => {
      try {
        const [summaryRes, subjectsRes, recommendationsRes] = await Promise.allSettled([
          studentApi.getDashboardSummary(),
          studentApi.getSubjects(),
          aiApi.getRecommendations()
        ])

        const newData: any = {}
        
        if (summaryRes.status === 'fulfilled') {
          Object.assign(newData, summaryRes.value.data)
        }
        
        if (recommendationsRes.status === 'fulfilled') {
          newData.recommendations = recommendationsRes.value.data
        } else {
          console.warn('AI Recommendations failed to load:', recommendationsRes.reason)
          newData.recommendations = []
        }

        if (subjectsRes.status === 'fulfilled') {
          setSubjectStats(subjectsRes.value.data)
        }

        setDashboardData(newData)
      } catch (err) {
        console.error('Critical dashboard load failure:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [user, router])

  if (!user) {
    return null
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white dark:bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-24 h-24 mx-auto mb-8">
            <div className="absolute inset-0 border-4 border-emerald-500/10 rounded-[2rem] animate-pulse" />
            <div className="absolute inset-0 border-4 border-emerald-500 border-t-transparent rounded-[2rem] animate-spin" />
            <Brain className="absolute inset-0 m-auto w-10 h-10 text-emerald-500" />
          </div>
          <p className="text-slate-900 dark:text-slate-100 font-outfit font-black text-xl tracking-tight">Base10 Intelligence</p>
          <p className="text-slate-400 dark:text-slate-600 font-bold text-xs uppercase tracking-[0.3em] mt-2">Optimizing your path...</p>
        </div>
      </div>
    )
  }

  const stats = [
    { label: 'Questions', value: dashboardData?.total_attempts || 0, icon: Target, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Accuracy', value: `${dashboardData?.overall_accuracy || 0}%`, icon: TrendingUp, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
    { label: 'Streak', value: `${dashboardData?.streak_days || 0} Days`, icon: Zap, color: 'text-amber-500', bg: 'bg-amber-500/10' },
    { label: 'Study Time', value: `${dashboardData?.study_time_hours || 0}h`, icon: Clock, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  ]

  const getSubjectIcon = (name: string) => {
    const icons: Record<string, string> = {
      'Mathematics': '📐',
      'English Language': '📚',
      'Physics': '⚛️',
      'Chemistry': '🧪',
      'Biology': '🧬',
      'Geography': '🌍',
      'Government': '🏛️',
      'Civic Education': '⚖️',
      'Financial Accounting': '💰',
    }
    return icons[name] || '📖'
  }

  const getMasteryColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'expert': return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20'
      case 'proficient': return 'text-blue-500 bg-blue-500/10 border-blue-500/20'
      case 'developing': return 'text-amber-500 bg-amber-500/10 border-amber-500/20'
      default: return 'text-slate-400 bg-slate-100 dark:bg-slate-900 border-slate-200 dark:border-slate-800'
    }
  }

  const subjects = [
    { name: 'Mathematics', icon: '📐', color: 'bg-blue-500', questions: 200, available: true },
    { name: 'English Language', icon: '📚', color: 'bg-purple-500', questions: 0, available: false },
    { name: 'Physics', icon: '⚛️', color: 'bg-cyan-500', questions: 200, available: true },
    { name: 'Chemistry', icon: '🧪', color: 'bg-green-500', questions: 0, available: false },
    { name: 'Biology', icon: '🧬', color: 'bg-emerald-500', questions: 200, available: true },
    { name: 'Geography', icon: '🌍', color: 'bg-teal-500', questions: 200, available: true },
    { name: 'Government', icon: '🏛️', color: 'bg-indigo-500', questions: 52, available: true },
    { name: 'Civic Education', icon: '⚖️', color: 'bg-amber-500', questions: 0, available: false },
    { name: 'Financial Accounting', icon: '💰', color: 'bg-rose-500', questions: 150, available: true },
  ]

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto px-6 lg:px-12 py-12">
        {/* Welcome Header */}
        <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-8">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="px-4 py-1.5 bg-emerald-500/10 border-2 border-emerald-500/20 rounded-full flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <span className="text-[10px] font-black text-emerald-700 dark:text-emerald-400 uppercase tracking-[0.2em]">Premium Access</span>
              </div>
              <div className="px-4 py-1.5 bg-slate-100 dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-800 rounded-full">
                <span className="text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-[0.2em]">v2.0.0</span>
              </div>
            </div>
            <h1 className="text-5xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tighter mb-3">
              Welcome back, <span className="text-emerald-600">{user?.full_name?.split(' ')[0]}</span>
            </h1>
            <div className="flex flex-col gap-4">
              <p className="text-lg font-medium text-slate-500 dark:text-slate-400 max-w-xl">
                Your WAEC preparation is <span className="text-slate-900 dark:text-slate-100 font-bold">74% complete</span>. You're on track for an A1 in Mathematics.
              </p>
              
              {/* Daily Goal Tracker */}
              <div className="flex items-center gap-4 max-w-xs">
                <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-900 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-emerald-500 transition-all duration-1000" 
                    style={{ width: `${Math.min(((dashboardData?.today_attempts || 0) / 20) * 100, 100)}%` }}
                  />
                </div>
                <span className="text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-[0.2em] whitespace-nowrap">
                  {dashboardData?.today_attempts || 0}/20 Questions Today
                </span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <Link 
              href="/practice"
              className="relative h-16 px-8 bg-emerald-600 hover:bg-emerald-500 text-white rounded-[2rem] font-outfit font-black text-sm uppercase tracking-[0.2em] shadow-2xl shadow-emerald-600/20 transition-all duration-500 flex items-center gap-3 group"
            >
              Start Practice
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              
              {/* Due Reviews Badge */}
              {(dashboardData?.due_reviews || 0) > 0 && (
                <span className="absolute -top-2 -right-2 w-8 h-8 bg-red-500 text-white text-[10px] font-black rounded-full flex items-center justify-center animate-bounce shadow-lg border-4 border-white dark:border-slate-950">
                  {dashboardData?.due_reviews}
                </span>
              )}
            </Link>
          </div>
        </header>

        {/* Target Exam Prompt */}
        {!loading && !dashboardData?.has_target_exam && (
          <div className="mb-12 p-8 bg-gradient-to-r from-emerald-600 to-teal-600 rounded-[2.5rem] text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl shadow-emerald-600/20 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32 blur-3xl group-hover:scale-150 transition-transform duration-1000" />
            <div className="relative z-10 flex items-center gap-6">
              <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur-xl flex items-center justify-center">
                <Target className="w-8 h-8 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-outfit font-black mb-1">Set Your Target Exam</h3>
                <p className="text-white/80 font-medium">Unlock personalized insights and a custom study plan tailored to your goals.</p>
              </div>
            </div>
            <button className="relative z-10 h-14 px-8 bg-white text-emerald-600 rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] hover:bg-emerald-50 transition-colors whitespace-nowrap">
              Set Target Now
            </button>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8 sm:mb-12">
          {loading ? (
            [...Array(4)].map((_, i) => (
              <div key={i} className="bg-white dark:bg-slate-950 p-6 sm:p-8 rounded-[2rem] sm:rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm animate-pulse">
                <div className="w-10 h-10 sm:w-14 sm:h-14 rounded-xl sm:rounded-2xl bg-slate-100 dark:bg-slate-900 mb-4 sm:mb-6" />
                <div className="h-2 w-16 sm:w-20 bg-slate-100 dark:bg-slate-900 rounded-full mb-2 sm:mb-3" />
                <div className="h-6 sm:h-8 w-20 sm:w-24 bg-slate-100 dark:bg-slate-900 rounded-lg sm:rounded-xl" />
              </div>
            ))
          ) : (
            stats.map((stat, i) => (
              <div key={i} className="bg-white dark:bg-slate-950 p-6 sm:p-8 rounded-[2rem] sm:rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm hover:shadow-2xl transition-all duration-500 group">
                <div className={cn("w-10 h-10 sm:w-14 sm:h-14 rounded-xl sm:rounded-2xl flex items-center justify-center mb-4 sm:mb-6 transition-transform duration-500 group-hover:scale-110 group-hover:rotate-3", stat.bg)}>
                  <stat.icon className={cn("w-5 h-5 sm:w-7 sm:h-7", stat.color)} />
                </div>
                <p className="text-[8px] sm:text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-[0.2em] mb-0.5 sm:mb-1">{stat.label}</p>
                <p className="text-xl sm:text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">{stat.value}</p>
              </div>
            ))
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content: Performance & Subjects */}
          <div className="lg:col-span-2 space-y-8">
            {/* Performance Radar */}
            <div className="bg-white dark:bg-slate-950 p-6 sm:p-8 rounded-[2rem] sm:rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
                <div>
                  <h2 className="text-xl sm:text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Performance Overview</h2>
                  <p className="text-[10px] font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest mt-1">Subject Mastery Analysis</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full bg-emerald-500" />
                  <span className="text-[8px] sm:text-[10px] font-black text-slate-500 uppercase tracking-widest">Current Accuracy</span>
                </div>
              </div>
              
              <div className="h-[250px] sm:h-[350px] flex items-center justify-center">
                {loading ? (
                  <div className="w-48 h-48 sm:w-64 sm:h-64 rounded-full border-4 border-dashed border-slate-100 dark:border-slate-900 animate-spin" />
                ) : (
                  <RadarChart 
                    data={dashboardData?.subject_performance?.map((sp: any) => ({
                      subject: sp.subject_name,
                      value: sp.accuracy,
                      fullMark: 100
                    })) || []} 
                    size={350}
                  />
                )}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Your Subjects</h2>
              <button className="text-xs font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-[0.2em] hover:underline">View All</button>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {subjectStats.map((subject, i) => (
                <div 
                  key={i}
                  className="group relative p-8 bg-white dark:bg-slate-950 rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 hover:border-emerald-500/50 shadow-sm hover:shadow-2xl transition-all duration-500 overflow-hidden"
                >
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-6">
                      <div className="text-4xl">{getSubjectIcon(subject.subject_name)}</div>
                      <div className={cn(
                        "px-3 py-1 rounded-xl text-[10px] font-black uppercase tracking-widest border",
                        getMasteryColor(subject.mastery_level)
                      )}>
                        {subject.mastery_level}
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-2">{subject.subject_name}</h3>
                    
                    <div className="flex items-center gap-4 mb-6">
                      <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-900 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-emerald-500 transition-all duration-1000" 
                          style={{ width: `${subject.accuracy}%` }}
                        />
                      </div>
                      <span className="text-xs font-bold text-slate-900 dark:text-slate-100">{subject.accuracy}%</span>
                    </div>

                    <div className="space-y-3">
                      <p className="text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-widest">Top Topics</p>
                      <div className="flex flex-wrap gap-2">
                        {subject.top_topics.map((topic, j) => (
                          <span key={j} className="px-3 py-1 bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 text-[10px] font-bold rounded-lg border border-slate-100 dark:border-slate-800">
                            {topic}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="absolute bottom-0 left-0 w-full h-1.5 bg-emerald-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-700 origin-left" />
                </div>
              ))}
            </div>
          </div>

          {/* Sidebar: Readiness & Recommendations */}
          <div className="space-y-8">
            {/* Readiness Card */}
            {dashboardData?.exam_readiness && (
              <div className="bg-slate-900 dark:bg-emerald-600 p-8 rounded-[2.5rem] text-white shadow-2xl shadow-emerald-600/20 relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 blur-2xl group-hover:scale-150 transition-transform duration-700" />
                
                <div className="relative z-10">
                  <div className="flex items-center gap-3 mb-8">
                    <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-xl flex items-center justify-center">
                      <Shield className="w-6 h-6 text-white" />
                    </div>
                    <p className="text-[10px] font-black uppercase tracking-[0.3em]">Exam Readiness</p>
                  </div>
                  
                  <div className="flex items-end gap-4 mb-6">
                    <span className="text-6xl font-outfit font-black leading-none">
                      {dashboardData.exam_readiness.readiness_score || 0}%
                    </span>
                    <div className="mb-2">
                      <p className="text-xs font-black uppercase tracking-widest opacity-60">Level</p>
                      <p className="text-sm font-bold">{dashboardData.exam_readiness.readiness_level || 'Analyzing'}</p>
                    </div>
                  </div>
                  
                  <p className="text-sm font-medium leading-relaxed opacity-80 mb-8">
                    {dashboardData.exam_readiness.message || 'Keep practicing to see your readiness score.'}
                  </p>
                  
                  <button className="w-full h-14 bg-white text-slate-900 rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] hover:bg-emerald-50 transition-colors">
                    View Detailed Report
                  </button>
                </div>
              </div>
            )}

            {/* Recommendations */}
            {dashboardData?.recommendations && dashboardData.recommendations.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight px-2">AI Recommendations</h3>
                {dashboardData.recommendations.map((rec, i) => (
                  <div key={i} className="bg-white dark:bg-slate-950 p-6 rounded-[2rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm hover:shadow-xl transition-all duration-500 group">
                    <div className="flex items-start gap-4">
                      <div className={cn(
                        "w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0",
                        rec.priority === 'high' ? 'bg-red-500/10 text-red-500' : 'bg-emerald-500/10 text-emerald-500'
                      )}>
                        <Star className="w-6 h-6" />
                      </div>
                      <div>
                        <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-600 mb-1">{rec.type}</p>
                        <h4 className="font-outfit font-black text-slate-900 dark:text-slate-100 mb-2">{rec.title}</h4>
                        <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-4">{rec.message}</p>
                        <button 
                          onClick={() => {
                            if (rec.action === 'practice_topics' && rec.data?.topics) {
                              router.push(`/practice?subject=${rec.data.topics[0]}`)
                            } else if (rec.action === 'maintain_streak') {
                              router.push('/practice')
                            }
                          }}
                          className="text-xs font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-[0.2em] flex items-center gap-2 group-hover:gap-3 transition-all"
                        >
                          {rec.action.replace('_', ' ')}
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
