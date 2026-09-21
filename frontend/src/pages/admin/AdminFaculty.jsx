import React, { useState, useEffect } from 'react'
import { managementApi } from '../../services/api'
import Card from '../../components/common/Card'
import Modal from '../../components/common/Modal'
import Button from '../../components/common/Button'
import FormInput from '../../components/common/FormInput'
import { notify } from '../../components/common/Toast'

export default function AdminFaculty() {
  const [faculty, setFaculty] = useState([])
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    department_id: '',
    employee_id: '',
    designation: 'Assistant Professor',
    phone: ''
  })
  const [submitting, setSubmitting] = useState(false)

  // Edit State
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [currentFaculty, setCurrentFaculty] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [saving, setSaving] = useState(false)

  const fetchData = async () => {
    try {
      const [facRes, deptRes] = await Promise.all([
        managementApi.getFaculty(),
        managementApi.getDepartments()
      ])
      setFaculty(facRes.data)
      setDepartments(deptRes.data)
      if (deptRes.data.length > 0 && !formData.department_id) {
        setFormData(f => ({ ...f, department_id: deptRes.data[0].id }))
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const res = await managementApi.createFaculty({
        ...formData,
        department_id: parseInt(formData.department_id)
      })
      notify.success(res.data.message || 'Faculty added successfully')
      
      if (res.data.temp_password) {
        alert(`Faculty Account Created!\nUsername: ${formData.name}\nTemp Password: ${res.data.temp_password}\n(Please save this, it won't be shown again)`)
      }
      
      setFormData({
        name: '', email: '', department_id: departments[0]?.id || '',
        employee_id: '', designation: 'Assistant Professor', phone: ''
      })
      fetchData()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to add faculty')
    } finally {
      setSubmitting(false)
    }
  }

  const handleEditClick = (f) => {
    setCurrentFaculty(f)
    const dept = departments.find(d => d.name === f.department)
    setEditForm({
      name: f.name || '',
      email: f.email || '',
      department_id: dept?.id || '',
      designation: f.designation || '',
      phone: f.phone || ''
    })
    setEditModalOpen(true)
  }

  const handleEditSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await managementApi.updateFaculty(currentFaculty.id, {
        ...editForm,
        department_id: parseInt(editForm.department_id)
      })
      notify.success('Faculty updated successfully')
      setEditModalOpen(false)
      fetchData()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to update faculty')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this faculty member?')) return
    try {
      await managementApi.deleteFaculty(id)
      notify.success('Faculty deleted')
      fetchData()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to delete faculty')
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Faculty Management</h1>
          <p className="page-subtitle">Manage faculty profiles and assignments.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: 'var(--space-6)', alignItems: 'start' }}>
        <Card title="Faculty Directory">
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="5" style={{ textAlign: 'center', padding: 'var(--space-4)' }}><div className="spinner" style={{ margin: '0 auto' }}></div></td></tr>
                ) : faculty.length === 0 ? (
                  <tr><td colSpan="5" style={{ textAlign: 'center', padding: 'var(--space-4)', color: 'var(--color-text-secondary)' }}>No faculty found.</td></tr>
                ) : (
                  faculty.map((f) => (
                    <tr key={f.id}>
                      <td><strong>{f.employee_id}</strong></td>
                      <td>
                        <div className="avatar-group">
                          <div className="avatar">{f.name?.charAt(0).toUpperCase()}</div>
                          <div>
                            <div style={{ fontWeight: '500' }}>{f.name}</div>
                            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>{f.email}</div>
                          </div>
                        </div>
                      </td>
                      <td>{f.department}</td>
                      <td>{f.designation}</td>
                      <td style={{ textAlign: 'right', display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        <Button variant="secondary" size="sm" onClick={() => handleEditClick(f)}>Edit</Button>
                        <Button variant="danger" size="sm" onClick={() => handleDelete(f.id)}>Delete</Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>

        <Card title="Add Faculty">
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <FormInput label="Employee ID" name="employee_id" value={formData.employee_id} onChange={handleChange} required placeholder="FAC-001" />
            <FormInput label="Full Name" name="name" value={formData.name} onChange={handleChange} required />
            <FormInput label="Email" type="email" name="email" value={formData.email} onChange={handleChange} required />
            
            <div>
              <label className="form-label">Department</label>
              <select 
                name="department_id" 
                value={formData.department_id} 
                onChange={handleChange} 
                className="form-input" 
                required
              >
                {departments.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            
            <FormInput label="Designation" name="designation" value={formData.designation} onChange={handleChange} required />
            <FormInput label="Phone" name="phone" value={formData.phone} onChange={handleChange} />
            
            <Button type="submit" loading={submitting} block>Add Faculty</Button>
          </form>
        </Card>
      </div>

      <Modal isOpen={editModalOpen} onClose={() => setEditModalOpen(false)} title={`Edit Faculty: ${currentFaculty?.employee_id}`}>
        <form onSubmit={handleEditSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <FormInput 
            label="Full Name" 
            value={editForm.name} 
            onChange={e => setEditForm({...editForm, name: e.target.value})} 
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
              onChange={e => setEditForm({...editForm, department_id: e.target.value})} 
              required
            >
              <option value="" disabled>Select Department</option>
              {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          <FormInput 
            label="Designation" 
            value={editForm.designation} 
            onChange={e => setEditForm({...editForm, designation: e.target.value})} 
            required 
          />
          <FormInput 
            label="Phone" 
            value={editForm.phone} 
            onChange={e => setEditForm({...editForm, phone: e.target.value})} 
          />
          
          <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-2)' }}>
            <Button type="button" variant="secondary" fullWidth onClick={() => setEditModalOpen(false)}>Cancel</Button>
            <Button type="submit" loading={saving} fullWidth>Save Changes</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
