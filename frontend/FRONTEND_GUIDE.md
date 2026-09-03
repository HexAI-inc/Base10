# 🌐 Base10 Web Frontend Guide (Next.js 14)

## Overview
This guide sets up the Base10 web app using **Next.js 14** with the **App Router**, **TypeScript**, **Tailwind CSS**, and integration with the live API.

---

## 📦 Project Setup

### 1. Initialize Next.js Project
```bash
cd /home/c_jalloh/Documents/IndabaX/base10-frontend/web
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir
```

When prompted:
- ✅ TypeScript
- ✅ Tailwind CSS
- ✅ App Router
- ❌ src directory (keep root)

### 2. Install Core Dependencies
```bash
npm install @tanstack/react-query axios zustand localforage
npm install katex react-katex
npm install react-paystack
npm install lucide-react  # Heroicons alternative with better Tree-shaking
```

### 3. Install Dev Dependencies
```bash
npm install -D @types/katex
```

---

## 🎨 Tailwind Configuration

Replace `tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        emerald: {
          500: '#22C55E',
          600: '#16A34A',
        },
        slate: {
          800: '#1E293B',
          900: '#0F172A',
        },
        gold: {
          400: '#FBBF24',
        },
        ruby: {
          500: '#EF4444',
        },
      },
      fontFamily: {
        outfit: ['Outfit', 'sans-serif'],
        jakarta: ['Plus Jakarta Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config
```

Update `app/layout.tsx` to load fonts:

```typescript
import { Outfit, Plus_Jakarta_Sans } from 'next/font/google'
import './globals.css'

const outfit = Outfit({ 
  subsets: ['latin'],
  variable: '--font-outfit',
})

const jakarta = Plus_Jakarta_Sans({ 
  subsets: ['latin'],
  variable: '--font-jakarta',
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${outfit.variable} ${jakarta.variable}`}>
      <body className="font-jakarta bg-slate-900 text-slate-100">{children}</body>
    </html>
  )
}
```

---

## 🔌 API Client Setup

Create `lib/api.ts`:

```typescript
import axios from 'axios'

const API_BASE_URL = 'https://stingray-app-x7lzo.ondigitalocean.app/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth endpoints
export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post('/auth/register', data),
  login: (email: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username: email, password })),
}

// Question endpoints
export const questionApi = {
  getRandomQuestions: (subject?: string, count: number = 10) =>
    api.get('/questions/random', { params: { subject, count } }),
  submitAnswer: (data: { question_id: number; user_answer: string }) =>
    api.post('/questions/submit', data),
}

// AI endpoints
export const aiApi = {
  getExplanation: (question_id: number, user_answer: string, correct_answer: string) =>
    api.post('/ai/explain', { question_id, user_answer, correct_answer }),
  chat: (message: string, context?: string) =>
    api.post('/ai/chat', { message, context }),
}

// Billing endpoints
export const billingApi = {
  getPlans: () => api.get('/billing/plans'),
  initializePayment: (plan_id: string) => api.post('/billing/initialize', { plan_id }),
}
```

---

## 🧩 Key Components

### Question Card Component

Create `components/QuestionCard.tsx`:

```typescript
'use client'
import { useState } from 'react'
import { Check, X } from 'lucide-react'
import 'katex/dist/katex.min.css'
import { InlineMath, BlockMath } from 'react-katex'

interface QuestionCardProps {
  question: {
    id: number
    question_text: string
    options: string[]
    correct_answer: string
  }
  onSubmit: (answer: string) => void
}

