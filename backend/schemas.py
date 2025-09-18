from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ReminderIn(BaseModel):
    title: str
    description: Optional[str] = None
    remind_at: Optional[datetime] = None

class ReminderOut(ReminderIn):
    id: int
    created_at: datetime

class MessageIn(BaseModel):
    user: str
    text: str

class LessonIn(BaseModel):
    phrase: str
    translation: Optional[str] = None

class LessonOut(LessonIn):
    id: int