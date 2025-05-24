import os
from dotenv import load_dotenv
import groq
from elevenlabs import ElevenLabs

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")


# Initialize clients
groq_client = groq.Groq(api_key=GROQ_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVEN_API_KEY)

