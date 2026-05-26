import os
import vertexai
from google.adk.models import Gemini
from google.adk.models.registry import LLMRegistry
from google.adk.agents import LlmAgent
from vertexai.preview.reasoning_engines import AdkApp

# 1. Configurações Dinâmicas
# A esteira de CI/CD ou o ambiente de deploy deve injetar essas variáveis
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "projeto-a-492414")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Inicializa o SDK do Vertex AI para o projeto correto
vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)

# Registra o modelo do Google para uso no ADK
LLMRegistry.register(Gemini)

# 2. Construtor do Serviço de Sessão
# Permite que o Vertex AI gerencie a memória de curto prazo (histórico do chat)
def session_service_builder():
    from google.adk.sessions import VertexAiSessionService
    return VertexAiSessionService(
        project=GOOGLE_CLOUD_PROJECT, 
        location=GOOGLE_CLOUD_LOCATION
    )

# 3. Definição do Aplicativo e do Agente
# O objeto 'agent_app' é o que o Vertex AI ModuleAgent vai procurar durante o deploy
agent_app = AdkApp(
    agent=LlmAgent(
        name="AssistenteNerd",
        model="gemini-2.5-flash",
        description="Assistente simples provisionado via esteira de CI/CD.",
        instruction=(
            "Você é um assistente de IA muito inteligente, mas responde sempre de "
            "forma sarcástica e usando referências de cultura pop (filmes, séries, "
            "tecnologia). Seja breve."
        ),
        tools=[], # Array vazio pois este agente foca puramente em texto/personalidade
    ),
    session_service_builder=session_service_builder,
)