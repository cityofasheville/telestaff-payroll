terraform {
  backend "s3" {
    bucket = "avl-tfstate-store"
    key    = "terraform/telestaff/terraform_dev.tfstate"
    region = "us-east-1"
  }
}

data "terraform_remote_state" "telestaff_layer" {
  backend = "s3"
  config = {
    bucket = "avl-tfstate-store"
    key    = "terraform/telestaff/layer/terraform_dev.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.region
}

resource "aws_lambda_function" "telestaff" {
  filename         = "function.zip"
  description      = "Telestaff Payroll-download from SFTP" 
  function_name    = "telestaff-payroll"
  role             = aws_iam_role.telestaff-role.arn # "arn:aws:iam::518970837364:role/telestaff-role"
  handler          = "index.handler"
  runtime          = "nodejs18.x"
  source_code_hash = filebase64sha256("function.zip")
  layers = [data.terraform_remote_state.telestaff_layer.outputs.telestaff_layer_arn]
  timeout          = 900
  # memory_size      = 256
  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }
  tags = {
    Name          = "telestaff-payroll"
    "coa:application" = "telestaff"
    "coa:department"  = "information-technology"
    "coa:owner"       = "jtwilson@ashevillenc.gov"
    "coa:owner-team"  = "dev"
    Description   = "Telestaff SFTP payroll download."
  }
}

output "telestaff_arn" {
  value = aws_lambda_function.telestaff.arn
}
