/**
 * BotRunPanel.jsx — Reusable embedded bot control panel.
 * Can be dropped into any admin page to show a "Run Bot" button
 * with live step progress and last-run summary.
 *
 * Props:
 *   botKey      : 'admission_bot' | 'attendance_bot' | 'results_bot'
 *   title       : string
 *   description : string
 *   steps       : string[] (ordered execution steps to animate)
 *   color       : hex color
 *   colorLight  : hex light bg color
 */
import React, { useState, useEffect, useRef } from 'react'
import { managementApi } from '../../services/api'
import { notify } from '../common/Toast'

export default function BotRunPanel({ botKey, title, description, steps, color, colorLight }) {
  const [running, setRunning] = useState(false)
  const [currentLogId, setCurrentLogId] = useState(null)
  const [lastRun, setLastRun] = useState(null)
  const [activeStep, setActiveStep] = useState(-1)
  const [summary, setSummary] = useState('')
  const pollRef = useRef(null)
  const stepRef = useRef(null)

  // Fetch last run on mount
  useEffect(() => {
    const fetchLast = async () => {
      try {
        const res = await managementApi.getRecentBotRuns()
        const runs = res.data.data[botKey] || []
        if (runs.length > 0) setLastRun(runs[0])
        // Re-attach if there's a running run
        const runningRun = runs.find(r => r.status === 'running')
        if (runningRun) {
          setCurrentLogId(runningRun.id)
          setRunning(true)
          setActiveStep(0)
        }
      } catch {}
    }
    fetchLast()
  }, [botKey])

  // Step simulator
  useEffect(() => {
    if (!running) { clearInterval(stepRef.current); setActiveStep(-1); return }
    setActiveStep(0)
    stepRef.current = setInterval(() => {
      setActiveStep(prev => (prev < steps.length - 2 ? prev + 1 : prev))
    }, 1400)
    return () => clearInterval(stepRef.current)
  }, [running, steps.length])

  // Poll status
  useEffect(() => {
    if (!running || !currentLogId) return
    pollRef.current = setInterval(async () => {
      try {
        const res = await managementApi.getBotStatus(currentLogId)
        const d = res.data.data
        if (d.summary) setSummary(d.summary.slice(-2000))
        if (d.status !== 'running') {
          clearInterval(pollRef.current)
          clearInterval(stepRef.current)
          setRunning(false)
          setLastRun(d)
          setActiveStep(steps.length)
          if (d.status === 'success') notify.success(`${title} completed! ✓`)
          else if (d.status === 'partial') notify.warn(`${title} finished with some errors.`)
          else notify.error(`${title} failed.`)
        }
      } catch {}
    }, 2500)
    return () => clearInterval(pollRef.current)
  }, [running, currentLogId, title, steps.length])

  const handleRun = async () => {
    try {
      setSummary('')
      setLastRun(null)
      const res = await managementApi.triggerBot(botKey)
      setCurrentLogId(res.data.log_id)
      setRunning(true)
      notify.success(`${title} started!`)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Failed to start bot.'
      notify.error(msg)
    }
  }

  const handleViewReport = () => {
    if (!lastRun?.id) return
    const token = localStorage.getItem('access_token')
    fetch(`/api/logs/${lastRun.id}/report`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async res => {
        if (!res.ok) throw new Error('No report')
        const blob = await res.blob()
        window.open(URL.createObjectURL(blob), '_blank')
      })
      .catch(() => notify.error('Report not available.'))
  }

  const statusColor = {
    success: '#15803D', failed: '#B91C1C', partial: '#B45309', running: '#1A56DB',
  }
  const statusBg = {
    success: '#F0FDF4', failed: '#FEF2F2', partial: '#FFFBEB', running: '#EBF1FF',
  }
  const statusLabel = {
    success: '✓ Last run: Success', failed: '✕ Last run: Failed',
    partial: '⚠ Last run: Partial', running: '⟳ Running…',
  }

  return (
    <div style={{
      border: `1px solid ${running ? color : '#E5E7EB'}`,
      borderRadius: '12px', background: '#fff',
      overflow: 'hidden',
      boxShadow: running ? `0 0 0 3px ${color}20` : 'none',
      transition: 'box-shadow 0.3s, border-color 0.3s',
      marginBottom: '24px',
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        background: colorLight,
        borderBottom: '1px solid #E5E7EB',
        display: 'flex', alignItems: 'center', gap: '14px',
      }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#111827' }}>
            🤖 {title} — Bot Control Panel
          </div>
          <div style={{ fontSize: '0.78rem', color: '#6B7280', marginTop: 2 }}>{description}</div>
        </div>
        {lastRun?.status && (
          <span style={{
            padding: '3px 10px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 600,
            background: statusBg[running ? 'running' : lastRun.status],
            color: statusColor[running ? 'running' : lastRun.status],
          }}>
            {statusLabel[running ? 'running' : lastRun.status]}
          </span>
        )}
      </div>

      {/* Body */}
      <div style={{ padding: '16px 20px', display: 'flex', gap: '20px', flexWrap: 'wrap', alignItems: 'flex-start' }}>
        {/* Steps column */}
        <div style={{ flex: '1 1 200px', minWidth: 180 }}>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#6B7280', letterSpacing: '0.05em', marginBottom: '8px' }}>
            AUTOMATION STEPS
          </div>
          {steps.map((step, i) => {
            const done = activeStep > i
            const active = activeStep === i && running
            return (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '3px 0', fontSize: '0.78rem',
              }}>
                <div style={{
                  width: 18, height: 18, borderRadius: '50%', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: done ? '#15803D' : active ? color : '#F3F4F6',
                  color: (done || active) ? '#fff' : '#9CA3AF',
                  fontSize: '0.6rem', fontWeight: 700, transition: 'background 0.3s',
                }}>
                  {done ? '✓' : i + 1}
                </div>
                <span style={{
                  color: done ? '#15803D' : active ? color : '#9CA3AF',
                  fontWeight: active ? 600 : 400,
                }}>{step}</span>
              </div>
            )
          })}
        </div>

        {/* Run info + button column */}
        <div style={{ flex: '1 1 180px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Last run stats */}
          {lastRun && !running && (
            <div style={{
              background: '#F8F9FA', borderRadius: '8px', padding: '10px 14px',
              fontSize: '0.78rem', color: '#374151', lineHeight: 1.8,
            }}>
              <div><strong>Duration:</strong> {lastRun.duration_seconds?.toFixed(1) || '—'}s</div>
              <div><strong>Passed:</strong> {lastRun.records_processed ?? '—'}</div>
              <div><strong>Failed:</strong> {lastRun.records_failed ?? '—'}</div>
              {lastRun.report_file_path && (
                <button onClick={handleViewReport} style={{
                  marginTop: '8px', fontSize: '0.72rem', padding: '4px 10px',
                  borderRadius: '5px', border: '1px solid #D1D5DB',
                  background: '#fff', cursor: 'pointer', color: '#374151',
                }}>
                  📄 View HTML Report
                </button>
              )}
            </div>
          )}

          {/* Animated progress when running */}
          {running && (
            <div style={{ background: '#F8F9FA', borderRadius: '8px', padding: '10px 14px' }}>
              <div style={{ fontSize: '0.75rem', color: color, fontWeight: 600 }}>
                Step {Math.min(activeStep + 1, steps.length)} of {steps.length}
              </div>
              <div style={{
                marginTop: '6px', height: '4px', background: '#E5E7EB', borderRadius: '2px', overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%', borderRadius: '2px', background: color,
                  width: `${((activeStep + 1) / steps.length) * 100}%`,
                  transition: 'width 1s ease',
                }} />
              </div>
            </div>
          )}

          <button
            onClick={handleRun}
            disabled={running}
            style={{
              padding: '11px 16px', borderRadius: '8px',
              border: 'none', fontWeight: 600, fontSize: '0.85rem',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
              cursor: running ? 'not-allowed' : 'pointer',
              background: running ? colorLight : color,
              color: running ? color : '#fff',
              transition: 'all 0.2s',
            }}
          >
            {running ? (
              <>
                <span style={{
                  width: 13, height: 13, borderRadius: '50%',
                  border: `2px solid ${color}`, borderTopColor: 'transparent',
                  animation: 'spin 0.6s linear infinite', display: 'inline-block',
                }} />
                Running…
              </>
            ) : `▶ Run ${title}`}
          </button>
        </div>
      </div>

      {/* Log output snip */}
      {summary && !running && (
        <div style={{ borderTop: '1px solid #F3F4F6', padding: '12px 20px', background: '#0F172A' }}>
          <div style={{ fontSize: '0.7rem', color: '#64748B', marginBottom: '6px', fontWeight: 600, letterSpacing: '0.05em' }}>
            BOT OUTPUT (last 15 lines)
          </div>
          <pre style={{
            color: '#94A3B8', fontSize: '0.68rem', lineHeight: 1.6,
            maxHeight: '120px', overflow: 'auto',
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0,
          }}>
            {summary.split('\n').slice(-15).join('\n')}
          </pre>
        </div>
      )}
    </div>
  )
}
