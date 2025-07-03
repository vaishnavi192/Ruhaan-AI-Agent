# Analytics route for tracking custom events
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime

router = APIRouter()

class AnalyticsEvent(BaseModel):
    event: str
    data: Dict[str, Any]
    timestamp: int
    session_id: Optional[str] = None

# Simple file-based storage (upgrade to database later)
ANALYTICS_FILE = "analytics_data.jsonl"

@router.post("/track")
async def track_event(event: AnalyticsEvent):
    """Track a custom analytics event"""
    try:
        # Add server timestamp
        event_data = {
            "event": event.event,
            "data": event.data,
            "client_timestamp": event.timestamp,
            "server_timestamp": int(datetime.now().timestamp() * 1000),
            "session_id": event.session_id
        }
        
        # Append to file (JSONL format)
        with open(ANALYTICS_FILE, "a") as f:
            f.write(json.dumps(event_data) + "\n")
        
        return {"status": "success", "message": "Event tracked"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track event: {str(e)}")

@router.get("/summary")
async def get_analytics_summary():
    """Get basic analytics summary"""
    try:
        if not os.path.exists(ANALYTICS_FILE):
            return {"total_events": 0, "events": []}
        
        events = []
        with open(ANALYTICS_FILE, "r") as f:
            for line in f:
                events.append(json.loads(line.strip()))
        
        # Basic aggregations
        event_counts = {}
        unique_users = set()
        unique_sessions = set()
        
        for event in events:
            event_name = event["event"]
            event_counts[event_name] = event_counts.get(event_name, 0) + 1
            
            if "user_id" in event["data"]:
                unique_users.add(event["data"]["user_id"])
            
            if event.get("session_id"):
                unique_sessions.add(event["session_id"])
        
        return {
            "total_events": len(events),
            "unique_users": len(unique_users),
            "unique_sessions": len(unique_sessions),
            "event_counts": event_counts,
            "latest_events": events[-10:] if events else []  # Last 10 events
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.get("/metrics")
async def get_detailed_metrics():
    """Get detailed product metrics"""
    try:
        if not os.path.exists(ANALYTICS_FILE):
            return {"error": "No analytics data available"}
        
        events = []
        with open(ANALYTICS_FILE, "r") as f:
            for line in f:
                events.append(json.loads(line.strip()))
        
        # Calculate detailed metrics
        metrics = {
            "user_engagement": calculate_user_engagement(events),
            "feature_usage": calculate_feature_usage(events),
            "conversation_metrics": calculate_conversation_metrics(events),
            "command_analytics": calculate_command_analytics(events),
            "retention_metrics": calculate_retention_metrics(events),
            "engagement_metrics": calculate_engagement_metrics(events),
            "dau_mau_trends": calculate_dau_mau_trends(events)
        }
        
        return metrics
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

def calculate_user_engagement(events):
    """Calculate user engagement metrics"""
    session_data = {}
    
    for event in events:
        session_id = event.get("session_id")
        if not session_id:
            continue
            
        if session_id not in session_data:
            session_data[session_id] = {
                "messages": 0,
                "voice_usage": 0,
                "features_used": set(),
                "start_time": None,
                "end_time": None
            }
        
        session = session_data[session_id]
        
        if event["event"] == "session_start":
            session["start_time"] = event["client_timestamp"]
        elif event["event"] == "session_end":
            session["end_time"] = event["client_timestamp"]
        elif event["event"] == "message_sent":
            session["messages"] += 1
        elif event["event"] == "voice_used":
            session["voice_usage"] += 1
        elif event["event"] == "feature_used":
            session["features_used"].add(event["data"].get("feature"))
    
    # Calculate averages
    total_sessions = len(session_data)
    if total_sessions == 0:
        return {"avg_messages_per_session": 0, "avg_session_duration": 0}
    
    total_messages = sum(s["messages"] for s in session_data.values())
    total_voice = sum(s["voice_usage"] for s in session_data.values())
    
    # Calculate session durations
    durations = []
    for session in session_data.values():
        if session["start_time"] and session["end_time"]:
            duration = (session["end_time"] - session["start_time"]) / (1000 * 60)  # minutes
            durations.append(duration)
    
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    return {
        "total_sessions": total_sessions,
        "avg_messages_per_session": total_messages / total_sessions,
        "avg_voice_usage_per_session": total_voice / total_sessions,
        "avg_session_duration_minutes": avg_duration,
        "voice_usage_percentage": (total_voice / max(total_messages, 1)) * 100
    }

def calculate_feature_usage(events):
    """Calculate feature usage metrics"""
    feature_events = [e for e in events if e["event"] == "feature_used"]
    
    feature_counts = {}
    for event in feature_events:
        feature = event["data"].get("feature")
        if feature:
            feature_counts[feature] = feature_counts.get(feature, 0) + 1
    
    total_feature_usage = sum(feature_counts.values())
    
    return {
        "feature_counts": feature_counts,
        "total_feature_usage": total_feature_usage,
        "most_popular_feature": max(feature_counts, key=feature_counts.get) if feature_counts else None
    }

def calculate_conversation_metrics(events):
    """Calculate conversation quality metrics"""
    message_events = [e for e in events if e["event"] == "message_sent"]
    
    total_messages = len(message_events)
    text_messages = len([e for e in message_events if e["data"].get("type") == "text"])
    voice_messages = len([e for e in message_events if e["data"].get("type") == "voice"])
    
    return {
        "total_messages": total_messages,
        "text_messages": text_messages,
        "voice_messages": voice_messages,
        "voice_percentage": (voice_messages / max(total_messages, 1)) * 100
    }

def calculate_retention_metrics(events):
    """Calculate comprehensive retention and activity metrics"""
    # Daily Active Users
    dau_events = [e for e in events if e["event"] == "daily_active_user"]
    daily_users = {}
    for event in dau_events:
        date = event["data"].get("date")
        user_id = event["data"].get("user_id")
        if date and user_id:
            if date not in daily_users:
                daily_users[date] = set()
            daily_users[date].add(user_id)
    
    # Monthly Active Users
    mau_events = [e for e in events if e["event"] == "monthly_active_user"]
    monthly_users = {}
    for event in mau_events:
        month = event["data"].get("month")
        user_id = event["data"].get("user_id")
        if month and user_id:
            if month not in monthly_users:
                monthly_users[month] = set()
            monthly_users[month].add(user_id)
    
    # Calculate return users and frequency
    return_events = [e for e in events if e["event"] == "return_user"]
    user_frequencies = {}
    for event in return_events:
        user_id = event["data"].get("user_id")
        frequency = event["data"].get("return_frequency")
        if user_id and frequency:
            user_frequencies[user_id] = frequency
    
    # Session data for stickiness
    session_events = [e for e in events if e["event"] == "session_start"]
    user_sessions = {}
    for event in session_events:
        user_id = event["data"].get("user_id")
        if user_id:
            if user_id not in user_sessions:
                user_sessions[user_id] = []
            user_sessions[user_id].append(event["client_timestamp"])
    
    # Calculate current period metrics
    from datetime import datetime, timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    this_month = datetime.now().strftime('%Y-%m')
    
    current_dau = len(daily_users.get(today, set()))
    current_mau = len(monthly_users.get(this_month, set()))
    
    # Calculate average metrics over last 7 days
    recent_dates = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        recent_dates.append(date)
    
    avg_dau_7days = sum(len(daily_users.get(date, set())) for date in recent_dates) / 7
    
    # User frequency distribution
    frequency_counts = {}
    for freq in user_frequencies.values():
        frequency_counts[freq] = frequency_counts.get(freq, 0) + 1
    
    return {
        "current_dau": current_dau,
        "current_mau": current_mau,
        "avg_dau_7days": round(avg_dau_7days, 1),
        "total_users": len(user_sessions),
        "returning_users": len([u for u, sessions in user_sessions.items() if len(sessions) > 1]),
        "return_rate_percentage": (len([u for u, sessions in user_sessions.items() if len(sessions) > 1]) / max(len(user_sessions), 1)) * 100,
        "user_frequency_distribution": frequency_counts,
        "daily_active_users_by_date": {date: len(users) for date, users in daily_users.items()},
        "monthly_active_users_by_month": {month: len(users) for month, users in monthly_users.items()}
    }

def calculate_engagement_metrics(events):
    """Calculate detailed engagement and time spent metrics"""
    time_events = [e for e in events if e["event"] == "time_spent_detailed"]
    session_events = [e for e in events if e["event"] == "session_end"]
    
    if not time_events and not session_events:
        return {"error": "No engagement data available"}
    
    # Time spent metrics
    total_session_time = 0
    total_interaction_time = 0
    engagement_scores = []
    
    for event in time_events:
        data = event["data"]
        total_session_time += data.get("session_duration_seconds", 0)
        total_interaction_time += data.get("interaction_time_seconds", 0)
    
    for event in session_events:
        score = event["data"].get("engagement_score")
        if score is not None:
            engagement_scores.append(score)
    
    # Page visibility metrics
    visibility_events = [e for e in events if e["event"] == "page_visibility"]
    total_visible_time = sum(
        e["data"].get("visible_duration_seconds", 0) 
        for e in visibility_events 
        if e["data"].get("event_type") == "hidden"
    )
    
    sessions_count = len(session_events)
    avg_session_duration = (total_session_time / sessions_count) if sessions_count > 0 else 0
    avg_interaction_time = (total_interaction_time / sessions_count) if sessions_count > 0 else 0
    avg_engagement_score = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
    
    return {
        "total_sessions": sessions_count,
        "avg_session_duration_minutes": round(avg_session_duration / 60, 2),
        "avg_interaction_time_minutes": round(avg_interaction_time / 60, 2),
        "avg_idle_time_minutes": round((avg_session_duration - avg_interaction_time) / 60, 2),
        "interaction_rate_percentage": round((avg_interaction_time / max(avg_session_duration, 1)) * 100, 1),
        "avg_engagement_score": round(avg_engagement_score, 1),
        "total_visible_time_hours": round(total_visible_time / 3600, 2),
        "engagement_score_distribution": {
            "high (80-100)": len([s for s in engagement_scores if s >= 80]),
            "medium (50-79)": len([s for s in engagement_scores if 50 <= s < 80]),
            "low (0-49)": len([s for s in engagement_scores if s < 50])
        }
    }

def calculate_dau_mau_trends(events):
    """Calculate DAU/MAU trends over time"""
    from datetime import datetime, timedelta
    
    dau_events = [e for e in events if e["event"] == "daily_active_user"]
    
    # Group by date
    daily_counts = {}
    for event in dau_events:
        date = event["data"].get("date")
        if date:
            daily_counts[date] = daily_counts.get(date, 0) + 1
    
    # Calculate trends for last 30 days
    trends = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        count = daily_counts.get(date, 0)
        trends.append({
            "date": date,
            "dau": count
        })
    
    trends.reverse()  # Oldest first
    
    # Calculate growth metrics
    current_week_avg = sum(t["dau"] for t in trends[-7:]) / 7
    previous_week_avg = sum(t["dau"] for t in trends[-14:-7]) / 7
    
    growth_rate = 0
    if previous_week_avg > 0:
        growth_rate = ((current_week_avg - previous_week_avg) / previous_week_avg) * 100
    
    return {
        "daily_trends": trends,
        "current_week_avg_dau": round(current_week_avg, 1),
        "previous_week_avg_dau": round(previous_week_avg, 1),
        "week_over_week_growth": round(growth_rate, 1),
        "peak_dau": max((t["dau"] for t in trends), default=0),
        "total_unique_users_30days": len(set(e["data"].get("user_id") for e in dau_events if e["data"].get("date") in [t["date"] for t in trends]))
    }

def calculate_command_analytics(events):
    """Calculate command execution analytics"""
    command_events = [e for e in events if e["event"] == "command_executed"]
    
    if not command_events:
        return {"total_commands": 0, "command_types": {}, "success_rate": 0}
    
    # Count by command type
    command_types = {}
    successful_commands = 0
    failed_commands = 0
    
    for event in command_events:
        data = event["data"]
        cmd_type = data.get("command_type", "unknown")
        success = data.get("success", True)
        
        # Count by type
        command_types[cmd_type] = command_types.get(cmd_type, 0) + 1
        
        # Count success/failure
        if success:
            successful_commands += 1
        else:
            failed_commands += 1
    
    total_commands = len(command_events)
    success_rate = (successful_commands / total_commands) * 100 if total_commands > 0 else 0
    
    # Most popular commands
    most_popular = max(command_types, key=command_types.get) if command_types else None
    
    return {
        "total_commands": total_commands,
        "command_types": command_types,
        "successful_commands": successful_commands,
        "failed_commands": failed_commands,
        "success_rate_percentage": round(success_rate, 1),
        "most_popular_command_type": most_popular,
        "command_distribution": {
            cmd_type: {
                "count": count,
                "percentage": round((count / total_commands) * 100, 1)
            }
            for cmd_type, count in command_types.items()
        }
    }
