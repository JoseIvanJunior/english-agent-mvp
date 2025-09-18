English Agent MVP
Este projeto é um MVP (Minimum Viable Product) de um agente de estudo de inglês que utiliza APIs de linguagem para criar e gerenciar aulas. Ele é composto por um backend em Python (usando FastAPI) e um frontend em HTML/CSS/JavaScript.

🚀 Como Começar
Siga os passos abaixo para instalar e rodar o projeto.

Backend
Instale o ambiente virtual:

No Windows (PowerShell):

python -m venv .venv; .\.venv\Scripts\Activate
No Linux/macOS:

python -m venv .venv; source .venv/bin/activate
Instale as dependências:

pip install -r backend/requirements.txt
Configure o banco de dados:

Copie o arquivo de exemplo:

cp .env.example .env
Se for usar Postgres, abra o novo arquivo .env e configure a variável DATABASE_URL com as suas credenciais. Se não for, o projeto usará SQLite por padrão.

Inicie o backend:

cd backend
python -m uvicorn app:app --reload
Frontend
Inicie um servidor web simples:

Navegue até a pasta do frontend e rode:

cd frontend
python -m http.server 5500
Acesse o aplicativo:

Abra o navegador e acesse a URL:

http://<IP_DO_SEU_PC>:5500/index.html
⚙️ Configurações Adicionais
Trocar para PostgreSQL
Se você decidir usar PostgreSQL em vez de SQLite, siga estes passos:

Atualize o arquivo .env com a sua DATABASE_URL.

Exemplo:

DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/seu_banco
Instale a biblioteca necessária para a conexão:

pip install psycopg2-binary
Reinicie o backend. O SQLAlchemy criará as tabelas automaticamente. Você pode verificar as tabelas usando ferramentas como pgAdmin ou DBeaver.

Usar o Gemini (Google Generative AI)
O projeto pode usar o modelo Gemini para gerar conteúdo, mas requer uma configuração.

Obtenha sua chave da API do Google.

Abra o arquivo .env e adicione a sua chave:

GOOGLE_API_KEY=sua_chave_aqui
Instale as bibliotecas adicionais:

pip install langchain langchain-google-genai
Se a chave da API não for configurada, o projeto usará um agente de fallback.

📝 Observações e Próximos Passos
Testes Iniciais
Crie uma lição no frontend. Ao clicar em Play, o backend irá gerar um arquivo de áudio lesson_X.mp3 e o navegador irá reproduzi-lo.

Se estiver usando SQLite, você pode inspecionar o banco de dados reminders.db com ferramentas como o DB Browser for SQLite ou a extensão do VS Code.

Sugestões de Melhorias
Autenticação: Implementar JWT para gerenciar usuários.

Banco de Dados: Usar Alembic para gerenciar as migrações do banco de dados de forma mais robusta.

Qualidade do Áudio: Trocar o gTTS (Google TTS) pela Google Cloud TTS para um áudio mais natural.

Notificações: Adicionar push notifications (FCM) para lembretes de estudo.

Áudio Offline: Substituir o gTTS por uma biblioteca TTS offline, se a conexão com a internet for um problema.