export default function QuestionCard({ question, onSubmit }: QuestionCardProps) {
  const [selected, setSelected] = useState<string | null>(null)
  const [submitted, setSubmitted] = useState(false)
  const [result, setResult] = useState<'correct' | 'incorrect' | null>(null)

  const handleSelect = (option: string) => {
    if (submitted) return
    setSelected(option)
  }

  const handleSubmit = () => {
    if (!selected) return
    setSubmitted(true)
    const isCorrect = selected === question.correct_answer
    setResult(isCorrect ? 'correct' : 'incorrect')
    onSubmit(selected)
  }

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
      <div className="mb-6">
        <InlineMath math={question.question_text} />
      </div>
      
      <div className="space-y-3">
        {question.options.map((option, idx) => {
          const isSelected = selected === option
          const isCorrect = submitted && option === question.correct_answer
          const isWrong = submitted && isSelected && option !== question.correct_answer
          
          return (
            <button
              key={idx}
              onClick={() => handleSelect(option)}
              disabled={submitted}
              className={`
                w-full p-4 rounded-lg border-2 text-left transition-all
                ${isSelected && !submitted ? 'border-emerald-500 bg-emerald-500/10' : 'border-slate-700'}
                ${isCorrect ? 'border-emerald-500 bg-emerald-500/10' : ''}
                ${isWrong ? 'border-ruby-500 bg-ruby-500/10' : ''}
                hover:border-emerald-500/50 disabled:cursor-not-allowed
              `}
            >
              <div className="flex items-center justify-between">
                <span>{option}</span>
                {isCorrect && <Check className="text-emerald-500" />}
                {isWrong && <X className="text-ruby-500" />}
              </div>
            </button>
          )
        })}
      </div>

      {!submitted && (
        <button
          onClick={handleSubmit}
          disabled={!selected}
          className="mt-6 w-full bg-emerald-500 text-white py-3 rounded-lg font-outfit font-bold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-emerald-600 transition"
        >
          Submit Answer
        </button>
      )}

      {submitted && result === 'correct' && (
        <div className="mt-4 p-4 bg-emerald-500/10 border border-emerald-500 rounded-lg">
          <p className="text-emerald-500 font-outfit font-bold">🎉 Correct!</p>
        </div>
      )}

      {submitted && result === 'incorrect' && (
        <div className="mt-4 p-4 bg-ruby-500/10 border border-ruby-500 rounded-lg">
          <p className="text-ruby-500 font-outfit font-bold">Not quite right</p>
          <p className="text-slate-400 text-sm mt-2">The correct answer was: {question.correct_answer}</p>
        </div>
      )}
    </div>
  )
}
```

### Sync Status Indicator

Create `components/SyncStatus.tsx`:

```typescript
'use client'
import { useEffect, useState } from 'react'
import { Wifi, WifiOff, Loader2 } from 'lucide-react'

export default function SyncStatus() {
  const [status, setStatus] = useState<'online' | 'offline' | 'syncing'>('online')

  useEffect(() => {
    const handleOnline = () => setStatus('online')
    const handleOffline = () => setStatus('offline')
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return (
    <div className="flex items-center gap-2 text-sm">
      {status === 'online' && (
        <>
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
          <Wifi className="w-4 h-4 text-emerald-500" />
          <span className="text-slate-400">Synced</span>
        </>
      )}
      {status === 'offline' && (
        <>
          <div className="w-2 h-2 bg-gold-400 rounded-full" />
          <WifiOff className="w-4 h-4 text-gold-400" />
          <span className="text-slate-400">Offline Mode</span>
        </>
      )}
      {status === 'syncing' && (
        <>
          <Loader2 className="w-4 h-4 text-emerald-500 animate-spin" />
          <span className="text-slate-400">Syncing...</span>
        </>
      )}
    </div>
  )
}
```

---

## 🔄 State Management with Zustand

Create `store/authStore.ts`:

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  token: string | null
  user: { id: number; email: string; full_name: string } | null
  setAuth: (token: string, user: any) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setAuth: (token, user) => {
        localStorage.setItem('access_token', token)
        set({ token, user })
      },
      logout: () => {
        localStorage.removeItem('access_token')
        set({ token: null, user: null })
      },
    }),
    { name: 'auth-storage' }
  )
)
```

---

## 📱 PWA Configuration

Create `public/manifest.json`:

```json
{
  "name": "Base10 - WAEC Study App",
  "short_name": "Base10",
  "description": "AI-powered WAEC exam preparation",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0F172A",
  "theme_color": "#22C55E",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

Add to `app/layout.tsx` `<head>`:

```typescript
<link rel="manifest" href="/manifest.json" />
<meta name="theme-color" content="#22C55E" />
```

---

## 🚀 Deployment (Vercel)

1. **Connect GitHub:**
```bash
git init
git add .
git commit -m "Initial Next.js setup"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Deploy to Vercel:**
- Go to [vercel.com](https://vercel.com)
- Import your repository
- Environment variables are auto-detected from `.env.local`
- Deploy!

3. **Environment Variables:**
```env
NEXT_PUBLIC_API_URL=https://stingray-app-x7lzo.ondigitalocean.app/api/v1
```

---

## ✅ Testing Checklist

- [ ] User registration flow works
- [ ] Login persists across page refreshes
- [ ] Questions load from API
- [ ] Answer submission updates score
- [ ] Math equations render with KaTeX
- [ ] Offline mode shows appropriate UI
- [ ] PWA installs on mobile browsers

---

## 📚 Next Steps

1. Build the AI Chat interface (`app/chat/page.tsx`)
2. Add flashcard mode (`app/flashcards/page.tsx`)
3. Integrate Paystack for premium subscriptions
4. Add offline sync with `localforage`
5. Implement progressive image loading for slow connections

**🔗 Live API:** https://stingray-app-x7lzo.ondigitalocean.app
