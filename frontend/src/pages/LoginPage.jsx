import React, { useState } from 'react';

export default function LoginPage({ apiBaseUrl, onLoginSuccess, onSwitchToRegister }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError('Please provide both your registered email address and password.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed. Please check your credentials.');
      }

      onLoginSuccess(data.access_token, data.user);
    } catch (err) {
      setError(err.message || 'Unable to connect to the authentication service.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError(null);
  };

  return (
    <div className="auth-page-container">
      <div className="auth-card">
        <div className="auth-card-header">
          <div className="railway-crest-icon">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#0B2545" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
          </div>
          <h1 className="auth-title">RailAssist AI Portal Login</h1>
          <p className="auth-subtitle">
            Sign in to access your passenger complaints, department action queues, or central administration.
          </p>
        </div>

        {error && (
          <div className="auth-error-banner" role="alert">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          <div className="form-group">
            <label htmlFor="login-email" className="form-label">
              Official Email Address <span className="required-asterisk">*</span>
            </label>
            <input
              id="login-email"
              type="email"
              className="form-input"
              placeholder="e.g. passenger@example.com or officer@railassist.gov.in"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <div className="label-with-toggle">
              <label htmlFor="login-password" className="form-label">
                Account Password <span className="required-asterisk">*</span>
              </label>
              <button
                type="button"
                className="toggle-password-btn"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex="-1"
              >
                {showPassword ? 'Hide Password' : 'Show Password'}
              </button>
            </div>
            <input
              id="login-password"
              type={showPassword ? 'text' : 'password'}
              className="form-input"
              placeholder="Enter your account password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              required
            />
          </div>

          <button
            id="login-submit-btn"
            type="submit"
            className="btn-primary auth-submit-btn"
            disabled={loading}
          >
            {loading ? (
              <span className="btn-loading-flex">
                <span className="spinner-dots"></span> Verifying Credentials...
              </span>
            ) : (
              'Secure Sign In'
            )}
          </button>
        </form>

        {/* Quick Demo Login Preset Bar */}
        <div className="demo-credentials-box">
          <span className="demo-box-title">⚡ Quick Academic Demonstration Logins:</span>
          <p className="demo-box-hint">Click any profile below to autofill verified seeded credentials:</p>
          <div className="demo-button-grid">
            <button
              type="button"
              className="demo-chip-btn"
              onClick={() => handleQuickDemo('passenger@example.com', 'Passenger@123')}
            >
              <span className="chip-icon">🚆</span>
              <span className="chip-text">Passenger User</span>
            </button>

            <button
              type="button"
              className="demo-chip-btn admin-chip"
              onClick={() => handleQuickDemo('admin@railassist.gov.in', 'AdminPassword@123')}
            >
              <span className="chip-icon">🛡️</span>
              <span className="chip-text">Railway Central Admin</span>
            </button>

            <button
              type="button"
              className="demo-chip-btn dept-chip"
              onClick={() => handleQuickDemo('catering.auth@railassist.gov.in', 'DeptPassword@123')}
            >
              <span className="chip-icon">🍽️</span>
              <span className="chip-text">Catering Authority</span>
            </button>

            <button
              type="button"
              className="demo-chip-btn dept-chip"
              onClick={() => handleQuickDemo('electrical.auth@railassist.gov.in', 'DeptPassword@123')}
            >
              <span className="chip-icon">⚡</span>
              <span className="chip-text">Electrical Authority</span>
            </button>
          </div>
        </div>

        <div className="auth-card-footer">
          <span>Are you a railway passenger without an account?</span>
          <button
            type="button"
            className="link-btn-highlight"
            onClick={onSwitchToRegister}
          >
            Register Passenger Account
          </button>
        </div>
      </div>
    </div>
  );
}
