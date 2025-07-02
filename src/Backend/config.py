import os
from dotenv import load_dotenv
from src.Backend.sarvam import Sarvam

load_dotenv()

SARVAM_API_KEY = "12fdbbc3-67a6-4347-9e0a-8ce1b5b45cad"

# Initialize clients
sarvam_client = Sarvam(api_key=SARVAM_API_KEY)
