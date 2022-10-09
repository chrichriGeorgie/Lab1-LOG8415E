# LOG8415E - Assignment 1
# infra.tf
# Terraform configuration relative to instance definitions

# Declaring 5 instances of the m4 type
resource "aws_instance" "m4_instance" {
  count                       = 5
  ami                         = "ami-0149b2da6ceec4bb0"
  instance_type               = "m4.large"
  associate_public_ip_address = true
  user_data = templatefile("../scripts/instance-config.sh.tftpl", {
    number = count.index
  })
  subnet_id              = aws_subnet.cluster1_subnet.id
  vpc_security_group_ids = [aws_security_group.flask_sg.id]
}

# Declaring 4 instances of the t2 type
resource "aws_instance" "t2_instance" {
  count                       = 4
  ami                         = "ami-0149b2da6ceec4bb0"
  instance_type               = "t2.large"
  associate_public_ip_address = true
  user_data = templatefile("../scripts/instance-config.sh.tftpl", {
    number = count.index + 5
  })
  subnet_id              = aws_subnet.cluster2_subnet.id
  vpc_security_group_ids = [aws_security_group.flask_sg.id]
}
