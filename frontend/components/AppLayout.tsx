'use client'
import { useState, useEffect } from 'react'
import Sidebar from '@/components/Sidebar'
import TopNavbar from '@/components/TopNavbar'
import EmailVerificationBanner from '@/components/EmailVerificationBanner'
import GlobalModal from '@/components/GlobalModal'
import NetworkBanner from '@/components/NetworkBanner'
import DataUsage from '@/components/DataUsage'
import ScientificCalc from '@/components/ScientificCalc'
import OnboardingWizard from '@/components/OnboardingWizard'
import { usePathname } from 'next/navigation'
import { useAuthStore } from '@/store/authStore'

interface AppLayoutProps {
  children: React.ReactNode
}

export default function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname()
  const { user } = useAuthStore()
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const [showOnboarding, setShowOnboarding] = useState(false)

  useEffect(() => {
    if (user && !user.is_onboarded) {
      // Check if they've already skipped it this session
      const skipped = sessionStorage.getItem('skip_onboarding')
      if (!skipped) {
        setShowOnboarding(true)
      }
    }
  }, [user])

  useEffect(() => {
    setMobileSidebarOpen(false)
  }, [pathname])

  const getPageTitle = () => {
    if (!pathname) return ''
    const titles: Record<string, string> = {
      '/dashboard': 'Dashboard',
      '/practice': 'Practice',
      '/chat': 'AI Tutor',
      '/flashcards': 'Flashcards',
      '/calculator': 'Calculator',
      '/leaderboard': 'Leaderboard',
      '/profile': 'Profile',
      '/settings': 'Settings',
      '/classrooms': 'Classrooms',
      '/admin': 'Admin Console',
    }
    return titles[pathname] || ''
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0F172A] text-slate-900 dark:text-slate-100">
      {showOnboarding && (
        <OnboardingWizard 
          onClose={() => {
            setShowOnboarding(false)
            sessionStorage.setItem('skip_onboarding', 'true')
          }} 
        />
      )}
      <NetworkBanner />
      <EmailVerificationBanner />
      
      {/* Sidebar - Desktop */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Sidebar - Mobile */}
      {mobileSidebarOpen && (
        <>
          <div 
            className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 lg:hidden"
            onClick={() => setMobileSidebarOpen(false)}
          />
          <div className="lg:hidden">
            <Sidebar />
          </div>
        </>
      )}

      {/* Main Content Area */}
      <div className="transition-all duration-300 lg:ml-72">
        {/* Top Navbar */}
        <TopNavbar 
          onMenuClick={() => setMobileSidebarOpen(true)}
          title={getPageTitle()}
        />

        {/* Page Content */}
        <main className="min-h-[calc(100vh-5rem)] p-6 lg:p-10">
          {children}
        </main>

        {/* Footer Info (Data Usage) */}
        <footer className="fixed bottom-8 right-8 z-30">
          <DataUsage />
        </footer>
      </div>

      {/* Global Components */}
      <ScientificCalc />
      <GlobalModal />
    </div>
  )
}
