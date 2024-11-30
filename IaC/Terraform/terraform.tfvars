lambda_name           = "iam-ic-visibility-lambda"
memory_size           = 1280
timeout               = 900
environment_variables = {
  INSTANCE_ARN      = "arn:aws:sso:::instance/ssoins-7223e41207ba70dc"
  IDENTITY_STORE_ID = "d-9067aa9e80"
  S3_BUCKET         = "prba-s3-iac-iam-ic"
}
log_retention         = 7
s3_bucket_name    = "prba-s3-iac-iam-ic"
lambda_cron_expression = "cron(30 1 * * ? *)"
