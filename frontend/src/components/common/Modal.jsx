import React, { useEffect } from 'react'

/**
 * Modal — Reusable overlay modal component for edit forms.
 *
 * Props:
 *   isOpen  : boolean
 *   onClose : function
 *   title   : string
 *   children: ReactNode
 */
export default function Modal({ isOpen, onClose, title, children }) {
  // Close on Escape key
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') onClose()
    }
    if (isOpen) {
      window.addEventListener('keydown', handleEsc)
      // Prevent body scrolling
      document.body.style.overflow = 'hidden'
    }
    return () => {
      window.removeEventListener('keydown', handleEsc)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div 
      className="fade-in" 
      style={{
        position: 'fixed',
        top: 0, left: 0, right: 0, bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.4)',
        backdropFilter: 'blur(4px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 'var(--space-4)'
      }}
      onClick={onClose}
    >
      <div 
        style={{
          background: 'var(--color-surface)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-xl)',
          width: '100%',
          maxWidth: '500px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
        onClick={e => e.stopPropagation()} // Prevent clicks inside modal from closing it
      >
        {/* Header */}
        <div style={{ 
          padding: 'var(--space-4) var(--space-5)', 
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 600, margin: 0 }}>{title}</h2>
          <button 
            onClick={onClose}
            style={{
              background: 'none', border: 'none', 
              fontSize: '24px', cursor: 'pointer', 
              color: 'var(--color-text-secondary)',
              lineHeight: 1
            }}
          >
            &times;
          </button>
        </div>
        
        {/* Body */}
        <div style={{ padding: 'var(--space-5)', overflowY: 'auto' }}>
          {children}
        </div>
      </div>
    </div>
  )
}
