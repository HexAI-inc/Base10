'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { useTheme } from '@/components/ThemeProvider'
import AppLayout from '@/components/AppLayout'
import { 
  Settings as SettingsIcon, Bell, Shield, Moon, Sun, Globe, 
  Volume2, Download, Smartphone, Lock, Eye, EyeOff, Save,
  Check, X, Loader2, Monitor, ChevronRight, Sparkles,
  Zap, Database, Languages, HelpCircle
} from 'lucide-react'
import { cn } from '@/lib/utils'

export default function SettingsPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const { theme, setTheme } = useTheme()
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('general')

  // Settings state
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    sms: false,
    daily_reminder: true,
    weekly_progress: true,
    exam_alerts: true,
  })

  const [privacy, setPrivacy] = useState({
    profile_visibility: 'public',
    show_progress: true,
    show_on_leaderboard: true,
    allow_friend_requests: true,
  })

  const [preferences, setPreferences] = useState({
    theme: theme,
    language: 'en',
    data_saver: false,
    auto_play_audio: false,
    show_hints: true,
    difficulty: 'mixed',
  })

  useEffect(() => {
    setPreferences(prev => ({ ...prev, theme }))
  }, [theme])

  useEffect(() => {
    if (!user) {
      router.push('/login')
    }
  }, [user, router])

  const handleSave = async () => {
    setSaving(true)
    setSuccess(null)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSuccess('Settings saved successfully!')
    setSaving(false)
    setTimeout(() => setSuccess(null), 3000)
  }

  const Toggle = ({ enabled, onChange, label, icon: Icon }: any) => (
    <div 
      onClick={() => onChange(!enabled)}
      className="flex items-center justify-between p-4 sm:p-6 bg-slate-50 dark:bg-slate-900/50 rounded-xl sm:rounded-2xl border-2 border-transparent hover:border-emerald-500/20 transition-all cursor-pointer group"
    >
      <div className="flex items-center gap-3 sm:gap-4">
        <div className={cn(
          "w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl flex items-center justify-center transition-all",
          enabled ? "bg-emerald-500/10 text-emerald-600" : "bg-slate-200 dark:bg-slate-800 text-slate-400"
        )}>
          <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
        </div>
        <span className="text-xs sm:text-sm font-bold text-slate-700 dark:text-slate-300">{label}</span>
      </div>
      <div className={cn(
        "w-12 h-6 sm:w-14 sm:h-7 rounded-full p-1 transition-all duration-500",
        enabled ? "bg-emerald-500" : "bg-slate-300 dark:bg-slate-700"
      )}>
        <div className={cn(
          "w-4 h-4 sm:w-5 sm:h-5 bg-white rounded-full shadow-sm transition-all duration-500",
          enabled ? "translate-x-6 sm:translate-x-7" : "translate-x-0"
        )} />
      </div>
    </div>
  )

  if (!user) return null

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-12">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 sm:gap-8 mb-8 sm:mb-12">
          <div>
            <div className="flex items-center gap-3 mb-2 sm:mb-4">
              <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                <SettingsIcon className="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" />
              </div>
              <h1 className="text-2xl sm:text-4xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">
                Settings
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 font-medium">
              Personalize your learning experience and account security
            </p>
          </div>

          <button 
            onClick={handleSave}
            disabled={saving}
            className="h-12 sm:h-14 px-6 sm:px-8 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl sm:rounded-2xl font-outfit font-black text-[10px] sm:text-xs uppercase tracking-[0.2em] flex items-center justify-center gap-2 sm:gap-3 shadow-xl hover:scale-105 transition-all disabled:opacity-50"
          >
            {saving ? <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" /> : <Save className="w-4 h-4 sm:w-5 sm:h-5" />}
            Save Changes
          </button>
        </div>

        {success && (
          <div className="mb-6 sm:mb-8 bg-emerald-500/10 border-2 border-emerald-500/20 rounded-xl sm:rounded-2xl p-4 sm:p-6 flex items-center gap-3 sm:gap-4 animate-in fade-in slide-in-from-top-4">
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500 flex items-center justify-center text-white">
              <Check className="w-4 h-4 sm:w-6 sm:h-6" />
            </div>
            <p className="text-xs sm:text-sm text-emerald-700 dark:text-emerald-400 font-bold">{success}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 sm:gap-12">
          {/* Sidebar Navigation */}
          <div className="flex lg:flex-col gap-2 overflow-x-auto pb-4 lg:pb-0 no-scrollbar">
            {[
              { id: 'general', label: 'General', icon: Monitor },
              { id: 'notifications', label: 'Notifications', icon: Bell },
              { id: 'privacy', label: 'Privacy', icon: Shield },
              { id: 'data', label: 'Data', icon: Database },
              { id: 'help', label: 'Help', icon: HelpCircle },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex-shrink-0 lg:w-full h-12 sm:h-14 px-4 sm:px-6 rounded-xl sm:rounded-2xl flex items-center gap-3 sm:gap-4 transition-all font-bold text-xs sm:text-sm whitespace-nowrap",
                  activeTab === tab.id 
                    ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/20" 
                    : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900"
                )}
              >
                <tab.icon className="w-4 h-4 sm:w-5 sm:h-5" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Content Area */}
          <div className="lg:col-span-3 space-y-8 sm:space-y-12">
            {activeTab === 'general' && (
              <div className="space-y-8 sm:space-y-12 animate-in fade-in slide-in-from-right-4">
                {/* Appearance */}
                <section>
                  <h3 className="text-lg sm:text-xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-6 sm:mb-8 tracking-tight">Appearance</h3>
                  <div className="grid grid-cols-3 gap-3 sm:gap-6">
                    {[
                      { id: 'light', label: 'Light', icon: Sun },
                      { id: 'dark', label: 'Dark', icon: Moon },
                      { id: 'system', label: 'System', icon: Monitor },
                    ].map((mode) => (
                      <button
                        key={mode.id}
                        onClick={() => setTheme(mode.id as any)}
                        className={cn(
                          "p-4 sm:p-8 rounded-[1.5rem] sm:rounded-[2rem] border-2 transition-all flex flex-col items-center gap-2 sm:gap-4",
                          theme === mode.id 
                            ? "border-emerald-500 bg-emerald-500/5" 
                            : "border-slate-100 dark:border-slate-900 bg-white dark:bg-slate-950"
                        )}
                      >
                        <div className={cn(
                          "w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl flex items-center justify-center",
                          theme === mode.id ? "bg-emerald-500 text-white" : "bg-slate-100 dark:bg-slate-900 text-slate-400"
                        )}>
                          <mode.icon className="w-5 h-5 sm:w-6 sm:h-6" />
                        </div>
                        <span className={cn(
                          "text-[8px] sm:text-[10px] font-black uppercase tracking-widest text-center",
                          theme === mode.id ? "text-emerald-600" : "text-slate-400"
                        )}>{mode.label}</span>
                      </button>
                    ))}
                  </div>
                </section>

                {/* Language */}
                <section>
                  <h3 className="text-lg sm:text-xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-6 sm:mb-8 tracking-tight">Language & Region</h3>
                  <div className="bg-white dark:bg-slate-950 p-6 sm:p-8 rounded-[2rem] sm:rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-600">
                          <Languages className="w-5 h-5 sm:w-6 sm:h-6" />
                        </div>
                        <div>
                          <p className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100">Display Language</p>
                          <p className="text-[10px] sm:text-xs text-slate-500">Choose your preferred language</p>
                        </div>
                      </div>
                      <select className="w-full sm:w-auto bg-slate-50 dark:bg-slate-900 border-2 border-slate-100 dark:border-slate-800 rounded-xl px-4 py-2 font-bold text-xs sm:text-sm outline-none focus:border-emerald-500/50">
                        <option value="en">English (UK)</option>
                        <option value="fr">Français</option>
                        <option value="yo">Yoruba</option>
                        <option value="ha">Hausa</option>
                        <option value="ig">Igbo</option>
                      </select>
                    </div>
                  </div>
                </section>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6 sm:space-y-8 animate-in fade-in slide-in-from-right-4">
                <h3 className="text-lg sm:text-xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-2 sm:mb-4 tracking-tight">Notification Preferences</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                  <Toggle 
                    label="Email Notifications" 
                    enabled={notifications.email} 
                    onChange={(v: boolean) => setNotifications({...notifications, email: v})}
                    icon={Bell}
                  />
                  <Toggle 
                    label="Push Notifications" 
                    enabled={notifications.push} 
                    onChange={(v: boolean) => setNotifications({...notifications, push: v})}
                    icon={Smartphone}
                  />
                  <Toggle 
                    label="Daily Reminders" 
                    enabled={notifications.daily_reminder} 
                    onChange={(v: boolean) => setNotifications({...notifications, daily_reminder: v})}
                    icon={Zap}
                  />
                  <Toggle 
                    label="Exam Alerts" 
                    enabled={notifications.exam_alerts} 
                    onChange={(v: boolean) => setNotifications({...notifications, exam_alerts: v})}
                    icon={Sparkles}
                  />
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="space-y-6 sm:space-y-8 animate-in fade-in slide-in-from-right-4">
                <h3 className="text-lg sm:text-xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-2 sm:mb-4 tracking-tight">Privacy & Security</h3>
                <div className="bg-white dark:bg-slate-950 p-6 sm:p-8 rounded-[2rem] sm:rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 space-y-6 sm:space-y-8">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-600">
                        <Lock className="w-5 h-5 sm:w-6 sm:h-6" />
                      </div>
                      <div>
                        <p className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100">Two-Factor Authentication</p>
                        <p className="text-[10px] sm:text-xs text-slate-500">Add an extra layer of security to your account</p>
                      </div>
                    </div>
                    <button className="w-full sm:w-auto px-6 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl font-black text-[10px] uppercase tracking-widest">Enable</button>
                  </div>
                  
                  <div className="h-px bg-slate-100 dark:bg-slate-900" />
                  
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl bg-amber-500/10 flex items-center justify-center text-amber-600">
                        <Eye className="w-5 h-5 sm:w-6 sm:h-6" />
                      </div>
                      <div>
                        <p className="text-xs sm:text-sm font-bold text-slate-900 dark:text-slate-100">Profile Visibility</p>
                        <p className="text-[10px] sm:text-xs text-slate-500">Control who can see your learning progress</p>
                      </div>
                    </div>
                    <select className="w-full sm:w-auto bg-slate-50 dark:bg-slate-900 border-2 border-slate-100 dark:border-slate-800 rounded-xl px-4 py-2 font-bold text-xs sm:text-sm outline-none">
                      <option value="public">Public</option>
                      <option value="friends">Friends Only</option>
                      <option value="private">Private</option>
                    </select>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
