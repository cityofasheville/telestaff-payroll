resource "aws_iam_role" "telestaff-role" {
    name = "telestaff-role"
    assume_role_policy = file("./policy_role.json")
    tags = {
      Name          = "telestaff-role"
      "coa:application" = "telestaff"
      "coa:department"  = "information-technology"
      "coa:owner"       = "jtwilson@ashevillenc.gov"
      "coa:owner-team"  = "dev"
      Description   = "Role used by telestaff lambda function."
    }
}

# Lambda Basic Execution
resource "aws_iam_role_policy_attachment" "lambda_basic-telestaff" {
    role        = aws_iam_role.telestaff-role.name
    policy_arn  = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# VPC (databases)
resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
    role        = aws_iam_role.telestaff-role.name
    policy_arn  = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Invoke another Lambda
resource "aws_iam_policy" "invoke_lambda_policy-telestaff" {
  name        = "invoke_lambda_policy-telestaff"
  description = "Invoke another Lambda"
  policy = templatefile("./policy_invoke_lambda.json",{})
}
resource "aws_iam_role_policy_attachment" "invoke_lambda_policy-telestaff" {
    role        = aws_iam_role.telestaff-role.name
    policy_arn  = aws_iam_policy.invoke_lambda_policy-telestaff.arn
}

# S3
resource "aws_iam_role_policy_attachment" "lambda_s3_access-telestaff" {
    role        = aws_iam_role.telestaff-role.name
    policy_arn  = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}


# 

output "telestaff_role_arn" {
  value = "${aws_iam_role.telestaff-role.arn}"
}