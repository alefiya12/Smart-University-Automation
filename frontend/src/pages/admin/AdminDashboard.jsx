/**
 * pages/admin/AdminDashboard.jsx — Admin home with stats overview.
 */
import React from 'react'
import { useNavigate, Routes, Route } from 'react-router-dom'
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
import AdminRPAControl from './AdminRPAControl'

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
  { section: 'System',    to: '/dashboard/admin/rpa-control',  label: '⚡ RPA Control',   icon: '🤖' },
  {                        to: '/dashboard/admin/bot-logs',    label: 'Bot Run Logs',   icon: '📜' },
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
        <Route path="rpa-control" element={<AdminRPAControl />} />
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
  const navigate = useNavigate()
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

  const quickActions = [
    {
      icon: '🎓', title: 'Admission Bot',
      desc: 'Upload Excel → auto-create student accounts, enrollment IDs & PDF letters.',
      path: '/dashboard/admin/admission',
      btnLabel: 'Open Admission Workflow',
      color: '#1A56DB', colorLight: '#EBF1FF',
    },
    {
      icon: '📋', title: 'Attendance Bot',
      desc: 'Bulk-upload attendance, compute rolling %, fire low-attendance warnings.',
      path: '/dashboard/admin/attendance',
      btnLabel: 'Open Attendance Workflow',
      color: '#15803D', colorLight: '#F0FDF4',
    },
    {
      icon: '📊', title: 'Results Bot',
      desc: 'Process marks, dual-threshold grading, compute SGPA/CGPA, publish results.',
      path: '/dashboard/admin/results',
      btnLabel: 'Open Results Workflow',
      color: '#B45309', colorLight: '#FFFBEB',
    },
    {
      icon: '🤖', title: 'RPA Control Center',
      desc: 'Trigger all Robot Framework bots, watch live step progress, audit run history.',
      path: '/dashboard/admin/rpa-control',
      btnLabel: '⚡ Launch RPA Control',
      color: '#7C3AED', colorLight: '#F5F3FF',
      highlight: true,
    },
  ]

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
        {quickActions.map(qa => (
          <div key={qa.title} style={{
            background: '#fff',
            border: qa.highlight ? `2px solid ${qa.color}40` : '1px solid var(--color-border)',
            borderRadius: '12px', padding: '20px',
            boxShadow: qa.highlight ? `0 4px 16px ${qa.color}15` : 'var(--shadow-xs)',
            display: 'flex', flexDirection: 'column', gap: '12px',
          }}>
            <div style={{
              width: 44, height: 44, borderRadius: '10px',
              background: qa.colorLight, fontSize: '1.4rem',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>{qa.icon}</div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#111827' }}>{qa.title}</div>
              <div style={{ fontSize: '0.8rem', color: '#6B7280', marginTop: 4, lineHeight: 1.5 }}>{qa.desc}</div>
            </div>
            <button
              onClick={() => navigate(qa.path)}
              style={{
                marginTop: 'auto', padding: '8px 14px',
                borderRadius: '7px', border: 'none',
                background: qa.color, color: '#fff',
                fontWeight: 600, fontSize: '0.8rem',
                cursor: 'pointer', textAlign: 'left',
              }}
            >{qa.btnLabel} →</button>
          </div>
        ))}
      </div>
    </>
  )
}
