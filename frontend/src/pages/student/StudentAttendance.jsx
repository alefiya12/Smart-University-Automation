import React, { useState, useEffect, useMemo } from 'react'
import { studentApi } from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify } from '../../components/common/Toast'

export default function StudentAttendance() {
  const [profile, setProfile] = useState(null)
  const [summaries, setSummaries] = useState([])
  const [dailyLogs, setDailyLogs] = useState([])
  const [activeTab, setActiveTab] = useState('both') // 'both', 'breakdown', 'logs'
  const [filterSubject, setFilterSubject] = useState('ALL')
  const [filterStatus, setFilterStatus] = useState('ALL')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadAttendance() {
      try {
        const profRes = await studentApi.getProfile()
        const prof = profRes.data?.data || profRes.data
        setProfile(prof)

        if (prof?.id) {
          const [sumRes, dailyRes] = await Promise.all([
            studentApi.getAttendanceSummary(prof.id),
            studentApi.getDailyAttendance(prof.id)
          ])
          setSummaries(sumRes.data?.data || sumRes.data || [])
          setDailyLogs(dailyRes.data?.data || dailyRes.data || [])
        }
      } catch (err) {
        notify.error('Failed to load attendance records.')
      } finally {
        setLoading(false)
      }
    }
    loadAttendance()
  }, [])

  // Defensively deduplicate subjects by normalized subject name
  const deduplicatedSummaries = useMemo(() => {
    const map = new Map()
    for (const s of summaries) {
      const name = (s.subject_name || s.subject || '').trim()
      if (!name) continue
      const normKey = name.toLowerCase()

      const currentAttended = s.lectures_attended ?? s.present ?? 0
      const currentTotal = s.total_conducted ?? s.total_classes ?? 0

      if (!map.has(normKey)) {
        map.set(normKey, {
          ...s,
          subject_name: name,
          subject: name,
          lectures_attended: currentAttended,
          present: currentAttended,
          total_conducted: currentTotal,
          total_classes: currentTotal,
        })
      } else {
        const existing = map.get(normKey)
        const mergedAttended = Math.max(existing.lectures_attended, currentAttended)
        const mergedTotal = Math.max(existing.total_conducted, currentTotal)
        const mergedPct = mergedTotal > 0 ? Number(((mergedAttended / mergedTotal) * 100).toFixed(1)) : 0
        map.set(normKey, {
          ...existing,
          lectures_attended: mergedAttended,
          present: mergedAttended,
          total_conducted: mergedTotal,
          total_classes: mergedTotal,
          percentage: mergedPct,
          cumulative_percentage: mergedPct,
          warning_flag: mergedPct < 75,
          warning: mergedPct < 75,
        })
      }
    }
    return Array.from(map.values())
  }, [summaries])

  // Overall attendance calculation
  const totalLectures = deduplicatedSummaries.reduce((acc, s) => acc + (s.total_conducted ?? s.total_classes ?? 0), 0)
  const totalAttended = deduplicatedSummaries.reduce((acc, s) => acc + (s.lectures_attended ?? s.present ?? 0), 0)
  let overallPct = '0.0'
  if (totalLectures > 0) {
    overallPct = ((totalAttended / totalLectures) * 100).toFixed(1)
  } else if (deduplicatedSummaries.length > 0) {
    const avg = deduplicatedSummaries.reduce((acc, s) => acc + (s.percentage ?? s.cumulative_percentage ?? 0), 0) / deduplicatedSummaries.length
    overallPct = avg.toFixed(1)
  }

  const hasWarnings = deduplicatedSummaries.some(s => {
    const pct = s.percentage ?? s.cumulative_percentage ?? (s.total_conducted > 0 ? (s.lectures_attended / s.total_conducted) * 100 : 0)
    return Number(pct) < 75 || s.warning_flag || s.warning || s.attendance_warning_flag
  })

  const isFullyEligible = Number(overallPct) >= 75 && !hasWarnings
  const isSubjectDeficit = Number(overallPct) >= 75 && hasWarnings
  const eligibilityStatus = isFullyEligible ? 'Eligible' : (isSubjectDeficit ? 'Subject Deficit' : 'At Risk')
  const eligibilityBg = isFullyEligible ? '#F0FDF4' : (isSubjectDeficit ? '#FEFCE8' : '#FEE2E2')
  const eligibilityColor = isFullyEligible ? 'var(--color-success)' : (isSubjectDeficit ? '#CA8A04' : 'var(--color-danger)')

  // Filtered daily logs
  const filteredDailyLogs = useMemo(() => {
    return (dailyLogs || []).filter(log => {
      const matchSubject = filterSubject === 'ALL' || (log.subject_name || log.subject) === filterSubject
      const logStatus = String(log.status || '').toLowerCase()
      const matchStatus = filterStatus === 'ALL' || logStatus === filterStatus.toLowerCase()
      return matchSubject && matchStatus
    })
  }, [dailyLogs, filterSubject, filterStatus])

  // Unique subject list for filter dropdown
  const uniqueSubjects = useMemo(() => {
    const set = new Set()
    ;(dailyLogs || []).forEach(l => {
      const name = l.subject_name || l.subject
      if (name) set.add(name)
    })
    return Array.from(set)
  }, [dailyLogs])

  const formatDateDisplay = (log) => {
    if (log.formatted_date) {
      return (
        <div>
          <div style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{log.formatted_date}</div>
          {log.day_of_week && (
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
              {log.day_of_week}
            </div>
          )}
        </div>
      )
    }
    // Fallback if formatted_date is not present
    try {
      const d = new Date(log.date)
      if (!isNaN(d.getTime())) {
        const dateStr = d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })
        const dayStr = d.toLocaleDateString('en-GB', { weekday: 'long' })
        return (
          <div>
            <div style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{dateStr}</div>
            <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>{dayStr}</div>
          </div>
        )
      }
    } catch {
      // ignore
    }
    return <span>{log.date}</span>
  }

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading attendance records...</div>

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Subject-Wise Attendance</h1>
          <p className="page-subtitle">Track your attendance compliance across all registered curriculum subjects.</p>
        </div>
        <div style={{ display: 'flex', gap: '8px', background: 'var(--color-bg-secondary)', padding: '4px', borderRadius: '8px', border: '1px solid var(--color-border)' }}>
          <button
            onClick={() => setActiveTab('both')}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              border: 'none',
              fontSize: 'var(--text-sm)',
              fontWeight: 500,
              cursor: 'pointer',
              background: activeTab === 'both' ? 'var(--color-primary)' : 'transparent',
              color: activeTab === 'both' ? '#FFF' : 'var(--color-text-secondary)',
              transition: 'all 0.15s ease-in-out'
            }}
          >
            📑 Complete View
          </button>
          <button
            onClick={() => setActiveTab('breakdown')}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              border: 'none',
              fontSize: 'var(--text-sm)',
              fontWeight: 500,
              cursor: 'pointer',
              background: activeTab === 'breakdown' ? 'var(--color-primary)' : 'transparent',
              color: activeTab === 'breakdown' ? '#FFF' : 'var(--color-text-secondary)',
              transition: 'all 0.15s ease-in-out'
            }}
          >
            📊 Performance Breakdown
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            style={{
              padding: '6px 14px',
              borderRadius: '6px',
              border: 'none',
              fontSize: 'var(--text-sm)',
              fontWeight: 500,
              cursor: 'pointer',
              background: activeTab === 'logs' ? 'var(--color-primary)' : 'transparent',
              color: activeTab === 'logs' ? '#FFF' : 'var(--color-text-secondary)',
              transition: 'all 0.15s ease-in-out'
            }}
          >
            📅 Daily Activity Logs
          </button>
        </div>
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
          <div className="stat-icon-box" style={{ background: eligibilityBg, color: eligibilityColor }}>
            {isFullyEligible ? '🛡️' : (isSubjectDeficit ? '⚠️' : '❌')}
          </div>
          <div>
            <div className="stat-value" style={{ color: eligibilityColor }}>{eligibilityStatus}</div>
            <div className="stat-label">Exam Eligibility Status</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-box" style={{ background: '#F8FAFC', color: 'var(--color-text-secondary)' }}>📚</div>
          <div>
            <div className="stat-value">{deduplicatedSummaries.length}</div>
            <div className="stat-label">Subjects Enrolled</div>
          </div>
        </div>
      </div>

      {/* SECTION 1: Subject Performance Breakdown */}
      {(activeTab === 'both' || activeTab === 'breakdown') && (
        <Card
          title="Subject Performance Breakdown"
          subtitle="Minimum 75% required for examination hall ticket generation"
          style={{ marginBottom: 'var(--space-6)' }}
        >
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
                {deduplicatedSummaries.length === 0 ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--color-text-secondary)' }}>
                      No attendance records found.
                    </td>
                  </tr>
                ) : (
                  deduplicatedSummaries.map((s, idx) => {
                    const subName = s.subject_name || s.subject || 'Subject'
                    const semNum = s.semester || (profile && profile.semester) || 1
                    const attended = s.lectures_attended ?? s.present ?? 0
                    const total = s.total_conducted ?? s.total_classes ?? 0
                    const pct = Number(s.percentage ?? s.cumulative_percentage ?? (total > 0 ? (attended / total) * 100 : 0)).toFixed(1)
                    const isWarn = s.warning_flag || s.warning || (total > 0 && Number(pct) < 75)

                    return (
                      <tr key={s.subject_id || `${subName}-${idx}`}>
                        <td style={{ fontWeight: 600 }}>{subName}</td>
                        <td>Semester {semNum}</td>
                        <td style={{ fontWeight: 500 }}>{attended}</td>
                        <td>{total}</td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <div style={{ flex: 1, minWidth: '90px', height: '8px', background: 'var(--color-border)', borderRadius: '4px', overflow: 'hidden' }}>
                              <div style={{
                                width: `${Math.min(Number(pct), 100)}%`,
                                height: '100%',
                                background: Number(pct) >= 75 ? 'var(--color-success)' : 'var(--color-danger)',
                                borderRadius: '4px',
                                transition: 'width 0.3s ease'
                              }} />
                            </div>
                            <span style={{ fontWeight: 600, minWidth: '45px' }}>{pct}%</span>
                          </div>
                        </td>
                        <td>
                          {isWarn ? (
                            <span className="badge badge-danger">Low Attendance</span>
                          ) : (
                            <span className="badge badge-success">Compliant</span>
                          )}
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* SECTION 2: Daily Attendance Activity Log */}
      {(activeTab === 'both' || activeTab === 'logs') && (
        <Card
          title="Daily Attendance Activity Log"
          subtitle="Chronological history of recorded lecture attendance with standardized date and badge formats"
        >
          {/* Filter Bar */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>Filter Subject:</span>
              <select
                className="form-input"
                style={{ width: 'auto', minWidth: '160px', padding: '6px 12px', fontSize: 'var(--text-sm)' }}
                value={filterSubject}
                onChange={e => setFilterSubject(e.target.value)}
              >
                <option value="ALL">All Subjects ({uniqueSubjects.length})</option>
                {uniqueSubjects.map(sub => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-text-secondary)', textTransform: 'uppercase' }}>Filter Status:</span>
              <select
                className="form-input"
                style={{ width: 'auto', minWidth: '130px', padding: '6px 12px', fontSize: 'var(--text-sm)' }}
                value={filterStatus}
                onChange={e => setFilterStatus(e.target.value)}
              >
                <option value="ALL">All Statuses</option>
                <option value="present">Present Only</option>
                <option value="absent">Absent Only</option>
              </select>
            </div>

            {(filterSubject !== 'ALL' || filterStatus !== 'ALL') && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => { setFilterSubject('ALL'); setFilterStatus('ALL') }}
              >
                Reset Filters
              </Button>
            )}

            <div style={{ marginLeft: 'auto', fontSize: 'var(--text-xs)', color: 'var(--color-text-muted)' }}>
              Showing {filteredDailyLogs.length} of {dailyLogs.length} lecture entries
            </div>
          </div>

          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '22%' }}>Date & Day</th>
                  <th style={{ width: '26%' }}>Subject</th>
                  <th style={{ width: '18%' }}>Semester</th>
                  <th style={{ width: '18%' }}>Session Type</th>
                  <th style={{ width: '16%' }}>Attendance Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredDailyLogs.length === 0 ? (
                  <tr>
                    <td colSpan="5" style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--color-text-secondary)' }}>
                      No daily logs match the selected filter criteria.
                    </td>
                  </tr>
                ) : (
                  filteredDailyLogs.map((log, idx) => {
                    const isPresent = String(log.status).toLowerCase() === 'present'
                    return (
                      <tr key={log.id || `${log.date}-${log.subject_name}-${idx}`}>
                        <td>{formatDateDisplay(log)}</td>
                        <td style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
                          {log.subject_name || log.subject}
                        </td>
                        <td>Semester {log.semester || (profile && profile.semester) || 1}</td>
                        <td style={{ color: 'var(--color-text-secondary)' }}>
                          {log.session_type || 'Regular Lecture'}
                        </td>
                        <td>
                          <span className={`badge ${isPresent ? 'badge-success' : 'badge-danger'}`} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                            {isPresent ? '✓ Present' : '✗ Absent'}
                          </span>
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  )
}
