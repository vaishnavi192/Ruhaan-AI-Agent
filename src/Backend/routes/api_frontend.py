# /api/chat -> api_frontend.py (chat endpoint)
# /api/speech/transcribe -> speech.py (speech to text)
# /api/speech/tts -> speech.py (text to speech)
# /api/command -> langchain.py (commands)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.Backend.routes.groqchat import chat_with_groq, classify_intent_and_respond
from src.Backend.routes.langchain import run_langchain_agent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat") #chatbot.jsx use krega iss endpoint ko
async def process_chat(request: ChatRequest):
    """Process chat messages and return appropriate response"""
    try:
        # First classify the intent
        intent_data = await classify_intent_and_respond(request.message)
        
        # If it's a command, use langchain
        if intent_data.get("type") == "command":
            response = run_langchain_agent(request.message)
            return {
                "status": "success",
                "data": {
                    "response": response,
                    "type": "command"
                }
            }
        
        # Otherwise use normal chat
        response = await chat_with_groq(request.message)
        return {
            "status": "success",
            "data": {
                "response": response["response"],
                "type": "chat"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

