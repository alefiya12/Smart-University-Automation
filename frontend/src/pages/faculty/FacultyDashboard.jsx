/**
 * pages/faculty/FacultyDashboard.jsx — Active Faculty Portal with child routing.
 */
import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import Card from '../../components/common/Card'
import { useAuth } from '../../contexts/AuthContext'

import FacultyAttendance from './FacultyAttendance'
import FacultyMarks from './FacultyMarks'
import FacultyStudents from './FacultyStudents'
import FacultyProfile from './FacultyProfile'

const SIDEBAR_ITEMS = [
  { section: 'Main',        to: '/dashboard/faculty',               label: 'Overview',     icon: '⊞', exact: true },
  { section: 'My Classes',  to: '/dashboard/faculty/attendance',    label: 'Attendance',   icon: '📋' },
  {                          to: '/dashboard/faculty/marks',         label: 'Upload Marks', icon: '📊' },
  { section: 'Students',    to: '/dashboard/faculty/students',      label: 'My Students',  icon: '👥' },
  { section: 'Account',     to: '/dashboard/faculty/profile',       label: 'Profile',      icon: '👤' },
]

export default function FacultyDashboard() {
  const { user } = useAuth()

  return (
    <DashboardLayout sidebarItems={SIDEBAR_ITEMS} pageTitle="Faculty Dashboard">
      <Routes>
        <Route index element={<FacultyOverview user={user} />} />
        <Route path="attendance" element={<FacultyAttendance />} />
        <Route path="marks" element={<FacultyMarks />} />
        <Route path="students" element={<FacultyStudents />} />
        <Route path="profile" element={<FacultyProfile />} />
      </Routes>
    </DashboardLayout>
  )
}

function FacultyOverview({ user }) {
  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Welcome, Professor {user?.username} 👋</h1>
          <p className="page-subtitle">Manage attendance logs, examination marks, and review academic rosters.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-6)' }}>
        <Card title="Class Attendance" subtitle="Daily lecture recording">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            Upload subject-wise attendance spreadsheets. The system automatically flags students under 75% and sends warning alerts.
          </p>
          <Link to="/dashboard/faculty/attendance" className="btn btn-primary" style={{ display: 'inline-block', textDecoration: 'none' }}>
            Upload Attendance Spreadsheet →
          </Link>
        </Card>

        <Card title="Examination Marks" subtitle="Dual-Threshold Evaluation">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            Submit marks with Internal (Max 30, Pass ≥ 12) and External (Max 70, Pass ≥ 28) thresholds for automated grading.
          </p>
          <Link to="/dashboard/faculty/marks" className="btn btn-primary" style={{ display: 'inline-block', textDecoration: 'none' }}>
            Upload Examination Marks →
          </Link>
        </Card>

        <Card title="Enrolled Students" subtitle="Class rosters and standing">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            Browse registered students in your department courses, review their active semesters, and check for academic backlog flags.
          </p>
          <Link to="/dashboard/faculty/students" className="btn btn-outline" style={{ display: 'inline-block', textDecoration: 'none' }}>
            View Student Roster →
          </Link>
        </Card>
      </div>
    </div>
  )
}
