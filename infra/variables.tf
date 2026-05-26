variable "project_id" {
  type        = string
  description = "O ID do projeto no Google Cloud"
  default     = "projeto-a-492414"
}

variable "location" {
  type        = string
  description = "A região onde os recursos serão provisionados"
  default     = "us-central1"
}

variable "bucket_name" {
  type        = string
  description = "O nome do bucket de staging para o Vertex AI Agent Engine"
  default     = "gcs-lab-agent"
}