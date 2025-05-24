import React, { useState, useEffect } from "react";

const ChatInput = ({ onSendMessage, isLoading, messages }) => {
    const [inputText, setInputText] = useState("");
    const [isInitialPosition, setIsInitialPosition] = useState(true);

    useEffect(() => {
        // If there are any messages, move input to bottom
        if (messages.length > 0) {
            setIsInitialPosition(false);
        }
    }, [messages]);

    const handleSend = () => {
        if (!inputText.trim() || isLoading) return;
        onSendMessage(inputText);
        setInputText("");
    };
    // const handleSend = async () => {
    //   if (!inputText.trim()) return;
      
    //   try {
    //     onSendMessage(inputText);
    //     setInputText("");
    //   } catch (error) {
    //     console.error("Error getting response:", error);
    //   } 
    // };
  
    return (
      <div className={`chat-input ${isInitialPosition ? 'initial-position' : 'bottom-position'}`}>
        <input
          type="text"
          id="chat-input-field"  // Added for accessibility
          name="message"
          placeholder="Type a message..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyUp={(e) => e.key === "Enter" && handleSend()}
          disabled={isLoading}
        />
        <button onClick={handleSend} disabled={isLoading}>
          {isLoading ? "..." : "send"}
        </button>
      </div>
    );
  };
  
  export default ChatInput;

