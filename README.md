# 🤖 Vertex AI Agent Engine - CI/CD Lab

Este repositório contém a infraestrutura e o código necessários para provisionar, fazer o deploy e testar de forma contínua um Agente de IA Generativa no **Google Cloud Platform (GCP)** utilizando o **Vertex AI Agent Engine**.

O objetivo deste laboratório é demonstrar um ciclo de vida de desenvolvimento de software (SDLC) completo para aplicações de IA (LLMOps), separando a camada de infraestrutura (IaC) da camada da aplicação, e automatizando as implantações via GitHub Actions.

## 🏗️ Arquitetura e Tecnologias

* **IA & LLM:** Google Cloud Vertex AI (Gemini 2.5 Flash), Google ADK (Agent Development Kit).
* **Infraestrutura como Código (IaC):** Terraform.
* **CI/CD:** GitHub Actions.
* **Segurança:** Workload Identity Federation (WIF) para autenticação *keyless*.
* **Linguagem:** Python 3.11.

## 📂 Estrutura do Repositório

```text
/
├── .github/workflows/
│   └── deploy-agent.yml       # Pipeline principal de CI/CD
├── agent/
│   ├── requirements.txt       # Dependências do motor do Agente
│   └── root_agent.py          # Definição do LlmAgent, Prompt e Tools
├── infra/
│   ├── main.tf                # Provisionamento de APIs e do Bucket GCS
│   ├── variables.tf           # Variáveis do Terraform
│   └── outputs.tf             # Outputs de infraestrutura
├── scripts/
│   ├── deploy.py              # Script de Create/Update idempotente
│   └── integration_test.py    # Teste End-to-End (E2E) pós-deploy
└── README.md