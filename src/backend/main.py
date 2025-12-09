from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from contextlib import asynccontextmanager
from .parser import ChatParser # Relative import for package
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load env vars
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAT_FILE = os.path.join(BASE_DIR, "whatsapp_export", "extracted", "_chat.txt")
ORIGINAL_CHAT_FILE = os.path.join(BASE_DIR, "whatsapp_export", "extracted", "_chat.txt")
IMAGES_DIR = os.path.join(BASE_DIR, "whatsapp_export", "extracted")

# Cache timeline in memory
timeline_cache = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load and parse chat log on startup
    global timeline_cache
    print(f"Loading chat from {CHAT_FILE} and images from {IMAGES_DIR}...")
    if os.path.exists(ORIGINAL_CHAT_FILE):
        print(f"Using original chat export for video dates: {ORIGINAL_CHAT_FILE}")
    else:
        print(f"Original chat file not found at {ORIGINAL_CHAT_FILE}")

    parser = ChatParser(CHAT_FILE, IMAGES_DIR, ORIGINAL_CHAT_FILE)
    timeline_cache = parser.parse()
    print(f"Loaded {len(timeline_cache)} days of content.")
    yield
    timeline_cache = None

app = FastAPI(lifespan=lifespan)

# Allow CORS for development
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Images
if os.path.exists(IMAGES_DIR):
    app.mount("/static", StaticFiles(directory=IMAGES_DIR), name="static")

@app.get("/api/timeline")
def get_timeline():
    if timeline_cache is None:
        return []
    return timeline_cache

@app.get("/api/search")
def search(q: str):
    if not timeline_cache:
        return []
    
    results = []
    query = q.lower()
    for day in timeline_cache:
        for msg in day['messages']:
            txt = msg['content'] if isinstance(msg['content'], str) else ""
            snd = msg['sender'] if isinstance(msg['sender'], str) else ""
            if query in txt.lower() or query in snd.lower():
                results.append({
                    "date": day['date'],
                    "time": msg['time'],
                    "sender": msg['sender'],
                    "snippet": txt[:200] + "..."
                })
    return results

class SummaryRequest(BaseModel):
    text: str

@app.post("/api/summary")
async def summarize(request: SummaryRequest):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    
    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
        
        prompt = (
            "Please provide a concise and insightful summary of the following content. "
            "If it's a conversation, highlight key points. "
            "If it's a transcript, extract the main takeaways. "
            "Keep it under 200 words.\n\n"
            f"{request.text[:10000]}" # Limit context window just in case
        )
        
        response = llm.invoke(prompt)
        return {"summary": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
