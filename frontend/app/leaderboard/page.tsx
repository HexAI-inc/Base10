'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import AppLayout from '@/components/AppLayout'
import { 
  Trophy, Medal, Crown, TrendingUp, Award, Star, 
  Filter, Loader2, Sparkles, Shield, ChevronRight,
  User, Target, Zap
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface LeaderboardEntry {
  rank: number
  user_id: number
  full_name: string
  avatar_url?: string
  total_points: number
  level: number
  accuracy: number
  streak_days: number
  subjects_mastered: number
  is_current_user?: boolean
}

export default function LeaderboardPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'weekly' | 'monthly'>('all')
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }

    setTimeout(() => {
      setLeaderboard([
        { rank: 1, user_id: 1, full_name: 'Aminata Kamara', total_points: 15420, level: 12, accuracy: 94.5, streak_days: 45, subjects_mastered: 6 },
        { rank: 2, user_id: 2, full_name: 'Ibrahim Sesay', total_points: 14280, level: 11, accuracy: 92.3, streak_days: 38, subjects_mastered: 5 },
        { rank: 3, user_id: 3, full_name: 'Fatmata Conteh', total_points: 13150, level: 11, accuracy: 91.8, streak_days: 42, subjects_mastered: 5 },
        { rank: 4, user_id: user.id, full_name: user.full_name || 'You', total_points: 12540, level: 10, accuracy: 89.2, streak_days: 28, subjects_mastered: 4, is_current_user: true },
        { rank: 5, user_id: 5, full_name: 'Mohamed Jalloh', total_points: 11920, level: 10, accuracy: 88.6, streak_days: 35, subjects_mastered: 4 },
        { rank: 6, user_id: 6, full_name: 'Isatu Bangura', total_points: 10850, level: 9, accuracy: 87.4, streak_days: 21, subjects_mastered: 4 },
        { rank: 7, user_id: 7, full_name: 'Sahr Koroma', total_points: 9740, level: 9, accuracy: 86.2, streak_days: 15, subjects_mastered: 3 },
      ])
      setLoading(false)
    }, 1000)
  }, [user, router])

  if (loading) {
    return (
      <AppLayout>
        <div className="min-h-[80vh] flex flex-col items-center justify-center">
          <div className="relative w-24 h-24 mb-8">
            <div className="absolute inset-0 border-4 border-emerald-500/10 rounded-[2rem] animate-pulse" />
            <div className="absolute inset-0 border-4 border-emerald-500 border-t-transparent rounded-[2rem] animate-spin" />
            <Trophy className="absolute inset-0 m-auto w-10 h-10 text-emerald-500" />
          </div>
          <p className="text-slate-900 dark:text-slate-100 font-outfit font-black text-xl tracking-tight">Ranking Students</p>
          <p className="text-slate-400 dark:text-slate-600 font-bold text-xs uppercase tracking-[0.3em] mt-2">Calculating scores...</p>
        </div>
      </AppLayout>
    )
  }

  const topThree = leaderboard.slice(0, 3)
  const others = leaderboard.slice(3)

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-12">
        {/* Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 sm:gap-8 mb-10 sm:mb-16">
          <div className="flex items-center gap-4 sm:gap-6">
            <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-xl sm:rounded-2xl bg-emerald-600 flex items-center justify-center shadow-2xl shadow-emerald-600/20">
              <Trophy className="w-6 h-6 sm:w-9 sm:h-9 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2 sm:gap-3 mb-0.5 sm:mb-1">
                <h1 className="text-2xl sm:text-4xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Leaderboard</h1>
                <div className="px-2 sm:px-3 py-0.5 sm:py-1 bg-emerald-500/10 border-2 border-emerald-500/20 rounded-full">
                  <span className="text-[8px] sm:text-[10px] font-black text-emerald-700 dark:text-emerald-400 uppercase tracking-widest">Global</span>
                </div>
              </div>
              <p className="text-[10px] sm:text-sm font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest">Top performing students</p>
            </div>
          </div>

          <div className="flex bg-slate-50 dark:bg-slate-900 p-1 sm:p-1.5 rounded-xl sm:rounded-2xl border-2 border-slate-100 dark:border-slate-800 overflow-x-auto scrollbar-hide">
            {['weekly', 'monthly', 'all'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as any)}
                className={cn(
                  "px-4 sm:px-6 py-2 sm:py-2.5 rounded-lg sm:rounded-xl text-[8px] sm:text-[10px] font-black uppercase tracking-widest transition-all whitespace-nowrap",
                  filter === f 
                    ? "bg-white dark:bg-slate-800 text-emerald-600 dark:text-emerald-400 shadow-sm" 
                    : "text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                )}
              >
                {f}
              </button>
            ))}
          </div>
        </header>

        {/* Podium */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 mb-10 sm:mb-16 items-end">
          {/* 2nd Place */}
          <div className="order-2 md:order-1">
            <div className="bg-white dark:bg-slate-950 p-6 sm:p-8 rounded-[2rem] sm:rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm text-center relative group hover:shadow-2xl transition-all duration-500">
              <div className="absolute -top-5 sm:-top-6 left-1/2 -translate-x-1/2 w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-slate-200 dark:bg-slate-800 flex items-center justify-center border-4 border-white dark:border-slate-950">
                <Medal className="w-5 h-5 sm:w-6 sm:h-6 text-slate-500" />
              </div>
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl sm:rounded-3xl bg-slate-100 dark:bg-slate-900 mx-auto mb-3 sm:mb-4 flex items-center justify-center text-xl sm:text-2xl font-black text-slate-400">
                {topThree[1].full_name[0]}
              </div>
              <h3 className="text-sm sm:text-base font-outfit font-black text-slate-900 dark:text-slate-100 mb-0.5 sm:mb-1">{topThree[1].full_name}</h3>
              <p className="text-[8px] sm:text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest mb-3 sm:mb-4">{topThree[1].total_points} PTS</p>
              <div className="flex items-center justify-center gap-3 sm:gap-4 pt-3 sm:pt-4 border-t-2 border-slate-50 dark:border-slate-900">
                <div>
                  <p className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">Level</p>
                  <p className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100">{topThree[1].level}</p>
                </div>
                <div className="w-px h-6 sm:h-8 bg-slate-100 dark:bg-slate-800" />
                <div>
                  <p className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">Acc</p>
                  <p className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100">{topThree[1].accuracy}%</p>
                </div>
              </div>
            </div>
          </div>

          {/* 1st Place */}
          <div className="order-1 md:order-2">
            <div className="bg-emerald-600 p-8 sm:p-10 rounded-[2.5rem] sm:rounded-[3rem] shadow-2xl shadow-emerald-600/20 text-center relative group hover:scale-105 transition-all duration-500">
              <div className="absolute -top-6 sm:-top-8 left-1/2 -translate-x-1/2 w-12 h-12 sm:w-16 sm:h-16 rounded-xl sm:rounded-2xl bg-amber-400 flex items-center justify-center border-4 border-white dark:border-slate-950 shadow-xl">
                <Crown className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
              </div>
              <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-[1.5rem] sm:rounded-[2rem] bg-white/20 backdrop-blur-xl mx-auto mb-4 sm:mb-6 flex items-center justify-center text-3xl sm:text-4xl font-black text-white">
                {topThree[0].full_name[0]}
              </div>
              <h3 className="text-xl sm:text-2xl font-outfit font-black text-white mb-0.5 sm:mb-1">{topThree[0].full_name}</h3>
              <p className="text-[10px] sm:text-xs font-black text-emerald-100 uppercase tracking-[0.2em] mb-4 sm:mb-6">{topThree[0].total_points} PTS</p>
              <div className="flex items-center justify-center gap-4 sm:gap-6 pt-4 sm:pt-6 border-t-2 border-white/10">
                <div>
                  <p className="text-[8px] sm:text-[10px] font-black text-emerald-100 uppercase tracking-widest opacity-60">Level</p>
                  <p className="text-base sm:text-lg font-black text-white">{topThree[0].level}</p>
                </div>
                <div className="w-px h-8 sm:h-10 bg-white/10" />
                <div>
                  <p className="text-[8px] sm:text-[10px] font-black text-emerald-100 uppercase tracking-widest opacity-60">Acc</p>
                  <p className="text-base sm:text-lg font-black text-white">{topThree[0].accuracy}%</p>
                </div>
              </div>
            </div>
          </div>

          {/* 3rd Place */}
          <div className="order-3">
            <div className="bg-white dark:bg-slate-950 p-6 sm:p-8 rounded-[2rem] sm:rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm text-center relative group hover:shadow-2xl transition-all duration-500">
              <div className="absolute -top-5 sm:-top-6 left-1/2 -translate-x-1/2 w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-amber-600/20 flex items-center justify-center border-4 border-white dark:border-slate-950">
                <Medal className="w-5 h-5 sm:w-6 sm:h-6 text-amber-700" />
              </div>
              <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl sm:rounded-3xl bg-slate-100 dark:bg-slate-900 mx-auto mb-3 sm:mb-4 flex items-center justify-center text-xl sm:text-2xl font-black text-slate-400">
                {topThree[2].full_name[0]}
              </div>
              <h3 className="text-sm sm:text-base font-outfit font-black text-slate-900 dark:text-slate-100 mb-0.5 sm:mb-1">{topThree[2].full_name}</h3>
              <p className="text-[8px] sm:text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest mb-3 sm:mb-4">{topThree[2].total_points} PTS</p>
              <div className="flex items-center justify-center gap-3 sm:gap-4 pt-3 sm:pt-4 border-t-2 border-slate-50 dark:border-slate-900">
                <div>
                  <p className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">Level</p>
                  <p className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100">{topThree[2].level}</p>
                </div>
                <div className="w-px h-6 sm:h-8 bg-slate-100 dark:bg-slate-800" />
                <div>
                  <p className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">Acc</p>
                  <p className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100">{topThree[2].accuracy}%</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* List */}
        <div className="space-y-3 sm:space-y-4">
          {others.map((entry) => (
            <div 
              key={entry.rank}
              className={cn(
                "p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border-2 transition-all duration-500 flex items-center gap-4 sm:gap-6 group",
                entry.is_current_user 
                  ? "bg-emerald-50 dark:bg-emerald-900/10 border-emerald-500/30 shadow-xl shadow-emerald-600/5" 
                  : "bg-white dark:bg-slate-950 border-slate-50 dark:border-slate-900 hover:border-emerald-500/30"
              )}
            >
              <div className="w-8 sm:w-12 text-lg sm:text-2xl font-outfit font-black text-slate-300 dark:text-slate-800 group-hover:text-emerald-500 transition-colors">
                #{entry.rank}
              </div>
              
              <div className="w-10 h-10 sm:w-14 sm:h-14 rounded-xl sm:rounded-2xl bg-slate-100 dark:bg-slate-900 flex items-center justify-center text-base sm:text-xl font-black text-slate-400 group-hover:scale-110 transition-transform">
                {entry.full_name[0]}
              </div>
              
              <div className="flex-1 min-w-0">
                <h4 className="font-outfit font-black text-slate-900 dark:text-slate-100 text-sm sm:text-lg truncate">
                  {entry.full_name}
                  {entry.is_current_user && (
                    <span className="ml-2 sm:ml-3 text-[8px] sm:text-[10px] bg-emerald-600 text-white px-1.5 sm:px-2 py-0.5 rounded-full uppercase tracking-widest">You</span>
                  )}
                </h4>
                <div className="flex items-center gap-2 sm:gap-4 mt-0.5 sm:mt-1">
                  <div className="flex items-center gap-1 sm:gap-1.5">
                    <Target className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-slate-400" />
                    <span className="text-[10px] sm:text-xs font-bold text-slate-500">{entry.accuracy}%</span>
                  </div>
                  <div className="w-1 h-1 rounded-full bg-slate-200 dark:bg-slate-800" />
                  <div className="flex items-center gap-1 sm:gap-1.5">
                    <Zap className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-amber-500" />
                    <span className="text-[10px] sm:text-xs font-bold text-slate-500">{entry.streak_days}d</span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <p className="text-base sm:text-xl font-outfit font-black text-slate-900 dark:text-slate-100 leading-none mb-0.5 sm:mb-1">{entry.total_points}</p>
                <p className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">Points</p>
              </div>
              
              <div className="hidden sm:flex w-12 h-12 rounded-2xl bg-slate-50 dark:bg-slate-900 items-center justify-center text-slate-300 group-hover:text-emerald-500 transition-colors">
                <ChevronRight className="w-6 h-6" />
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-12 sm:mt-16 flex items-center justify-center gap-6 sm:gap-8">
          <div className="flex items-center gap-2 sm:gap-3">
            <Shield className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-500" />
            <span className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">Verified</span>
          </div>
          <div className="flex items-center gap-2 sm:gap-3">
            <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-amber-500" />
            <span className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest">Live</span>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
