"use client"
import Modal from './Modal'
import { useModalStore } from '@/store/modalStore'

export default function GlobalModal() {
  const { isOpen, title, message, type, onConfirm, confirmText, cancelText, closeModal } = useModalStore()
  
  return (
    <Modal
      isOpen={isOpen}
      onClose={closeModal}
      title={title}
      message={message}
      type={type}
      onConfirm={onConfirm}
      confirmText={confirmText}
      cancelText={cancelText}
    />
  )
}
