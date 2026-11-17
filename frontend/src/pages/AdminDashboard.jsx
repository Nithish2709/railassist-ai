import React, { useState, useEffect } from 'react';
import { getAuthHeaders } from '../utils/auth';

export default function AdminDashboard({
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
  const [categoryFilter, setCategoryFilter] = useState('');
  const [deptFilter, setDeptFilter] = useState('');

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const dashRes = await fetch(`${apiBaseUrl}/admin/dashboard`, {
        headers: getAuthHeaders(),
      });
      if (!dashRes.ok) throw new Error('Failed to load administrative dashboard statistics.');
      const dashData = await dashRes.json();
      setStats(dashData);

      // Fetch all complaints with filters
      const queryParams = new URLSearchParams();
      if (statusFilter) queryParams.append('status', statusFilter);
      if (categoryFilter) queryParams.append('category', categoryFilter);
      if (deptFilter) queryParams.append('department_id', deptFilter);
      if (searchTerm) queryParams.append('search', searchTerm);

      const listRes = await fetch(`${apiBaseUrl}/admin/complaints?${queryParams.toString()}`, {
        headers: getAuthHeaders(),
      });
      if (!listRes.ok) throw new Error('Failed to load complaint list.');
      const listData = await listRes.json();
      setComplaints(listData);
    } catch (err) {
      setError(err.message || 'Error communicating with backend server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [apiBaseUrl, statusFilter, categoryFilter, deptFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchDashboardData();
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
      {/* Admin Executive Header */}
      <div className="admin-header-panel">
        <div className="admin-badge-cluster">
          <span className="gov-seal-pill">🛡️ Central Vigilance & Grievance Cell</span>
          <span className="gov-admin-tag">Central Railway Administrator</span>
        </div>
        <h1 className="admin-title">National Railway Grievance Monitoring Dashboard</h1>
        <p className="admin-meta-text">
          Logged in as: <strong>{user?.full_name}</strong> ({user?.email}) | Department Routing: <strong>Automated AI via TF-IDF + Random Forest (200 Trees)</strong>
        </p>
      </div>

      {loading && !stats ? (
        <div className="loading-state-card">
          <div className="spinner-dots"></div>
          <span>Querying MySQL database across all operational railway departments...</span>
        </div>
      ) : error ? (
        <div className="error-state-card">
          <span>⚠️ {error}</span>
        </div>
      ) : stats ? (
        <>
          {/* Executive Metrics Overview */}
          <div className="metrics-grid-six">
            <div className="metric-card card-navy">
              <div className="metric-label">Total Network Complaints</div>
              <div className="metric-value">{stats.total_complaints}</div>
              <div className="metric-sub">Logged in MySQL database</div>
            </div>

            <div className="metric-card card-blue">
              <div className="metric-label">Submitted / New</div>
              <div className="metric-value">{stats.submitted_count}</div>
              <div className="metric-sub">Initial passenger lodging</div>
            </div>

            <div className="metric-card card-indigo">
              <div className="metric-label">Actively Assigned</div>
              <div className="metric-value">{stats.assigned_count}</div>
              <div className="metric-sub">Routed to department</div>
            </div>

            <div className="metric-card card-amber">
              <div className="metric-label">In-Progress Action</div>
              <div className="metric-value">{stats.in_progress_count}</div>
              <div className="metric-sub">Investigation active</div>
            </div>

            <div className="metric-card card-green">
              <div className="metric-label">Resolved Complaints</div>
              <div className="metric-value">{stats.resolved_count}</div>
              <div className="metric-sub">Remedial action taken</div>
            </div>

            <div className="metric-card card-slate">
              <div className="metric-label">Formally Closed</div>
              <div className="metric-value">{stats.closed_count}</div>
              <div className="metric-sub">Case closed in database</div>
            </div>
          </div>

          {/* Department Breakdown Bar Grid */}
          <div className="breakdown-cards-grid">
            <div className="table-card-container">
              <div className="table-card-header">
                <div>
                  <h2 className="section-heading">Complaints by Indian Railways Department</h2>
                  <p className="section-subtext">Real-time breakdown aggregated from database records.</p>
                </div>
              </div>
              <div className="breakdown-list-padded">
                {stats.by_department && Object.entries(stats.by_department).map(([dept, count]) => (
                  <div key={dept} className="breakdown-row">
                    <span className="dept-name-bold">{dept}</span>
                    <span className="dept-count-badge">{count} complaints</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="table-card-container">
              <div className="table-card-header">
                <div>
                  <h2 className="section-heading">Complaints by AI Predicted Category</h2>
                  <p className="section-subtext">Classified automatically using TF-IDF + Random Forest.</p>
                </div>
              </div>
              <div className="breakdown-list-padded">
                {stats.by_category && Object.entries(stats.by_category).map(([cat, count]) => (
                  <div key={cat} className="breakdown-row">
                    <span className="dept-name-bold">{cat}</span>
                    <span className="dept-count-badge cat-badge">{count} complaints</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Comprehensive All Complaints Monitoring Table */}
          <div className="table-card-container" style={{ marginTop: '1.5rem' }}>
            <div className="table-card-header">
              <div>
                <h2 className="section-heading">Master Railway Complaints Register</h2>
                <p className="section-subtext">
                  Central monitoring feed across all 8 operational railway departments with live status inspection.
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
                  placeholder="Search by Reference Number, Passenger, Train, or PNR..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                <button type="submit" className="btn-search-go">Search</button>
              </form>

              <div className="dropdown-filter-group">
                <select
                  className="portal-select"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="SUBMITTED">Submitted</option>
                  <option value="ASSIGNED">Assigned</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="RESOLVED">Resolved</option>
                  <option value="CLOSED">Closed</option>
                </select>

                <select
                  className="portal-select"
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <option value="">All Categories (8 Active)</option>
                  <option value="Catering">Catering</option>
                  <option value="Coach Maintenance">Coach Maintenance</option>
                  <option value="Electrical">Electrical</option>
                  <option value="Housekeeping">Housekeeping</option>
                  <option value="Operations & Traffic">Operations & Traffic</option>
                  <option value="Passenger Grievance">Passenger Grievance</option>
                  <option value="Security">Security</option>
                  <option value="Water & Sanitation">Water & Sanitation</option>
                </select>

                {(searchTerm || statusFilter || categoryFilter || deptFilter) && (
                  <button
                    className="btn-clear-filters"
                    onClick={() => {
                      setSearchTerm('');
                      setStatusFilter('');
                      setCategoryFilter('');
                      setDeptFilter('');
                    }}
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            </div>

            {complaints.length > 0 ? (
              <div className="data-table-wrapper">
                <table className="portal-table">
                  <thead>
                    <tr>
                      <th>Ref Number</th>
                      <th>Complainant</th>
                      <th>Complaint Title</th>
                      <th>AI Category</th>
                      <th>Assigned Department</th>
                      <th>Status</th>
                      <th>Date</th>
                      <th>Action</th>
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
                            Audit Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state-box">
                <div className="empty-icon">🔍</div>
                <h3>No Matching Complaints Found</h3>
                <p>No complaints matched your search or filter selection.</p>
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}
