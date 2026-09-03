import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: number
  email?: string
  phone_number?: string
  username?: string
  full_name: string
  role?: 'student' | 'teacher' | 'parent' | 'admin'
  is_active?: boolean
  is_verified?: boolean
  verified_at?: string
  created_at?: string
  avatar_url?: string
  ai_quota_limit?: number
  ai_quota_used?: number
  is_onboarded?: boolean
  onboarding_step?: number
}

interface AuthState {
  token: string | null
  user: User | null
  setAuth: (token: string, user: any) => void
  setUser: (user: any) => void
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
      setUser: (user) => set({ user }),
      logout: () => {
        localStorage.removeItem('access_token')
        set({ token: null, user: null })
      },
    }),
    { name: 'auth-storage' }
  )
)
