from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from pydantic import BaseModel

from db import Base, engine, get_db

# ------------------------------
# MODELO SQLAlchemy
# ------------------------------
class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    remind_at = Column(DateTime, nullable=False)

# Cria tabelas no banco
Base.metadata.create_all(bind=engine)

# ------------------------------
# SCHEMAS (Pydantic)
# ------------------------------
class ReminderBase(BaseModel):
    title: str
    description: str | None = None
    remind_at: datetime

class ReminderCreate(ReminderBase):
    pass

class ReminderResponse(ReminderBase):
    id: int

    class Config:
        orm_mode = True

# ------------------------------
# FASTAPI APP
# ------------------------------
app = FastAPI(title="Reminder API")

@app.post("/reminders/", response_model=ReminderResponse)
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = Reminder(**reminder.dict())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@app.get("/reminders/", response_model=List[ReminderResponse])
def list_reminders(db: Session = Depends(get_db)):
    return db.query(Reminder).all()

@app.get("/reminders/{reminder_id}", response_model=ReminderResponse)
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@app.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted successfully"}
