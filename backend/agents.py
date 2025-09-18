import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from pathlib import Path

# Define o caminho base do diretório 'backend'
BASE_DIR = Path(__file__).resolve().parent

# 1. Carregue as variáveis de ambiente, especificando o caminho do .env.
load_dotenv(BASE_DIR / ".env")

# 2. Obtenha a chave da API.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 3. Inicialize o modelo do Gemini.
if GOOGLE_API_KEY:
    try:
        os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7
        )
        print("✅ Modelo Gemini inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar o modelo Gemini: {e}")
        llm = None
else:
    llm = None
    print("⚠️ GOOGLE_API_KEY não encontrada, usando agente de fallback.")

# Prompt do agente de conversação ajustado
ENGLISH_TEACHER_PROMPT = """
You are a bilingual English teacher (Portuguese + English).
Your main goal is to help the student improve their English.

Rules:
- If the student writes in English:
    • Correct grammar and spelling.
    • Provide a short explanation in simple English.
- If the student writes in Portuguese:
    • Answer in Portuguese, but include English examples, corrections or translations.
    • Encourage the student to practice writing in English.

Examples:
- User (EN): I goed to the park yesterday.
- Agent: Correction: I went to the park yesterday. ("Went" is the past tense of "go".)

- User (EN): What is the capital of France?
- Agent: The capital of France is Paris.

- User (PT): No que você pode me ajudar?
- Agent: Posso te ajudar a melhorar seu inglês! Por exemplo, se você escrever "Eu fui ao parque", em inglês seria "I went to the park". Podemos praticar juntos!

User: {text}
Agent:
"""
prompt_template = PromptTemplate(
    input_variables=["text"],
    template=ENGLISH_TEACHER_PROMPT
)

def fallback_agent(text: str) -> str:
    """Função de fallback caso o agente principal não esteja disponível."""
    return f"English teacher (fallback): Eu li: '{text}'. Tente escrever frases curtas em inglês. (Ative o Gemini para respostas mais inteligentes.)"

# Agente de conversação com o professor de inglês
def ask_english_teacher(text: str) -> str:
    if llm:
        try:
            chain = prompt_template | llm
            response = chain.invoke({"text": text})
            return response.content
        except Exception as e:
            print(f"Erro na chamada do Gemini: {e}")
            return fallback_agent(text)
    else:
        return fallback_agent(text)
