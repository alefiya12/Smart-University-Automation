/**
 * pages/student/StudentDashboard.jsx — Interactive Student Portal with live routes and metrics.
 */
import React, { useState, useEffect } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import Card from '../../components/common/Card'
import { useAuth } from '../../contexts/AuthContext'
import { studentApi, notificationApi } from '../../services/api'

import StudentAdmission from './StudentAdmission'
import StudentAttendance from './StudentAttendance'
import StudentResults from './StudentResults'
import StudentFees from './StudentFees'
import StudentNotifications from './StudentNotifications'
import StudentProfile from './StudentProfile'

const SIDEBAR_ITEMS = [
  { section: 'Main',       to: '/dashboard/student',              label: 'Overview',       icon: '⊞', exact: true },
  { section: 'My Records', to: '/dashboard/student/admission',    label: 'Admission',      icon: '🎓' },
  {                         to: '/dashboard/student/attendance',   label: 'My Attendance',  icon: '📋' },
  {                         to: '/dashboard/student/results',      label: 'My Results',     icon: '📊' },
  {                         to: '/dashboard/student/fees',         label: 'Fee Status',     icon: '💰' },
  { section: 'Other',      to: '/dashboard/student/notifications',label: 'Notifications',  icon: '🔔' },
  {                         to: '/dashboard/student/profile',      label: 'Profile',        icon: '👤' },
]

export default function StudentDashboard() {
  const { user } = useAuth()

  return (
    <DashboardLayout sidebarItems={SIDEBAR_ITEMS} pageTitle="Student Portal">
      <Routes>
        <Route index element={<StudentOverview user={user} />} />
        <Route path="admission" element={<StudentAdmission />} />
        <Route path="attendance" element={<StudentAttendance />} />
        <Route path="results" element={<StudentResults />} />
        <Route path="fees" element={<StudentFees />} />
        <Route path="notifications" element={<StudentNotifications />} />
        <Route path="profile" element={<StudentProfile />} />
      </Routes>
    </DashboardLayout>
  )
}

function StudentOverview({ user }) {
  const [profile, setProfile] = useState(null)
  const [stats, setStats] = useState({
    attendancePct: '—',
    cgpa: '—',
    feeStatus: '—',
    unreadNotifs: 0,
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const profRes = await studentApi.getProfile()
        const prof = profRes.data.data
        setProfile(prof)

        const [attRes, resRes, feeRes, notifRes] = await Promise.all([
          studentApi.getAttendanceSummary(prof.id).catch(() => ({ data: { data: [] } })),
          studentApi.getResults(prof.id).catch(() => ({ data: { data: [] } })),
          studentApi.getFees().catch(() => ({ data: { data: [] } })),
          notificationApi.getMyNotifications(true).catch(() => ({ data: { data: [] } })),
        ])

        // Attendance %
        const summaries = attRes.data.data || []
        const totalLec = summaries.reduce((acc, s) => acc + s.total_conducted, 0)
        const totalAtt = summaries.reduce((acc, s) => acc + s.lectures_attended, 0)
        const attPct = totalLec > 0 ? `${((totalAtt / totalLec) * 100).toFixed(1)}%` : '100%'

        // CGPA
        const results = resRes.data.data || []
        const latestCgpa = results.length > 0 && results[0].cgpa !== null ? results[0].cgpa.toFixed(2) : '—'

        // Fees
        const fees = feeRes.data.data || []
        const pendingTotal = fees.filter(f => f.status.toLowerCase() !== 'paid').reduce((acc, f) => acc + f.amount, 0)
        const feeStatus = pendingTotal > 0 ? `₹${pendingTotal.toLocaleString()} Due` : 'Cleared'

        // Unread notifs
        const unreadCount = notifRes.data.data ? notifRes.data.data.length : 0

        setStats({
          attendancePct: attPct,
          cgpa: latestCgpa,
          feeStatus: feeStatus,
          unreadNotifs: unreadCount,
        })
      } catch (err) {
        console.error('Failed to load student overview', err)
      } finally {
        setLoading(false)
      }
    }
    loadDashboardData()
  }, [])

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Welcome back, {profile?.full_name || user?.username} 👋</h1>
          <p className="page-subtitle">
            {profile?.course ? `${profile.course} • Semester ${profile.semester}` : 'Your university academic summary at a glance.'}
          </p>
        </div>
      </div>

      {/* Live Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-5)', marginBottom: 'var(--space-6)' }}>
        <Link to="/dashboard/student/attendance" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="stat-card" style={{ cursor: 'pointer', transition: 'transform 0.15s' }}>
            <div className="stat-icon-box" style={{ background: 'var(--color-primary-light)', color: 'var(--color-primary)' }}>📋</div>
            <div>
              <div className="stat-value">{stats.attendancePct}</div>
              <div className="stat-label">Attendance Rate</div>
            </div>
          </div>
        </Link>

        <Link to="/dashboard/student/results" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="stat-card" style={{ cursor: 'pointer', transition: 'transform 0.15s' }}>
            <div className="stat-icon-box" style={{ background: '#F0FDF4', color: 'var(--color-success)' }}>📊</div>
            <div>
              <div className="stat-value">{stats.cgpa}</div>
              <div className="stat-label">Cumulative CGPA</div>
            </div>
          </div>
        </Link>

        <Link to="/dashboard/student/fees" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="stat-card" style={{ cursor: 'pointer', transition: 'transform 0.15s' }}>
            <div className="stat-icon-box" style={{ background: stats.feeStatus.includes('Due') ? '#FEE2E2' : '#F0FDF4', color: stats.feeStatus.includes('Due') ? 'var(--color-danger)' : 'var(--color-success)' }}>💰</div>
            <div>
              <div className="stat-value">{stats.feeStatus}</div>
              <div className="stat-label">Fee Account Status</div>
            </div>
          </div>
        </Link>

        <Link to="/dashboard/student/notifications" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="stat-card" style={{ cursor: 'pointer', transition: 'transform 0.15s' }}>
            <div className="stat-icon-box" style={{ background: '#F0F9FF', color: 'var(--color-info)' }}>🔔</div>
            <div>
              <div className="stat-value">{stats.unreadNotifs}</div>
              <div className="stat-label">Unread Notifications</div>
            </div>
          </div>
        </Link>
      </div>

      {/* Quick Access Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-5)' }}>
        <Card title="Admission Credentials" subtitle="Enrollment verification & letter">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            View your registered enrollment ID ({profile?.enrollment_no || '...'}) and download your verified admission certificate.
          </p>
          <Link to="/dashboard/student/admission" className="btn btn-outline" style={{ display: 'inline-block', textDecoration: 'none' }}>
            View Admission Letter →
          </Link>
        </Card>

        <Card title="Subject Attendance" subtitle="Track 75% examination eligibility">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            Review detailed subject-wise lecture attendance, compliance badges, and daily attendance logs.
          </p>
          <Link to="/dashboard/student/attendance" className="btn btn-outline" style={{ display: 'inline-block', textDecoration: 'none' }}>
            Check Attendance →
          </Link>
        </Card>

        <Card title="Grade Marksheets" subtitle="Dual-Threshold Evaluation">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            View your internal and external marks breakdown, semester SGPA, and download official PDF marksheets.
          </p>
          <Link to="/dashboard/student/results" className="btn btn-outline" style={{ display: 'inline-block', textDecoration: 'none' }}>
            View Marksheet & GPA →
          </Link>
        </Card>
      </div>
    </div>
  )
}
