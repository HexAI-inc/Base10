'use client'
import { Bell, Search, Moon, Sun, Menu } from 'lucide-react'
import { useState, useEffect } from 'react'
import ThemeToggle from './ThemeToggle'
import SyncStatus from './SyncStatus'

interface TopNavbarProps {
  onMenuClick?: () => void
  title?: string
}

export default function TopNavbar({ onMenuClick, title }: TopNavbarProps) {
  const [notifications, setNotifications] = useState(3) // Mock notification count

  return (
    <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-100 dark:border-slate-800 sticky top-0 z-30 h-20 transition-colors duration-500">
      <div className="h-full px-6 sm:px-8 flex items-center justify-between">
        {/* Left Section - Mobile Menu + Title */}
        <div className="flex items-center gap-6">
          {/* Mobile Menu Button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-3 rounded-2xl bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all"
          >
            <Menu className="w-6 h-6 text-slate-600 dark:text-slate-400" />
          </button>

          {/* Page Title */}
          {title && (
            <h2 className="text-2xl font-outfit font-black text-slate-900 dark:text-slate-100 tracking-tight">
              {title}
            </h2>
          )}
        </div>

        {/* Center Section - Search Bar (Desktop) */}
        <div className="hidden md:flex flex-1 max-w-xl mx-12">
          <div className="relative w-full group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
            <input
              type="text"
              placeholder="Search questions, subjects..."
              className="w-full h-12 pl-12 pr-6 bg-slate-50 dark:bg-slate-800/50 border-2 border-transparent focus:border-emerald-500/20 rounded-2xl focus:outline-none focus:ring-4 focus:ring-emerald-500/5 text-slate-900 dark:text-slate-100 font-medium transition-all placeholder:text-slate-400 dark:placeholder:text-slate-600"
            />
          </div>
        </div>

        {/* Right Section - Actions */}
        <div className="flex items-center gap-4">
          {/* Sync Status */}
          <div className="hidden sm:block">
            <SyncStatus />
          </div>

          {/* Search Button (Mobile) */}
          <button className="md:hidden p-3 rounded-2xl bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all">
            <Search className="w-5 h-5 text-slate-600 dark:text-slate-400" />
          </button>

          {/* Notifications */}
          <button className="relative p-3 rounded-2xl bg-slate-50 dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all group">
            <Bell className="w-5 h-5 text-slate-600 dark:text-slate-400 group-hover:text-emerald-500 transition-colors" />
            {notifications > 0 && (
              <span className="absolute top-2 right-2 w-5 h-5 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center font-black border-2 border-white dark:border-slate-900 shadow-lg shadow-red-500/20">
                {notifications}
              </span>
            )}
          </button>

          {/* Theme Toggle */}
          <div className="pl-2 border-l border-slate-100 dark:border-slate-800">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  )
}
