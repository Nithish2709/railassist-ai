import React, { useState } from 'react';

const SAMPLE_COMPLAINTS = [
  {
    label: "Dirty Bio-Toilet",
    text: "The bio-toilet in coach S4 is severely clogged, overflowing with filthy water, and emitting an unbearable foul smell."
  },
  {
    label: "Train Delay / Punctuality",
    text: "Train 12951 Rajdhani Express is running 4 hours late without any announcement or explanation from station authorities."
  },
  {
    label: "AC Electrical Failure",
    text: "Air conditioning in coach B3 stopped cooling over an hour ago. Passengers and children are sweating heavily in 40 degree heat."
  },
  {
    label: "Spoiled Food Quality",
    text: "Bad quality food served for lunch, catering tea was cold, stale and tasted sour. The pantry vendor charged 120 rupees without receipt."
  },
  {
    label: "Luggage Theft / Security",
    text: "My laptop bag and wallet were stolen from upper berth 46 in coach A2 while I was sleeping between Bhopal and Itarsi. Need urgent RPF assistance."
  },
  {
    label: "No Water in Washroom",
    text: "The washbasin and toilet flush tanks in coach S7 are completely dry since early morning. No water is available for passengers."
  }
];

export default function ClassifyPage({ apiBaseUrl }) {
  const [complaintText, setComplaintText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const charCount = complaintText.length;
  const isTooShort = charCount > 0 && charCount < 5;
  const isTooLong = charCount > 1500;
  const isValid = charCount >= 5 && charCount <= 1500;

  const handleClear = () => {
    setComplaintText("");
    setError(null);
    setResult(null);
  };

  const handleSelectSample = (sample) => {
    setComplaintText(sample.text);
    setError(null);
    setResult(null);
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!isValid || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${apiBaseUrl}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: complaintText })
      });

      if (!response.ok) {
        let errorDetail = "Server returned an error. Please try again.";
        try {
          const errData = await response.json();
          errorDetail = errData.detail || JSON.stringify(errData);
        } catch {
          errorDetail = `Request failed with HTTP status ${response.status} (${response.statusText})`;
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Classification error:", err);
      setError(err.message || "Failed to reach classification backend. Please verify FastAPI is running at port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="classifier-layout">
      <div className="section-header" style={{ margin: '1rem 0 2rem' }}>
        <h1 className="section-title">Classify Railway Complaint</h1>
        <p className="section-subtitle">
          Enter a passenger grievance in plain English. The machine learning pipeline will infer the category and assign the responsible department.
        </p>
      </div>

      <div className="classifier-card">
        <form onSubmit={handleSubmit}>
          <label htmlFor="complaint-input" className="form-label">
            Passenger Complaint Description
          </label>

          <div className="textarea-container">
            <textarea
              id="complaint-input"
              className="complaint-textarea"
              placeholder="Describe your railway complaint in plain English..."
              value={complaintText}
              onChange={(e) => setComplaintText(e.target.value)}
              disabled={loading}
              rows={5}
              aria-describedby="char-counter input-hint"
            />
          </div>

          <div className="textarea-meta">
            <span id="input-hint">
              {isTooShort && <span style={{ color: '#f87171' }}>Minimum 5 characters required</span>}
              {isTooLong && <span style={{ color: '#f87171' }}>Exceeds maximum limit of 1,500 characters</span>}
              {!isTooShort && !isTooLong && <span>Plain English description (5–1,500 characters)</span>}
            </span>
            <span
              id="char-counter"
              className={`char-counter ${charCount > 1300 ? 'near-limit' : ''} ${isTooLong ? 'over-limit' : ''}`}
            >
              {charCount.toLocaleString()} / 1,500
            </span>
          </div>

          {/* Quick-Test Prompts */}
          <div className="samples-header">
            <span>⚡ Quick Test Examples (Click to populate):</span>
          </div>
          <div className="sample-pills">
            {SAMPLE_COMPLAINTS.map((item, idx) => (
              <button
                key={idx}
                type="button"
                className="sample-pill-btn"
                onClick={() => handleSelectSample(item)}
                disabled={loading}
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="actions-row">
            <button
              id="clear-complaint-btn"
              type="button"
              className="btn-secondary"
              onClick={handleClear}
              disabled={loading || charCount === 0}
            >
              Clear
            </button>

            <button
              id="classify-complaint-btn"
              type="submit"
              className="btn-primary"
              disabled={!isValid || loading}
            >
              {loading ? (
                <>
                  <span className="spinner" aria-hidden="true"></span>
                  <span>Analyzing with Random Forest...</span>
                </>
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.3-4.3" />
                  </svg>
                  <span>Classify Complaint</span>
                </>
              )}
            </button>
          </div>
        </form>

        {/* Error Feedback */}
        {error && (
          <div className="error-box" role="alert">
            <span style={{ fontSize: '1.25rem' }}>⚠️</span>
            <div>
              <strong>Classification Request Failed:</strong> {error}
            </div>
          </div>
        )}
      </div>

      {/* Prediction Result Display */}
      {result && (
        <div id="prediction-result" className="result-card" role="region" aria-live="polite">
          <div className="result-header">
            <div>
              <span style={{ fontSize: '0.85rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Classification Output
              </span>
              <h2 style={{ fontSize: '1.35rem', color: '#ffffff', marginTop: '0.2rem' }}>
                Analysis & Departmental Routing
              </h2>
            </div>
            <span className={`result-badge ${result.status}`}>
              {result.status === 'success' ? '✓ High Agreement' : '⚠️ Uncertain / Multi-Topic'}
            </span>
          </div>

          <div className="input-quote-box">
            <strong>Entered Complaint:</strong> “{result.complaint_text}”
          </div>

          <div className="result-grid">
            <div className="result-box">
              <div className="result-box-label">Predicted Complaint Category</div>
              <div id="result-category" className="result-category-title">
                {result.predicted_category}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.35rem' }}>
                Predicted by TF-IDF + Random Forest Pipeline
              </div>
            </div>

            <div className="result-box">
              <div className="result-box-label">Assigned Railway Department</div>
              <div id="result-department" className="result-dept-title">
                {result.department}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.35rem' }}>
                Deterministic operational mapping logic
              </div>
            </div>
          </div>

          {/* Model Confidence Meter */}
          <div className="confidence-section">
            <div className="confidence-header">
              <span style={{ fontWeight: 600, color: '#ffffff', fontSize: '0.9rem' }}>
                Model Ensemble Confidence:
              </span>
              <span id="result-confidence" style={{ fontWeight: 700, color: '#f59e0b', fontSize: '1.05rem' }}>
                {result.confidence_percentage}
              </span>
            </div>

            <div className="confidence-bar-outer" role="progressbar" aria-valuenow={Math.round(result.confidence_score * 100)} aria-valuemin={0} aria-valuemax={100}>
              <div
                className={`confidence-bar-inner ${result.confidence_score < 0.4 ? 'low' : ''}`}
                style={{ width: `${Math.min(Math.max(result.confidence_score * 100, 5), 100)}%` }}
              ></div>
            </div>

            <p className="confidence-explanation-text">
              {result.confidence_explanation}
            </p>
          </div>

          {/* Limitations and Emergency Notice */}
          <div className="alert-box info" style={{ margin: '1rem 0 0' }}>
            <div className="alert-icon">ℹ️</div>
            <div className="alert-text">
              <strong>Prediction Disclaimer:</strong> Machine learning predictions can occasionally be inaccurate, 
              especially for complaints combining multiple distinct grievances. In addition, this prototype does 
              <strong> not</strong> automatically trigger emergency rescue or medical dispatch. In real life emergencies, contact railway helpline 139 or RPF immediately.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
