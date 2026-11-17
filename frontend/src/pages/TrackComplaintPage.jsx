import React, { useState } from 'react';
import { getAuthHeaders } from '../utils/auth';

export default function TrackComplaintPage({
  apiBaseUrl,
  onSelectComplaint,
  onSwitchToLogin,
}) {
  const [refInput, setRefInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleTrackSubmit = async (e) => {
    e.preventDefault();
    const trimmed = refInput.trim().toUpperCase();
    if (!trimmed) {
      setError('Please enter a valid complaint reference number (e.g. RAIL-2026-10001).');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${apiBaseUrl}/complaints/track/${trimmed}`, {
        headers: getAuthHeaders(),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Complaint reference number not found.');
      }
      setResult(data);
    } catch (err) {
      setError(err.message || 'Unable to retrieve complaint tracking details.');
    } finally {
      setLoading(false);
    }
  };

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
      <div className="track-hero-card">
        <div className="track-hero-header">
          <div className="track-icon-large">🔎</div>
          <h1 className="track-title">Track Railway Grievance Status</h1>
          <p className="track-subtitle">
            Enter your official complaint reference number to view real-time department routing, investigation milestones, and remediation remarks.
          </p>
        </div>

        <form onSubmit={handleTrackSubmit} className="track-input-form">
          <input
            type="text"
            className="track-large-input mono-ref-number"
            placeholder="e.g. RAIL-2026-10001"
            value={refInput}
            onChange={(e) => setRefInput(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="btn-primary btn-track-large"
            disabled={loading || !refInput.trim()}
          >
            {loading ? 'Querying Database...' : 'Track Grievance'}
          </button>
        </form>

        <div className="track-sample-chips">
          <span className="sample-label">Try Seeded Benchmark Records:</span>
          <button
            type="button"
            className="sample-ref-chip"
            onClick={() => setRefInput('RAIL-2026-10001')}
          >
            RAIL-2026-10001 (Electrical)
          </button>
          <button
            type="button"
            className="sample-ref-chip"
            onClick={() => setRefInput('RAIL-2026-10002')}
          >
            RAIL-2026-10002 (Housekeeping)
          </button>
          <button
            type="button"
            className="sample-ref-chip"
            onClick={() => setRefInput('RAIL-2026-10003')}
          >
            RAIL-2026-10003 (Catering)
          </button>
        </div>

        {error && (
          <div className="auth-error-banner" style={{ marginTop: '1.5rem' }} role="alert">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}
      </div>

      {result && (
        <div className="track-result-wrapper" style={{ marginTop: '2rem' }}>
          <div className="detail-card">
            <div className="detail-header-flex">
              <div>
                <span className="ref-number-badge mono-ref-number">{result.reference_number}</span>
                <h2 className="complaint-title-large">{result.title}</h2>
              </div>
              <span className={`status-pill status-pill-large ${getStatusBadgeClass(result.status)}`}>
                {result.status}
              </span>
            </div>

            <div className="ai-routing-highlight-card">
              <div className="ai-result-duo">
                <div>
                  <span className="meta-dim-label">AI Categorization</span>
                  <strong className="ai-category-text">{result.predicted_category}</strong>
                </div>
                <div>
                  <span className="meta-dim-label">Assigned Department</span>
                  <strong className="ai-dept-text">{result.department_name}</strong>
                </div>
              </div>
            </div>

            <div className="detail-body-section">
              <h3 className="section-label">Complaint Summary</h3>
              <p className="description-quote-box">{result.description}</p>
            </div>

            {/* Visual Timeline */}
            <div className="detail-body-section">
              <h3 className="section-label">Status Progression & Officer Remarks</h3>
              <div className="timeline-trail">
                {result.history && result.history.map((h, idx) => (
                  <div key={h.id || idx} className="timeline-node">
                    <div className="timeline-marker">
                      <span className="timeline-dot"></span>
                      {idx < result.history.length - 1 && <span className="timeline-line"></span>}
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
                        <span>Attribution: <strong>{h.updated_by_name}</strong></span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
