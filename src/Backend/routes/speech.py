from fastapi import APIRouter, UploadFile, File, HTTPException
from src.Backend.routes.groqchat import classify_intent_and_respond
import os
import whisper
from src.Backend.routes.langchain import run_langchain_agent
from elevenlabs.client import ElevenLabs 
from fastapi.responses import StreamingResponse
import io
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
api_key = os.getenv("ELEVEN_API_KEY")
# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=api_key)
# Load the Whisper model
model = whisper.load_model("base")


@router.post("/transcribe/") #micrecorder.jsx use krega iss endpoint ko
async def transcribe_audio_file(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="Invalid file type")
            
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
            
        # Save to temp file
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)
        print(f"Saved temp file: {temp_path}")
        # Transcribe
        try:
            result = model.transcribe(
                temp_path,
                fp16=True,      # Faster processing
                beam_size=1     # Reduce beam size for speed
            )
            transcription = result["text"]
            print(f"Transcription successful: {transcription}")  # Debug log
        except Exception as transcribe_error:
            print(f"Transcription error: {str(transcribe_error)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Transcription failed: {str(transcribe_error)}")
        
        # Get response
        try:
            intent_data = await classify_intent_and_respond(transcription)
            if intent_data.get("type") == "command":
                response_text = run_langchain_agent(transcription)
            else:
                response_text = intent_data.get("message")
                print(f"Response generated: {response_text}")  # Debug log
        except Exception as response_error:
            print(f"Response generation error: {str(response_error)}")  # Debug log
            raise HTTPException(status_code=500, detail=f"Response generation failed: {str(response_error)}")
            
        # Cleanup
        os.remove(temp_path)
        
        return {
            "status": "success",
            "data": {
                "transcription": transcription,
                "response_text": response_text
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/text-to-speech/")
async def text_to_speech_api(data: dict):
    text = data.get("text", "")
    if not text.strip():
        return {"error": "No text provided."}

    # Intent classify + agent (optional, jaise tumhe chahiye)
    intent_data = await classify_intent_and_respond(text)
    intent_type = intent_data.get("type")
    message = intent_data.get("message")

    if intent_type == "command":
        message = run_langchain_agent(text)

    # ElevenLabs TTS
    audio = elevenlabs_client.text_to_speech.convert(
        text=message,
        voice_id="zgqefOY5FPQ3bB7OZTVR",  
        model_id="eleven_turbo_v2",
        output_format="mp3_44100_128",
        optimize_streaming_latency=4
    )
    # Convert generator to bytes
    audio_bytes = b''.join(audio)  # This consumes the generator

    # Now wrap in BytesIO
    audio_stream = io.BytesIO(audio_bytes)

    # Return as a streaming response
    return StreamingResponse(audio_stream, media_type="audio/mpeg")