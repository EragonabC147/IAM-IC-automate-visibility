variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "lambda_name" {
  description = "Nombre de la función Lambda"
  type        = string
}

variable "memory_size" {
  description = "Tamaño de memoria para el Lambda"
  type        = number
}

variable "timeout" {
  description = "Tiempo máximo de ejecución del Lambda (en segundos)"
  type        = number
}

variable "environment_variables" {
  description = "Variables de entorno para la función Lambda"
  type        = map(string)
}

variable "log_retention" {
  description = "Días de retención de logs en CloudWatch"
  type        = number
}

variable "s3_bucket_name" {
  description = "Nombre del bucket S3"
  type        = string
}

variable "lambda_cron_expression" {
  description = "Expresión CRON para programar la ejecución periódica del Lambda"
  type        = string
}
