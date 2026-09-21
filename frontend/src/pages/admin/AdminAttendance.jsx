import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify as toast } from '../../components/common/Toast'

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
      toast.success(res.data.message || 'Attendance bot processed successfully!')
      setFile(null)
      document.getElementById('attendance-file-upload').value = ''
      
      if (res.data.errors && res.data.errors.length > 0) {
        setLogs(res.data.errors)
      } else {
        setLogs([`Successfully processed ${res.data.succeeded} records.`])
      }
    } catch (err) {
      let errorMsg = 'Attendance bot failed to run.'
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMsg = err.response.data.detail
        } else if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail.map(d => `${d.loc?.join('.')}: ${d.msg}`).join(', ')
        }
      }
      toast.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Attendance Automation</h1>
          <p className="page-subtitle">Upload daily attendance records via Excel to auto-calculate percentages and trigger warnings.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 'var(--space-6)' }}>
        {/* Upload Card */}
        <Card title="Run Attendance Bot" subtitle="Supported formats: .xlsx">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', maxWidth: '400px' }}>
            <select 
              value={selectedCourse} 
              onChange={e => setSelectedCourse(e.target.value)}
              style={{
                padding: 'var(--space-2)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-bg)'
              }}
            >
              <option value="">-- Select Course --</option>
              {courses.map(c => (
                <option key={c.id} value={c.id}>{c.department_name} - {c.name}</option>
              ))}
            </select>
            <input 
              id="attendance-file-upload"
              type="file" 
              accept=".xlsx, .xls"
              onChange={handleFileChange}
              style={{
                padding: 'var(--space-3)',
                border: '1px dashed var(--color-border)',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-background-soft)'
              }}
            />
            <Button 
              variant="primary" 
              onClick={handleRunBot} 
              isLoading={loading}
              disabled={!file}
              style={{ width: 'fit-content' }}
            >
              🚀 Execute Automation
            </Button>
          </div>
        </Card>

        {/* Status/Logs */}
        {logs.length > 0 && (
          <Card title="Run Logs">
            <div style={{ padding: 'var(--space-4)', backgroundColor: 'var(--color-background-soft)', borderRadius: 'var(--radius-md)' }}>
              {logs.map((log, i) => (
                <div key={i} style={{ marginBottom: '4px', fontFamily: 'monospace', fontSize: '13px' }}>{log}</div>
              ))}
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}
