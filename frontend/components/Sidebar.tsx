'use client'
import { useState, useMemo } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard, BookOpen, MessageCircle, Zap, Calculator, 
  User, Trophy, Settings, LogOut, ChevronLeft, ChevronRight,
  Brain, Shield, Sparkles, Users
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'
import ThemeToggle from './ThemeToggle'
import AIQuotaIndicator from './AIQuotaIndicator'

const navigationItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Classrooms', href: '/classrooms', icon: BookOpen },
  { name: 'Practice', href: '/practice', icon: BookOpen },
  { name: 'AI Tutor', href: '/chat', icon: MessageCircle },
  { name: 'Flashcards', href: '/flashcards', icon: Zap },
  { name: 'Calculator', href: '/calculator', icon: Calculator },
  { name: 'Leaderboard', href: '/leaderboard', icon: Trophy },
  { name: 'Profile', href: '/profile', icon: User },
  { name: 'Settings', href: '/settings', icon: Settings },
]

const adminNavigationItems = [
  { name: 'Admin Home', href: '/admin', icon: Shield },
  { name: 'Moderation', href: '/admin/moderation', icon: Zap },
  { name: 'User Management', href: '/admin/users', icon: Users },
  { name: 'Question Bank', href: '/admin/questions', icon: BookOpen },
  { name: 'Reports', href: '/admin/reports', icon: Shield },
  { name: 'Role Management', href: '/admin/roles', icon: Shield },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuthStore()
  const [collapsed, setCollapsed] = useState(false)

  // Check if user is admin
  const isAdmin = useMemo(() => {
    const adminEmails = ['cjalloh25@gmail.com', 'esjallow03@gmail.com', 'esjallow@gmail.com']
    return user?.role === 'admin' || (user?.email && adminEmails.includes(user.email))
  }, [user])

  const handleLogout = () => {
    logout()
    router.push('/login')
  }

  // Navigation items based on role
  const currentNavigation = isAdmin ? adminNavigationItems : navigationItems

  return (
    <aside 
      className={cn(
        "fixed left-0 top-0 h-screen bg-white dark:bg-slate-950 border-r-2 border-slate-50 dark:border-slate-900",
        "transition-all duration-500 ease-in-out z-40 flex flex-col",
        collapsed ? 'w-24' : 'w-72'
      )}
    >
      {/* Header */}
      <div className="p-8">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center gap-4 group cursor-pointer">
              <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-xl shadow-emerald-600/20 group-hover:scale-110 transition-all duration-500">
                <Brain className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tighter">Base10</h1>
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                  <p className="text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-[0.2em]">{isAdmin ? 'Admin Console' : 'WAEC Pro'}</p>
                </div>
              </div>
            </div>
          )}
          {collapsed && (
            <div className="w-12 h-12 rounded-2xl bg-emerald-600 flex items-center justify-center shadow-xl shadow-emerald-600/20 mx-auto group-hover:scale-110 transition-all duration-500">
              <Brain className="w-7 h-7 text-white" />
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-6 scrollbar-hide">
        <ul className="space-y-2 px-6">
          {currentNavigation.map((item) => {
            const isActive = pathname === item.href || pathname?.startsWith(item.href + '/')
            const Icon = item.icon
            
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-4 px-4 h-14 rounded-2xl transition-all duration-500 group relative overflow-hidden",
                    collapsed ? 'justify-center' : '',
                    isActive 
                      ? (isAdmin ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-950 shadow-xl' : 'bg-emerald-600 text-white shadow-xl shadow-emerald-600/20')
                      : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900/50'
                  )}
                  title={collapsed ? item.name : undefined}
                >
                  {isActive && (
                    <div className="absolute left-0 top-0 w-1 h-full bg-white/20" />
                  )}
                  <Icon className={cn(
                    "w-6 h-6 shrink-0 transition-all duration-500",
                    isActive ? (isAdmin ? 'text-white dark:text-slate-950' : 'text-white') : 'group-hover:scale-110 group-hover:text-emerald-500'
                  )} />
                  {!collapsed && (
                    <span className="font-black text-sm uppercase tracking-widest">{item.name}</span>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer / User Section */}
      <div className="p-6 mt-auto border-t-2 border-slate-50 dark:border-slate-900 space-y-4">
        {!collapsed && <AIQuotaIndicator />}
        
        {!collapsed && (
          <div className="p-4 bg-slate-50 dark:bg-slate-900/50 rounded-2xl border border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                <User className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-black text-slate-900 dark:text-slate-100 truncate">
                  {user?.full_name || 'Student'}
                </p>
                <p className="text-[10px] font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest truncate">
                  {user?.email || 'Free Plan'}
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full h-10 flex items-center justify-center gap-2 text-xs font-black text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-all uppercase tracking-widest"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        )}

        <div className="flex items-center justify-between">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-3 rounded-2xl bg-slate-50 dark:bg-slate-900 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all text-slate-400 dark:text-slate-600"
          >
            {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
          
          {!collapsed && (
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <div className="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <span className="text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-widest">v2.0.0</span>
            </div>
          )}
          {collapsed && <ThemeToggle />}
        </div>
      </div>
    </aside>
  )
}
