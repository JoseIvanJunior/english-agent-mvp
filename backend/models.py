# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, func
from backend.db import Base

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    remind_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True, default="junior")
    sender = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EnglishLesson(Base):
    __tablename__ = "english_lessons"
    id = Column(Integer, primary_key=True, index=True)
    phrase = Column(Text, nullable=False)
    translation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
