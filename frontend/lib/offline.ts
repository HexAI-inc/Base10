import localforage from 'localforage'
import { syncApi } from './api'
import { useSyncStore } from '@/store/syncStore'

export interface PendingAttempt {
  question_id: number
  selected_option: number
  is_correct: boolean
  attempted_at: string
  time_taken_ms?: number
  confidence_level?: number
}

const attemptsStore = localforage.createInstance({
  name: 'base10-offline',
  storeName: 'pending_attempts',
})

const questionsCacheStore = localforage.createInstance({
  name: 'base10-offline',
  storeName: 'cached_questions',
})

/** Cache the last successfully-fetched question set for a given
 * subject+difficulty, so practice can still start while offline. */
export async function cacheQuestions(key: string, questions: unknown[]): Promise<void> {
  await questionsCacheStore.setItem(key, questions)
}

export async function getCachedQuestions<T = unknown>(key: string): Promise<T[] | null> {
  return questionsCacheStore.getItem<T[]>(key)
}

/** Stable per-device id, persisted across sessions - required by /sync/push. */
export function getDeviceId(): string {
  if (typeof window === 'undefined') return 'server'
  let id = window.localStorage.getItem('device_id')
  if (!id) {
    id = (typeof crypto !== 'undefined' && 'randomUUID' in crypto)
      ? crypto.randomUUID()
      : `device_${Date.now()}_${Math.random().toString(36).slice(2)}`
    window.localStorage.setItem('device_id', id)
  }
  return id
}

/** Save an attempt locally. Called before any network attempt, so nothing is
 * lost regardless of connectivity - a subsequent flush is what actually
 * reaches the server. */
export async function queueAttempt(attempt: PendingAttempt): Promise<void> {
  const key = `${attempt.question_id}_${attempt.attempted_at}_${Math.random().toString(36).slice(2, 8)}`
  await attemptsStore.setItem(key, attempt)
  await refreshPendingCount()
}

export async function getPendingCount(): Promise<number> {
  const keys = await attemptsStore.keys()
  return keys.length
}

async function refreshPendingCount(): Promise<void> {
  useSyncStore.getState().setPendingCount(await getPendingCount())
}

let flushing = false

/** Push everything queued locally via /sync/push. Best-effort: on failure
 * (offline, server error) the queue is left intact for the next attempt -
 * on success the whole pushed batch is cleared (the API only reports counts,
 * not which attempts failed, so partial-failure handling isn't possible
 * without a richer response contract). */
export async function flushPendingAttempts(): Promise<void> {
  if (flushing) return
  if (typeof navigator !== 'undefined' && !navigator.onLine) return

  const keys = await attemptsStore.keys()
  if (keys.length === 0) return

  flushing = true
  useSyncStore.getState().setStatus('syncing')

  try {
    const attempts: PendingAttempt[] = []
    for (const key of keys) {
      const value = await attemptsStore.getItem<PendingAttempt>(key)
      if (value) attempts.push(value)
    }

    await syncApi.push(attempts, getDeviceId())

    await Promise.all(keys.map((key) => attemptsStore.removeItem(key)))
    useSyncStore.getState().setStatus('idle')
  } catch (err) {
    console.warn('Sync flush failed, will retry later:', err)
    useSyncStore.getState().setStatus('error')
  } finally {
    flushing = false
    await refreshPendingCount()
  }
}

/** Call once from a top-level client component (AppLayout) so the queue
 * drains automatically on load and whenever connectivity returns. */
export function initOfflineSync(): () => void {
  refreshPendingCount()
  flushPendingAttempts()

  const handleOnline = () => flushPendingAttempts()
  window.addEventListener('online', handleOnline)
  return () => window.removeEventListener('online', handleOnline)
}
