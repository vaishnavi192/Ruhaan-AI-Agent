import React, { useState } from 'react';
import './App.css';
// uvicorn src.Backend.main:app --reload
function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isChatStarted, setIsChatStarted] = useState(false);

  const handleSendMessage = () => {
    if (inputText.trim()) {
      setMessages([...messages, { text: inputText, sender: 'user' }]);
      setInputText('');
      setIsChatStarted(true); // Move chat input to bottom after first message
      // Simulate a bot response
      setTimeout(() => {
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: 'Hello! How can I help you?', sender: 'bot' },
        ]);
      }, 1000);
    }
  };

  return (
    <div className="app-container">
      {/* Brand Name */}
      <div className="brand-name">RuhaanAI</div>

      {/* Left Side: Voice Listener */}
      <div className="voice-listener">
        <div className="voice-circle">🎤</div>
      </div>

      {/* Right Side: Chatbot Interface */}
      <div className="chatbot-interface">
        {/* Initial Text */}
        {!isChatStarted && (
          <div className="initial-text">
            <div className="initial-text-main">Hi! I am Ruhh!</div>
            <div className="initial-text-sub">How are you feeling today?</div>
          </div>
          
        )}

        {/* Chat Messages */}
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.sender === 'user' ? 'user' : 'bot'}`}
            >
              {message.text}
            </div>
          ))}
        </div>

        {/* Chat Input Box */}
        <div className={`chat-input ${isChatStarted ? 'chat-input-bottom' : ''}`}>
          <input
            type="text"
            placeholder="Type a message..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyUp={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <button onClick={handleSendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}

export default App;