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
    
    // Custom backend tracking
    this.logEvent('session_start', {
      timestamp: Date.now(),
      user_id: this.userId
    });
  }

  trackSessionEnd() {
    const duration = (Date.now() - this.sessionStart) / (1000 * 60);
    
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
    return userId;
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
    return {
      userId: this.userId,
      sessionDuration: (Date.now() - this.sessionStart) / (1000 * 60),
      messageCount: this.messageCount,
      voiceUsageCount: this.voiceUsageCount,
      featuresUsed: Array.from(this.featuresUsed),
      localEvents: JSON.parse(localStorage.getItem('ruhaan_analytics_events') || '[]').length
    };
  }
}

export default RuhaanAnalytics;
