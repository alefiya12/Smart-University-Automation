import React from 'react'
import { Toaster, toast } from 'react-hot-toast'

/**
 * ToastProvider — wrap your app with this once (already in App.jsx via react-hot-toast).
 * Use the exported helpers instead of calling toast() directly everywhere.
 */
export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      gutter={8}
      toastOptions={{
        duration: 4000,
        style: {
          fontFamily: 'var(--font-sans)',
          fontSize: 'var(--text-sm)',
          background: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          border: '1px solid var(--color-border)',
          boxShadow: 'var(--shadow-md)',
          borderRadius: 'var(--radius-md)',
          padding: '10px 14px',
          maxWidth: '380px',
        },
        success: {
          iconTheme: { primary: 'var(--color-success)', secondary: '#fff' },
        },
        error: {
          iconTheme: { primary: 'var(--color-danger)', secondary: '#fff' },
          duration: 5000,
        },
      }}
    />
  )
}

/* ─── Convenience wrappers ─────────────────────────────────────────────────── */
export const notify = {
  success: (msg) => toast.success(msg),
  error:   (msg) => toast.error(msg),
  info:    (msg) => toast(msg, { icon: 'ℹ️' }),
  warning: (msg) => toast(msg, { icon: '⚠️' }),
  loading: (msg) => toast.loading(msg),
  dismiss: (id)  => toast.dismiss(id),
  promise: (promise, msgs) => toast.promise(promise, msgs),
}
