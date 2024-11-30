variable "lambda_name" {
  description = "Nombre de la función Lambda"
  type        = string
}

variable "lambda_handler" {
  description = "Manejador del Lambda (archivo.función)"
  type        = string
  default     = "main.lambda_handler"
}

variable "runtime" {
  description = "Entorno de ejecución del Lambda"
  type        = string
  default     = "python3.10"
}

variable "memory_size" {
  description = "Tamaño de memoria para el Lambda"
  type        = number
  default     = 1280
}

variable "timeout" {
  description = "Tiempo máximo de ejecución del Lambda (en segundos)"
  type        = number
  default     = 60
}

variable "environment_variables" {
  description = "Variables de entorno para el Lambda"
  type        = map(string)
  default     = {}
}

variable "log_retention" {
  description = "Días de retención de logs de CloudWatch"
  type        = number
  default     = 7
}

variable "s3_bucket_arn" {
  description = "ARN del bucket S3 para usar en la política inline"
  type        = string
}

variable "lambda_cron_expression" {
  description = "Expresión CRON para la ejecución periódica del Lambda"
  type        = string
  default     = "rate(5 minutes)" # Valor por defecto (cada 5 minutos)
}
