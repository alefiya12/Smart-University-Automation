/**
 * AdminRPAControl.jsx — Premium RPA Control Center
 * Shows all 3 bots with live status, run-history timeline,
 * trigger buttons, log output previews, and Robot HTML report downloads.
 */
import React, { useState, useEffect, useCallback, useRef } from 'react'
import { managementApi } from '../../services/api'
import { notify } from '../../components/common/Toast'

/* ── Colour palette for each bot ─────────────────────────────────────── */
const BOT_META = {
  admission_bot: {
    icon: '🎓',
    title: 'Admission Bot',
    color: '#1A56DB',
    colorLight: '#EBF1FF',
    description:
      'Reads the admission sample Excel, creates student accounts, auto-generates enrollment IDs (SU{year}-XXXX), produces PDF admission letters, and queues confirmation emails.',
    steps: ['Read Excel file', 'Validate records', 'Create student accounts', 'Generate enrollment IDs', 'Generate PDF letters', 'Queue emails', 'Write BotRunLog'],
  },
  attendance_bot: {
    icon: '📋',
    title: 'Attendance Bot',
    color: '#15803D',
    colorLight: '#F0FDF4',
    description:
      'Ingests daily attendance matrix Excel, upserts records per student per subject per date, recomputes rolling attendance %, and fires in-app + email warnings for students below threshold.',
    steps: ['Read attendance Excel', 'Resolve student IDs', 'Upsert attendance rows', 'Update subject summaries', 'Evaluate thresholds', 'Fire low-attendance alerts', 'Write BotRunLog'],
  },
  results_bot: {
    icon: '📊',
    title: 'Results Bot',
    color: '#B45309',
    colorLight: '#FFFBEB',
    description:
      'Processes marks Excel with Dual-Threshold grading (Internal ≥12/30, External ≥28/70), calculates SGPA/CGPA via percentage method, flags F-grades for admin review, publishes approved results, and generates PDF marksheets.',
    steps: ['Read marks Excel', 'Resolve students & subjects', 'Dual-threshold grade eval', 'Flag F-grade records', 'Publish approved results', 'Compute SGPA / CGPA', 'Generate PDF marksheets', 'Write BotRunLog'],
  },
}

/* ── Small utility components ─────────────────────────────────────────── */
function StatusBadge({ status }) {
  const map = {
    success: { bg: '#F0FDF4', color: '#15803D', label: '✓ Success' },
    running: { bg: '#EBF1FF', color: '#1A56DB', label: '⟳ Running' },
    failed:  { bg: '#FEF2F2', color: '#B91C1C', label: '✕ Failed' },
    partial: { bg: '#FFFBEB', color: '#B45309', label: '⚠ Partial' },
  }
  const s = map[status] || { bg: '#F3F4F6', color: '#6B7280', label: status }
  return (
    <span style={{
      padding: '2px 10px', borderRadius: '9999px',
      fontSize: '0.72rem', fontWeight: 600,
      background: s.bg, color: s.color,
    }}>{s.label}</span>
  )
}

function RunHistoryRow({ run, onViewReport }) {
  const dur = run.duration_seconds ? `${run.duration_seconds.toFixed(1)}s` : '—'
  const when = run.started_at ? new Date(run.started_at).toLocaleString() : '—'
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '12px',
      padding: '10px 0', borderBottom: '1px solid #F3F4F6',
      fontSize: '0.82rem',
    }}>
      <div style={{ flex: 1, color: '#6B7280' }}>{when}</div>
      <StatusBadge status={run.status} />
      <div style={{ color: '#6B7280', minWidth: 50, textAlign: 'right' }}>{dur}</div>
      <div style={{ color: '#6B7280', minWidth: 80, textAlign: 'right' }}>
        {run.records_processed}/{run.records_total}
      </div>
      {(run.report_file_path) ? (
        <button
          onClick={() => onViewReport(run.id)}
          style={{
            padding: '2px 8px', borderRadius: '4px', cursor: 'pointer',
            fontSize: '0.72rem', border: '1px solid #D1D5DB',
            background: '#fff', color: '#374151',
          }}
        >HTML Report</button>
      ) : <div style={{ width: 72 }} />}
    </div>
  )
}

