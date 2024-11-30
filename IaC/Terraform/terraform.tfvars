lambda_name           = "your_name_for_lambda"
memory_size           = 1280
timeout               = 900
environment_variables = {
  INSTANCE_ARN      = "your_instance_arn"
  IDENTITY_STORE_ID = "your_identity_store_id"
  S3_BUCKET         = "your_s3_bucket"
}
log_retention         = 7
s3_bucket_name    = "your_s3_bucket"
lambda_cron_expression = "cron(* * * * * *)"
