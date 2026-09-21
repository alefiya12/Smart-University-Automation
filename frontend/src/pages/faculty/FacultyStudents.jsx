import React, { useState, useEffect } from 'react'
import api from '../../services/api'
import Card from '../../components/common/Card'
import { notify } from '../../components/common/Toast'

export default function FacultyStudents() {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    api.get('/admission/')
      .then(res => setStudents(res.data.data || []))
      .catch(() => notify.error('Failed to load student directory'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = students.filter(s => {
    const term = searchTerm.toLowerCase()
    return (
      (s.enrollment_no && s.enrollment_no.toLowerCase().includes(term)) ||
      (s.full_name && s.full_name.toLowerCase().includes(term)) ||
      (s.username && s.username.toLowerCase().includes(term)) ||
      (s.course && s.course.toLowerCase().includes(term))
    )
  })

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Enrolled Student Roster</h1>
          <p className="page-subtitle">View enrolled students and check academic standing across departments.</p>
        </div>
        <input
          type="text"
          className="form-input"
          placeholder="Search students by name, enrollment, course..."
          style={{ width: '300px' }}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <Card title="Student Directory" subtitle={`Total registered students: ${students.length}`}>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Enrollment #</th>
                <th>Full Name</th>
                <th>Department</th>
                <th>Course</th>
                <th>Semester</th>
                <th>Academic Standing</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" style={{ textAlign: 'center', padding: '2rem' }}>Loading students...</td></tr>
              ) : filtered.length === 0 ? (
                <tr><td colSpan="6" style={{ textAlign: 'center', padding: '2rem' }}>No matching students found.</td></tr>
              ) : (
                filtered.map(s => (
                  <tr key={s.id}>
                    <td style={{ fontWeight: 600, color: 'var(--color-primary)' }}>{s.enrollment_no}</td>
                    <td>{s.full_name || s.username}</td>
                    <td>{s.department || '—'}</td>
                    <td>{s.course || '—'}</td>
                    <td>Semester {s.semester}</td>
                    <td>
                      <span className={`badge ${s.academic_standing === 'Backlog' ? 'badge-danger' : 'badge-success'}`}>
                        {s.academic_standing || 'Good Standing'}
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
