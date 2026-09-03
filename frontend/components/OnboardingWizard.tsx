'use client'
import { useState, useEffect } from 'react'
import { onboardingApi } from '@/lib/api'
import { useAuthStore } from '@/store/authStore'
import { useModalStore } from '@/store/modalStore'
import { 
  Brain, Sparkles, BookOpen, Target, Clock, 
  ChevronRight, ChevronLeft, Check, Loader2,
  GraduationCap, School, Award, X
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface OnboardingWizardProps {
  onClose?: () => void
}

export default function OnboardingWizard({ onClose }: OnboardingWizardProps) {
  const { user, setUser } = useAuthStore()
  const { showSuccess, showError } = useModalStore()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)

  // Lock body scroll when onboarding is open
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [])

  // Student State
  const [studentData, setStudentData] = useState({
    education_level: 'SSS3',
    preferred_subjects: [] as string[],
    target_exam_date: new Date(new Date().getFullYear(), 5, 15).toISOString(),
    learning_style: 'visual',
    study_time_preference: 'morning'
  })

  // Teacher State
  const [teacherData, setTeacherData] = useState({
    bio: '',
    subjects_taught: [] as string[],
    first_classroom_name: '',
    first_classroom_subject: 'Mathematics',
    first_classroom_grade: 'SSS3'
  })

  const subjects = [
    'Mathematics', 'English', 'Physics', 'Chemistry', 
    'Biology', 'Economics', 'Government', 'Literature'
  ]

  const handleStudentSubmit = async () => {
    if (studentData.preferred_subjects.length === 0) {
      showError('Please select at least one subject', 'Missing Info')
      return
    }
    setLoading(true)
    try {
      const res = await onboardingApi.completeStudent(studentData)
      setUser(res.data)
      showSuccess('Welcome to Base10! You earned 50 points and the Welcome Pioneer badge.', 'Onboarding Complete')
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Failed to complete onboarding')
    } finally {
      setLoading(false)
    }
  }

  const handleTeacherSubmit = async () => {
    if (!teacherData.bio || !teacherData.first_classroom_name) {
      showError('Please fill in all required fields', 'Missing Info')
      return
    }
    setLoading(true)
    try {
      const res = await onboardingApi.completeTeacher(teacherData)
      setUser(res.data)
      showSuccess('Welcome Educator! Your first classroom is ready.', 'Onboarding Complete')
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Failed to complete onboarding')
    } finally {
      setLoading(false)
    }
  }

  const renderStudentStep = () => {
    switch(step) {
      case 1:
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500 flex items-center justify-center text-white shadow-xl shadow-emerald-500/20 mx-auto mb-6">
                <GraduationCap className="w-8 h-8" />
              </div>
              <h2 className="text-3xl font-outfit font-black text-slate-900 dark:text-white tracking-tight mb-2">Your Education</h2>
              <p className="text-slate-500 dark:text-slate-400">Tell us about your current level</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {['JSS3', 'SSS1', 'SSS2', 'SSS3'].map((level) => (
                <button
                  key={level}
                  onClick={() => setStudentData({...studentData, education_level: level})}
                  className={cn(
                    "h-20 rounded-2xl border-2 transition-all font-black uppercase tracking-widest text-sm",
                    studentData.education_level === level 
                      ? "bg-emerald-600 border-emerald-600 text-white shadow-lg shadow-emerald-600/20"
                      : "bg-white dark:bg-slate-900 border-slate-100 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-emerald-500/50"
                  )}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>
        )
      case 2:
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-blue-500 flex items-center justify-center text-white shadow-xl shadow-blue-500/20 mx-auto mb-6">
                <BookOpen className="w-8 h-8" />
              </div>
              <h2 className="text-3xl font-outfit font-black text-slate-900 dark:text-white tracking-tight mb-2">Your Subjects</h2>
              <p className="text-slate-500 dark:text-slate-400">Select the subjects you want to focus on</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {subjects.map((subject) => {
                const isSelected = studentData.preferred_subjects.includes(subject)
                return (
                  <button
                    key={subject}
                    onClick={() => {
                      const newSubjects = isSelected 
                        ? studentData.preferred_subjects.filter(s => s !== subject)
                        : [...studentData.preferred_subjects, subject]
                      setStudentData({...studentData, preferred_subjects: newSubjects})
                    }}
                    className={cn(
                      "h-14 px-4 rounded-xl border-2 transition-all font-bold text-xs flex items-center justify-between",
                      isSelected 
                        ? "bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-600/20"
                        : "bg-white dark:bg-slate-900 border-slate-100 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-blue-500/50"
                    )}
                  >
                    {subject}
                    {isSelected && <Check className="w-4 h-4" />}
                  </button>
                )
              })}
            </div>
          </div>
        )
      case 3:
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-purple-500 flex items-center justify-center text-white shadow-xl shadow-purple-500/20 mx-auto mb-6">
                <Sparkles className="w-8 h-8" />
              </div>
              <h2 className="text-3xl font-outfit font-black text-slate-900 dark:text-white tracking-tight mb-2">Learning Style</h2>
              <p className="text-slate-500 dark:text-slate-400">How do you learn best?</p>
            </div>
            <div className="space-y-3">
              {[
                { id: 'visual', label: 'Visual (Images & Videos)', icon: '👁️' },
                { id: 'auditory', label: 'Auditory (Listening)', icon: '👂' },
                { id: 'reading', label: 'Reading & Writing', icon: '📖' },
                { id: 'kinesthetic', label: 'Kinesthetic (Doing)', icon: '✋' }
              ].map((style) => (
                <button
                  key={style.id}
                  onClick={() => setStudentData({...studentData, learning_style: style.id})}
                  className={cn(
                    "w-full h-16 px-6 rounded-2xl border-2 transition-all font-bold flex items-center gap-4",
                    studentData.learning_style === style.id 
                      ? "bg-purple-600 border-purple-600 text-white shadow-lg shadow-purple-600/20"
                      : "bg-white dark:bg-slate-900 border-slate-100 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-purple-500/50"
                  )}
                >
                  <span className="text-xl">{style.icon}</span>
                  {style.label}
                </button>
              ))}
            </div>
          </div>
        )
      default: return null
    }
  }

  const renderTeacherStep = () => {
    switch(step) {
      case 1:
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500 flex items-center justify-center text-white shadow-xl shadow-emerald-500/20 mx-auto mb-6">
                <School className="w-8 h-8" />
              </div>
              <h2 className="text-3xl font-outfit font-black text-slate-900 dark:text-white tracking-tight mb-2">Teacher Profile</h2>
              <p className="text-slate-500 dark:text-slate-400">Tell your students about yourself</p>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Professional Bio</label>
                <textarea
                  value={teacherData.bio}
                  onChange={(e) => setTeacherData({...teacherData, bio: e.target.value})}
                  className="w-full h-32 p-6 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-emerald-500/50 rounded-2xl outline-none text-slate-900 dark:text-slate-100 font-medium transition-all resize-none"
                  placeholder="e.g. Senior Mathematics Lead with 10 years experience..."
                />
              </div>
            </div>
          </div>
        )
      case 2:
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-blue-500 flex items-center justify-center text-white shadow-xl shadow-blue-500/20 mx-auto mb-6">
                <Brain className="w-8 h-8" />
              </div>
              <h2 className="text-3xl font-outfit font-black text-slate-900 dark:text-white tracking-tight mb-2">First Classroom</h2>
              <p className="text-slate-500 dark:text-slate-400">Let's set up your first learning space</p>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Classroom Name</label>
                <input
                  type="text"
                  value={teacherData.first_classroom_name}
                  onChange={(e) => setTeacherData({...teacherData, first_classroom_name: e.target.value})}
                  className="w-full h-16 px-6 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-blue-500/50 rounded-2xl outline-none text-slate-900 dark:text-slate-100 font-bold transition-all"
                  placeholder="e.g. Grade 9 Alpha"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Subject</label>
                  <select
                    value={teacherData.first_classroom_subject}
                    onChange={(e) => setTeacherData({...teacherData, first_classroom_subject: e.target.value})}
                    className="w-full h-16 px-6 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-blue-500/50 rounded-2xl outline-none text-slate-900 dark:text-slate-100 font-bold transition-all appearance-none"
                  >
                    {subjects.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-4">Grade</label>
                  <select
                    value={teacherData.first_classroom_grade}
                    onChange={(e) => setTeacherData({...teacherData, first_classroom_grade: e.target.value})}
                    className="w-full h-16 px-6 bg-slate-50 dark:bg-slate-900 border-2 border-transparent focus:border-blue-500/50 rounded-2xl outline-none text-slate-900 dark:text-slate-100 font-bold transition-all appearance-none"
                  >
                    {['JSS3', 'SSS1', 'SSS2', 'SSS3'].map(g => <option key={g} value={g}>{g}</option>)}
                  </select>
                </div>
              </div>
            </div>
          </div>
        )
      default: return null
    }
  }

  const isStudent = user?.role === 'student'
  const totalSteps = isStudent ? 3 : 2

  return (
    <div className="fixed inset-0 z-[100] bg-[#0F172A] flex items-center justify-center p-6 overflow-y-auto">
      {/* Background Effects */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-500/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px]" />

      <div className="max-w-xl w-full relative z-10">
        <div className="bg-white dark:bg-slate-950 rounded-[3rem] border-2 border-slate-50 dark:border-slate-900 p-8 sm:p-12 shadow-2xl relative">
          {/* Close Button */}
          <button 
            onClick={onClose}
            className="absolute top-8 right-8 p-2 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-900 text-slate-400 transition-all"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Progress Bar */}
          <div className="flex gap-2 mb-12">
            {Array.from({ length: totalSteps }).map((_, i) => (
              <div 
                key={i}
                className={cn(
                  "h-1.5 flex-1 rounded-full transition-all duration-500",
                  i + 1 <= step ? "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.3)]" : "bg-slate-100 dark:bg-slate-900"
                )}
              />
            ))}
          </div>

          {/* Content */}
          <div className="min-h-[400px]">
            {isStudent ? renderStudentStep() : renderTeacherStep()}
          </div>

          {/* Footer */}
          <div className="mt-12 flex items-center justify-between gap-4">
            <button
              onClick={() => setStep(s => Math.max(1, s - 1))}
              disabled={step === 1 || loading}
              className="flex items-center gap-2 px-6 h-14 rounded-2xl font-black uppercase tracking-widest text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-all disabled:opacity-0"
            >
              <ChevronLeft className="w-4 h-4" />
              Back
            </button>

            {step < totalSteps ? (
              <button
                onClick={() => setStep(s => s + 1)}
                className="flex items-center gap-3 px-10 h-14 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl font-black uppercase tracking-widest text-xs hover:scale-105 active:scale-95 transition-all shadow-xl"
              >
                Next Step
                <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={isStudent ? handleStudentSubmit : handleTeacherSubmit}
                disabled={loading}
                className="flex items-center gap-3 px-10 h-14 bg-emerald-600 text-white rounded-2xl font-black uppercase tracking-widest text-xs hover:scale-105 active:scale-95 transition-all shadow-xl shadow-emerald-600/20 disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    Complete Setup
                    <Check className="w-4 h-4" />
                  </>
                )}
              </button>
            )}
          </div>

          {/* Skip for now */}
          <div className="mt-8 text-center">
            <button 
              onClick={onClose}
              className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] hover:text-emerald-500 transition-colors"
            >
              Skip for now, I'll do this later
            </button>
          </div>
        </div>

        {/* Badge Preview */}
        <div className="mt-8 flex items-center justify-center gap-3 animate-bounce">
          <div className="w-10 h-10 rounded-full bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
            <Award className="w-5 h-5 text-amber-500" />
          </div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
            Earn 50 Points & {isStudent ? 'Welcome Pioneer' : 'Founding Educator'} Badge
          </p>
        </div>
      </div>
    </div>
  )
}
