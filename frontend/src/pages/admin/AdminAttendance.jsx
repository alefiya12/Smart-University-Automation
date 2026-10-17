import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify as toast } from '../../components/common/Toast'
import BotRunPanel from '../../components/common/BotRunPanel'

const BOT_STEPS = [
  'Read attendance Excel file',
  'Resolve student IDs from DB',
  'Upsert attendance rows',
  'Update subject summaries',
  'Evaluate attendance thresholds (75%)',
  'Fire low-attendance alerts',
  'Write BotRunLog entry',
]

export default function AdminAttendance() {
  const [courses, setCourses] = useState([])
  const [selectedCourse, setSelectedCourse] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState([])

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const res = await api.get('/departments/')
        const allCourses = []
        if (Array.isArray(res.data)) {
          res.data.forEach(dept => {
            if (dept.courses) {
              dept.courses.forEach(c => {
                allCourses.push({ ...c, department_name: dept.name })
              })
            }
          })
        }
        setCourses(allCourses)
      } catch (err) {
        console.error('Failed to load courses', err)
      }
    }
    fetchCourses()
  }, [])

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  const handleRunBot = async () => {
    if (!selectedCourse) { toast.error('Please select a course first.'); return }
    if (!file) { toast.error('Please select an Excel file first.'); return }

    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)
    formData.append('course_id', selectedCourse)

    try {
      const res = await api.post('/attendance/bulk/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      toast.success(res.data.message || 'Attendance processed successfully!')
      setFile(null)
      document.getElementById('attendance-file-upload').value = ''
      setLogs(
        res.data.errors?.length > 0
          ? res.data.errors
          : [`✓ Successfully processed ${res.data.succeeded} records.`]
      )
    } catch (err) {
      let msg = 'Attendance upload failed.'
      if (err.response?.data?.detail) {
        msg = typeof err.response.data.detail === 'string'
          ? err.response.data.detail
          : err.response.data.detail.map(d => `${d.loc?.join('.')}: ${d.msg}`).join(', ')
      }
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Attendance Automation</h1>
          <p className="page-subtitle">Upload daily attendance records via Excel to auto-calculate percentages and trigger low-attendance warnings.</p>
        </div>
      </div>

      {/* ── Bot Control Panel ────────────────────────────────────────────── */}
      <BotRunPanel
        botKey="attendance_bot"
        title="Attendance Bot"
        description="Ingests daily attendance matrix Excel, upserts per-student per-subject rows, recomputes rolling %, and fires in-app + email warnings for students below 75% threshold."
        steps={BOT_STEPS}
        color="#15803D"
        colorLight="#F0FDF4"
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 'var(--space-6)' }}>
        {/* Manual Upload Card */}
        <Card title="Manual Upload — Attendance Excel" subtitle="Supported formats: .xlsx / .xls">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', maxWidth: '460px' }}>
            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-sm)', fontWeight: 500, marginBottom: '6px', color: '#374151' }}>
                Course
              </label>
              <select
                value={selectedCourse}
                onChange={e => setSelectedCourse(e.target.value)}
                className="form-input"
                style={{ width: '100%' }}
              >
                <option value="">-- Select Course --</option>
                {courses.map(c => (
                  <option key={c.id} value={c.id}>{c.department_name} — {c.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-sm)', fontWeight: 500, marginBottom: '6px', color: '#374151' }}>
                Attendance Excel File
              </label>
              <input
                id="attendance-file-upload"
                type="file"
                accept=".xlsx, .xls"
                onChange={handleFileChange}
                style={{
                  width: '100%',
                  padding: 'var(--space-3)',
                  border: '2px dashed var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--color-bg)',
                  cursor: 'pointer',
                }}
              />
            </div>

            <Button
              variant="primary"
              onClick={handleRunBot}
              isLoading={loading}
              disabled={!file || !selectedCourse}
              style={{ width: 'fit-content' }}
            >
              📥 Upload & Process Attendance
            </Button>
          </div>
        </Card>

        {/* Processing Results */}
        {logs.length > 0 && (
          <Card title="Processing Results">
            <div style={{
              padding: 'var(--space-4)',
              backgroundColor: '#0F172A',
              borderRadius: 'var(--radius-md)',
            }}>
              {logs.map((log, i) => (
                <div key={i} style={{
                  marginBottom: '4px',
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '13px',
                  color: log.startsWith('✓') ? '#86EFAC' : '#FDA4AF',
                }}>
                  {log}
                </div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
