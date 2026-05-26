import os
import sys
import ast
import vertexai
from vertexai import agent_engines

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "projeto-a-492414")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
AGENT_DISPLAY_NAME = "agente_teste_simples"

vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)

def run_integration_test():
    print("🧪 Iniciando Teste de Integração (E2E) pós-deploy...")

    # 1. Identificar com quem vamos falar
    try:
        # Tenta ler o arquivo gerado pelo step de deploy anterior
        with open("agent_resource_name.txt", "r") as f:
            resource_name = f.read().strip()
    except FileNotFoundError:
        print("⚠️ Arquivo agent_resource_name.txt não encontrado. Buscando ID via API...")
        engines = agent_engines.list()
        existing_engine = next((e for e in engines if e.display_name == AGENT_DISPLAY_NAME), None)
        if not existing_engine:
            print("❌ Falha: O agente não foi encontrado no projeto. Deploy falhou ou nome está incorreto.")
            sys.exit(1)
        resource_name = existing_engine.resource_name

    print(f"🔗 Conectando ao endpoint: {resource_name}")
    
    try:
        agente_remoto = agent_engines.get(resource_name)
        
        # 2. Configura a sessão de testes
        usuario = "usuario_cicd_test"
        sessao = agente_remoto.create_session(user_id=usuario)
        id_sessao = sessao['id'] if isinstance(sessao, dict) else sessao.id

        print("✉️ Enviando payload de teste...")
        
        # Faz uma pergunta focada para verificar se o motor do LLM e a conexão estão hígidos
        resposta_stream = agente_remoto.stream_query(
            user_id=usuario,
            session_id=id_sessao,
            message="Ping! Responda apenas com a palavra 'PONG' para confirmar conectividade."
        )

        # 3. Processa e avalia a resposta
        texto_final = ""
        for evento in resposta_stream:
            if isinstance(evento, str):
                evento_dict = ast.literal_eval(evento)
            else:
                evento_dict = evento
                
            if isinstance(evento_dict, dict) and 'content' in evento_dict:
                partes = evento_dict['content'].get('parts', [])
                for parte in partes:
                    if 'text' in parte:
                        texto_final += parte['text']

        print(f"🤖 Resposta do Agente: '{texto_final.strip()}'")

        if texto_final.strip():
            print("✅ Sucesso: O agente processou a requisição e devolveu uma resposta válida.")
            sys.exit(0) # Sinaliza sucesso para a esteira CI/CD
        else:
            print("❌ Falha: A requisição completou, mas o texto da resposta veio vazio.")
            sys.exit(1) # Sinaliza erro para a esteira CI/CD

    except Exception as e:
        print(f"❌ Falha Crítica na execução do teste: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_integration_test()