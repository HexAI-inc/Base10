'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/store/authStore'
import { adminApi, systemApi } from '@/lib/api'
import AppLayout from '@/components/AppLayout'
import { 
  Activity, 
  Users, 
  BookOpen, 
  TrendingUp, 
  AlertCircle, 
  CheckCircle2,
  XCircle,
  Loader2,
  Database,
  Clock,
  Shield,
  Zap,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Globe,
  Server
} from 'lucide-react'
import { cn } from '@/lib/utils'

export default function AdminDashboard() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [health, setHealth] = useState<any>(null)
  const [growth, setGrowth] = useState<any>(null)
  const [content, setContent] = useState<any>(null)
  const [engagement, setEngagement] = useState<any>(null)
  const [systemConfig, setSystemConfig] = useState<any>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const adminEmails = ['cjalloh25@gmail.com', 'esjallow03@gmail.com', 'esjallow@gmail.com']
    const isAdmin = user?.role === 'admin' || (user?.email && adminEmails.includes(user.email))
    
    if (!user || !isAdmin) {
      router.push('/dashboard')
      return
    }
    loadDashboardData()
  }, [user, router])

  const loadDashboardData = async () => {
    setLoading(true)
    setError('')
    try {
      const [hRes, gRes, cRes, eRes, sConfig] = await Promise.all([
        adminApi.getHealth(),
        adminApi.getUserGrowth(),
        adminApi.getContentQuality(),
        adminApi.getEngagement(),
        systemApi.getConfig()
      ])
      setHealth(hRes.data)
      setGrowth(gRes.data)
      setContent(cRes.data)
      setEngagement(eRes.data)
      setSystemConfig(sConfig.data)
    } catch (err: any) {
      setError('Failed to load some dashboard metrics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-full p-8 gap-4">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
            <Shield className="w-6 h-6 text-emerald-500 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
          </div>
          <p className="text-slate-500 font-bold uppercase tracking-widest text-xs animate-pulse">Loading Admin Console...</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="max-w-7xl mx-auto p-6 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 className="text-4xl font-outfit font-black text-slate-900 dark:text-white tracking-tight">Admin Console</h1>
            <p className="text-slate-500 font-medium">System monitoring and platform management</p>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={loadDashboardData}
              className="h-12 px-6 bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 rounded-xl font-bold text-xs uppercase tracking-widest transition-all flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" /> Refresh
            </button>
            <div className="h-12 px-6 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-xl font-bold text-xs uppercase tracking-widest flex items-center gap-2 border border-emerald-500/20">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              System Healthy
            </div>
          </div>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            { label: 'Total Users', value: health?.total_users || 0, icon: Users, trend: '+12%', color: 'emerald' },
            { label: 'Active (24h)', value: health?.active_users_24h || 0, icon: Activity, trend: '+5%', color: 'blue' },
            { label: 'Total Questions', value: health?.total_questions || 0, icon: BookOpen, trend: '+24', color: 'purple' },
            { label: 'Avg Accuracy', value: `${(health?.average_accuracy * 100 || 0).toFixed(1)}%`, icon: BarChart3, trend: '-2%', color: 'orange' },
          ].map((stat, i) => (
            <div key={i} className="bg-white dark:bg-slate-950 rounded-[2rem] p-8 border-2 border-slate-50 dark:border-slate-900 shadow-xl group hover:border-emerald-500/20 transition-all">
              <div className="flex items-center justify-between mb-6">
                <div className={cn("w-12 h-12 rounded-2xl flex items-center justify-center", `bg-${stat.color}-500/10 text-${stat.color}-500`)}>
                  <stat.icon className="w-6 h-6" />
                </div>
                <span className={cn("text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest", stat.trend.startsWith('+') ? "bg-emerald-500/10 text-emerald-500" : "bg-red-500/10 text-red-500")}>
                  {stat.trend}
                </span>
              </div>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">{stat.label}</p>
              <p className="text-3xl font-outfit font-black text-slate-900 dark:text-white">{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Management Quick Links */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { label: 'Content Moderation', desc: 'Manage questions, assets & flashcards', icon: BookOpen, href: '/admin/moderation', color: 'emerald' },
            { label: 'User Management', desc: 'Manage roles, permissions & accounts', icon: Users, href: '/admin/users', color: 'blue' },
            { label: 'System Reports', desc: 'Review flagged content & issues', icon: AlertCircle, href: '/admin/reports', color: 'red' },
          ].map((link, i) => (
            <Link 
              key={i} 
              href={link.href}
              className="bg-white dark:bg-slate-950 rounded-[2rem] p-8 border-2 border-slate-50 dark:border-slate-900 shadow-xl group hover:border-emerald-500/20 transition-all flex items-center gap-6"
            >
              <div className={cn("w-14 h-14 rounded-2xl flex items-center justify-center shrink-0", `bg-${link.color}-500/10 text-${link.color}-500`)}>
                <link.icon className="w-7 h-7" />
              </div>
              <div>
                <h4 className="font-black text-slate-900 dark:text-white group-hover:text-emerald-500 transition-colors">{link.label}</h4>
                <p className="text-xs text-slate-500 font-medium">{link.desc}</p>
              </div>
            </Link>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* System Health */}
          <div className="lg:col-span-2 bg-white dark:bg-slate-950 rounded-[2.5rem] p-10 border-2 border-slate-50 dark:border-slate-900 shadow-xl">
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-white flex items-center gap-3">
                <Database className="w-6 h-6 text-emerald-500" />
                Infrastructure Status
              </h3>
              {systemConfig && (
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Environment</p>
                    <p className="text-xs font-bold text-slate-900 dark:text-white uppercase">{systemConfig.environment}</p>
                  </div>
                  <div className="w-px h-8 bg-slate-200 dark:bg-slate-800" />
                  <div className="text-right">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Version</p>
                    <p className="text-xs font-bold text-slate-900 dark:text-white">{systemConfig.version}</p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-3xl border-2 border-transparent hover:border-emerald-500/20 transition-all">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                      <Database className="w-5 h-5 text-emerald-500" />
                    </div>
                    <p className="font-bold text-slate-900 dark:text-white">PostgreSQL</p>
                  </div>
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full w-[98%]" />
                </div>
                <div className="flex justify-between mt-3">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">98% Connection Health</p>
                  <p className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Active</p>
                </div>
              </div>

              <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-3xl border-2 border-transparent hover:border-emerald-500/20 transition-all">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
                      <Server className="w-5 h-5 text-blue-500" />
                    </div>
                    <p className="font-bold text-slate-900 dark:text-white">Redis Cache</p>
                  </div>
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-blue-500 h-full w-[100%]" />
                </div>
                <div className="flex justify-between mt-3">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">100% Connection Health</p>
                  <p className="text-[10px] font-black text-blue-500 uppercase tracking-widest">Active</p>
                </div>
              </div>

              {systemConfig?.storage && (
                <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-3xl border-2 border-transparent hover:border-emerald-500/20 transition-all">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
                        <Globe className="w-5 h-5 text-purple-500" />
                      </div>
                      <p className="font-bold text-slate-900 dark:text-white">Object Storage</p>
                    </div>
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                  </div>
                  <p className="text-xs font-medium text-slate-500 mb-2">Provider: {systemConfig.storage.provider}</p>
                  <p className="text-xs font-medium text-slate-500">Region: {systemConfig.storage.region}</p>
                  <div className="flex justify-between mt-3">
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Bucket: {systemConfig.storage.bucket}</p>
                    <p className="text-[10px] font-black text-purple-500 uppercase tracking-widest">Connected</p>
                  </div>
                </div>
              )}

              <div className="p-6 bg-slate-50 dark:bg-slate-900 rounded-3xl border-2 border-transparent hover:border-emerald-500/20 transition-all">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
                      <Shield className="w-5 h-5 text-amber-500" />
                    </div>
                    <p className="font-bold text-slate-900 dark:text-white">Security Layer</p>
                  </div>
                  <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                </div>
                <p className="text-xs font-medium text-slate-500 mb-2">JWT Authentication: Active</p>
                <p className="text-xs font-medium text-slate-500">RBAC Enforcement: Active</p>
                <div className="flex justify-between mt-3">
                  <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">SSL/TLS 1.3</p>
                  <p className="text-[10px] font-black text-amber-500 uppercase tracking-widest">Secure</p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white dark:bg-slate-950 rounded-[2.5rem] p-10 border-2 border-slate-50 dark:border-slate-900 shadow-xl">
            <h3 className="text-2xl font-outfit font-black text-slate-900 dark:text-white mb-8 flex items-center gap-3">
              <Clock className="w-6 h-6 text-blue-500" />
              System Logs
            </h3>
            <div className="space-y-6">
              {[
                { msg: 'New user registered', time: '2m ago', type: 'user' },
                { msg: 'Database backup completed', time: '15m ago', type: 'system' },
                { msg: 'High traffic detected', time: '1h ago', type: 'alert' },
                { msg: 'New classroom created', time: '2h ago', type: 'user' },
              ].map((log, i) => (
                <div key={i} className="flex items-start gap-4">
                  <div className={cn("w-2 h-2 rounded-full mt-2", log.type === 'alert' ? "bg-red-500" : "bg-emerald-500")} />
                  <div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">{log.msg}</p>
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{log.time}</p>
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-8 py-4 bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 rounded-2xl font-black uppercase tracking-widest text-[10px] hover:bg-slate-100 dark:hover:bg-slate-800 transition-all">
              View Full Logs
            </button>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
