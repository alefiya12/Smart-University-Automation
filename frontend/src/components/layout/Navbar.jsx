import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

/**
 * Navbar — top navigation bar for authenticated pages.
 * Shows brand, optional page title, and user menu.
 */
export default function Navbar({ pageTitle }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const initials = user
    ? (user.username || user.email || '?').slice(0, 2).toUpperCase()
    : '?'

  const roleBadgeMap = {
    admin: { label: 'Admin', color: 'var(--color-primary)' },
    faculty: { label: 'Faculty', color: 'var(--color-success)' },
    student: { label: 'Student', color: 'var(--color-warning)' },
  }
  const roleMeta = roleBadgeMap[user?.role] || {}

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar" role="banner">
      {/* Brand */}
      <Link to="/" className="navbar-brand">
        <div className="navbar-logo" aria-hidden="true">S</div>
        <span>Smart University</span>
      </Link>

      {/* Optional page title breadcrumb */}
      {pageTitle && (
        <>
          <span style={{ color: 'var(--color-border-strong)', fontSize: 'var(--text-lg)' }}>
            /
          </span>
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', fontWeight: 'var(--font-medium)' }}>
            {pageTitle}
          </span>
        </>
      )}

      <div className="navbar-spacer" />

      {/* Actions */}
      <div className="navbar-actions">
        {user && (
          <>
            {/* Role badge */}
            <span
              className="badge"
              style={{ background: `${roleMeta.color}18`, color: roleMeta.color, border: `1px solid ${roleMeta.color}30` }}
            >
              {roleMeta.label}
            </span>

            {/* User pill */}
            <div className="navbar-user" onClick={handleLogout} title="Click to logout" role="button" tabIndex={0}
                 onKeyDown={e => e.key === 'Enter' && handleLogout()}>
              <div className="navbar-avatar">{initials}</div>
              <span style={{ fontSize: 'var(--text-sm)', fontWeight: 'var(--font-medium)', color: 'var(--color-text-primary)' }}>
                {user.username || user.email}
              </span>
              <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>
                ⎋
              </span>
            </div>
          </>
        )}
      </div>
    </nav>
  )
}
