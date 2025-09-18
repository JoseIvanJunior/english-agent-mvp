# backend/routes/reminder.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend import models, schemas
from backend.db import get_db

router = APIRouter(prefix="/reminders", tags=["Reminders"])

@router.post("/", response_model=schemas.ReminderOut)
def create_reminder(reminder: schemas.ReminderIn, db: Session = Depends(get_db)):
    db_reminder = models.Reminder(**reminder.dict())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@router.get("/", response_model=List[schemas.ReminderOut])
def list_reminders(db: Session = Depends(get_db)):
    return db.query(models.Reminder).order_by(models.Reminder.id.desc()).all()

@router.get("/{reminder_id}", response_model=schemas.ReminderOut)
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder = db.query(models.Reminder).filter(models.Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted successfully"}
