'use client'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Brain, MessageCircle, BookOpen, Target } from 'lucide-react'

export default function Navigation() {
  const pathname = usePathname()

  const links = [
    { href: '/practice', label: 'Practice', icon: Target },
    { href: '/flashcards', label: 'Flashcards', icon: BookOpen },
    { href: '/chat', label: 'AI Tutor', icon: MessageCircle },
  ]

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-slate-800 border-t border-slate-700 md:hidden z-50">
      <div className="flex items-center justify-around py-3">
        {links.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href
          return (
            <Link
              key={href}
              href={href}
              className={`flex flex-col items-center gap-1 px-4 py-2 rounded-lg transition ${
                isActive
                  ? 'text-emerald-500'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs font-medium">{label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
