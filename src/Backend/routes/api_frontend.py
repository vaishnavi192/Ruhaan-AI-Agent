from fastapi import APIRouter
from pydantic import BaseModel
from routes.groqchat import groq_response  # service layer ka call
from routes.langchain import run_langchain_agent
router = APIRouter()

class ChatRequest(BaseModel): #base model  Automatic Data Validation Ensures required fields are
    # present Checks data types (e.g., ensures message is a string)
    message: str
    
@router.post("/process/")
async def process_text(request: ChatRequest):
    print("Received:", request.message)
    if request.message:
        chat_response = run_langchain_agent(request.message)
        return {"chat_response": chat_response}
    else:
        return {"chat_response": "No message provided"}

# class ChatRequest(BaseModel): #base model  Automatic Data Validation Ensures required fields are
#     # present Checks data types (e.g., ensures message is a string)
#     message: str
# @router.post("/process/")
# async def process_text(request: ChatRequest):
#     print(f"Received message: {request.message}")  # Log the received message for debugging

#     if request.message:
#         # Get response from Groq API (this function should call the Groq API)
#         groq_res = await groq_response(request.message)
#         print("Groq Response:", groq_res)  # Log the Groq API response
        
#         # Extract the content (you might need to adjust this based on the Groq response structure)
#         chat_response = groq_res.get("choices", [])[0].get("message", {}).get("content", "No response")

#         print(f"Sending response: {chat_response}")  # Log the final response
#         return {"chat_response": chat_response}
#     else:
#         # Handle empty or invalid input
#         return {"chat_response": "No response"}

# @app.post("/process/")
# async def process_text(request: ChatRequest):
#     chat_response = await groq_response(request.message)  # Ensure this correctly calls the API

#     print("Groq API Response:", chat_response)  # Debugging
#     print("Type of chat_response:", type(chat_response))
#     if not isinstance(chat_response, dict):
#         return {"error": "Invalid response format", "response": str(chat_response)}

#     try:
#         chat_content = chat_response.get("choices", [{}])[0].get("message", {}).get("content", "No response")
#         return {"chat_response": chat_content}
#     except Exception as e:
#         return {"error": "Unexpected response structure", "details": str(e), "response": chat_response}
