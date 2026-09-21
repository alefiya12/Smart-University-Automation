/**
 * pages/auth/VerifyEmail.jsx — Handles ?token= link from verification email.
 */
import React, { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { authApi } from '../../services/api'
import Button from '../../components/common/Button'

export default function VerifyEmail() {
  const [params]  = useSearchParams()
  const [status, setStatus] = useState('loading') // loading | success | error
  const [message, setMessage] = useState('')

  useEffect(() => {
    const token = params.get('token')
    if (!token) { setStatus('error'); setMessage('No token provided.'); return }
    authApi.verifyEmail(token)
      .then(({ data }) => { setStatus('success'); setMessage(data.message) })
      .catch(err => { setStatus('error'); setMessage(err.response?.data?.detail || 'Verification failed.') })
  }, [])

  return (
    <div className="auth-wrapper">
      <div className="auth-card" style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 48, marginBottom: 'var(--space-4)' }}>
          {status === 'loading' ? '⏳' : status === 'success' ? '✅' : '❌'}
        </div>
        <h2 style={{ fontWeight: 700, marginBottom: 'var(--space-2)' }}>
          {status === 'loading' ? 'Verifying…' : status === 'success' ? 'Email Verified!' : 'Verification Failed'}
        </h2>
        {message && (
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-6)' }}>
            {message}
          </p>
        )}
        {status !== 'loading' && (
          <Link to="/login">
            <Button variant="primary" fullWidth>Go to Login</Button>
          </Link>
        )}
      </div>
    </div>
  )
}
