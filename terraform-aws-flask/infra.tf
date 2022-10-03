terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-1"
}

resource "m4_instance" "app_server" {
  count         = 5
  ami           = "ami-0149b2da6ceec4bb0"
  instance_type = "M4.large"
}

resource "t2_instance" "app_server" {
  count         = 4
  ami           = "ami-0149b2da6ceec4bb0"
  instance_type = "T2.large"
}