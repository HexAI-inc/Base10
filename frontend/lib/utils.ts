import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * FastAPI returns `detail` as a plain string for most errors, but as an
 * array of Pydantic validation-error objects ({type, loc, msg, ...}) for
 * 422s. Extracts a displayable string from either shape.
 */
export function getErrorMessage(err: any, fallback: string): string {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => (typeof d === 'string' ? d : d?.msg)).filter(Boolean).join(', ') || fallback
  }
  return fallback
}
