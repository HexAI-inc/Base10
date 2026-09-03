import { create } from 'zustand'

interface SyncState {
  status: 'idle' | 'syncing' | 'error'
  pendingCount: number
  setStatus: (status: SyncState['status']) => void
  setPendingCount: (count: number) => void
}

// Tracks the offline attempt queue's state (lib/offline.ts) so any component
// (SyncStatus in the top bar, a future "N pending" badge, etc.) can reflect
// it without threading props through the whole tree.
export const useSyncStore = create<SyncState>((set) => ({
  status: 'idle',
  pendingCount: 0,
  setStatus: (status) => set({ status }),
  setPendingCount: (pendingCount) => set({ pendingCount }),
}))
