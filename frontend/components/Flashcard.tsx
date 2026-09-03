'use client'
import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'

interface FlashcardProps {
  front: string
  back: string
  image?: string
  context?: string
  onNext: () => void
  onPrevious: () => void
  onSwipe?: (type: 'forgot' | 'remembered') => void
  currentIndex: number
  total: number
}

export default function Flashcard({ 
  front, 
  back, 
  image, 
  context, 
  onNext, 
  onPrevious, 
  onSwipe,
  currentIndex, 
  total 
}: FlashcardProps) {
  const [flipped, setFlipped] = useState(false)
  const [touchStart, setTouchStart] = useState<number | null>(null)
  const [touchEnd, setTouchEnd] = useState<number | null>(null)
  
  // Minimum swipe distance (50px)
  const minSwipeDistance = 50

  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null)
    setTouchStart(e.targetTouches[0].clientX)
  }
  
  const handleTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX)
  }
  
  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return
    
    const distance = touchStart - touchEnd
    const isLeftSwipe = distance > minSwipeDistance
    const isRightSwipe = distance < -minSwipeDistance
    
    if (isLeftSwipe) {
      // Forgot - move to review pile
      if (onSwipe) onSwipe('forgot')
      onNext()
    }
    if (isRightSwipe) {
      // Remembered - move to known pile
      if (onSwipe) onSwipe('remembered')
      onNext()
    }
    
    setTouchStart(null)
    setTouchEnd(null)
  }

  useEffect(() => {
    setFlipped(false)
  }, [currentIndex])

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Swipe hint indicators */}
      <div className="relative h-96 mb-8">
        {touchStart !== null && touchEnd !== null && (
          <>
            {touchStart - touchEnd > 20 && (
              <div className="absolute left-4 top-1/2 -translate-y-1/2 z-20 text-red-500 font-black animate-pulse bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-6 py-3 rounded-2xl border-2 border-red-500 shadow-xl shadow-red-500/20">
                ← Forgot
              </div>
            )}
            {touchEnd - touchStart > 20 && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2 z-20 text-emerald-500 font-black animate-pulse bg-white/90 dark:bg-slate-900/90 backdrop-blur-md px-6 py-3 rounded-2xl border-2 border-emerald-500 shadow-xl shadow-emerald-500/20">
                Remembered →
              </div>
            )}
          </>
        )}

        {/* 3D Card Container */}
        <div
          className="relative w-full h-full cursor-pointer select-none"
          style={{ perspective: '2000px' }}
          onClick={() => setFlipped(!flipped)}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          <div
            className={cn(
              "absolute inset-0 w-full h-full transition-all duration-700 ease-out transform-style-preserve-3d",
              flipped && "rotate-y-180"
            )}
          >
            {/* Front Face */}
            <div className="absolute inset-0 w-full h-full backface-hidden bg-white dark:bg-slate-800 rounded-[2.5rem] p-10 flex flex-col justify-between shadow-2xl border-2 border-slate-100 dark:border-slate-700">
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 px-4 py-1.5 rounded-xl text-xs font-black uppercase tracking-widest mb-8">
                  Question
                </div>
                <h3 className="text-3xl font-outfit font-black text-slate-900 dark:text-slate-100 mb-6 leading-tight">
                  {front}
                </h3>
                {image && (
                  <div className="relative w-full h-48 mt-4 rounded-2xl overflow-hidden border-2 border-slate-100 dark:border-slate-700">
                    <img
                      src={image}
                      alt="Flashcard visual"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
              </div>
              <div className="flex items-center justify-center gap-2 text-slate-400 dark:text-slate-500 text-[10px] font-bold uppercase tracking-widest">
                <span>Tap to flip</span>
                <span className="w-1 h-1 bg-slate-300 dark:bg-slate-600 rounded-full" />
                <span>Swipe to answer</span>
              </div>
            </div>
            
            {/* Back Face */}
            <div className="absolute inset-0 w-full h-full backface-hidden bg-emerald-600 rounded-[2.5rem] p-10 flex flex-col justify-between shadow-2xl rotate-y-180 border-4 border-white dark:border-slate-900">
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="bg-white/20 text-white px-4 py-1.5 rounded-xl text-xs font-black uppercase tracking-widest mb-8">
                  Answer
                </div>
                <p className="text-2xl font-outfit font-bold text-white leading-relaxed mb-6">
                  {back}
                </p>
                {context && (
                  <div className="bg-white/10 backdrop-blur-sm p-5 rounded-2xl border border-white/20 text-left">
                    <p className="text-sm text-emerald-50 leading-relaxed">
                      <span className="font-black mr-2">💡 PRO TIP:</span>
                      {context}
                    </p>
                  </div>
                )}
              </div>
              <div className="text-center text-emerald-100/60 text-[10px] font-bold uppercase tracking-widest">
                Tap to flip back
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation & Progress */}
      <div className="flex items-center justify-between px-2">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onPrevious()
          }}
          disabled={currentIndex === 0}
          className="h-14 px-8 bg-white dark:bg-slate-800 border-2 border-slate-100 dark:border-slate-700 text-slate-600 dark:text-slate-300 rounded-2xl font-black text-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-all disabled:opacity-30 disabled:cursor-not-allowed shadow-sm"
        >
          PREVIOUS
        </button>

        <div className="flex flex-col items-center">
          <span className="text-slate-900 dark:text-slate-100 font-outfit font-black text-lg">
            {currentIndex + 1} <span className="text-slate-400 dark:text-slate-600 text-sm">/ {total}</span>
          </span>
          <div className="w-32 h-2 bg-slate-100 dark:bg-slate-800 rounded-full mt-2 overflow-hidden border border-slate-200 dark:border-slate-700">
            <div 
              className="h-full bg-emerald-500 transition-all duration-500 ease-out"
              style={{ width: `${((currentIndex + 1) / total) * 100}%` }}
            />
          </div>
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation()
            onNext()
          }}
          disabled={currentIndex === total - 1}
          className="h-14 px-8 bg-emerald-600 text-white rounded-2xl font-black text-sm hover:bg-emerald-500 transition-all disabled:opacity-30 disabled:cursor-not-allowed shadow-lg shadow-emerald-600/20"
        >
          NEXT
        </button>
      </div>
    </div>
  )
}

