import './App.css';
import { useState, useEffect, useRef } from 'react';
import Chatbot from "./Components/Chatbot";
import MicRecorder from "./Components/MicRecorder";
import GoalBreakdown from "./Components/GoalBreakdown";
import HabitLogger from "./Components/HabitLogger";
import { requestNotificationPermission, scheduleReminderNotification } from "./utils/reminderNotifications";
import RuhaanAnalytics from "./utils/analytics";

function App() {
  const [messages, setMessages] = useState([]);
  const [currentView, setCurrentView] = useState('chat'); // 'chat', 'goals', 'habits'
  const [isRecording, setIsRecording] = useState(false);
  const analytics = useRef(new RuhaanAnalytics()).current;

  const handleLogoClick = () => {
    // Toggle recording state and pass to MicRecorder
    setIsRecording(!isRecording);
  };

  useEffect(() => {
    requestNotificationPermission();
    
    // Track session start
    analytics.trackSessionStart();
    
    // Track session end on page unload
    const handleBeforeUnload = () => {
      analytics.trackSessionEnd();
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      analytics.trackSessionEnd();
    };
  }, [analytics]);

  // Listen for new reminder messages and schedule notifications
  useEffect(() => {
    if (messages.length > 0) {
      const lastMsg = messages[messages.length - 1];
      // If the last message is a reminder response from backend
      if (lastMsg && lastMsg.reply && lastMsg.reply.reminder_time) {
        scheduleReminderNotification(lastMsg.reply);
      }
      // If using /execute endpoint, adapt to lastMsg.response.reminder_time
      if (lastMsg && lastMsg.response && lastMsg.response.reminder_time) {
        scheduleReminderNotification(lastMsg.response);
      }
    }
  }, [messages]);

  const renderCurrentView = () => {
    switch (currentView) {
      case 'goals':
        // Track feature usage
        analytics.trackFeatureUsed('goals');
        return (
          <>
            <div className="navigation-bar">
              <button 
                className="nav-btn goals-btn"
                onClick={() => setCurrentView('goals')}
              >
                🎯 Goals
              </button>
              <button 
                className="nav-btn habits-btn"
                onClick={() => setCurrentView('habits')}
              >
                📊 Habits
              </button>
            </div>
            <GoalBreakdown onBack={() => setCurrentView('chat')} />
          </>
        );
      case 'habits':
        // Track feature usage
        analytics.trackFeatureUsed('habits');
        return (
          <>
            <div className="navigation-bar">
              <button 
                className="nav-btn goals-btn"
                onClick={() => setCurrentView('goals')}
              >
                🎯 Goals
              </button>
              <button 
                className="nav-btn habits-btn"
                onClick={() => setCurrentView('habits')}
              >
                📊 Habits
              </button>
            </div>
            <HabitLogger onBack={() => setCurrentView('chat')} />
          </>
        );
      default:
        return (
          <>
            <div className="navigation-bar">
              <button 
                className="nav-btn goals-btn"
                onClick={() => setCurrentView('goals')}
              >
                🎯 Goals
              </button>
              <button 
                className="nav-btn habits-btn"
                onClick={() => setCurrentView('habits')}
              >
                📊 Habits
              </button>
            </div>
            <MicRecorder 
              setMessages={setMessages} 
              isRecording={isRecording}
              setIsRecording={setIsRecording}
              analytics={analytics}
            />
            <Chatbot 
              messages={messages} 
              setMessages={setMessages}
              analytics={analytics}
            />
          </>
        );
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="brand-name">
          RuhaanAI
        </div>
        <div className="voice-listener" onClick={handleLogoClick}>
          <div className="logo-container">
            <img 
              src="/ruhhhh.png" 
              alt="AI Avatar" 
              className={`mic-image ${isRecording ? 'recording' : ''}`}
            />
          </div>
        </div>
      </div>
      
      {/* Main Content Area */}
      <div className="main-content">
        {renderCurrentView()}
      </div>
      
      <a 
        href="https://tally.so/r/nPyo5V" 
        target="_blank" 
        rel="noopener noreferrer" 
        className="waitlist-button"
      >
        See Instructions to use Ruhaan
      </a>
    </div>
  );
}

export default App;