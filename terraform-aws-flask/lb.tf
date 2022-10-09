# LOG8415E - Assignment 1
# lb.tf
# Terraform configuration relative to load balancer and target groups

# Declaring the two clusters
resource "aws_lb_target_group" "cluster1-target" {
  name     = "tg-cl1"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = aws_vpc.vpc.id
}

resource "aws_lb_target_group" "cluster2-target" {
  name     = "tg-cl2"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = aws_vpc.vpc.id
}

# Attaching instances to the clusters
resource "aws_lb_target_group_attachment" "attachments-cluster1-m4" {
  count            = length(aws_instance.m4_instance)
  target_group_arn = aws_lb_target_group.cluster1-target.arn
  target_id        = aws_instance.m4_instance[count.index].id
  port             = 5000
}

resource "aws_lb_target_group_attachment" "attachments-cluster2-t2" {
  count            = length(aws_instance.t2_instance)
  target_group_arn = aws_lb_target_group.cluster2-target.arn
  target_id        = aws_instance.t2_instance[count.index].id
  port             = 5000
}

# Creating the load balancer and its listener
resource "aws_lb" "load-balancer" {
  name               = "flask-load-balancer"
  internal           = false
  ip_address_type    = "ipv4"
  load_balancer_type = "application"
  security_groups    = [aws_security_group.flask_sg.id]
  subnets            = [aws_subnet.cluster1_subnet.id, aws_subnet.cluster2_subnet.id]
}

resource "aws_lb_listener" "listener_http" {
  load_balancer_arn = aws_lb.load-balancer.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "Nothing to show here."
      status_code  = "404"
    }
  }
}

# This is a load balancer rule designed to forward /cluster1 traffic to the appropriate target group
resource "aws_lb_listener_rule" "to-cluster-1" {
  listener_arn = aws_lb_listener.listener_http.arn
  priority     = 101

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

# This is a load balancer rule designed to respond to /teapot traffic with the appropriate response (easter egg)
resource "aws_lb_listener_rule" "to-teapot" {
  listener_arn = aws_lb_listener.listener_http.arn
  priority     = 99

  action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "This is a teapot! You're not supposed to do that :)"
      status_code  = "418"
    }
  }

  condition {
    path_pattern {
      values = ["/teapot"]
    }
  }
}
