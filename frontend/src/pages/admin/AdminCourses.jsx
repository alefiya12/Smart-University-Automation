import React, { useState, useEffect } from 'react'
import { managementApi } from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Input from '../../components/common/FormInput'
import Modal from '../../components/common/Modal'
import { notify as toast } from '../../components/common/Toast'

export default function AdminCourses() {
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  
  const [editCourse, setEditCourse] = useState(null)
  const [formData, setFormData] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Subject Management
  const [subjectsModalOpen, setSubjectsModalOpen] = useState(false)
  const [currentCourse, setCurrentCourse] = useState(null)
  const [subjects, setSubjects] = useState([])
  const [newSubject, setNewSubject] = useState('')
  const [newSubjectSem, setNewSubjectSem] = useState(1)
  const [loadingSubjects, setLoadingSubjects] = useState(false)

  const fetchDepartments = async () => {
    try {
      const res = await managementApi.getDepartments()
      setDepartments(res.data)
    } catch (err) {
      toast.error('Failed to load courses')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDepartments()
  }, [])

  const handleEditClick = (course) => {
    setEditCourse(course)
    setFormData({
      name: course.name,
      code: course.code,
      duration_semesters: course.duration_semesters,
      total_seats: course.total_seats,
      quota_sc: course.quota_sc,
      quota_st: course.quota_st,
      quota_obc: course.quota_obc,
      quota_ews: course.quota_ews,
      min_class_12_pct: course.min_class_12_pct,
      min_core_subject_score: course.min_core_subject_score,
      relaxation_sc_st_pct: course.relaxation_sc_st_pct,
      relaxation_obc_ews_pct: course.relaxation_obc_ews_pct
    })
  }

  const handleFormChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: field === 'name' || field === 'code' ? value : Number(value)
    }))
  }

  const handleSave = async () => {
    // Validate quotas
    const totalQuota = formData.quota_sc + formData.quota_st + formData.quota_obc + formData.quota_ews
    if (totalQuota > 100) {
      toast.error(`Total quota percentage cannot exceed 100%. Currently it is ${totalQuota}%.`)
      return
    }

    setIsSubmitting(true)
    try {
      await managementApi.updateCourse(editCourse.id, formData)
      toast.success('Course settings updated successfully')
      setEditCourse(null)
      fetchDepartments()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update course settings')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleManageSubjects = async (course) => {
    setCurrentCourse(course)
    setSubjectsModalOpen(true)
    setLoadingSubjects(true)
    try {
      const res = await managementApi.getCourseSubjects(course.id)
      setSubjects(res.data)
    } catch (err) {
      toast.error('Failed to fetch subjects')
    } finally {
      setLoadingSubjects(false)
    }
  }

  const handleAddSubject = async (e) => {
    e.preventDefault()
    if (!newSubject.trim()) return
    try {
      const res = await managementApi.addCourseSubject(currentCourse.id, { 
        subject_name: newSubject.trim(),
        semester: Number(newSubjectSem)
      })
      setSubjects([...subjects, res.data])
      setNewSubject('')
      setNewSubjectSem(1)
      toast.success('Subject added successfully')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add subject')
    }
  }

  const handleDeleteSubject = async (subjectId) => {
    if (!window.confirm('Are you sure you want to delete this subject?')) return
    try {
      await managementApi.deleteCourseSubject(currentCourse.id, subjectId)
      setSubjects(subjects.filter(s => s.id !== subjectId))
      toast.success('Subject deleted successfully')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete subject')
    }
  }

  if (loading) return <div>Loading course settings...</div>

  return (
    <div className="admin-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Course Settings</h1>
          <p className="page-subtitle">Configure seat capacities, reservation quotas, and eligibility rules for courses.</p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        {departments.map(dept => (
          dept.courses.length > 0 && (
            <Card key={dept.id} title={`${dept.name} (${dept.code})`} subtitle="Department Courses">
              <div className="table-responsive">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Course</th>
                      <th>Total Seats</th>
                      <th>Quotas (SC / ST / OBC / EWS)</th>
                      <th>Open Merit (GEN)</th>
                      <th>Eligibility Min %</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dept.courses.map(course => {
                      const totalReserved = course.quota_sc + course.quota_st + course.quota_obc + course.quota_ews;
                      const openMerit = Math.max(0, 100 - totalReserved);
                      
                      return (
                        <tr key={course.id}>
                          <td>
                            <div style={{ fontWeight: '500' }}>{course.name}</div>
                            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>{course.code} • {course.duration_semesters} Sems</div>
                          </td>
                          <td>
                            <span className="badge badge-primary">{course.total_seats} Seats</span>
                          </td>
                          <td style={{ fontSize: 'var(--text-xs)' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px' }}>
                              <span>SC: {course.quota_sc}%</span>
                              <span>ST: {course.quota_st}%</span>
                              <span>OBC: {course.quota_obc}%</span>
                              <span>EWS: {course.quota_ews}%</span>
                            </div>
                          </td>
                          <td>
                            <span className={`badge badge-${openMerit > 0 ? 'success' : 'danger'}`}>{openMerit.toFixed(1)}%</span>
                          </td>
                          <td style={{ fontSize: 'var(--text-xs)' }}>
                            <div>12th: {course.min_class_12_pct}%</div>
                            <div>Core: {course.min_core_subject_score}%</div>
                          </td>
                          <td style={{ display: 'flex', gap: '8px' }}>
                            <Button variant="secondary" size="sm" onClick={() => handleEditClick(course)}>
                              ⚙️ Configure
                            </Button>
                            <Button variant="primary" size="sm" onClick={() => handleManageSubjects(course)}>
                              📚 Subjects
                            </Button>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </Card>
          )
        ))}
      </div>

      {editCourse && formData && (
        <Modal
          title={`Configure Settings: ${editCourse.name}`}
          isOpen={true}
          onClose={() => setEditCourse(null)}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
            
            {/* General Settings */}
            <div>
              <h4 style={{ marginBottom: 'var(--space-3)', color: 'var(--color-text-primary)' }}>General Configurations</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                <Input label="Course Name" value={formData.name} onChange={e => handleFormChange('name', e.target.value)} required />
                <Input label="Course Code" value={formData.code} onChange={e => handleFormChange('code', e.target.value)} required />
                <Input label="Total Semesters" type="number" value={formData.duration_semesters} onChange={e => handleFormChange('duration_semesters', e.target.value)} required />
                <Input label="Total Seats Capacity" type="number" value={formData.total_seats} onChange={e => handleFormChange('total_seats', e.target.value)} required />
              </div>
            </div>

            {/* Quota Settings */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 'var(--space-3)' }}>
                <h4 style={{ color: 'var(--color-text-primary)' }}>Vertical Reservation Quotas (%)</h4>
                <span className={`badge badge-${(formData.quota_sc + formData.quota_st + formData.quota_obc + formData.quota_ews) > 100 ? 'danger' : 'success'}`}>
                  Total: {formData.quota_sc + formData.quota_st + formData.quota_obc + formData.quota_ews}%
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                <Input label="SC Quota %" type="number" step="0.1" value={formData.quota_sc} onChange={e => handleFormChange('quota_sc', e.target.value)} />
                <Input label="ST Quota %" type="number" step="0.1" value={formData.quota_st} onChange={e => handleFormChange('quota_st', e.target.value)} />
                <Input label="OBC Quota %" type="number" step="0.1" value={formData.quota_obc} onChange={e => handleFormChange('quota_obc', e.target.value)} />
                <Input label="EWS Quota %" type="number" step="0.1" value={formData.quota_ews} onChange={e => handleFormChange('quota_ews', e.target.value)} />
              </div>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: 'var(--space-2)' }}>
                * Remaining percentage ({(100 - (formData.quota_sc + formData.quota_st + formData.quota_obc + formData.quota_ews)).toFixed(1)}%) will be automatically allocated to Open Merit (GEN).
              </p>
            </div>

            {/* Eligibility Settings */}
            <div>
              <h4 style={{ marginBottom: 'var(--space-3)', color: 'var(--color-text-primary)' }}>Eligibility Rules</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                <Input label="Min 12th Percentage" type="number" step="0.1" value={formData.min_class_12_pct} onChange={e => handleFormChange('min_class_12_pct', e.target.value)} />
                <Input label="Min Core Subject Score" type="number" step="0.1" value={formData.min_core_subject_score} onChange={e => handleFormChange('min_core_subject_score', e.target.value)} />
                <Input label="SC/ST Relaxation %" type="number" step="0.1" value={formData.relaxation_sc_st_pct} onChange={e => handleFormChange('relaxation_sc_st_pct', e.target.value)} />
                <Input label="OBC/EWS Relaxation %" type="number" step="0.1" value={formData.relaxation_obc_ews_pct} onChange={e => handleFormChange('relaxation_obc_ews_pct', e.target.value)} />
              </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-3)', marginTop: 'var(--space-4)', paddingTop: 'var(--space-4)', borderTop: '1px solid var(--color-border)' }}>
              <Button variant="ghost" onClick={() => setEditCourse(null)}>Cancel</Button>
              <Button variant="primary" onClick={handleSave} loading={isSubmitting}>Save Settings</Button>
            </div>

          </div>
        </Modal>
      )}

      {subjectsModalOpen && currentCourse && (
        <Modal
          title={`Manage Subjects: ${currentCourse.name}`}
          isOpen={true}
          onClose={() => setSubjectsModalOpen(false)}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
            
            <form onSubmit={handleAddSubject} style={{ display: 'flex', gap: 'var(--space-2)' }}>
              <div style={{ flex: 2 }}>
                <Input 
                  placeholder="Subject name..." 
                  value={newSubject} 
                  onChange={e => setNewSubject(e.target.value)} 
                  required 
                />
              </div>
              <div style={{ flex: 1 }}>
                <Input 
                  type="number"
                  min="1" max="10"
                  placeholder="Sem" 
                  value={newSubjectSem} 
                  onChange={e => setNewSubjectSem(e.target.value)} 
                  required 
                />
              </div>
              <Button type="submit" variant="primary">Add</Button>
            </form>

            <div style={{ marginTop: 'var(--space-4)' }}>
              <h4 style={{ marginBottom: 'var(--space-3)' }}>Registered Subjects</h4>
              {loadingSubjects ? (
                <div style={{ padding: 'var(--space-4)', textAlign: 'center' }}>Loading subjects...</div>
              ) : subjects.length === 0 ? (
                <div style={{ padding: 'var(--space-4)', textAlign: 'center', color: 'var(--color-text-secondary)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                  No subjects registered. Add subjects to allow attendance tracking.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                  {subjects.map(sub => (
                    <div key={sub.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 'var(--space-3)', background: 'var(--color-bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                      <div style={{ fontWeight: '500' }}>
                        {sub.subject_name} <span className="badge badge-secondary" style={{marginLeft: '8px'}}>Sem {sub.semester}</span>
                      </div>
                      <Button variant="danger" size="sm" onClick={() => handleDeleteSubject(sub.id)}>Delete</Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'var(--space-4)', paddingTop: 'var(--space-4)', borderTop: '1px solid var(--color-border)' }}>
              <Button variant="secondary" onClick={() => setSubjectsModalOpen(false)}>Close</Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}

