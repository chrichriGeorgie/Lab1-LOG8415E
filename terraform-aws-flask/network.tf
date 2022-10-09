# LOG8415E - Assignment 1
# network.tf
# Terraform configuration relative to networking configuration

# Custom virtual private cloud for private addresses behind the load balancer
resource "aws_vpc" "vpc" {
  cidr_block         = "10.0.0.0/16"
  enable_dns_support = true
}

# Defining one subnet per target group to satisfy the requirement to have machines in us-east-1a et 1b
resource "aws_subnet" "cluster1_subnet" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
}

resource "aws_subnet" "cluster2_subnet" {
  vpc_id            = aws_vpc.vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
}

# Virtual private cloud configuration
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.vpc.id
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  route {
    ipv6_cidr_block = "::/0"
    gateway_id      = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "Public Route Table"
  }
}

resource "aws_route_table_association" "rt_a_cluster1" {
  subnet_id      = aws_subnet.cluster1_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "rt_a_cluster2" {
  subnet_id      = aws_subnet.cluster2_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

# Security group rules to allow ssh and http on the load balancer from all addresses
resource "aws_security_group" "flask_sg" {
  name   = "FLASK and SSH"
  vpc_id = aws_vpc.vpc.id

  ingress {
    from_port   = 80
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }
}