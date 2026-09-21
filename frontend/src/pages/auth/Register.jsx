/**
 * pages/auth/Register.jsx
 * Centered white card (max-width 420px).
 * Role selector: faculty | student only (Admin never self-registers).
 * Password strength meter, inline validation.
 */
import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import Button from '../../components/common/Button'
import FormInput, { PasswordStrengthMeter } from '../../components/common/FormInput'
import { notify } from '../../components/common/Toast'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    username: '', email: '', password: '', confirmPassword: '', role: 'student',
  })
  const [errors, setErrors]   = useState({})
  const [loading, setLoading] = useState(false)
  const [showPw, setShowPw]   = useState(false)
  const [done, setDone]       = useState(false)

  function set(field) {
    return e => setForm(f => ({ ...f, [field]: e.target.value }))
  }

  function validate() {
    const e = {}
    if (!form.username.trim())             e.username = 'Username is required'
    else if (form.username.length < 3)     e.username = 'At least 3 characters'
    else if (!/^[a-zA-Z0-9_.-]+$/.test(form.username))
                                           e.username = 'Letters, numbers, _ . - only'
    if (!form.email.trim())                e.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Invalid email address'
    if (!form.password)                    e.password = 'Password is required'
    else if (form.password.length < 8)     e.password = 'At least 8 characters'
    else if (!/[A-Z]/.test(form.password)) e.password = 'Must include an uppercase letter'
    else if (!/[0-9]/.test(form.password)) e.password = 'Must include a number'
    if (form.password !== form.confirmPassword) e.confirmPassword = 'Passwords do not match'
    if (!form.role) e.role = 'Please select a role'
    return e
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }
    setErrors({})
    setLoading(true)
    try {
      const { message } = await register({
        username: form.username,
        email: form.email,
        password: form.password,
        role: form.role,
      })
      setDone(true)
      notify.success(message || 'Account created! Check your email.')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed. Please try again.'
      notify.error(msg)
      setErrors({ general: msg })
    } finally {
      setLoading(false)
    }
  }

  if (done) {
    return (
      <div className="auth-wrapper">
        <div className="auth-card" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 'var(--space-4)' }}>📧</div>
          <h2 style={{ fontWeight: 700, marginBottom: 'var(--space-2)' }}>Check Your Email</h2>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-6)' }}>
            We've sent a verification link to <strong>{form.email}</strong>.
            Click the link to activate your account.
          </p>
          <Button variant="secondary" fullWidth onClick={() => navigate('/login')}>
            Go to Login
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        {/* Brand */}
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-6)' }}>
          <div style={{
            width: 44, height: 44,
            background: 'var(--color-primary)',
            borderRadius: 'var(--radius-lg)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto var(--space-3)',
          }}>
            <span style={{ color: '#fff', fontWeight: 800, fontSize: 20 }}>S</span>
          </div>
          <h1 style={{ fontSize: 'var(--text-xl)', fontWeight: 700, margin: 0 }}>Create Account</h1>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginTop: 4 }}>
            Smart University Portal
          </p>
        </div>

        {errors.general && (
          <div className="alert alert-danger" style={{ marginBottom: 'var(--space-4)' }}>
            <span>⚠</span><span>{errors.general}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>

            {/* Role selector — Admin hidden */}
            <div className="form-group">
              <label className="form-label">
                I am a <span className="required">*</span>
              </label>
              <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
                {['student', 'faculty'].map(r => (
                  <label
                    key={r}
                    style={{
                      flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                      gap: 'var(--space-2)', padding: 'var(--space-2) var(--space-3)',
                      border: `1px solid ${form.role === r ? 'var(--color-primary)' : 'var(--color-border-strong)'}`,
                      borderRadius: 'var(--radius-md)',
                      background: form.role === r ? 'var(--color-primary-light)' : 'var(--color-surface)',
                      color: form.role === r ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                      fontWeight: form.role === r ? 600 : 400,
                      fontSize: 'var(--text-sm)',
                      cursor: 'pointer',
                      transition: 'all var(--transition-fast)',
                    }}
                  >
                    <input
                      type="radio" name="role" value={r}
                      checked={form.role === r}
                      onChange={set('role')}
                      style={{ display: 'none' }}
                    />
                    {r === 'student' ? '🎓' : '👨‍🏫'} {r.charAt(0).toUpperCase() + r.slice(1)}
                  </label>
                ))}
              </div>
              {errors.role && <span className="form-error">{errors.role}</span>}
            </div>

            <FormInput id="reg-username" label="Username" type="text"
              placeholder="e.g. john_doe" value={form.username}
              onChange={set('username')} error={errors.username} required
              hint="Letters, numbers, underscores, dots, hyphens"
            />

            <FormInput id="reg-email" label="Email Address" type="email"
              placeholder="you@example.com" value={form.email}
              onChange={set('email')} error={errors.email} required
            />

            <div className="form-group">
              <FormInput id="reg-password" label="Password"
                type={showPw ? 'text' : 'password'}
                placeholder="Min 8 chars, 1 uppercase, 1 number"
                value={form.password} onChange={set('password')}
                error={errors.password} required
                rightIcon={
                  <span onClick={() => setShowPw(s => !s)}
                    style={{ cursor: 'pointer', fontSize: 'var(--text-sm)' }}>
                    {showPw ? '🙈' : '👁'}
                  </span>
                }
              />
              <PasswordStrengthMeter password={form.password} />
            </div>

            <FormInput id="reg-confirm" label="Confirm Password"
              type={showPw ? 'text' : 'password'}
              placeholder="Repeat your password"
              value={form.confirmPassword} onChange={set('confirmPassword')}
              error={errors.confirmPassword} required
            />

            <Button
              type="submit" variant="primary" size="lg" fullWidth
              loading={loading} id="register-submit-btn"
            >
              Create Account
            </Button>
          </div>
        </form>

        <div className="divider" style={{ margin: 'var(--space-5) 0' }} />
        <p style={{ textAlign: 'center', fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: 'var(--color-primary)', fontWeight: 600 }}>
            Sign In
          </Link>
        </p>
      </div>
    </div>
  )
}
