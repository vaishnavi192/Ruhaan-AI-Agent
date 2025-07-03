import React, { useState } from 'react';
import './AdminLogin.css';

const AdminLogin = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Simple admin password (in production, use proper authentication)
  const ADMIN_PASSWORD = 'ruhaan_admin_2025';

  const handleLogin = (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Simulate API call delay
    setTimeout(() => {
      if (password === ADMIN_PASSWORD) {
        // Store admin session in localStorage
        localStorage.setItem('ruhaan_admin_auth', 'true');
        localStorage.setItem('ruhaan_admin_login_time', Date.now().toString());
        onLogin(true);
      } else {
        setError('Invalid admin password');
      }
      setLoading(false);
    }, 500);
  };

  return (
    <div className="admin-login-container">
      <div className="admin-login-box">
        <div className="admin-header">
          <h2>🔐 Admin Access Required</h2>
          <p>Enter admin password to view analytics dashboard</p>
        </div>
        
        <form onSubmit={handleLogin} className="admin-form">
          <div className="input-group">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Admin password"
              className="admin-input"
              required
            />
          </div>
          
          {error && (
            <div className="error-message">
              ❌ {error}
            </div>
          )}
          
          <button 
            type="submit" 
            disabled={loading || !password}
            className="admin-submit-btn"
          >
            {loading ? '🔄 Verifying...' : '🚀 Access Dashboard'}
          </button>
        </form>
        
        <div className="admin-info">
          <p>👑 Admin-only feature</p>
          <p>This dashboard contains user analytics data</p>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;
