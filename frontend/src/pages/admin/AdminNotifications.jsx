import React, { useState, useEffect } from 'react'
import { notificationApi } from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify } from '../../components/common/Toast'

export default function AdminNotifications() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [categoryFilter, setCategoryFilter] = useState('')
  const [page, setPage] = useState(1)
  const [pagination, setPagination] = useState({ page: 1, total: 0, pages: 1 })

  const fetchNotifications = async (p = 1) => {
    setLoading(true)
    try {
      const params = { page: p, page_size: 25 }
      if (categoryFilter) params.category = categoryFilter
      const res = await notificationApi.getAllNotifications(params)
      setNotifications(res.data.data || [])
      setPagination(res.data.pagination || { page: 1, total: 0, pages: 1 })
    } catch {
      notify.error('Failed to load notification audit trail.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchNotifications(page)
  }, [categoryFilter, page])

  const getCategoryBadge = (category) => {
    switch (category) {
      case 'attendance_warning':
        return <span className="badge badge-warning">Attendance Warning</span>
      case 'result_published':
        return <span className="badge badge-primary">Result Published</span>
      case 'admission':
        return <span className="badge badge-success">Admission Confirmed</span>
      case 'fee_reminder':
        return <span className="badge badge-danger">Fee Reminder</span>
      default:
        return <span className="badge">{category}</span>
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Notification Audit & Dispatch Log</h1>
          <p className="page-subtitle">Real-time delivery log of in-app announcements, attendance warnings, and results.</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <select
            className="form-input"
            style={{ width: '200px' }}
            value={categoryFilter}
            onChange={(e) => {
              setCategoryFilter(e.target.value)
              setPage(1)
            }}
          >
            <option value="">All Categories</option>
            <option value="attendance_warning">Attendance Warnings</option>
            <option value="result_published">Results Published</option>
            <option value="admission">Admissions</option>
            <option value="fee_reminder">Fee Reminders</option>
          </select>
          <Button variant="outline" onClick={() => fetchNotifications(page)}>
            🔄 Refresh
          </Button>
        </div>
      </div>

      <Card title="System Dispatches" subtitle={`Total logged notifications: ${pagination.total}`}>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Recipient</th>
                <th>Category</th>
                <th>Channel</th>
                <th>Title & Message</th>
                <th>Status</th>
                <th>Dispatched At</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="7" style={{ textAlign: 'center', padding: '2rem' }}>Loading notifications...</td></tr>
              ) : notifications.length === 0 ? (
                <tr><td colSpan="7" style={{ textAlign: 'center', padding: '2rem' }}>No notifications found matching filter.</td></tr>
              ) : (
                notifications.map(n => (
                  <tr key={n.id}>
                    <td>#{n.id}</td>
                    <td style={{ fontWeight: 600 }}>{n.student_name}</td>
                    <td>{getCategoryBadge(n.category)}</td>
                    <td>
                      <span style={{ textTransform: 'uppercase', fontSize: '11px', fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                        {n.notification_type}
                      </span>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)', color: 'var(--color-text-primary)' }}>
                        {n.title}
                      </div>
                      <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', maxWidth: '420px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {n.message}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${n.status === 'sent' || n.status === 'read' ? 'badge-success' : (n.status === 'failed' ? 'badge-danger' : 'badge-warning')}`}>
                        {n.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ fontSize: '12px', whiteSpace: 'nowrap' }}>
                      {n.created_at ? new Date(n.created_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {pagination.pages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: 'var(--space-4)' }}>
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage(p => Math.max(p - 1, 1))}
            >
              Previous
            </Button>
            <span style={{ alignSelf: 'center', fontSize: 'var(--text-sm)' }}>
              Page {page} of {pagination.pages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= pagination.pages}
              onClick={() => setPage(p => Math.min(p + 1, pagination.pages))}
            >
              Next
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}
