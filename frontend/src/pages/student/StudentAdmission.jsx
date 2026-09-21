import React, { useState, useEffect } from 'react'
import { studentApi } from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify } from '../../components/common/Toast'

export default function StudentAdmission() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    studentApi.getProfile()
      .then(res => setProfile(res.data.data))
      .catch(err => notify.error(err.response?.data?.detail || 'Failed to load admission details'))
      .finally(() => setLoading(false))
  }, [])

  const handleDownloadLetter = () => {
    if (!profile) return
    const token = localStorage.getItem('access_token')
    fetch(`/api/admission/${profile.id}/letter`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(async (res) => {
      if (!res.ok) throw new Error('Letter not found')
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Admission_Letter_${profile.enrollment_no}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    })
    .catch(() => notify.error('Could not download admission letter.'))
  }

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading admission details...</div>
  if (!profile) return <div style={{ padding: '2rem' }}>No admission record found.</div>

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Admission & Enrollment Details</h1>
          <p className="page-subtitle">Your official university registration and admission credentials.</p>
        </div>
        <Button variant="primary" onClick={handleDownloadLetter}>
          📄 Download Admission Letter (PDF)
        </Button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-6)' }}>
        <Card title="Student Identification" subtitle="Official identity within the university system">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-sm)' }}>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Enrollment Number</td>
                <td style={{ padding: '12px 0', fontWeight: 600, color: 'var(--color-primary)' }}>{profile.enrollment_no}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Full Name</td>
                <td style={{ padding: '12px 0', fontWeight: 500 }}>{profile.full_name}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Official Email</td>
                <td style={{ padding: '12px 0' }}>{profile.email}</td>
              </tr>
              <tr>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Academic Standing</td>
                <td style={{ padding: '12px 0' }}>
                  <span className={`badge ${profile.academic_standing === 'Backlog' ? 'badge-danger' : 'badge-success'}`}>
                    {profile.academic_standing || 'Good Standing'}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </Card>

        <Card title="Program & Academic Placement" subtitle="Department and enrolled curriculum">
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 'var(--text-sm)' }}>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Department</td>
                <td style={{ padding: '12px 0', fontWeight: 500 }}>{profile.department || 'Not Assigned'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Course</td>
                <td style={{ padding: '12px 0', fontWeight: 500 }}>{profile.course || 'Not Assigned'}</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Current Semester</td>
                <td style={{ padding: '12px 0' }}>Semester {profile.semester}</td>
              </tr>
              <tr>
                <td style={{ padding: '12px 0', color: 'var(--color-text-secondary)' }}>Admission Year</td>
                <td style={{ padding: '12px 0' }}>{profile.admission_year || 2026}</td>
              </tr>
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  )
}
