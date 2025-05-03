import './App.css';
import Chatbot from "./Components/Chatbot";
import MicRecorder from "./Components/MicRecorder"; 

// uvicorn src.Backend.main:app --reload
//.\venv\Scripts\activate
function App() {
  return (
    <div className="app-container">
      <div className="brand-name">RuhaanAI</div>
      <MicRecorder />
      <Chatbot />
    </div>
  );
}

export default App;