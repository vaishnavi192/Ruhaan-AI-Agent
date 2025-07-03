// Enhanced Analytics utility for tracking Ruhaan metrics
class RuhaanAnalytics {
  constructor() {
    this.userId = this.getUserId();
    this.sessionStart = Date.now();
    this.messageCount = 0;
    this.voiceUsageCount = 0;
    this.featuresUsed = new Set();
  }

  // Session tracking
  trackSessionStart() {
    // Google Analytics event
    if (typeof gtag !== 'undefined') {
      gtag('event', 'session_start', {
        custom_parameter: 'ruhaan_session'
      });
    }
    
    // Track return user patterns
    this.trackReturnUser();
    
    // Start page visibility tracking
    this.visibilityCleanup = this.trackPageVisibility();
    
    // Custom backend tracking
    this.logEvent('session_start', {
      timestamp: Date.now(),
      user_id: this.userId,
      user_frequency: this.getReturnFrequency(),
      session_id: this.getSessionId()
    });
  }

  trackSessionEnd() {
    const duration = (Date.now() - this.sessionStart) / (1000 * 60);
    
    // Track detailed time spent metrics
    this.trackDetailedTimeSpent();
    
    // Cleanup page visibility tracking
    if (this.visibilityCleanup) {
      this.visibilityCleanup();
    }
    
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'session_end', {
        value: Math.round(duration),
        custom_parameter: `${this.messageCount}_messages`
      });
    }
    
    // Custom tracking
    this.logEvent('session_end', {
      duration_minutes: duration,
      total_messages: this.messageCount,
      voice_usage_count: this.voiceUsageCount,
      features_used: Array.from(this.featuresUsed),
      engagement_score: this.calculateEngagementScore(),
      user_id: this.userId
    });
  }

  // Message tracking
  trackMessageSent(type = 'text', messageLength = 0) {
    this.messageCount++;
    
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'message_sent', {
        method: type,
        value: messageLength
      });
    }
    
    // Custom tracking
    this.logEvent('message_sent', {
      type: type,
      message_length: messageLength,
      session_message_count: this.messageCount,
      user_id: this.userId,
      timestamp: Date.now()
    });
  }

  trackAIResponse(responseTime, responseQuality = null) {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'ai_response', {
        value: responseTime,
        custom_parameter: responseQuality || 'unknown'
      });
    }
    
    // Custom tracking
    this.logEvent('ai_response', {
      response_time_ms: responseTime,
      quality_rating: responseQuality,
      user_id: this.userId
    });
  }

  // Voice tracking
  trackVoiceUsage(duration, transcriptionAccuracy = null) {
    this.voiceUsageCount++;
    
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'voice_usage', {
        value: duration,
        custom_parameter: 'voice_interaction'
      });
    }
    
    // Custom tracking
    this.logEvent('voice_used', {
      duration_seconds: duration,
      transcription_accuracy: transcriptionAccuracy,
      session_voice_count: this.voiceUsageCount,
      user_id: this.userId
    });
  }

  // Feature tracking
  trackFeatureUsed(feature) {
    this.featuresUsed.add(feature);
    
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'feature_used', {
        feature_name: feature,
        custom_parameter: 'feature_engagement'
      });
    }
    
    // Custom tracking
    this.logEvent('feature_used', {
      feature: feature,
      first_time_use: !this.hasUsedFeatureBefore(feature),
      session_features_count: this.featuresUsed.size,
      user_id: this.userId
    });
  }

  // Goal & Habit tracking
  trackGoalCreated(goalType, difficulty = null) {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'goal_created', {
        goal_type: goalType,
        value: difficulty || 1
      });
    }
    
    // Custom tracking
    this.logEvent('goal_created', {
      goal_type: goalType,
      difficulty: difficulty,
      user_id: this.userId,
      goals_created_total: this.getGoalsCreatedCount() + 1
    });
  }

  trackGoalCompleted(goalType, timeToComplete = null) {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'goal_completed', {
        goal_type: goalType,
        value: timeToComplete || 1
      });
    }
    
    // Custom tracking
    this.logEvent('goal_completed', {
      goal_type: goalType,
      time_to_complete_days: timeToComplete,
      user_id: this.userId
    });
  }

  trackHabitLogged(habitType, streakLength = 1) {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'habit_logged', {
        habit_type: habitType,
        value: streakLength
      });
    }
    
    // Custom tracking
    this.logEvent('habit_logged', {
      habit_type: habitType,
      streak_length: streakLength,
      user_id: this.userId
    });
  }

  // User satisfaction
  trackUserFeedback(rating, feature = null) {
    // Google Analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'user_feedback', {
        rating: rating,
        feature: feature || 'general'
      });
    }
    
    // Custom tracking
    this.logEvent('user_feedback', {
      rating: rating, // 1-5 scale
      feature: feature,
      user_id: this.userId
    });
  }

  // Helper methods
  getUserId() {
    let userId = localStorage.getItem('ruhaan_user_id');
    if (!userId) {
      userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('ruhaan_user_id', userId);
      
      // Track new user registration
      this.logEvent('new_user_registered', { user_id: userId });
    }
    
    // Track daily and monthly activity
    this.trackUserActivity();
    
    return userId;
  }

  trackUserActivity() {
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const thisMonth = new Date().toISOString().slice(0, 7); // YYYY-MM
    
    // Track daily active user
    const lastActiveDay = localStorage.getItem('ruhaan_last_active_day');
    if (lastActiveDay !== today) {
      localStorage.setItem('ruhaan_last_active_day', today);
      this.logEvent('daily_active_user', {
        user_id: this.userId,
        date: today,
        previous_active_day: lastActiveDay
      });
    }
    
    // Track monthly active user
    const lastActiveMonth = localStorage.getItem('ruhaan_last_active_month');
    if (lastActiveMonth !== thisMonth) {
      localStorage.setItem('ruhaan_last_active_month', thisMonth);
      this.logEvent('monthly_active_user', {
        user_id: this.userId,
        month: thisMonth,
        previous_active_month: lastActiveMonth
      });
    }
  }

  // Enhanced session tracking with detailed time metrics
  trackDetailedTimeSpent() {
    const sessionDuration = (Date.now() - this.sessionStart) / 1000; // seconds
    const timeSpentInteracting = this.calculateInteractionTime();
    
    this.logEvent('time_spent_detailed', {
      user_id: this.userId,
      session_duration_seconds: sessionDuration,
      interaction_time_seconds: timeSpentInteracting.total,
      idle_time_seconds: sessionDuration - timeSpentInteracting.total,
      interaction_events: timeSpentInteracting.events,
      engagement_score: this.calculateEngagementScore(),
      timestamp: Date.now()
    });
  }

  calculateInteractionTime() {
    // Calculate time spent actively interacting (not idle)
    const events = JSON.parse(localStorage.getItem('ruhaan_analytics_events') || '[]');
    const sessionEvents = events.filter(e => 
      e.timestamp >= this.sessionStart && 
      ['message_sent', 'voice_used', 'feature_used'].includes(e.event)
    );
    
    let totalInteractionTime = 0;
    let lastInteractionTime = this.sessionStart;
    
    sessionEvents.forEach(event => {
      const timeSinceLastInteraction = event.timestamp - lastInteractionTime;
      // Count as interaction time if less than 30 seconds between events
      if (timeSinceLastInteraction < 30000) {
        totalInteractionTime += timeSinceLastInteraction;
      }
      lastInteractionTime = event.timestamp;
    });
    
    return {
      total: totalInteractionTime / 1000, // convert to seconds
      events: sessionEvents.length
    };
  }

  calculateEngagementScore() {
    // Calculate engagement score based on multiple factors (0-100)
    let score = 0;
    
    // Message count (max 30 points)
    score += Math.min(this.messageCount * 3, 30);
    
    // Voice usage (max 20 points)
    score += Math.min(this.voiceUsageCount * 5, 20);
    
    // Feature diversity (max 25 points)
    score += Math.min(this.featuresUsed.size * 8, 25);
    
    // Session duration (max 25 points)
    const sessionMinutes = (Date.now() - this.sessionStart) / (1000 * 60);
    score += Math.min(sessionMinutes * 2, 25);
    
    return Math.round(score);
  }

  // Track page visibility for accurate time measurement
  trackPageVisibility() {
    let isVisible = !document.hidden;
    let visibilityStart = Date.now();
    
    const handleVisibilityChange = () => {
      const now = Date.now();
      
      if (document.hidden && isVisible) {
        // Page became hidden
        const visibleDuration = now - visibilityStart;
        this.logEvent('page_visibility', {
          user_id: this.userId,
          visible_duration_seconds: visibleDuration / 1000,
          event_type: 'hidden'
        });
        isVisible = false;
      } else if (!document.hidden && !isVisible) {
        // Page became visible
        visibilityStart = now;
        this.logEvent('page_visibility', {
          user_id: this.userId,
          event_type: 'visible'
        });
        isVisible = true;
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Return cleanup function
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }

  // Track user return patterns
  trackReturnUser() {
    const lastVisit = localStorage.getItem('ruhaan_last_visit');
    const now = Date.now();
    
    if (lastVisit) {
      const daysSinceLastVisit = (now - parseInt(lastVisit)) / (1000 * 60 * 60 * 24);
      
      this.logEvent('return_user', {
        user_id: this.userId,
        days_since_last_visit: daysSinceLastVisit,
        last_visit_timestamp: parseInt(lastVisit),
        return_frequency: this.getReturnFrequency()
      });
    }
    
    localStorage.setItem('ruhaan_last_visit', now.toString());
  }

  getReturnFrequency() {
    const visits = JSON.parse(localStorage.getItem('ruhaan_visit_count') || '0');
    const newVisitCount = visits + 1;
    localStorage.setItem('ruhaan_visit_count', newVisitCount.toString());
    
    if (newVisitCount === 1) return 'first_time';
    if (newVisitCount <= 3) return 'new_user';
    if (newVisitCount <= 10) return 'regular_user';
    return 'power_user';
  }

  hasUsedFeatureBefore(feature) {
    const usedFeatures = JSON.parse(localStorage.getItem('ruhaan_used_features') || '[]');
    return usedFeatures.includes(feature);
  }

  getGoalsCreatedCount() {
    return parseInt(localStorage.getItem('ruhaan_goals_created') || '0');
  }

  logEvent(eventName, data) {
    // Send to your backend analytics endpoint
    fetch('/api/analytics/track', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        event: eventName,
        data: data,
        timestamp: Date.now(),
        session_id: this.getSessionId()
      })
    }).catch(err => console.log('Analytics error:', err));

    // Store locally for offline analysis
    this.storeEventLocally(eventName, data);
  }
  // Get DAU/MAU metrics (for backend analytics dashboard)
  static getActivityMetrics() {
    const events = JSON.parse(localStorage.getItem('ruhaan_analytics_events') || '[]');
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    const thisMonth = now.toISOString().slice(0, 7);
    
    // Count unique users today
    const todayEvents = events.filter(e => {
      const eventDate = new Date(e.timestamp).toISOString().split('T')[0];
      return eventDate === today && e.event === 'daily_active_user';
    });
    
    // Count unique users this month
    const monthEvents = events.filter(e => {
      const eventDate = new Date(e.timestamp).toISOString().slice(0, 7);
      return eventDate === thisMonth && e.event === 'monthly_active_user';
    });
    
    return {
      dailyActiveUsers: todayEvents.length,
      monthlyActiveUsers: monthEvents.length,
      totalEvents: events.length,
      lastActivityDate: events.length > 0 ? new Date(events[events.length - 1].timestamp) : null
    };
  }
  getSessionId() {
    let sessionId = sessionStorage.getItem('ruhaan_session_id');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      sessionStorage.setItem('ruhaan_session_id', sessionId);
    }
    return sessionId;
  }

  storeEventLocally(eventName, data) {
    const events = JSON.parse(localStorage.getItem('ruhaan_analytics_events') || '[]');
    events.push({
      event: eventName,
      data: data,
      timestamp: Date.now()
    });
    
    // Keep only last 100 events to avoid storage issues
    if (events.length > 100) {
      events.splice(0, events.length - 100);
    }
    
    localStorage.setItem('ruhaan_analytics_events', JSON.stringify(events));
  }

  // Get analytics summary for debugging
  getAnalyticsSummary() {
    const interactionTime = this.calculateInteractionTime();
    
    return {
      userId: this.userId,
      sessionDuration: (Date.now() - this.sessionStart) / (1000 * 60),
      interactionTime: interactionTime.total / 60, // minutes
      idleTime: ((Date.now() - this.sessionStart) / 1000 - interactionTime.total) / 60, // minutes
      messageCount: this.messageCount,
      voiceUsageCount: this.voiceUsageCount,
      featuresUsed: Array.from(this.featuresUsed),
      engagementScore: this.calculateEngagementScore(),
      userFrequency: this.getReturnFrequency(),
      localEvents: JSON.parse(localStorage.getItem('ruhaan_analytics_events') || '[]').length,
      lastActiveDay: localStorage.getItem('ruhaan_last_active_day'),
      lastActiveMonth: localStorage.getItem('ruhaan_last_active_month'),
      visitCount: parseInt(localStorage.getItem('ruhaan_visit_count') || '0')
    };
  }

  
}

export default RuhaanAnalytics;
