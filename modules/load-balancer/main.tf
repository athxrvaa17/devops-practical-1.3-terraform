resource "aws_security_group" "alb" {
  name        = "nimbus-q13-alb-sg"
  description = "Allow HTTP traffic to Application Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow public HTTP traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow HTTP traffic to application servers"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.20.0.0/16"]
  }

  tags = {
    Name = "nimbus-q13-alb-sg"
  }
}
