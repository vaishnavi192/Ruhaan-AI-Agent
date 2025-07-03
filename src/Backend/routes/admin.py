# Admin authentication route
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from datetime import datetime, timedelta
import secrets

router = APIRouter()

class AdminLoginRequest(BaseModel):
    password: str

# Simple session storage (upgrade to Redis/database in production)
admin_sessions = {}

# Admin credentials
ADMIN_PASSWORD = "ruhaan_admin_2025"
SESSION_DURATION_HOURS = 24

@router.get("/login", response_class=HTMLResponse)
async def admin_login_page():
    """Serve the admin login page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ruhaan Analytics - Admin Login</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .login-container {
                background: white;
                padding: 2rem;
                border-radius: 15px;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 400px;
                text-align: center;
            }
            
            .logo {
                font-size: 2.5rem;
                color: #667eea;
                margin-bottom: 1rem;
            }
            
            .title {
                color: #333;
                margin-bottom: 0.5rem;
                font-size: 1.5rem;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 2rem;
                font-size: 0.9rem;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
                text-align: left;
            }
            
            .form-label {
                display: block;
                margin-bottom: 0.5rem;
                color: #333;
                font-weight: 500;
            }
            
            .form-input {
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 1rem;
                transition: border-color 0.3s ease;
            }
            
            .form-input:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .login-btn {
                width: 100%;
                padding: 12px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }
            
            .login-btn:hover {
                background: #5a67d8;
            }
            
            .login-btn:disabled {
                background: #a0aec0;
                cursor: not-allowed;
            }
            
            .error-message {
                color: #e53e3e;
                margin-top: 1rem;
                font-size: 0.9rem;
                display: none;
            }
            
            .success-message {
                color: #38a169;
                margin-top: 1rem;
                font-size: 0.9rem;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">🔐</div>
            <h1 class="title">Analytics Dashboard</h1>
            <p class="subtitle">Admin Access Required</p>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="password" class="form-label">Admin Password</label>
                    <input 
                        type="password" 
                        id="password" 
                        name="password" 
                        class="form-input" 
                        placeholder="Enter admin password"
                        required
                    >
                </div>
                
                <button type="submit" class="login-btn" id="loginBtn">
                    Access Dashboard
                </button>
                
                <div id="errorMessage" class="error-message"></div>
                <div id="successMessage" class="success-message"></div>
            </form>
        </div>
        
        <script>
            const form = document.getElementById('loginForm');
            const passwordInput = document.getElementById('password');
            const loginBtn = document.getElementById('loginBtn');
            const errorMessage = document.getElementById('errorMessage');
            const successMessage = document.getElementById('successMessage');
            
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const password = passwordInput.value;
                
                if (!password) {
                    showError('Please enter the admin password');
                    return;
                }
                
                loginBtn.disabled = true;
                loginBtn.textContent = 'Authenticating...';
                
                try {
                    const response = await fetch('/api/admin/authenticate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ password })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok && data.success) {
                        showSuccess('Authentication successful! Redirecting...');
                        
                        // Store session token
                        localStorage.setItem('admin_session', data.session_token);
                        
                        // Redirect to main app with admin session
                        setTimeout(() => {
                            window.location.href = '/?admin_session=' + data.session_token;
                        }, 1500);
                    } else {
                        showError(data.message || 'Invalid password');
                    }
                } catch (error) {
                    showError('Network error. Please try again.');
                } finally {
                    loginBtn.disabled = false;
                    loginBtn.textContent = 'Access Dashboard';
                }
            });
            
            function showError(message) {
                errorMessage.textContent = message;
                errorMessage.style.display = 'block';
                successMessage.style.display = 'none';
            }
            
            function showSuccess(message) {
                successMessage.textContent = message;
                successMessage.style.display = 'block';
                errorMessage.style.display = 'none';
            }
            
            // Focus password input on load
            passwordInput.focus();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/authenticate")
async def authenticate_admin(request: AdminLoginRequest):
    """Authenticate admin user"""
    try:
        if request.password != ADMIN_PASSWORD:
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        
        # Store session with expiration
        admin_sessions[session_token] = {
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=SESSION_DURATION_HOURS),
            "authenticated": True
        }
        
        return {
            "success": True,
            "message": "Authentication successful",
            "session_token": session_token,
            "expires_in_hours": SESSION_DURATION_HOURS
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@router.get("/verify/{session_token}")
async def verify_admin_session(session_token: str):
    """Verify admin session token"""
    try:
        if session_token not in admin_sessions:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        session = admin_sessions[session_token]
        
        # Check if session is expired
        if datetime.now() > session["expires_at"]:
            del admin_sessions[session_token]
            raise HTTPException(status_code=401, detail="Session expired")
        
        return {
            "valid": True,
            "authenticated": session["authenticated"],
            "expires_at": session["expires_at"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")

@router.post("/logout")
async def logout_admin(request: Request):
    """Logout admin user"""
    try:
        # Get session token from header or body
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            session_token = auth_header.split(" ")[1]
            
            if session_token in admin_sessions:
                del admin_sessions[session_token]
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout error: {str(e)}")
