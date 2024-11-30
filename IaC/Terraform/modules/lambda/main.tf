resource "aws_iam_role" "lambda_role" {
  name               = "${var.lambda_name}_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}


resource "aws_iam_role_policy" "lambda_inline_policy" {
  name   = "${var.lambda_name}_policy"
  role   = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["sso:Describe*", "sso:Get*", "sso:List*"],
        Resource = "*"
      },
      {
        Effect   = "Allow",
        Action   = ["iam:GetPolicy", "iam:GetPolicyVersion"],
        Resource = "arn:aws:iam::*:policy/*"
      },
      {
        Effect   = "Allow",
        Action   = ["s3:PutObject", "s3:ListBucket", "s3:GetObject"],
        Resource = [
          "${var.s3_bucket_arn}",
          "${var.s3_bucket_arn}/*"
        ]
      },
      {
        Effect   = "Allow",
        Action   = ["identitystore:Describe*", "identitystore:List*"],
        Resource = ["*", "arn:aws:identitystore:::user/*", "arn:aws:identitystore::*:identitystore/*"]
      }
    ]
  })
}

resource "aws_lambda_layer_version" "this" {
  filename          = "${path.module}/files/layer.zip" # Ruta al archivo ZIP del layer
  layer_name        = "${var.lambda_name}_layer"      # Nombre del Layer
  compatible_runtimes = [                             # Runtimes compatibles
    var.runtime
  ]
  description       = "Custom Layer for ${var.lambda_name}"
}
resource "aws_lambda_function" "this" {
  function_name = var.lambda_name
  handler       = var.lambda_handler
  runtime       = var.runtime
  memory_size   = var.memory_size
  timeout       = var.timeout
  role          = aws_iam_role.lambda_role.arn
  filename      = data.archive_file.archive_lambda.output_path

  environment {
    variables = var.environment_variables
  }

  layers = [aws_lambda_layer_version.this.arn]
}


resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.lambda_name}"
  retention_in_days = var.log_retention
}

# Recurso para la regla de EventBridge
resource "aws_cloudwatch_event_rule" "lambda_schedule" {
  name        = "${var.lambda_name}_schedule_rule"
  description = "Regla para ejecutar ${var.lambda_name} de forma periódica"
  schedule_expression = var.lambda_cron_expression # Expresión CRON pasada como variable
}

# Permitir que EventBridge invoque la función Lambda
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_schedule.arn
}

# Asociar la regla de EventBridge con el Lambda
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.lambda_schedule.name
  target_id = "lambda"
  arn       = aws_lambda_function.this.arn
}
