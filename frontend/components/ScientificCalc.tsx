'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Calculator, X, Minimize2, RotateCcw } from 'lucide-react'

interface ScientificCalcProps {
  onClose?: () => void
  isStatic?: boolean
}

export default function ScientificCalc({ onClose, isStatic = false }: ScientificCalcProps) {
  const [display, setDisplay] = useState('0')
  const [memory, setMemory] = useState<number | null>(null)
  const [lastOperation, setLastOperation] = useState<string | null>(null)
  const [isMinimized, setIsMinimized] = useState(isStatic ? false : true)
  const [position, setPosition] = useState({ x: 100, y: 100 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })

  // Persist minimized state
  useEffect(() => {
    if (isStatic) return
    const saved = localStorage.getItem('calc_minimized')
    if (saved !== null) {
      setIsMinimized(saved === 'true')
    }
  }, [isStatic])

  const toggleMinimized = (val: boolean) => {
    if (isStatic) return
    setIsMinimized(val)
    localStorage.setItem('calc_minimized', val.toString())
  }

  const handleNumber = (num: string) => {
    setDisplay(prev => prev === '0' ? num : prev + num)
  }

  const handleOperation = (op: string) => {
    setMemory(parseFloat(display))
    setLastOperation(op)
    setDisplay('0')
  }

  const handleEquals = () => {
    if (memory === null || lastOperation === null) return
    const current = parseFloat(display)
    let result = 0
    switch (lastOperation) {
      case '+': result = memory + current; break
      case '-': result = memory - current; break
      case '×': result = memory * current; break
      case '÷': result = memory / current; break
      case '^': result = Math.pow(memory, current); break
    }
    setDisplay(result.toString())
    setMemory(null)
    setLastOperation(null)
  }

  const handleScientific = (func: string) => {
    const current = parseFloat(display)
    let result = 0
    switch (func) {
      case 'sin': result = Math.sin(current); break
      case 'cos': result = Math.cos(current); break
      case 'tan': result = Math.tan(current); break
      case 'sqrt': result = Math.sqrt(current); break
      case 'log': result = Math.log10(current); break
      case 'ln': result = Math.log(current); break
      case '1/x': result = 1 / current; break
      case 'x²': result = current * current; break
    }
    setDisplay(result.toString())
  }

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true)
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    })
  }

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      })
    }
  }, [isDragging, dragOffset])

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, handleMouseMove])

  // Minimized FAB
  if (isMinimized) {
    return (
      <button
        onClick={() => toggleMinimized(false)}
        className="fixed bottom-8 right-8 w-16 h-16 bg-emerald-600 hover:bg-emerald-500 rounded-2xl shadow-xl shadow-emerald-600/20 flex items-center justify-center text-white transition-all hover:scale-110 z-50 border-4 border-white dark:border-slate-900"
        aria-label="Open calculator"
      >
        <Calculator className="w-8 h-8" />
      </button>
    )
  }
  
  // Expanded Calculator
  return (
    <div
      className={`${isStatic ? 'relative' : 'fixed'} bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden z-50 transition-colors duration-500`}
      style={isStatic ? { width: '100%' } : {
        left: `${position.x}px`,
        top: `${position.y}px`,
        width: '340px',
        cursor: isDragging ? 'grabbing' : 'default'
      }}
    >
      {/* Draggable Header */}
      <div
        className={`bg-slate-50 dark:bg-slate-900 px-6 py-4 flex items-center justify-between ${isStatic ? '' : 'cursor-grab active:cursor-grabbing'} select-none border-b border-slate-200 dark:border-slate-800`}
        onMouseDown={isStatic ? undefined : handleMouseDown}
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-emerald-100 dark:bg-emerald-900/50 rounded-xl flex items-center justify-center">
            <Calculator className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h3 className="font-outfit font-black text-slate-900 dark:text-slate-100 text-xs uppercase tracking-widest">Scientific Calculator</h3>
        </div>
        <div className="flex items-center gap-2">
          {!isStatic && (
            <button
              onClick={() => toggleMinimized(true)}
              className="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-xl transition-colors"
            >
              <Minimize2 className="w-4 h-4 text-slate-500 dark:text-slate-400" />
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-xl group transition-colors"
            >
              <X className="w-4 h-4 text-slate-500 dark:text-slate-400 group-hover:text-red-500" />
            </button>
          )}
        </div>
      </div>

      {/* Display */}
      <div className="p-6 bg-slate-50 dark:bg-slate-900/50">
        <div className="bg-white dark:bg-slate-950 rounded-2xl p-6 border-2 border-slate-100 dark:border-slate-800 shadow-inner">
          <div className="text-right text-slate-400 dark:text-slate-600 text-xs font-mono h-4 mb-1 overflow-hidden">
            {memory !== null && `${memory} ${lastOperation || ''}`}
          </div>
          <div className="text-right text-3xl font-mono font-bold text-slate-900 dark:text-slate-100 overflow-hidden whitespace-nowrap">
            {display}
          </div>
        </div>
      </div>

      {/* Keypad */}
      <div className="p-6 grid grid-cols-4 gap-3">
        {/* Scientific Row 1 */}
        {['sin', 'cos', 'tan', 'sqrt'].map(func => (
          <button
            key={func}
            onClick={() => handleScientific(func)}
            className="h-12 rounded-xl bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-400 font-bold text-xs hover:bg-emerald-50 dark:hover:bg-emerald-900/30 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all"
          >
            {func}
          </button>
        ))}
        
        {/* Scientific Row 2 */}
        {['log', 'ln', '1/x', '^'].map(func => (
          <button
            key={func}
            onClick={() => func === '^' ? handleOperation('^') : handleScientific(func)}
            className="h-12 rounded-xl bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-400 font-bold text-xs hover:bg-emerald-50 dark:hover:bg-emerald-900/30 hover:text-emerald-600 dark:hover:text-emerald-400 transition-all"
          >
            {func}
          </button>
        ))}

        {/* Numbers and Basic Ops */}
        <button onClick={() => setDisplay('0')} className="h-14 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 font-black text-sm hover:bg-red-100 dark:hover:bg-red-900/40 transition-all">AC</button>
        <button onClick={() => setDisplay(display.slice(0, -1) || '0')} className="h-14 rounded-xl bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-400 font-black text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-all">DEL</button>
        <button onClick={() => handleOperation('÷')} className="h-14 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 font-black text-lg hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition-all">÷</button>
        <button onClick={() => handleOperation('×')} className="h-14 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 font-black text-lg hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition-all">×</button>

        {[7, 8, 9].map(n => (
          <button key={n} onClick={() => handleNumber(n.toString())} className="h-14 rounded-xl bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 font-bold text-lg shadow-sm border border-slate-100 dark:border-slate-600 hover:border-emerald-500 transition-all">{n}</button>
        ))}
        <button onClick={() => handleOperation('-')} className="h-14 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 font-black text-lg hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition-all">−</button>

        {[4, 5, 6].map(n => (
          <button key={n} onClick={() => handleNumber(n.toString())} className="h-14 rounded-xl bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 font-bold text-lg shadow-sm border border-slate-100 dark:border-slate-600 hover:border-emerald-500 transition-all">{n}</button>
        ))}
        <button onClick={() => handleOperation('+')} className="h-14 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 font-black text-lg hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition-all">+</button>

        {[1, 2, 3].map(n => (
          <button key={n} onClick={() => handleNumber(n.toString())} className="h-14 rounded-xl bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 font-bold text-lg shadow-sm border border-slate-100 dark:border-slate-600 hover:border-emerald-500 transition-all">{n}</button>
        ))}
        <button onClick={handleEquals} className="h-14 rounded-xl bg-emerald-600 text-white font-black text-lg shadow-lg shadow-emerald-600/20 hover:bg-emerald-700 transition-all">=</button>

        <button onClick={() => handleNumber('0')} className="col-span-2 h-14 rounded-xl bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 font-bold text-lg shadow-sm border border-slate-100 dark:border-slate-600 hover:border-emerald-500 transition-all">0</button>
        <button onClick={() => handleNumber('.')} className="h-14 rounded-xl bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100 font-bold text-lg shadow-sm border border-slate-100 dark:border-slate-600 hover:border-emerald-500 transition-all">.</button>
        <button onClick={() => handleScientific('x²')} className="h-14 rounded-xl bg-slate-100 dark:bg-slate-700/50 text-slate-600 dark:text-slate-400 font-bold text-sm hover:bg-emerald-50 dark:hover:bg-emerald-900/30 transition-all">x²</button>
      </div>
    </div>
  )
}
