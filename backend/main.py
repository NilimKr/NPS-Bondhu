from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from groq import Groq
from src.rag_chain import get_rag_chain_with_sources, get_sources_from_query, format_sources_for_display
from src.translator import translate_to_english, translate_from_english

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://npsbondhu.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        # HuggingFace Space URL
        "https://NilimKr-nps-bondhu-backend.hf.space",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    language: str = "en"

class ChatResponse(BaseModel):
    answer: str
    sources: str = ""

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Translate to English for vector search if needed
        query_in_english = translate_to_english(request.message, request.language)
        
        # Get response from RAG chain with user requested language
        rag_chain_func = get_rag_chain_with_sources(
            streaming=False,
            search_type="mmr",
            language=request.language
        )
        
        result = rag_chain_func({"input": query_in_english})
        answer = result["answer"]
        sources_raw = result["sources"]
        
        return ChatResponse(
            answer=answer,
            sources=str(sources_raw) if sources_raw else ""
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe_endpoint(
    file: UploadFile = File(...),
    language: str = Form("en")
):
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY is not set")

        client = Groq(api_key=groq_api_key)
        audio_content = await file.read()

        lang_code = language.lower().strip()
        if lang_code not in ("as", "hi", "en"):
            lang_code = "en"

        filename = file.filename or "recording.webm"
        if not filename.endswith((".webm", ".wav", ".mp3", ".m4a", ".ogg")):
            filename += ".webm"

        transcription = client.audio.transcriptions.create(
            file=(filename, audio_content),
            model="whisper-large-v3",
            language=lang_code,
            response_format="json"
        )
        return {"text": transcription.text.strip()}
    except Exception as e:
        print(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    groq_key = os.getenv("GROQ_API_KEY", "")
    return {
        "status": "ok",
        "groq_api_key_set": bool(groq_key),
        "groq_key_preview": groq_key[:8] + "..." if groq_key else "NOT SET — add GROQ_API_KEY to Space Secrets!",
    }
