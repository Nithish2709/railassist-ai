import React, { useState, useEffect } from 'react';
import { getAuthHeaders } from '../utils/auth';

export default function DepartmentDashboard({
  apiBaseUrl,
  user,
  onSelectComplaint,
}) {
  const [stats, setStats] = useState(null);
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Status Update Modal State
  const [selectedComplaintForUpdate, setSelectedComplaintForUpdate] = useState(null);
  const [newStatus, setNewStatus] = useState('IN_PROGRESS');
  const [remarks, setRemarks] = useState('');
  const [updating, setUpdating] = useState(false);
  const [updateError, setUpdateError] = useState(null);
  const [updateSuccessMsg, setUpdateSuccessMsg] = useState(null);

  const fetchDepartmentData = async () => {
    setLoading(true);
    setError(null);
    try {
      const dashRes = await fetch(`${apiBaseUrl}/department/dashboard`, {
        headers: getAuthHeaders(),
      });
      if (!dashRes.ok) throw new Error('Failed to load department authority metrics.');
      const dashData = await dashRes.json();
      setStats(dashData);

      const queryParams = new URLSearchParams();
      if (statusFilter) queryParams.append('status', statusFilter);
      if (searchTerm) queryParams.append('search', searchTerm);

      const listRes = await fetch(`${apiBaseUrl}/department/complaints?${queryParams.toString()}`, {
        headers: getAuthHeaders(),
      });
      if (!listRes.ok) throw new Error('Failed to load assigned department complaints.');
      const listData = await listRes.json();
      setComplaints(listData);
    } catch (err) {
      setError(err.message || 'Error communicating with backend server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDepartmentData();
  }, [apiBaseUrl, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchDepartmentData();
  };

  const handleOpenStatusModal = (complaint) => {
    setSelectedComplaintForUpdate(complaint);
    setNewStatus(complaint.status === 'SUBMITTED' ? 'ASSIGNED' : complaint.status === 'ASSIGNED' ? 'IN_PROGRESS' : 'RESOLVED');
    setRemarks('');
    setUpdateError(null);
  };

  const handleCloseStatusModal = () => {
    setSelectedComplaintForUpdate(null);
    setRemarks('');
    setUpdateError(null);
  };

  const handleStatusUpdateSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComplaintForUpdate) return;

    if (!remarks.trim() || remarks.trim().length < 5) {
      setUpdateError('Mandatory remarks must be at least 5 characters explaining this status update.');
      return;
    }

    if (newStatus === 'RESOLVED' && remarks.trim().length < 10) {
      setUpdateError('Resolution remarks must provide sufficient explanation (at least 10 characters).');
      return;
    }

    setUpdating(true);
    setUpdateError(null);

    try {
      const res = await fetch(
        `${apiBaseUrl}/department/complaints/${selectedComplaintForUpdate.reference_number}/status`,
        {
          method: 'PATCH',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            new_status: newStatus,
            remarks: remarks.trim(),
          }),
        }
      );

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to update complaint status.');
      }

      setUpdateSuccessMsg(
        `Complaint ${selectedComplaintForUpdate.reference_number} updated to ${newStatus} with remarks recorded.`
      );
      handleCloseStatusModal();
      fetchDepartmentData();

      setTimeout(() => setUpdateSuccessMsg(null), 6000);
    } catch (err) {
      setUpdateError(err.message || 'Error updating complaint status.');
    } finally {
      setUpdating(false);
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
    <div className="dashboard-container">
      {/* Department Header */}
      <div className="dept-header-panel">
        <div className="dept-badge-cluster">
          <span className="gov-seal-pill">🏢 Departmental Grievance Action Cell</span>
          <span className="dept-name-tag">{stats?.department_name || user?.department_name || 'Designated Department'}</span>
        </div>
        <h1 className="admin-title">Department Authority Workstation</h1>
        <p className="admin-meta-text">
          Authorized Officer: <strong>{user?.full_name}</strong> ({user?.email}) | Department Scoped: <strong>{stats?.department_name || user?.department_name}</strong>
        </p>
      </div>

      {updateSuccessMsg && (
        <div className="alert-success-banner">
          <span className="success-icon">✓</span>
          <span>{updateSuccessMsg}</span>
        </div>
      )}

      {loading && !stats ? (
        <div className="loading-state-card">
          <div className="spinner-dots"></div>
          <span>Loading assigned department grievances...</span>
        </div>
      ) : error ? (
        <div className="error-state-card">
          <span>⚠️ {error}</span>
        </div>
      ) : stats ? (
        <>
          {/* Department Metrics */}
          <div className="metrics-grid-five">
            <div className="metric-card card-navy">
              <div className="metric-label">Total Assigned</div>
              <div className="metric-value">{stats.total_assigned}</div>
              <div className="metric-sub">Complaints for this department</div>
            </div>

            <div className="metric-card card-blue">
              <div className="metric-label">Newly Assigned</div>
              <div className="metric-value">{stats.newly_assigned}</div>
              <div className="metric-sub">Pending initial action</div>
            </div>

            <div className="metric-card card-amber">
              <div className="metric-label">In-Progress Action</div>
              <div className="metric-value">{stats.in_progress}</div>
              <div className="metric-sub">Under active remediation</div>
            </div>

            <div className="metric-card card-green">
              <div className="metric-label">Resolved Cases</div>
              <div className="metric-value">{stats.resolved}</div>
              <div className="metric-sub">Remedied with remarks</div>
            </div>

            <div className="metric-card card-slate">
              <div className="metric-label">Closed Cases</div>
              <div className="metric-value">{stats.closed}</div>
              <div className="metric-sub">Concluded cases</div>
            </div>
          </div>

          {/* Department Complaints Table */}
          <div className="table-card-container" style={{ marginTop: '1.5rem' }}>
            <div className="table-card-header">
              <div>
                <h2 className="section-heading">Assigned Grievances Queue</h2>
                <p className="section-subtext">
                  Complaints routed automatically to this department by the TF-IDF + Random Forest classification pipeline.
                </p>
              </div>
            </div>

            {/* Filter and Search Bar */}
            <div className="filter-search-toolbar">
              <form onSubmit={handleSearchSubmit} className="search-box-wrapper">
                <span className="search-box-icon">🔍</span>
                <input
                  type="text"
                  className="search-box-input"
                  placeholder="Search in assigned complaints..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <button type="submit" className="btn-search-go">Search</button>
              </form>

              <div className="status-filter-pills">
                {['', 'SUBMITTED', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED'].map((st) => (
                  <button
                    key={st}
                    className={`filter-pill-btn ${statusFilter === st ? 'active' : ''}`}
                    onClick={() => setStatusFilter(st)}
                  >
                    {st === '' ? 'All Assigned' : st}
                  </button>
                ))}
              </div>
            </div>

            {complaints.length > 0 ? (
              <div className="data-table-wrapper">
                <table className="portal-table">
                  <thead>
                    <tr>
                      <th>Ref Number</th>
                      <th>Complainant</th>
                      <th>Title</th>
                      <th>AI Category</th>
                      <th>Current Status</th>
                      <th>Submission Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {complaints.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <span className="mono-ref-number">{item.reference_number}</span>
                        </td>
                        <td>
                          <span className="table-passenger-name">{item.passenger_name}</span>
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
                          <span className={`status-pill ${getStatusBadgeClass(item.status)}`}>
                            {item.status}
                          </span>
                        </td>
                        <td>
                          <span className="date-cell-text">
                            {new Date(item.created_at).toLocaleDateString()}
                          </span>
                        </td>
                        <td className="actions-cell-flex">
                          <button
                            className="btn-update-status"
                            onClick={() => handleOpenStatusModal(item)}
                          >
                            Update Status
                          </button>
                          <button
                            className="btn-table-action"
                            onClick={() => onSelectComplaint(item.reference_number)}
                          >
                            Timeline
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state-box">
                <div className="empty-icon">✓</div>
                <h3>Queue Clear</h3>
                <p>No complaints currently match the selected status filter for your department.</p>
              </div>
            )}
          </div>
        </>
      ) : null}

      {/* Status Update Modal */}
      {selectedComplaintForUpdate && (
        <div className="modal-backdrop">
          <div className="modal-content-card">
            <div className="modal-header">
              <div>
                <span className="modal-subheading">Department Remedial Action</span>
                <h3 className="modal-title">
                  Update Complaint: <span className="mono-ref-number">{selectedComplaintForUpdate.reference_number}</span>
                </h3>
              </div>
              <button className="modal-close-btn" onClick={handleCloseStatusModal}>✕</button>
            </div>

            <p className="modal-complaint-title">
              <strong>Subject:</strong> {selectedComplaintForUpdate.title}
            </p>

            {updateError && (
              <div className="auth-error-banner" role="alert">
                <span className="error-icon">⚠️</span>
                <span>{updateError}</span>
              </div>
            )}

            <form onSubmit={handleStatusUpdateSubmit} className="modal-form">
              <div className="form-group">
                <label className="form-label">
                  New Status Transition <span className="required-asterisk">*</span>
                </label>
                <select
                  className="portal-select full-width-select"
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  disabled={updating}
                >
                  <option value="ASSIGNED">ASSIGNED — Acknowledged by department desk</option>
                  <option value="IN_PROGRESS">IN_PROGRESS — Field officer / staff dispatched</option>
                  <option value="RESOLVED">RESOLVED — Remedial action completed successfully</option>
                  <option value="CLOSED">CLOSED — Complaint concluded and archived</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">
                  Official Department Remarks & Audit Notes <span className="required-asterisk">*</span>
                </label>
                <textarea
                  className="form-textarea"
                  rows="4"
                  placeholder="Enter specific actions taken, staff dispatched, or resolution notes..."
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  disabled={updating}
                  required
                />
                <span className="field-hint">
                  Remarks will be permanently recorded in the MySQL audit history with your officer attribution.
                </span>
              </div>

              <div className="modal-actions-bar">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleCloseStatusModal}
                  disabled={updating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={updating || !remarks.trim()}
                >
                  {updating ? 'Saving Status in Database...' : 'Confirm Status Update'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
