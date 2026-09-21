import React, { useState, useEffect } from 'react'
import { studentApi } from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify } from '../../components/common/Toast'

export default function StudentResults() {
  const [profile, setProfile] = useState(null)
  const [semester, setSemester] = useState(1)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    async function loadData() {
      try {
        const profRes = await studentApi.getProfile()
        const prof = profRes.data.data
        setProfile(prof)
        setSemester(prof.semester || 1)

        const resRes = await studentApi.getResults(prof.id, prof.semester || 1)
        setResults(resRes.data.data || [])
      } catch (err) {
        notify.error('Failed to load academic results.')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const handleSemesterChange = async (newSem) => {
    setSemester(newSem)
    if (!profile) return
    try {
      setLoading(true)
      const res = await studentApi.getResults(profile.id, newSem)
      setResults(res.data.data || [])
    } catch {
      notify.error('Failed to fetch results for selected semester.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadMarksheet = () => {
    if (!profile || results.length === 0) {
      notify.warn('No published results available for download.')
      return
    }
    setDownloading(true)
    const token = localStorage.getItem('access_token')
    fetch(`/api/results/${profile.id}/semester/${semester}/marksheet`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(async (res) => {
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}))
        throw new Error(errJson.detail || 'Marksheet generation failed')
      }
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Marksheet_${profile.enrollment_no}_Sem${semester}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      notify.success('Marksheet downloaded successfully.')
    })
    .catch(err => notify.error(err.message || 'Could not download marksheet.'))
    .finally(() => setDownloading(false))
  }

  if (loading && !profile) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading examination results...</div>

  const sgpa = results.length > 0 && results[0].sgpa !== null ? results[0].sgpa : '—'
  const cgpa = results.length > 0 && results[0].cgpa !== null ? results[0].cgpa : '—'
  const hasBacklogs = results.some(r => !r.pass_status)

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Examination Results & Grade Card</h1>
          <p className="page-subtitle">Evaluation split (Internal Max 30 / External Max 70) and SGPA computation.</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <select 
            className="form-input" 
            style={{ width: '160px' }}
            value={semester}
            onChange={(e) => handleSemesterChange(parseInt(e.target.value))}
          >
            {[1, 2, 3, 4, 5, 6].map(s => (
              <option key={s} value={s}>Semester {s}</option>
            ))}
          </select>
          <Button variant="primary" onClick={handleDownloadMarksheet} disabled={downloading || results.length === 0}>
            {downloading ? 'Generating PDF...' : '📄 Download Marksheet PDF'}
          </Button>
        </div>
      </div>

      {/* GPA Scorecards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-5)', marginBottom: 'var(--space-6)' }}>
        <div className="stat-card">
          <div className="stat-icon-box" style={{ background: 'var(--color-primary-light)', color: 'var(--color-primary)' }}>🎯</div>
          <div>
            <div className="stat-value">{sgpa}</div>
            <div className="stat-label">Semester SGPA</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-box" style={{ background: '#F0FDF4', color: 'var(--color-success)' }}>⭐</div>
          <div>
            <div className="stat-value">{cgpa}</div>
            <div className="stat-label">Cumulative CGPA</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-box" style={{ background: !hasBacklogs ? '#F0FDF4' : '#FEE2E2', color: !hasBacklogs ? 'var(--color-success)' : 'var(--color-danger)' }}>
            {!hasBacklogs ? '✓' : '⚠️'}
          </div>
          <div>
            <div className="stat-value">{!hasBacklogs ? 'All Cleared' : 'Backlog Alert'}</div>
            <div className="stat-label">Semester Progression Status</div>
          </div>
        </div>
      </div>

      <Card title={`Semester ${semester} Detailed Marksheet`} subtitle="Threshold Passing Criteria: Internal ≥ 12.00 / 30.00 and External ≥ 28.00 / 70.00">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Subject Name</th>
                <th>Internal (/30)</th>
                <th>External (/70)</th>
                <th>Total (/100)</th>
                <th>Grade Letter</th>
                <th>Grade Points</th>
                <th>Result Status</th>
              </tr>
            </thead>
            <tbody>
              {results.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--color-text-secondary)' }}>
                    No published marks found for Semester {semester}. Results may still be under administrative evaluation.
                  </td>
                </tr>
              ) : (
                results.map(r => (
                  <tr key={r.id}>
                    <td style={{ fontWeight: 600 }}>{r.subject}</td>
                    <td>
                      <span style={{ color: r.internal_score >= 12.0 ? 'inherit' : 'var(--color-danger)', fontWeight: r.internal_score < 12 ? 600 : 400 }}>
                        {r.internal_score} {r.internal_score < 12 && '⚠️'}
                      </span>
                    </td>
                    <td>
                      <span style={{ color: r.external_score >= 28.0 ? 'inherit' : 'var(--color-danger)', fontWeight: r.external_score < 28 ? 600 : 400 }}>
                        {r.external_score} {r.external_score < 28 && '⚠️'}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{r.total_marks_obtained}</td>
                    <td>
                      <span style={{ fontWeight: 700, color: r.grade_letter === 'F' ? 'var(--color-danger)' : 'var(--color-primary)' }}>
                        {r.grade_letter}
                      </span>
                    </td>
                    <td>{r.grade_points}</td>
                    <td>
                      <span className={`badge ${r.pass_status ? 'badge-success' : 'badge-danger'}`}>
                        {r.pass_status ? 'PASS' : 'FAIL'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
