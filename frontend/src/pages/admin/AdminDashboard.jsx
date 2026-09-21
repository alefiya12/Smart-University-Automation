/**
 * pages/admin/AdminDashboard.jsx — Admin home with stats overview.
 */
import React from 'react'
import { Routes, Route } from 'react-router-dom'
import DashboardLayout from '../../components/layout/DashboardLayout'
import Card from '../../components/common/Card'
import { useAuth } from '../../contexts/AuthContext'
import { managementApi } from '../../services/api'
import AdminAdmission from './AdminAdmission'
import AdminAttendance from './AdminAttendance'
import AdminResults from './AdminResults'
import AdminStudents from './AdminStudents'
import AdminFaculty from './AdminFaculty'
import AdminDepartments from './AdminDepartments'
import AdminCourses from './AdminCourses'
import AdminFees from './AdminFees'
import AdminBotLogs from './AdminBotLogs'
import AdminNotifications from './AdminNotifications'

const SIDEBAR_ITEMS = [
  { section: 'Main',      to: '/dashboard/admin',             label: 'Overview',       icon: '⊞', exact: true },
  { section: 'Automation',to: '/dashboard/admin/admission',   label: 'Admissions',     icon: '🎓' },
  {                        to: '/dashboard/admin/courses',     label: 'Course Settings',icon: '⚙️' },
  {                        to: '/dashboard/admin/attendance',  label: 'Attendance',     icon: '📋' },
  {                        to: '/dashboard/admin/results',     label: 'Results',        icon: '📊' },
  { section: 'Management',to: '/dashboard/admin/students',    label: 'Students',       icon: '👥' },
  {                        to: '/dashboard/admin/faculty',     label: 'Faculty',        icon: '👨‍🏫' },
  {                        to: '/dashboard/admin/departments', label: 'Departments',    icon: '🏛' },
  {                        to: '/dashboard/admin/fees',        label: 'Fees',           icon: '💰' },
  { section: 'System',    to: '/dashboard/admin/bot-logs',    label: 'Bot Run Logs',   icon: '🤖' },
  {                        to: '/dashboard/admin/notifications',label:'Notifications',  icon: '🔔' },
]



export default function AdminDashboard() {
  const { user } = useAuth()

  return (
    <DashboardLayout sidebarItems={SIDEBAR_ITEMS} pageTitle="Dashboard">
      <Routes>
        <Route index element={<AdminOverview user={user} />} />
        <Route path="admission" element={<AdminAdmission />} />
        <Route path="courses" element={<AdminCourses />} />
        <Route path="attendance" element={<AdminAttendance />} />
        <Route path="results" element={<AdminResults />} />
        <Route path="students" element={<AdminStudents />} />
        <Route path="faculty" element={<AdminFaculty />} />
        <Route path="departments" element={<AdminDepartments />} />
        <Route path="fees" element={<AdminFees />} />
        <Route path="bot-logs" element={<AdminBotLogs />} />
        <Route path="notifications" element={<AdminNotifications />} />
      </Routes>
    </DashboardLayout>
  )
}

function Placeholder({ title, desc }) {
  return (
    <div className="page-header">
      <div>
        <h1 className="page-title">{title}</h1>
        <p className="page-subtitle">{desc}</p>
      </div>
    </div>
  )
}

function AdminOverview({ user }) {
  const [statsData, setStatsData] = React.useState([
    { label: 'Total Students',   value: '—', icon: '🎓', color: 'var(--color-primary-light)',   iconColor: 'var(--color-primary)' },
    { label: 'Faculty Members',  value: '—', icon: '👨‍🏫', color: '#F0FDF4', iconColor: 'var(--color-success)' },
    { label: 'Bot Runs Today',   value: '—', icon: '🤖', color: '#F0F9FF', iconColor: 'var(--color-info)' },
    { label: 'Pending Reviews',  value: '—', icon: '⚠️', color: 'var(--color-warning-bg)',      iconColor: 'var(--color-warning)' },
  ])

  React.useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await managementApi.getDashboardStats()
        const data = res.data.data
        setStatsData([
          { label: 'Total Students',   value: data.total_students, icon: '🎓', color: 'var(--color-primary-light)',   iconColor: 'var(--color-primary)' },
          { label: 'Faculty Members',  value: data.faculty_members, icon: '👨‍🏫', color: '#F0FDF4', iconColor: 'var(--color-success)' },
          { label: 'Bot Runs Today',   value: data.bot_runs_today, icon: '🤖', color: '#F0F9FF', iconColor: 'var(--color-info)' },
          { label: 'Pending Reviews',  value: data.pending_reviews, icon: '⚠️', color: 'var(--color-warning-bg)',      iconColor: 'var(--color-warning)' },
        ])
      } catch (err) {
        console.error("Failed to fetch dashboard stats", err)
      }
    }
    fetchStats()
  }, [])

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Welcome back, {user?.username} 👋</h1>
          <p className="page-subtitle">Here's what's happening at Smart University today.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-5)', marginBottom: 'var(--space-8)' }}>
        {statsData.map(s => (
          <div key={s.label} className="stat-card">
            <div className="stat-icon-box" style={{ background: s.color, color: s.iconColor }}>
              {s.icon}
            </div>
            <div>
              <div className="stat-value">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-5)' }}>
        <Card title="Admission Automation" subtitle="Upload Excel → bulk-process admissions">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            Run the admission bot to auto-create student accounts, generate enrollment numbers, and send confirmation emails.
          </p>
        </Card>

        <Card title="Attendance Automation" subtitle="Upload attendance Excel files">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            Bulk-upload attendance, auto-calculate percentages, and send low-attendance warning emails to students.
          </p>
        </Card>

        <Card title="Result Processing" subtitle="Grade calculation & marksheets">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            Process marks Excel, compute SGPA/CGPA, generate PDF marksheets, and publish results with email notification.
          </p>
        </Card>

        <Card title="Bot Run Logs" subtitle="Audit every automation run">
          <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', marginBottom: 'var(--space-4)' }}>
            View execution history, records processed, duration, and links to Robot Framework HTML logs.
          </p>
        </Card>
      </div>
    </>
  )
}
