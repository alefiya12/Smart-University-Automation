import React, { useState, useEffect } from 'react'
import { managementApi } from '../../services/api'
import Card from '../../components/common/Card'
import Modal from '../../components/common/Modal'
import Button from '../../components/common/Button'
import FormInput from '../../components/common/FormInput'
import { notify } from '../../components/common/Toast'

export default function AdminDepartments() {
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)

  const [deptForm, setDeptForm] = useState({ name: '', code: '' })
  const initialCourseState = {
    name: '', code: '', duration_semesters: 6,
    total_seats: 60, quota_obc: 27.0, quota_sc: 15.0, quota_st: 7.5, quota_ews: 10.0,
    min_class_12_pct: 60.0, min_core_subject_score: 50.0,
    relaxation_sc_st_pct: 5.0, relaxation_obc_ews_pct: 0.0
  }
  const [courseForm, setCourseForm] = useState(initialCourseState)
  const [selectedDeptId, setSelectedDeptId] = useState('')

  const [submittingDept, setSubmittingDept] = useState(false)
  const [submittingCourse, setSubmittingCourse] = useState(false)

  // Edit States
  const [editDeptModalOpen, setEditDeptModalOpen] = useState(false)
  const [editCourseModalOpen, setEditCourseModalOpen] = useState(false)
  
  const [currentDept, setCurrentDept] = useState(null)
  const [currentCourse, setCurrentCourse] = useState(null)
  
  const [editDeptForm, setEditDeptForm] = useState({})
  const [editCourseForm, setEditCourseForm] = useState({})
  const [saving, setSaving] = useState(false)

  const fetchDepartments = async () => {
    try {
      const res = await managementApi.getDepartments()
      setDepartments(res.data)
      if (res.data.length > 0 && !selectedDeptId) {
        setSelectedDeptId(res.data[0].id.toString())
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDepartments()
  }, [])

  const handleCreateDept = async (e) => {
    e.preventDefault()
    setSubmittingDept(true)
    try {
      await managementApi.createDepartment(deptForm)
      notify.success('Department created')
      setDeptForm({ name: '', code: '' })
      fetchDepartments()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to create department')
    } finally {
      setSubmittingDept(false)
    }
  }

  const handleCreateCourse = async (e) => {
    e.preventDefault()
    if (!selectedDeptId) return notify.error("Select a department first")
    setSubmittingCourse(true)
    try {
      await managementApi.createCourse(selectedDeptId, courseForm)
      notify.success('Course created')
      setCourseForm(initialCourseState)
      fetchDepartments()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to create course')
    } finally {
      setSubmittingCourse(false)
    }
  }

  // Edit/Delete Department
  const handleEditDeptClick = (d) => {
    setCurrentDept(d)
    setEditDeptForm({ name: d.name, code: d.code })
    setEditDeptModalOpen(true)
  }

  const handleEditDeptSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await managementApi.updateDepartment(currentDept.id, editDeptForm)
      notify.success('Department updated')
      setEditDeptModalOpen(false)
      fetchDepartments()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to update department')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteDept = async (id) => {
    if (!window.confirm('Delete this department? All nested courses will also be deleted. This cannot be undone.')) return
    try {
      await managementApi.deleteDepartment(id)
      notify.success('Department deleted')
      fetchDepartments()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to delete department')
    }
  }

  // Edit/Delete Course
  const handleEditCourseClick = (c) => {
    setCurrentCourse(c)
    setEditCourseForm({ 
      name: c.name, code: c.code, duration_semesters: c.duration_semesters,
      total_seats: c.total_seats ?? 60,
      quota_obc: c.quota_obc ?? 27.0,
      quota_sc: c.quota_sc ?? 15.0,
      quota_st: c.quota_st ?? 7.5,
      quota_ews: c.quota_ews ?? 10.0,
      min_class_12_pct: c.min_class_12_pct ?? 60.0,
      min_core_subject_score: c.min_core_subject_score ?? 50.0,
      relaxation_sc_st_pct: c.relaxation_sc_st_pct ?? 5.0,
      relaxation_obc_ews_pct: c.relaxation_obc_ews_pct ?? 0.0
    })
    setEditCourseModalOpen(true)
  }

  const handleEditCourseSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await managementApi.updateCourse(currentCourse.id, {
        ...editCourseForm,
        duration_semesters: parseInt(editCourseForm.duration_semesters),
        total_seats: parseInt(editCourseForm.total_seats),
        quota_obc: parseFloat(editCourseForm.quota_obc),
        quota_sc: parseFloat(editCourseForm.quota_sc),
        quota_st: parseFloat(editCourseForm.quota_st),
        quota_ews: parseFloat(editCourseForm.quota_ews),
        min_class_12_pct: parseFloat(editCourseForm.min_class_12_pct),
        min_core_subject_score: parseFloat(editCourseForm.min_core_subject_score),
        relaxation_sc_st_pct: parseFloat(editCourseForm.relaxation_sc_st_pct),
        relaxation_obc_ews_pct: parseFloat(editCourseForm.relaxation_obc_ews_pct)
      })
      notify.success('Course updated')
      setEditCourseModalOpen(false)
      fetchDepartments()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to update course')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteCourse = async (id) => {
    if (!window.confirm('Delete this course? This cannot be undone.')) return
    try {
      await managementApi.deleteCourse(id)
      notify.success('Course deleted')
      fetchDepartments()
    } catch (err) {
      notify.error(err.response?.data?.detail || 'Failed to delete course')
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Departments & Courses</h1>
          <p className="page-subtitle">Configure the academic structure of the university.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--space-6)', marginBottom: 'var(--space-6)' }}>
        <Card title="Add Department">
          <form onSubmit={handleCreateDept} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <FormInput label="Department Name" value={deptForm.name} onChange={e => setDeptForm({...deptForm, name: e.target.value})} required placeholder="e.g. Computer Science" />
            <FormInput label="Department Code" value={deptForm.code} onChange={e => setDeptForm({...deptForm, code: e.target.value})} required placeholder="e.g. CS" />
            <Button type="submit" loading={submittingDept}>Create Department</Button>
          </form>
        </Card>

        <Card title="Add Course">
          <form onSubmit={handleCreateCourse} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            <div>
              <label className="form-label">Under Department</label>
              <select className="form-input" value={selectedDeptId} onChange={e => setSelectedDeptId(e.target.value)} required>
                {departments.map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
            <FormInput label="Course Name" value={courseForm.name} onChange={e => setCourseForm({...courseForm, name: e.target.value})} required placeholder="e.g. B.Tech CSE" />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
              <FormInput label="Course Code" value={courseForm.code} onChange={e => setCourseForm({...courseForm, code: e.target.value})} required placeholder="e.g. BTECH-CSE" />
              <FormInput label="Total Semesters" type="number" min="1" max="10" value={courseForm.duration_semesters} onChange={e => setCourseForm({...courseForm, duration_semesters: parseInt(e.target.value)})} required />
            </div>
            <Button type="submit" loading={submittingCourse}>Create Course</Button>
          </form>
        </Card>
      </div>

      <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: '600', marginBottom: 'var(--space-4)' }}>Current Structure</h2>
      {loading ? (
        <div className="spinner" style={{ margin: 'var(--space-8) auto' }}></div>
      ) : departments.length === 0 ? (
        <div style={{ color: 'var(--color-text-secondary)' }}>No departments found.</div>
      ) : (
        <div style={{ display: 'grid', gap: 'var(--space-4)' }}>
          {departments.map(d => (
            <Card key={d.id}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
                <h3 style={{ margin: 0, fontSize: 'var(--text-md)', fontWeight: 600 }}>{d.name} ({d.code})</h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Button variant="secondary" size="sm" onClick={() => handleEditDeptClick(d)}>Edit Dept</Button>
                  <Button variant="danger" size="sm" onClick={() => handleDeleteDept(d.id)}>Delete</Button>
                </div>
              </div>
              
              {d.courses && d.courses.length > 0 ? (
                <div style={{ display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
                  {d.courses.map(c => (
                    <div key={c.id} style={{ 
                      background: '#F3F4F6', color: 'var(--color-text-primary)', 
                      padding: '8px 12px', fontSize: 'var(--text-sm)', borderRadius: 'var(--radius-md)',
                      display: 'flex', alignItems: 'center', gap: '8px'
                    }}>
                      <span>{c.name} ({c.code}) - {c.duration_semesters} Sems</span>
                      <span onClick={() => handleEditCourseClick(c)} style={{ cursor: 'pointer', opacity: 0.6 }}>✏️</span>
                      <span onClick={() => handleDeleteCourse(c.id)} style={{ cursor: 'pointer', opacity: 0.6 }}>✖</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ color: 'var(--color-text-tertiary)', fontSize: 'var(--text-sm)' }}>No courses assigned to this department yet.</div>
              )}
            </Card>
          ))}
        </div>
      )}

      {/* Edit Department Modal */}
      <Modal isOpen={editDeptModalOpen} onClose={() => setEditDeptModalOpen(false)} title="Edit Department">
        <form onSubmit={handleEditDeptSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <FormInput 
            label="Department Name" 
            value={editDeptForm.name} 
            onChange={e => setEditDeptForm({...editDeptForm, name: e.target.value})} 
            required 
          />
          <FormInput 
            label="Department Code" 
            value={editDeptForm.code} 
            onChange={e => setEditDeptForm({...editDeptForm, code: e.target.value})} 
            required 
          />
          <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-2)' }}>
            <Button type="button" variant="secondary" fullWidth onClick={() => setEditDeptModalOpen(false)}>Cancel</Button>
            <Button type="submit" loading={saving} fullWidth>Save Changes</Button>
          </div>
        </form>
      </Modal>

      {/* Edit Course Modal */}
      <Modal isOpen={editCourseModalOpen} onClose={() => setEditCourseModalOpen(false)} title="Edit Course Configuration">
        <form onSubmit={handleEditCourseSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', maxHeight: '70vh', overflowY: 'auto', paddingRight: '10px' }}>
          
          <h4 style={{ margin: '0 0 var(--space-2) 0', color: 'var(--color-primary)' }}>Basic Details</h4>
          <FormInput 
            label="Course Name" 
            value={editCourseForm.name} 
            onChange={e => setEditCourseForm({...editCourseForm, name: e.target.value})} 
            required 
          />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--space-4)' }}>
            <FormInput 
              label="Course Code" 
              value={editCourseForm.code} 
              onChange={e => setEditCourseForm({...editCourseForm, code: e.target.value})} 
              required 
            />
            <FormInput 
              label="Total Semesters" 
              type="number" min="1" max="10" 
              value={editCourseForm.duration_semesters} 
              onChange={e => setEditCourseForm({...editCourseForm, duration_semesters: e.target.value})} 
              required 
            />
            <FormInput 
              label="Total Seats" 
              type="number" min="1"
              value={editCourseForm.total_seats} 
              onChange={e => setEditCourseForm({...editCourseForm, total_seats: e.target.value})} 
              required 
            />
          </div>

          <h4 style={{ margin: 'var(--space-2) 0 0 0', color: 'var(--color-primary)' }}>Reservation Matrix (%)</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 'var(--space-4)' }}>
            <FormInput label="OBC Quota" type="number" step="0.1" value={editCourseForm.quota_obc} onChange={e => setEditCourseForm({...editCourseForm, quota_obc: e.target.value})} />
            <FormInput label="SC Quota" type="number" step="0.1" value={editCourseForm.quota_sc} onChange={e => setEditCourseForm({...editCourseForm, quota_sc: e.target.value})} />
            <FormInput label="ST Quota" type="number" step="0.1" value={editCourseForm.quota_st} onChange={e => setEditCourseForm({...editCourseForm, quota_st: e.target.value})} />
            <FormInput label="EWS Quota" type="number" step="0.1" value={editCourseForm.quota_ews} onChange={e => setEditCourseForm({...editCourseForm, quota_ews: e.target.value})} />
          </div>

          <h4 style={{ margin: 'var(--space-2) 0 0 0', color: 'var(--color-primary)' }}>Eligibility & Relaxation Thresholds</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
            <FormInput label="Min Class 12 %" type="number" step="0.1" value={editCourseForm.min_class_12_pct} onChange={e => setEditCourseForm({...editCourseForm, min_class_12_pct: e.target.value})} />
            <FormInput label="Min Core Subject Score" type="number" step="0.1" value={editCourseForm.min_core_subject_score} onChange={e => setEditCourseForm({...editCourseForm, min_core_subject_score: e.target.value})} />
            <FormInput label="SC/ST Relaxation %" type="number" step="0.1" value={editCourseForm.relaxation_sc_st_pct} onChange={e => setEditCourseForm({...editCourseForm, relaxation_sc_st_pct: e.target.value})} />
            <FormInput label="OBC/EWS Relaxation %" type="number" step="0.1" value={editCourseForm.relaxation_obc_ews_pct} onChange={e => setEditCourseForm({...editCourseForm, relaxation_obc_ews_pct: e.target.value})} />
          </div>

          <div style={{ display: 'flex', gap: 'var(--space-3)', marginTop: 'var(--space-4)' }}>
            <Button type="button" variant="secondary" fullWidth onClick={() => setEditCourseModalOpen(false)}>Cancel</Button>
            <Button type="submit" loading={saving} fullWidth>Save Changes</Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
