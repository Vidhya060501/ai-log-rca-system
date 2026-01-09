terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
resource "aws_vpc" "rca_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "rca-chatbot-vpc"
  }
}

resource "aws_subnet" "public_subnet" {
  count             = 2
  vpc_id            = aws_vpc.rca_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "rca-chatbot-public-${count.index + 1}"
  }
}

resource "aws_subnet" "private_subnet" {
  count             = 2
  vpc_id            = aws_vpc.rca_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "rca-chatbot-private-${count.index + 1}"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_internet_gateway" "rca_igw" {
  vpc_id = aws_vpc.rca_vpc.id

  tags = {
    Name = "rca-chatbot-igw"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.rca_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.rca_igw.id
  }

  tags = {
    Name = "rca-chatbot-public-rt"
  }
}

resource "aws_route_table_association" "public_rta" {
  count          = length(aws_subnet.public_subnet)
  subnet_id      = aws_subnet.public_subnet[count.index].id
  route_table_id = aws_route_table.public_rt.id
}

# Security Groups
resource "aws_security_group" "ecs_sg" {
  name        = "rca-chatbot-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.rca_vpc.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rca-chatbot-ecs-sg"
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "rca-chatbot-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.rca_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rca-chatbot-rds-sg"
  }
}

# RDS PostgreSQL with pgvector
resource "aws_db_subnet_group" "rca_db_subnet" {
  name       = "rca-chatbot-db-subnet"
  subnet_ids = aws_subnet.private_subnet[*].id

  tags = {
    Name = "rca-chatbot-db-subnet"
  }
}

resource "aws_db_instance" "rca_postgres" {
  identifier             = "rca-chatbot-db"
  engine                 = "postgres"
  engine_version         = "16.1"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  storage_type           = "gp3"
  db_name                = "rca_db"
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.rca_db_subnet.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true
  publicly_accessible    = false

  tags = {
    Name = "rca-chatbot-db"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "rca_cluster" {
  name = "rca-chatbot-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "rca-chatbot-cluster"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "rca_logs" {
  name              = "/ecs/rca-chatbot"
  retention_in_days = 7

  tags = {
    Name = "rca-chatbot-logs"
  }
}

# Application Load Balancer
resource "aws_lb" "rca_alb" {
  name               = "rca-chatbot-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_sg.id]
  subnets            = aws_subnet.public_subnet[*].id

  enable_deletion_protection = false

  tags = {
    Name = "rca-chatbot-alb"
  }
}

resource "aws_lb_target_group" "rca_tg" {
  name        = "rca-chatbot-tg"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.rca_vpc.id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    protocol            = "HTTP"
    matcher             = "200"
  }

  tags = {
    Name = "rca-chatbot-tg"
  }
}

resource "aws_lb_listener" "rca_listener" {
  load_balancer_arn = aws_lb.rca_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.rca_tg.arn
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "rca_user"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Outputs
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.rca_alb.dns_name
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.rca_postgres.endpoint
  sensitive   = true
}


