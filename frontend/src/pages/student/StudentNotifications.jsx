import React, { useState, useEffect } from 'react'
import { notificationApi } from '../../services/api'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import { notify } from '../../components/common/Toast'

export default function StudentNotifications() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchNotifications = () => {
    setLoading(true)
    notificationApi.getMyNotifications()
      .then(res => setNotifications(res.data.data || []))
      .catch(() => notify.error('Failed to load notifications.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchNotifications()
  }, [])

  const handleMarkRead = async (id) => {
    try {
      await notificationApi.markAsRead(id)
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
      notify.success('Notification marked as read.')
    } catch {
      notify.error('Failed to mark notification.')
    }
  }

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading notification feed...</div>

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'attendance_warning': return '⚠️'
      case 'result_published':   return '📊'
      case 'admission':          return '🎓'
      case 'fee_reminder':       return '💰'
      default:                   return '🔔'
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Notification Center</h1>
          <p className="page-subtitle">Real-time alerts, academic warnings, and examination updates.</p>
        </div>
      </div>

      <Card title="Incoming Announcements & Alerts">
        {notifications.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-secondary)' }}>
            <span style={{ fontSize: '36px', display: 'block', marginBottom: '8px' }}>🎉</span>
            You have no notifications at this time. All caught up!
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {notifications.map(n => (
              <div 
                key={n.id}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  padding: '16px 20px',
                  borderRadius: '10px',
                  border: '1px solid var(--color-border)',
                  background: n.is_read ? 'var(--color-bg-card, #FFFFFF)' : 'var(--color-primary-light, #EFF6FF)',
                  transition: 'background 0.2s'
                }}
              >
                <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                  <div style={{
                    fontSize: '22px',
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: '#FFFFFF',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.08)'
                  }}>
                    {getCategoryIcon(n.category)}
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <span style={{ fontWeight: 600, fontSize: 'var(--text-base)', color: 'var(--color-text-primary)' }}>
                        {n.title}
                      </span>
                      {!n.is_read && <span className="badge badge-primary" style={{ fontSize: '10px' }}>New</span>}
                    </div>
                    <p style={{ margin: '0 0 6px 0', fontSize: 'var(--text-sm)', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                      {n.message}
                    </p>
                    <span style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>
                      {n.created_at ? new Date(n.created_at).toLocaleString() : ''}
                    </span>
                  </div>
                </div>

                {!n.is_read && (
                  <Button variant="outline" size="sm" onClick={() => handleMarkRead(n.id)}>
                    Mark Read
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
