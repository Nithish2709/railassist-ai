import React, { useState } from 'react';
import { getAuthHeaders } from '../utils/auth';

export default function SubmitComplaintPage({
  apiBaseUrl,
  onComplaintCreated,
  onCancel,
}) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [trainNumber, setTrainNumber] = useState('');
  const [pnrNumber, setPnrNumber] = useState('');
  const [journeyDate, setJourneyDate] = useState('');
  const [location, setLocation] = useState('');
  const [coachNumber, setCoachNumber] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successResult, setSuccessResult] = useState(null);

  const charCount = description.trim().length;
  const isTooShort = charCount > 0 && charCount < 5;
  const isTooLong = charCount > 1500;
  const isValid = title.trim().length >= 5 && charCount >= 5 && !isTooLong;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isValid) return;

    setLoading(true);
    setError(null);

    const payload = {
      title: title.trim(),
      description: description.trim(),
      train_number: trainNumber.trim() || null,
      pnr_number: pnrNumber.trim() || null,
      journey_date: journeyDate || null,
      location: location.trim() || null,
      coach_number: coachNumber.trim() || null,
    };

    try {
      const response = await fetch(`${apiBaseUrl}/complaints`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to submit complaint.');
      }

      setSuccessResult(data);
    } catch (err) {
      setError(err.message || 'Unable to connect to the complaint lodging service.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setTitle('');
    setDescription('');
    setTrainNumber('');
    setPnrNumber('');
    setJourneyDate('');
    setLocation('');
    setCoachNumber('');
    setSuccessResult(null);
    setError(null);
  };

  if (successResult) {
    return (
      <div className="submit-success-card">
        <div className="success-header-badge">
          <span className="success-check-icon">✓</span>
          <h2>Complaint Successfully Lodged & Classified</h2>
        </div>

        <p className="success-lead-text">
          Your complaint has been processed by the <strong>RailAssist AI</strong> inference engine and persisted into the official database.
        </p>

        <div className="success-meta-grid">
          <div className="success-stat-box">
            <span className="box-label">Official Reference Number</span>
            <span className="box-val-ref mono-ref-number">{successResult.reference_number}</span>
            <span className="box-hint">Save this number to track grievance updates</span>
          </div>

          <div className="success-stat-box">
            <span className="box-label">AI Predicted Category</span>
            <span className="box-val-category">{successResult.predicted_category}</span>
            <span className="box-hint">TF-IDF + Random Forest Classifier</span>
          </div>

          <div className="success-stat-box full-span-box">
            <span className="box-label">Assigned Indian Railways Department</span>
            <span className="box-val-dept">{successResult.department_name}</span>
            <span className="box-hint">Deterministically routed per Railway operational guidelines</span>
          </div>
        </div>

        <div className="success-actions-row">
          <button
            className="btn-primary"
            onClick={() => onComplaintCreated(successResult.reference_number)}
          >
            View Live Status Audit Trail
          </button>
          <button
            className="btn-secondary"
            onClick={handleReset}
          >
            Lodge Another Complaint
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="submit-complaint-wrapper">
      <div className="form-card-container">
        <div className="form-card-header">
          <div className="header-icon-circle">📝</div>
          <div>
            <h1 className="form-heading">Lodge Railway Complaint</h1>
            <p className="form-subheading">
              Describe your issue in plain English. The integrated AI model automatically determines the correct railway department and registers your grievance into the MySQL persistent database.
            </p>
          </div>
        </div>

        {error && (
          <div className="auth-error-banner" role="alert">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="complaint-entry-form" noValidate>
          {/* Section 1: Complaint Information */}
          <div className="form-fieldset">
            <h2 className="fieldset-title">1. Grievance Description</h2>

            <div className="form-group">
              <label htmlFor="complaint-title" className="form-label">
                Complaint Title / Brief Subject <span className="required-asterisk">*</span>
              </label>
              <input
                id="complaint-title"
                type="text"
                className="form-input"
                placeholder="e.g. Air conditioning not cooling in 3AC coach B2"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={loading}
                required
              />
              {title.trim().length > 0 && title.trim().length < 5 && (
                <p className="field-error-msg">Title must be at least 5 characters.</p>
              )}
            </div>

            <div className="form-group">
              <div className="label-with-toggle">
                <label htmlFor="complaint-desc" className="form-label">
                  Detailed Complaint Description in Plain English <span className="required-asterisk">*</span>
                </label>
                <span className={`char-counter ${isTooLong ? 'limit-exceeded' : ''}`}>
                  {charCount} / 1500 chars
                </span>
              </div>
              <textarea
                id="complaint-desc"
                className={`form-textarea ${isTooShort || isTooLong ? 'input-error' : ''}`}
                rows="5"
                placeholder="Describe your issue in detail. For example: The bio-toilet in coach S4 is clogged and overflowing with terrible foul smell, please clean immediately..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={loading}
                required
              />
              {isTooShort && (
                <p className="field-error-msg">Please provide at least 5 characters for accurate AI classification.</p>
              )}
              {isTooLong && (
                <p className="field-error-msg">Exceeds maximum character limit of 1500 characters.</p>
              )}
            </div>
          </div>

          {/* Section 2: Journey Details */}
          <div className="form-fieldset">
            <h2 className="fieldset-title">2. Journey & Coach Metadata <span className="optional-tag">(Optional)</span></h2>

            <div className="form-row-two-col">
              <div className="form-group">
                <label htmlFor="train-number" className="form-label">
                  Train Number or Train Name
                </label>
                <input
                  id="train-number"
                  type="text"
                  className="form-input"
                  placeholder="e.g. 12951 Mumbai Rajdhani"
                  value={trainNumber}
                  onChange={(e) => setTrainNumber(e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="pnr-number" className="form-label">
                  10-Digit PNR Number
                </label>
                <input
                  id="pnr-number"
                  type="text"
                  maxLength="10"
                  className="form-input"
                  placeholder="e.g. 2458963214"
                  value={pnrNumber}
                  onChange={(e) => setPnrNumber(e.target.value)}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-row-three-col">
              <div className="form-group">
                <label htmlFor="journey-date" className="form-label">
                  Date of Journey
                </label>
                <input
                  id="journey-date"
                  type="date"
                  className="form-input"
                  value={journeyDate}
                  onChange={(e) => setJourneyDate(e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="station-loc" className="form-label">
                  Station or Location
                </label>
                <input
                  id="station-loc"
                  type="text"
                  className="form-input"
                  placeholder="e.g. Kanpur Central"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="coach-seat" className="form-label">
                  Coach & Berth Number
                </label>
                <input
                  id="coach-seat"
                  type="text"
                  className="form-input"
                  placeholder="e.g. B2 - Berth 24"
                  value={coachNumber}
                  onChange={(e) => setCoachNumber(e.target.value)}
                  disabled={loading}
                />
              </div>
            </div>
          </div>

          <div className="form-submit-bar">
            <button
              type="button"
              className="btn-secondary"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </button>

            <button
              id="submit-complaint-btn"
              type="submit"
              className="btn-primary"
              disabled={!isValid || loading}
            >
              {loading ? (
                <span className="btn-loading-flex">
                  <span className="spinner-dots"></span> Processing AI Classification...
                </span>
              ) : (
                'Submit & Route via AI'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
