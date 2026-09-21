import React, { useState, useEffect } from 'react'
import { studentApi } from '../../services/api'
import Card from '../../components/common/Card'
import { notify } from '../../components/common/Toast'

export default function StudentProfile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    studentApi.getProfile()
      .then(res => setProfile(res.data.data))
      .catch(() => notify.error('Failed to load profile.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading user profile...</div>
  if (!profile) return <div style={{ padding: '2rem' }}>Profile not found.</div>

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Student Profile</h1>
          <p className="page-subtitle">Personal and academic identification records.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-6)' }}>
        <Card title="Personal Information" subtitle="Registered contact and emergency details">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-sm)' }}>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)', width: '40%' }}>Full Name</td>
                <td style={{ padding: '12px 0', fontWeight: 600 }}>{profile.full_name}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Contact Phone</td>
                <td style={{ padding: '12px 0' }}>{profile.phone || '—'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Residential Address</td>
                <td style={{ padding: '12px 0' }}>{profile.address || '—'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Guardian / Parent Name</td>
                <td style={{ padding: '12px 0' }}>{profile.guardian_name || '—'}</td>
              </tr>
              <tr>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Guardian Contact</td>
                <td style={{ padding: '12px 0' }}>{profile.guardian_phone || '—'}</td>
              </tr>
            </tbody>
          </table>
        </Card>

        <Card title="University Registration" subtitle="Academic enrollment status">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-sm)' }}>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)', width: '40%' }}>Enrollment No.</td>
                <td style={{ padding: '12px 0', fontWeight: 600, color: 'var(--color-primary)' }}>{profile.enrollment_no}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Department</td>
                <td style={{ padding: '12px 0' }}>{profile.department || '—'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Program / Course</td>
                <td style={{ padding: '12px 0' }}>{profile.course || '—'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Semester</td>
                <td style={{ padding: '12px 0' }}>Semester {profile.semester}</td>
              </tr>
              <tr>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Admission Status</td>
                <td style={{ padding: '12px 0' }}>
                  <span className={`badge ${profile.is_admitted ? 'badge-success' : 'badge-warning'}`}>
                    {profile.is_admitted ? 'CONFIRMED' : 'PENDING'}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  )
}
