import React, { useState, useEffect } from 'react'
import api, { managementApi } from '../../services/api'
import Card from '../../components/common/Card'
import Modal from '../../components/common/Modal'
import Button from '../../components/common/Button'
import FormInput from '../../components/common/FormInput'
import { notify } from '../../components/common/Toast'

export default function AdminStudents() {
  const [students, setStudents] = useState([])
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)

  // Edit State
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [currentStudent, setCurrentStudent] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [saving, setSaving] = useState(false)

  const fetchData = async () => {
    try {
      const [resStudents, resDepts] = await Promise.all([
        api.get('/admission/'),
        managementApi.getDepartments()
      ])
      setStudents(resStudents.data.data || [])
      setDepartments(resDepts.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleEditClick = (student) => {
    setCurrentStudent(student)
    // Find department id matching student's department name
    const dept = departments.find(d => d.name === student.department)
    const course = dept?.courses?.find(c => c.name === student.course)

    setEditForm({
      full_name: student.username || '',
      email: student.email || '',
      department_id: dept?.id || '',
      course_id: course?.id || '',
      semester: student.semester || 1,
      is_admitted: student.is_admitted !== undefined ? student.is_admitted : 0
    })
    setEditModalOpen(true)
  }

  const handleEditSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await managementApi.updateStudent(currentStudent.id, {
        ...editForm,
        department_id: parseInt(editForm.department_id),
        course_id: parseInt(editForm.course_id),
        semester: parseInt(editForm.semester),
        is_admitted: parseInt(editForm.is_admitted)
      })
      notify.success('Student updated successfully')
      setEditModalOpen(false)
      fetchData()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to update student')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this student? This action cannot be undone.')) return
    try {
      await managementApi.deleteStudent(id)
      notify.success('Student deleted')
      fetchData()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to delete student')
    }
  }

  // Get courses for currently selected department in edit form
  const selectedDept = departments.find(d => d.id === parseInt(editForm.department_id))
  const courses = selectedDept?.courses || []

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Student Directory</h1>
          <p className="page-subtitle">View, edit, and manage admitted students.</p>
        </div>
      </div>

      <Card>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Enrollment No</th>
                <th>Name</th>
                <th>Department</th>
                <th>Course</th>
                <th>Semester</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: 'var(--space-4)' }}>
                    <div className="spinner" style={{ margin: '0 auto' }}></div>
                  </td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: 'var(--space-4)', color: 'var(--color-text-secondary)' }}>
                    No students found. Run the Admission automation to enroll students.
                  </td>
                </tr>
              ) : (
                students.map((s) => (
                  <tr key={s.id}>
                    <td><strong>{s.enrollment_no}</strong></td>
                    <td>
                      <div className="avatar-group">
                        <div className="avatar">{s.username?.charAt(0).toUpperCase()}</div>
                        <div>
                          <div style={{ fontWeight: '500' }}>{s.username}</div>
                          <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>{s.email}</div>
                        </div>
                      </div>
                    </td>
                    <td>{s.department || 'N/A'}</td>
                    <td>{s.course || 'N/A'}</td>
                    <td>Sem {s.semester}</td>
                    <td>
                      {s.is_admitted ? (
                        <span className="badge badge-success">Admitted</span>
                      ) : (
                        <span className="badge badge-warning">Pending</span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right', display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                      <Button variant="secondary" size="sm" onClick={() => handleEditClick(s)}>Edit</Button>
                      <Button variant="danger" size="sm" onClick={() => handleDelete(s.id)}>Delete</Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Modal isOpen={editModalOpen} onClose={() => setEditModalOpen(false)} title={`Edit Student: ${currentStudent?.enrollment_no}`}>
        <form onSubmit={handleEditSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <FormInput 
            label="Full Name" 
            value={editForm.full_name} 
            onChange={e => setEditForm({...editForm, full_name: e.target.value})} 
            required 
          />
          <FormInput 
            label="Email" 
            type="email" 
            value={editForm.email} 
            onChange={e => setEditForm({...editForm, email: e.target.value})} 
            required 
          />
          
          <div>
            <label className="form-label">Department</label>
            <select 
              className="form-input" 
              value={editForm.department_id} 
              onChange={e => setEditForm({...editForm, department_id: e.target.value, course_id: ''})} 
              required
            >
              <option value="" disabled>Select Department</option>
              {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          
          <div>
            <label className="form-label">Course</label>
            <select 
              className="form-input" 
              value={editForm.course_id} 
              onChange={e => setEditForm({...editForm, course_id: e.target.value})} 
              required
            >
              <option value="" disabled>Select Course</option>
              {courses.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>

          <FormInput 
            label="Semester" 
            type="number" 
            min="1" max="10" 
            value={editForm.semester} 
            onChange={e => setEditForm({...editForm, semester: e.target.value})} 
            required 
          />

          <div>
            <label className="form-label">Admission Status</label>
            <select 
              className="form-input" 
              value={editForm.is_admitted} 
              onChange={e => setEditForm({...editForm, is_admitted: e.target.value})} 
              required
            >
              <option value={0}>Pending</option>
              <option value={1}>Admitted</option>
              <option value={2}>Rejected</option>
            </select>
          </div>
          
          <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-2)' }}>
            <Button type="button" variant="secondary" fullWidth onClick={() => setEditModalOpen(false)}>Cancel</Button>
            <Button type="submit" loading={saving} fullWidth>Save Changes</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
