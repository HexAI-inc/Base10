'use client'
import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/lib/api'
import { 
  Mail, 
  Lock, 
  Loader2, 
  Eye, 
  EyeOff, 
  Brain, 
  ArrowRight, 
  Sparkles, 
  User, 
  Phone, 
  ChevronLeft,
  BookOpen,
  Trophy
} from 'lucide-react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'

function FeatureItem({ icon, text }: { icon: React.ReactNode, text: string }) {
  return (
    <div className="flex items-center gap-3 text-white/90 font-bold">
      <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
        {icon}
      </div>
      <span className="text-sm">{text}</span>
    </div>
  )
}

function TestimonialCard({ text, author, role, delay, x, y }: { text: string, author: string, role: string, delay: number, x: string, y: string }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ 
        opacity: [0.4, 0.7, 0.4],
        y: [0, -20, 0],
      }}
      transition={{ 
        duration: 5, 
        repeat: Infinity, 
        delay: delay,
        ease: "easeInOut"
      }}
      style={{ left: x, top: y }}
      className="absolute z-0 hidden lg:flex items-center gap-4 bg-white/5 backdrop-blur-md p-4 rounded-2xl border border-white/10 w-64"
    >
      <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-xl shrink-0">
        🎓
      </div>
      <div>
        <p className="text-white/80 font-medium text-[10px] leading-tight mb-1">"{text}"</p>
        <p className="text-emerald-400 text-[8px] font-bold uppercase tracking-wider">— {author}</p>
      </div>
    </motion.div>
  )
}

function AuthContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const setAuth = useAuthStore((state) => state.setAuth)
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  useEffect(() => {
    if (searchParams.get('mode') === 'signup') {
      setIsLogin(false)
    }
  }, [searchParams])

  // Login State
  const [loginData, setLoginData] = useState({ username: '', password: '' })
  
  // Register State
  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone_number: '',
  })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const response = await authApi.login(loginData.username, loginData.password)
      const { access_token, user } = response.data
      setAuth(access_token, user)
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await authApi.register(registerData)
      setIsLogin(true)
      setError('Registration successful! Please sign in.')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center p-4 md:p-8 relative overflow-hidden font-sans">
      {/* Background Decorative Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-emerald-500/10 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-500/10 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '2s' }} />

      {/* Floating Testimonials */}
      <TestimonialCard 
        text="Base10 helped me get 7 A1s in my WASSCE!" 
        author="Fatoumatta B." 
        role="Science Student"
        delay={0}
        x="5%"
        y="15%"
      />
      <TestimonialCard 
        text="The offline mode is a lifesaver for my village." 
        author="Ibrahim K." 
        role="Arts Student"
        delay={2}
        x="75%"
        y="10%"
      />
      <TestimonialCard 
        text="Socratic AI is like having a personal tutor 24/7." 
        author="Mariama S." 
        role="Commercial Student"
        delay={4}
        x="10%"
        y="75%"
      />
      <TestimonialCard 
        text="I finally understand Physics thanks to the AI Lab!" 
        author="Alieu J." 
        role="Science Student"
        delay={1}
        x="80%"
        y="80%"
      />

      <motion.div 
        layout
        className="max-w-5xl w-full min-h-[700px] bg-slate-900/50 backdrop-blur-xl rounded-[3rem] border border-white/10 shadow-2xl overflow-hidden flex flex-col md:flex-row relative"
      >
        {/* --- CONTENT SIDE (The one that flips) --- */}
        <motion.div 
          animate={{ 
            x: isLogin ? '0%' : '100%',
          }}
          transition={{ type: "spring", stiffness: 50, damping: 15 }}
          className="hidden md:flex w-1/2 bg-gradient-to-br from-emerald-600 to-emerald-400 p-12 flex-col justify-between relative z-20"
        >
          <div className="relative z-10">
            <Link href="/" className="inline-flex items-center gap-2 text-white/90 hover:text-white transition mb-12">
              <ChevronLeft className="w-5 h-5" />
              <span className="font-bold text-sm uppercase tracking-widest">Back to Home</span>
            </Link>
            
            <div className="space-y-6">
              <motion.div
                key={isLogin ? 'login-content' : 'register-content'}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                <h2 className="text-5xl font-black text-white leading-tight">
                  {isLogin ? "Welcome Back to Base10" : "Start Your Journey Today"}
                </h2>
                <p className="text-emerald-50/80 text-lg font-medium leading-relaxed">
                  {isLogin 
                    ? "Continue mastering your subjects with West Africa's most advanced AI tutor." 
                    : "Join thousands of students achieving excellence with offline-first learning."}
                </p>
              </motion.div>

              <div className="grid grid-cols-1 gap-4 mt-12">
                <FeatureItem icon={<BookOpen />} text="20,000+ Past Questions" />
                <FeatureItem icon={<Brain />} text="Socratic AI Explanations" />
                <FeatureItem icon={<Trophy />} text="Performance Tracking" />
              </div>
            </div>
          </div>

          {/* Decorative Circles */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32 blur-3xl" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-black/5 rounded-full -ml-32 -mb-32 blur-3xl" />
        </motion.div>

        {/* --- FORM SIDE --- */}
        <motion.div 
          animate={{ 
            x: isLogin ? '0%' : '-100%',
          }}
          transition={{ type: "spring", stiffness: 50, damping: 15 }}
          className="w-full md:w-1/2 p-8 md:p-16 flex flex-col justify-center relative z-10"
        >
          <div className="mb-10">
            <div className="w-12 h-12 rounded-xl bg-emerald-500 flex items-center justify-center shadow-lg shadow-emerald-500/20 mb-6">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-3xl font-black text-white mb-2">
              {isLogin ? "Sign In" : "Create Account"}
            </h3>
            <p className="text-slate-400 font-medium">
              {isLogin ? "Enter your details to continue" : "Fill in the form to get started"}
            </p>
          </div>

          <AnimatePresence mode="wait">
            {isLogin ? (
              <motion.form 
                key="login-form"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                onSubmit={handleLogin} 
                className="space-y-6"
              >
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-2">Email or Phone</label>
                  <div className="relative group">
                    <Mail className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                    <input
                      type="text"
                      value={loginData.username}
                      onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                      required
                      className="w-full h-14 pl-14 pr-6 bg-slate-800/50 border border-slate-700 focus:border-emerald-500/50 rounded-2xl outline-none text-white font-bold transition-all"
                      placeholder="you@example.com"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between px-2">
                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Password</label>
                    <Link href="/forgot-password" title="Forgot Password" className="text-[10px] font-black text-emerald-500 uppercase tracking-widest hover:text-emerald-400 transition-colors">Forgot?</Link>
                  </div>
                  <div className="relative group">
                    <Lock className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={loginData.password}
                      onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                      required
                      className="w-full h-14 pl-14 pr-14 bg-slate-800/50 border border-slate-700 focus:border-emerald-500/50 rounded-2xl outline-none text-white font-bold transition-all"
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    <p className="text-red-400 text-xs font-bold uppercase tracking-widest">{error}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full h-14 bg-emerald-500 hover:bg-emerald-400 disabled:bg-emerald-500/50 text-slate-950 font-black rounded-2xl transition-all flex items-center justify-center gap-3 shadow-xl shadow-emerald-500/20 group"
                >
                  {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : (
                    <>
                      Sign In
                      <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </button>

                <p className="text-center text-slate-500 text-sm font-medium">
                  Don't have an account?{' '}
                  <button 
                    type="button"
                    onClick={() => setIsLogin(false)}
                    className="text-emerald-500 font-bold hover:text-emerald-400 transition"
                  >
                    Create one for free
                  </button>
                </p>
              </motion.form>
            ) : (
              <motion.form 
                key="register-form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                onSubmit={handleRegister} 
                className="space-y-4"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-2">Full Name</label>
                    <div className="relative group">
                      <User className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                      <input
                        type="text"
                        value={registerData.full_name}
                        onChange={(e) => setRegisterData({ ...registerData, full_name: e.target.value })}
                        required
                        className="w-full h-14 pl-14 pr-6 bg-slate-800/50 border border-slate-700 focus:border-emerald-500/50 rounded-2xl outline-none text-white font-bold transition-all"
                        placeholder="John Doe"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-2">Phone</label>
                    <div className="relative group">
                      <Phone className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                      <input
                        type="tel"
                        value={registerData.phone_number}
                        onChange={(e) => setRegisterData({ ...registerData, phone_number: e.target.value })}
                        required
                        className="w-full h-14 pl-14 pr-6 bg-slate-800/50 border border-slate-700 focus:border-emerald-500/50 rounded-2xl outline-none text-white font-bold transition-all"
                        placeholder="+220..."
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-2">Email Address</label>
                  <div className="relative group">
                    <Mail className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                    <input
                      type="email"
                      value={registerData.email}
                      onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                      required
                      className="w-full h-14 pl-14 pr-6 bg-slate-800/50 border border-slate-700 focus:border-emerald-500/50 rounded-2xl outline-none text-white font-bold transition-all"
                      placeholder="john@example.com"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] ml-2">Password</label>
                  <div className="relative group">
                    <Lock className="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={registerData.password}
                      onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                      required
                      className="w-full h-14 pl-14 pr-14 bg-slate-800/50 border border-slate-700 focus:border-emerald-500/50 rounded-2xl outline-none text-white font-bold transition-all"
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                    <p className="text-red-400 text-xs font-bold uppercase tracking-widest">{error}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full h-14 bg-emerald-500 hover:bg-emerald-400 disabled:bg-emerald-500/50 text-slate-950 font-black rounded-2xl transition-all flex items-center justify-center gap-3 shadow-xl shadow-emerald-500/20 group"
                >
                  {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : (
                    <>
                      Create Account
                      <Sparkles className="w-5 h-5 group-hover:scale-110 transition-transform" />
                    </>
                  )}
                </button>

                <p className="text-center text-slate-500 text-sm font-medium">
                  Already have an account?{' '}
                  <button 
                    type="button"
                    onClick={() => setIsLogin(true)}
                    className="text-emerald-500 font-bold hover:text-emerald-400 transition"
                  >
                    Sign in here
                  </button>
                </p>
              </motion.form>
            )}
          </AnimatePresence>
        </motion.div>
      </motion.div>
    </div>
  )
}

export default function AuthPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#020617] flex items-center justify-center"><Loader2 className="w-12 h-12 text-emerald-500 animate-spin" /></div>}>
      <AuthContent />
    </Suspense>
  )
}
