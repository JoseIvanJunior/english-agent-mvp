# English Agent MVP

## Instalação (backend)
1. Crie e ative um virtualenv:
   - Windows (PowerShell): `python -m venv .venv; .\.venv\Scripts\Activate`
   - Linux/macOS: `python -m venv .venv; source .venv/bin/activate`

2. Instale dependências:
pip install -r backend/requirements.txt


3. Copie `.env.example` para `.env` e ajuste `DATABASE_URL` se for usar Postgres.

4. Rode o backend:
cd backend
python -m uvicorn backend.app:app --reload
# python -m uvicorn app:app --reload


## Frontend
1. Abra a pasta `frontend` com um servido simples:
cd frontend
python -m http.server 5500

2. No celular/PC acesse:
`http://<IP_DO_PC>:5500/index.html`

## Trocar para Postgres
- Configure `DATABASE_URL` no `.env`:
DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/seu_banco

- Instale `psycopg2-binary` e reinicie o backend. O SQLAlchemy criará as tabelas no Postgres.

## Observações
- `gTTS` gera MP3 usando Google TTS; precisa de internet.
- Se quiser usar Gemini/Google generative, coloque `GOOGLE_API_KEY` em `.env` e instale as libs `langchain` e `langchain-google-genai`.


Notas finais e próximos passos sugeridos (práticos)

Testes iniciais: crie lessons no frontend e clique Play → o backend gera audio/lesson_X.mp3 e o navegador toca.

Verificação do DB: se estiver em SQLite, abra reminders.db com DB Browser for SQLite ou a extensão do VSCode.

Trocar para Postgres: atualize .env e reinicie. Verifique tabelas no pgAdmin/DBeaver.

Melhorias rápidas que recomendo:

usar JWT se planejar usuários reais;

adicionar migrations com Alembic;

usar Google Cloud TTS (mais natural) se quiser qualidade;

integrar push notifications (FCM) para lembretes reais;

trocar gTTS por um TTS offline se quiser rodar sem internet.

Deploy: para produção, rode backend em um servidor (Gunicorn/Uvicorn behind Nginx), banco Postgres e sirva frontend via CDN.

Se quiser eu já faço adaptações específicas agora:

adaptar agents.py para incorporar seu código (o TRIAGEM_PROMPT/triagem_chain que você mostrou) — posso mesclar com o ask_english_teacher;

trocar gTTS por Google Cloud TTS (se você tiver credenciais);

ou gerar um arquivo Docker Compose pronto com Postgres + backend + frontend.

Diz qual dessas opções quer que eu faça agora e eu já te dou o código pronto.

http://127.0.0.1:8000/docs#/

✅ Resumindo, o que fazer:

Ative seu virtualenv:

.\.venv\Scripts\activate


Instale as dependências faltantes:

pip install requests
pip install langchain langchain-google-genai google-generativeai


Rode novamente:

python -m uvicorn app:app --reload


Agora o backend deve subir sem erros.

Se Gemini não estiver configurado (sem GOOGLE_API_KEY), ele ainda usará o fallback agent.

Se quiser evoluir o projeto, aqui vão algumas ideias rápidas:

🔄 Suporte a histórico no prompt para que o agente entenda o contexto.

📈 Logs de chamadas e falhas do Gemini para analytics ou debug.

🌐 Suporte a múltiplos idiomas (com tradução automática).

🧠 Cache de respostas para economizar chamadas na API.

💡 Modo de explicação gramatical mais detalhado para estudantes avançados.

Se quiser ajuda com alguma dessas ideias ou algo mais, só chamar. Boa, professor de inglês com IA ativado! 😄👏