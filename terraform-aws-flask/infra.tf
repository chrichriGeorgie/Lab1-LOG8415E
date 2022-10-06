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
  user_data = templatefile("./instance-config.sh.tftpl", {
    number = count.index
  })
}

resource "aws_instance" "t2_instance" {
  count         = 4
  ami           = "ami-0149b2da6ceec4bb0"
  instance_type = "T2.large"
  availability_zone = "us-east-1"
  user_data = templatefile("./instance-config.sh.tftpl", {
    number = count.index + 5
  })
}

resource "aws_lb_target_group" "cluster1-target" {
  name     = "tf-example-lb-tg"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = aws_vpc.vpc.id
}

resource "aws_lb_target_group" "cluster2-target" {
  name     = "tf-example-lb-tg"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = aws_vpc.vpc.id
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

resource "aws_lb" "load-balancer" {
  name = "flask-load-balancer"
  internal        = false
  ip_address_type = "ipv4"
  load_balancer_type = "application"
  security_groups = [aws_security_group.flask_sg.id]
  subnets = [aws_subnet.cluster1_subnet.id, aws_subnet.cluster2_subnet.id]
}

resource "aws_lb_listener" "listener_http" {
  load_balancer_arn = aws_lb.load-balancer.arn
  port = "80"
  protocol = "http"
  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "No destination specified or you don't know what you're doing."
      status_code =  "404"
    }
  }
}

# This is a load balancer rule designed to forward /cluster1 traffic to the appropriate target group
resource "aws_lb_listener_rule" "to-cluster-1" {
  listener_arn = aws_lb_listener.listener_http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.cluster1-target.arn
  }

  condition {
    path_pattern {
      values = ["/cluster1"]
    }
  }
}

# This is a load balancer rule designed to forward /cluster2 traffic to the appropriate target group
resource "aws_lb_listener_rule" "to-cluster-2" {
  listener_arn = aws_lb_listener.listener_http.arn
  priority     = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.cluster2-target.arn
  }

  condition {
    path_pattern {
      values = ["/cluster2"]
    }
  }
}

