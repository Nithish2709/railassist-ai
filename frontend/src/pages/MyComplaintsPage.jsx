import React, { useState, useEffect } from 'react';
import { getAuthHeaders } from '../utils/auth';

export default function MyComplaintsPage({
  apiBaseUrl,
  onSelectComplaint,
  onLodgeNew,
  onBackToDashboard,
}) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    let isMounted = true;
    async function fetchComplaints() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${apiBaseUrl}/complaints/my`, {
          headers: getAuthHeaders(),
        });
        if (!res.ok) {
          throw new Error('Failed to retrieve your complaints from the server.');
        }
        const data = await res.json();
        if (isMounted) setComplaints(data);
      } catch (err) {
        if (isMounted) setError(err.message || 'Error fetching complaints.');
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    fetchComplaints();
    return () => { isMounted = false; };
  }, [apiBaseUrl]);

  const filteredComplaints = complaints.filter((c) => {
    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
    const term = searchTerm.toLowerCase().trim();
    const matchesSearch =
      !term ||
      c.reference_number.toLowerCase().includes(term) ||
      c.title.toLowerCase().includes(term) ||
      c.predicted_category.toLowerCase().includes(term) ||
      c.department_name.toLowerCase().includes(term);
    return matchesStatus && matchesSearch;
  });

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
      {/* Breadcrumb Bar */}
      <div className="breadcrumb-nav">
        <button className="breadcrumb-link" onClick={onBackToDashboard}>
          Passenger Dashboard
        </button>
        <span className="breadcrumb-separator">/</span>
        <span className="breadcrumb-current">My Complaints</span>
      </div>

      <div className="page-header-flex">
        <div>
          <h1 className="page-title">My Registered Complaints</h1>
          <p className="page-subtitle">
            Complete record of your railway complaints persisted in MySQL with AI category classifications and assigned departments.
          </p>
        </div>
        <button className="btn-primary" onClick={onLodgeNew}>
          ➕ Lodge New Complaint
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="filter-search-toolbar">
        <div className="search-box-wrapper">
          <span className="search-box-icon">🔍</span>
          <input
            type="text"
            className="search-box-input"
            placeholder="Search by reference number, title, category, or department..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button className="search-clear-btn" onClick={() => setSearchTerm('')}>
              ✕
            </button>
          )}
        </div>

        <div className="status-filter-pills">
          {['ALL', 'SUBMITTED', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED'].map((st) => (
            <button
              key={st}
              className={`filter-pill-btn ${statusFilter === st ? 'active' : ''}`}
              onClick={() => setStatusFilter(st)}
            >
              {st === 'ALL' ? 'All Complaints' : st}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="loading-state-card">
          <div className="spinner-dots"></div>
          <span>Loading complaints from MySQL database...</span>
        </div>
      ) : error ? (
        <div className="error-state-card">
          <span>⚠️ {error}</span>
        </div>
      ) : filteredComplaints.length > 0 ? (
        <div className="table-card-container">
          <div className="data-table-wrapper">
            <table className="portal-table">
              <thead>
                <tr>
                  <th>Ref Number</th>
                  <th>Complaint Title</th>
                  <th>AI Category</th>
                  <th>Assigned Department</th>
                  <th>Status</th>
                  <th>Lodged Date</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredComplaints.map((item) => (
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
                        View Timeline
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="table-footer-meta">
            Showing {filteredComplaints.length} of {complaints.length} total complaints
          </div>
        </div>
      ) : (
        <div className="empty-state-box">
          <div className="empty-icon">🔍</div>
          <h3>No Matching Complaints Found</h3>
          <p>
            {searchTerm || statusFilter !== 'ALL'
              ? 'No complaints matched your current search and filter criteria. Try adjusting or clearing filters.'
              : 'You have not registered any complaints yet.'}
          </p>
          {(searchTerm || statusFilter !== 'ALL') && (
            <button
              className="btn-secondary"
              onClick={() => {
                setSearchTerm('');
                setStatusFilter('ALL');
              }}
            >
              Reset Filters
            </button>
          )}
        </div>
      )}
    </div>
  );
}
