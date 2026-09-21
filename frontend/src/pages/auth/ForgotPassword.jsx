/**
 * pages/auth/ForgotPassword.jsx
 */
import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { authApi } from '../../services/api'
import Button from '../../components/common/Button'
import FormInput from '../../components/common/FormInput'
import { notify } from '../../components/common/Toast'

export default function ForgotPassword() {
  const [email, setEmail]   = useState('')
  const [error, setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent]     = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!email.trim()) { setError('Email is required'); return }
    setError(''); setLoading(true)
    try {
      await authApi.forgotPassword(email)
      setSent(true)
      notify.success('Reset link sent!')
    } catch {
      notify.error('Something went wrong. Please try again.')
    } finally { setLoading(false) }
  }

  if (sent) return (
    <div className="auth-wrapper">
      <div className="auth-card" style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 48, marginBottom: 'var(--space-4)' }}>📬</div>
        <h2 style={{ fontWeight: 700, marginBottom: 8 }}>Check Your Email</h2>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-6)' }}>
          If <strong>{email}</strong> is registered, a reset link has been sent.
        </p>
        <Link to="/login"><Button variant="secondary" fullWidth>Back to Login</Button></Link>
      </div>
    </div>
  )

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <h2 style={{ fontWeight: 700, marginBottom: 8 }}>Forgot Password</h2>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-6)' }}>
          Enter your email and we'll send a reset link.
        </p>
        <form onSubmit={handleSubmit} noValidate>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <FormInput id="forgot-email" label="Email" type="email"
              placeholder="you@example.com" value={email}
              onChange={e => setEmail(e.target.value)} error={error} required />
            <Button type="submit" variant="primary" fullWidth loading={loading} id="forgot-submit-btn">
              Send Reset Link
            </Button>
          </div>
        </form>
        <div className="divider" style={{ margin: 'var(--space-5) 0' }} />
        <p style={{ textAlign: 'center', fontSize: 'var(--text-sm)' }}>
          <Link to="/login" style={{ color: 'var(--color-primary)', fontWeight: 600 }}>← Back to Login</Link>
        </p>
      </div>
    </div>
  )
}
