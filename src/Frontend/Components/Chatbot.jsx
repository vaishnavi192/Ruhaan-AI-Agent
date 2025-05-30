import React, { useState, useRef, useEffect } from "react";
import ChatInput from "./ChatInput";
import { processTextQuery, textToSpeech } from "./api";

const Chatbot = ({ messages, setMessages }) => {
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [expandedSections, setExpandedSections] = useState({});

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleSendMessage = async (messageText) => {
    const userMessage = { text: messageText, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
  
    try {
      const response = await processTextQuery(messageText);
      console.log("Backend Response:", response); // Debug log
      
      if (response.status === "success") {
        const botReply = response.data.response;
        console.log("Bot Reply:", botReply); // Debug log
        
        // Check if response has error
        if (botReply.error) {
          console.error("Error in response:", botReply.error);
          setMessages((prev) => [
            ...prev,
            { text: "Sorry, I'm having trouble processing that. Please try again.", sender: "bot" },
          ]);
          return;
        }

        setMessages((prevMessages) => [
          ...prevMessages,
          { text: botReply, sender: "bot", structured: true },
        ]);

        // Get voice response from ElevenLabs
        try {
          const audioBlob = await textToSpeech(JSON.stringify(botReply));
          if (audioBlob) {
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            audio.play();
          }
        } catch (error) {
          console.error("Error playing audio:", error);
        }
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { text: "Sorry, I'm having trouble responding.", sender: "bot" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderStructuredMessage = (message) => {
    if (!message.structured) return message.text;
    
    console.log("Rendering structured message:", message.text); // Debug log

    const sections = [
      { key: "psychological", title: "Psychological Analysis", color: "#4a90e2" },
      { key: "philosophical", title: "Philosophical Perspective", color: "#50c878" },
      { key: "autobiographical", title: "Autobiographical Insight", color: "#e67e22" },
      { key: "logical", title: "Logical Framework", color: "#9b59b6" }
    ];

    return (
      <div className="structured-response">
        {sections.map(section => {
          const content = message.text[section.key];
          console.log(`Rendering section ${section.key}:`, content); // Debug log
          
          if (!content) {
            console.warn(`Missing content for section ${section.key}`);
            return null;
          }

          return (
            <div key={section.key} className="response-box" style={{ borderColor: section.color }}>
              <h3 style={{ color: section.color }}>{section.title}</h3>
              <p>{content.analysis || content.perspective || content.story || content.framework}</p>
              {content.key_points && content.key_points.length > 0 && (
                <ul>
                  {content.key_points.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="chatbot-interface">
      {messages.length === 0 && (
        <div className="initial-text">
          <div className="initial-text-main">Hey There! I am Ruhh!</div>
          <div className="initial-text-sub">What's holding you back today?</div>
        </div>
      )}
    
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={`${msg.sender}-${index}`} className={`message ${msg.sender}`}>
            {msg.structured ? renderStructuredMessage(msg) : msg.text}
          </div>
        ))}

        {isLoading && (
          <div className="message bot typing">
            <span className="typing-dots">•••</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} messages={messages} />
    </div>
  );
};

export default Chatbot;
    
