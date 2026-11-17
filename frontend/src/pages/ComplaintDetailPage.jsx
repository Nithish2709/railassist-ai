import React, { useState, useEffect } from 'react';
import { getAuthHeaders } from '../utils/auth';

export default function ComplaintDetailPage({
  apiBaseUrl,
  referenceNumber,
  user,
  onBack,
}) {
  const [complaint, setComplaint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function fetchDetail() {
      if (!referenceNumber) return;
      setLoading(true);
      setError(null);

      try {
        // Choose appropriate endpoint based on user role
        let endpoint = `${apiBaseUrl}/complaints/track/${referenceNumber}`;
        if (user?.role === 'RAILWAY_ADMIN') {
          endpoint = `${apiBaseUrl}/admin/complaints/${referenceNumber}`;
        } else if (user?.role === 'DEPARTMENT_AUTHORITY') {
          endpoint = `${apiBaseUrl}/department/complaints/${referenceNumber}`;
        }

        const res = await fetch(endpoint, {
          headers: getAuthHeaders(),
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || 'Failed to retrieve complaint detail.');
        }

        if (isMounted) setComplaint(data);
      } catch (err) {
        if (isMounted) setError(err.message || 'Error fetching complaint information.');
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    fetchDetail();
    return () => { isMounted = false; };
  }, [apiBaseUrl, referenceNumber, user]);

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'RESOLVED':
      case 'CLOSED':
        return 'badge-status-resolved';
      case 'IN_PROGRESS':
        return 'badge-status-in-progress';
      case 'ASSIGNED':
        return 'badge-status-assigned';
      default:
        return 'badge-status-submitted';
    }
  };

  return (
    <div className="portal-content-container">
      {/* Breadcrumb Header */}
      <div className="breadcrumb-nav">
        <button className="breadcrumb-link" onClick={onBack}>
          {user?.role === 'RAILWAY_ADMIN'
            ? 'Admin Dashboard'
            : user?.role === 'DEPARTMENT_AUTHORITY'
            ? 'Department Dashboard'
            : 'Passenger Dashboard'}
        </button>
        <span className="breadcrumb-separator">/</span>
        <span className="breadcrumb-current">Complaint: {referenceNumber}</span>
      </div>

      {loading ? (
        <div className="loading-state-card">
          <div className="spinner-dots"></div>
          <span>Loading grievance record and audit trail...</span>
        </div>
      ) : error ? (
        <div className="error-state-card">
          <span>⚠️ {error}</span>
          <button className="btn-secondary" style={{ marginTop: '1rem' }} onClick={onBack}>
            Return to Dashboard
          </button>
        </div>
      ) : complaint ? (
        <div className="complaint-detail-layout">
          {/* Main Complaint Overview Panel */}
          <div className="detail-left-column">
            <div className="detail-card">
              <div className="detail-header-flex">
                <div>
                  <span className="ref-number-badge mono-ref-number">{complaint.reference_number}</span>
                  <h1 className="complaint-title-large">{complaint.title}</h1>
                </div>
                <div>
                  <span className={`status-pill status-pill-large ${getStatusBadgeClass(complaint.status)}`}>
                    {complaint.status}
                  </span>
                </div>
              </div>

              {/* AI Classification Highlight Card */}
              <div className="ai-routing-highlight-card">
                <div className="ai-chip-header">
                  <span className="chip-ai-tag">🤖 AI Categorization Engine</span>
                  <span className="chip-model-sub">TF-IDF + Random Forest (200 Trees)</span>
                </div>
                <div className="ai-result-duo">
                  <div>
                    <span className="meta-dim-label">Predicted Category</span>
                    <strong className="ai-category-text">{complaint.predicted_category}</strong>
                  </div>
                  <div>
                    <span className="meta-dim-label">Assigned Department</span>
                    <strong className="ai-dept-text">{complaint.department_name}</strong>
                  </div>
                </div>
              </div>

              {/* Full Description */}
              <div className="detail-body-section">
                <h3 className="section-label">Detailed Complaint Statement</h3>
                <div className="description-quote-box">
                  <p>{complaint.description}</p>
                </div>
              </div>

              {/* Journey Metadata */}
              <div className="detail-body-section">
                <h3 className="section-label">Journey & Location Metadata</h3>
                <div className="journey-meta-grid">
                  <div className="meta-item">
                    <span className="meta-key">Train Number / Name:</span>
                    <span className="meta-val">{complaint.train_number || 'Not Specified'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-key">PNR Number:</span>
                    <span className="meta-val">{complaint.pnr_number || 'Not Specified'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-key">Journey Date:</span>
                    <span className="meta-val">{complaint.journey_date || 'Not Specified'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-key">Station / Location:</span>
                    <span className="meta-val">{complaint.location || 'Not Specified'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-key">Coach & Berth:</span>
                    <span className="meta-val">{complaint.coach_number || 'Not Specified'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-key">Lodged On:</span>
                    <span className="meta-val">{new Date(complaint.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Passenger Attribution */}
              <div className="detail-body-section">
                <h3 className="section-label">Complainant Contact Details</h3>
                <div className="journey-meta-grid">
                  <div className="meta-item">
                    <span className="meta-key">Passenger Name:</span>
                    <span className="meta-val">{complaint.passenger_name}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-key">Email Address:</span>
                    <span className="meta-val">{complaint.passenger_email}</span>
                  </div>
                  {complaint.passenger_phone && (
                    <div className="meta-item">
                      <span className="meta-key">Phone:</span>
                      <span className="meta-val">{complaint.passenger_phone}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Status Timeline & Audit Trail */}
          <div className="detail-right-column">
            <div className="timeline-card">
              <h2 className="timeline-title">Official Action & Status Timeline</h2>
              <p className="timeline-sub">
                Immutable audit trail logged in MySQL recording all administrative and departmental updates.
              </p>

              {complaint.history && complaint.history.length > 0 ? (
                <div className="timeline-trail">
                  {complaint.history.map((h, idx) => (
                    <div key={h.id || idx} className="timeline-node">
                      <div className="timeline-marker">
                        <span className="timeline-dot"></span>
                        {idx < complaint.history.length - 1 && <span className="timeline-line"></span>}
                      </div>
                      <div className="timeline-content">
                        <div className="timeline-status-header">
                          <span className={`status-pill ${getStatusBadgeClass(h.new_status)}`}>
                            {h.new_status}
                          </span>
                          <span className="timeline-timestamp">
                            {new Date(h.created_at).toLocaleString()}
                          </span>
                        </div>
                        <div className="timeline-remarks-box">
                          <p>{h.remarks}</p>
                        </div>
                        <div className="timeline-author-tag">
                          <span>Updated by: <strong>{h.updated_by_name}</strong></span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state-box">
                  <p>No history updates recorded yet.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
