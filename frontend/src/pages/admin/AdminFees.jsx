import React, { useState, useEffect } from 'react'
import { managementApi } from '../../services/api'
import Card from '../../components/common/Card'
import Modal from '../../components/common/Modal'
import Button from '../../components/common/Button'
import FormInput from '../../components/common/FormInput'
import { notify } from '../../components/common/Toast'

export default function AdminFees() {
  const [fees, setFees] = useState([])
  const [loading, setLoading] = useState(true)

  const [formData, setFormData] = useState({
    enrollment_no: '',
    fee_type: 'tuition',
    amount: '',
    description: '',
    due_date: '',
    semester: '1',
    academic_year: '2026-2027'
  })
  const [submitting, setSubmitting] = useState(false)

  // Edit State
  const [editModalOpen, setEditModalOpen] = useState(false)
  const [currentFee, setCurrentFee] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [saving, setSaving] = useState(false)

  const fetchFees = async () => {
    try {
      const res = await managementApi.getFees()
      setFees(res.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchFees()
  }, [])

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await managementApi.createFee({
        ...formData,
        amount: parseFloat(formData.amount),
        semester: parseInt(formData.semester)
      })
      notify.success('Fee invoice generated')
      setFormData({
        ...formData, enrollment_no: '', amount: '', description: ''
      })
      fetchFees()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to generate invoice')
    } finally {
      setSubmitting(false)
    }
  }

  const handleEditClick = (f) => {
    setCurrentFee(f)
    setEditForm({
      amount: f.amount || '',
      due_date: f.due_date || '',
      status: f.status || 'pending'
    })
    setEditModalOpen(true)
  }

  const handleEditSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await managementApi.updateFee(currentFee.id, {
        ...editForm,
        amount: parseFloat(editForm.amount)
      })
      notify.success('Fee invoice updated')
      setEditModalOpen(false)
      fetchFees()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to update fee')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this invoice?')) return
    try {
      await managementApi.deleteFee(id)
      notify.success('Fee invoice deleted')
      fetchFees()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to delete invoice')
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Fee Management</h1>
          <p className="page-subtitle">Track payments and manage invoices.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: 'var(--space-6)', alignItems: 'start' }}>
        <Card title="Fee Invoices">
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Due Date</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan="6" style={{ textAlign: 'center', padding: 'var(--space-4)' }}><div className="spinner" style={{ margin: '0 auto' }}></div></td></tr>
                ) : fees.length === 0 ? (
                  <tr><td colSpan="6" style={{ textAlign: 'center', padding: 'var(--space-4)', color: 'var(--color-text-secondary)' }}>No fee invoices found.</td></tr>
                ) : (
                  fees.map((f) => (
                    <tr key={f.id}>
                      <td>
                        <div className="avatar-group">
                          <div className="avatar" style={{ background: '#F0F9FF', color: 'var(--color-info)' }}>{f.student_name?.charAt(0).toUpperCase()}</div>
                          <div>
                            <div style={{ fontWeight: '500' }}>{f.student_name}</div>
                            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>{f.enrollment_no}</div>
                          </div>
                        </div>
                      </td>
                      <td style={{ textTransform: 'capitalize' }}>{f.fee_type}</td>
                      <td>${f.amount.toFixed(2)}</td>
                      <td>{f.due_date || 'N/A'}</td>
                      <td>
                        <span className={`badge ${
                          f.status === 'paid' ? 'badge-success' : 
                          f.status === 'pending' ? 'badge-warning' : 
                          f.status === 'overdue' ? 'badge-danger' : 'badge-primary'
                        }`}>
                          {f.status}
                        </span>
                      </td>
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

        <Card title="Generate Invoice">
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <FormInput label="Student Enrollment No" name="enrollment_no" value={formData.enrollment_no} onChange={handleChange} required placeholder="SU2026-0001" />
            
            <div>
              <label className="form-label">Fee Type</label>
              <select name="fee_type" value={formData.fee_type} onChange={handleChange} className="form-input" required>
                <option value="tuition">Tuition Fee</option>
                <option value="exam">Exam Fee</option>
                <option value="library">Library Fee</option>
                <option value="hostel">Hostel Fee</option>
                <option value="other">Other</option>
              </select>
            </div>
            
            <FormInput label="Amount ($)" type="number" step="0.01" name="amount" value={formData.amount} onChange={handleChange} required placeholder="1500.00" />
            <FormInput label="Due Date" type="date" name="due_date" value={formData.due_date} onChange={handleChange} required />
            <FormInput label="Semester" type="number" min="1" max="10" name="semester" value={formData.semester} onChange={handleChange} required />
            <FormInput label="Academic Year" name="academic_year" value={formData.academic_year} onChange={handleChange} required />
            <FormInput label="Description (Optional)" name="description" value={formData.description} onChange={handleChange} placeholder="e.g. Fall Semester Tuition" />
            
            <Button type="submit" loading={submitting} block>Generate Invoice</Button>
          </form>
        </Card>
      </div>

      <Modal isOpen={editModalOpen} onClose={() => setEditModalOpen(false)} title={`Edit Fee Invoice`}>
        <form onSubmit={handleEditSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <FormInput 
            label="Amount ($)" 
            type="number" step="0.01" 
            value={editForm.amount} 
            onChange={e => setEditForm({...editForm, amount: e.target.value})} 
            required 
          />
          <FormInput 
            label="Due Date" 
            type="date" 
            value={editForm.due_date} 
            onChange={e => setEditForm({...editForm, due_date: e.target.value})} 
            required 
          />
          <div>
            <label className="form-label">Status</label>
            <select 
              className="form-input" 
              value={editForm.status} 
              onChange={e => setEditForm({...editForm, status: e.target.value})} 
              required
            >
              <option value="pending">Pending</option>
              <option value="paid">Paid</option>
              <option value="overdue">Overdue</option>
              <option value="refunded">Refunded</option>
              <option value="cancelled">Cancelled</option>
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
