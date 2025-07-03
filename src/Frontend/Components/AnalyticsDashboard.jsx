import React, { useState, useEffect } from 'react';
import './AnalyticsDashboard.css';

const AnalyticsDashboard = ({ onBack, onLogout }) => {
  const [metrics, setMetrics] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      
      const [metricsResponse, summaryResponse] = await Promise.all([
        fetch('http://localhost:8000/api/analytics/metrics'),
        fetch('http://localhost:8000/api/analytics/summary')
      ]);

      if (metricsResponse.ok && summaryResponse.ok) {
        const metricsData = await metricsResponse.json();
        const summaryData = await summaryResponse.json();
        
        setMetrics(metricsData);
        setSummary(summaryData);
      } else {
        console.error('Failed to fetch analytics data');
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (!num && num !== 0) return 'N/A';
    return typeof num === 'number' ? num.toLocaleString() : num;
  };

  const formatPercentage = (num) => {
    if (!num && num !== 0) return '0%';
    return `${Math.round(num)}%`;
  };

  const renderMetricCard = (title, value, subtitle = '', icon = '📊') => (
    <div className="metric-card">
      <div className="metric-icon">{icon}</div>
      <div className="metric-content">
        <h3 className="metric-title">{title}</h3>
        <div className="metric-value">{formatNumber(value)}</div>
        {subtitle && <div className="metric-subtitle">{subtitle}</div>}
      </div>
    </div>
  );

  const renderProgressBar = (label, current, total, color = '#4CAF50') => (
    <div className="progress-item">
      <div className="progress-label">
        <span>{label}</span>
        <span>{current}/{total}</span>
      </div>
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ 
            width: `${total > 0 ? (current / total) * 100 : 0}%`,
            backgroundColor: color 
          }}
        />
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="analytics-dashboard">
        <div className="dashboard-header">
          <button onClick={onBack} className="back-button">←</button>
          <h1>📊 Analytics Dashboard</h1>
        </div>
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!metrics || !summary) {
    return (
      <div className="analytics-dashboard">
        <div className="dashboard-header">
          <button onClick={onBack} className="back-button">←</button>
          <h1>📊 Analytics Dashboard</h1>
        </div>
        <div className="error-state">
          <p>⚠️ No analytics data available. Start using the app to generate data!</p>
          <button onClick={fetchAnalytics} className="retry-button">
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <button onClick={onBack} className="back-button">←</button>
        <h1>📊 Analytics Dashboard</h1>
        <div className="header-actions">
          <button onClick={fetchAnalytics} className="refresh-button">
            🔄 Refresh
          </button>
          {onLogout && (
            <button onClick={onLogout} className="logout-button">
              🚪 Logout
            </button>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📈 Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'engagement' ? 'active' : ''}`}
          onClick={() => setActiveTab('engagement')}
        >
          🔥 Engagement
        </button>
        <button 
          className={`tab-button ${activeTab === 'features' ? 'active' : ''}`}
          onClick={() => setActiveTab('features')}
        >
          🎯 Features
        </button>
        <button 
          className={`tab-button ${activeTab === 'commands' ? 'active' : ''}`}
          onClick={() => setActiveTab('commands')}
        >
          ⚡ Commands
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="tab-content">
          <div className="metrics-grid">
            {renderMetricCard('Total Events', summary.total_events, 'All tracked events', '📈')}
            {renderMetricCard('Unique Users', summary.unique_users, 'Different users', '👥')}
            {renderMetricCard('Sessions', summary.unique_sessions, 'Total sessions', '🔄')}
            {renderMetricCard('DAU', metrics.retention_metrics?.current_dau || 0, 'Daily Active Users', '📅')}
          </div>

          <div className="chart-section">
            <h2>📊 User Activity</h2>
            <div className="metrics-grid">
              {renderMetricCard(
                'Avg Session Duration', 
                `${metrics.user_engagement?.avg_session_duration_minutes?.toFixed(1) || 0} min`,
                'Time per session',
                '⏱️'
              )}
              {renderMetricCard(
                'Messages per Session',
                metrics.user_engagement?.avg_messages_per_session?.toFixed(1) || 0,
                'Average messages',
                '💬'
              )}
              {renderMetricCard(
                'Return Rate',
                formatPercentage(metrics.retention_metrics?.return_rate_percentage || 0),
                'Users who return',
                '🔄'
              )}
            </div>
          </div>
        </div>
      )}

      {/* Engagement Tab */}
      {activeTab === 'engagement' && (
        <div className="tab-content">
          <div className="metrics-grid">
            {renderMetricCard(
              'Avg Engagement Score',
              metrics.engagement_metrics?.avg_engagement_score?.toFixed(1) || 0,
              'Out of 100',
              '🔥'
            )}
            {renderMetricCard(
              'Interaction Rate',
              formatPercentage(metrics.engagement_metrics?.interaction_rate_percentage || 0),
              'Active vs idle time',
              '🎯'
            )}
            {renderMetricCard(
              'Voice Usage',
              formatPercentage(metrics.user_engagement?.voice_usage_percentage || 0),
              'Voice vs text',
              '🎤'
            )}
          </div>

          <div className="engagement-breakdown">
            <h2>🎯 Engagement Distribution</h2>
            <div className="engagement-bars">
              {metrics.engagement_metrics?.engagement_score_distribution && (
                <>
                  {renderProgressBar(
                    'High Engagement (80-100)',
                    metrics.engagement_metrics.engagement_score_distribution['high (80-100)'] || 0,
                    metrics.engagement_metrics.total_sessions || 1,
                    '#4CAF50'
                  )}
                  {renderProgressBar(
                    'Medium Engagement (50-79)',
                    metrics.engagement_metrics.engagement_score_distribution['medium (50-79)'] || 0,
                    metrics.engagement_metrics.total_sessions || 1,
                    '#FF9800'
                  )}
                  {renderProgressBar(
                    'Low Engagement (0-49)',
                    metrics.engagement_metrics.engagement_score_distribution['low (0-49)'] || 0,
                    metrics.engagement_metrics.total_sessions || 1,
                    '#F44336'
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Features Tab */}
      {activeTab === 'features' && (
        <div className="tab-content">
          <div className="metrics-grid">
            {renderMetricCard(
              'Total Feature Usage',
              metrics.feature_usage?.total_feature_usage || 0,
              'Feature interactions',
              '🎯'
            )}
            {renderMetricCard(
              'Most Popular',
              metrics.feature_usage?.most_popular_feature || 'None',
              'Top feature',
              '🏆'
            )}
          </div>

          <div className="feature-breakdown">
            <h2>📊 Feature Usage Breakdown</h2>
            <div className="feature-bars">
              {metrics.feature_usage?.feature_counts && Object.entries(metrics.feature_usage.feature_counts).map(([feature, count]) => (
                <div key={feature} className="feature-item">
                  <div className="feature-info">
                    <span className="feature-name">
                      {feature === 'chat' ? '💬 Chat' :
                       feature === 'goals' ? '🎯 Goals' :
                       feature === 'habits' ? '📊 Habits' :
                       feature === 'voice' ? '🎤 Voice' : `🔧 ${feature}`}
                    </span>
                    <span className="feature-count">{count}</span>
                  </div>
                  <div className="feature-bar">
                    <div 
                      className="feature-fill"
                      style={{ 
                        width: `${(count / Math.max(...Object.values(metrics.feature_usage.feature_counts))) * 100}%`
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Commands Tab */}
      {activeTab === 'commands' && (
        <div className="tab-content">
          <div className="metrics-grid">
            {renderMetricCard(
              'Total Commands',
              metrics.command_analytics?.total_commands || 0,
              'Commands executed',
              '⚡'
            )}
            {renderMetricCard(
              'Success Rate',
              formatPercentage(metrics.command_analytics?.success_rate_percentage || 0),
              'Successful commands',
              '✅'
            )}
            {renderMetricCard(
              'Most Popular',
              metrics.command_analytics?.most_popular_command_type || 'None',
              'Top command type',
              '🏆'
            )}
          </div>

          <div className="command-breakdown">
            <h2>⚡ Command Types</h2>
            <div className="command-bars">
              {metrics.command_analytics?.command_distribution && Object.entries(metrics.command_analytics.command_distribution).map(([cmdType, data]) => (
                <div key={cmdType} className="command-item">
                  <div className="command-info">
                    <span className="command-name">
                      {cmdType === 'reminder' ? '⏰ Reminders' :
                       cmdType === 'goal_breakdown' ? '🎯 Goal Breakdown' :
                       cmdType === 'habit_log' ? '📊 Habit Logging' :
                       cmdType === 'browser' ? '🌐 Browser' :
                       cmdType === 'note' ? '📝 Notes' :
                       cmdType === 'chat' ? '💬 Chat' : `🔧 ${cmdType}`}
                    </span>
                    <span className="command-stats">
                      {data.count} ({data.percentage}%)
                    </span>
                  </div>
                  <div className="command-bar">
                    <div 
                      className="command-fill"
                      style={{ width: `${data.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recent Events */}
      <div className="recent-events">
        <h2>🕒 Recent Activity</h2>
        <div className="events-list">
          {summary.latest_events?.slice(0, 5).map((event, index) => (
            <div key={index} className="event-item">
              <div className="event-icon">
                {event.event === 'session_start' ? '🟢' :
                 event.event === 'message_sent' ? '💬' :
                 event.event === 'voice_used' ? '🎤' :
                 event.event === 'feature_used' ? '🎯' :
                 event.event === 'command_executed' ? '⚡' : '📊'}
              </div>
              <div className="event-details">
                <div className="event-type">{event.event.replace('_', ' ').toUpperCase()}</div>
                <div className="event-time">
                  {new Date(event.client_timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
