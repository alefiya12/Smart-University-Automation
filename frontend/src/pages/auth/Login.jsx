/**
 * pages/auth/Login.jsx
 * Centered white card (max-width 420px) with inline validation.
 * On success → redirects to role-based dashboard.
 */
import React, { useState } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import Button from '../../components/common/Button'
import FormInput from '../../components/common/FormInput'
import { notify } from '../../components/common/Toast'

const ROLE_HOME = {
  admin:   '/dashboard/admin',
  faculty: '/dashboard/faculty',
  student: '/dashboard/student',
}

export default function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const location  = useLocation()

  const [form, setForm] = useState({ username: '', password: '' })
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  function validate() {
    const e = {}
    if (!form.username.trim()) e.username = 'Username or email is required'
    if (!form.password)        e.password = 'Password is required'
    return e
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setErrors({})
    setLoading(true)
    try {
      const role = await login(form.username, form.password)
      const from = location.state?.from?.pathname || ROLE_HOME[role] || '/'
      notify.success('Welcome back!')
      navigate(from, { replace: true })
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please try again.'
      notify.error(msg)
      setErrors({ general: msg })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        {/* Brand */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)' }}>
          <div style={{
            width: 48, height: 48,
            background: 'var(--color-primary)',
            borderRadius: 'var(--radius-lg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto var(--space-4)',
          }}>
            <span style={{ color: '#fff', fontWeight: 800, fontSize: 22 }}>S</span>
          </div>
          <h1 style={{ fontSize: 'var(--text-2xl)', fontWeight: 700, margin: 0 }}>
            Smart University
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginTop: 'var(--space-1)' }}>
            Sign in to your account
          </p>
        </div>

        {/* Error banner */}
        {errors.general && (
          <div className="alert alert-danger" style={{ marginBottom: 'var(--space-5)' }}>
            <span>⚠</span>
            <span>{errors.general}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <FormInput
              id="login-username"
              label="Username or Email"
              type="text"
              placeholder="Enter your username or email"
              value={form.username}
              onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
              error={errors.username}
              required
              autoComplete="username"
              autoFocus
            />

            <FormInput
              id="login-password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              value={form.password}
              onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              error={errors.password}
              required
              autoComplete="current-password"
              rightIcon={
                <span
                  onClick={() => setShowPassword(s => !s)}
                  style={{ cursor: 'pointer', fontSize: 'var(--text-sm)', userSelect: 'none' }}
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? '🙈' : '👁'}
                </span>
              }
            />

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Link
                to="/forgot-password"
                style={{ fontSize: 'var(--text-sm)', color: 'var(--color-primary)' }}
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              loading={loading}
              id="login-submit-btn"
            >
              Sign In
            </Button>
          </div>
        </form>

        <div className="divider" style={{ margin: 'var(--space-6) 0' }} />

        <p style={{ textAlign: 'center', fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: 'var(--color-primary)', fontWeight: 600 }}>
            Register
          </Link>
        </p>
      </div>
    </div>
  )
}
