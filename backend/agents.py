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
# A biblioteca do Google GenAI pode precisar que a variável de ambiente seja
# definida no nível do sistema, então a linha abaixo garante isso.
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

# Prompt do agente de conversação
ENGLISH_TEACHER_PROMPT = """
You are a helpful English teacher. Your goal is to help me improve my English.
Please correct my grammar, spelling, and provide a short, simple explanation for the correction.
If I ask a general question, please answer it as a helpful teacher would.
Examples:
- User: I goed to the park yesterday.
- Agent: Correction: I went to the park yesterday. ("Went" is the past tense of "go".)
- User: What is the capital of France?
- Agent: The capital of France is Paris.

User: {text}
Agent:
"""
prompt_template = PromptTemplate(
    input_variables=["text"],
    template=ENGLISH_TEACHER_PROMPT
)

def fallback_agent(text: str) -> str:
    """Função de fallback caso o agente principal não esteja disponível."""
    return f"English teacher (fallback): I read: '{text}'. Try to write short sentences. (Enable Gemini for smarter replies.)"

# Agente de conversação com o professor de inglês
def ask_english_teacher(text: str) -> str:
    if llm:
        try:
            chain = prompt_template | llm
            response = chain.invoke({"text": text})
            return response.content
        except Exception as e:
            # Se o modelo Gemini falhar na chamada, use o fallback.
            print(f"Erro na chamada do Gemini: {e}")
            return fallback_agent(text)
    else:
        # Se o Gemini não foi inicializado (chave não encontrada), use o fallback.
        return fallback_agent(text)