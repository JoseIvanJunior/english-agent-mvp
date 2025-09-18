# backend/app.py

import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from gtts import gTTS
from typing import List

# Importações absolutas corrigidas
from backend import schemas, models
from backend.db import get_db, engine, Base
from backend.routes import reminder
from backend.agents import ask_english_teacher
from backend.reminder_scheduler import schedule_daily_reminder

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Cria tabelas no banco, se não existirem
Base.metadata.create_all(bind=engine)

# Diretório para salvar áudios
AUDIO_DIR = BASE_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# --- Configuração do FastAPI ---
app = FastAPI(title="English Agent Backend")

# --- CORS ---
origins = [
    "http://localhost",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos de áudio
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# --- Routers adicionais ---
app.include_router(reminder.router)

# ---------------- Lessons ----------------
@app.post("/lessons/", response_model=schemas.LessonOut)
def create_lesson(lesson: schemas.LessonIn, db: Session = Depends(get_db)):
    db_lesson = models.EnglishLesson(phrase=lesson.phrase, translation=lesson.translation)
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

@app.get("/lessons/", response_model=List[schemas.LessonOut])
def list_lessons(db: Session = Depends(get_db)):
    return db.query(models.EnglishLesson).order_by(models.EnglishLesson.id.desc()).all()

# ---------------- Speak (TTS) ----------------
@app.get("/speak/{lesson_id}")
def speak_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(models.EnglishLesson).filter(models.EnglishLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    text = lesson.phrase
    filename = f"lesson_{lesson_id}.mp3"
    filepath = AUDIO_DIR / filename

    try:
        # Aqui forçamos inglês, mas se quiser detectar pode usar langdetect
        tts = gTTS(text=text, lang="en")
        tts.save(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

    return {"text": text, "audio_url": f"/audio/{filename}"}

# ---------------- Chat ----------------
@app.post("/send_message")
def send_message(msg: schemas.MessageIn, db: Session = Depends(get_db)):
    """Recebe mensagem do usuário, envia para o agente e retorna a resposta."""
    # Log do usuário
    user_msg = models.Message(user=msg.user, sender="user", text=msg.text)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    try:
        response_text = ask_english_teacher(msg.text)
    except Exception as e:
        response_text = f"(Agent error) {e}"

    # Log da resposta do agente
    agent_msg = models.Message(user=msg.user, sender="agent", text=response_text)
    db.add(agent_msg)
    db.commit()
    db.refresh(agent_msg)

    return {"response": response_text}

@app.get("/history/{user}")
def history(user: str, db: Session = Depends(get_db)):
    """Retorna todo o histórico de conversas de um usuário específico."""
    msgs = (
        db.query(models.Message)
        .filter(models.Message.user == user)
        .order_by(models.Message.created_at.asc())
        .all()
    )
    return [
        {
            "sender": m.sender,
            "text": m.text,
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for m in msgs
    ]

# ---------------- Scheduler ----------------
@app.on_event("startup")
def startup_event():
    """Inicializa o agendador de lembretes diários ao subir a API."""
    try:
        schedule_daily_reminder(hour=20, minute=0)
        print("✅ Scheduler started: daily reminder at 20:00")
    except Exception as e:
        print("⚠️ Scheduler not started:", e)
