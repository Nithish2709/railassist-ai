import React from 'react';

export default function Navbar({ activeTab, setActiveTab, apiOnline, user, onLogout, theme, onToggleTheme }) {
  const getDashboardTab = () => {
    if (!user) return 'login';
    if (user.role === 'RAILWAY_ADMIN') return 'admin-dashboard';
    if (user.role === 'DEPARTMENT_AUTHORITY') return 'dept-dashboard';
    return 'passenger-dashboard';
  };

  const getRoleLabel = () => {
    if (!user) return '';
    if (user.role === 'RAILWAY_ADMIN') return 'Central Admin';
    if (user.role === 'DEPARTMENT_AUTHORITY') return user.department_name ? `Dept: ${user.department_name.split(' ')[0]}` : 'Dept Officer';
    return 'Passenger';
  };

  return (
    <header className="navbar-wrapper">
      {/* Indian Railways Official Identity Sub-bar */}
      <div className="gov-topbar">
        <div className="gov-topbar-inner">
          <div className="gov-brand-text">
            <span className="gov-flag-stripes">
              <span className="stripe-saffron"></span>
              <span className="stripe-white"></span>
              <span className="stripe-green"></span>
            </span>
            <span className="gov-portal-name">INDIAN RAILWAYS GRIEVANCE REDRESSAL SYSTEM</span>
            <span className="gov-academic-badge">Academic Prototype</span>
          </div>
          <div className="gov-support-contact">
            <span>RailMadad AI Research Initiative</span>
          </div>
        </div>
      </div>

      <div className="navbar">
        <div className="navbar-inner">
          <div className="brand-container" onClick={() => setActiveTab('home')}>
            <div className="brand-logo-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="4" y="3" width="16" height="16" rx="3" fill="#0B2545" />
                <path d="M4 11h16" stroke="#E2E8F0" />
                <path d="M12 3v8" stroke="#E2E8F0" />
                <path d="m8 19-2 3" stroke="#F59E0B" strokeWidth="2.5" />
                <path d="m16 19 2 3" stroke="#F59E0B" strokeWidth="2.5" />
                <circle cx="8" cy="15" r="1.5" fill="#38BDF8" stroke="none" />
                <circle cx="16" cy="15" r="1.5" fill="#38BDF8" stroke="none" />
              </svg>
            </div>
            <div className="brand-text-block">
              <span className="brand-title">
                RailAssist <span className="brand-accent">AI</span>
              </span>
              <span className="brand-subtitle">Automated Grievance Classification Portal</span>
            </div>
          </div>

          <nav className="nav-links" aria-label="Main Navigation">
            <button
              id="nav-home"
              className={`nav-btn ${activeTab === 'home' ? 'active' : ''}`}
              onClick={() => setActiveTab('home')}
            >
              Home
            </button>

            <button
              id="nav-track"
              className={`nav-btn ${activeTab === 'track' ? 'active' : ''}`}
              onClick={() => setActiveTab('track')}
            >
              Track Complaint
            </button>

            <button
              id="nav-classify"
              className={`nav-btn ${activeTab === 'classify' ? 'active' : ''}`}
              onClick={() => setActiveTab('classify')}
              title="Interactive Plain-Text ML Classifier Demonstration"
            >
              AI Classifier Demo
            </button>

            <button
              id="nav-about"
              className={`nav-btn ${activeTab === 'about' ? 'active' : ''}`}
              onClick={() => setActiveTab('about')}
            >
              About
            </button>

            {user ? (
              <div className="nav-user-cluster">
                <button
                  id="nav-dashboard"
                  className={`nav-btn primary-nav-btn ${activeTab.includes('dashboard') ? 'active' : ''}`}
                  onClick={() => setActiveTab(getDashboardTab())}
                >
                  Dashboard
                </button>
                <div className="user-profile-badge" title={user.email}>
                  <div className="user-avatar-circle">
                    {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                  </div>
                  <div className="user-info-text">
                    <span className="user-name-label">{user.full_name}</span>
                    <span className="user-role-tag">{getRoleLabel()}</span>
                  </div>
                </div>
                <button
                  id="nav-logout-btn"
                  className="nav-btn logout-nav-btn"
                  onClick={onLogout}
                  title="Sign out of your account"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="nav-auth-cluster">
                <button
                  id="nav-login-btn"
                  className={`nav-btn login-nav-btn ${activeTab === 'login' ? 'active' : ''}`}
                  onClick={() => setActiveTab('login')}
                >
                  Sign In
                </button>
                <button
                  id="nav-register-btn"
                  className={`nav-btn register-nav-btn ${activeTab === 'register' ? 'active' : ''}`}
                  onClick={() => setActiveTab('register')}
                >
                  Register
                </button>
              </div>
            )}

            {/* Theme Toggle Button */}
            <button
              id="theme-toggle-btn"
              className="theme-toggle-btn"
              onClick={onToggleTheme}
              title={theme === 'dark' ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
              aria-label="Toggle visual theme"
            >
              {theme === 'dark' ? (
                <span className="theme-toggle-icon">
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#FBBF24" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="5" fill="#FBBF24" fillOpacity="0.2" />
                    <line x1="12" y1="1" x2="12" y2="3" />
                    <line x1="12" y1="21" x2="12" y2="23" />
                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                    <line x1="1" y1="12" x2="3" y2="12" />
                    <line x1="21" y1="12" x2="23" y2="12" />
                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                  </svg>
                  <span className="theme-name">Light</span>
                </span>
              ) : (
                <span className="theme-toggle-icon">
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" fill="#38BDF8" fillOpacity="0.2" />
                  </svg>
                  <span className="theme-name">Dark</span>
                </span>
              )}
            </button>

            <div
              id="api-status-indicator"
              className={`api-status-badge ${apiOnline ? 'online' : 'offline'}`}
              title={apiOnline ? 'Backend API and ML Model loaded on port 8000' : 'Backend API unreachable at port 8000'}
            >
              <span className="status-dot"></span>
              <span>{apiOnline ? 'API Active' : 'API Offline'}</span>
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}
