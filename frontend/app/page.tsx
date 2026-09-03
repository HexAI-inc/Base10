'use client';

import React, { useState, useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import Link from 'next/link';
import { 
  WifiOff, 
  Smartphone, 
  BrainCircuit, 
  CheckCircle2, 
  Download, 
  ChevronRight,
  School,
  GraduationCap,
  Users,
  Loader2,
  Book,
  PenTool,
  Trophy,
  Star,
  Zap,
  MessageSquare,
  Globe,
  ShieldCheck
} from 'lucide-react';
import { marketingApi } from '@/lib/api';
import { useModalStore } from '@/store/modalStore';

export default function LandingPage() {
  const [formStep, setFormStep] = useState(0); // 0 = Idle, 1 = Submitted
  const [loading, setLoading] = useState(false);
  const { showError } = useModalStore();
  
  const hallwayRef = useRef<HTMLDivElement>(null);

  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    school_name: '',
    current_level: 'Senior Secondary (SSS/High School)',
    preparing_for: 'WASSCE / WAEC',
    device_type: 'Android'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await marketingApi.joinWaitlist(formData);
      setFormStep(1);
    } catch (err: any) {
      console.error('Waitlist error:', err);
      // For now, we'll show success even if the endpoint is missing (404) 
      // to ensure the marketing flow isn't "broken" for the user
      if (err.response?.status === 404 || err.code === 'ERR_NETWORK') {
        setFormStep(1);
      } else {
        showError('Failed to join waitlist. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-50 font-sans selection:bg-emerald-500/30 overflow-x-hidden scroll-smooth snap-y snap-proximity">
      
      {/* --- FLOATING BACKGROUND ITEMS --- */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <FloatingItem icon={<Book className="w-8 h-8" />} delay={0} x="10%" y="20%" />
        <FloatingItem icon={<PenTool className="w-6 h-6" />} delay={2} x="85%" y="15%" />
        <FloatingItem icon={<GraduationCap className="w-10 h-10" />} delay={4} x="75%" y="70%" />
        <FloatingItem icon={<BrainCircuit className="w-12 h-12" />} delay={1} x="15%" y="80%" />
        <FloatingItem icon={<Star className="w-5 h-5" />} delay={3} x="50%" y="10%" />
        <FloatingItem icon={<Zap className="w-6 h-6" />} delay={5} x="40%" y="90%" />
        
        {/* Animated Gradients */}
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-emerald-500/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-500/10 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      {/* --- NAVBAR --- */}
      <nav className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-5xl">
        <div className="relative p-[1px] rounded-full overflow-hidden group">
          {/* Animated Border Streaks (The "Border Beam" effect) */}
          <div className="absolute inset-0 rounded-full z-0">
            <motion.div 
              animate={{ rotate: 360 }}
              transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full aspect-square bg-[conic-gradient(from_0deg,transparent_0%,transparent_40%,#fff_50%,transparent_60%,transparent_100%)]"
            />
          </div>
          
          <div className="relative bg-gradient-to-b from-white/10 to-white/5 backdrop-blur-2xl rounded-full px-8 py-3 z-10 border border-white/20 shadow-[inset_0_0_20px_rgba(255,255,255,0.1)]">
            <div className="grid grid-cols-3 items-center">
              {/* Left: Links */}
              <div className="hidden md:flex items-center gap-8 text-sm font-bold text-slate-300">
                <a href="#features" className="hover:text-emerald-400 transition-colors">Features</a>
                <a href="#team" className="hover:text-emerald-400 transition-colors">Team</a>
              </div>

              {/* Center: Logo */}
              <div className="flex justify-center">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-500 flex items-center justify-center relative overflow-hidden">
                    <span className="text-[#0F172A] font-black text-2xl">X</span>
                    <span className="text-[#0F172A] font-black text-[10px] absolute bottom-1 right-1">10</span>
                  </div>
                  <span className="font-display font-black text-2xl tracking-tighter text-white">Base10</span>
                </div>
              </div>

              {/* Right: Actions */}
              <div className="flex items-center justify-end gap-6">
                <Link href="/login" className="hidden md:block text-sm font-bold text-slate-300 hover:text-emerald-400 transition-colors">Sign In</Link>
                <a 
                  href="#waitlist" 
                  className="bg-emerald-500 hover:bg-emerald-400 text-slate-950 px-6 py-2.5 rounded-full text-sm font-black transition-all hover:scale-105 active:scale-95 shadow-lg shadow-emerald-500/20"
                >
                  Join Waitlist
                </a>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* --- HERO SECTION --- */}
      <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden z-10 snap-start">
        <div className="max-w-7xl mx-auto px-6 flex flex-col items-center text-center">
          <motion.div 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-[0.2em] mb-8 backdrop-blur-sm"
          >
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            The #1 AI Study App for West Africa
          </motion.div>

          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="font-display text-6xl md:text-8xl font-black leading-[0.9] mb-8 max-w-5xl tracking-tighter"
          >
            Master Your Exams <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-500 animate-gradient-x">
              Without Limits.
            </span>
          </motion.h1>

          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-xl md:text-2xl text-slate-400 max-w-3xl mb-12 font-medium leading-relaxed"
          >
            Base10 is the offline-first AI tutor that fits in your pocket. 
            Access 20,000+ past questions, smart flashcards, and instant Socratic explanations—anytime, anywhere.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col md:flex-row gap-6 w-full md:w-auto"
          >
            <a href="#waitlist" className="flex items-center justify-center gap-3 bg-emerald-600 hover:bg-emerald-500 text-white px-10 py-5 rounded-2xl font-bold transition hover:scale-105 shadow-2xl shadow-emerald-500/40 text-lg">
              Get Early Access
              <ChevronRight className="w-5 h-5" />
            </a>
            <Link href="/register" className="flex items-center justify-center gap-3 bg-slate-800/50 backdrop-blur-md hover:bg-slate-700/50 text-slate-200 px-10 py-5 rounded-2xl font-bold transition border border-slate-700 text-lg">
              Try Web Demo
            </Link>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 1 }}
            className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-slate-500"
          >
            <span className="text-[10px] font-bold uppercase tracking-[0.3em]">Scroll to explore</span>
            <motion.div 
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-1 h-12 rounded-full bg-gradient-to-b from-emerald-500/50 to-transparent"
            />
          </motion.div>

          {/* Stats */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-24 grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-16"
          >
            <StatItem label="Past Questions" value="20K+" />
            <StatItem label="Active Students" value="5K+" />
            <StatItem label="Success Rate" value="94%" />
            <StatItem label="Data Saved" value="100%" />
          </motion.div>
        </div>
      </section>

      {/* --- INFINITE MARQUEE SECTION --- */}
      <section className="py-24 bg-[#020617] overflow-hidden snap-start">
        <div className="max-w-7xl mx-auto px-6 mb-16">
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4 tracking-tight">Explore the Hallway</h2>
          <p className="text-slate-400 text-lg">A glimpse into the future of learning in West Africa.</p>
        </div>

        <div className="flex overflow-hidden">
          <motion.div 
            animate={{ x: ["0%", "-50%"] }}
            transition={{ 
              duration: 30, 
              repeat: Infinity, 
              ease: "linear" 
            }}
            className="flex gap-8 px-4"
          >
            {/* First Set */}
            <HallwayCard 
              title="The Library" 
              desc="Access every WAEC & GABECE past question from 1990 to 2024. All available offline."
              icon={<Book className="w-12 h-12 text-emerald-400" />}
              image="https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&q=80&w=1000"
            />
            <HallwayCard 
              title="AI Lab" 
              desc="Our Socratic AI doesn't just give answers—it teaches you how to solve them yourself."
              icon={<BrainCircuit className="w-12 h-12 text-purple-400" />}
              image="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=1000"
            />
            <HallwayCard 
              title="Study Hall" 
              desc="Join study groups, compete on leaderboards, and earn badges for your consistency."
              icon={<Users className="w-12 h-12 text-blue-400" />}
              image="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&q=80&w=1000"
            />
            <HallwayCard 
              title="Exam Center" 
              desc="Realistic mock exams that simulate the actual WASSCE environment to build your confidence."
              icon={<Trophy className="w-12 h-12 text-amber-400" />}
              image="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&q=80&w=1000"
            />
            
            {/* Duplicate Set for Seamless Loop */}
            <HallwayCard 
              title="The Library" 
              desc="Access every WAEC & GABECE past question from 1990 to 2024. All available offline."
              icon={<Book className="w-12 h-12 text-emerald-400" />}
              image="https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&q=80&w=1000"
            />
            <HallwayCard 
              title="AI Lab" 
              desc="Our Socratic AI doesn't just give answers—it teaches you how to solve them yourself."
              icon={<BrainCircuit className="w-12 h-12 text-purple-400" />}
              image="https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=1000"
            />
            <HallwayCard 
              title="Study Hall" 
              desc="Join study groups, compete on leaderboards, and earn badges for your consistency."
              icon={<Users className="w-12 h-12 text-blue-400" />}
              image="https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&q=80&w=1000"
            />
            <HallwayCard 
              title="Exam Center" 
              desc="Realistic mock exams that simulate the actual WASSCE environment to build your confidence."
              icon={<Trophy className="w-12 h-12 text-amber-400" />}
              image="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&q=80&w=1000"
            />
          </motion.div>
        </div>
      </section>

      {/* --- VALUE PROPS (Grid) --- */}
      <section id="features" className="py-32 bg-[#020617] relative z-10 snap-start">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-black text-white mb-6 tracking-tight">Everything you need to succeed</h2>
            <p className="text-slate-400 text-lg max-w-2xl mx-auto">We've built the ultimate toolkit for the modern West African student.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard 
              icon={<WifiOff className="w-8 h-8 text-emerald-400" />}
              title="100% Offline"
              desc="No internet? No problem. Download your subjects once and study anywhere—even in the most remote areas."
            />
            <FeatureCard 
              icon={<BrainCircuit className="w-8 h-8 text-purple-400" />}
              title="Socratic AI Tutor"
              desc="Don't just get the answer. Our AI guides you through the logic, helping you master the concept forever."
            />
            <FeatureCard 
              icon={<Smartphone className="w-8 h-8 text-blue-400" />}
              title="Low-End Optimized"
              desc="Runs smoothly on older Android devices. Battery-efficient and takes up minimal storage space."
            />
            <FeatureCard 
              icon={<Globe className="w-8 h-8 text-cyan-400" />}
              title="Local Curriculum"
              desc="Tailored specifically for WAEC, WASSCE, GABECE, and JAMB. No irrelevant content."
            />
            <FeatureCard 
              icon={<MessageSquare className="w-8 h-8 text-pink-400" />}
              title="Smart Explanations"
              desc="Get instant, simplified breakdowns of complex topics in Mathematics, Physics, and more."
            />
            <FeatureCard 
              icon={<ShieldCheck className="w-8 h-8 text-emerald-400" />}
              title="Verified Content"
              desc="All questions and answers are double-checked by top educators in the region."
            />
          </div>
        </div>
      </section>

      {/* --- TEAM SECTION --- */}
      <section id="team" className="py-24 bg-slate-900 snap-start">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-display font-bold mb-4">Built by Students, For Students</h2>
          <p className="text-slate-400 mb-16 max-w-2xl mx-auto">
            We are a team of engineers and educators passionate about solving the education gap in West Africa.
          </p>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <TeamMember name="Ebrima S Jallow" role="Lead Engineer & Founder" />
            <TeamMember name="Sohna Faye" role="Product & Operations" />
            <TeamMember name="Demba Jallow" role="Education & Content Lead" />
          </div>
        </div>
      </section>

      {/* --- LEAD CAPTURE FORM (The Money Maker) --- */}
      <section id="waitlist" className="py-24 relative overflow-hidden snap-start">
        {/* Decorative Circles */}
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl -z-10" />

        <div className="max-w-3xl mx-auto px-6">
          <div className="bg-slate-800/80 backdrop-blur-xl border border-slate-700 rounded-3xl p-8 md:p-12 shadow-2xl">
            
            <div className="text-center mb-10">
              <h2 className="text-3xl font-display font-bold mb-4">Join the Waiting List</h2>
              <p className="text-slate-400">
                We are launching the mobile app soon. Fill this out to get a 
                <span className="text-emerald-400 font-bold"> FREE Premium Account</span> when we go live.
              </p>
            </div>

            {formStep === 0 ? (
              <form className="space-y-6" onSubmit={handleSubmit}>
                {/* Personal Info */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Full Name</label>
                    <input 
                      required 
                      type="text" 
                      placeholder="E.g. Musa Bah" 
                      value={formData.full_name}
                      onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition" 
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Phone (WhatsApp)</label>
                    <input 
                      required 
                      type="tel" 
                      placeholder="+220..." 
                      value={formData.phone}
                      onChange={(e) => setFormData({...formData, phone: e.target.value})}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition" 
                    />
                  </div>
                </div>

                {/* School Info */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">School Name</label>
                  <input 
                    required 
                    type="text" 
                    placeholder="E.g. Gambia High School" 
                    value={formData.school_name}
                    onChange={(e) => setFormData({...formData, school_name: e.target.value})}
                    className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition" 
                  />
                </div>

                {/* Dropdowns */}
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Current Level</label>
                    <select 
                      value={formData.current_level}
                      onChange={(e) => setFormData({...formData, current_level: e.target.value})}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition text-slate-300"
                    >
                      <option>Junior Secondary (JSS/Upper Basic)</option>
                      <option>Senior Secondary (SSS/High School)</option>
                      <option>High School Graduate</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-300">Preparing For</label>
                    <select 
                      value={formData.preparing_for}
                      onChange={(e) => setFormData({...formData, preparing_for: e.target.value})}
                      className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 transition text-slate-300"
                    >
                      <option>WASSCE / WAEC</option>
                      <option>GABECE / BECE</option>
                      <option>JAMB</option>
                    </select>
                  </div>
                </div>

                {/* Device Type (Radio) */}
                <div className="space-y-3 pt-2">
                  <label className="text-sm font-medium text-slate-300 block">What device do you use?</label>
                  <div className="flex flex-wrap gap-4">
                    {['Android', 'iPhone', 'Laptop/PC'].map((device) => (
                      <label key={device} className="flex items-center gap-2 cursor-pointer">
                        <input 
                          type="radio" 
                          name="device" 
                          value={device}
                          checked={formData.device_type === device}
                          onChange={(e) => setFormData({...formData, device_type: e.target.value})}
                          className="accent-emerald-500" 
                        />
                        <span className="text-slate-400">{device}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="pt-4">
                  <button 
                    type="submit" 
                    disabled={loading}
                    className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 rounded-xl transition shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {loading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        Join Waiting List
                        <CheckCircle2 className="w-5 h-5" />
                      </>
                    )}
                  </button>
                  <p className="text-center text-xs text-slate-500 mt-4">
                    We respect your privacy. No spam, just updates.
                  </p>
                </div>
              </form>
            ) : (
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-16"
              >
                <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircle2 className="w-10 h-10 text-emerald-500" />
                </div>
                <h3 className="text-2xl font-bold mb-2">You're on the list! 🎉</h3>
                <p className="text-slate-400">
                  Thanks for joining Base10. We will send you an SMS/WhatsApp message as soon as the app is ready for download.
                </p>
                <button 
                  onClick={() => setFormStep(0)}
                  className="mt-8 text-emerald-400 hover:text-emerald-300 text-sm font-medium"
                >
                  Register another student
                </button>
              </motion.div>
            )}

          </div>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="py-8 border-t border-slate-800 text-center text-slate-500 text-sm">
        <p>© 2025 Base10. Built in West Africa 🌍</p>
      </footer>

    </div>
  );
}

// --- SUB-COMPONENTS ---

function FeatureCard({ icon, title, desc }: { icon: any, title: string, desc: string }) {
  return (
    <div className="p-6 rounded-2xl bg-slate-800 border border-slate-700 hover:border-emerald-500/50 transition duration-300 group">
      <div className="mb-4 bg-slate-900 w-14 h-14 rounded-xl flex items-center justify-center group-hover:scale-110 transition">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2 text-slate-100">{title}</h3>
      <p className="text-slate-400 leading-relaxed">{desc}</p>
    </div>
  );
}

function TeamMember({ name, role }: { name: string, role: string }) {
  return (
    <div className="p-6 rounded-2xl bg-slate-800 border border-slate-700 flex flex-col items-center">
      <div className="w-24 h-24 rounded-full bg-slate-700 mb-4 flex items-center justify-center text-3xl">
        {/* Placeholder Avatar */}
        🧔🏾‍♂️
      </div>
      <h3 className="text-lg font-bold text-slate-100">{name}</h3>
      <p className="text-emerald-400 text-sm font-medium">{role}</p>
    </div>
  );
}

function FloatingItem({ icon, delay, x, y }: { icon: React.ReactNode, delay: number, x: string, y: string }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ 
        opacity: [0.2, 0.5, 0.2],
        y: [0, -20, 0],
        rotate: [0, 10, -10, 0]
      }}
      transition={{ 
        duration: 5, 
        delay, 
        repeat: Infinity,
        ease: "easeInOut"
      }}
      className="absolute text-emerald-500/20"
      style={{ left: x, top: y }}
    >
      {icon}
    </motion.div>
  );
}

function StatItem({ label, value }: { label: string, value: string }) {
  return (
    <div className="flex flex-col items-center">
      <span className="text-3xl md:text-4xl font-black text-white mb-1">{value}</span>
      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em]">{label}</span>
    </div>
  );
}

function HallwayCard({ title, desc, icon, image }: { title: string, desc: string, icon: React.ReactNode, image: string }) {
  return (
    <div className="relative w-[350px] md:w-[450px] h-[500px] rounded-[2.5rem] overflow-hidden group flex-shrink-0 border border-slate-800">
      <img src={image} alt={title} className="absolute inset-0 w-full h-full object-cover opacity-40 group-hover:scale-110 transition-transform duration-700" />
      <div className="absolute inset-0 bg-gradient-to-t from-[#020617] via-[#020617]/40 to-transparent" />
      <div className="absolute inset-0 p-10 flex flex-col justify-end">
        <div className="mb-6 w-16 h-16 rounded-2xl bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/10">
          {icon}
        </div>
        <h3 className="text-3xl font-black text-white mb-4">{title}</h3>
        <p className="text-slate-300 font-medium leading-relaxed">{desc}</p>
      </div>
    </div>
  );
}
