import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from gtts import gTTS
from pathlib import Path
from datetime import datetime

# Importações corrigidas
from . import schemas, models
from .db import get_db, engine, Base
from .agents import ask_english_teacher
from .reminder_scheduler import schedule_daily_reminder

# Define o caminho base do diretório 'backend'
# Isso garante que os caminhos são relativos ao app.py, e não ao diretório de execução
BASE_DIR = Path(__file__).resolve().parent

# Carrega as variáveis de ambiente do .env que está DENTRO da pasta backend
load_dotenv(BASE_DIR / ".env")

# Crie as tabelas do DB se não existirem
Base.metadata.create_all(bind=engine)

# Define o caminho da pasta de áudio dentro do 'backend'
AUDIO_DIR = BASE_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="English Agent Backend")

# Adicione o middleware CORS
origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Sirva arquivos de áudio
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# ------------------
# Endpoints - Reminders
# ------------------
@app.post("/reminders/", response_model=schemas.ReminderOut)
def create_reminder(reminder: schemas.ReminderIn, db: Session = Depends(get_db)):
    """Cria um novo lembrete com data e hora."""
    db_reminder = models.Reminder(**reminder.dict())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@app.get("/reminders/", response_model=List[schemas.ReminderOut])
def list_reminders(db: Session = Depends(get_db)):
    """Lista todos os lembretes."""
    return db.query(models.Reminder).order_by(models.Reminder.id.desc()).all()

# ------------------
# Endpoints - Lessons
# ------------------
@app.post("/lessons/", response_model=schemas.LessonOut)
def create_lesson(lesson: schemas.LessonIn, db: Session = Depends(get_db)):
    """Cria uma nova lição de inglês."""
    db_lesson = models.EnglishLesson(phrase=lesson.phrase, translation=lesson.translation)
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

@app.get("/lessons/", response_model=List[schemas.LessonOut])
def list_lessons(db: Session = Depends(get_db)):
    """Lista todas as lições de inglês."""
    return db.query(models.EnglishLesson).order_by(models.EnglishLesson.id.desc()).all()

# ------------------
# Endpoint - Speak (gerar áudio MP3)
# ------------------
@app.get("/speak/{lesson_id}")
def speak_lesson(lesson_id: int, db: Session = Depends(get_db)):
    """Gera e retorna a URL de um arquivo de áudio para uma lição."""
    lesson = db.query(models.EnglishLesson).filter(models.EnglishLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    text = lesson.phrase
    filename = f"lesson_{lesson_id}.mp3"
    filepath = AUDIO_DIR / filename

    try:
        tts = gTTS(text=text, lang="en")
        tts.save(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

    return {"text": text, "audio_url": f"/audio/{filename}"}

# ------------------
# Endpoint - Enviar mensagem ao agente
# ------------------
@app.post("/send_message")
def send_message(msg: schemas.MessageIn, db: Session = Depends(get_db)):
    """Envia uma mensagem ao agente de IA e retorna a resposta."""
    # Salvar a mensagem do usuário
    message = models.Message(user=msg.user, sender="user", text=msg.text)
    db.add(message)
    db.commit()
    db.refresh(message)

    # Obter a resposta do agente
    try:
        response_text = ask_english_teacher(msg.text)
    except Exception as e:
        response_text = f"(Agent error) {e}"

    # Salvar a resposta do agente
    agent_msg = models.Message(user=msg.user, sender="agent", text=response_text)
    db.add(agent_msg)
    db.commit()
    db.refresh(agent_msg)

    return {"response": response_text}

# ------------------
# Endpoint - Histórico de mensagens
# ------------------
@app.get("/history/{user}")
def history(user: str, db: Session = Depends(get_db)):
    """Retorna o histórico de conversas para um usuário específico."""
    msgs = db.query(models.Message).filter(models.Message.user == user).order_by(models.Message.id.asc()).all()
    return [{"sender": m.sender, "text": m.text, "created_at": m.created_at} for m in msgs]

# ------------------
# Inicialização - Agendamento de lembrete diário
# ------------------
@app.on_event("startup")
def startup_event():
    """Agende um lembrete diário ao iniciar a aplicação."""
    try:
        schedule_daily_reminder(hour=20, minute=0)
        print("Scheduler started: daily reminder at 20:00")
    except Exception as e:
        print("Scheduler not started:", e)