import React, { useState, useEffect } from 'react'
import { studentApi } from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify } from '../../components/common/Toast'

export default function StudentAttendance() {
  const [profile, setProfile] = useState(null)
  const [summaries, setSummaries] = useState([])
  const [dailyLogs, setDailyLogs] = useState([])
  const [showDaily, setShowDaily] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadAttendance() {
      try {
        const profRes = await studentApi.getProfile()
        const prof = profRes.data.data
        setProfile(prof)

        const [sumRes, dailyRes] = await Promise.all([
          studentApi.getAttendanceSummary(prof.id),
          studentApi.getDailyAttendance(prof.id)
        ])
        setSummaries(sumRes.data.data || [])
        setDailyLogs(dailyRes.data.data || [])
      } catch (err) {
        notify.error('Failed to load attendance records.')
      } finally {
        setLoading(false)
      }
    }
    loadAttendance()
  }, [])

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading attendance records...</div>

  // Overall attendance calculation
  const totalLectures = summaries.reduce((acc, s) => acc + s.total_conducted, 0)
  const totalAttended = summaries.reduce((acc, s) => acc + s.lectures_attended, 0)
  const overallPct = totalLectures > 0 ? ((totalAttended / totalLectures) * 100).toFixed(1) : 0

  const hasWarnings = summaries.some(s => s.warning_flag)

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Subject-Wise Attendance</h1>
          <p className="page-subtitle">Track your attendance compliance across all registered subjects.</p>
        </div>
        <Button variant="outline" onClick={() => setShowDaily(!showDaily)}>
          {showDaily ? 'View Subject Summary' : 'View Daily Log'}
        </Button>
      </div>

      {hasWarnings && (
        <div style={{
          background: 'var(--color-danger-light, #FEE2E2)',
          borderLeft: '4px solid var(--color-danger, #EF4444)',
          padding: '16px 20px',
          borderRadius: '8px',
          marginBottom: 'var(--space-6)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}>
          <span style={{ fontSize: '24px' }}>⚠️</span>
          <div>
            <div style={{ fontWeight: 600, color: '#991B1B' }}>Attendance Advisory Notice</div>
            <div style={{ fontSize: 'var(--text-sm)', color: '#B91C1C' }}>
              One or more subjects have fallen below the mandatory 75% threshold. Please meet with your faculty advisor.
            </div>
          </div>
        </div>
      )}

      {/* Stats Summary Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)', marginBottom: 'var(--space-6)' }}>
        <div className="stat-card">
          <div className="stat-icon-box" style={{ background: 'var(--color-primary-light)', color: 'var(--color-primary)' }}>📊</div>
          <div>
            <div className="stat-value">{overallPct}%</div>
            <div className="stat-label">Cumulative Attendance</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-box" style={{ background: '#F0FDF4', color: 'var(--color-success)' }}>✓</div>
          <div>
            <div className="stat-value">{totalAttended} / {totalLectures}</div>
            <div className="stat-label">Total Lectures Attended</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-box" style={{ background: overallPct >= 75 ? '#F0FDF4' : '#FEE2E2', color: overallPct >= 75 ? 'var(--color-success)' : 'var(--color-danger)' }}>
            {overallPct >= 75 ? '🛡️' : '⚠️'}
          </div>
          <div>
            <div className="stat-value">{overallPct >= 75 ? 'Eligible' : 'At Risk'}</div>
            <div className="stat-label">Exam Eligibility Status</div>
          </div>
        </div>
      </div>

      {!showDaily ? (
        <Card title="Subject Performance Breakdown" subtitle="Minimum 75% required for examination hall ticket generation">
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Semester</th>
                  <th>Lectures Attended</th>
                  <th>Total Lectures</th>
                  <th>Attendance %</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {summaries.length === 0 ? (
                  <tr><td colSpan="6" style={{ textAlign: 'center', padding: '2rem' }}>No attendance records found.</td></tr>
                ) : (
                  summaries.map((s, idx) => (
                    <tr key={s.subject_id || s.subject_name || idx}>
                      <td style={{ fontWeight: 600 }}>{s.subject_name}</td>
                      <td>Semester {s.semester}</td>
                      <td>{s.lectures_attended}</td>
                      <td>{s.total_conducted}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <div style={{ flex: 1, height: '8px', background: 'var(--color-border)', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{
                              width: `${Math.min(s.percentage, 100)}%`,
                              height: '100%',
                              background: s.percentage >= 75 ? 'var(--color-success)' : 'var(--color-danger)',
                              borderRadius: '4px'
                            }} />
                          </div>
                          <span style={{ fontWeight: 600, minWidth: '45px' }}>{s.percentage}%</span>
                        </div>
                      </td>
                      <td>
                        {s.warning_flag ? (
                          <span className="badge badge-danger">Low Attendance</span>
                        ) : (
                          <span className="badge badge-success">Compliant</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        <Card title="Daily Attendance Activity Log" subtitle="History of recent lecture attendance submissions">
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Subject</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {dailyLogs.length === 0 ? (
                  <tr><td colSpan="3" style={{ textAlign: 'center', padding: '2rem' }}>No daily logs found.</td></tr>
                ) : (
                  dailyLogs.map((log, idx) => (
                    <tr key={log.id || `${log.date}-${log.subject_name}-${idx}`}>
                      <td>{log.date}</td>
                      <td style={{ fontWeight: 500 }}>{log.subject_name}</td>
                      <td>
                        <span className={`badge ${log.status === 'Present' ? 'badge-success' : 'badge-danger'}`}>
                          {log.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
