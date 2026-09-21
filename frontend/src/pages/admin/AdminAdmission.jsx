import React, { useState, useEffect } from 'react'
import { managementApi } from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify as toast } from '../../components/common/Toast'

export default function AdminAdmission() {
  const [stagingRecords, setStagingRecords] = useState([])
  const [fetching, setFetching] = useState(true)

  // Advanced Allocation Engine State
  const [allocationFile, setAllocationFile] = useState(null)
  const [allocationLoading, setAllocationLoading] = useState({ upload: false, run: false, commit: false })

  const fetchStagingRecords = async () => {
    try {
      setFetching(true)
      const res = await managementApi.getStagingRecords()
      setStagingRecords(res.data.data)
    } catch (err) {
      toast.error('Failed to fetch staging records.')
    } finally {
      setFetching(false)
    }
  }

  useEffect(() => {
    fetchStagingRecords()
  }, [])

  const getStatusBadge = (status) => {
    switch(status) {
      case 'ADMISSION_CONFIRMED': return <span className="badge badge-success">Confirmed</span>
      case 'ELIGIBLE_FOR_ADMISSION': return <span className="badge badge-primary">Eligible</span>
      case 'ADMISSION_CANCELLED': return <span className="badge badge-danger">Cancelled</span>
      case 'WAITLISTED': return <span className="badge badge-warning">Waitlisted</span>
      case 'REJECTED_INELIGIBLE': return <span className="badge badge-danger">Rejected</span>
      case 'PENDING': return <span className="badge badge-primary" style={{opacity: 0.7}}>Pending</span>
      default: return <span className="badge">{status}</span>
    }
  }



  // --- Advanced Allocation Engine Handlers ---
  const handleAllocationFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setAllocationFile(e.target.files[0])
    }
  }

  const handleUploadStaging = async () => {
    if (!allocationFile) {
      toast.error('Please select an Excel file first.')
      return
    }
    setAllocationLoading(prev => ({ ...prev, upload: true }))
    const formData = new FormData()
    formData.append('file', allocationFile)

    try {
      const res = await managementApi.uploadStaging(formData)
      toast.success(res.data.message || 'Records staged successfully!')
      setAllocationFile(null)
      document.getElementById('allocation-file-upload').value = ''
      fetchStagingRecords()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to upload staging records.')
    } finally {
      setAllocationLoading(prev => ({ ...prev, upload: false }))
    }
  }

  const handleRunAllocation = async () => {
    setAllocationLoading(prev => ({ ...prev, run: true }))
    try {
      const res = await managementApi.runAllocation()
      toast.success(res.data.message || 'Allocation run successfully!')
      fetchStagingRecords()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to run allocation.')
    } finally {
      setAllocationLoading(prev => ({ ...prev, run: false }))
    }
  }

  const handleCommitAllocations = async () => {
    if (!window.confirm("Are you sure? This will create student accounts and generate admission PDFs for all Confirmed students.")) return
    setAllocationLoading(prev => ({ ...prev, commit: true }))
    try {
      const res = await managementApi.commitAllocations()
      if (res.data.success) {
        toast.success(res.data.message || 'Admissions provisioned successfully!')
        fetchStagingRecords()
      } else {
        toast.error(res.data.message || 'No records to commit.')
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to commit allocations.')
    } finally {
      setAllocationLoading(prev => ({ ...prev, commit: false }))
    }
  }

  const handleConfirmAction = async (id) => {
    try {
      const res = await managementApi.confirmAllocation(id)
      toast.success(res.data.message)
      fetchStagingRecords()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to confirm.')
    }
  }

  const handleCancelAction = async (id) => {
    if(!window.confirm("Cancel this admission? This will automatically advance the waitlist.")) return
    try {
      const res = await managementApi.cancelAllocation(id)
      toast.success(res.data.message)
      fetchStagingRecords()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to cancel.')
    }
  }

  const handleExportAllocation = () => {
    const token = localStorage.getItem('access_token')
    fetch('/api/allocation/export', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(async (res) => {
      if (!res.ok) throw new Error('Export failed')
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `allocation_results.xlsx`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    })
    .catch((err) => {
      toast.error('Failed to download allocation results.')
    })
  }

  const handleClearStaging = async () => {
    if (!window.confirm("Are you sure you want to clear all staging records? This cannot be undone.")) return
    try {
      const res = await managementApi.clearStaging()
      toast.success(res.data.message || 'Staging cleared successfully')
      fetchStagingRecords()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to clear staging.')
    }
  }

  return (
    <div className="admin-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Admission Automation</h1>
          <p className="page-subtitle">Upload student records via Excel to auto-admit, generate letters, and send emails.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 'var(--space-6)' }}>
        {/* Advanced Allocation Engine Card */}
        <Card title="Advanced Allocation Engine" subtitle="Automated seat matrix, quotas & tie-breaking logic">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 'var(--space-5)', alignItems: 'start' }}>
            
            {/* Step 1 */}
            <div style={{ padding: 'var(--space-4)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', background: 'var(--color-bg)' }}>
              <h3 style={{ fontSize: 'var(--text-sm)', marginBottom: 'var(--space-3)' }}>Step 1: Upload Staging Data</h3>
              <input 
                id="allocation-file-upload"
                type="file" 
                accept=".xlsx, .xls"
                onChange={handleAllocationFileChange}
                style={{
                  width: '100%',
                  padding: 'var(--space-2)',
                  border: '1px dashed var(--color-border)',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: 'var(--space-3)',
                  fontSize: 'var(--text-xs)'
                }}
              />
              <Button 
                variant="primary" 
                size="sm"
                onClick={handleUploadStaging} 
                isLoading={allocationLoading.upload}
                disabled={!allocationFile}
                style={{ width: '100%' }}
              >
                📥 Stage Records
              </Button>
            </div>

            {/* Step 2 */}
            <div style={{ padding: 'var(--space-4)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', background: 'var(--color-bg)' }}>
              <h3 style={{ fontSize: 'var(--text-sm)', marginBottom: 'var(--space-3)' }}>Step 2: Run Allocation Engine</h3>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-3)' }}>
                Executes the two-pass eligibility and deterministic merit tie-breaking algorithm across all quotas.
              </p>
              <Button 
                variant="primary" 
                size="sm"
                onClick={handleRunAllocation} 
                isLoading={allocationLoading.run}
                style={{ width: '100%' }}
              >
                ⚙️ Run Engine
              </Button>
            </div>

            {/* Step 3 */}
            <div style={{ padding: 'var(--space-4)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', background: 'var(--color-bg)' }}>
              <h3 style={{ fontSize: 'var(--text-sm)', marginBottom: 'var(--space-3)' }}>Step 3: Commit & Provision</h3>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-3)' }}>
                Creates student accounts and generates Admission Letters for confirmed candidates.
              </p>
              <Button 
                variant="primary" 
                size="sm"
                onClick={handleCommitAllocations} 
                isLoading={allocationLoading.commit}
                style={{ width: '100%' }}
              >
                ✅ Commit Admissions
              </Button>
            </div>

            {/* Step 4 */}
            <div style={{ padding: 'var(--space-4)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', background: 'var(--color-bg)' }}>
              <h3 style={{ fontSize: 'var(--text-sm)', marginBottom: 'var(--space-3)' }}>Step 4: Export Results</h3>
              <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-3)' }}>
                Download the exact seat allocations, waitlist ranks, and rejection reason logs.
              </p>
              <Button 
                variant="secondary" 
                size="sm"
                onClick={handleExportAllocation} 
                style={{ width: '100%' }}
              >
                📊 Download Excel
              </Button>
            </div>

          </div>
        </Card>

        {/* Staged Applications Table */}
        <Card 
          title="Staged Applications & Allocations" 
          subtitle="Live view of the staging database"
          actions={
            <Button variant="danger" size="sm" onClick={handleClearStaging}>
              🗑️ Clear Staging
            </Button>
          }
        >
          {fetching ? (
            <p>Loading staging data...</p>
          ) : stagingRecords.length === 0 ? (
            <p style={{ color: 'var(--color-text-secondary)' }}>No staging records found. Upload an Excel file to begin.</p>
          ) : (
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Course</th>
                    <th>Category</th>
                    <th>Scores (12th / Core / Entrance)</th>
                    <th>Status</th>
                    <th>Seat Type</th>
                    <th>Reason / Details</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {stagingRecords.map((r) => (
                    <tr key={r.id}>
                      <td>
                        <div className="avatar-group">
                          <div className="avatar">{r.student_name?.charAt(0).toUpperCase()}</div>
                          <div>
                            <div style={{ fontWeight: '500' }}>{r.student_name}</div>
                            <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)' }}>{r.student_id}</div>
                          </div>
                        </div>
                      </td>
                      <td>{r.applied_course}</td>
                      <td>{r.candidate_category}</td>
                      <td style={{ fontSize: 'var(--text-xs)' }}>
                        <div>12th: {r.class_12_pct}%</div>
                        <div>Core: {r.core_subject_score}</div>
                        <div>Entrance: {r.entrance_exam_score}</div>
                      </td>
                      <td>{getStatusBadge(r.final_admission_status)}</td>
                      <td>{r.allocated_seat_type === 'NONE' ? '-' : r.allocated_seat_type}</td>
                      <td style={{ fontSize: 'var(--text-xs)', maxWidth: '200px', whiteSpace: 'normal' }}>
                        {r.reason_code_logs || '-'}
                      </td>
                      <td>
                        {r.final_admission_status === 'ELIGIBLE_FOR_ADMISSION' && (
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <Button variant="success" size="sm" onClick={() => handleConfirmAction(r.id)}>Confirm</Button>
                            <Button variant="danger" size="sm" onClick={() => handleCancelAction(r.id)}>Cancel</Button>
                          </div>
                        )}
                        {(() => {
                          const provisionMatch = r.reason_code_logs?.match(/\[PROVISIONED:\s*([^\]]+)\]/);
                          if (provisionMatch) {
                            const enrollNo = provisionMatch[1];
                            return (
                              <a href={`http://localhost:8000/api/admission/letter/${enrollNo}`} target="_blank" rel="noreferrer" style={{ display: 'inline-block', marginTop: r.final_admission_status === 'ELIGIBLE_FOR_ADMISSION' ? '8px' : '0' }}>
                                <Button variant="secondary" size="sm">📄 Letter</Button>
                              </a>
                            );
                          }
                          return null;
                        })()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
