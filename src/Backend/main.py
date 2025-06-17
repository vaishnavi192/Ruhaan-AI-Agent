from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv 
import os
import uvicorn 
load_dotenv()

# Import routers
from src.Backend.routes.api_frontend import router as api_frontend_router
from src.Backend.routes.speech import router as speech_router
from src.Backend.routes.langchain import router as langchain_router

app = FastAPI()

# CORS middleware to allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Allow all headers to be exposed
)

# Route registrations
app.include_router(api_frontend_router, prefix="/api", tags=["Frontend API"])
app.include_router(speech_router, prefix="/api/speech", tags=["Speech"])
app.include_router(langchain_router, prefix="/api/command", tags=["Commands"])

@app.get("/")
async def root():
    return {"message": "Ruhaan AI backend is running!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

