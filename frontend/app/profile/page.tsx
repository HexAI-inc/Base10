'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/lib/api'
import { 
  User, Mail, Phone, MapPin, Globe, Book, Clock, Bell, 
  Shield, Trophy, Star, Camera, Loader2, Save, Edit2,
  Sparkles, ChevronRight, Target, Zap, CheckCircle2,
  Calendar, Plus
} from 'lucide-react'
import AppLayout from '@/components/AppLayout'
import CalendarPicker from '@/components/CalendarPicker'
import AIQuotaIndicator from '@/components/AIQuotaIndicator'
import { cn } from '@/lib/utils'

interface ProfileData {
  id: number
  phone_number: string
  email: string
  full_name: string
  avatar_url?: string
  bio?: string
  country?: string
  location?: string
  education_level?: string
  learning_style?: string
  study_time_preference?: string
  target_exam_date?: string
  preferred_subjects?: string[]
  notification_settings?: {
    email_enabled: boolean
    sms_enabled: boolean
    push_enabled: boolean
    daily_reminder: boolean
    weekly_progress: boolean
    exam_countdown: boolean
    achievement_alerts: boolean
  }
  privacy_settings?: {
    show_profile: boolean
    show_progress: boolean
    show_in_leaderboard: boolean
    allow_classmate_comparison: boolean
  }
  achievement_badges?: any[]
  total_points: number
  level: number
  profile_completion_percentage: number
  study_streak: number
  is_verified: boolean
  created_at: string
}

