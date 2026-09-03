'use client'
import AppLayout from '@/components/AppLayout'
import ScientificCalc from '@/components/ScientificCalc'
import { Calculator, Sparkles, History, Settings2, Info } from 'lucide-react'

export default function CalculatorPage() {
  return (
    <AppLayout>
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="flex flex-col lg:flex-row gap-12">
          {/* Left Side: Info & History */}
          <div className="lg:w-1/3 space-y-8">
            <div>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 flex items-center justify-center">
                  <Calculator className="w-6 h-6 text-emerald-600" />
                </div>
                <span className="text-[10px] font-black text-emerald-600 uppercase tracking-[0.3em]">Scientific Tool</span>
              </div>
              <h1 className="text-4xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight mb-6">
                Advanced <span className="text-emerald-600">Calculator</span>
              </h1>
              <p className="text-slate-500 dark:text-slate-400 font-medium leading-relaxed">
                A high-precision scientific calculator optimized for WASSCE mathematics and science subjects. Supports trigonometry, logarithms, and complex expressions.
              </p>
            </div>

            {/* Quick Tips */}
            <div className="bg-white dark:bg-slate-950 p-8 rounded-[2.5rem] border-2 border-slate-50 dark:border-slate-900 shadow-sm">
              <div className="flex items-center gap-3 mb-6">
                <Info className="w-5 h-5 text-blue-500" />
                <h3 className="text-sm font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest">Pro Tips</h3>
              </div>
              <ul className="space-y-4">
                {[
                  'Use DEG/RAD toggle for trig functions',
                  'Access inverse functions via the INV button',
                  'History is saved locally for your session',
                  'Keyboard shortcuts supported for numbers'
                ].map((tip, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-slate-500 dark:text-slate-400">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                    {tip}
                  </li>
                ))}
              </ul>
            </div>

            {/* History Placeholder */}
            <div className="bg-slate-900 dark:bg-emerald-600 p-8 rounded-[2.5rem] text-white shadow-2xl shadow-emerald-600/20 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 blur-2xl group-hover:scale-150 transition-transform duration-700" />
              <div className="relative z-10">
                <div className="flex items-center gap-3 mb-6">
                  <History className="w-5 h-5" />
                  <h3 className="text-sm font-black uppercase tracking-widest">Recent History</h3>
                </div>
                <div className="space-y-4 opacity-60">
                  <div className="flex justify-between text-xs font-bold">
                    <span>sin(45) * 2</span>
                    <span>1.414</span>
                  </div>
                  <div className="h-px bg-white/10" />
                  <div className="flex justify-between text-xs font-bold">
                    <span>log(100)</span>
                    <span>2</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side: The Calculator */}
          <div className="lg:w-2/3">
            <div className="bg-white dark:bg-slate-950 p-4 rounded-[3.5rem] border-2 border-slate-50 dark:border-slate-900 shadow-2xl">
              <ScientificCalc isStatic />
            </div>
            
            <div className="mt-8 flex items-center justify-center gap-8">
              <div className="flex items-center gap-2 text-slate-400">
                <Settings2 className="w-4 h-4" />
                <span className="text-[10px] font-black uppercase tracking-widest">Precision: 10 Decimal Places</span>
              </div>
              <div className="flex items-center gap-2 text-slate-400">
                <Sparkles className="w-4 h-4" />
                <span className="text-[10px] font-black uppercase tracking-widest">AI Powered Verification</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
