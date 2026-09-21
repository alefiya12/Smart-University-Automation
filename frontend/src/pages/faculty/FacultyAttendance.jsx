import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify as toast } from '../../components/common/Toast'

export default function FacultyAttendance() {
  const [courses, setCourses] = useState([])
  const [selectedCourse, setSelectedCourse] = useState('')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState([])

  useEffect(() => {
    api.get('/departments/')
      .then(res => {
        const allCourses = []
        if (Array.isArray(res.data)) {
          res.data.forEach(dept => {
            if (dept.courses) {
              dept.courses.forEach(c => allCourses.push({ ...c, department_name: dept.name }))
            }
          })
        }
        setCourses(allCourses)
        if (allCourses.length > 0) setSelectedCourse(allCourses[0].id)
      })
      .catch(() => toast.error('Failed to load courses'))
  }, [])

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedCourse) {
      toast.error('Please select a course first.')
      return
    }
    if (!file) {
      toast.error('Please select an Excel file first.')
      return
    }

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
      const fileInput = document.getElementById('faculty-att-file')
      if (fileInput) fileInput.value = ''

      if (res.data.errors && res.data.errors.length > 0) {
        setLogs(res.data.errors)
      } else {
        setLogs([`Successfully recorded attendance for ${res.data.succeeded} student entries.`])
      }
    } catch (err) {
      const detail = err.response?.data?.detail
      const msg = typeof detail === 'string' ? detail : 'Attendance upload failed'
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
          <h1 className="page-title">Record Class Attendance</h1>
          <p className="page-subtitle">Upload subject-wise lecture attendance spreadsheet for your classes.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 'var(--space-6)' }}>
        <Card title="Upload Attendance Spreadsheet" subtitle="Matrix format: student_id, date, Subject1, Subject2...">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div>
              <label className="form-label" style={{ fontWeight: 600, marginBottom: '6px', display: 'block' }}>
                Select Course
              </label>
              <select
                className="form-input"
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(e.target.value)}
              >
                {courses.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.name} ({c.department_name})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="form-label" style={{ fontWeight: 600, marginBottom: '6px', display: 'block' }}>
                Attendance Excel (.xlsx)
              </label>
              <input
                id="faculty-att-file"
                type="file"
                accept=".xlsx, .xls"
                className="form-input"
                onChange={handleFileChange}
              />
            </div>

            <Button variant="primary" onClick={handleUpload} disabled={loading || !file}>
              {loading ? 'Processing Attendance...' : '🚀 Submit Attendance File'}
            </Button>
          </div>
        </Card>

        <Card title="Format Guidelines & Verification" subtitle="Automated threshold evaluation">
          <ul style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', paddingLeft: '20px', lineHeight: 1.7 }}>
            <li>Excel sheet must include <code>student_id</code> (e.g. SU2026-0001) and <code>date</code> (YYYY-MM-DD).</li>
            <li>Subject column headers must match course subjects (e.g. <code>Mathematics</code>, <code>Physics</code>).</li>
            <li>Use <code>1</code> for Present and <code>0</code> for Absent.</li>
            <li>Low-attendance alerts will be automatically dispatched to students whose cumulative attendance drops below 75%.</li>
          </ul>
        </Card>
      </div>

      {logs.length > 0 && (
        <Card title="Submission Execution Log" style={{ marginTop: 'var(--space-6)' }}>
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
