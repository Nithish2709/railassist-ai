import React, { useState } from 'react';

export default function RegisterPage({ apiBaseUrl, onRegisterSuccess, onSwitchToLogin }) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!fullName.trim() || fullName.trim().length < 2) {
      setError('Please provide your full legal name (at least 2 characters).');
      return;
    }
    if (!email.trim()) {
      setError('A valid email address is required for complaint status notifications.');
      return;
    }
    if (password.length < 6) {
      setError('Password must contain at least 6 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match. Please re-enter identical passwords.');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: fullName.trim(),
          email: email.trim(),
          phone: phone.trim() || null,
          password: password,
          confirm_password: confirmPassword,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed. Please review your input.');
      }

      onRegisterSuccess(data.access_token, data.user);
    } catch (err) {
      setError(err.message || 'Unable to complete passenger registration.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-container">
      <div className="auth-card register-card-wide">
        <div className="auth-card-header">
          <div className="railway-crest-icon">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#0B2545" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <line x1="19" y1="8" x2="19" y2="14" />
              <line x1="22" y1="11" x2="16" y2="11" />
            </svg>
          </div>
          <h1 className="auth-title">Register Passenger Account</h1>
          <p className="auth-subtitle">
            Create an Indian Railways passenger profile to lodge complaints, receive automated AI department routing, and track resolution timelines.
          </p>
        </div>

        <div className="role-confinement-notice">
          <span className="notice-icon">ℹ️</span>
          <span>
            <strong>Public Registration Scope:</strong> This form creates a verified <strong>Passenger (USER)</strong> account. Administrative officers and Department Authorities are provisioned through internal Railway Board security controls.
          </span>
        </div>

        {error && (
          <div className="auth-error-banner" role="alert">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form" noValidate>
          <div className="form-row-two-col">
            <div className="form-group">
              <label htmlFor="reg-fullname" className="form-label">
                Full Legal Name <span className="required-asterisk">*</span>
              </label>
              <input
                id="reg-fullname"
                type="text"
                className="form-input"
                placeholder="e.g. Surendar Kumar"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="reg-email" className="form-label">
                Email Address <span className="required-asterisk">*</span>
              </label>
              <input
                id="reg-email"
                type="email"
                className="form-input"
                placeholder="e.g. surendar@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="reg-phone" className="form-label">
              Mobile Contact Number <span className="optional-tag">(Optional)</span>
            </label>
            <input
              id="reg-phone"
              type="tel"
              className="form-input"
              placeholder="+91 98765 43210"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="form-row-two-col">
            <div className="form-group">
              <div className="label-with-toggle">
                <label htmlFor="reg-password" className="form-label">
                  Password (min 6 chars) <span className="required-asterisk">*</span>
                </label>
                <button
                  type="button"
                  className="toggle-password-btn"
                  onClick={() => setShowPassword(!showPassword)}
                  tabIndex="-1"
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>
              <input
                id="reg-password"
                type={showPassword ? 'text' : 'password'}
                className="form-input"
                placeholder="Enter secure password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="reg-confirm-password" className="form-label">
                Confirm Password <span className="required-asterisk">*</span>
              </label>
              <input
                id="reg-confirm-password"
                type={showPassword ? 'text' : 'password'}
                className="form-input"
                placeholder="Re-enter password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                required
              />
            </div>
          </div>

          <button
            id="register-submit-btn"
            type="submit"
            className="btn-primary auth-submit-btn"
            disabled={loading}
          >
            {loading ? (
              <span className="btn-loading-flex">
                <span className="spinner-dots"></span> Creating Passenger Account...
              </span>
            ) : (
              'Complete Registration & Open Dashboard'
            )}
          </button>
        </form>

        <div className="auth-card-footer">
          <span>Already have an account?</span>
          <button
            type="button"
            className="link-btn-highlight"
            onClick={onSwitchToLogin}
          >
            Sign In Here
          </button>
        </div>
      </div>
    </div>
  );
}
