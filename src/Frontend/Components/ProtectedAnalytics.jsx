import React, { useState, useEffect } from 'react';
import AdminLogin from './AdminLogin';
import AnalyticsDashboard from './AnalyticsDashboard';

const ProtectedAnalytics = ({ onBack }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if admin is already logged in
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
  }, []);

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
