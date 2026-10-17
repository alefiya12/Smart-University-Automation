import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify as toast } from '../../components/common/Toast'
import BotRunPanel from '../../components/common/BotRunPanel'

const BOT_STEPS = [
  'Read marks Excel file',
  'Resolve students & subjects',
  'Apply dual-threshold grading (Int ≥12/30, Ext ≥28/70)',
  'Flag F-grade records for review',
  'Publish approved results',
  'Compute SGPA per semester',
  'Compute cumulative CGPA',
  'Generate PDF marksheets',
  'Write BotRunLog entry',
]

export default function AdminResults() {
  const [courses, setCourses] = useState([])
  const [selectedCourse, setSelectedCourse] = useState('')
  const [selectedSemester, setSelectedSemester] = useState(1)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [exportLoading, setExportLoading] = useState(false)
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
    if (!file) { toast.error('Please select an Excel file first.'); return }

    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await api.post('/results/bulk', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      toast.success(res.data.message || 'Results processed successfully!')
      setFile(null)
      document.getElementById('results-file-upload').value = ''
      setLogs(
        res.data.errors?.length > 0
          ? res.data.errors
          : [`✓ Successfully processed ${res.data.succeeded} records.`]
      )
    } catch (err) {
      let msg = 'Results upload failed.'
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

  const handleExport = async () => {
    if (!selectedCourse) { toast.error('Please select a course first.'); return }
    setExportLoading(true)
    try {
      const res = await api.get(
        `/results/export?course_id=${selectedCourse}&semester=${selectedSemester}`,
        { responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Results_Course_${selectedCourse}_Sem_${selectedSemester}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
      toast.success('Report card downloaded successfully')
    } catch {
      toast.error('Failed to export. Make sure results exist for this course and semester.')
    } finally {
      setExportLoading(false)
    }
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Results Automation</h1>
          <p className="page-subtitle">Upload examination marks via Excel to compute GPAs, flag failing students, and publish results.</p>
        </div>
      </div>

      {/* ── Bot Control Panel ────────────────────────────────────────────── */}
      <BotRunPanel
        botKey="results_bot"
        title="Results Bot"
        description="Processes marks Excel with Dual-Threshold grading (Internal ≥12/30, External ≥28/70). Computes SGPA/CGPA by percentage method, flags F-grades for admin review, publishes approved results, and generates PDF marksheets."
        steps={BOT_STEPS}
        color="#B45309"
        colorLight="#FFFBEB"
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
        {/* Upload Card */}
        <Card title="Manual Upload — Marks Excel" subtitle="Supported formats: .xlsx / .xls">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', maxWidth: '400px' }}>
            <div>
              <label style={{ display: 'block', fontSize: 'var(--text-sm)', fontWeight: 500, marginBottom: '6px', color: '#374151' }}>
                Marks Excel File
              </label>
              <input
                id="results-file-upload"
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
              disabled={!file}
              style={{ width: 'fit-content' }}
            >
              🚀 Upload & Process Marks
            </Button>
          </div>
        </Card>

        {/* Export Card */}
        <Card title="Consolidated Report Cards" subtitle="Export dual-threshold results for administration">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', maxWidth: '400px' }}>
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
                Semester
              </label>
              <input
                type="number"
                placeholder="Semester"
                value={selectedSemester}
                onChange={e => setSelectedSemester(Number(e.target.value))}
                min={1} max={8}
                className="form-input"
                style={{ width: '100%' }}
              />
            </div>

            <Button
              variant="secondary"
              onClick={handleExport}
              isLoading={exportLoading}
              disabled={!selectedCourse}
              style={{ width: 'fit-content' }}
            >
              📊 Export Report (.xlsx)
            </Button>
          </div>
        </Card>
      </div>

      {/* Processing Results */}
      {logs.length > 0 && (
        <div style={{ marginTop: 'var(--space-6)' }}>
          <Card title="Processing Results & Pending Reviews">
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
            <div style={{
              marginTop: 'var(--space-4)', padding: 'var(--space-3)',
              background: '#FFFBEB', borderRadius: 'var(--radius-md)',
              fontSize: 'var(--text-sm)', color: '#B45309', borderLeft: '3px solid #B45309',
            }}>
              ⚠️ Any 'F' grades computed have been flagged for mandatory administrative review before result publication.
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}
