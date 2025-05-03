import React, { useState } from "react";
import { processTextQuery } from "./api";

const ChatInput = ({ onSendMessage, isLoading }) => {
    const [inputText, setInputText] = useState("");
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
      <div className="chat-input">
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
          {isLoading ? "..." : "Send"}
        </button>
      </div>
    );
  };
  
  export default ChatInput;

