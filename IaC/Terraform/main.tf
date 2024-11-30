module "s3" {
  source      = "./modules/s3"
  bucket_name = var.s3_bucket_name
}

module "lambda" {
  source = "./modules/lambda"

  lambda_name           = var.lambda_name
  memory_size           = var.memory_size
  timeout               = var.timeout
  environment_variables = var.environment_variables
  log_retention         = var.log_retention
  s3_bucket_arn         = module.s3.bucket_arn
  lambda_cron_expression = var.lambda_cron_expression
}
