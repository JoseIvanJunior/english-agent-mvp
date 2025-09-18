# backend/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pathlib import Path

# Caminho para a pasta backend (onde o db.py está)
BASE_DIR = Path(__file__).resolve().parent # Agora aponta para 'backend'
ENV_PATH = BASE_DIR / ".env"

# Carregar variáveis do .env
load_dotenv(ENV_PATH)

# Obter DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(f"DATABASE_URL not found. Please check your .env file at {ENV_PATH}")

# Configuração do SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependência para injeção do DB nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()