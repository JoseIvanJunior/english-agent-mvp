# Usa a imagem oficial do Python 3.11 em sua versão slim, ideal para produção
FROM python:3.11-slim

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia os arquivos do backend primeiro, aproveitando o cache do Docker
COPY ./backend/ ./backend/

# Instala as dependências do backend
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copia os arquivos do frontend
COPY ./frontend/ ./frontend/

# Expõe a porta que será usada pela aplicação (ex: Uvicorn)
EXPOSE 8000

# Define o comando padrão para rodar o servidor (usando FastAPI com Uvicorn)
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
