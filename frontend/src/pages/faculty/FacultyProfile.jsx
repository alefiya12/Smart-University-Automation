import React, { useState, useEffect } from 'react'
import { facultyApi } from '../../services/api'
import Card from '../../components/common/Card'
import { notify } from '../../components/common/Toast'

export default function FacultyProfile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    facultyApi.getProfile()
      .then(res => setProfile(res.data.data))
      .catch(() => notify.error('Failed to load faculty profile'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading faculty profile...</div>
  if (!profile) return <div style={{ padding: '2rem' }}>Faculty profile not found.</div>

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Faculty Profile</h1>
          <p className="page-subtitle">Your university faculty identification and department assignment.</p>
        </div>
      </div>

      <div style={{ maxWidth: '650px' }}>
        <Card title="Official Credentials" subtitle="Faculty information record">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-sm)' }}>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)', width: '35%' }}>Employee ID</td>
                <td style={{ padding: '12px 0', fontWeight: 600, color: 'var(--color-primary)' }}>{profile.employee_id}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Faculty Name</td>
                <td style={{ padding: '12px 0', fontWeight: 600 }}>{profile.name}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Designation</td>
                <td style={{ padding: '12px 0' }}>{profile.designation}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Department</td>
                <td style={{ padding: '12px 0' }}>{profile.department || 'General'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Email Address</td>
                <td style={{ padding: '12px 0' }}>{profile.email}</td>
              </tr>
              <tr>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Contact Phone</td>
                <td style={{ padding: '12px 0' }}>{profile.phone || '—'}</td>
              </tr>
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  )
}
