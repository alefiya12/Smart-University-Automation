import React, { useState, useEffect } from 'react'
import { studentApi } from '../../services/api'
import Card from '../../components/common/Card'
import { notify } from '../../components/common/Toast'

export default function StudentFees() {
  const [fees, setFees] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    studentApi.getFees()
      .then(res => setFees(res.data.data || []))
      .catch(() => notify.error('Failed to load fee ledger.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading fee details...</div>

  const totalOutstanding = fees
    .filter(f => f.status.toLowerCase() !== 'paid')
    .reduce((acc, f) => acc + f.amount, 0)

  const totalPaid = fees
    .filter(f => f.status.toLowerCase() === 'paid')
    .reduce((acc, f) => acc + f.amount, 0)

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">University Fee Ledger & Invoices</h1>
          <p className="page-subtitle">Track semester tuition fees, hostel, exam charges, and payment confirmations.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--space-5)', marginBottom: 'var(--space-6)' }}>
        <div className="stat-card">
          <div className="stat-icon-box" style={{ background: totalOutstanding > 0 ? '#FEE2E2' : '#F0FDF4', color: totalOutstanding > 0 ? 'var(--color-danger)' : 'var(--color-success)' }}>
            💰
          </div>
          <div>
            <div className="stat-value">₹{totalOutstanding.toLocaleString()}</div>
            <div className="stat-label">Total Outstanding Dues</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon-box" style={{ background: '#F0FDF4', color: 'var(--color-success)' }}>
            ✓
          </div>
          <div>
            <div className="stat-value">₹{totalPaid.toLocaleString()}</div>
            <div className="stat-label">Total Paid & Cleared</div>
          </div>
        </div>
      </div>

      <Card title="Fee Invoices & Receipts" subtitle="Official university invoices and receipts">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Category</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Due Date</th>
                <th>Status</th>
                <th>Paid Date</th>
                <th>Receipt #</th>
              </tr>
            </thead>
            <tbody>
              {fees.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-secondary)' }}>
                    No fee invoices generated yet.
                  </td>
                </tr>
              ) : (
                fees.map(f => (
                  <tr key={f.id}>
                    <td>INV-{f.id.toString().padStart(4, '0')}</td>
                    <td style={{ textTransform: 'capitalize', fontWeight: 500 }}>{f.fee_type}</td>
                    <td>{f.description || '—'}</td>
                    <td style={{ fontWeight: 600 }}>₹{f.amount.toLocaleString()}</td>
                    <td>{f.due_date || '—'}</td>
                    <td>
                      <span className={`badge ${f.status.toLowerCase() === 'paid' ? 'badge-success' : 'badge-warning'}`}>
                        {f.status.toUpperCase()}
                      </span>
                    </td>
                    <td>{f.paid_date || '—'}</td>
                    <td>{f.receipt_no ? <code style={{ color: 'var(--color-primary)' }}>{f.receipt_no}</code> : '—'}</td>
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
