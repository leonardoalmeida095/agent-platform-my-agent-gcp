import os
import sys
import vertexai
from vertexai import agent_engines

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
agent_dir = os.path.join(parent_dir, 'agent')
sys.path.append(agent_dir)

# Agora o import deve funcionar
from root_agent import agent_app

# 1. Captura variáveis de ambiente injetadas pela pipeline de CI/CD
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "projeto-a-492414")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GOOGLE_CLOUD_BUCKET = os.getenv("GOOGLE_CLOUD_BUCKET", "gs://gcs-lab-agent")
AGENT_DISPLAY_NAME = "agente_teste_simples"

# Inicializa o Vertex AI com o bucket de staging
vertexai.init(
    project=GOOGLE_CLOUD_PROJECT, 
    location=GOOGLE_CLOUD_LOCATION,
    staging_bucket=GOOGLE_CLOUD_BUCKET
)

def deploy_agent():
    print(f"🚀 Iniciando processo de deploy para o agente: {AGENT_DISPLAY_NAME}")
    
    # Busca a lista de agentes provisionados para verificar existência
    try:
        engines = agent_engines.list()
        existing_engine = next((e for e in engines if e.display_name == AGENT_DISPLAY_NAME), None)
    except Exception as e:
        print(f"❌ Erro ao listar agentes no Vertex AI: {e}")
        sys.exit(1)

    # Configuração do módulo que será enviado
    agent_config = agent_engines.ModuleAgent(
        module_name="root_agent", # Referência ao nome do arquivo (sem o .py)
        agent_name="agent_app",   # Referência ao objeto dentro do código
        register_operations={
          '': ['get_session', 'list_sessions', 'create_session', 'delete_session'],
          'async': ['async_get_session', 'async_list_sessions', 'async_create_session', 'async_delete_session', 'async_add_session_to_memory', 'async_search_memory'],
          'stream': ['stream_query', 'streaming_agent_run_with_events'],
          'async_stream': ['async_stream_query']
        }
    )
    
    # Adicionadas as libs que deram falta no log anterior
    requirements = [
        "google-cloud-aiplatform[adk,agent-engines]>=1.110.0",
        "vertexai>=1.43.0",
        "pydantic>=2.13.4",
        "cloudpickle>=3.1.2"
    ]
    
    # Caminho do diretório como pacote (garante que o __init__.py vá junto)
    extra_packages = ["agent/"]
    env_vars = {"GOOGLE_GENAI_USE_VERTEXAI": "True"}

    try:
        if existing_engine:
            print(f"🔄 Agente encontrado ({existing_engine.resource_name}). Iniciando UPDATE...")
            remote_app = agent_engines.update(
                resource_name=existing_engine.resource_name,
                agent_engine=agent_config,
                requirements=requirements,
                extra_packages=extra_packages,
                env_vars=env_vars,
            )
            print(f"✅ UPDATE finalizado com sucesso! Resource Name: {remote_app.resource_name}")
        else:
            print("🆕 Agente não encontrado. Iniciando CREATE...")
            remote_app = agent_engines.create(
                display_name=AGENT_DISPLAY_NAME,
                description="Agente puramente textual gerido via CI/CD",
                agent_engine=agent_config,
                requirements=requirements,
                extra_packages=extra_packages,
                env_vars=env_vars,
            )
            print(f"✅ CREATE finalizado com sucesso! Resource Name: {remote_app.resource_name}")

        # Exporta o nome do recurso para um arquivo temporário
        # O próximo step da pipeline (integration test) vai ler este arquivo
        with open("agent_resource_name.txt", "w") as f:
            f.write(remote_app.resource_name)

    except Exception as e:
        print(f"❌ Erro crítico durante o provisionamento do Agente: {e}")
        sys.exit(1) # Quebra a pipeline indicando falha

if __name__ == "__main__":
    deploy_agent()