import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import ClassifyPage from './pages/ClassifyPage';
import AboutPage from './pages/AboutPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import TrackComplaintPage from './pages/TrackComplaintPage';
import PassengerDashboard from './pages/PassengerDashboard';
import SubmitComplaintPage from './pages/SubmitComplaintPage';
import MyComplaintsPage from './pages/MyComplaintsPage';
import ComplaintDetailPage from './pages/ComplaintDetailPage';
import AdminDashboard from './pages/AdminDashboard';
import DepartmentDashboard from './pages/DepartmentDashboard';

import {
  getAuthToken,
  getAuthUser,
  setAuthSession,
  clearAuthSession,
  getAuthHeaders,
} from './utils/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [apiOnline, setApiOnline] = useState(false);
  const [categories, setCategories] = useState([]);
  const [user, setUser] = useState(getAuthUser());
  const [selectedRefNumber, setSelectedRefNumber] = useState(null);
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('railassist_theme') || 'light';
  });

  // Sync theme with document root attribute
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('railassist_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  // Validate or restore authentication session on mount
  useEffect(() => {
    let isMounted = true;

    async function verifySession() {
      const token = getAuthToken();
      if (!token) {
        if (isMounted) setUser(null);
        return;
      }

      try {
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: getAuthHeaders(),
        });
        if (res.ok) {
          const userData = await res.json();
          if (isMounted) {
            setUser(userData);
            setAuthSession(token, userData);
          }
        } else {
          // Token expired or invalid
          clearAuthSession();
          if (isMounted) setUser(null);
        }
      } catch {
        // Keep cached user if network is momentarily disconnected
      }
    }

    verifySession();
    return () => { isMounted = false; };
  }, []);

  // Check backend health & fetch categories on mount
  useEffect(() => {
    let isMounted = true;

    async function checkBackend() {
      try {
        const healthRes = await fetch(`${API_BASE_URL}/health`);
        if (healthRes.ok) {
          const healthData = await healthRes.json();
          if (isMounted) setApiOnline(healthData.model_loaded);
        } else {
          if (isMounted) setApiOnline(false);
        }
      } catch {
        if (isMounted) setApiOnline(false);
      }

      try {
        const catRes = await fetch(`${API_BASE_URL}/categories`);
        if (catRes.ok) {
          const catData = await catRes.json();
          if (isMounted && catData.categories) {
            setCategories(catData.categories);
          }
        }
      } catch (err) {
        console.warn("Could not fetch categories list from backend:", err);
      }
    }

    checkBackend();
    const interval = setInterval(checkBackend, 15000); // Heartbeat every 15s

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleLoginSuccess = (token, loggedInUser) => {
    setAuthSession(token, loggedInUser);
    setUser(loggedInUser);

    // Redirect to designated role dashboard
    if (loggedInUser.role === 'RAILWAY_ADMIN') {
      setActiveTab('admin-dashboard');
    } else if (loggedInUser.role === 'DEPARTMENT_AUTHORITY') {
      setActiveTab('dept-dashboard');
    } else {
      setActiveTab('passenger-dashboard');
    }
  };

  const handleLogout = () => {
    clearAuthSession();
    setUser(null);
    setActiveTab('home');
  };

  const handleSelectComplaint = (refNumber) => {
    setSelectedRefNumber(refNumber);
    setActiveTab('complaint-detail');
  };

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        apiOnline={apiOnline}
        user={user}
        onLogout={handleLogout}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      <main className="main-content">
        {/* Public Pages */}
        {activeTab === 'home' && (
          <HomePage
            onStartClassify={() => setActiveTab('classify')}
            onLearnMore={() => setActiveTab('about')}
            onGoToLogin={() => setActiveTab('login')}
            onGoToRegister={() => setActiveTab('register')}
            onGoToTrack={() => setActiveTab('track')}
            user={user}
            categories={categories}
          />
        )}

        {activeTab === 'classify' && (
          <ClassifyPage
            apiBaseUrl={API_BASE_URL}
          />
        )}

        {activeTab === 'about' && (
          <AboutPage
            categories={categories}
          />
        )}

        {activeTab === 'track' && (
          <TrackComplaintPage
            apiBaseUrl={API_BASE_URL}
            onSelectComplaint={handleSelectComplaint}
            onSwitchToLogin={() => setActiveTab('login')}
          />
        )}

        {/* Authentication Pages */}
        {activeTab === 'login' && (
          <LoginPage
            apiBaseUrl={API_BASE_URL}
            onLoginSuccess={handleLoginSuccess}
            onSwitchToRegister={() => setActiveTab('register')}
          />
        )}

        {activeTab === 'register' && (
          <RegisterPage
            apiBaseUrl={API_BASE_URL}
            onRegisterSuccess={handleLoginSuccess}
            onSwitchToLogin={() => setActiveTab('login')}
          />
        )}

        {/* Passenger Pages */}
        {activeTab === 'passenger-dashboard' && (
          <PassengerDashboard
            apiBaseUrl={API_BASE_URL}
            user={user}
            onLodgeComplaint={() => setActiveTab('submit-complaint')}
            onViewMyComplaints={() => setActiveTab('my-complaints')}
            onSelectComplaint={handleSelectComplaint}
          />
        )}

        {activeTab === 'submit-complaint' && (
          <SubmitComplaintPage
            apiBaseUrl={API_BASE_URL}
            onComplaintCreated={handleSelectComplaint}
            onCancel={() => setActiveTab('passenger-dashboard')}
          />
        )}

        {activeTab === 'my-complaints' && (
          <MyComplaintsPage
            apiBaseUrl={API_BASE_URL}
            onSelectComplaint={handleSelectComplaint}
            onLodgeNew={() => setActiveTab('submit-complaint')}
            onBackToDashboard={() => setActiveTab('passenger-dashboard')}
          />
        )}

        {/* Universal Complaint Detail / Timeline */}
        {activeTab === 'complaint-detail' && (
          <ComplaintDetailPage
            apiBaseUrl={API_BASE_URL}
            referenceNumber={selectedRefNumber}
            user={user}
            onBack={() => {
              if (user?.role === 'RAILWAY_ADMIN') setActiveTab('admin-dashboard');
              else if (user?.role === 'DEPARTMENT_AUTHORITY') setActiveTab('dept-dashboard');
              else if (user?.role === 'USER') setActiveTab('passenger-dashboard');
              else setActiveTab('track');
            }}
          />
        )}

        {/* Railway Admin Dashboard */}
        {activeTab === 'admin-dashboard' && (
          <AdminDashboard
            apiBaseUrl={API_BASE_URL}
            user={user}
            onSelectComplaint={handleSelectComplaint}
          />
        )}

        {/* Department Authority Dashboard */}
        {activeTab === 'dept-dashboard' && (
          <DepartmentDashboard
            apiBaseUrl={API_BASE_URL}
            user={user}
            onSelectComplaint={handleSelectComplaint}
          />
        )}
      </main>

      <Footer onNavClick={(tab) => setActiveTab(tab)} />
    </div>
  );
}
