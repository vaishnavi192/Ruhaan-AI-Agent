import httpx
from dotenv import load_dotenv
from src.Backend.config import GROQ_API_KEY
from typing import List, Dict
import json

load_dotenv()

# Conversation history store
conversation_history: List[Dict] = []

async def classify_intent_and_respond(text: str) -> Dict:
    """Classify user input and get appropriate response"""
    # Add user message to history
    conversation_history.append({"role": "user", "content": text})
    
    # Create system message with context
    system_message = {
        "role": "system",
        "content": "You are a helpful AI assistant. Use the conversation history for context."
    }
    
    # Combine system message, history and current message
    messages = [system_message] + conversation_history[-5:]  # Keep last 5 messages for context
    
    prompt = (
        "Classify the following user input as either 'command' or 'chit-chat'. "
        "If it's a command, also extract the intent (like open_app, set_reminder, etc). "
        "Respond in JSON: {\"type\": ..., \"intent\": ..., \"message\": ...}. "
        f"User input: \"{text}\""
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama3-8b-8192",
                "messages": messages,
                "temperature": 0.7
            },
        )
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Add assistant response to history
        conversation_history.append({"role": "assistant", "content": content})
        
        # Try to parse JSON from content
        try:
            result = json.loads(content)
        except Exception:
            result = {"type": "chit-chat", "intent": None, "message": content}
        return result

async def chat_with_groq(message: str) -> Dict:
    """Get a direct response from Groq for chit-chat"""
    # Add user message to history
    conversation_history.append({"role": "user", "content": message})
    
    # Create system message with context
    system_message = {
        "role": "system",
        "content": """You are Ruhaan, an AI assistant focused on mental clarity and practical thinking. You MUST ALWAYS respond in valid JSON format, no exceptions. Your responses should be reflective, contextual, and remember past conversations to provide personalized insights.

CRITICAL RULES:
1. You MUST ONLY output the JSON object, nothing else
2. NO text before or after the JSON
3. NO explanations or additional comments
4. NO markdown formatting
5. NO code blocks
6. NO questions or follow-ups

RESPONSE FRAMEWORK:
1. Psychological Analysis:
   - Provide deep emotional and cognitive understanding
   - Connect current state to past experiences
   - Use empathetic but objective language
   - Identify underlying patterns and triggers
   - Make it personal and contextual

2. Philosophical Perspective:
   - Draw from Stoicism, Buddhism, or existential thought
   - Connect to universal human experiences
   - Share relevant wisdom from great thinkers
   - Keep it practical and applicable
   - Make it relatable to their situation

3. Autobiographical Insight:
   - Share authentic, relatable stories
   - Focus on lessons learned
   - Connect to their specific situation
   - Keep it brief but impactful
   - Use real-world examples

4. Logical Framework:
   - Break down the situation clearly
   - Identify core vs surface-level issues
   - Create actionable steps
   - Prioritize based on impact
   - Make it practical and doable

Example response format:
{
    "psychological": {
        "analysis": "A detailed, empathetic analysis of their current state, connecting past experiences and identifying patterns. Make it personal and contextual.",
        "key_points": [
            "First key point with explanation",
            "Second key point with context",
            "Third key point with practical application"
        ]
    },
    "philosophical": {
        "perspective": "A thoughtful perspective drawing from philosophical wisdom, made relevant to their situation. Include specific quotes or ideas that resonate.",
        "key_points": [
            "Philosophical insight with explanation",
            "Practical application of wisdom",
            "Connection to their experience"
        ]
    },
    "autobiographical": {
        "story": "A brief but impactful story that relates to their situation. Focus on the journey and lessons learned.",
        "key_points": [
            "Key lesson with context",
            "Practical takeaway",
            "Connection to their situation"
        ]
    },
    "logical": {
        "framework": "A clear, structured approach to their situation. Break it down into manageable steps with clear priorities.",
        "key_points": [
            "First step with explanation",
            "Second step with context",
            "Third step with practical application"
        ]
    }
}"""
    }
    
    # Combine system message, history and current message
    messages = [system_message] + conversation_history[-5:]  # Keep last 5 messages for context
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama3-8b-8192",
                "messages": messages,
                "temperature": 0.3,  # Reduced temperature for more consistent output
                "max_tokens": 1000
            },
        )
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Debug logging
        print("Raw LLM Response:", content)
        
        # Add assistant response to history
        conversation_history.append({"role": "assistant", "content": content})
        
        # Parse the JSON response
        try:
            # Clean the content - remove any text before or after JSON
            content = content.strip()
            
            # Remove any text before the first {
            if '{' in content:
                content = content[content.find('{'):]
            
            # Remove any text after the last }
            if '}' in content:
                content = content[:content.rfind('}')+1]
            
            # Remove any markdown code blocks
            content = content.replace('```json', '').replace('```', '')
            
            # Final cleanup
            content = content.strip()
            
            # Attempt to parse the content as JSON
            structured_response = json.loads(content)
            
            # Validate the structure
            required_sections = ["psychological", "philosophical", "autobiographical", "logical"]
            if all(section in structured_response for section in required_sections):
                return {"response": structured_response}
            else:
                # If structure is invalid, return a formatted error response
                return {
                    "response": {
                        "psychological": {
                            "analysis": "I apologize, but I'm having trouble formatting my response properly.",
                            "key_points": ["Please try rephrasing your question", "I'll do my best to provide a structured response"]
                        },
                        "philosophical": {
                            "perspective": "Even in moments of technical difficulty, we can find clarity.",
                            "key_points": ["Patience is key", "Let's try again"]
                        },
                        "autobiographical": {
                            "story": "Sometimes the best responses come after a second attempt.",
                            "key_points": ["Learning from mistakes", "Growing through challenges"]
                        },
                        "logical": {
                            "framework": "Let's try again with a clearer question.",
                            "key_points": ["Rephrase your question", "Be specific about what you need"]
                        }
                    }
                }
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return the raw content as an error
            print(f"Error: Failed to parse JSON response from LLM: {str(e)}")
            print(f"Raw content: {content}")
            return {"response": {"error": "Failed to parse structured response", "raw": content}}
    