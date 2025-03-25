from fastapi import FastAPI, File, UploadFile
import whisper
import os
import groq
import httpx
from dotenv import load_dotenv
# Initialize FastAPI app
app = FastAPI()

# Load environment variables from .env file
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Initialize Groq client
client = groq.Groq(api_key=GROQ_API_KEY)
print("API Key:", os.getenv("GROQ_API_KEY"))
# Load the Whisper model
model = whisper.load_model("base")
@app.get("/")
def read_root():
    return {"message": "Welcome to the Ruhaan AI API"}
async def chatgpt_response(transcription):
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
            return {"transcription": transcription, "chatgpt_response": f"Error: {response.text}"}

        response_data = response.json()
        print("Groq API Response:", response_data)  # Debugging

        # Check if "choices" exists in response
        if "choices" in response_data and response_data["choices"]:
            chat_response = response_data["choices"][0]["message"]["content"]
        else:
            chat_response = "Error: No valid response from Groq API"

    return {
        "transcription": transcription,
        "chatgpt_response": chat_response
    }
@app.post("/transcribe/")
async def transcribe_audio_file(file: UploadFile = File(...)):
    # Save the uploaded audio file temporarily
    audio_path = os.path.join("Assets", file.filename)
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    # Transcribe the audio file
    result = model.transcribe(audio_path)
    
    # Return the transcription text as a JSON response
    transcription = result["text"]
    # Send transcription to ChatGPT and wait for response
    chat_response = await chatgpt_response(transcription)

    # Return both transcription and ChatGPT response
    return chat_response
# Send transcription to ChatGPT
