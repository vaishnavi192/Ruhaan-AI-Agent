import os
import requests
from dotenv import load_dotenv
# Load API key from environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# API endpoint
url = "https://api.groq.com/openai/v1/chat/completions"

# Headers
headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# Request body
data = {
    "model": "llama3-8b-8192",
    "messages": [{"role": "user", "content": "Hello, Groq!"}],
    "temperature": 0.7
}

# Make API request
response = requests.post(url, headers=headers, json=data)

# Print response
print(response.status_code)
print(response.json())
