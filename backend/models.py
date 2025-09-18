# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, func, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime

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
    sender = Column(String)  # "user" or "agent" or "system"
    text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EnglishLesson(Base):
    __tablename__ = "english_lessons"
    id = Column(Integer, primary_key=True, index=True)
    phrase = Column(Text, nullable=False)         # frase em inglês
    translation = Column(Text, nullable=True)     # tradução
    created_at = Column(DateTime(timezone=True), server_default=func.now())
