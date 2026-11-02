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

import re

def is_hallucination_or_silence(text: str, target_lang: str) -> bool:
    if not text or not text.strip():
        return True
    
    t_clean = text.lower().strip()
    
    # Common Whisper silence / boilerplate hallucinations
    common_hallucinations = [
        "thank you", "thanks for watching", "subtitles", "subscribe", 
        "divar.org", "you", "amara.org", "so let's get started", "bye",
        "watching", "farsi", "welcome"
    ]
    for h in common_hallucinations:
        if h in t_clean and len(t_clean) < 40:
            return True
            
    # If Assamese was requested, reject scripts outside Eastern Nagari (Bengali/Assamese) and basic Latin
    # Whisper has a known bug of hallucinating Malayalam, Gujarati, Gurmukhi, Telugu, etc. for 'as'
    if target_lang == "as":
        # Unicode ranges:
        # Gurmukhi (0A00-0A7F), Gujarati (0A80-0AFF), Oriya (0B00-0B7F), Tamil (0B80-0BFF),
        # Telugu (0C00-0C7F), Kannada (0C80-0CFF), Malayalam (0D00-0D7F), Arabic (0600-06FF)
        if re.search(r"[\u0A00-\u0AFF\u0B80-\u0DFF\u0600-\u06FF]", text):
            print(f"Filtered out foreign script hallucination for Assamese: {text}")
            return True

    return False

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
        if len(audio_content) < 500:
            return {"text": ""}

        lang_code = language.lower().strip()
        if lang_code not in ("as", "hi", "en"):
            lang_code = "en"

        filename = file.filename or "recording.webm"
        if not filename.endswith((".webm", ".wav", ".mp3", ".m4a", ".ogg", ".mp4")):
            filename += ".webm"

        # Whisper-large-v3 has a known defect with the 'as' language token, frequently hallucinating
        # Malayalam, Gujarati, Gurmukhi or English silence artifacts.
        # Since Assamese uses the Eastern Nagari script (U+0980-U+09FF) shared with Bengali,
        # using language="bn" without prompt forcing allows Whisper's acoustic model to decode
        # phonetically into Eastern Nagari script while maintaining accurate no_speech_prob detection.
        whisper_lang = "bn" if lang_code == "as" else lang_code

        transcription = client.audio.transcriptions.create(
            file=(filename, audio_content),
            model="whisper-large-v3",
            language=whisper_lang,
            temperature=0.0,
            response_format="verbose_json"
        )

        segments = getattr(transcription, "segments", []) or []
        # If all segments indicate high probability of no speech, reject as silence
        if segments and all(s.get("no_speech_prob", 0) > 0.65 for s in segments):
            print(f"Filtered out silence based on no_speech_prob (avg: {sum(s.get('no_speech_prob', 0) for s in segments)/len(segments):.2f})")
            return {"text": ""}

        raw_text = transcription.text.strip() if hasattr(transcription, "text") else ""
        print(f"Whisper raw transcription ({lang_code}): {raw_text}")

        if is_hallucination_or_silence(raw_text, lang_code):
            print(f"Filtered out hallucination/silence: {raw_text}")
            return {"text": ""}

        # If Assamese, perform rapid LLM post-processing to clean phonetic artifacts
        # and ensure proper Assamese vocabulary & characters ('ৰ' and 'ৱ')
        if lang_code == "as" and raw_text:
            try:
                chat = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an Assamese speech-to-text post-processor for an NPS (National Pension System) chatbot.\n"
                                "The user spoke Assamese.\n"
                                "Clean up any minor phonetic artifacts or typos into natural, clean Assamese text in Eastern Nagari script.\n"
                                "Return ONLY the cleaned Assamese text.\n"
                                "CRITICAL: If the input is silence artifact, non-sensical syllables, random letters, gibberish, or unintelligible noise, output absolutely NOTHING (empty string)."
                            )
                        },
                        {"role": "user", "content": f"Audio transcription: {raw_text}"}
                    ],
                    temperature=0.0
                )
                cleaned = chat.choices[0].message.content.strip().strip('"\'')
                if cleaned.lower() in ("none", "null", "empty", "n/a", ""):
                    print(f"LLM identified gibberish/silence: returning empty string")
                    return {"text": ""}
                print(f"Cleaned Assamese text: {cleaned}")
                return {"text": cleaned}
            except Exception as e:
                print(f"Assamese post-processing error: {e}")

        return {"text": raw_text}
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
