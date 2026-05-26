terraform {
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.location
}

# 1. Ativação automatizada das APIs necessárias no projeto
resource "google_project_service" "gcp_services" {
  for_each = toset([
    "aiplatform.googleapis.com", # Vertex AI / Agent Engine
    "storage.googleapis.com",    # Cloud Storage
  ])

  service            = each.key
  disable_on_destroy = false
}

# 2. Criação do Bucket de Staging
resource "google_storage_bucket" "staging_bucket" {
  name          = var.bucket_name
  location      = var.location
  force_destroy = true # Permite deletar o bucket mesmo se ele contiver artefatos antigos do Agent Engine

  # Garante que o acesso seja controlado estritamente via IAM (Melhor prática do GCP)
  uniform_bucket_level_access = true

  # Mantém um histórico de versões dos códigos enviados, útil para auditoria da esteira
  versioning {
    enabled = true
  }

  # Regra de ciclo de vida: remove automaticamente artefatos de staging mais antigos que 30 dias para economizar custos
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30
    }
  }

  # Garante que o Terraform só tentará criar o bucket após as APIs estarem ativas
  depends_on = [google_project_service.gcp_services]
}