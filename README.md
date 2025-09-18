# 🧠 English Agent MVP

Um agente de conversação em inglês alimentado por IA, feito para ajudar você a melhorar suas habilidades no idioma. O projeto é composto por:

- ⚙️ **Backend** com FastAPI (Python)
- 🌐 **Frontend** simples com HTML + JavaScript

---

## 🚀 Funcionalidades

- 🧑‍🏫 **Professor de Inglês (AI):** Usa a API do Google Gemini para corrigir gramática e responder perguntas.
- 📚 **Armazenamento de Lições:** Salva frases e traduções no banco de dados.
- 🔊 **Text-to-Speech (TTS):** Converte frases em áudio MP3 usando `gTTS`.

---

## ⚙️ Instalação e Configuração

### 1. 🔙 Backend

#### 📁 Acesse a pasta `backend`:

```bash
cd backend

🐍 Crie e ative o ambiente virtual:

Windows (PowerShell):

python -m venv .venv; .\.venv\Scripts\Activate

Linux/macOS:

python -m venv .venv; source .venv/bin/activate

📦 Instale as dependências:

pip install -r requirements.txt

⚙️ Configure o ambiente:

1. Copie o arquivo .env.example para .env.

2. Adicione sua chave da API do Google:
GOOGLE_API_KEY=SUA_CHAVE_AQUI

▶️ Rode o backend:

Volte para a raiz do projeto:

cd ..

Inicie o servidor FastAPI com Uvicorn:

python -m uvicorn backend.app:app --reload

O backend estará disponível em: http://127.0.0.1:8000

Documentação interativa da API: http://127.0.0.1:8000/docs

2. 🌐 Frontend
📁 Acesse a pasta frontend:

cd frontend

🚀 Inicie um servidor web local:

python -m http.server 5500

Acesse no navegador:

Local: http://127.0.0.1:5500

Outro dispositivo na rede: http://<IP_DO_SEU_PC>:5500

🧪 Testes e Observações

🎧 Teste de Áudio: Crie uma nova lição e clique em "play" para ouvir o áudio gerado pelo backend.

🗃️ Banco de Dados: Usa SQLite (reminders.db) por padrão.

Você pode visualizar usando o DB Browser for SQLite

🛠️ Trocar para PostgreSQL

Edite o arquivo .env:

DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/seu_banco

2. Instale o driver:

pip install psycopg2-binary

3. Reinicie o backend.

O SQLAlchemy criará as tabelas automaticamente.

🌐 Requisitos de Internet

A funcionalidade TTS (gTTS)

API Gemini (Google AI)

Ambos requerem conexão com a internet para funcionar corretamente.

📌 Próximos Passos Sugeridos

💬 Histórico de Conversas: Enviar histórico de mensagens no prompt para manter o contexto.

🎙️ Melhorias no TTS: Integrar com Google Cloud TTS para melhor qualidade de áudio.

🔐 Autenticação: Adicionar login e registro com JWT para múltiplos usuários.

🛠️ Gerenciamento de DB: Usar ferramentas como Alembic para migrações.

🔔 Notificações: Integrar push notifications (via FCM) para lembretes diários.

🧑‍💻 Tecnologias Utilizadas

FastAPI

Google Gemini API

gTTS (Google Text-to-Speech)

SQLite

Uvicorn

HTML/CSS/JavaScript

📄 Licença

Este projeto é open-source e licenciado sob a MIT License.


Se quiser, posso também gerar o arquivo `README.md` para download. Deseja isso?
