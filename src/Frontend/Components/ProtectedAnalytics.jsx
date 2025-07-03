import React, { useState, useEffect } from 'react';
import AdminLogin from './AdminLogin';
import AnalyticsDashboard from './AnalyticsDashboard';

const ProtectedAnalytics = ({ onBack }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check URL parameters for admin session
    const urlParams = new URLSearchParams(window.location.search);
    const adminSession = urlParams.get('admin_session');
    
    if (adminSession) {
      // Verify session with backend
      verifyAdminSession(adminSession);
    } else {
      // Check if admin is already logged in locally
      const authStatus = localStorage.getItem('ruhaan_admin_auth');
      const loginTime = localStorage.getItem('ruhaan_admin_login_time');
      
      if (authStatus === 'true' && loginTime) {
        // Check if login is still valid (24 hours)
        const now = Date.now();
        const loginTimestamp = parseInt(loginTime);
        const twentyFourHours = 24 * 60 * 60 * 1000;
        
        if (now - loginTimestamp < twentyFourHours) {
          setIsAuthenticated(true);
        } else {
          // Session expired, clear auth
          localStorage.removeItem('ruhaan_admin_auth');
          localStorage.removeItem('ruhaan_admin_login_time');
        }
      }
      
      setLoading(false);
    }
  }, []);

  const verifyAdminSession = async (sessionToken) => {
    try {
      const response = await fetch(`https://ruhaan-336f0cf6b1b5.herokuapp.com/api/admin/verify/${sessionToken}`);
      const data = await response.json();
      
      if (response.ok && data.valid) {
        setIsAuthenticated(true);
        localStorage.setItem('ruhaan_admin_auth', 'true');
        localStorage.setItem('ruhaan_admin_login_time', Date.now().toString());
        localStorage.setItem('admin_session_token', sessionToken);
        
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
      } else {
        console.error('Invalid admin session');
      }
    } catch (error) {
      console.error('Session verification failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (success) => {
    setIsAuthenticated(success);
  };

  const handleLogout = () => {
    localStorage.removeItem('ruhaan_admin_auth');
    localStorage.removeItem('ruhaan_admin_login_time');
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '50vh',
        color: '#fff'
      }}>
        <div>🔄 Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AdminLogin onLogin={handleLogin} />;
  }

  return (
    <div>
      {/* Add logout button to dashboard */}
      <AnalyticsDashboard 
        onBack={onBack} 
        onLogout={handleLogout}
      />
    </div>
  );
};

export default ProtectedAnalytics;
