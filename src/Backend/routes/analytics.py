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
            "retention_metrics": calculate_retention_metrics(events)
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
    """Calculate basic retention metrics"""
    user_sessions = {}
    
    for event in events:
        user_id = event["data"].get("user_id")
        if user_id and event["event"] == "session_start":
            if user_id not in user_sessions:
                user_sessions[user_id] = []
            user_sessions[user_id].append(event["client_timestamp"])
    
    # Calculate return users
    returning_users = len([u for u, sessions in user_sessions.items() if len(sessions) > 1])
    total_users = len(user_sessions)
    
    return {
        "total_users": total_users,
        "returning_users": returning_users,
        "return_rate_percentage": (returning_users / max(total_users, 1)) * 100
    }
