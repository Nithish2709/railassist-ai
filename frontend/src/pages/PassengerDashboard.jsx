import React, { useState, useEffect } from 'react';
import { getAuthHeaders } from '../utils/auth';

export default function PassengerDashboard({
  apiBaseUrl,
  user,
  onLodgeComplaint,
  onViewMyComplaints,
  onSelectComplaint,
}) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trackRefInput, setTrackRefInput] = useState('');
  const [trackError, setTrackError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function fetchDashboard() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${apiBaseUrl}/dashboard/passenger`, {
          headers: getAuthHeaders(),
        });
        if (!res.ok) {
          throw new Error('Failed to retrieve passenger dashboard data.');
        }
        const data = await res.json();
        if (isMounted) setStats(data);
      } catch (err) {
        if (isMounted) setError(err.message || 'Error loading dashboard metrics.');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    fetchDashboard();
    return () => { isMounted = false; };
  }, [apiBaseUrl]);

  const handleQuickTrack = (e) => {
    e.preventDefault();
    const trimmed = trackRefInput.trim();
    if (!trimmed) {
      setTrackError('Please enter a valid complaint reference number (e.g. RAIL-2026-10001).');
      return;
    }
    setTrackError(null);
    onSelectComplaint(trimmed.toUpperCase());
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
    <div className="dashboard-container">
      {/* Header Banner */}
      <div className="dashboard-header-panel">
        <div className="dashboard-header-text">
          <span className="user-salutation">Indian Railways Passenger Portal</span>
          <h1 className="dashboard-title">Welcome, {user?.full_name || 'Passenger'}</h1>
          <p className="dashboard-meta-text">
            Official account: <strong>{user?.email}</strong> | Role: <span className="pill-role-user">Verified Passenger</span>
          </p>
        </div>
        <div className="dashboard-header-actions">
          <button
            id="dash-lodge-complaint-btn"
            className="btn-primary btn-action-pulse"
            onClick={onLodgeComplaint}
          >
            <span className="btn-icon">➕</span> Lodge New Complaint
          </button>
        </div>
      </div>

      {/* Quick Track Input Bar */}
      <div className="quick-track-strip">
        <form onSubmit={handleQuickTrack} className="quick-track-form">
          <div className="quick-track-icon">🔍</div>
          <input
            type="text"
            className="quick-track-input"
            placeholder="Track complaint by Reference Number (e.g. RAIL-2026-10001)..."
            value={trackRefInput}
            onChange={(e) => setTrackRefInput(e.target.value)}
          />
          <button type="submit" className="btn-track-submit">
            Track Status
          </button>
        </form>
        {trackError && <p className="track-input-error">{trackError}</p>}
      </div>

      {loading ? (
        <div className="loading-state-card">
          <div className="spinner-dots"></div>
          <span>Retrieving passenger records from MySQL database...</span>
        </div>
      ) : error ? (
        <div className="error-state-card">
          <span>⚠️ {error}</span>
        </div>
      ) : stats ? (
        <>
          {/* Key Stat Cards */}
          <div className="metrics-grid-four">
            <div className="metric-card card-navy">
              <div className="metric-label">Total Lodged Complaints</div>
              <div className="metric-value">{stats.total_complaints}</div>
              <div className="metric-sub">Active MySQL database records</div>
            </div>

            <div className="metric-card card-blue">
              <div className="metric-label">Submitted / Under Review</div>
              <div className="metric-value">{stats.submitted_count}</div>
              <div className="metric-sub">Awaiting department inspection</div>
            </div>

            <div className="metric-card card-amber">
              <div className="metric-label">In-Progress Investigation</div>
              <div className="metric-value">{stats.in_progress_count}</div>
              <div className="metric-sub">Assigned officer deployed</div>
            </div>

            <div className="metric-card card-green">
              <div className="metric-label">Successfully Resolved</div>
              <div className="metric-value">{stats.resolved_count}</div>
              <div className="metric-sub">Action taken with remarks</div>
            </div>
          </div>

          {/* Recent Complaints Section */}
          <div className="table-card-container">
            <div className="table-card-header">
              <div>
                <h2 className="section-heading">Recent Complaints Activity</h2>
                <p className="section-subtext">Latest passenger complaints logged through RailAssist AI.</p>
              </div>
              <button
                className="btn-secondary"
                onClick={onViewMyComplaints}
              >
                View All My Complaints ({stats.total_complaints})
              </button>
            </div>

            {stats.recent_complaints && stats.recent_complaints.length > 0 ? (
              <div className="data-table-wrapper">
                <table className="portal-table">
                  <thead>
                    <tr>
                      <th>Ref Number</th>
                      <th>Complaint Title</th>
                      <th>AI Predicted Category</th>
                      <th>Assigned Department</th>
                      <th>Status</th>
                      <th>Submission Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.recent_complaints.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <span className="mono-ref-number">{item.reference_number}</span>
                        </td>
                        <td>
                          <span className="table-complaint-title" title={item.title}>
                            {item.title}
                          </span>
                        </td>
                        <td>
                          <span className="category-pill-tag">{item.predicted_category}</span>
                        </td>
                        <td>
                          <span className="dept-cell-text" title={item.department_name}>
                            {item.department_name}
                          </span>
                        </td>
                        <td>
                          <span className={`status-pill ${getStatusBadgeClass(item.status)}`}>
                            {item.status}
                          </span>
                        </td>
                        <td>
                          <span className="date-cell-text">
                            {new Date(item.created_at).toLocaleDateString()}
                          </span>
                        </td>
                        <td>
                          <button
                            className="btn-table-action"
                            onClick={() => onSelectComplaint(item.reference_number)}
                          >
                            View Audit Trail
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state-box">
                <div className="empty-icon">📂</div>
                <h3>No Complaints Registered Yet</h3>
                <p>You have not lodged any railway complaints yet. Click the button below to register a complaint with automated AI department routing.</p>
                <button className="btn-primary" onClick={onLodgeComplaint}>
                  Lodge Your First Complaint
                </button>
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}
