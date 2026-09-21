/**
 * components/common/ProtectedRoute.jsx
 * Redirects unauthenticated users to /login and
 * wrong-role users to their own dashboard.
 */
import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

const ROLE_HOME = {
  admin:   '/dashboard/admin',
  faculty: '/dashboard/faculty',
  student: '/dashboard/student',
}

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="auth-wrapper">
        <div style={{ textAlign: 'center' }}>
          <div className="btn-spinner" style={{ width: 28, height: 28, margin: '0 auto', borderWidth: 3 }} />
          <p className="text-secondary" style={{ marginTop: 'var(--space-4)', fontSize: 'var(--text-sm)' }}>
            Loading…
          </p>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    // Redirect to the user's own dashboard
    return <Navigate to={ROLE_HOME[user.role] || '/'} replace />
  }

  return children
}
