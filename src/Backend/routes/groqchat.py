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
    
    # --- Simple message handling --- 
    # Convert input to lower case for easier matching
    lower_text = text.lower().strip()
    
    # Define simple greetings or common simple inputs
    simple_greetings = ["hi", "hello", "hey", "namaste", "hii"]
    simple_acknowledgements = ["thank you", "thanks", "ok", "okay", "great"]
    
    # Check if it's a simple greeting or acknowledgement
    if lower_text in simple_greetings:
        # Return a simple predefined response for greetings
        return {"type": "chit-chat", "intent": None, "message": "Hello! How can I help you today?"}
    elif lower_text in simple_acknowledgements:
         # Return a simple predefined response for acknowledgements
         return {"type": "chit-chat", "intent": None, "message": "You're welcome! Anything else?"}
    # Add more simple message checks here if needed

    # --- End Simple message handling ---

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
        "content": """You are Ruhaan, an AI assistant focused on mental clarity and practical thinking. You MUST ALWAYS respond in valid JSON format, no exceptions. Your responses should be reflective, contextual, and remember past conversations to provide personalized insights. Your primary goal is to help the user gain clarity on their thoughts and feelings and provide actionable steps.

CRITICAL RULES:
1. You MUST ONLY output the JSON object, nothing else.
2. NO text before or after the JSON.
3. NO explanations or additional comments outside the JSON.
4. NO markdown formatting.
5. NO code blocks.
6. NO questions or follow-ups within the response.
7. You MUST provide EXACTLY 3 key points for each section, no more and no less.
8. Each key point MUST be detailed, descriptive, provide complete context, and offer actionable insights or practical takeaways (at least 2-3 sentences each).
9. NEVER cut off responses in the middle of a sentence.
10. Make sure each point provides complete context and actionable insights.
11. Keep the main text content for 'analysis', 'perspective', 'story', and 'framework' sections concise and brief, serving as introductions to the key points.
12. Ensure the entire response is highly relevant and directly addresses the user's query from all four perspectives.

RESPONSE FRAMEWORK:
1. Psychological Analysis:
   - Provide a deep, empathetic understanding of the user's emotional and cognitive state related to their query.
   - Connect current state to potential underlying patterns or past experiences, offering insights into *why* they might be feeling/thinking this way.
   - Identify underlying patterns and triggers in their thoughts/feelings.
   - Make it personal and contextual, reflecting their input and conversation history.
   - **Keep this section's main 'analysis' text brief and to the point.**

2. Philosophical Perspective:
   - Draw from relevant philosophical wisdom (like Stoicism, Buddhism, existentialism, etc.) that speaks to the user's situation.
   - Connect to universal human experiences and timeless challenges.
   - Share relevant wisdom from great thinkers or philosophical concepts, explaining how they apply practically.
   - Keep it practical and applicable to modern life.
   - Make it relatable to their specific situation.
   - **Keep this section's main 'perspective' text brief and to the point.**

3. Autobiographical Insight:
   - Share a brief, authentic, and relatable story or analogy that connects to the user's situation.
   - Focus on lessons learned or insights gained from this experience.
   - Clearly connect the story back to their specific situation, highlighting the relevance.
   - Keep it brief but impactful.
   - Use real-world examples.
   - **Keep this section's main 'story' text brief and to the point.**

4. Logical Framework:
   - Break down the user's situation or problem into clear, manageable components.
   - Identify core underlying issues vs surface-level symptoms.
   - Create concrete, actionable steps the user can take to address the situation.
   - Prioritize steps based on potential impact or ease of implementation.
   - Make the steps practical, doable, and easy to understand.
   - **Keep this section's main 'framework' text brief and to the point.**

Example response format:
{
    "psychological": {
        "analysis": "A deep analysis reflecting empathy and connecting to potential patterns. **Keep this brief.**",
        "key_points": [
            "Detailed point offering insight into cognitive patterns, with a specific example.",
            "Empathetic point relating current feelings to past experiences, explaining the connection clearly.",
            "Actionable psychological technique to manage a specific thought or emotion, with clear steps."
        ]
    },
    "philosophical": {
        "perspective": "Relevant philosophical view applied to the user's context. **Keep this brief.**",
        "key_points": [
            "Explanation of a philosophical concept and its historical context, clearly related to the user's issue.",
            "Practical application of philosophical wisdom with concrete, modern examples of how to live by it.",
            "Relatable insight from a philosopher or school of thought, explaining its direct relevance to their challenge."
        ]
    },
    "autobiographical": {
        "story": "A brief personal story or analogy related to their struggle. **Keep this brief.**",
        "key_points": [
            "The key lesson learned from the story, explained in detail.",
            "A practical takeaway from the experience that the user can apply.",
            "Explicit connection of the story's relevance to the user's current situation."
        ]
    },
    "logical": {
        "framework": "A clear, step-by-step plan for addressing the situation. **Keep this brief.**",
        "key_points": [
            "First concrete, actionable step with clear instructions and why it's important.",
            "Second practical step with details on implementation and potential benefits.",
            "Third doable step outlining how to integrate it into daily routine, with focus on outcomes."
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
                "max_tokens": 2000  # Increased from 1000 to 2000 for longer responses
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

            # Only keep 2 key points per section and truncate initial text
            for section in ["psychological", "philosophical", "autobiographical", "logical"]:
                if section in structured_response:
                    # Truncate initial text
                    for key in ["analysis", "perspective", "story", "framework"]:
                        if key in structured_response[section]:
                            # Find the last sentence-ending punctuation near the 120 character limit
                            original_text = structured_response[section][key]
                            if len(original_text) > 120:
                                # Search for punctuation in the first 200 characters (or original length if less than 200)
                                search_area = original_text[:min(len(original_text), 200)]
                                truncation_point = 120 # Default truncation point

                                # Find the last punctuation before or at 200 characters
                                last_punctuation_index = -1
                                for i in range(len(search_area) - 1, -1, -1):
                                    if search_area[i] in ['.', '?', '!']:
                                        last_punctuation_index = i
                                        break

                                if last_punctuation_index != -1 and last_punctuation_index >= 100: # Truncate if punctuation is found after character 100
                                     truncation_point = last_punctuation_index + 1 # Include the punctuation
                                elif last_punctuation_index == -1 and len(original_text) > 200:
                                     # If no punctuation found in first 200 chars and text is longer, still truncate to avoid massive text
                                     truncation_point = 200 # Truncate at a slightly larger fixed point if no punctuation
                                else:
                                    # If punctuation is too early or text is short, keep default 120 or original length
                                    truncation_point = min(len(original_text), 120)
                                    
                                structured_response[section][key] = original_text[:truncation_point].strip()
                            # If original text is 120 or less, keep as is (or handle if needed)
                            # structured_response[section][key] = structured_response[section][key][:120] # Original line
                    # Only keep first 3 key points
                    if "key_points" in structured_response[section]:
                        structured_response[section]["key_points"] = structured_response[section]["key_points"][:3]

            # Validate the structure and return appropriate response
            required_sections = ["psychological", "philosophical", "autobiographical", "logical"]
            if all(section in structured_response for section in required_sections):
                return {"response": structured_response}
            else:
                # If structure is invalid after parsing, return a simple text response
                print("Warning: LLM response missing required sections. Returning simple text fallback.")
                # Attempt to extract some text from the potentially malformed response
                fallback_message = "I'm sorry, I couldn't generate the full structured response right now. How can I help?"
                # Try to find any message content in the parsed (but incomplete) structure
                if structured_response:
                    for section_data in structured_response.values():
                        if isinstance(section_data, dict):
                            for key, value in section_data.items():
                                if isinstance(value, str) and len(value) > 10:
                                    fallback_message = value # Use the first reasonable string found
                                    break
                                elif isinstance(value, list) and value:
                                     # Use the first item in a list if it's a string
                                     if isinstance(value[0], str) and len(value[0]) > 10:
                                         fallback_message = value[0]
                                         break
                        if fallback_message != "I'm sorry, I couldn't generate the full structured response right now. How can I help?":
                            break
                return {"response": {"error": "Failed to parse structured response", "raw": fallback_message}}
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return the raw content as an error
            print(f"Error: Failed to parse JSON response from LLM: {str(e)}")
            print(f"Raw content: {content}")
            return {"response": {"error": "Failed to parse structured response", "raw": content}}
    