function StepsList({ steps, activeStep }) {
  return (
    <div style={{ marginTop: '16px' }}>
      {steps.map((step, i) => {
        const done = activeStep > i
        const active = activeStep === i
        return (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            padding: '5px 0', fontSize: '0.82rem',
          }}>
            <div style={{
              width: 20, height: 20, borderRadius: '50%', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: done ? '#15803D' : active ? '#1A56DB' : '#F3F4F6',
              color: (done || active) ? '#fff' : '#9CA3AF',
              fontSize: '0.65rem', fontWeight: 700,
              transition: 'background 0.3s',
            }}>
              {done ? '✓' : i + 1}
            </div>
            <span style={{
              color: done ? '#15803D' : active ? '#1A56DB' : '#9CA3AF',
              fontWeight: active ? 600 : 400,
            }}>{step}</span>
            {active && (
              <span style={{
                marginLeft: 'auto', width: 12, height: 12, borderRadius: '50%',
                border: '2px solid #1A56DB', borderTopColor: 'transparent',
                animation: 'spin 0.6s linear infinite', display: 'inline-block',
              }} />
            )}
          </div>
        )
      })}
    </div>
  )
}

/* ── Main Bot Card ────────────────────────────────────────────────────── */
function BotControlCard({ botKey, meta, recentRuns = [], onRefresh }) {
  const [running, setRunning] = useState(false)
  const [currentLogId, setCurrentLogId] = useState(null)
  const [statusData, setStatusData] = useState(null)
  const [activeStep, setActiveStep] = useState(-1)
  const [logText, setLogText] = useState('')
  const pollRef = useRef(null)

  // If there's a running run in recent history, re-attach to it
  useEffect(() => {
    const runningRun = recentRuns.find(r => r.status === 'running')
    if (runningRun && !running) {
      setCurrentLogId(runningRun.id)
      setRunning(true)
    }
  }, [recentRuns])

  // Step simulator: increments activeStep every ~1.2s while running
  useEffect(() => {
    if (!running) { setActiveStep(-1); return }
    const interval = setInterval(() => {
      setActiveStep(prev => (prev < meta.steps.length - 2 ? prev + 1 : prev))
    }, 1200)
    return () => clearInterval(interval)
  }, [running, meta.steps.length])

  // Poll status every 2s while running
  useEffect(() => {
    if (!running || !currentLogId) return
    pollRef.current = setInterval(async () => {
      try {
        const res = await managementApi.getBotStatus(currentLogId)
        const d = res.data.data
        setStatusData(d)
        if (d.summary) setLogText(d.summary.slice(-3000))
        if (d.status !== 'running') {
          clearInterval(pollRef.current)
          setRunning(false)
          setActiveStep(meta.steps.length) // all steps done
          onRefresh()
          if (d.status === 'success') notify.success(`${meta.title} completed successfully! ✓`)
          else if (d.status === 'partial') notify.warn(`${meta.title} finished with some errors.`)
          else notify.error(`${meta.title} failed. Check the run logs.`)
        }
      } catch {}
    }, 2000)
    return () => clearInterval(pollRef.current)
  }, [running, currentLogId])

  const handleRun = async () => {
    try {
      setLogText('')
      setStatusData(null)
      const res = await managementApi.triggerBot(botKey)
      setCurrentLogId(res.data.log_id)
      setRunning(true)
      setActiveStep(0)
      notify.success(`${meta.title} started!`)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to start bot.'
      notify.error(msg)
    }
  }

  const handleViewReport = (logId) => {
    const token = localStorage.getItem('access_token')
    fetch(`/api/logs/${logId}/report`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async res => {
        if (!res.ok) throw new Error('No report')
        const blob = await res.blob()
        const url = window.URL.createObjectURL(blob)
        window.open(url, '_blank')
      })
      .catch(() => notify.error('Report not found on disk.'))
  }

  const latestRun = statusData || recentRuns[0]
  const isIdle = !running

  return (
    <div style={{
      background: '#fff', border: '1px solid #E5E7EB',
      borderRadius: '12px', overflow: 'hidden',
      boxShadow: running ? `0 0 0 2px ${meta.color}30` : '0 1px 3px rgba(0,0,0,0.06)',
      transition: 'box-shadow 0.3s',
    }}>
      {/* ── Header ────────────────── */}
      <div style={{
        padding: '20px 24px', borderBottom: '1px solid #F3F4F6',
        display: 'flex', alignItems: 'center', gap: '14px',
      }}>
        <div style={{
          width: 48, height: 48, borderRadius: '10px',
          background: meta.colorLight, fontSize: '1.5rem',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>{meta.icon}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: '1rem', color: '#111827' }}>{meta.title}</div>
          <div style={{ fontSize: '0.78rem', color: '#6B7280', marginTop: 2 }}>{meta.description.slice(0, 80)}…</div>
        </div>
        {latestRun && <StatusBadge status={running ? 'running' : latestRun.status} />}
      </div>

      {/* ── Body ──────────────────── */}
      <div style={{ padding: '20px 24px' }}>
        {/* Steps progress */}
        {running && (
          <div style={{
            background: '#F8F9FA', borderRadius: '8px',
            padding: '16px', marginBottom: '16px',
          }}>
            <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#374151', marginBottom: '4px' }}>
              EXECUTION PROGRESS
            </div>
            <StepsList steps={meta.steps} activeStep={activeStep} />
          </div>
        )}

        {/* Log preview (last 20 lines) */}
        {logText && !running && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#6B7280', marginBottom: '6px', letterSpacing: '0.05em' }}>
              EXECUTION OUTPUT
            </div>
            <pre style={{
              background: '#0F172A', color: '#94A3B8',
              padding: '12px', borderRadius: '6px',
              fontSize: '0.7rem', lineHeight: 1.6,
              maxHeight: '160px', overflow: 'auto',
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              whiteSpace: 'pre-wrap', wordBreak: 'break-all',
            }}>
              {logText.split('\n').slice(-20).join('\n')}
            </pre>
          </div>
        )}

        {/* Run history */}
        {recentRuns.length > 0 && (
          <div style={{ marginBottom: '16px' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#6B7280', marginBottom: '6px', letterSpacing: '0.05em' }}>
              RECENT RUNS
            </div>
            <div style={{ fontSize: '0.72rem', color: '#9CA3AF', display: 'flex', gap: 12, marginBottom: '4px' }}>
              <span style={{ flex: 1 }}>Started At</span>
              <span>Status</span>
              <span style={{ minWidth: 50, textAlign: 'right' }}>Duration</span>
              <span style={{ minWidth: 80, textAlign: 'right' }}>Pass/Total</span>
              <span style={{ width: 72 }} />
            </div>
            {recentRuns.slice(0, 4).map(run => (
              <RunHistoryRow key={run.id} run={run} onViewReport={handleViewReport} />
            ))}
          </div>
        )}

        {/* Run button */}
        <button
          onClick={handleRun}
          disabled={running}
          style={{
            width: '100%', padding: '12px', borderRadius: '8px',
            cursor: running ? 'not-allowed' : 'pointer',
            border: 'none', fontWeight: 600, fontSize: '0.875rem',
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
            background: running ? meta.colorLight : meta.color,
            color: running ? meta.color : '#fff',
            transition: 'all 0.2s',
          }}
        >
          {running ? (
            <>
              <span style={{
                width: 14, height: 14, borderRadius: '50%',
                border: `2px solid ${meta.color}`, borderTopColor: 'transparent',
                animation: 'spin 0.6s linear infinite', display: 'inline-block',
              }} />
              Running…
            </>
          ) : (
            <>▶ Run {meta.title}</>
          )}
        </button>
      </div>
    </div>
  )
}

/* ── Page ─────────────────────────────────────────────────────────────── */
export default function AdminRPAControl() {
  const [recentRuns, setRecentRuns] = useState({})
  const [loadingHistory, setLoadingHistory] = useState(true)

  const fetchRecent = useCallback(async () => {
    try {
      const res = await managementApi.getRecentBotRuns()
      setRecentRuns(res.data.data)
    } catch (err) {
      console.error('Failed to load recent runs', err)
    } finally {
      setLoadingHistory(false)
    }
  }, [])

  useEffect(() => {
    fetchRecent()
    const interval = setInterval(fetchRecent, 15000) // auto-refresh every 15s
    return () => clearInterval(interval)
  }, [fetchRecent])

  return (
    <div className="fade-in">
      {/* ── Page Header ─────────────────────────────────────── */}
      <div className="page-header">
        <div>
          <h1 className="page-title">🤖 RPA Control Center</h1>
          <p className="page-subtitle">
            Trigger, monitor, and audit your Robot Framework automation bots in real time.
          </p>
        </div>
        <div style={{ fontSize: '0.8rem', color: '#6B7280', alignSelf: 'flex-end' }}>
          Auto-refreshes every 15s
        </div>
      </div>

      {/* ── Architecture callout ────────────────────────────── */}
      <div style={{
        background: '#EBF1FF', border: '1px solid #BFDBFE',
        borderRadius: '10px', padding: '14px 20px',
        marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px',
      }}>
        <span style={{ fontSize: '1.2rem' }}>ℹ️</span>
        <div style={{ fontSize: '0.82rem', color: '#1E40AF', lineHeight: 1.5 }}>
          <strong>Architecture:</strong> Each bot runs as a Robot Framework 7 subprocess via the FastAPI backend.
          Bots directly access the SQLite database through SQLAlchemy — no HTTP calls.
          All runs are logged to <code>logs/</code> and recorded in <em>BotRunLog</em> for full audit traceability.
        </div>
      </div>

      {/* ── Bot Cards Grid ──────────────────────────────────── */}
      {loadingHistory ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#6B7280' }}>
          <div className="spinner" style={{ margin: '0 auto 16px' }} />
          Loading bot status…
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '24px',
        }}>
          {Object.entries(BOT_META).map(([botKey, meta]) => (
            <BotControlCard
              key={botKey}
              botKey={botKey}
              meta={meta}
              recentRuns={recentRuns[botKey] || []}
              onRefresh={fetchRecent}
            />
          ))}
        </div>
      )}

      {/* ── Legend ─────────────────────────────────────────── */}
      <div style={{
        marginTop: '32px', background: '#F8F9FA',
        border: '1px solid #E5E7EB', borderRadius: '10px', padding: '20px 24px',
      }}>
        <div style={{ fontWeight: 600, fontSize: '0.875rem', color: '#374151', marginBottom: '12px' }}>
          📖 Sample Data Files Used by Bots
        </div>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px',
        }}>
          {[
            { icon: '🎓', file: 'docs/sample_data/admission_sample.xlsx', desc: '8 student records across departments' },
            { icon: '📋', file: 'docs/sample_data/attendance_sample.xlsx', desc: 'Subject-wise matrix per student per date' },
            { icon: '📊', file: 'docs/sample_data/marks_sample.xlsx', desc: 'Internal+External marks per subject per semester' },
          ].map(item => (
            <div key={item.file} style={{
              background: '#fff', border: '1px solid #E5E7EB',
              borderRadius: '8px', padding: '12px 14px',
            }}>
              <div style={{ fontSize: '1rem', marginBottom: '4px' }}>{item.icon}</div>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#374151', fontFamily: 'monospace' }}>
                {item.file}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6B7280', marginTop: '4px' }}>{item.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
