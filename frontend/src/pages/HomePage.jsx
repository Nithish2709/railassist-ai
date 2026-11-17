import React from 'react';

export default function HomePage({
  onStartClassify,
  onLearnMore,
  onGoToLogin,
  onGoToRegister,
  onGoToTrack,
  user,
  categories,
}) {
  return (
    <div className="home-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-pill">
          <span>🚂 Natural Language Processing Prototype • MySQL Persistent Portal</span>
        </div>
        <h1 className="hero-title">
          AI-Powered Railway Complaint Classification
        </h1>
        <p className="hero-subtitle">
          RailAssist AI automatically categorizes passenger grievances from plain-English descriptions 
          using machine learning and deterministically routes each complaint to the responsible Indian Railways department.
        </p>

        <div className="hero-actions">
          {user ? (
            <button
              id="hero-dashboard-btn"
              className="btn-primary"
              onClick={onGoToLogin}
            >
              <span>Access Your Dashboard</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14" />
                <path d="m12 5 7 7-7 7" />
              </svg>
            </button>
          ) : (
            <>
              <button
                id="hero-register-btn"
                className="btn-primary"
                onClick={onGoToRegister}
              >
                <span>Lodge a Complaint (Sign Up)</span>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14" />
                  <path d="m12 5 7 7-7 7" />
                </svg>
              </button>

              <button
                id="hero-signin-btn"
                className="btn-secondary"
                onClick={onGoToLogin}
              >
                <span>Portal Sign In</span>
              </button>
            </>
          )}

          <button
            id="hero-track-btn"
            className="btn-secondary"
            onClick={onGoToTrack}
          >
            <span>Track Grievance</span>
          </button>

          <button
            id="hero-classify-btn"
            className="btn-secondary"
            onClick={onStartClassify}
          >
            <span>Try AI Classifier Demo</span>
          </button>
        </div>
      </section>

      {/* Academic Disclaimer Box */}
      <div className="alert-box warning" role="alert">
        <div className="alert-icon">⚠️</div>
        <div>
          <div className="alert-title">Academic Demonstration Prototype</div>
          <div className="alert-text">
            RailAssist AI is a standalone academic research project demonstrating automated text classification using TF-IDF and Random Forest. 
            It is <strong>not</strong> officially integrated with Indian Railways, IRCTC, or RailMadad. Emergency complaints entered here do not reach real railway authorities.
          </div>
        </div>
      </div>

      {/* 3-Step Process Section */}
      <section className="section-process" aria-labelledby="process-heading">
        <div className="section-header">
          <h2 id="process-heading" className="section-title">How RailAssist AI Works</h2>
          <p className="section-subtitle">Three deterministic steps from passenger grievance to departmental action</p>
        </div>

        <div className="process-grid">
          <div className="process-step-card">
            <span className="step-number">01</span>
            <div className="step-icon-wrap">✍️</div>
            <h3 className="card-title">1. Enter Complaint</h3>
            <p className="card-text">
              The passenger describes an issue in natural, unconstrained English — whether it involves dirty bio-toilets, train delays, catering quality, or electrical faults.
            </p>
          </div>

          <div className="process-step-card">
            <span className="step-number">02</span>
            <div className="step-icon-wrap">⚙️</div>
            <h3 className="card-title">2. ML Analyzes Text</h3>
            <p className="card-text">
              A TF-IDF vectorizer extracts unigram and bigram n-gram features. An ensemble of 200 Random Forest decision trees analyzes text patterns to predict the specific complaint category.
            </p>
          </div>

          <div className="process-step-card">
            <span className="step-number">03</span>
            <div className="step-icon-wrap">🏛️</div>
            <h3 className="card-title">3. Route Department</h3>
            <p className="card-text">
              A deterministic mapping engine, completely separate from the statistical model, routes the complaint directly to the specialized Indian Railways department for resolution.
            </p>
          </div>
        </div>
      </section>

      {/* Supported Categories Overview */}
      <section className="section-categories" style={{ marginTop: '4rem' }} aria-labelledby="cat-overview-heading">
        <div className="section-header">
          <h2 id="cat-overview-heading" className="section-title">Target Operational Categories</h2>
          <p className="section-subtitle">8 core Indian Railways complaint domains with verified training data</p>
        </div>

        <div className="category-pills-grid">
          {categories && categories.length > 0 ? (
            categories.map((cat) => (
              <div key={cat.id} className="category-pill-card">
                <div className="cat-header">
                  <span className="cat-name">{cat.name}</span>
                  <span className="cat-badge operational">Operational</span>
                </div>
                <div className="cat-dept">{cat.department}</div>
                <div style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '0.25rem' }}>
                  {cat.description}
                </div>
              </div>
            ))
          ) : (
            <div style={{ color: '#94a3b8', gridColumn: '1 / -1', textAlign: 'center', padding: '2rem' }}>
              Loading operational category configuration...
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
