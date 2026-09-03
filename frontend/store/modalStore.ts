"use client"
import { create } from 'zustand'

interface ModalState {
  isOpen: boolean
  title?: string
  message: string
  type: 'success' | 'error' | 'info' | 'confirm'
  onConfirm?: () => void
  confirmText?: string
  cancelText?: string
}

interface ModalStore extends ModalState {
  showModal: (config: Omit<ModalState, 'isOpen'>) => void
  showSuccess: (message: string, title?: string) => void
  showError: (message: string, title?: string) => void
  showInfo: (message: string, title?: string) => void
  showConfirm: (message: string, onConfirm: () => void, title?: string) => void
  closeModal: () => void
}

export const useModalStore = create<ModalStore>((set) => ({
  isOpen: false,
  message: '',
  type: 'info',
  
  showModal: (config) => set({ ...config, isOpen: true }),
  
  showSuccess: (message, title) => set({ 
    isOpen: true, 
    message, 
    title: title || 'Success', 
    type: 'success',
    onConfirm: undefined
  }),
  
  showError: (message, title) => set({ 
    isOpen: true, 
    message, 
    title: title || 'Error', 
    type: 'error',
    onConfirm: undefined
  }),
  
  showInfo: (message, title) => set({ 
    isOpen: true, 
    message, 
    title: title || 'Info', 
    type: 'info',
    onConfirm: undefined
  }),
  
  showConfirm: (message, onConfirm, title) => set({ 
    isOpen: true, 
    message, 
    title: title || 'Confirm', 
    type: 'confirm',
    onConfirm
  }),
  
  closeModal: () => set({ isOpen: false })
}))
