# Usa Python oficial leve
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o backend
COPY . .

# Expõe a porta padrão do FastAPI
EXPOSE 8000

# Comando para rodar no Railway
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
