# app.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from chatBot import ask_rag


app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


chat_sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    if req.session_id not in chat_sessions:
        chat_sessions[req.session_id] = []

    try:
        result = ask_rag(req.message, chat_sessions[req.session_id])
        MAX_HISTORY = 12  # 6 user + 6 AI messages
        if len(chat_sessions[req.session_id]) > MAX_HISTORY:
            chat_sessions[req.session_id] = chat_sessions[req.session_id][-MAX_HISTORY:]
        
        return{
            "answer":result["answer"],
            "urgency_level": result["urgency_level"],
            "urgency_label": result["urgency_label"]
        }
    except Exception as e:
        return {
            "answer": "System temporarily unavailable",
            "urgency_level": 0,
            "urgency_label": "Low"
        }
