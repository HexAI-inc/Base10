'use client'
import { useState, useMemo } from 'react'
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react'

interface CalendarPickerProps {
  value?: string
  onChange: (date: string) => void
  minDate?: Date
  maxDate?: Date
  placeholder?: string
}

export default function CalendarPicker({ 
  value, 
  onChange, 
  minDate, 
  maxDate,
  placeholder = 'Select date'
}: CalendarPickerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [currentMonth, setCurrentMonth] = useState(
    value ? new Date(value) : new Date()
  )

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  const daysInMonth = useMemo(() => {
    const year = currentMonth.getFullYear()
    const month = currentMonth.getMonth()
    return new Date(year, month + 1, 0).getDate()
  }, [currentMonth])

  const firstDayOfMonth = useMemo(() => {
    const year = currentMonth.getFullYear()
    const month = currentMonth.getMonth()
    return new Date(year, month, 1).getDay()
  }, [currentMonth])

  const selectedDate = value ? new Date(value) : null

  const handlePrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))
  }

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))
  }

  const handleDateSelect = (day: number) => {
    const selected = new Date(
      currentMonth.getFullYear(),
      currentMonth.getMonth(),
      day
    )
    
    // Check min/max dates
    if (minDate && selected < minDate) return
    if (maxDate && selected > maxDate) return
    
    onChange(selected.toISOString().split('T')[0])
    setIsOpen(false)
  }

  const isDateDisabled = (day: number) => {
    const date = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day)
    if (minDate && date < minDate) return true
    if (maxDate && date > maxDate) return true
    return false
  }

  const isToday = (day: number) => {
    const today = new Date()
    return (
      day === today.getDate() &&
      currentMonth.getMonth() === today.getMonth() &&
      currentMonth.getFullYear() === today.getFullYear()
    )
  }

  const isSelected = (day: number) => {
    if (!selectedDate) return false
    return (
      day === selectedDate.getDate() &&
      currentMonth.getMonth() === selectedDate.getMonth() &&
      currentMonth.getFullYear() === selectedDate.getFullYear()
    )
  }

  const days = []
  
  // Empty cells for days before month starts
  for (let i = 0; i < firstDayOfMonth; i++) {
    days.push(<div key={`empty-${i}`} className="aspect-square" />)
  }
  
  // Days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    const disabled = isDateDisabled(day)
    const today = isToday(day)
    const selected = isSelected(day)
    
    days.push(
      <button
        key={day}
        onClick={() => !disabled && handleDateSelect(day)}
        disabled={disabled}
        className={`
          aspect-square rounded-xl flex items-center justify-center text-sm font-bold transition-all
          ${disabled ? 'text-slate-200 dark:text-slate-800 cursor-not-allowed' : 'hover:bg-emerald-50 dark:hover:bg-emerald-900/20'}
          ${today && !selected ? 'text-emerald-600 dark:text-emerald-400 ring-2 ring-emerald-100 dark:ring-emerald-900/30' : ''}
          ${selected ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/20 scale-110' : 'text-slate-900 dark:text-slate-100'}
        `}
      >
        {day}
      </button>
    )
  }

  return (
    <div className="relative">
      {/* Input Trigger */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full h-14 px-6 border-2 border-slate-100 dark:border-slate-800 rounded-2xl bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 flex items-center justify-between hover:border-emerald-500 transition-all shadow-sm"
      >
        <span className={`font-medium ${value ? 'text-slate-900 dark:text-slate-100' : 'text-slate-400'}`}>
          {value ? new Date(value).toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          }) : placeholder}
        </span>
        <Calendar className="w-5 h-5 text-slate-400" />
      </button>

      {/* Calendar Popup */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Calendar */}
          <div className="absolute z-50 mt-3 bg-white dark:bg-slate-800 border-2 border-slate-100 dark:border-slate-700 rounded-[2rem] shadow-2xl p-6 w-80 backdrop-blur-xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <button
                type="button"
                onClick={handlePrevMonth}
                className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-all"
              >
                <ChevronLeft className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              </button>
              
              <div className="font-outfit font-black text-slate-900 dark:text-slate-100 uppercase tracking-widest text-xs">
                {months[currentMonth.getMonth()]} {currentMonth.getFullYear()}
              </div>
              
              <button
                type="button"
                onClick={handleNextMonth}
                className="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl transition-all"
              >
                <ChevronRight className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              </button>
            </div>

            {/* Weekday Headers */}
            <div className="grid grid-cols-7 gap-1 mb-4">
              {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map(day => (
                <div key={day} className="text-center text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-tighter">
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-2">
              {days}
            </div>

            {/* Quick Actions */}
            <div className="mt-6 pt-6 border-t-2 border-slate-50 dark:border-slate-700/50 flex gap-3">
              <button
                type="button"
                onClick={() => {
                  onChange(new Date().toISOString().split('T')[0])
                  setIsOpen(false)
                }}
                className="flex-1 h-10 text-xs font-black bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 rounded-xl hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition-all uppercase tracking-widest"
              >
                Today
              </button>
              <button
                type="button"
                onClick={() => {
                  onChange('')
                  setIsOpen(false)
                }}
                className="flex-1 h-10 text-xs font-black bg-slate-50 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-600 transition-all uppercase tracking-widest"
              >
                Clear
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
