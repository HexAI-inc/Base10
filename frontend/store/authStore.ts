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
  // True once zustand has finished reading persisted state from localStorage.
  // Auth guards must wait for this before redirecting on a missing user -
  // on first client render after a hard reload/direct nav, `user` is briefly
  // null even for a logged-in visitor because hydration hasn't run yet.
  hasHydrated: boolean
  setAuth: (token: string, user: any) => void
  setUser: (user: any) => void
  logout: () => void
  setHasHydrated: (value: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      hasHydrated: false,
      setAuth: (token, user) => {
        localStorage.setItem('access_token', token)
        set({ token, user })
      },
      setUser: (user) => set({ user }),
      logout: () => {
        localStorage.removeItem('access_token')
        set({ token: null, user: null })
      },
      setHasHydrated: (value) => set({ hasHydrated: value }),
    }),
    {
      name: 'auth-storage',
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true)
      },
    }
  )
)
