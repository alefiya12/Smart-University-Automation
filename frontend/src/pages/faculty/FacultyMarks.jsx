import React, { useState } from 'react'
import api from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify as toast } from '../../components/common/Toast'

export default function FacultyMarks() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState([])

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select an Excel file first.')
      return
    }

    setLoading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await api.post('/results/bulk', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      toast.success(res.data.message || 'Marks uploaded and grades computed successfully!')
      setFile(null)
      const fileInput = document.getElementById('faculty-marks-file')
      if (fileInput) fileInput.value = ''

      if (res.data.errors && res.data.errors.length > 0) {
        setLogs(res.data.errors)
      } else {
        setLogs([`Successfully ingested ${res.data.succeeded} student marks records.`])
      }
    } catch (err) {
      const detail = err.response?.data?.detail
      const msg = typeof detail === 'string' ? detail : 'Marks upload failed'
      toast.error(msg)
      setLogs([`ERROR: ${msg}`])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Submit Examination Marks</h1>
          <p className="page-subtitle">Dual-Threshold Grading Matrix: Internal (Max 30) and External (Max 70).</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-6)' }}>
        <Card title="Upload Marks Spreadsheet" subtitle="Accepts .xlsx or .xls files">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div>
              <label className="form-label" style={{ fontWeight: 600, marginBottom: '6px', display: 'block' }}>
                Select Marks Excel (.xlsx)
              </label>
              <input
                id="faculty-marks-file"
                type="file"
                accept=".xlsx, .xls"
                className="form-input"
                onChange={handleFileChange}
              />
            </div>

            <Button variant="primary" onClick={handleUpload} disabled={loading || !file}>
              {loading ? 'Evaluating & Ingesting Marks...' : '📊 Ingest & Compute Grades'}
            </Button>
          </div>
        </Card>

        <Card title="Dual-Threshold Evaluation Matrix" subtitle="Strict Passing Metrics">
          <div style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>
            <p style={{ margin: '0 0 10px 0' }}>The calculation engine enforces independent passing criteria:</p>
            <ul style={{ paddingLeft: '20px', margin: '0 0 12px 0' }}>
              <li><strong>Internal Score:</strong> Max 30.00 — Passing threshold is <strong>≥ 12.00 (40%)</strong>.</li>
              <li><strong>External Score:</strong> Max 70.00 — Passing threshold is <strong>≥ 28.00 (40%)</strong>.</li>
              <li>Required columns: <code>student_id</code> (or <code>enrollment_no</code>), <code>subject_name</code>, <code>internal_score</code>, <code>external_score</code>.</li>
            </ul>
            <p style={{ margin: 0 }}>
              Scores exceeding 30 (internal) or 70 (external) will immediately trigger atomic transaction rollback.
            </p>
          </div>
        </Card>
      </div>

      {logs.length > 0 && (
        <Card title="Ingestion Log" style={{ marginTop: 'var(--space-6)' }}>
          <div style={{
            background: 'var(--color-bg-base, #111827)',
            color: '#10B981',
            padding: '16px',
            borderRadius: '8px',
            fontFamily: 'monospace',
            fontSize: 'var(--text-sm)',
            maxHeight: '200px',
            overflowY: 'auto'
          }}>
            {logs.map((l, i) => (
              <div key={i} style={{ marginBottom: '4px', color: l.startsWith('ERROR') ? '#EF4444' : '#10B981' }}>
                {l}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
