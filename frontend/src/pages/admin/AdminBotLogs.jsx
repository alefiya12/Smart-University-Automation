import React, { useState, useEffect } from 'react'
import { managementApi } from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify } from '../../components/common/Toast'

export default function AdminBotLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  const [filters, setFilters] = useState({
    bot_name: '',
    status: ''
  })
  const [pagination, setPagination] = useState({ page: 1, total: 0, pages: 1 })

  const fetchLogs = async (page = 1) => {
    setLoading(true)
    try {
      const params = { page, page_size: 20 }
      if (filters.bot_name) params.bot_name = filters.bot_name
      if (filters.status) params.status = filters.status
      
      const res = await managementApi.getBotLogs(params)
      setLogs(res.data.data)
      setPagination(res.data.pagination)
    } catch (err) {
      console.error(err)
      notify.error('Failed to fetch bot logs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs(1)
  }, [filters])

  const getStatusBadge = (status) => {
    switch(status) {
      case 'success': return <span className="badge badge-success">Success</span>
      case 'running': return <span className="badge badge-primary">Running</span>
      case 'failed':  return <span className="badge badge-danger">Failed</span>
      case 'partial': return <span className="badge badge-warning">Partial</span>
      default:        return <span className="badge">{status}</span>
    }
  }

  const handleDownloadReport = (logId) => {
    const token = localStorage.getItem('access_token')
    
    // We fetch the report via JS so we can send the Bearer token
    fetch(`/api/logs/${logId}/report`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    .then(async (res) => {
      if (!res.ok) throw new Error('Report not found')
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `report_${logId}.html`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    })
    .catch((err) => {
      notify.error('Report file not found on disk.')
    })
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Bot Run Logs</h1>
          <p className="page-subtitle">Audit RPA automation execution history.</p>
        </div>
      </div>

      <Card>
        <div style={{ display: 'flex', gap: 'var(--space-4)', marginBottom: 'var(--space-5)' }}>
          <select 
            className="form-input" 
            style={{ maxWidth: '200px' }}
            value={filters.bot_name} 
            onChange={(e) => setFilters({...filters, bot_name: e.target.value})}
          >
            <option value="">All Bots</option>
            <option value="admission_bot">Admission Bot</option>
            <option value="attendance_bot">Attendance Bot</option>
            <option value="results_bot">Results Bot</option>
          </select>

          <select 
            className="form-input" 
            style={{ maxWidth: '200px' }}
            value={filters.status} 
            onChange={(e) => setFilters({...filters, status: e.target.value})}
          >
            <option value="">All Statuses</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
            <option value="partial">Partial</option>
            <option value="running">Running</option>
          </select>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Bot Name</th>
                <th>Triggered By</th>
                <th>Status</th>
                <th>Records (Processed/Total)</th>
                <th>Duration (s)</th>
                <th>Started At</th>
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
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: 'var(--space-4)', color: 'var(--color-text-secondary)' }}>
                    No bot logs found.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id}>
                    <td>
                      <div className="avatar-group">
                        <div className="avatar" style={{ background: '#F0FDF4', color: 'var(--color-success)' }}>🤖</div>
                        <div>
                          <div style={{ fontWeight: '500' }}>{log.bot_name}</div>
                        </div>
                      </div>
                    </td>
                    <td>{log.triggered_by || 'System'}</td>
                    <td>{getStatusBadge(log.status)}</td>
                    <td>
                      {log.records_processed} / {log.records_total} 
                      {log.records_failed > 0 && <span style={{ color: 'var(--color-danger)', marginLeft: '8px' }}>({log.records_failed} failed)</span>}
                    </td>
                    <td>{log.duration_seconds ? log.duration_seconds.toFixed(2) : '-'}</td>
                    <td style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)' }}>
                      {log.started_at ? new Date(log.started_at).toLocaleString() : '-'}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <Button variant="secondary" size="sm" onClick={() => handleDownloadReport(log.id)}>View Report</Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {pagination.pages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-3)', marginTop: 'var(--space-5)' }}>
            <Button 
              variant="secondary" 
              size="sm" 
              disabled={pagination.page === 1}
              onClick={() => fetchLogs(pagination.page - 1)}
            >
              Previous
            </Button>
            <span style={{ fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', alignSelf: 'center' }}>
              Page {pagination.page} of {pagination.pages}
            </span>
            <Button 
              variant="secondary" 
              size="sm" 
              disabled={pagination.page === pagination.pages}
              onClick={() => fetchLogs(pagination.page + 1)}
            >
              Next
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}
