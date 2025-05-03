from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv 

load_dotenv()

# Import routers
from routes.api_frontend import router as api_frontend_router
from routes.speech import router as speech_router
from routes.groqchat import router as groqchat_router
from routes.langchain import router as langchain_router

app = FastAPI()

# CORS middleware to allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registrations
app.include_router(api_frontend_router, prefix="/api", tags=["Frontend API"])
app.include_router(speech_router, prefix="/speech", tags=["Speech"])
app.include_router(groqchat_router, prefix="/groq", tags=["Groq"])
app.include_router(langchain_router, prefix="/langchain", tags=["Langchain"])

@app.get("/")
async def root():
    return {"message": "Ruhaan AI backend is running!"}


# previous safe code 
# from fastapi import FastAPI, File, UploadFile, Query
# import whisper
# from elevenlabs.client import ElevenLabs
# from elevenlabs import play
# import os
# import groq
# import httpx
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv

# # Initialize FastAPI app
# app = FastAPI()
# # origins = [
# #     "http://localhost:5173",
# #     "http://127.0.0.1:5173",
# # ]
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=origins,  # Allow frontend React app
# #     allow_credentials=True,
# #     allow_methods=["*"],  # Allow all HTTP methods
# #     allow_headers=["*"],  # Allow all headers
# # )
# # Load environment variables from .env file
# load_dotenv()
# #Both approaches are valid; it's just that in the case of ElevenLabsAPI, the API key is passed
# # when initializing the object, while in some cases (like with Groq), the API key might be used
# # in the function call or may be passed separately when needed.
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# api_key = os.getenv("ELEVEN_API_KEY")

# # Initialize ElevenLabs client
# elevenlabs_client = ElevenLabs(api_key=api_key)
# # Initialize Groq client
# groq_client = groq.Groq(api_key=GROQ_API_KEY)

# # Load the Whisper model
# model = whisper.load_model("base")
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the Ruhaan AI API backend"}

# async def groq_response(transcription):
#     print(f"Sending transcription to Groq API: {transcription}")

#     async with httpx.AsyncClient() as client:
#         response = await client.post(
#             "https://api.groq.com/openai/v1/chat/completions",
#             headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
#             json={
#                 "model": "llama3-8b-8192",
#                 "messages": [{"role": "user", "content": transcription}],
#                 "temperature": 0.7
#             },
#             )
        
#         if response.status_code != 200:
#             print(f"Error: Received status code {response.status_code}")
#             print(f"Response: {response.text}")
#             return {"transcription": transcription, "groq_response": f"Error: {response.text}"}

#         response_data = response.json()
        
#         # Check if "choices" exists in response
#         chat_response = (
#         response_data.get("choices", [{}])[0]  # Fallback to empty dict if no choices
#         .get("message", {})                   # Fallback if no message
#         .get("content", "Error: Invalid response format")  # Final fallback
# )

#     return {
#         "transcription": transcription,
#         "groq_response": chat_response
#     }
# @app.get("/text-to-speech")
# async def text_to_speech(transcription: str = Query(...)):
#     try:
#         if not transcription.strip():
#             return {"error": "No transcription provided."}

#         # Step 1: Get Groq's response (sync call)
#         groq_response = groq_client.chat.completions.create(
#             model="llama3-8b-8192",
#             messages=[{"role": "user", "content": transcription}]
#         )
#         response_text = groq_response.choices[0].message.content

#         # Step 2: Generate speech with ElevenLabs
#         audio = elevenlabs_client.text_to_speech.convert(
#             text=response_text,
#             voice_id="21m00Tcm4TlvDq8ikWAM",
#             model_id="eleven_turbo_v2",
#             output_format="mp3_44100_128"
#         )

#         # Step 3: Play audio using ElevenLabs' built-in play()
#         play(audio)  # Uses ElevenLabs' implementation
        
#         return {"message": "Speech played successfully."}

#     except Exception as e:
#         return {
#             "error": "Failed to generate speech",
#             "details": str(e),
#             "type": type(e).__name__
#         }
# @app.post("/transcribe/")
# async def transcribe_audio_file(file: UploadFile = File(...)):
#     # Save the uploaded audio file temporarily
#     audio_path = os.path.join("Assets", file.filename)
#     with open(audio_path, "wb") as f:
#         f.write(await file.read())

#     # Transcribe the audio file
#     result = model.transcribe(audio_path)
    
#     # Return the transcription text as a JSON response
#     transcription = result["text"]
#     # Send transcription to ChatGPT and wait for response
#     chat_response = await groq_response(transcription)

#     # Return both transcription and ChatGPT response
#     return chat_response

# class ChatRequest(BaseModel): #base model  Automatic Data Validation Ensures required fields are
#     # present Checks data types (e.g., ensures message is a string)
#     message: str
    
# @app.post("/process/")
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

