import React, { useState } from "react";
import ChatInput from "./ChatInput";

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [isChatStarted, setIsChatStarted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

const handleSendMessage = async (text) => {
    if (text.trim()) {
      setMessages((prevMessages) => [...prevMessages, { text: "...", sender: "bot" }]);
      setIsChatStarted(true);
      setIsLoading(true);

      try {
        // Send the user message to the backend (FastAPI)
        const response = await fetch("http://127.0.0.1:8000/process/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: text }),
          mode: "no-cors",
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
        const data = await response.json();
        console.log("Backend response:", data);
        // Ensure the response is valid
        const botReply = data.chat_response || "Sorry, I couldn't get a response.";
        console.log("Bot Response:", botReply);
        // Add the bot's response to the chat
        setMessages((prevMessages) => [
          ...prevMessages.slice(0, -1),
          { text: botReply, sender: "bot" },
        ]);
      } catch (error) {
        console.error("Error:", error);
        setMessages((prev) => [
          ...prev,
          { text: "Sorry, I'm having trouble responding.", sender: "bot" },
        ]); 
        console.error("API Error:", error);
    } finally {
      setIsLoading(false);
      }
    }
    };
    return (
        <div className="chatbot-interface">
          {!isChatStarted && (
            <div className="initial-text">
              <div className="initial-text-main">Hi! I am Ruhh!</div>
              <div className="initial-text-sub">How are you feeling today?</div>
            </div>
          )}
    
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <div
                key={`${msg.sender}-${index}`}
                className={`message ${msg.sender} ${msg.text === "..." ? "typing" : ""}`}
              >
                {msg.text === "..." ? (
                  <span className="typing-dots">•••</span>
                ) : (
                  msg.text
                )}
              </div>
            ))}
    
            {isLoading && (
              <div className="message bot typing">
                <span className="typing-dots">•••</span>
              </div>
            )}
          </div>
    
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
        </div>
      );
    };
    
    export default Chatbot;
    
