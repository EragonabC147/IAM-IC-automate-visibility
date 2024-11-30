output "lambda_arn" {
  description = "ARN de la función Lambda"
  value       = aws_lambda_function.this.arn
}

output "lambda_role_arn" {
  description = "ARN del rol IAM asignado al Lambda"
  value       = aws_iam_role.lambda_role.arn
}

output "layer_arn" {
  value = aws_lambda_layer_version.this.arn
}