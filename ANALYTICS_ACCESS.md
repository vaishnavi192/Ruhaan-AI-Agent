# 🔐 Analytics Dashboard - Admin Access

## How to Access Analytics Dashboard

The analytics dashboard is **protected and hidden** from regular users. Only admins can access it.

### 🗝️ Access Methods

#### Method 1: Secret Key Combination
- Press **`Ctrl + Shift + A`** anywhere in the app
- This will open the admin login screen

#### Method 2: Admin Password
- Once the login screen appears, enter the admin password:
- **Password**: `ruhaan_admin_2025`

### 🛡️ Security Features

1. **Hidden Access**: No visible buttons or links to analytics
2. **Password Protection**: Requires admin password to enter
3. **Session Timeout**: Admin sessions expire after 24 hours
4. **Logout Function**: Secure logout button in dashboard
5. **Local Storage**: Auth status stored locally (not sent to server)

### 📊 What's Available

The dashboard provides comprehensive analytics including:

- **Overview**: Total events, users, sessions, DAU
- **Engagement**: Session duration, interaction rates, engagement scores
- **Features**: Usage breakdown by feature (chat, goals, habits, voice)
- **Commands**: Backend command analytics and success rates
- **Recent Activity**: Live feed of user interactions

### 🔄 Usage Instructions

1. **Access**: Use `Ctrl + Shift + A` to open login
2. **Login**: Enter admin password
3. **Navigate**: Use tabs to explore different metrics
4. **Refresh**: Click refresh button for latest data  
5. **Logout**: Use logout button when done

### 🚨 Important Notes

- **Keep Password Secret**: Only share with authorized admins
- **Regular Logout**: Always logout when finished
- **Production**: Change password for production deployment
- **Privacy**: Analytics contain sensitive user data

### 🔧 For Developers

To change the admin password, edit this line in `AdminLogin.jsx`:
```javascript
const ADMIN_PASSWORD = 'your_new_password_here';
```

The analytics data is stored in `analytics_data.jsonl` and can be viewed via:
- GET `/api/analytics/summary` - Basic summary
- GET `/api/analytics/metrics` - Detailed metrics
