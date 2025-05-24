import './App.css';
import { useState } from 'react';
import Chatbot from "./Components/Chatbot";
import MicRecorder from "./Components/MicRecorder"; 
// uvicorn src.Backend.main:app --reload
//.\venv\Scripts\activate
function App() {
  const [messages, setMessages] = useState([]);

  return (
    <div className="app-container">
      <div className="brand-name">RuhaanAI</div>
      <MicRecorder setMessages={setMessages} />
      <Chatbot messages={messages} setMessages={setMessages} />
      <a 
        href="https://tally.so/r/nPyo5V" 
        target="_blank" 
        rel="noopener noreferrer" 
        className="waitlist-button"
      >
        Get Early Access to Ruhaan AI — Join the Waitlist!
      </a>
    </div>
  );
}

export default App;