export default function ProfilePage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [profile, setProfile] = useState<ProfileData | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editData, setEditData] = useState<Partial<ProfileData>>({})
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }
    fetchProfile()
  }, [user, router])

  const fetchProfile = async () => {
    try {
      const response = await authApi.getProfile()
      setProfile(response.data)
      setEditData(response.data)
    } catch (err) {
      console.error('Failed to load profile:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    setSuccess(null)
    try {
      await authApi.updateProfile(editData)
      await fetchProfile()
      setEditing(false)
      setSuccess('Profile updated successfully!')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err: any) {
      setError('Failed to update profile. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="min-h-[80vh] flex flex-col items-center justify-center">
          <div className="relative w-24 h-24 mb-8">
            <div className="absolute inset-0 border-4 border-emerald-500/10 rounded-[2rem] animate-pulse" />
            <div className="absolute inset-0 border-4 border-emerald-500 border-t-transparent rounded-[2rem] animate-spin" />
            <User className="absolute inset-0 m-auto w-10 h-10 text-emerald-500" />
          </div>
          <p className="text-slate-900 dark:text-slate-100 font-outfit font-black text-xl tracking-tight">Loading Profile</p>
          <p className="text-slate-400 dark:text-slate-600 font-bold text-xs uppercase tracking-[0.3em] mt-2">Retrieving your data...</p>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-12">
        {/* Profile Header Card */}
        <div className="bg-white dark:bg-slate-950 rounded-[2rem] sm:rounded-[3rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm overflow-hidden mb-8 sm:mb-12 relative">
          <div className="h-32 sm:h-48 bg-slate-900 dark:bg-emerald-600 relative overflow-hidden">
            <div className="absolute inset-0 opacity-20">
              <div className="absolute top-0 left-0 w-48 sm:w-64 h-48 sm:h-64 bg-white rounded-full -ml-24 sm:-ml-32 -mt-24 sm:-mt-32 blur-3xl" />
              <div className="absolute bottom-0 right-0 w-64 sm:w-96 h-64 sm:h-96 bg-white rounded-full -mr-32 sm:-mr-48 -mb-32 sm:-mb-48 blur-3xl" />
            </div>
          </div>
          
          <div className="px-6 sm:px-12 pb-8 sm:pb-12 relative">
            <div className="flex flex-col md:flex-row md:items-end gap-6 sm:gap-8 -mt-12 sm:-mt-20 mb-6 sm:mb-8">
              <div className="relative group self-center md:self-auto">
                <div className="w-32 h-32 sm:w-40 sm:h-40 rounded-[2rem] sm:rounded-[2.5rem] bg-white dark:bg-slate-950 p-1.5 sm:p-2 shadow-2xl">
                  <div className="w-full h-full rounded-[1.5rem] sm:rounded-[2rem] bg-slate-100 dark:bg-slate-900 flex items-center justify-center text-4xl sm:text-5xl font-black text-slate-400 overflow-hidden">
                    {profile?.avatar_url ? (
                      <img src={profile.avatar_url} alt="" className="w-full h-full object-cover" />
                    ) : (
                      profile?.full_name?.[0] || 'U'
                    )}
                  </div>
                </div>
                <button className="absolute bottom-1 right-1 sm:bottom-2 sm:right-2 w-10 h-10 sm:w-12 sm:h-12 bg-emerald-600 text-white rounded-xl sm:rounded-2xl shadow-xl flex items-center justify-center hover:scale-110 transition-all">
                  <Camera className="w-5 h-5 sm:w-6 sm:h-6" />
                </button>
              </div>
              
              <div className="flex-1 text-center md:text-left">
                <div className="flex flex-col md:flex-row items-center gap-2 sm:gap-4 mb-2">
                  <h1 className="text-2xl sm:text-4xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">
                    {profile?.full_name}
                  </h1>
                  {profile?.is_verified && (
                    <div className="w-6 h-6 sm:w-8 sm:h-8 rounded-lg sm:rounded-xl bg-emerald-500/10 flex items-center justify-center">
                      <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-500" />
                    </div>
                  )}
                </div>
                <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 sm:gap-6">
                  <div className="flex items-center gap-1.5 sm:gap-2 text-slate-400 dark:text-slate-600">
                    <Mail className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    <span className="text-xs sm:text-sm font-bold">{profile?.email}</span>
                  </div>
                  <div className="flex items-center gap-1.5 sm:gap-2 text-slate-400 dark:text-slate-600">
                    <MapPin className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    <span className="text-xs sm:text-sm font-bold">{profile?.location || 'Sierra Leone'}</span>
                  </div>
                  <div className="px-2 sm:px-3 py-0.5 sm:py-1 bg-emerald-500/10 border-2 border-emerald-500/20 rounded-full">
                    <span className="text-[8px] sm:text-[10px] font-black text-emerald-700 dark:text-emerald-400 uppercase tracking-widest">Level {profile?.level}</span>
                  </div>
                </div>
              </div>
              
              <button 
                onClick={() => editing ? handleSave() : setEditing(true)}
                disabled={saving}
                className={cn(
                  "h-12 sm:h-14 px-6 sm:px-8 rounded-xl sm:rounded-2xl font-outfit font-black text-[10px] sm:text-xs uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-2 sm:gap-3 shadow-xl",
                  editing 
                    ? "bg-emerald-600 text-white shadow-emerald-600/20" 
                    : "bg-slate-900 dark:bg-white text-white dark:text-slate-900"
                )}
              >
                {saving ? <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" /> : editing ? <Save className="w-4 h-4 sm:w-5 sm:h-5" /> : <Edit2 className="w-4 h-4 sm:w-5 sm:h-5" />}
                {editing ? 'Save' : 'Edit Profile'}
              </button>
            </div>
            
            {/* Profile Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
              {[
                { label: 'Points', value: profile?.total_points, icon: Trophy, color: 'text-amber-500', bg: 'bg-amber-500/10' },
                { label: 'Streak', value: `${profile?.study_streak}d`, icon: Zap, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
                { label: 'Progress', value: `${profile?.profile_completion_percentage}%`, icon: Target, color: 'text-blue-500', bg: 'bg-blue-500/10' },
                { label: 'Badges', value: profile?.achievement_badges?.length || 0, icon: Star, color: 'text-purple-500', bg: 'bg-purple-500/10' },
              ].map((stat, i) => (
                <div key={i} className="bg-slate-50 dark:bg-slate-900/50 p-4 sm:p-6 rounded-[1.5rem] sm:rounded-[2rem] border-2 border-slate-100 dark:border-slate-800">
                  <div className={cn("w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl flex items-center justify-center mb-3 sm:mb-4", stat.bg)}>
                    <stat.icon className={cn("w-5 h-5 sm:w-6 sm:h-6", stat.color)} />
                  </div>
                  <p className="text-[8px] sm:text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-widest mb-0.5 sm:mb-1">{stat.label}</p>
                  <p className="text-lg sm:text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">{stat.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 sm:gap-12">
          {/* Main Settings */}
          <div className="lg:col-span-2 space-y-8 sm:space-y-12">
            {/* Personal Info */}
            <section>
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 flex items-center justify-center">
                  <User className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-600" />
                </div>
                <h2 className="text-xl sm:text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Personal Info</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-8">
                <div className="space-y-1.5 sm:space-y-2">
                  <label className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest ml-3 sm:ml-4">Full Name</label>
                  <input 
                    type="text" 
                    disabled={!editing}
                    value={editData.full_name || ''}
                    onChange={(e) => setEditData({...editData, full_name: e.target.value})}
                    className="w-full h-12 sm:h-16 px-6 sm:px-8 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-900 rounded-xl sm:rounded-2xl font-medium text-sm sm:text-base focus:border-emerald-500/50 outline-none transition-all dark:text-white disabled:opacity-50"
                  />
                </div>
                <div className="space-y-1.5 sm:space-y-2">
                  <label className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest ml-3 sm:ml-4">Phone</label>
                  <input 
                    type="text" 
                    disabled={!editing}
                    value={editData.phone_number || ''}
                    onChange={(e) => setEditData({...editData, phone_number: e.target.value})}
                    className="w-full h-12 sm:h-16 px-6 sm:px-8 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-900 rounded-xl sm:rounded-2xl font-medium text-sm sm:text-base focus:border-emerald-500/50 outline-none transition-all dark:text-white disabled:opacity-50"
                  />
                </div>
                <div className="md:col-span-2 space-y-1.5 sm:space-y-2">
                  <label className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest ml-3 sm:ml-4">Bio</label>
                  <textarea 
                    disabled={!editing}
                    value={editData.bio || ''}
                    onChange={(e) => setEditData({...editData, bio: e.target.value})}
                    className="w-full h-24 sm:h-32 p-6 sm:p-8 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-900 rounded-[1.5rem] sm:rounded-[2rem] font-medium text-sm sm:text-base focus:border-emerald-500/50 outline-none transition-all dark:text-white disabled:opacity-50 resize-none"
                  />
                </div>
              </div>
            </section>

            {/* Education Settings */}
            <section>
              <div className="flex items-center gap-3 mb-6 sm:mb-8">
                <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 flex items-center justify-center">
                  <Book className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
                </div>
                <h2 className="text-xl sm:text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Education & Learning</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-8">
                <div className="space-y-1.5 sm:space-y-2">
                  <label className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest ml-3 sm:ml-4">Education Level</label>
                  <select 
                    disabled={!editing}
                    value={editData.education_level || ''}
                    onChange={(e) => setEditData({...editData, education_level: e.target.value})}
                    className="w-full h-12 sm:h-16 px-6 sm:px-8 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-900 rounded-xl sm:rounded-2xl font-medium text-sm sm:text-base focus:border-emerald-500/50 outline-none transition-all dark:text-white disabled:opacity-50 appearance-none"
                  >
                    <option value="SSS1">SSS 1</option>
                    <option value="SSS2">SSS 2</option>
                    <option value="SSS3">SSS 3 / WASSCE Candidate</option>
                    <option value="Graduate">Graduate</option>
                  </select>
                </div>
                <div className="space-y-1.5 sm:space-y-2">
                  <label className="text-[8px] sm:text-[10px] font-black text-slate-400 uppercase tracking-widest ml-3 sm:ml-4">Learning Style</label>
                  <select 
                    disabled={!editing}
                    value={editData.learning_style || ''}
                    onChange={(e) => setEditData({...editData, learning_style: e.target.value})}
                    className="w-full h-12 sm:h-16 px-6 sm:px-8 bg-white dark:bg-slate-950 border-2 border-slate-100 dark:border-slate-900 rounded-xl sm:rounded-2xl font-medium text-sm sm:text-base focus:border-emerald-500/50 outline-none transition-all dark:text-white disabled:opacity-50 appearance-none"
                  >
                    <option value="Visual">Visual Learner</option>
                    <option value="Auditory">Auditory Learner</option>
                    <option value="Reading">Reading/Writing</option>
                    <option value="Kinesthetic">Kinesthetic Learner</option>
                  </select>
                </div>
              </div>
            </section>
          </div>

          {/* Sidebar Settings */}
          <div className="space-y-8 sm:space-y-12">
            {/* AI Quota */}
            <AIQuotaIndicator />

            {/* Exam Countdown */}
            <div className="bg-slate-900 dark:bg-emerald-600 p-6 sm:p-8 rounded-[2rem] sm:rounded-[2.5rem] text-white shadow-2xl shadow-emerald-600/20 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 blur-2xl group-hover:scale-150 transition-transform duration-700" />
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-6 sm:mb-8">
                  <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-white/10 flex items-center justify-center">
                    <Calendar className="w-5 h-5 sm:w-6 sm:h-6" />
                  </div>
                  <div>
                    <p className="text-[8px] sm:text-[10px] font-black text-white/60 uppercase tracking-widest">WASSCE 2025</p>
                    <h4 className="text-lg sm:text-xl font-outfit font-black tracking-tight">Exam Countdown</h4>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-3 sm:gap-4 mb-6 sm:mb-8">
                  {[
                    { label: 'Days', value: '142' },
                    { label: 'Hrs', value: '08' },
                    { label: 'Min', value: '45' },
                  ].map((time, i) => (
                    <div key={i} className="bg-white/10 rounded-xl sm:rounded-2xl p-3 sm:p-4 text-center">
                      <p className="text-lg sm:text-2xl font-outfit font-black">{time.value}</p>
                      <p className="text-[8px] sm:text-[10px] font-black text-white/40 uppercase tracking-widest">{time.label}</p>
                    </div>
                  ))}
                </div>
                
                <button className="w-full h-12 sm:h-14 bg-white text-slate-900 rounded-xl sm:rounded-2xl font-outfit font-black text-[10px] sm:text-xs uppercase tracking-widest hover:scale-[1.02] transition-all">
                  Set Study Goal
                </button>
              </div>
            </div>

            {/* Achievements */}
            <section>
              <div className="flex items-center justify-between mb-6 sm:mb-8">
                <h3 className="text-lg sm:text-xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">Achievements</h3>
                <span className="text-[8px] sm:text-[10px] font-black text-emerald-600 uppercase tracking-widest">View All</span>
              </div>
              
              <div className="grid grid-cols-3 gap-3 sm:gap-4">
                {profile?.achievement_badges?.map((badge: any, i: number) => (
                  <div key={i} className="aspect-square rounded-xl sm:rounded-2xl bg-slate-50 dark:bg-slate-900 border-2 border-slate-100 dark:border-slate-800 flex items-center justify-center group cursor-pointer hover:border-emerald-500/30 transition-all">
                    <div className="w-8 h-8 sm:w-12 sm:h-12 rounded-full bg-emerald-500/10 flex items-center justify-center group-hover:scale-110 transition-all">
                      <Star className="w-4 h-4 sm:w-6 sm:h-6 text-emerald-600" />
                    </div>
                  </div>
                ))}
                <div className="aspect-square rounded-xl sm:rounded-2xl border-2 border-dashed border-slate-200 dark:border-slate-800 flex items-center justify-center">
                  <Plus className="w-5 h-5 sm:w-6 sm:h-6 text-slate-300" />
                </div>
              </div>
            </section>
          </div>

          {/* Sidebar Settings */}
          <div className="space-y-12">
            {/* Exam Countdown */}
            <div className="bg-slate-900 dark:bg-emerald-600 p-8 rounded-[2.5rem] text-white shadow-2xl shadow-emerald-600/20 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 blur-2xl group-hover:scale-150 transition-transform duration-700" />
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-8">
                  <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-xl flex items-center justify-center">
                    <Clock className="w-6 h-6 text-white" />
                  </div>
                  <p className="text-[10px] font-black uppercase tracking-[0.3em]">WASSCE Countdown</p>
                </div>
                
                <div className="flex items-end gap-4 mb-6">
                  <span className="text-6xl font-outfit font-black leading-none">42</span>
                  <div className="mb-2">
                    <p className="text-xs font-black uppercase tracking-widest opacity-60">Days</p>
                    <p className="text-sm font-bold">Remaining</p>
                  </div>
                </div>
                
                <p className="text-sm font-medium leading-relaxed opacity-80 mb-8">
                  Your target exam date is set for <span className="font-bold">May 15, 2024</span>. Stay focused!
                </p>
                
                <button className="w-full h-14 bg-white text-slate-900 rounded-2xl font-outfit font-black text-xs uppercase tracking-[0.2em] hover:bg-emerald-50 transition-colors">
                  Update Target Date
                </button>
              </div>
            </div>

            {/* Quick Settings */}
            <div className="bg-white dark:bg-slate-950 p-8 rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm">
              <h3 className="text-lg font-outfit font-black text-slate-900 dark:text-slate-100 mb-8 tracking-tight">Quick Settings</h3>
              <div className="space-y-6">
                {[
                  { label: 'Email Notifications', icon: Bell, enabled: profile?.notification_settings?.email_enabled },
                  { label: 'Public Profile', icon: Globe, enabled: profile?.privacy_settings?.show_profile },
                  { label: 'Leaderboard Visibility', icon: Trophy, enabled: profile?.privacy_settings?.show_in_leaderboard },
                  { label: 'Two-Factor Auth', icon: Shield, enabled: true },
                ].map((setting, i) => (
                  <div key={i} className="flex items-center justify-between group cursor-pointer">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-xl bg-slate-50 dark:bg-slate-900 flex items-center justify-center text-slate-400 group-hover:text-emerald-500 transition-colors">
                        <setting.icon className="w-5 h-5" />
                      </div>
                      <span className="text-sm font-bold text-slate-600 dark:text-slate-400">{setting.label}</span>
                    </div>
                    <div className={cn(
                      "w-12 h-6 rounded-full p-1 transition-all duration-500",
                      setting.enabled ? "bg-emerald-500" : "bg-slate-200 dark:bg-slate-800"
                    )}>
                      <div className={cn(
                        "w-4 h-4 bg-white rounded-full transition-all duration-500",
                        setting.enabled ? "translate-x-6" : "translate-x-0"
                      )} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
