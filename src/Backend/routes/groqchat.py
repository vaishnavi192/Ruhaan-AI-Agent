from fastapi import APIRouter
import groq
import os
import httpx
from dotenv import load_dotenv
from Backend.config import GROQ_API_KEY
load_dotenv()
router = APIRouter()

async def groq_response(transcription):
    print(f"Sending transcription to Groq API: {transcription}")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": transcription}],
                "temperature": 0.7 
            },
            )
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return {"transcription": transcription, "groq_response": f"Error: {response.text}"}

        response_data = response.json()
        
        # Check if "choices" exists in response
        chat_response = (
        response_data.get("choices", [{}])[0]  # Fallback to empty dict if no choices
        .get("message", {})                   # Fallback if no message
        .get("content", "Error: Invalid response format")  # Final fallback
)

    return {
        "transcription": transcription,
        "groq_response": chat_response
    }