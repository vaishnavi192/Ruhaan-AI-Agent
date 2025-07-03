import React, { useState } from 'react';
import './AdminLoginPage.css';

const AdminLoginPage = ({ onAuthSuccess }) => {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!password) {
      setError('Please enter the admin password');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('https://ruhaan-336f0cf6b1b5.herokuapp.com//api/admin/authenticate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password })
      });
      
      const data = await response.json();
      
      if (response.ok && data.success) {
        setSuccess('Authentication successful! Accessing dashboard...');
        
        // Store session token
        localStorage.setItem('admin_session', data.session_token);
        
        // Call parent callback to update app state
        setTimeout(() => {
          onAuthSuccess(data.session_token);
        }, 1000);
      } else {
        setError(data.message || 'Invalid password');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-login-page">
      <div className="login-container">
        <div className="logo">🔐</div>
        <h1 className="title">Analytics Dashboard</h1>
        <p className="subtitle">Admin Access Required</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="password" className="form-label">Admin Password</label>
            <input 
              type="password" 
              id="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-input" 
              placeholder="Enter admin password"
              required
              autoFocus
            />
          </div>
          
          <button 
            type="submit" 
            className="login-btn" 
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Access Dashboard'}
          </button>
          
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
        </form>
      </div>
    </div>
  );
};

export default AdminLoginPage;
