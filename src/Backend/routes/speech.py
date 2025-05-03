from fastapi import APIRouter, UploadFile, File, Query
from routes.groqchat import groq_response
import os
from Backend.config import groq_client
import whisper
from elevenlabs.client import ElevenLabs 
from elevenlabs import play
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
api_key = os.getenv("ELEVEN_API_KEY")
# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=api_key)
# Load the Whisper model
model = whisper.load_model("base")
@router.get("/text-to-speech")
async def text_to_speech(transcription: str = Query(...)):
    try:
        if not transcription.strip():
            return {"error": "No transcription provided."}

        # Step 1: Get Groq's response (sync call)
        groq_response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": transcription}]
        )
        response_text = groq_response.choices[0].message.content

        # Step 2: Generate speech with ElevenLabs
        audio = elevenlabs_client.text_to_speech.convert(
            text=response_text,
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model_id="eleven_turbo_v2",
            output_format="mp3_44100_128"
        )

        # Step 3: Play audio using ElevenLabs' built-in play()
        play(audio)  # Uses ElevenLabs' implementation
        
        return {"message": "Speech played successfully."}

    except Exception as e:
        return {
            "error": "Failed to generate speech",
            "details": str(e),
            "type": type(e).__name__
        }
@router.post("/transcribe/")
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
    chat_response = await groq_response(transcription)

    # Return both transcription and ChatGPT response
    return chat_response