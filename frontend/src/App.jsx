import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

// Context
import { AuthProvider } from './contexts/AuthContext'

// Components
import { ToastProvider } from './components/common/Toast'
import ProtectedRoute from './components/common/ProtectedRoute'

// Auth pages
import Login          from './pages/auth/Login'
import Register       from './pages/auth/Register'
import VerifyEmail    from './pages/auth/VerifyEmail'
import ForgotPassword from './pages/auth/ForgotPassword'

// Dashboard shells
import AdminDashboard   from './pages/admin/AdminDashboard'
import FacultyDashboard from './pages/faculty/FacultyDashboard'
import StudentDashboard from './pages/student/StudentDashboard'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider />
        <Routes>
          {/* Public */}
          <Route path="/login"           element={<Login />} />
          <Route path="/register"        element={<Register />} />
          <Route path="/verify-email"    element={<VerifyEmail />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />

          {/* Protected — Admin */}
          <Route path="/dashboard/admin/*" element={
            <ProtectedRoute allowedRoles={['admin']}>
              <AdminDashboard />
            </ProtectedRoute>
          } />

          {/* Protected — Faculty */}
          <Route path="/dashboard/faculty/*" element={
            <ProtectedRoute allowedRoles={['faculty', 'admin']}>
              <FacultyDashboard />
            </ProtectedRoute>
          } />

          {/* Protected — Student */}
          <Route path="/dashboard/student/*" element={
            <ProtectedRoute allowedRoles={['student']}>
              <StudentDashboard />
            </ProtectedRoute>
          } />

          {/* Root redirect → login */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
