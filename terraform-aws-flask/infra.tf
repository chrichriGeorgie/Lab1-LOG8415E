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

resource "aws_instance" "m4_instance" {
  count         = 5
  ami           = "ami-0149b2da6ceec4bb0"
  instance_type = "M4.large"
  availability_zone = "us-east-1"
}

resource "aws_instance" "t2_instance" {
  count         = 4
  ami           = "ami-0149b2da6ceec4bb0"
  instance_type = "T2.large"
  availability_zone = "us-east-1"
}

resource "aws_vpc" "cluster1-vpc" {
  cidr_block = "10.0.0.0/16"
}
resource "aws_vpc" "cluster2-vpc" {
  cidr_block = "10.1.0.0/16"
}

resource "aws_lb_target_group" "cluster1-target" {
  name     = "tf-example-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.cluster1-vpc.id
}

resource "aws_lb_target_group" "cluster2-target" {
  name     = "tf-example-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.cluster2-vpc.id
}

resource "aws_lb_target_group_attachment" "attachments-cluster1-m4" {
  count = length(aws_instance.m4_instance)
  target_group_arn = aws_lb_target_group.cluster1-target.arn
  target_id = aws_instance.m4_instance[count.index].id
}

resource "aws_lb_target_group_attachment" "attachments-cluster2-t2" {
  count = length(aws_instance.t2_instance)
  target_group_arn = aws_lb_target_group.cluster2-target.arn
  target_id = aws_instance.t2_instance[count.index].id
}

resource "aws_elb" "load-balancer" {
  name = "flask-load-balancer"
  availability_zones = ["us-east-1"]

  listener {
    instance_port     = 5000 # Flask listens on port 5000
    instance_protocol = "http"
    lb_port           = 80 # The load balancer receives requests on the classic HTTP port 80
    lb_protocol       = "http"
  }

  instances = [aws_instance.m4_instance[0].id, aws_instance.m4_instance[1].id, aws_instance.m4_instance[2].id, aws_instance.m4_instance[3].id, aws_instance.m4_instance[4].id, aws_instance.t2_instance[0].id,aws_instance.t2_instance[1].id,aws_instance.t2_instance[2].id,aws_instance.t2_instance[3].id]
}