terraform {
  backend "s3" {
    bucket = "avl-tfstate-store"
    key    = "terraform/telestaff/layer/terraform_dev.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.region
}

resource "aws_lambda_layer_version" "telestaff_layer" {
  filename   = "layer.zip"
  source_code_hash = filebase64sha256("layer.zip")
  layer_name = "telestaff_layer"
}

output "telestaff_layer_arn" {
  value = aws_lambda_layer_version.telestaff_layer.arn
}
